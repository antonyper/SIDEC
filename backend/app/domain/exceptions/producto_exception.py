from app.domain.exceptions.base_exception import BusinessException
from fastapi import status

class ProductoNotFoundException(BusinessException):
    """Exception raised when a product is not found."""
    
    def __init__(self):
        message = f"El producto no existe."
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)

class ProductoCodigoDuplicadoException(BusinessException):
    """Exception raised when a product with the same code already exists."""
    
    def __init__(self, codigo: str):
        message = f"Ya existe un producto con el código '{codigo}'."
        super().__init__(message, status_code=status.HTTP_400_BAD_REQUEST)
                