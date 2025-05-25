# Dashboard Design Plan - Agenturvergleich

## Projektziel
Redesign der Dashboard-Seite von einer einzelagentur-fokussierten Ansicht zu einer vergleichenden Übersicht aller Agenturen. Ziel: Nutzer sollen schnell erkennen, welche Agenturen in welchen Bereichen schlecht abschneiden.

## Prioritätsbewertung der KPIs (Skala 1-10)

### Quoten & Performance
- **Abbruchrate**: 8 (kritisch)
- **Startrate**: 8 (kritisch) - *Kehrbruch der Abbruchrate*
- **Abschlussrate**: 8 (kritisch)
- **Erfüllungsrate**: 4 (ergänzend)
- **Reservierungsrate**: 3 (ergänzend)
- *Gesamte Ausschreibungen*: Kein Vergleichswert, wird ausgeblendet

### Reaktionszeiten
- **Ankunft bis Abbruch**: 7 (wichtig)
- **Reservierung bis Personalvorschlag**: 4 (ergänzend)
- **Ausschreibung bis Reservierung**: 2 (niedrig, ausgeblendet)

### Profilqualität
- *Wird übersprungen* - keine Daten verfügbar

### Problematische Einsätze
- **Gesamtanzahl problematischer Einsätze**: 9 (höchste Priorität)
- **Instant Departures (Sofortabgänge)**: 6 (wichtig)
- **Kundenzufriedenheitswerte**: 3 (ergänzend)
- *Abbruchgründe-Verteilung*: 5, aber zu breit für Dashboard

## Finales Dashboard-Design: 8 Widgets Maximum

### Designprinzip: "Weniger ist mehr"
- Maximal 8 Widgets auf der Hauptansicht
- Fokus auf Priorität 6-10 KPIs
- Expandierbare/klappbare Details
- Scrollbare Listen für vollständige Daten

### Widget-Layout

#### **Top Section (2 Widgets)**

**1. 🚨 PROBLEMATISCHE EINSÄTZE (Priorität 9)**
```
┌─────────────────────────────────────────────┐
│ Top 5 Worst ⚡ 8.7% ⚡ 12.1% ⚡ 15.3% ⚡... │
│ [Alle anzeigen ▼] - Expandiert zu Volliste │
└─────────────────────────────────────────────┘
```

**2. ⚖️ CONVERSION PERFORMANCE (Priorität 8)**
```
┌─────────────────────────────────────────────┐
│ Abbruch vs. Start - Top 5 Performer        │
│ Donut Charts mini + [Details ▼]            │
└─────────────────────────────────────────────┘
```

#### **Middle Section (4 Widgets)**

**3. ✅ ABSCHLUSSRATE (Priorität 8)**
```
┌─────────────────────────────────────────────┐
│ Completion Rate Ranking                     │
│ Horizontal Bar Chart - Top/Flop 10         │
└─────────────────────────────────────────────┘
```

**4. ⏱️ ANKUNFT BIS ABBRUCH (Priorität 7)**
```
┌─────────────────────────────────────────────┐
│ Durchschnittliche Tage - Heatmap           │
│ [Zeitverteilung ▼] - Expandiert zu Details │
└─────────────────────────────────────────────┘
```

**5. 🏃 INSTANT DEPARTURES (Priorität 6)**
```
┌─────────────────────────────────────────────┐
│ Sofortabgänge % - Bubble Chart             │
│ X=Gesamtprobleme, Y=Instant%               │
└─────────────────────────────────────────────┘
```

**6. 📊 PERFORMANCE OVERVIEW**
```
┌─────────────────────────────────────────────┐
│ Mini-Scorecard der Top/Flop 10             │
│ Kompakte Tabelle mit allen 6-10 KPIs       │
└─────────────────────────────────────────────┘
```

#### **Bottom Section (2 Widgets)**

**7. 🔄 QUICK FILTERS**
```
┌─────────────────────────────────────────────┐
│ [Zeitraum] [Region] [Mindestvolumen]       │
│ [Reset] [Alle Daten laden]                 │
└─────────────────────────────────────────────┘
```

**8. 📈 TREND INDICATOR**
```
┌─────────────────────────────────────────────┐
│ Verschlechterungen/Verbesserungen           │
│ Sparklines für kritische KPIs              │
└─────────────────────────────────────────────┘
```

## KPI-Logik & Vermeidung von Redundanz

### Performance Trinity - Logisch getrennte Bereiche:

**1. CONVERSION PERFORMANCE**
- "Ausschreibung → Start"
- Kombiniert: Abbruchrate vs. Startrate (sind Kehrbrüche)
- Visualisierung: Donut Chart oder kombinierter Balken

**2. COMPLETION PERFORMANCE**
- "Start → Abschluss" 
- Abschlussrate vs. vorzeitige Beendigung
- Zeigt Zuverlässigkeit gestarteter Einsätze

**3. PROBLEM DENSITY**
- Gesamtproblemrate als übergeordneter Indikator
- Höchste Priorität (9)

## Interaktivitätskonzept

- **[▼]** = Expandiert zu Vollansicht mit allen Agenturen
- **Hover** = Tooltips mit exakten Werten
- **Click** = Navigation zu Detail-Seite der Agentur
- **Scroll-Listen** in expandierten Widgets
- **Caching** für alle API-Calls wie auf anderen Seiten

## Technische Umsetzung

### Reihenfolge der Implementierung:
1. **Start**: Widget 1 - Problematische Einsätze (Priorität 9)
2. Widget 2 - Conversion Performance
3. Widgets 3-6 - Middle Section
4. Widgets 7-8 - Bottom Section

### Caching-Integration:
- Alle Dashboard-API-Calls in bestehende Cache-Architektur einbinden
- Cache-Keys für Agentur-übergreifende Daten definieren
- Preload-Funktionalität für Dashboard-Daten

## Status
- ✅ Planung abgeschlossen
- ⏳ Implementierung: Beginnt mit Widget 1 (Problematische Einsätze)
- ⏳ Noch zu implementieren: Widgets 2-8

---

*Letzte Aktualisierung: [Datum der Git-Commit]*