# CV-Qualitätsbewertung - Konzept

## Kernidee
Messung der Diskrepanz zwischen den Angaben in Betreuungskraft-CVs und der tatsächlich wahrgenommenen Realität beim Kunden.

## Ziel
Identifikation von Agenturen, die ungenaue oder falsche Angaben in CVs ihrer Betreuungskräfte machen, was zu Enttäuschungen und Kündigungen führt.

## Methodologie

### 1. Datenquellen
- **Erwartungshaltung**: CV-Angaben der Betreuungskräfte
- **Wahrgenommene Realität**: 
  - Emails von Kunden
  - Interne Support-Tickets
  - Kundenkommunikation

### 2. Bewertungskategorien
- **Sprachkenntnisse** (primär Deutsch)
- **Berufserfahrung** (Jahre + erwartete Fähigkeiten)
- **Harte Eigenschaften**:
  - Führerschein (ja/nein)
  - Raucherstatus
  - Alter
  - Weitere verifizierbare Angaben

### 3. Bewertungssystem

#### Erfüllungsbemessung
- **Ausgangswert**: 5/5 oder "true" (Benefit of the doubt)
- **Anpassung**: Basierend auf KI-Analyse der Kundenkommunikation
- **Skala**: 
  - Boolean (true/false) für binäre Eigenschaften
  - 1-5 Skala für graduelle Eigenschaften

#### Prozess
1. CV-Daten extrahieren und kategorisieren
2. Speicherung in lokaler DB oder Supabase
3. Kundenkommunikation sammeln (Emails + Tickets)
4. KI-Analyse auf Enttäuschungen/Beschwerden
5. Validierung unrealistischer Kundenerwartungen
6. Anpassung der Erfüllungsbemessung

### 4. KI-Analyse

#### Zu erkennende Muster
- Explizite Beschwerden über Diskrepanzen
- Enttäuschungsäußerungen
- Kündigungsgründe im Zusammenhang mit CV-Angaben
- Indirekte Hinweise auf Unstimmigkeiten

#### Prompt-Strategie
- Strukturierte Abfrage nach Kategorien
- Sentiment-Analyse für Enttäuschungsgrad
- Kontextuelle Validierung der Kundenerwartungen

### 5. Aggregation und Reporting

#### Metriken pro Agentur
- Durchschnittliche Erfüllungsquote pro Kategorie
- Anzahl problematischer CV-Angaben
- Trend über Zeit
- Vergleich zum Branchendurchschnitt

#### Visualisierung
- Heatmap: Agentur vs. Problemkategorie
- Ranking: Agenturen nach CV-Qualität
- Detailansicht: Einzelne Problemfälle
- Zeitverlauf: Verbesserung/Verschlechterung

## Erwarteter Nutzen
1. Transparenz über CV-Qualität verschiedener Agenturen
2. Früherkennung systematischer Falschdarstellungen
3. Reduktion von Kundenunzufriedenheit
4. Basis für Qualitätsverbesserungen bei Agenturen
5. Objektive Grundlage für Agentur-Feedback

## Technische Überlegungen
- Integration in bestehende Agency Reporter Architektur
- Erweiterung der BigQuery-Schemas
- Neue API-Endpoints für CV-Qualitätsdaten
- Frontend-Komponenten für neue Auswertungsseite
- Datenschutz bei Email/Ticket-Verarbeitung