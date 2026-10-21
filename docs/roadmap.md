# SIDEC Roadmap

## Sprint 1 — Agencias

- [x] Crear Agencia
- [x] Listar Agencias
- [x] Consultar Agencia
- [x] Editar Agencia
- [x] Dar de baja Agencia
- [x] Reactivar Agencia
- [x] Buscar Agencia
- [x] Campos de geolocalización (ruta, latitud, longitud)

---

## Sprint 2 — Productos

- [x] CRUD completo de Productos
- [x] Dar de baja / Reactivar
- [x] Buscar por nombre o categoría
- [x] Eliminación lógica (soft delete) independiente del estado

---

## Sprint 3 — Guías

- [x] Crear, listar, consultar, editar y anular guías
- [x] Número de guía autogenerado y editable
- [x] Editar agencia y estado de una guía existente

---

## Sprint 4 — Liquidaciones

- [x] Liquidaciones

---

## Sprint 5 — Cobranzas

- [x] Cobranzas

---

## Sprint 6 — Reportes

- [x] Dashboard de cobranza
- [x] Detalle por agencia (con exportación a PDF)
- [x] Distribución agencia × producto
- [x] Rankings y resúmenes por período

---

## Sprint 7 — Autenticación y roles

- [x] Login con JWT
- [x] Roles ADMIN / OPERADOR
- [x] Gestión de usuarios

---

## Sprint 8 — Despliegue

- [x] Dockerfiles (backend y frontend)
- [x] docker-compose.yml (Postgres + backend + frontend + Caddy)
- [x] Caddyfile (HTTPS automático)
- [ ] Ejecutar el despliegue en la VPS de producción
- [ ] Backups automáticos (`pg_dump` + cron)
