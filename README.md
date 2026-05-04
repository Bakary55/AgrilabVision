# AgrilabVision

Intelligent mobile app for **soil analysis**, **crop and fertilizer recommendations**, and **weather / map** context for farmers. The stack is a **FastAPI** backend and an **Expo (React Native)** mobile client, with optional **Google Gemini** for AI soil insights and **Open-Meteo** or **OpenWeather** for weather data.

## Repository layout

| Path | Description |
|------|-------------|
| [`backend/`](backend/) | FastAPI application (`app.main`), SQLAlchemy models, auth (`/auth`), AI (`/ai`), integrations (`/weather/current`, `/insights/farming`). |
| [`frontend/mobile/`](frontend/mobile/) | Expo app: auth, home, soil analysis, map & weather, account. |
| [`documentation/`](documentation/) | Project docs: setup notes, SRS / Gantt (add PDFs and sources here when ready). |
| [`deployment/`](deployment/) | **Installation, dependencies, and deployment** — start with [`deployment/INSTALL.md`](deployment/INSTALL.md). |
| [`user-documentation/`](user-documentation/) | End-user help — see [`user-documentation/README.md`](user-documentation/README.md) (full `USER_GUIDE.md` to be completed for submission). |
| [`render.yaml`](render.yaml) | Example Render.com configuration for hosting the API. |

## Quick start (local)

1. **Backend:** from `backend/`, configure `.env` from [`backend/.env.example`](backend/.env.example), install dependencies, run `uvicorn` on port `8000`. Details: [`deployment/INSTALL.md`](deployment/INSTALL.md).
2. **Mobile:** from `frontend/mobile/`, copy [`.env.example`](frontend/mobile/.env.example) to `.env`, set `EXPO_PUBLIC_API_BASE_URL` (LAN IP for a physical device, or `127.0.0.1` / `10.0.2.2` for simulators), then `npx expo start`.

API interactive docs: `http://127.0.0.1:8000/docs` when the backend is running.

Additional setup notes (Wi‑Fi, Render, Maps): [`documentation/SETUP.md`](documentation/SETUP.md).

## Main features (current implementation)

- **Authentication:** register, login, password reset flows (`/auth`).
- **Soil samples & recommendations:** REST endpoints under the main app (see `main.py`) plus **AI soil photo analysis** under `/ai/soil-analyze` (requires `GEMINI_API_KEY`).
- **Mobile screens:** Auth → Home, **Soil analysis**, **Map & weather**, **My account** (see `frontend/mobile/App.tsx`).
- **Weather:** `/weather/current` (Open-Meteo if `OPENWEATHER_API_KEY` is unset).

## Tech stack

- **Backend:** Python 3, FastAPI, Uvicorn, SQLAlchemy, Pydantic, JWT auth (see `backend/requirements.txt`).
- **Mobile:** Expo ~54, React 19, React Native 0.81, React Navigation 7 (see `frontend/mobile/package.json`).

## Team — GitHub usernames

Replace or extend the table below for your course submission (instructor will verify collaborators on GitHub).

| Name | GitHub username |
|------|-----------------|
| Bakary Coulibaly | @Bakary55 |
| *(other members)* | *@…* |

## License / course use

This repository is maintained for the AgrilabVision course project. Add a `LICENSE` file if you distribute the code beyond class scope.
