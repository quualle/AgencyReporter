from fastapi import APIRouter, Depends, HTTPException, Query as QueryParam
from typing import Dict, List, Optional, Any
from ..utils.query_manager import QueryManager
from ..utils.bigquery_connection import BigQueryConnection
from ..models import TimeFilter, AgencyRequest
from ..dependencies import get_settings
from ..services.database_cache_service import get_cache_service
from ..queries.quotas.quotas_with_reasons import GET_ALL_PROBLEM_CASES
from datetime import datetime, timedelta

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
        # Check cache first
        cache_service = get_cache_service()
        endpoint = f"/quotas_with_reasons/{agency_id}/cancellation-reasons"
        cache_key = cache_service.create_cache_key(endpoint, {"agency_id": agency_id, "time_period": time_period})
        cached_data = await cache_service.get_cached_data(cache_key)
        if cached_data is not None:
            return cached_data.get("data", cached_data)
        
        # Use the query manager to get quotas and related data
        query_manager = QueryManager()
        
        # For now, we'll return mock data
        # In the future, this will be connected to real LLM analysis
        result = {
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
        # Check cache first
        cache_service = get_cache_service()
        endpoint = f"/quotas_with_reasons/{agency_id}/early-end-reasons"
        cache_key = cache_service.create_cache_key(endpoint, {"agency_id": agency_id, "time_period": time_period})
        cached_data = await cache_service.get_cached_data(cache_key)
        if cached_data is not None:
            return cached_data.get("data", cached_data)
        
        # Use the query manager to get quotas and related data
        query_manager = QueryManager()
        
        # For now, we'll return mock data
        # In the future, this will be connected to real LLM analysis
        result = {
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
        raise HTTPException(status_code=500, detail=f"Failed to fetch early end reasons: {str(e)}")

@router.get("/{agency_id}/all-problem-cases")
async def get_all_problem_cases(
    agency_id: str,
    start_date: str = QueryParam(None),
    end_date: str = QueryParam(None),
    time_period: str = QueryParam("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$")
):
    """
    Get all problem cases (cancelled first stays, cancelled follow stays, shortened stays) for a specific agency
    """
    try:
        # Setup date range based on time_period or explicit start/end dates
        today = datetime.now()
        
        if not start_date:
            if time_period == "last_month":
                start_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")
            elif time_period == "last_quarter":
                start_date = (today - timedelta(days=90)).strftime("%Y-%m-%d")
            elif time_period == "last_year":
                start_date = (today - timedelta(days=365)).strftime("%Y-%m-%d")
            else:  # all_time
                start_date = "2020-01-01"  # Earliest relevant data
        
        if not end_date:
            end_date = today.strftime("%Y-%m-%d")
            
        # Use the query manager to execute the query
        query_manager = QueryManager()
        connection = BigQueryConnection()
        
        # Execute the query with parameters
        query_params = {
            "agency_id": agency_id,
            "start_date": start_date,
            "end_date": end_date
        }
        
        results = connection.execute_query(GET_ALL_PROBLEM_CASES, query_params)
        
        # Process and format the results
        problem_cases = []
        for row in results:
            problem_case = dict(row.items())
            problem_cases.append(problem_case)
            
        return {
            "agency_id": agency_id,
            "time_period": time_period,
            "start_date": start_date,
            "end_date": end_date,
            "problem_cases": problem_cases,
            "total_count": len(problem_cases)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch problem cases: {str(e)}")

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