# modelo_datos.md

# Modelo de Datos - SIDEC

## Objetivo

Definir las entidades principales del sistema y sus relaciones para soportar el proceso completo de distribución, liquidación, cobranza e inventario.

---

# Entidades

## Agencia

Representa un punto de distribución donde se entregan productos en consignación.

### Atributos

* id_agencia
* codigo
* nombre
* responsable
* telefono
* direccion
* estado

---

## Producto

Representa un producto distribuido por la empresa.

### Atributos

* id_producto
* codigo
* nombre
* categoria
* precio
* estado

---

## Guía

Representa una entrega realizada a una agencia.

### Atributos

* id_guia
* numero_guia
* fecha
* id_agencia
* estado
* observacion

### Estados

* Pendiente
* Pendiente de Liquidación
* Parcialmente Liquidada
* Liquidada
* Anulada

---

## DetalleGuia

Representa cada producto entregado dentro de una guía.

### Atributos

* id_detalle_guia
* id_guia
* id_producto
* cantidad_entregada
* precio
* porcentaje_cobro

---

## Liquidación

Representa una visita realizada a una agencia para registrar ventas y devoluciones.

### Atributos

* id_liquidacion
* fecha
* id_agencia
* observacion

Una guía puede generar múltiples liquidaciones.

---

## DetalleLiquidacion

Representa el resultado de la liquidación de un producto.

### Atributos

* id_detalle_liquidacion
* id_liquidacion
* id_detalle_guia
* cantidad_vendida
* cantidad_devuelta

---

## Cobranza

Representa un pago realizado por una agencia.

### Atributos

* id_cobranza
* fecha
* id_agencia
* monto_total
* metodo_pago
* observacion

---

## DetalleCobranza

Relaciona una cobranza con una o varias liquidaciones.

### Atributos

* id_detalle_cobranza
* id_cobranza
* id_liquidacion
* monto_pagado

---

# Relaciones

Agencia

* 1:N Guía
* 1:N Liquidación
* 1:N Cobranza

Guía

* 1:N DetalleGuia

Producto

* 1:N DetalleGuia

Liquidación

* 1:N DetalleLiquidacion

DetalleGuia

* 1:N DetalleLiquidacion

Cobranza

* 1:N DetalleCobranza

Liquidación

* 1:N DetalleCobranza

---

# Relación General

Agencia

├── Guía

│ └── DetalleGuia

│ └── Producto

│

├── Liquidación

│ └── DetalleLiquidacion

│

└── Cobranza

└── DetalleCobranza

---

# Consideraciones

* Una guía puede liquidarse en varias visitas.
* Una liquidación puede liquidar parcialmente una guía.
* Una liquidación puede pagarse mediante varios cobros.
* Una cobranza puede cancelar varias liquidaciones.
* El inventario se actualizará automáticamente cuando se registren entregas y devoluciones.
