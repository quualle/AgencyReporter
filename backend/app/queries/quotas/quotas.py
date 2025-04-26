"""
Quota-related queries.
These queries measure various KPIs that compare different metrics for agencies.
"""

# Query to get all postings (total)     
GET_TOTAL_POSTINGS = """
SELECT
    COUNT(*) AS posting_count
FROM
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.postings` p
WHERE
    p.created_at BETWEEN @start_date AND @end_date
"""

# Query to get reservations per agency
GET_AGENCY_RESERVATIONS = """
SELECT
    COUNT(*) AS anzahl_reservierungen,
    a.name AS agency_name
FROM
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.reservations` r
JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.visors` v ON r.visor_id = v._id
JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.agencies` a ON v.agency_id = a._id
WHERE
    a._id = @agency_id
    AND r.created_at BETWEEN @start_date AND @end_date
GROUP BY
    a.name
"""

# 2. Quote: Anzahl Reservierungen - Anzahl erfüllte Reservierungen
# Erläuterung: "Zeigt wie viel % Ihrer Reservierungen die Agentur schlussendlich auch mit einem BK Vorschlag erfüllt hat"
GET_FULFILLED_RESERVATIONS = """
SELECT
    COUNT(*) AS fulfilled_reservations_count,
    a.name AS agency_name
FROM
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.reservations` r
JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.visors` v ON r.visor_id = v._id
JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.agencies` a ON v.agency_id = a._id
WHERE
    r.fulfilled = "true"
    AND a._id = @agency_id
    AND r.created_at BETWEEN @start_date AND @end_date
GROUP BY
    a.name
"""

# 3. Quote: Anzahl Reservierungen - Anzahl abgebrochene Reservierungen
# Erläuterung: "Zeigt wie viel % ihrer eigenen Reservierungen die Agentur selbstständig abgebrochen hat. Besser als nicht abzubrechen und einfach liegen zu lassen!"
GET_WITHDRAWN_RESERVATIONS = """
SELECT
    COUNT(*) AS withdrawn_reservations_count,
    a.name AS agency_name
FROM
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.reservations` r
JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.visors` v ON r.visor_id = v._id
JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.agencies` a ON v.agency_id = a._id
WHERE
    r.withdrawn = "true"
    AND a._id = @agency_id
    AND r.created_at BETWEEN @start_date AND @end_date
GROUP BY
    a.name
"""

# 4. Quote: Anzahl Reservierungen - Anzahl reservierungen, die weder zurückgezogen noch erfüllt wurden
# Erläuterung: "Zeigt, wie viele % der reservierungen, die eine Agentur getätigt hat, dannach weder zurückgezogen noch erfüllt wurden - also einfach liegen gelassen!"
GET_PENDING_RESERVATIONS = """
SELECT
    COUNT(*) AS pending_reservations_count,
    a.name AS agency_name
FROM
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.reservations` r
JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.visors` v ON r.visor_id = v._id
JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.agencies` a ON v.agency_id = a._id
WHERE
    r.fulfilled = "false"
    AND r.cancelled = "false"
    AND r.withdrawn = "false"
    AND a._id = @agency_id
    AND r.created_at BETWEEN @start_date AND @end_date
GROUP BY
    a.name
"""

# 5. Quote: Reservierung mit Personalvorschlag erfüllt - Pflegeeinsatz angetreten
# Erläuterung: "Zeigt wie viel % der vorgeschlagenen Pflegekräfte schlussendlich auch wirklich angereist sind"
GET_STARTED_CARE_STAYS = """
SELECT 
    COUNT(*) AS successfully_started_care_stays_count,
    a.name AS agency_name
FROM 
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs
JOIN 
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.contracts` c ON cs.contract_id = c._id
JOIN 
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.agencies` a ON c.agency_id = a._id
WHERE 
    a._id = @agency_id
    AND cs.created_at BETWEEN @start_date AND @end_date
    AND cs.arrival IS NOT NULL
    AND cs.arrival != ''
    AND (
        -- Aktuell im Status "Bestätigt"
        (cs.stage = 'Bestätigt')
        OR
        -- Oder war bestätigt und wurde erst nach Anreise abgebrochen
        (cs.stage = 'Abgebrochen' AND 
         EXISTS (
             SELECT 1
             FROM UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track
             WHERE 
                 JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Abgebrochen'
                 AND TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at')) >= 
                    TIMESTAMP_ADD(TIMESTAMP(cs.arrival), INTERVAL 1 DAY)
         ))
    )
    -- Bestätigung muss vor oder am Anreisedatum erfolgt sein
    AND EXISTS (
        SELECT 1
        FROM UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track
        WHERE 
            JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Bestätigt'
            AND TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at')) <= TIMESTAMP(cs.arrival)
    )
GROUP BY
    a.name
"""

# 5. Quote (korrigiert): Nur erste Pflegeeinsätze zählen (keine Folgeeinsätze)
# Erläuterung: "Zeigt wie viel % der vorgeschlagenen Pflegekräfte schlussendlich auch wirklich angereist sind"
GET_STARTED_FIRST_CARE_STAYS = """
SELECT 
    COUNT(*) AS successfully_started_care_stays_count,
    a.name AS agency_name
FROM 
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs
JOIN 
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.contracts` c ON cs.contract_id = c._id
JOIN 
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.agencies` a ON c.agency_id = a._id
WHERE 
    a._id = @agency_id
    AND cs.created_at BETWEEN @start_date AND @end_date
    AND cs.arrival IS NOT NULL
    AND cs.arrival != ''
    -- Nur erste Einsätze, keine Folgeeinsätze
    AND cs.is_swap = "false"
    AND (
        -- Aktuell im Status "Bestätigt"
        (cs.stage = 'Bestätigt')
        OR
        -- Oder war bestätigt und wurde erst nach Anreise abgebrochen
        (cs.stage = 'Abgebrochen' AND 
         EXISTS (
             SELECT 1
             FROM UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track
             WHERE 
                 JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Abgebrochen'
                 AND TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at')) >= 
                    TIMESTAMP_ADD(TIMESTAMP(cs.arrival), INTERVAL 1 DAY)
         ))
    )
    -- Bestätigung muss vor oder am Anreisedatum erfolgt sein
    AND EXISTS (
        SELECT 1
        FROM UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track
        WHERE 
            JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Bestätigt'
            AND TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at')) <= TIMESTAMP(cs.arrival)
    )
GROUP BY
    a.name
"""

# 6. Quote: Anzahl gemachter Personalvorschläge - Anzahl VOR Einsatz abgebrochener Pflegeeinsätze
# Erläuterung: "Zeigt, wie viel % der vorgeschlagenen Pflegekräfte von der Agentur wieder abgebrochen wurden (vor Anreise)"
GET_PERSONNEL_PROPOSALS = """
SELECT
    COUNT(*) AS proposal_count,
    a.name AS agency_name
FROM
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs
JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.contracts` c ON cs.contract_id = c._id
JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.agencies` a ON c.agency_id = a._id
WHERE
    a._id = @agency_id
    AND cs.created_at BETWEEN @start_date AND @end_date
GROUP BY
    a.name
"""

GET_CANCELLED_BEFORE_ARRIVAL = """
WITH parsed AS (
  SELECT
    cs._id,
    cs.arrival,
    cs.created_at,
    cs.visor_id,
    cs.is_swap,
    JSON_EXTRACT_ARRAY(cs.tracks) AS track_array
  FROM
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs
  JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.visors` v ON cs.visor_id = v._id
  WHERE
    cs.stage = 'Abgebrochen'
    AND cs.arrival IS NOT NULL
    AND cs.arrival != ''
    AND v.agency_id = @agency_id
    AND cs.created_at BETWEEN @start_date AND @end_date
),
abbruchzeiten AS (
  SELECT
    p._id,
    p.arrival,
    p.visor_id,
    p.is_swap,
    MIN(TIMESTAMP(JSON_EXTRACT_SCALAR(track_item, '$.created_at'))) AS cancelled_at
  FROM
    parsed p,
    UNNEST(p.track_array) AS track_item
  WHERE
    JSON_EXTRACT_SCALAR(track_item, '$.differences.stage[1]') = 'Abgebrochen'
    AND TIMESTAMP(JSON_EXTRACT_SCALAR(track_item, '$.created_at')) < TIMESTAMP(p.arrival)
  GROUP BY
    p._id, p.arrival, p.visor_id, p.is_swap
),
diffs AS (
  SELECT
    _id,
    visor_id,
    is_swap,
    TIMESTAMP_DIFF(TIMESTAMP(arrival), cancelled_at, DAY) AS days_before_arrival
  FROM abbruchzeiten
  WHERE TIMESTAMP_DIFF(TIMESTAMP(arrival), cancelled_at, DAY) >= 0
    AND TIMESTAMP_DIFF(TIMESTAMP(arrival), cancelled_at, DAY) <= 30
)
SELECT
  'gesamt' AS gruppe,
  COUNT(*) AS abgebrochen_vor_arrival,
  COUNTIF(days_before_arrival < 3) AS lt_3_days,
  COUNTIF(days_before_arrival BETWEEN 3 AND 7) AS btw_3_7_days,
  COUNTIF(days_before_arrival BETWEEN 8 AND 14) AS btw_8_14_days,
  COUNTIF(days_before_arrival BETWEEN 15 AND 30) AS btw_15_30_days
FROM diffs
UNION ALL
SELECT
  'nur_erstanreise' AS gruppe,
  COUNT(*) AS abgebrochen_vor_arrival,
  COUNTIF(days_before_arrival < 3) AS lt_3_days,
  COUNTIF(days_before_arrival BETWEEN 3 AND 7) AS btw_3_7_days,
  COUNTIF(days_before_arrival BETWEEN 8 AND 14) AS btw_8_14_days,
  COUNTIF(days_before_arrival BETWEEN 15 AND 30) AS btw_15_30_days
FROM diffs
WHERE is_swap = 'false'
UNION ALL
SELECT
  'ohne_erstanreise' AS gruppe,
  COUNT(*) AS abgebrochen_vor_arrival,
  COUNTIF(days_before_arrival < 3) AS lt_3_days,
  COUNTIF(days_before_arrival BETWEEN 3 AND 7) AS btw_3_7_days,
  COUNTIF(days_before_arrival BETWEEN 8 AND 14) AS btw_8_14_days,
  COUNTIF(days_before_arrival BETWEEN 15 AND 30) AS btw_15_30_days
FROM diffs
WHERE is_swap != 'false'
"""

# 7. Quote: Pflegeeinsatz angetreten - Pflegeinsatz vollständig beendet
# Erläuterung: "Zeigt, wie viel % der zum Kunden angereisten Pflegekräfte den Einsatz wie geplant bis zum Schluss durchgezogen haben"
GET_COMPLETED_CARE_STAYS = """
WITH parsed AS (
  SELECT
    cs._id,
    cs.arrival,
    cs.departure,
    cs.created_at,
    cs.stage,
    a._id as agency_id,
    a.name as agency_name,
    JSON_EXTRACT_ARRAY(cs.tracks) AS track_array
  FROM
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs
  JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.contracts` c ON cs.contract_id = c._id
  JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.agencies` a ON c.agency_id = a._id
  WHERE
    cs.stage = 'Bestätigt'
    AND cs.arrival IS NOT NULL
    AND cs.departure IS NOT NULL
    AND TIMESTAMP(cs.departure) < CURRENT_TIMESTAMP()
    AND a._id = @agency_id
    AND cs.created_at BETWEEN @start_date AND @end_date
)
SELECT
  COUNT(*) AS completed_full_term,
  agency_name
FROM parsed
WHERE
  NOT EXISTS (
    SELECT 1
    FROM UNNEST(track_array) AS track_item
    WHERE JSON_EXTRACT_SCALAR(track_item, '$.differences.departure[0]') IS NOT NULL
  )
GROUP BY
  agency_name
"""