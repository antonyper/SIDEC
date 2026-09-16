import Link from "next/link";
import PageHeader from "@/components/ui/PageHeader";

const modules = [
  { href: "/guias", icon: "▤", title: "Guías", text: "Crear y consultar entregas" },
  { href: "/liquidaciones", icon: "✓", title: "Liquidaciones", text: "Registrar devoluciones" },
  { href: "/cobranzas", icon: "$", title: "Cobranzas", text: "Registrar y consultar pagos" },
  { href: "/inventario", icon: "▦", title: "Inventario", text: "Consultar existencias" },
  { href: "/agencias", icon: "●", title: "Agencias", text: "Gestionar agencias" },
  { href: "/productos", icon: "◇", title: "Productos", text: "Gestionar productos" },
  { href: "/reportes", icon: "▥", title: "Reportes", text: "Ver el estado del negocio" },
];

export default function Home() {
  return (
    <>
      <PageHeader title="Panel principal" subtitle="SIDEC" />
      <div className="page">
        <div className="hero">
          <p>Panel principal</p>
          <span>¿Qué necesitas hacer? Selecciona una opción para empezar.</span>
        </div>
        <div className="grid">
          {modules.map((item) => (
            <Link className="module" key={item.href} href={item.href}>
              <b>{item.icon}</b>
              <strong>{item.title}</strong>
              <small>{item.text}</small>
            </Link>
          ))}
        </div>
      </div>
    </>
  );
}
