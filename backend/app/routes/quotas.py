from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, List, Optional, Any
from ..utils.query_manager import QueryManager
from ..models import TimeFilter, AgencyRequest
from ..dependencies import get_settings
from ..services.database_cache_service import get_cache_service

router = APIRouter()

@router.get("/postings")
async def get_posting_metrics(
    time_period: str = Query("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$")
):
    """
    Get metrics for all postings
    """
    try:
        query_manager = QueryManager()
        posting_metrics = query_manager.get_posting_metrics(time_period=time_period)
        return posting_metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch posting metrics: {str(e)}")

@router.get("/{agency_id}/reservations")
async def get_agency_reservation_metrics(
    agency_id: str,
    time_period: str = Query("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$"),
    start_date: str = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(None, description="End date in YYYY-MM-DD format")
):
    """
    Get reservation metrics for a specific agency
    """
    try:
        query_manager = QueryManager()
        reservation_metrics = query_manager.get_agency_reservation_metrics(
            agency_id=agency_id,
            start_date=start_date,
            end_date=end_date,
            time_period=time_period
        )
        return reservation_metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch reservation metrics: {str(e)}")

@router.get("/{agency_id}/fulfillment", deprecated=True)
async def get_fulfillment_rate(
    agency_id: str,
    time_period: str = Query("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$")
):
    """
    [DEPRECATED] Use /{agency_id}/reservation-fulfillment instead.
    Get fulfillment rate for a specific agency
    (Quote 2: Anzahl Reservierungen - Anzahl erfüllte Reservierungen)
    """
    try:
        query_manager = QueryManager()
        fulfillment_metrics = query_manager.get_reservation_fulfillment_rate(
            agency_id=agency_id,
            time_period=time_period
        )
        return fulfillment_metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch fulfillment rate: {str(e)}")

@router.get("/{agency_id}/reservation-fulfillment")
async def get_reservation_fulfillment_rate(
    agency_id: str,
    time_period: str = Query("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$")
):
    """
    Get reservation fulfillment rate for a specific agency
    (Quote 2: Anzahl Reservierungen - Anzahl erfüllte Reservierungen)
    """
    try:
        query_manager = QueryManager()
        fulfillment_metrics = query_manager.get_fulfillment_rate(
            agency_id=agency_id,
            time_period=time_period
        )
        return fulfillment_metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch reservation fulfillment rate: {str(e)}")

@router.get("/{agency_id}/withdrawal")
async def get_withdrawal_rate(
    agency_id: str,
    time_period: str = Query("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$")
):
    """
    Get withdrawal rate for a specific agency
    (Quote 3: Anzahl Reservierungen - Anzahl abgebrochene Reservierungen)
    """
    try:
        query_manager = QueryManager()
        withdrawal_metrics = query_manager.get_withdrawal_rate(
            agency_id=agency_id,
            time_period=time_period
        )
        return withdrawal_metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch withdrawal rate: {str(e)}")

@router.get("/{agency_id}/pending")
async def get_pending_rate(
    agency_id: str,
    time_period: str = Query("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$")
):
    """
    Get pending rate for a specific agency
    (Quote 4: Anzahl Reservierungen - Anzahl reservierungen, die weder zurückgezogen noch erfüllt wurden)
    """
    try:
        query_manager = QueryManager()
        pending_metrics = query_manager.get_pending_rate(
            agency_id=agency_id,
            time_period=time_period
        )
        return pending_metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch pending rate: {str(e)}")

@router.get("/{agency_id}/arrival")
async def get_arrival_metrics(
    agency_id: str,
    time_period: str = Query("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$")
):
    """
    Get arrival metrics for a specific agency, differenziert nach Erst- und Folgeeinsätzen.
    Includes counts for different stages with the following flow:
    - All care stays (total)
    - First-time stays only (is_swap = false)
    - Follow-up stays only (is_swap = true)
    
    Stages follow this workflow:
    1. Reservation (reservation_fulfillment_count): Agentur reserviert einen freien Platz für ein Posting
    2. Personalvorschlag (pv_count): Care Stay wird erstellt mit Status "Neu" (jeder PV erzeugt einen Care Stay)
    3. "Vorgestellt": Status nach Vorstellung beim Kunden
    4. "Angenommen": Status nach Akzeptanz durch den Kunden (accepted_count)
    5. "Bestätigt": Status nach Bestätigung durch die Pflegekraft (confirmed_count)
    6. "Anreise": Tatsächliche Anreise, wenn nicht vorher abgebrochen (arrived_count)
    
    Notes:
    - For follow-up stays, reservation_fulfillment_count is always 0 as reservations are only possible for new postings
    - "PV count" counts all care stays (each care stay is a Personalvorschlag, regardless of status)
    - "Accepted" counts care stays that have reached status "Angenommen"
    - "Confirmed" counts care stays that have reached status "Bestätigt" (should be ≤ accepted)
    - "Arrived" counts care stays that have reached status "Bestätigt", have a valid arrival date, 
      and were NOT canceled before arrival (should be ≤ confirmed)
    
    Each category provides ratios between these stages, including the new pv_to_arrival_ratio.
    (Related to Quote 5)
    """
    try:
        query_manager = QueryManager()
        arrival_metrics = query_manager.get_arrival_metrics(
            agency_id=agency_id,
            time_period=time_period
        )
        return arrival_metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch arrival metrics: {str(e)}")

@router.get("/{agency_id}/cancellation-before-arrival")
async def get_cancellation_before_arrival_rate(
    agency_id: str,
    time_period: str = Query("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$")
):
    """
    Get cancellation before arrival rate for a specific agency
    (Quote 6: Anzahl gemachter Personalvorschläge - Anzahl VOR Einsatz abgebrochener Pflegeeinsätze)
    """
    try:
        # Check cache first
        cache_service = get_cache_service()
        endpoint = f"/quotas/{agency_id}/cancellation-before-arrival"
        cache_key = cache_service.create_cache_key(endpoint, {"time_period": time_period})
        cached_data = await cache_service.get_cached_data(cache_key)
        if cached_data is not None:
            return cached_data.get("data", cached_data)
        
        query_manager = QueryManager()
        cancellation_metrics = query_manager.get_cancellation_before_arrival_rate(
            agency_id=agency_id,
            time_period=time_period
        )
        
        # Save to cache
        await cache_service.save_cached_data(
            cache_key=cache_key,
            data={"data": cancellation_metrics},
            endpoint=endpoint,
            agency_id=agency_id,
            time_period=time_period,
            expires_hours=48
        )
        
        return cancellation_metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch cancellation before arrival rate: {str(e)}")

@router.get("/{agency_id}/completion")
async def get_completion_rate(
    agency_id: str,
    time_period: str = Query("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$")
):
    """
    Get completion rate for a specific agency
    (Quote 7: Pflegeeinsatz angetreten - Pflegeinsatz vollständig beendet)
    """
    try:
        query_manager = QueryManager()
        completion_metrics = query_manager.get_completion_rate(
            agency_id=agency_id,
            time_period=time_period
        )
        return completion_metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch completion rate: {str(e)}")

@router.get("/{agency_id}/all")
async def get_all_quotas(
    agency_id: str,
    time_period: str = Query("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$"),
    start_date: str = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(None, description="End date in YYYY-MM-DD format")
):
    """
    Get all quota metrics for a specific agency
    """
    try:
        # Check cache first
        cache_service = get_cache_service()
        endpoint = f"/quotas/{agency_id}/all"
        params = {"time_period": time_period}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        cache_key = cache_service.create_cache_key(endpoint, params)
        cached_data = await cache_service.get_cached_data(cache_key)
        if cached_data is not None:
            return cached_data.get("data", cached_data)
        
        query_manager = QueryManager()
        all_quotas = query_manager.get_all_quotas(
            agency_id=agency_id,
            start_date=start_date,
            end_date=end_date,
            time_period=time_period
        )
        
        # Save to cache
        await cache_service.save_cached_data(
            cache_key=cache_key,
            data={"data": all_quotas},
            endpoint=endpoint,
            agency_id=agency_id,
            time_period=time_period,
            expires_hours=48
        )
        
        return all_quotas
    except Exception as e:
        # Check if it's a specific timestamp error and provide a more helpful message
        error_msg = str(e)
        if "Invalid timestamp" in error_msg and "252024" in error_msg:
            raise HTTPException(
                status_code=400, 
                detail=f"Data quality issue: Invalid timestamp found in database. This agency may have corrupted date data. Please contact support."
            )
        raise HTTPException(status_code=500, detail=f"Failed to fetch all quotas: {error_msg}")

@router.post("/custom")
async def get_custom_metrics(request: Dict[str, Any]):
    """
    Get custom metrics based on request parameters
    """
    try:
        query_manager = QueryManager()
        
        agency_id = request.get("agency_id")
        time_period = request.get("time_period", "last_quarter")
        metrics_type = request.get("metrics_type", "reservations")
        
        if not agency_id:
            raise HTTPException(status_code=400, detail="agency_id is required")
        
        if metrics_type == "reservations":
            metrics = query_manager.get_agency_reservation_metrics(
                agency_id=agency_id,
                time_period=time_period
            )
        elif metrics_type == "fulfillment":
            # Deprecated but still supported for backwards compatibility
            metrics = query_manager.get_reservation_fulfillment_rate(
                agency_id=agency_id,
                time_period=time_period
            )
        elif metrics_type == "reservation-fulfillment":
            metrics = query_manager.get_reservation_fulfillment_rate(
                agency_id=agency_id,
                time_period=time_period
            )
        elif metrics_type == "withdrawal":
            metrics = query_manager.get_withdrawal_rate(
                agency_id=agency_id,
                time_period=time_period
            )
        elif metrics_type == "pending":
            metrics = query_manager.get_pending_rate(
                agency_id=agency_id,
                time_period=time_period
            )
        elif metrics_type == "arrival":
            metrics = query_manager.get_arrival_metrics(
                agency_id=agency_id,
                time_period=time_period
            )
        elif metrics_type == "cancellation":
            metrics = query_manager.get_cancellation_before_arrival_rate(
                agency_id=agency_id,
                time_period=time_period
            )
        elif metrics_type == "completion":
            metrics = query_manager.get_completion_rate(
                agency_id=agency_id,
                time_period=time_period
            )
        elif metrics_type == "all":
            metrics = query_manager.get_all_quotas(
                agency_id=agency_id,
                time_period=time_period
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported metrics_type: {metrics_type}")
        
        return metrics
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch custom metrics: {str(e)}")

@router.get("/stats/overall/cancellation-before-arrival")
async def get_overall_cancellation_stats(
    start_date: Optional[str] = Query(None, description="Startdatum im Format YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="Enddatum im Format YYYY-MM-DD"),
    time_period: str = Query("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$")
):
    """
    Get overall average cancellation before arrival stats across all agencies.
    """
    try:
        query_manager = QueryManager()
        stats = query_manager.get_overall_cancellation_before_arrival_stats(start_date, end_date, time_period)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch overall cancellation before arrival stats: {str(e)}")

@router.get("/all-agencies/conversion")
async def get_all_agencies_conversion_stats(
    time_period: str = Query("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$")
):
    """
    Get conversion performance (start rate and cancellation rate) for all agencies.
    Returns: agency_id, agency_name, start_rate, cancellation_rate, total_postings
    """
    try:
        # Check cache first
        cache_service = get_cache_service()
        endpoint = f"/quotas/all-agencies/conversion"
        cache_key = cache_service.create_cache_key(endpoint, {"time_period": time_period})
        cached_data = await cache_service.get_cached_data(cache_key)
        if cached_data is not None:
            return cached_data.get("data", cached_data)
        
        query_manager = QueryManager()
        conversion_stats = query_manager.get_all_agencies_conversion_stats(time_period)
        
        # Save to cache
        await cache_service.save_cached_data(
            cache_key=cache_key,
            data={"data": conversion_stats},
            endpoint=endpoint,
            agency_id=None,  # All agencies
            time_period=time_period
        )
        
        return conversion_stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch all agencies conversion stats: {str(e)}")


# Include other routers if necessary
# from . import other_router
# router.include_router(other_router.router)