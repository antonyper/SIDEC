from enum import Enum


class TipoMovimientoInventario(str, Enum):
    STOCK_INICIAL = "STOCK_INICIAL"
    INGRESO = "INGRESO"
    SALIDA_GUIA = "SALIDA_GUIA"
    DEVOLUCION = "DEVOLUCION"
