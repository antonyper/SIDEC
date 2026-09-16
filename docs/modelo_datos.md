# Modelo de Datos — SIDEC

Este documento refleja el esquema real de PostgreSQL, verificado el 12 de
septiembre de 2026. La migración aplicada es `bb7815f5e997`.

Todas las tablas funcionales usan `id` como clave primaria. Salvo `producto`,
que permite nulos en sus marcas de tiempo, todas incluyen `created_at` y
`updated_at` obligatorios. `alembic_version` es una tabla técnica para el
control de migraciones y no forma parte del negocio.

## Agencia (`agencias`)

| Campo | Tipo | Obligatorio | Notas |
| --- | --- | --- | --- |
| `id` | entero | Sí | Clave primaria. |
| `codigo` | texto | Sí | Único. |
| `nombre` | texto | Sí |  |
| `telefono`, `direccion` | texto | No |  |
| `agente`, `propietario` | texto | No |  |
| `estado` | enum `estado` | Sí | Actualmente: `ACTIVO`. |
| `created_at`, `updated_at` | fecha y hora con zona | Sí | Auditoría. |

## Producto (`producto`)

| Campo | Tipo | Obligatorio | Notas |
| --- | --- | --- | --- |
| `id` | entero | Sí | Clave primaria. |
| `codigo` | texto | Sí | Único. |
| `nombre` | texto | Sí |  |
| `categoria` | texto | No |  |
| `precio` | decimal (10,2) | Sí | Precio vigente. |
| `estado` | enum `estado` | Sí | Actualmente: `ACTIVO`. |
| `created_at`, `updated_at` | fecha y hora con zona | No | La base actual permite nulos. |

## Guía (`guia`)

| Campo | Tipo | Obligatorio | Notas |
| --- | --- | --- | --- |
| `id` | entero | Sí | Clave primaria. |
| `numero_guia` | texto | Sí | Único. |
| `fecha` | fecha | Sí | Fecha de emisión registrada. |
| `estado` | enum `estadoguia` | Sí | Ver estados abajo. |
| `agencia_id` | entero | Sí | FK a `agencias.id`. |
| `observacion` | texto | No |  |
| `created_at`, `updated_at` | fecha y hora con zona | Sí | `created_at` define el plazo de 30 días. |

Estados: `PENDIENTE`, `PENDIENTE_LIQUIDACION`,
`PARCIALMENTE_LIQUIDADA`, `LIQUIDADA` y `ANULADA`.

## Detalle de guía (`detalle_guia`)

| Campo | Tipo | Obligatorio | Notas |
| --- | --- | --- | --- |
| `id` | entero | Sí | Clave primaria. |
| `guia_id` | entero | Sí | FK a `guia.id`. |
| `producto_id` | entero | Sí | FK a `producto.id`. |
| `cantidad` | decimal (10,2) | Sí | Cantidad repartida. |
| `precio` | decimal (10,2) | Sí | Precio aplicado. |
| `porcentaje_cobro` | decimal (5,2) | Sí |  |
| `created_at`, `updated_at` | fecha y hora con zona | Sí | Auditoría. |

## Liquidación (`liquidaciones`)

Una liquidación pertenece a una guía; la agencia se obtiene a través de esa
guía y no existe una columna `agencia_id` directa.

| Campo | Tipo | Obligatorio | Notas |
| --- | --- | --- | --- |
| `id` | entero | Sí | Clave primaria. |
| `fecha` | fecha | Sí | Fecha de liquidación. |
| `guia_id` | entero | Sí | FK a `guia.id`. |
| `estado` | enum `estadoliquidacion` | Sí | `ACTIVA` o `ANULADA`. |
| `observacion` | texto | No |  |
| `created_at`, `updated_at` | fecha y hora con zona | Sí | Auditoría. |

## Detalle de liquidación (`detalle_liquidaciones`)

| Campo | Tipo | Obligatorio | Notas |
| --- | --- | --- | --- |
| `id` | entero | Sí | Clave primaria. |
| `liquidacion_id` | entero | Sí | FK a `liquidaciones.id`. |
| `detalle_guia_id` | entero | Sí | FK a `detalle_guia.id`. |
| `cantidad_vendida` | entero | Sí |  |
| `cantidad_devuelta` | entero | Sí | Aumenta el inventario. |
| `total` | decimal (10,2) | Sí |  |
| `created_at`, `updated_at` | fecha y hora con zona | Sí | Auditoría. |

## Cobranza (`cobranzas`)

La implementación actual permite como máximo una cobranza por liquidación:
`liquidacion_id` tiene una restricción única. No existen aún las tablas
`detalle_cobranza` ni una cobranza asociada a varias liquidaciones.

| Campo | Tipo | Obligatorio | Notas |
| --- | --- | --- | --- |
| `id` | entero | Sí | Clave primaria. |
| `liquidacion_id` | entero | Sí | FK única a `liquidaciones.id`. |
| `monto`, `monto_pagado`, `monto_pendiente` | decimal (10,2) | Sí | Importes de la cobranza. |
| `estado` | enum `estadocobranza` | Sí | `PENDIENTE`, `COBRADO` o `ANULADA`. |
| `created_at`, `updated_at` | fecha y hora con zona | Sí | Auditoría. |

## Movimiento de inventario (`movimientos_inventario`)

Cada variación de existencias queda registrada como un movimiento. El stock no
es un número editable: se calcula a partir del historial.

| Campo | Tipo | Obligatorio | Notas |
| --- | --- | --- | --- |
| `id` | entero | Sí | Clave primaria. |
| `producto_id` | entero | Sí | FK a `producto.id`. |
| `tipo` | enum `tipomovimientoinventario` | Sí | Ver tipos abajo. |
| `cantidad` | decimal (10,2) | Sí | Debe ser mayor que cero. |
| `fecha` | fecha | Sí | Fecha del movimiento. |
| `observacion` | texto | No |  |
| `detalle_guia_id` | entero | No | FK única; identifica la salida por guía. |
| `detalle_liquidacion_id` | entero | No | FK única; identifica la devolución. |
| `created_at`, `updated_at` | fecha y hora con zona | Sí | Auditoría. |

Tipos de movimiento:

* `STOCK_INICIAL`: cantidad con la que se empieza a controlar el producto.
* `INGRESO`: reposición o entrada posterior al almacén.
* `SALIDA_GUIA`: producto repartido a una agencia; resta stock.
* `DEVOLUCION`: producto devuelto durante una liquidación; suma stock.

```text
stock = STOCK_INICIAL + INGRESO + DEVOLUCION - SALIDA_GUIA
```

Si aún no se declara stock inicial, una salida por guía puede dejar el saldo
negativo. Esto permite empezar a registrar repartos y añadir el stock inicial
más adelante sin perder el historial.

## Relaciones reales

```text
Agencia 1 ─── N Guía
Guía 1 ────── N DetalleGuia
Producto 1 ─── N DetalleGuia
Guía 1 ────── N Liquidación
Liquidación 1 ─ N DetalleLiquidacion
DetalleGuia 1 ─ N DetalleLiquidacion
Liquidación 1 ─ 0..1 Cobranza
Producto 1 ─── N MovimientoInventario
DetalleGuia 1 ─ 0..1 MovimientoInventario de salida
DetalleLiquidacion 1 ─ 0..1 MovimientoInventario de devolución
```

## Restricciones principales

* Son únicos: `agencias.codigo`, `producto.codigo`, `guia.numero_guia`,
  `cobranzas.liquidacion_id`, `movimientos_inventario.detalle_guia_id` y
  `movimientos_inventario.detalle_liquidacion_id`.
* Las claves foráneas protegen todas las relaciones indicadas.
* La cantidad de un movimiento de inventario debe ser estrictamente positiva.
