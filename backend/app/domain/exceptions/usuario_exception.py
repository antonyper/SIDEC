from app.domain.exceptions.base_exception import BusinessException
from fastapi import status

class UsuarioNotFoundException(BusinessException):
    """Exception raised when a user is not found."""

    def __init__(self):
        message = "El usuario no existe."
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)

class UsuarioDuplicadoException(BusinessException):
    """Exception raised when a user with the same username already exists."""

    def __init__(self, username: str):
        message = f"Ya existe un usuario con el nombre de usuario '{username}'."
        super().__init__(message, status_code=status.HTTP_400_BAD_REQUEST)

class CredencialesInvalidasException(BusinessException):
    """Exception raised when login credentials are invalid."""

    def __init__(self):
        message = "Usuario o contraseña incorrectos."
        super().__init__(message, status_code=status.HTTP_401_UNAUTHORIZED)

class UsuarioInactivoException(BusinessException):
    """Exception raised when a deactivated user tries to log in."""

    def __init__(self):
        message = "El usuario está inactivo."
        super().__init__(message, status_code=status.HTTP_401_UNAUTHORIZED)

class NoAutenticadoException(BusinessException):
    """Exception raised when no valid authentication token is provided."""

    def __init__(self):
        message = "No has iniciado sesión o tu sesión expiró."
        super().__init__(message, status_code=status.HTTP_401_UNAUTHORIZED)
