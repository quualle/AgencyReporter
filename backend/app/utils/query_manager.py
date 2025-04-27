"""
Query Manager module for loading and executing BigQuery queries.
This centralizes the handling of SQL queries across the application.
"""

from typing import Dict, List, Any, Optional, Union
import logging
import os
import importlib
from datetime import datetime, timedelta
from ..dependencies import get_settings, get_bigquery_client
from .bigquery_connection import BigQueryConnection

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QueryManager:
    """
    A class to manage BigQuery queries, including loading, executing, and caching.
    """
    
    def __init__(self):
        """
        Initialize the QueryManager
        """
        self.bq_connection = BigQueryConnection()
        self.query_cache = {}  # Simple in-memory cache for query results
        self.queries = {}  # Dictionary to store loaded queries
        
        # Load all queries
        self._load_queries()
    
    def _load_queries(self):
        """
        Load all query modules and store their queries
        """
        try:
            # Load agency queries
            from ..queries.agencies import agencies
            self.queries.update({
                "GET_ALL_AGENCIES": agencies.GET_ALL_AGENCIES,
                "GET_AGENCY_DETAILS": agencies.GET_AGENCY_DETAILS
            })
            
            # Load quota queries
            from ..queries.quotas import quotas
            self.queries.update({
                # Quote 1: Gesamtzahl Stellen - Reservierungen getätigt
                "GET_TOTAL_POSTINGS": quotas.GET_TOTAL_POSTINGS,
                "GET_AGENCY_RESERVATIONS": quotas.GET_AGENCY_RESERVATIONS,
                
                # Quote 2: Anzahl Reservierungen - Anzahl erfüllte Reservierungen
                "GET_FULFILLED_RESERVATIONS": quotas.GET_FULFILLED_RESERVATIONS,
                
                # Quote 3: Anzahl Reservierungen - Anzahl abgebrochene Reservierungen
                "GET_WITHDRAWN_RESERVATIONS": quotas.GET_WITHDRAWN_RESERVATIONS,
                
                # Quote 4: Anzahl Reservierungen - Anzahl pending Reservierungen
                "GET_PENDING_RESERVATIONS": quotas.GET_PENDING_RESERVATIONS,
                
                # Quote 5: Erfüllte Reservierungen - Pflegeeinsatz angetreten
                "GET_STARTED_CARE_STAYS": quotas.GET_STARTED_CARE_STAYS,
                "GET_STARTED_FIRST_CARE_STAYS": quotas.GET_STARTED_FIRST_CARE_STAYS,
                
                # Quote 6: Personalvorschläge - VOR Anreise abgebrochene
                "GET_PERSONNEL_PROPOSALS": quotas.GET_PERSONNEL_PROPOSALS,
                "GET_CANCELLED_BEFORE_ARRIVAL": quotas.GET_CANCELLED_BEFORE_ARRIVAL,
                
                # Quote 7: Pflegeeinsatz angetreten - vollständig beendet
                "GET_COMPLETED_CARE_STAYS": quotas.GET_COMPLETED_CARE_STAYS,
                # Neue Query für Overall Stats hinzufügen
                "GET_OVERALL_CANCELLED_BEFORE_ARRIVAL_STATS": quotas.GET_OVERALL_CANCELLED_BEFORE_ARRIVAL_STATS
            })
            
            # Load reaction time queries
            from ..queries.reaction_times import reaction_times
            self.queries.update({
                "TIME_POSTING_TO_RESERVATION_STATS": reaction_times.TIME_POSTING_TO_RESERVATION_STATS,
                "TIME_RESERVATION_TO_FIRST_PROPOSAL_STATS": reaction_times.TIME_RESERVATION_TO_FIRST_PROPOSAL_STATS,
                "TIME_PROPOSAL_TO_CANCELLATION_STATS": reaction_times.TIME_PROPOSAL_TO_CANCELLATION_STATS,
                "TIME_ARRIVAL_TO_CANCELLATION_STATS": reaction_times.TIME_ARRIVAL_TO_CANCELLATION_STATS,
                # Overall Stats
                "TIME_POSTING_TO_RESERVATION_STATS_OVERALL": reaction_times.TIME_POSTING_TO_RESERVATION_STATS_OVERALL,
                "TIME_RESERVATION_TO_FIRST_PROPOSAL_STATS_OVERALL": reaction_times.TIME_RESERVATION_TO_FIRST_PROPOSAL_STATS_OVERALL,
                "TIME_PROPOSAL_TO_CANCELLATION_STATS_OVERALL": reaction_times.TIME_PROPOSAL_TO_CANCELLATION_STATS_OVERALL,
                "TIME_ARRIVAL_TO_CANCELLATION_STATS_OVERALL": reaction_times.TIME_ARRIVAL_TO_CANCELLATION_STATS_OVERALL
            })
            
            # Load profile quality queries (to be added when provided)
            # from ..queries.profile_quality import profile_quality
            
            # Load LLM analysis queries (to be added when provided)
            # from ..queries.llm_analysis import llm_analysis
            
            logger.info(f"Loaded {len(self.queries)} queries successfully")
        except Exception as e:
            logger.error(f"Error loading queries: {str(e)}")
            raise
    
    def execute_query(self, query_name: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a named query with optional parameters
        
        Args:
            query_name (str): The name of the query to execute
            params (dict, optional): Parameters for the query
            
        Returns:
            list: List of dictionaries with query results
        """
        if query_name not in self.queries:
            raise ValueError(f"Query '{query_name}' not found")
        
        query = self.queries[query_name]
        
        # Check cache if applicable
        cache_key = f"{query_name}:{str(params)}"
        if cache_key in self.query_cache:
            return self.query_cache[cache_key]
        
        # Execute query through BigQuery connection
        results = self.bq_connection.execute_query(query, params)
        
        # Store in cache (simple implementation, can be improved)
        self.query_cache[cache_key] = results
        
        return results
    
    def get_all_agencies(self) -> List[Dict[str, Any]]:
        """
        Get a list of all agencies
        
        Returns:
            list: List of dictionaries with agency information
        """
        return self.execute_query("GET_ALL_AGENCIES")
    
    def get_agency_details(self, agency_id: str) -> Dict[str, Any]:
        """
        Get details for a specific agency
        
        Args:
            agency_id (str): The ID of the agency
            
        Returns:
            dict: Dictionary with agency details
        """
        results = self.execute_query("GET_AGENCY_DETAILS", {"agency_id": agency_id})
        return results[0] if results else {}
    
    def get_posting_metrics(self, start_date: str = None, end_date: str = None, time_period: str = "last_quarter") -> Dict[str, Any]:
        """
        Get metrics for postings and reservations
        
        Args:
            start_date (str, optional): Start date in 'YYYY-MM-DD' format
            end_date (str, optional): End date in 'YYYY-MM-DD' format
            time_period (str, optional): Predefined time period (last_quarter, last_month, etc.)
            
        Returns:
            dict: Dictionary with posting metrics
        """
        # Calculate date range if not provided
        if not start_date or not end_date:
            start_date, end_date = self._calculate_date_range(time_period)
        
        # Get total postings
        posting_results = self.execute_query("GET_TOTAL_POSTINGS", {
            "start_date": start_date,
            "end_date": end_date
        })
        
        return posting_results[0] if posting_results else {"posting_count": 0}
    
    def get_agency_reservation_metrics(self, agency_id: str, start_date: str = None, end_date: str = None, time_period: str = "last_quarter") -> Dict[str, Any]:
        """
        Get reservation metrics for a specific agency
        
        Args:
            agency_id (str): The ID of the agency
            start_date (str, optional): Start date in 'YYYY-MM-DD' format
            end_date (str, optional): End date in 'YYYY-MM-DD' format
            time_period (str, optional): Predefined time period (last_quarter, last_month, etc.)
            
        Returns:
            dict: Dictionary with reservation metrics
        """
        # Calculate date range if not provided
        if not start_date or not end_date:
            start_date, end_date = self._calculate_date_range(time_period)
        
        # Get agency reservations
        reservation_results = self.execute_query("GET_AGENCY_RESERVATIONS", {
            "agency_id": agency_id,
            "start_date": start_date,
            "end_date": end_date
        })
        
        # Calculate posting-to-reservation ratio
        posting_metrics = self.get_posting_metrics(start_date, end_date)
        reservation_count = reservation_results[0]["anzahl_reservierungen"] if reservation_results else 0
        posting_count = posting_metrics.get("posting_count", 0)
        
        ratio = 0
        if posting_count > 0:
            ratio = reservation_count / posting_count
        
        result = {
            "agency_id": agency_id,
            "reservation_count": reservation_count,
            "total_posting_count": posting_count,
            "posting_to_reservation_ratio": ratio,
            "ratio_percentage": f"{ratio * 100:.1f}%",
            "name": "Reservierungsrate",
            "description": "Zeigt bei wie viel % der gesamt verfügbaren Stellen die Agentur eine Reservierung gemacht hat"
        }
        
        if reservation_results:
            result["agency_name"] = reservation_results[0]["agency_name"]
        
        return result
        
    def get_fulfillment_rate(self, agency_id: str, start_date: str = None, end_date: str = None, time_period: str = "last_quarter") -> Dict[str, Any]:
        """
        Quote 2: Anzahl Reservierungen - Anzahl erfüllte Reservierungen
        Zeigt wie viel % Ihrer Reservierungen die Agentur schlussendlich auch mit einem BK Vorschlag erfüllt hat
        
        Args:
            agency_id (str): The ID of the agency
            start_date (str, optional): Start date in 'YYYY-MM-DD' format
            end_date (str, optional): End date in 'YYYY-MM-DD' format
            time_period (str, optional): Predefined time period (last_quarter, last_month, etc.)
            
        Returns:
            dict: Dictionary with fulfillment metrics
        """
        # Calculate date range if not provided
        if not start_date or not end_date:
            start_date, end_date = self._calculate_date_range(time_period)
        
        # Get reservations for this agency
        reservation_results = self.execute_query("GET_AGENCY_RESERVATIONS", {
            "agency_id": agency_id,
            "start_date": start_date,
            "end_date": end_date
        })
        
        # Get fulfilled reservations for this agency
        fulfilled_results = self.execute_query("GET_FULFILLED_RESERVATIONS", {
            "agency_id": agency_id,
            "start_date": start_date,
            "end_date": end_date
        })
        
        # Calculate fulfillment rate
        reservation_count = reservation_results[0]["anzahl_reservierungen"] if reservation_results else 0
        fulfilled_count = fulfilled_results[0]["fulfilled_reservations_count"] if fulfilled_results else 0
        
        ratio = 0
        if reservation_count > 0:
            ratio = fulfilled_count / reservation_count
        
        agency_name = None
        if reservation_results:
            agency_name = reservation_results[0]["agency_name"]
        elif fulfilled_results:
            agency_name = fulfilled_results[0]["agency_name"]
        
        return {
            "agency_id": agency_id,
            "agency_name": agency_name,
            "reservation_count": reservation_count,
            "fulfilled_count": fulfilled_count,
            "fulfillment_ratio": ratio,
            "ratio_percentage": f"{ratio * 100:.1f}%",
            "name": "Erfüllungsrate",
            "description": "Zeigt wie viel % Ihrer Reservierungen die Agentur schlussendlich auch mit einem BK Vorschlag erfüllt hat"
        }
        
    def get_withdrawal_rate(self, agency_id: str, start_date: str = None, end_date: str = None, time_period: str = "last_quarter") -> Dict[str, Any]:
        """
        Quote 3: Anzahl Reservierungen - Anzahl abgebrochene Reservierungen
        Zeigt wie viel % ihrer eigenen Reservierungen die Agentur selbstständig abgebrochen hat
        
        Args:
            agency_id (str): The ID of the agency
            start_date (str, optional): Start date in 'YYYY-MM-DD' format
            end_date (str, optional): End date in 'YYYY-MM-DD' format
            time_period (str, optional): Predefined time period (last_quarter, last_month, etc.)
            
        Returns:
            dict: Dictionary with withdrawal metrics
        """
        # Calculate date range if not provided
        if not start_date or not end_date:
            start_date, end_date = self._calculate_date_range(time_period)
        
        # Get reservations for this agency
        reservation_results = self.execute_query("GET_AGENCY_RESERVATIONS", {
            "agency_id": agency_id,
            "start_date": start_date,
            "end_date": end_date
        })
        
        # Get withdrawn reservations for this agency
        withdrawn_results = self.execute_query("GET_WITHDRAWN_RESERVATIONS", {
            "agency_id": agency_id,
            "start_date": start_date,
            "end_date": end_date
        })
        
        # Calculate withdrawal rate
        reservation_count = reservation_results[0]["anzahl_reservierungen"] if reservation_results else 0
        withdrawn_count = withdrawn_results[0]["withdrawn_reservations_count"] if withdrawn_results else 0
        
        ratio = 0
        if reservation_count > 0:
            ratio = withdrawn_count / reservation_count
        
        agency_name = None
        if reservation_results:
            agency_name = reservation_results[0]["agency_name"]
        elif withdrawn_results:
            agency_name = withdrawn_results[0]["agency_name"]
        
        return {
            "agency_id": agency_id,
            "agency_name": agency_name,
            "reservation_count": reservation_count,
            "withdrawn_count": withdrawn_count,
            "withdrawal_ratio": ratio,
            "ratio_percentage": f"{ratio * 100:.1f}%",
            "name": "Abbruchrate",
            "description": "Zeigt wie viel % ihrer eigenen Reservierungen die Agentur selbstständig abgebrochen hat. Besser als nicht abzubrechen und einfach liegen zu lassen!"
        }
        
    def get_pending_rate(self, agency_id: str, start_date: str = None, end_date: str = None, time_period: str = "last_quarter") -> Dict[str, Any]:
        """
        Quote 4: Anzahl Reservierungen - Anzahl reservierungen, die weder zurückgezogen noch erfüllt wurden
        Zeigt, wie viele % der reservierungen, die eine Agentur getätigt hat, dannach weder zurückgezogen noch erfüllt wurden
        
        Args:
            agency_id (str): The ID of the agency
            start_date (str, optional): Start date in 'YYYY-MM-DD' format
            end_date (str, optional): End date in 'YYYY-MM-DD' format
            time_period (str, optional): Predefined time period (last_quarter, last_month, etc.)
            
        Returns:
            dict: Dictionary with pending metrics
        """
        # Calculate date range if not provided
        if not start_date or not end_date:
            start_date, end_date = self._calculate_date_range(time_period)
        
        # Get reservations for this agency
        reservation_results = self.execute_query("GET_AGENCY_RESERVATIONS", {
            "agency_id": agency_id,
            "start_date": start_date,
            "end_date": end_date
        })
        
        # Get pending reservations for this agency
        pending_results = self.execute_query("GET_PENDING_RESERVATIONS", {
            "agency_id": agency_id,
            "start_date": start_date,
            "end_date": end_date
        })
        
        # Calculate pending rate
        reservation_count = reservation_results[0]["anzahl_reservierungen"] if reservation_results else 0
        pending_count = pending_results[0]["pending_reservations_count"] if pending_results else 0
        
        ratio = 0
        if reservation_count > 0:
            ratio = pending_count / reservation_count
        
        agency_name = None
        if reservation_results:
            agency_name = reservation_results[0]["agency_name"]
        elif pending_results:
            agency_name = pending_results[0]["agency_name"]
        
        return {
            "agency_id": agency_id,
            "agency_name": agency_name,
            "reservation_count": reservation_count,
            "pending_count": pending_count,
            "pending_ratio": ratio,
            "ratio_percentage": f"{ratio * 100:.1f}%",
            "name": "Offene Reservierungsrate",
            "description": "Zeigt, wie viele % der reservierungen, die eine Agentur getätigt hat, dannach weder zurückgezogen noch erfüllt wurden - also einfach liegen gelassen!"
        }
        
    def get_arrival_rate(self, agency_id: str, start_date: str = None, end_date: str = None, time_period: str = "last_quarter") -> Dict[str, Any]:
        """
        Quote 5: Reservierung mit Personalvorschlag erfüllt - Pflegeeinsatz angetreten
        Zeigt wie viel % der vorgeschlagenen Pflegekräfte schlussendlich auch wirklich angereist sind
        
        Args:
            agency_id (str): The ID of the agency
            start_date (str, optional): Start date in 'YYYY-MM-DD' format
            end_date (str, optional): End date in 'YYYY-MM-DD' format
            time_period (str, optional): Predefined time period (last_quarter, last_month, etc.)
            
        Returns:
            dict: Dictionary with arrival metrics
        """
        # Calculate date range if not provided
        if not start_date or not end_date:
            start_date, end_date = self._calculate_date_range(time_period)
        
        # Get fulfilled reservations for this agency
        fulfilled_results = self.execute_query("GET_FULFILLED_RESERVATIONS", {
            "agency_id": agency_id,
            "start_date": start_date,
            "end_date": end_date
        })
        
        # Get started care stays for this agency (nur erste Einsätze, keine Folgeeinsätze)
        started_results = self.execute_query("GET_STARTED_FIRST_CARE_STAYS", {
            "agency_id": agency_id,
            "start_date": start_date,
            "end_date": end_date
        })
        
        # Calculate arrival rate
        fulfilled_count = fulfilled_results[0]["fulfilled_reservations_count"] if fulfilled_results else 0
        started_count = started_results[0]["successfully_started_care_stays_count"] if started_results else 0
        
        ratio = 0
        if fulfilled_count > 0:
            ratio = started_count / fulfilled_count
        
        agency_name = None
        if fulfilled_results:
            agency_name = fulfilled_results[0]["agency_name"]
        elif started_results:
            agency_name = started_results[0]["agency_name"]
        
        return {
            "agency_id": agency_id,
            "agency_name": agency_name,
            "fulfilled_count": fulfilled_count,
            "started_count": started_count,
            "arrival_ratio": ratio,
            "ratio_percentage": f"{ratio * 100:.1f}%",
            "name": "Anreiserate",
            "description": "Zeigt wie viel % der vorgeschlagenen Pflegekräfte schlussendlich auch wirklich angereist sind (nur Ersteinsätze)"
        }
        
    def get_cancellation_before_arrival_rate(self, agency_id: str, start_date: str = None, end_date: str = None, time_period: str = "last_quarter") -> Dict[str, Any]:
        """
        Quote 6: Anzahl gemachter Personalvorschläge - Anzahl VOR Einsatz abgebrochener Pflegeeinsätze
        Zeigt, wie viel % der vorgeschlagenen Pflegekräfte von der Agentur wieder abgebrochen wurden (vor Anreise)
        
        Args:
            agency_id (str): The ID of the agency
            start_date (str, optional): Start date in 'YYYY-MM-DD' format
            end_date (str, optional): End date in 'YYYY-MM-DD' format
            time_period (str, optional): Predefined time period (last_quarter, last_month, etc.)
            
        Returns:
            dict: Dictionary with cancellation metrics
        """
        # Calculate date range if not provided
        if not start_date or not end_date:
            start_date, end_date = self._calculate_date_range(time_period)
        
        # Get personnel proposals for this agency
        proposal_results = self.execute_query("GET_PERSONNEL_PROPOSALS", {
            "agency_id": agency_id,
            "start_date": start_date,
            "end_date": end_date
        })
        
        # Get cancelled before arrival for this agency
        cancelled_results = self.execute_query("GET_CANCELLED_BEFORE_ARRIVAL", {
            "agency_id": agency_id,
            "start_date": start_date,
            "end_date": end_date
        })
        
        # Calculate relative ratios for each bucket
        def fmt_ratio(val, total):
            return f"{(val / total) * 100:.1f}%" if total > 0 else "0.0%"
        
        def bucket_output(row, total):
            return {
                "count": row["abgebrochen_vor_arrival"],
                "lt_3_days": {"count": row["lt_3_days"], "ratio": fmt_ratio(row["lt_3_days"], total)},
                "btw_3_7_days": {"count": row["btw_3_7_days"], "ratio": fmt_ratio(row["btw_3_7_days"], total)},
                "btw_8_14_days": {"count": row["btw_8_14_days"], "ratio": fmt_ratio(row["btw_8_14_days"], total)},
                "btw_15_30_days": {"count": row["btw_15_30_days"], "ratio": fmt_ratio(row["btw_15_30_days"], total)}
            }
        
        # Map results by group
        # Calculate proposal count for denominator
        proposal_count = proposal_results[0]["proposal_count"] if proposal_results else 0
        
        # Extract bucket counts per group
        buckets = {"gesamt": {}, "nur_erstanreise": {}, "ohne_erstanreise": {}}
        for row in cancelled_results:
            gruppe = row["gruppe"]
            if gruppe in buckets:
                buckets[gruppe] = bucket_output(row, proposal_count)
        
        # Calculate overall cancellation ratio
        gesamt_cancelled = buckets.get("gesamt", {}).get("count", 0)
        gesamt_ratio = gesamt_cancelled / proposal_count if proposal_count > 0 else 0
        
        agency_name = None
        if proposal_results:
            agency_name = proposal_results[0]["agency_name"]
        
        return {
            "agency_id": agency_id,
            "agency_name": agency_name,
            "proposal_count": proposal_count,
            "cancellation_ratio_gesamt": f"{gesamt_ratio * 100:.1f}%",
            "cancellation_buckets": buckets,
            "name": "Abbruchrate vor Anreise",
            "description": "Zeigt, wie viel % der vorgeschlagenen Pflegekräfte von der Agentur wieder abgebrochen wurden (vor Anreise), aufgeschlüsselt nach Kurzfristigkeit und Erstanreise/Wechsel."
        }
        
    def get_completion_rate(self, agency_id: str, start_date: str = None, end_date: str = None, time_period: str = "last_quarter") -> Dict[str, Any]:
        """
        Quote 7: Pflegeeinsatz angetreten - Pflegeinsatz vollständig beendet
        Zeigt, wie viel % der zum Kunden angereisten Pflegekräfte den Einsatz wie geplant bis zum Schluss durchgezogen haben
        
        Args:
            agency_id (str): The ID of the agency
            start_date (str, optional): Start date in 'YYYY-MM-DD' format
            end_date (str, optional): End date in 'YYYY-MM-DD' format
            time_period (str, optional): Predefined time period (last_quarter, last_month, etc.)
            
        Returns:
            dict: Dictionary with completion metrics
        """
        # Calculate date range if not provided
        if not start_date or not end_date:
            start_date, end_date = self._calculate_date_range(time_period)
        
        # Get started care stays for this agency
        started_results = self.execute_query("GET_STARTED_CARE_STAYS", {
            "agency_id": agency_id,
            "start_date": start_date,
            "end_date": end_date
        })
        
        # Get completed care stays for this agency
        completed_results = self.execute_query("GET_COMPLETED_CARE_STAYS", {
            "agency_id": agency_id,
            "start_date": start_date,
            "end_date": end_date
        })
        
        # Calculate completion rate
        started_count = started_results[0]["successfully_started_care_stays_count"] if started_results else 0
        completed_count = completed_results[0]["completed_full_term"] if completed_results else 0
        
        ratio = 0
        if started_count > 0:
            ratio = completed_count / started_count
        
        agency_name = None
        if started_results:
            agency_name = started_results[0]["agency_name"]
        elif completed_results:
            agency_name = completed_results[0]["agency_name"]
        
        return {
            "agency_id": agency_id,
            "agency_name": agency_name,
            "started_count": started_count,
            "completed_count": completed_count,
            "completion_ratio": ratio,
            "ratio_percentage": f"{ratio * 100:.1f}%",
            "name": "Abschlussrate",
            "description": "Zeigt, wie viel % der zum Kunden angereisten Pflegekräfte den Einsatz wie geplant bis zum Schluss durchgezogen haben"
        }
    
    def get_all_quotas(self, agency_id: str, start_date: str = None, end_date: str = None, time_period: str = "last_quarter") -> Dict[str, Any]:
        """
        Get all quota metrics for a specific agency
        
        Args:
            agency_id (str): The ID of the agency
            start_date (str, optional): Start date in 'YYYY-MM-DD' format
            end_date (str, optional): End date in 'YYYY-MM-DD' format
            time_period (str, optional): Predefined time period (last_quarter, last_month, etc.)
            
        Returns:
            dict: Dictionary with all quota metrics
        """
        # Calculate date range if not provided
        if not start_date or not end_date:
            start_date, end_date = self._calculate_date_range(time_period)
            
        # Get agency details
        agency_details = self.get_agency_details(agency_id)
        agency_name = agency_details.get("agency_name", "Unknown Agency")
        
        # Get all quotas
        quotas = {
            "quota1_reservation": self.get_agency_reservation_metrics(agency_id, start_date, end_date),
            "quota2_fulfillment": self.get_fulfillment_rate(agency_id, start_date, end_date),
            "quota3_withdrawal": self.get_withdrawal_rate(agency_id, start_date, end_date),
            "quota4_pending": self.get_pending_rate(agency_id, start_date, end_date),
            "quota5_arrival": self.get_arrival_rate(agency_id, start_date, end_date),
            "quota6_cancellation": self.get_cancellation_before_arrival_rate(agency_id, start_date, end_date),
            "quota7_completion": self.get_completion_rate(agency_id, start_date, end_date)
        }
        
        return {
            "agency_id": agency_id,
            "agency_name": agency_name,
            "time_period": time_period,
            "start_date": start_date,
            "end_date": end_date,
            "quotas": quotas
        }
    
    def _calculate_date_range(self, time_period: str) -> tuple:
        """
        Calculate start and end dates based on time period
        
        Args:
            time_period (str): The time period (last_quarter, last_month, last_year, etc.)
            
        Returns:
            tuple: (start_date, end_date) as strings in 'YYYY-MM-DD' format
        """
        end_date = datetime.now()
        
        if time_period == "last_quarter":
            start_date = end_date - timedelta(days=90)
        elif time_period == "last_month":
            start_date = end_date - timedelta(days=30)
        elif time_period == "last_year":
            start_date = end_date - timedelta(days=365)
        elif time_period == "all_time":
            start_date = datetime(2000, 1, 1)  # Very old date to include all data
        else:
            # Default to last quarter
            start_date = end_date - timedelta(days=90)
        
        return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")

    # --- Methods for Overall Reaction Time Stats --- 

    def get_overall_posting_to_reservation_stats(self, start_date: str = None, end_date: str = None, time_period: str = "last_quarter") -> dict:
        if not start_date or not end_date:
            start_date, end_date = self._calculate_date_range(time_period)
        params = {"start_date": start_date, "end_date": end_date}
        results = self.execute_query("TIME_POSTING_TO_RESERVATION_STATS_OVERALL", params)
        return results[0] if results else {"median_hours": None, "avg_hours": None}

    def get_overall_reservation_to_first_proposal_stats(self, start_date: str = None, end_date: str = None, time_period: str = "last_quarter") -> dict:
        if not start_date or not end_date:
            start_date, end_date = self._calculate_date_range(time_period)
        params = {"start_date": start_date, "end_date": end_date}
        results = self.execute_query("TIME_RESERVATION_TO_FIRST_PROPOSAL_STATS_OVERALL", params)
        return results[0] if results else {"median_hours": None, "avg_hours": None}

    def get_overall_proposal_to_cancellation_stats(self, start_date: str = None, end_date: str = None, time_period: str = "last_quarter") -> dict:
        if not start_date or not end_date:
            start_date, end_date = self._calculate_date_range(time_period)
        params = {"start_date": start_date, "end_date": end_date}
        results = self.execute_query("TIME_PROPOSAL_TO_CANCELLATION_STATS_OVERALL", params)
        return results[0] if results else {"median_hours": None, "avg_hours": None}

    def get_overall_arrival_to_cancellation_stats(self, start_date: str = None, end_date: str = None, time_period: str = "last_quarter") -> dict:
        if not start_date or not end_date:
            start_date, end_date = self._calculate_date_range(time_period)
        params = {"start_date": start_date, "end_date": end_date}
        results = self.execute_query("TIME_ARRIVAL_TO_CANCELLATION_STATS_OVERALL", params)
        stats = {"overall": None, "first_stays": None, "followup_stays": None}
        for row in results:
            group = row.get("group_type")
            if group in stats:
                stats[group] = {
                    "median_hours": row["median_hours"],
                    "avg_hours": row["avg_hours"]
                }
        return stats

    def get_overall_cancellation_before_arrival_stats(self, start_date: str = None, end_date: str = None, time_period: str = "last_quarter") -> Dict[str, Any]:
        """
        Get overall average cancellation before arrival stats across all agencies.
        Includes average counts for buckets and average proposal count.
        """
        if not start_date or not end_date:
            start_date, end_date = self._calculate_date_range(time_period)
            
        params = {"start_date": start_date, "end_date": end_date}
        results = self.execute_query("GET_OVERALL_CANCELLED_BEFORE_ARRIVAL_STATS", params)
        
        if results:
            # Helper to calculate average ratio for buckets
            avg_proposal_count = results[0].get("avg_proposal_count", 1) # Avoid division by zero
            def avg_rel(avg_count):
                 return f"{(avg_count / avg_proposal_count) * 100:.1f}%" if avg_proposal_count > 0 and avg_count is not None else "0.0%"

            return {
                "avg_proposal_count": results[0].get("avg_proposal_count"),
                "avg_cancellation_ratio_gesamt": f"{results[0].get('avg_cancellation_ratio', 0) * 100:.1f}%",
                "avg_cancellation_buckets": {
                    "gesamt": {"count": results[0].get("avg_total_cancelled")},
                    "lt_3_days": {"count": results[0].get("avg_lt_3_days"), "ratio": avg_rel(results[0].get("avg_lt_3_days"))},
                    "btw_3_7_days": {"count": results[0].get("avg_btw_3_7_days"), "ratio": avg_rel(results[0].get("avg_btw_3_7_days"))},
                    "btw_8_14_days": {"count": results[0].get("avg_btw_8_14_days"), "ratio": avg_rel(results[0].get("avg_btw_8_14_days"))},
                    "btw_15_30_days": {"count": results[0].get("avg_btw_15_30_days"), "ratio": avg_rel(results[0].get("avg_btw_15_30_days"))}
                }
            }
        return {"avg_proposal_count": None, "avg_cancellation_ratio_gesamt": None, "avg_cancellation_buckets": {}}