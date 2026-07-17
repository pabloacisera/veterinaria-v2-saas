# Pre-Production Checklist

> Hito obligatorio antes del pase a producción. Completar en orden.

## 1. Seguridad

- [ ] **HTTPS/TLS**: Configurar Caddy con `auto_https on` (producción) o verificar que Cloudflare Tunnel termina correctamente TLS.
- [x] **CSP Headers**: Content-Security-Policy agregado en Caddyfile.prod.
- [x] **CORS**: Caddyfile.prod tiene `Access-Control-Allow-Origin` restringido (cambiar https://midominio.com por el dominio real antes de deploy).
- [x] **httpOnly Cookies**: Migrar tokens JWT de `localStorage` a cookies httpOnly (requiere backend + frontend).
- [ ] **Rate limiting**: Configurar rate limiting en Cloudflare (borde) o agregar build custom de Caddy con `xcaddy`.
- [ ] **Secrets rotation**: Rotar todas las credenciales en producción (no reusar las de dev).

## 2. Infraestructura

- [x] **Resource limits**: Resource limits definidos en docker-compose.yml (base). Verificar antes de deploy.
- [ ] **Volumes persistence**: Confirmar backups periódicos de los volúmenes named (`core_db_data`, etc.).
- [ ] **Monitoring**: Configurar Prometheus + Grafana (métricas de app e infraestructura).
- [x] **Healthchecks**: Todos los servicios tienen healthchecks configurados en docker-compose.yml.
- [x] **Restart policies**: Servicios críticos tienen `restart: unless-stopped`.

## 3. Performance & Escalabilidad

- [ ] **CDN**: Configurar Cloudflare CDN para assets estáticos (JS, CSS, imágenes).
- [x] **Code splitting**: Verificar code splitting por ruta en frontend (React.lazy + Suspense).
- [x] **Database indexes**: HNSW index para pgvector + B-tree indexes en migraciones verificados. Falta EXPLAIN ANALYZE con datos reales.
- [ ] **Read replicas**: Evaluar necesidad de read replicas de Postgres (>100 usuarios concurrentes).
- [ ] **Load balancing**: Si hay múltiples instancias backend, configurar balanceo en Caddy.

## 4. Testing

- [ ] **Full E2E suite**: Correr `tests/e2e-full-stack/*` contra producción (o staging idéntico).
- [ ] **Integration tests**: Correr `pytest src/tests/integration` con BD real.
- [ ] **Contract tests**: Correr `pytest src/tests/contract`.
- [ ] **Load test**: Ejecutar prueba de carga con k6 o artillery en endpoints críticos.
- [ ] **Backup restore test**: Probar restauración desde backup de Backblaze B2.

## 5. Deployment

- [ ] **CI/CD**: Pipeline publica imágenes a registry (Docker Hub / GHCR) y deploy automático.
- [ ] **Zero-downtime deploy**: Verificar estrategia de rolling update.
- [ ] **Rollback plan**: Documentar procedimiento de rollback (última imagen + `docker compose down` + `docker compose up`).
- [ ] **DNS**: Configurar registros DNS (CNAME / A) apuntando al VPS.
- [ ] **SSL certificate**: Verificar que Let's Encrypt o Cloudflare Origin CA emite certificados válidos.

## 6. Monitoreo Post-Deploy

- [ ] **Error tracking**: Configurar Sentio o similar para errores en backend/frontend.
- [ ] **Uptime monitoring**: Configurar healthcheck externo (Pingdom, UptimeRobot, o el mismo Prometheus).
- [ ] **Log aggregation**: Verificar que logs de todos los servicios son accesibles (Docker logs + Loki si aplica).
- [ ] **Alerting**: Configurar alertas para: caída de servicio, disco lleno, memoria agotada, backups fallidos.

## 7. Documentación

- [ ] **Runbook**: Documentar procedimientos de: deploy, rollback, backup, restore, escalado.
- [x] **Env vars**: `.env.example` actualizado con todas las variables. `validate-env.sh` mejorado para checkearlas en CI.
- [ ] **Architecture diagram**: Actualizar diagrama de red/flujo si hubo cambios de infraestructura.
