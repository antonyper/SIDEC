from datetime import date

from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select, func
from app.enums.estado_liquidacion import EstadoLiquidacion

from app.models.liquidacion import Liquidacion
from app.models.detalle_liquidacion import DetalleLiquidacion
from app.models.detalle_guia import DetalleGuia


from app.schemas.liquidacion_schema import LiquidacionCreate, LiquidacionUpdate

from app.models.guia import Guia
from app.models.producto import Producto
from app.models.movimiento_inventario import MovimientoInventario
from app.enums.tipo_movimiento_inventario import TipoMovimientoInventario

class LiquidacionRepository:
    
    def __init__(self, db: Session):
        self.db = db

    # ==========================
    # Queries
    # ==========================

    def get_all(self):
        return self.db.scalars(
            select(Liquidacion)
            .options(selectinload(Liquidacion.detalles))
            .order_by(Liquidacion.id.desc())
        ).all()

    def get_by_id(self, liquidacion_id: int):
        return self.db.scalar(
            select(Liquidacion)
            .options(selectinload(Liquidacion.detalles))
            .where(Liquidacion.id == liquidacion_id)
        )

    def get_by_guia_id(self, guia_id: int):
        return self.db.scalars(
            select(Liquidacion)
            .options(
                selectinload(Liquidacion.detalles)
            )
            .where(Liquidacion.guia_id == guia_id)
            .order_by(Liquidacion.id.desc())
        ).all()

    def get_detalle_guia_by_id(self, detalle_guia_id: int):
        return self.db.scalar(
            select(DetalleGuia)
            .where(DetalleGuia.id == detalle_guia_id)
        )
    
    def get_liquidacion_by_detalle_guia(
        self,
        detalle_guia_id: int
    ):
        return self.db.scalar(
            select(DetalleLiquidacion)
            .join(Liquidacion)
            .where(
                DetalleLiquidacion.detalle_guia_id == detalle_guia_id,
                Liquidacion.estado == EstadoLiquidacion.LIQUIDADO
            )
        )

    def get_detalles_liquidados_by_guia(
        self,
        guia_id: int
    ):
        result = self.db.scalars(
            select(DetalleLiquidacion)
            .join(Liquidacion)
            .join(DetalleGuia)
            .where(
                DetalleGuia.guia_id == guia_id,
                Liquidacion.estado == EstadoLiquidacion.LIQUIDADO
            )
        )

        return result.all()
    # ==========================
    # Commands
    # ==========================

    def create(
        self,
        liquidacion_data: LiquidacionCreate,
        detalles_calculados: list[dict]
    ):
        liquidacion = Liquidacion(
            fecha=liquidacion_data.fecha,
            guia_id=liquidacion_data.guia_id,
            observacion=liquidacion_data.observacion
        )

        self.db.add(liquidacion)
        self.db.flush()

        guia = self.db.get(Guia, liquidacion_data.guia_id)
        agencia_nombre = guia.agencia.nombre if guia and guia.agencia else None

        for detalle in detalles_calculados:
            detalle_liquidacion = DetalleLiquidacion(
                liquidacion_id=liquidacion.id,
                detalle_guia_id=detalle["detalle_guia_id"],
                cantidad_vendida=detalle["cantidad_vendida"],
                cantidad_devuelta=detalle["cantidad_devuelta"],
                total=detalle["total"],
            )
            self.db.add(detalle_liquidacion)
            self.db.flush()

            if detalle["cantidad_devuelta"] > 0:
                detalle_guia = self.get_detalle_guia_by_id(
                    detalle["detalle_guia_id"]
                )
                self.db.add(
                    MovimientoInventario(
                        producto_id=detalle_guia.producto_id,
                        tipo=TipoMovimientoInventario.DEVOLUCION,
                        cantidad=detalle["cantidad_devuelta"],
                        fecha=liquidacion_data.fecha,
                        observacion=agencia_nombre,
                        detalle_liquidacion_id=detalle_liquidacion.id,
                    )
                )

        self.db.commit()
        self.db.refresh(liquidacion)

        return self.get_by_id(liquidacion.id)
    

    def registrar_ingreso_por_anulacion(self, liquidacion: Liquidacion):
        for detalle in liquidacion.detalles:
            if detalle.cantidad_vendida <= 0:
                continue

            detalle_guia = self.get_detalle_guia_by_id(
                detalle.detalle_guia_id
            )

            self.db.add(
                MovimientoInventario(
                    producto_id=detalle_guia.producto_id,
                    tipo=TipoMovimientoInventario.INGRESO,
                    cantidad=detalle.cantidad_vendida,
                    fecha=date.today(),
                    observacion="Liquidación anulada",
                    detalle_liquidacion_id=detalle.id,
                )
            )

        self.db.commit()

    def save(self, liquidacion: Liquidacion):
        self.db.commit()
        self.db.refresh(liquidacion)

        return liquidacion
    
    def get_guia_para_liquidar(self, guia_id: int):
        return self.db.scalar(
            select(Guia)
            .options(
                selectinload(Guia.agencia),
                selectinload(Guia.detalles)
                .selectinload(DetalleGuia.producto)
            )
            .where(Guia.id == guia_id)
        )
    def get_detalle_liquidacion(
        self,
        liquidacion_id: int,
        detalle_guia_id: int
        ):
        return self.db.scalar(
            select(DetalleLiquidacion)
            .where(
                DetalleLiquidacion.liquidacion_id
                == liquidacion_id,
                DetalleLiquidacion.detalle_guia_id
                == detalle_guia_id
            )
        )
    def update(
        self,
        liquidacion,
        detalles_calculados
    ):
        for detalle_data in detalles_calculados:

            detalle = detalle_data["detalle_liquidacion"]

            detalle.cantidad_vendida = (
                detalle_data["cantidad_vendida"]
            )

            detalle.cantidad_devuelta = (
                detalle_data["cantidad_devuelta"]
            )

            detalle.total = (
                detalle_data["total"]
            )

        self.db.commit()
        self.db.refresh(liquidacion)

        return self.get_by_id(liquidacion.id)

    def count_detalles_guia(
        self,
        guia_id: int
    ):
        return self.db.scalar(
            select(func.count(DetalleGuia.id))
            .where(
                DetalleGuia.guia_id == guia_id
            )
        )


    def count_detalles_liquidados(
        self,
        guia_id: int
    ):
        return self.db.scalar(
            select(func.count(DetalleLiquidacion.id))
            .join(
                Liquidacion,
                Liquidacion.id
                == DetalleLiquidacion.liquidacion_id
            )
            .join(
                DetalleGuia,
                DetalleGuia.id
                == DetalleLiquidacion.detalle_guia_id
            )
            .where(
                DetalleGuia.guia_id == guia_id,
                Liquidacion.estado
                == EstadoLiquidacion.LIQUIDADO
            )
        )
    def count_detalles_liquidados_by_guia(
        self,
        guia_id: int
    ):
        return self.db.scalar(
            select(func.count(DetalleLiquidacion.id))
            .join(
                Liquidacion,
                Liquidacion.id
                == DetalleLiquidacion.liquidacion_id
            )
            .join(
                DetalleGuia,
                DetalleGuia.id
                == DetalleLiquidacion.detalle_guia_id
            )
            .where(
                DetalleGuia.guia_id == guia_id,
                Liquidacion.estado
                == EstadoLiquidacion.LIQUIDADO
            )
        ) or 0