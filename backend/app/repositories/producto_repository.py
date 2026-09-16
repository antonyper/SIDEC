from sqlalchemy.orm import Session
from app.models.producto import Producto
from sqlalchemy import or_, select

class ProductoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self,
        nombre: str | None = None,
        categoria: str | None = None,
        estado: str | None = None,
        precio: float | None = None,
        buscar: str | None = None,
    ) -> list[Producto]:
        statement = select(Producto).where(Producto.eliminado.is_(False))
        if buscar:
            statement = statement.where(
                or_(
                    Producto.nombre.ilike(f"%{buscar}%"),
                    Producto.categoria.ilike(f"%{buscar}%"),
                )
            )
        if nombre:
            statement = statement.where(
                Producto.nombre.ilike(f"%{nombre}%"))
        if categoria:
            statement = statement.where(
                Producto.categoria.ilike(f"%{categoria}%"))
        if estado:
            statement = statement.where(
                Producto.estado == estado)
        if precio:
            statement = statement.where(
                Producto.precio == precio)
        statement = statement.order_by(Producto.nombre)

        return list(self.db.scalars(statement))
        

    def get_by_id(self, producto_id: str) -> Producto | None:
        statement = select(Producto).where(Producto.id == producto_id)
        return self.db.scalar(statement)

    def create(self, producto: Producto) -> Producto:
        self.db.add(producto)
        self.db.commit()
        self.db.refresh(producto)
        return producto

    def update(
        self,
        producto: Producto,
    ) -> Producto:
        self.db.commit()
        self.db.refresh(producto)
        return producto

    def eliminar(self, producto: Producto) -> None:
        producto.eliminado = True
        self.db.commit()
    
    def generar_codigo(self) -> str:
        statement = (
            select(Producto)
            .order_by(Producto.id.desc())
        )
        last_producto = self.db.scalar(statement)
        if last_producto:
            last_id = int(last_producto.codigo[1:])
            last_id = last_id + 1
        else:
            last_id = 1
        return f"P{last_id:03d}"