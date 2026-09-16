"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import PageHeader from "@/components/ui/PageHeader";
import { ApiError } from "@/lib/http";
import {
  ESTADO_LIQUIDACION_BADGE,
  ESTADO_LIQUIDACION_LABEL,
  listarLiquidaciones,
  type LiquidacionListItem,
} from "@/lib/liquidaciones";

export default function LiquidacionesPage() {
  const [liquidaciones, setLiquidaciones] = useState<LiquidacionListItem[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    listarLiquidaciones()
      .then(setLiquidaciones)
      .catch((err) => setError(err instanceof ApiError ? err.message : "No se pudo cargar la lista de liquidaciones."))
      .finally(() => setCargando(false));
  }, []);

  return (
    <>
      <PageHeader
        title="Liquidaciones"
        subtitle={`${liquidaciones.length} registradas`}
        actions={
          <>
            <Link href="/reportes/cobranzas-por-periodo" className="btn btn-ghost">
              Ver reporte
            </Link>
            <Link href="/guias" className="btn">
              Liquidar una guía
            </Link>
          </>
        }
      />
      <div className="page">
        {error && <p className="error-banner">{error}</p>}
        {cargando ? (
          <p className="empty-state">Cargando liquidaciones…</p>
        ) : liquidaciones.length === 0 ? (
          <p className="empty-state">
            No hay liquidaciones todavía. Empieza desde el módulo de{" "}
            <Link href="/guias" style={{ color: "var(--blue)", fontWeight: 700 }}>
              Guías
            </Link>
            .
          </p>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Fecha</th>
                  <th>Guía</th>
                  <th>Observación</th>
                  <th>Estado</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {liquidaciones.map((l) => (
                  <tr key={l.id}>
                    <td>{l.fecha}</td>
                    <td>
                      <Link href={`/guias/${l.guia_id}`} style={{ color: "var(--blue)", fontWeight: 700 }}>
                        Ver guía #{l.guia_id}
                      </Link>
                    </td>
                    <td>{l.observacion ?? "—"}</td>
                    <td>
                      <span className={`badge ${ESTADO_LIQUIDACION_BADGE[l.estado]}`}>
                        {ESTADO_LIQUIDACION_LABEL[l.estado]}
                      </span>
                    </td>
                    <td className="row-actions">
                      <Link href={`/liquidaciones/${l.id}`} className="btn btn-secondary btn-sm">
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
