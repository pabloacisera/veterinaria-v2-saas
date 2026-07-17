# Design — Production Hardening

## Enfoque general

Este spec no introduce arquitectura nueva — usa exclusivamente lo ya decidido en
`docs/decisions/` (ver steering `architecture-decisions.md`). El trabajo es de
**configuración, verificación y documentación** sobre la infraestructura existente:
Cloudflare (Tunnel + CDN + borde), Caddy, Docker Compose, Backblaze B2, RabbitMQ/Redis ya
definidos. Si algún punto de este spec requiriera una pieza de infraestructura nueva (ej.
Prometheus + Grafana, Sentry, Loki), corresponde registrar un ADR antes de agregarla,
siguiendo la regla no negociable de `rules.md`.

## 1. Borde de red y TLS

- Rate limiting (TASK-102): configurar reglas en el dashboard de Cloudflare (WAF/Rate
  Limiting Rules), no en Caddy ni en el backend a nivel de infraestructura — el backend
  mantiene su rate limit de negocio (cupo de requests al RAG por CUIT/plan), que es un
  concepto distinto y ya implementado.
- TLS (TASK-104, TASK-121): verificar `Caddyfile.prod` — `auto_https` puede quedar
  desactivado porque Cloudflare termina el TLS (ADR-006), pero validar que el modo de
  Cloudflare sea "Full (strict)" y no "Flexible", para que el tramo Cloudflare↔origen
  también vaya cifrado.
- CSP/CORS (TASK-105): revisar `infra/Caddyfile.prod` contra los orígenes reales del
  frontend en producción; el `nginx.conf.unused` no aplica (Nginx fue descartado, ADR-006).
- DNS (TASK-120): registros A/AAAA o CNAME proxied (naranja) en Cloudflare hacia el VPS
  Contabo, consistente con el modelo de Tunnel (no exponer la IP del VPS directamente si se
  puede evitar).

## 2. Credenciales (TASK-103)

Checklist de rotación: `MP_PLATFORM_*`, `MP_OAUTH_*`, `GOOGLE_CLIENT_SECRET`,
`AFIPSDK_ACCESS_TOKEN`, `CLOUDFLARE_TUNNEL_ID` (nuevo túnel para prod), credenciales de
RabbitMQ/Postgres/Redis, `ENCRYPTION_KEY`. Ninguna se reutiliza de desarrollo. Ver nota de
seguridad general: si `INTEGRATIONS.md` llegó a tener valores reales committeados en algún
momento del historial de git, tratar esos valores como comprometidos independientemente de
esta tarea.

## 3. Backups y DR

- TASK-106: `docker-compose.prod.yml` debe declarar backup de los volúmenes nombrados, no
  solo `pg_dump` — evaluar snapshot de volumen vía `restic` apuntando también a los paths de
  datos, no únicamente al dump lógico.
- TASK-116: ensayo de restore completo en un entorno aislado (no contra producción), midiendo
  tiempo de recuperación (RTO) y pérdida de datos aceptable (RPO), documentado en el runbook.

## 4. Observabilidad

- Prometheus + Grafana (TASK-107) y alerting (TASK-108) son infraestructura nueva → requieren
  ADR antes de implementar, justificando qué problema resuelven que no resuelven los logs de
  Docker actuales.
- Sentry (TASK-122) y uptime monitoring externo (TASK-123): evaluar si un ADR es necesario
  según el impacto — son servicios externos SaaS, no infraestructura propia, pero igual
  agregan una dependencia nueva y deben quedar documentados en `integrations.md`.
- Log aggregation (TASK-124): "si aplica" según el volumen del proyecto — decisión explícita
  a tomar y registrar como ADR (aceptado o descartado, con motivo), no dejarlo implícito.

## 5. Performance y escalado

- CDN (TASK-109): Cloudflare ya está en el flujo de red (ADR-005); habilitar cache de assets
  estáticos del build de frontend no requiere infraestructura nueva.
- Read replicas (TASK-110) y load balancing (TASK-111): **evaluar**, no implementar todavía
  salvo que el volumen real de usuarios lo justifique — Caddy ya soporta múltiples upstreams
  nativamente (ADR-006), así que load balancing es principalmente configuración cuando llegue
  el momento, no una decisión arquitectónica nueva.
- Load test (TASK-115): correr contra staging, nunca contra producción real con datos de
  tenants reales.

## 6. Validación contra entorno real

TASK-112/113/114: requieren un entorno de staging que replique producción (mismas versiones
de Postgres/Redis/RabbitMQ, mismo `docker-compose.prod.yml`). Los contract tests (TASK-114)
usan credenciales de sandbox de cada proveedor (MP sandbox, etc.), nunca las de producción.

## 7. CI/CD

TASK-117/118/119/127 extienden los workflows ya existentes en `.github/workflows/`
(actualmente: unit+integration en push, e2e antes de merge a main, code review agent). Se
agrega un cuarto flujo: build+push de imagen + deploy. El fix de TASK-127 (migraciones de
`community_db` faltantes en `entrypoint.sh`) es un bugfix simple, no necesita spec propio —
se resuelve directo, con test de regresión que verifique que ambos sets de migraciones
(`alembic/` y `community_alembic/`) corren al levantar el contenedor.

## 8. Documentación

TASK-125/126 son actualización de docs para humanos — no bloquean funcionalidad pero sí el
lanzamiento responsable a producción.
