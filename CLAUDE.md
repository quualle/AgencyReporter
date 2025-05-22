# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build Commands
- Backend: `cd backend && python -m uvicorn app.main:app --reload`
- Frontend: `cd frontend && npm start`
- Docker: `docker-compose up -d`
- Tests: `cd backend && pytest tests/test_api.py -v`

## Lint/Format Commands
- Frontend: `cd frontend && npm run build` (includes type checking)
- TypeScript check: `cd frontend && tsc --noEmit`

## Project Structure
- Frontend: React/TypeScript app for agency performance dashboard
- Backend: FastAPI server with BigQuery integration
- Docker: Configuration for containerized deployment
- Main features: Agency reporting, quotas analysis, problematic stays tracking

## Environment Requirements
- Google BigQuery credentials (`credentials.json` in project root)
- Environment variables (in `.env` or `docker-compose.yml`):
  - `GOOGLE_APPLICATION_CREDENTIALS`: Path to credentials
  - `BIGQUERY_PROJECT_ID`: Google Cloud project ID
  - `BIGQUERY_DATASET`: BigQuery dataset
  - `OPENAI_API_KEY`: Optional for LLM analysis
  - `OPENAI_MODEL`: Optional model selection

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
- Use lazy loading for performance optimization