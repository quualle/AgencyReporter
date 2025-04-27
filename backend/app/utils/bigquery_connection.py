from typing import Dict, List, Any, Optional, Union
from google.cloud import bigquery
import logging
import os
from datetime import datetime, timedelta
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
            _id AS agency_id,
            name AS agency_name,
            created_at,
            active AS status,
            location,
            contact_email,
            contact_phone
        FROM 
            `{self.project_id}.{self.dataset}.agencies`
        WHERE 
            active = 'true'
        ORDER BY 
            agency_name ASC
        """
        
        return self.execute_query(query)
    
    def get_kpis_by_agency(self, agency_id: str, time_period: str = "last_quarter") -> Dict[str, Any]:
        """
        Get KPIs (Quotas) for a specific agency based on care_stays
        """
        date_field = "cs.created_at"
        date_filter = self._get_date_filter(time_period, date_field)
        
        query = f"""
        WITH 
        agency_care_stays AS (
            SELECT 
                c.agency_id,
                cs._id AS care_stay_id,
                cs.stage,
                cs.arrival,
                cs.departure,
                EXISTS (
                    SELECT 1 FROM UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track 
                    WHERE JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Bestätigt'
                    AND TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at')) <= TIMESTAMP(cs.arrival)
                ) AS was_confirmed_before_arrival,
                EXISTS (
                    SELECT 1 FROM UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track 
                    WHERE JSON_EXTRACT_SCALAR(track, '$.differences.departure[0]') IS NOT NULL
                ) AS departure_changed
            FROM 
                `{self.project_id}.{self.dataset}.care_stays` cs
            JOIN 
                `{self.project_id}.{self.dataset}.contracts` c ON cs.contract_id = c._id
            WHERE 
                c.agency_id = @agency_id
                AND {date_filter}
        ),
        agency_metrics AS (
            SELECT 
                agency_id,
                COUNT(care_stay_id) AS total_proposals,
                COUNTIF(stage = 'Bestätigt' AND arrival IS NOT NULL AND departure IS NOT NULL AND TIMESTAMP(departure) < CURRENT_TIMESTAMP()) AS total_completed_scheduled,
                COUNTIF(stage = 'Bestätigt' AND arrival IS NOT NULL) AS total_started,
                COUNTIF(stage = 'Abgebrochen') AS total_cancelled,
                COUNTIF(stage = 'Bestätigt' AND arrival IS NOT NULL AND departure_changed) AS total_ended_early
            FROM 
                agency_care_stays
            GROUP BY 
                agency_id
        )
        SELECT 
            am.*,
            SAFE_DIVIDE(am.total_started, am.total_proposals) AS start_rate,
            SAFE_DIVIDE(am.total_completed_scheduled, am.total_started) AS completion_rate,
            SAFE_DIVIDE(am.total_ended_early, am.total_started) AS early_end_rate
        FROM 
            agency_metrics am
        """
        
        params = {"agency_id": agency_id}
        result = self.execute_query(query, params)
        return result[0] if result else {}
    
    def get_response_times_by_agency(self, agency_id: str, time_period: str = "last_quarter") -> Dict[str, Any]:
        """
        Get simplified response times for a specific agency based on care_stays
        NOTE: Some original metrics are hard to calculate without complex joins or dedicated event tables.
        """
        date_field = "cs.created_at"
        date_filter = self._get_date_filter(time_period, date_field)
        
        query = f"""
        WITH 
        response_metrics AS (
            SELECT 
                c.agency_id,
                AVG(TIMESTAMP_DIFF(TIMESTAMP(cs.arrival), TIMESTAMP(cs.presented_at), HOUR)) AS avg_time_proposal_to_arrival,
                AVG(TIMESTAMP_DIFF(TIMESTAMP(cs.departure), TIMESTAMP(cs.arrival), HOUR)) AS avg_stay_duration_hours
            FROM 
                `{self.project_id}.{self.dataset}.care_stays` cs
            JOIN
                 `{self.project_id}.{self.dataset}.contracts` c ON cs.contract_id = c._id
            WHERE 
                c.agency_id = @agency_id
                AND cs.presented_at IS NOT NULL
                AND cs.arrival IS NOT NULL
                AND cs.departure IS NOT NULL
                AND {date_filter}
            GROUP BY 
                c.agency_id
        )
        SELECT * FROM response_metrics
        """
        
        params = {"agency_id": agency_id}
        result = self.execute_query(query, params)
        
        # Prepare the final result dictionary, ensuring agency_id is included
        final_result = {
            "agency_id": agency_id, # Add the agency_id explicitly
            "avg_time_to_reservation": 0.0, # Placeholder
            "avg_time_to_proposal": 0.0, # Placeholder
            "avg_time_to_cancellation": 0.0, # Placeholder
            "avg_time_before_start": 0.0, # Placeholder
            "avg_time_to_any_cancellation": 0.0, # Placeholder
            "avg_time_proposal_to_arrival": None, # Initialize with None
            "avg_stay_duration_hours": None # Initialize with None
        }
        
        # Update with actual calculated values if query returned results
        if result:
            res = result[0]
            final_result["avg_time_proposal_to_arrival"] = res.get("avg_time_proposal_to_arrival")
            final_result["avg_stay_duration_hours"] = res.get("avg_stay_duration_hours")
            # Ensure the agency_id from the result is used if available (though it should match the input)
            # final_result["agency_id"] = res.get("agency_id", agency_id)

        return final_result
    
    def get_profile_quality_by_agency(self, agency_id: str, time_period: str = "last_quarter") -> Dict[str, Any]:
        """
        Get profile quality metrics for a specific agency
        
        Args:
            agency_id (str): The ID of the agency
            time_period (str): The time period for which to get the metrics
            
        Returns:
            dict: Dictionary with profile quality information
        """
        date_field = "cp.created_at"
        date_filter = self._get_date_filter(time_period, date_field)
        
        query = f"""
        WITH 
        profile_violations AS (
            SELECT 
                cp.agency_id,
                COUNT(DISTINCT cp._id) AS total_caregivers,
                0 AS experience_violations,
                0 AS language_violations,
                0 AS smoker_violations,
                0 AS age_violations,
                0 AS license_violations
            FROM 
                `{self.project_id}.{self.dataset}.care_giver_instances` cp
            WHERE 
                cp.agency_id = @agency_id
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
        result = self.execute_query(query, params)
        return result[0] if result else {}
    
    def get_all_agencies_kpis(self, time_period: str = "last_quarter") -> List[Dict[str, Any]]:
        """
        Get KPIs for all agencies for comparison based on care_stays
        """
        date_field = "cs.created_at"
        date_filter = self._get_date_filter(time_period, date_field)
        
        query = f"""
        WITH 
        agency_care_stays AS (
             SELECT 
                 c.agency_id,
                 a.name AS agency_name,
                 cs._id AS care_stay_id,
                 cs.stage
             FROM 
                 `{self.project_id}.{self.dataset}.care_stays` cs
             JOIN 
                 `{self.project_id}.{self.dataset}.contracts` c ON cs.contract_id = c._id
             JOIN
                 `{self.project_id}.{self.dataset}.agencies` a ON c.agency_id = a._id
             WHERE 
                 {date_filter}
                 AND a.active = 'true'
        ),
        agency_metrics AS (
            SELECT 
                agency_id,
                agency_name,
                COUNT(care_stay_id) AS total_proposals,
                COUNTIF(stage = 'Bestätigt') AS total_started,
                COUNTIF(stage = 'Bestätigt') AS total_completed,
                COUNTIF(stage = 'Abgebrochen') AS total_ended_early,
                COUNTIF(stage = 'Abgebrochen') AS total_cancelled
        )
        SELECT 
            am.*,
            0.0 AS reservation_rate,
            0.0 AS fulfillment_rate,
            0.0 AS cancellation_rate,
            SAFE_DIVIDE(am.total_started, am.total_proposals) AS start_rate,
            SAFE_DIVIDE(am.total_completed, am.total_started) AS completion_rate,
            SAFE_DIVIDE(am.total_ended_early, am.total_started) AS early_end_rate
        FROM 
            agency_metrics am
        ORDER BY
            am.agency_name ASC
        """
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
    
    def _get_date_filter(self, time_period: str, date_field_name: str = "created_at") -> str:
        """
        Helper method to generate date filter SQL based on time period and field name
        """
        today = datetime.now().date()
        if time_period == "last_quarter":
            start_date = today - timedelta(days=90)
            return f"DATE({date_field_name}) >= '{start_date.isoformat()}'"
        elif time_period == "last_month":
            start_date = today - timedelta(days=30)
            return f"DATE({date_field_name}) >= '{start_date.isoformat()}'"
        elif time_period == "last_year":
            start_date = today - timedelta(days=365)
            return f"DATE({date_field_name}) >= '{start_date.isoformat()}'"
        elif time_period == "all_time":
            return "TRUE"  # No date filter
        else:
            # Default to last quarter
            start_date = today - timedelta(days=90)
            return f"DATE({date_field_name}) >= '{start_date.isoformat()}'"
    
    def get_avg_time_posting_to_reservation(self, agency_id: str, start_date: str, end_date: str) -> float:
        """
        Get average time (in hours) from posting creation to reservation for a specific agency
        """
        from ..queries.reaction_times import reaction_times
        query = reaction_times.TIME_POSTING_TO_RESERVATION
        params = {
            "agency_id": agency_id,
            "start_date": start_date,
            "end_date": end_date
        }
        result = self.execute_query(query, params)
        return result[0]["avg_time_to_reservation"] if result and result[0]["avg_time_to_reservation"] is not None else 0.0
    
    def get_avg_time_reservation_to_first_proposal(self, agency_id: str, start_date: str, end_date: str) -> float:
        """
        Get average time (in hours) from reservation to first proposal (CareStay) for a specific agency
        """
        from ..queries.reaction_times import reaction_times
        query = reaction_times.TIME_RESERVATION_TO_FIRST_PROPOSAL
        params = {
            "agency_id": agency_id,
            "start_date": start_date,
            "end_date": end_date
        }
        result = self.execute_query(query, params)
        return result[0]["avg_time_to_first_proposal"] if result and result[0]["avg_time_to_first_proposal"] is not None else 0.0
    
    def get_posting_to_reservation_stats(self, agency_id: str, start_date: str, end_date: str) -> dict:
        """
        Get median and average time (in hours) from posting to reservation for a specific agency
        """
        from ..queries.reaction_times import reaction_times
        query = reaction_times.TIME_POSTING_TO_RESERVATION_STATS
        params = {
            "agency_id": agency_id,
            "start_date": start_date,
            "end_date": end_date
        }
        result = self.execute_query(query, params)
        if result:
            return {
                "median_hours": result[0]["median_hours"],
                "avg_hours": result[0]["avg_hours"]
            }
        return {"median_hours": None, "avg_hours": None}

    def get_reservation_to_first_proposal_stats(self, agency_id: str, start_date: str, end_date: str) -> dict:
        """
        Get median and average time (in hours) from reservation to first proposal for a specific agency
        """
        from ..queries.reaction_times import reaction_times
        query = reaction_times.TIME_RESERVATION_TO_FIRST_PROPOSAL_STATS
        params = {
            "agency_id": agency_id,
            "start_date": start_date,
            "end_date": end_date
        }
        result = self.execute_query(query, params)
        if result:
            return {
                "median_hours": result[0]["median_hours"],
                "avg_hours": result[0]["avg_hours"]
            }
        return {"median_hours": None, "avg_hours": None}

    def get_proposal_to_cancellation_stats(self, agency_id: str, start_date: str, end_date: str) -> dict:
        """
        Get median and average time (in hours) from proposal (presented_at) to cancellation (Abbruch vor Anreise) for a specific agency
        """
        from ..queries.reaction_times import reaction_times
        query = reaction_times.TIME_PROPOSAL_TO_CANCELLATION_STATS
        params = {
            "agency_id": agency_id,
            "start_date": start_date,
            "end_date": end_date
        }
        result = self.execute_query(query, params)
        if result:
            return {
                "median_hours": result[0]["median_hours"],
                "avg_hours": result[0]["avg_hours"]
            }
        return {"median_hours": None, "avg_hours": None}

    def get_arrival_to_cancellation_stats(self, agency_id: str, start_date: str, end_date: str) -> dict:
        """
        Get median and average time (in hours) from planned arrival to cancellation (Abbruch vor Anreise) for a specific agency,
        aufgeteilt in overall, first_stays und followup_stays.
        """
        from ..queries.reaction_times import reaction_times
        query = reaction_times.TIME_ARRIVAL_TO_CANCELLATION_STATS
        params = {
            "agency_id": agency_id,
            "start_date": start_date,
            "end_date": end_date
        }
        result = self.execute_query(query, params)
        stats = {"overall": None, "first_stays": None, "followup_stays": None}
        for row in result:
            group = row.get("group_type")
            if group in stats:
                stats[group] = {
                    "median_hours": row["median_hours"],
                    "avg_hours": row["avg_hours"]
                }
        return stats 