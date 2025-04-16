from fastapi import APIRouter, Depends, HTTPException, Query as QueryParam
from typing import Dict, List, Optional, Any
from ..utils.query_manager import QueryManager
from ..models import TimeFilter, AgencyRequest
from ..dependencies import get_settings

router = APIRouter()

@router.get("/postings")
async def get_posting_metrics(
    time_period: str = QueryParam("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$")
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
    time_period: str = QueryParam("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$")
):
    """
    Get reservation metrics for a specific agency
    """
    try:
        query_manager = QueryManager()
        reservation_metrics = query_manager.get_agency_reservation_metrics(
            agency_id=agency_id,
            time_period=time_period
        )
        return reservation_metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch reservation metrics: {str(e)}")

@router.get("/{agency_id}/fulfillment")
async def get_fulfillment_rate(
    agency_id: str,
    time_period: str = QueryParam("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$")
):
    """
    Get fulfillment rate for a specific agency
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
        raise HTTPException(status_code=500, detail=f"Failed to fetch fulfillment rate: {str(e)}")

@router.get("/{agency_id}/withdrawal")
async def get_withdrawal_rate(
    agency_id: str,
    time_period: str = QueryParam("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$")
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
    time_period: str = QueryParam("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$")
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
async def get_arrival_rate(
    agency_id: str,
    time_period: str = QueryParam("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$")
):
    """
    Get arrival rate for a specific agency
    (Quote 5: Reservierung mit Personalvorschlag erfüllt - Pflegeeinsatz angetreten)
    """
    try:
        query_manager = QueryManager()
        arrival_metrics = query_manager.get_arrival_rate(
            agency_id=agency_id,
            time_period=time_period
        )
        return arrival_metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch arrival rate: {str(e)}")

@router.get("/{agency_id}/cancellation-before-arrival")
async def get_cancellation_before_arrival_rate(
    agency_id: str,
    time_period: str = QueryParam("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$")
):
    """
    Get cancellation before arrival rate for a specific agency
    (Quote 6: Anzahl gemachter Personalvorschläge - Anzahl VOR Einsatz abgebrochener Pflegeeinsätze)
    """
    try:
        query_manager = QueryManager()
        cancellation_metrics = query_manager.get_cancellation_before_arrival_rate(
            agency_id=agency_id,
            time_period=time_period
        )
        return cancellation_metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch cancellation before arrival rate: {str(e)}")

@router.get("/{agency_id}/completion")
async def get_completion_rate(
    agency_id: str,
    time_period: str = QueryParam("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$")
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
    time_period: str = QueryParam("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$")
):
    """
    Get all quota metrics for a specific agency
    """
    try:
        query_manager = QueryManager()
        all_quotas = query_manager.get_all_quotas(
            agency_id=agency_id,
            time_period=time_period
        )
        return all_quotas
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch all quotas: {str(e)}")

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
            metrics = query_manager.get_fulfillment_rate(
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
            metrics = query_manager.get_arrival_rate(
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