"use client";

import { use, useEffect, useState } from "react";
import Link from "next/link";
import PageHeader from "@/components/ui/PageHeader";
import Modal from "@/components/ui/Modal";
import { ApiError } from "@/lib/http";
import {
  actualizarMovimiento,
  listarMovimientosPorProducto,
  registrarMovimiento,
  TIPO_MOVIMIENTO_LABEL,
  TIPO_MOVIMIENTO_SIGNO,
  type MovimientoInventario,
  type TipoMovimientoInventario,
} from "@/lib/inventario";
import { obtenerProducto, type Producto } from "@/lib/productos";

function hoy(): string {
  return new Date().toISOString().slice(0, 10);
}

export default function InventarioMovimientosPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);

  const [producto, setProducto] = useState<Producto | null>(null);
  const [movimientos, setMovimientos] = useState<MovimientoInventario[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  const [editando, setEditando] = useState<MovimientoInventario | null>(null);
  const [creando, setCreando] = useState(false);
  const [tipo, setTipo] = useState<TipoMovimientoInventario>("INGRESO");
  const [cantidad, setCantidad] = useState("");
  const [fecha, setFecha] = useState("");
  const [observacion, setObservacion] = useState("");
  const [guardando, setGuardando] = useState(false);
  const [errorModal, setErrorModal] = useState("");

  async function cargar() {
    setCargando(true);
    setError("");
    try {
      const [p, movs] = await Promise.all([
        obtenerProducto(Number(id)),
        listarMovimientosPorProducto(Number(id)),
      ]);
      setProducto(p);
      setMovimientos(movs);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo cargar el registro de movimientos.");
    } finally {
      setCargando(false);
    }
  }

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- carga inicial de datos desde la API
    cargar();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  function abrirEdicion(m: MovimientoInventario) {
    setEditando(m);
    setCreando(false);
    setTipo(m.tipo);
    setCantidad(String(m.cantidad));
    setFecha(m.fecha);
    setObservacion(m.observacion ?? "");
    setErrorModal("");
  }

  function abrirCreacion() {
    setEditando(null);
    setCreando(true);
    setTipo("INGRESO");
    setCantidad("");
    setFecha(hoy());
    setObservacion("");
    setErrorModal("");
  }

  function cerrarModal() {
    setEditando(null);
    setCreando(false);
  }

  async function guardarMovimiento(event: React.FormEvent) {
    event.preventDefault();
    setErrorModal("");
    setGuardando(true);
    try {
      if (editando) {
        await actualizarMovimiento(editando.id, {
          tipo,
          cantidad: Number(cantidad),
          fecha,
          observacion: observacion || undefined,
        });
      } else {
        await registrarMovimiento({
          producto_id: Number(id),
          tipo,
          cantidad: Number(cantidad),
          fecha,
          observacion: observacion || undefined,
        });
      }
      cerrarModal();
      await cargar();
    } catch (err) {
      setErrorModal(
        err instanceof ApiError ? err.message : "No se pudo guardar el movimiento."
      );
    } finally {
      setGuardando(false);
    }
  }

  return (
    <>
      <PageHeader
        title={producto ? `Movimientos — ${producto.nombre}` : "Movimientos"}
        subtitle="Inventario"
        actions={
          <>
            <Link href="/inventario" className="btn btn-secondary">
              Volver
            </Link>
            {producto && (
              <button type="button" className="btn" onClick={abrirCreacion}>
                + Registrar movimiento
              </button>
            )}
          </>
        }
      />
      <div className="page">
        {error && <p className="error-banner">{error}</p>}
        {cargando ? (
          <p className="empty-state">Cargando…</p>
        ) : !producto ? (
          <p className="empty-state">No se encontró el producto.</p>
        ) : movimientos.length === 0 ? (
          <p className="empty-state">Este producto no tiene movimientos registrados.</p>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Fecha</th>
                  <th>Tipo</th>
                  <th className="num">Cantidad</th>
                  <th>Observación</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {movimientos.map((m) => {
                  const signo = TIPO_MOVIMIENTO_SIGNO[m.tipo];
                  return (
                    <tr key={m.id}>
                      <td>{m.fecha}</td>
                      <td>{TIPO_MOVIMIENTO_LABEL[m.tipo]}</td>
                      <td className="num" style={{ color: signo > 0 ? "var(--green, #16a34a)" : "var(--red, #dc2626)" }}>
                        {signo > 0 ? "+" : "-"}
                        {m.cantidad}
                      </td>
                      <td>{m.observacion ?? "—"}</td>
                      <td className="row-actions">
                        {m.editable ? (
                          <button type="button" className="btn btn-secondary btn-sm" onClick={() => abrirEdicion(m)}>
                            Editar
                          </button>
                        ) : (
                          <span style={{ color: "var(--muted)" }}>Automático</span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <Modal
        open={editando !== null || creando}
        title={editando ? "Editar movimiento" : `Registrar movimiento — ${producto?.nombre ?? ""}`}
        onClose={cerrarModal}
      >
        {errorModal && <p className="error-banner">{errorModal}</p>}
        <form onSubmit={guardarMovimiento}>
          <div className="form-grid" style={{ marginBottom: 16 }}>
            <label className="field">
              Tipo de movimiento *
              <select className="input" value={tipo} onChange={(e) => setTipo(e.target.value as TipoMovimientoInventario)}>
                <option value="INGRESO">Ingreso</option>
                <option value="STOCK_INICIAL">Stock inicial</option>
              </select>
            </label>
            <label className="field">
              Cantidad *
              <input
                className="input"
                type="number"
                min="1"
                value={cantidad}
                onChange={(e) => setCantidad(e.target.value)}
                required
              />
            </label>
            <label className="field">
              Fecha *
              <input className="input" type="date" value={fecha} onChange={(e) => setFecha(e.target.value)} required />
            </label>
            <label className="field">
              Observación
              <textarea className="input" value={observacion} onChange={(e) => setObservacion(e.target.value)} />
            </label>
          </div>
          <div className="modal-actions">
            <button type="button" className="btn btn-secondary" onClick={cerrarModal}>
              Cancelar
            </button>
            <button type="submit" className="btn" disabled={guardando}>
              {guardando ? "Guardando…" : "Guardar"}
            </button>
          </div>
        </form>
      </Modal>
    </>
  );
}
