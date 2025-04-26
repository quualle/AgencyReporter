"""
Reaction time queries.
These queries measure the time between different events in the agency process.
"""

# Sample reaction time query templates 
# These will be replaced with actual queries when provided

# 1. Time between job posting and agency reservation
TIME_POSTING_TO_RESERVATION = """
WITH first_arrival_per_visor AS (
  SELECT
    visor_id,
    MIN(TIMESTAMP(arrival)) AS first_arrival
  FROM
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays`
  WHERE
    arrival IS NOT NULL
  GROUP BY
    visor_id
)
SELECT
  a._id AS agency_id,
  a.name AS agency_name,
  AVG(TIMESTAMP_DIFF(TIMESTAMP(r.created_at), TIMESTAMP(p.created_at), HOUR)) AS avg_time_to_reservation
FROM
  `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.reservations` r
JOIN
  `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.visors` v ON r.visor_id = v._id
JOIN
  `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.agencies` a ON v.agency_id = a._id
JOIN
  `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.postings` p ON v.posting_id = p._id
JOIN
  first_arrival_per_visor fa ON v._id = fa.visor_id
WHERE
  a._id = @agency_id
  AND TIMESTAMP(r.created_at) < fa.first_arrival
  AND TIMESTAMP(p.created_at) < fa.first_arrival
  AND TIMESTAMP(r.created_at) >= TIMESTAMP(@start_date)
  AND TIMESTAMP(r.created_at) < TIMESTAMP(@end_date)
GROUP BY
  a._id, a.name
"""

# 2. Time between reservation and proposal submission
TIME_RESERVATION_TO_PROPOSAL = """
-- Calculate time between agency reservation and proposal submission
-- This is a template and will be updated with the actual query
"""

# 3. Time between reservation and first proposal (CareStay)
TIME_RESERVATION_TO_FIRST_PROPOSAL = """
WITH first_arrival_per_visor AS (
  SELECT
    visor_id,
    MIN(TIMESTAMP(arrival)) AS first_arrival
  FROM
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays`
  WHERE
    arrival IS NOT NULL
  GROUP BY
    visor_id
)
SELECT
  a._id AS agency_id,
  a.name AS agency_name,
  AVG(
    TIMESTAMP_DIFF(
      (
        SELECT MIN(TIMESTAMP(cs.presented_at))
        FROM `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs
        WHERE cs.visor_id = v._id
          AND TIMESTAMP(cs.presented_at) >= TIMESTAMP(r.created_at)
          AND TIMESTAMP(cs.presented_at) < fa.first_arrival
      ),
      TIMESTAMP(r.created_at),
      HOUR
    )
  ) AS avg_time_to_first_proposal
FROM
  `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.reservations` r
JOIN
  `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.visors` v ON r.visor_id = v._id
JOIN
  `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.agencies` a ON v.agency_id = a._id
JOIN
  first_arrival_per_visor fa ON v._id = fa.visor_id
WHERE
  a._id = @agency_id
  AND TIMESTAMP(r.created_at) < fa.first_arrival
  AND TIMESTAMP(r.created_at) >= TIMESTAMP(@start_date)
  AND TIMESTAMP(r.created_at) < TIMESTAMP(@end_date)
  -- Filter: Reservierung maximal 1 Monat vor Proposal
  AND TIMESTAMP(r.created_at) >= TIMESTAMP_SUB(
    (
      SELECT MIN(TIMESTAMP(cs.presented_at))
      FROM `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs
      WHERE cs.visor_id = v._id
        AND TIMESTAMP(cs.presented_at) >= TIMESTAMP(r.created_at)
        AND TIMESTAMP(cs.presented_at) < fa.first_arrival
    ),
    INTERVAL 30 DAY
  )
GROUP BY
  a._id, a.name
"""

# Additional reaction time queries will be added here as they are provided

TIME_POSTING_TO_RESERVATION_STATS = """
WITH first_arrival_per_visor AS (
  SELECT
    visor_id,
    MIN(TIMESTAMP(arrival)) AS first_arrival
  FROM
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays`
  WHERE
    arrival IS NOT NULL
  GROUP BY
    visor_id
),
diffs AS (
  SELECT
    TIMESTAMP_DIFF(TIMESTAMP(r.created_at), TIMESTAMP(p.created_at), HOUR) AS diff_hours
  FROM
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.reservations` r
  JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.visors` v ON r.visor_id = v._id
  JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.agencies` a ON v.agency_id = a._id
  JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.postings` p ON v.posting_id = p._id
  JOIN
    first_arrival_per_visor fa ON v._id = fa.visor_id
  WHERE
    a._id = @agency_id
    AND TIMESTAMP(r.created_at) < fa.first_arrival
    AND TIMESTAMP(p.created_at) < fa.first_arrival
    AND TIMESTAMP(r.created_at) >= TIMESTAMP(@start_date)
    AND TIMESTAMP(r.created_at) < TIMESTAMP(@end_date)
    AND TIMESTAMP(p.created_at) >= TIMESTAMP_SUB(TIMESTAMP(r.created_at), INTERVAL 30 DAY)
)
SELECT
  APPROX_QUANTILES(diff_hours, 2)[OFFSET(1)] AS median_hours,
  AVG(diff_hours) AS avg_hours
FROM diffs
"""

TIME_RESERVATION_TO_FIRST_PROPOSAL_STATS = """
WITH first_arrival_per_visor AS (
  SELECT
    visor_id,
    MIN(TIMESTAMP(arrival)) AS first_arrival
  FROM
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays`
  WHERE
    arrival IS NOT NULL
  GROUP BY
    visor_id
),
diffs AS (
  SELECT
    TIMESTAMP_DIFF(
      (
        SELECT MIN(TIMESTAMP(cs.presented_at))
        FROM `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs
        WHERE cs.visor_id = v._id
          AND TIMESTAMP(cs.presented_at) >= TIMESTAMP(r.created_at)
          AND TIMESTAMP(cs.presented_at) < fa.first_arrival
      ),
      TIMESTAMP(r.created_at),
      HOUR
    ) AS diff_hours
  FROM
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.reservations` r
  JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.visors` v ON r.visor_id = v._id
  JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.agencies` a ON v.agency_id = a._id
  JOIN
    first_arrival_per_visor fa ON v._id = fa.visor_id
  WHERE
    a._id = @agency_id
    AND TIMESTAMP(r.created_at) < fa.first_arrival
    AND TIMESTAMP(r.created_at) >= TIMESTAMP(@start_date)
    AND TIMESTAMP(r.created_at) < TIMESTAMP(@end_date)
    -- Filter: Reservierung maximal 1 Monat vor Proposal
    AND TIMESTAMP(r.created_at) >= TIMESTAMP_SUB(
      (
        SELECT MIN(TIMESTAMP(cs.presented_at))
        FROM `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs
        WHERE cs.visor_id = v._id
          AND TIMESTAMP(cs.presented_at) >= TIMESTAMP(r.created_at)
          AND TIMESTAMP(cs.presented_at) < fa.first_arrival
      ),
      INTERVAL 30 DAY
    )
)
SELECT
  APPROX_QUANTILES(diff_hours, 2)[OFFSET(1)] AS median_hours,
  AVG(diff_hours) AS avg_hours
FROM diffs
"""

TIME_PROPOSAL_TO_CANCELLATION_STATS = """
WITH parsed AS (
  SELECT
    cs._id,
    cs.presented_at,
    cs.arrival,
    cs.stage,
    v.agency_id,
    JSON_EXTRACT_ARRAY(cs.tracks) AS track_array
  FROM
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs
  JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.visors` v ON cs.visor_id = v._id
  WHERE
    cs.stage = 'Abgebrochen'
    AND cs.presented_at IS NOT NULL
    AND cs.arrival IS NOT NULL
    AND v.agency_id = @agency_id
    AND cs.presented_at BETWEEN @start_date AND @end_date
),
abbruchzeiten AS (
  SELECT
    p._id,
    p.presented_at,
    p.arrival,
    p.agency_id,
    MIN(TIMESTAMP(JSON_EXTRACT_SCALAR(track_item, '$.created_at'))) AS cancelled_at
  FROM
    parsed p,
    UNNEST(p.track_array) AS track_item
  WHERE
    JSON_EXTRACT_SCALAR(track_item, '$.differences.stage[1]') = 'Abgebrochen'
    AND TIMESTAMP(JSON_EXTRACT_SCALAR(track_item, '$.created_at')) < TIMESTAMP(p.arrival)
  GROUP BY
    p._id, p.presented_at, p.arrival, p.agency_id
)
SELECT
  agency_id,
  APPROX_QUANTILES(TIMESTAMP_DIFF(cancelled_at, TIMESTAMP(presented_at), HOUR), 2)[OFFSET(1)] AS median_hours,
  AVG(TIMESTAMP_DIFF(cancelled_at, TIMESTAMP(presented_at), HOUR)) AS avg_hours
FROM abbruchzeiten
GROUP BY agency_id
"""

TIME_ARRIVAL_TO_CANCELLATION_STATS = """
WITH parsed AS (
  SELECT
    cs._id,
    cs.arrival,
    cs.stage,
    cs.is_swap,
    v.agency_id,
    JSON_EXTRACT_ARRAY(cs.tracks) AS track_array
  FROM
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs
  JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.visors` v ON cs.visor_id = v._id
  WHERE
    cs.stage = 'Abgebrochen'
    AND cs.arrival IS NOT NULL
    AND v.agency_id = @agency_id
    AND cs.arrival BETWEEN @start_date AND @end_date
),
abbruchzeiten AS (
  SELECT
    p._id,
    p.arrival,
    p.agency_id,
    p.is_swap,
    MIN(TIMESTAMP(JSON_EXTRACT_SCALAR(track_item, '$.created_at'))) AS cancelled_at
  FROM
    parsed p,
    UNNEST(p.track_array) AS track_item
  WHERE
    JSON_EXTRACT_SCALAR(track_item, '$.differences.stage[0]') = 'Bestätigt'
    AND JSON_EXTRACT_SCALAR(track_item, '$.differences.stage[1]') = 'Abgebrochen'
    AND TIMESTAMP(JSON_EXTRACT_SCALAR(track_item, '$.created_at')) < TIMESTAMP(p.arrival)
  GROUP BY
    p._id, p.arrival, p.agency_id, p.is_swap
),
diffs AS (
  SELECT
    agency_id,
    is_swap,
    TIMESTAMP_DIFF(TIMESTAMP(arrival), cancelled_at, HOUR) AS diff_hours
  FROM abbruchzeiten
  WHERE TIMESTAMP_DIFF(TIMESTAMP(arrival), cancelled_at, HOUR) >= 0
    AND TIMESTAMP_DIFF(TIMESTAMP(arrival), cancelled_at, HOUR) <= 720
)
SELECT
  'overall' AS group_type,
  agency_id,
  APPROX_QUANTILES(diff_hours, 2)[OFFSET(1)] AS median_hours,
  AVG(diff_hours) AS avg_hours
FROM diffs
GROUP BY agency_id
UNION ALL
SELECT
  'first_stays' AS group_type,
  agency_id,
  APPROX_QUANTILES(diff_hours, 2)[OFFSET(1)] AS median_hours,
  AVG(diff_hours) AS avg_hours
FROM diffs
WHERE is_swap = 'false'
GROUP BY agency_id
UNION ALL
SELECT
  'followup_stays' AS group_type,
  agency_id,
  APPROX_QUANTILES(diff_hours, 2)[OFFSET(1)] AS median_hours,
  AVG(diff_hours) AS avg_hours
FROM diffs
WHERE is_swap != 'false'
GROUP BY agency_id
"""