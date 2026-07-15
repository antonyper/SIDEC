# casos_uso.md

# Casos de Uso - SIDEC

## Actor Principal

**Distribuidor**

Es el usuario encargado de realizar la distribución, las liquidaciones y las cobranzas.

---

# CU-01 Gestionar Agencias

El distribuidor registra, consulta, modifica y desactiva agencias.

---

# CU-02 Gestionar Productos

Permite administrar el catálogo de productos disponibles para distribución.

---

# CU-03 Crear Guía

### Flujo

1. Seleccionar agencia.
2. Agregar uno o varios productos.
3. Registrar cantidades.
4. Confirmar la guía.
5. Actualizar el inventario.
6. Imprimir la guía.
7. Guardar la guía.

---

# CU-04 Consultar Guías

Permite buscar guías por:

* Agencia
* Fecha
* Estado
* Número de guía

---

# CU-05 Registrar Liquidación

### Flujo

1. Seleccionar la agencia.
2. Seleccionar una guía pendiente.
3. Seleccionar los productos a liquidar.
4. Registrar cantidades vendidas.
5. Registrar cantidades devueltas.
6. Actualizar inventario.
7. Guardar la liquidación.

---

# CU-06 Registrar Cobranza

### Flujo

1. Seleccionar agencia.
2. Consultar liquidaciones pendientes.
3. Seleccionar una o varias liquidaciones.
4. Registrar monto recibido.
5. Registrar método de pago.
6. Guardar la cobranza.

---

# CU-07 Consultar Estado de Cuenta

Permite visualizar:

* Liquidaciones pendientes.
* Pagos realizados.
* Saldo pendiente.

---

# CU-08 Consultar Inventario

Permite consultar el inventario por:

* Agencia.
* Producto.
* Categoría.

Con filtros y ordenamientos similares a una hoja de cálculo.

---

# CU-09 Enviar Notificación por WhatsApp

### Flujo

1. Consultar las guías en estado **Pendiente de Liquidación**.
2. Seleccionar una o varias agencias.
3. Pulsar **Enviar WhatsApp**.
4. Generar automáticamente el mensaje.
5. Abrir WhatsApp con el mensaje listo para enviar.
6. Registrar la fecha del envío.

---

# CU-10 Reportes

El sistema permitirá generar reportes de:

* Guías emitidas.
* Productos entregados.
* Productos vendidos.
* Productos devueltos.
* Cobros realizados.
* Saldos pendientes.
* Inventario por agencia.
