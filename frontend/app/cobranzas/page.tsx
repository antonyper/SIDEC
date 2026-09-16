"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import PageHeader from "@/components/ui/PageHeader";
import Modal from "@/components/ui/Modal";
import { ApiError } from "@/lib/http";
import {
  ESTADO_COBRANZA_BADGE,
  ESTADO_COBRANZA_LABEL,
  listarCobranzas,
  registrarPago,
  type Cobranza,
  type EstadoCobranza,
} from "@/lib/cobranzas";

export default function CobranzasPage() {
  const [cobranzas, setCobranzas] = useState<Cobranza[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");
  const [filtroEstado, setFiltroEstado] = useState<EstadoCobranza | "">("");
  const [editando, setEditando] = useState<Cobranza | null>(null);
  const [montoPagado, setMontoPagado] = useState("");
  const [guardando, setGuardando] = useState(false);

  function cargar() {
    setCargando(true);
    setError("");
    listarCobranzas()
      .then(setCobranzas)
      .catch((err) => setError(err instanceof ApiError ? err.message : "No se pudo cargar la lista de cobranzas."))
      .finally(() => setCargando(false));
  }

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- carga inicial de datos desde la API
    cargar();
  }, []);

  function abrirPago(cobranza: Cobranza) {
    setEditando(cobranza);
    setMontoPagado(String(cobranza.monto_pagado));
    setError("");
  }

  async function guardarPago(event: React.FormEvent) {
    event.preventDefault();
    if (!editando) return;
    setGuardando(true);
    setError("");
    try {
      await registrarPago(editando.id, Number(montoPagado));
      setEditando(null);
      cargar();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo registrar el pago.");
    } finally {
      setGuardando(false);
    }
  }

  const filtradas = cobranzas.filter((c) => !filtroEstado || c.estado === filtroEstado);
  const totalPendiente = cobranzas.reduce((acc, c) => acc + (c.estado !== "ANULADA" ? c.monto_pendiente : 0), 0);

  return (
    <>
      <PageHeader
        title="Cobranzas"
        subtitle={`${cobranzas.length} registradas`}
        actions={
          <>
            <Link href="/reportes/dashboard-cobranza" className="btn btn-ghost">
              Dashboard de cobranza
            </Link>
            <Link href="/reportes/deuda-pendiente" className="btn btn-ghost">
              Ver reporte
            </Link>
          </>
        }
      />
      <div className="page">
        <div className="stat-grid">
          <div className="stat-card">
            <span>Deuda pendiente total</span>
            <strong>S/ {totalPendiente.toFixed(2)}</strong>
          </div>
        </div>

        <div className="toolbar">
          <select className="input" value={filtroEstado} onChange={(e) => setFiltroEstado(e.target.value as EstadoCobranza | "")}>
            <option value="">Todos los estados</option>
            {Object.entries(ESTADO_COBRANZA_LABEL).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </div>

        {error && !editando && <p className="error-banner">{error}</p>}

        {cargando ? (
          <p className="empty-state">Cargando cobranzas…</p>
        ) : filtradas.length === 0 ? (
          <p className="empty-state">No se encontraron cobranzas.</p>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Liquidación</th>
                  <th>Agencia</th>
                  <th className="num">Monto</th>
                  <th className="num">Pagado</th>
                  <th className="num">Pendiente</th>
                  <th>Estado</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {filtradas.map((c) => (
                  <tr key={c.id}>
                    <td>
                      <Link href={`/liquidaciones/${c.liquidacion_id}`} style={{ color: "var(--blue)", fontWeight: 700 }}>
                        Liquidación #{c.liquidacion_id}
                      </Link>
                    </td>
                    <td>{c.agencia_nombre ?? "—"}</td>
                    <td className="num">S/ {c.monto.toFixed(2)}</td>
                    <td className="num">S/ {c.monto_pagado.toFixed(2)}</td>
                    <td className="num">S/ {c.monto_pendiente.toFixed(2)}</td>
                    <td>
                      <span className={`badge ${ESTADO_COBRANZA_BADGE[c.estado]}`}>{ESTADO_COBRANZA_LABEL[c.estado]}</span>
                    </td>
                    <td className="row-actions">
                      {c.estado === "PENDIENTE" && (
                        <button type="button" className="btn btn-secondary btn-sm" onClick={() => abrirPago(c)}>
                          Registrar pago
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <Modal open={editando !== null} title="Registrar pago" onClose={() => setEditando(null)}>
        {editando && (
          <>
            <p style={{ color: "var(--muted)", marginBottom: 16 }}>Liquidación #{editando.liquidacion_id}</p>
            {error && <p className="error-banner">{error}</p>}
            <form onSubmit={guardarPago}>
              <label className="field" style={{ marginBottom: 16 }}>
                Monto total pagado (de S/ {editando.monto.toFixed(2)})
                <input
                  className="input"
                  type="number"
                  step="0.01"
                  min="0"
                  max={editando.monto}
                  value={montoPagado}
                  onChange={(e) => setMontoPagado(e.target.value)}
                  required
                />
              </label>
              <div className="modal-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setEditando(null)}>
                  Cancelar
                </button>
                <button type="submit" className="btn" disabled={guardando}>
                  {guardando ? "Guardando…" : "Guardar"}
                </button>
              </div>
            </form>
          </>
        )}
      </Modal>
    </>
  );
}
