# SIDEC — contexto para agentes

Leer esto entero antes de tocar código, datos o despliegue. Es el mapa del repo: qué es SIDEC,
cómo encajan las piezas, qué reglas de negocio no se pueden romper y dónde vive cada cosa en
producción. El detalle funcional está en `docs/` (enlazado abajo); aquí va lo que hace falta para
no equivocarse.

## Qué es

Sistema de distribución y consignación de publicaciones (diarios, revistas). Un distribuidor
entrega producto a **agencias** (puntos de venta) con una **guía**; días después visita la
agencia, registra lo devuelto (**liquidación**) y cobra lo vendido (**cobranza**). El stock de
almacén se lleva como historial de **movimientos de inventario**. Usuarios: `ADMIN` y `OPERADOR`.

## Stack

| Capa | Tecnología | Dónde |
|---|---|---|
| Frontend | Next.js 16 (App Router, `output: "standalone"`), React 19, TypeScript, Tailwind 4 | `frontend/` |
| Backend | FastAPI, SQLAlchemy 2, Pydantic 2, Alembic, PyJWT + bcrypt, reportlab (PDF) | `backend/` |
| Base de datos | PostgreSQL 16 | `docker-compose.yml` / `sidec-db` en el clúster |

`frontend/AGENTS.md` avisa de que Next 16 tiene cambios incompatibles con lo que un modelo
conoce: antes de escribir código de Next, leer la guía en `frontend/node_modules/next/dist/docs/`.

## Mapa del código

```text
backend/app/
  main.py                 app FastAPI: routers, /health, /health/ready, lifespan
                          (crea el ADMIN inicial y lanza la tarea diaria de guías vencidas)
  core/config.py          Settings (variables de entorno); valida SECRET_KEY
  core/security.py        bcrypt + JWT HS256 (sub = id de usuario, rol)
  core/auth_dependencies.py  get_current_user / require_admin
  core/exception_handler.py  BusinessException → {"message": ...} con su status
  api/v1/*_router.py      endpoints HTTP (una carpeta por módulo, sin prefijo /api)
  services/*_service.py   reglas de negocio y cálculos
  repositories/*_repository.py  consultas; hacen commit + refresh
  models/                 tablas SQLAlchemy (BaseModel añade id, created_at, updated_at)
  schemas/                Pydantic (Create / Update / Response)
  enums/                  estados (ver abajo)
  domain/exceptions/      excepciones de negocio por módulo
  services/bootstrap_service.py  primer ADMIN desde variables de entorno
  services/pdf_service.py PDF del detalle por agencia (reportlab)
backend/alembic/versions/ migraciones (una sola cabeza; el CI lo comprueba)

frontend/
  app/<modulo>/page.tsx   pantallas: agencias, productos, guias (+nueva, [id]), liquidaciones
                          (+nueva, [id]), cobranzas, inventario ([id]), reportes ([reporte],
                          dashboard-cobranza), usuarios, login
  lib/http.ts             fetch a /api con el token; 401 → cierra sesión (evento sidec:auth-expired)
  lib/<modulo>.ts         cliente HTTP y tipos de cada módulo
  components/auth/AuthContext.tsx  sesión en localStorage (clave sidec_token)
  components/layout/      AppShell, Sidebar, nav-items (oculta Reportes/Usuarios a OPERADOR)
  components/ui/          Modal, ConfirmDialog, PageHeader, BarChart (SVG propio, sin librería)
```

Capas del backend, siempre en este sentido: **Router → Service → Repository → Model**. El router
no tiene lógica; el service no escribe SQL; los errores de negocio son `BusinessException` (o
subclases de `domain/exceptions/`), nunca `HTTPException` desde un service.

## Modelo y reglas que no se pueden romper

Relaciones: `Agencia 1─N Guia 1─N DetalleGuia N─1 Producto`; `Guia 1─N Liquidacion 1─N
DetalleLiquidacion N─1 DetalleGuia`; `Liquidacion 1─0..1 Cobranza`; `Producto 1─N
MovimientoInventario`.

Estados reales en código (los de `enums/` mandan sobre los documentos):

| Entidad | Estados |
|---|---|
| Guía | `EN_VENTA`, `PENDIENTE_LIQUIDACION`, `PARCIALMENTE_LIQUIDADA`, `LIQUIDADA`, `ANULADA` |
| Liquidación | `LIQUIDADO`, `ANULADA` (los docs dicen `ACTIVA`: se renombró en la migración `4968dc4e7608`) |
| Cobranza | `PENDIENTE`, `COBRADO`, `ANULADA` |
| Agencia / Producto | `ACTIVO`, `INACTIVO` (+ `producto.eliminado` como soft delete aparte) |

Reglas:

- **Guía**: número correlativo `G000001…` sugerido por `GET /guias/siguiente-numero`, editable y
  único. Al editar, el frontend reenvía todos los detalles y el backend los reconcilia por
  `detalle_guia_id`: nunca borrar y recrear detalles que tengan una liquidación activa.
- **Liquidación parcial por detalle, nunca por unidades.** Un detalle con liquidación activa no se
  vuelve a liquidar, ni se edita, ni se borra de su guía.
- El frontend envía `cantidad_devuelta`; el backend calcula `cantidad_vendida = entregada −
  devuelta` y `total`. No existe `cantidad_pendiente`.
- Estado de la guía = f(detalles con liquidación activa): ninguno → `PENDIENTE_LIQUIDACION`,
  algunos → `PARCIALMENTE_LIQUIDADA`, todos → `LIQUIDADA`. Se recalcula al **crear** y al
  **anular** una liquidación; editar una liquidación no lo cambia.
- Una guía `EN_VENTA` con más de 30 días pasa sola a `PENDIENTE_LIQUIDACION` (tarea diaria en
  `main.py` → `GuiaRepository.actualizar_guias_pendientes_vencidas`).
- **Cobranza implícita**: se crea al crear la liquidación, nunca a mano. `pago_a_cuenta` vacío o 0
  ⇒ cobrado completo (`COBRADO`); si no, `monto_pagado = pago_a_cuenta` y `PENDIENTE`. Los pagos
  posteriores actualizan `monto_pagado` acumulado (`PUT /cobranzas/{id}`); no hay tabla de pagos.
  Prohibido: pagado negativo, pagado > monto, tocar una cobranza anulada.
- **Anular liquidación** ⇒ liquidación `ANULADA`, su cobranza `ANULADA`, estado de la guía
  recalculado y sus detalles desbloqueados (si no hay otra liquidación activa sobre ellos).
- **Inventario**: el stock no se edita, se calcula: `STOCK_INICIAL + INGRESO + DEVOLUCION −
  SALIDA_GUIA`. Puede quedar negativo (se permite registrar repartos antes del stock inicial).
- **Métrica central de reportes**: "50 % estimado" = `0.5 × cantidad × precio × porcentaje_cobro / 100`.
  "Vencida" se calcula en tiempo real con la fecha, no con el estado guardado.
- Permisos: OPERADOR no ve Reportes, no gestiona Usuarios y no registra movimientos manuales de
  inventario; todo lo demás igual que ADMIN. No hay registro público.

Fuentes: `docs/SIDEC_reglas_negocio_funcionalidades.md` (reglas por sprint, la más completa),
`docs/modelo_datos.md`, `docs/casos_de_uso.md`, `docs/modelo_negocio.md`, `docs/arquitectura.md`.

## Configuración (backend)

| Variable | Uso |
|---|---|
| `DATABASE_HOST/PORT/NAME/USER/PASSWORD` | conexión (la URL se arma con `URL.create`: la contraseña puede tener cualquier carácter) |
| `SECRET_KEY` | firma de los JWT. **Obligatoria**, ≥ 32 caracteres; el valor de `.env.example` se rechaza al arrancar |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 720 por defecto |
| `API_ROOT_PATH` | prefijo público de la API (`/api`), para que Swagger encuentre `openapi.json` |
| `SIDEC_ADMIN_USERNAME/PASSWORD/NOMBRE` | primer ADMIN; solo se usa si la tabla `usuarios` está vacía |

Frontend: `BACKEND_URL` es **argumento de build**, no de runtime. Next fija los rewrites de
`next.config.ts` en `next build`; cambiarlo en el contenedor no tiene efecto (así nació el 500 de
`/api` del primer despliegue).

## Ejecutar en local

```bash
cp .env.example .env        # completar: contraseña de DB, SECRET_KEY (≥32), SIDEC_ADMIN_*
docker compose up -d --build db backend frontend
# sin Caddy: publicar puertos con un override o usar `docker compose up -d --build` completo
python3 scripts/smoke_e2e.py http://localhost:3000/api admin '<SIDEC_ADMIN_PASSWORD>'
```

`scripts/smoke_e2e.py` recorre el flujo completo (agencia → producto → stock → guía →
liquidación parcial con pago a cuenta → cobranza → reportes y PDF → permisos de OPERADOR →
anulación) y verifica las reglas de arriba. Crea datos con sufijo aleatorio: **no correrlo contra
una base con datos reales**. Es la prueba de regresión del repo hasta que haya tests unitarios.

Swagger: `/api/docs` (publicado) o `http://127.0.0.1:8000/docs` (backend directo).

## Despliegue en Bifrost (entorno de prueba)

URL: **https://sidec.tyc-iasolutions.com** (cuenta Cloudflare TYC, mismo túnel y Envoy Gateway que
`iavigil.tyc-iasolutions.com`). Detalle y operación en `docs/despliegue-bifrost.md`.

```text
Cloudflare (túnel tyc) → Envoy Gateway bifrost-gw
   ├─ /api/*  → Service sidec-backend:8000   (ns bifrost-next-ui; el Gateway quita el /api)
   └─ /*      → Service sidec-frontend:3000  (ns bifrost-next-ui)
sidec-backend → sidec-db.sidec.svc:5432      (Postgres 16, PVC 2Gi, ns sidec)
```

| Pieza | Repo / archivo |
|---|---|
| ECR `sidec-backend`, `sidec-frontend`, rol OIDC del CI, secretos en Vault | `Bifrost3-0/argocd_application` → `sidec.tf` |
| DNS + ruta del túnel | `argocd_application` → `tyc_cloudflare.tf` |
| Apps ArgoCD `sidec-frontend`, `sidec-backend`, `sidec-db` | `argocd_application` → `tfvars/microservices/09_bifrost_next_apps_dev.tfvars` |
| Values de cada app (chart común `bifrost-app-chart`) | `Bifrost3-0/helm_charts` → `charts/bifrost-app-chart/values-sidec-{frontend,backend,db}.yaml` |
| Secretos (`DATABASE_PASSWORD`, `SECRET_KEY`, `SIDEC_ADMIN_PASSWORD`) | Vault `clients-prod/sidec`, generados por Terraform; llegan como Secret por External Secrets |
| Build y despliegue | `.github/workflows/deploy.yml` (este repo) |

Flujo: push a `main` → CI (import de la app, una sola cabeza de Alembic, lint + build del
frontend) → imágenes `linux/amd64` con tag = SHA corto en ECR → `repository_dispatch` a
`helm_charts` actualiza `image.tag` → ArgoCD sincroniza. El backend aplica `alembic upgrade head`
al arrancar.

Reglas del ecosistema Bifrost que aplican aquí: todo por GitOps (nada permanente con `kubectl` o
`helm` a mano), ningún secreto en git (Terraform → Vault → External Secrets), y las apps nuevas por
`bifrost_next_apps_*` + `bifrost-app-chart`, nunca con módulos legacy ni rutas Kong.

## Cómo cambiar cosas sin romperlas

- **Modelo de datos**: cambiar el modelo, `alembic revision --autogenerate -m "..."` desde
  `backend/`, revisar el script generado (los enums de Postgres no se autogeneran bien: escribir el
  `ALTER TYPE` a mano) y comprobar que queda una sola cabeza. Migraciones aditivas: el pod anterior
  sigue sirviendo mientras arranca el nuevo.
- **Nuevo endpoint**: router en `api/v1/` con su dependencia (`get_current_user` o `require_admin`),
  lógica en un service, SQL en el repository, schema Pydantic propio; registrar el router en
  `main.py`; cliente en `frontend/lib/<modulo>.ts` usando `apiGet`/`apiSend` (nunca `fetch` directo
  sin token).
- **Nueva pantalla**: `frontend/app/<ruta>/page.tsx` + entrada en `components/layout/nav-items.ts`
  (con el rol si es solo ADMIN).
- **Reglas de negocio**: cambiarlas en el service y actualizar `docs/SIDEC_reglas_negocio_funcionalidades.md`
  y este archivo en el mismo cambio; ampliar `scripts/smoke_e2e.py` con la regla nueva.
- **Antes de dar algo por terminado**: `docker compose up -d --build` + `scripts/smoke_e2e.py` en
  verde, `npm run lint` y `npm run build` en `frontend/`.

## Trampas conocidas

- `BACKEND_URL` en runtime no hace nada (ver Configuración).
- Sin `SIDEC_ADMIN_*` en una base vacía nadie puede entrar; el backend lo avisa en el log.
- `estado` de liquidación es `LIQUIDADO`, no `ACTIVA`, aunque los documentos digan lo contrario.
- Los repositories hacen `commit` por operación: una operación de service que toca varias tablas
  no es atómica. **Toda validación va antes de la primera escritura.** Caso real ya corregido: el
  límite de `pago_a_cuenta` se validaba después de que `LiquidacionRepository.create` confirmara,
  y un 400 dejaba una liquidación guardada sin cobranza y el detalle bloqueado para siempre
  (regresión cubierta en `scripts/smoke_e2e.py`).
- La tarea de guías vencidas corre en cada réplica del backend; con una réplica (el despliegue
  actual) no importa, con varias la actualización es idempotente pero se repite.
- `"name": "fronted"` en `frontend/package.json` es un typo histórico, no afecta a nada.
