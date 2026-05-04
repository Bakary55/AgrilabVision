# AgrilabVision — User guide

This guide describes the **Expo mobile app** (`frontend/mobile/`) used with the **FastAPI backend**. For installation and URLs, see [`../deployment/INSTALL.md`](../deployment/INSTALL.md).

---

## 1. Getting started

1. **Install** the backend and start it (`uvicorn` on port **8000**). See `deployment/INSTALL.md`.
2. On your phone or emulator, set **`EXPO_PUBLIC_API_BASE_URL`** in `frontend/mobile/.env` to the machine that runs the API (LAN IP for a real phone, or `127.0.0.1` / `10.0.2.2` for simulators).
3. Start the app: `cd frontend/mobile && npx expo start`, then open the project in **Expo Go** or a dev build.
4. **Register** a new account or **log in** on the first screen.

---

## 2. Main screens

### Authentication

- **Login:** email and password.
- **Register:** first name, last name, email, age (13+), role (e.g. farmer), password.
- **Forgot password / reset:** use the links on the auth screen; follow the messages from the server (reset flow depends on backend configuration).

### Home

After login you see **AgrilabVision** with a short description and two actions:

- **Analyze a soil photo** — opens soil analysis (camera / gallery, optional manual fields, CSV import).
- **Map, weather & decision support** — opens map, current weather, and AI farming insights (GPS required for best results).

Use the **avatar** (top right) to open **My account**. **Log out** is at the bottom of the home screen.

### Soil analysis (`Analyze`)

- Choose **analysis language** (English / French) for labels and results.
- **Choose photo** or **Take photo** — the app asks for media/camera permission if needed.
- Tap **Analyze soil** to send the image to the backend (**Gemini** must be configured on the server).
- Optional **manual soil input** (pH, moisture, organic matter, etc.) then **Analyze manual data** for recommendations when the photo alone is not enough.
- **Import CSV** — select a `.csv` file to bulk-import lab-style rows (format must match what the API expects).
- From results, you can go to **Weather, map & decision support** with context from the analysis.

### Map & weather (`MapWeather`)

- Allows **location** access when prompted so the map centers on you.
- Shows **current weather** from the backend (Open-Meteo or OpenWeather, depending on server config).
- **Generate agronomic insights** sends soil context (when opened from analysis) plus weather to the AI — requires a working API and keys on the server.
- **Open in Google Maps** opens the coordinates in the external Maps app if embedded maps are not configured.

### My account (`Account`)

- Shows your name, email, and role.
- **Add / change profile photo** — stored locally on the device with your session (not necessarily synced to the server profile).

---

## 3. Screenshots (place files in `screenshots/`)

Add PNG (or JPG) files next to this guide so the images render on GitHub.

| # | File to add | What to capture |
|---|-------------|-----------------|
| 1 | `screenshots/01-auth.png` | Login or register screen |
| 2 | `screenshots/02-home.png` | Home with the two main buttons |
| 3 | `screenshots/03-analyze.png` | Analyze screen with a photo or results |
| 4 | `screenshots/04-map-weather.png` | Map and weather panel |
| 5 | `screenshots/05-account.png` | Account screen with profile |

Example (after you add the files):

![Login](screenshots/01-auth.png)

![Home](screenshots/02-home.png)

---

## 4. Troubleshooting

| Problem | What to try |
|--------|-------------|
| **Network request failed** / cannot reach API | Confirm the backend is running. On a **physical phone**, use your PC’s **Wi‑Fi IPv4** in `.env`, not `127.0.0.1`. Backend must use `--host 0.0.0.0`. |
| **401 / Login failed** | Check email/password. Register first if you have no account. |
| **AI / soil analysis error** | Server needs `GEMINI_API_KEY`. Check server logs and `GET /docs` on the API. |
| **Weather unavailable** | Backend must be reachable; check `/weather/current` in API docs. |
| **Location or map issues** | Grant **location** permission in system settings; for map SDK keys see `documentation/SETUP.md`. |
| **Permission denied (photos)** | Allow **Photos** / **Camera** for Expo Go in Android or iOS settings. |
| **App crashes on launch in release** | Set `EXPO_PUBLIC_API_BASE_URL` in `.env` for production builds (see `frontend/mobile/src/constants/config.ts`). |

---

## 5. FAQ

**Do I need an internet connection?**  
Yes for login, analysis, weather, and AI. The app is built around online APIs.

**Is my data synced across devices?**  
Account and soil data are on the **server** when you use the API; the **profile photo** in Account is stored **locally** on the device in the current implementation.

**Which languages are supported in the app?**  
Soil analysis labels and some map/weather strings support **English** and **French** via the language toggle on the Analyze screen.

**Where is the API documented?**  
Open `http://<your-api-host>:8000/docs` when the backend is running (Swagger UI).

---

## 6. Support

For course-related questions, contact your instructor. For technical setup, see the repository **`deployment/INSTALL.md`** and **`documentation/SETUP.md`**.
