"use client";

import { useEffect, useState } from "react";
import PageHeader from "@/components/ui/PageHeader";
import ConfirmDialog from "@/components/ui/ConfirmDialog";
import {
  actualizarUsuario,
  ApiError,
  crearUsuario,
  darDeBajaUsuario,
  listarUsuarios,
  reactivarUsuario,
  type RolUsuario,
  type Usuario,
  type UsuarioInput,
} from "@/lib/auth";

type Vista = "lista" | "formulario";

const FORM_VACIO: UsuarioInput = { nombre: "", username: "", password: "", rol: "OPERADOR" };

export default function UsuariosPage() {
  const [vista, setVista] = useState<Vista>("lista");
  const [usuarios, setUsuarios] = useState<Usuario[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  const [editandoId, setEditandoId] = useState<number | null>(null);
  const [form, setForm] = useState<UsuarioInput>(FORM_VACIO);
  const [guardando, setGuardando] = useState(false);
  const [accionEnCurso, setAccionEnCurso] = useState<Usuario | null>(null);

  async function cargarUsuarios() {
    setCargando(true);
    setError("");
    try {
      setUsuarios(await listarUsuarios());
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo cargar la lista de usuarios.");
    } finally {
      setCargando(false);
    }
  }

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- carga inicial desde la API externa
    cargarUsuarios();
  }, []);

  function abrirNuevoUsuario() {
    setEditandoId(null);
    setForm(FORM_VACIO);
    setError("");
    setVista("formulario");
  }

  function abrirEdicion(usuario: Usuario) {
    setEditandoId(usuario.id);
    setForm({ nombre: usuario.nombre, username: usuario.username, password: "", rol: usuario.rol });
    setError("");
    setVista("formulario");
  }

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!form.nombre.trim() || !form.username.trim()) {
      setError("Nombre y usuario son obligatorios.");
      return;
    }
    if (!editandoId && !form.password.trim()) {
      setError("La contraseña es obligatoria para un usuario nuevo.");
      return;
    }

    setGuardando(true);
    setError("");
    try {
      if (editandoId) {
        await actualizarUsuario(editandoId, {
          nombre: form.nombre,
          rol: form.rol,
          password: form.password || undefined,
        });
      } else {
        await crearUsuario(form);
      }
      await cargarUsuarios();
      setVista("lista");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo guardar el usuario.");
    } finally {
      setGuardando(false);
    }
  }

  async function confirmarToggleEstado() {
    const usuario = accionEnCurso;
    if (!usuario) return;
    setAccionEnCurso(null);
    setError("");
    try {
      if (usuario.activo) {
        await darDeBajaUsuario(usuario.id);
      } else {
        await reactivarUsuario(usuario.id);
      }
      await cargarUsuarios();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo actualizar el estado.");
    }
  }

  if (vista === "formulario") {
    return (
      <>
        <PageHeader title={editandoId ? "Editar usuario" : "Nuevo usuario"} subtitle="Usuarios" />
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
                Usuario *
                <input
                  className="input"
                  value={form.username}
                  onChange={(e) => setForm({ ...form, username: e.target.value })}
                  disabled={editandoId !== null}
                  required
                />
              </label>
              <label className="field">
                {editandoId ? "Nueva contraseña (opcional)" : "Contraseña *"}
                <input
                  className="input"
                  type="password"
                  value={form.password}
                  onChange={(e) => setForm({ ...form, password: e.target.value })}
                  required={!editandoId}
                />
              </label>
              <label className="field">
                Rol *
                <select
                  className="input"
                  value={form.rol}
                  onChange={(e) => setForm({ ...form, rol: e.target.value as RolUsuario })}
                  required
                >
                  <option value="OPERADOR">Operador</option>
                  <option value="ADMIN">Administrador</option>
                </select>
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
        title="Usuarios"
        subtitle={`${usuarios.length} registrados`}
        actions={
          <button type="button" className="btn" onClick={abrirNuevoUsuario}>
            + Nuevo usuario
          </button>
        }
      />
      <div className="page">
        {error && <p className="error-banner">{error}</p>}

        {cargando && usuarios.length === 0 ? (
          <p className="empty-state">Cargando usuarios…</p>
        ) : usuarios.length === 0 ? (
          <p className="empty-state">No se encontraron usuarios.</p>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Nombre</th>
                  <th>Usuario</th>
                  <th>Rol</th>
                  <th>Estado</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {usuarios.map((usuario) => (
                  <tr key={usuario.id}>
                    <td>{usuario.nombre}</td>
                    <td>{usuario.username}</td>
                    <td>{usuario.rol === "ADMIN" ? "Administrador" : "Operador"}</td>
                    <td>
                      <span className={`badge ${usuario.activo ? "badge-ok" : "badge-off"}`}>
                        {usuario.activo ? "Activo" : "Inactivo"}
                      </span>
                    </td>
                    <td className="row-actions">
                      <button type="button" className="btn btn-secondary btn-sm" onClick={() => abrirEdicion(usuario)}>
                        Editar
                      </button>
                      <button
                        type="button"
                        className="btn btn-secondary btn-sm"
                        onClick={() => setAccionEnCurso(usuario)}
                      >
                        {usuario.activo ? "Dar de baja" : "Reactivar"}
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
          accionEnCurso?.activo
            ? `¿Dar de baja a "${accionEnCurso?.nombre}"?`
            : `¿Reactivar a "${accionEnCurso?.nombre}"?`
        }
        description={
          accionEnCurso?.activo
            ? "El usuario ya no podrá iniciar sesión en el sistema."
            : "El usuario podrá volver a iniciar sesión en el sistema."
        }
        confirmLabel={accionEnCurso?.activo ? "Dar de baja" : "Reactivar"}
        danger={accionEnCurso?.activo}
        onConfirm={confirmarToggleEstado}
        onCancel={() => setAccionEnCurso(null)}
      />
    </>
  );
}
