from typing import List, Dict, Any, Optional
from google.cloud import bigquery
from datetime import datetime

from ...utils.bigquery_connection import get_bigquery_client


def interpret_german_score(score: str) -> str:
    """
    Interpretiert die Deutschnote (gs) in eine verständliche Beschreibung
    """
    if not score:
        return "Unbekannt"
    
    score_map = {
        "1": "Sehr gut (fließend)",
        "2": "Gut",
        "3": "Befriedigend (mittelmäßig)",
        "4": "Ausreichend (grundlegend)",
        "5": "Mangelhaft (sehr wenig)",
        "6": "Ungenügend (keine Kenntnisse)"
    }
    
    return score_map.get(str(score), f"Note {score} (unbekannte Skala)")

async def get_care_stays_for_cv_analysis(
    agency_id: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """
    Get list of care stays with basic information for CV quality analysis
    """
    client = get_bigquery_client()
    
    query = """
    SELECT 
        cs._id as care_stay_id,
        cgi.agency_id,
        a.name as agency_name,
        c.household_id as customer_id,
        cs.arrival as start_date,
        cs.departure as end_date,
        cs.stage as status,
        cs.rejection_reason as cancellation_reason,
        CASE 
            WHEN cs.stage = 'Abgebrochen' AND EXISTS (
                SELECT 1
                FROM UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track
                WHERE 
                    JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Abgebrochen'
                    AND TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at')) < TIMESTAMP(cs.arrival)
            ) THEN TRUE
            ELSE FALSE
        END as cancelled_before_arrival,
        DATE_DIFF(DATE(TIMESTAMP(cs.departure)), DATE(TIMESTAMP(cs.arrival)), DAY) as duration_days,
        -- Care Giver Instance Felder
        cgi._id as caregiver_instance_id,
        cgi.care_giver_id as caregiver_id,
        cgi.birthday as caregiver_birthday,
        cgi.exp as caregiver_experience,
        cgi.exp_ger as caregiver_experience_germany,
        cgi.description as caregiver_description,
        cgi.phone as caregiver_phone,
        cgi.external_id as caregiver_external_id,
        cgi.gs as caregiver_german_score,
        -- Care Giver Felder
        cg._id as caregiver_base_id,
        cg.first_name as caregiver_first_name,
        cg.last_name as caregiver_last_name,
        cg.machine_first_name as caregiver_machine_first_name,
        cg.machine_last_name as caregiver_machine_last_name,
        cg.gender as caregiver_gender,
        cg.salutation as caregiver_salutation,
        -- Household/Customer Felder
        h._id as household_id,
        h.lead_id as lead_id,
        h.designation as household_designation,
        h.is_customer as is_customer,
        h.hot_notes as household_notes,
        -- Lead Contact Info (Ansprechpartner/Entscheider)
        l.first_name as lead_first_name,
        l.last_name as lead_last_name,
        l.email as lead_email,
        l.phone1 as lead_phone,
        l.Vertriebspartner as lead_sales_partner,
        -- Care Receiver Address (wo die Pflege stattfindet - aus care_receivers)
        cr.street as care_location_street,
        cr.zip_code as care_location_zip,
        cr.location as care_location_city,
        -- Care Receiver Basic Info
        cr.first_name as care_receiver_first_name,
        cr.last_name as care_receiver_last_name,
        cr.care_level as care_receiver_care_level
    FROM 
        `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs
    JOIN 
        `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_giver_instances` cgi
        ON cs.care_giver_instance_id = cgi._id
    JOIN 
        `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.agencies` a
        ON cgi.agency_id = a._id
    JOIN
        `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.contracts` c
        ON cs.contract_id = c._id
    LEFT JOIN 
        `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_givers` cg
        ON cgi.care_giver_id = cg._id
    LEFT JOIN
        `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.households` h
        ON c.household_id = h._id
    LEFT JOIN
        `gcpxbixpflegehilfesenioren.dataform_staging.leads_and_seller_and_source_with_address` l
        ON h.lead_id = l._id
    LEFT JOIN
        `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_receivers` cr
        ON cr.household_id = h._id
    WHERE 
        cs.arrival IS NOT NULL
        AND cs.arrival != ''
        -- Nur vergangene Anreisen
        AND DATE(TIMESTAMP(cs.arrival)) < CURRENT_DATE()
        AND DATE(TIMESTAMP(cs.arrival)) >= DATE_SUB(CURRENT_DATE(), INTERVAL 6 MONTH)
        -- Care stay wurde bestätigt
        AND EXISTS (
            SELECT 1
            FROM UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track
            WHERE JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Bestätigt'
        )
        -- UND wurde NICHT vor Anreise abgebrochen
        AND NOT (
            cs.stage = 'Abgebrochen' AND 
            EXISTS (
                SELECT 1
                FROM UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track
                WHERE 
                    JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Abgebrochen'
                    AND TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at')) < TIMESTAMP(cs.arrival)
            )
        )
    """
    
    if agency_id:
        query += f" AND cgi.agency_id = '{agency_id}'"
    
    query += f"""
    ORDER BY cs.arrival DESC
    LIMIT {limit}
    OFFSET {offset}
    """
    
    query_job = client.query(query)
    results = query_job.result()
    
    care_stays = []
    for row in results:
        care_stays.append({
            "care_stay_id": row.care_stay_id,
            "agency_id": row.agency_id,
            "agency_name": row.agency_name,
            "customer_id": row.customer_id,
            "start_date": row.start_date if isinstance(row.start_date, str) else (row.start_date.isoformat() if row.start_date else None),
            "end_date": row.end_date if isinstance(row.end_date, str) else (row.end_date.isoformat() if row.end_date else None),
            "status": row.status,
            "cancellation_reason": row.cancellation_reason,
            "cancelled_before_arrival": row.cancelled_before_arrival,
            "duration_days": row.duration_days,
            # Caregiver Instance Daten
            "caregiver_instance_id": row.caregiver_instance_id,
            "caregiver_id": row.caregiver_id,
            "caregiver_birthday": row.caregiver_birthday,
            "caregiver_experience": row.caregiver_experience,
            "caregiver_experience_germany": row.caregiver_experience_germany,
            "caregiver_description": row.caregiver_description,
            "caregiver_phone": row.caregiver_phone,
            "caregiver_external_id": row.caregiver_external_id,
            "caregiver_german_score": row.caregiver_german_score,
            "caregiver_german_level": interpret_german_score(row.caregiver_german_score),
            # Caregiver Basis Daten
            "caregiver_first_name": getattr(row, 'caregiver_first_name', ''),
            "caregiver_last_name": getattr(row, 'caregiver_last_name', ''),
            "caregiver_full_name": f"{getattr(row, 'caregiver_first_name', '')} {getattr(row, 'caregiver_last_name', '')}".strip(),
            "caregiver_gender": getattr(row, 'caregiver_gender', ''),
            "caregiver_salutation": getattr(row, 'caregiver_salutation', ''),
            # Household/Customer Daten
            "household_id": getattr(row, 'household_id', ''),
            "lead_id": getattr(row, 'lead_id', ''),
            "household_designation": getattr(row, 'household_designation', ''),
            "is_customer": getattr(row, 'is_customer', ''),
            "household_notes": getattr(row, 'household_notes', ''),
            # Lead Contact Info (Ansprechpartner)
            "lead_first_name": getattr(row, 'lead_first_name', ''),
            "lead_last_name": getattr(row, 'lead_last_name', ''),
            "lead_full_name": f"{getattr(row, 'lead_first_name', '')} {getattr(row, 'lead_last_name', '')}".strip(),
            "lead_email": getattr(row, 'lead_email', ''),
            "lead_phone": getattr(row, 'lead_phone', ''),
            "lead_sales_partner": getattr(row, 'lead_sales_partner', ''),
            # Care Location (wo die Pflege stattfindet)
            "care_location_street": getattr(row, 'care_location_street', ''),
            "care_location_zip": getattr(row, 'care_location_zip', ''),
            "care_location_city": getattr(row, 'care_location_city', ''),
            "care_location_full": f"{getattr(row, 'care_location_street', '')} {getattr(row, 'care_location_zip', '')} {getattr(row, 'care_location_city', '')}".strip(),
            # Care Receiver Info (Pflegebedürftiger)
            "care_receiver_first_name": getattr(row, 'care_receiver_first_name', ''),
            "care_receiver_last_name": getattr(row, 'care_receiver_last_name', ''),
            "care_receiver_full_name": f"{getattr(row, 'care_receiver_first_name', '')} {getattr(row, 'care_receiver_last_name', '')}".strip(),
            "care_receiver_care_level": getattr(row, 'care_receiver_care_level', '')
        })
    
    return care_stays

async def get_care_stay_details(care_stay_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific care stay
    """
    client = get_bigquery_client()
    
    query = """
    SELECT 
        cs._id as care_stay_id,
        cgi.agency_id,
        a.name as agency_name,
        c.household_id as customer_id,
        h.designation as customer_name,
        CONCAT(cg.first_name, ' ', cg.last_name) as caregiver_name,
        cgi.external_id as caregiver_nationality,
        SAFE_CAST(cgi.exp AS INT64) as years_of_experience,
        cs.arrival as start_date,
        cs.departure as end_date,
        cs.stage as status,
        cs.rejection_reason as cancellation_reason
    FROM 
        `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs
    JOIN 
        `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_giver_instances` cgi
        ON cs.care_giver_instance_id = cgi._id
    JOIN 
        `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.agencies` a
        ON cgi.agency_id = a._id
    JOIN
        `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.contracts` c
        ON cs.contract_id = c._id
    LEFT JOIN 
        `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.households` h
        ON c.household_id = h._id
    LEFT JOIN 
        `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_givers` cg
        ON cgi.care_giver_id = cg._id
    WHERE 
        cs._id = @care_stay_id
    """
    
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("care_stay_id", "STRING", care_stay_id)
        ]
    )
    
    query_job = client.query(query, job_config=job_config)
    results = list(query_job.result())
    
    if not results:
        raise ValueError(f"Care stay {care_stay_id} not found")
    
    row = results[0]
    return {
        "care_stay_id": row.care_stay_id,
        "agency_id": row.agency_id,
        "agency_name": row.agency_name,
        "customer_id": row.customer_id,
        "customer_name": getattr(row, 'customer_name', 'Unknown'),
        "caregiver_id": row.caregiver_id,
        "caregiver_name": getattr(row, 'caregiver_name', 'Unknown'),
        "caregiver_nationality": getattr(row, 'nationality', 'Unknown'),
        "caregiver_experience_years": getattr(row, 'years_of_experience', 0),
        "start_date": row.start_date if isinstance(row.start_date, str) else (row.start_date.isoformat() if row.start_date else None),
        "end_date": row.end_date if isinstance(row.end_date, str) else (row.end_date.isoformat() if row.end_date else None),
        "status": row.status,
        "cancellation_reason": row.cancellation_reason
    }