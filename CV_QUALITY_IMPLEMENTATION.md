# CV-Quality Implementation - Projektdokumentation

## Projektzeitraum
7. Juni 2025, ca. 19:00 - 20:45 Uhr (1:45 Stunden)

## Ausgangslage
Nach einer längeren Entwicklungspause sollte das Agency Reporter Projekt um ein neues Feature erweitert werden: Die Bewertung der Qualität von Betreuungskraft-CVs durch Abgleich mit tatsächlicher Kundenerfahrung.

## Projektziel
Entwicklung eines Systems zur Messung der Diskrepanz zwischen CV-Angaben und wahrgenommener Realität beim Kunden. Die Kernidee: Falsche oder übertriebene Angaben in CVs führen zu Enttäuschungen und Kündigungen.

## Implementierte Komponenten

### 1. Konzeptentwicklung und Dokumentation
- **CV_QUALITY_CONCEPT.md** erstellt mit detaillierter Methodologie
- Bewertungssystem definiert: Benefit of the doubt (5/5 Ausgangswert)
- Kategorien festgelegt: Deutschkenntnisse, Berufserfahrung, harte Eigenschaften (Führerschein, Raucher, etc.)
- KI-basierte Enttäuschungserkennung in Kundenkommunikation geplant

### 2. Backend-Implementation

#### 2.1 Neue API-Endpoints
**`GET /api/cv_quality/care_stays/list`**
- Listet alle angetretenen Care Stays der letzten 6 Monate
- Komplexe BigQuery-Abfrage mit mehreren JOINs über 6 Tabellen
- Korrekte Anreise-Logik: Nur Care Stays die bestätigt wurden UND nicht vor Anreise abgebrochen wurden

**`GET /api/cv_quality/care_stays/{care_stay_id}/communications`**
- Holt alle Emails und Tickets für einen spezifischen Care Stay
- Zeitfenster: 7 Tage vor Start bis 14 Tage nach Ende

**`POST /api/cv_quality/analyze`**
- CV-Upload (PDF/Text) mit care_stay_id
- PDF-Parsing mit PyPDF2
- OpenAI-Integration für Enttäuschungserkennung
- Speicherung der Analyse-Ergebnisse in SQLite

#### 2.2 Datenbank-Erweiterungen
- Neue Tabelle `cv_analysis_results` mit optimierten Indizes
- JSON-basierte Speicherung für flexible Kategorien
- Skalierbare Score-Speicherung (Integer * 10 für Float-Präzision)

#### 2.3 Query-Optimierungen
- BigQuery-Schema-Analyse und korrekte Tabellen-Referenzen
- Von AgencyReporter-Dataset zu PflegehilfeSeniore_BI migriert
- dataform_staging für Lead-View identifiziert
- UNNEST für JSON-Array-Verarbeitung in BigQuery
- Timestamp-Konvertierung für String-basierte Datumsfelder

### 3. Datenmodell-Design

#### 3.1 Umfangreiche Datenintegration (der "Super-Endpoint")
**Care Stay Daten:**
- Basis-Informationen (ID, Daten, Status, Dauer)
- Korrekte cancelled_before_arrival Berechnung

**Agency Daten:**
- Agency ID und Name für Aggregationen

**Caregiver Daten (das Herzstück für CV-Analyse):**
- Care Giver Instance: Profil zum Zeitpunkt des Einsatzes
- Deutschnote (gs) mit Interpretation (1=Sehr gut bis 6=Ungenügend)
- Erfahrung (allgemein und Deutschland-spezifisch)
- Profilbeschreibung (für CV-Vergleich)
- Geburtsdatum (für Altersberechnung)
- Persönliche Daten (Name, Geschlecht, Telefon)

**Lead/Customer Daten (wichtige Erkenntnis: Lead ≠ Care Receiver):**
- Lead = Ansprechpartner (Sohn/Tochter), deren Kontaktdaten relevant sind
- Care Receiver = Pflegebedürftiger (nur Adresse relevant)
- Household als Bindeglied zwischen Lead und Care Receiver
- Vertriebspartner-Information für internen Kontext

**Care Location:**
- Tatsächliche Pflegeadresse (aus care_receivers)
- Wichtig für Kontext (z.B. Führerschein-Relevanz bei ländlicher Lage)

### 4. Technische Herausforderungen gemeistert

#### 4.1 BigQuery-Spezifika
- Korrekte Dataset-Identifikation (3 verschiedene Datasets im Einsatz)
- String-zu-Date Konvertierung mit PARSE_DATE/TIMESTAMP
- JSON-Verarbeitung mit UNNEST und JSON_EXTRACT_SCALAR
- Komplexe JOIN-Logik über care_giver_instances statt contracts

#### 4.2 Architektur-Entscheidungen
- MVP-Ansatz: Einzeleinsatz-Bewerter statt Vollautomatisierung
- "Überladener" Endpoint bewusst gewählt (1x täglich ist Speed unwichtig)
- Alle Daten in einem Call für Konsistenz und Flexibilität

### 5. Pydantic Models und Type Safety
- CareStayInfo Model mit 30+ Feldern
- CVAnalysisResult Model für strukturierte Analyse-Ergebnisse
- CVCategory Model für granulare Bewertungen
- Vollständige Type-Hints für bessere IDE-Unterstützung

## Entwicklungszeit-Einschätzung für erfahrenen Developer

### Optimistisches Szenario (Senior Developer, kennt den Tech-Stack):
- **Konzept & Planung**: 1-2 Stunden
- **API-Endpoints Implementation**: 3-4 Stunden
- **BigQuery-Queries entwickeln**: 2-3 Stunden (ohne Trial & Error bei Datasets)
- **Datenbank-Schema**: 1 Stunde
- **OpenAI-Integration**: 2 Stunden
- **Testing & Debugging**: 2-3 Stunden
- **Dokumentation**: 1 Stunde
**Gesamt: 12-16 Stunden**

### Realistisches Szenario (Senior Developer, neu im Projekt):
- **Projekt-Einarbeitung**: 2-3 Stunden
- **BigQuery-Schema verstehen**: 2-3 Stunden
- **Dataset-Verwirrung auflösen**: 2 Stunden
- **Konzept & Implementation**: 16 Stunden (wie oben)
- **Integration in bestehendes System**: 2 Stunden
**Gesamt: 24-28 Stunden (3-3.5 Arbeitstage)**

### Kritische Faktoren:
- BigQuery-Erfahrung essentiell (UNNEST, JSON-Funktionen)
- Verständnis der Domäne (Lead vs. Household vs. Care Receiver)
- Kenntnis der verschiedenen Datasets
- FastAPI/SQLAlchemy Erfahrung

## Erreichte Meilensteine
1. ✅ Vollständiger API-Endpoint mit allen relevanten Daten
2. ✅ Korrekte Filterung auf angetretene Einsätze
3. ✅ PDF-Upload und Parsing implementiert
4. ✅ OpenAI-Integration vorbereitet
5. ✅ Datenbank-Schema für Ergebnisspeicherung
6. ✅ Umfassende Dokumentation

## Nächste Schritte
1. Frontend-UI für CV-Upload und Analyse
2. Implementierung der Email/Ticket-Abruf-Logik
3. Feintuning der KI-Prompts für Enttäuschungserkennung
4. Aggregations-Endpoints für Agentur-Übersichten
5. Export-Funktionalität für Reports

## Fazit
In knapp 2 Stunden wurde die komplette Backend-Infrastruktur für das CV-Quality Feature implementiert. Die größten Herausforderungen waren das Verständnis der komplexen Datenbank-Struktur und die korrekte Identifikation der verschiedenen BigQuery-Datasets. Die Lösung ist bewusst als "Super-Endpoint" designed, der alle relevanten Daten in einem Call liefert - perfekt für den Use-Case mit geringer Abruf-Frequenz.