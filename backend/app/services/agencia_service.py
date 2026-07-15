from app.models.agencia import Agencia
from app.repositories.agencia_repository import AgenciaRepository
from app.schemas.agencia_schema import AgenciaCreate, AgenciaResponse, AgenciaListResponse, AgenciaUpdate
from app.domain.exceptions.agencia_exception import AgenciaNotFoundException, AgenciaCodigoDuplicadoException


class AgenciaService:

    def __init__(self, repository: AgenciaRepository):
        self.repository = repository

    def _generar_codigo(self) -> str:
        """Genera un código único para la agencia. Temporal
        """
        return "A001"  # Ejemplo simple, se puede mejorar para generar códigos únicos

    def create(self, data: AgenciaCreate) -> AgenciaResponse:
        
        agencia = Agencia(
            codigo=self._generar_codigo(),
            nombre=data.nombre,
            propietario=data.propietario,
            telefono=data.telefono,
            direccion=data.direccion,
        )
        agencia = self.repository.create(agencia)
        return AgenciaResponse.model_validate(agencia)
    
    def get_all(
        self,
        nombre: str | None = None,
        propietario: str | None = None,
        estado: Estado | None = None,
    ) -> list[AgenciaListResponse]:

        agencias = self.repository.get_all(
            nombre,
            propietario,
            estado,
        )

        return [
            AgenciaListResponse.model_validate(a)
            for a in agencias
        ]
    def get_by_id(self, agencia_id: int) -> AgenciaResponse:
        agencia = self.repository.get_by_id(agencia_id)
        if not agencia:
            raise AgenciaNotFoundException()
        return AgenciaResponse.model_validate(agencia)
    
    def update(
        self, 
        agencia_id: int, 
        data: AgenciaUpdate 
    ) -> AgenciaResponse:

        agencia = self.repository.get_by_id(agencia_id)
        if not agencia:
            raise AgenciaNotFoundException()

        agencia.nombre = data.nombre or agencia.nombre
        agencia.propietario = data.propietario or agencia.propietario
        agencia.agente = data.agente or agencia.agente
        agencia.telefono = data.telefono or agencia.telefono
        agencia.direccion = data.direccion or agencia.direccion 

        agencia = self.repository.update(agencia)
        return AgenciaResponse.model_validate(agencia)
    
    def dar_baja(self, agencia_id: int) -> AgenciaResponse:
        agencia = self.repository.get_by_id(agencia_id)
        if not agencia:
            raise AgenciaNotFoundException()
        
        agencia.estado = Estado.INACTIVO
        agencia = self.repository.update(agencia)
        return AgenciaResponse.model_validate(agencia)
    
    def reactivar(self, agencia_id: int) -> AgenciaResponse:
        agencia = self.repository.get_by_id(agencia_id)
        if not agencia:
            raise AgenciaNotFoundException()
        
        agencia.estado = Estado.ACTIVO
        agencia = self.repository.update(agencia)
        return AgenciaResponse.model_validate(agencia) 