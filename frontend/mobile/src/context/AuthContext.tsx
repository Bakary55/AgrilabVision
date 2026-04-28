import AsyncStorage from "@react-native-async-storage/async-storage";
import {
  createContext,
  ReactNode,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import { API_BASE_URL } from "../constants/config";
import type { AuthUser, LoginResponse } from "../types/api";

const TOKEN_KEY = "agrilabvision_access_token";
const USER_KEY = "agrilabvision_user_json";

type AuthContextValue = {
  token: string | null;
  user: AuthUser | null;
  ready: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  logout: () => Promise<void>;
};

export type RegisterPayload = {
  first_name: string;
  last_name: string;
  email: string;
  age: number;
  user_type: "farmer" | "student" | "researcher";
  password: string;
};

const AuthContext = createContext<AuthContextValue | null>(null);

async function parseErrorDetail(res: Response, data: unknown): Promise<string> {
  if (typeof data === "object" && data !== null && "detail" in data) {
    const d = (data as { detail: unknown }).detail;
    if (typeof d === "string") return d;
    if (Array.isArray(d) && d[0]?.msg) return String(d[0].msg);
  }
  return `Request failed (${res.status})`;
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<AuthUser | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const [t, u] = await Promise.all([
          AsyncStorage.getItem(TOKEN_KEY),
          AsyncStorage.getItem(USER_KEY),
        ]);
        setToken(t);
        if (u) setUser(JSON.parse(u) as AuthUser);
      } catch {
        setToken(null);
        setUser(null);
      } finally {
        setReady(true);
      }
    })();
  }, []);

  const persistSession = useCallback(async (t: string, u: AuthUser) => {
    await AsyncStorage.multiSet([
      [TOKEN_KEY, t],
      [USER_KEY, JSON.stringify(u)],
    ]);
    setToken(t);
    setUser(u);
  }, []);

  const login = useCallback(
    async (email: string, password: string) => {
      const res = await fetch(`${API_BASE_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email.trim(), password }),
      });
      const data = (await res.json().catch(() => ({}))) as LoginResponse & {
        detail?: unknown;
      };
      if (!res.ok) {
        throw new Error(await parseErrorDetail(res, data));
      }
      await persistSession(data.access_token, data.user);
    },
    [persistSession]
  );

  const register = useCallback(
    async (payload: RegisterPayload) => {
      const res = await fetch(`${API_BASE_URL}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(await parseErrorDetail(res, data));
      }
      await login(payload.email, payload.password);
    },
    [login]
  );

  const logout = useCallback(async () => {
    await AsyncStorage.multiRemove([TOKEN_KEY, USER_KEY]);
    setToken(null);
    setUser(null);
  }, []);

  const value = useMemo(
    () => ({ token, user, ready, login, register, logout }),
    [token, user, ready, login, register, logout]
  );

  return (
    <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
