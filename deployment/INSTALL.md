# AgrilabVision — installation & deployment

## Prerequisites

- **Python** 3.10+ (3.11 or 3.12 recommended)
- **Node.js** 20 LTS (or compatible with Expo 54)
- **npm** (ships with Node)
- **Git**
- Optional: **Android Studio** / **Xcode** for emulators; **Expo Go** on a phone for quickest testing

## Backend (FastAPI)

### 1. Environment variables

From the `backend` directory:

```bash
copy .env.example .env   # Windows
# cp .env.example .env   # macOS / Linux
```

Edit `.env`:

| Variable | Required | Purpose |
|----------|----------|---------|
| `SECRET_KEY` | Yes (production) | JWT / crypto secret |
| `GEMINI_API_KEY` | Yes for AI | `/ai/soil-analyze` and related AI features |
| `OPENWEATHER_API_KEY` | No | If empty, `/weather/current` uses Open-Meteo |
| `CORS_ORIGINS` | Recommended | Comma-separated front-end origins (see `.env.example`) |
| `DATABASE_URL` | Optional locally | Defaults to SQLite `./agrilabvision.db`; use Postgres in production |

### 2. Dependencies (pinned reference — mobile)

The API’s Python packages are listed in **`backend/requirements.txt`** without strict pins in-repo. Install with:

```bash
cd backend
pip install -r requirements.txt
```

Typical resolved stack: **FastAPI**, **Uvicorn**, **SQLAlchemy**, **Pydantic v2**, **python-jose**, **bcrypt**, **python-multipart**, **python-dotenv**, **google-generativeai**, **httpx**, **psycopg2-binary**.

To pin exact versions for a report, run after install:

```bash
pip freeze > requirements-lock.txt
```

### 3. Run the API

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- Health: `GET http://127.0.0.1:8000/`
- OpenAPI UI: `http://127.0.0.1:8000/docs`

Main route groups: **`/auth`**, **`/ai`**, **`/weather/current`**, **`/insights/farming`**, plus soil sample / recommendation endpoints on the app root (see `app/main.py`).

---

## Mobile app (Expo)

### 1. Dependencies (from `frontend/mobile/package.json`)

| Package | Version (approx.) |
|---------|-------------------|
| expo | ~54.0.34 |
| react | 19.1.0 |
| react-native | 0.81.5 |
| @react-navigation/native | ^7.2.2 |
| @react-navigation/native-stack | ^7.14.10 |
| typescript (dev) | ~5.9.2 |

Install:

```bash
cd frontend/mobile
npm install
```

### 2. Environment

Copy **`frontend/mobile/.env.example`** to **`.env`** and set:

```env
EXPO_PUBLIC_API_BASE_URL=http://YOUR_HOST:8000
```

- **iOS Simulator:** `http://127.0.0.1:8000`
- **Android emulator:** `http://10.0.2.2:8000`
- **Physical device (same Wi‑Fi as PC):** `http://<PC_LAN_IP>:8000` (backend must use `--host 0.0.0.0`)

Restart Expo after any `.env` change.

### 3. Run

```bash
cd frontend/mobile
npx expo start
```

Open in **Expo Go** or an emulator. Store builds: see `frontend/mobile/README.md` (EAS).

---

## Optional: Google Maps SDK

For embedded maps keys, configure `android.config.googleMaps.apiKey` in `frontend/mobile/app.json`, or use external “Open in Google Maps” flows (see `documentation/SETUP.md`).

---

## Deployment (example: Render)

1. Push this repository to GitHub.
2. Create a **Web Service** pointing at this repo; set **Root Directory** to `backend` if the platform does not use `render.yaml` automatically.
3. **Build:** `pip install -r requirements.txt`  
   **Start:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Set the same env vars as in `.env.example` (`GEMINI_API_KEY`, `DATABASE_URL` for Postgres, `CORS_ORIGINS` including your Expo web/dev URLs).

See also root **`render.yaml`** and **`documentation/SETUP.md`**.

## Live demo URL

- **Backend:** set after deploy, e.g. `https://<your-service>.onrender.com`
- **Mobile:** usually distributed via Expo Go or store builds; put your public demo link here if you have one.

*If nothing is hosted, state: “No public URL — local demo only.”*
