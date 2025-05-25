"""
Database-backed cache service to replace in-memory caching.
Provides persistent storage for API responses with intelligent freshness checking.
"""

import json
import hashlib
import uuid
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from sqlalchemy import select, delete, update, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from ..models.database import CachedData, PreloadSession, DataFreshness
from ..utils.database_connection import get_database_manager

logger = logging.getLogger(__name__)


class DatabaseCacheService:
    """
    Service class for database-backed caching operations.
    Replaces the in-memory cache with persistent SQLite storage.
    """
    
    def __init__(self):
        self.db_manager = get_database_manager()
    
    @staticmethod
    def create_cache_key(endpoint: str, params: Dict[str, Any] = None) -> str:
        """
        Create a consistent cache key from endpoint and parameters.
        Compatible with the existing frontend cache key format.
        """
        # Ensure endpoint starts with /
        if not endpoint.startswith('/'):
            endpoint = f"/{endpoint}"
        
        if params and len(params) > 0:
            # Sort parameters for consistent key generation
            sorted_params = sorted(params.items())
            param_string = "&".join([f"{k}={v}" for k, v in sorted_params])
            return f"{endpoint}?{param_string}"
        return endpoint
    
    async def get_cached_data(self, cache_key: str) -> Optional[Dict[Any, Any]]:
        """
        Retrieve cached data by cache key.
        
        Args:
            cache_key: The cache key to look up
            
        Returns:
            Cached data as dictionary, or None if not found/expired
        """
        try:
            async with self.db_manager.get_async_session() as session:
                # Query for the cache entry
                result = await session.execute(
                    select(CachedData).where(CachedData.cache_key == cache_key)
                )
                cache_entry = result.scalar_one_or_none()
                
                if not cache_entry:
                    logger.debug(f"Cache miss for key: {cache_key}")
                    return None
                
                # Check if expired
                if cache_entry.is_expired():
                    logger.debug(f"Cache expired for key: {cache_key}")
                    # Schedule deletion without blocking main operation
                    asyncio.create_task(self._delete_expired_entry(cache_key))
                    return None
                
                logger.debug(f"Cache hit for key: {cache_key}")
                return cache_entry.get_data()
                
        except Exception as e:
            logger.error(f"Error retrieving cached data for key {cache_key}: {e}")
            return None
    
    async def save_cached_data(
        self,
        cache_key: str,
        data: Dict[Any, Any],
        endpoint: str,
        agency_id: Optional[str] = None,
        time_period: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        expires_hours: int = 24,
        is_preloaded: bool = False
    ) -> bool:
        """
        Save data to cache with metadata.
        
        Args:
            cache_key: Unique cache key
            data: Data to cache
            endpoint: API endpoint that generated this data
            agency_id: Optional agency ID for filtering
            time_period: Optional time period for filtering
            params: Optional additional parameters
            expires_hours: Hours until expiry (default 24)
            is_preloaded: Whether this data was preloaded
            
        Returns:
            True if saved successfully, False otherwise
        """
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Use a new session for each attempt to avoid state issues
                async with self.db_manager.get_async_session() as session:
                    try:
                        # Check if entry exists first
                        existing_result = await session.execute(
                            select(CachedData).where(CachedData.cache_key == cache_key)
                        )
                        existing_entry = existing_result.scalar_one_or_none()
                        
                        if existing_entry:
                            # Update existing entry
                            existing_entry.set_data(data)
                            existing_entry.set_parameters(params)
                            existing_entry.created_at = datetime.utcnow()
                            existing_entry.set_expiry(expires_hours)
                            existing_entry.is_preloaded = is_preloaded
                            logger.debug(f"Updated existing cache entry for key: {cache_key}")
                        else:
                            # Create new entry
                            cache_entry = CachedData(
                                cache_key=cache_key,
                                endpoint=endpoint,
                                agency_id=agency_id,
                                time_period=time_period,
                                is_preloaded=is_preloaded
                            )
                            cache_entry.set_data(data)
                            cache_entry.set_parameters(params)
                            cache_entry.set_expiry(expires_hours)
                            
                            session.add(cache_entry)
                            logger.debug(f"Created new cache entry for key: {cache_key}")
                        
                        # Commit the cache data first
                        await session.commit()
                        
                        logger.debug(f"Saved cache entry for key: {cache_key}")
                        
                        # Update data freshness in background to avoid blocking
                        asyncio.create_task(
                            self._update_data_freshness_background(endpoint, agency_id, time_period, expires_hours)
                        )
                        
                        return True
                        
                    except Exception as e:
                        try:
                            await session.rollback()
                        except:
                            pass  # Ignore rollback errors
                        raise e
                    
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed saving cache key {cache_key}: {e}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to save cached data after {max_retries} attempts: {e}")
                    return False
                
                # Exponential backoff
                await asyncio.sleep(0.2 * (2 ** attempt))
                
        return False
    
    async def is_data_fresh(
        self,
        data_type: str,
        agency_id: Optional[str] = None,
        time_period: Optional[str] = None
    ) -> Tuple[bool, Optional[float]]:
        """
        Check if data is still fresh based on freshness rules.
        
        Args:
            data_type: Type of data (quotas, reaction_times, problematic_stays)
            agency_id: Optional agency ID
            time_period: Optional time period
            
        Returns:
            Tuple of (is_fresh: bool, hours_until_stale: Optional[float])
        """
        try:
            async with self.db_manager.get_async_session() as session:
                try:
                    result = await session.execute(
                        select(DataFreshness).where(
                            and_(
                                DataFreshness.data_type == data_type,
                                DataFreshness.agency_id == agency_id,
                                DataFreshness.time_period == time_period
                            )
                        )
                    )
                    freshness_entry = result.scalar_one_or_none()
                    
                    if not freshness_entry:
                        # No freshness data = not fresh
                        return False, None
                    
                    is_fresh = freshness_entry.is_data_fresh()
                    hours_until_stale = freshness_entry.time_until_stale_hours()
                    
                    return is_fresh, hours_until_stale
                    
                except Exception as e:
                    try:
                        await session.rollback()
                    except:
                        pass  # Ignore rollback errors
                    raise e
                
        except Exception as e:
            logger.error(f"Error checking data freshness: {e}")
            return False, None
    
    async def get_stale_data_types(self, agency_id: str) -> List[Dict[str, Any]]:
        """
        Get all stale data types for an agency.
        
        Args:
            agency_id: Agency ID to check
            
        Returns:
            List of stale data information
        """
        try:
            async with self.db_manager.get_async_session() as session:
                # Get all DataFreshness entries for this agency
                result = await session.execute(
                    select(DataFreshness).where(DataFreshness.agency_id == agency_id)
                )
                freshness_entries = result.scalars().all()
                
                stale_data = []
                for entry in freshness_entries:
                    # Check if data is stale using the model's method
                    if not entry.is_data_fresh():
                        stale_data.append({
                            "data_type": entry.data_type,
                            "time_period": entry.time_period,
                            "age_hours": entry.get_age_hours(),
                            "freshness_duration": entry.freshness_duration_hours
                        })
                
                return stale_data
                
        except Exception as e:
            logger.error(f"Error getting stale data types for agency {agency_id}: {e}")
            return []
    
    async def create_preload_session(self, agency_id: str) -> str:
        """
        Create a new preload session.
        
        Args:
            agency_id: Agency ID for the preload
            
        Returns:
            Session key for tracking
        """
        try:
            session_key = f"preload_{agency_id}_{uuid.uuid4().hex[:8]}"
            
            async with self.db_manager.get_async_session() as session:
                preload_session = PreloadSession(
                    agency_id=agency_id,
                    session_key=session_key
                )
                session.add(preload_session)
                await session.commit()
                
                logger.info(f"Created preload session: {session_key}")
                return session_key
                
        except Exception as e:
            logger.error(f"Error creating preload session for agency {agency_id}: {e}")
            raise
    
    async def update_preload_progress(
        self,
        session_key: str,
        total_requests: int,
        successful_requests: int,
        failed_requests: int
    ) -> bool:
        """
        Update preload session progress.
        
        Args:
            session_key: Session key to update
            total_requests: Total number of requests
            successful_requests: Number of successful requests
            failed_requests: Number of failed requests
            
        Returns:
            True if updated successfully
        """
        try:
            async with self.db_manager.get_async_session() as session:
                result = await session.execute(
                    update(PreloadSession)
                    .where(PreloadSession.session_key == session_key)
                    .values(
                        total_requests=total_requests,
                        successful_requests=successful_requests,
                        failed_requests=failed_requests
                    )
                )
                await session.commit()
                
                return result.rowcount > 0
                
        except Exception as e:
            logger.error(f"Error updating preload progress for session {session_key}: {e}")
            return False
    
    async def complete_preload_session(self, session_key: str, success: bool = True, error_msg: str = None) -> bool:
        """
        Mark preload session as completed or failed.
        
        Args:
            session_key: Session key to complete
            success: Whether the session completed successfully
            error_msg: Optional error message if failed
            
        Returns:
            True if updated successfully
        """
        try:
            async with self.db_manager.get_async_session() as session:
                result = await session.execute(
                    select(PreloadSession).where(PreloadSession.session_key == session_key)
                )
                preload_session = result.scalar_one_or_none()
                
                if not preload_session:
                    return False
                
                if success:
                    preload_session.mark_completed()
                else:
                    preload_session.mark_failed(error_msg or "Unknown error")
                
                await session.commit()
                logger.info(f"Preload session {session_key} marked as {'completed' if success else 'failed'}")
                return True
                
        except Exception as e:
            logger.error(f"Error completing preload session {session_key}: {e}")
            return False
    
    async def get_preload_session_info(self, session_key: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a preload session.
        
        Args:
            session_key: Session key to query
            
        Returns:
            Session information or None if not found
        """
        try:
            async with self.db_manager.get_async_session() as session:
                result = await session.execute(
                    select(PreloadSession).where(PreloadSession.session_key == session_key)
                )
                preload_session = result.scalar_one_or_none()
                
                if not preload_session:
                    return None
                
                return {
                    "session_key": preload_session.session_key,
                    "agency_id": preload_session.agency_id,
                    "status": preload_session.status,
                    "started_at": preload_session.started_at.isoformat(),
                    "completed_at": preload_session.completed_at.isoformat() if preload_session.completed_at else None,
                    "total_requests": preload_session.total_requests,
                    "successful_requests": preload_session.successful_requests,
                    "failed_requests": preload_session.failed_requests,
                    "success_rate": preload_session.get_success_rate(),
                    "duration_minutes": preload_session.get_duration_minutes(),
                    "error_message": preload_session.error_message
                }
                
        except Exception as e:
            logger.error(f"Error getting preload session info for {session_key}: {e}")
            return None
    
    async def cleanup_expired_data(self) -> int:
        """Remove expired cache entries."""
        return await self.db_manager.cleanup_expired_data()
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics for monitoring.
        
        Returns:
            Dictionary with cache statistics
        """
        try:
            async with self.db_manager.get_async_session() as session:
                # Total entries
                total_result = await session.execute(select(func.count(CachedData.id)))
                total_entries = total_result.scalar()
                
                # Preloaded entries
                preloaded_result = await session.execute(
                    select(func.count(CachedData.id)).where(CachedData.is_preloaded == True)
                )
                preloaded_entries = preloaded_result.scalar()
                
                # Expired entries
                expired_result = await session.execute(
                    select(func.count(CachedData.id)).where(
                        and_(
                            CachedData.expires_at.isnot(None),
                            CachedData.expires_at < datetime.utcnow()
                        )
                    )
                )
                expired_entries = expired_result.scalar()
                
                # Recent sessions
                recent_sessions_result = await session.execute(
                    select(func.count(PreloadSession.id)).where(
                        PreloadSession.started_at > (datetime.utcnow() - timedelta(days=1))
                    )
                )
                recent_sessions = recent_sessions_result.scalar()
                
                return {
                    "total_entries": total_entries,
                    "preloaded_entries": preloaded_entries,
                    "expired_entries": expired_entries,
                    "recent_sessions_24h": recent_sessions,
                    "database_info": self.db_manager.get_database_info()
                }
                
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"error": str(e)}
    

    async def _update_data_freshness(
        self,
        session: AsyncSession,
        endpoint: str,
        agency_id: Optional[str],
        time_period: Optional[str],
        freshness_hours: int
    ):
        """Update data freshness tracking."""
        try:
            # Extract data type from endpoint
            data_type = self._extract_data_type(endpoint)
            if not data_type:
                return
            
            # Simple check and update approach
            result = await session.execute(
                select(DataFreshness).where(
                    and_(
                        DataFreshness.data_type == data_type,
                        DataFreshness.agency_id == agency_id,
                        DataFreshness.time_period == time_period
                    )
                )
            )
            freshness_entry = result.scalar_one_or_none()
            
            if freshness_entry:
                freshness_entry.update_freshness()
                freshness_entry.freshness_duration_hours = freshness_hours
            else:
                # Check again for race condition
                try:
                    freshness_entry = DataFreshness(
                        data_type=data_type,
                        agency_id=agency_id,
                        time_period=time_period,
                        freshness_duration_hours=freshness_hours
                    )
                    session.add(freshness_entry)
                except Exception:
                    # If it fails due to unique constraint, just ignore
                    await session.rollback()
                    # Try to find the existing one that was created by another session
                    result = await session.execute(
                        select(DataFreshness).where(
                            and_(
                                DataFreshness.data_type == data_type,
                                DataFreshness.agency_id == agency_id,
                                DataFreshness.time_period == time_period
                            )
                        )
                    )
                    freshness_entry = result.scalar_one_or_none()
                    if freshness_entry:
                        freshness_entry.update_freshness()
                        freshness_entry.freshness_duration_hours = freshness_hours
                    
        except Exception as e:
            logger.warning(f"Error updating data freshness: {e}")

    async def _update_data_freshness_background(
        self,
        endpoint: str,
        agency_id: Optional[str],
        time_period: Optional[str],
        freshness_hours: int
    ):
        """Update data freshness tracking in background."""
        try:
            # Use a completely separate session to avoid conflicts
            async with self.db_manager.get_async_session() as session:
                await self._update_data_freshness(session, endpoint, agency_id, time_period, freshness_hours)
                await session.commit()
        except Exception as e:
            logger.warning(f"Error updating data freshness in background: {e}")
    
    async def _delete_expired_entry(self, cache_key: str):
        """Delete expired entry in background without blocking."""
        try:
            async with self.db_manager.get_async_session() as session:
                result = await session.execute(
                    select(CachedData).where(CachedData.cache_key == cache_key)
                )
                cache_entry = result.scalar_one_or_none()
                if cache_entry and cache_entry.is_expired():
                    await session.delete(cache_entry)
                    await session.commit()
                    logger.debug(f"Deleted expired cache entry: {cache_key}")
        except Exception as e:
            logger.warning(f"Error deleting expired entry {cache_key}: {e}")
    
    @staticmethod
    def _extract_data_type(endpoint: str) -> Optional[str]:
        """Extract data type from endpoint path."""
        if "quotas" in endpoint:
            return "quotas"
        elif "reaction_times" in endpoint:
            return "reaction_times"
        elif "problematic_stays" in endpoint:
            return "problematic_stays"
        elif "profile_quality" in endpoint:
            return "profile_quality"
        return None


# Global service instance
_cache_service: Optional[DatabaseCacheService] = None

def get_cache_service() -> DatabaseCacheService:
    """Get the global cache service instance."""
    global _cache_service
    if _cache_service is None:
        _cache_service = DatabaseCacheService()
    return _cache_service