# Agency Reporter

Ein datenbasiertes Analyse-Dashboard für die Bewertung und den Vergleich von Partneragenturen.

## Übersicht

Dieses System bietet ein umfassendes Dashboard zur Analyse und zum Vergleich von 45 Partneragenturen. Es wird quartalsweise vom Geschäftsführer genutzt, um in Gesprächen mit jeder einzelnen Agentur deren Leistungen zu analysieren, vergleichen und bewerten.

## Funktionen

- **Quoten-Analyse**: Vergleicht KPIs wie Erfolgsraten, Abbruchquoten und mehr.
- **Reaktionszeiten**: Misst und visualisiert die Reaktionsgeschwindigkeit in verschiedenen Prozessschritten.
- **Qualitätsanalyse**: Bewertet die Profilqualität der Betreuungskräfte und identifiziert mögliche Regelverstöße.
- **Stärken- und Schwächenanalyse**: Bietet eine automatische Identifikation von Stärken und Schwächen jeder Agentur.
- **Export-Funktionalität**: Ermöglicht den Export der Datenansicht als PDF.

## Technologie-Stack

- **Frontend**: React + TypeScript + TailwindCSS
- **Datenvisualisierung**: Recharts + ECharts
- **Backend/API**: FastAPI (Python)
- **Datenanbindung**: Google BigQuery
- **LLM-Modul**: OpenAI GPT via API

## Installation und Start

### Option 1: Lokale Entwicklung

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Unter Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend
npm install
npm start
```

### Option 2: Docker-Deployment

Das Projekt kann einfach mit Docker und Docker Compose gestartet werden:

1. Stellen Sie sicher, dass Docker und Docker Compose installiert sind
2. Legen Sie eine `credentials.json` für Google BigQuery im Hauptverzeichnis ab
3. Erstellen Sie eine `.env`-Datei mit Ihrem OpenAI API-Key:
   ```
   OPENAI_API_KEY=your-api-key-here
   ```
4. Starten Sie die Anwendung:
   ```bash
   docker-compose up -d
   ```
5. Das Frontend ist dann unter http://localhost verfügbar, das Backend unter http://localhost:8000

## Konfiguration

### Umgebungsvariablen

#### Backend (.env)

```
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/credentials.json
BIGQUERY_PROJECT_ID=your-project-id
BIGQUERY_DATASET=your-dataset-name
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4-turbo
```

#### Frontend (.env)

```
REACT_APP_API_URL=http://localhost:8000/api
```

## Projektstruktur

Die detaillierte Projektstruktur und der Entwicklungsprozess sind in der [PROJECT_PLAN.md](PROJECT_PLAN.md) dokumentiert.

### Frontend-Struktur

- `src/components/`: Wiederverwendbare UI-Komponenten
  - `common/`: Gemeinsame Komponenten wie Buttons, Modals, etc.
  - `layout/`: Layout-Komponenten wie Header und Sidebar
- `src/pages/`: Hauptseiten der Anwendung
- `src/services/`: API-Service für Backend-Kommunikation
- `src/store/`: Zustand-Management mit Zustand
- `src/styles/`: CSS und Styling
- `src/utils/`: Hilfsfunktionen und Utilities

### Backend-Struktur

- `app/`: Hauptanwendungscode
  - `routes/`: API-Endpunkte
  - `models.py`: Datenmodelle
  - `main.py`: Hauptanwendung
- `utils/`: Hilfsfunktionen
  - `bigquery_connection.py`: Verbindung zu BigQuery
  - `openai_integration.py`: Integration mit OpenAI

## BigQuery-Integration

Das System verwendet Google BigQuery für Datenabfragen. Sie benötigen einen Google Cloud-Account mit aktivierter BigQuery-API und entsprechenden Berechtigungen.

## LLM-Integration

Zur Ursachenanalyse bei Abbrüchen und zur Identifikation von Regelverstößen wird OpenAI GPT verwendet. Die Anwendung benötigt einen gültigen OpenAI API-Key.

## Testing

Das Projekt enthält automatisierte Tests für das Backend:

```bash
cd backend
pytest
```

## Leistungsoptimierung

Das Dashboard verwendet:
- Lazy Loading für Charts und Visualisierungen
- Memoization für teure Berechnungen
- Optimierte Bundle-Größe im Frontend
- Caching von API-Antworten

## Mitwirkende

Dieses Projekt wurde von einem autonomen KI-Entwicklungssystem erstellt.

## Lizenz

MIT 