1. Quote: Gesamtzahl Stellen (1) - Reservierungen getätigt (2)
Erläuterung: "Zeigt bei wie viel % der gesamt verfügbaren Stellen die Agentur eine Reservierung gemacht hat"

SQL Query (1):
"""
SELECT
    COUNT(*) AS posting_count
FROM
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.postings` p
WHERE
    p.created_at BETWEEN '2025-01-01' AND '2025-01-31'
"""

SQL Query (2):
"""
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
    a._id = '5eb000fe2c3484b37749fec4'  -- Hier die ID der gewünschten Agentur einfügen
    AND r.created_at BETWEEN '2025-01-01' AND '2025-03-01'  -- Datumsformat: 'YYYY-MM-DD'
GROUP BY
    a.name;
    """

#################################################################################################################################################################


2. Quote: Anzahl Reservierungen (2) - Anzahl erfüllte reservierungen (3)
Erläuterung: "Zeigt wie viel % Ihrer Reservierungen die Agentur schlussendlich auch mit einem BK Vorschlag erfüllt hat"

SQL Query(2):
"""
wie (2)
"""

SQL Query(3):
"""
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
    AND a._id = '614c91bdf57558ebcb6326d0'
    AND r.created_at BETWEEN '2025-01-01' AND '2025-01-31'
GROUP BY
    a.name;
"""


#################################################################################################################################################################

3. Quote:  Anzahl Reservierungen (2) -  Anzahl abgebrochene Reservierungen(4)
Erläuterung: "Zeigt wie viel % ihrer eigenen Reservierungen die Agentur selbstständig abgebrochen hat. Besser als nicht abzubrechen und einfach liegen zu lassen!"

SQL Query(4):
"""
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
    AND a._id = '614c91bdf57558ebcb6326d0'
     AND r.created_at BETWEEN '2025-01-01' AND '2025-02-01'
GROUP BY
    a.name;
"""

#################################################################################################################################################################

4. Quote:  Anzahl Reservierungen (2) - Anzahl reservierungen, die weder von Vertriebspartner oder Agentur zurückgezogen wurden, noch mit Personalvorschlag erfüllt(5)
Erläuterung: "Zeigt, wie viele % der reservierungen, die eine Agentur getätigt hat, dannach weder zurückgezogen noch erfüllt wurden - also einfach liegen gelassen!"

SQL Query(5):
"""
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
    AND a._id = '5eb000fe2c3484b37749fec4'
    AND r.created_at BETWEEN '2025-01-01' AND '2025-04-31'
GROUP BY
    a.name;
"""

#################################################################################################################################################################

5. Quote:  Reservierung mit Personalvorschlag erfüllt(3) - Pflegeeinsatz angetreten(6)
Erläuterung: "Zeigt wie viel % der vorgeschlagenen Pflegekräfte schlussendlich auch wirklich angereist sind"

SQL Query(3), schon oben


SQL Query(6):
"""
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
    a._id = '649aa2dc2d847c6e7cbe0b56'
    AND cs.created_at BETWEEN '2025-01-01' AND '2025-01-05'
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
    a.name;
"""

#################################################################################################################################################################

6. Quote:  Anzahl gemachter Personalvorschläge (8) - Anzahl VOR Einsatz abgebrochener Pflegeeinsätze (7)
Erläuterung: "Zeigt, wie viel % der vorgeschlagenen Pflegekräfte von der Agentur wieder abgebrochen wurden (vor Anreise)"
SQL Query(7):
"""
WITH parsed AS (
  SELECT
    cs._id,
    cs.arrival,
    cs.created_at,
    cs.visor_id,  -- Für die Filterung nach Agentur nutzen wir visor_id
    JSON_EXTRACT_ARRAY(cs.tracks) AS track_array
  FROM
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs
  JOIN
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.visors` v ON cs.visor_id = v._id
  WHERE
    cs.stage = 'Abgebrochen'
    AND cs.arrival IS NOT NULL
    AND cs.arrival != ''
    AND v.agency_id = '649aa2dc2d847c6e7cbe0b56'  -- Wir filtern über visors nach agency_id
    AND cs.created_at BETWEEN '2025-01-01' AND '2025-05-01'
)
SELECT
  COUNT(DISTINCT _id) AS abgebrochen_vor_arrival
FROM parsed,
UNNEST(track_array) AS track_item
WHERE
  JSON_EXTRACT_SCALAR(track_item, '$.differences.stage[1]') = 'Abgebrochen'
  AND (
    JSON_EXTRACT_SCALAR(track_item, '$.differences.stage[0]') = 'Vorgestellt'
    OR JSON_EXTRACT_SCALAR(track_item, '$.differences.stage[0]') = 'Angenommen'
    OR JSON_EXTRACT_SCALAR(track_item, '$.differences.stage[0]') = 'Bestätigt'
    OR JSON_EXTRACT_SCALAR(track_item, '$.differences.stage[0]') = 'Neu'
  )
  AND TIMESTAMP(JSON_EXTRACT_SCALAR(track_item, '$.created_at')) < TIMESTAMP(arrival);
"""

SQL Query (8): Anzahl gemachter Personalvorschläge
"""
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
    a._id = '649aa2dc2d847c6e7cbe0b56'
    AND cs.created_at BETWEEN '2025-01-01' AND '2025-05-01'
GROUP BY
    a.name;
"""

#################################################################################################################################################################

7. Quote: Pflegeeinsatz angetreten(6) - Pflegeinsatz vollständig beendet(9)
Erläuterung: "Zeigt, wie viel % der zum Kunden angereisten Pflegekräfte den Einsatz wie geplant bis zum Schluss durchgezogen haben"
SQL Query(9):
"""
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
    AND TIMESTAMP(cs.departure) < CURRENT_TIMESTAMP()  -- Datum in Timestamp umwandeln
    AND a._id = '649aa2dc2d847c6e7cbe0b56'
    AND cs.created_at BETWEEN '2025-01-01' AND '2025-05-01'
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
  agency_name;
"""

#################################################################################################################################################################
. Quote: Pflegeeinsatz angetreten(6) - Pflegeinsatz vollständig beendet(9)

SQL Query():
"""

"""

#################################################################################################################################################################

. Quote:  () - Anzahl erfüllte Reservierungen ()

SQL Query():
"""

"""

#################################################################################################################################################################

. Quote:  () - Anzahl erfüllte Reservierungen ()

SQL Query():
"""

"""

#################################################################################################################################################################

. Quote:  () - Anzahl erfüllte Reservierungen ()

SQL Query():
"""

"""