#!/usr/bin/env python3

"""
Debug-Script für die Diskrepanz zwischen Dashboard-Statistiken und Detail-View
"""

import asyncio
from app.utils.bigquery_connection import BigQueryConnection
from app.utils.query_manager import QueryManager

async def debug_discrepancy():
    """
    Analysiert die Diskrepanz zwischen Dashboard (299 vorzeitig beendet) 
    und Detail-View (65 tatsächliche Departure-Änderungen)
    """
    
    connection = BigQueryConnection()
    query_manager = QueryManager()
    
    # Beispiel-Agentur-ID aus dem User-Beispiel
    agency_id = "649aa2dc2d847c6e7cbe0b56"  # Ändern falls nötig
    start_date, end_date = query_manager._calculate_date_range("last_quarter")
    
    print(f"=== ANALYSE FÜR AGENTUR {agency_id} ===")
    print(f"Zeitraum: {start_date} bis {end_date}")
    print()
    
    # 1. Dashboard-Logik nachrechnen
    print("1. DASHBOARD-BERECHNUNG:")
    
    # Angetretene Einsätze
    query_started = """
    SELECT 
        COUNT(*) AS total_started,
        a.name AS agency_name
    FROM 
        `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs
    JOIN 
        `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.contracts` c ON cs.contract_id = c._id
    JOIN 
        `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.agencies` a ON c.agency_id = a._id
    WHERE 
        c.agency_id = @agency_id
        AND cs.created_at BETWEEN @start_date AND @end_date
        AND cs.arrival IS NOT NULL
        AND cs.arrival != ''
        AND EXISTS (
            SELECT 1
            FROM UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track
            WHERE JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Bestätigt'
        )
        AND NOT (
            cs.stage = 'Abgebrochen' AND 
            EXISTS (
                SELECT 1
                FROM UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track
                WHERE 
                    JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Abgebrochen'
                    AND TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at')) < TIMESTAMP(cs.arrival)
            )
        )
    GROUP BY a.name
    """
    
    results_started = connection.execute_query(query_started, {
        "agency_id": agency_id,
        "start_date": start_date,
        "end_date": end_date
    })
    
    for row in results_started:
        total_started = row.get('total_started', 0)
        agency_name = row.get('agency_name', 'Unknown')
        print(f"  Angetretene Einsätze: {total_started}")
        print(f"  Agentur: {agency_name}")
    
    # Erfolgreich durchgeführte Einsätze
    query_completed = """
    WITH parsed AS (
        SELECT
            cs._id,
            cs.arrival,
            cs.departure,
            cs.created_at,
            cs.stage,
            c.agency_id,
            JSON_EXTRACT_ARRAY(cs.tracks) AS track_array
        FROM
            `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs
        JOIN
            `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.contracts` c ON cs.contract_id = c._id
        WHERE
            c.agency_id = @agency_id
            AND cs.created_at BETWEEN @start_date AND @end_date
            AND cs.arrival IS NOT NULL
            AND cs.arrival != ''
            AND EXISTS (
                SELECT 1
                FROM UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track
                WHERE JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Bestätigt'
            )
            AND NOT (
                cs.stage = 'Abgebrochen' AND 
                EXISTS (
                    SELECT 1
                    FROM UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track
                    WHERE 
                        JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Abgebrochen'
                        AND TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at')) < TIMESTAMP(cs.arrival)
                )
            )
            AND cs.departure IS NOT NULL
            AND cs.departure != ''
            AND TIMESTAMP(cs.departure) < CURRENT_TIMESTAMP()
    ),
    departure_changes AS (
        SELECT
            p._id,
            p.agency_id,
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
            AND SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', JSON_EXTRACT_SCALAR(track_item, '$.differences.departure[0]')) IS NOT NULL
            AND SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', JSON_EXTRACT_SCALAR(track_item, '$.differences.departure[1]')) IS NOT NULL
        GROUP BY
            p._id, p.agency_id
    )
    SELECT
        COUNT(*) AS total_completed
    FROM parsed p
    LEFT JOIN departure_changes dc ON p._id = dc._id
    WHERE
        dc._id IS NULL
        OR
        SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', dc.first_change.new_departure) > SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', dc.first_change.original_departure)
        OR
        SAFE_DIVIDE(
            TIMESTAMP_DIFF(
                SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', dc.first_change.original_departure),
                SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', dc.first_change.new_departure),
                DAY
            ),
            TIMESTAMP_DIFF(
                SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', dc.first_change.original_departure),
                TIMESTAMP(p.arrival),
                DAY
            )
        ) <= 0.33
    """
    
    results_completed = connection.execute_query(query_completed, {
        "agency_id": agency_id,
        "start_date": start_date,
        "end_date": end_date
    })
    
    for row in results_completed:
        total_completed = row.get('total_completed', 0)
        print(f"  Erfolgreich durchgeführte Einsätze: {total_completed}")
        dashboard_early_terminated = total_started - total_completed
        print(f"  Dashboard vorzeitig beendet: {dashboard_early_terminated}")
    
    print()
    
    # 2. Detail-View-Logik
    print("2. DETAIL-VIEW-BERECHNUNG:")
    
    query_details = """
    WITH parsed AS (
        SELECT
            cs._id as care_stay_id,
            cs.arrival,
            cs.departure,
            cs.created_at,
            cs.stage,
            c.agency_id,
            JSON_EXTRACT_ARRAY(cs.tracks) AS track_array
        FROM
            `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs
        JOIN
            `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.contracts` c ON cs.contract_id = c._id
        WHERE
            c.agency_id = @agency_id
            AND cs.created_at BETWEEN @start_date AND @end_date
            AND cs.arrival IS NOT NULL
            AND cs.arrival != ''
            AND EXISTS (
                SELECT 1
                FROM UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track
                WHERE JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Bestätigt'
            )
            AND NOT (
                cs.stage = 'Abgebrochen' AND 
                EXISTS (
                    SELECT 1
                    FROM UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track
                    WHERE 
                        JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Abgebrochen'
                        AND TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at')) < TIMESTAMP(cs.arrival)
                )
            )
            AND cs.departure IS NOT NULL
            AND cs.departure != ''
            AND TIMESTAMP(cs.departure) < CURRENT_TIMESTAMP()
    ),
    departure_changes AS (
        SELECT
            p.care_stay_id,
            p.agency_id,
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
            AND SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', JSON_EXTRACT_SCALAR(track_item, '$.differences.departure[0]')) IS NOT NULL
            AND SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', JSON_EXTRACT_SCALAR(track_item, '$.differences.departure[1]')) IS NOT NULL
        GROUP BY
            p.care_stay_id, p.agency_id
    )
    SELECT
        COUNT(*) as total_with_departure_changes,
        COUNT(CASE 
            WHEN SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', dc.first_change.new_departure) < SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', dc.first_change.original_departure)
                AND SAFE_DIVIDE(
                    TIMESTAMP_DIFF(
                        SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', dc.first_change.original_departure),
                        SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', dc.first_change.new_departure),
                        DAY
                    ),
                    TIMESTAMP_DIFF(
                        SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', dc.first_change.original_departure),
                        TIMESTAMP(p.arrival),
                        DAY
                    )
                ) > 0.33 
            THEN 1 
        END) as early_terminations_with_changes
    FROM parsed p
    INNER JOIN departure_changes dc ON p.care_stay_id = dc.care_stay_id
    """
    
    results_details = connection.execute_query(query_details, {
        "agency_id": agency_id,
        "start_date": start_date,
        "end_date": end_date
    })
    
    for row in results_details:
        total_with_changes = row.get('total_with_departure_changes', 0)
        early_with_changes = row.get('early_terminations_with_changes', 0)
        print(f"  Einsätze mit Departure-Änderungen: {total_with_changes}")
        print(f"  Davon vorzeitig beendet (>33%): {early_with_changes}")
    
    print()
    
    # 3. Kategorisierung der Differenz
    print("3. MÖGLICHE ERKLÄRUNGEN FÜR DIE DIFFERENZ:")
    
    query_categorization = """
    WITH parsed AS (
        SELECT
            cs._id as care_stay_id,
            cs.arrival,
            cs.departure,
            cs.created_at,
            cs.stage,
            c.agency_id,
            JSON_EXTRACT_ARRAY(cs.tracks) AS track_array,
            -- Prüfe, ob departure-Änderungen existieren
            CASE 
                WHEN EXISTS (
                    SELECT 1 
                    FROM UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track
                    WHERE JSON_EXTRACT_SCALAR(track, '$.differences.departure[0]') IS NOT NULL
                ) THEN 'has_departure_changes'
                ELSE 'no_departure_changes'
            END as has_changes,
            -- Prüfe aktuellen Status
            cs.stage as current_stage
        FROM
            `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs
        JOIN
            `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.contracts` c ON cs.contract_id = c._id
        WHERE
            c.agency_id = @agency_id
            AND cs.created_at BETWEEN @start_date AND @end_date
            AND cs.arrival IS NOT NULL
            AND cs.arrival != ''
            AND EXISTS (
                SELECT 1
                FROM UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track
                WHERE JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Bestätigt'
            )
            AND NOT (
                cs.stage = 'Abgebrochen' AND 
                EXISTS (
                    SELECT 1
                    FROM UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track
                    WHERE 
                        JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Abgebrochen'
                        AND TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at')) < TIMESTAMP(cs.arrival)
                )
            )
    )
    SELECT
        has_changes,
        current_stage,
        COUNT(*) as count
    FROM parsed
    GROUP BY has_changes, current_stage
    ORDER BY has_changes, current_stage
    """
    
    results_cat = connection.execute_query(query_categorization, {
        "agency_id": agency_id,
        "start_date": start_date,
        "end_date": end_date
    })
    
    for row in results_cat:
        has_changes = row.get('has_changes', '')
        stage = row.get('current_stage', '')
        count = row.get('count', 0)
        print(f"  {has_changes} + {stage}: {count} Einsätze")

if __name__ == "__main__":
    asyncio.run(debug_discrepancy())