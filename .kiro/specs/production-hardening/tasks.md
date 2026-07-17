# Tasks — Production Hardening

> Antes de marcar cualquiera de estas como hecha en Kiro, ejecutar
> `scripts/task.sh cerrar TASK-XXX` con el ID original para mantener `backlog.json`
> sincronizado — este archivo no lo reemplaza, lo complementa.

## Borde de red y TLS

- [ ] 1. Configurar rate limiting en Cloudflare (borde anti-flood) — `TASK-102`
- [ ] 2. Verificar HTTPS/TLS: Caddy `auto_https` o terminación TLS de Cloudflare Tunnel — `TASK-104`
- [ ] 3. Auditar CSP headers y CORS restringido en `Caddyfile.prod` — `TASK-105`
- [ ] 4. Configurar registros DNS apuntando al VPS Contabo — `TASK-120`
- [ ] 5. Verificar certificados SSL/Let's Encrypt o Cloudflare Origin CA — `TASK-121`

## Credenciales

- [ ] 6. Rotar todas las credenciales/secrets para producción (no reusar las de dev) — `TASK-103`

## Backups y DR

- [ ] 7. Confirmar backups periódicos de volúmenes Docker (`core_db_data`, etc.) — `TASK-106`
- [ ] 8. Probar restauración de backup desde Backblaze B2 — `TASK-116`

## Observabilidad

- [ ] 9. Configurar monitoring: Prometheus + Grafana — `TASK-107` (requiere ADR, ver design.md)
- [ ] 10. Configurar alerting: caída de servicio, disco lleno, memoria, backups fallidos — `TASK-108`
- [ ] 11. Configurar error tracking (Sentry o similar) — `TASK-122`
- [ ] 12. Configurar uptime monitoring externo (Pingdom, UptimeRobot) — `TASK-123`
- [ ] 13. Verificar log aggregation: Docker logs + Loki si aplica — `TASK-124` (decisión a registrar como ADR, aceptada o descartada)

## Performance y escalado

- [ ] 14. Configurar Cloudflare CDN para assets estáticos — `TASK-109`
- [ ] 15. Evaluar necesidad de read replicas de Postgres (>100 usuarios concurrentes) — `TASK-110`
- [ ] 16. Evaluar load balancing si hay múltiples instancias backend — `TASK-111`
- [ ] 17. Ejecutar load test con k6 o artillery en endpoints críticos — `TASK-115`

## Validación contra entorno real

- [ ] 18. Ejecutar suite E2E completa contra producción (o staging idéntico) — `TASK-112`
- [ ] 19. Ejecutar integration tests con BD real de producción — `TASK-113`
- [ ] 20. Ejecutar contract tests contra APIs reales de terceros (sandbox) — `TASK-114`

## CI/CD y despliegue

- [ ] 21. CI/CD: pipeline que publique imágenes a registry (Docker Hub/GHCR) y deploy automático — `TASK-117`
- [ ] 22. Verificar zero-downtime deploy (rolling update strategy) — `TASK-118`
- [ ] 23. Documentar procedimiento de rollback (última imagen + docker compose) — `TASK-119`
- [ ] 24. Fix `entrypoint.sh`: agregar migraciones de `community_db` — `TASK-127` (bugfix, no requiere spec propio)

## Documentación

- [ ] 25. Documentar runbook: deploy, rollback, backup, restore, escalado — `TASK-125`
- [ ] 26. Actualizar architecture diagram si hubo cambios de infraestructura — `TASK-126`
