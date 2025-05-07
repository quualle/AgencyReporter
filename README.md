# AgencyReporter - Installationsanleitung

Diese Anleitung hilft dir, AgencyReporter auf deinem MacBook einzurichten und zu starten.

## Voraussetzungen

- Ein MacBook mit macOS
- Internetverbindung
- Terminal-Kenntnisse (grundlegend)

## Installation & Start

### Option 1: Einfache Installation (empfohlen)

1. Öffne das Terminal (über Spotlight mit `Cmd + Leertaste` und dann "Terminal" eingeben)
2. Navigiere zum entpackten Projektordner:
   ```
   cd Pfad/zum/AgencyReporter
   ```
3. Mache das Setup-Skript ausführbar:
   ```
   chmod +x setup.sh
   ```
4. Führe das Setup-Skript aus:
   ```
   ./setup.sh
   ```
5. Folge den Anweisungen auf dem Bildschirm

Das Skript installiert automatisch alle notwendigen Abhängigkeiten und startet die Anwendung.

### Option 2: Manuelle Installation

Falls das Setup-Skript nicht funktioniert, kannst du die folgenden Schritte manuell ausführen:

1. Installiere Homebrew (falls nicht vorhanden):
   ```
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. Installiere Python und Node.js:
   ```
   brew install python node
   ```

3. Richte das Backend ein:
   ```
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. Richte das Frontend ein:
   ```
   cd ../frontend
   npm install
   ```

5. Starte das Backend:
   ```
   cd ../backend
   source venv/bin/activate
   python -m app.main
   ```

6. Starte das Frontend (in einem neuen Terminal-Fenster):
   ```
   cd Pfad/zum/AgencyReporter/frontend
   npm run dev
   ```

## Verwendung der Anwendung

Sobald beide Server gestartet sind, kannst du auf die Anwendung zugreifen:

- **Frontend:** http://localhost:3000
- **API-Dokumentation:** http://localhost:8000/docs

### BigQuery-Zugriff

Für die Verwendung der SQL-Abfragen in BigQuery:

1. Melde dich bei [Google BigQuery](https://console.cloud.google.com/bigquery) an
2. Kopiere die gewünschte SQL-Abfrage aus der Anwendung
3. Füge sie in das BigQuery-Abfragefenster ein und führe sie aus

## Fehlerbehebung

### Problem: "Port wird bereits verwendet"

Wenn du eine Fehlermeldung erhältst, dass der Port 3000 oder 8000 bereits verwendet wird:

```
lsof -i :3000    # Prüft, welcher Prozess Port 3000 belegt
lsof -i :8000    # Prüft, welcher Prozess Port 8000 belegt
kill -9 [PID]    # Beendet den Prozess mit der angegebenen ID
```

### Problem: "Module nicht gefunden"

Wenn Python-Module nicht gefunden werden:
```
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### Problem: "Node-Module nicht gefunden"

Wenn Node-Module nicht gefunden werden:
```
cd frontend
rm -rf node_modules
npm install
```

## SQL-Abfragen

### Problematic Stays Analyse

Die folgende SQL-Abfrage kann verwendet werden, um problematische Pflegeeinsätze aus der BigQuery-Tabelle zu analysieren:

```sql
SELECT 
  care_stay_id,
  agency_id,
  agency_name,
  stay_type,
  event_type,
  event_date,
  arrival_date,
  original_departure_date,
  new_departure_date,
  days_difference,
  has_replacement,
  has_follow_up,
  JSON_EXTRACT_SCALAR(analysis_result, '$.selected_reason') AS reason,
  CAST(JSON_EXTRACT_SCALAR(analysis_result, '$.confidence') AS INT64) AS confidence,
  JSON_EXTRACT_SCALAR(analysis_result, '$.customer_satisfaction') AS customer_satisfaction,
  JSON_EXTRACT_SCALAR(analysis_result, '$.comment') AS comment
FROM 
  `gcpxbixpflegehilfesenioren.Agencyreporter.problematic_stays`
WHERE 
  analysis_status = 'completed'
ORDER BY 
  event_date DESC
```

Diese Abfrage extrahiert die wichtigsten Felder aus der JSON-Struktur und zeigt die analysierten problematischen Pflegeeinsätze mit ihren Gründen an.

Weitere spezifische Abfragen:

```sql
-- Häufigste Abbruchgründe vor Anreise
SELECT 
  JSON_EXTRACT_SCALAR(analysis_result, '$.selected_reason') AS reason,
  COUNT(*) AS count
FROM 
  `gcpxbixpflegehilfesenioren.Agencyreporter.problematic_stays`
WHERE 
  event_type = 'cancelled_before_arrival'
  AND analysis_status = 'completed'
GROUP BY 
  reason
ORDER BY 
  count DESC
```

```sql
-- Häufigste Gründe für vorzeitige Beendigung nach Anreise
SELECT 
  JSON_EXTRACT_SCALAR(analysis_result, '$.selected_reason') AS reason,
  COUNT(*) AS count
FROM 
  `gcpxbixpflegehilfesenioren.Agencyreporter.problematic_stays`
WHERE 
  event_type = 'shortened_after_arrival'
  AND analysis_status = 'completed'
GROUP BY 
  reason
ORDER BY 
  count DESC
```

```sql
-- Analyse der Kundenzufriedenheit bei problematischen Einsätzen
SELECT 
  agency_name,
  JSON_EXTRACT_SCALAR(analysis_result, '$.customer_satisfaction') AS satisfaction,
  COUNT(*) AS count
FROM 
  `gcpxbixpflegehilfesenioren.Agencyreporter.problematic_stays`
WHERE 
  analysis_status = 'completed'
GROUP BY 
  agency_name, satisfaction
ORDER BY 
  agency_name, satisfaction
```

## Support

Bei Problemen oder Fragen wende dich bitte an:
- E-Mail: [deine-support-email@beispiel.de]
- Telefon: [deine Telefonnummer] 