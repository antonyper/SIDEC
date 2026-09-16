"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import PageHeader from "@/components/ui/PageHeader";
import { ApiError } from "@/lib/http";
import { crearGuia, type DetalleGuiaInput } from "@/lib/guias";
import { listarAgencias, type AgenciaListItem } from "@/lib/agencias";
import { listarProductos, type ProductoListItem } from "@/lib/productos";

type LineaForm = {
  producto_id: string;
  cantidad: string;
  precio: string;
  porcentaje_cobro: string;
};

const LINEA_VACIA: LineaForm = { producto_id: "", cantidad: "1", precio: "", porcentaje_cobro: "" };

function hoy(): string {
  return new Date().toISOString().slice(0, 10);
}

export default function NuevaGuiaPage() {
  const router = useRouter();
  const [agencias, setAgencias] = useState<AgenciaListItem[]>([]);
  const [productos, setProductos] = useState<ProductoListItem[]>([]);
  const [fecha, setFecha] = useState(hoy());
  const [agenciaId, setAgenciaId] = useState("");
  const [observacion, setObservacion] = useState("");
  const [lineas, setLineas] = useState<LineaForm[]>([{ ...LINEA_VACIA }]);
  const [error, setError] = useState("");
  const [guardando, setGuardando] = useState(false);

  useEffect(() => {
    listarAgencias({ estado: "ACTIVO" }).then(setAgencias).catch(() => {});
    listarProductos({ estado: "ACTIVO" }).then(setProductos).catch(() => {});
  }, []);

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
    setLineas((prev) => [...prev, { ...LINEA_VACIA }]);
  }

  function quitarLinea(index: number) {
    setLineas((prev) => prev.filter((_, i) => i !== index));
  }

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError("");

    if (!agenciaId) {
      setError("Selecciona una agencia.");
      return;
    }
    if (lineas.length === 0) {
      setError("Agrega al menos un producto.");
      return;
    }

    const detalles: DetalleGuiaInput[] = [];
    for (const linea of lineas) {
      if (!linea.producto_id || !linea.cantidad || !linea.precio || linea.porcentaje_cobro === "") {
        setError("Completa producto, cantidad, precio y porcentaje de cobro en cada línea.");
        return;
      }
      detalles.push({
        producto_id: Number(linea.producto_id),
        cantidad: Number(linea.cantidad),
        precio: Number(linea.precio),
        porcentaje_cobro: Number(linea.porcentaje_cobro),
      });
    }

    setGuardando(true);
    try {
      const guia = await crearGuia({
        fecha,
        agencia_id: Number(agenciaId),
        observacion: observacion || undefined,
        detalles,
      });
      router.push(`/guias/${guia.id}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo crear la guía.");
      setGuardando(false);
    }
  }

  return (
    <>
      <PageHeader title="Nueva guía" subtitle="Guías" />
      <div className="page">
        <div className="card">
          {error && <p className="error-banner">{error}</p>}
          <form onSubmit={handleSubmit}>
            <div style={{ maxWidth: 920, margin: "0 auto" }}>
            <div className="form-grid cols-2" style={{ marginBottom: 24, maxWidth: "none" }}>
              <label className="field">
                Fecha *
                <input className="input" type="date" value={fecha} onChange={(e) => setFecha(e.target.value)} required />
              </label>
              <label className="field">
                Agencia *
                <select className="input" value={agenciaId} onChange={(e) => setAgenciaId(e.target.value)} required>
                  <option value="">Selecciona una agencia</option>
                  {agencias.map((a) => (
                    <option key={a.id} value={a.id}>
                      {a.nombre}
                    </option>
                  ))}
                </select>
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
                              placeholder="entre 0 y 100, ej. 20"
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

              <label className="field" style={{ marginTop: 20 }}>
                Observación
                <textarea
                  className="input"
                  value={observacion}
                  onChange={(e) => setObservacion(e.target.value)}
                />
              </label>
            </div>

            <div className="form-actions" style={{ marginTop: 24 }}>
              <button type="button" className="btn btn-secondary" onClick={() => router.push("/guias")}>
                Cancelar
              </button>
              <button type="submit" className="btn" disabled={guardando}>
                {guardando ? "Guardando…" : "Crear guía"}
              </button>
            </div>
          </form>
        </div>
      </div>
    </>
  );
}
