# Garmin – Local Personal AI Assistant (Scaffold)

This repository contains the initial scaffolding for the Garmin project per Task 001.

## Backend (FastAPI + Poetry)

- Python 3.11+
- Commands:
  - Install deps: `poetry install`
  - Run tests: `poetry run pytest`
  - Run server: `poetry run uvicorn app.main:app --reload`

## Frontend (Tauri + React + Tailwind)

- Node.js 20+
- Commands:
  - Install deps: `cd frontend && npm install`
  - Run tests: `npm run test`
  - Dev server: `npm run dev`

## CI

GitHub Actions run backend and frontend tests on each push/PR to `main`.

## Notes

- `/health` endpoint returns `{ "status": "ok" }`.
- `App` renders a "Chat placeholder" heading.

