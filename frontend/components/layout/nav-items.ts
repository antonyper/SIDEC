export type NavItem = {
  href: string;
  icon: string;
  label: string;
};

export const NAV_ITEMS: NavItem[] = [
  { href: "/", icon: "⌂", label: "Inicio" },
  { href: "/guias", icon: "▤", label: "Guías" },
  { href: "/liquidaciones", icon: "✓", label: "Liquidaciones" },
  { href: "/cobranzas", icon: "$", label: "Cobranzas" },
  { href: "/inventario", icon: "▦", label: "Inventario" },
  { href: "/agencias", icon: "●", label: "Agencias" },
  { href: "/productos", icon: "◇", label: "Productos" },
  { href: "/reportes", icon: "▥", label: "Reportes" },
];
