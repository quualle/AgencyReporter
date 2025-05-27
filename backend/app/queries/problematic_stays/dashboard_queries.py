"""
Dashboard-spezifische Queries für die Problematic Stays Übersicht.
Diese Queries sind speziell für die Dashboard-Widgets optimiert und zeigen
konsistente Zahlen basierend auf bestätigten Care Stays.
"""

# Dashboard-spezifische Query für alle drei Widgets
GET_DASHBOARD_PROBLEMATIC_OVERVIEW = """
WITH confirmed_stays AS (
  -- Basis: Alle bestätigten Care Stays im Zeitraum
  SELECT
    c.agency_id,
    a.name AS agency_name,
    COUNT(DISTINCT cs._id) AS total_confirmed_stays
  FROM
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs
  JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.contracts` c ON cs.contract_id = c._id
  JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.agencies` a ON c.agency_id = a._id
  WHERE
    SUBSTR(cs.created_at, 1, 10) BETWEEN @start_date AND @end_date
    -- Nur Care Stays, die jemals bestätigt wurden
    AND EXISTS (
      SELECT 1
      FROM UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track
      WHERE JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Bestätigt'
    )
  GROUP BY
    c.agency_id, a.name
),
problematic_counts AS (
  -- Zähle die verschiedenen Problemtypen aus der problematic_stays Tabelle
  SELECT
    p.agency_id,
    COUNT(DISTINCT CASE WHEN p.event_type = 'cancelled_before_arrival' THEN p.care_stay_id END) AS cancelled_before_arrival_count,
    COUNT(DISTINCT CASE WHEN p.event_type = 'shortened_after_arrival' THEN p.care_stay_id END) AS shortened_after_arrival_count,
    COUNT(DISTINCT p.care_stay_id) AS total_problematic_count
  FROM
    `gcpxbixpflegehilfesenioren.AgencyReporter.problematic_stays` p
  WHERE
    p.analysis_status = 'analyzed'
    AND p.created_at BETWEEN @start_date AND @end_date
  GROUP BY
    p.agency_id
)

SELECT
  cs.agency_id,
  cs.agency_name,
  cs.total_confirmed_stays,
  COALESCE(pc.cancelled_before_arrival_count, 0) AS cancelled_before_arrival_count,
  COALESCE(pc.shortened_after_arrival_count, 0) AS shortened_after_arrival_count,
  COALESCE(pc.total_problematic_count, 0) AS total_problematic_count,
  
  -- Prozentsätze für Sortierung
  SAFE_DIVIDE(COALESCE(pc.total_problematic_count, 0), cs.total_confirmed_stays) * 100 AS problematic_percentage,
  SAFE_DIVIDE(COALESCE(pc.cancelled_before_arrival_count, 0), cs.total_confirmed_stays) * 100 AS cancellation_percentage,
  SAFE_DIVIDE(COALESCE(pc.shortened_after_arrival_count, 0), cs.total_confirmed_stays) * 100 AS early_termination_percentage
FROM
  confirmed_stays cs
LEFT JOIN
  problematic_counts pc ON cs.agency_id = pc.agency_id
WHERE
  cs.total_confirmed_stays > 0
ORDER BY
  problematic_percentage DESC, cs.agency_name
"""