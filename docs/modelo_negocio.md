# Modelo de Negocio - Sistema de Distribución y Consignación

## Objetivo

Desarrollar un sistema para gestionar la distribución de productos entregados en consignación a distintas agencias, permitiendo controlar las entregas, liquidaciones, cobranzas e inventario desde una aplicación web utilizada por los distribuidores.

---

# Flujo General del Negocio

El proceso operativo de la empresa se divide en cuatro etapas:

1. Distribución de productos.
2. Liquidación de los productos entregados.
3. Cobranza de las ventas realizadas.
4. Control del inventario.

Cada una de estas etapas es independiente y representa un proceso diferente dentro del sistema.

---

# Entidades del Negocio

## Agencia

Representa un punto de distribución donde los canillitas recogen los productos para su venta.

Una agencia:

* Tiene un responsable.
* Puede recibir muchas guías.
* Puede realizar muchas liquidaciones.
* Puede realizar muchos pagos.

---

## Producto

Representa un producto distribuido por la empresa.

Ejemplos:

* Revista Forbes
* Revista Vogue
* Revista GQ
* Selecciones

Cada producto posee:

* Precio de venta.
* Categoría.
* Estado.

Un mismo producto puede ser entregado a múltiples agencias.

---

## Guía de Remisión

Representa una entrega de productos realizada a una agencia.

Una guía:

* Pertenece a una sola agencia.
* Contiene uno o varios productos.
* Se genera en una fecha determinada.
* Puede imprimirse en una impresora térmica.
* Puede liquidarse parcialmente en varias visitas.

Una guía representa únicamente la entrega de productos.

No representa ventas ni pagos.

---

## Detalle de Guía

Representa cada producto entregado dentro de una guía.

Cada registro contiene:

* Producto entregado.
* Cantidad entregada.
* Precio vigente.
* Porcentaje de cobranza.

Una guía puede contener múltiples registros de detalle.

---

## Liquidación

Representa una visita posterior del distribuidor para cerrar total o parcialmente la venta de los productos entregados.

Una liquidación:

* Se realiza sobre una agencia.
* Puede liquidar uno o varios productos.
* Puede liquidar únicamente una parte de los productos entregados.
* Puede existir más de una liquidación para una misma guía.

La liquidación determina:

* Cantidad vendida.
* Cantidad devuelta.

---

## Detalle de Liquidación

Cada detalle corresponde a un producto liquidado.

Para cada producto se registra:

* Cantidad vendida.
* Cantidad devuelta.

La suma de las cantidades liquidadas nunca puede superar la cantidad entregada originalmente.

---

## Cobranza

Representa el dinero recibido por parte de una agencia.

La cobranza es independiente de la liquidación.

Una agencia puede:

* Pagar una liquidación completamente.
* Pagar parcialmente una liquidación.
* Pagar varias liquidaciones en un solo pago.

El sistema deberá permitir registrar pagos parciales.

---

## Inventario

El inventario representa el stock disponible de cada producto.

El inventario disminuye cuando:

* Se entrega un producto mediante una guía.

El inventario aumenta cuando:

* Se recibe una devolución durante una liquidación.

---

# Reglas de Negocio

## Distribución

* Una guía pertenece a una sola agencia.
* Una guía puede contener múltiples productos.
* Un producto puede aparecer en muchas guías.

---

## Liquidaciones

* Una guía puede tener una o varias liquidaciones.
* Una liquidación puede registrar uno o varios productos.
* Un producto puede liquidarse en diferentes fechas.
* No se puede liquidar una cantidad superior a la entregada.

---

## Devoluciones

Toda devolución registrada:

* Incrementa automáticamente el inventario.
* Queda asociada a la liquidación correspondiente.

---

## Cobranzas

Las cobranzas son independientes de las liquidaciones.

Se debe permitir:

* Pago total.
* Pago parcial.
* Múltiples pagos para una misma liquidación.

---

## Estados

## Estados de la Guía

Una guía puede encontrarse en alguno de los siguientes estados durante su ciclo de vida (nombre implementado entre paréntesis):

* **En venta** (`EN_VENTA`): la guía ha sido emitida y los productos fueron entregados a la agencia.
* **Pendiente de Liquidación** (`PENDIENTE_LIQUIDACION`): han transcurrido más de 30 días desde la creación de la guía y la agencia debe ser contactada para coordinar la visita de liquidación.
* **Parcialmente Liquidada** (`PARCIALMENTE_LIQUIDADA`): una parte de los productos de la guía ya fue liquidada, pero aún existen productos pendientes.
* **Liquidada** (`LIQUIDADA`): todos los productos de la guía fueron liquidados.
* **Anulada** (`ANULADA`): la guía fue anulada y no forma parte del proceso operativo.

### Reglas de Negocio

* Una guía permanecerá en estado **En venta** durante los primeros 30 días desde su creación.
* Al superar 30 días desde su creación, el sistema cambiará automáticamente su estado a **Pendiente de Liquidación**, siempre que aún existan productos pendientes de liquidar.
* Cuando todos los productos de la guía hayan sido liquidados, el estado cambiará automáticamente a **Liquidada**.
* Si solo una parte de los productos ha sido liquidada, el estado será **Parcialmente Liquidada**.
* El estado de una guía también puede corregirse manualmente desde la pantalla de edición (por ejemplo, para revertir una anulación), además de los cambios automáticos descritos arriba.

---

## Notificación de Liquidación

El sistema dispondrá de una funcionalidad para facilitar la comunicación con las agencias.

En la pantalla **Pendientes de Liquidación** existirá un botón **"Enviar WhatsApp"**, que permitirá enviar automáticamente un mensaje a la agencia utilizando el número de teléfono registrado.

El objetivo de esta funcionalidad es avisar a la agencia que el distribuidor realizará la visita de liquidación y cobranza.

### Funcionalidades previstas

* Enviar el mensaje a una agencia seleccionada.
* Enviar mensajes masivos a todas las agencias con guías en estado **Pendiente de Liquidación**.
* Registrar la fecha y hora del último envío.
* Registrar el usuario que realizó el envío.
* Permitir reenviar el mensaje cuando sea necesario.

### Ejemplo de mensaje

> Buenos días. Le informamos que su guía se encuentra pendiente de liquidación. En los próximos días estaremos realizando la visita para efectuar la liquidación de los productos entregados y la cobranza correspondiente. Muchas gracias.

### Producto

* Activo
* Inactivo

### Agencia

* Activa
* Inactiva

---

# Pantallas del Sistema

## Catálogos

* Agencias
* Productos

---

## Distribución

* Nueva Guía
* Historial de Guías

---

## Liquidaciones

* Nueva Liquidación
* Historial de Liquidaciones

---

## Cobranzas

* Registrar Cobranza
* Estado de Cuenta

---

## Inventario

* Inventario por Agencia
* Inventario por Producto
* Movimientos de Inventario

---

## Reportes

Implementados (acceso restringido al rol Administrador):

* Dashboard de cobranza
* Detalle por agencia (con exportación a PDF)
* Distribución agencia × producto
* Ranking de agencias por % de venta
* Reporte por agencia
* Reporte por producto
* Resumen por período

---

# Objetivos del Sistema

El sistema deberá permitir:

* Gestionar agencias.
* Gestionar productos.
* Registrar entregas mediante guías.
* Liquidar productos en una o varias visitas.
* Registrar devoluciones.
* Actualizar automáticamente el inventario.
* Registrar cobranzas parciales o totales.
* Consultar el estado de cuenta de cada agencia.
* Consultar el historial completo de movimientos.
* Imprimir guías en impresoras térmicas.
* Exportar información a Excel.

---

# Consideraciones para Futuras Versiones

El diseño deberá permitir incorporar nuevas funcionalidades sin modificar la lógica principal del sistema.

> **Nota:** la gestión de usuarios y roles (`ADMIN` / `OPERADOR`) ya fue implementada y dejó de ser una consideración futura; ver `SIDEC_reglas_negocio_funcionalidades.md`, sección 9.

Entre las posibles ampliaciones se encuentran:

* Firma digital de recepción.
* Captura de fotografías.
* Geolocalización de entregas.
* Escaneo de códigos de barras.
* Integración con SUNAT.
* Dashboard de indicadores.
* Notificaciones automáticas.
* Modo offline con sincronización.
