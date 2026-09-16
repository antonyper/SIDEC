from enum import Enum


class EstadoCobranza(str, Enum):
    PENDIENTE = "PENDIENTE"
    COBRADO = "COBRADO"
    ANULADA = "ANULADA"