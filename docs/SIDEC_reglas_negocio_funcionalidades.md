# SIDEC — Reglas de Negocio y Funcionalidades Implementadas

## Estado del documento

Este documento consolida las reglas de negocio y funcionalidades que hemos definido e implementado hasta el momento en SIDEC, organizadas por módulo/sprint.

> **Importante:** los módulos indicados como cerrados corresponden a funcionalidades que ya fueron probadas correctamente mediante Swagger.

---

# 1. Guías

## Funcionalidades

- Crear guías.
- Consultar/listar guías.
- Consultar una guía por ID.
- Actualizar una guía.
- Gestionar los detalles de una guía.
- El estado de la guía se relaciona con el proceso de liquidación.

## Reglas de negocio

### Detalles de guía

Cada guía puede contener múltiples `DetalleGuia`.

Un detalle representa un producto dentro de la guía y contiene, entre otros:

- `producto_id`
- `cantidad`
- `precio`
- `porcentaje_cobro`

### Actualización de detalles

La actualización de una guía debe conservar los IDs existentes de los detalles.

El frontend envía nuevamente todos los detalles de la guía cuando modifica uno de ellos. El backend debe reconciliar los detalles recibidos con los existentes utilizando `detalle_guia_id`.

No se deben eliminar y recrear indiscriminadamente todos los detalles de una guía cuando existen liquidaciones activas relacionadas.

### Detalles con liquidación activa

Un `DetalleGuia` que pertenece a una liquidación activa no puede:

- ser eliminado de la guía;
- ser modificado en sus datos relevantes.

Esto evita romper las referencias de `DetalleLiquidacion`.

Si la liquidación relacionada fue anulada y no existe otra liquidación activa sobre ese detalle, el detalle vuelve a poder modificarse/eliminarse según las reglas normales de actualización de la guía.

---

# 2. Liquidaciones — Sprint 4

**Estado: CERRADO Y PROBADO**

## Funcionalidades

- Crear liquidaciones.
- Listar liquidaciones.
- Obtener una liquidación por ID.
- Obtener información de una guía para liquidarla.
- Actualizar liquidaciones.
- Anular liquidaciones.
- Realizar liquidaciones parciales por producto/detalle.
- Calcular automáticamente los importes de los detalles.
- Actualizar el estado de la guía según su avance de liquidación.
- Crear automáticamente una cobranza asociada al crear una liquidación.

## Reglas de negocio

### Liquidación de una guía

Una guía puede tener múltiples visitas/liquidaciones.

Por lo tanto, una guía no queda limitada a una única liquidación.

### Liquidación parcial

La liquidación parcial se realiza por `DetalleGuia`/producto.

**No se maneja liquidación parcial por unidades.**

Es decir, la unidad de selección para liquidar es el detalle de la guía.

### Detalle ya liquidado

Una vez que un `DetalleGuia` pertenece a una liquidación activa, no puede volver a liquidarse.

Esto evita duplicar la liquidación del mismo producto/detalle.

### Cantidad devuelta y vendida

El frontend envía:

```text
cantidad_devuelta
```

El backend calcula:

```text
cantidad_vendida = cantidad_entregada - cantidad_devuelta
```

No se utiliza `cantidad_pendiente`.

### DetalleLiquidacion

Un detalle de liquidación contiene:

- `liquidacion_id`
- `detalle_guia_id`
- `cantidad_vendida`
- `cantidad_devuelta`
- `total`

### Estado de liquidación

Los estados definidos son:

```text
ACTIVA
ANULADA
```

Una liquidación se crea como `ACTIVA`.

Una liquidación activa puede ser anulada y pasa a `ANULADA`.

Una liquidación ya anulada no puede volver a anularse.

### Estado de la guía

El estado de la guía se determina según sus detalles liquidados activamente:

```text
0 detalles liquidados
    ↓
PENDIENTE_LIQUIDACION

Algunos detalles liquidados
    ↓
PARCIALMENTE_LIQUIDADA

Todos los detalles liquidados
    ↓
LIQUIDADA
```

El estado de la guía se actualiza al:

- crear una liquidación;
- anular una liquidación.

**Modificar una liquidación no cambia el estado de la guía.**

### Anulación de liquidación

Al anular una liquidación:

1. La liquidación pasa a `ANULADA`.
2. Se anula la cobranza asociada.
3. Se recalcula el estado de la guía.
4. Los `DetalleGuia` relacionados dejan de estar bloqueados por esa liquidación, siempre que no exista otra liquidación activa que los utilice.

---

# 3. Cobranzas — Sprint 5

**Estado: CERRADO Y PROBADO**

## Concepto

La cobranza es implícita a una liquidación.

Cada vez que se crea una liquidación, se genera automáticamente una cobranza asociada.

No se crea la cobranza manualmente desde el frontend.

## Relación

La relación definida es:

```text
Liquidacion 1 ───── 1 Cobranza
```

`Cobranza` utiliza:

```text
liquidacion_id
```

como referencia a la liquidación.

No se agrega `guia_id` ni `detalle_guia_id` a `Cobranza`, porque la cobranza corresponde a la liquidación completa.

La guía puede obtenerse mediante:

```text
Cobranza
   ↓
Liquidacion
   ↓
guia_id
```

Esto evita duplicar la fuente de verdad.

## Datos de una cobranza

Una cobranza contiene:

- `liquidacion_id`
- `monto`
- `monto_pagado`
- `monto_pendiente`
- `estado`

## Estados

Los estados definidos son:

```text
PENDIENTE
COBRADO
ANULADA
```

## Pago a cuenta al crear una liquidación

La ventana de Liquidación tiene el campo opcional:

```text
pago_a_cuenta
```

El frontend envía `pago_a_cuenta`.

El backend calcula:

```text
monto
monto_pagado
monto_pendiente
estado
```

El frontend no envía directamente `monto_pagado` para crear la cobranza.

### Caso 1 — Pago a cuenta parcial

Ejemplo:

```text
Monto de liquidación: S/ 1,000
Pago a cuenta:        S/   500
```

Resultado:

```text
monto:           S/ 1,000
monto_pagado:    S/   500
monto_pendiente: S/   500
estado:          PENDIENTE
```

### Caso 2 — Sin pago a cuenta

Si `pago_a_cuenta` está vacío o es `0`:

Se considera que la liquidación fue cobrada completamente.

Ejemplo:

```text
Monto de liquidación: S/ 1,000
Pago a cuenta:        S/ 0
```

Resultado:

```text
monto:           S/ 1,000
monto_pagado:    S/ 1,000
monto_pendiente: S/ 0
estado:          COBRADO
```

## Pagos posteriores

No existe una tabla independiente de `Pagos` en la implementación actual.

La cobranza mantiene el acumulado mediante:

```text
monto_pagado
```

Por ejemplo:

```text
Monto:           S/ 1,000
Pagado inicial:  S/   500
Pendiente:       S/   500
```

Posteriormente se registra un pago acumulado de:

```text
monto_pagado = S/ 800
```

Resultado:

```text
monto:           S/ 1,000
monto_pagado:    S/   800
monto_pendiente: S/   200
estado:          PENDIENTE
```

Cuando:

```text
monto_pagado = monto
```

la cobranza pasa a:

```text
COBRADO
```

## Validaciones de cobranza

No se permite:

- monto pagado negativo;
- monto pagado superior al monto total de la cobranza;
- modificar una cobranza anulada.

El monto pendiente se calcula como:

```text
monto_pendiente = monto - monto_pagado
```

## Anulación

Cuando se anula una liquidación:

```text
Liquidación → ANULADA
Cobranza     → ANULADA
```

La cobranza queda asociada a la liquidación, pero su estado refleja que la operación fue anulada.

---

# 4. Arquitectura implementada

El backend sigue la separación:

```text
Router
   ↓
Service
   ↓
Repository
   ↓
Model / Database
```

## Router

Responsable de:

- exponer endpoints;
- recibir parámetros y schemas;
- devolver respuestas HTTP;
- convertir errores de negocio (`ValueError`) en respuestas HTTP.

## Service

Responsable de:

- reglas de negocio;
- validaciones;
- cálculos;
- coordinación entre repositorios;
- actualización de estados relacionados.

## Repository

Responsable de:

- consultas a la base de datos;
- creación de registros;
- actualización;
- persistencia.

Los repositories existentes siguen el patrón del proyecto de realizar `commit` y `refresh`.

---

# 5. Flujo principal del sistema

El flujo implementado hasta ahora puede representarse así:

```text
GUÍA
 │
 │ contiene
 ▼
DETALLES DE GUÍA
 │
 │ se liquidan
 ▼
LIQUIDACIÓN
 │
 ├── ACTIVA / ANULADA
 │
 │ genera automáticamente
 ▼
COBRANZA
 │
 ├── PENDIENTE
 │
 ├── COBRADO
 │
 └── ANULADA
```

La relación funcional principal es:

```text
Guía
  ↓
DetalleGuia
  ↓
DetalleLiquidacion
  ↓
Liquidacion
  ↓
Cobranza
```

---

# 6. Endpoints implementados en Cobranzas

Actualmente se dispone de:

```text
GET  /cobranzas
GET  /cobranzas/{cobranza_id}
GET  /cobranzas/liquidacion/{liquidacion_id}
PUT  /cobranzas/{cobranza_id}
```

## GET /cobranzas

Lista las cobranzas existentes.

## GET /cobranzas/{cobranza_id}

Obtiene una cobranza por ID.

## GET /cobranzas/liquidacion/{liquidacion_id}

Obtiene la cobranza asociada a una liquidación.

## PUT /cobranzas/{cobranza_id}

Actualiza el monto pagado acumulado y recalcula:

- monto pendiente;
- estado.

---

# 7. Reglas que NO forman parte de la implementación actual

Para evitar introducir lógica que no hemos definido:

- No existe una tabla `Pagos` independiente.
- No existe `guia_id` dentro de `Cobranza`.
- No existe `detalle_guia_id` dentro de `Cobranza`.
- No existe `cantidad_pendiente` en los detalles de liquidación.
- La liquidación parcial no se maneja por unidades.
- Modificar una liquidación no recalcula el estado de la guía.
- No se crea una cobranza manualmente para una liquidación.
- La cobranza corresponde a la liquidación completa, no a cada detalle individual.

---

# 8. Estado actual del proyecto

## Módulos cerrados

| Módulo | Sprint | Estado |
|---|---:|---|
| Guías | — | Implementado / probado en el flujo actual |
| Liquidaciones | 4 | ✅ Cerrado |
| Cobranzas | 5 | ✅ Cerrado |

## Próximo paso

El siguiente sprint debe definirse a partir de los requisitos pendientes del proyecto, evitando asumir funcionalidades que todavía no hayan sido especificadas.
