# arquitectura.md

# Arquitectura - SIDEC

## Arquitectura General

SIDEC será una aplicación web desarrollada bajo una arquitectura cliente-servidor basada en una API REST.

El sistema estará compuesto por un frontend desarrollado en React con Next.js (PWA), un backend desarrollado en Python con FastAPI y una base de datos PostgreSQL. La comunicación entre el frontend y el backend se realizará mediante peticiones HTTP utilizando una API REST.

---

# Arquitectura Lógica

```text
                 Tablet / PC

                      │

                      ▼

        React + Next.js (PWA)

                      │
         HTTP / REST API + JWT (Authorization: Bearer)

                      ▼

                 FastAPI
         (valida token y rol por ruta)

                      │

          SQLAlchemy + Alembic

                      │

                  PostgreSQL
```

En producción, Caddy actúa como reverse proxy con HTTPS automático frente al
frontend, y backend/base de datos quedan solo en la red interna de Docker
(ver sección "Despliegue").

---

# Componentes

## Frontend

Responsabilidades:

* Interfaz de usuario.
* Validaciones básicas.
* Consumo de la API.
* Impresión de guías.
* Gestión de sesión (token guardado en `localStorage`, redirección a `/login` si no hay sesión o si expira).

Pendiente: apertura de WhatsApp (definida en el modelo de negocio, no implementada aún).

Tecnologías:

* React
* Next.js
* TypeScript
* Tailwind CSS

---

## Backend

Responsabilidades:

* Lógica de negocio.
* Validación de datos.
* Autenticación (JWT) y autorización por rol (`ADMIN` / `OPERADOR`).
* Exposición de la API REST.
* Actualización de inventario.
* Gestión de liquidaciones.
* Gestión de cobranzas.
* Generación de reportes y exportación a PDF.

Tecnologías:

* Python
* FastAPI

---

## Persistencia

La persistencia será gestionada mediante:

* PostgreSQL
* SQLAlchemy
* Alembic

---

# Organización del Proyecto

```text
sidec/

├── backend/
│   ├── app/
│   │   ├── api/v1/
│   │   ├── core/        (config, security.py, auth_dependencies.py)
│   │   ├── models/, repositories/, services/, schemas/, enums/
│   │   └── main.py
│   ├── alembic/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .venv/
│
├── frontend/
│   ├── app/              (incluye /login, /usuarios)
│   ├── components/
│   ├── lib/               (clientes HTTP por módulo, incluye auth.ts)
│   ├── Dockerfile
│   └── public/
│
├── docker-compose.yml
├── Caddyfile
├── .env.example
│
├── docs/
│   ├── arquitectura.md
│   ├── modelo_negocio.md
│   ├── modelo_datos.md
│   ├── casos_de_uso.md
│   ├── readme.md
│   ├── roadmap.md
│   └── SIDEC_reglas_negocio_funcionalidades.md
│
└── README.md
```

---

# Flujo de una Solicitud

1. El distribuidor realiza una acción desde la tablet.
2. El frontend envía una petición a la API REST.
3. FastAPI valida la información.
4. SQLAlchemy ejecuta las operaciones sobre PostgreSQL.
5. FastAPI devuelve la respuesta.
6. El frontend actualiza la interfaz.

---

# Principios de Diseño

* Separación entre presentación, lógica de negocio y persistencia.
* API REST desacoplada del frontend.
* Código organizado por módulos.
* Modelo de datos versionado mediante Alembic.
* Escalabilidad para incorporar nuevos módulos sin afectar los existentes.

---

# Módulos Funcionales

* Catálogos

  * Agencias
  * Productos

* Distribución

  * Guías
  * Impresión

* Liquidaciones

* Cobranzas

* Inventario

* Reportes (acceso restringido al rol Administrador)

* Autenticación y usuarios

  * Login (JWT)
  * Gestión de usuarios y roles (`ADMIN` / `OPERADOR`)

* Configuración

---

# Despliegue

En producción, el sistema corre mediante Docker Compose con 4 servicios:

```text
Internet
    │
Caddy (puertos 80/443, HTTPS automático)
    │
Frontend (Next.js, puerto 3000 interno)
    │
Backend (FastAPI, puerto 8000 interno)
    │
PostgreSQL (puerto 5432 interno)
```

Solo Caddy queda expuesto a internet; el resto de servicios solo son
accesibles dentro de la red interna de Docker. El backend aplica las
migraciones de Alembic automáticamente al iniciar el contenedor.
