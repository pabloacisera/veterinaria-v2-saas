# Requirements — Production Hardening

> Migrado desde `docs/tasks/backlog.json`, Sprint 12 — "Pre-Production Hardening".
> Tareas de origen: TASK-102 a TASK-127 (todas en estado `pendiente` al momento de la
> migración). El `id` de tarea original se conserva en `tasks.md` para trazabilidad —
> no crear TASK-IDs nuevos para este trabajo, seguir cerrando los mismos con
> `scripts/task.sh cerrar TASK-XXX` a medida que se completan acá.

## 1. Borde de red y TLS

- WHEN una request llega al dominio público THE SYSTEM SHALL estar protegida por rate
  limiting anti-flood en el borde de Cloudflare (TASK-102).
- WHEN el tráfico llega a Caddy en producción THE SYSTEM SHALL servir sobre HTTPS válido,
  ya sea vía terminación TLS de Cloudflare Tunnel o `auto_https` de Caddy, sin contenido
  mixto (TASK-104).
- WHEN se sirve una respuesta desde `Caddyfile.prod` THE SYSTEM SHALL incluir headers CSP
  correctos y CORS restringido solo a los orígenes esperados del frontend (TASK-105).
- WHEN se configuran los registros DNS del dominio de producción THE SYSTEM SHALL apuntar
  correctamente al VPS Contabo (TASK-120).
- WHEN se valida el certificado SSL de producción THE SYSTEM SHALL usar Let's Encrypt o
  Cloudflare Origin CA correctamente configurado y vigente (TASK-121).

## 2. Credenciales

- WHEN el proyecto pasa de desarrollo a producción THE SYSTEM SHALL usar credenciales y
  secrets nuevos, nunca reutilizar los de desarrollo (TASK-103). Ver también la nota de
  seguridad sobre `INTEGRATIONS.md` — si hubo secrets committeados alguna vez en el
  historial de git, la rotación debe cubrir también esos valores, no solo los de `.env`.

## 3. Backups y recuperación ante desastres

- WHEN corre el cron de backup semanal o se dispara manualmente THE SYSTEM SHALL confirmar
  que los volúmenes Docker (`core_db_data`, etc.) quedan incluidos en el backup periódico,
  no solo el dump lógico de la base (TASK-106).
- WHEN se solicita una restauración THE SYSTEM SHALL poder restaurar exitosamente un backup
  real desde Backblaze B2, verificado con una prueba end-to-end de restore (TASK-116).

## 4. Observabilidad

- WHEN el sistema está en producción THE SYSTEM SHALL exponer métricas de aplicación e
  infraestructura consultables vía Prometheus + Grafana (TASK-107).
- WHEN ocurre una condición crítica (caída de servicio, disco lleno, memoria, backup
  fallido) THE SYSTEM SHALL generar una alerta hacia el canal configurado (TASK-108).
- WHEN ocurre una excepción no controlada en backend o frontend THE SYSTEM SHALL registrarla
  en una herramienta de error tracking (Sentry o equivalente) (TASK-122).
- WHEN el servicio deja de responder externamente THE SYSTEM SHALL ser detectado por un
  monitor de uptime externo (Pingdom, UptimeRobot o similar) (TASK-123).
- WHEN se generan logs de los contenedores Docker THE SYSTEM SHALL estar centralizados en
  un agregador de logs (ej. Loki), si aplica al volumen del proyecto (TASK-124).

## 5. Performance y escalado

- WHEN se sirven assets estáticos del frontend (JS, CSS, imágenes) THE SYSTEM SHALL
  distribuirlos vía Cloudflare CDN (TASK-109).
- WHEN la cantidad de usuarios concurrentes supere ~100 THE SYSTEM SHALL tener evaluado si
  se necesitan read replicas de Postgres (TASK-110).
- WHEN se evalúe correr múltiples instancias de backend THE SYSTEM SHALL tener validado el
  balanceo de carga nativo de Caddy (`reverse_proxy backend1:8000 backend2:8000 ...`, ya
  contemplado en ADR-006) (TASK-111).
- WHEN se ejecuta un load test contra endpoints críticos (login, chat IA, checkout) THE
  SYSTEM SHALL sostener la carga esperada sin degradación inaceptable, medido con k6 o
  artillery (TASK-115).

## 6. Validación contra entorno real

- WHEN se corre la suite E2E completa (Playwright) THE SYSTEM SHALL pasar contra producción
  o un staging idéntico, no solo contra el entorno de desarrollo (TASK-112).
- WHEN se corren los tests de integración THE SYSTEM SHALL pasar contra una base de datos
  real equivalente a producción (TASK-113).
- WHEN se corren los tests de contrato THE SYSTEM SHALL validarse contra las APIs reales de
  terceros (Mercado Pago, Mailjet, Cloudinary, AFIP), no solo contra mocks (TASK-114).

## 7. CI/CD y despliegue

- WHEN se mergea a `main` THE SYSTEM SHALL tener un pipeline que publique imágenes Docker a
  un registry (Docker Hub o GHCR) y despliegue automáticamente (TASK-117).
- WHEN se despliega una nueva versión THE SYSTEM SHALL soportar rolling update sin downtime
  perceptible (TASK-118).
- WHEN un deploy falla o introduce una regresión THE SYSTEM SHALL tener un procedimiento de
  rollback documentado y probado (TASK-119).
- WHEN el script `entrypoint.sh` corre al levantar el contenedor backend THE SYSTEM SHALL
  ejecutar también las migraciones de `community_db`, no solo las de `core_db` (TASK-127 —
  bug conocido, no solo hardening).

## 8. Documentación operativa

- WHEN un operador necesita hacer deploy, rollback, backup, restore o escalar THE SYSTEM
  SHALL tener un runbook documentado con los pasos exactos (TASK-125).
- WHEN hubo cambios de infraestructura durante este sprint THE SYSTEM SHALL reflejarse en el
  architecture diagram del proyecto (TASK-126).
