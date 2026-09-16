"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import PageHeader from "@/components/ui/PageHeader";
import BarChart from "@/components/ui/BarChart";
import { ApiError } from "@/lib/http";
import {
  reporteDeudaPendiente,
  reporteDetallePorAgencia,
  type DeudaPendienteResponse,
  type DetalleAgenciaResponse,
} from "@/lib/reportes";
import { ESTADO_GUIA_LABEL, type EstadoGuia } from "@/lib/guias";

function money(n: number) {
  return `S/ ${n.toFixed(2)}`;
}

const MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"];

function formatMes(anioMes: string): string {
  const [anio, mes] = anioMes.split("-");
  return `${MESES[Number(mes) - 1]} ${anio}`;
}

const ESTADO_COLOR: Record<string, string> = {
  EN_VENTA: "var(--blue)",
  PENDIENTE_LIQUIDACION: "var(--warn-fg)",
  PARCIALMENTE_LIQUIDADA: "#c2820a",
};

function diasTranscurridos(fecha: string): number {
  const hoy = new Date();
  const f = new Date(fecha + "T00:00:00");
  return Math.floor((hoy.getTime() - f.getTime()) / 86400000);
}

export default function DashboardCobranzaPage() {
  const [deuda, setDeuda] = useState<DeudaPendienteResponse | null>(null);
  const [detalle, setDetalle] = useState<DetalleAgenciaResponse | null>(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([reporteDeudaPendiente(), reporteDetallePorAgencia({})])
      .then(([d, det]) => {
        setDeuda(d);
        setDetalle(det);
      })
      .catch((err) => setError(err instanceof ApiError ? err.message : "No se pudo cargar el dashboard."))
      .finally(() => setCargando(false));
  }, []);

  // Todas las líneas de "detalle por agencia" en una sola lista, cada una con sus días transcurridos.
  const lineas = (detalle?.grupos ?? []).flatMap((grupo) =>
    grupo.detalles.map((d) => ({ ...d, agencia: grupo.agencia, dias: diasTranscurridos(d.fecha) }))
  );

  const guiasVencidasIds = new Set(lineas.filter((l) => l.dias > 30).map((l) => l.guia_id));
  const estimadoGuiasVencidas = lineas.filter((l) => l.dias > 30).reduce((acc, l) => acc + l.x_estimado, 0);
  const estimadoTotal = detalle?.total_general ?? 0;

  const porMes = Object.entries(
    lineas.reduce<Record<string, number>>((acc, l) => {
      const clave = l.fecha.slice(0, 7);
      acc[clave] = (acc[clave] ?? 0) + l.x_estimado;
      return acc;
    }, {})
  )
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([clave, monto]) => ({ label: formatMes(clave), value: monto }));

  const estadosGuia: EstadoGuia[] = ["EN_VENTA", "PENDIENTE_LIQUIDACION", "PARCIALMENTE_LIQUIDADA"];
  const chartEstados = estadosGuia
    .map((estado) => ({
      estado,
      monto: lineas.filter((l) => l.estado_guia === estado).reduce((acc, l) => acc + l.x_estimado, 0),
    }))
    .filter((e) => e.monto > 0)
    .map((e) => ({
      label: ESTADO_GUIA_LABEL[e.estado],
      value: e.monto,
      color: ESTADO_COLOR[e.estado],
    }));

  const topDeudores = deuda
    ? Object.values(
        deuda.items.reduce<Record<string, { agencia: string; total: number }>>((acc, item) => {
          acc[item.agencia] = acc[item.agencia] ?? { agencia: item.agencia, total: 0 };
          acc[item.agencia].total += item.monto_pendiente;
          return acc;
        }, {})
      )
        .sort((a, b) => b.total - a.total)
        .slice(0, 10)
    : [];

  const porAgencia = (detalle?.grupos ?? [])
    .map((grupo) => ({
      agencia: grupo.agencia,
      nroGuias: new Set(grupo.detalles.map((d) => d.guia_id)).size,
      nroProductos: new Set(grupo.detalles.map((d) => d.producto_id)).size,
      montoEstimado: grupo.total_entregado,
    }))
    .sort((a, b) => b.montoEstimado - a.montoEstimado);

  return (
    <>
      <PageHeader
        title="Dashboard de cobranza"
        subtitle="Reportes"
        actions={
          <Link href="/reportes" className="btn btn-secondary">
            Volver a reportes
          </Link>
        }
      />
      <div className="page">
        {error && <p className="error-banner">{error}</p>}
        {cargando ? (
          <p className="empty-state">Cargando…</p>
        ) : (
          <>
            <div className="stat-grid">
              <div className="stat-card">
                <span>Estimado 50% total</span>
                <strong>{money(estimadoTotal)}</strong>
              </div>
              <div className="stat-card">
                <span>Deuda por cobrar</span>
                <strong>{deuda ? money(deuda.total_pendiente) : "—"}</strong>
              </div>
              <div className="stat-card">
                <span>Guías vencidas (30 días)</span>
                <strong style={{ color: guiasVencidasIds.size > 0 ? "var(--off-fg)" : "var(--ink)" }}>
                  {guiasVencidasIds.size}
                </strong>
              </div>
              <div className="stat-card">
                <span>Estimado 50% guías vencidas</span>
                <strong style={{ color: estimadoGuiasVencidas > 0 ? "var(--off-fg)" : "var(--ink)" }}>
                  {money(estimadoGuiasVencidas)}
                </strong>
              </div>
            </div>

            <div className="form-grid cols-2" style={{ maxWidth: "none", marginBottom: 20 }}>
              <div className="card">
                <h2 style={{ marginBottom: 16 }}>Estimado 50% por mes</h2>
                {porMes.length === 0 ? (
                  <p className="empty-state">No hay guías pendientes de liquidar.</p>
                ) : (
                  <BarChart data={porMes} valueFormatter={money} orientation="vertical" />
                )}
              </div>
              <div className="card">
                <h2 style={{ marginBottom: 16 }}>Estimado por estado de guía</h2>
                {chartEstados.length === 0 ? (
                  <p className="empty-state">No hay guías pendientes de liquidar.</p>
                ) : (
                  <BarChart
                    data={chartEstados}
                    valueFormatter={(v) => `${money(v)} (${estimadoTotal > 0 ? ((v / estimadoTotal) * 100).toFixed(0) : 0}%)`}
                  />
                )}
              </div>
            </div>

            <div className="form-grid cols-2" style={{ maxWidth: "none" }}>
              <div className="card">
                <h2 style={{ marginBottom: 12 }}>Estimado por agencia</h2>
                {porAgencia.length === 0 ? (
                  <p className="empty-state">No hay guías pendientes de liquidar.</p>
                ) : (
                  <div className="table-wrap">
                    <table>
                      <thead>
                        <tr>
                          <th>Agencia</th>
                          <th className="num">N° Guías</th>
                          <th className="num">N° Productos</th>
                          <th className="num">Monto estimado</th>
                        </tr>
                      </thead>
                      <tbody>
                        {porAgencia.map((a) => (
                          <tr key={a.agencia}>
                            <td>{a.agencia}</td>
                            <td className="num">{a.nroGuias}</td>
                            <td className="num">{a.nroProductos}</td>
                            <td className="num">{money(a.montoEstimado)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
              <div className="card">
                <h2 style={{ marginBottom: 12 }}>Top 10 agencias con más deuda</h2>
                {topDeudores.length === 0 ? (
                  <p className="empty-state">No hay deuda pendiente.</p>
                ) : (
                  <BarChart
                    data={topDeudores.map((d) => ({ label: d.agencia, value: d.total }))}
                    valueFormatter={money}
                  />
                )}
              </div>
            </div>
          </>
        )}
      </div>
    </>
  );
}
