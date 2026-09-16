"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import PageHeader from "@/components/ui/PageHeader";
import { ApiError } from "@/lib/http";
import { ESTADO_GUIA_BADGE, ESTADO_GUIA_LABEL, listarGuias, type EstadoGuia, type Guia } from "@/lib/guias";
import { listarAgencias, type AgenciaListItem } from "@/lib/agencias";

export default function GuiasPage() {
  const [guias, setGuias] = useState<Guia[]>([]);
  const [agencias, setAgencias] = useState<AgenciaListItem[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");
  const [busqueda, setBusqueda] = useState("");
  const [filtroEstado, setFiltroEstado] = useState<EstadoGuia | "">("");

  useEffect(() => {
    Promise.all([listarGuias(), listarAgencias()])
      .then(([g, a]) => {
        setGuias(g);
        setAgencias(a);
      })
      .catch((err) => setError(err instanceof ApiError ? err.message : "No se pudo cargar la lista de guías."))
      .finally(() => setCargando(false));
  }, []);

  const nombreAgencia = useMemo(() => {
    const map = new Map(agencias.map((a) => [a.id, a.nombre]));
    return (id: number) => map.get(id) ?? `Agencia #${id}`;
  }, [agencias]);

  const guiasFiltradas = guias.filter((g) => {
    if (filtroEstado && g.estado !== filtroEstado) return false;
    if (!busqueda.trim()) return true;
    const texto = `${g.numero_guia} ${nombreAgencia(g.agencia_id)}`.toLowerCase();
    return texto.includes(busqueda.trim().toLowerCase());
  });

  return (
    <>
      <PageHeader
        title="Guías"
        subtitle={`${guias.length} registradas`}
        actions={
          <>
            <Link href="/reportes/dashboard-cobranza" className="btn btn-ghost">
              Dashboard de cobranza
            </Link>
            <Link href="/reportes/detalle-por-agencia" className="btn btn-ghost">
              Detalle por agencia
            </Link>
            <Link href="/guias/nueva" className="btn">
              + Nueva guía
            </Link>
          </>
        }
      />
      <div className="page">
        <div className="toolbar">
          <input
            className="input"
            placeholder="Buscar por número o agencia"
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
          />
          <select className="input" value={filtroEstado} onChange={(e) => setFiltroEstado(e.target.value as EstadoGuia | "")}>
            <option value="">Todos los estados</option>
            {Object.entries(ESTADO_GUIA_LABEL).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </div>

        {error && <p className="error-banner">{error}</p>}

        {cargando ? (
          <p className="empty-state">Cargando guías…</p>
        ) : guiasFiltradas.length === 0 ? (
          <p className="empty-state">No se encontraron guías.</p>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>N° Guía</th>
                  <th>Fecha</th>
                  <th>Agencia</th>
                  <th className="num">Productos</th>
                  <th>Estado</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {guiasFiltradas.map((g) => (
                  <tr key={g.id}>
                    <td>{g.numero_guia}</td>
                    <td>{g.fecha}</td>
                    <td>{nombreAgencia(g.agencia_id)}</td>
                    <td className="num">{g.detalles.length}</td>
                    <td>
                      <span className={`badge ${ESTADO_GUIA_BADGE[g.estado]}`}>{ESTADO_GUIA_LABEL[g.estado]}</span>
                    </td>
                    <td className="row-actions">
                      {(g.estado === "EN_VENTA" ||
                        g.estado === "PENDIENTE_LIQUIDACION" ||
                        g.estado === "PARCIALMENTE_LIQUIDADA") && (
                        <Link href={`/liquidaciones/nueva?guia_id=${g.id}`} className="btn btn-sm">
                          Liquidar
                        </Link>
                      )}
                      <Link href={`/guias/${g.id}`} className="btn btn-secondary btn-sm">
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
    </>
  );
}
