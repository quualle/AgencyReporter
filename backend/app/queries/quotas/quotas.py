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

# New query to get unique posting reservations per agency
GET_UNIQUE_POSTING_RESERVATIONS = """
SELECT
    COUNT(DISTINCT v.posting_id) AS anzahl_reservierungen,
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

# Neue Query: Anzahl akzeptierter/angenommener Pflegeeinsätze
# Erläuterung: Zählt Einsätze, die irgendwann den Status "Angenommen" erreicht haben
GET_ACCEPTED_CARE_STAYS = """
SELECT 
    COUNT(DISTINCT cs._id) AS accepted_care_stays_count,
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
    AND EXISTS (
        SELECT 1
        FROM UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track
        WHERE 
            JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Angenommen'
    )
GROUP BY
    a.name
"""

# Neue Query: Anzahl akzeptierter Ersteinsätze (Nur is_swap = false)
GET_ACCEPTED_FIRST_CARE_STAYS = """
SELECT 
    COUNT(DISTINCT cs._id) AS accepted_first_care_stays_count,
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
    AND cs.is_swap = "false"
    -- Stellt sicher, dass auch ein Visor vorhanden ist
    AND cs.visor_id IS NOT NULL
    -- Prüft explizit, dass eine Statusänderung zu 'Angenommen' stattgefunden hat
    AND EXISTS (
        SELECT 1
        FROM UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track
        WHERE 
            JSON_EXTRACT_SCALAR(track, '$.differences.stage[0]') IS NOT NULL
            AND JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Angenommen'
    )
GROUP BY
    a.name
"""

# Neue Query: Anzahl akzeptierter Folgeeinsätze (Nur is_swap = true)
GET_ACCEPTED_FOLLOW_CARE_STAYS = """
SELECT 
    COUNT(DISTINCT cs._id) AS accepted_follow_care_stays_count,
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
    AND cs.is_swap = "true"
    AND EXISTS (
        SELECT 1
        FROM UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track
        WHERE 
            JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Angenommen'
    )
GROUP BY
    a.name
"""

# Neue Query: Anzahl bestätigter Pflegeeinsätze
# Erläuterung: Zählt Einsätze, die irgendwann den Status "Bestätigt" erreicht haben.
GET_CONFIRMED_CARE_STAYS = """
SELECT 
    COUNT(DISTINCT cs._id) AS confirmed_care_stays_count,
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
    AND EXISTS (
        SELECT 1
        FROM UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track
        WHERE 
            JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Bestätigt'
    )
GROUP BY
    a.name
"""

# Neue Query: Anzahl bestätigter Ersteinsätze (Nur is_swap = false)
GET_CONFIRMED_FIRST_CARE_STAYS = """
SELECT 
    COUNT(DISTINCT cs._id) AS confirmed_first_care_stays_count,
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
    AND cs.is_swap = "false"
    AND EXISTS (
        SELECT 1
        FROM UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track
        WHERE 
            JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Bestätigt'
    )
GROUP BY
    a.name
"""

# Neue Query: Anzahl bestätigter Folgeeinsätze (Nur is_swap = true)
GET_CONFIRMED_FOLLOW_CARE_STAYS = """
SELECT 
    COUNT(DISTINCT cs._id) AS confirmed_follow_care_stays_count,
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
    AND cs.is_swap = "true"
    AND EXISTS (
        SELECT 1
        FROM UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track
        WHERE 
            JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Bestätigt'
    )
GROUP BY
    a.name
"""

# Neue Query: Zählung tatsächlich angereister Ersteinsätze
# Zählt Care Stays, die:
# 1. ein Anreisedatum haben
# 2. den Status "Bestätigt" erreicht haben
# 3. nicht vor dem Anreisedatum abgebrochen wurden
GET_SIMPLE_ARRIVED_FIRST_CARE_STAYS = """
SELECT 
    COUNT(*) AS simple_arrived_first_care_stays_count,
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
    -- Muss den Status "Bestätigt" erreicht haben
    AND EXISTS (
        SELECT 1
        FROM UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track
        WHERE JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Bestätigt'
    )
    -- Wurde nicht vor Anreise abgebrochen
    AND NOT (
        cs.stage = 'Abgebrochen' AND 
        EXISTS (
            -- Sucht nach einem Tracking-Event "Abgebrochen" VOR dem Anreisedatum
            SELECT 1
            FROM UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track
            WHERE 
                JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Abgebrochen'
                AND TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at')) < TIMESTAMP(cs.arrival)
        )
    )
GROUP BY
    a.name
"""

# Neue Query: Zählung tatsächlich angereister Folgeeinsätze
GET_SIMPLE_ARRIVED_FOLLOW_CARE_STAYS = """
SELECT 
    COUNT(*) AS simple_arrived_follow_care_stays_count,
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
    -- Nur Folgeeinsätze
    AND cs.is_swap = "true"
    -- Muss den Status "Bestätigt" erreicht haben
    AND EXISTS (
        SELECT 1
        FROM UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track
        WHERE JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Bestätigt'
    )
    -- Wurde nicht vor Anreise abgebrochen
    AND NOT (
        cs.stage = 'Abgebrochen' AND 
        EXISTS (
            -- Sucht nach einem Tracking-Event "Abgebrochen" VOR dem Anreisedatum
            SELECT 1
            FROM UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track
            WHERE 
                JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Abgebrochen'
                AND TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at')) < TIMESTAMP(cs.arrival)
        )
    )
GROUP BY
    a.name
"""

# Neue Query: Zählung aller tatsächlich angereisten Einsätze
GET_SIMPLE_ARRIVED_ALL_CARE_STAYS = """
SELECT 
    COUNT(*) AS simple_arrived_all_care_stays_count,
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
    -- Muss den Status "Bestätigt" erreicht haben
    AND EXISTS (
        SELECT 1
        FROM UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track
        WHERE JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Bestätigt'
    )
    -- Wurde nicht vor Anreise abgebrochen
    AND NOT (
        cs.stage = 'Abgebrochen' AND 
        EXISTS (
            -- Sucht nach einem Tracking-Event "Abgebrochen" VOR dem Anreisedatum
            SELECT 1
            FROM UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track
            WHERE 
                JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Abgebrochen'
                AND TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at')) < TIMESTAMP(cs.arrival)
        )
    )
GROUP BY
    a.name
"""

# Neue Query: Anzahl erfüllter Reservierungen mit Ersteinsätzen
# Wichtig: Wir filtern sowohl r.created_at ALS AUCH cs.created_at mit demselben Zeitraum!
GET_FULFILLED_RESERVATIONS_FIRST_STAYS = """
WITH valid_care_stays AS (
    -- Nur Care Stays im ausgewählten Zeitraum
    SELECT
        cs._id,
        cs.visor_id
    FROM 
        `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs
    WHERE 
        cs.created_at BETWEEN @start_date AND @end_date
        AND cs.is_swap = "false"
)
SELECT 
    COUNT(DISTINCT vcs._id) AS fulfilled_first_reservations_count,
    a.name AS agency_name
FROM
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.reservations` r
JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.visors` v ON r.visor_id = v._id
JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.agencies` a ON v.agency_id = a._id
-- JOIN mit der validen Care Stays Tabelle
JOIN
    valid_care_stays vcs ON v._id = vcs.visor_id
WHERE
    r.fulfilled = "true"
    AND a._id = @agency_id
    -- Zusätzlicher Zeitraumfilter auch für Reservierungen
    AND r.created_at BETWEEN @start_date AND @end_date
GROUP BY 
    a.name
"""

# Neue Query: Anzahl erfüllter Reservierungen mit Folgeeinsätzen (is_swap = true)
GET_FULFILLED_RESERVATIONS_FOLLOW_STAYS = """
SELECT
    COUNT(*) AS fulfilled_follow_reservations_count,
    a.name AS agency_name
FROM
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.reservations` r
JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.visors` v ON r.visor_id = v._id
JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs ON v._id = cs.visor_id
JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.agencies` a ON v.agency_id = a._id
WHERE
    r.fulfilled = "true"
    AND a._id = @agency_id
    AND r.created_at BETWEEN @start_date AND @end_date
    AND cs.is_swap = "true"
GROUP BY
    a.name
"""

# 6. Quote: Anzahl gemachter Personalvorschläge - Anzahl VOR Einsatz abgebrochener Pflegeeinsätze
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
# Hinweis: Verlängerungen oder leichte Verkürzungen (bis zu 2 Wochen) gelten als erfolgreich durchgeführt
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
),
departure_changes AS (
  -- Für jeden Care Stay die Departure-Änderungen extrahieren und analysieren
  SELECT
    p._id,
    -- Ursprüngliches departure-Datum aus den tracks ermitteln (erste Version)
    ARRAY_AGG(
      STRUCT(
        JSON_EXTRACT_SCALAR(track_item, '$.differences.departure[0]') AS original_departure,
        JSON_EXTRACT_SCALAR(track_item, '$.differences.departure[1]') AS new_departure,
        JSON_EXTRACT_SCALAR(track_item, '$.created_at') AS change_timestamp
      )
      ORDER BY JSON_EXTRACT_SCALAR(track_item, '$.created_at') ASC
    )[OFFSET(0)] AS first_change
  FROM
    parsed p,
    UNNEST(p.track_array) AS track_item
  WHERE
    JSON_EXTRACT_SCALAR(track_item, '$.differences.departure[0]') IS NOT NULL
  GROUP BY
    p._id
)
SELECT
  COUNT(*) AS completed_full_term,
  agency_name
FROM parsed p
LEFT JOIN departure_changes dc ON p._id = dc._id
WHERE
  -- Entweder keine Änderung am Departure-Datum
  dc._id IS NULL
  OR
  -- Oder Verlängerung (neues Datum später als ursprüngliches)
  TIMESTAMP(dc.first_change.new_departure) > TIMESTAMP(dc.first_change.original_departure)
  OR
  -- Oder nur leichte Verkürzung (maximal 14 Tage früher)
  TIMESTAMP_DIFF(
    TIMESTAMP(dc.first_change.original_departure),
    TIMESTAMP(dc.first_change.new_departure),
    DAY
  ) <= 14
GROUP BY
  agency_name
"""

GET_OVERALL_CANCELLED_BEFORE_ARRIVAL_STATS = """
-- Berechnet die durchschnittlichen Abbruchzahlen und Buckets über ALLE Agenturen
WITH parsed AS (
    -- Wählt relevante Felder aus care_stays und fügt agency_id hinzu
    SELECT
        cs._id, cs.arrival, cs.created_at, cs.is_swap, v.agency_id,
        JSON_EXTRACT_ARRAY(cs.tracks) AS track_array
    FROM `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs
    JOIN `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.visors` v ON cs.visor_id = v._id
    WHERE cs.stage = 'Abgebrochen'
      AND cs.arrival IS NOT NULL AND cs.arrival != ''
      AND cs.created_at BETWEEN @start_date AND @end_date -- Filter nach CareStay-Erstellung
),
abbruchzeiten AS (
    -- Ermittelt den frühesten Abbruchzeitpunkt vor Anreise für jeden CareStay
    SELECT
        p._id, p.arrival, p.agency_id, p.is_swap,
        MIN(TIMESTAMP(JSON_EXTRACT_SCALAR(track_item, '$.created_at'))) AS cancelled_at
    FROM parsed p, UNNEST(p.track_array) AS track_item
    WHERE JSON_EXTRACT_SCALAR(track_item, '$.differences.stage[1]') = 'Abgebrochen'
      AND TIMESTAMP(JSON_EXTRACT_SCALAR(track_item, '$.created_at')) < TIMESTAMP(p.arrival)
    GROUP BY p._id, p.arrival, p.agency_id, p.is_swap
),
diffs_per_agency AS (
    -- Berechnet die Tage vor Anreise pro Abbruch und gruppiert nach Agentur
    SELECT
        agency_id,
        is_swap,
        TIMESTAMP_DIFF(TIMESTAMP(arrival), cancelled_at, DAY) AS days_before_arrival
    FROM abbruchzeiten
    WHERE TIMESTAMP_DIFF(TIMESTAMP(arrival), cancelled_at, DAY) >= 0
      AND TIMESTAMP_DIFF(TIMESTAMP(arrival), cancelled_at, DAY) <= 30
),
buckets_per_agency AS (
    -- Zählt Abbrüche pro Bucket FÜR JEDE Agentur
    SELECT
        agency_id,
        COUNT(*) AS total_cancelled,
        COUNTIF(days_before_arrival < 3) AS lt_3_days,
        COUNTIF(days_before_arrival BETWEEN 3 AND 7) AS btw_3_7_days,
        COUNTIF(days_before_arrival BETWEEN 8 AND 14) AS btw_8_14_days,
        COUNTIF(days_before_arrival BETWEEN 15 AND 30) AS btw_15_30_days
    FROM diffs_per_agency
    GROUP BY agency_id
),
proposals_per_agency AS (
    -- Zählt Vorschläge FÜR JEDE Agentur
    SELECT
        a._id as agency_id,
        COUNT(cs._id) AS proposal_count
    FROM `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs
    JOIN `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.contracts` c ON cs.contract_id = c._id
    JOIN `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.agencies` a ON c.agency_id = a._id
    WHERE cs.created_at BETWEEN @start_date AND @end_date
    GROUP BY a._id
)
-- Berechnet die Durchschnittswerte über alle Agenturen
SELECT
    AVG(bpa.total_cancelled) AS avg_total_cancelled,
    AVG(bpa.lt_3_days) AS avg_lt_3_days,
    AVG(bpa.btw_3_7_days) AS avg_btw_3_7_days,
    AVG(bpa.btw_8_14_days) AS avg_btw_8_14_days,
    AVG(bpa.btw_15_30_days) AS avg_btw_15_30_days,
    AVG(ppa.proposal_count) AS avg_proposal_count,
    SAFE_DIVIDE(AVG(bpa.total_cancelled), AVG(ppa.proposal_count)) AS avg_cancellation_ratio
FROM buckets_per_agency bpa
JOIN proposals_per_agency ppa ON bpa.agency_id = ppa.agency_id
"""

# Neue Query: Anzahl aller Personalvorschläge (Care Stays)
GET_PV_COUNT = """
SELECT 
    COUNT(DISTINCT cs._id) AS pv_count,
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

# Neue Query: Anzahl der Personalvorschläge für Ersteinsätze
GET_PV_FIRST_COUNT = """
SELECT 
    COUNT(DISTINCT cs._id) AS pv_first_count,
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
    AND cs.is_swap = "false"
    -- Stellt sicher, dass auch ein Visor vorhanden ist
    AND cs.visor_id IS NOT NULL
GROUP BY
    a.name
"""

# Neue Query: Anzahl der Personalvorschläge für Folgeeinsätze
GET_PV_FOLLOW_COUNT = """
SELECT 
    COUNT(DISTINCT cs._id) AS pv_follow_count,
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
    AND cs.is_swap = "true"
    -- Stellt sicher, dass auch ein Visor vorhanden ist
    AND cs.visor_id IS NOT NULL
GROUP BY
    a.name
"""