# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build Commands
- Backend: `cd backend && python -m uvicorn app.main:app --reload`
- Frontend: `cd frontend && npm start`
- Frontend (simple mode): `cd frontend && npm run start-simple`
- Docker: `docker-compose up -d`
- Tests: `cd backend && pytest tests/test_api.py -v`

## Lint/Format Commands
- Frontend: `cd frontend && npm run build` (includes type checking)
- TypeScript check: `cd frontend && tsc --noEmit`

## Architecture Overview
- **Frontend**: React/TypeScript SPA with Zustand state management and TailwindCSS
- **Backend**: FastAPI server with SQLAlchemy ORM and async database operations
- **Data Sources**: Google BigQuery for analytics data + SQLite for persistent caching
- **Caching Layer**: Database-backed cache service with preload capabilities and freshness tracking
- **Deployment**: Docker containerization with nginx reverse proxy

## Key Components
- **Routes**: API endpoints in `backend/app/routes/` (agencies, quotas, cache, etc.)
- **Queries**: BigQuery operations in `backend/app/queries/` organized by feature
- **Models**: Pydantic models in `backend/app/models/` for API contracts and database schemas
- **Cache Service**: `backend/app/services/database_cache_service.py` for persistent caching
- **Database Manager**: `backend/app/utils/database_connection.py` for SQLite connection management
- **Store**: Zustand state management in `frontend/src/store/appStore.ts`

## Database Architecture
- **Primary Data**: BigQuery tables for agency performance metrics
- **Cache Storage**: SQLite database (`backend/database/agency_cache.db`) with:
  - `cached_data`: API response cache with expiry and metadata
  - `preload_sessions`: Tracking for data preloading operations
  - `data_freshness`: Freshness rules and staleness detection

## Environment Requirements
- Google BigQuery credentials (`credentials.json` in project root)
- Environment variables (in `.env` or `docker-compose.yml`):
  - `GOOGLE_APPLICATION_CREDENTIALS`: Path to credentials
  - `BIGQUERY_PROJECT_ID`: Google Cloud project ID (gcpxbixpflegehilfesenioren)
  - `BIGQUERY_DATASET`: BigQuery dataset (AgencyReporter)
  - `OPENAI_API_KEY`: Optional for LLM analysis
  - `OPENAI_MODEL`: Optional model selection (gpt-4o)

## Code Style Guidelines
- Backend: Python with FastAPI, follow PEP 8 conventions
- Frontend: TypeScript/React with TailwindCSS
- Use named exports for React components
- Components should be in PascalCase (e.g., TimeFilter.tsx)
- Utility functions should be in camelCase
- Use TypeScript interfaces for props and state
- State management with Zustand
- Data visualization with Recharts and ECharts
- Async operations with axios
- Database operations use SQLAlchemy async patterns

## Development Notes
- okay ich habe jetzt die website betreten und NOCH NICHT auf den Button Alle Agenturen laden gedrückt. Schau die jetzt kurz die DB an um dannach einen direkten vergliech zu haben