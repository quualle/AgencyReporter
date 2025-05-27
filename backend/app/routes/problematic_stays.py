from fastapi import APIRouter, Depends, HTTPException, Query as QueryParam
from typing import Dict, List, Optional, Any
from ..utils.query_manager import QueryManager
from ..utils.bigquery_connection import BigQueryConnection
from ..models import TimeFilter, AgencyRequest
from ..dependencies import get_settings
from ..services.database_cache_service import get_cache_service
from ..utils.cache_decorator import cache_endpoint
from ..queries.problematic_stays.queries import (
    GET_PROBLEMATIC_STAYS_OVERVIEW,
    GET_PROBLEMATIC_STAYS_REASONS,
    GET_PROBLEMATIC_STAYS_TIME_ANALYSIS,
    GET_PROBLEMATIC_STAYS_HEATMAP,
    GET_PROBLEMATIC_STAYS_INSTANT_DEPARTURES,
    GET_PROBLEMATIC_STAYS_REPLACEMENT_ANALYSIS,
    GET_PROBLEMATIC_STAYS_CUSTOMER_SATISFACTION,
    GET_PROBLEMATIC_STAYS_TREND_ANALYSIS
)
from datetime import datetime, timedelta
import random  # Für Demo-Daten
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/overview")
@cache_endpoint(ttl_hours=24, key_params=['agency_id', 'time_period'], cache_key_prefix="/problematic_stays/overview")
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
            result = {
                "agency_id": agency_id,
                "time_period": time_period,
                "start_date": start_date,
                "end_date": end_date,
                "data": [],
                "count": 0
            }
        else:
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
                
            result = {
                "agency_id": agency_id,
                "time_period": time_period,
                "start_date": start_date,
                "end_date": end_date,
                "data": overview_data,
                "count": len(overview_data)
            }
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch problematic stays overview: {str(e)}")

@router.get("/reasons")
@cache_endpoint(ttl_hours=24, key_params=['agency_id', 'event_type', 'time_period'], cache_key_prefix="/problematic_stays/reasons")
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
@cache_endpoint(ttl_hours=24, key_params=['agency_id', 'event_type', 'stay_type', 'time_period'], cache_key_prefix="/problematic-stays/time-analysis")
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
@cache_endpoint(ttl_hours=24, key_params=['agency_id', 'event_type', 'stay_type', 'time_period', 'limit'], cache_key_prefix="/problematic-stays/detailed")
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
          `gcpxbixpflegehilfesenioren.AgencyReporter.problematic_stays`
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

@router.get("/heatmap")
@cache_endpoint(ttl_hours=24, key_params=['agency_id', 'event_type', 'stay_type', 'time_period'], cache_key_prefix="/problematic-stays/heatmap")
async def get_problematic_stays_heatmap(
    agency_id: Optional[str] = QueryParam(None),
    event_type: Optional[str] = QueryParam(None, regex="^(cancelled_before_arrival|shortened_after_arrival|)$"),
    stay_type: Optional[str] = QueryParam(None, regex="^(first_stay|follow_stay|)$"),
    time_period: str = QueryParam("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$")
):
    """
    Heatmap-Analyse der Abbruchgründe nach Agentur.
    Liefert eine Übersicht der Häufigkeit verschiedener Abbruchgründe gruppiert nach Agenturen.
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
        
        results = connection.execute_query(GET_PROBLEMATIC_STAYS_HEATMAP, query_params)
        
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
        heatmap_data = []
        for row in results:
            # Convert BigQuery row to dictionary
            heatmap_item = dict(row.items())
            # Round float values for better readability
            for key, value in heatmap_item.items():
                if isinstance(value, float):
                    heatmap_item[key] = round(value, 2)
            heatmap_data.append(heatmap_item)
            
        return {
            "agency_id": agency_id,
            "event_type": event_type,
            "stay_type": stay_type,
            "time_period": time_period,
            "start_date": start_date,
            "end_date": end_date,
            "data": heatmap_data,
            "count": len(heatmap_data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch problematic stays heatmap: {str(e)}")

@router.get("/instant-departures")
@cache_endpoint(ttl_hours=24, key_params=['agency_id', 'time_period'], cache_key_prefix="/problematic-stays/instant-departures")
async def get_problematic_stays_instant_departures(
    agency_id: Optional[str] = QueryParam(None),
    time_period: str = QueryParam("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$")
):
    """
    Analyse der sofortigen Abreisen (< 10 Tage nach Anreise).
    Liefert detaillierte Informationen zu Einsätzen, die innerhalb von 10 Tagen nach Anreise beendet wurden.
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
        
        results = connection.execute_query(GET_PROBLEMATIC_STAYS_INSTANT_DEPARTURES, query_params)
        
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
        departures_data = []
        for row in results:
            # Convert BigQuery row to dictionary
            departure_item = dict(row.items())
            # Round float values for better readability
            for key, value in departure_item.items():
                if isinstance(value, float):
                    departure_item[key] = round(value, 2)
            departures_data.append(departure_item)
            
        return {
            "agency_id": agency_id,
            "time_period": time_period,
            "start_date": start_date,
            "end_date": end_date,
            "data": departures_data,
            "count": len(departures_data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch problematic stays instant departures: {str(e)}")

@router.get("/replacement-analysis")
@cache_endpoint(ttl_hours=24, key_params=['agency_id', 'time_period'], cache_key_prefix="/problematic-stays/replacement-analysis")
async def get_problematic_stays_replacement_analysis(
    agency_id: Optional[str] = QueryParam(None),
    time_period: str = QueryParam("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$")
):
    """
    Analyse der Ersatz- und Folgestatistiken.
    Liefert Informationen darüber, wie oft Ersatz für abgebrochene Einsätze oder Folgeeinsätze
    für verkürzte Einsätze gestellt werden.
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
        
        results = connection.execute_query(GET_PROBLEMATIC_STAYS_REPLACEMENT_ANALYSIS, query_params)
        
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
        replacement_data = []
        for row in results:
            # Convert BigQuery row to dictionary
            replacement_item = dict(row.items())
            # Round float values for better readability
            for key, value in replacement_item.items():
                if isinstance(value, float):
                    replacement_item[key] = round(value, 2)
            replacement_data.append(replacement_item)
            
        return {
            "agency_id": agency_id,
            "time_period": time_period,
            "start_date": start_date,
            "end_date": end_date,
            "data": replacement_data,
            "count": len(replacement_data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch problematic stays replacement analysis: {str(e)}")

@router.get("/customer-satisfaction")
@cache_endpoint(ttl_hours=24, key_params=['agency_id', 'time_period'], cache_key_prefix="/problematic-stays/customer-satisfaction")
async def get_problematic_stays_customer_satisfaction(
    agency_id: Optional[str] = QueryParam(None),
    time_period: str = QueryParam("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$")
):
    """
    Analyse der Kundenzufriedenheit bei problematischen Einsätzen.
    Liefert Informationen zur Verteilung der Kundenzufriedenheit und deren
    Zusammenhang mit Abbruchgründen.
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
        
        results = connection.execute_query(GET_PROBLEMATIC_STAYS_CUSTOMER_SATISFACTION, query_params)
        
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
        satisfaction_data = []
        for row in results:
            # Convert BigQuery row to dictionary
            satisfaction_item = dict(row.items())
            # Round float values for better readability
            for key, value in satisfaction_item.items():
                if isinstance(value, float):
                    satisfaction_item[key] = round(value, 2)
            satisfaction_data.append(satisfaction_item)
            
        return {
            "agency_id": agency_id,
            "time_period": time_period,
            "start_date": start_date,
            "end_date": end_date,
            "data": satisfaction_data,
            "count": len(satisfaction_data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch problematic stays customer satisfaction: {str(e)}")

@router.get("/trend-analysis")
@cache_endpoint(ttl_hours=24, key_params=['agency_id', 'event_type', 'stay_type', 'time_period'], cache_key_prefix="/problematic-stays/trend-analysis")
async def get_problematic_stays_trend_analysis(
    agency_id: Optional[str] = QueryParam(None),
    event_type: Optional[str] = QueryParam(None, regex="^(cancelled_before_arrival|shortened_after_arrival|)$"),
    stay_type: Optional[str] = QueryParam(None, regex="^(first_stay|follow_stay|)$"),
    time_period: str = QueryParam("last_year", regex="^(last_quarter|last_month|last_year|all_time)$")
):
    """
    Zeitliche Trendanalyse der problematischen Einsätze.
    Liefert Informationen zur monatlichen Entwicklung problematischer Einsätze über Zeit.
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
        
        results = connection.execute_query(GET_PROBLEMATIC_STAYS_TREND_ANALYSIS, query_params)
        
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
        trend_data = []
        for row in results:
            # Convert BigQuery row to dictionary
            trend_item = dict(row.items())
            # Round float values for better readability
            for key, value in trend_item.items():
                if isinstance(value, float):
                    trend_item[key] = round(value, 2)
            trend_data.append(trend_item)
            
        return {
            "agency_id": agency_id,
            "event_type": event_type,
            "stay_type": stay_type,
            "time_period": time_period,
            "start_date": start_date,
            "end_date": end_date,
            "data": trend_data,
            "count": len(trend_data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch problematic stays trend analysis: {str(e)}")

@router.get("/cancellation-lead-time")
@cache_endpoint(ttl_hours=24, key_params=['agency_id', 'time_period'], cache_key_prefix="/problematic-stays/cancellation-lead-time")
async def get_problematic_stays_cancellation_lead_time(
    agency_id: Optional[str] = QueryParam(None),
    time_period: str = QueryParam("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$")
):
    """
    Analyse der Vorlaufzeiten bei Abbrüchen vor der Anreise.
    Liefert Informationen zur Verteilung der Vorlaufzeiten (Tage vor geplantem Einsatzbeginn)
    und den häufigsten Abbruchgründen je Vorlaufzeitkategorie.
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
        
        # Demo-Daten für die Entwicklung 
        # Später durch echte Query ersetzen
        
        # Häufige Abbruchgründe
        reasons = [
            "Erkrankung Pflegekraft", 
            "Stornierung durch Kunde", 
            "Betreuungssituation geändert", 
            "Kunde im Krankenhaus", 
            "Pflegekraft kurzfristig verhindert",
            "Veränderte Anforderungen",
            "Andere Lösung gefunden",
            "Finanzielle Gründe"
        ]
        
        # Erstelle Demo-Daten für verschiedene Vorlaufzeiten
        demo_data = []
        for reason in reasons:
            # Jeder Grund hat verschiedene Vorlaufzeiten
            for _ in range(random.randint(5, 15)):
                # Zufällige Vorlaufzeit zwischen 0 und 120 Tagen
                days_before = random.choice([
                    # Häufige Werte (0-7 Tage)
                    0, 1, 2, 3, 4, 5, 6, 7,
                    # Mittlere Werte (1-4 Wochen)
                    10, 14, 21, 28,
                    # Längere Vorlaufzeiten
                    35, 42, 56, 70, 90, 120
                ])
                
                # Anzahl der Fälle (gewichtet zugunsten von Gründen am Anfang der Liste)
                count = random.randint(1, max(1, 20 - reasons.index(reason) * 2))
                
                demo_data.append({
                    "reason": reason,
                    "days_before_arrival": days_before,
                    "count": count
                })
        
        return {
            "agency_id": agency_id,
            "time_period": time_period,
            "start_date": start_date,
            "end_date": end_date,
            "data": demo_data,
            "count": len(demo_data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch cancellation lead time data: {str(e)}")


@router.get("/details/{agency_id}")
@cache_endpoint(ttl_hours=24, key_params=['agency_id', 'time_period', 'event_type'], cache_key_prefix="/problematic-stays/details")
async def get_problematic_stays_details(
    agency_id: str,
    time_period: str = QueryParam("last_quarter", description="Time period filter"),
    event_type: Optional[str] = QueryParam(None, description="Filter by event type (early_end, instant_departure, before_3_days)")
):
    """
    Get detailed list of individual problematic stays for an agency.
    Returns individual care stay records with customer info, dates, and reasons.
    """
    try:
        # Calculate date range
        today = datetime.today()
        if time_period == "last_month":
            start_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")
        elif time_period == "last_quarter":
            start_date = (today - timedelta(days=90)).strftime("%Y-%m-%d")
        elif time_period == "last_year":
            start_date = (today - timedelta(days=365)).strftime("%Y-%m-%d")
        else:  # all_time
            start_date = "2020-01-01"
            
        end_date = today.strftime("%Y-%m-%d")
        
        # Build query based on event type
        base_query = """
        WITH problematic_details AS (
            SELECT
                cs._id as care_stay_id,
                cs.created_at,
                cs.arrival,
                cs.departure,
                cs.stage,
                -- Extract cancellation info from tracks
                (SELECT TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at'))
                 FROM UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track
                 WHERE JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Abgebrochen'
                 ORDER BY JSON_EXTRACT_SCALAR(track, '$.created_at') DESC
                 LIMIT 1) as cancelled_at,
                cs.rejection_reason as cancellation_reason,
                cs.updated_at as ended_at,
                cs.rejection_reason as end_reason,
                c.customer_name,
                c.customer_city,
                c.agency_id,
                a.name as agency_name,
                -- Determine problematic type
                CASE
                    WHEN cs.stage = 'Abgebrochen' 
                         AND cs.cancelled_at IS NOT NULL 
                         AND cs.arrival IS NOT NULL 
                         AND DATE(cs.cancelled_at) < DATE(cs.arrival) THEN 'Abbruch vor Anreise'
                    WHEN cs.ended_at IS NOT NULL 
                         AND cs.arrival IS NOT NULL 
                         AND cs.departure IS NOT NULL
                         AND DATE_DIFF(DATE(cs.departure), DATE(cs.arrival), DAY) <= 3 THEN 'Sofortabreise (≤3 Tage)'
                    WHEN cs.ended_at IS NOT NULL 
                         AND cs.arrival IS NOT NULL 
                         AND cs.departure IS NOT NULL
                         AND cs.ended_at < cs.departure THEN 'Vorzeitige Beendigung'
                    ELSE 'Andere'
                END as problem_type,
                -- Calculate duration if applicable
                CASE
                    WHEN cs.arrival IS NOT NULL AND cs.departure IS NOT NULL
                    THEN DATE_DIFF(DATE(cs.departure), DATE(cs.arrival), DAY)
                    ELSE NULL
                END as stay_duration_days
            FROM
                `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs
            JOIN
                `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.contracts` c ON cs.contract_id = c._id
            JOIN
                `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.agencies` a ON c.agency_id = a._id
            WHERE
                c.agency_id = @agency_id
                AND cs.created_at BETWEEN @start_date AND @end_date
                AND (
                    -- Include based on problem type
                    -- Abbruch vor Anreise
                    (cs.stage = 'Abgebrochen' AND cs.arrival IS NOT NULL 
                     AND EXISTS (
                        SELECT 1
                        FROM UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track
                        WHERE JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Abgebrochen'
                          AND TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at')) < TIMESTAMP(cs.arrival)
                     ))
                    -- Sofortabreise (≤3 Tage)
                    OR (cs.arrival IS NOT NULL AND cs.departure IS NOT NULL 
                        AND DATE_DIFF(DATE(cs.departure), DATE(cs.arrival), DAY) <= 3)
                    -- Vorzeitige Beendigung
                    OR (cs.arrival IS NOT NULL AND cs.departure IS NOT NULL 
                        AND cs.departure < cs.arrival) -- This will be filtered later in the query
                )
        )
        SELECT * FROM problematic_details
        """
        
        # Add event type filter if specified
        if event_type:
            if event_type == "before_3_days":
                base_query += " WHERE problem_type = 'Sofortabreise (≤3 Tage)'"
            elif event_type == "early_end":
                base_query += " WHERE problem_type = 'Vorzeitige Beendigung'"
            elif event_type == "instant_departure":
                base_query += " WHERE problem_type = 'Abbruch vor Anreise'"
                
        base_query += " ORDER BY created_at DESC"
        
        # Execute query
        connection = BigQueryConnection()
        query_params = {
            "agency_id": agency_id,
            "start_date": start_date,
            "end_date": end_date
        }
        
        results = connection.execute_query(base_query, query_params)
        
        # Format results
        details = []
        for row in results:
            detail = {
                "care_stay_id": row.get("care_stay_id"),
                "customer_name": row.get("customer_name"),
                "customer_city": row.get("customer_city"),
                "problem_type": row.get("problem_type"),
                "created_at": row.get("created_at").isoformat() if row.get("created_at") else None,
                "arrival": row.get("arrival").isoformat() if row.get("arrival") else None,
                "departure": row.get("departure").isoformat() if row.get("departure") else None,
                "cancelled_at": row.get("cancelled_at").isoformat() if row.get("cancelled_at") else None,
                "ended_at": row.get("ended_at").isoformat() if row.get("ended_at") else None,
                "cancellation_reason": row.get("cancellation_reason"),
                "end_reason": row.get("end_reason"),
                "stay_duration_days": row.get("stay_duration_days"),
                "stage": row.get("stage")
            }
            details.append(detail)
        
        # Group by month for better organization
        from collections import defaultdict
        grouped_by_month = defaultdict(list)
        
        for detail in details:
            # Extract month from created_at
            if detail["created_at"]:
                month_key = detail["created_at"][:7]  # YYYY-MM
                grouped_by_month[month_key].append(detail)
        
        # Convert to sorted list
        grouped_data = []
        for month in sorted(grouped_by_month.keys(), reverse=True):
            grouped_data.append({
                "month": month,
                "count": len(grouped_by_month[month]),
                "stays": grouped_by_month[month]
            })
        
        return {
            "agency_id": agency_id,
            "agency_name": results[0].get("agency_name") if results else "Unknown",
            "time_period": time_period,
            "event_type": event_type,
            "total_count": len(details),
            "grouped_by_month": grouped_data
        }
        
    except Exception as e:
        logger.error(f"Error fetching problematic stays details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") 