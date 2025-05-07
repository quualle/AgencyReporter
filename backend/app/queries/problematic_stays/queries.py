"""
SQL Queries für Problematic Stays Analysen.
Diese Abfragen greifen auf die von n8n-Workflows erstellte Tabelle 'problematic_stays' zu
und liefern relevante Analysen über problematische Pflegeeinsätze.
"""

# Abfrage für die Übersichtsstatistik problematischer Einsätze
GET_PROBLEMATIC_STAYS_OVERVIEW = """
WITH total_carestays AS (
  -- Gesamtanzahl aller Pflegeeinsätze pro Agentur im Zeitraum
  SELECT
    agency_id,
    COUNT(*) AS total_count
  FROM
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays`
  WHERE
    agency_id = @agency_id OR @agency_id IS NULL
    AND created_at BETWEEN @start_date AND @end_date
  GROUP BY
    agency_id
),
problematic_stats AS (
  -- Statistiken zu problematischen Einsätzen
  SELECT
    p.agency_id,
    p.agency_name,
    COUNT(*) AS total_problematic,
    
    -- Aufschlüsselung nach Event-Typ
    COUNTIF(p.event_type = 'cancelled_before_arrival') AS cancelled_before_arrival_count,
    COUNTIF(p.event_type = 'shortened_after_arrival') AS shortened_after_arrival_count,
    
    -- Aufschlüsselung nach Stay-Typ
    COUNTIF(p.stay_type = 'first_stay') AS first_stay_count,
    COUNTIF(p.stay_type = 'follow_stay') AS follow_stay_count,
    
    -- Kombinierte Aufschlüsselung
    COUNTIF(p.event_type = 'cancelled_before_arrival' AND p.stay_type = 'first_stay') AS cancelled_first_stays,
    COUNTIF(p.event_type = 'cancelled_before_arrival' AND p.stay_type = 'follow_stay') AS cancelled_follow_stays,
    COUNTIF(p.event_type = 'shortened_after_arrival' AND p.stay_type = 'first_stay') AS shortened_first_stays,
    COUNTIF(p.event_type = 'shortened_after_arrival' AND p.stay_type = 'follow_stay') AS shortened_follow_stays,
    
    -- Ersatz-Statistiken
    COUNTIF(p.has_replacement = TRUE) AS with_replacement_count,
    COUNTIF(p.has_follow_up = TRUE) AS with_follow_up_count,
    
    -- Sofortige Abreise (<10 Tage)
    COUNTIF(p.instant_departure_after IS NOT NULL) AS instant_departure_count,
    AVG(CASE WHEN p.instant_departure_after IS NOT NULL THEN p.instant_departure_after ELSE NULL END) AS avg_instant_departure_days,
    
    -- Zeitleiche Analysen
    AVG(CASE WHEN p.event_type = 'cancelled_before_arrival' THEN p.days_difference ELSE NULL END) AS avg_days_before_arrival,
    AVG(CASE WHEN p.event_type = 'shortened_after_arrival' THEN p.days_difference ELSE NULL END) AS avg_shortened_days,
    
    -- Kundenzufriedenheitsstatistik (aus JSON extrahiert)
    COUNTIF(JSON_EXTRACT_SCALAR(p.analysis_result, '$.customer_satisfaction') = 'satisfied') AS satisfied_count,
    COUNTIF(JSON_EXTRACT_SCALAR(p.analysis_result, '$.customer_satisfaction') = 'not_satisfied') AS not_satisfied_count,
    COUNTIF(JSON_EXTRACT_SCALAR(p.analysis_result, '$.customer_satisfaction') = 'n/a') AS satisfaction_na_count,
    
    -- Durchschnittliche Confidence-Scores
    AVG(CAST(JSON_EXTRACT_SCALAR(p.analysis_result, '$.confidence') AS INT64)) AS avg_reason_confidence,
    AVG(CAST(JSON_EXTRACT_SCALAR(p.analysis_result, '$.confidence_cussat') AS INT64)) AS avg_satisfaction_confidence
  FROM
    `gcpxbixpflegehilfesenioren.Agencyreporter.problematic_stays` p
  WHERE
    p.analysis_status = 'completed'
    AND (p.agency_id = @agency_id OR @agency_id IS NULL)
    AND (p.event_date BETWEEN @start_date AND @end_date OR 
         (@start_date IS NULL AND @end_date IS NULL))
  GROUP BY
    p.agency_id, p.agency_name
)

SELECT
  p.agency_id,
  p.agency_name,
  p.total_problematic,
  tc.total_count AS total_carestays,
  SAFE_DIVIDE(p.total_problematic, tc.total_count) * 100 AS problematic_percentage,
  
  -- Event-Typ-Statistiken
  p.cancelled_before_arrival_count,
  p.shortened_after_arrival_count,
  SAFE_DIVIDE(p.cancelled_before_arrival_count, p.total_problematic) * 100 AS cancelled_percentage,
  SAFE_DIVIDE(p.shortened_after_arrival_count, p.total_problematic) * 100 AS shortened_percentage,
  
  -- Stay-Typ-Statistiken
  p.first_stay_count,
  p.follow_stay_count,
  SAFE_DIVIDE(p.first_stay_count, p.total_problematic) * 100 AS first_stay_percentage,
  SAFE_DIVIDE(p.follow_stay_count, p.total_problematic) * 100 AS follow_stay_percentage,
  
  -- Kombinierte Statistiken
  p.cancelled_first_stays,
  p.cancelled_follow_stays,
  p.shortened_first_stays,
  p.shortened_follow_stays,
  
  -- Ersatz-Statistiken
  p.with_replacement_count,
  p.with_follow_up_count,
  SAFE_DIVIDE(p.with_replacement_count, p.cancelled_before_arrival_count) * 100 AS replacement_percentage,
  SAFE_DIVIDE(p.with_follow_up_count, p.shortened_after_arrival_count) * 100 AS follow_up_percentage,
  
  -- Sofortige Abreise
  p.instant_departure_count,
  p.avg_instant_departure_days,
  SAFE_DIVIDE(p.instant_departure_count, p.shortened_after_arrival_count) * 100 AS instant_departure_percentage,
  
  -- Zeitliche Analysen
  p.avg_days_before_arrival,
  p.avg_shortened_days,
  
  -- Kundenzufriedenheitsstatistik
  p.satisfied_count,
  p.not_satisfied_count,
  p.satisfaction_na_count,
  SAFE_DIVIDE(p.satisfied_count, p.total_problematic) * 100 AS satisfied_percentage,
  SAFE_DIVIDE(p.not_satisfied_count, p.total_problematic) * 100 AS not_satisfied_percentage,
  
  -- Confidence-Scores
  p.avg_reason_confidence,
  p.avg_satisfaction_confidence
FROM
  problematic_stats p
LEFT JOIN
  total_carestays tc ON p.agency_id = tc.agency_id
ORDER BY
  p.total_problematic DESC
"""

# Abfrage für die Häufigkeitsverteilung der Abbruchgründe
GET_PROBLEMATIC_STAYS_REASONS = """
SELECT
  p.agency_id,
  p.agency_name,
  p.event_type,
  JSON_EXTRACT_SCALAR(p.analysis_result, '$.selected_reason') AS reason,
  COUNT(*) AS count,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (
    PARTITION BY p.agency_id, p.event_type
  ), 1) AS percentage,
  AVG(CAST(JSON_EXTRACT_SCALAR(p.analysis_result, '$.confidence') AS INT64)) AS avg_confidence
FROM
  `gcpxbixpflegehilfesenioren.Agencyreporter.problematic_stays` p
WHERE
  p.analysis_status = 'completed'
  AND (p.agency_id = @agency_id OR @agency_id IS NULL)
  AND (p.event_date BETWEEN @start_date AND @end_date OR 
       (@start_date IS NULL AND @end_date IS NULL))
  AND (p.event_type = @event_type OR @event_type IS NULL)
GROUP BY
  p.agency_id, p.agency_name, p.event_type, reason
ORDER BY
  p.agency_id, p.event_type, count DESC
"""

# Abfrage für die zeitliche Analyse
GET_PROBLEMATIC_STAYS_TIME_ANALYSIS = """
SELECT
  p.agency_id,
  p.agency_name,
  p.event_type,
  p.stay_type,
  FORMAT_DATE('%Y-%m', DATE(p.event_date)) AS event_month,
  COUNT(*) AS count,
  AVG(p.days_difference) AS avg_days_difference,
  COUNTIF(p.instant_departure_after IS NOT NULL) AS instant_departure_count,
  AVG(CASE WHEN p.instant_departure_after IS NOT NULL THEN p.instant_departure_after ELSE NULL END) AS avg_instant_departure_days,
  COUNTIF(JSON_EXTRACT_SCALAR(p.analysis_result, '$.customer_satisfaction') = 'satisfied') AS satisfied_count,
  COUNTIF(JSON_EXTRACT_SCALAR(p.analysis_result, '$.customer_satisfaction') = 'not_satisfied') AS not_satisfied_count
FROM
  `gcpxbixpflegehilfesenioren.Agencyreporter.problematic_stays` p
WHERE
  p.analysis_status = 'completed'
  AND (p.agency_id = @agency_id OR @agency_id IS NULL)
  AND (p.event_date BETWEEN @start_date AND @end_date OR 
       (@start_date IS NULL AND @end_date IS NULL))
  AND (p.event_type = @event_type OR @event_type IS NULL)
  AND (p.stay_type = @stay_type OR @stay_type IS NULL)
GROUP BY
  p.agency_id, p.agency_name, p.event_type, p.stay_type, event_month
ORDER BY
  p.agency_id, event_month, p.event_type, p.stay_type
""" 