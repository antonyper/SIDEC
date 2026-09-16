from sqlalchemy import case, select
from sqlalchemy.orm import Session

from app.enums.estado_cobranza import EstadoCobranza
from app.models.cobranza import Cobranza


class CobranzaRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        orden_estado = case(
            (Cobranza.estado == EstadoCobranza.PENDIENTE, 0),
            (Cobranza.estado == EstadoCobranza.COBRADO, 1),
            (Cobranza.estado == EstadoCobranza.ANULADA, 2),
            else_=3,
        )
        return self.db.scalars(
            select(Cobranza)
            .order_by(orden_estado, Cobranza.id.desc())
        ).all()

    def get_by_id(self, cobranza_id: int):
        return self.db.scalar(
            select(Cobranza).where(
                Cobranza.id == cobranza_id
            )
        )

    def get_by_liquidacion_id(self, liquidacion_id: int):
        return self.db.scalar(
            select(Cobranza).where(
                Cobranza.liquidacion_id == liquidacion_id
            )
        )

    def create(
        self,
        liquidacion_id: int,
        monto,
        monto_pagado,
        monto_pendiente,
        estado
    ):
        cobranza = Cobranza(
            liquidacion_id=liquidacion_id,
            monto=monto,
            monto_pagado=monto_pagado,
            monto_pendiente=monto_pendiente,
            estado=estado
        )

        self.db.add(cobranza)
        self.db.commit()
        self.db.refresh(cobranza)

        return cobranza

    def update(self, cobranza: Cobranza):
        self.db.commit()
        self.db.refresh(cobranza)

        return cobranza

    def save(self, cobranza: Cobranza):
        self.db.commit()
        self.db.refresh(cobranza)

        return cobranza