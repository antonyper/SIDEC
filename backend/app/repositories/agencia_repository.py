from sqlalchemy.orm import Session
from app.models.agencia import Agencia
from sqlalchemy import select

class AgenciaRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self,
        nombre: str | None = None,
        propietario: str | None = None,
        estado: str | None = None,
    ) -> list[Agencia]:
        statement = select(Agencia)
        if nombre:
            statement = statement.where(
                Agencia.nombre.ilike(f"%{nombre}%"))
        if propietario:
            statement = statement.where(
                Agencia.propietario.ilike(f"%{propietario}%"))
        if estado:
            statement = statement.where(
                Agencia.estado == estado)
        statement = statement.order_by(Agencia.nombre)

        return list(self.db.scalars(statement))
        

    def get_by_id(self, agencia_id: str) -> Agencia | None:
        statement = select(Agencia).where(Agencia.id == agencia_id)
        return self.db.scalar(statement)

    def create(self, agencia: Agencia) -> Agencia:
        self.db.add(agencia)
        self.db.commit()
        self.db.refresh(agencia)
        return agencia
    
    def update(
        self,
        agencia: Agencia,
    ) -> Agencia:
        self.db.commit()
        self.db.refresh(agencia)
        return agencia

    # def update_agencia(self, agencia: Agencia) -> Agencia:
    #     self.db.commit()
    #     self.db.refresh(agencia)
    #     return agencia

    # def delete_agencia(self, agencia: Agencia) -> None:
    #     self.db.delete(agencia)
    #     self.db.commit()