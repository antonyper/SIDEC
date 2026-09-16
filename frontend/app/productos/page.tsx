"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import PageHeader from "@/components/ui/PageHeader";
import ConfirmDialog from "@/components/ui/ConfirmDialog";
import {
  actualizarProducto,
  ApiError,
  crearProducto,
  darDeBajaProducto,
  eliminarProducto,
  listarProductos,
  reactivarProducto,
  type Estado,
  type ProductoInput,
  type ProductoListItem,
} from "@/lib/productos";

type Vista = "lista" | "formulario";

const FORM_VACIO: ProductoInput = { nombre: "", categoria: "", precio: undefined };

export default function ProductosPage() {
  const [vista, setVista] = useState<Vista>("lista");
  const [productos, setProductos] = useState<ProductoListItem[]>([]);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState("");

  const [filtroBusqueda, setFiltroBusqueda] = useState("");
  const [filtroEstado, setFiltroEstado] = useState<Estado | "">("");

  const [editandoId, setEditandoId] = useState<number | null>(null);
  const [form, setForm] = useState<ProductoInput>(FORM_VACIO);
  const [guardando, setGuardando] = useState(false);
  const [accionEnCurso, setAccionEnCurso] = useState<ProductoListItem | null>(null);
  const [productoAEliminar, setProductoAEliminar] = useState<ProductoListItem | null>(null);

  async function cargarProductos(busquedaOverride?: string) {
    const buscar = busquedaOverride !== undefined ? busquedaOverride : filtroBusqueda;
    setCargando(true);
    setError("");
    try {
      const data = await listarProductos({
        buscar: buscar || undefined,
        estado: filtroEstado || undefined,
      });
      setProductos(data);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo cargar la lista de productos.");
    } finally {
      setCargando(false);
    }
  }

  function handleBusquedaChange(valor: string) {
    setFiltroBusqueda(valor);
    if (valor === "") {
      cargarProductos("");
    }
  }

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- sincroniza la lista con la API externa al cambiar el filtro
    cargarProductos();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filtroEstado]);

  function abrirNuevoProducto() {
    setEditandoId(null);
    setForm(FORM_VACIO);
    setError("");
    setVista("formulario");
  }

  function abrirEdicion(producto: ProductoListItem) {
    setEditandoId(producto.id);
    setForm({
      nombre: producto.nombre,
      categoria: producto.categoria ?? "",
      precio: producto.precio ?? undefined,
    });
    setError("");
    setVista("formulario");
  }

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!form.nombre.trim()) {
      setError("El nombre es obligatorio.");
      return;
    }

    setGuardando(true);
    setError("");
    try {
      if (editandoId) {
        await actualizarProducto(editandoId, form);
      } else {
        await crearProducto(form);
      }
      await cargarProductos();
      setVista("lista");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo guardar el producto.");
    } finally {
      setGuardando(false);
    }
  }

  async function confirmarToggleEstado() {
    const producto = accionEnCurso;
    if (!producto) return;
    setAccionEnCurso(null);
    setError("");
    try {
      if (producto.estado === "ACTIVO") {
        await darDeBajaProducto(producto.id);
      } else {
        await reactivarProducto(producto.id);
      }
      await cargarProductos();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo actualizar el estado.");
    }
  }

  async function confirmarEliminar() {
    const producto = productoAEliminar;
    if (!producto) return;
    setProductoAEliminar(null);
    setError("");
    try {
      await eliminarProducto(producto.id);
      await cargarProductos();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo eliminar el producto.");
    }
  }

  if (vista === "formulario") {
    return (
      <>
        <PageHeader title={editandoId ? "Editar producto" : "Nuevo producto"} subtitle="Productos" />
        <div className="page">
          <div className="card">
            {error && <p className="error-banner">{error}</p>}
            <form className="form-grid cols-2" onSubmit={handleSubmit}>
              <label className="field">
                Nombre *
                <input
                  className="input"
                  value={form.nombre}
                  onChange={(e) => setForm({ ...form, nombre: e.target.value })}
                  required
                />
              </label>
              <label className="field">
                Categoría
                <input
                  className="input"
                  value={form.categoria}
                  onChange={(e) => setForm({ ...form, categoria: e.target.value })}
                />
              </label>
              <label className="field">
                Precio *
                <input
                  className="input"
                  type="number"
                  step="0.01"
                  min="0"
                  value={form.precio ?? ""}
                  onChange={(e) =>
                    setForm({ ...form, precio: e.target.value === "" ? undefined : Number(e.target.value) })
                  }
                  required
                />
              </label>
              <div className="form-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setVista("lista")}>
                  Cancelar
                </button>
                <button type="submit" className="btn" disabled={guardando}>
                  {guardando ? "Guardando…" : "Guardar"}
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
        title="Productos"
        subtitle={`${productos.length} registrados`}
        actions={
          <>
            <Link href="/reportes/por-producto" className="btn btn-ghost">
              Ver reporte
            </Link>
            <button type="button" className="btn" onClick={abrirNuevoProducto}>
              + Nuevo producto
            </button>
          </>
        }
      />
      <div className="page">
        <div className="toolbar">
          <input
            className="input"
            placeholder="Buscar por nombre o categoría"
            value={filtroBusqueda}
            onChange={(e) => handleBusquedaChange(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && cargarProductos()}
          />
          <select
            className="input"
            value={filtroEstado}
            onChange={(e) => setFiltroEstado(e.target.value as Estado | "")}
          >
            <option value="">Todos los estados</option>
            <option value="ACTIVO">Activos</option>
            <option value="INACTIVO">Inactivos</option>
          </select>
          <button type="button" className="btn btn-secondary" onClick={() => cargarProductos()}>
            Buscar
          </button>
        </div>

        {error && <p className="error-banner">{error}</p>}

        {cargando ? (
          <p className="empty-state">Cargando productos…</p>
        ) : productos.length === 0 ? (
          <p className="empty-state">No se encontraron productos.</p>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Código</th>
                  <th>Nombre</th>
                  <th>Categoría</th>
                  <th className="num">Precio</th>
                  <th>Estado</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {productos.map((producto) => (
                  <tr key={producto.id}>
                    <td>{producto.codigo}</td>
                    <td>{producto.nombre}</td>
                    <td>{producto.categoria ?? "—"}</td>
                    <td className="num">{producto.precio != null ? `S/ ${producto.precio.toFixed(2)}` : "—"}</td>
                    <td>
                      <span className={`badge ${producto.estado === "ACTIVO" ? "badge-ok" : "badge-off"}`}>
                        {producto.estado === "ACTIVO" ? "Activo" : "Inactivo"}
                      </span>
                    </td>
                    <td className="row-actions">
                      <button type="button" className="btn btn-secondary btn-sm" onClick={() => abrirEdicion(producto)}>
                        Editar
                      </button>
                      <button
                        type="button"
                        className="btn btn-secondary btn-sm"
                        onClick={() => setAccionEnCurso(producto)}
                      >
                        {producto.estado === "ACTIVO" ? "Dar de baja" : "Reactivar"}
                      </button>
                      <button
                        type="button"
                        className="btn btn-danger btn-sm"
                        title="Eliminar producto"
                        onClick={() => setProductoAEliminar(producto)}
                      >
                        🗑️ Eliminar
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <ConfirmDialog
        open={accionEnCurso !== null}
        title={
          accionEnCurso?.estado === "ACTIVO"
            ? `¿Dar de baja "${accionEnCurso?.nombre}"?`
            : `¿Reactivar "${accionEnCurso?.nombre}"?`
        }
        description={
          accionEnCurso?.estado === "ACTIVO"
            ? "El producto dejará de estar disponible para nuevas guías."
            : "El producto volverá a estar disponible para nuevas guías."
        }
        confirmLabel={accionEnCurso?.estado === "ACTIVO" ? "Dar de baja" : "Reactivar"}
        danger={accionEnCurso?.estado === "ACTIVO"}
        onConfirm={confirmarToggleEstado}
        onCancel={() => setAccionEnCurso(null)}
      />

      <ConfirmDialog
        open={productoAEliminar !== null}
        title={`¿Eliminar "${productoAEliminar?.nombre}"?`}
        description="El producto dejará de aparecer en el sistema, pero se conserva en el historial de guías y liquidaciones. Esta acción no se puede deshacer desde la web."
        confirmLabel="Eliminar"
        danger
        onConfirm={confirmarEliminar}
        onCancel={() => setProductoAEliminar(null)}
      />
    </>
  );
}
