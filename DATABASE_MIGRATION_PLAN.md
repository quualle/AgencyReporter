# Database Migration Plan: From In-Memory Cache to Persistent Storage

## Übersicht
Migration von dem aktuellen In-Memory-Cache-System zu einer persistenten SQLite-Datenbank für bessere Datenbeständigkeit und Performance.

## Aktuelle Situation
- ✅ Frontend-Cache funktioniert perfekt
- ✅ Preload-System lädt alle relevanten Daten 
- ✅ Instantane Navigation zwischen Seiten
- ❌ Daten gehen bei Server-Restart verloren
- ❌ Keine persistente Speicherung über Sessions hinweg

## Ziele der Migration
1. **Persistente Speicherung**: Daten bleiben über Server-Restarts hinweg erhalten
2. **Datenfrische-Prüfung**: Intelligente Erkennung, ob Daten bereits aktuell sind
3. **Duplicate Prevention**: Vermeidung redundanter BigQuery-Aufrufe
4. **Performance**: Schnellere Ladezeiten durch persistente Speicherung
5. **Fallback**: Robustes System mit Cache als Fallback bei DB-Problemen

## Technische Architektur

### Database Choice: SQLite
- **Warum SQLite?**
  - Keine zusätzliche Server-Installation nötig
  - Eingebettet in Python
  - Perfekt für lokale Entwicklung
  - Einfache Migration zu PostgreSQL später möglich
  - Unterstützt JSON-Spalten für flexible Datenstrukturen

### Database Schema

```sql
-- Tabelle für gecachte API-Responses
CREATE TABLE cached_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cache_key VARCHAR(500) UNIQUE NOT NULL,
    endpoint VARCHAR(200) NOT NULL,
    agency_id VARCHAR(100),
    time_period VARCHAR(50),
    parameters TEXT, -- JSON string für zusätzliche Parameter
    data TEXT NOT NULL, -- JSON string der API Response
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    is_preloaded BOOLEAN DEFAULT FALSE,
    data_hash VARCHAR(64), -- SHA256 hash für Datenintegrität
    INDEX idx_cache_key (cache_key),
    INDEX idx_agency_period (agency_id, time_period),
    INDEX idx_endpoint (endpoint),
    INDEX idx_expires (expires_at)
);

-- Tabelle für Preload-Sessions
CREATE TABLE preload_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agency_id VARCHAR(100) NOT NULL,
    session_key VARCHAR(200) UNIQUE NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    total_requests INTEGER,
    successful_requests INTEGER,
    failed_requests INTEGER,
    status VARCHAR(50) DEFAULT 'running', -- running, completed, failed
    INDEX idx_agency_session (agency_id, session_key)
);

-- Tabelle für Data Freshness Tracking
CREATE TABLE data_freshness (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data_type VARCHAR(100) NOT NULL,
    agency_id VARCHAR(100),
    time_period VARCHAR(50),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_query_executed_at TIMESTAMP,
    is_fresh BOOLEAN DEFAULT TRUE,
    freshness_duration_hours INTEGER DEFAULT 24,
    UNIQUE(data_type, agency_id, time_period)
);
```

## Implementation Plan

### Phase 1: Database Setup & Models
1. **SQLite Setup**
   - SQLAlchemy integration
   - Database models (Pydantic + SQLAlchemy)
   - Connection management
   - Migration scripts

2. **Database Models**
   ```python
   # backend/app/models/database.py
   class CachedData(Base):
       __tablename__ = "cached_data"
       
   class PreloadSession(Base):
       __tablename__ = "preload_sessions"
       
   class DataFreshness(Base):
       __tablename__ = "data_freshness"
   ```

### Phase 2: Database Service Layer
```python
# backend/app/services/database_service.py
class DatabaseCacheService:
    async def get_cached_data(cache_key: str)
    async def save_cached_data(cache_key: str, data: dict, expires_hours: int)
    async def is_data_fresh(data_type: str, agency_id: str, time_period: str)
    async def create_preload_session(agency_id: str)
    async def complete_preload_session(session_key: str)
    async def cleanup_expired_data()
```

### Phase 3: Frontend Integration
1. **API Service Migration**
   - Update `cacheHelper` in `api.ts`
   - Database-backed cache checks
   - Fallback auf In-Memory-Cache bei DB-Problemen

2. **Preload Logic Update**
   - Datenfrische-Prüfung vor Preload
   - Session-Tracking
   - Progress-Updates über Database

### Phase 4: Data Freshness Logic
```python
# Beispiel Freshness-Check
def check_data_freshness(data_type: str, agency_id: str, time_period: str) -> bool:
    """
    Prüft ob Daten noch frisch sind basierend auf:
    - Datentyp (quotas: 24h, reaction_times: 12h, etc.)
    - Zeitraum (current_*: 1h, last_*: 24h, all_time: 7 days)
    - Letzte BigQuery-Ausführung
    """
    freshness_rules = {
        "quotas": {"last_quarter": 24, "last_year": 168, "all_time": 168},
        "reaction_times": {"last_quarter": 12, "last_year": 72},
        "problematic_stays": {"last_quarter": 24, "last_year": 168}
    }
    
    return is_within_freshness_window(data_type, time_period, freshness_rules)
```

## Migration Strategy

### Schritt 1: Parallelbetrieb
- Database-System parallel zum Cache implementieren
- Cache bleibt als Fallback aktiv
- Schrittweise Migration einzelner Endpoints

### Schritt 2: Database-First
- Database wird primäre Datenquelle
- Cache nur noch für Session-Daten
- Comprehensive Testing

### Schritt 3: Cache-Removal
- Entfernung des In-Memory-Cache
- Vollständiger Database-Betrieb
- Performance-Optimierungen

## Preload Button Logic (Neu)

### Aktuelles Verhalten
```typescript
// Lädt immer alle Daten neu
await preloadService.preloadAllData(selectedAgencyId, onProgress)
```

### Neues Verhalten
```typescript
// 1. Prüfe Data Freshness
const freshnessCheck = await api.get(`/cache/freshness/${selectedAgencyId}`)

if (freshnessCheck.allDataFresh) {
    showMessage("Alle Daten sind bereits aktuell geladen!")
    return
}

// 2. Selective Preload nur für veraltete Daten
const staleDataTypes = freshnessCheck.staleDataTypes
await preloadService.preloadSelectedData(selectedAgencyId, staleDataTypes, onProgress)
```

## Benefits der Migration

### Performance
- ✅ Daten bleiben über Server-Restarts erhalten
- ✅ Keine redundanten BigQuery-Aufrufe
- ✅ Schnellere Entwicklungszyklen

### User Experience  
- ✅ Intelligenter Preload (nur was nötig ist)
- ✅ Datenfrische-Feedback
- ✅ Konsistente Performance

### Development
- ✅ Bessere Debugging-Möglichkeiten
- ✅ Datenhistorie und Analytics möglich
- ✅ Einfache Backup/Restore-Prozesse

## Risiken & Mitigation

### Risiko 1: Database Corruption
**Mitigation**: Regelmäßige Backups + SQLite Integrity Checks

### Risiko 2: Performance-Degradation
**Mitigation**: Proper Indexing + Connection Pooling

### Risiko 3: Migration-Fehler
**Mitigation**: Schrittweise Migration + Comprehensive Testing + Git Fallback

## Timeline

### Week 1: Infrastructure
- [ ] SQLite setup
- [ ] Database models
- [ ] Basic CRUD operations

### Week 2: Integration
- [ ] Database service layer
- [ ] API integration
- [ ] Freshness logic

### Week 3: Frontend
- [ ] Frontend cache migration
- [ ] Preload logic update
- [ ] User feedback

### Week 4: Testing & Optimization
- [ ] Performance testing
- [ ] Edge case handling
- [ ] Documentation

## Files to Modify

### Backend
- `backend/requirements.txt` - SQLAlchemy, Alembic
- `backend/app/models/database.py` - Neue Models
- `backend/app/services/database_service.py` - Database Service
- `backend/app/utils/database_connection.py` - Connection Management
- `backend/app/routes/cache.py` - Cache Management Endpoints

### Frontend
- `frontend/src/services/api.ts` - Database-backed caching
- `frontend/src/components/layout/Sidebar.tsx` - Preload button logic
- `frontend/package.json` - Eventuell neue Dependencies

### Infrastructure
- `database/` - Neuer Ordner für DB Files
- `database/migrations/` - Alembic Migrations
- `database/agency_cache.db` - SQLite Database File

## Success Criteria

1. ✅ Alle bisherigen Cache-Features funktionieren identisch
2. ✅ Daten bleiben über Server-Restarts hinweg verfügbar
3. ✅ Preload-Button zeigt intelligente Meldungen
4. ✅ Keine Performance-Verschlechterung
5. ✅ Umfassende Tests bestanden
6. ✅ Fallback-System funktioniert bei DB-Problemen

---

**Git Fallback**: `796db61` - "Caching fertiggestellt - fallback point"