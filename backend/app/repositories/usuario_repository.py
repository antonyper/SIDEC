from sqlalchemy.orm import Session
from app.models.usuario import Usuario
from sqlalchemy import select

class UsuarioRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Usuario]:
        statement = select(Usuario).order_by(Usuario.nombre)
        return list(self.db.scalars(statement))

    def get_by_id(self, usuario_id: int) -> Usuario | None:
        statement = select(Usuario).where(Usuario.id == usuario_id)
        return self.db.scalar(statement)

    def get_by_username(self, username: str) -> Usuario | None:
        statement = select(Usuario).where(Usuario.username == username)
        return self.db.scalar(statement)

    def create(self, usuario: Usuario) -> Usuario:
        self.db.add(usuario)
        self.db.commit()
        self.db.refresh(usuario)
        return usuario

    def update(self, usuario: Usuario) -> Usuario:
        self.db.commit()
        self.db.refresh(usuario)
        return usuario
