## Daten- und Analyse-Anforderungen für das Agentur-Dashboard

Diese Liste beschreibt **alle Datenpunkte und KPIs**, die im Web-Dashboard verarbeitet und visualisiert werden sollen. Sie ist **Teil der Gesamtanforderung** und muss von der KI bei der Umsetzung berücksichtigt werden.

---

### 0. TECHNISCHE IMPLEMENTIERUNGSDETAILS

| Aspekt                  | Spezifikation                                                            |
|-------------------------|--------------------------------------------------------------------------|
| Datenquellen            | - 20 SQL-Queries (werden separat bereitgestellt)                         |
|                         | - Tickets aus BigQuery                                                   |
|                         | - E-Mails über Google API (müssen mit den Einzelfällen verknüpft werden) |
| LLM-Integration         | Externe LLM-API für Analyse der Kommunikationsdaten                      |
| Fallbasis               | 28 identifizierte Problemfälle für die Ursachenanalyse                   |

---

### 1. PROFILQUALITÄT DER BETREUUNGSKRÄFTE

Ziel: Vergleich zwischen **Profilangaben** und **realer Wahrnehmung** anhand Kommunikation (E-Mail/Tickets). Negative Abweichungen gelten als **Regelverstöße**, die von einem LLM identifiziert werden sollen.

| Merkmal               | Typ             | Vergleich / Logik                                        |
|-----------------------|------------------|----------------------------------------------------------|
| Erfahrung              | Integer/String   | Jahre laut Profil vs. Eindruck vor Ort                   |
| Deutschkenntnisse     | Schulnote (1–6)  | Angabe vs. reale Kommunikation                          |
| Raucher               | Boolean          | Profilangabe vs. Beobachtung vor Ort                     |
| Alter                 | Integer          | Alter laut Profil vs. tatsächliches Alter               |
| Führerschein          | Boolean          | Hat laut Profil einen Führerschein – wurde bestätigt?    |

**Verarbeitung durch LLM:**
- Scannt E-Mails (via Google API) & Tickets (aus BigQuery) auf Abweichungen
- Prüft, ob ein Regelverstoß bestätigt wurde
- Für jeden Regelverstoß wird ein Zähler um 1 erhöht ("rule-violence" Counter)
- Erstellt für jeden Punkt eine Regelverstoß-Statistik pro Agentur

---

### 2. REAKTIONSZEITEN

Ziel: Messung der Reaktionsgeschwindigkeit in verschiedenen Prozessschritten. Je schneller, desto besser.

| Reaktionszeit-Messung                              | Beschreibung                                                              |
|----------------------------------------------------|---------------------------------------------------------------------------|
| Ausschreibung → Reservierung                     | Zeit zwischen Stellenerstellung und Agenturreaktion                       |
| Reservierung → Personalvorschlag                 | Zeit zwischen Buchung und Nennung einer geeigneten Kraft                  |
| Personalvorschlag → Abbruch (falls vorhanden)    | Zeit zwischen Vorschlag und Abbruch (z. B. durch Agentur)                |
| Abbruch → geplanter Anreisetermin                | Zeitspanne zwischen Absage und geplantem Einsatz                         |
| Zeit bis generelle Abbrüche / Rückzüge             | Durchschnittliche Zeit bis Reservierungen abgebrochen oder zurückgezogen wurden |

**Implementierung:** 
- 7 spezifische Reaktionszeiten werden durch Subtraktion von Zeitstempeln berechnet
- Daten werden durch SQL-Abfragen gewonnen

---

### 3. QUOTEN (KPIs)

Ziel: Statistische Erfolgskennzahlen, die den Vermittlungsprozess und seine Qualität abbilden.

| KPI-Bezeichnung                                                        | Beschreibung                                                   |
|------------------------------------------------------------------------|---------------------------------------------------------------|
| Gesehene Stellen / reservierte Stellen                                 | Sichtbarkeit vs. Engagement                                   |
| Reservierte Stellen / erfüllte Stellen (mit Personalvorschlag)         | Effizienz bei der Umsetzung                                   |
| Reservierte Stellen / abgebrochene durch Agentur                       | Abbruchquote auf Agenturseite                                 |
| Reservierte Stellen ohne Ergebnis                                      | Weder erfüllt noch gecancelt – offene Vorgänge                |
| Erfüllte Personalvorschläge / Pflegeeinsätze angetreten                | Erfolgsquote ab Vorschlag bis Umsetzung                       |
| Personalvorschläge bestätigt / abgebrochene Vorschläge               | Erfolgsquote bei konkreter Auswahl                            |
| Pflegeeinsatz angetreten / vorzeitig beendet                           | Quote vorzeitiger Abbrüche während des Einsatzes              |
| Pflegeeinsatz angetreten / vollständig zu Ende gebracht                | Abschlussquote erfolgreicher Pflegeeinsätze                   |

**Implementierung:**
- Jede Quote besteht typischerweise aus 2 SQL-Abfragen, die miteinander verglichen werden
- Beispielinterpretation: "Agentur XYZ hat erfolgreich 72/100 (72%) ihrer versprochenen 'Personalvorschläge' zum Kunden gebracht"

---

### 4. LLM-GESTÜTZTE URSACHENANALYSE

Ziel: Automatische Ursachenanalyse bei **Abbrüchen von Vorschlägen und Einsätzen** durch ein LLM.

#### 4.1 Gründe für Abbruch von **Personalvorschlägen**
- Kommunikation wird analysiert (E-Mails via Google API, Tickets aus BigQuery)
- Analyse konzentriert sich auf die 28 identifizierten Problemfälle
- SQL-Abfrage liefert diese Fälle, bei denen die Agentur gescheitert ist
- Jeder Fall wird über die LLM-API analysiert
- Jeder Vorfall wird durch das LLM **einem von ca. 20 vordefinierten Gründen** zugeordnet
- Der jeweilige Zähler für den identifizierten Grund wird um 1 erhöht
- Häufigkeiten der Gründe werden gezählt und visualisiert
- Dieses Vorgehen erstellt einen Datensatz, der die Gründe und Häufigkeit von Fehlern erfasst

#### 4.2 Gründe für Abbruch von **Pflegeeinsätzen nach Antritt**
- Gleiches Vorgehen wie bei Vorschlägen
- Ziel: Ursachen für vorzeitige Einsatzabbrüche ermitteln

**Beispielhafte Gründe (müssen definiert werden):**
- Betreuungskraft erkrankt
- Kunde nicht zufrieden
- Persönliche Gründe der Kraft
- Unklare Kommunikation
- … usw. (Liste auf etwa 20 Kategorien erweitern)

---

### 5. VISUALISIERUNGEN

Alle oben genannten Datenpunkte sollen visuell im Dashboard dargestellt werden – aufgeschlüsselt **pro Agentur** mit Vergleichsmöglichkeiten (Benchmarking). Beispiele:

- Scatterplots mit farblicher Hervorhebung der ausgewählten Agentur
- Balken-/Säulendiagramme für Top/Flop-Werte
- Heatmaps bei Häufung von Regelverstößen
- Liniendiagramme für Reaktionszeiten im Zeitverlauf
- Tabellen für Ranking und Vergleich
- Stärken-/Schwächenübersicht mit automatischer Markierung

---

### 6. DATENTYPEN (Standardisierung)

| Datenfeld                | Typ       | Beschreibung                                       |
|--------------------------|-----------|----------------------------------------------------|
| Agenturname              | String    | Eindeutige ID oder Name der Agentur               |
| Zeitraum                 | DateRange | Typischerweise Quartal                             |
| KPI-Wert                 | Float     | Prozentualer oder numerischer Wert                |
| Regelverstoß             | Boolean   | „True" = bestätigter Verstoß                      |
| Reaktionszeit            | Integer   | In Stunden oder Tagen                             |
| Grund (LLM)              | Enum      | Einer von vordefinierten ca. 20 Gründen            |

---

Diese Datei ist verbindlicher Bestandteil der Projektspezifikation und wird für die Entwicklung aller Komponenten verwendet.

