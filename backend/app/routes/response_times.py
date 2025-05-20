from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from ..utils.bigquery_connection import BigQueryConnection
from ..models import ResponseTimeData, TimeFilter, AgencyRequest, ResponseTimeComparison
from ..dependencies import get_settings

router = APIRouter()

@router.get("/{agency_id}", response_model=ResponseTimeData)
async def get_agency_response_times(
    agency_id: str, 
    time_period: str = Query("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$")
):
    """
    Get response times for a specific agency
    """
    try:
        bq = BigQueryConnection()
        response_time_data = bq.get_response_times_by_agency(agency_id, time_period)
        
        # If no data is found
        if not response_time_data:
            return ResponseTimeData(agency_id=agency_id)
        
        return response_time_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch response times: {str(e)}")

@router.post("/filter")
async def filter_response_times(time_filter: TimeFilter):
    """
    Get response times for all agencies based on time filter
    """
    try:
        bq = BigQueryConnection()
        # This is a placeholder until we implement the actual method in BigQueryConnection
        # For now, we'll return an empty list
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to filter response times: {str(e)}")

@router.post("/compare", response_model=ResponseTimeComparison)
async def compare_agency_response_times(request: AgencyRequest):
    """
    Compare response times for a specific agency with all other agencies
    """
    try:
        bq = BigQueryConnection()
        
        # Get data for the selected agency
        selected_agency = bq.get_response_times_by_agency(request.agency_id, request.time_period)
        
        # If no data is found for the selected agency
        if not selected_agency:
            selected_agency = {"agency_id": request.agency_id}
        
        # For now, we'll use placeholder data for all agencies
        # In a real implementation, we would fetch data for all agencies
        all_agencies_data = []
        
        # Calculate industry averages
        industry_average = _calculate_industry_average(all_agencies_data)
        
        # Ensure the agency_id is set for the industry average
        industry_average["agency_id"] = "industry_average"
        industry_average["agency_name"] = "Industry Average"
        
        # Create response
        response = {
            "selected_agency": selected_agency,
            "all_agencies": all_agencies_data,
            "industry_average": industry_average
        }
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to compare response times: {str(e)}")

def _calculate_industry_average(agencies_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate industry average response times from a list of agency data
    """
    # If no data, return empty record
    if not agencies_data:
        return {
            "agency_id": "industry_average",
            "avg_time_to_reservation": 0.0,
            "avg_time_to_proposal": 0.0,
            "avg_time_to_cancellation": 0.0,
            "avg_time_before_start": 0.0,
            "avg_time_to_any_cancellation": 0.0
        }
    
    # Initialize dictionary for sums
    sums = {}
    counts = {}
    
    # Sum values for each numeric field
    for agency in agencies_data:
        for key, value in agency.items():
            # Skip non-numeric fields and None values
            if key in ["agency_id", "agency_name"] or value is None:
                continue
            
            try:
                # Convert to float to handle both int and float
                numeric_value = float(value)
                
                # Add to sums
                if key not in sums:
                    sums[key] = 0
                    counts[key] = 0
                
                sums[key] += numeric_value
                counts[key] += 1
            except (ValueError, TypeError):
                # Skip if value cannot be converted to float
                continue
    
    # Calculate averages
    averages = {"agency_id": "industry_average"}
    for key in sums:
        if counts[key] > 0:
            averages[key] = sums[key] / counts[key]
        else:
            averages[key] = 0
    
    return averages 