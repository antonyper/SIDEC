"use client";

import { use, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import PageHeader from "@/components/ui/PageHeader";
import ConfirmDialog from "@/components/ui/ConfirmDialog";
import { ApiError } from "@/lib/http";
import {
  actualizarGuia,
  anularGuia,
  ESTADO_GUIA_BADGE,
  ESTADO_GUIA_LABEL,
  obtenerGuia,
  type DetalleGuiaUpdateInput,
  type Guia,
} from "@/lib/guias";
import { obtenerAgencia, type Agencia } from "@/lib/agencias";
import { listarProductos, type ProductoListItem } from "@/lib/productos";

type LineaForm = {
  detalle_guia_id?: number;
  producto_id: string;
  cantidad: string;
  precio: string;
  porcentaje_cobro: string;
};

export default function GuiaDetallePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const router = useRouter();

  const [guia, setGuia] = useState<Guia | null>(null);
  const [agencia, setAgencia] = useState<Agencia | null>(null);
  const [productos, setProductos] = useState<ProductoListItem[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");
  const [confirmarAnular, setConfirmarAnular] = useState(false);

  const [editando, setEditando] = useState(false);
  const [fecha, setFecha] = useState("");
  const [observacion, setObservacion] = useState("");
  const [lineas, setLineas] = useState<LineaForm[]>([]);
  const [guardando, setGuardando] = useState(false);

  async function cargar() {
    setCargando(true);
    setError("");
    try {
      const g = await obtenerGuia(Number(id));
      setGuia(g);
      const [a, prods] = await Promise.all([obtenerAgencia(g.agencia_id), listarProductos()]);
      setAgencia(a);
      setProductos(prods);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo cargar la guía.");
    } finally {
      setCargando(false);
    }
  }

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- carga inicial de datos desde la API
    cargar();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  const nombreProducto = (productoId: number) =>
    productos.find((p) => p.id === productoId)?.nombre ?? `Producto #${productoId}`;

  async function confirmarAnulacion() {
    setConfirmarAnular(false);
    if (!guia) return;
    try {
      await anularGuia(guia.id);
      await cargar();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo anular la guía.");
    }
  }

  function abrirEdicion() {
    if (!guia) return;
    setFecha(guia.fecha);
    setObservacion(guia.observacion ?? "");
    setLineas(
      guia.detalles.map((d) => ({
        detalle_guia_id: d.id,
        producto_id: String(d.producto_id),
        cantidad: String(d.cantidad),
        precio: d.precio != null ? String(d.precio) : "",
        porcentaje_cobro: d.porcentaje_cobro != null ? String(d.porcentaje_cobro) : "",
      }))
    );
    setError("");
    setEditando(true);
  }

  function actualizarLinea(index: number, cambios: Partial<LineaForm>) {
    setLineas((prev) => prev.map((linea, i) => (i === index ? { ...linea, ...cambios } : linea)));
  }

  function seleccionarProducto(index: number, productoId: string) {
    const producto = productos.find((p) => String(p.id) === productoId);
    actualizarLinea(index, {
      producto_id: productoId,
      precio: producto?.precio != null ? String(producto.precio) : "",
    });
  }

  function agregarLinea() {
    setLineas((prev) => [...prev, { producto_id: "", cantidad: "1", precio: "", porcentaje_cobro: "" }]);
  }

  function quitarLinea(index: number) {
    setLineas((prev) => prev.filter((_, i) => i !== index));
  }

  async function handleGuardar(event: React.FormEvent) {
    event.preventDefault();
    if (!guia) return;
    setError("");

    if (lineas.length === 0) {
      setError("La guía debe tener al menos un producto.");
      return;
    }

    const detalles: DetalleGuiaUpdateInput[] = [];
    for (const linea of lineas) {
      if (!linea.producto_id || !linea.cantidad || !linea.precio || linea.porcentaje_cobro === "") {
        setError("Completa producto, cantidad, precio y porcentaje de cobro en cada línea.");
        return;
      }
      detalles.push({
        detalle_guia_id: linea.detalle_guia_id,
        producto_id: Number(linea.producto_id),
        cantidad: Number(linea.cantidad),
        precio: Number(linea.precio),
        porcentaje_cobro: Number(linea.porcentaje_cobro),
      });
    }

    setGuardando(true);
    try {
      await actualizarGuia(guia.id, {
        fecha,
        observacion: observacion || undefined,
        detalles,
      });
      setEditando(false);
      await cargar();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo guardar la guía.");
    } finally {
      setGuardando(false);
    }
  }

  const puedeLiquidar =
    guia?.estado === "EN_VENTA" ||
    guia?.estado === "PENDIENTE_LIQUIDACION" ||
    guia?.estado === "PARCIALMENTE_LIQUIDADA";
  const puedeAnular = guia && guia.estado !== "LIQUIDADA" && guia.estado !== "PARCIALMENTE_LIQUIDADA" && guia.estado !== "ANULADA";
  const puedeEditar = guia && guia.estado !== "ANULADA";

  if (guia && editando) {
    return (
      <>
        <PageHeader title={`Editar guía ${guia.numero_guia}`} subtitle="Guías" />
        <div className="page">
          <div className="card">
            {error && <p className="error-banner">{error}</p>}
            <form onSubmit={handleGuardar}>
              <div style={{ maxWidth: 920, margin: "0 auto" }}>
              <div className="form-grid cols-2" style={{ marginBottom: 24, maxWidth: "none" }}>
                <label className="field">
                  Fecha *
                  <input className="input" type="date" value={fecha} onChange={(e) => setFecha(e.target.value)} required />
                </label>
                <label className="field" style={{ gridColumn: "1 / -1" }}>
                  Observación
                  <textarea className="input" value={observacion} onChange={(e) => setObservacion(e.target.value)} />
                </label>
              </div>

              <h2 style={{ marginBottom: 12 }}>Productos entregados</h2>
                <div className="table-wrap" style={{ marginBottom: 12 }}>
                  <table className="lineas-table" style={{ tableLayout: "fixed", width: "100%" }}>
                    <thead>
                      <tr>
                        <th style={{ width: 260 }}>Producto</th>
                        <th className="num" style={{ width: 90 }}>
                          Cantidad
                        </th>
                        <th className="num" style={{ width: 105 }}>
                          Precio público
                        </th>
                        <th className="num" style={{ width: 140 }}>
                          % Cobro agencia
                        </th>
                        <th className="num" style={{ width: 130 }}>
                          Precio agencia
                        </th>
                        <th style={{ width: 90 }}></th>
                      </tr>
                    </thead>
                    <tbody>
                      {lineas.map((linea, index) => {
                        const precioAgencia =
                          linea.precio && linea.porcentaje_cobro
                            ? (Number(linea.precio) * Number(linea.porcentaje_cobro)) / 100
                            : null;
                        return (
                          <tr key={index}>
                            <td>
                              <select
                                className="input"
                                value={linea.producto_id}
                                onChange={(e) => seleccionarProducto(index, e.target.value)}
                                required
                              >
                                <option value="">Selecciona…</option>
                                {productos.map((p) => (
                                  <option key={p.id} value={p.id}>
                                    {p.nombre}
                                  </option>
                                ))}
                              </select>
                            </td>
                            <td>
                              <input
                                className="input"
                                type="number"
                                min="1"
                                value={linea.cantidad}
                                onChange={(e) => actualizarLinea(index, { cantidad: e.target.value })}
                                required
                              />
                            </td>
                            <td>
                              <input
                                className="input"
                                type="number"
                                step="0.01"
                                min="0"
                                value={linea.precio}
                                onChange={(e) => actualizarLinea(index, { precio: e.target.value })}
                                required
                              />
                            </td>
                            <td>
                              <input
                                className="input"
                                type="number"
                                step="0.01"
                                min="0"
                                max="100"
                                placeholder="entre 0 y 100"
                                value={linea.porcentaje_cobro}
                                onChange={(e) => actualizarLinea(index, { porcentaje_cobro: e.target.value })}
                                required
                              />
                            </td>
                            <td className="num">{precioAgencia != null ? `S/ ${precioAgencia.toFixed(2)}` : "—"}</td>
                            <td>
                              {lineas.length > 1 && (
                                <button
                                  type="button"
                                  className="btn btn-danger btn-sm"
                                  onClick={() => quitarLinea(index)}
                                >
                                  Quitar
                                </button>
                              )}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
                <button type="button" className="btn btn-secondary btn-sm" onClick={agregarLinea}>
                  + Agregar producto
                </button>
              </div>

              <div className="form-actions" style={{ marginTop: 24 }}>
                <button type="button" className="btn btn-secondary" onClick={() => setEditando(false)}>
                  Cancelar
                </button>
                <button type="submit" className="btn" disabled={guardando}>
                  {guardando ? "Guardando…" : "Guardar cambios"}
                </button>
              </div>
            </form>
          </div>
        </div>
      </>
    );
  }

  return (
    <>
      <PageHeader
        title={guia ? `Guía ${guia.numero_guia}` : "Guía"}
        subtitle="Guías"
        actions={
          <>
            <button type="button" className="btn btn-secondary" onClick={() => router.back()}>
              Volver
            </button>
            {guia && (
              <button type="button" className="btn btn-secondary" onClick={() => window.print()}>
                Imprimir
              </button>
            )}
            {puedeEditar && (
              <button type="button" className="btn btn-secondary" onClick={abrirEdicion}>
                Editar
              </button>
            )}
            {puedeLiquidar && (
              <Link href={`/liquidaciones/nueva?guia_id=${id}`} className="btn">
                Liquidar
              </Link>
            )}
            {puedeAnular && (
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
        ) : !guia ? (
          <p className="empty-state">No se encontró la guía.</p>
        ) : (
          <>
            <div className="stat-grid">
              <div className="stat-card">
                <span>Fecha</span>
                <strong>{guia.fecha}</strong>
              </div>
              <div className="stat-card">
                <span>Agencia</span>
                <strong>{agencia?.nombre ?? "—"}</strong>
              </div>
              <div className="stat-card">
                <span>Estado</span>
                <span className={`badge ${ESTADO_GUIA_BADGE[guia.estado]}`}>{ESTADO_GUIA_LABEL[guia.estado]}</span>
              </div>
            </div>

            {guia.observacion && (
              <div className="card" style={{ marginBottom: 20 }}>
                <strong>Observación</strong>
                <p style={{ marginTop: 6 }}>{guia.observacion}</p>
              </div>
            )}

            <h2 style={{ marginBottom: 12 }}>Productos entregados</h2>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Producto</th>
                    <th className="num">Cantidad</th>
                    <th className="num">Precio público</th>
                    <th className="num">% Cobro agencia</th>
                    <th className="num">Precio agencia</th>
                    <th>Liquidado en</th>
                  </tr>
                </thead>
                <tbody>
                  {guia.detalles.map((d) => {
                    const precioAgencia =
                      d.precio != null && d.porcentaje_cobro != null ? (d.precio * d.porcentaje_cobro) / 100 : null;
                    return (
                      <tr key={d.id}>
                        <td>{nombreProducto(d.producto_id)}</td>
                        <td className="num">{d.cantidad}</td>
                        <td className="num">{d.precio != null ? `S/ ${d.precio.toFixed(2)}` : "—"}</td>
                        <td className="num">{d.porcentaje_cobro != null ? `${d.porcentaje_cobro}%` : "—"}</td>
                        <td className="num">{precioAgencia != null ? `S/ ${precioAgencia.toFixed(2)}` : "—"}</td>
                        <td>
                          {d.liquidaciones_activas.length === 0 ? (
                            "—"
                          ) : (
                            d.liquidaciones_activas.map((l) => (
                              <div key={l.liquidacion_id}>
                                <Link href={`/liquidaciones/${l.liquidacion_id}`} style={{ color: "var(--blue)" }}>
                                  Liquidación #{l.liquidacion_id}
                                </Link>{" "}
                                ({l.fecha_liquidacion})
                              </div>
                            ))
                          )}
                        </td>
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
        title={`¿Anular la guía ${guia?.numero_guia}?`}
        description="Esta acción no se puede deshacer."
        confirmLabel="Anular guía"
        danger
        onConfirm={confirmarAnulacion}
        onCancel={() => setConfirmarAnular(false)}
      />
    </>
  );
}
