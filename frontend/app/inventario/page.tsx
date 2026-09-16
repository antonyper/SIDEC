"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import PageHeader from "@/components/ui/PageHeader";
import Modal from "@/components/ui/Modal";
import { ApiError } from "@/lib/http";
import { listarInventario, registrarMovimiento, type InventarioItem, type TipoMovimientoInventario } from "@/lib/inventario";
import { listarProductos, type ProductoListItem } from "@/lib/productos";

function hoy(): string {
  return new Date().toISOString().slice(0, 10);
}

export default function InventarioPage() {
  const [items, setItems] = useState<InventarioItem[]>([]);
  const [productos, setProductos] = useState<ProductoListItem[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");
  const [busqueda, setBusqueda] = useState("");

  const [modalAbierto, setModalAbierto] = useState(false);
  const [productoId, setProductoId] = useState("");
  const [tipo, setTipo] = useState<TipoMovimientoInventario>("INGRESO");
  const [cantidad, setCantidad] = useState("");
  const [fecha, setFecha] = useState(hoy());
  const [observacion, setObservacion] = useState("");
  const [guardando, setGuardando] = useState(false);
  const [errorModal, setErrorModal] = useState("");

  function cargar() {
    setCargando(true);
    setError("");
    Promise.all([listarInventario(), listarProductos({ estado: "ACTIVO" })])
      .then(([inv, prods]) => {
        setItems(inv);
        setProductos(prods);
      })
      .catch((err) => setError(err instanceof ApiError ? err.message : "No se pudo cargar el inventario."))
      .finally(() => setCargando(false));
  }

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- carga inicial de datos desde la API
    cargar();
  }, []);

  function abrirModal() {
    setProductoId("");
    setTipo("INGRESO");
    setCantidad("");
    setFecha(hoy());
    setObservacion("");
    setErrorModal("");
    setModalAbierto(true);
  }

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setErrorModal("");
    if (!productoId || !cantidad) {
      setErrorModal("Selecciona un producto e ingresa la cantidad.");
      return;
    }
    setGuardando(true);
    try {
      await registrarMovimiento({
        producto_id: Number(productoId),
        tipo,
        cantidad: Number(cantidad),
        fecha,
        observacion: observacion || undefined,
      });
      setModalAbierto(false);
      cargar();
    } catch (err) {
      setErrorModal(err instanceof ApiError ? err.message : "No se pudo registrar el movimiento.");
    } finally {
      setGuardando(false);
    }
  }

  const filtrados = items.filter((i) => i.producto.toLowerCase().includes(busqueda.trim().toLowerCase()));

  return (
    <>
      <PageHeader
        title="Inventario"
        subtitle={`${items.length} productos`}
        actions={
          <>
            <Link href="/reportes/por-producto" className="btn btn-ghost">
              Ver reporte
            </Link>
            <button type="button" className="btn" onClick={abrirModal}>
              + Registrar movimiento
            </button>
          </>
        }
      />
      <div className="page">
        <div className="toolbar">
          <input
            className="input"
            placeholder="Buscar producto"
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
          />
        </div>

        {error && <p className="error-banner">{error}</p>}

        {cargando ? (
          <p className="empty-state">Cargando inventario…</p>
        ) : filtrados.length === 0 ? (
          <p className="empty-state">No se encontraron productos.</p>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Código</th>
                  <th>Producto</th>
                  <th className="num">Stock actual</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {filtrados.map((i) => (
                  <tr key={i.producto_id}>
                    <td>{i.codigo}</td>
                    <td>{i.producto}</td>
                    <td className="num">
                      <span className={`badge ${i.stock > 0 ? "badge-ok" : "badge-off"}`}>{i.stock}</span>
                    </td>
                    <td className="row-actions">
                      <Link href={`/inventario/${i.producto_id}`} className="btn btn-secondary btn-sm">
                        Ver
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <Modal open={modalAbierto} title="Registrar movimiento" onClose={() => setModalAbierto(false)}>
        {errorModal && <p className="error-banner">{errorModal}</p>}
        <form onSubmit={handleSubmit}>
          <div className="form-grid" style={{ marginBottom: 16 }}>
            <label className="field">
              Producto *
              <select className="input" value={productoId} onChange={(e) => setProductoId(e.target.value)} required>
                <option value="">Selecciona…</option>
                {productos.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.nombre}
                  </option>
                ))}
              </select>
            </label>
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
            <button type="button" className="btn btn-secondary" onClick={() => setModalAbierto(false)}>
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
