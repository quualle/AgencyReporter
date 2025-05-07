# Strategische & Taktische Planung – *Agency Reporter*

> Version: **v0.2-plan** · Scope: **7 Arbeitstage (Kurzfristig)** · Audience: **KI-Agenten & Vibe-Coder**

---

## 0 Zweck
Diese Datei legt alle strategischen, taktischen **und mittel-/langfristigen** Leitplanken fest. Sie dient der KI-gestützten Entwicklung ("Vibe-Coding") und muss maschinenverständlich und eindeutig sein.

---

## 1 Kurzfristige Ziele (nächste 7 aktive Arbeitstage)

| # | Deliverable | Nutzen | Acceptance Criteria |
|---|-------------|--------|---------------------|
| **1** | **Reaktionszeiten-Seite (RT-Page)** | Visualisiert, wie schnell Agenturen reagieren. | KPI-Kacheln, Chart "Abbrüche vor Anreise", Benchmarks, 200 ms Chart-Render, 90 % Testabdeckung |
| **2** | **Quoten-Seite (Quota-Page)** | Erfolgs- & Fehlerquoten der Agenturen transparent machen. | 8 KPI-Blöcke, parametrische SQL-Views, Heat-map, Interpretationen, CSV-Export |
| **3** | **Qualitätssicherung** | Verlässlichkeit der Zahlen & UI sicherstellen. | Playwright E2E Test, Lighthouse ≥ 85, dbt-Style Tests für SQL |
| **4** | **Dokumentation & Übergabe** | Schnelle Einarbeitung neuer KI-Instanzen. | README aktualisiert, SQL-Views kommentiert, CHANGELOG gepflegt |

---

## 2 Mittel- und Langfristige Ziele

| Bereich | Ziel | Beschreibung |
|--------|------|--------------|
| **Profilqualitäts-Analyse** | LLM-gestützte Regelverstoß-Erkennung | Vergleich von Profilangaben und realer Wahrnehmung auf Basis von E-Mail- und Ticketanalyse. |
| **LLM-Ursachenanalyse** | Gründe für Vorschlags- und Einsatzabbrüche | E-Mails und Tickets automatisch clustern, Zuordnung zu vordefinierten Problemkategorien, statistische Aufbereitung pro Agentur. |
| **XORA-Integration** | Vorbereitung der Datenstruktur | Aufbau eines Unstructured Ingest-Moduls (PoC) zur späteren Anbindung an XORA MCP. |
| **Graph-Augmented Retrieval** | LightRAG PoC | Vorbereitung für zukünftige hybride Such-/Analysefunktionen über Metadaten und Dokumenteninhalte. |
| **Automatische Agentur-Benachrichtigungen** | Slack-/E-Mail-Bot | Alert-System basierend auf Performance- oder Regelverstoßgrenzen. |
| **SSO & Rollen-Management** | Sicherheit und Benutzerfreundlichkeit | Zugriffskontrolle für verschiedene Benutzerrollen (CEO, Agenturbetreuer etc.). |
| **Performance & Kostenkontrolle** | BigQuery-Optimierung | Einsatz von Views, EXPLAIN-Analysen, Caching zur Reduktion von Abfragekosten. |


---

## 3 Kontext & Status-Quo

| Bereich | Aktueller Status |
|------|--------------|
| **Daten** | 32+ parametrisierte SQL-Queries; Rohdaten aus BigQuery. |
| **Domain** | Seniorenpflege-Vermittlung; Qualitätsanalyse von 45 Partneragenturen. |
| **Analysetiefe** | Aktuell Level-2 Metriken (Abbrüche, Reaktionszeiten); Level-3 (LLM-Analyse) geplant. |
| **Technologie-Stack** | React + TypeScript, FastAPI (Python), BigQuery, Docker. |
| **Zukunftsplattform** | XORA MCP, LightRAG, Gemini 2.5 Pro oder bestverfügbares Modell. |

---

## 4 Architektur & Verzeichnisstruktur

```
agentur-report/
  ├─ api/
  │   ├─ routes/
  │   ├─ controllers/
  │   └─ index.ts
  ├─ sql/
  │   ├─ views/
  │   └─ seeds/
  ├─ dashboard/
  │   ├─ src/
  │   └─ build/
  ├─ ingestion/          # Stretch-Goal
  ├─ docs/
  └─ tests/
```

---

## 5 Daten- und Analyse-Anforderungen

### 5.1 Profilqualität (Mittel-/Langfristig)
- Vergleich von Profilangaben (Alter, Erfahrung, Sprache etc.) und realer Wahrnehmung.
- LLM identifiziert und kategorisiert Regelverstöße.

### 5.2 Reaktionszeiten (Kurzfristig)
- 7 KPI-Messpunkte im Matching-Prozess.
- Visualisierung und Benchmarking.

### 5.3 Erfolgsquoten (Kurzfristig)
- 8 KPI-Quoten von Reservierung bis Einsatzende.
- Heatmap-Stärken-Schwächen-Darstellung.

### 5.4 LLM-Ursachenanalyse (Langfristig)
- Clustering und Kategorisierung von Gründen für Abbrüche vor/nach Antritt.
- **Implementation primär über n8n-Workflows** für maximale Flexibilität und einfache Wartung.
- **Prozessablauf zur Datenerfassung:**
  1. **Identifikation relevanter Einsätze** durch SQL-Queries:
     - Vor Ersteinsatz abgebrochene Einsätze (mit/ohne Ersatzlieferung)
     - Vor Wechseleinsatz abgebrochene Einsätze (mit/ohne Ersatzlieferung)
     - Nach Anreise >2 Wochen verkürzte Einsätze (mit Unterscheidung ob Folge-Einsatz oder Kündigung)
  2. **Kommunikationsdatenerfassung** für jeden identifizierten Einsatz:
     - Tickets aus BigQuery 
     - E-Mails aus Gmail (Technische Herausforderungen: E-Mail-Abfrage, Kundenadress-Ermittlung, Einzelabfrage)
  3. **LLM-basierte Analyse** der gesammelten Kommunikationsdaten
  4. **Kategorisierung** in vordefinierte Abbruch- und Beendigungsgründe
  5. **Statistische Aufbereitung** pro Agentur mit zeitbasierten Filteroptionen

- **Implementierte n8n-Workflows zur Problematic Stays Analyse:**
  1. **Analysewürdige Carestays Identifikation:** 
     - Identifiziert zwei Arten problematischer Einsätze:
       - `cancelled_before_arrival`: Abbrüche vor Anreise
       - `shortened_after_arrival`: Kürzungen laufender Carestays um mehr als 14 Tage
     - Relevante Metadaten werden in Supabase gespeichert
  
  2. **Ticket-Bezug für Problemfälle:**
     - Bei `cancelled_before_arrival`: Tickets ±14 Tage um das Abbruchdatum (event_date)
     - Bei `shortened_after_arrival`: Tickets während des Aufenthalts und 14 Tage danach
  
  3. **LLM-Analyse der Tickets:**
     - Bündelung der Tickets pro Carestay als "ticket_dump"
     - OpenAI Completions-Anfragen mit spezifischen Prompts je nach event_type
     - Zuordnung zu vordefinierten Gründen/Kategorien für Abbrüche
     - Bewertung der Kundenzufriedenheit und Konfidenz der Analysen
  
  4. **BigQuery-Export:** 
     - Übertragung in die BigQuery-Tabelle `gcpxbixpflegehilfesenioren.Agencyreporter.problematic_stays`
     - Schema enthält detaillierte Analysedaten inklusive KI-Bewertung und Metadaten

- **Wichtige Datenparameter für die Analyse:**
  - `days_difference`: Bei `cancelled_before_arrival` die Tage bis zur geplanten Anreise; bei `shortened_after_arrival` die Tage, um die der Einsatz verkürzt wurde
  - `has_replacement`/`has_follow_up`: Ob Ersatz bereitgestellt wurde oder ein Folgeeinsatz stattfand
  - `instant_departure_after`: Bei `shortened_after_arrival` die Anzahl der Tage, die der Einsatz gedauert hat (besonders kritisch wenn <10 Tage)
  - `analysis_result`: JSON-Struktur mit den Ergebnissen der LLM-Analyse (Grund, Konfidenz, Kundenzufriedenheit, Kommentar)

- **Leitfragen für die Datenanalyse der Problematic Stays:**
  1. **Quantitative Analyse:**
     - Wie viele Carestays hat eine Agentur insgesamt im Verhältnis zu problematischen Carestays?
     - Wie viele vorzeitige Abreisen (`shortened_after_arrival`) im Verhältnis zur Gesamtzahl?
     - Wie viele Abbrüche vor Anreise (`cancelled_before_arrival`) im Verhältnis zur Gesamtzahl?
     - Verteilung nach Einsatztyp (`first_stay` vs. `follow_stay`)?

  2. **Zeitliche Analyse:**
     - Bei `shortened_after_arrival`: Um wie viele Tage werden Einsätze durchschnittlich verkürzt?
     - Bei `cancelled_before_arrival`: Mit welcher Vorlaufzeit zur Anreise werden Abbrüche mitgeteilt?
     - Wie viele Pflegeeinsätze enden sehr kurz nach Antritt (< 10 Tage)?
     - Prozentsatz der Einsätze, die vor definiertem Zeitpunkt (z.B. 3 Tage) unplanmäßig enden?

  3. **Ersatz- und Folgeanalyse:**
     - Bei abgebrochenen Einsätzen: Wie oft wird Ersatz gestellt (`has_replacement`)?
     - Bei verkürzten Einsätzen: Wie oft folgt ein weiterer Einsatz (`has_follow_up`)?
     - Unterschiede zwischen Agenturen bei der Ersatzbereitstellung?

  4. **Ursachenanalyse basierend auf LLM-Ergebnissen:**
     - Häufigste Gründe für Abbrüche vor Anreise pro Agentur?
     - Häufigste Gründe für vorzeitige Beendigungen nach Anreise pro Agentur?
     - Verteilung der Kundenzufriedenheit bei problematischen Carestays?
     - Korrelation zwischen Abbruchgründen und Kundenzufriedenheit?
     - Konfidenzlevel der KI-Analyse zur Bewertung der Zuverlässigkeit?

  5. **Visualisierungsmöglichkeiten:**
     - Heatmap: Verteilung der Abbruch-/Beendigungsgründe pro Agentur
     - Balkendiagramm: Top 5 Gründe nach Einsatztyp
     - Tortendiagramm: Kundenzufriedenheitsverteilung
     - Zeitreihe: Entwicklung problematischer Einsätze über Zeit
     - Vergleichsansicht: Agenturen mit höchster/niedrigster Problemrate

### 5.5 Visuelle Darstellung
- Scatterplots, Säulendiagramme, Heatmaps, Line Charts, Tabellen.
- Responsive und optimiert für PDF-Export.

---

## 6 KI-Pipeline & Modellstrategie

- **Prinzip**: Always use best available LLM (OpenAI, Gemini, Claude)
- **Aktuell**: gpt-4o-mini für KPI-Interpretationen
- **Zukunft**: Hybrid-Architektur LightRAG + LLM für Ursachenanalyse

---

## 7 Risiken & Mitigations

| Risiko | Auswirkung | Gegenmaßnahme |
|--------|------------|---------------|
| **BQ-Kosten Spikes** | Budget-Überschreitung | Caching, Query-Optimierung, Kostenmonitoring |
| **LLM Halluzinationen** | Fehlerhafte Analysen | JSON-Validation, manuelle Stichproben |
| **Render-Lags** | Schlechte UX | Lazy Load, Memoization, kleinere Payloads |
| **GDPR-Probleme** | Datenschutzverstöße | Nur ID-Reporting; keine PII im Frontend |

---

## 8 Glossar

| Begriff | Bedeutung |
|---------|-----------|
| **MVP** | Minimal Viable Product – erste lauffähige Version |
| **KPI** | Key Performance Indicator – Leistungskennzahl |
| **RT-Page** | Reaktionszeiten-Seite |
| **Quota-Page** | Quoten/KPI-Seite |
| **View** | Parametrisierte SQL-Abfrage |
| **XORA** | Plattform für intelligente Datenprozesse |

---

*Ende der Datei – Änderungen bitte via Pull-Request oder ChatGPT-Prompt "update planning.md".*

