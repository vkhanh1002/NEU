"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { api, User } from "@/lib/api";

type AuthContextValue = {
  user: User | null;
  ready: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
};
const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [ready, setReady] = useState(false);
  useEffect(() => {
    const token = window.sessionStorage.getItem("study_access_token");
    const stored = window.sessionStorage.getItem("study_user");
    if (!token || !stored) { setReady(true); return; }
    try {
      const parsed = JSON.parse(stored) as User;
      api<User>("/auth/me").then(setUser).catch(() => {
        window.sessionStorage.removeItem("study_access_token");
        window.sessionStorage.removeItem("study_refresh_token");
        window.sessionStorage.removeItem("study_user");
      }).finally(() => setReady(true));
      setUser(parsed);
    } catch { setReady(true); }
  }, []);
  const login = useCallback(async (email: string, password: string) => {
    const tokens = await api<{ access_token: string; refresh_token: string; user: User }>("/auth/login", {
      method: "POST", body: JSON.stringify({ email, password }),
    });
    window.sessionStorage.setItem("study_access_token", tokens.access_token);
    window.sessionStorage.setItem("study_refresh_token", tokens.refresh_token);
    window.sessionStorage.setItem("study_user", JSON.stringify(tokens.user));
    setUser(tokens.user);
    setReady(true);
  }, []);
  const logout = useCallback(() => {
    window.sessionStorage.removeItem("study_access_token");
    window.sessionStorage.removeItem("study_refresh_token");
    window.sessionStorage.removeItem("study_user");
    setUser(null);
  }, []);
  const value = useMemo(() => ({ user, ready, login, logout }), [user, ready, login, logout]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) throw new Error("useAuth must be used inside AuthProvider");
  return value;
}
