# AgrilabVision — mobile app (Expo)

React Native via Expo. Use **Expo Go** for development; use **EAS Build** for Play Store / App Store.

## Requirements

- Node.js (LTS)
- Backend running (repo root)

## Install

```bash
cd mobile
npm install
```

## Backend URL

Create `mobile/.env` from `.env.example`:

```env
EXPO_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

- **Android emulator:** `http://10.0.2.2:8000`
- **Physical device (same Wi‑Fi):** `http://YOUR_PC_IP:8000`

Restart `npx expo start` after changing `.env`.

## Run

```bash
npx expo start
```

Scan the QR code with **Expo Go**.

## Google Maps (embedded map)

1. Create a **Maps SDK for Android** API key in Google Cloud Console.
2. Put it in `app.json` under `expo.android.config.googleMaps.apiKey`.

The **Open in Google Maps** button works without an SDK key.

## Store distribution

```bash
npm install -g eas-cli
eas login
eas build:configure
eas build --platform android
```

See [Expo EAS Build](https://docs.expo.dev/build/introduction/).
