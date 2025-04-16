from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from ..utils.query_manager import QueryManager
from ..models import Agency, TimeFilter
from ..dependencies import get_settings

router = APIRouter()

@router.get("/", response_model=List[Agency])
async def get_all_agencies():
    """
    Get a list of all agencies
    """
    try:
        query_manager = QueryManager()
        agencies = query_manager.get_all_agencies()
        return agencies
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch agencies: {str(e)}")

@router.get("/{agency_id}", response_model=Agency)
async def get_agency(agency_id: str):
    """
    Get a specific agency by ID
    """
    try:
        query_manager = QueryManager()
        agency = query_manager.get_agency_details(agency_id)
        
        if not agency:
            raise HTTPException(status_code=404, detail=f"Agency with ID {agency_id} not found")
        
        return agency
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch agency: {str(e)}")

@router.post("/filter")
async def filter_agencies(time_filter: TimeFilter):
    """
    Filter agencies by time period
    """
    try:
        query_manager = QueryManager()
        # For now, we don't use the time filter for the agencies endpoint
        # but it's here for consistency with other endpoints
        agencies = query_manager.get_all_agencies()
        return agencies
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to filter agencies: {str(e)}")