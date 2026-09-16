from app.core.security import create_access_token, hash_password, verify_password
from app.models.usuario import Usuario
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.usuario_schema import (
    LoginRequest,
    TokenResponse,
    UsuarioCreate,
    UsuarioResponse,
    UsuarioUpdate,
)
from app.domain.exceptions.usuario_exception import (
    CredencialesInvalidasException,
    UsuarioDuplicadoException,
    UsuarioInactivoException,
    UsuarioNotFoundException,
)

class UsuarioService:

    def __init__(self, repository: UsuarioRepository):
        self.repository = repository

    def create(self, data: UsuarioCreate) -> UsuarioResponse:
        if self.repository.get_by_username(data.username):
            raise UsuarioDuplicadoException(data.username)

        usuario = Usuario(
            nombre=data.nombre,
            username=data.username,
            password_hash=hash_password(data.password),
            rol=data.rol,
        )
        usuario = self.repository.create(usuario)
        return UsuarioResponse.model_validate(usuario)

    def get_all(self) -> list[UsuarioResponse]:
        return [UsuarioResponse.model_validate(u) for u in self.repository.get_all()]

    def get_by_id(self, usuario_id: int) -> UsuarioResponse:
        usuario = self.repository.get_by_id(usuario_id)
        if not usuario:
            raise UsuarioNotFoundException()
        return UsuarioResponse.model_validate(usuario)

    def update(self, usuario_id: int, data: UsuarioUpdate) -> UsuarioResponse:
        usuario = self.repository.get_by_id(usuario_id)
        if not usuario:
            raise UsuarioNotFoundException()

        if data.nombre:
            usuario.nombre = data.nombre
        if data.password:
            usuario.password_hash = hash_password(data.password)
        if data.rol is not None:
            usuario.rol = data.rol

        usuario = self.repository.update(usuario)
        return UsuarioResponse.model_validate(usuario)

    def dar_baja(self, usuario_id: int) -> UsuarioResponse:
        usuario = self.repository.get_by_id(usuario_id)
        if not usuario:
            raise UsuarioNotFoundException()
        usuario.activo = False
        usuario = self.repository.update(usuario)
        return UsuarioResponse.model_validate(usuario)

    def reactivar(self, usuario_id: int) -> UsuarioResponse:
        usuario = self.repository.get_by_id(usuario_id)
        if not usuario:
            raise UsuarioNotFoundException()
        usuario.activo = True
        usuario = self.repository.update(usuario)
        return UsuarioResponse.model_validate(usuario)

    def login(self, data: LoginRequest) -> TokenResponse:
        usuario = self.repository.get_by_username(data.username)
        if not usuario or not verify_password(data.password, usuario.password_hash):
            raise CredencialesInvalidasException()
        if not usuario.activo:
            raise UsuarioInactivoException()

        token = create_access_token(subject=str(usuario.id), rol=usuario.rol.value)
        return TokenResponse(
            access_token=token,
            usuario=UsuarioResponse.model_validate(usuario),
        )
