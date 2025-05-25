from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from ..utils.query_manager import QueryManager
from ..models import Agency, TimeFilter
from ..dependencies import get_settings
from ..services.database_cache_service import get_cache_service
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=List[Agency])
async def get_all_agencies():
    """
    Get a list of all agencies with database caching
    """
    cache_service = get_cache_service()
    endpoint = "/agencies"
    
    # Create cache key
    cache_key = cache_service.create_cache_key(endpoint)
    
    try:
        # Check cache first
        cached_data = await cache_service.get_cached_data(cache_key)
        if cached_data is not None:
            logger.info(f"Cache hit for agencies endpoint")
            return cached_data.get("data", cached_data)
        
        # Cache miss - fetch fresh data
        logger.info(f"Cache miss for agencies endpoint, fetching fresh data")
        query_manager = QueryManager()
        agencies = query_manager.get_all_agencies()
        
        # Save to cache (agencies data changes rarely, so cache for 48 hours)
        await cache_service.save_cached_data(
            cache_key=cache_key,
            data={"data": agencies, "count": len(agencies)},
            endpoint=endpoint,
            expires_hours=48  # Agencies change rarely
        )
        
        logger.info(f"Cached {len(agencies)} agencies for 48 hours")
        return agencies
        
    except Exception as e:
        logger.error(f"Error in get_all_agencies: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch agencies: {str(e)}")

@router.get("/{agency_id}", response_model=Agency)
async def get_agency(agency_id: str):
    """
    Get a specific agency by ID with database caching
    """
    cache_service = get_cache_service()
    endpoint = f"/agencies/{agency_id}"
    
    # Create cache key
    cache_key = cache_service.create_cache_key(endpoint)
    
    try:
        # Check cache first
        cached_data = await cache_service.get_cached_data(cache_key)
        if cached_data is not None:
            logger.info(f"Cache hit for agency {agency_id}")
            return cached_data.get("data", cached_data)
        
        # Cache miss - fetch fresh data
        logger.info(f"Cache miss for agency {agency_id}, fetching fresh data")
        query_manager = QueryManager()
        agency = query_manager.get_agency_details(agency_id)
        
        if not agency:
            raise HTTPException(status_code=404, detail=f"Agency with ID {agency_id} not found")
        
        # Save to cache (individual agency data changes rarely, cache for 24 hours)
        await cache_service.save_cached_data(
            cache_key=cache_key,
            data={"data": agency},
            endpoint=endpoint,
            agency_id=agency_id,
            expires_hours=24
        )
        
        logger.info(f"Cached agency {agency_id} for 24 hours")
        return agency
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_agency for {agency_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch agency: {str(e)}")

@router.post("/filter")
async def filter_agencies(time_filter: TimeFilter):
    """
    Filter agencies by time period with database caching
    """
    cache_service = get_cache_service()
    endpoint = "/agencies/filter"
    
    # Create cache key including time filter parameters
    params = {
        "time_period": time_filter.time_period,
        "start_date": time_filter.start_date.isoformat() if time_filter.start_date else None,
        "end_date": time_filter.end_date.isoformat() if time_filter.end_date else None
    }
    cache_key = cache_service.create_cache_key(endpoint, params)
    
    try:
        # Check cache first
        cached_data = await cache_service.get_cached_data(cache_key)
        if cached_data is not None:
            logger.info(f"Cache hit for agencies filter with time_period: {time_filter.time_period}")
            return cached_data.get("data", cached_data)
        
        # Cache miss - fetch fresh data
        logger.info(f"Cache miss for agencies filter, fetching fresh data")
        query_manager = QueryManager()
        # For now, we don't use the time filter for the agencies endpoint
        # but it's here for consistency with other endpoints
        agencies = query_manager.get_all_agencies()
        
        # Save to cache 
        await cache_service.save_cached_data(
            cache_key=cache_key,
            data={"data": agencies, "count": len(agencies)},
            endpoint=endpoint,
            time_period=time_filter.time_period,
            params=params,
            expires_hours=24
        )
        
        logger.info(f"Cached filtered agencies (time_period: {time_filter.time_period}) for 24 hours")
        return agencies
        
    except Exception as e:
        logger.error(f"Error in filter_agencies: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to filter agencies: {str(e)}")