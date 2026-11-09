# Despliegue en Bifrost — sidec.tyc-iasolutions.com

Entorno de prueba de SIDEC sobre el clúster Laredo de Bifrost, con una base Postgres pequeña
propia. Sustituye al despliegue en VPS con Docker Compose + Caddy (que sigue funcionando para
local o para una VPS).

## Arquitectura

```text
Navegador ──HTTPS──> Cloudflare (cuenta TYC, túnel "tyc")
                         │
                         ▼
              Envoy Gateway bifrost-gw (listener *.tyc-iasolutions.com)
                ├─ PathPrefix /api ──(quita /api)──> sidec-backend:8000   ns bifrost-next-ui
                └─ PathPrefix /     ─────────────────> sidec-frontend:3000 ns bifrost-next-ui
                                                          │
                                         sidec-backend ──> sidec-db.sidec.svc:5432
                                                           Postgres 16.15, PVC 2Gi (openebs-hostpath)
```

La autenticación es la propia de SIDEC (JWT); el Gateway no añade login. Los tres componentes son
apps ArgoCD del proyecto `bifrost-next-dev` sobre el chart común `bifrost-app-chart`.

## Dónde está cada pieza

| Pieza | Ubicación |
|---|---|
| ECR `sidec-backend` / `sidec-frontend`, rol IAM `sidec-github-ecr-push`, secretos | `Bifrost3-0/argocd_application/sidec.tf` |
| DNS `sidec.tyc-iasolutions.com` + regla del túnel | `Bifrost3-0/argocd_application/tyc_cloudflare.tf` |
| Apps ArgoCD | `Bifrost3-0/argocd_application/tfvars/microservices/09_bifrost_next_apps_dev.tfvars` |
| Values | `Bifrost3-0/helm_charts/charts/bifrost-app-chart/values-sidec-{frontend,backend,db}.yaml` |
| Secretos | Vault `clients-prod/sidec`: `DATABASE_PASSWORD`, `SECRET_KEY`, `SIDEC_ADMIN_PASSWORD` (generados por Terraform, nunca en git) |
| CI/CD | `.github/workflows/deploy.yml` |

## Puesta en marcha (una vez)

1. Merge de los cambios de `argocd_application` (crea ECR, rol, secretos, DNS y apps) y de
   `helm_charts` (values). La base arranca enseguida; backend y frontend quedan esperando imagen.
2. En este repo: variable `SIDEC_ECR_ROLE_ARN` = output `sidec_github_role_arn` de Terraform, variable
   `AIP_APP_ID` = `5669545` y secret `AIP_APP_PRIVATE_KEY` con la clave `.pem` de la GitHub App
   `aip-bifrost-agentes`. Cada ejecución pide a la App un token de 1 hora solo para
   `Bifrost3-0/helm_charts`: no hay token personal permanente (el 08/11 un PAT sin acceso a
   `helm_charts` dejó SIDEC sin desplegar).
3. Merge a `main`: el CI publica las imágenes y actualiza los tags; ArgoCD despliega.

## Acceso de la persona que prueba

Cuenta nominal `tester` (rol `ADMIN`), creada por el seed. Su contraseña la genera Terraform:

```bash
vault kv get -field=SIDEC_SEED_ADMIN_PASSWORD clients-prod/sidec
```

`admin` (`SIDEC_ADMIN_PASSWORD`) queda para la administración; no compartirla.

## Datos demo

`SIDEC_SEED_DEMO=true` en `values-sidec-backend.yaml`: con la base sin agencias, el backend carga al
arrancar 6 productos, 6 agencias y 12 guías en todos los estados (ver "Seed" en `AGENTS.md`), así los
reportes y el dashboard tienen datos desde el primer login. Con datos ya cargados no hace nada. Para
volver a los datos demo: vaciar la base (ver Operación) y reiniciar el backend.

## Operación

```bash
# Estado y logs
kubectl -n bifrost-next-ui get pods -l app.kubernetes.io/name=sidec-backend
kubectl -n bifrost-next-ui logs deploy/sidec-backend --tail=100
kubectl -n sidec logs deploy/sidec-db --tail=50

# Consola SQL de la base de prueba
kubectl -n sidec exec -it deploy/sidec-db -- psql -U sidec -d sidec

# Backup puntual (la base es de prueba: no hay backup programado)
kubectl -n sidec exec deploy/sidec-db -- pg_dump -U sidec -d sidec > sidec-$(date +%F).sql
```

- **Empezar de cero**: no hay botón. Vaciar el esquema (`DROP SCHEMA public CASCADE; CREATE SCHEMA public;`
  desde psql) y reiniciar el backend: aplica las migraciones, recrea `admin` y `tester` y vuelve a
  cargar los datos demo.
- **SQL por `kubectl exec`**: la API del clúster está detrás del WAF de Cloudflare, que bloquea SQL en
  los argumentos (`psql -c "..."`). Pasar el SQL por stdin (`kubectl exec -i ... -- psql <<'EOF'`) o
  usar la consola interactiva.
- **Rotar la contraseña del admin**: el bootstrap solo actúa con la tabla `usuarios` vacía; cambiarla
  desde la pantalla **Usuarios** (o vaciando la base, como arriba).
- **Retirar el entorno**: quitar las tres entradas `sidec-*` de los tfvars y la ruta de
  `tyc_cloudflare.tf`, y los values de `helm_charts`. El PVC de la base se borra con su app.

## Límites conscientes (es un entorno de prueba)

- Una réplica de cada componente y Postgres en un Deployment con PVC local (`openebs-hostpath`):
  si el nodo cae, la base no se mueve a otro nodo hasta que vuelva.
- Sin backups programados ni alta disponibilidad. Para producción real: Postgres gestionado
  (o un operador como CloudNativePG) con backup, y al menos 2 réplicas de backend y frontend.
