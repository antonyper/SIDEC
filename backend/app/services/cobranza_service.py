from decimal import Decimal

from app.enums.estado_cobranza import EstadoCobranza
from app.repositories.cobranza_repository import CobranzaRepository
from app.schemas.cobranza_schema import CobranzaUpdate


class CobranzaService:

    def __init__(
        self,
        repository: CobranzaRepository
    ):
        self.repository = repository

    def get_all(self):
        return self.repository.get_all()

    def get_by_id(self, cobranza_id: int):

        cobranza = self.repository.get_by_id(cobranza_id)

        if not cobranza:
            raise ValueError("La cobranza no existe.")

        return cobranza

    def get_by_liquidacion_id(self, liquidacion_id: int):

        cobranza = self.repository.get_by_liquidacion_id(
            liquidacion_id
        )

        if not cobranza:
            raise ValueError(
                "La cobranza de la liquidación no existe."
            )

        return cobranza

    def update(
        self,
        cobranza_id: int,
        cobranza_data: CobranzaUpdate
    ):

        cobranza = self.get_by_id(cobranza_id)

        if cobranza.estado == EstadoCobranza.ANULADA:
            raise ValueError(
                "No se puede modificar una cobranza anulada."
            )

        monto_pagado = cobranza_data.monto_pagado

        if monto_pagado < Decimal("0.00"):
            raise ValueError(
                "El monto pagado no puede ser negativo."
            )

        if monto_pagado > cobranza.monto:
            raise ValueError(
                "El monto pagado no puede ser mayor "
                "al monto de la cobranza."
            )

        monto_pendiente = (
            cobranza.monto - monto_pagado
        )

        if monto_pendiente == Decimal("0.00"):
            estado = EstadoCobranza.COBRADO
        else:
            estado = EstadoCobranza.PENDIENTE

        cobranza.monto_pagado = monto_pagado
        cobranza.monto_pendiente = monto_pendiente
        cobranza.estado = estado

        return self.repository.update(cobranza)

    def anular(self, cobranza_id: int):

        cobranza = self.get_by_id(cobranza_id)

        if cobranza.estado == EstadoCobranza.ANULADA:
            raise ValueError(
                "La cobranza ya está anulada."
            )

        cobranza.estado = EstadoCobranza.ANULADA

        return self.repository.save(cobranza)