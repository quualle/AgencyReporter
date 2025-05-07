"""
Quotas with reasons analysis queries.
Diese Abfragen identifizieren Einsätze, die einer Abbruch- oder Beendigungsanalyse unterzogen werden sollen.
Sie bilden die Grundlage für die n8n-Workflows zur LLM-basierten Ursachenanalyse.
"""

# Abfrage für abgebrochene Ersteinsätze (mit/ohne Ersatzlieferung)
GET_CANCELLED_FIRST_STAYS = """
WITH cancelled_stays AS (
  SELECT
    cs._id,
    cs.contract_id,
    cs.visor_id,
    cs.arrival,
    cs.created_at,
    cs.is_swap,
    a._id as agency_id,
    a.name as agency_name,
    JSON_EXTRACT_ARRAY(cs.tracks) AS track_array,
    -- Ermittlung, ob ein Ersatz-Care-Stay existiert
    EXISTS (
      SELECT 1
      FROM `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs2
      WHERE 
        cs2.contract_id = cs.contract_id
        AND cs2._id != cs._id
        AND cs2.arrival > cs.arrival
        AND cs2.stage IN ('Bestätigt', 'Angenommen')
    ) AS has_replacement
  FROM
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs
  JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.contracts` c ON cs.contract_id = c._id
  JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.agencies` a ON c.agency_id = a._id
  WHERE
    cs.stage = 'Abgebrochen'
    AND cs.arrival IS NOT NULL
    AND cs.arrival != ''
    AND cs.is_swap = "false"  -- Nur Ersteinsätze
    AND a._id = @agency_id
    AND cs.created_at BETWEEN @start_date AND @end_date
),
abbruchzeiten AS (
  -- Ermittelt den frühesten Abbruchzeitpunkt für jeden Care Stay
  SELECT
    c._id,
    c.agency_id,
    c.agency_name,
    c.arrival,
    c.has_replacement,
    MIN(TIMESTAMP(JSON_EXTRACT_SCALAR(track_item, '$.created_at'))) AS cancelled_at
  FROM
    cancelled_stays c,
    UNNEST(c.track_array) AS track_item
  WHERE
    JSON_EXTRACT_SCALAR(track_item, '$.differences.stage[1]') = 'Abgebrochen'
    AND TIMESTAMP(JSON_EXTRACT_SCALAR(track_item, '$.created_at')) < TIMESTAMP(c.arrival)
  GROUP BY
    c._id, c.agency_id, c.agency_name, c.arrival, c.has_replacement
)
SELECT
  _id AS care_stay_id,
  agency_id,
  agency_name,
  FORMAT_TIMESTAMP('%Y-%m-%d', TIMESTAMP(arrival)) AS arrival_date,
  FORMAT_TIMESTAMP('%Y-%m-%d', cancelled_at) AS cancellation_date,
  TIMESTAMP_DIFF(TIMESTAMP(arrival), cancelled_at, DAY) AS days_before_arrival,
  has_replacement,
  'first_stay' AS stay_type
FROM abbruchzeiten
WHERE 
  -- Filter für Abbrüche, die nicht zu weit in der Vergangenheit liegen
  TIMESTAMP_DIFF(TIMESTAMP(arrival), cancelled_at, DAY) >= 0
  AND TIMESTAMP_DIFF(TIMESTAMP(arrival), cancelled_at, DAY) <= 30
"""

# Abfrage für abgebrochene Wechseleinsätze (mit/ohne Ersatzlieferung)
GET_CANCELLED_FOLLOW_STAYS = """
WITH cancelled_stays AS (
  SELECT
    cs._id,
    cs.contract_id,
    cs.visor_id,
    cs.arrival,
    cs.created_at,
    cs.is_swap,
    a._id as agency_id,
    a.name as agency_name,
    JSON_EXTRACT_ARRAY(cs.tracks) AS track_array,
    -- Ermittlung, ob ein Ersatz-Care-Stay existiert
    EXISTS (
      SELECT 1
      FROM `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs2
      WHERE 
        cs2.contract_id = cs.contract_id
        AND cs2._id != cs._id
        AND cs2.arrival > cs.arrival
        AND cs2.stage IN ('Bestätigt', 'Angenommen')
    ) AS has_replacement
  FROM
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs
  JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.contracts` c ON cs.contract_id = c._id
  JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.agencies` a ON c.agency_id = a._id
  WHERE
    cs.stage = 'Abgebrochen'
    AND cs.arrival IS NOT NULL
    AND cs.arrival != ''
    AND cs.is_swap = "true"  -- Nur Wechseleinsätze
    AND a._id = @agency_id
    AND cs.created_at BETWEEN @start_date AND @end_date
),
abbruchzeiten AS (
  -- Ermittelt den frühesten Abbruchzeitpunkt für jeden Care Stay
  SELECT
    c._id,
    c.agency_id,
    c.agency_name,
    c.arrival,
    c.has_replacement,
    MIN(TIMESTAMP(JSON_EXTRACT_SCALAR(track_item, '$.created_at'))) AS cancelled_at
  FROM
    cancelled_stays c,
    UNNEST(c.track_array) AS track_item
  WHERE
    JSON_EXTRACT_SCALAR(track_item, '$.differences.stage[1]') = 'Abgebrochen'
    AND TIMESTAMP(JSON_EXTRACT_SCALAR(track_item, '$.created_at')) < TIMESTAMP(c.arrival)
  GROUP BY
    c._id, c.agency_id, c.agency_name, c.arrival, c.has_replacement
)
SELECT
  _id AS care_stay_id,
  agency_id,
  agency_name,
  FORMAT_TIMESTAMP('%Y-%m-%d', TIMESTAMP(arrival)) AS arrival_date,
  FORMAT_TIMESTAMP('%Y-%m-%d', cancelled_at) AS cancellation_date,
  TIMESTAMP_DIFF(TIMESTAMP(arrival), cancelled_at, DAY) AS days_before_arrival,
  has_replacement,
  'follow_stay' AS stay_type
FROM abbruchzeiten
WHERE 
  -- Filter für Abbrüche, die nicht zu weit in der Vergangenheit liegen
  TIMESTAMP_DIFF(TIMESTAMP(arrival), cancelled_at, DAY) >= 0
  AND TIMESTAMP_DIFF(TIMESTAMP(arrival), cancelled_at, DAY) <= 30
"""

# Abfrage für nach Anreise eingekürzte Einsätze (>2 Wochen)
GET_SHORTENED_STAYS = """
WITH parsed AS (
  SELECT
    cs._id,
    cs.contract_id,
    cs.arrival,
    cs.departure,
    cs.created_at,
    cs.is_swap,
    a._id as agency_id,
    a.name as agency_name,
    JSON_EXTRACT_ARRAY(cs.tracks) AS track_array,
    -- Ermittlung, ob ein Folge-Care-Stay existiert
    EXISTS (
      SELECT 1
      FROM `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs2
      WHERE 
        cs2.contract_id = cs.contract_id
        AND cs2._id != cs._id
        AND cs2.arrival > cs.departure
        AND cs2.stage IN ('Bestätigt', 'Angenommen')
    ) AS has_follow_up
  FROM
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs
  JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.contracts` c ON cs.contract_id = c._id
  JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.agencies` a ON c.agency_id = a._id
  WHERE
    cs.arrival IS NOT NULL
    AND cs.departure IS NOT NULL
    AND cs.arrival != ''
    AND cs.departure != ''
    AND a._id = @agency_id
    AND cs.created_at BETWEEN @start_date AND @end_date
),
departure_changes AS (
  -- Für jeden Care Stay die Departure-Änderungen extrahieren und analysieren
  SELECT
    p._id,
    p.agency_id,
    p.agency_name,
    p.arrival,
    p.departure,
    p.is_swap,
    p.has_follow_up,
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
    AND TIMESTAMP(JSON_EXTRACT_SCALAR(track_item, '$.created_at')) > TIMESTAMP(p.arrival)
  GROUP BY
    p._id, p.agency_id, p.agency_name, p.arrival, p.departure, p.is_swap, p.has_follow_up
)
SELECT
  _id AS care_stay_id,
  agency_id,
  agency_name,
  FORMAT_TIMESTAMP('%Y-%m-%d', TIMESTAMP(arrival)) AS arrival_date,
  FORMAT_TIMESTAMP('%Y-%m-%d', TIMESTAMP(first_change.original_departure)) AS original_departure_date,
  FORMAT_TIMESTAMP('%Y-%m-%d', TIMESTAMP(first_change.new_departure)) AS new_departure_date,
  FORMAT_TIMESTAMP('%Y-%m-%d', TIMESTAMP(first_change.change_timestamp)) AS change_date,
  TIMESTAMP_DIFF(TIMESTAMP(first_change.original_departure), TIMESTAMP(first_change.new_departure), DAY) AS days_shortened,
  has_follow_up,
  CASE WHEN is_swap = "true" THEN 'follow_stay' ELSE 'first_stay' END AS stay_type
FROM departure_changes
WHERE
  -- Nur signifikante Verkürzungen (>14 Tage)
  TIMESTAMP(first_change.new_departure) < TIMESTAMP(first_change.original_departure)
  AND TIMESTAMP_DIFF(TIMESTAMP(first_change.original_departure), TIMESTAMP(first_change.new_departure), DAY) > 14
"""

# Umfassende Abfrage für alle Problemfälle (abgebrochene Ersteinsätze, abgebrochene Wechseleinsätze und verkürzte Einsätze)
GET_ALL_PROBLEM_CASES = """
WITH cancelled_first_stays AS (
  SELECT
    cs._id AS care_stay_id,
    c.agency_id,
    a.name AS agency_name,
    'first_stay' AS stay_type,
    'cancelled_before_arrival' AS event_type,
    FORMAT_TIMESTAMP('%Y-%m-%d', MIN(
      CASE 
        WHEN JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Abgebrochen'
        AND SAFE.TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at')) < SAFE.TIMESTAMP(cs.arrival)
        THEN SAFE.TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at'))
        ELSE NULL
      END
    )) AS event_date,
    FORMAT_TIMESTAMP('%Y-%m-%d', SAFE.TIMESTAMP(cs.arrival)) AS arrival_date,
    CAST(NULL AS STRING) AS original_departure_date,
    CAST(NULL AS STRING) AS new_departure_date,
    TIMESTAMP_DIFF(
      SAFE.TIMESTAMP(cs.arrival),
      MIN(
        CASE 
          WHEN JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Abgebrochen'
          AND SAFE.TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at')) < SAFE.TIMESTAMP(cs.arrival)
          THEN SAFE.TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at'))
          ELSE NULL
        END
      ),
      DAY
    ) AS days_difference,
    EXISTS (
      SELECT 1
      FROM `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs2
      WHERE 
        cs2.contract_id = cs.contract_id
        AND cs2._id != cs._id
        AND cs2.arrival > cs.arrival
        AND cs2.stage IN ('Bestätigt', 'Angenommen')
    ) AS has_replacement,
    FALSE AS has_follow_up,
    -- Felder für die verknüpften Daten
    cs.visor_id,
    v._id AS visor_id_from_table,
    p._id AS posting_id,
    h._id AS household_id,
    l._id AS lead_id,
    l.seller_id,
    s.Name AS seller_name,
    cs.contract_id,
    -- Neue Spalte (NULL für cancelled_first_stays)
    CAST(NULL AS INT64) AS instant_departure_after
  FROM
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs,
    UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track
  JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.contracts` c ON cs.contract_id = c._id
  JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.agencies` a ON c.agency_id = a._id
  -- Joins
  LEFT JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.visors` v ON cs.visor_id = v._id
  LEFT JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.postings` p ON v.posting_id = p._id
  LEFT JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.households` h ON p.household_id = h._id
  LEFT JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.leads` l ON h.lead_id = l._id
  -- Neuer Join für seller_name
  LEFT JOIN
    `gcpxbixpflegehilfesenioren.dataform_staging.active_sellers` s ON l.seller_id = s.seller_id
  WHERE
    cs.stage = 'Abgebrochen'
    AND cs.arrival IS NOT NULL AND cs.arrival != ''
    AND cs.is_swap = "false"
    AND cs.created_at BETWEEN @start_date AND @end_date
  GROUP BY
    cs._id, c.agency_id, a.name, cs.arrival, cs.contract_id, 
    cs.visor_id, v._id, p._id, h._id, l._id, l.seller_id, s.Name
  HAVING
    MIN(
      CASE 
        WHEN JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Abgebrochen'
        AND SAFE.TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at')) < SAFE.TIMESTAMP(cs.arrival)
        THEN SAFE.TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at'))
        ELSE NULL
      END
    ) IS NOT NULL
),

cancelled_follow_stays AS (
  SELECT
    cs._id AS care_stay_id,
    c.agency_id,
    a.name AS agency_name,
    'follow_stay' AS stay_type,
    'cancelled_before_arrival' AS event_type,
    FORMAT_TIMESTAMP('%Y-%m-%d', MIN(
      CASE 
        WHEN JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Abgebrochen'
        AND SAFE.TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at')) < SAFE.TIMESTAMP(cs.arrival)
        THEN SAFE.TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at'))
        ELSE NULL
      END
    )) AS event_date,
    FORMAT_TIMESTAMP('%Y-%m-%d', SAFE.TIMESTAMP(cs.arrival)) AS arrival_date,
    CAST(NULL AS STRING) AS original_departure_date,
    CAST(NULL AS STRING) AS new_departure_date,
    TIMESTAMP_DIFF(
      SAFE.TIMESTAMP(cs.arrival),
      MIN(
        CASE 
          WHEN JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Abgebrochen'
          AND SAFE.TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at')) < SAFE.TIMESTAMP(cs.arrival)
          THEN SAFE.TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at'))
          ELSE NULL
        END
      ),
      DAY
    ) AS days_difference,
    EXISTS (
      SELECT 1
      FROM `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs2
      WHERE 
        cs2.contract_id = cs.contract_id
        AND cs2._id != cs._id
        AND cs2.arrival > cs.arrival
        AND cs2.stage IN ('Bestätigt', 'Angenommen')
    ) AS has_replacement,
    FALSE AS has_follow_up,
    -- Felder für die verknüpften Daten
    cs.visor_id,
    v._id AS visor_id_from_table,
    p._id AS posting_id,
    h._id AS household_id,
    l._id AS lead_id,
    l.seller_id,
    s.Name AS seller_name,
    cs.contract_id,
    -- Neue Spalte (NULL für cancelled_follow_stays)
    CAST(NULL AS INT64) AS instant_departure_after
  FROM
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs,
    UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track
  JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.contracts` c ON cs.contract_id = c._id
  JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.agencies` a ON c.agency_id = a._id
  -- Joins
  LEFT JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.visors` v ON cs.visor_id = v._id
  LEFT JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.postings` p ON v.posting_id = p._id
  LEFT JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.households` h ON p.household_id = h._id
  LEFT JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.leads` l ON h.lead_id = l._id
  -- Neuer Join für seller_name
  LEFT JOIN
    `gcpxbixpflegehilfesenioren.dataform_staging.active_sellers` s ON l.seller_id = s.seller_id
  WHERE
    cs.stage = 'Abgebrochen'
    AND cs.arrival IS NOT NULL AND cs.arrival != ''
    AND cs.is_swap = "true"
    AND cs.created_at BETWEEN @start_date AND @end_date
  GROUP BY
    cs._id, c.agency_id, a.name, cs.arrival, cs.contract_id,
    cs.visor_id, v._id, p._id, h._id, l._id, l.seller_id, s.Name
  HAVING
    MIN(
      CASE 
        WHEN JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Abgebrochen'
        AND SAFE.TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at')) < SAFE.TIMESTAMP(cs.arrival)
        THEN SAFE.TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at'))
        ELSE NULL
      END
    ) IS NOT NULL
),

shortened_stays AS (
  SELECT
    cs._id AS care_stay_id,
    c.agency_id,
    a.name AS agency_name,
    CASE WHEN cs.is_swap = "true" THEN 'follow_stay' ELSE 'first_stay' END AS stay_type,
    'shortened_after_arrival' AS event_type,
    MIN(
      CASE 
        WHEN JSON_EXTRACT_SCALAR(track, '$.differences.departure[0]') IS NOT NULL
        AND SAFE.TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at')) > SAFE.TIMESTAMP(cs.arrival)
        THEN FORMAT_TIMESTAMP('%Y-%m-%d', SAFE.TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at')))
        ELSE NULL
      END
    ) AS event_date,
    FORMAT_TIMESTAMP('%Y-%m-%d', SAFE.TIMESTAMP(cs.arrival)) AS arrival_date,
    MIN(
      CASE 
        WHEN JSON_EXTRACT_SCALAR(track, '$.differences.departure[0]') IS NOT NULL
        AND SAFE.TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at')) > SAFE.TIMESTAMP(cs.arrival)
        THEN FORMAT_TIMESTAMP('%Y-%m-%d', SAFE.TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.differences.departure[0]')))
        ELSE NULL
      END
    ) AS original_departure_date,
    MIN(
      CASE 
        WHEN JSON_EXTRACT_SCALAR(track, '$.differences.departure[0]') IS NOT NULL
        AND SAFE.TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at')) > SAFE.TIMESTAMP(cs.arrival)
        THEN FORMAT_TIMESTAMP('%Y-%m-%d', SAFE.TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.differences.departure[1]')))
        ELSE NULL
      END
    ) AS new_departure_date,
    TIMESTAMP_DIFF(
      SAFE.TIMESTAMP(MIN(
        CASE 
          WHEN JSON_EXTRACT_SCALAR(track, '$.differences.departure[0]') IS NOT NULL
          AND SAFE.TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at')) > SAFE.TIMESTAMP(cs.arrival)
          THEN JSON_EXTRACT_SCALAR(track, '$.differences.departure[0]')
          ELSE NULL
        END
      )),
      SAFE.TIMESTAMP(MIN(
        CASE 
          WHEN JSON_EXTRACT_SCALAR(track, '$.differences.departure[0]') IS NOT NULL
          AND SAFE.TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at')) > SAFE.TIMESTAMP(cs.arrival)
          THEN JSON_EXTRACT_SCALAR(track, '$.differences.departure[1]')
          ELSE NULL
        END
      )),
      DAY
    ) AS days_difference,
    FALSE AS has_replacement,
    EXISTS (
      SELECT 1
      FROM `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs2
      WHERE 
        cs2.contract_id = cs.contract_id
        AND cs2._id != cs._id
        AND cs2.arrival > cs.departure
        AND cs2.stage IN ('Bestätigt', 'Angenommen')
    ) AS has_follow_up,
    -- Felder für die verknüpften Daten
    cs.visor_id,
    v._id AS visor_id_from_table,
    p._id AS posting_id,
    h._id AS household_id,
    l._id AS lead_id,
    l.seller_id,
    s.Name AS seller_name,
    cs.contract_id,
    -- Neue Spalte für sofortige Abreise (< 10 Tage)
    CASE 
      WHEN TIMESTAMP_DIFF(SAFE.TIMESTAMP(cs.departure), SAFE.TIMESTAMP(cs.arrival), DAY) < 10 
      THEN TIMESTAMP_DIFF(SAFE.TIMESTAMP(cs.departure), SAFE.TIMESTAMP(cs.arrival), DAY)
      ELSE NULL
    END AS instant_departure_after
  FROM
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs,
    UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track
  JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.contracts` c ON cs.contract_id = c._id
  JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.agencies` a ON c.agency_id = a._id
  -- Joins
  LEFT JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.visors` v ON cs.visor_id = v._id
  LEFT JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.postings` p ON v.posting_id = p._id
  LEFT JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.households` h ON p.household_id = h._id
  LEFT JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.leads` l ON h.lead_id = l._id
  -- Neuer Join für seller_name
  LEFT JOIN
    `gcpxbixpflegehilfesenioren.dataform_staging.active_sellers` s ON l.seller_id = s.seller_id
  WHERE
    cs.arrival IS NOT NULL AND cs.arrival != ''
    AND cs.departure IS NOT NULL AND cs.departure != ''
    AND cs.created_at BETWEEN @start_date AND @end_date
  GROUP BY
    cs._id, c.agency_id, a.name, cs.arrival, cs.departure, cs.is_swap, cs.contract_id,
    cs.visor_id, v._id, p._id, h._id, l._id, l.seller_id, s.Name
  HAVING
    MIN(
      CASE 
        WHEN JSON_EXTRACT_SCALAR(track, '$.differences.departure[0]') IS NOT NULL
        AND SAFE.TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at')) > SAFE.TIMESTAMP(cs.arrival)
        AND SAFE.TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.differences.departure[1]')) < SAFE.TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.differences.departure[0]'))
        AND TIMESTAMP_DIFF(
          SAFE.TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.differences.departure[0]')),
          SAFE.TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.differences.departure[1]')),
          DAY
        ) > 7
        THEN 1
        ELSE NULL
      END
    ) IS NOT NULL
)

SELECT * FROM cancelled_first_stays
UNION ALL
SELECT * FROM cancelled_follow_stays
UNION ALL
SELECT * FROM shortened_stays
ORDER BY event_date DESC
"""

# Abfrage zum Abrufen von Ticket-Daten zu einem bestimmten Einsatz
GET_TICKETS_FOR_CARE_STAY = """
SELECT
  t._id AS ticket_id, 
  t.title,
  t.description,
  t.created_at,
  t.updated_at,
  t.status,
  t.priority,
  t.assignee,
  t.creator,
  t.tags
FROM
  `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.tickets` t
WHERE
  t.related_care_stay_id = @care_stay_id
ORDER BY
  t.created_at DESC
"""

# Abfrage zum Abrufen der Kundenemailadresse aus den Leaddaten
GET_CUSTOMER_EMAIL_FROM_LEAD = """
SELECT
  l.email AS customer_email,
  l.first_name,
  l.last_name
FROM
  `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.leads` l
JOIN
  `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.contracts` c ON l._id = c.lead_id
JOIN
  `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs ON c._id = cs.contract_id
WHERE
  cs._id = @care_stay_id
LIMIT 1
"""

# Schema für die Speicherung der Analyseergebnisse
# Diese Tabelle würde in BigQuery erstellt werden, um die Ergebnisse der LLM-Analyse zu speichern
CREATE_ANALYSIS_RESULTS_TABLE = """
CREATE TABLE IF NOT EXISTS `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.cancellation_analysis_results` (
  care_stay_id STRING NOT NULL,
  agency_id STRING NOT NULL,
  agency_name STRING NOT NULL,
  stay_type STRING NOT NULL,  -- 'first_stay' oder 'follow_stay'
  event_type STRING NOT NULL, -- 'cancelled_before_arrival', 'shortened_after_arrival', 'terminated_early'
  has_replacement BOOLEAN,    -- Nur relevant bei cancelled_before_arrival
  has_follow_up BOOLEAN,      -- Nur relevant bei shortened_after_arrival
  event_date DATE NOT NULL,   -- Datum des Abbruchs oder der Verkürzung
  arrival_date DATE,          -- Geplantes Anreisedatum
  original_departure_date DATE, -- Ursprüngliches Abreisedatum (bei Verkürzungen)
  new_departure_date DATE,    -- Neues Abreisedatum (bei Verkürzungen)
  days_difference INT,        -- Tage vor Anreise bei Abbrüchen / Tage der Verkürzung
  primary_reason STRING NOT NULL,  -- Hauptgrund (LLM-Kategorisierung)
  secondary_reason STRING,     -- Sekundärer Grund (falls vorhanden)
  confidence_score FLOAT64,    -- Konfidenzwert der LLM-Analyse (0-1)
  analysis_timestamp TIMESTAMP NOT NULL, -- Zeitpunkt der Analyse
  raw_communications JSON,     -- Originale Kommunikationsdaten (ggf. anonymisiert)
  llm_analysis_result JSON,    -- Vollständiges LLM-Analyseergebnis
  created_by STRING NOT NULL,  -- z.B. 'n8n-workflow'
  notes STRING                 -- Zusätzliche Hinweise
)
"""

# Query zu Sammlung aller wichtigen Einsätze - Kombinierte Version
GET_ALL_IMPORTANT_EVENTS = """
-- Abgebrochene Ersteinsätze
WITH cancelled_first_stays AS (
  SELECT
    cs._id AS care_stay_id,
    c.agency_id,
    a.name AS agency_name,
    'first_stay' AS stay_type,
    'cancelled_before_arrival' AS event_type,
    FORMAT_TIMESTAMP('%Y-%m-%d', MIN(
      CASE 
        WHEN JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Abgebrochen'
        AND TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at')) < TIMESTAMP(cs.arrival)
        THEN TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at'))
        ELSE NULL
      END
    )) AS event_date,
    FORMAT_TIMESTAMP('%Y-%m-%d', TIMESTAMP(cs.arrival)) AS arrival_date,
    NULL AS original_departure_date,
    NULL AS new_departure_date,
    TIMESTAMP_DIFF(
      TIMESTAMP(cs.arrival),
      MIN(
        CASE 
          WHEN JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Abgebrochen'
          AND TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at')) < TIMESTAMP(cs.arrival)
          THEN TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at'))
          ELSE NULL
        END
      ),
      DAY
    ) AS days_difference,
    EXISTS (
      SELECT 1
      FROM `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs2
      WHERE 
        cs2.contract_id = cs.contract_id
        AND cs2._id != cs._id
        AND cs2.arrival > cs.arrival
        AND cs2.stage IN ('Bestätigt', 'Angenommen')
    ) AS has_replacement,
    FALSE AS has_follow_up
  FROM
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs,
    UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track
  JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.contracts` c ON cs.contract_id = c._id
  JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.agencies` a ON c.agency_id = a._id
  WHERE
    cs.stage = 'Abgebrochen'
    AND cs.arrival IS NOT NULL AND cs.arrival != ''
    AND cs.is_swap = "false"
    AND cs.created_at BETWEEN @start_date AND @end_date
  GROUP BY
    cs._id, c.agency_id, a.name, cs.arrival, cs.contract_id
  HAVING
    MIN(
      CASE 
        WHEN JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Abgebrochen'
        AND TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at')) < TIMESTAMP(cs.arrival)
        THEN TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at'))
        ELSE NULL
      END
    ) IS NOT NULL
),

-- Abgebrochene Wechseleinsätze
cancelled_follow_stays AS (
  SELECT
    cs._id AS care_stay_id,
    c.agency_id,
    a.name AS agency_name,
    'follow_stay' AS stay_type,
    'cancelled_before_arrival' AS event_type,
    FORMAT_TIMESTAMP('%Y-%m-%d', MIN(
      CASE 
        WHEN JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Abgebrochen'
        AND TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at')) < TIMESTAMP(cs.arrival)
        THEN TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at'))
        ELSE NULL
      END
    )) AS event_date,
    FORMAT_TIMESTAMP('%Y-%m-%d', TIMESTAMP(cs.arrival)) AS arrival_date,
    NULL AS original_departure_date,
    NULL AS new_departure_date,
    TIMESTAMP_DIFF(
      TIMESTAMP(cs.arrival),
      MIN(
        CASE 
          WHEN JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Abgebrochen'
          AND TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at')) < TIMESTAMP(cs.arrival)
          THEN TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at'))
          ELSE NULL
        END
      ),
      DAY
    ) AS days_difference,
    EXISTS (
      SELECT 1
      FROM `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs2
      WHERE 
        cs2.contract_id = cs.contract_id
        AND cs2._id != cs._id
        AND cs2.arrival > cs.arrival
        AND cs2.stage IN ('Bestätigt', 'Angenommen')
    ) AS has_replacement,
    FALSE AS has_follow_up
  FROM
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs,
    UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track
  JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.contracts` c ON cs.contract_id = c._id
  JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.agencies` a ON c.agency_id = a._id
  WHERE
    cs.stage = 'Abgebrochen'
    AND cs.arrival IS NOT NULL AND cs.arrival != ''
    AND cs.is_swap = "true"
    AND cs.created_at BETWEEN @start_date AND @end_date
  GROUP BY
    cs._id, c.agency_id, a.name, cs.arrival, cs.contract_id
  HAVING
    MIN(
      CASE 
        WHEN JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Abgebrochen'
        AND TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at')) < TIMESTAMP(cs.arrival)
        THEN TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at'))
        ELSE NULL
      END
    ) IS NOT NULL
),

-- Nach Anreise eingekürzte Einsätze
shortened_stays AS (
  SELECT
    cs._id AS care_stay_id,
    c.agency_id,
    a.name AS agency_name,
    CASE WHEN cs.is_swap = "true" THEN 'follow_stay' ELSE 'first_stay' END AS stay_type,
    'shortened_after_arrival' AS event_type,
    MIN(
      CASE 
        WHEN JSON_EXTRACT_SCALAR(track, '$.differences.departure[0]') IS NOT NULL
        AND TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at')) > TIMESTAMP(cs.arrival)
        THEN FORMAT_TIMESTAMP('%Y-%m-%d', TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at')))
        ELSE NULL
      END
    ) AS event_date,
    FORMAT_TIMESTAMP('%Y-%m-%d', TIMESTAMP(cs.arrival)) AS arrival_date,
    MIN(
      CASE 
        WHEN JSON_EXTRACT_SCALAR(track, '$.differences.departure[0]') IS NOT NULL
        AND TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at')) > TIMESTAMP(cs.arrival)
        THEN FORMAT_TIMESTAMP('%Y-%m-%d', TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.differences.departure[0]')))
        ELSE NULL
      END
    ) AS original_departure_date,
    MIN(
      CASE 
        WHEN JSON_EXTRACT_SCALAR(track, '$.differences.departure[0]') IS NOT NULL
        AND TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at')) > TIMESTAMP(cs.arrival)
        THEN FORMAT_TIMESTAMP('%Y-%m-%d', TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.differences.departure[1]')))
        ELSE NULL
      END
    ) AS new_departure_date,
    TIMESTAMP_DIFF(
      TIMESTAMP(MIN(
        CASE 
          WHEN JSON_EXTRACT_SCALAR(track, '$.differences.departure[0]') IS NOT NULL
          AND TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at')) > TIMESTAMP(cs.arrival)
          THEN JSON_EXTRACT_SCALAR(track, '$.differences.departure[0]')
          ELSE NULL
        END
      )),
      TIMESTAMP(MIN(
        CASE 
          WHEN JSON_EXTRACT_SCALAR(track, '$.differences.departure[0]') IS NOT NULL
          AND TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at')) > TIMESTAMP(cs.arrival)
          THEN JSON_EXTRACT_SCALAR(track, '$.differences.departure[1]')
          ELSE NULL
        END
      )),
      DAY
    ) AS days_difference,
    FALSE AS has_replacement,
    EXISTS (
      SELECT 1
      FROM `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs2
      WHERE 
        cs2.contract_id = cs.contract_id
        AND cs2._id != cs._id
        AND cs2.arrival > cs.departure
        AND cs2.stage IN ('Bestätigt', 'Angenommen')
    ) AS has_follow_up
  FROM
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs,
    UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track
  JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.contracts` c ON cs.contract_id = c._id
  JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.agencies` a ON c.agency_id = a._id
  WHERE
    cs.arrival IS NOT NULL AND cs.arrival != ''
    AND cs.departure IS NOT NULL AND cs.departure != ''
    AND cs.created_at BETWEEN @start_date AND @end_date
  GROUP BY
    cs._id, c.agency_id, a.name, cs.arrival, cs.departure, cs.is_swap, cs.contract_id
  HAVING
    MIN(
      CASE 
        WHEN JSON_EXTRACT_SCALAR(track, '$.differences.departure[0]') IS NOT NULL
        AND TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at')) > TIMESTAMP(cs.arrival)
        AND TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.differences.departure[1]')) < TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.differences.departure[0]'))
        AND TIMESTAMP_DIFF(
          TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.differences.departure[0]')),
          TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.differences.departure[1]')),
          DAY
        ) > 14
        THEN 1
        ELSE NULL
      END
    ) IS NOT NULL
)

-- Vereinigung aller relevanten Einsätze
SELECT * FROM cancelled_first_stays
UNION ALL
SELECT * FROM cancelled_follow_stays
UNION ALL
SELECT * FROM shortened_stays
ORDER BY event_date DESC
"""

# Query zum Einfügen der Analyseergebnisse in die Ergebnistabelle
# Dies würde in n8n verwendet werden, um die Ergebnisse der LLM-Analyse in BigQuery zu speichern
INSERT_ANALYSIS_RESULT = """
INSERT INTO `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.cancellation_analysis_results` (
  care_stay_id,
  agency_id,
  agency_name,
  stay_type,
  event_type,
  has_replacement,
  has_follow_up,
  event_date,
  arrival_date,
  original_departure_date,
  new_departure_date,
  days_difference,
  primary_reason,
  secondary_reason,
  confidence_score,
  analysis_timestamp,
  raw_communications,
  llm_analysis_result,
  created_by,
  notes
) VALUES (
  @care_stay_id,
  @agency_id,
  @agency_name,
  @stay_type,
  @event_type,
  @has_replacement,
  @has_follow_up,
  @event_date,
  @arrival_date,
  @original_departure_date,
  @new_departure_date,
  @days_difference,
  @primary_reason,
  @secondary_reason,
  @confidence_score,
  CURRENT_TIMESTAMP(),
  @raw_communications,
  @llm_analysis_result,
  @created_by,
  @notes
)
"""

# Abfrage zum Abrufen der Top-Abbruchgründe pro Agentur für das Dashboard
GET_TOP_CANCELLATION_REASONS = """
SELECT
  agency_id,
  agency_name,
  event_type,
  primary_reason,
  COUNT(*) AS count,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY agency_id, event_type), 1) AS percentage
FROM
  `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.cancellation_analysis_results`
WHERE
  agency_id = @agency_id
  AND event_date BETWEEN @start_date AND @end_date
GROUP BY
  agency_id, agency_name, event_type, primary_reason
ORDER BY
  event_type, count DESC
"""

# Abfrage zum Vergleich der Abbruchgründe einer Agentur mit dem Durchschnitt
GET_CANCELLATION_REASONS_COMPARISON = """
WITH agency_reasons AS (
  SELECT
    'agency' AS source,
    event_type,
    primary_reason,
    COUNT(*) AS count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY event_type), 1) AS percentage
  FROM
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.cancellation_analysis_results`
  WHERE
    agency_id = @agency_id
    AND event_date BETWEEN @start_date AND @end_date
  GROUP BY
    event_type, primary_reason
),
overall_reasons AS (
  SELECT
    'average' AS source,
    event_type,
    primary_reason,
    COUNT(*) AS count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY event_type), 1) AS percentage
  FROM
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.cancellation_analysis_results`
  WHERE
    event_date BETWEEN @start_date AND @end_date
  GROUP BY
    event_type, primary_reason
)
SELECT 
  COALESCE(a.event_type, o.event_type) AS event_type,
  COALESCE(a.primary_reason, o.primary_reason) AS primary_reason,
  a.count AS agency_count,
  a.percentage AS agency_percentage,
  o.count AS average_count,
  o.percentage AS average_percentage,
  COALESCE(a.percentage, 0) - COALESCE(o.percentage, 0) AS percentage_difference
FROM
  agency_reasons a
FULL OUTER JOIN
  overall_reasons o ON a.event_type = o.event_type AND a.primary_reason = o.primary_reason
ORDER BY
  event_type, 
  COALESCE(a.count, 0) DESC
"""

# Alias für die bestehende Funktionalität
GET_ALL_PROBLEM_CASES = GET_ALL_IMPORTANT_EVENTS 