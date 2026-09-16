"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import PageHeader from "@/components/ui/PageHeader";
import ConfirmDialog from "@/components/ui/ConfirmDialog";
import {
  actualizarAgencia,
  ApiError,
  crearAgencia,
  darDeBajaAgencia,
  listarAgencias,
  reactivarAgencia,
  type AgenciaInput,
  type AgenciaListItem,
  type Estado,
} from "@/lib/agencias";

type Vista = "lista" | "formulario";

const FORM_VACIO: AgenciaInput = {
  nombre: "",
  propietario: "",
  agente: "",
  telefono: "",
  direccion: "",
};

export default function AgenciasPage() {
  const [vista, setVista] = useState<Vista>("lista");
  const [agencias, setAgencias] = useState<AgenciaListItem[]>([]);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState("");

  const [filtroNombre, setFiltroNombre] = useState("");
  const [filtroEstado, setFiltroEstado] = useState<Estado | "">("");

  const [editandoId, setEditandoId] = useState<number | null>(null);
  const [form, setForm] = useState<AgenciaInput>(FORM_VACIO);
  const [guardando, setGuardando] = useState(false);
  const [accionEnCurso, setAccionEnCurso] = useState<AgenciaListItem | null>(null);

  async function cargarAgencias() {
    setCargando(true);
    setError("");
    try {
      const data = await listarAgencias({
        nombre: filtroNombre || undefined,
        estado: filtroEstado || undefined,
      });
      const ordenado = [...data].sort((a, b) =>
        a.estado === b.estado ? 0 : a.estado === "ACTIVO" ? -1 : 1
      );
      setAgencias(ordenado);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo cargar la lista de agencias.");
    } finally {
      setCargando(false);
    }
  }

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- sincroniza la lista con la API externa al cambiar el filtro
    cargarAgencias();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filtroEstado]);

  function abrirNuevaAgencia() {
    setEditandoId(null);
    setForm(FORM_VACIO);
    setError("");
    setVista("formulario");
  }

  function abrirEdicion(agencia: AgenciaListItem) {
    setEditandoId(agencia.id);
    setForm({
      nombre: agencia.nombre,
      propietario: agencia.propietario ?? "",
      agente: agencia.agente ?? "",
      telefono: agencia.telefono ?? "",
      direccion: "",
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
        await actualizarAgencia(editandoId, form);
      } else {
        await crearAgencia(form);
      }
      await cargarAgencias();
      setVista("lista");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo guardar la agencia.");
    } finally {
      setGuardando(false);
    }
  }

  async function confirmarToggleEstado() {
    const agencia = accionEnCurso;
    if (!agencia) return;
    setAccionEnCurso(null);
    setError("");
    try {
      if (agencia.estado === "ACTIVO") {
        await darDeBajaAgencia(agencia.id);
      } else {
        await reactivarAgencia(agencia.id);
      }
      await cargarAgencias();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo actualizar el estado.");
    }
  }

  if (vista === "formulario") {
    return (
      <>
        <PageHeader title={editandoId ? "Editar agencia" : "Nueva agencia"} subtitle="Agencias" />
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
                Propietario
                <input
                  className="input"
                  value={form.propietario}
                  onChange={(e) => setForm({ ...form, propietario: e.target.value })}
                />
              </label>
              <label className="field">
                Agente
                <input
                  className="input"
                  value={form.agente}
                  onChange={(e) => setForm({ ...form, agente: e.target.value })}
                />
              </label>
              <label className="field">
                Teléfono
                <input
                  className="input"
                  value={form.telefono}
                  onChange={(e) => setForm({ ...form, telefono: e.target.value })}
                />
              </label>
              <label className="field">
                Dirección
                <input
                  className="input"
                  value={form.direccion}
                  onChange={(e) => setForm({ ...form, direccion: e.target.value })}
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
        title="Agencias"
        subtitle={`${agencias.length} registradas`}
        actions={
          <>
            <Link href="/reportes/desempeno-agencias" className="btn btn-ghost">
              Ver reporte
            </Link>
            <button type="button" className="btn" onClick={abrirNuevaAgencia}>
              + Nueva agencia
            </button>
          </>
        }
      />
      <div className="page">
        <div className="toolbar">
          <input
            className="input"
            placeholder="Buscar por nombre"
            value={filtroNombre}
            onChange={(e) => setFiltroNombre(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && cargarAgencias()}
          />
          <select
            className="input"
            value={filtroEstado}
            onChange={(e) => setFiltroEstado(e.target.value as Estado | "")}
          >
            <option value="">Todos los estados</option>
            <option value="ACTIVO">Activas</option>
            <option value="INACTIVO">Inactivas</option>
          </select>
          <button type="button" className="btn btn-secondary" onClick={cargarAgencias}>
            Buscar
          </button>
        </div>

        {error && <p className="error-banner">{error}</p>}

        {cargando && agencias.length === 0 ? (
          <p className="empty-state">Cargando agencias…</p>
        ) : agencias.length === 0 ? (
          <p className="empty-state">No se encontraron agencias.</p>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Código</th>
                  <th>Nombre</th>
                  <th>Propietario</th>
                  <th>Agente</th>
                  <th>Teléfono</th>
                  <th>Estado</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {agencias.map((agencia) => (
                  <tr key={agencia.id}>
                    <td>{agencia.codigo}</td>
                    <td>{agencia.nombre}</td>
                    <td>{agencia.propietario ?? "—"}</td>
                    <td>{agencia.agente ?? "—"}</td>
                    <td>{agencia.telefono ?? "—"}</td>
                    <td>
                      <span className={`badge ${agencia.estado === "ACTIVO" ? "badge-ok" : "badge-off"}`}>
                        {agencia.estado === "ACTIVO" ? "Activa" : "Inactiva"}
                      </span>
                    </td>
                    <td className="row-actions">
                      <button type="button" className="btn btn-secondary btn-sm" onClick={() => abrirEdicion(agencia)}>
                        Editar
                      </button>
                      <button
                        type="button"
                        className="btn btn-secondary btn-sm"
                        onClick={() => setAccionEnCurso(agencia)}
                      >
                        {agencia.estado === "ACTIVO" ? "Dar de baja" : "Reactivar"}
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
            ? `¿Dar de baja a "${accionEnCurso?.nombre}"?`
            : `¿Reactivar "${accionEnCurso?.nombre}"?`
        }
        description={
          accionEnCurso?.estado === "ACTIVO"
            ? "La agencia dejará de aparecer como disponible para nuevas guías."
            : "La agencia volverá a estar disponible para nuevas guías."
        }
        confirmLabel={accionEnCurso?.estado === "ACTIVO" ? "Dar de baja" : "Reactivar"}
        danger={accionEnCurso?.estado === "ACTIVO"}
        onConfirm={confirmarToggleEstado}
        onCancel={() => setAccionEnCurso(null)}
      />
    </>
  );
}
