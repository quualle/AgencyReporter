#!/usr/bin/env python3

"""
Korrigierte Analyse mit dem Verständnis:
- Status "Abgebrochen" = VOR Anreise (nie angereist)
- Vorzeitige Beendigung NACH Anreise = NUR durch Departure-Änderung
"""

import asyncio
from app.utils.bigquery_connection import BigQueryConnection
from app.utils.query_manager import QueryManager

async def analyze_correct_logic():
    connection = BigQueryConnection()
    query_manager = QueryManager()
    
    agency_id = "649aa2dc2d847c6e7cbe0b56"
    start_date, end_date = query_manager._calculate_date_range("last_quarter")
    
    print("=" * 80)
    print("KORRIGIERTE ANALYSE - VORZEITIGE BEENDIGUNGEN")
    print("=" * 80)
    print("Verständnis: ")
    print("- 'Abgebrochen' = VOR Anreise (sollte nicht in 'angetreten' sein)")
    print("- Vorzeitige Beendigung = NUR durch Departure-Änderung")
    print("=" * 80)
    print()
    
    # 1. Basis-Analyse
    print("1. BASIS-ANALYSE DER DATEN")
    print("-" * 50)
    
    query_base = """
    WITH care_stay_analysis AS (
        SELECT 
            cs._id,
            cs.arrival,
            cs.departure,
            cs.stage,
            cs.created_at,
            -- Hat jemals "Bestätigt" erreicht?
            EXISTS (
                SELECT 1 FROM UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track
                WHERE JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Bestätigt'
            ) as ever_confirmed,
            -- Wurde vor Anreise abgebrochen?
            CASE 
                WHEN cs.stage = 'Abgebrochen' AND EXISTS (
                    SELECT 1 FROM UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track
                    WHERE JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Abgebrochen'
                        AND TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at')) < TIMESTAMP(cs.arrival)
                ) THEN TRUE
                ELSE FALSE
            END as cancelled_before_arrival,
            -- Hat Departure-Änderungen?
            EXISTS (
                SELECT 1 FROM UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track
                WHERE JSON_EXTRACT_SCALAR(track, '$.differences.departure[0]') IS NOT NULL
            ) as has_departure_changes,
            -- Departure in Vergangenheit?
            CASE 
                WHEN cs.departure IS NOT NULL 
                    AND cs.departure != ''
                    AND TIMESTAMP(cs.departure) < CURRENT_TIMESTAMP()
                THEN TRUE
                ELSE FALSE
            END as departure_in_past
        FROM `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs
        JOIN `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.contracts` c ON cs.contract_id = c._id
        WHERE c.agency_id = @agency_id
            AND cs.created_at BETWEEN @start_date AND @end_date
            AND cs.arrival IS NOT NULL
            AND cs.arrival != ''
    )
    SELECT 
        COUNT(*) as total_with_arrival,
        
        -- Verschiedene Kategorien
        COUNT(CASE WHEN stage = 'Abgebrochen' THEN 1 END) as status_abgebrochen,
        COUNT(CASE WHEN stage = 'Bestätigt' THEN 1 END) as status_bestaetigt,
        COUNT(CASE WHEN cancelled_before_arrival THEN 1 END) as cancelled_before_arrival,
        COUNT(CASE WHEN ever_confirmed AND NOT cancelled_before_arrival THEN 1 END) as actually_started,
        
        -- Von den tatsächlich angetretenen
        COUNT(CASE WHEN ever_confirmed AND NOT cancelled_before_arrival AND departure_in_past THEN 1 END) as started_with_past_departure,
        COUNT(CASE WHEN ever_confirmed AND NOT cancelled_before_arrival AND NOT departure_in_past THEN 1 END) as started_still_running,
        
        -- Departure-Änderungen
        COUNT(CASE WHEN ever_confirmed AND NOT cancelled_before_arrival AND has_departure_changes THEN 1 END) as started_with_departure_changes
        
    FROM care_stay_analysis
    """
    
    results = connection.execute_query(query_base, {
        "agency_id": agency_id,
        "start_date": start_date,
        "end_date": end_date
    })
    
    for row in results:
        total = row.get('total_with_arrival', 0)
        abgebrochen = row.get('status_abgebrochen', 0)
        bestaetigt = row.get('status_bestaetigt', 0)
        cancelled_before = row.get('cancelled_before_arrival', 0)
        actually_started = row.get('actually_started', 0)
        with_past_departure = row.get('started_with_past_departure', 0)
        still_running = row.get('started_still_running', 0)
        with_changes = row.get('started_with_departure_changes', 0)
        
        print(f"Gesamt mit Arrival-Datum: {total}")
        print(f"  Status 'Abgebrochen': {abgebrochen}")
        print(f"  Status 'Bestätigt': {bestaetigt}")
        print(f"  Vor Anreise abgebrochen: {cancelled_before}")
        print()
        print(f"TATSÄCHLICH ANGETRETEN: {actually_started}")
        print(f"  Davon mit Departure in Vergangenheit: {with_past_departure}")
        print(f"  Davon noch laufend (kein past departure): {still_running}")
        print(f"  Davon mit Departure-Änderungen: {with_changes}")
    
    print()
    print("2. DETAILANALYSE DER ABGESCHLOSSENEN EINSÄTZE")
    print("-" * 50)
    
    query_completed = """
    WITH completed_stays AS (
        SELECT 
            cs._id,
            cs.arrival,
            cs.departure,
            JSON_EXTRACT_ARRAY(cs.tracks) AS track_array
        FROM `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs
        JOIN `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.contracts` c ON cs.contract_id = c._id
        WHERE c.agency_id = @agency_id
            AND cs.created_at BETWEEN @start_date AND @end_date
            AND cs.arrival IS NOT NULL AND cs.arrival != ''
            -- Tatsächlich angetreten
            AND EXISTS (
                SELECT 1 FROM UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track
                WHERE JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Bestätigt'
            )
            AND NOT (
                cs.stage = 'Abgebrochen' AND EXISTS (
                    SELECT 1 FROM UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track
                    WHERE JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Abgebrochen'
                        AND TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at')) < TIMESTAMP(cs.arrival)
                )
            )
            -- Abgeschlossen (departure in Vergangenheit)
            AND cs.departure IS NOT NULL
            AND cs.departure != ''
            AND TIMESTAMP(cs.departure) < CURRENT_TIMESTAMP()
    ),
    departure_analysis AS (
        SELECT 
            cs._id,
            cs.arrival,
            cs.departure,
            -- Erste Departure-Änderung
            ARRAY_AGG(
                STRUCT(
                    JSON_EXTRACT_SCALAR(track, '$.differences.departure[0]') AS original,
                    JSON_EXTRACT_SCALAR(track, '$.differences.departure[1]') AS new_departure,
                    JSON_EXTRACT_SCALAR(track, '$.created_at') AS timestamp
                )
                ORDER BY JSON_EXTRACT_SCALAR(track, '$.created_at') ASC
            )[SAFE_OFFSET(0)] AS first_change
        FROM completed_stays cs,
        UNNEST(cs.track_array) AS track
        WHERE JSON_EXTRACT_SCALAR(track, '$.differences.departure[0]') IS NOT NULL
            AND SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', JSON_EXTRACT_SCALAR(track, '$.differences.departure[0]')) IS NOT NULL
            AND SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', JSON_EXTRACT_SCALAR(track, '$.differences.departure[1]')) IS NOT NULL
        GROUP BY cs._id, cs.arrival, cs.departure
    )
    SELECT 
        COUNT(DISTINCT cs._id) as total_completed,
        COUNT(DISTINCT da._id) as with_departure_changes,
        COUNT(DISTINCT CASE 
            WHEN da._id IS NULL THEN cs._id 
        END) as without_departure_changes,
        
        -- Analyse der Änderungen
        COUNT(DISTINCT CASE 
            WHEN SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', da.first_change.new_departure) > 
                 SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', da.first_change.original)
            THEN da._id 
        END) as extended,
        
        COUNT(DISTINCT CASE 
            WHEN SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', da.first_change.new_departure) < 
                 SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', da.first_change.original)
            AND SAFE_DIVIDE(
                TIMESTAMP_DIFF(
                    SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', da.first_change.original),
                    SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', da.first_change.new_departure),
                    DAY
                ),
                TIMESTAMP_DIFF(
                    SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', da.first_change.original),
                    TIMESTAMP(da.arrival),
                    DAY
                )
            ) <= 0.33
            THEN da._id 
        END) as shortened_moderate,
        
        COUNT(DISTINCT CASE 
            WHEN SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', da.first_change.new_departure) < 
                 SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', da.first_change.original)
            AND SAFE_DIVIDE(
                TIMESTAMP_DIFF(
                    SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', da.first_change.original),
                    SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', da.first_change.new_departure),
                    DAY
                ),
                TIMESTAMP_DIFF(
                    SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', da.first_change.original),
                    TIMESTAMP(da.arrival),
                    DAY
                )
            ) > 0.33
            THEN da._id 
        END) as shortened_significant
        
    FROM completed_stays cs
    LEFT JOIN departure_analysis da ON cs._id = da._id
    """
    
    results = connection.execute_query(query_completed, {
        "agency_id": agency_id,
        "start_date": start_date,
        "end_date": end_date
    })
    
    for row in results:
        total = row.get('total_completed', 0)
        with_changes = row.get('with_departure_changes', 0)
        without_changes = row.get('without_departure_changes', 0)
        extended = row.get('extended', 0)
        moderate = row.get('shortened_moderate', 0)
        significant = row.get('shortened_significant', 0)
        
        print(f"Abgeschlossene Einsätze (mit past departure): {total}")
        print(f"  OHNE Departure-Änderungen: {without_changes}")
        print(f"  MIT Departure-Änderungen: {with_changes}")
        print(f"    → Verlängert: {extended}")
        print(f"    → Moderat verkürzt (≤33%): {moderate}")
        print(f"    → Signifikant verkürzt (>33%): {significant}")
        print()
        print(f"KORREKTE VORZEITIGE BEENDIGUNGSRATE:")
        print(f"  Nur signifikante Verkürzungen: {significant} von {total} = {(significant/total*100):.1f}%")
    
    print()
    print("3. PROBLEM MIT AKTUELLER BERECHNUNG")
    print("-" * 50)
    
    query_problem = """
    SELECT 
        -- Aktuelle fehlerhafte Berechnung
        COUNT(CASE 
            WHEN cs.arrival IS NOT NULL 
                AND EXISTS (
                    SELECT 1 FROM UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track
                    WHERE JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Bestätigt'
                )
                AND NOT (
                    cs.stage = 'Abgebrochen' AND EXISTS (
                        SELECT 1 FROM UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track
                        WHERE JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Abgebrochen'
                            AND TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at')) < TIMESTAMP(cs.arrival)
                    )
                )
            THEN 1 
        END) as current_logic_started,
        
        -- Davon: Wie viele haben KEIN departure in der Vergangenheit?
        COUNT(CASE 
            WHEN cs.arrival IS NOT NULL 
                AND EXISTS (
                    SELECT 1 FROM UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track
                    WHERE JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Bestätigt'
                )
                AND NOT (
                    cs.stage = 'Abgebrochen' AND EXISTS (
                        SELECT 1 FROM UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track
                        WHERE JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Abgebrochen'
                            AND TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at')) < TIMESTAMP(cs.arrival)
                    )
                )
                AND NOT (
                    cs.departure IS NOT NULL 
                    AND cs.departure != ''
                    AND TIMESTAMP(cs.departure) < CURRENT_TIMESTAMP()
                )
            THEN 1 
        END) as still_running_or_future
        
    FROM `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs
    JOIN `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.contracts` c ON cs.contract_id = c._id
    WHERE c.agency_id = @agency_id
        AND cs.created_at BETWEEN @start_date AND @end_date
    """
    
    results = connection.execute_query(query_problem, {
        "agency_id": agency_id,
        "start_date": start_date,
        "end_date": end_date
    })
    
    for row in results:
        started = row.get('current_logic_started', 0)
        still_running = row.get('still_running_or_future', 0)
        
        print(f"Aktuelle Logik zählt als 'angetreten': {started}")
        print(f"Davon noch laufend/zukünftig: {still_running}")
        print(f"→ Diese {still_running} werden FÄLSCHLICH als 'vorzeitig beendet' gezählt!")

if __name__ == "__main__":
    asyncio.run(analyze_correct_logic())