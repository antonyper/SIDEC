from app.enums.estado_guia import EstadoGuia
from app.models.guia import Guia
from app.repositories.guia_repository import GuiaRepository
from app.schemas.guia_schema import GuiaCreate, GuiaUpdate


class GuiaService:

    def __init__(self, repository: GuiaRepository):
        self.repository = repository

    def get_all(self):
        self.repository.actualizar_guias_pendientes_vencidas()
        return self.repository.get_all()

    def get_by_id(self, guia_id: int):
        self.repository.actualizar_guias_pendientes_vencidas()
        guia = self.repository.get_by_id(guia_id)

        if not guia:
            raise ValueError("La guía no existe.")

        return guia

    def actualizar_guias_pendientes_vencidas(self) -> int:
        return self.repository.actualizar_guias_pendientes_vencidas()

    def create(self, guia_data: GuiaCreate):
        ultimo = self.repository.get_last()

        if ultimo:
            numero = int(ultimo.numero_guia[1:]) + 1
        else:
            numero = 1

        numero_guia = f"G{numero:06d}"

        return self.repository.create(
            guia_data=guia_data,
            numero_guia=numero_guia
        )

    def update(self, guia_id: int, guia_data: GuiaUpdate):
        guia = self.get_by_id(guia_id)

        return self.repository.update(
            guia,
            guia_data
        )

    def delete(self, guia_id: int):
        guia = self.get_by_id(guia_id)

        if guia.estado in (
            EstadoGuia.PARCIALMENTE_LIQUIDADA,
            EstadoGuia.LIQUIDADA,
        ):
            raise ValueError("No se puede eliminar una guía que este liquidada.")

        guia.estado = EstadoGuia.ANULADA

        return self.repository.update(
            guia,
            GuiaUpdate()
        )
