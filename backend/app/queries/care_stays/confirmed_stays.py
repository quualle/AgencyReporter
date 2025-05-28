from app.utils.bigquery_connection import get_bigquery_client
from app.dependencies import get_settings


def get_confirmed_stays_query(start_date: str, end_date: str, agency_id: str = None) -> str:
    """
    Holt die Anzahl der bestätigten Care Stays pro Agentur im Zeitraum.
    
    Args:
        start_date: Startdatum im Format YYYY-MM-DD
        end_date: Enddatum im Format YYYY-MM-DD  
        agency_id: Optional - Filter für eine spezifische Agentur
        
    Returns:
        SQL-Query als String
    """
    settings = get_settings()
    dataset = f"{settings.bigquery_project_id}.{settings.bigquery_dataset}"
    
    query = f"""
    WITH confirmed_stays AS (
        SELECT
            c.agency_id,
            a.name AS agency_name,
            COUNT(DISTINCT cs._id) AS confirmed_stays_count
        FROM `{dataset}.care_stays` cs
        JOIN `{dataset}.contracts` c ON cs.contract_id = c._id
        JOIN `{dataset}.agencies` a ON c.agency_id = a._id
        WHERE
            -- Zeitraum-Filter basierend auf created_at (wann der Care Stay erstellt wurde)
            SUBSTR(cs.created_at, 1, 10) BETWEEN @start_date AND @end_date
            -- Nur bestätigte Care Stays
            AND EXISTS (
                SELECT 1
                FROM UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track
                WHERE JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Bestätigt'
            )
            {"AND c.agency_id = @agency_id" if agency_id else ""}
        GROUP BY c.agency_id, a.name
    )
    SELECT 
        agency_id,
        agency_name,
        confirmed_stays_count,
        -- Ranking für Vergleichbarkeit
        RANK() OVER (ORDER BY confirmed_stays_count DESC) AS rank_by_count
    FROM confirmed_stays
    ORDER BY confirmed_stays_count DESC
    """
    
    return query


def execute_confirmed_stays_query(start_date: str, end_date: str, agency_id: str = None) -> list:
    """
    Führt die Query für bestätigte Care Stays aus.
    
    Args:
        start_date: Startdatum
        end_date: Enddatum
        agency_id: Optional - Filter für eine spezifische Agentur
        
    Returns:
        Liste mit Agenturen und deren bestätigten Care Stays
    """
    client = get_bigquery_client()
    
    query = get_confirmed_stays_query(start_date, end_date, agency_id)
    
    from google.cloud import bigquery
    job_config = bigquery.QueryJobConfig()
    job_config.query_parameters = [
        bigquery.ScalarQueryParameter("start_date", "STRING", start_date),
        bigquery.ScalarQueryParameter("end_date", "STRING", end_date),
    ]
    
    if agency_id:
        job_config.query_parameters.append(
            bigquery.ScalarQueryParameter("agency_id", "STRING", agency_id)
        )
    
    results = client.query(query, job_config=job_config).result()
    
    return [dict(row) for row in results]