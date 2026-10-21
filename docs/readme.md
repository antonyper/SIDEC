# SIDEC

**Sistema Integral de Distribución Editorial y Cobranzas**

SIDEC es una aplicación desarrollada para gestionar el proceso completo de distribución de publicaciones en consignación, desde la administración de agencias y productos hasta la generación de guías, liquidaciones y cobranzas.

El objetivo del sistema es digitalizar y optimizar el flujo operativo de una distribuidora editorial, permitiendo un mejor control de la información, reduciendo errores operativos y facilitando el seguimiento de cada guía distribuida.

---

# Estado del proyecto

**Versión actual:** `v1.0.0`

## Módulos

### ✅ Agencias

* Crear, listar, consultar, editar, dar de baja, reactivar
* Buscar y filtrar agencias
* Campos de geolocalización (`ruta`, `latitud`, `longitud`)

### ✅ Productos

* Crear, listar, consultar, editar, dar de baja, reactivar
* Eliminación lógica (`eliminado`) independiente del estado ACTIVO/INACTIVO
* Buscador combinado por nombre o categoría

### ✅ Guías

* Crear, listar, consultar, editar, anular
* Número de guía autogenerado (correlativo) pero editable
* Reasignación de agencia y cambio manual de estado al editar

### ✅ Liquidaciones

* Crear, listar, consultar, editar, anular
* Liquidación parcial por producto/detalle

### ✅ Cobranzas

* Generadas automáticamente al crear una liquidación
* Registro de pagos a cuenta y acumulados

### ✅ Reportes

* Dashboard de cobranza, detalle por agencia (con exportación a PDF), distribución agencia × producto, rankings y resúmenes por período
* Acceso restringido al rol `ADMIN`

### ✅ Autenticación y usuarios

* Login con JWT, roles `ADMIN` y `OPERADOR`
* Gestión de usuarios desde `/usuarios` (solo `ADMIN`)

### 🚧 Pendiente

* Ejecutar el despliegue en la VPS de producción (ya preparado, ver sección Despliegue)
* Notificaciones automáticas por WhatsApp (definido en el modelo de negocio, no implementado aún)

---

# Arquitectura

El proyecto sigue una arquitectura por capas para separar responsabilidades y facilitar el mantenimiento.

```text
Navegador (Next.js / React, "use client")
    │
Rewrite /api/:path* → BACKEND_URL
    │
FastAPI (Router) ── valida JWT (Authorization: Bearer) y rol
    │
Services
    │
Repositories
    │
SQLAlchemy ORM
    │
PostgreSQL
```

Cada capa tiene una responsabilidad específica:

* **Router:** expone los endpoints HTTP y aplica las dependencias de autenticación/autorización (`get_current_user`, `require_admin`).
* **Service:** implementa la lógica del negocio.
* **Repository:** gestiona el acceso a la base de datos.
* **Models:** representan las entidades de la base de datos.
* **Schemas:** definen los contratos de entrada y salida de la API.
* **Enums:** contienen los estados y valores del dominio.
* **Exceptions:** encapsulan las reglas de negocio y los errores del dominio.
* **Core (auth):** `security.py` (hash de contraseñas con `bcrypt`, firma/verificación de JWT) y `auth_dependencies.py` (resolución del usuario autenticado y control de rol).

El frontend es un cliente puro (sin SSR de datos): todas las páginas son componentes `"use client"` que consumen la API vía `fetch`, y el rewrite de `next.config.ts` reenvía `/api/*` al backend (`BACKEND_URL`).

---

# Tecnologías

## Backend

* Python 3.14
* FastAPI
* SQLAlchemy 2.0
* Alembic
* Pydantic v2
* Psycopg2
* PyJWT + bcrypt (autenticación)
* ReportLab (generación de PDF de reportes)

## Frontend

* Next.js 16 (App Router, Turbopack)
* React 19
* TypeScript

## Base de datos

* PostgreSQL

## Despliegue

* Docker Compose (`db`, `backend`, `frontend`, `caddy`)
* Caddy (reverse proxy + HTTPS automático)

## Documentación

* Swagger UI
* OpenAPI

---

# Estructura del proyecto

```text
sidec/

├── backend/
│   ├── alembic/
│   ├── app/
│   │   ├── api/v1/
│   │   ├── core/          (config, security.py, auth_dependencies.py)
│   │   ├── db/
│   │   ├── domain/
│   │   ├── enums/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .venv/
│
├── frontend/
│   ├── app/                (rutas, App Router)
│   ├── components/
│   ├── lib/                (clientes HTTP por módulo)
│   ├── Dockerfile
│   └── next.config.ts
│
├── docker-compose.yml
├── Caddyfile
├── .env.example
│
└── docs/
```

---

# Instalación (desarrollo local, sin Docker)

## Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

El frontend corre en `http://localhost:3000` y reenvía `/api/*` al backend en `http://localhost:8000` (configurable con `BACKEND_URL`).

---

# Variables de entorno

## Backend (`backend/.env`)

```env
APP_NAME=SIDEC
APP_VERSION=1.0.0

DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=distribuidora
DATABASE_USER=postgres
DATABASE_PASSWORD=

DATABASE_ECHO=False

SECRET_KEY=genera-una-clave-aleatoria-fuerte
ACCESS_TOKEN_EXPIRE_MINUTES=720
```

`SECRET_KEY` firma los tokens de sesión (JWT); generar una nueva con:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```

## Despliegue con Docker (`.env` en la raíz)

Ver `.env.example`: `DOMAIN`, `DATABASE_NAME`, `DATABASE_USER`, `DATABASE_PASSWORD`, `SECRET_KEY`.

---

# Migraciones

Crear una migración:

```bash
alembic revision --autogenerate -m "descripcion"
```

Aplicar migraciones:

```bash
alembic upgrade head
```

---

# Despliegue en producción (VPS, con Docker)

```bash
cp .env.example .env     # completar DOMAIN, credenciales y SECRET_KEY
docker compose up -d --build
```

Esto levanta Postgres, el backend (migraciones + uvicorn), el frontend (build `standalone` de Next.js) y Caddy como reverse proxy con HTTPS automático. Solo Caddy queda expuesto a internet (puertos 80/443).

Útiles:

```bash
docker compose ps              # ver estado de los contenedores
docker compose logs -f backend # ver logs de un servicio
docker compose down            # apagar todo
```

---

# Documentación de la API

Swagger:

```
http://127.0.0.1:8000/docs
```

OpenAPI:

```
http://127.0.0.1:8000/openapi.json
```

---

# Principios del proyecto

SIDEC sigue las siguientes reglas de desarrollo:

* Arquitectura por capas.
* Separación entre lógica de negocio y acceso a datos.
* Soft Delete para las entidades del negocio.
* Uso de Enumeraciones para los estados.
* Validación mediante Pydantic.
* Migraciones controladas con Alembic.
* Desarrollo basado en Casos de Uso.
* Autenticación por JWT con control de acceso por rol.

---

# Roadmap

* ✅ Agencias
* ✅ Productos
* ✅ Guías
* ✅ Liquidaciones
* ✅ Cobranzas
* ✅ Inventario
* ✅ Reportes
* ✅ Autenticación y roles
* 🚧 Despliegue en VPS de producción (preparado, falta ejecutar)

---

# Licencia

Proyecto desarrollado para uso interno de **Grupo PERVAR SAC**.
