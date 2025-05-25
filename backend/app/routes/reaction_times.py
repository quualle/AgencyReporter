from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from ..utils.bigquery_connection import BigQueryConnection
from ..models import ResponseTimeData as ReactionTimeData, TimeFilter, AgencyRequest, ResponseTimeComparison as ReactionTimeComparison
from ..dependencies import get_settings
from ..utils.query_manager import QueryManager
from ..services.database_cache_service import get_cache_service

router = APIRouter()

@router.get("/{agency_id}", response_model=ReactionTimeData)
async def get_agency_reaction_times(
    agency_id: str, 
    time_period: str = Query("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$")
):
    """
    Get reaction times for a specific agency
    """
    try:
        # Check cache first
        cache_service = get_cache_service()
        endpoint = f"/reaction_times/{agency_id}"
        cache_key = cache_service.create_cache_key(endpoint, {"time_period": time_period})
        cached_data = await cache_service.get_cached_data(cache_key)
        if cached_data is not None:
            cached_result = cached_data.get("data", cached_data)
            # Convert dict to ReactionTimeData if needed
            if isinstance(cached_result, dict):
                return ReactionTimeData(**cached_result)
            return cached_result
        
        bq = BigQueryConnection()
        reaction_time_data = bq.get_response_times_by_agency(agency_id, time_period)
        
        # If no data is found
        if not reaction_time_data:
            reaction_time_data = ReactionTimeData(agency_id=agency_id)
        
        # Save to cache (convert to dict for serialization)
        data_dict = reaction_time_data.dict() if hasattr(reaction_time_data, 'dict') else reaction_time_data
        await cache_service.save_cached_data(
            cache_key=cache_key,
            data={"data": data_dict},
            endpoint=endpoint,
            agency_id=agency_id,
            time_period=time_period,
            expires_hours=48
        )
        
        return reaction_time_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch reaction times: {str(e)}")

@router.post("/filter")
async def filter_reaction_times(time_filter: TimeFilter):
    """
    Get reaction times for all agencies based on time filter
    """
    try:
        bq = BigQueryConnection()
        # This is a placeholder until we implement the actual method in BigQueryConnection
        # For now, we'll return an empty list
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to filter reaction times: {str(e)}")

@router.post("/compare", response_model=ReactionTimeComparison)
async def compare_agency_reaction_times(request: AgencyRequest):
    """
    Compare reaction times for a specific agency with all other agencies
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
        raise HTTPException(status_code=500, detail=f"Failed to compare reaction times: {str(e)}")

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

@router.get("/{agency_id}/posting_to_reservation")
async def get_posting_to_reservation_stats(
    agency_id: str,
    start_date: Optional[str] = Query(None, description="Startdatum im Format YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="Enddatum im Format YYYY-MM-DD"),
    time_period: str = Query("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$")
):
    """
    Median und Durchschnitt (in Stunden) von Posting bis Reservierung für eine Agentur
    """
    try:
        bq = BigQueryConnection()
        if not start_date or not end_date:
            from ..utils.query_manager import QueryManager
            qm = QueryManager()
            start_date, end_date = qm._calculate_date_range(time_period)
        stats = bq.get_posting_to_reservation_stats(agency_id, start_date, end_date)
        median_hours = stats["median_hours"]
        avg_hours = stats["avg_hours"]
        return {
            "agency_id": agency_id,
            "median_hours": f"{median_hours:.2f}" if median_hours is not None else None,
            "avg_hours": f"{avg_hours:.2f}" if avg_hours is not None else None,
            "start_date": start_date,
            "end_date": end_date
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch posting_to_reservation stats: {str(e)}")

@router.get("/{agency_id}/reservation_to_first_proposal")
async def get_reservation_to_first_proposal_stats(
    agency_id: str,
    start_date: Optional[str] = Query(None, description="Startdatum im Format YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="Enddatum im Format YYYY-MM-DD"),
    time_period: str = Query("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$")
):
    """
    Median und Durchschnitt (in Stunden) von Reservierung bis zum ersten Personalvorschlag (CareStay) für eine Agentur
    """
    try:
        bq = BigQueryConnection()
        if not start_date or not end_date:
            from ..utils.query_manager import QueryManager
            qm = QueryManager()
            start_date, end_date = qm._calculate_date_range(time_period)
        stats = bq.get_reservation_to_first_proposal_stats(agency_id, start_date, end_date)
        median_hours = stats["median_hours"]
        avg_hours = stats["avg_hours"]
        return {
            "agency_id": agency_id,
            "median_hours": f"{median_hours:.2f}" if median_hours is not None else None,
            "avg_hours": f"{avg_hours:.2f}" if avg_hours is not None else None,
            "start_date": start_date,
            "end_date": end_date
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch reservation_to_first_proposal stats: {str(e)}")

@router.get("/{agency_id}/proposal_to_cancellation")
async def get_proposal_to_cancellation_stats(
    agency_id: str,
    start_date: Optional[str] = Query(None, description="Startdatum im Format YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="Enddatum im Format YYYY-MM-DD"),
    time_period: str = Query("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$")
):
    """
    Median und Durchschnitt (in Stunden) von Personalvorschlag (presented_at) bis Abbruch (vor Anreise) für abgebrochene CareStays
    """
    try:
        bq = BigQueryConnection()
        if not start_date or not end_date:
            from ..utils.query_manager import QueryManager
            qm = QueryManager()
            start_date, end_date = qm._calculate_date_range(time_period)
        stats = bq.get_proposal_to_cancellation_stats(agency_id, start_date, end_date)
        median_hours = stats["median_hours"]
        avg_hours = stats["avg_hours"]
        return {
            "agency_id": agency_id,
            "median_hours": f"{median_hours:.2f}" if median_hours is not None else None,
            "avg_hours": f"{avg_hours:.2f}" if avg_hours is not None else None,
            "start_date": start_date,
            "end_date": end_date
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch proposal_to_cancellation stats: {str(e)}")

@router.get("/{agency_id}/arrival_to_cancellation")
async def get_arrival_to_cancellation_stats(
    agency_id: str,
    start_date: Optional[str] = Query(None, description="Startdatum im Format YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="Enddatum im Format YYYY-MM-DD"),
    time_period: str = Query("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$")
):
    """
    Median und Durchschnitt (in Stunden) von geplanter Anreise (arrival) bis Abbruch (vor Anreise) für abgebrochene CareStays
    Aufgeteilt in: overall, first_stays (Neukunden), followup_stays (Wechsel)
    """
    try:
        # Check cache first
        cache_service = get_cache_service()
        endpoint = f"/reaction_times/{agency_id}/arrival_to_cancellation"
        params = {"time_period": time_period}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        cache_key = cache_service.create_cache_key(endpoint, params)
        cached_data = await cache_service.get_cached_data(cache_key)
        if cached_data is not None:
            return cached_data.get("data", cached_data)
        
        bq = BigQueryConnection()
        if not start_date or not end_date:
            from ..utils.query_manager import QueryManager
            qm = QueryManager()
            start_date, end_date = qm._calculate_date_range(time_period)
        stats = bq.get_arrival_to_cancellation_stats(agency_id, start_date, end_date)
        def fmt(val):
            return f"{val:.2f}" if val is not None else None
        
        result = {
            "agency_id": agency_id,
            "overall": {
                "median_hours": fmt(stats["overall"]["median_hours"]) if stats["overall"] else None,
                "avg_hours": fmt(stats["overall"]["avg_hours"]) if stats["overall"] else None
            },
            "first_stays": {
                "median_hours": fmt(stats["first_stays"]["median_hours"]) if stats["first_stays"] else None,
                "avg_hours": fmt(stats["first_stays"]["avg_hours"]) if stats["first_stays"] else None
            },
            "followup_stays": {
                "median_hours": fmt(stats["followup_stays"]["median_hours"]) if stats["followup_stays"] else None,
                "avg_hours": fmt(stats["followup_stays"]["avg_hours"]) if stats["followup_stays"] else None
            },
            "start_date": start_date,
            "end_date": end_date
        }
        
        # Save to cache
        await cache_service.save_cached_data(
            cache_key=cache_key,
            data={"data": result},
            endpoint=endpoint,
            agency_id=agency_id,
            time_period=time_period,
            expires_hours=48
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch arrival_to_cancellation stats: {str(e)}")

# --- Endpoints for Overall Reaction Time Stats --- 

@router.get("/stats/overall/posting_to_reservation")
async def get_overall_posting_to_reservation_stats(
    start_date: Optional[str] = Query(None, description="Startdatum im Format YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="Enddatum im Format YYYY-MM-DD"),
    time_period: str = Query("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$")
):
    """
    Median und Durchschnitt (in Stunden) von Posting bis Reservierung für ALLE Agenturen
    """
    try:
        qm = QueryManager()
        stats = qm.get_overall_posting_to_reservation_stats(start_date, end_date, time_period)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch overall posting_to_reservation stats: {str(e)}")

@router.get("/stats/overall/reservation_to_first_proposal")
async def get_overall_reservation_to_first_proposal_stats(
    start_date: Optional[str] = Query(None, description="Startdatum im Format YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="Enddatum im Format YYYY-MM-DD"),
    time_period: str = Query("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$")
):
    """
    Median und Durchschnitt (in Stunden) von Reservierung bis erstem Vorschlag für ALLE Agenturen
    """
    try:
        qm = QueryManager()
        stats = qm.get_overall_reservation_to_first_proposal_stats(start_date, end_date, time_period)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch overall reservation_to_first_proposal stats: {str(e)}")

@router.get("/stats/overall/proposal_to_cancellation")
async def get_overall_proposal_to_cancellation_stats(
    start_date: Optional[str] = Query(None, description="Startdatum im Format YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="Enddatum im Format YYYY-MM-DD"),
    time_period: str = Query("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$")
):
    """
    Median und Durchschnitt (in Stunden) von Vorschlag bis Abbruch (vor Anreise) für ALLE Agenturen
    """
    try:
        qm = QueryManager()
        stats = qm.get_overall_proposal_to_cancellation_stats(start_date, end_date, time_period)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch overall proposal_to_cancellation stats: {str(e)}")

@router.get("/stats/overall/arrival_to_cancellation")
async def get_overall_arrival_to_cancellation_stats(
    start_date: Optional[str] = Query(None, description="Startdatum im Format YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="Enddatum im Format YYYY-MM-DD"),
    time_period: str = Query("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$")
):
    """
    Median und Durchschnitt (in Stunden) von Anreise bis Abbruch (vor Anreise) für ALLE Agenturen (inkl. Buckets)
    """
    try:
        qm = QueryManager()
        stats = qm.get_overall_arrival_to_cancellation_stats(start_date, end_date, time_period)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch overall arrival_to_cancellation stats: {str(e)}") 