# Vollständiger Ausbau des Agenturvergleichsmoduls

## 1. Verfügbare API-Endpoints und Nutzungsmöglichkeiten

### 1.1 Kernendpoints für Agenturvergleiche

- **Grundlegende Daten und KPIs**
  - `/api/agencies/` - Liste aller Agenturen
  - `/api/kpis/filter` - KPIs für alle Agenturen basierend auf Zeitfilter
  - `/api/kpis/compare` - Vergleich einer Agentur mit allen anderen und Branchendurchschnitt

- **Leistungsfähigkeit und Volumen**
  - `/api/quotas/postings` - Metriken für alle Ausschreibungen
  - `/api/quotas/stats/overall/cancellation-before-arrival` - Durchschnittliche Stornierungsstatistiken
  - `/api/reaction_times/filter` - Reaktionszeiten für alle Agenturen

- **Qualitäts- und Problemmetriken**
  - `/api/problematic_stays/overview` - Statistiken zu problematischen Einsätzen (mit/ohne agency_id)
  - `/api/problematic_stays/reasons` - Gründe für problematische Einsätze
  - `/api/problematic_stays/heatmap` - Heatmap-Analyse der Abbruchgründe nach Agentur
  - `/api/profile_quality/filter` - Profilqualitätsmetriken für alle Agenturen
  - `/api/llm_analysis/{agency_id}/strength-weakness` - Stärken und Schwächen einer Agentur

### 1.2 Tiefergehende Analyse-Endpoints

- **Zeitliche Analyse**
  - `/api/problematic_stays/time-analysis` - Zeitliche Trends problematischer Einsätze
  - `/api/problematic_stays/trend-analysis` - Längerfristige Entwicklungstrends

- **Detailanalysen**
  - `/api/problematic_stays/customer-satisfaction` - Kundenzufriedenheit bei Problemfällen
  - `/api/problematic_stays/replacement-analysis` - Ersatzbereitstellung bei Abbrüchen
  - `/api/quotas_with_reasons/{agency_id}/all-problem-cases` - Alle Problemfälle mit Gründen

## 2. Umfassende Strategie für den Agenturvergleich

Die überarbeitete Agenturvergleichsseite muss folgende strategische Aspekte abdecken:

1. **Marktpositionierung und Volumen** - Welche Agenturen dominieren den Markt?
2. **Leistungseffizienz** - Welche Agenturen arbeiten am effizientesten?
3. **Qualitätsführerschaft** - Welche Agenturen liefern die höchste Qualität?
4. **Problemmanagement** - Welche Agenturen bewältigen Probleme am besten?
5. **Gesamtperformance** - Welche Agenturen sind insgesamt am leistungsstärksten?

## 3. Konzeption und Design des Agenturvergleichsmoduls

### 3.1 Hauptbereiche der Agenturvergleichsseite

1. **Übersichts-Dashboard**
   - Zeigt die Top-3 und Flop-3 Agenturen basierend auf einer konfigurierbaren Gesamtbewertung
   - Enthält eine Gesamtrangliste mit konfigurierbarer Gewichtung der KPIs
   - Ermöglicht das Speichern benutzerdefinierter Gewichtungsprofile

2. **Marktposition und Volumen**
   - Horizontales Balkendiagramm mit dem Gesamtvolumen jeder Agentur
   - Treemap-Visualisierung für Marktanteile
   - Historische Entwicklung der Marktanteile als Liniendiagramm

3. **Reaktionsgeschwindigkeit und Effizienz**
   - Vergleich der durchschnittlichen Reaktionszeiten in verschiedenen Phasen
   - "Zeit-bis-zur-Reservierung"-Benchmark für alle Agenturen
   - "Zeit-bis-zur-Personalvorstellung"-Vergleich

4. **Qualitätsvergleich**
   - Matrix-Visualisierung von Profilqualitätsmetriken (Verstöße je Kategorie)
   - Erfüllungsquoten und Abschlussraten im Vergleich
   - KI-generierte Qualitätsbewertung durch LLM-Analyse

5. **Problemmanagement-Vergleich**
   - Stacked-Bar-Chart für Abbruchgründe nach Agentur
   - Heatmap der problematischen Einsätze nach Typ und Agentur
   - Radar-Chart für Problemmanagement-Metriken

### 3.2 Interaktive Analysefunktionen

1. **Direktvergleich zweier Agenturen**
   - Side-by-Side-Vergleich aller relevanten Metriken
   - Hervorhebung signifikanter Unterschiede
   - Grafische Gegenüberstellung der Stärken und Schwächen

2. **"Was-wäre-wenn"-Szenarien**
   - Simulationstool zum Visualisieren von Verbesserungspotenzialen
   - Zielwert-Definition und Abstandsanalyse zum Branchenbesten

3. **Trendanalyse-Tools**
   - Interaktives Liniendiagramm zur Anzeige der zeitlichen Entwicklung wichtiger KPIs
   - Vergleich mehrerer Agenturen über verschiedene Zeitperioden

### 3.3 Visualisierungsansätze für wichtige Metriken

| Metrik | Visualisierungstyp | API-Endpoint |
|--------|-------------------|--------------|
| Gesamtvolumen | Horizontales Balkendiagramm | `/api/kpis/filter` |
| Marktanteile | Treemap oder Donut-Chart | `/api/kpis/filter` |
| Problematische Einsätze | Heatmap | `/api/problematic_stays/heatmap` |
| Reaktionszeiten | Grouped Bar Chart | `/api/reaction_times/filter` |
| Abbruchgründe | Stacked Bar Chart | `/api/problematic_stays/reasons` |
| Qualitätsmetriken | Radar-Chart | `/api/profile_quality/filter` |
| Gesamtbewertung | Sortierbare Tabelle mit Mikro-Sparklines | Aggregiert aus mehreren Endpoints |
| Zehn-Wochen-Trend | Small Multiples Liniendiagramm | `/api/problematic_stays/trend-analysis` |
| Stärken/Schwächen | Butterfly-Chart | `/api/llm_analysis/{agency_id}/strength-weakness` |

## 4. Implementierungsroadmap

### 4.1 Phase 1: Grundlegende Vergleichsansicht (Kurzfristig)

- [x] **Scrollbare Listen aller Agenturen nach verschiedenen Metriken**
   - [x] Implementierung eines scrollbaren `AgencyRankingList`-Components
   - [x] Integration der relevanten API-Endpoints
   - [x] Styling und UI-Verbesserungen

- [ ] **Erweiterter Vergleichsdaten-Abruf**
   - [ ] Implementierung eines Batch-Abrufs für alle benötigten API-Endpoints
   - [ ] Caching-Mechanismen für Vergleichsdaten
   - [ ] Progressives Laden der Daten mit visuellen Lade-Indikatoren

- [ ] **Verbesserte Navigations- und Filteroptionen**
   - [ ] Implementierung konfigurierbarer Filter für alle Listen
   - [ ] Speichern von Filtereinstellungen im App-State
   - [ ] "Vergleichen"-Funktion für ausgewählte Agenturen hinzufügen

### 4.2 Phase 2: Erweiterte Visualisierungen (Mittelfristig)

- [ ] **Implementierung der Kernvisualierungen**
   - [ ] Heatmap für Problemverteilung nach Agentur
   - [ ] Marktanteil-Treemap für Volumenvisualisierung
   - [ ] Radar-Charts für multidimensionale KPI-Vergleiche
   - [ ] Reaktionszeit-Vergleichsdiagramme

- [ ] **Detailvergleichsansichten**
   - [ ] Side-by-Side-Vergleich zweier ausgewählter Agenturen
   - [ ] Trendlinien für wichtige KPIs
   - [ ] Detail-Drilldowns für spezifische Metriken

- [ ] **UI/UX-Optimierungen**
   - [ ] Einheitliches Design für alle Visualisierungen
   - [ ] Responsive Anpassungen für verschiedene Bildschirmgrößen
   - [ ] Tooltip- und Interaktionsmechanismen verbessern

### 4.3 Phase 3: Fortgeschrittene Analyse-Features (Langfristig)

- [ ] **Implementierung der Gesamtbewertung**
   - [ ] Entwicklung eines gewichteten Scoring-Systems
   - [ ] UI für die Anpassung der Gewichtungen
   - [ ] Speichern und Laden von Bewertungsprofilen

- [ ] **"Was-wäre-wenn"-Analysetools**
   - [ ] UI zur Definition von Zielwerten
   - [ ] Visualisierung von Verbesserungspotenzialen
   - [ ] Vergleichsanalyse mit Best Practices

- [ ] **Performance-Optimierungen**
   - [ ] Verbessertes Daten-Caching
   - [ ] Lazy Loading von komplexen Visualisierungen
   - [ ] Backend-Unterstützung für aggregierte Daten

## 5. Detaillierte Anforderungen an Visualisierungen

### 5.1 Marktanteil und Volumen

**Treemap-Visualisierung der Marktanteile**
- **Datenquelle**: `/api/kpis/filter` zur Berechnung der Marktanteile basierend auf Gesamteinsätzen
- **Beantwortete Frage**: Wie ist die Größenverteilung der Agenturen im Markt?
- **Umsetzung**: Rechtecke proportional zum Marktanteil; Farbkodierung nach Effizienz (z.B. Verhältnis erfolgreicher Einsätze)
- **Interaktivität**: Hover für detaillierte Informationen, Klick für Agenturdetails

**Horizontales Balkendiagramm für Gesamteinsätze**
- **Datenquelle**: `/api/kpis/filter` für absolute Zahlen der Einsätze
- **Beantwortete Frage**: Welche Agenturen haben das höchste Volumen?
- **Umsetzung**: Sortierte Balken mit absoluten Zahlen und prozentualen Anteilen
- **Interaktivität**: Sortierung nach verschiedenen Zeiträumen (Quartal, Jahr, Gesamt)

### 5.2 Effizienz- und Reaktionszeitvergleich

**Multi-Metrik-Vergleichsdiagramm für Reaktionszeiten**
- **Datenquelle**: `/api/reaction_times/filter` für verschiedene Zeitmetriken
- **Beantwortete Frage**: Welche Agenturen reagieren am schnellsten in welchen Prozessschritten?
- **Umsetzung**: Grouped Bar Chart mit verschiedenen Zeitkategorien pro Agentur
- **Zusatzinfo**: Branchendurchschnitt als Referenzlinie

**Prozesseffizienz-Trendlinien**
- **Datenquelle**: `/api/reaction_times/filter` mit historischen Daten
- **Beantwortete Frage**: Verbessern sich Agenturen in ihrer Reaktionsgeschwindigkeit?
- **Umsetzung**: Small Multiples für Top-5-Agenturen mit Trendlinien
- **Strategische Erkenntnis**: Identifikation systematischer Verbesserungen oder Verschlechterungen

### 5.3 Qualitäts- und Problemmanagement

**Heatmap der problematischen Einsätze**
- **Datenquelle**: `/api/problematic_stays/heatmap`
- **Beantwortete Frage**: Wo liegen die Hauptproblembereiche jeder Agentur?
- **Umsetzung**: Farbkodierte Matrix mit Agenturen in Zeilen und Problemtypen in Spalten
- **Strategische Erkenntnis**: Muster in den Problemarten nach Agentur identifizieren

**Abbruchgründe-Vergleich**
- **Datenquelle**: `/api/problematic_stays/reasons` für verschiedene Agenturen
- **Beantwortete Frage**: Unterscheiden sich die Hauptgründe für Abbrüche zwischen Agenturen?
- **Umsetzung**: Grouped oder Stacked Bar Chart mit Top-5-Gründen pro Agentur
- **Zusatzinfo**: Vergleich zu Branchendurchschnitt

**Kundenzufriedenheits-Vergleich**
- **Datenquelle**: `/api/problematic_stays/customer-satisfaction`
- **Beantwortete Frage**: Welche Agenturen halten Kundenzufriedenheit trotz Probleme hoch?
- **Umsetzung**: Horizontal Bullet Chart mit Zielbereichen
- **Strategische Erkenntnis**: Identifikation von Best Practices im Kundenbeziehungsmanagement

### 5.4 Gesamtperformance und strategische Bewertung

**Konfigurierbare Gesamtrangliste**
- **Datenquelle**: Aggregiert aus mehreren Endpoints
- **Beantwortete Frage**: Welche Agenturen performen insgesamt am besten?
- **Umsetzung**: Interaktive Tabelle mit Mikro-Sparklines und konfigurierbaren Gewichtungen
- **Interaktivität**: Drag-and-Drop-UI für Gewichtungsanpassung

**Stärken-Schwächen-Vergleich ausgewählter Agenturen**
- **Datenquelle**: `/api/llm_analysis/{agency_id}/strength-weakness` für mehrere Agenturen
- **Beantwortete Frage**: Wo liegen komparative Vor- und Nachteile spezifischer Agenturen?
- **Umsetzung**: Side-by-Side-Vergleich mit visueller Hervorhebung der Differenzen
- **Strategische Erkenntnis**: Möglichkeiten für Best-Practice-Transfer identifizieren

## 6. Strategische Erkenntnisse durch integrierte Analyse

Die Kombination verschiedener Metriken und Visualisierungen ermöglicht tiefgreifende strategische Erkenntnisse:

1. **Qualität vs. Volumen**
   - Korrelation zwischen Agenturgrößen und Qualitätsmetriken visualisieren
   - Beantwortete Frage: Gibt es einen "Sweet Spot" für optimale Agenturgrößen?

2. **Spezialisierungsmuster**
   - Erkennung von Agenturen mit außergewöhnlichen Leistungen in bestimmten Kategorien
   - Beantwortete Frage: Welche Agenturen haben besondere Stärken in spezifischen Bereichen?

3. **Systematische Schwachstellen**
   - Identifikation von Problemmustern, die über mehrere Agenturen hinweg bestehen
   - Beantwortete Frage: Welche Probleme sind systemischer Natur vs. agenturspezifisch?

4. **Best Practice Transfer**
   - Agentur-übergreifende Lernmöglichkeiten basierend auf Leistungsunterschieden
   - Beantwortete Frage: Welche erfolgreichen Prozesse könnten auf andere Agenturen übertragen werden?

5. **Frühwarnindikatoren**
   - Korrelationen zwischen frühen Warnsignalen und späteren Problemen
   - Beantwortete Frage: Welche Frühindikatoren sagen zukünftige Probleme voraus?

## 7. Nächste konkrete Umsetzungsschritte

1. [ ] **Erweiterte Datenintegration**
   - [ ] Implementierung eines kombinierten API-Abrufs für konsistente Agenturlisten
   - [ ] Entwicklung eines Datenstruktur-Mappers für die Vereinheitlichung von Agenturvergleichsdaten
   - [ ] Caching-Mechanismen für schnellere Darstellung und reduzierte API-Last

2. [ ] **Core Visualisierungskomponenten**
   - [ ] Erstellung einer responsiven `AgencyHeatmap`-Komponente
   - [ ] Entwicklung einer interaktiven `MarketShareTreemap`-Komponente
   - [ ] Implementierung einer konfigurierbaren `PerformanceRadarChart`-Komponente
   - [ ] Entwicklung eines wiederverwendbaren `SideBySideComparison`-Layouts

3. [ ] **UI-Elemente für Benutzerinteraktion**
   - [ ] Gewichtungs-Konfigurator für die Gesamtbewertung
   - [ ] Filter- und Auswahl-UI für gezielte Agenturvergleiche
   - [ ] Speichern und Laden von Benutzereinstellungen

4. [ ] **Integration in bestehende App-Struktur**
   - [ ] Erweiterung des App-States für Vergleichsmetriken und -einstellungen
   - [ ] Entwicklung einer Tab-Struktur für die verschiedenen Vergleichsaspekte
   - [ ] Export-Funktionalität für Berichte und Rohdaten

5. [ ] **Performance-Optimierungen**
   - [ ] Lazy Loading für komplexe Visualisierungen
   - [ ] Responsive Anpassung der Diagrammkomplexität
   - [ ] Daten-Pagination für umfangreiche Vergleichslisten