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
              HTTP / REST API

                      ▼

                 FastAPI

                      │

          SQLAlchemy + Alembic

                      │

                  PostgreSQL
```

---

# Componentes

## Frontend

Responsabilidades:

* Interfaz de usuario.
* Validaciones básicas.
* Consumo de la API.
* Impresión de guías.
* Apertura de WhatsApp.
* Gestión de sesión.

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
* Autenticación.
* Exposición de la API REST.
* Actualización de inventario.
* Gestión de liquidaciones.
* Gestión de cobranzas.

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
│   ├── alembic/
│   ├── requirements.txt
│   └── .venv/
│
├── frontend/
│   ├── app/
│   ├── components/
│   ├── services/
│   └── public/
│
├── docs/
│   ├── arquitectura.md
│   ├── modelo_negocio.md
│   ├── modelo_datos.md
│   ├── casos_uso.md
│   └── roadmap.md
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

* Reportes

* Configuración
