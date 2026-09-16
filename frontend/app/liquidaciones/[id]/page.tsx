"use client";

import { use, useEffect, useState } from "react";
import Link from "next/link";
import PageHeader from "@/components/ui/PageHeader";
import ConfirmDialog from "@/components/ui/ConfirmDialog";
import { ApiError } from "@/lib/http";
import {
  anularLiquidacion,
  ESTADO_LIQUIDACION_BADGE,
  ESTADO_LIQUIDACION_LABEL,
  obtenerLiquidacion,
  type Liquidacion,
} from "@/lib/liquidaciones";
import {
  obtenerCobranzaPorLiquidacion,
  ESTADO_COBRANZA_BADGE,
  ESTADO_COBRANZA_LABEL,
  type Cobranza,
} from "@/lib/cobranzas";
import { obtenerGuia, type DetalleGuia } from "@/lib/guias";
import { listarProductos, type ProductoListItem } from "@/lib/productos";

export default function LiquidacionDetallePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);

  const [liquidacion, setLiquidacion] = useState<Liquidacion | null>(null);
  const [cobranza, setCobranza] = useState<Cobranza | null>(null);
  const [detallesGuia, setDetallesGuia] = useState<Record<number, DetalleGuia>>({});
  const [productos, setProductos] = useState<ProductoListItem[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");
  const [confirmarAnular, setConfirmarAnular] = useState(false);

  async function cargar() {
    setCargando(true);
    setError("");
    try {
      const l = await obtenerLiquidacion(Number(id));
      setLiquidacion(l);
      try {
        setCobranza(await obtenerCobranzaPorLiquidacion(l.id));
      } catch {
        setCobranza(null);
      }
      const [guia, prods] = await Promise.all([obtenerGuia(l.guia_id), listarProductos()]);
      setDetallesGuia(Object.fromEntries(guia.detalles.map((d) => [d.id, d])));
      setProductos(prods);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo cargar la liquidación.");
    } finally {
      setCargando(false);
    }
  }

  function nombreProducto(detalleGuiaId: number) {
    const productoId = detallesGuia[detalleGuiaId]?.producto_id;
    return productos.find((p) => p.id === productoId)?.nombre ?? "—";
  }

  function precioAgencia(detalleGuiaId: number) {
    const detalle = detallesGuia[detalleGuiaId];
    if (!detalle || detalle.precio == null || detalle.porcentaje_cobro == null) return null;
    return (detalle.precio * detalle.porcentaje_cobro) / 100;
  }

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- carga inicial de datos desde la API
    cargar();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  async function confirmarAnulacion() {
    setConfirmarAnular(false);
    if (!liquidacion) return;
    try {
      await anularLiquidacion(liquidacion.id);
      await cargar();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo anular la liquidación.");
    }
  }

  return (
    <>
      <PageHeader
        title={liquidacion ? `Liquidación #${liquidacion.id}` : "Liquidación"}
        subtitle="Liquidaciones"
        actions={
          <>
            <Link href="/liquidaciones" className="btn btn-secondary">
              Volver
            </Link>
            {liquidacion && (
              <button type="button" className="btn btn-secondary" onClick={() => window.print()}>
                Imprimir
              </button>
            )}
            {liquidacion?.estado === "LIQUIDADO" && (
              <button type="button" className="btn btn-danger" onClick={() => setConfirmarAnular(true)}>
                Anular
              </button>
            )}
          </>
        }
      />
      <div className="page">
        {error && <p className="error-banner">{error}</p>}
        {cargando ? (
          <p className="empty-state">Cargando…</p>
        ) : !liquidacion ? (
          <p className="empty-state">No se encontró la liquidación.</p>
        ) : (
          <>
            <div className="stat-grid">
              <div className="stat-card">
                <span>Fecha</span>
                <strong>{liquidacion.fecha}</strong>
              </div>
              <div className="stat-card">
                <span>Guía</span>
                <Link href={`/guias/${liquidacion.guia_id}`} style={{ color: "var(--blue)" }}>
                  <strong>Ver guía #{liquidacion.guia_id}</strong>
                </Link>
              </div>
              <div className="stat-card">
                <span>Estado</span>
                <span className={`badge ${ESTADO_LIQUIDACION_BADGE[liquidacion.estado]}`}>
                  {ESTADO_LIQUIDACION_LABEL[liquidacion.estado]}
                </span>
              </div>
              {cobranza && (
                <div className="stat-card">
                  <span>Cobranza</span>
                  <span className={`badge ${ESTADO_COBRANZA_BADGE[cobranza.estado]}`}>
                    {ESTADO_COBRANZA_LABEL[cobranza.estado]}
                  </span>
                </div>
              )}
            </div>

            {cobranza && (
              <div className="card" style={{ marginBottom: 20 }}>
                <h2 style={{ marginBottom: 14 }}>Cobranza</h2>
                <div className="stat-grid" style={{ marginBottom: 0 }}>
                  <div className="stat-card">
                    <span>Monto total</span>
                    <strong>S/ {cobranza.monto.toFixed(2)}</strong>
                  </div>
                  <div className="stat-card">
                    <span>{cobranza.monto_pendiente > 0 ? "A cuenta" : "Pagado"}</span>
                    <strong>S/ {cobranza.monto_pagado.toFixed(2)}</strong>
                  </div>
                  <div className="stat-card">
                    <span>{cobranza.monto_pendiente > 0 ? "Saldo pendiente" : "Pendiente"}</span>
                    <strong>S/ {cobranza.monto_pendiente.toFixed(2)}</strong>
                  </div>
                </div>
                <div style={{ marginTop: 16 }}>
                  <Link href="/cobranzas" className="btn btn-secondary btn-sm">
                    Gestionar en Cobranzas
                  </Link>
                </div>
              </div>
            )}

            {liquidacion.observacion && (
              <div className="card" style={{ marginBottom: 20 }}>
                <strong>Observación</strong>
                <p style={{ marginTop: 6 }}>{liquidacion.observacion}</p>
              </div>
            )}

            <h2 style={{ marginBottom: 12 }}>Detalle</h2>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Producto</th>
                    <th className="num">Precio público</th>
                    <th className="num">Precio agencia</th>
                    <th className="num">Vendido</th>
                    <th className="num">Devoluciones</th>
                    <th className="num">% Venta</th>
                    <th className="num">Total</th>
                  </tr>
                </thead>
                <tbody>
                  {liquidacion.detalles.map((d) => {
                    const precioPublico = detallesGuia[d.detalle_guia_id]?.precio ?? null;
                    const precio = precioAgencia(d.detalle_guia_id);
                    const entregado = d.cantidad_vendida + d.cantidad_devuelta;
                    const porcentajeVenta = entregado > 0 ? (d.cantidad_vendida / entregado) * 100 : null;
                    return (
                      <tr key={d.id}>
                        <td>{nombreProducto(d.detalle_guia_id)}</td>
                        <td className="num">{precioPublico != null ? `S/ ${precioPublico.toFixed(2)}` : "—"}</td>
                        <td className="num">{precio != null ? `S/ ${precio.toFixed(2)}` : "—"}</td>
                        <td className="num">{d.cantidad_vendida}</td>
                        <td className="num">{d.cantidad_devuelta}</td>
                        <td className="num">{porcentajeVenta != null ? `${porcentajeVenta.toFixed(0)}%` : "—"}</td>
                        <td className="num">S/ {d.total.toFixed(2)}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </>
        )}
      </div>

      <ConfirmDialog
        open={confirmarAnular}
        title={`¿Anular la liquidación #${liquidacion?.id}?`}
        description="También se anulará la cobranza asociada. Esta acción no se puede deshacer."
        confirmLabel="Anular liquidación"
        danger
        onConfirm={confirmarAnulacion}
        onCancel={() => setConfirmarAnular(false)}
      />
    </>
  );
}
