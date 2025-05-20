#!/usr/bin/env python
"""
Debug-Skript zum manuellen Testen der problematic_stays SQL-Abfragen
"""
import os
import sys
from dotenv import load_dotenv
from utils.bigquery_connection import BigQueryConnection
from queries.problematic_stays.queries import (
    GET_PROBLEMATIC_STAYS_OVERVIEW,
    GET_PROBLEMATIC_STAYS_REASONS,
    GET_PROBLEMATIC_STAYS_TIME_ANALYSIS
)
from datetime import datetime, timedelta

# Lade Umgebungsvariablen
load_dotenv()

# Verbindung zu BigQuery herstellen
connection = BigQueryConnection()

# Testparameter
today = datetime.now()
start_date = (today - timedelta(days=90)).strftime("%Y-%m-%d")
end_date = today.strftime("%Y-%m-%d")
test_agency_id = "649aa2dc2d847c6e7cbe0b56"  # Testweise verwenden wir die Agency-ID aus dem Fehler

print("=== Debug: Problematic Stays SQL Queries ===")
print(f"Start Date: {start_date}")
print(f"End Date: {end_date}")
print(f"Agency ID: {test_agency_id}")

# Test 1: Einfache Abfrage zum Testen der Tabelle
print("\n=== Test 1: Einfache Tabellenzugriffsprüfung ===")
try:
    test_query = """
    SELECT COUNT(*) as count
    FROM `gcpxbixpflegehilfesenioren.AgencyReporter.problematic_stays`
    """
    results = connection.execute_query(test_query, {})
    print(f"Anzahl der Einträge in der Tabelle: {results[0]['count']}")
except Exception as e:
    print(f"Fehler beim Ausführen der einfachen Abfrage: {str(e)}")

# Test 2: Abfrage mit agency_id Filter
print("\n=== Test 2: Abfrage mit Agency-Filter ===")
try:
    test_query = """
    SELECT COUNT(*) as count
    FROM `gcpxbixpflegehilfesenioren.AgencyReporter.problematic_stays`
    WHERE agency_id = @agency_id
    """
    results = connection.execute_query(test_query, {"agency_id": test_agency_id})
    print(f"Anzahl der Einträge für agency_id {test_agency_id}: {results[0]['count']}")
except Exception as e:
    print(f"Fehler beim Ausführen der Agency-Filter-Abfrage: {str(e)}")

# Test 3: Vollständige Overview-Abfrage
print("\n=== Test 3: Vollständige Overview-Abfrage ===")
try:
    query_params = {
        "agency_id": test_agency_id,
        "start_date": start_date,
        "end_date": end_date
    }
    
    results = connection.execute_query(GET_PROBLEMATIC_STAYS_OVERVIEW, query_params)
    if results and len(results) > 0:
        print(f"Overview-Abfrage erfolgreich: {len(results)} Ergebnisse")
        # Zeige die ersten 5 Spalten des ersten Ergebnisses
        first_result = dict(results[0].items())
        print("Erste 5 Spalten des Ergebnisses:")
        for i, (key, value) in enumerate(first_result.items()):
            if i < 5:
                print(f"  {key}: {value}")
    else:
        print("Overview-Abfrage erfolgreich, aber keine Ergebnisse gefunden.")
except Exception as e:
    print(f"Fehler beim Ausführen der Overview-Abfrage: {str(e)}")
    import traceback
    traceback.print_exc()

print("\nDebug abgeschlossen.") 