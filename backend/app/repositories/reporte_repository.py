from datetime import date
from decimal import Decimal

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.enums.estado_cobranza import EstadoCobranza
from app.enums.estado_guia import EstadoGuia
from app.enums.estado_liquidacion import EstadoLiquidacion
from app.enums.tipo_movimiento_inventario import TipoMovimientoInventario
from app.models.agencia import Agencia
from app.models.cobranza import Cobranza
from app.models.detalle_guia import DetalleGuia
from app.models.detalle_liquidacion import DetalleLiquidacion
from app.models.guia import Guia
from app.models.liquidacion import Liquidacion
from app.models.movimiento_inventario import MovimientoInventario
from app.models.producto import Producto


class ReporteRepository:

    def __init__(self, db: Session):
        self.db = db

    # ==========================
    # 1. Cobranzas por período
    # ==========================

    def cobranzas_por_periodo(self, desde: date | None, hasta: date | None):
        statement = (
            select(
                Liquidacion.id.label("liquidacion_id"),
                Liquidacion.fecha,
                Agencia.nombre.label("agencia"),
                Cobranza.monto,
                Cobranza.monto_pagado,
                Cobranza.monto_pendiente,
                Cobranza.estado,
            )
            .join(Liquidacion, Liquidacion.id == Cobranza.liquidacion_id)
            .join(Guia, Guia.id == Liquidacion.guia_id)
            .join(Agencia, Agencia.id == Guia.agencia_id)
            .order_by(Liquidacion.fecha.desc())
        )
        if desde:
            statement = statement.where(Liquidacion.fecha >= desde)
        if hasta:
            statement = statement.where(Liquidacion.fecha <= hasta)

        return self.db.execute(statement).mappings().all()

    # ==========================
    # 2 y 3. Guías pendientes / pendientes de liquidación
    # ==========================

    def guias_por_estados(self, estados: list[EstadoGuia]):
        statement = (
            select(
                Guia.id.label("guia_id"),
                Guia.numero_guia,
                Guia.fecha,
                Agencia.nombre.label("agencia"),
                Guia.estado,
            )
            .join(Agencia, Agencia.id == Guia.agencia_id)
            .where(Guia.estado.in_(estados))
            .order_by(Guia.fecha.asc())
        )
        filas = self.db.execute(statement).mappings().all()
        hoy = date.today()
        return [
            {**fila, "dias_transcurridos": (hoy - fila["fecha"]).days}
            for fila in filas
        ]

    # ==========================
    # 4. Resumen de guías
    # ==========================

    def resumen_guias(self):
        por_estado = self.db.execute(
            select(Guia.estado, func.count(Guia.id))
            .group_by(Guia.estado)
        ).all()

        valor_total = self.db.execute(
            select(func.coalesce(func.sum(DetalleGuia.cantidad * DetalleGuia.precio), 0))
        ).scalar_one()

        total_guias = sum(cantidad for _, cantidad in por_estado)

        return {
            "total_guias": total_guias,
            "por_estado": [
                {"estado": estado.value, "cantidad": cantidad}
                for estado, cantidad in por_estado
            ],
            "valor_total_entregado": valor_total,
        }

    # ==========================
    # 5. Desempeño de agencias
    # ==========================

    def desempeno_agencias(self, desde: date | None, hasta: date | None):
        agencias = self.db.execute(select(Agencia).order_by(Agencia.nombre)).scalars().all()

        resultado = []
        for agencia in agencias:
            guias_stmt = select(func.count(Guia.id)).where(Guia.agencia_id == agencia.id)
            if desde:
                guias_stmt = guias_stmt.where(Guia.fecha >= desde)
            if hasta:
                guias_stmt = guias_stmt.where(Guia.fecha <= hasta)
            total_guias = self.db.execute(guias_stmt).scalar_one()

            vendido_stmt = (
                select(func.coalesce(func.sum(DetalleLiquidacion.total), 0))
                .join(DetalleGuia, DetalleGuia.id == DetalleLiquidacion.detalle_guia_id)
                .join(Guia, Guia.id == DetalleGuia.guia_id)
                .join(Liquidacion, Liquidacion.id == DetalleLiquidacion.liquidacion_id)
                .where(
                    Guia.agencia_id == agencia.id,
                    Liquidacion.estado == EstadoLiquidacion.LIQUIDADO,
                )
            )
            cobrado_stmt = (
                select(func.coalesce(func.sum(Cobranza.monto_pagado), 0))
                .join(Liquidacion, Liquidacion.id == Cobranza.liquidacion_id)
                .join(Guia, Guia.id == Liquidacion.guia_id)
                .where(
                    Guia.agencia_id == agencia.id,
                    Cobranza.estado != EstadoCobranza.ANULADA,
                )
            )
            pendiente_stmt = (
                select(func.coalesce(func.sum(Cobranza.monto_pendiente), 0))
                .join(Liquidacion, Liquidacion.id == Cobranza.liquidacion_id)
                .join(Guia, Guia.id == Liquidacion.guia_id)
                .where(
                    Guia.agencia_id == agencia.id,
                    Cobranza.estado == EstadoCobranza.PENDIENTE,
                )
            )
            if desde:
                vendido_stmt = vendido_stmt.where(Liquidacion.fecha >= desde)
                cobrado_stmt = cobrado_stmt.where(Liquidacion.fecha >= desde)
                pendiente_stmt = pendiente_stmt.where(Liquidacion.fecha >= desde)
            if hasta:
                vendido_stmt = vendido_stmt.where(Liquidacion.fecha <= hasta)
                cobrado_stmt = cobrado_stmt.where(Liquidacion.fecha <= hasta)
                pendiente_stmt = pendiente_stmt.where(Liquidacion.fecha <= hasta)

            resultado.append(
                {
                    "agencia_id": agencia.id,
                    "agencia": agencia.nombre,
                    "estado": agencia.estado.value,
                    "total_guias": total_guias,
                    "total_vendido": self.db.execute(vendido_stmt).scalar_one(),
                    "total_cobrado": self.db.execute(cobrado_stmt).scalar_one(),
                    "deuda_pendiente": self.db.execute(pendiente_stmt).scalar_one(),
                }
            )

        return resultado

    # ==========================
    # 6. Deuda pendiente
    # ==========================

    def deuda_pendiente(self):
        statement = (
            select(
                Cobranza.id.label("cobranza_id"),
                Liquidacion.id.label("liquidacion_id"),
                Guia.id.label("guia_id"),
                Guia.numero_guia,
                Agencia.nombre.label("agencia"),
                Liquidacion.fecha,
                Cobranza.monto_pendiente,
            )
            .join(Liquidacion, Liquidacion.id == Cobranza.liquidacion_id)
            .join(Guia, Guia.id == Liquidacion.guia_id)
            .join(Agencia, Agencia.id == Guia.agencia_id)
            .where(Cobranza.estado == EstadoCobranza.PENDIENTE)
            .order_by(Liquidacion.fecha.asc())
        )
        filas = self.db.execute(statement).mappings().all()
        hoy = date.today()
        items = [
            {**fila, "dias_pendiente": (hoy - fila["fecha"]).days}
            for fila in filas
        ]
        total = sum((item["monto_pendiente"] for item in items), Decimal("0.00"))
        return {"total_pendiente": total, "items": items}

    # ==========================
    # 7. Reporte por producto
    # ==========================

    def reporte_por_producto(self):
        productos = self.db.execute(select(Producto).order_by(Producto.nombre)).scalars().all()

        entregas = dict(
            self.db.execute(
                select(DetalleGuia.producto_id, func.coalesce(func.sum(DetalleGuia.cantidad), 0))
                .group_by(DetalleGuia.producto_id)
            ).all()
        )

        ventas = self.db.execute(
            select(
                DetalleGuia.producto_id,
                func.coalesce(func.sum(DetalleLiquidacion.cantidad_vendida), 0),
                func.coalesce(func.sum(DetalleLiquidacion.total), 0),
            )
            .join(DetalleGuia, DetalleGuia.id == DetalleLiquidacion.detalle_guia_id)
            .join(Liquidacion, Liquidacion.id == DetalleLiquidacion.liquidacion_id)
            .where(Liquidacion.estado == EstadoLiquidacion.LIQUIDADO)
            .group_by(DetalleGuia.producto_id)
        ).all()
        vendido_por_producto = {row[0]: (row[1], row[2]) for row in ventas}

        entradas = case(
            (
                MovimientoInventario.tipo.in_(
                    [
                        TipoMovimientoInventario.STOCK_INICIAL,
                        TipoMovimientoInventario.INGRESO,
                        TipoMovimientoInventario.DEVOLUCION,
                    ]
                ),
                MovimientoInventario.cantidad,
            ),
            else_=-MovimientoInventario.cantidad,
        )
        stock_por_producto = dict(
            self.db.execute(
                select(MovimientoInventario.producto_id, func.coalesce(func.sum(entradas), 0))
                .group_by(MovimientoInventario.producto_id)
            ).all()
        )

        resultado = []
        for producto in productos:
            vendida, ingresos = vendido_por_producto.get(producto.id, (0, Decimal("0.00")))
            entregada = entregas.get(producto.id, 0)
            porcentaje_venta = (
                (Decimal(vendida) / Decimal(entregada) * Decimal("100")).quantize(Decimal("0.01"))
                if entregada
                else Decimal("0.00")
            )
            resultado.append(
                {
                    "producto_id": producto.id,
                    "codigo": producto.codigo,
                    "producto": producto.nombre,
                    "cantidad_entregada": entregada,
                    "cantidad_vendida": vendida,
                    "porcentaje_venta": porcentaje_venta,
                    "ingresos": ingresos,
                    "stock_actual": stock_por_producto.get(producto.id, 0),
                }
            )
        return resultado

    # ==========================
    # 8. Reporte de agencias
    # ==========================

    def reporte_agencias(self):
        agencias = self.db.execute(select(Agencia).order_by(Agencia.nombre)).scalars().all()

        totales = dict(
            self.db.execute(
                select(Guia.agencia_id, func.count(Guia.id)).group_by(Guia.agencia_id)
            ).all()
        )
        activas = dict(
            self.db.execute(
                select(Guia.agencia_id, func.count(Guia.id))
                .where(Guia.estado != EstadoGuia.ANULADA)
                .group_by(Guia.agencia_id)
            ).all()
        )

        return [
            {
                "agencia_id": agencia.id,
                "codigo": agencia.codigo,
                "agencia": agencia.nombre,
                "propietario": agencia.propietario,
                "agente": agencia.agente,
                "telefono": agencia.telefono,
                "estado": agencia.estado.value,
                "total_guias": totales.get(agencia.id, 0),
                "guias_activas": activas.get(agencia.id, 0),
            }
            for agencia in agencias
        ]

    # ==========================
    # 9. Resumen por período
    # ==========================

    def resumen_periodo(self, desde: date | None, hasta: date | None):
        guias_stmt = select(func.count(Guia.id))
        valor_stmt = select(
            func.coalesce(func.sum(DetalleGuia.cantidad * DetalleGuia.precio), 0)
        ).select_from(DetalleGuia).join(Guia, Guia.id == DetalleGuia.guia_id)

        if desde:
            guias_stmt = guias_stmt.where(Guia.fecha >= desde)
            valor_stmt = valor_stmt.where(Guia.fecha >= desde)
        if hasta:
            guias_stmt = guias_stmt.where(Guia.fecha <= hasta)
            valor_stmt = valor_stmt.where(Guia.fecha <= hasta)

        liquidado_stmt = (
            select(func.coalesce(func.sum(DetalleLiquidacion.total), 0))
            .join(Liquidacion, Liquidacion.id == DetalleLiquidacion.liquidacion_id)
            .where(Liquidacion.estado == EstadoLiquidacion.LIQUIDADO)
        )
        cobrado_stmt = (
            select(func.coalesce(func.sum(Cobranza.monto_pagado), 0))
            .join(Liquidacion, Liquidacion.id == Cobranza.liquidacion_id)
            .where(Cobranza.estado != EstadoCobranza.ANULADA)
        )
        pendiente_stmt = (
            select(func.coalesce(func.sum(Cobranza.monto_pendiente), 0))
            .join(Liquidacion, Liquidacion.id == Cobranza.liquidacion_id)
            .where(Cobranza.estado == EstadoCobranza.PENDIENTE)
        )
        if desde:
            liquidado_stmt = liquidado_stmt.where(Liquidacion.fecha >= desde)
            cobrado_stmt = cobrado_stmt.where(Liquidacion.fecha >= desde)
            pendiente_stmt = pendiente_stmt.where(Liquidacion.fecha >= desde)
        if hasta:
            liquidado_stmt = liquidado_stmt.where(Liquidacion.fecha <= hasta)
            cobrado_stmt = cobrado_stmt.where(Liquidacion.fecha <= hasta)
            pendiente_stmt = pendiente_stmt.where(Liquidacion.fecha <= hasta)

        return {
            "desde": desde,
            "hasta": hasta,
            "guias_emitidas": self.db.execute(guias_stmt).scalar_one(),
            "valor_entregado": self.db.execute(valor_stmt).scalar_one(),
            "total_liquidado": self.db.execute(liquidado_stmt).scalar_one(),
            "total_cobrado": self.db.execute(cobrado_stmt).scalar_one(),
            "total_pendiente": self.db.execute(pendiente_stmt).scalar_one(),
        }

    # ==========================
    # 10. Kardex de inventario
    # ==========================

    def kardex_inventario(
        self,
        producto_id: int | None,
        desde: date | None,
        hasta: date | None,
    ):
        statement = (
            select(
                MovimientoInventario.fecha,
                MovimientoInventario.producto_id,
                Producto.nombre.label("producto"),
                MovimientoInventario.tipo,
                MovimientoInventario.cantidad,
                MovimientoInventario.observacion,
            )
            .join(Producto, Producto.id == MovimientoInventario.producto_id)
            .order_by(MovimientoInventario.fecha.desc(), MovimientoInventario.id.desc())
        )
        if producto_id:
            statement = statement.where(MovimientoInventario.producto_id == producto_id)
        if desde:
            statement = statement.where(MovimientoInventario.fecha >= desde)
        if hasta:
            statement = statement.where(MovimientoInventario.fecha <= hasta)

        filas = self.db.execute(statement).mappings().all()
        return [
            {**fila, "tipo": fila["tipo"].value}
            for fila in filas
        ]

    # ==========================
    # 11. Ranking de agencias por % de venta
    # ==========================

    def ranking_agencias_venta(self, desde: date | None, hasta: date | None):
        statement = (
            select(
                Agencia.id.label("agencia_id"),
                Agencia.nombre.label("agencia"),
                func.coalesce(func.sum(DetalleLiquidacion.cantidad_vendida), 0).label("vendidas"),
                func.coalesce(func.sum(DetalleLiquidacion.cantidad_devuelta), 0).label("devueltas"),
            )
            .select_from(Agencia)
            .join(Guia, Guia.agencia_id == Agencia.id)
            .join(DetalleGuia, DetalleGuia.guia_id == Guia.id)
            .join(DetalleLiquidacion, DetalleLiquidacion.detalle_guia_id == DetalleGuia.id)
            .join(Liquidacion, Liquidacion.id == DetalleLiquidacion.liquidacion_id)
            .where(Liquidacion.estado == EstadoLiquidacion.LIQUIDADO)
            .group_by(Agencia.id, Agencia.nombre)
        )
        if desde:
            statement = statement.where(Liquidacion.fecha >= desde)
        if hasta:
            statement = statement.where(Liquidacion.fecha <= hasta)

        filas = self.db.execute(statement).all()

        resultado = []
        for agencia_id, agencia, vendidas, devueltas in filas:
            entregadas = vendidas + devueltas
            porcentaje = (
                (Decimal(vendidas) / Decimal(entregadas) * Decimal("100")).quantize(Decimal("0.01"))
                if entregadas
                else Decimal("0.00")
            )
            resultado.append(
                {
                    "agencia_id": agencia_id,
                    "agencia": agencia,
                    "unidades_entregadas": entregadas,
                    "unidades_vendidas": vendidas,
                    "unidades_devueltas": devueltas,
                    "porcentaje_venta": porcentaje,
                }
            )

        resultado.sort(key=lambda fila: fila["porcentaje_venta"], reverse=True)
        return resultado

    # ==========================
    # 12. Guías por vencer
    # ==========================

    def guias_por_vencer(self):
        statement = (
            select(
                Guia.id.label("guia_id"),
                Guia.numero_guia,
                Guia.fecha,
                Agencia.nombre.label("agencia"),
            )
            .join(Agencia, Agencia.id == Guia.agencia_id)
            .where(Guia.estado == EstadoGuia.EN_VENTA)
            .order_by(Guia.fecha.asc())
        )
        filas = self.db.execute(statement).mappings().all()
        hoy = date.today()
        resultado = []
        for fila in filas:
            dias_transcurridos = (hoy - fila["fecha"]).days
            resultado.append(
                {
                    **fila,
                    "dias_transcurridos": dias_transcurridos,
                    "dias_restantes": 30 - dias_transcurridos,
                }
            )
        return resultado

    # ==========================
    # 13. Distribución (agencias x productos)
    # ==========================

    def reporte_distribucion(
        self,
        desde: date | None,
        hasta: date | None,
        producto_ids: list[int] | None = None,
    ):
        statement = (
            select(
                Guia.agencia_id,
                DetalleGuia.producto_id,
                Producto.nombre.label("producto"),
                func.coalesce(func.sum(DetalleGuia.cantidad), 0).label("cantidad"),
            )
            .select_from(DetalleGuia)
            .join(Guia, Guia.id == DetalleGuia.guia_id)
            .join(Producto, Producto.id == DetalleGuia.producto_id)
            .where(Guia.estado != EstadoGuia.ANULADA)
            .group_by(Guia.agencia_id, DetalleGuia.producto_id, Producto.nombre)
        )
        if producto_ids:
            statement = statement.where(DetalleGuia.producto_id.in_(producto_ids))
        if desde:
            statement = statement.where(Guia.fecha >= desde)
        if hasta:
            statement = statement.where(Guia.fecha <= hasta)

        filas_raw = self.db.execute(statement).all()

        producto_totales: dict[int, dict] = {}
        valores: dict[tuple[int, int], int] = {}
        totales_por_agencia: dict[int, int] = {}

        for agencia_id, producto_id_fila, producto, cantidad in filas_raw:
            cantidad = int(cantidad)
            valores[(agencia_id, producto_id_fila)] = cantidad

            producto_info = producto_totales.setdefault(producto_id_fila, {"nombre": producto, "total": 0})
            producto_info["total"] += cantidad

            totales_por_agencia[agencia_id] = totales_por_agencia.get(agencia_id, 0) + cantidad

        productos_ordenados = sorted(
            producto_totales.items(), key=lambda kv: kv[1]["total"], reverse=True
        )

        columnas = [
            {"producto_id": pid, "producto": info["nombre"], "total": info["total"]}
            for pid, info in productos_ordenados
        ]

        todas_agencias = self.db.execute(
            select(Agencia.id, Agencia.nombre).order_by(Agencia.nombre)
        ).all()

        filas = [
            {
                "agencia_id": aid,
                "agencia": anombre,
                "total": totales_por_agencia.get(aid, 0),
                "valores": [valores.get((aid, pid), 0) for pid, _ in productos_ordenados],
            }
            for aid, anombre in todas_agencias
        ]
        filas.sort(key=lambda fila: fila["total"], reverse=True)

        total_general = sum(totales_por_agencia.values())

        return {
            "columnas": columnas,
            "filas": filas,
            "total_general": total_general,
        }

    # ==========================
    # 14. Detalle por agencia
    # ==========================

    def detalle_por_agencia(self, desde: date | None, hasta: date | None):
        no_liquidado = ~(
            select(DetalleLiquidacion.id)
            .join(Liquidacion, Liquidacion.id == DetalleLiquidacion.liquidacion_id)
            .where(
                DetalleLiquidacion.detalle_guia_id == DetalleGuia.id,
                Liquidacion.estado == EstadoLiquidacion.LIQUIDADO,
            )
            .exists()
        )

        statement = (
            select(
                Agencia.id.label("agencia_id"),
                Agencia.nombre.label("agencia"),
                Guia.id.label("guia_id"),
                Guia.numero_guia,
                Guia.fecha,
                Guia.estado,
                DetalleGuia.producto_id,
                Producto.nombre.label("producto"),
                DetalleGuia.cantidad,
                DetalleGuia.precio.label("precio_publico"),
                DetalleGuia.porcentaje_cobro,
            )
            .select_from(DetalleGuia)
            .join(Guia, Guia.id == DetalleGuia.guia_id)
            .join(Agencia, Agencia.id == Guia.agencia_id)
            .join(Producto, Producto.id == DetalleGuia.producto_id)
            .where(
                Guia.estado.in_(
                    [
                        EstadoGuia.EN_VENTA,
                        EstadoGuia.PENDIENTE_LIQUIDACION,
                        EstadoGuia.PARCIALMENTE_LIQUIDADA,
                    ]
                ),
                no_liquidado,
            )
            .order_by(Agencia.nombre, Guia.fecha, Guia.numero_guia)
        )
        if desde:
            statement = statement.where(Guia.fecha >= desde)
        if hasta:
            statement = statement.where(Guia.fecha <= hasta)

        filas = self.db.execute(statement).all()

        grupos: dict[int, dict] = {}
        total_general = Decimal("0.00")

        for (
            agencia_id,
            agencia,
            guia_id,
            numero_guia,
            fecha,
            estado_guia,
            producto_id,
            producto,
            cantidad,
            precio_publico,
            porcentaje_cobro,
        ) in filas:
            precio_publico = precio_publico if precio_publico is not None else Decimal("0.00")
            porcentaje_cobro = porcentaje_cobro if porcentaje_cobro is not None else Decimal("0.00")

            precio_agencia = (
                precio_publico * porcentaje_cobro / Decimal("100")
            ).quantize(Decimal("0.01"))

            x_estimado = (
                Decimal("0.5") * Decimal(cantidad) * precio_agencia
            ).quantize(Decimal("0.01"))

            grupo = grupos.setdefault(
                agencia_id,
                {
                    "agencia_id": agencia_id,
                    "agencia": agencia,
                    "detalles": [],
                    "total_entregado": Decimal("0.00"),
                },
            )
            grupo["detalles"].append(
                {
                    "guia_id": guia_id,
                    "numero_guia": numero_guia,
                    "fecha": fecha,
                    "estado_guia": estado_guia.value,
                    "producto_id": producto_id,
                    "producto": producto,
                    "cantidad": cantidad,
                    "precio_publico": precio_publico,
                    "precio_agencia": precio_agencia,
                    "x_estimado": x_estimado,
                }
            )
            grupo["total_entregado"] += x_estimado
            total_general += x_estimado

        for grupo in grupos.values():
            grupo["detalles"].sort(key=lambda detalle: (detalle["fecha"], detalle["numero_guia"]))

        grupos_ordenados = sorted(grupos.values(), key=lambda grupo: grupo["agencia"].lower())

        return {
            "grupos": grupos_ordenados,
            "total_general": total_general,
        }

    # ==========================
    # 15. Top agencias por variedad de productos
    # ==========================

    def top_agencias_por_productos(self):
        statement = (
            select(
                Agencia.id.label("agencia_id"),
                Agencia.nombre.label("agencia"),
                func.count(func.distinct(DetalleGuia.producto_id)).label("cantidad_productos"),
            )
            .select_from(DetalleGuia)
            .join(Guia, Guia.id == DetalleGuia.guia_id)
            .join(Agencia, Agencia.id == Guia.agencia_id)
            .where(Guia.estado != EstadoGuia.ANULADA)
            .group_by(Agencia.id, Agencia.nombre)
            .order_by(func.count(func.distinct(DetalleGuia.producto_id)).desc())
        )
        return self.db.execute(statement).mappings().all()
