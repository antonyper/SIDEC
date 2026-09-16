from app.models.producto import Producto
from app.repositories.producto_repository import ProductoRepository
from app.schemas.producto_schema import ProductoCreate, ProductoResponse, ProductoListResponse, ProductoUpdate
from app.domain.exceptions.producto_exception import ProductoNotFoundException, ProductoCodigoDuplicadoException
from app.enums.estado import Estado
from decimal import Decimal

class ProductoService:

    def __init__(self, repository: ProductoRepository):
        self.repository = repository


    def create(self, data: ProductoCreate) -> ProductoResponse:
        
        producto = Producto(
            codigo=self.repository.generar_codigo(),
            nombre=data.nombre,
            categoria=data.categoria,
            precio=data.precio,
        )
        producto = self.repository.create(producto)
        return ProductoResponse.model_validate(producto)
    
    def get_all(
        self,
        nombre: str | None = None,
        categoria: str | None = None,
        estado: Estado | None = None,
        precio: Decimal | None = None,
        buscar: str | None = None,
    ) -> list[ProductoListResponse]:

        productos = self.repository.get_all(
            nombre,
            categoria,
            estado,
            precio,
            buscar,
        )

        return [
            ProductoListResponse.model_validate(producto)
            for producto in productos
        ]
    def get_by_id(self, producto_id: int) -> ProductoResponse:
        producto = self.repository.get_by_id(producto_id)
        if not producto:
            raise ProductoNotFoundException()
        return ProductoResponse.model_validate(producto)
    
    def update(
        self, 
        producto_id: int, 
        data: ProductoUpdate 
    ) -> ProductoResponse:

        producto = self.repository.get_by_id(producto_id)
        if not producto:
            raise ProductoNotFoundException()

        producto.nombre = data.nombre or producto.nombre
        producto.categoria = data.categoria or producto.categoria
        producto.precio = data.precio or producto.precio

        producto = self.repository.update(producto)
        return ProductoResponse.model_validate(producto)
    
    def dar_baja(self, producto_id: int) -> ProductoResponse:
        producto = self.repository.get_by_id(producto_id)
        if not producto:
            raise ProductoNotFoundException()
        
        producto.estado = Estado.INACTIVO
        producto = self.repository.update(producto)
        return ProductoResponse.model_validate(producto)
    
    def reactivar(self, producto_id: int) -> ProductoResponse:
        producto = self.repository.get_by_id(producto_id)
        if not producto:
            raise ProductoNotFoundException()

        producto.estado = Estado.ACTIVO
        producto = self.repository.update(producto)
        return ProductoResponse.model_validate(producto)

    def eliminar(self, producto_id: int) -> None:
        producto = self.repository.get_by_id(producto_id)
        if not producto:
            raise ProductoNotFoundException()

        self.repository.eliminar(producto)