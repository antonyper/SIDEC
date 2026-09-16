"use client";

import { use, useEffect, useState } from "react";
import Link from "next/link";
import PageHeader from "@/components/ui/PageHeader";
import { ApiError } from "@/lib/http";
import {
  reporteAgencias,
  reporteCobranzasPorPeriodo,
  reporteDesempenoAgencias,
  descargarDetallePorAgenciaPdf,
  reporteDetallePorAgencia,
  reporteDeudaPendiente,
  reporteDistribucion,
  reporteGuiasPendientes,
  reporteGuiasPendientesLiquidacion,
  reporteGuiasPorVencer,
  reporteKardexInventario,
  reportePorProducto,
  reporteRankingAgenciasVenta,
  reporteResumenGuias,
  reporteResumenPeriodo,
  reporteTopAgenciasProductos,
  type RangoFechas,
} from "@/lib/reportes";
import { listarProductos, type ProductoListItem } from "@/lib/productos";
import { TIPO_MOVIMIENTO_LABEL, type TipoMovimientoInventario } from "@/lib/inventario";
import { ESTADO_GUIA_BADGE, ESTADO_GUIA_LABEL, type EstadoGuia } from "@/lib/guias";
import BarChart from "@/components/ui/BarChart";

const TITULOS: Record<string, string> = {
  "cobranzas-por-periodo": "Cobranzas por período",
  "guias-pendientes": "Guías pendientes",
  "guias-pendientes-liquidacion": "Guías pendientes de liquidación",
  "resumen-guias": "Resumen de guías",
  "desempeno-agencias": "Desempeño de agencias",
  "deuda-pendiente": "Deuda pendiente",
  "por-producto": "Reporte por producto",
  agencias: "Reporte de agencias",
  "resumen-periodo": "Resumen por período",
  "kardex-inventario": "Kardex de inventario",
  "ranking-agencias-venta": "Ranking de agencias por % de venta",
  "guias-por-vencer": "Guías por vencer",
  distribucion: "Distribución",
  "detalle-por-agencia": "Detalle por agencia",
  "top-agencias-productos": "Top 10 agencias por variedad de productos",
};

const CON_FILTRO_FECHA = new Set([
  "cobranzas-por-periodo",
  "desempeno-agencias",
  "resumen-periodo",
  "kardex-inventario",
  "ranking-agencias-venta",
  "distribucion",
  "detalle-por-agencia",
]);

const CON_FILTRO_PRODUCTO = new Set(["kardex-inventario", "distribucion"]);

const ESTADO_GUIA_LABEL_CORTO: Record<EstadoGuia, string> = {
  EN_VENTA: "En venta",
  PENDIENTE_LIQUIDACION: "Pdte. liquidación",
  PARCIALMENTE_LIQUIDADA: "Parcial",
  LIQUIDADA: "Liquidada",
  ANULADA: "Anulada",
};

function money(n: number) {
  return `S/ ${n.toFixed(2)}`;
}

function iso(fecha: Date): string {
  return fecha.toISOString().slice(0, 10);
}

function inicioDeSemana(hoy: Date): Date {
  const dia = hoy.getDay();
  const desplazamiento = dia === 0 ? 6 : dia - 1;
  const inicio = new Date(hoy);
  inicio.setDate(hoy.getDate() - desplazamiento);
  return inicio;
}

function DateRangeFilter({ rango, onChange }: { rango: RangoFechas; onChange: (r: RangoFechas) => void }) {
  const hoy = new Date();

  function aplicarPreset(desde: Date) {
    onChange({ desde: iso(desde), hasta: iso(hoy) });
  }

  return (
    <div className="toolbar" style={{ flexWrap: "wrap" }}>
      <label className="field" style={{ flex: "0 0 auto" }}>
        Desde
        <input
          className="input"
          type="date"
          value={rango.desde ?? ""}
          onChange={(e) => onChange({ ...rango, desde: e.target.value || undefined })}
        />
      </label>
      <label className="field" style={{ flex: "0 0 auto" }}>
        Hasta
        <input
          className="input"
          type="date"
          value={rango.hasta ?? ""}
          onChange={(e) => onChange({ ...rango, hasta: e.target.value || undefined })}
        />
      </label>
      <div style={{ display: "flex", gap: 8, alignItems: "flex-end", flexWrap: "wrap" }}>
        <button type="button" className="btn btn-secondary btn-sm" onClick={() => aplicarPreset(inicioDeSemana(hoy))}>
          Semana actual
        </button>
        <button
          type="button"
          className="btn btn-secondary btn-sm"
          onClick={() => aplicarPreset(new Date(hoy.getFullYear(), hoy.getMonth(), 1))}
        >
          Mes actual
        </button>
        <button
          type="button"
          className="btn btn-secondary btn-sm"
          onClick={() => {
            const desde = new Date(hoy);
            desde.setDate(hoy.getDate() - 29);
            aplicarPreset(desde);
          }}
        >
          Últimos 30 días
        </button>
        <button type="button" className="btn btn-ghost btn-sm" onClick={() => onChange({})}>
          Limpiar
        </button>
      </div>
    </div>
  );
}

export default function ReportePage({ params }: { params: Promise<{ reporte: string }> }) {
  const { reporte } = use(params);
  const [rango, setRango] = useState<RangoFechas>({});
  const [productoId, setProductoId] = useState("");
  const [productosSeleccionados, setProductosSeleccionados] = useState<Set<number>>(new Set());
  const [productos, setProductos] = useState<ProductoListItem[]>([]);
  const [data, setData] = useState<unknown>(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");
  const [descargandoPdf, setDescargandoPdf] = useState(false);

  async function handleDescargarPdf() {
    setDescargandoPdf(true);
    setError("");
    try {
      await descargarDetallePorAgenciaPdf(rango);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo generar el PDF.");
    } finally {
      setDescargandoPdf(false);
    }
  }

  useEffect(() => {
    if (!CON_FILTRO_PRODUCTO.has(reporte)) return;
    listarProductos()
      .then(setProductos)
      .catch(() => {});
  }, [reporte]);

  useEffect(() => {
    /* eslint-disable react-hooks/set-state-in-effect -- sincroniza el reporte con la API al cambiar filtros */
    let cancelado = false;
    setCargando(true);
    setError("");

    const cargar = (): Promise<unknown> => {
      switch (reporte) {
        case "cobranzas-por-periodo":
          return reporteCobranzasPorPeriodo(rango);
        case "guias-pendientes":
          return reporteGuiasPendientes();
        case "guias-pendientes-liquidacion":
          return reporteGuiasPendientesLiquidacion();
        case "resumen-guias":
          return reporteResumenGuias();
        case "desempeno-agencias":
          return reporteDesempenoAgencias(rango);
        case "deuda-pendiente":
          return reporteDeudaPendiente();
        case "por-producto":
          return reportePorProducto();
        case "agencias":
          return reporteAgencias();
        case "resumen-periodo":
          return reporteResumenPeriodo(rango);
        case "kardex-inventario":
          return reporteKardexInventario({ ...rango, producto_id: productoId ? Number(productoId) : undefined });
        case "ranking-agencias-venta":
          return reporteRankingAgenciasVenta(rango);
        case "guias-por-vencer":
          return reporteGuiasPorVencer();
        case "distribucion":
          return reporteDistribucion({
            ...rango,
            producto_ids: productosSeleccionados.size > 0 ? Array.from(productosSeleccionados) : undefined,
          });
        case "detalle-por-agencia":
          return reporteDetallePorAgencia(rango);
        case "top-agencias-productos":
          return reporteTopAgenciasProductos();
        default:
          return Promise.reject(new ApiError("Reporte no encontrado."));
      }
    };

    cargar()
      .then((res) => !cancelado && setData(res))
      .catch((err) => !cancelado && setError(err instanceof ApiError ? err.message : "No se pudo cargar el reporte."))
      .finally(() => !cancelado && setCargando(false));
    /* eslint-enable react-hooks/set-state-in-effect */

    return () => {
      cancelado = true;
    };
  }, [reporte, rango, productoId, productosSeleccionados]);

  function toggleProducto(id: number) {
    setProductosSeleccionados((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  return (
    <>
      <PageHeader
        title={TITULOS[reporte] ?? "Reporte"}
        subtitle="Reportes"
        actions={
          <>
            <Link href="/reportes" className="btn btn-secondary">
              Volver a reportes
            </Link>
            {reporte === "detalle-por-agencia" && (
              <button type="button" className="btn" onClick={handleDescargarPdf} disabled={descargandoPdf}>
                {descargandoPdf ? "Generando PDF…" : "Descargar PDF"}
              </button>
            )}
          </>
        }
      />
      <div className="page">
        {reporte === "kardex-inventario" && (
          <div className="toolbar">
            <select className="input" value={productoId} onChange={(e) => setProductoId(e.target.value)}>
              <option value="">Todos los productos</option>
              {productos.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.nombre}
                </option>
              ))}
            </select>
          </div>
        )}
        {reporte === "distribucion" && (
          <div className="card" style={{ marginBottom: 16, padding: 16 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
              <strong>Productos a mostrar</strong>
              <div style={{ display: "flex", gap: 8 }}>
                <button
                  type="button"
                  className="btn btn-ghost btn-sm"
                  onClick={() => setProductosSeleccionados(new Set(productos.map((p) => p.id)))}
                >
                  Seleccionar todos
                </button>
                <button type="button" className="btn btn-ghost btn-sm" onClick={() => setProductosSeleccionados(new Set())}>
                  Ninguno (mostrar todos)
                </button>
              </div>
            </div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "10px 20px" }}>
              {productos.map((p) => (
                <label key={p.id} style={{ display: "flex", alignItems: "center", gap: 6, fontWeight: 500 }}>
                  <input
                    type="checkbox"
                    checked={productosSeleccionados.has(p.id)}
                    onChange={() => toggleProducto(p.id)}
                  />
                  {p.nombre}
                </label>
              ))}
            </div>
          </div>
        )}
        {CON_FILTRO_FECHA.has(reporte) && <DateRangeFilter rango={rango} onChange={setRango} />}
        {error && <p className="error-banner">{error}</p>}
        {cargando ? (
          <p className="empty-state">Cargando reporte…</p>
        ) : (
          <ReporteContenido reporte={reporte} data={data} />
        )}
      </div>
    </>
  );
}

function ReporteContenido({ reporte, data }: { reporte: string; data: unknown }) {
  switch (reporte) {
    case "cobranzas-por-periodo":
      return <TablaCobranzasPorPeriodo data={data as Awaited<ReturnType<typeof reporteCobranzasPorPeriodo>>} />;
    case "guias-pendientes":
    case "guias-pendientes-liquidacion":
      return <TablaGuiasPendientes data={data as Awaited<ReturnType<typeof reporteGuiasPendientes>>} />;
    case "resumen-guias":
      return <ResumenGuias data={data as Awaited<ReturnType<typeof reporteResumenGuias>>} />;
    case "desempeno-agencias":
      return <TablaDesempenoAgencias data={data as Awaited<ReturnType<typeof reporteDesempenoAgencias>>} />;
    case "deuda-pendiente":
      return <TablaDeudaPendiente data={data as Awaited<ReturnType<typeof reporteDeudaPendiente>>} />;
    case "por-producto":
      return <TablaPorProducto data={data as Awaited<ReturnType<typeof reportePorProducto>>} />;
    case "agencias":
      return <TablaAgencias data={data as Awaited<ReturnType<typeof reporteAgencias>>} />;
    case "resumen-periodo":
      return <ResumenPeriodo data={data as Awaited<ReturnType<typeof reporteResumenPeriodo>>} />;
    case "kardex-inventario":
      return <TablaKardexInventario data={data as Awaited<ReturnType<typeof reporteKardexInventario>>} />;
    case "ranking-agencias-venta":
      return <TablaRankingAgencias data={data as Awaited<ReturnType<typeof reporteRankingAgenciasVenta>>} />;
    case "guias-por-vencer":
      return <TablaGuiasPorVencer data={data as Awaited<ReturnType<typeof reporteGuiasPorVencer>>} />;
    case "distribucion":
      return <TablaDistribucion data={data as Awaited<ReturnType<typeof reporteDistribucion>>} />;
    case "detalle-por-agencia":
      return <TablaDetallePorAgencia data={data as Awaited<ReturnType<typeof reporteDetallePorAgencia>>} />;
    case "top-agencias-productos":
      return <GraficoTopAgenciasProductos data={data as Awaited<ReturnType<typeof reporteTopAgenciasProductos>>} />;
    default:
      return <p className="empty-state">Reporte no encontrado.</p>;
  }
}

function TablaCobranzasPorPeriodo({ data }: { data: Awaited<ReturnType<typeof reporteCobranzasPorPeriodo>> }) {
  if (!data?.length) return <p className="empty-state">No hay cobranzas en el rango seleccionado.</p>;
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Fecha</th>
            <th>Agencia</th>
            <th className="num">Monto</th>
            <th className="num">Pagado</th>
            <th className="num">Pendiente</th>
            <th>Estado</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row) => (
            <tr key={row.liquidacion_id}>
              <td>{row.fecha}</td>
              <td>{row.agencia}</td>
              <td className="num">{money(row.monto)}</td>
              <td className="num">{money(row.monto_pagado)}</td>
              <td className="num">{money(row.monto_pendiente)}</td>
              <td>{row.estado}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function TablaGuiasPendientes({ data }: { data: Awaited<ReturnType<typeof reporteGuiasPendientes>> }) {
  if (!data?.length) return <p className="empty-state">No hay guías en esta categoría.</p>;
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>N° Guía</th>
            <th>Fecha</th>
            <th>Agencia</th>
            <th>Estado</th>
            <th className="num">Días transcurridos</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row) => (
            <tr key={row.guia_id}>
              <td>
                <Link href={`/guias/${row.guia_id}`} style={{ color: "var(--blue)", fontWeight: 700 }}>
                  {row.numero_guia}
                </Link>
              </td>
              <td>{row.fecha}</td>
              <td>{row.agencia}</td>
              <td>{row.estado}</td>
              <td className="num">{row.dias_transcurridos}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ResumenGuias({ data }: { data: Awaited<ReturnType<typeof reporteResumenGuias>> }) {
  if (!data) return null;
  return (
    <>
      <div className="stat-grid">
        <div className="stat-card">
          <span>Total de guías</span>
          <strong>{data.total_guias}</strong>
        </div>
        <div className="stat-card">
          <span>Valor total entregado</span>
          <strong>{money(data.valor_total_entregado)}</strong>
        </div>
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Estado</th>
              <th className="num">Cantidad</th>
            </tr>
          </thead>
          <tbody>
            {data.por_estado.map((row) => (
              <tr key={row.estado}>
                <td>{row.estado}</td>
                <td className="num">{row.cantidad}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}

function TablaDesempenoAgencias({ data }: { data: Awaited<ReturnType<typeof reporteDesempenoAgencias>> }) {
  if (!data?.length) return <p className="empty-state">Sin datos.</p>;
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Agencia</th>
            <th>Estado</th>
            <th className="num">Guías</th>
            <th className="num">Vendido</th>
            <th className="num">Cobrado</th>
            <th className="num">Deuda pendiente</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row) => (
            <tr key={row.agencia_id}>
              <td>{row.agencia}</td>
              <td>
                <span className={`badge ${row.estado === "ACTIVO" ? "badge-ok" : "badge-off"}`}>
                  {row.estado === "ACTIVO" ? "Activa" : "Inactiva"}
                </span>
              </td>
              <td className="num">{row.total_guias}</td>
              <td className="num">{money(row.total_vendido)}</td>
              <td className="num">{money(row.total_cobrado)}</td>
              <td className="num">{money(row.deuda_pendiente)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

const RANGOS_ANTIGUEDAD: { label: string; min: number; max: number; color: string }[] = [
  { label: "0-15 días", min: 0, max: 15, color: "var(--ok-fg)" },
  { label: "16-30 días", min: 16, max: 30, color: "var(--warn-fg)" },
  { label: "31-60 días", min: 31, max: 60, color: "#c2410c" },
  { label: "Más de 60 días", min: 61, max: Infinity, color: "var(--off-fg)" },
];

function TablaDeudaPendiente({ data }: { data: Awaited<ReturnType<typeof reporteDeudaPendiente>> }) {
  if (!data) return null;

  const antiguedad = RANGOS_ANTIGUEDAD.map((rango) => ({
    label: rango.label,
    value: data.items
      .filter((item) => item.dias_pendiente >= rango.min && item.dias_pendiente <= rango.max)
      .reduce((acc, item) => acc + item.monto_pendiente, 0),
    color: rango.color,
  }));

  return (
    <>
      <div className="stat-grid">
        <div className="stat-card">
          <span>Total pendiente</span>
          <strong>{money(data.total_pendiente)}</strong>
        </div>
      </div>
      {data.items.length === 0 ? (
        <p className="empty-state">No hay deuda pendiente.</p>
      ) : (
        <>
          <div className="card" style={{ marginBottom: 20 }}>
            <h2 style={{ marginBottom: 16 }}>Antigüedad de la deuda</h2>
            <BarChart data={antiguedad} valueFormatter={money} />
          </div>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Fecha</th>
                  <th>Guía</th>
                  <th>Agencia</th>
                  <th className="num">Días</th>
                  <th className="num">Pendiente</th>
                </tr>
              </thead>
              <tbody>
                {data.items.map((row) => (
                  <tr key={row.cobranza_id}>
                    <td>{row.fecha}</td>
                    <td>
                      <Link href={`/guias/${row.guia_id}`} style={{ color: "var(--blue)", fontWeight: 700 }}>
                        {row.numero_guia}
                      </Link>
                    </td>
                    <td>{row.agencia}</td>
                    <td className="num">
                      <span
                        className={`badge ${row.dias_pendiente > 30 ? "badge-off" : row.dias_pendiente > 15 ? "badge-warn" : "badge-ok"}`}
                      >
                        {row.dias_pendiente}
                      </span>
                    </td>
                    <td className="num">{money(row.monto_pendiente)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </>
  );
}

function TablaPorProducto({ data }: { data: Awaited<ReturnType<typeof reportePorProducto>> }) {
  if (!data?.length) return <p className="empty-state">Sin datos.</p>;
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Código</th>
            <th>Producto</th>
            <th className="num">Entregado</th>
            <th className="num">Vendido</th>
            <th className="num">% Venta</th>
            <th className="num">Ingresos</th>
            <th className="num">Stock actual</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row) => (
            <tr key={row.producto_id}>
              <td>{row.codigo}</td>
              <td>{row.producto}</td>
              <td className="num">{row.cantidad_entregada}</td>
              <td className="num">{row.cantidad_vendida}</td>
              <td className="num">
                <span
                  className={`badge ${row.porcentaje_venta >= 60 ? "badge-ok" : row.porcentaje_venta >= 40 ? "badge-warn" : "badge-off"}`}
                >
                  {row.porcentaje_venta.toFixed(0)}%
                </span>
              </td>
              <td className="num">{money(row.ingresos)}</td>
              <td className="num">{row.stock_actual}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function TablaAgencias({ data }: { data: Awaited<ReturnType<typeof reporteAgencias>> }) {
  if (!data?.length) return <p className="empty-state">Sin datos.</p>;
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Código</th>
            <th>Agencia</th>
            <th>Propietario</th>
            <th>Teléfono</th>
            <th>Estado</th>
            <th className="num">Guías totales</th>
            <th className="num">Guías activas</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row) => (
            <tr key={row.agencia_id}>
              <td>{row.codigo}</td>
              <td>{row.agencia}</td>
              <td>{row.propietario ?? "—"}</td>
              <td>{row.telefono ?? "—"}</td>
              <td>
                <span className={`badge ${row.estado === "ACTIVO" ? "badge-ok" : "badge-off"}`}>
                  {row.estado === "ACTIVO" ? "Activa" : "Inactiva"}
                </span>
              </td>
              <td className="num">{row.total_guias}</td>
              <td className="num">{row.guias_activas}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function TablaKardexInventario({ data }: { data: Awaited<ReturnType<typeof reporteKardexInventario>> }) {
  if (!data?.length) return <p className="empty-state">No hay movimientos en el rango seleccionado.</p>;
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Fecha</th>
            <th>Producto</th>
            <th>Tipo</th>
            <th className="num">Cantidad</th>
            <th>Observación</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row, index) => {
            const esSalida = row.tipo === "SALIDA_GUIA";
            return (
              <tr key={index}>
                <td>{row.fecha}</td>
                <td>
                  <Link href={`/inventario/${row.producto_id}`} style={{ color: "var(--blue)", fontWeight: 700 }}>
                    {row.producto}
                  </Link>
                </td>
                <td>{TIPO_MOVIMIENTO_LABEL[row.tipo as TipoMovimientoInventario] ?? row.tipo}</td>
                <td className="num" style={{ color: esSalida ? "var(--red, #dc2626)" : "var(--green, #16a34a)" }}>
                  {esSalida ? "-" : "+"}
                  {row.cantidad}
                </td>
                <td>{row.observacion ?? "—"}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function TablaRankingAgencias({ data }: { data: Awaited<ReturnType<typeof reporteRankingAgenciasVenta>> }) {
  if (!data?.length) return <p className="empty-state">Sin datos para el rango seleccionado.</p>;
  return (
    <>
      <div className="card" style={{ marginBottom: 20 }}>
        <h2 style={{ marginBottom: 16 }}>% de venta por agencia</h2>
        <BarChart
          data={data.map((row) => ({
            label: row.agencia,
            value: row.porcentaje_venta,
            color: row.porcentaje_venta >= 60 ? "var(--ok-fg)" : row.porcentaje_venta >= 40 ? "var(--warn-fg)" : "var(--off-fg)",
          }))}
          valueFormatter={(v) => `${v.toFixed(0)}%`}
        />
      </div>
      <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Agencia</th>
            <th className="num">Entregadas</th>
            <th className="num">Vendidas</th>
            <th className="num">Devueltas</th>
            <th className="num">% Venta</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row) => (
            <tr key={row.agencia_id}>
              <td>{row.agencia}</td>
              <td className="num">{row.unidades_entregadas}</td>
              <td className="num">{row.unidades_vendidas}</td>
              <td className="num">{row.unidades_devueltas}</td>
              <td className="num">
                <span className={`badge ${row.porcentaje_venta >= 60 ? "badge-ok" : row.porcentaje_venta >= 40 ? "badge-warn" : "badge-off"}`}>
                  {row.porcentaje_venta.toFixed(0)}%
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      </div>
    </>
  );
}

function TablaGuiasPorVencer({ data }: { data: Awaited<ReturnType<typeof reporteGuiasPorVencer>> }) {
  if (!data?.length) return <p className="empty-state">No hay guías en venta actualmente.</p>;
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>N° Guía</th>
            <th>Fecha</th>
            <th>Agencia</th>
            <th className="num">Días transcurridos</th>
            <th className="num">Días restantes</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row) => (
            <tr key={row.guia_id}>
              <td>
                <Link href={`/guias/${row.guia_id}`} style={{ color: "var(--blue)", fontWeight: 700 }}>
                  {row.numero_guia}
                </Link>
              </td>
              <td>{row.fecha}</td>
              <td>{row.agencia}</td>
              <td className="num">{row.dias_transcurridos}</td>
              <td className="num">
                <span className={`badge ${row.dias_restantes <= 0 ? "badge-off" : row.dias_restantes <= 5 ? "badge-warn" : "badge-ok"}`}>
                  {row.dias_restantes}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function GraficoTopAgenciasProductos({ data }: { data: Awaited<ReturnType<typeof reporteTopAgenciasProductos>> }) {
  if (!data?.length) return <p className="empty-state">Sin datos.</p>;
  const top10 = data.slice(0, 10);
  return (
    <div className="card">
      <h2 style={{ marginBottom: 16 }}>Top 10 agencias por variedad de productos</h2>
      <BarChart
        data={top10.map((row) => ({ label: row.agencia, value: row.cantidad_productos }))}
        valueFormatter={(v) => `${v} productos`}
      />
    </div>
  );
}

function diasTranscurridosDesde(fecha: string): number {
  const hoy = new Date();
  const f = new Date(fecha + "T00:00:00");
  return Math.floor((hoy.getTime() - f.getTime()) / 86400000);
}

function TablaDetallePorAgencia({ data }: { data: Awaited<ReturnType<typeof reporteDetallePorAgencia>> }) {
  if (!data || data.grupos.length === 0) {
    return <p className="empty-state">No hay guías entregadas en el rango seleccionado.</p>;
  }

  const lineas = data.grupos.flatMap((grupo) =>
    grupo.detalles.map((d) => ({ ...d, dias: diasTranscurridosDesde(d.fecha) }))
  );

  const enVenta = lineas.filter((l) => l.estado_guia !== "PARCIALMENTE_LIQUIDADA" && l.dias < 25);
  const proximasAVencer = lineas.filter((l) => l.estado_guia !== "PARCIALMENTE_LIQUIDADA" && l.dias >= 25 && l.dias <= 30);
  const vencidas = lineas.filter((l) => l.estado_guia !== "PARCIALMENTE_LIQUIDADA" && l.dias > 30);
  const parcialmenteLiquidadas = lineas.filter((l) => l.estado_guia === "PARCIALMENTE_LIQUIDADA");

  const suma = (arr: typeof lineas) => arr.reduce((acc, l) => acc + l.x_estimado, 0);

  return (
    <>
      <div className="stat-grid">
        <div className="stat-card">
          <span style={{ minHeight: 36 }}>En venta</span>
          <strong style={{ color: "var(--ok-fg)" }}>{money(suma(enVenta))}</strong>
        </div>
        <div className="stat-card">
          <span style={{ minHeight: 36 }}>Próximas a vencer (25-30 días)</span>
          <strong style={{ color: "var(--warn-fg)" }}>{money(suma(proximasAVencer))}</strong>
        </div>
        <div className="stat-card">
          <span style={{ minHeight: 36 }}>Vencidas (+30 días)</span>
          <strong style={{ color: "var(--off-fg)" }}>{money(suma(vencidas))}</strong>
        </div>
        <div className="stat-card">
          <span style={{ minHeight: 36 }}>Parcialmente liquidadas</span>
          <strong style={{ color: "var(--off-fg)" }}>{money(suma(parcialmenteLiquidadas))}</strong>
        </div>
        <div className="stat-card">
          <span style={{ minHeight: 36 }}>Total estimado general</span>
          <strong style={{ color: "var(--blue)" }}>{money(data.total_general)}</strong>
        </div>
      </div>
      {data.grupos.map((grupo) => (
        <div className="card" key={grupo.agencia_id} style={{ marginBottom: 20 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
            <h2>{grupo.agencia}</h2>
            <span style={{ color: "var(--muted)" }}>
              Total entregado: <strong style={{ color: "var(--ink)" }}>{money(grupo.total_entregado)}</strong>
            </span>
          </div>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>N° Guía</th>
                  <th>Fecha</th>
                  <th>Producto</th>
                  <th>Estado</th>
                  <th className="num">Cantidad</th>
                  <th className="num">Precio público</th>
                  <th className="num">Precio agencia</th>
                  <th className="num">50% estimado</th>
                </tr>
              </thead>
              <tbody>
                {grupo.detalles.map((d, index) => (
                  <tr key={`${d.guia_id}-${d.producto_id}-${index}`}>
                    <td>
                      <Link href={`/guias/${d.guia_id}`} style={{ color: "var(--blue)", fontWeight: 700 }}>
                        {d.numero_guia}
                      </Link>
                    </td>
                    <td>{d.fecha}</td>
                    <td>{d.producto}</td>
                    <td>
                      <span
                        className={`badge ${ESTADO_GUIA_BADGE[d.estado_guia as EstadoGuia] ?? "badge-off"}`}
                        title={ESTADO_GUIA_LABEL[d.estado_guia as EstadoGuia] ?? d.estado_guia}
                      >
                        {ESTADO_GUIA_LABEL_CORTO[d.estado_guia as EstadoGuia] ?? d.estado_guia}
                      </span>
                    </td>
                    <td className="num">{d.cantidad}</td>
                    <td className="num">{money(d.precio_publico)}</td>
                    <td className="num">{money(d.precio_agencia)}</td>
                    <td className="num">{money(d.x_estimado)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ))}
    </>
  );
}

function TablaDistribucion({ data }: { data: Awaited<ReturnType<typeof reporteDistribucion>> }) {
  if (!data || data.filas.length === 0 || data.columnas.length === 0) {
    return <p className="empty-state">No hay guías entregadas en el rango seleccionado.</p>;
  }

  const celdaAgenciaBase: React.CSSProperties = {
    position: "sticky",
    left: 0,
    fontWeight: 700,
    background: "var(--blue-light)",
    color: "var(--blue-dark)",
  };

  return (
    <>
      <div className="stat-grid">
        <div className="stat-card">
          <span>Total distribuido</span>
          <strong>{data.total_general}</strong>
        </div>
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th style={celdaAgenciaBase}>Agencia</th>
              {data.columnas.map((col) => (
                <th key={col.producto_id} className="num">
                  {col.producto}
                </th>
              ))}
              <th className="num">Total</th>
            </tr>
          </thead>
          <tbody>
            {data.filas.map((fila) => (
              <tr key={fila.agencia_id}>
                <td style={celdaAgenciaBase}>{fila.agencia}</td>
                {fila.valores.map((valor, index) => (
                  <td key={data.columnas[index].producto_id} className="num">
                    {valor > 0 ? valor : "—"}
                  </td>
                ))}
                <td className="num" style={{ fontWeight: 700 }}>
                  {fila.total}
                </td>
              </tr>
            ))}
          </tbody>
          <tfoot>
            <tr>
              <td style={celdaAgenciaBase}>Total</td>
              {data.columnas.map((col) => (
                <td key={col.producto_id} className="num" style={{ fontWeight: 700 }}>
                  {col.total}
                </td>
              ))}
              <td className="num" style={{ fontWeight: 700 }}>
                {data.total_general}
              </td>
            </tr>
          </tfoot>
        </table>
      </div>
    </>
  );
}

function ResumenPeriodo({ data }: { data: Awaited<ReturnType<typeof reporteResumenPeriodo>> }) {
  if (!data) return null;
  return (
    <div className="stat-grid">
      <div className="stat-card">
        <span>Guías emitidas</span>
        <strong>{data.guias_emitidas}</strong>
      </div>
      <div className="stat-card">
        <span>Valor entregado</span>
        <strong>{money(data.valor_entregado)}</strong>
      </div>
      <div className="stat-card">
        <span>Total liquidado</span>
        <strong>{money(data.total_liquidado)}</strong>
      </div>
      <div className="stat-card">
        <span>Total cobrado</span>
        <strong>{money(data.total_cobrado)}</strong>
      </div>
      <div className="stat-card">
        <span>Total pendiente</span>
        <strong>{money(data.total_pendiente)}</strong>
      </div>
    </div>
  );
}
