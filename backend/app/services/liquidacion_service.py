from decimal import Decimal

from app.enums.estado_liquidacion import EstadoLiquidacion
from app.enums.estado_guia import EstadoGuia
from app.enums.estado_cobranza import EstadoCobranza
from app.repositories.cobranza_repository import CobranzaRepository
from app.repositories.liquidacion_repository import LiquidacionRepository
from app.schemas.liquidacion_schema import (
    LiquidacionCreate,
    LiquidacionUpdate,
)
from app.repositories.guia_repository import GuiaRepository


class LiquidacionService:

    def __init__(
        self,
        repository: LiquidacionRepository,
        guia_repository: GuiaRepository,
        cobranza_repository: CobranzaRepository
    ):
        self.repository = repository
        self.guia_repository = guia_repository
        self.cobranza_repository = cobranza_repository

    # ==========================
    # Queries
    # ==========================

    def get_all(self):
        return self.repository.get_all()

    def get_by_id(self, liquidacion_id: int):
        liquidacion = self.repository.get_by_id(liquidacion_id)

        if not liquidacion:
            raise ValueError("La liquidación no existe.")

        return liquidacion

    def get_by_guia_id(self, guia_id: int):
        return self.repository.get_by_guia_id(guia_id)

    # ==========================
    # Create
    # ==========================
    def create(
        self,
        liquidacion_data: LiquidacionCreate
    ):

        if not liquidacion_data.detalles:
            raise ValueError(
                "La liquidación debe contener al menos un producto."
            )

        detalles_calculados = []

        detalles_ids = set()

        for detalle in liquidacion_data.detalles:

            # ==========================
            # Validar duplicados
            # ==========================

            if detalle.detalle_guia_id in detalles_ids:
                raise ValueError(
                    "No se puede repetir el mismo producto "
                    "en la misma liquidación."
                )

            detalles_ids.add(
                detalle.detalle_guia_id
            )

            # ==========================
            # Obtener detalle de guía
            # ==========================

            detalle_guia = (
                self.repository.get_detalle_guia_by_id(
                    detalle.detalle_guia_id
                )
            )

            if not detalle_guia:
                raise ValueError(
                    f"El detalle de guía "
                    f"{detalle.detalle_guia_id} "
                    f"no existe."
                )

            # ==========================
            # Validar pertenencia
            # ==========================

            if (
                detalle_guia.guia_id
                != liquidacion_data.guia_id
            ):
                raise ValueError(
                    "El producto no pertenece "
                    "a la guía indicada."
                )

            # ==========================
            # Validar cantidad devuelta
            # ==========================

            if detalle.cantidad_devuelta < 0:
                raise ValueError(
                    "La cantidad devuelta "
                    "no puede ser negativa."
                )

            if (
                detalle.cantidad_devuelta
                > detalle_guia.cantidad
            ):
                raise ValueError(
                    "La cantidad devuelta "
                    "no puede ser mayor "
                    "a la cantidad entregada."
                )

            # ==========================
            # Validar que no esté liquidado
            # ==========================

            liquidacion_existente = (
                self.repository.get_liquidacion_by_detalle_guia(
                    detalle.detalle_guia_id
                )
            )

            if liquidacion_existente:
                raise ValueError(
                    f"El producto con detalle de guía "
                    f"{detalle.detalle_guia_id} "
                    f"ya fue liquidado."
                )

            # ==========================
            # Calcular cantidad vendida
            # ==========================

            cantidad_vendida = (
                detalle_guia.cantidad
                - detalle.cantidad_devuelta
            )

            # ==========================
            # Precio
            # ==========================

            precio = Decimal(
                detalle_guia.precio
            )

            porcentaje_cobro = Decimal(
                detalle_guia.porcentaje_cobro
            )

            # ==========================
            # Precio a liquidar = precio agencia
            # (precio público × % cobro agencia; se puede sobrescribir manualmente)
            # ==========================

            if detalle.precio_a_liquidar is not None:
                precio_a_liquidar = detalle.precio_a_liquidar
            else:
                precio_a_liquidar = (
                    precio
                    * porcentaje_cobro
                    / Decimal("100")
                ).quantize(
                    Decimal("0.01")
                )

            # ==========================
            # Total
            # ==========================

            total = (
                Decimal(cantidad_vendida)
                * precio_a_liquidar
            ).quantize(
                Decimal("0.01")
            )

            # ==========================
            # Preparar detalle
            # ==========================

            detalles_calculados.append(
                {
                    "detalle_guia_id":
                        detalle.detalle_guia_id,

                    "cantidad_vendida":
                        cantidad_vendida,

                    "cantidad_devuelta":
                        detalle.cantidad_devuelta,

                    "total":
                        total,
                }
            )

        # ==========================
        # Crear liquidación
        # ==========================

        liquidacion = self.repository.create(
            liquidacion_data=liquidacion_data,
            detalles_calculados=detalles_calculados,
        )

        # ==========================
        # Crear cobranza
        # ==========================

        monto_cobranza = sum(
            (
                detalle["total"]
                for detalle in detalles_calculados
            ),
            Decimal("0.00")
        )

        pago_a_cuenta = liquidacion_data.pago_a_cuenta

        if pago_a_cuenta < Decimal("0.00"):
            raise ValueError(
                "El pago a cuenta no puede ser negativo."
            )

        if pago_a_cuenta > monto_cobranza:
            raise ValueError(
                "El pago a cuenta no puede ser mayor "
                "al monto de la liquidación."
            )

        # Si no se indica pago a cuenta,
        # se considera la liquidación totalmente cobrada.
        if pago_a_cuenta == Decimal("0.00"):
            monto_pagado = monto_cobranza
        else:
            monto_pagado = pago_a_cuenta

        monto_pendiente = (
            monto_cobranza - monto_pagado
        )

        if monto_pendiente == Decimal("0.00"):
            estado_cobranza = EstadoCobranza.COBRADO
        else:
            estado_cobranza = EstadoCobranza.PENDIENTE

        self.cobranza_repository.create(
            liquidacion_id=liquidacion.id,
            monto=monto_cobranza,
            monto_pagado=monto_pagado,
            monto_pendiente=monto_pendiente,
            estado=estado_cobranza
        )

        self.actualizar_estado_guia(
            liquidacion_data.guia_id
        )

        return liquidacion

    def update(
        self,
        liquidacion_id: int,
        liquidacion_data: LiquidacionUpdate
    ):
        liquidacion = self.repository.get_by_id(liquidacion_id)

        if not liquidacion:
            raise ValueError("La liquidación no existe.")

        if liquidacion_data.fecha is not None:
            liquidacion.fecha = liquidacion_data.fecha

        if liquidacion_data.observacion is not None:
            liquidacion.observacion = liquidacion_data.observacion

        detalles_calculados = []

        if liquidacion_data.detalles is not None:

            for detalle in liquidacion_data.detalles:

                detalle_liquidacion = (
                    self.repository.get_detalle_liquidacion(
                        liquidacion_id=liquidacion_id,
                        detalle_guia_id=detalle.detalle_guia_id
                    )
                )

                if not detalle_liquidacion:
                    raise ValueError(
                        f"El detalle de guía {detalle.detalle_guia_id} "
                        f"no pertenece a la liquidación {liquidacion_id}."
                    )

                detalle_guia = (
                    self.repository.get_detalle_guia_by_id(
                        detalle.detalle_guia_id
                    )
                )

                if not detalle_guia:
                    raise ValueError(
                        f"El detalle de guía {detalle.detalle_guia_id} "
                        "no existe."
                    )

                if detalle.cantidad_devuelta < 0:
                    raise ValueError(
                        "La cantidad devuelta no puede ser negativa."
                    )

                if detalle.cantidad_devuelta > detalle_guia.cantidad:
                    raise ValueError(
                        "La cantidad devuelta no puede ser mayor "
                        "a la cantidad entregada."
                    )

                cantidad_vendida = (
                    detalle_guia.cantidad
                    - detalle.cantidad_devuelta
                )

                precio = Decimal(detalle_guia.precio)

                porcentaje_cobro = Decimal(
                    detalle_guia.porcentaje_cobro
                )

                if detalle.precio_a_liquidar is not None:
                    precio_a_liquidar = detalle.precio_a_liquidar
                else:
                    precio_a_liquidar = (
                        precio
                        * porcentaje_cobro
                        / Decimal("100")
                    ).quantize(
                        Decimal("0.01")
                    )

                total = (
                    Decimal(cantidad_vendida)
                    * precio_a_liquidar
                ).quantize(
                    Decimal("0.01")
                )

                detalles_calculados.append(
                    {
                        "detalle_liquidacion": detalle_liquidacion,
                        "cantidad_vendida": cantidad_vendida,
                        "cantidad_devuelta": detalle.cantidad_devuelta,
                        "total": total,
                    }
                )

        return self.repository.update(
            liquidacion=liquidacion,
            detalles_calculados=detalles_calculados
        )


    def get_guia_para_liquidar(
        self,
        guia_id: int
    ):

        guia = self.repository.get_guia_para_liquidar(
            guia_id
        )

        if not guia:
            raise ValueError(
                "La guía no existe."
            )

        detalles_response = []

        for detalle_guia in guia.detalles:

            # ==========================
            # Verificar si ya fue liquidado
            # ==========================

            liquidacion_existente = (
                self.repository.get_liquidacion_by_detalle_guia(
                    detalle_guia.id
                )
            )

            if liquidacion_existente:
                continue

            # ==========================
            # Precio
            # ==========================

            precio = Decimal(
                detalle_guia.precio
            )

            porcentaje_cobro = Decimal(
                detalle_guia.porcentaje_cobro
            )

            # ==========================
            # Precio a liquidar = precio agencia
            # (precio público × % cobro agencia)
            # ==========================

            precio_a_liquidar = (
                precio
                * porcentaje_cobro
                / Decimal("100")
            ).quantize(
                Decimal("0.01")
            )

            # ==========================
            # Preparar respuesta
            # ==========================

            detalles_response.append(
                {
                    "detalle_guia_id": detalle_guia.id,
                    "producto_id": detalle_guia.producto_id,
                    "producto": detalle_guia.producto.nombre,
                    "cantidad": detalle_guia.cantidad,
                    "precio": precio,
                    "porcentaje_cobro": porcentaje_cobro,
                    "precio_a_liquidar": precio_a_liquidar,
                }
            )

        return {
            "guia_id": guia.id,
            "numero_guia": guia.numero_guia,
            "fecha": guia.fecha,
            "agencia_id": guia.agencia_id,
            "agencia": guia.agencia.nombre,
            "detalles": detalles_response,
        }

    def anular(self, liquidacion_id: int):

        liquidacion = self.repository.get_by_id(
            liquidacion_id
        )

        if not liquidacion:
            raise ValueError(
                "La liquidación no existe."
            )

        if liquidacion.estado == EstadoLiquidacion.ANULADA:
            raise ValueError(
                "La liquidación ya está anulada."
            )

        liquidacion.estado = EstadoLiquidacion.ANULADA

        self.repository.save(liquidacion)

        # ==========================
        # Reingresar a inventario lo vendido
        # ==========================

        self.repository.registrar_ingreso_por_anulacion(liquidacion)

        # ==========================
        # Anular cobranza relacionada
        # ==========================

        cobranza = (
            self.cobranza_repository
            .get_by_liquidacion_id(liquidacion.id)
        )

        if cobranza:
            cobranza.estado = EstadoCobranza.ANULADA

            self.cobranza_repository.save(
                cobranza
            )

        self.actualizar_estado_guia(
            liquidacion.guia_id
        )

        return self.repository.get_by_id(
            liquidacion_id
        )




    def actualizar_estado_guia(self, guia_id: int):

        guia = self.guia_repository.get_by_id(guia_id)

        if not guia:
            raise ValueError(
                "La guía no existe."
            )

        # Una guía anulada no debe modificarse
        if guia.estado == EstadoGuia.ANULADA:
            return

        total_detalles = len(guia.detalles)

        detalles_liquidados = (
            self.repository.count_detalles_liquidados_by_guia(
                guia_id
            )
        )

        if detalles_liquidados == 0:

            nuevo_estado = (
                EstadoGuia.PENDIENTE_LIQUIDACION
            )

        elif detalles_liquidados < total_detalles:

            nuevo_estado = (
                EstadoGuia.PARCIALMENTE_LIQUIDADA
            )

        else:

            nuevo_estado = (
                EstadoGuia.LIQUIDADA
            )

        self.guia_repository.update_estado(
            guia,
            nuevo_estado
        )