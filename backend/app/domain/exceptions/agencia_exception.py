from app.domain.exceptions.base_exception import BusinessException
from fastapi import status

class AgenciaNotFoundException(BusinessException):
    """Exception raised when an agency is not found."""
    
    def __init__(self):
        message = f"La agencia no existe."
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)

class AgenciaCodigoDuplicadoException(BusinessException):
    """Exception raised when an agency with the same code already exists."""
    
    def __init__(self, codigo: str):
        message = f"Ya existe una agencia con el código '{codigo}'."
        super().__init__(message, status_code=status.HTTP_400_BAD_REQUEST)
        