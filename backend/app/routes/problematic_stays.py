from fastapi import APIRouter, Depends, HTTPException, Query as QueryParam
from typing import Dict, List, Optional, Any
from ..utils.query_manager import QueryManager
from ..utils.bigquery_connection import BigQueryConnection
from ..models import TimeFilter, AgencyRequest
from ..dependencies import get_settings
from ..queries.problematic_stays.queries import (
    GET_PROBLEMATIC_STAYS_OVERVIEW,
    GET_PROBLEMATIC_STAYS_REASONS,
    GET_PROBLEMATIC_STAYS_TIME_ANALYSIS
)
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/overview")
async def get_problematic_stays_overview(
    agency_id: Optional[str] = QueryParam(None),
    time_period: str = QueryParam("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$")
):
    """
    Übersichtsstatistiken zu problematischen Pflegeeinsätzen.
    Liefert aggregierte Daten zu abgebrochenen und verkürzten Einsätzen mit Aufschlüsselung nach
    Event-Typ, Stay-Typ, Ersatzstellungen und Kundenzufriedenheit.
    """
    try:
        # Setup date range based on time_period
        today = datetime.now()
        
        if time_period == "last_month":
            start_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")
        elif time_period == "last_quarter":
            start_date = (today - timedelta(days=90)).strftime("%Y-%m-%d")
        elif time_period == "last_year":
            start_date = (today - timedelta(days=365)).strftime("%Y-%m-%d")
        else:  # all_time
            start_date = "2020-01-01"  # Earliest relevant data
            
        end_date = today.strftime("%Y-%m-%d")
        
        # Execute the query with parameters
        connection = BigQueryConnection()
        query_params = {
            "agency_id": agency_id,
            "start_date": start_date,
            "end_date": end_date
        }
        
        results = connection.execute_query(GET_PROBLEMATIC_STAYS_OVERVIEW, query_params)
        
        # Process and format the results
        if not results or len(results) == 0:
            # Return empty results if no data found
            return {
                "agency_id": agency_id,
                "time_period": time_period,
                "start_date": start_date,
                "end_date": end_date,
                "data": [],
                "count": 0
            }
        
        # Process the results into a list of dictionaries
        overview_data = []
        for row in results:
            # Convert BigQuery row to dictionary
            overview_item = dict(row.items())
            # Round float values for better readability
            for key, value in overview_item.items():
                if isinstance(value, float):
                    overview_item[key] = round(value, 2)
            overview_data.append(overview_item)
            
        return {
            "agency_id": agency_id,
            "time_period": time_period,
            "start_date": start_date,
            "end_date": end_date,
            "data": overview_data,
            "count": len(overview_data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch problematic stays overview: {str(e)}")

@router.get("/reasons")
async def get_problematic_stays_reasons(
    agency_id: Optional[str] = QueryParam(None),
    event_type: Optional[str] = QueryParam(None, regex="^(cancelled_before_arrival|shortened_after_arrival|)$"),
    time_period: str = QueryParam("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$")
):
    """
    Analyse der Gründe für problematische Pflegeeinsätze.
    Extrahiert Gründe aus der JSON-Spalte analysis_result und liefert Häufigkeitsverteilungen.
    """
    try:
        # Setup date range based on time_period
        today = datetime.now()
        
        if time_period == "last_month":
            start_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")
        elif time_period == "last_quarter":
            start_date = (today - timedelta(days=90)).strftime("%Y-%m-%d")
        elif time_period == "last_year":
            start_date = (today - timedelta(days=365)).strftime("%Y-%m-%d")
        else:  # all_time
            start_date = "2020-01-01"  # Earliest relevant data
            
        end_date = today.strftime("%Y-%m-%d")
        
        # Execute the query with parameters
        connection = BigQueryConnection()
        query_params = {
            "agency_id": agency_id,
            "event_type": event_type,
            "start_date": start_date,
            "end_date": end_date
        }
        
        results = connection.execute_query(GET_PROBLEMATIC_STAYS_REASONS, query_params)
        
        # Process and format the results
        if not results or len(results) == 0:
            # Return empty results if no data found
            return {
                "agency_id": agency_id,
                "event_type": event_type,
                "time_period": time_period,
                "start_date": start_date,
                "end_date": end_date,
                "data": [],
                "count": 0
            }
        
        # Process the results into a list of dictionaries
        reasons_data = []
        for row in results:
            # Convert BigQuery row to dictionary
            reason_item = dict(row.items())
            # Round float values for better readability
            for key, value in reason_item.items():
                if isinstance(value, float):
                    reason_item[key] = round(value, 2)
            reasons_data.append(reason_item)
            
        return {
            "agency_id": agency_id,
            "event_type": event_type,
            "time_period": time_period,
            "start_date": start_date,
            "end_date": end_date,
            "data": reasons_data,
            "count": len(reasons_data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch problematic stays reasons: {str(e)}")

@router.get("/time-analysis")
async def get_problematic_stays_time_analysis(
    agency_id: Optional[str] = QueryParam(None),
    event_type: Optional[str] = QueryParam(None, regex="^(cancelled_before_arrival|shortened_after_arrival|)$"),
    stay_type: Optional[str] = QueryParam(None, regex="^(first_stay|follow_stay|)$"),
    time_period: str = QueryParam("last_year", regex="^(last_quarter|last_month|last_year|all_time)$")
):
    """
    Zeitliche Analyse der problematischen Pflegeeinsätze.
    Gruppiert Daten nach Monaten und liefert Trends über Zeit.
    """
    try:
        # Setup date range based on time_period
        today = datetime.now()
        
        if time_period == "last_month":
            start_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")
        elif time_period == "last_quarter":
            start_date = (today - timedelta(days=90)).strftime("%Y-%m-%d")
        elif time_period == "last_year":
            start_date = (today - timedelta(days=365)).strftime("%Y-%m-%d")
        else:  # all_time
            start_date = "2020-01-01"  # Earliest relevant data
            
        end_date = today.strftime("%Y-%m-%d")
        
        # Execute the query with parameters
        connection = BigQueryConnection()
        query_params = {
            "agency_id": agency_id,
            "event_type": event_type,
            "stay_type": stay_type,
            "start_date": start_date,
            "end_date": end_date
        }
        
        results = connection.execute_query(GET_PROBLEMATIC_STAYS_TIME_ANALYSIS, query_params)
        
        # Process and format the results
        if not results or len(results) == 0:
            # Return empty results if no data found
            return {
                "agency_id": agency_id,
                "event_type": event_type,
                "stay_type": stay_type,
                "time_period": time_period,
                "start_date": start_date,
                "end_date": end_date,
                "data": [],
                "count": 0
            }
        
        # Process the results into a list of dictionaries
        time_data = []
        for row in results:
            # Convert BigQuery row to dictionary
            time_item = dict(row.items())
            # Round float values for better readability
            for key, value in time_item.items():
                if isinstance(value, float):
                    time_item[key] = round(value, 2)
            time_data.append(time_item)
            
        return {
            "agency_id": agency_id,
            "event_type": event_type,
            "stay_type": stay_type,
            "time_period": time_period,
            "start_date": start_date,
            "end_date": end_date,
            "data": time_data,
            "count": len(time_data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch problematic stays time analysis: {str(e)}")

@router.get("/{agency_id}/detailed")
async def get_problematic_stays_detailed(
    agency_id: str,
    event_type: Optional[str] = QueryParam(None, regex="^(cancelled_before_arrival|shortened_after_arrival|)$"),
    stay_type: Optional[str] = QueryParam(None, regex="^(first_stay|follow_stay|)$"),
    time_period: str = QueryParam("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$"),
    limit: int = QueryParam(50, ge=1, le=1000)
):
    """
    Detaillierte Daten zu einzelnen problematischen Pflegeeinsätzen einer Agentur.
    Liefert Rohdaten mit Pagination für detaillierte Analysen oder Tabellenansichten.
    """
    try:
        # Setup date range based on time_period
        today = datetime.now()
        
        if time_period == "last_month":
            start_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")
        elif time_period == "last_quarter":
            start_date = (today - timedelta(days=90)).strftime("%Y-%m-%d")
        elif time_period == "last_year":
            start_date = (today - timedelta(days=365)).strftime("%Y-%m-%d")
        else:  # all_time
            start_date = "2020-01-01"  # Earliest relevant data
            
        end_date = today.strftime("%Y-%m-%d")
        
        # For now, we return a more basic query directly
        query = f"""
        SELECT
          care_stay_id,
          agency_id,
          agency_name,
          stay_type,
          event_type,
          event_date,
          arrival_date,
          original_departure_date,
          new_departure_date,
          days_difference,
          has_replacement,
          has_follow_up,
          instant_departure_after,
          JSON_EXTRACT_SCALAR(analysis_result, '$.selected_reason') AS reason,
          CAST(JSON_EXTRACT_SCALAR(analysis_result, '$.confidence') AS INT64) AS confidence,
          JSON_EXTRACT_SCALAR(analysis_result, '$.customer_satisfaction') AS customer_satisfaction,
          JSON_EXTRACT_SCALAR(analysis_result, '$.comment') AS comment,
          analysis_timestamp
        FROM
          `gcpxbixpflegehilfesenioren.Agencyreporter.problematic_stays`
        WHERE
          analysis_status = 'completed'
          AND agency_id = @agency_id
          {f"AND event_type = @event_type" if event_type else ""}
          {f"AND stay_type = @stay_type" if stay_type else ""}
          AND event_date BETWEEN @start_date AND @end_date
        ORDER BY
          event_date DESC
        LIMIT {limit}
        """
        
        # Execute the query with parameters
        connection = BigQueryConnection()
        query_params = {
            "agency_id": agency_id,
            "event_type": event_type,
            "stay_type": stay_type,
            "start_date": start_date,
            "end_date": end_date
        }
        
        results = connection.execute_query(query, query_params)
        
        # Process and format the results
        detailed_data = []
        for row in results:
            # Convert BigQuery row to dictionary
            detail_item = dict(row.items())
            # Convert timestamp to ISO format string
            if 'analysis_timestamp' in detail_item and detail_item['analysis_timestamp']:
                detail_item['analysis_timestamp'] = detail_item['analysis_timestamp'].isoformat()
            detailed_data.append(detail_item)
            
        return {
            "agency_id": agency_id,
            "event_type": event_type,
            "stay_type": stay_type,
            "time_period": time_period,
            "start_date": start_date,
            "end_date": end_date,
            "data": detailed_data,
            "count": len(detailed_data),
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch detailed problematic stays: {str(e)}") 