from datetime import timedelta

from sqlalchemy import select, delete, func, update
from sqlalchemy.orm import Session, selectinload

from app.models.guia import Guia
from app.models.detalle_guia import DetalleGuia
from app.models.detalle_liquidacion import DetalleLiquidacion
from app.models.liquidacion import Liquidacion
from app.models.agencia import Agencia
from app.models.movimiento_inventario import MovimientoInventario

from app.schemas.guia_schema import GuiaCreate, GuiaUpdate

from app.enums.estado_guia import EstadoGuia
from app.enums.estado_liquidacion import EstadoLiquidacion
from app.enums.tipo_movimiento_inventario import TipoMovimientoInventario


class GuiaRepository:

    def __init__(self, db: Session):
        self.db = db

    # ==========================
    # Queries
    # ==========================

    def get_all(self):
        return self.db.scalars(
            select(Guia)
            .options(
                selectinload(Guia.detalles)
            )
            .order_by(Guia.id.desc())
        ).all()

    def get_by_id(self, guia_id: int):
        return self.db.scalar(
            select(Guia)
            .options(
                selectinload(Guia.detalles)
            )
            .where(
                Guia.id == guia_id
            )
        )

    def get_last(self):
        return self.db.scalars(
            select(Guia)
            .order_by(
                Guia.id.desc()
            )
        ).first()

    def get_by_numero_guia(self, numero_guia: str):
        return self.db.scalar(
            select(Guia).where(Guia.numero_guia == numero_guia)
        )

    # ==========================
    # Create
    # ==========================

    def create(
        self,
        guia_data: GuiaCreate,
        numero_guia: str
    ):
        guia = Guia(
            numero_guia=numero_guia,
            fecha=guia_data.fecha,
            agencia_id=guia_data.agencia_id,
            observacion=guia_data.observacion
        )

        self.db.add(guia)

        self.db.flush()

        detalles_creados = []

        for detalle in guia_data.detalles:
            detalle_guia = DetalleGuia(
                guia_id=guia.id,
                producto_id=detalle.producto_id,
                cantidad=detalle.cantidad,
                precio=detalle.precio,
                porcentaje_cobro=detalle.porcentaje_cobro
            )
            self.db.add(detalle_guia)
            detalles_creados.append(detalle_guia)

        self.db.flush()

        agencia = self.db.get(Agencia, guia_data.agencia_id)

        for detalle_guia in detalles_creados:
            self.db.add(
                MovimientoInventario(
                    producto_id=detalle_guia.producto_id,
                    tipo=TipoMovimientoInventario.SALIDA_GUIA,
                    cantidad=detalle_guia.cantidad,
                    fecha=guia_data.fecha,
                    observacion=agencia.nombre if agencia else None,
                    detalle_guia_id=detalle_guia.id,
                )
            )

        self.db.commit()

        self.db.refresh(guia)

        return guia

    # ==========================
    # Update
    # ==========================

    def update(
        self,
        guia: Guia,
        guia_data: GuiaUpdate
    ):
        if guia_data.numero_guia is not None and guia_data.numero_guia != guia.numero_guia:
            existente = self.db.scalar(
                select(Guia).where(
                    Guia.numero_guia == guia_data.numero_guia,
                    Guia.id != guia.id,
                )
            )
            if existente:
                raise ValueError(
                    f"Ya existe otra guía con el número '{guia_data.numero_guia}'."
                )
            guia.numero_guia = guia_data.numero_guia

        if guia_data.fecha is not None:
            guia.fecha = guia_data.fecha

        if guia_data.agencia_id is not None and guia_data.agencia_id != guia.agencia_id:
            if not self.db.get(Agencia, guia_data.agencia_id):
                raise ValueError("La agencia seleccionada no existe.")
            guia.agencia_id = guia_data.agencia_id

        if guia_data.observacion is not None:
            guia.observacion = guia_data.observacion

        if guia_data.estado is not None:
            guia.estado = guia_data.estado

        if guia_data.detalles is not None:

            detalles_actuales = {
                detalle.id: detalle
                for detalle in guia.detalles
            }

            ids_recibidos = set()

            for detalle_data in guia_data.detalles:

                detalle_id = detalle_data.detalle_guia_id

                if detalle_id is None:
                    # Línea nueva: se agrega un detalle de guía adicional.
                    detalle_guia_nuevo = DetalleGuia(
                        guia_id=guia.id,
                        producto_id=detalle_data.producto_id,
                        cantidad=detalle_data.cantidad,
                        precio=detalle_data.precio,
                        porcentaje_cobro=detalle_data.porcentaje_cobro,
                    )
                    self.db.add(detalle_guia_nuevo)
                    self.db.flush()

                    agencia = self.db.get(Agencia, guia.agencia_id)

                    self.db.add(
                        MovimientoInventario(
                            producto_id=detalle_guia_nuevo.producto_id,
                            tipo=TipoMovimientoInventario.SALIDA_GUIA,
                            cantidad=detalle_guia_nuevo.cantidad,
                            fecha=guia.fecha,
                            observacion=agencia.nombre if agencia else None,
                            detalle_guia_id=detalle_guia_nuevo.id,
                        )
                    )
                    continue

                if detalle_id in ids_recibidos:
                    raise ValueError(
                        f"El detalle de guía {detalle_id} está repetido."
                    )

                ids_recibidos.add(detalle_id)

                detalle = detalles_actuales.get(detalle_id)

                if not detalle:
                    raise ValueError(
                        f"El detalle de guía {detalle_id} "
                        f"no pertenece a la guía {guia.id}."
                    )

                liquidacion_activa = (
                    self.get_liquidacion_activa_by_detalle_guia(
                        detalle_id
                    )
                )

                if liquidacion_activa:
                    if (
                        detalle.producto_id != detalle_data.producto_id
                        or detalle.cantidad != detalle_data.cantidad
                        or detalle.precio != detalle_data.precio
                        or detalle.porcentaje_cobro
                        != detalle_data.porcentaje_cobro
                    ):
                        raise ValueError(
                            f"No se puede modificar el detalle de guía "
                            f"{detalle_id} porque tiene una liquidación activa."
                        )

                    continue

                detalle.producto_id = detalle_data.producto_id
                detalle.cantidad = detalle_data.cantidad
                detalle.precio = detalle_data.precio
                detalle.porcentaje_cobro = (
                    detalle_data.porcentaje_cobro
                )

            # Detalles que existían pero ya no vienen en el request
            for detalle_id, detalle in detalles_actuales.items():

                if detalle_id not in ids_recibidos:

                    liquidacion_activa = (
                        self.get_liquidacion_activa_by_detalle_guia(
                            detalle_id
                        )
                    )

                    if liquidacion_activa:
                        raise ValueError(
                            f"No se puede eliminar el detalle de guía "
                            f"{detalle_id} porque tiene una liquidación activa."
                        )

                    self.db.delete(detalle)

        self.db.commit()
        self.db.refresh(guia)

        return guia

    # ==========================
    # Delete
    # ==========================

    def delete(
        self,
        guia: Guia
    ):
        self.db.delete(guia)

        self.db.commit()

    def update_estado(
        self,
        guia: Guia,
        estado: EstadoGuia
    ):
        guia.estado = estado

        self.db.commit()
        self.db.refresh(guia)

        return guia

    def actualizar_guias_pendientes_vencidas(self) -> int:
        """Marca para liquidación las guías en venta cuya fecha supera los 30 días."""
        result = self.db.execute(
            update(Guia)
            .where(
                Guia.estado == EstadoGuia.EN_VENTA,
                Guia.fecha < func.current_date() - timedelta(days=30),
            )
            .values(estado=EstadoGuia.PENDIENTE_LIQUIDACION)
        )
        self.db.commit()

        return result.rowcount
    
    def get_liquidacion_activa_by_detalle_guia(
        self,
        detalle_guia_id: int
    ):
        return self.db.scalar(
            select(DetalleLiquidacion)
            .join(
                Liquidacion,
                Liquidacion.id == DetalleLiquidacion.liquidacion_id
            )
            .where(
                DetalleLiquidacion.detalle_guia_id == detalle_guia_id,
                Liquidacion.estado == EstadoLiquidacion.LIQUIDADO
            )
        )
