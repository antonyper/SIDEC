"use client";

import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { login as apiLogin, logout as apiLogout, obtenerUsuarioActual, type Usuario } from "@/lib/auth";
import { getToken } from "@/lib/http";

type AuthContextValue = {
  usuario: Usuario | null;
  cargando: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

const RUTA_LOGIN = "/login";

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [cargando, setCargando] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  const cerrarSesion = useCallback(() => {
    apiLogout();
    setUsuario(null);
    router.push(RUTA_LOGIN);
  }, [router]);

  useEffect(() => {
    if (!getToken()) {
      // eslint-disable-next-line react-hooks/set-state-in-effect -- no hay sesión guardada, se resuelve de inmediato
      setCargando(false);
      return;
    }
    obtenerUsuarioActual()
      .then(setUsuario)
      .catch(() => setUsuario(null))
      .finally(() => setCargando(false));
  }, []);

  useEffect(() => {
    window.addEventListener("sidec:auth-expired", cerrarSesion);
    return () => window.removeEventListener("sidec:auth-expired", cerrarSesion);
  }, [cerrarSesion]);

  useEffect(() => {
    if (cargando) return;
    if (!usuario && pathname !== RUTA_LOGIN) {
      router.replace(RUTA_LOGIN);
    } else if (usuario && pathname === RUTA_LOGIN) {
      router.replace("/");
    }
  }, [cargando, usuario, pathname, router]);

  async function login(username: string, password: string) {
    const u = await apiLogin(username, password);
    setUsuario(u);
  }

  return (
    <AuthContext.Provider value={{ usuario, cargando, login, logout: cerrarSesion }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth debe usarse dentro de AuthProvider");
  return ctx;
}
