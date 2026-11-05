"""Datos de arranque: usuario ADMIN adicional y datos demo para un entorno de prueba.

Todo pasa por los services de la app, nunca por SQL directo: así el seed respeta las mismas
reglas que la API (salidas de inventario por guía, estado de la guía según sus liquidaciones,
cobranza implícita al liquidar). Si una regla cambia, el seed la sigue sin tocarlo.
"""
import logging
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.enums.rol_usuario import RolUsuario
from app.enums.tipo_movimiento_inventario import TipoMovimientoInventario
from app.models.agencia import Agencia
from app.models.movimiento_inventario import MovimientoInventario
from app.models.usuario import Usuario
from app.repositories.agencia_repository import AgenciaRepository
from app.repositories.cobranza_repository import CobranzaRepository
from app.repositories.guia_repository import GuiaRepository
from app.repositories.liquidacion_repository import LiquidacionRepository
from app.repositories.producto_repository import ProductoRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.agencia_schema import AgenciaCreate
from app.schemas.cobranza_schema import CobranzaUpdate
from app.schemas.detalle_guia_schema import DetalleGuiaCreate
from app.schemas.detalle_liquidacion_schema import DetalleLiquidacionCreate
from app.schemas.guia_schema import GuiaCreate
from app.schemas.liquidacion_schema import LiquidacionCreate
from app.schemas.producto_schema import ProductoCreate
from app.services.agencia_service import AgenciaService
from app.services.cobranza_service import CobranzaService
from app.services.guia_service import GuiaService
from app.services.liquidacion_service import LiquidacionService
from app.services.producto_service import ProductoService

logger = logging.getLogger(__name__)


# ==========================
# Usuario ADMIN adicional
# ==========================

def crear_admin_seed(db: Session) -> bool:
    """Crea el ADMIN de SIDEC_SEED_ADMIN_USERNAME si todavía no existe.

    A diferencia del ADMIN inicial, no depende de que la tabla esté vacía: sirve para dar
    una cuenta nominal a quien prueba sin compartir la de `admin`. Nunca modifica un usuario
    existente (no resetea contraseñas).
    """
    username = settings.SIDEC_SEED_ADMIN_USERNAME
    if not username:
        return False
    if not settings.SIDEC_SEED_ADMIN_PASSWORD:
        logger.warning("SIDEC_SEED_ADMIN_USERNAME='%s' sin SIDEC_SEED_ADMIN_PASSWORD: no se crea.", username)
        return False
    if UsuarioRepository(db).get_by_username(username):
        return False

    db.add(
        Usuario(
            nombre=settings.SIDEC_SEED_ADMIN_NOMBRE,
            username=username,
            password_hash=hash_password(settings.SIDEC_SEED_ADMIN_PASSWORD),
            rol=RolUsuario.ADMIN,
        )
    )
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return False

    logger.info("ADMIN '%s' creado por el seed.", username)
    return True


# ==========================
# Datos demo
# ==========================

# (nombre, categoría, precio público)
PRODUCTOS_DEMO = [
    ("El Comercio", "Diarios", "3.50"),
    ("Gestión", "Diarios", "4.00"),
    ("Perú21", "Diarios", "1.00"),
    ("Trome", "Diarios", "0.80"),
    ("Ojo", "Diarios", "0.80"),
    ("Somos", "Revistas", "6.00"),
]

# (nombre, propietario, agente, teléfono, dirección, ruta, latitud, longitud)
AGENCIAS_DEMO = [
    ("Agencia Miraflores", "Rosa Quispe", "Carlos Díaz", "987654321", "Av. Larco 345, Miraflores", "Ruta Sur", "-12.121900", "-77.029700"),
    ("Agencia San Isidro", "Luis Torres", "Carlos Díaz", "987111222", "Av. Arequipa 2450, San Isidro", "Ruta Sur", "-12.097500", "-77.036500"),
    ("Agencia Surco", "Ana Mendoza", "Jorge Ramos", "986333444", "Av. Primavera 890, Surco", "Ruta Sur", "-12.110200", "-76.989400"),
    ("Agencia Los Olivos", "Pedro Huamán", "Jorge Ramos", "985555666", "Av. Universitaria 6550, Los Olivos", "Ruta Norte", "-11.957800", "-77.071400"),
    ("Agencia San Juan de Lurigancho", "María Flores", "Elena Castro", "984777888", "Av. Próceres 1200, SJL", "Ruta Este", "-12.000600", "-77.005600"),
    ("Agencia Callao", "Jorge Vargas", "Elena Castro", "983999000", "Av. Sáenz Peña 560, Callao", "Ruta Oeste", "-12.056400", "-77.118100"),
]

# Cada guía: (agencia, días atrás, [(producto, cantidad, % cobro)], escenario)
# Escenarios: "en_venta" (reciente), "vencida" (>30 días sin liquidar), "liquidada_cobrada",
# "liquidada_parcialmente_cobrada", "parcial" (un detalle liquidado), "liquidacion_anulada",
# "anulada".
GUIAS_DEMO = [
    (0, 3, [("El Comercio", 60, "80"), ("Trome", 120, "75")], "en_venta"),
    (1, 5, [("Gestión", 40, "80"), ("Perú21", 90, "75")], "en_venta"),
    (2, 2, [("Somos", 25, "70"), ("El Comercio", 50, "80")], "en_venta"),
    (3, 40, [("Trome", 150, "75"), ("Ojo", 100, "75")], "vencida"),
    (4, 45, [("Perú21", 80, "75"), ("Trome", 140, "75")], "vencida"),
    (0, 20, [("El Comercio", 70, "80"), ("Somos", 30, "70")], "liquidada_cobrada"),
    (1, 18, [("Gestión", 45, "80")], "liquidada_cobrada"),
    (5, 25, [("Trome", 130, "75"), ("Ojo", 90, "75")], "liquidada_parcialmente_cobrada"),
    (2, 15, [("El Comercio", 55, "80"), ("Perú21", 85, "75")], "parcial"),
    (3, 12, [("Somos", 20, "70"), ("Gestión", 35, "80")], "liquidacion_anulada"),
    (4, 8, [("Ojo", 60, "75")], "anulada"),
    (5, 55, [("El Comercio", 65, "80"), ("Trome", 110, "75")], "liquidada_cobrada"),
]

STOCK_INICIAL = Decimal("800")
INGRESO_REPOSICION = Decimal("300")


def _devolucion(cantidad: int) -> int:
    """Devuelve ~20 % de lo entregado: un consignatario típico no vende todo."""
    return cantidad // 5


def cargar_datos_demo(db: Session) -> bool:
    """Carga datos demo si la base no tiene agencias. Idempotente: no toca una base con datos."""
    if db.scalar(select(func.count()).select_from(Agencia)):
        return False

    hoy = date.today()
    agencia_service = AgenciaService(AgenciaRepository(db))
    producto_service = ProductoService(ProductoRepository(db))
    guia_service = GuiaService(GuiaRepository(db))
    cobranza_service = CobranzaService(CobranzaRepository(db))
    liquidacion_service = LiquidacionService(
        LiquidacionRepository(db),
        GuiaRepository(db),
        CobranzaRepository(db),
    )

    productos = {}
    for nombre, categoria, precio in PRODUCTOS_DEMO:
        producto = producto_service.create(ProductoCreate(nombre=nombre, categoria=categoria, precio=float(precio)))
        productos[nombre] = producto
        # Mismo registro que POST /inventario/movimientos (solo STOCK_INICIAL e INGRESO son manuales).
        db.add(MovimientoInventario(
            producto_id=producto.id,
            tipo=TipoMovimientoInventario.STOCK_INICIAL,
            cantidad=STOCK_INICIAL,
            fecha=hoy - timedelta(days=60),
            observacion="Stock inicial (datos demo)",
        ))
        db.add(MovimientoInventario(
            producto_id=producto.id,
            tipo=TipoMovimientoInventario.INGRESO,
            cantidad=INGRESO_REPOSICION,
            fecha=hoy - timedelta(days=21),
            observacion="Reposición (datos demo)",
        ))
    db.commit()

    agencias = [
        agencia_service.create(AgenciaCreate(
            nombre=nombre, propietario=propietario, agente=agente, telefono=telefono,
            direccion=direccion, ruta=ruta, latitud=Decimal(latitud), longitud=Decimal(longitud),
        ))
        for nombre, propietario, agente, telefono, direccion, ruta, latitud, longitud in AGENCIAS_DEMO
    ]

    for indice_agencia, dias_atras, lineas, escenario in GUIAS_DEMO:
        fecha_guia = hoy - timedelta(days=dias_atras)
        guia = guia_service.create(GuiaCreate(
            fecha=fecha_guia,
            agencia_id=agencias[indice_agencia].id,
            observacion=f"Datos demo: {escenario.replace('_', ' ')}",
            detalles=[
                DetalleGuiaCreate(
                    producto_id=productos[producto].id,
                    cantidad=cantidad,
                    precio=Decimal(next(p for n, _, p in PRODUCTOS_DEMO if n == producto)),
                    porcentaje_cobro=Decimal(porcentaje),
                )
                for producto, cantidad, porcentaje in lineas
            ],
        ))

        if escenario in ("en_venta", "vencida"):
            # "vencida" pasa sola a PENDIENTE_LIQUIDACION (tarea diaria / al listar guías).
            continue

        if escenario == "anulada":
            guia_service.delete(guia.id)
            continue

        detalles = guia.detalles
        if escenario == "parcial":
            # Solo el primer detalle: la guía queda PARCIALMENTE_LIQUIDADA.
            detalles = detalles[:1]

        fecha_liquidacion = min(fecha_guia + timedelta(days=7), hoy)
        pago_a_cuenta = Decimal("0")
        if escenario in ("liquidada_parcialmente_cobrada", "parcial"):
            pago_a_cuenta = Decimal("50.00")

        liquidacion = liquidacion_service.create(LiquidacionCreate(
            fecha=fecha_liquidacion,
            guia_id=guia.id,
            pago_a_cuenta=pago_a_cuenta,
            observacion="Datos demo",
            detalles=[
                DetalleLiquidacionCreate(detalle_guia_id=d.id, cantidad_devuelta=_devolucion(d.cantidad))
                for d in detalles
            ],
        ))

        if escenario == "liquidada_parcialmente_cobrada":
            # Segundo pago acumulado, todavía sin cubrir el total: la cobranza sigue PENDIENTE.
            cobranza = cobranza_service.get_by_liquidacion_id(liquidacion.id)
            cobranza_service.update(cobranza.id, CobranzaUpdate(monto_pagado=Decimal("80.00")))
        elif escenario == "liquidacion_anulada":
            # Anula la liquidación y su cobranza; la guía vuelve a PENDIENTE_LIQUIDACION.
            liquidacion_service.anular(liquidacion.id)

    guia_service.actualizar_guias_pendientes_vencidas()
    logger.info(
        "Datos demo cargados: %s productos, %s agencias, %s guías.",
        len(PRODUCTOS_DEMO), len(AGENCIAS_DEMO), len(GUIAS_DEMO),
    )
    return True
