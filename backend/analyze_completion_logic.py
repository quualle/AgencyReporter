#!/usr/bin/env python3

"""
Ausführliche Analyse der Completion-Rate-Berechnung
"""

import asyncio
from app.utils.bigquery_connection import BigQueryConnection
from app.utils.query_manager import QueryManager

async def analyze_completion_logic():
    """
    Detaillierte Analyse aller Faktoren, die zu hohen vorzeitigen Beendigungsraten führen
    """
    
    connection = BigQueryConnection()
    query_manager = QueryManager()
    
    # Beispiel-Agentur mit hoher Rate
    agency_id = "649aa2dc2d847c6e7cbe0b56"
    start_date, end_date = query_manager._calculate_date_range("last_quarter")
    
    print("=" * 80)
    print("VOLLSTÄNDIGE ANALYSE DER COMPLETION-RATE-BERECHNUNG")
    print("=" * 80)
    print(f"Agentur: {agency_id}")
    print(f"Zeitraum: {start_date} bis {end_date}")
    print()
    
    # 1. Basis-Population: Alle Care Stays
    print("1. BASIS-POPULATION: Alle Care Stays")
    print("-" * 50)
    
    query_all = """
    SELECT 
        COUNT(*) as total_care_stays,
        COUNT(CASE WHEN cs.arrival IS NOT NULL AND cs.arrival != '' THEN 1 END) as with_arrival,
        COUNT(CASE WHEN cs.departure IS NOT NULL AND cs.departure != '' THEN 1 END) as with_departure,
        COUNT(CASE WHEN cs.stage = 'Bestätigt' THEN 1 END) as current_bestaetigt,
        COUNT(CASE WHEN cs.stage = 'Abgebrochen' THEN 1 END) as current_abgebrochen,
        COUNT(CASE WHEN cs.stage = 'Angenommen' THEN 1 END) as current_angenommen
    FROM 
        `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs
    JOIN 
        `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.contracts` c ON cs.contract_id = c._id
    WHERE 
        c.agency_id = @agency_id
        AND cs.created_at BETWEEN @start_date AND @end_date
    """
    
    results = connection.execute_query(query_all, {
        "agency_id": agency_id,
        "start_date": start_date,
        "end_date": end_date
    })
    
    for row in results:
        print(f"  Gesamt Care Stays: {row.get('total_care_stays', 0)}")
        print(f"  Mit Arrival-Datum: {row.get('with_arrival', 0)}")
        print(f"  Mit Departure-Datum: {row.get('with_departure', 0)}")
        print(f"  Aktueller Status 'Bestätigt': {row.get('current_bestaetigt', 0)}")
        print(f"  Aktueller Status 'Abgebrochen': {row.get('current_abgebrochen', 0)}")
        print(f"  Aktueller Status 'Angenommen': {row.get('current_angenommen', 0)}")
    
    print()
    
    # 2. Filter-Schritte für "angetretene" Einsätze
    print("2. FILTER FÜR 'ANGETRETENE' EINSÄTZE")
    print("-" * 50)
    
    # Schritt 1: Mit Arrival
    query_step1 = """
    SELECT COUNT(*) as count
    FROM `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs
    JOIN `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.contracts` c ON cs.contract_id = c._id
    WHERE c.agency_id = @agency_id
        AND cs.created_at BETWEEN @start_date AND @end_date
        AND cs.arrival IS NOT NULL
        AND cs.arrival != ''
    """
    
    result = connection.execute_query(query_step1, {
        "agency_id": agency_id, "start_date": start_date, "end_date": end_date
    })
    step1_count = list(result)[0].get('count', 0)
    print(f"  Schritt 1 - Mit Arrival-Datum: {step1_count}")
    
    # Schritt 2: + jemals "Bestätigt"
    query_step2 = """
    SELECT COUNT(*) as count
    FROM `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs
    JOIN `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.contracts` c ON cs.contract_id = c._id
    WHERE c.agency_id = @agency_id
        AND cs.created_at BETWEEN @start_date AND @end_date
        AND cs.arrival IS NOT NULL
        AND cs.arrival != ''
        AND EXISTS (
            SELECT 1
            FROM UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track
            WHERE JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Bestätigt'
        )
    """
    
    result = connection.execute_query(query_step2, {
        "agency_id": agency_id, "start_date": start_date, "end_date": end_date
    })
    step2_count = list(result)[0].get('count', 0)
    print(f"  Schritt 2 - + Jemals 'Bestätigt': {step2_count}")
    
    # Schritt 3: - vor Arrival abgebrochen
    query_step3 = """
    SELECT COUNT(*) as count
    FROM `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs
    JOIN `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.contracts` c ON cs.contract_id = c._id
    WHERE c.agency_id = @agency_id
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
                WHERE JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Abgebrochen'
                    AND TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at')) < TIMESTAMP(cs.arrival)
            )
        )
    """
    
    result = connection.execute_query(query_step3, {
        "agency_id": agency_id, "start_date": start_date, "end_date": end_date
    })
    step3_count = list(result)[0].get('count', 0)
    print(f"  Schritt 3 - Nicht vor Arrival abgebrochen: {step3_count}")
    print(f"  → FINALE 'ANGETRETENE' EINSÄTZE: {step3_count}")
    
    print()
    
    # 3. Filter für "erfolgreich durchgeführte" Einsätze
    print("3. FILTER FÜR 'ERFOLGREICH DURCHGEFÜHRTE' EINSÄTZE")
    print("-" * 50)
    
    # Schritt 1: Basis (angetretene)
    print(f"  Basis (angetretene): {step3_count}")
    
    # Schritt 2: + Mit Departure in Vergangenheit
    query_with_past_departure = """
    SELECT COUNT(*) as count
    FROM `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs
    JOIN `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.contracts` c ON cs.contract_id = c._id
    WHERE c.agency_id = @agency_id
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
                WHERE JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Abgebrochen'
                    AND TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at')) < TIMESTAMP(cs.arrival)
            )
        )
        AND cs.departure IS NOT NULL
        AND cs.departure != ''
        AND TIMESTAMP(cs.departure) < CURRENT_TIMESTAMP()
    """
    
    result = connection.execute_query(query_with_past_departure, {
        "agency_id": agency_id, "start_date": start_date, "end_date": end_date
    })
    with_past_departure = list(result)[0].get('count', 0)
    print(f"  + Mit Departure in Vergangenheit: {with_past_departure}")
    
    # Schritt 3: Aufschlüsselung der Completion-Kriterien
    query_completion_breakdown = """
    WITH base_stays AS (
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
            AND EXISTS (
                SELECT 1 FROM UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track
                WHERE JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Bestätigt'
            )
            AND NOT (
                cs.stage = 'Abgebrochen' AND 
                EXISTS (
                    SELECT 1 FROM UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track
                    WHERE JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Abgebrochen'
                        AND TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at')) < TIMESTAMP(cs.arrival)
                )
            )
            AND cs.departure IS NOT NULL AND cs.departure != ''
            AND TIMESTAMP(cs.departure) < CURRENT_TIMESTAMP()
    ),
    departure_analysis AS (
        SELECT 
            bs._id,
            -- Prüfe ob departure-Änderungen existieren
            CASE 
                WHEN EXISTS (
                    SELECT 1 FROM UNNEST(bs.track_array) AS track
                    WHERE JSON_EXTRACT_SCALAR(track, '$.differences.departure[0]') IS NOT NULL
                ) THEN 'has_departure_changes'
                ELSE 'no_departure_changes'
            END as has_changes,
            
            -- Bei Änderungen: Erste Änderung analysieren
            CASE 
                WHEN EXISTS (
                    SELECT 1 FROM UNNEST(bs.track_array) AS track
                    WHERE JSON_EXTRACT_SCALAR(track, '$.differences.departure[0]') IS NOT NULL
                ) THEN
                    CASE 
                        WHEN (
                            SELECT SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', 
                                JSON_EXTRACT_SCALAR(track, '$.differences.departure[1]'))
                            FROM UNNEST(bs.track_array) AS track
                            WHERE JSON_EXTRACT_SCALAR(track, '$.differences.departure[0]') IS NOT NULL
                            ORDER BY JSON_EXTRACT_SCALAR(track, '$.created_at') ASC
                            LIMIT 1
                        ) > (
                            SELECT SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', 
                                JSON_EXTRACT_SCALAR(track, '$.differences.departure[0]'))
                            FROM UNNEST(bs.track_array) AS track
                            WHERE JSON_EXTRACT_SCALAR(track, '$.differences.departure[0]') IS NOT NULL
                            ORDER BY JSON_EXTRACT_SCALAR(track, '$.created_at') ASC
                            LIMIT 1
                        ) THEN 'extended'
                        WHEN (
                            SELECT SAFE_DIVIDE(
                                TIMESTAMP_DIFF(
                                    SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', 
                                        JSON_EXTRACT_SCALAR(track, '$.differences.departure[0]')),
                                    SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', 
                                        JSON_EXTRACT_SCALAR(track, '$.differences.departure[1]')),
                                    DAY
                                ),
                                TIMESTAMP_DIFF(
                                    SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', 
                                        JSON_EXTRACT_SCALAR(track, '$.differences.departure[0]')),
                                    TIMESTAMP(bs.arrival),
                                    DAY
                                )
                            )
                            FROM UNNEST(bs.track_array) AS track
                            WHERE JSON_EXTRACT_SCALAR(track, '$.differences.departure[0]') IS NOT NULL
                            ORDER BY JSON_EXTRACT_SCALAR(track, '$.created_at') ASC
                            LIMIT 1
                        ) <= 0.33 THEN 'shortened_moderate'
                        ELSE 'shortened_significant'
                    END
                ELSE 'no_changes'
            END as change_type
        FROM base_stays bs
    )
    SELECT 
        has_changes,
        change_type,
        COUNT(*) as count,
        -- Diese zählen als "erfolgreich durchgeführt"
        CASE 
            WHEN has_changes = 'no_departure_changes' THEN 'COMPLETED'
            WHEN change_type = 'extended' THEN 'COMPLETED'
            WHEN change_type = 'shortened_moderate' THEN 'COMPLETED'
            ELSE 'EARLY_TERMINATED'
        END as classification
    FROM departure_analysis
    GROUP BY has_changes, change_type
    ORDER BY has_changes, change_type
    """
    
    results = connection.execute_query(query_completion_breakdown, {
        "agency_id": agency_id, "start_date": start_date, "end_date": end_date
    })
    
    total_completed = 0
    total_early_terminated = 0
    
    print("  Detailaufschlüsselung:")
    for row in results:
        has_changes = row.get('has_changes', '')
        change_type = row.get('change_type', '')
        count = row.get('count', 0)
        classification = row.get('classification', '')
        
        print(f"    {has_changes} | {change_type}: {count} ({classification})")
        
        if classification == 'COMPLETED':
            total_completed += count
        else:
            total_early_terminated += count
    
    print(f"  → FINALE 'ERFOLGREICH DURCHGEFÜHRTE': {total_completed}")
    print(f"  → VORZEITIG BEENDET: {step3_count - total_completed}")
    print(f"  → VORZEITIGE BEENDIGUNGSRATE: {((step3_count - total_completed) / step3_count * 100):.1f}%")
    
    print()
    print("4. ALTERNATIVE BERECHNUNGSMETHODEN")
    print("-" * 50)
    
    # Alternative 1: Nur echte Departure-Änderungen
    print("ALTERNATIVE 1: Nur dokumentierte Departure-Verkürzungen")
    query_alt1 = """
    WITH base_stays AS (
        SELECT cs._id, cs.arrival, JSON_EXTRACT_ARRAY(cs.tracks) AS track_array
        FROM `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs
        JOIN `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.contracts` c ON cs.contract_id = c._id
        WHERE c.agency_id = @agency_id
            AND cs.created_at BETWEEN @start_date AND @end_date
            AND cs.arrival IS NOT NULL AND cs.arrival != ''
            AND EXISTS (
                SELECT 1 FROM UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track
                WHERE JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Bestätigt'
            )
    )
    SELECT 
        COUNT(*) as total_started,
        COUNT(CASE 
            WHEN EXISTS (
                SELECT 1 FROM UNNEST(bs.track_array) AS track
                WHERE JSON_EXTRACT_SCALAR(track, '$.differences.departure[0]') IS NOT NULL
                    AND SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', 
                        JSON_EXTRACT_SCALAR(track, '$.differences.departure[1]')) < 
                        SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', 
                        JSON_EXTRACT_SCALAR(track, '$.differences.departure[0]'))
            ) THEN 1 
        END) as documented_early_terminations
    FROM base_stays bs
    """
    
    result = connection.execute_query(query_alt1, {
        "agency_id": agency_id, "start_date": start_date, "end_date": end_date
    })
    
    for row in result:
        total = row.get('total_started', 0)
        early = row.get('documented_early_terminations', 0)
        rate = (early / total * 100) if total > 0 else 0
        print(f"  Angetretene Einsätze: {total}")
        print(f"  Dokumentierte Verkürzungen: {early}")
        print(f"  Rate: {rate:.1f}%")
    
    print()
    
    # Alternative 2: Status-basiert
    print("ALTERNATIVE 2: Nur nach aktuellem Status")
    query_alt2 = """
    SELECT 
        COUNT(*) as total_started,
        COUNT(CASE WHEN cs.stage = 'Bestätigt' THEN 1 END) as still_confirmed,
        COUNT(CASE WHEN cs.stage = 'Abgebrochen' THEN 1 END) as cancelled_after_arrival
    FROM `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs
    JOIN `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.contracts` c ON cs.contract_id = c._id
    WHERE c.agency_id = @agency_id
        AND cs.created_at BETWEEN @start_date AND @end_date
        AND cs.arrival IS NOT NULL AND cs.arrival != ''
        AND EXISTS (
            SELECT 1 FROM UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track
            WHERE JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Bestätigt'
        )
        AND NOT (
            cs.stage = 'Abgebrochen' AND 
            EXISTS (
                SELECT 1 FROM UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track
                WHERE JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Abgebrochen'
                    AND TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at')) < TIMESTAMP(cs.arrival)
            )
        )
    """
    
    result = connection.execute_query(query_alt2, {
        "agency_id": agency_id, "start_date": start_date, "end_date": end_date
    })
    
    for row in result:
        total = row.get('total_started', 0)
        confirmed = row.get('still_confirmed', 0)
        cancelled = row.get('cancelled_after_arrival', 0)
        print(f"  Angetretene Einsätze: {total}")
        print(f"  Noch 'Bestätigt': {confirmed}")
        print(f"  'Abgebrochen' nach Arrival: {cancelled}")
        print(f"  Abbruchrate: {(cancelled / total * 100):.1f}%")

if __name__ == "__main__":
    asyncio.run(analyze_completion_logic())