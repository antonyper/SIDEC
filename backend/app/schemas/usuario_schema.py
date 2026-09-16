from datetime import datetime

from app.schemas.base_schema import BaseSchema
from app.enums.rol_usuario import RolUsuario

# ==========================
# Commands
# ==========================

class UsuarioCreate(BaseSchema):
    nombre: str
    username: str
    password: str
    rol: RolUsuario = RolUsuario.OPERADOR

class UsuarioUpdate(BaseSchema):
    nombre: str | None = None
    password: str | None = None
    rol: RolUsuario | None = None

class LoginRequest(BaseSchema):
    username: str
    password: str

# ==========================
# Queries
# ==========================

class UsuarioResponse(BaseSchema):
    id: int
    nombre: str
    username: str
    rol: RolUsuario
    activo: bool
    created_at: datetime

class TokenResponse(BaseSchema):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioResponse
