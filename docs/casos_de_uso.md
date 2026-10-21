# casos_uso.md

# Casos de Uso - SIDEC

## Actores

**Operador** (rol `OPERADOR`)

Es el usuario encargado de realizar la distribución, las liquidaciones y las cobranzas en el día a día: gestiona guías, agencias, productos, liquidaciones y cobranzas.

**Administrador** (rol `ADMIN`)

Tiene todos los permisos del Operador, y además es el único que puede consultar reportes y gestionar las cuentas de usuario del sistema (crear, editar, dar de baja).

Todo acceso al sistema requiere iniciar sesión (`CU-00`).

---

# CU-00 Iniciar Sesión

### Flujo

1. Ingresar usuario y contraseña en `/login`.
2. El sistema valida las credenciales y entrega un token de sesión (JWT).
3. El sistema redirige a la pantalla de inicio.
4. Si el token expira o es inválido en una petición posterior, el sistema cierra la sesión automáticamente y vuelve a `/login`.

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

Disponible únicamente para el rol Administrador. El sistema permite generar:

* Dashboard de cobranza (estimados, deuda por cobrar, guías vencidas).
* Detalle por agencia, con exportación a PDF.
* Distribución de productos por agencia.
* Ranking de agencias por % de venta.
* Reporte por agencia y por producto.
* Resumen por período.

---

# CU-11 Gestionar Usuarios

Disponible únicamente para el rol Administrador.

### Flujo

1. Crear una cuenta nueva (nombre, usuario, contraseña, rol).
2. Editar nombre, contraseña o rol de una cuenta existente.
3. Dar de baja o reactivar una cuenta.

No existe autoregistro: toda cuenta debe ser creada por un Administrador.
