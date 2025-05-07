# Tasks für die Optimierung der Reaktionszeiten- und Quoten-Seite

## 1. Reaktionszeiten-Seite überprüfen
- [ ] Alle Widgets nochmals genau ansehen.
- [ ] Sicherstellen, dass jedes Widget eine konkrete Fragestellung des CEOs beantwortet.
- [ ] Plausibilität der Daten überprüfen, insbesondere auf Filter und SQL-Queries, die die Daten ungewollt verzerren könnten.pass

## 2. Quoten-Seite: Pipeline-Übersicht überarbeiten
- [x] Im Widget "Pipeline-Übersicht: von Stellenausschreibung bis Abschluss" die angezeigten Werte anpassen.
  - [x] "Personalvorschläge" zu "Stellen mit PV" umbenannt (28.06.2024)
  - [x] "Angetretene Einsätze" zu "Angetretene Ersteinsätze" präzisiert, um nur first_stays zu berücksichtigen (28.06.2024)
- [x] Überprüfen, welche SQL-Queries im Hintergrund genutzt werden.
  - [x] GET_PV_COUNT angepasst, um DISTINCT posting_id zu zählen (28.06.2024)
  - [x] GET_COMPLETED_CARE_STAYS optimiert, um auch Verlängerungen und leichte Verkürzungen (bis 14 Tage) als erfolgreich zu werten (28.06.2024)
- [x] Sicherstellen, dass im Erfolgsfunnel die tatsächlichen absoluten Zahlen dargestellt werden.
- [x] Dropdown-Menü zur Auswahl von "Nur Ersteinsätze", "Nur Wechseleinsätze" und "Gesamt" hinzugefügt (29.06.2024)

## 3. Konfigurierbarer Vergleichswert im Dashboard
- [x] Vergleichswert variabel über ein Dropdown auswählbar machen (08.07.2024)
  - [x] Durchschnitt aller Agenturen (Standard)
  - [x] Historischer Wert der gleichen Agentur aus einer Vorperiode
  - [x] Vergleich mit einer frei auswählbaren anderen Agentur
- [x] Sicherstellen, dass die optische Struktur und Klarheit des Dashboards erhalten bleibt (09.07.2024)

## 4. Top-Ten- und Flop-Ten-Anzeige für jede KPI
- [ ] Für ausgewählte KPIs die Top-Ten und Flop-Ten Agenturen anzeigen
  - [ ] Button zum Ein- und Ausblenden implementieren
  - [ ] Zunächst auf ein bis zwei exemplarische KPIs beschränken
  - [ ] Dashboard optisch aufgeräumt halten

## 5. Gesamtrangliste auf Basis aller KPIs
- [ ] Rangliste der Agenturen basierend auf allen KPIs erstellen
- [ ] Gewichtung der KPIs konfigurierbar machen
- [ ] Beste Agentur auf Basis einer Gesamtbewertung identifizieren

## 6. Monitoring- und Long-Term-Watcher-System
- [ ] System zur Überwachung von KPIs entwickeln (ggf. mit n8n)
- [ ] Automatische Benachrichtigungen bei Über- oder Unterschreitung von Schwellenwerten konfigurieren
- [ ] Sicherstellen, dass wichtige Ereignisse (negativ oder positiv) nicht unbemerkt bleiben

## 7. Quoten-Seite: Kleine Widgets überprüfen
- [ ] **Reservierungsrate:**  
  - [ ] Der dargestellte Wert scheint im Format 1-x falsch zu sein.  
  - [ ] SQL-Query überprüfen und ggf. korrigieren.
- [ ] **Eindeutige Reservierungen:**  
  - [ ] Scheint korrekt, sollte aber zur Sicherheit überprüft werden.
- [ ] **Reservierungserfüllungsrate:**  
  - [ ] Ebenfalls korrekt erscheinend, dennoch eine Kontrolle der SQL-Query erforderlich.
- [ ] **Abbruchrate vor Anreise:**  
  - [ ] Aktuell korrekt dargestellt.  
  - [ ] Ergänzen um:  
    - [ ] Abbruchrate nach Anreise  
    - [ ] Abbruchrate gesamt (Summe beider Abbruchraten)

## 8. Quoten-Seite: Trendanalyse und Periodenvergleich optimieren
- [ ] **Button "Trend anzeigen" prominenter positionieren**, da er wichtig ist und aktuell zu wenig Aufmerksamkeit bekommt.
- [ ] **Trendanalyse: Quoten im Zeitverlauf:**  
  - [ ] Y-Achse sinnvoll skalieren, um Veränderungen besser erkennbar zu machen.
  - [ ] Optional: Delta (Veränderung) statt absolute Werte anzeigen, um Trends sichtbarer zu machen.
  - [ ] SQL-Query identifizieren und inhaltlich überprüfen.
- [ ] **Periodenvergleich: aktuell vs. Vorperiode vs. Vorjahr:**  
  - [ ] Optische Optimierung zur besseren Lesbarkeit (weniger visuelle Überlastung).
  - [ ] Überlegen, die auswählbaren Vergleichszeiträume einstellbar zu machen oder zumindest die exakten Zeiträume (mit Datumsangabe) einzublenden.

## 9. Quoten-Seite: Detaillierte KPIs und Export-Funktion
- [ ] Widget "Detaillierte KPIs" weiterhin am unteren Ende der Seite belassen.
- [ ] Button zum Export der Rohdaten hinzufügen, um eine schnelle KI-gestützte Analyse zu ermöglichen.
- [ ] Neben dem "Als PDF exportieren"-Button einen neuen Button "Zu den detaillierten KPIs" einfügen, der direkt zu diesem Abschnitt scrollt.

## 10. Quoten-Seite: Vergleich mit anderen Agenturen
- [x] Neue "Vergleichsansicht" Dropdown-Funktionalität vollständig implementieren:
  - [x] "Mit sich selbst" Ansicht implementieren (09.07.2024)
  - [x] "Mit anderer Agentur" Ansicht implementieren (09.07.2024)
  - [x] "Mit Durchschnitt" Ansicht implementieren (Standard) (08.07.2024)
- [ ] Widget "Mit anderen Agenturen vergleichen" mit realen Daten befüllen
- [x] Integration mit "Konfigurierbarem Vergleichswert" (Punkt 3) (09.07.2024)

## 11. Implementierung des "quotas_with_reasons"-Moduls
- [x] n8n-Workflow für die Identifikation relevanter Einsätze erstellen
  - [x] SQL-Query für abgebrochene Ersteinsätze entwickeln (mit/ohne Ersatzlieferung)
  - [x] SQL-Query für abgebrochene Wechseleinsätze entwickeln (mit/ohne Ersatzlieferung)
  - [x] SQL-Query für nach Anreise verkürzte Einsätze (>2 Wochen) entwickeln
  - [x] Unterscheidung zwischen verkürzten Einsätzen mit Folgeeinsatz vs. Kündigung
- [x] n8n-Workflow für Kommunikationsdatenerfassung implementieren
  - [x] Ticket-Daten aus BigQuery abrufen
  - [ ] E-Mail-Abfrage aus Gmail implementieren
  - [ ] Kundenemailadressen aus Leaddaten in BigQuery ermitteln
  - [x] Mapping von Einsätzen zu relevanten Kommunikationen
- [x] LLM-Analyse-Workflow in n8n erstellen
  - [x] Vorverarbeitung der Kommunikationsdaten
  - [x] Integration mit OpenAI API
  - [x] Entwicklung des Prompting-Templates für die Kategorisierung
  - [x] Parsing und Nachbearbeitung der LLM-Ergebnisse
- [x] Datenspeicherung für die Analyseergebnisse einrichten
  - [x] Schema für Abbruch- und Beendigungsgründe definiert (in BigQuery-Tabelle)
  - [x] Speicherort festgelegt: BigQuery-Tabelle `gcpxbixpflegehilfesenioren.Agencyreporter.problematic_stays`
- [ ] Frontend-Komponenten für "Abbruch-Gründe Analyse" erstellen
  - [ ] Dashboard-Widget für häufigste Abbruchgründe
  - [ ] Filtermöglichkeiten nach Zeitraum und Agentur
  - [ ] Detailansicht für einzelne Abbruchkategorien
- [ ] Frontend-Komponenten für "Vorzeitige Beendigungs-Gründe" erstellen
  - [ ] Dashboard-Widget für häufigste Beendigungsgründe
  - [ ] Vergleichsansicht zwischen Agenturen
  - [ ] Trend-Analyse über Zeit

### Implementierte n8n-Workflows für Problematic Stays

Es wurden drei miteinander verknüpfte n8n-Workflows implementiert:

1. **Workflow 1: Identifikation analysewürdiger Carestays**
   - Identifiziert zwei Arten problematischer Pflegeeinsätze:
     - `cancelled_before_arrival`: Abbrüche vor Anreise
     - `shortened_after_arrival`: Kürzungen laufender Carestays um mehr als 14 Tage
   - Speichert relevante Metadaten in Supabase-Datenbank

2. **Workflow 2: Ticket-Sammlung für jeden Problemfall**
   - Bei `cancelled_before_arrival`: Tickets ±14 Tage um das Abbruchdatum (event_date)
   - Bei `shortened_after_arrival`: Tickets während des Aufenthalts (arrival - departure) und 14 Tage danach
   - Erstellt einen "ticket_dump" pro Carestay

3. **Workflow 3: LLM-Analyse und Kategorisierung**
   - Verwendet unterschiedliche Prompts je nach event_type:
     - `cancelled_before_arrival`: Prompt für Abbruchgründe vor Anreise
     - `shortened_after_arrival`: Prompt für Gründe bei vorzeitiger Beendigung nach Anreise
   - OpenAI-Integration zur Zuordnung zu vordefinierten Gründen
   - Bewertet Kundenzufriedenheit und Konfidenzniveau
   - Generiert einen erklärenden Kurzkommentar

4. **Workflow 4: BigQuery-Export**
   - Überträgt Analyseergebnisse in die BigQuery-Tabelle `gcpxbixpflegehilfesenioren.Agencyreporter.problematic_stays`
   - Schema enthält alle erforderlichen Felder für die Analyse

Die KI-Analyse verwendet zwei unterschiedliche Prompt-Templates:
- Für `cancelled_before_arrival`: Fokus auf Abbruchgründe vor Anreise (z.B. "BK - ohne Grund abgesagt", "BK - hat Verletzung", etc.)
- Für `shortened_after_arrival`: Fokus auf Gründe für vorzeitige Beendigung (z.B. "BK - Deutschkenntnisse zu schlecht", "BK - Fühlt sich unwohl", etc.)

Das Ergebnis wird als JSON gespeichert mit folgender Struktur:
```json
{
  "selected_reason": "String (einer der vordefinierten Gründe)",
  "confidence": "Integer (0-100)",
  "customer_satisfaction": "String (satisfied/not_satisfied/n/a)",
  "confidence_cussat": "Integer (0-100)",
  "comment": "String (10-15 Worte Zusammenfassung)"
}
```

## 12. Problematic Stays Analyse-Modul

### 12.1 SQL und API-Endpunkte für Problematic Stays

- [ ] **Basisendpunkt für problematische Carestays erstellen**
  - [ ] SQL-Query für allgemeine Statistiken entwickeln
  - [ ] API-Route `/api/problematic-stays/overview` implementieren
  - [ ] Parameter für Zeitraum- und Agenturfilterung einbauen

- [ ] **Endpunkte für spezifische Analysen erstellen**
  - [ ] `/api/problematic-stays/by-event-type`: Abbrüche vor/nach Anreise aufschlüsseln
  - [ ] `/api/problematic-stays/by-stay-type`: First-Stay vs. Follow-Stay analysieren
  - [ ] `/api/problematic-stays/time-analysis`: Zeitliche Analysen (Tage bis Abbruch/Vorlaufzeit)
  - [ ] `/api/problematic-stays/replacement-analysis`: Ersatz- und Folgeanalyse
  - [ ] `/api/problematic-stays/reasons`: Häufigste Gründe, extrahiert aus analysis_result
  - [ ] `/api/problematic-stays/customer-satisfaction`: Kundenzufriedenheitsanalyse

- [ ] **SQL-Views optimieren**
  - [ ] JSON-Extraktion für analysis_result-Felder im SQL implementieren
  - [ ] Berechnungen für Prozentsätze und Verhältniswerte optimieren
  - [ ] Performanzoptimierung für Zeitreihenabfragen

### 12.2 Frontend-Implementierung für Problematic Stays

- [ ] **Übersichtsseite für Problematic Stays erstellen**
  - [ ] Layout mit KPI-Kacheln und Filteroptionen entwerfen
  - [ ] Schnittstelle zur API implementieren
  - [ ] Responsive Design für verschiedene Bildschirmgrößen

- [ ] **KPI-Widgets für quantitative Analyse erstellen**
  - [ ] Widget für Gesamtverhältnis problematischer Einsätze
  - [ ] Widget für Abbruchquote vor Anreise
  - [ ] Widget für Verkürzungsquote nach Anreise
  - [ ] Vergleichsansicht mit Durchschnitt/historischen Daten

- [ ] **Charts für zeitliche Analyse implementieren**
  - [ ] Balkendiagramm für durchschnittliche Verkürzung/Vorlaufzeit
  - [ ] Tortendiagramm für Einsätze mit sehr frühem Ende (<10 Tage)
  - [ ] Zeitreihendiagramm für Entwicklung über Zeit

- [ ] **Visualisierungen für Ursachenanalyse erstellen**
  - [ ] Heatmap: Verteilung der Gründe nach Agenturen
  - [ ] Balkendiagramm: Top 5 Gründe nach Einsatztyp
  - [ ] Tortendiagramm: Kundenzufriedenheitsverteilung

- [ ] **Detailansicht für einzelne problematische Carestays**
  - [ ] Tabelle mit Suchfunktion für individuelle Carestays
  - [ ] Detail-Modal mit vollständigen Informationen inkl. Kommentar
  - [ ] Export-Funktionalität für Rohdaten

### 12.3 Spezialberichte und Drilldown-Funktionen

- [ ] **Spezialberichte für Management implementieren**
  - [ ] "Problemagenturen"-Bericht mit Ranking nach Problemhäufigkeit
  - [ ] "Frühabbrecher"-Bericht (Fokus auf <10 Tage Einsatzlänge)
  - [ ] "Ersatz-Effizienz"-Bericht (Analyse der Ersatzbereitstellung)

- [ ] **Drilldown-Funktionen für Analysten**
  - [ ] Interaktive Filterung nach allen relevanten Parametern
  - [ ] Dynamische Chartgenerierung basierend auf Filterauswahl
  - [ ] Exportmöglichkeiten für weiterführende Analysen

- [ ] **Dashboard-Integration**
  - [ ] Wichtigste KPIs in bestehende Dashboards integrieren
  - [ ] Toggle für tiefergehende Analyse hinzufügen
  - [ ] Konsistente Designsprache sicherstellen

## Gefundene und behobene Probleme (in chronologischer Reihenfolge)

- **28.06.2024 - Korrektur der Personalvorschläge-Zählung**: 
  Die `GET_PV_COUNT`-Abfrage wurde geändert, um nur einzigartige Stellenausschreibungen mit Personalvorschlägen zu zählen (`COUNT(DISTINCT v.posting_id)`) anstatt alle Personalvorschläge.

- **28.06.2024 - Präzisierung der Pipeline-Übersicht**: 
  Die "Angetretene Einsätze" wurden zu "Angetretene Ersteinsätze" präzisiert, um klarzustellen, dass nur first_stays (is_swap = "false") in der Fortschrittskette berücksichtigt werden, nicht alle Einsätze.

- **28.06.2024 - Verbesserte Definition der "Abgeschlossene Einsätze"**: 
  Die `GET_COMPLETED_CARE_STAYS`-Abfrage wurde optimiert, um auch Verlängerungen und leichte Verkürzungen des Abreisedatums (bis zu 14 Tage) als erfolgreich abgeschlossen zu werten. Nur starke Verkürzungen werden als nicht erfolgreich betrachtet.

- **28.06.2024 - Korrektur der Prozentberechnung in "Erfolgsschritte im Prozess"**:
  Die Prozentberechnung für "Einsatz vollständig durchgezogen" wurde korrigiert, sodass sie sich auf "Angetretene Ersteinsätze" bezieht und nicht auf eine vorhergehende Stufe.

- **28.06.2024 - Identifikation des Problems mit fehlendem Balken**:
  Es wurde festgestellt, dass im "Erfolgsschritte im Prozess"-Diagramm der Balken für "Einsatz vollständig durchgezogen" nicht angezeigt wird, obwohl die Daten korrekt vorbereitet werden. Eine Debug-Anzeige wurde hinzugefügt, um die tatsächlichen Werte anzuzeigen und eine Lösung zu finden.

- **29.06.2024 - Implementierung eines Einsatztyp-Filters**:
  Ein Dropdown-Menü wurde zur Pipeline-Übersicht hinzugefügt, das zukünftig erlaubt, zwischen "Nur Ersteinsätzen", "Nur Wechseleinsätzen" und "Gesamt" zu filtern. Die Funktionalität ist als "In Entwicklung" gekennzeichnet und wird in einem späteren Update vollständig implementiert.

- **08.07.2024 - Implementierung des variablen Vergleichswerts**:
  Ein Dropdown-Menü wurde hinzugefügt, mit dem der Benutzer zwischen verschiedenen Vergleichswerten wählen kann: "Mit Durchschnitt" (Standard), "Mit sich selbst" (historischer Vergleich) und "Mit anderer Agentur". Entsprechende API-Funktionen wurden implementiert und die UI wurde angepasst, um die Auswahl unterschiedlicher Vergleichsparameter zu ermöglichen.

- **09.07.2024 - Implementierung des historischen Vergleichs**:
  Der historische Vergleich wurde implementiert, indem auf den gleichen API-Endpunkt mit einem unterschiedlichen Zeitraumparameter zugegriffen wird. Da das Backend derzeit nur begrenzte Zeitraumparameter unterstützt, wird temporär 'last_year' als Parameter für alle historischen Vergleiche verwendet. Die UI wurde angepasst, um zwischen "Vorquartal", "Vorjahr" und "Letzte 6 Monate" auszuwählen und die entsprechenden Vergleichsdaten anzuzeigen.

## 13. Implementierung des Problematic Stays Dashboards

### 13.1 Frontend-Komponenten für das Übersichtsdashboard
- [x] **Hauptstatistik-Widget erstellen**
  - [x] Komponente für KPI-Kacheln entwickeln (Gesamtzahl problematischer Einsätze, Abbrüche vor Anreise, vorzeitige Beendigungen, sofortige Abreisen)
  - [x] Vergleichswerte zum Durchschnitt/Vorperiode hinzufügen
  - [x] Trend-Indikatoren (Pfeile) für Entwicklung implementieren
  - [x] Mit `/api/problematic_stays/overview` API-Endpunkt verbinden
  - [x] Filter für Zeitraum implementieren

- [x] **Verteilungsdiagramm erstellen**
  - [x] Säulendiagramm zur Darstellung der Verteilung nach Problemtyp und Einsatztyp
  - [x] Farbliche Differenzierung zwischen first_stay und follow_stay
  - [x] Tooltip mit detaillierten Informationen
  - [x] Mit `/api/problematic_stays/overview` API-Endpunkt verbinden
  - [x] Responsive Design für verschiedene Bildschirmgrößen

### 13.2 Widgets für zeitliche Analyse
- [x] **Vorlaufzeit-Analyse-Widget erstellen**
  - [x] Box-Plot oder ähnliches Diagramm zur Darstellung der Vorlaufzeit bei Abbrüchen
  - [x] Durchschnittslinie implementieren
  - [x] Mit `/api/problematic_stays/time-analysis` API-Endpunkt verbinden
  - [x] Filter für event_type="cancelled_before_arrival" implementieren

- [x] **Verkürzungsdauer-Analyse-Widget erstellen**
  - [x] Diagramm zur Darstellung der Verkürzungsdauer
  - [x] Markierung kritischer Bereiche (>30 Tage)
  - [x] Mit `/api/problematic_stays/time-analysis` API-Endpunkt verbinden
  - [x] Filter für event_type="shortened_after_arrival" implementieren

- [x] **Sofortige-Abreise-Widget erstellen**
  - [x] Balkendiagramm für Einsätze mit sofortiger Abreise (<10 Tage)
  - [x] Filtern der Daten für instant_departure_after IS NOT NULL
  - [x] Gruppierung nach Tagen (1-9)
  - [x] Mit `/api/problematic_stays/overview` oder spezieller Abfrage verbinden

### 13.3 Widgets für Ersatz- und Folgeanalyse
- [ ] **Ersatzbereitstellungs-Widget erstellen**
  - [ ] Donut-Chart zur Darstellung der Ersatzbereitstellung
  - [ ] KPI zur Anzeige der Ersatzbereitstellungsquote
  - [ ] Vergleich mit Durchschnitt
  - [ ] Mit `/api/problematic_stays/overview` API-Endpunkt verbinden

- [ ] **Folgeeinsatz-Analyse-Widget erstellen**
  - [ ] Donut-Chart zur Darstellung der Folgeeinsätze
  - [ ] KPI zur Anzeige der Folgeeinsatzquote
  - [ ] Vergleich mit Durchschnitt
  - [ ] Mit `/api/problematic_stays/overview` API-Endpunkt verbinden

### 13.4 Widgets für Ursachenanalyse
- [ ] **Widget für Abbruchgründe erstellen**
  - [ ] Horizontales Balkendiagramm für die Top 5 Gründe
  - [ ] Vergleich mit Durchschnitt aller Agenturen
  - [ ] Mit `/api/problematic_stays/reasons` API-Endpunkt verbinden
  - [ ] Filter für event_type="cancelled_before_arrival" implementieren

- [ ] **Widget für Beendigungsgründe erstellen**
  - [ ] Horizontales Balkendiagramm für die Top 5 Gründe
  - [ ] Vergleich mit Durchschnitt aller Agenturen
  - [ ] Mit `/api/problematic_stays/reasons` API-Endpunkt verbinden
  - [ ] Filter für event_type="shortened_after_arrival" implementieren

- [ ] **Kundenzufriedenheits-Widget erstellen**
  - [ ] Donut-Chart zur Darstellung der Kundenzufriedenheit
  - [ ] Segmente für zufrieden/unzufrieden/neutral
  - [ ] Mit `/api/problematic_stays/overview` oder spezieller Abfrage verbinden
  - [ ] Filter nach Problemtyp und Grund implementieren

- [ ] **Heatmap für Gründe nach Agenturen erstellen**
  - [ ] Matrix mit Agenturen auf X-Achse und Gründen auf Y-Achse
  - [ ] Farbskala zur Darstellung der Häufigkeit
  - [ ] Mit `/api/problematic_stays/reasons` API-Endpunkt verbinden
  - [ ] Tooltip mit detaillierten Informationen

### 13.5 Zeitreihenanalyse-Widgets
- [ ] **Entwicklungs-Widget über Zeit erstellen**
  - [ ] Liniendiagramm zur Darstellung der monatlichen Entwicklung
  - [ ] Mehrere Linien für verschiedene Problemtypen
  - [ ] Mit `/api/problematic_stays/time-analysis` API-Endpunkt verbinden
  - [ ] Option zum Vergleich mit Vorjahr

### 13.6 Detailtabelle und Dashboard-Integration
- [ ] **Detailtabelle für Einzelfallansicht erstellen**
  - [ ] Interaktive Tabelle mit filterbaren Einsätzen
  - [ ] Erweiterbare Zeilen für Details
  - [ ] Mit `/api/problematic_stays/{agency_id}/detailed` API-Endpunkt verbinden
  - [ ] Pagination und Suchfunktion

- [ ] **Dashboard-Integration**
  - [ ] Layout für das gesamte Dashboard erstellen
  - [ ] Dashboard-Seite zur Navigation hinzufügen
  - [ ] Responsive Design für verschiedene Bildschirmgrößen
  - [ ] Export-Funktionalität (PDF, CSV) implementieren
  - [ ] Filter-Leiste für globale Filterung nach Agentur, Zeitraum, etc.

### 13.7 Qualitätssicherung und Dokumentation
- [ ] **Tests schreiben**
  - [ ] Unit-Tests für API-Aufrufe
  - [ ] Komponentententests für Visualisierungen
  - [ ] End-to-End-Tests für Dashboard

- [ ] **Dokumentation aktualisieren**
  - [ ] README.md mit Beschreibung der neuen Funktionalität
  - [ ] API-Dokumentation für neue Endpunkte
  - [ ] Benutzerhandbuch mit Screenshots und Erklärungen

- [ ] **Performance-Optimierung**
  - [ ] Caching für API-Antworten implementieren
  - [ ] Lazy Loading für Dashboard-Komponenten
  - [ ] Memoization für rechenintensive Operationen
