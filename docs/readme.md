# SIDEC

**Sistema Integral de Distribución Editorial y Cobranzas**

SIDEC es una aplicación desarrollada para gestionar el proceso completo de distribución de publicaciones en consignación, desde la administración de agencias y productos hasta la generación de guías, liquidaciones y cobranzas.

El objetivo del sistema es digitalizar y optimizar el flujo operativo de una distribuidora editorial, permitiendo un mejor control de la información, reduciendo errores operativos y facilitando el seguimiento de cada guía distribuida.

---

# Estado del proyecto

**Versión actual:** `v0.1.0`

## Módulos

### ✅ Agencias

* Crear agencia
* Listar agencias
* Consultar agencia
* Editar agencia
* Dar de baja
* Reactivar
* Buscar y filtrar agencias

### 🚧 En desarrollo

* Productos
* Guías
* Liquidaciones
* Cobranzas
* Reportes

---

# Arquitectura

El proyecto sigue una arquitectura por capas para separar responsabilidades y facilitar el mantenimiento.

```text
Cliente
    │
FastAPI (Router)
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

* **Router:** expone los endpoints HTTP.
* **Service:** implementa la lógica del negocio.
* **Repository:** gestiona el acceso a la base de datos.
* **Models:** representan las entidades de la base de datos.
* **Schemas:** definen los contratos de entrada y salida de la API.
* **Enums:** contienen los estados y valores del dominio.
* **Exceptions:** encapsulan las reglas de negocio y los errores del dominio.

---

# Tecnologías

## Backend

* Python 3.14
* FastAPI
* SQLAlchemy 2.0
* Alembic
* Pydantic v2
* Psycopg2

## Base de datos

* PostgreSQL

## Documentación

* Swagger UI
* OpenAPI

---

# Estructura del proyecto

```text
backend/

├── alembic/
│
├── app/
│   ├── api/
│   │   └── v1/
│   │
│   ├── core/
│   │
│   ├── db/
│   │
│   ├── domain/
│   │
│   ├── enums/
│   │
│   ├── models/
│   │
│   ├── repositories/
│   │
│   ├── schemas/
│   │
│   ├── services/
│   │
│   └── main.py
│
├── docs/
│
└── tests/
```

---

# Instalación

## 1. Clonar el repositorio

```bash
git clone <repositorio>
```

## 2. Crear el entorno virtual

```bash
python3 -m venv .venv
```

## 3. Activar el entorno

### macOS / Linux

```bash
source .venv/bin/activate
```

### Windows

```powershell
.venv\Scripts\activate
```

## 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

# Variables de entorno

Crear un archivo `.env` en la raíz del proyecto.

Ejemplo:

```env
APP_NAME=SIDEC
APP_VERSION=0.1.0

DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=distribuidora
DATABASE_USER=postgres
DATABASE_PASSWORD=

DATABASE_ECHO=False
```

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

# Ejecutar la aplicación

```bash
python -m uvicorn app.main:app --reload
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

---

# Roadmap

## Sprint 1

* ✅ Agencias

## Sprint 2

* ⏳ Productos

## Sprint 3

* ⏳ Guías

## Sprint 4

* ⏳ Liquidaciones

## Sprint 5

* ⏳ Cobranzas

## Sprint 6

* ⏳ Reportes

---

# Licencia

Proyecto desarrollado para uso interno de **Grupo PERVAR SAC**.
