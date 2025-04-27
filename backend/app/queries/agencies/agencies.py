"""
Agency related queries.
"""

GET_ALL_AGENCIES = """
WITH active_stays_last_30_days AS (
    -- Finde alle agency_ids, die in den letzten 30 Tagen aktive CareStays hatten
    SELECT DISTINCT
        c.agency_id
    FROM
        `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs
    JOIN
        `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.contracts` c ON cs.contract_id = c._id
    WHERE
        cs.arrival IS NOT NULL
        AND SAFE.TIMESTAMP(cs.arrival) IS NOT NULL -- Stelle sicher, dass Anreise geparsed werden kann
        AND SAFE.TIMESTAMP(cs.arrival) <= CURRENT_TIMESTAMP() -- Muss begonnen haben
        AND ( -- Aktiv, wenn entweder kein Enddatum ODER Enddatum nicht älter als 30 Tage
             cs.departure IS NULL
             OR (SAFE.TIMESTAMP(cs.departure) IS NOT NULL -- Stelle sicher, dass Abreise geparsed werden kann
                 AND SAFE.TIMESTAMP(cs.departure) >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
                )
            )
)
SELECT
    a._id AS agency_id,
    a.name AS agency_name,
    -- Füge weitere Felder hinzu, falls vom Frontend benötigt (z.B. a.active für Systemstatus)
    CASE
        WHEN act.agency_id IS NOT NULL THEN TRUE
        ELSE FALSE
    END AS is_active_recently -- Neues Flag basierend auf CareStays
FROM
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.agencies` a
LEFT JOIN
    active_stays_last_30_days act ON a._id = act.agency_id
-- Optional: Nur Agenturen anzeigen, die im System generell als aktiv gelten?
-- WHERE a.active = 'active'
ORDER BY
    is_active_recently DESC, -- Aktive zuerst
    a.name ASC
"""

GET_AGENCY_DETAILS = """
SELECT 
    _id as agency_id, 
    name as agency_name, 
    created_at, 
    active as status, 
    jurisdiction as location, 
    homepage as website, 
    nationalities,
    contract_duration,
    health_insurance,
    liability_insurance,
    accident_insurance,
    hours_per_week,
    night_care,
    ger_minimum_wage
    -- Add other relevant fields as needed
FROM 
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.agencies`
WHERE 
    _id = @agency_id
"""