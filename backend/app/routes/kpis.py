from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from ..utils.bigquery_connection import BigQueryConnection
from ..models import KPIData, TimeFilter, AgencyRequest, AgencyComparison
from ..dependencies import get_settings
import statistics

router = APIRouter()

@router.get("/{agency_id}", response_model=KPIData)
async def get_agency_kpis(
    agency_id: str, 
    time_period: str = Query("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$")
):
    """
    Get KPIs for a specific agency
    """
    try:
        bq = BigQueryConnection()
        kpi_data = bq.get_kpis_by_agency(agency_id, time_period)
        
        # If no data is found
        if not kpi_data:
            return KPIData(agency_id=agency_id)
        
        return kpi_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch KPIs: {str(e)}")

@router.post("/filter")
async def filter_kpis(time_filter: TimeFilter):
    """
    Get KPIs for all agencies based on time filter
    """
    try:
        bq = BigQueryConnection()
        all_kpis = bq.get_all_agencies_kpis(time_filter.time_period)
        return all_kpis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to filter KPIs: {str(e)}")

@router.post("/compare", response_model=AgencyComparison)
async def compare_agency_kpis(request: AgencyRequest):
    """
    Compare KPIs for a specific agency with all other agencies
    """
    try:
        bq = BigQueryConnection()
        
        # Get data for all agencies
        all_agencies_data = bq.get_all_agencies_kpis(request.time_period)
        
        # Find the selected agency
        selected_agency = None
        for agency in all_agencies_data:
            if agency.get("agency_id") == request.agency_id:
                selected_agency = agency
                break
        
        # If the selected agency is not found in the results
        if not selected_agency:
            # Try to get it separately
            selected_agency = bq.get_kpis_by_agency(request.agency_id, request.time_period)
            
            # If still not found, create an empty record
            if not selected_agency:
                selected_agency = {"agency_id": request.agency_id}
        
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
        raise HTTPException(status_code=500, detail=f"Failed to compare KPIs: {str(e)}")

def _calculate_industry_average(agencies_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate industry average KPIs from a list of agency data
    """
    # If no data, return empty record
    if not agencies_data:
        return {"agency_id": "industry_average"}
    
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
    averages = {}
    for key in sums:
        if counts[key] > 0:
            averages[key] = sums[key] / counts[key]
        else:
            averages[key] = 0
    
    return averages 