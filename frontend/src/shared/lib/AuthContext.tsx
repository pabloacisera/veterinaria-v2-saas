import { createContext, useContext, useState, useCallback, useEffect, type ReactNode } from "react";
import { apiGet, apiPost } from "./api";

interface AuthUser {
  email: string;
  name: string;
}

interface AuthContextType {
  user: AuthUser | null;
  isAuthenticated: boolean;
  login: (token: string, user: AuthUser) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(() => {
    if (import.meta.env.PROD) return null;
    const stored = localStorage.getItem("auth_user");
    return stored ? JSON.parse(stored) : null;
  });

  useEffect(() => {
    if (import.meta.env.PROD) {
      apiGet<{ email: string; name: string }>("/auth/me")
        .then((userData) => setUser({ email: userData.email, name: userData.name }))
        .catch(() => setUser(null));
    }
  }, []);

  const login = useCallback((token: string, userData: AuthUser) => {
    if (import.meta.env.PROD) {
      setUser(userData);
    } else {
      localStorage.setItem("access_token", token);
      localStorage.setItem("auth_user", JSON.stringify(userData));
      setUser(userData);
    }
  }, []);

  const logout = useCallback(() => {
    if (import.meta.env.PROD) {
      apiPost("/auth/logout", {}).catch(() => {});
    } else {
      localStorage.removeItem("access_token");
      localStorage.removeItem("auth_user");
    }
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, isAuthenticated: !!user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
