import Constants from "expo-constants";

/**
 * FastAPI backend base URL (no trailing slash).
 * - iOS Simulator: http://127.0.0.1:8000
 * - Android emulator: http://10.0.2.2:8000
 * - Physical device: http://YOUR_PC_LAN_IP:8000
 *
 * Set EXPO_PUBLIC_API_BASE_URL in mobile/.env (see .env.example).
 */
const extraUrl = Constants.expoConfig?.extra?.apiBaseUrl as string | undefined;

export const API_BASE_URL =
  process.env.EXPO_PUBLIC_API_BASE_URL?.trim() ||
  extraUrl?.trim() ||
  "http://127.0.0.1:8000";
