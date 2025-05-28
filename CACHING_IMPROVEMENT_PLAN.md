# Caching-System Verbesserungsplan

## Übersicht
Schrittweise Implementierung eines einheitlichen und effizienten Caching-Systems für alle API-Endpoints.

## Phase 1: Grundlagen schaffen

### 1.1 Cache-Decorator implementieren
- Erstelle einen wiederverwendbaren `@cache_endpoint` Decorator
- Parameter: TTL, Cache-Key-Strategie, Preload-Unterstützung
- Einheitliches Logging für Cache-Hit/Miss
- Automatische Fehlerbehandlung

### 1.2 Logging-System vereinheitlichen
- Standardisierte Log-Messages für alle Cache-Operationen
- Performance-Metriken (Response-Zeit, Cache-Hit-Rate)
- Strukturierte Logs für bessere Auswertbarkeit

### 1.3 Cache-Key-Generator optimieren
- Konsistente Key-Generierung für alle Endpoints
- Berücksichtigung aller relevanten Parameter
- Vermeidung von Key-Kollisionen

## Phase 2: Endpoints migrieren

### 2.1 Quotas-Endpoints cachen
- `/api/quotas/postings`
- `/api/quotas/{agency_id}/reservations`
- `/api/quotas/{agency_id}/fulfillment`
- `/api/quotas/{agency_id}/completion`
- TTL: 24 Stunden (da sich Quoten täglich ändern können)

### 2.2 Reaction-Times-Endpoints verbessern
- Explizite Cache-Hit/Miss Logs hinzufügen
- `/api/reaction_times/{agency_id}`
- `/api/reaction_times/overview`
- `/api/reaction_times/comparison`
- TTL: 48 Stunden

### 2.3 Profile-Quality-Endpoints cachen
- `/api/profile_quality/{agency_id}`
- `/api/profile_quality/overview`
- TTL: 48 Stunden

### 2.4 Problematic-Stays-Endpoints optimieren
- Cache-Logging verbessern
- Alle Unterendpoints erfassen
- TTL: 24 Stunden (aktuelle Daten wichtig)

## Phase 3: Dashboard-Optimierung

### 3.1 Dashboard-Summary-Endpoint erstellen
- Neuer Endpoint: `/api/dashboard/summary`
- Aggregiert Daten von mehreren Endpoints
- Optimiert für schnelles Laden der Startseite
- TTL: 12 Stunden

### 3.2 Batch-Cache-Warming implementieren
- Endpoint zum Vorladen häufig genutzter Daten
- `/api/cache/warm-up`
- Intelligente Priorisierung basierend auf Nutzungsmuster

### 3.3 Cache-Preloading für Agenturen
- Automatisches Vorladen beim Start
- Top 10 Agenturen basierend auf Aktivität
- Hintergrund-Job für regelmäßige Updates

## Phase 4: Monitoring & Wartung

### 4.1 Cache-Statistics-Endpoint erweitern
- Hit-Rate pro Endpoint
- Durchschnittliche Response-Zeiten
- Cache-Größe und Speichernutzung
- Top-gecachte Queries

### 4.2 Cache-Invalidierung verbessern
- Selective Invalidierung nach Datenänderungen
- Webhook-Support für externe Trigger
- Admin-Interface für manuelles Cache-Clearing

### 4.3 Performance-Dashboard
- Visualisierung der Cache-Performance
- Kosten-Nutzen-Analyse (BigQuery-Kosten vs. Cache-Hits)
- Alerts bei niedrigen Hit-Rates

## Phase 5: Advanced Features

### 5.1 Intelligentes Cache-Warming
- ML-basierte Vorhersage häufig angefragter Daten
- Zeitbasiertes Preloading (z.B. vor Geschäftszeiten)
- Adaptive TTL basierend auf Datenänderungsrate

### 5.2 Multi-Level-Caching
- In-Memory-Cache für ultra-schnelle Responses
- Redis als verteilter Cache (für Skalierung)
- SQLite als persistenter Fallback

### 5.3 Cache-Partitionierung
- Separate Caches für verschiedene Datentypen
- Optimierte Storage-Strategien pro Datenart
- Bessere Cache-Eviction-Policies

## Implementierungsreihenfolge

1. **Sofort (Quick Wins)**
   - 1.1 Cache-Decorator
   - 2.1 Quotas-Endpoints cachen
   - 1.2 Logging vereinheitlichen

2. **Kurzfristig (1-2 Tage)**
   - 2.2-2.4 Alle Endpoints migrieren
   - 3.1 Dashboard-Summary-Endpoint
   - 4.1 Cache-Statistics erweitern

3. **Mittelfristig (1 Woche)**
   - 3.2-3.3 Cache-Warming
   - 4.2-4.3 Monitoring verbessern

4. **Langfristig (Optional)**
   - 5.1-5.3 Advanced Features

## Erfolgskriterien

- ✓ 95%+ Cache-Hit-Rate für häufige Queries
- ✓ 80% Reduktion der BigQuery-Kosten
- ✓ < 100ms Response-Zeit für gecachte Daten
- ✓ Einheitliches Logging über alle Endpoints
- ✓ Automatisches Cache-Warming für Top-Agenturen

## Technische Details

### Cache-Decorator Beispiel
```python
@cache_endpoint(
    ttl_hours=24,
    key_params=['agency_id', 'time_period'],
    preloadable=True
)
async def get_quotas_data(agency_id: str, time_period: str):
    # Implementation
```

### Logging-Format
```
INFO: [CACHE] Endpoint: /api/quotas/{agency_id} | Status: HIT | Response Time: 45ms
INFO: [CACHE] Endpoint: /api/quotas/{agency_id} | Status: MISS | BigQuery Time: 850ms | Cached for: 24h
```