from fastapi import APIRouter, Depends, HTTPException, Query as QueryParam
from typing import Dict, List, Optional, Any
from ..utils.query_manager import QueryManager
from ..utils.bigquery_connection import BigQueryConnection
from ..models import TimeFilter, AgencyRequest
from ..dependencies import get_settings

router = APIRouter()

@router.get("/{agency_id}/cancellation-reasons")
async def get_agency_cancellation_reasons(
    agency_id: str,
    time_period: str = QueryParam("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$")
):
    """
    Get cancellation reasons for a specific agency analyzed by LLM
    """
    try:
        # Use the query manager to get quotas and related data
        query_manager = QueryManager()
        
        # For now, we'll return mock data
        # In the future, this will be connected to real LLM analysis
        return {
            "agency_id": agency_id,
            "time_period": time_period,
            "cancellation_reasons": {
                "caregiver_unavailable": 5,
                "customer_dissatisfied": 3,
                "health_issues": 7,
                "communication_problems": 4,
                "administrative_issues": 2
            },
            "total_cancellations": 21
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch cancellation reasons: {str(e)}")

@router.get("/{agency_id}/early-end-reasons")
async def get_agency_early_end_reasons(
    agency_id: str,
    time_period: str = QueryParam("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$")
):
    """
    Get reasons for early ending of services for a specific agency analyzed by LLM
    """
    try:
        # Use the query manager to get quotas and related data
        query_manager = QueryManager()
        
        # For now, we'll return mock data
        # In the future, this will be connected to real LLM analysis
        return {
            "agency_id": agency_id,
            "time_period": time_period,
            "early_end_reasons": {
                "caregiver_health_issue": 8,
                "customer_conflict": 5,
                "better_opportunity": 3,
                "personal_emergency": 6,
                "compensation_dispute": 2
            },
            "total_early_ends": 24
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch early end reasons: {str(e)}")

@router.post("/custom-analysis")
async def get_custom_quota_analysis(request: Dict[str, Any]):
    """
    Get custom quota analysis with reasons based on request parameters
    """
    try:
        # Validate request
        agency_id = request.get("agency_id")
        if not agency_id:
            raise HTTPException(status_code=400, detail="agency_id is required")
            
        time_period = request.get("time_period", "last_quarter")
        analysis_type = request.get("analysis_type", "cancellation")
        
        # Return appropriate analysis based on type
        if analysis_type == "cancellation":
            return {
                "agency_id": agency_id,
                "time_period": time_period,
                "cancellation_reasons": {
                    "caregiver_unavailable": 5,
                    "customer_dissatisfied": 3,
                    "health_issues": 7,
                    "communication_problems": 4,
                    "administrative_issues": 2
                },
                "total_cancellations": 21
            }
        elif analysis_type == "early_end":
            return {
                "agency_id": agency_id,
                "time_period": time_period,
                "early_end_reasons": {
                    "caregiver_health_issue": 8,
                    "customer_conflict": 5,
                    "better_opportunity": 3,
                    "personal_emergency": 6,
                    "compensation_dispute": 2
                },
                "total_early_ends": 24
            }
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported analysis_type: {analysis_type}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to perform custom quota analysis: {str(e)}")