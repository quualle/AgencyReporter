from typing import Dict, List, Any, Optional, Union
from google.cloud import bigquery
import logging
import os
from datetime import datetime
from ..dependencies import get_settings, get_bigquery_client

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BigQueryConnection:
    """
    A class to handle BigQuery connections and queries for the Agency Reporter
    """
    
    def __init__(self):
        """
        Initialize the BigQuery connection
        """
        self.client = get_bigquery_client()
        self.settings = get_settings()
        self.project_id = self.settings.bigquery_project_id
        self.dataset = self.settings.bigquery_dataset
    
    def execute_query(self, query: str, query_params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a BigQuery SQL query and return the results as a list of dictionaries
        
        Args:
            query (str): The SQL query to execute
            query_params (dict, optional): Parameters for the query
            
        Returns:
            list: List of dictionaries with the query results
        """
        try:
            # Create query job config
            job_config = bigquery.QueryJobConfig()
            query_parameters = []
            
            # Add parameters if provided
            if query_params:
                for param_name, param_value in query_params.items():
                    # Determine parameter type
                    if isinstance(param_value, int):
                        param_type = "INT64"
                    elif isinstance(param_value, float):
                        param_type = "FLOAT64"
                    elif isinstance(param_value, bool):
                        param_type = "BOOL"
                    elif isinstance(param_value, datetime):
                        param_type = "TIMESTAMP"
                    else:
                        param_type = "STRING"
                    
                    # Add parameter to the list
                    query_parameters.append(
                        bigquery.ScalarQueryParameter(param_name, param_type, param_value)
                    )
                
                job_config.query_parameters = query_parameters
            
            # Execute query
            query_job = self.client.query(query, job_config=job_config)
            results = query_job.result()
            
            # Convert results to list of dictionaries
            rows = []
            for row in results:
                row_dict = {}
                for key, value in row.items():
                    # Convert non-serializable values
                    if hasattr(value, 'isoformat'):
                        row_dict[key] = value.isoformat()
                    else:
                        row_dict[key] = value
                rows.append(row_dict)
            
            return rows
        
        except Exception as e:
            logger.error(f"Error executing BigQuery query: {str(e)}")
            raise
    
    def get_agencies(self) -> List[Dict[str, Any]]:
        """
        Get a list of all agencies
        
        Returns:
            list: List of dictionaries with agency information
        """
        query = f"""
        SELECT 
            agency_id,
            agency_name,
            created_at,
            status,
            location,
            contact_email,
            contact_phone
        FROM 
            `{self.project_id}.{self.dataset}.agencies`
        WHERE 
            status = 'active'
        ORDER BY 
            agency_name ASC
        """
        
        return self.execute_query(query)
    
    def get_kpis_by_agency(self, agency_id: str, time_period: str = "last_quarter") -> Dict[str, Any]:
        """
        Get KPIs for a specific agency
        
        Args:
            agency_id (str): The ID of the agency
            time_period (str): The time period for which to get the KPIs
            
        Returns:
            dict: Dictionary with KPI information
        """
        # Calculate date range based on time period
        date_filter = self._get_date_filter(time_period)
        
        query = f"""
        WITH 
        agency_metrics AS (
            SELECT 
                agency_id,
                COUNT(DISTINCT job_id) AS total_jobs_viewed,
                COUNT(DISTINCT CASE WHEN status = 'reserved' THEN job_id END) AS total_jobs_reserved,
                COUNT(DISTINCT CASE WHEN status = 'fulfilled' THEN job_id END) AS total_jobs_fulfilled,
                COUNT(DISTINCT CASE WHEN status = 'cancelled_by_agency' THEN job_id END) AS total_jobs_cancelled,
                COUNT(DISTINCT CASE WHEN status = 'pending' THEN job_id END) AS total_jobs_pending,
                COUNT(DISTINCT CASE WHEN status = 'caregiver_assigned' THEN job_id END) AS total_caregivers_assigned,
                COUNT(DISTINCT CASE WHEN status = 'caregiver_started' THEN job_id END) AS total_caregivers_started,
                COUNT(DISTINCT CASE WHEN status = 'ended_early' THEN job_id END) AS total_ended_early,
                COUNT(DISTINCT CASE WHEN status = 'completed' THEN job_id END) AS total_completed
            FROM 
                `{self.project_id}.{self.dataset}.job_placements`
            WHERE 
                agency_id = @agency_id
                AND {date_filter}
            GROUP BY 
                agency_id
        )
        
        SELECT 
            am.*,
            SAFE_DIVIDE(am.total_jobs_reserved, am.total_jobs_viewed) AS reservation_rate,
            SAFE_DIVIDE(am.total_jobs_fulfilled, am.total_jobs_reserved) AS fulfillment_rate,
            SAFE_DIVIDE(am.total_jobs_cancelled, am.total_jobs_reserved) AS cancellation_rate,
            SAFE_DIVIDE(am.total_caregivers_started, am.total_caregivers_assigned) AS start_rate,
            SAFE_DIVIDE(am.total_completed, am.total_caregivers_started) AS completion_rate,
            SAFE_DIVIDE(am.total_ended_early, am.total_caregivers_started) AS early_end_rate
        FROM 
            agency_metrics am
        """
        
        params = {"agency_id": agency_id}
        
        # Execute the query
        result = self.execute_query(query, params)
        
        # Return the first row if available, otherwise empty dict
        return result[0] if result else {}
    
    def get_response_times_by_agency(self, agency_id: str, time_period: str = "last_quarter") -> Dict[str, Any]:
        """
        Get response times for a specific agency
        
        Args:
            agency_id (str): The ID of the agency
            time_period (str): The time period for which to get the response times
            
        Returns:
            dict: Dictionary with response times information
        """
        # Calculate date range based on time period
        date_filter = self._get_date_filter(time_period)
        
        query = f"""
        WITH 
        response_metrics AS (
            SELECT 
                agency_id,
                AVG(TIMESTAMP_DIFF(reservation_time, job_created_time, HOUR)) AS avg_time_to_reservation,
                AVG(TIMESTAMP_DIFF(proposal_time, reservation_time, HOUR)) AS avg_time_to_proposal,
                AVG(CASE WHEN status = 'cancelled_by_agency' THEN TIMESTAMP_DIFF(cancellation_time, proposal_time, HOUR) END) AS avg_time_to_cancellation,
                AVG(CASE WHEN status = 'cancelled_by_agency' THEN TIMESTAMP_DIFF(planned_start_date, cancellation_time, HOUR) END) AS avg_time_before_start,
                AVG(TIMESTAMP_DIFF(cancellation_time, reservation_time, HOUR)) AS avg_time_to_any_cancellation
            FROM 
                `{self.project_id}.{self.dataset}.job_placements`
            WHERE 
                agency_id = @agency_id
                AND {date_filter}
            GROUP BY 
                agency_id
        )
        
        SELECT * FROM response_metrics
        """
        
        params = {"agency_id": agency_id}
        
        # Execute the query
        result = self.execute_query(query, params)
        
        # Return the first row if available, otherwise empty dict
        return result[0] if result else {}
    
    def get_profile_quality_by_agency(self, agency_id: str, time_period: str = "last_quarter") -> Dict[str, Any]:
        """
        Get profile quality metrics for a specific agency
        
        Args:
            agency_id (str): The ID of the agency
            time_period (str): The time period for which to get the metrics
            
        Returns:
            dict: Dictionary with profile quality information
        """
        # Calculate date range based on time period
        date_filter = self._get_date_filter(time_period)
        
        query = f"""
        WITH 
        profile_violations AS (
            SELECT 
                cp.agency_id,
                COUNT(DISTINCT cp.caregiver_id) AS total_caregivers,
                COUNT(DISTINCT CASE WHEN pv.violation_type = 'experience' THEN cp.caregiver_id END) AS experience_violations,
                COUNT(DISTINCT CASE WHEN pv.violation_type = 'language' THEN cp.caregiver_id END) AS language_violations,
                COUNT(DISTINCT CASE WHEN pv.violation_type = 'smoker' THEN cp.caregiver_id END) AS smoker_violations,
                COUNT(DISTINCT CASE WHEN pv.violation_type = 'age' THEN cp.caregiver_id END) AS age_violations,
                COUNT(DISTINCT CASE WHEN pv.violation_type = 'drivers_license' THEN cp.caregiver_id END) AS license_violations
            FROM 
                `{self.project_id}.{self.dataset}.caregiver_profiles` cp
            LEFT JOIN 
                `{self.project_id}.{self.dataset}.profile_violations` pv
            ON 
                cp.caregiver_id = pv.caregiver_id
            WHERE 
                cp.agency_id = @agency_id
                AND {date_filter}
            GROUP BY 
                cp.agency_id
        )
        
        SELECT 
            pv.*,
            SAFE_DIVIDE(pv.experience_violations, pv.total_caregivers) AS experience_violation_rate,
            SAFE_DIVIDE(pv.language_violations, pv.total_caregivers) AS language_violation_rate,
            SAFE_DIVIDE(pv.smoker_violations, pv.total_caregivers) AS smoker_violation_rate,
            SAFE_DIVIDE(pv.age_violations, pv.total_caregivers) AS age_violation_rate,
            SAFE_DIVIDE(pv.license_violations, pv.total_caregivers) AS license_violation_rate
        FROM 
            profile_violations pv
        """
        
        params = {"agency_id": agency_id}
        
        # Execute the query
        result = self.execute_query(query, params)
        
        # Return the first row if available, otherwise empty dict
        return result[0] if result else {}
    
    def get_all_agencies_kpis(self, time_period: str = "last_quarter") -> List[Dict[str, Any]]:
        """
        Get KPIs for all agencies for comparison
        
        Args:
            time_period (str): The time period for which to get the KPIs
            
        Returns:
            list: List of dictionaries with KPI information for all agencies
        """
        # Calculate date range based on time period
        date_filter = self._get_date_filter(time_period)
        
        query = f"""
        WITH 
        agency_metrics AS (
            SELECT 
                jp.agency_id,
                a.agency_name,
                COUNT(DISTINCT jp.job_id) AS total_jobs_viewed,
                COUNT(DISTINCT CASE WHEN jp.status = 'reserved' THEN jp.job_id END) AS total_jobs_reserved,
                COUNT(DISTINCT CASE WHEN jp.status = 'fulfilled' THEN jp.job_id END) AS total_jobs_fulfilled,
                COUNT(DISTINCT CASE WHEN jp.status = 'cancelled_by_agency' THEN jp.job_id END) AS total_jobs_cancelled,
                COUNT(DISTINCT CASE WHEN jp.status = 'pending' THEN jp.job_id END) AS total_jobs_pending,
                COUNT(DISTINCT CASE WHEN jp.status = 'caregiver_assigned' THEN jp.job_id END) AS total_caregivers_assigned,
                COUNT(DISTINCT CASE WHEN jp.status = 'caregiver_started' THEN jp.job_id END) AS total_caregivers_started,
                COUNT(DISTINCT CASE WHEN jp.status = 'ended_early' THEN jp.job_id END) AS total_ended_early,
                COUNT(DISTINCT CASE WHEN jp.status = 'completed' THEN jp.job_id END) AS total_completed
            FROM 
                `{self.project_id}.{self.dataset}.job_placements` jp
            JOIN
                `{self.project_id}.{self.dataset}.agencies` a
            ON
                jp.agency_id = a.agency_id
            WHERE 
                {date_filter}
                AND a.status = 'active'
            GROUP BY 
                jp.agency_id, a.agency_name
        )
        
        SELECT 
            am.*,
            SAFE_DIVIDE(am.total_jobs_reserved, am.total_jobs_viewed) AS reservation_rate,
            SAFE_DIVIDE(am.total_jobs_fulfilled, am.total_jobs_reserved) AS fulfillment_rate,
            SAFE_DIVIDE(am.total_jobs_cancelled, am.total_jobs_reserved) AS cancellation_rate,
            SAFE_DIVIDE(am.total_caregivers_started, am.total_caregivers_assigned) AS start_rate,
            SAFE_DIVIDE(am.total_completed, am.total_caregivers_started) AS completion_rate,
            SAFE_DIVIDE(am.total_ended_early, am.total_caregivers_started) AS early_end_rate
        FROM 
            agency_metrics am
        ORDER BY
            am.agency_name ASC
        """
        
        # Execute the query
        return self.execute_query(query)
    
    def get_cancellation_texts(self, agency_id: str, time_period: str = "last_quarter") -> List[str]:
        """
        Get texts (emails, tickets, notes) related to cancellations for a specific agency
        
        Args:
            agency_id (str): The ID of the agency
            time_period (str): The time period for which to get the texts
            
        Returns:
            list: List of text strings
        """
        # Calculate date range based on time period
        date_filter = self._get_date_filter(time_period)
        
        query = f"""
        SELECT 
            c.message_text
        FROM 
            `{self.project_id}.{self.dataset}.communications` c
        JOIN
            `{self.project_id}.{self.dataset}.job_placements` jp
        ON
            c.job_id = jp.job_id
        WHERE 
            jp.agency_id = @agency_id
            AND jp.status = 'cancelled_by_agency'
            AND c.message_type IN ('email', 'ticket', 'note')
            AND {date_filter}
            AND c.message_text IS NOT NULL
            AND LENGTH(c.message_text) > 20
        ORDER BY
            c.created_at DESC
        LIMIT 100
        """
        
        params = {"agency_id": agency_id}
        
        # Execute the query
        results = self.execute_query(query, params)
        
        # Extract text from results
        texts = [row.get("message_text", "") for row in results if row.get("message_text")]
        
        # In case no real data is available, generate mock data for development
        if not texts:
            # Generate 10 mock cancellation texts for development/testing
            texts = [
                "Die Betreuungskraft Frau Müller hat leider kurzfristig abgesagt, da sie erkrankt ist und nicht anreisen kann.",
                "Wir müssen den Einsatz leider absagen, da der Kunde mit dem Profil der vorgeschlagenen Pflegekraft nicht zufrieden war und andere Qualifikationen erwartet hat.",
                "Die Pflegekraft hat einen besseren Auftrag bekommen und steht daher nicht mehr zur Verfügung.",
                "Aufgrund von Kommunikationsproblemen mit der Pflegekraft müssen wir den Einsatz absagen.",
                "Der Einsatz wird storniert, da die zugesagte Pflegekraft familiäre Probleme hat und nicht anreisen kann.",
                "Die Reservierung wurde zurückgezogen, da wir Probleme mit den Dokumenten der Pflegekraft haben.",
                "Die Betreuungskraft hat Transportprobleme und kann den Einsatzort nicht erreichen.",
                "Der Kunde hat kurzfristig andere Anforderungen gestellt, die wir mit der vorgeschlagenen Kraft nicht erfüllen können.",
                "Die Betreuungskraft ist mit der angebotenen Unterkunft nicht einverstanden und sagt daher den Einsatz ab.",
                "Die Betreuungskraft hat Probleme mit dem Visum und kann daher den Einsatz nicht antreten."
            ]
        
        return texts
    
    def get_violation_texts(self, agency_id: str, time_period: str = "last_quarter") -> List[str]:
        """
        Get texts (emails, tickets, notes) related to profile violations for a specific agency
        
        Args:
            agency_id (str): The ID of the agency
            time_period (str): The time period for which to get the texts
            
        Returns:
            list: List of text strings
        """
        # Calculate date range based on time period
        date_filter = self._get_date_filter(time_period)
        
        query = f"""
        SELECT 
            pv.violation_description
        FROM 
            `{self.project_id}.{self.dataset}.profile_violations` pv
        JOIN
            `{self.project_id}.{self.dataset}.caregiver_profiles` cp
        ON
            pv.caregiver_id = cp.caregiver_id
        WHERE 
            cp.agency_id = @agency_id
            AND {date_filter}
            AND pv.violation_description IS NOT NULL
            AND LENGTH(pv.violation_description) > 20
        ORDER BY
            pv.reported_at DESC
        LIMIT 100
        """
        
        params = {"agency_id": agency_id}
        
        # Execute the query
        results = self.execute_query(query, params)
        
        # Extract text from results
        texts = [row.get("violation_description", "") for row in results if row.get("violation_description")]
        
        # In case no real data is available, generate mock data for development
        if not texts:
            # Generate 10 mock violation texts for development/testing
            texts = [
                "Die Betreuungskraft hat angegeben, 5 Jahre Berufserfahrung zu haben, aber tatsächlich war sie erst 2 Jahre in der Pflege tätig.",
                "Die Deutschkenntnisse wurden im Profil als 'sehr gut' (B2) angegeben, aber die Pflegekraft kann sich kaum verständigen (A1-Niveau).",
                "Im Profil wurde angegeben, dass die Betreuungskraft Nichtraucherin ist, aber sie raucht regelmäßig in der Wohnung des Kunden.",
                "Das im Profil angegebene Alter (45) weicht vom tatsächlichen Alter (52) der Betreuungskraft ab.",
                "Die Pflegekraft hat angegeben, einen gültigen Führerschein zu besitzen, aber sie hat keinen und kann daher das Auto des Kunden nicht nutzen.",
                "Die angegebene Ausbildung als examinierte Pflegekraft konnte nicht nachgewiesen werden.",
                "Die Betreuungskraft hat behauptet, Erfahrung mit Demenzpatienten zu haben, aber sie weiß nicht, wie man mit der Erkrankung umgeht.",
                "Die Kraft hat angegeben, keine Haustierallergien zu haben, reagiert aber allergisch auf die Katze des Kunden.",
                "Im Profil wurde vermerkt, dass die Pflegekraft kochen kann, aber ihre Fähigkeiten in diesem Bereich sind sehr begrenzt.",
                "Die Pflegekraft hat im Profil angegeben, nachts durchzuschlafen, aber sie steht mehrmals nachts auf und ist dadurch tagsüber müde."
            ]
        
        return texts
    
    def _get_date_filter(self, time_period: str) -> str:
        """
        Helper method to generate date filter SQL based on time period
        
        Args:
            time_period (str): The time period (last_quarter, last_month, last_year, etc.)
            
        Returns:
            str: SQL condition for date filtering
        """
        if time_period == "last_quarter":
            return "date_field >= DATE_SUB(CURRENT_DATE(), INTERVAL 3 MONTH)"
        elif time_period == "last_month":
            return "date_field >= DATE_SUB(CURRENT_DATE(), INTERVAL 1 MONTH)"
        elif time_period == "last_year":
            return "date_field >= DATE_SUB(CURRENT_DATE(), INTERVAL 1 YEAR)"
        elif time_period == "all_time":
            return "TRUE"  # No date filter
        else:
            # Default to last quarter
            return "date_field >= DATE_SUB(CURRENT_DATE(), INTERVAL 3 MONTH)" 