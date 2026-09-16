import Link from "next/link";
import PageHeader from "@/components/ui/PageHeader";

const grupos = [
  {
    titulo: "General",
    reportes: [
      {
        href: "/reportes/dashboard-cobranza",
        nombre: "Dashboard de cobranza",
        texto: "Guías por vencer y deuda pendiente, todo en un solo lugar.",
      },
      {
        href: "/reportes/detalle-por-agencia",
        nombre: "Detalle por agencia",
        texto: "Productos entregados por agencia con estimado (50% precio agencia).",
      },
      {
        href: "/reportes/distribucion",
        nombre: "Distribución",
        texto: "Matriz de cantidad entregada por agencia y producto.",
      },
      {
        href: "/reportes/resumen-periodo",
        nombre: "Resumen por período",
        texto: "Vista general del negocio en un rango de fechas.",
      },
    ],
  },
  {
    titulo: "Guías",
    reportes: [
      { href: "/reportes/resumen-guias", nombre: "Resumen de guías", texto: "Cantidad de guías por estado." },
    ],
  },
  {
    titulo: "Cobranzas",
    reportes: [
      {
        href: "/reportes/cobranzas-por-periodo",
        nombre: "Cobranzas por período",
        texto: "Cobranzas generadas en un rango de fechas.",
      },
      { href: "/reportes/deuda-pendiente", nombre: "Deuda pendiente", texto: "Cobranzas con saldo por cobrar." },
    ],
  },
  {
    titulo: "Agencias",
    reportes: [
      { href: "/reportes/agencias", nombre: "Reporte de agencias", texto: "Directorio con totales de guías." },
      {
        href: "/reportes/ranking-agencias-venta",
        nombre: "Ranking de agencias por % de venta",
        texto: "Qué agencias venden más y cuáles devuelven más.",
      },
    ],
  },
  {
    titulo: "Productos",
    reportes: [
      {
        href: "/reportes/por-producto",
        nombre: "Reporte por producto",
        texto: "Entregado, vendido, ingresos y stock.",
      },
    ],
  },
];

export default function ReportesPage() {
  return (
    <>
      <PageHeader title="Reportes" subtitle="Vista general del negocio" />
      <div className="page">
        {grupos.map((grupo) => (
          <div className="report-group" key={grupo.titulo}>
            <h2>{grupo.titulo}</h2>
            <div className="report-list">
              {grupo.reportes.map((r) => (
                <Link key={r.href} href={r.href} className="report-link">
                  <strong>{r.nombre}</strong>
                  <small>{r.texto}</small>
                </Link>
              ))}
            </div>
          </div>
        ))}
      </div>
    </>
  );
}
