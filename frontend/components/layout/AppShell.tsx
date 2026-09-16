"use client";

import { usePathname } from "next/navigation";
import { useAuth } from "@/components/auth/AuthContext";
import Sidebar from "./Sidebar";

export default function AppShell({ children }: { children: React.ReactNode }) {
  const { usuario, cargando } = useAuth();
  const pathname = usePathname();

  if (pathname === "/login") {
    return <>{children}</>;
  }

  if (cargando || !usuario) {
    return (
      <div className="auth-loading">
        <p>Cargando…</p>
      </div>
    );
  }

  return (
    <div className="app-shell">
      <Sidebar />
      <div className="content">{children}</div>
    </div>
  );
}
