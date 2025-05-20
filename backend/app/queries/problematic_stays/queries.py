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
    c.agency_id,
    COUNT(*) AS total_count
  FROM
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs
  JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.contracts` c ON cs.contract_id = c._id
  WHERE
    (c.agency_id = @agency_id OR @agency_id IS NULL)
    AND SUBSTR(cs.created_at, 1, 10) BETWEEN @start_date AND @end_date
  GROUP BY
    c.agency_id
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
    COUNTIF(p.event_type = 'cancelled_before_arrival' AND p.stay_type = 'first_stay') AS first_stay_cancelled_count,
    COUNTIF(p.event_type = 'cancelled_before_arrival' AND p.stay_type = 'follow_stay') AS follow_stay_cancelled_count,
    COUNTIF(p.event_type = 'shortened_after_arrival' AND p.stay_type = 'first_stay') AS first_stay_shortened_count,
    COUNTIF(p.event_type = 'shortened_after_arrival' AND p.stay_type = 'follow_stay') AS follow_stay_shortened_count,
    
    -- Ersatz-Statistiken
    COUNTIF(p.has_replacement = TRUE) AS with_replacement_count,
    COUNTIF(p.has_follow_up = TRUE) AS with_follow_up_count,
    
    -- Sofortige Abreise (<10 Tage)
    COUNTIF(p.instant_departure_after IS NOT NULL) AS instant_departure_count,
    AVG(CASE WHEN p.instant_departure_after IS NOT NULL THEN p.instant_departure_after ELSE NULL END) AS avg_instant_departure_days,
    
    -- Sofortige Abreise (<10 Tage) aufgeschlüsselt nach Tagen
    COUNTIF(p.instant_departure_after = 1) AS instant_departure_day_1,
    COUNTIF(p.instant_departure_after = 2) AS instant_departure_day_2,
    COUNTIF(p.instant_departure_after = 3) AS instant_departure_day_3,
    COUNTIF(p.instant_departure_after = 4) AS instant_departure_day_4,
    COUNTIF(p.instant_departure_after = 5) AS instant_departure_day_5,
    COUNTIF(p.instant_departure_after = 6) AS instant_departure_day_6,
    COUNTIF(p.instant_departure_after = 7) AS instant_departure_day_7,
    COUNTIF(p.instant_departure_after = 8) AS instant_departure_day_8,
    COUNTIF(p.instant_departure_after = 9) AS instant_departure_day_9,
    
    -- Vorlaufzeit und Verkürzungsdauer zeitliche Gruppierung
    -- Für Abbrüche vor Anreise
    COUNTIF(p.event_type = 'cancelled_before_arrival' AND p.days_difference <= 3) AS cancelled_1_3_days,
    COUNTIF(p.event_type = 'cancelled_before_arrival' AND p.days_difference > 3 AND p.days_difference <= 7) AS cancelled_4_7_days,
    COUNTIF(p.event_type = 'cancelled_before_arrival' AND p.days_difference > 7 AND p.days_difference <= 14) AS cancelled_8_14_days,
    COUNTIF(p.event_type = 'cancelled_before_arrival' AND p.days_difference > 14 AND p.days_difference <= 30) AS cancelled_15_30_days,
    COUNTIF(p.event_type = 'cancelled_before_arrival' AND p.days_difference > 30) AS cancelled_over_30_days,
    
    -- Für Verkürzungen nach Anreise
    COUNTIF(p.event_type = 'shortened_after_arrival' AND p.days_difference >= 14 AND p.days_difference <= 21) AS shortened_14_21_days,
    COUNTIF(p.event_type = 'shortened_after_arrival' AND p.days_difference > 21 AND p.days_difference <= 30) AS shortened_22_30_days,
    COUNTIF(p.event_type = 'shortened_after_arrival' AND p.days_difference > 30 AND p.days_difference <= 60) AS shortened_31_60_days,
    COUNTIF(p.event_type = 'shortened_after_arrival' AND p.days_difference > 60 AND p.days_difference <= 90) AS shortened_61_90_days,
    COUNTIF(p.event_type = 'shortened_after_arrival' AND p.days_difference > 90) AS shortened_over_90_days,
    
    -- Zeitleiche Analysen
    AVG(CASE WHEN p.event_type = 'cancelled_before_arrival' THEN p.days_difference ELSE NULL END) AS avg_days_before_arrival,
    AVG(CASE WHEN p.event_type = 'shortened_after_arrival' THEN p.days_difference ELSE NULL END) AS avg_shortened_days,
    
    -- Zeitleiche Analysen nach stay_type
    AVG(CASE WHEN p.event_type = 'cancelled_before_arrival' AND p.stay_type = 'first_stay' THEN p.days_difference ELSE NULL END) AS first_stay_avg_days_before_arrival,
    AVG(CASE WHEN p.event_type = 'cancelled_before_arrival' AND p.stay_type = 'follow_stay' THEN p.days_difference ELSE NULL END) AS follow_stay_avg_days_before_arrival,
    AVG(CASE WHEN p.event_type = 'shortened_after_arrival' AND p.stay_type = 'first_stay' THEN p.days_difference ELSE NULL END) AS first_stay_avg_shortened_days,
    AVG(CASE WHEN p.event_type = 'shortened_after_arrival' AND p.stay_type = 'follow_stay' THEN p.days_difference ELSE NULL END) AS follow_stay_avg_shortened_days,
    
    -- Kundenzufriedenheitsstatistik (aus JSON extrahiert)
    COUNTIF(JSON_EXTRACT_SCALAR(p.analysis_result, '$.customer_satisfaction') = 'satisfied') AS satisfied_count,
    COUNTIF(JSON_EXTRACT_SCALAR(p.analysis_result, '$.customer_satisfaction') = 'not_satisfied') AS not_satisfied_count,
    COUNTIF(JSON_EXTRACT_SCALAR(p.analysis_result, '$.customer_satisfaction') = 'n/a') AS satisfaction_na_count,
    
    -- Durchschnittliche Confidence-Scores
    AVG(CAST(JSON_EXTRACT_SCALAR(p.analysis_result, '$.confidence') AS INT64)) AS avg_reason_confidence,
    AVG(CAST(JSON_EXTRACT_SCALAR(p.analysis_result, '$.confidence_cussat') AS INT64)) AS avg_satisfaction_confidence
  FROM
    `gcpxbixpflegehilfesenioren.AgencyReporter.problematic_stays` p
  WHERE
    p.analysis_status = 'analyzed'
    AND (p.agency_id = @agency_id OR @agency_id IS NULL)
    AND p.event_date BETWEEN @start_date AND @end_date
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
  SAFE_DIVIDE(p.cancelled_before_arrival_count, tc.total_count) * 100 AS cancelled_percentage,
  SAFE_DIVIDE(p.shortened_after_arrival_count, tc.total_count) * 100 AS shortened_percentage,
  
  -- Stay-Typ-Statistiken
  p.first_stay_count,
  p.follow_stay_count,
  SAFE_DIVIDE(p.first_stay_count, p.total_problematic) * 100 AS first_stay_percentage,
  SAFE_DIVIDE(p.follow_stay_count, p.total_problematic) * 100 AS follow_stay_percentage,
  
  -- Kombinierte Statistiken
  p.first_stay_cancelled_count,
  p.follow_stay_cancelled_count,
  p.first_stay_shortened_count,
  p.follow_stay_shortened_count,
  
  -- Ersatz-Statistiken
  p.with_replacement_count,
  p.with_follow_up_count,
  SAFE_DIVIDE(p.with_replacement_count, tc.total_count) * 100 AS replacement_percentage,
  SAFE_DIVIDE(p.with_follow_up_count, p.shortened_after_arrival_count) * 100 AS follow_up_percentage,
  
  -- Sofortige Abreise
  p.instant_departure_count,
  p.avg_instant_departure_days,
  SAFE_DIVIDE(p.instant_departure_count, tc.total_count) * 100 AS instant_departure_percentage,
  
  -- Sofortige Abreise nach Tagen
  p.instant_departure_day_1,
  p.instant_departure_day_2,
  p.instant_departure_day_3,
  p.instant_departure_day_4,
  p.instant_departure_day_5,
  p.instant_departure_day_6,
  p.instant_departure_day_7,
  p.instant_departure_day_8,
  p.instant_departure_day_9,
  
  -- Gruppierung nach Tagen
  p.cancelled_1_3_days,
  p.cancelled_4_7_days,
  p.cancelled_8_14_days,
  p.cancelled_15_30_days,
  p.cancelled_over_30_days,
  p.shortened_14_21_days,
  p.shortened_22_30_days,
  p.shortened_31_60_days,
  p.shortened_61_90_days,
  p.shortened_over_90_days,
  
  -- Zeitliche Analysen
  p.avg_days_before_arrival,
  p.avg_shortened_days,
  p.first_stay_avg_days_before_arrival,
  p.follow_stay_avg_days_before_arrival,
  p.first_stay_avg_shortened_days,
  p.follow_stay_avg_shortened_days,
  
  -- Kundenzufriedenheitsstatistik
  p.satisfied_count,
  p.not_satisfied_count,
  p.satisfaction_na_count,
  SAFE_DIVIDE(p.satisfied_count, tc.total_count) * 100 AS satisfied_percentage,
  SAFE_DIVIDE(p.not_satisfied_count, tc.total_count) * 100 AS not_satisfied_percentage,
  
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
  `gcpxbixpflegehilfesenioren.AgencyReporter.problematic_stays` p
WHERE
  p.analysis_status = 'analyzed'
  AND (p.agency_id = @agency_id OR @agency_id IS NULL)
  AND p.event_date BETWEEN @start_date AND @end_date
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
  `gcpxbixpflegehilfesenioren.AgencyReporter.problematic_stays` p
WHERE
  p.analysis_status = 'analyzed'
  AND (p.agency_id = @agency_id OR @agency_id IS NULL)
  AND p.event_date BETWEEN @start_date AND @end_date
  AND (p.event_type = @event_type OR @event_type IS NULL)
  AND (p.stay_type = @stay_type OR @stay_type IS NULL)
GROUP BY
  p.agency_id, p.agency_name, p.event_type, p.stay_type, event_month
ORDER BY
  p.agency_id, event_month, p.event_type, p.stay_type
"""

# Abfrage für die Heatmap der Abbruchgründe nach Agentur
GET_PROBLEMATIC_STAYS_HEATMAP = """
SELECT
  p.agency_id,
  p.agency_name,
  JSON_EXTRACT_SCALAR(p.analysis_result, '$.selected_reason') AS reason,
  p.event_type,
  COUNT(*) AS count,
  SUM(COUNT(*)) OVER (PARTITION BY p.agency_id) AS agency_total,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY p.agency_id), 1) AS percentage
FROM
  `gcpxbixpflegehilfesenioren.AgencyReporter.problematic_stays` p
WHERE
  p.analysis_status = 'analyzed'
  AND (p.agency_id = @agency_id OR @agency_id IS NULL)
  AND p.event_date BETWEEN @start_date AND @end_date
  AND (p.event_type = @event_type OR @event_type IS NULL)
  AND (p.stay_type = @stay_type OR @stay_type IS NULL)
GROUP BY
  p.agency_id, p.agency_name, reason, p.event_type
ORDER BY
  agency_total DESC, p.agency_id, reason
"""

# Abfrage für sofortige Abreisen (< 10 Tage nach Anreise)
GET_PROBLEMATIC_STAYS_INSTANT_DEPARTURES = """
SELECT
  p.agency_id,
  p.agency_name,
  p.instant_departure_after,
  COUNT(*) AS count,
  JSON_EXTRACT_SCALAR(p.analysis_result, '$.selected_reason') AS reason,
  JSON_EXTRACT_SCALAR(p.analysis_result, '$.customer_satisfaction') AS customer_satisfaction,
  AVG(CAST(JSON_EXTRACT_SCALAR(p.analysis_result, '$.confidence') AS INT64)) AS avg_confidence,
  COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY p.agency_id) AS percentage_of_agency_problems
FROM
  `gcpxbixpflegehilfesenioren.AgencyReporter.problematic_stays` p
WHERE
  p.analysis_status = 'analyzed'
  AND p.event_type = 'shortened_after_arrival'
  AND p.instant_departure_after IS NOT NULL
  AND p.instant_departure_after <= 9
  AND (p.agency_id = @agency_id OR @agency_id IS NULL)
  AND p.event_date BETWEEN @start_date AND @end_date
GROUP BY
  p.agency_id, p.agency_name, p.instant_departure_after, reason, customer_satisfaction
ORDER BY
  p.agency_id, p.instant_departure_after
"""

# Abfrage für Ersatz- und Folgeanalyse
GET_PROBLEMATIC_STAYS_REPLACEMENT_ANALYSIS = """
SELECT
  p.agency_id,
  p.agency_name,
  p.event_type,
  p.stay_type,
  COUNT(*) AS total_count,
  COUNTIF(p.has_replacement = TRUE) AS with_replacement_count,
  COUNTIF(p.has_follow_up = TRUE) AS with_follow_up_count,
  SAFE_DIVIDE(COUNTIF(p.has_replacement = TRUE), COUNTIF(p.event_type = 'cancelled_before_arrival')) * 100 AS replacement_percentage,
  SAFE_DIVIDE(COUNTIF(p.has_follow_up = TRUE), COUNTIF(p.event_type = 'shortened_after_arrival')) * 100 AS follow_up_percentage
FROM
  `gcpxbixpflegehilfesenioren.AgencyReporter.problematic_stays` p
WHERE
  p.analysis_status = 'analyzed'
  AND (p.agency_id = @agency_id OR @agency_id IS NULL)
  AND p.event_date BETWEEN @start_date AND @end_date
GROUP BY
  p.agency_id, p.agency_name, p.event_type, p.stay_type
ORDER BY
  replacement_percentage DESC, follow_up_percentage DESC
"""

# Abfrage für Kundenzufriedenheitsanalyse
GET_PROBLEMATIC_STAYS_CUSTOMER_SATISFACTION = """
SELECT
  p.agency_id,
  p.agency_name,
  JSON_EXTRACT_SCALAR(p.analysis_result, '$.customer_satisfaction') AS satisfaction,
  JSON_EXTRACT_SCALAR(p.analysis_result, '$.selected_reason') AS reason,
  p.event_type,
  p.stay_type,
  COUNT(*) AS count,
  AVG(CAST(JSON_EXTRACT_SCALAR(p.analysis_result, '$.confidence_cussat') AS INT64)) AS avg_confidence,
  COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY p.agency_id) AS percentage
FROM
  `gcpxbixpflegehilfesenioren.AgencyReporter.problematic_stays` p
WHERE
  p.analysis_status = 'analyzed'
  AND (p.agency_id = @agency_id OR @agency_id IS NULL)
  AND p.event_date BETWEEN @start_date AND @end_date
GROUP BY
  p.agency_id, p.agency_name, satisfaction, reason, p.event_type, p.stay_type
ORDER BY
  p.agency_id, count DESC
"""

# Abfrage für Trend-Analyse über die Zeit
GET_PROBLEMATIC_STAYS_TREND_ANALYSIS = """
WITH total_carestays_per_month AS (
  -- Gesamtanzahl aller Pflegeeinsätze pro Agentur und Monat im Zeitraum
  SELECT
    c.agency_id,
    FORMAT_DATE('%Y-%m', DATE(cs.created_at)) AS event_month,
    COUNT(*) AS total_count
  FROM
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs
  JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.contracts` c ON cs.contract_id = c._id
  WHERE
    (c.agency_id = @agency_id OR @agency_id IS NULL)
    AND DATE(cs.created_at) BETWEEN @start_date AND @end_date
  GROUP BY
    c.agency_id, event_month
)

SELECT
  p.agency_id,
  p.agency_name,
  FORMAT_DATE('%Y-%m', DATE(p.event_date)) AS event_month,
  p.event_type,
  p.stay_type,
  COUNT(*) AS count,
  tc.total_count AS total_carestays,
  SAFE_DIVIDE(COUNT(*), tc.total_count) * 100 AS percentage,
  COUNTIF(p.has_replacement = TRUE) AS with_replacement_count,
  COUNTIF(p.has_follow_up = TRUE) AS with_follow_up_count,
  COUNTIF(p.instant_departure_after IS NOT NULL AND p.instant_departure_after <= 9) AS instant_departure_count,
  COUNTIF(JSON_EXTRACT_SCALAR(p.analysis_result, '$.customer_satisfaction') = 'satisfied') AS satisfied_count,
  COUNTIF(JSON_EXTRACT_SCALAR(p.analysis_result, '$.customer_satisfaction') = 'not_satisfied') AS not_satisfied_count,
  AVG(CAST(JSON_EXTRACT_SCALAR(p.analysis_result, '$.confidence') AS INT64)) AS avg_reason_confidence
FROM
  `gcpxbixpflegehilfesenioren.AgencyReporter.problematic_stays` p
LEFT JOIN
  total_carestays_per_month tc ON p.agency_id = tc.agency_id AND FORMAT_DATE('%Y-%m', DATE(p.event_date)) = tc.event_month
WHERE
  p.analysis_status = 'analyzed'
  AND (p.agency_id = @agency_id OR @agency_id IS NULL)
  AND p.event_date BETWEEN @start_date AND @end_date
  AND (p.event_type = @event_type OR @event_type IS NULL)
  AND (p.stay_type = @stay_type OR @stay_type IS NULL)
GROUP BY
  p.agency_id, p.agency_name, event_month, p.event_type, p.stay_type, tc.total_count
ORDER BY
  p.agency_id, event_month
""" 