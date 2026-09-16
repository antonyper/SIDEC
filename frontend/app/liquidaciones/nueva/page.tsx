"use client";

import { Suspense, useEffect, useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import PageHeader from "@/components/ui/PageHeader";
import { ApiError } from "@/lib/http";
import {
  crearLiquidacion,
  obtenerGuiaParaLiquidar,
  type DetalleLiquidacionInput,
  type GuiaParaLiquidar,
} from "@/lib/liquidaciones";
import { listarGuias, type Guia } from "@/lib/guias";

function hoy(): string {
  return new Date().toISOString().slice(0, 10);
}

export default function NuevaLiquidacionPage() {
  return (
    <Suspense fallback={<p className="empty-state">Cargando…</p>}>
      <NuevaLiquidacionForm />
    </Suspense>
  );
}

function NuevaLiquidacionForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const guiaIdInicial = searchParams.get("guia_id") ?? "";

  const [guiasDisponibles, setGuiasDisponibles] = useState<Guia[]>([]);
  const [guiaId, setGuiaId] = useState(guiaIdInicial);
  const [guiaInfo, setGuiaInfo] = useState<GuiaParaLiquidar | null>(null);
  const [devoluciones, setDevoluciones] = useState<Record<number, string>>({});
  const [precios, setPrecios] = useState<Record<number, string>>({});
  const [excluidos, setExcluidos] = useState<Set<number>>(new Set());
  const [fecha, setFecha] = useState(hoy());
  const [observacion, setObservacion] = useState("");
  const [pagoACuenta, setPagoACuenta] = useState("");
  const [cargandoGuia, setCargandoGuia] = useState(false);
  const [error, setError] = useState("");
  const [guardando, setGuardando] = useState(false);

  useEffect(() => {
    listarGuias()
      .then((guias) =>
        setGuiasDisponibles(
          guias.filter(
            (g) =>
              g.estado === "EN_VENTA" ||
              g.estado === "PENDIENTE_LIQUIDACION" ||
              g.estado === "PARCIALMENTE_LIQUIDADA"
          )
        )
      )
      .catch(() => {});
  }, []);

  useEffect(() => {
    /* eslint-disable react-hooks/set-state-in-effect -- sincroniza el detalle con la guía seleccionada */
    if (!guiaId) {
      setGuiaInfo(null);
      return;
    }
    setCargandoGuia(true);
    setError("");
    obtenerGuiaParaLiquidar(Number(guiaId))
      .then((info) => {
        setGuiaInfo(info);
        setDevoluciones(Object.fromEntries(info.detalles.map((d) => [d.detalle_guia_id, "0"])));
        setPrecios(Object.fromEntries(info.detalles.map((d) => [d.detalle_guia_id, String(d.precio_a_liquidar)])));
        setExcluidos(new Set());
      })
      .catch((err) => {
        setGuiaInfo(null);
        setError(err instanceof ApiError ? err.message : "No se pudo cargar la guía seleccionada.");
      })
      .finally(() => setCargandoGuia(false));
    /* eslint-enable react-hooks/set-state-in-effect */
  }, [guiaId]);

  const detallesIncluidos = useMemo(
    () => (guiaInfo ? guiaInfo.detalles.filter((d) => !excluidos.has(d.detalle_guia_id)) : []),
    [guiaInfo, excluidos]
  );

  const resumen = useMemo(() => {
    const filas = detallesIncluidos.map((d) => {
      const devuelta = Number(devoluciones[d.detalle_guia_id] || 0);
      const vendida = Math.max(d.cantidad - devuelta, 0);
      const precioUnitario = Number(precios[d.detalle_guia_id] ?? d.precio_a_liquidar);
      const subtotal = vendida * precioUnitario;
      return { detalle_guia_id: d.detalle_guia_id, producto: d.producto, vendida, total: subtotal };
    });
    const total = filas.reduce((acc, fila) => acc + fila.total, 0);
    return { total, filas };
  }, [detallesIncluidos, devoluciones, precios]);

  function quitarLinea(detalleGuiaId: number) {
    setExcluidos((prev) => new Set(prev).add(detalleGuiaId));
  }

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError("");
    if (!guiaInfo) {
      setError("Selecciona una guía para liquidar.");
      return;
    }

    if (detallesIncluidos.length === 0) {
      setError("Selecciona al menos un producto para liquidar.");
      return;
    }

    const detalles: DetalleLiquidacionInput[] = detallesIncluidos.map((d) => ({
      detalle_guia_id: d.detalle_guia_id,
      cantidad_devuelta: Number(devoluciones[d.detalle_guia_id] || 0),
      precio_a_liquidar: Number(precios[d.detalle_guia_id] ?? d.precio_a_liquidar),
    }));

    setGuardando(true);
    try {
      const liquidacion = await crearLiquidacion({
        fecha,
        guia_id: guiaInfo.guia_id,
        observacion: observacion || undefined,
        detalles,
        pago_a_cuenta: pagoACuenta ? Number(pagoACuenta) : undefined,
      });
      router.push(`/liquidaciones/${liquidacion.id}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo crear la liquidación.");
      setGuardando(false);
    }
  }

  return (
    <>
      <PageHeader title="Nueva liquidación" subtitle="Liquidaciones" />
      <div className="page">
        <div className="card">
          {error && <p className="error-banner">{error}</p>}
          <form onSubmit={handleSubmit}>
            <div className="form-grid cols-2" style={{ marginBottom: 24 }}>
              <label className="field">
                Guía a liquidar *
                <select className="input" value={guiaId} onChange={(e) => setGuiaId(e.target.value)} required>
                  <option value="">Selecciona una guía</option>
                  {guiasDisponibles.map((g) => (
                    <option key={g.id} value={g.id}>
                      {g.numero_guia} — {g.fecha}
                    </option>
                  ))}
                </select>
              </label>
              <label className="field">
                Fecha *
                <input className="input" type="date" value={fecha} onChange={(e) => setFecha(e.target.value)} required />
              </label>
              <label className="field" style={{ gridColumn: "1 / -1" }}>
                Observación
                <textarea className="input" value={observacion} onChange={(e) => setObservacion(e.target.value)} />
              </label>
            </div>

            {cargandoGuia && <p className="empty-state">Cargando productos de la guía…</p>}

            {guiaInfo && (
              <>
                <p style={{ marginBottom: 8, color: "var(--muted)" }}>
                  Agencia: <strong style={{ color: "var(--ink)" }}>{guiaInfo.agencia}</strong>
                </p>
                {detallesIncluidos.length === 0 ? (
                  <p className="empty-state">Quitaste todos los productos. Agrega al menos uno para continuar.</p>
                ) : (
                  <div className="table-wrap" style={{ marginBottom: 16 }}>
                    <table>
                      <thead>
                        <tr>
                          <th>Producto</th>
                          <th className="num">Entregado</th>
                          <th style={{ textAlign: "center" }}>Devoluciones</th>
                          <th className="num">Vendido</th>
                          <th className="num">% Venta</th>
                          <th className="num">Precio a liquidar</th>
                          <th className="num">Subtotal</th>
                          <th></th>
                        </tr>
                      </thead>
                      <tbody>
                        {detallesIncluidos.map((d) => {
                          const fila = resumen.filas.find((f) => f.detalle_guia_id === d.detalle_guia_id);
                          return (
                            <tr key={d.detalle_guia_id}>
                              <td>{d.producto}</td>
                              <td className="num">{d.cantidad}</td>
                              <td style={{ textAlign: "center" }}>
                                <input
                                  className="input"
                                  type="number"
                                  min="0"
                                  max={d.cantidad}
                                  style={{ textAlign: "center", width: "100%", minHeight: 38 }}
                                  value={devoluciones[d.detalle_guia_id] ?? "0"}
                                  onChange={(e) =>
                                    setDevoluciones((prev) => ({ ...prev, [d.detalle_guia_id]: e.target.value }))
                                  }
                                />
                              </td>
                              <td className="num">{fila?.vendida ?? 0}</td>
                              <td className="num">
                                {d.cantidad > 0 ? `${(((fila?.vendida ?? 0) / d.cantidad) * 100).toFixed(0)}%` : "—"}
                              </td>
                              <td>
                                <input
                                  className="input"
                                  type="number"
                                  step="0.01"
                                  min="0"
                                  style={{ textAlign: "right", width: "100%", minHeight: 38 }}
                                  value={precios[d.detalle_guia_id] ?? String(d.precio_a_liquidar)}
                                  onChange={(e) =>
                                    setPrecios((prev) => ({ ...prev, [d.detalle_guia_id]: e.target.value }))
                                  }
                                />
                              </td>
                              <td className="num">S/ {(fila?.total ?? 0).toFixed(2)}</td>
                              <td>
                                <button
                                  type="button"
                                  className="btn btn-danger btn-sm"
                                  onClick={() => quitarLinea(d.detalle_guia_id)}
                                >
                                  Quitar
                                </button>
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                )}

                <div className="stat-grid">
                  <div className="stat-card">
                    <span>Total a cobrar</span>
                    <strong>S/ {resumen.total.toFixed(2)}</strong>
                  </div>
                  <div className="stat-card">
                    <span>Pago a cuenta (opcional)</span>
                    <input
                      className="input"
                      type="number"
                      step="0.01"
                      min="0"
                      max={resumen.total}
                      placeholder="Dejar vacío si se cobra todo"
                      value={pagoACuenta}
                      onChange={(e) => setPagoACuenta(e.target.value)}
                    />
                  </div>
                </div>
              </>
            )}

            <div className="form-actions" style={{ marginTop: 24 }}>
              <button type="button" className="btn btn-secondary" onClick={() => router.push("/liquidaciones")}>
                Cancelar
              </button>
              <button type="submit" className="btn" disabled={guardando || !guiaInfo || detallesIncluidos.length === 0}>
                {guardando ? "Guardando…" : "Crear liquidación"}
              </button>
            </div>
          </form>
        </div>
      </div>
    </>
  );
}
