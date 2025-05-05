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