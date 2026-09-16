"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/components/auth/AuthContext";
import { NAV_ITEMS } from "./nav-items";

export default function Sidebar() {
  const pathname = usePathname();
  const { usuario, logout } = useAuth();

  const items = NAV_ITEMS.filter((item) => !item.roles || (usuario && item.roles.includes(usuario.rol)));

  return (
    <aside className="sidebar">
      <Link href="/" className="sidebar-brand">
        <i>SD</i>
        <span>
          <strong>SIDEC</strong>
          <span>Distribución y consignación</span>
        </span>
      </Link>
      <nav className="sidebar-nav">
        {items.map((item) => {
          const active = item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`sidebar-link${active ? " active" : ""}`}
              aria-current={active ? "page" : undefined}
            >
              <b>{item.icon}</b>
              {item.label}
            </Link>
          );
        })}
      </nav>
      <div className="sidebar-user">
        <div className="sidebar-user-info">
          <strong>{usuario?.nombre}</strong>
          <span>{usuario?.rol === "ADMIN" ? "Administrador" : "Operador"}</span>
        </div>
        <button type="button" className="sidebar-logout" onClick={logout}>
          Cerrar sesión
        </button>
      </div>
      <p className="sidebar-foot">v1.0 · uso interno</p>
    </aside>
  );
}
