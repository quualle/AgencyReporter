"""
Cache management endpoints for database-backed caching system.
Provides API endpoints for cache operations, freshness checking, and preload management.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List, Optional
import logging
from urllib.parse import unquote

from ..services.database_cache_service import get_cache_service
from ..utils.database_connection import get_async_db_session

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health")
async def cache_health():
    """
    Check cache system health.
    """
    try:
        cache_service = get_cache_service()
        db_manager = cache_service.db_manager
        
        # Test database connection
        connection_ok = await db_manager.test_connection()
        
        if not connection_ok:
            raise HTTPException(status_code=503, detail="Database connection failed")
        
        # Get basic stats
        stats = await cache_service.get_cache_stats()
        
        return {
            "status": "healthy",
            "database_connected": connection_ok,
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"Cache health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Cache system unhealthy: {str(e)}")


@router.get("/stats")
async def get_cache_stats():
    """
    Get comprehensive cache statistics.
    """
    try:
        cache_service = get_cache_service()
        stats = await cache_service.get_cache_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get cache stats: {str(e)}")


@router.get("/freshness/{agency_id}")
async def check_data_freshness(
    agency_id: str,
    data_types: Optional[List[str]] = Query(None, description="Specific data types to check"),
    time_periods: Optional[List[str]] = Query(None, description="Specific time periods to check")
):
    """
    Check data freshness for an agency.
    
    Args:
        agency_id: Agency ID to check
        data_types: Optional list of data types to check (quotas, reaction_times, problematic_stays)
        time_periods: Optional list of time periods to check (last_quarter, last_year, etc.)
        
    Returns:
        Freshness information including stale data types
    """
    try:
        cache_service = get_cache_service()
        
        # Default data types and time periods if not specified
        if not data_types:
            data_types = ["quotas", "reaction_times", "problematic_stays"]
        
        if not time_periods:
            time_periods = ["last_quarter", "last_year", "last_month", "all_time"]
        
        freshness_results = {}
        stale_data = []
        all_fresh = True
        
        # Check freshness for each combination
        for data_type in data_types:
            freshness_results[data_type] = {}
            
            for time_period in time_periods:
                is_fresh, hours_until_stale = await cache_service.is_data_fresh(
                    data_type, agency_id, time_period
                )
                
                freshness_results[data_type][time_period] = {
                    "is_fresh": is_fresh,
                    "hours_until_stale": hours_until_stale
                }
                
                if not is_fresh:
                    all_fresh = False
                    stale_data.append({
                        "data_type": data_type,
                        "time_period": time_period
                    })
        
        # Get detailed stale data information
        stale_data_details = await cache_service.get_stale_data_types(agency_id)
        
        return {
            "agency_id": agency_id,
            "all_data_fresh": all_fresh,
            "freshness_details": freshness_results,
            "stale_data_types": stale_data,
            "stale_data_details": stale_data_details
        }
        
    except Exception as e:
        logger.error(f"Error checking data freshness for agency {agency_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to check data freshness: {str(e)}")


@router.post("/preload/{agency_id}")
async def start_preload_session(agency_id: str):
    """
    Start a new preload session for an agency.
    
    Args:
        agency_id: Agency ID to preload data for
        
    Returns:
        Session information including session key for tracking
    """
    try:
        cache_service = get_cache_service()
        
        # Check data freshness using cache service directly
        data_types = ["quotas", "reaction_times", "problematic_stays"]
        time_periods = ["last_quarter", "last_year", "last_month", "all_time"]
        
        all_fresh = True
        stale_data = []
        
        # Check freshness for each combination
        for data_type in data_types:
            for time_period in time_periods:
                is_fresh, hours_until_stale = await cache_service.is_data_fresh(
                    data_type, agency_id, time_period
                )
                
                if not is_fresh:
                    all_fresh = False
                    stale_data.append({
                        "data_type": data_type,
                        "time_period": time_period
                    })
        
        # If all data is fresh, return early
        if all_fresh:
            return {
                "message": "Alle Daten sind bereits aktuell geladen!",
                "all_data_fresh": True,
                "session_key": None,
                "stale_data_types": []
            }
        
        # Create new preload session
        session_key = await cache_service.create_preload_session(agency_id)
        
        return {
            "message": "Preload-Session gestartet",
            "all_data_fresh": False,
            "session_key": session_key,
            "stale_data_types": stale_data
        }
        
    except Exception as e:
        logger.error(f"Error starting preload session for agency {agency_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start preload session: {str(e)}")


@router.post("/preload/comprehensive")
async def start_comprehensive_preload():
    """
    Start comprehensive preload session for ALL agencies and ALL time periods.
    This will load all data into the database cache, potentially taking a long time.
    
    Returns:
        Session information including session key for tracking progress
    """
    try:
        cache_service = get_cache_service()
        
        # Create comprehensive preload session
        session_key = await cache_service.create_preload_session("comprehensive_all_agencies")
        
        logger.info(f"Started comprehensive preload session: {session_key}")
        
        return {
            "message": "Comprehensive preload session started for all agencies and time periods",
            "session_key": session_key,
            "estimated_duration": "This may take 10-30 minutes depending on data size",
            "comprehensive": True
        }
        
    except Exception as e:
        logger.error(f"Error starting comprehensive preload session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start comprehensive preload: {str(e)}")


@router.post("/preload/comprehensive/execute")
async def execute_comprehensive_preload():
    """
    Execute comprehensive preload for ALL agencies and ALL time periods.
    This creates cache entries that mimic what the frontend would call.
    WARNING: This can take a very long time and load a lot of data.
    
    Returns:
        Results of the comprehensive preload operation
    """
    import asyncio
    import httpx
    from ..utils.query_manager import QueryManager
    
    try:
        cache_service = get_cache_service()
        session_key = await cache_service.create_preload_session("comprehensive_execution")
        
        # Get all agencies
        query_manager = QueryManager()
        agencies = query_manager.get_all_agencies()
        
        # Define time periods and data types
        time_periods = ["last_quarter", "last_year", "last_month", "all_time"]
        
        # Calculate total requests
        total_requests = len(agencies) * len(time_periods) * 7  # 7 different API types per agency/period
        completed_requests = 0
        successful_requests = 0
        failed_requests = 0
        skipped_requests = 0
        
        logger.info(f"Starting comprehensive preload for {len(agencies)} agencies, {len(time_periods)} time periods = {total_requests} total requests")
        
        # Update initial progress
        await cache_service.update_preload_progress(session_key, total_requests, 0, 0)
        
        # Base URL for internal API calls
        base_url = "http://localhost:8000/api"
        
        # Process each agency
        async with httpx.AsyncClient(timeout=60.0) as client:
            for agency in agencies:
                # Handle both dict and object formats
                if isinstance(agency, dict):
                    agency_id = agency.get('agency_id') or agency.get('_id')
                    agency_name = agency.get('agency_name') or agency.get('name')
                else:
                    agency_id = agency.agency_id
                    agency_name = agency.agency_name
                
                logger.info(f"Processing agency: {agency_id} ({agency_name})")
                
                for time_period in time_periods:
                    # List of API endpoints to call for each agency/time period combination
                    api_endpoints = [
                        f"/quotas/{agency_id}/all?time_period={time_period}",
                        f"/quotas/{agency_id}/cancellation-before-arrival?time_period={time_period}",
                        f"/reaction_times/{agency_id}?time_period={time_period}",
                        f"/reaction_times/{agency_id}/arrival_to_cancellation?time_period={time_period}",
                        f"/quotas_with_reasons/{agency_id}/early-end-reasons?time_period={time_period}",
                        f"/quotas_with_reasons/{agency_id}/cancellation-reasons?time_period={time_period}",
                        f"/problematic_stays/overview?agency_id={agency_id}&time_period={time_period}"
                    ]
                    
                    for endpoint in api_endpoints:
                        try:
                            # Skip problematic endpoints that might cause timestamp issues
                            if "all_time" in endpoint and ("quotas" in endpoint or "reaction_times" in endpoint):
                                logger.warning(f"Skipping potentially problematic endpoint: {endpoint}")
                                skipped_requests += 1
                                completed_requests += 1
                                continue
                            
                            # Make the API call
                            url = f"{base_url}{endpoint}"
                            response = await client.get(url)
                            
                            if response.status_code == 200:
                                successful_requests += 1
                                logger.debug(f"Successfully preloaded: {endpoint}")
                            else:
                                failed_requests += 1
                                logger.warning(f"Failed to preload {endpoint}: HTTP {response.status_code}")
                                
                        except Exception as e:
                            failed_requests += 1
                            logger.error(f"Error preloading {endpoint}: {e}")
                        
                        completed_requests += 1
                        
                        # Update progress periodically
                        if completed_requests % 10 == 0:
                            await cache_service.update_preload_progress(
                                session_key, total_requests, successful_requests, failed_requests
                            )
                            logger.info(f"Progress: {completed_requests}/{total_requests} ({(completed_requests/total_requests)*100:.1f}%)")
        
        # Final progress update
        await cache_service.update_preload_progress(
            session_key, total_requests, successful_requests, failed_requests
        )
        
        # Complete the session
        # Success if no actual failures (skipped requests don't count as failures)
        success = failed_requests == 0
        
        if success:
            logger.info(f"Comprehensive preload completed successfully: {successful_requests} successful, {skipped_requests} skipped, {failed_requests} failed")
            await cache_service.complete_preload_session(session_key, True, None)
        else:
            error_message = f"{failed_requests} requests failed (excluding {skipped_requests} skipped)"
            logger.warning(f"Comprehensive preload completed with errors: {successful_requests} successful, {skipped_requests} skipped, {failed_requests} failed")
            await cache_service.complete_preload_session(session_key, False, error_message)
        
        return {
            "message": "Comprehensive preload completed",
            "session_key": session_key,
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "success_rate": (successful_requests / total_requests) * 100 if total_requests > 0 else 0,
            "agencies_processed": len(agencies)
        }
        
    except Exception as e:
        logger.error(f"Error during comprehensive preload execution: {e}")
        raise HTTPException(status_code=500, detail=f"Comprehensive preload failed: {str(e)}")


@router.get("/preload/session/{session_key}")
async def get_preload_session_info(session_key: str):
    """
    Get information about a preload session.
    
    Args:
        session_key: Session key to query
        
    Returns:
        Session information including progress and status
    """
    try:
        cache_service = get_cache_service()
        session_info = await cache_service.get_preload_session_info(session_key)
        
        if not session_info:
            raise HTTPException(status_code=404, detail="Preload session not found")
        
        return session_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting preload session info for {session_key}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get session info: {str(e)}")


@router.put("/preload/session/{session_key}/progress")
async def update_preload_progress(
    session_key: str,
    total_requests: int = Query(..., description="Total number of requests"),
    successful_requests: int = Query(..., description="Number of successful requests"),
    failed_requests: int = Query(..., description="Number of failed requests")
):
    """
    Update preload session progress.
    
    Args:
        session_key: Session key to update
        total_requests: Total number of requests
        successful_requests: Number of successful requests
        failed_requests: Number of failed requests
    """
    try:
        cache_service = get_cache_service()
        
        success = await cache_service.update_preload_progress(
            session_key, total_requests, successful_requests, failed_requests
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Preload session not found")
        
        return {"message": "Progress updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating preload progress for {session_key}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update progress: {str(e)}")


@router.put("/preload/session/{session_key}/complete")
async def complete_preload_session(
    session_key: str,
    success: bool = Query(True, description="Whether the session completed successfully"),
    error_message: Optional[str] = Query(None, description="Optional error message if failed")
):
    """
    Mark preload session as completed or failed.
    
    Args:
        session_key: Session key to complete
        success: Whether the session completed successfully
        error_message: Optional error message if failed
    """
    try:
        cache_service = get_cache_service()
        
        result = await cache_service.complete_preload_session(session_key, success, error_message)
        
        if not result:
            raise HTTPException(status_code=404, detail="Preload session not found")
        
        return {
            "message": f"Session marked as {'completed' if success else 'failed'}",
            "success": success
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing preload session {session_key}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to complete session: {str(e)}")


@router.delete("/cleanup")
async def cleanup_expired_data():
    """
    Remove expired cache entries and clean up stuck sessions.
    
    Returns:
        Number of entries removed and sessions cleaned
    """
    try:
        cache_service = get_cache_service()
        
        # Clean expired cache entries
        deleted_count = await cache_service.cleanup_expired_data()
        
        # Clean up stuck preload sessions (running for more than 1 hour)
        async with cache_service.db_manager.get_async_session() as session:
            from datetime import datetime, timedelta
            from sqlalchemy import update, text
            
            # Update stuck sessions
            cutoff_time = datetime.utcnow() - timedelta(hours=1)
            result = await session.execute(
                text("""UPDATE preload_sessions 
                        SET status = 'failed', 
                            completed_at = datetime('now'),
                            error_message = 'Session timeout - automatically cleaned up'
                        WHERE status = 'running' 
                        AND started_at < :cutoff_time"""),
                {"cutoff_time": cutoff_time}
            )
            await session.commit()
            
            cleaned_sessions = result.rowcount
        
        return {
            "message": f"Cleanup completed",
            "deleted_entries": deleted_count,
            "cleaned_sessions": cleaned_sessions
        }
        
    except Exception as e:
        logger.error(f"Error during cache cleanup: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to cleanup cache: {str(e)}")


@router.post("/vacuum")
async def vacuum_database():
    """
    Optimize database by running VACUUM (SQLite only).
    This can help reduce database size and improve performance.
    """
    try:
        cache_service = get_cache_service()
        await cache_service.db_manager.vacuum_database()
        
        return {"message": "Database VACUUM completed successfully"}
        
    except Exception as e:
        logger.error(f"Error during database vacuum: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to vacuum database: {str(e)}")


@router.get("/data/{cache_key:path}")
async def get_cached_data_by_key(cache_key: str):
    """
    Get cached data by cache key.
    
    Args:
        cache_key: Cache key to lookup (URL path parameter, automatically decoded by FastAPI)
        
    Returns:
        Cached data or 404 if not found
    """
    try:
        # URL decode the cache key to handle encoded characters
        decoded_cache_key = unquote(cache_key)
        logger.info(f"Looking up cache key: '{cache_key}' -> decoded: '{decoded_cache_key}'")
        
        cache_service = get_cache_service()
        data = await cache_service.get_cached_data(decoded_cache_key)
        
        if data is None:
            logger.warning(f"Cache miss for decoded key: '{decoded_cache_key}'")
            raise HTTPException(status_code=404, detail="Cache entry not found or expired")
        
        return {
            "cache_key": decoded_cache_key,
            "data": data,
            "retrieved_at": "now"  # Could add actual retrieval timestamp
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting cached data for key {cache_key}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get cached data: {str(e)}")


@router.post("/save")
async def save_cached_data(cache_request: dict):
    """
    Save data to cache.
    
    Args:
        cache_request: Cache data to save including key, data, metadata
        
    Returns:
        Success confirmation
    """
    try:
        cache_service = get_cache_service()
        
        # Extract required fields
        cache_key = cache_request.get("cache_key")
        data = cache_request.get("data")
        endpoint = cache_request.get("endpoint")
        
        if not cache_key or not data or not endpoint:
            raise HTTPException(status_code=400, detail="Missing required fields: cache_key, data, endpoint")
        
        # Extract optional fields
        agency_id = cache_request.get("agency_id")
        time_period = cache_request.get("time_period")
        params = cache_request.get("params")
        expires_hours = cache_request.get("expires_hours", 24)
        is_preloaded = cache_request.get("is_preloaded", False)
        
        # Save to database cache
        success = await cache_service.save_cached_data(
            cache_key=cache_key,
            data=data,
            endpoint=endpoint,
            agency_id=agency_id,
            time_period=time_period,
            params=params,
            expires_hours=expires_hours,
            is_preloaded=is_preloaded
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save to cache")
        
        return {
            "message": "Data saved to cache successfully",
            "cache_key": cache_key,
            "expires_hours": expires_hours
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving cached data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save cached data: {str(e)}")