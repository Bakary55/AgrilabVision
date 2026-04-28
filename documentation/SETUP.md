# AgrilabVision — setup (backend + mobile)

## Backend

1. Backend `.env`:
   - `GEMINI_API_KEY` — required for AI (soil photo + farming insights).
   - `OPENWEATHER_API_KEY` — optional; if empty, weather uses Open-Meteo (no signup).

2. Install and run:
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. API docs: `http://127.0.0.1:8000/docs`

## Mobile (Expo)

1. `cd frontend/mobile && npm install`
2. Copy `frontend/mobile/.env.example` to `frontend/mobile/.env` and set `EXPO_PUBLIC_API_BASE_URL` to your machine’s LAN IP (same Wi‑Fi as the phone), e.g. `http://192.168.1.10:8000`.
3. `npx expo start` — open in **Expo Go**.

## Google Maps (optional)

Set `android.config.googleMaps.apiKey` in `frontend/mobile/app.json`, or use **Open in Google Maps** in the app (no SDK key).

## Store builds

See `frontend/mobile/README.md` (EAS Build).

## Deploy backend on Render (recommended for demos)

This removes the "same Wi-Fi" requirement between phone and computer.

1. Push the repo to GitHub.
2. In Render, create a **Web Service** from the repo.
3. Render auto-detects `render.yaml` at repo root. If needed, confirm:
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables in Render:
   - `GEMINI_API_KEY` (required)
   - `OPENWEATHER_API_KEY` (optional)
   - `DATABASE_URL` (recommended: managed Postgres URL)
5. Deploy and copy your public API URL, for example:
   - `https://agrilabvision-api.onrender.com`

Then update mobile:

1. Set `frontend/mobile/.env`:
   - `EXPO_PUBLIC_API_BASE_URL=https://your-render-url.onrender.com`
2. Restart Expo (`npx expo start`).
3. Test from mobile data (4G/5G) to confirm public access.
