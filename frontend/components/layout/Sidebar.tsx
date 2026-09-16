"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { NAV_ITEMS } from "./nav-items";

export default function Sidebar() {
  const pathname = usePathname();

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
        {NAV_ITEMS.map((item) => {
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
      <p className="sidebar-foot">v1.0 · uso interno</p>
    </aside>
  );
}
