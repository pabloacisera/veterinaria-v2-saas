# DEPLOY.md — Guía de Desarrollo y Producción

> Guía completa para levantar el entorno de desarrollo y desplegar en producción.

---

## Tabla de Contenidos

1. [Requisitos Previos](#1-requisitos-previos)
2. [Entorno de Desarrollo (Local)](#2-entorno-de-desarrollo-local)
3. [Los Tres Sistemas en tu Navegador](#3-los-tres-sistemas-en-tu-navegador)
4. [Producción (Contabo VPS)](#4-producción-contabo-vps)
5. [Cloudflare Tunnel — No es Efímero](#5-cloudflare-tunnel--no-es-efímero)
6. [Variables de Entorno](#6-variables-de-entorno)
7. [Operaciones Comunes](#7-operaciones-comunes)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. Requisitos Previos

### Desarrollo local

| Herramienta | Versión mínima | Para qué |
|---|---|---|
| Docker + Docker Compose | v2.x | Infraestructura (DBs, Redis, RabbitMQ) |
| Python | 3.11+ | Backend (FastAPI) |
| Node.js | 20+ | Frontend (React + Vite) |
| pnpm o npm | — | Gestión de paquetes frontend |
| cloudflared | Última | Túnel de desarrollo (opcional) |

### Producción (VPS Contabo)

| Herramienta | Para qué |
|---|---|
| Docker + Docker Compose v2 | Orquestación de servicios |
| rclone | Backups a Backblaze B2 |
| cloudflared | Túnel de Cloudflare (puerto de entrada único) |

---

## 2. Entorno de Desarrollo (Local)

### Paso 1: Configurar variables de entorno

```bash
cp env.example .env
# Editar .env con valores reales (credenciales de servicios externos)
```

**Nunca** commitear el `.env` real. Variables de testing van en `.env.test.local`.

### Paso 2: Levantar infraestructura

```bash
make up
# Equivale a: docker compose up -d core_db community_db redis rabbitmq + migraciones
```

Esto levanta:
- `core_db` → PostgreSQL + pgvector en `localhost:5444`
- `community_db` → PostgreSQL en `localhost:5435`
- `Redis` → `localhost:6379`
- `RabbitMQ` → `localhost:5672` (management UI en `localhost:15672`)
- Ejecuta migraciones Alembic para ambas bases

**Nota:** El esquema de base de datos es manejado exclusivamente por Alembic (single source of truth). No hay SQL init scripts. Ver ADR-016.

### Paso 3 (opcional): Cargar datos de prueba

```bash
make seed
# Crea usuario admin, company de prueba, clientes, mascotas, insumos
```

### Paso 4: Levantar todo junto

```bash
make dev
# Equivale a: start-all.sh (infra + backend + frontend + tunnel)
```

Esto levanta:
- **Backend:** `uvicorn src.main:app --reload` en `http://localhost:8000`
- **Frontend:** `vite dev` en `http://localhost:5173`
- **Túnel:** cloudflared apuntando a `localhost:8000` (opcional)

### Sin Makefile

```bash
scripts/dev-up.sh        # Infraestructura Docker + migraciones
scripts/seed-test-data.sh # Datos de prueba (opcional)
scripts/start-all.sh      # Todo junto
```

### Detener todo

```bash
make down
# Equivale a: docker compose down
```

---

## 3. Los Tres Sistemas en tu Navegador

Una vez levantado `make dev`, los tres subsistemas están disponibles:

### Sistema de Usuario (Veterinario)

```
http://localhost:5173
```

- Registro manual (email + código de activación de 6 dígitos)
- Login con email/password o Google OAuth
- Dashboard completo: clientes, mascotas, consultas, tienda, caja, chat IA, comunidad
- Configuración: planes, suscripción, conexión Mercado Pago

### Sistema de Cliente (Dueño de Mascota)

```
http://localhost:5173/cliente/acceso
```

- Ingresa el **código de acceso** del cliente (se genera automáticamente en la primera consulta)
- Vista de solo lectura: mascotas, facturas (pagadas/pendientes), prescripciones
- Si hay pago pendiente por QR/transferencia, muestra el QR o alias/CBU

### Sistema de Administrador (Operador de Plataforma)

```
http://localhost:5173/access_role/admin/developer
```

- **Ruta oculto** — no está enlazada desde ningún lugar público
- Login con credenciales fijas (SUPER_ADMIN_EMAIL / SUPER_ADMIN_PASSWORD del `.env`)
- Gestión de tenants: listar, bloquear/desbloquear, suscripción gratuita
- Historial de backups, exportar CSV con pandas

### API Docs

```
http://localhost:8000/docs    # Swagger UI
http://localhost:8000/redoc   # ReDoc
```

---

## 4. Producción (EC2 + Nginx + Cloudflare Tunnel)

### 4.1 Arquitectura (Ver ADR-017)

```
Cliente (navegador)
  → Cloudflare (DNS + TLS + WAF + rate limiting)
  → cloudflared (túnel, conexión saliente, sin puertos públicos en VPS)
  → Nginx global (reverse proxy, puerto 81, server_name routing)
  → Backend (FastAPI :4001) / Frontend (archivos estáticos via Nginx)
  → PostgreSQL / Redis / RabbitMQ (red interna Docker, sin puertos expuestos)
```

**Puertos expuestos en producción:** Solo backend (4001) y Nginx (81). Todo el tráfico entra por Cloudflare Tunnel.

### 4.2 Pre-requisitos (Capa 1 - ya configurado)

El servidor EC2 ya tiene configurado:
- Docker + Docker Compose
- cloudflared (servicio systemd)
- Nginx global en `/home/ec2-user/global/nginx/` (puerto 81)
- Cloudflare Tunnel apuntando a `localhost:81`

### 4.3 Desplegar (Capa 2 - por cada app)

```bash
# 1. Conectarse al servidor
ssh -i ~/.ssh/modula-prod-key.pem ec2-user@3.19.181.164

# 2. Clonar/actualizar repo
cd /opt
git clone <repo-url> veter.v2
cd veter.v2

# 3. Copiar .env de producción (NUNCA usar el de desarrollo)
# Generar nuevos secrets con: openssl rand -base64 64
cp env.example .env
nano .env  # Completar con credenciales de PRODUCCIÓN

# 4. Ejecutar deploy
scripts/ops/deploy-prod.sh
```

### 4.4 Deploy manual (paso a paso)

```bash
# Build y levantar backend
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build backend

# Healthcheck
curl http://localhost:4001/health

# Ejecutar migraciones
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec -T backend alembic upgrade head
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec -T backend alembic -c community_alembic.ini upgrade head

# Copiar frontend a directorio de Nginx
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d frontend
sleep 5
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec -T frontend sh -c "cp -r /app/dist/. /opt/veter.v2/frontend/dist/"

# Configurar Nginx (una sola vez)
sudo cp infra/nginx/veterinaria.conf /home/ec2-user/global/nginx/conf.d/
docker exec nginx-global nginx -t && docker exec nginx-global nginx -s reload
```

### 4.5 Archivos de configuración

| Archivo | Ubicación en servidor | Propósito |
|---|---|---|
| `Dockerfile.frontend.prod` | `/opt/veter.v2/` | Frontend simplificado (sin init container) |
| `docker-compose.prod.yml` | `/opt/veter.v2/` | Overrides de producción (sin Caddy/cloudflared) |
| `scripts/ops/deploy-prod.sh` | `/opt/veter.v2/` | Script de deploy adaptado |
| `infra/nginx/veterinaria.conf` | `/home/ec2-user/global/nginx/conf.d/` | Config de Nginx para esta app |

### 4.6 Verificar

```bash
# Health check backend
curl http://localhost:4001/health

# Verificar que el túnel funciona
curl https://veterinaria.artisandevs.site/api/v1/health

# Logs del backend
docker compose -f docker-compose.yml -f docker-compose.prod.yml logs -f backend

# Logs de Nginx
docker exec nginx-global tail -f /var/log/nginx/access.log
```

---

## 5. Cloudflare Tunnel — No es Efímero

El túnel de Cloudflare **no es efímero**. Es un recurso persistente:

- Se crea **una sola vez** en el dashboard de Cloudflare
- Tiene un **ID fijo** permanente (`CLOUDFLARE_TUNNEL_ID` en `.env`)
- Las credenciales viven en `~/.cloudflared/00cbc17e-...json`
- La configuración está en `~/.cloudflared/config.yml`
- El daemon `cloudflared` mantiene la conexión activa permanentemente
- Si se cae, se reconecta automáticamente (servicio systemd en producción)

### Configuración del túnel

El archivo `~/.cloudflared/config.yml` define el routing:

```yaml
tunnel: 00cbc17e-2070-42b8-8a49-83728afd1273
credentials-file: /home/kscod/.cloudflared/00cbc17e-2070-42b8-8a49-83728afd1273.json

ingress:
  - hostname: dev-api.artisandevs.site
    service: http://localhost:8000       # Desarrollo: FastAPI directo
  - service: http_status:404            # Catch-all OBLIGATORIO
```

### Desarrollo vs Producción

| Aspecto | Desarrollo | Producción |
|---|---|---|
| Túnel apunta a | `localhost:8000` (FastAPI) | Caddy (reverse proxy) |
| Caddy | No existe | Sirve estáticos + reverse proxy |
| TLS | Terminado en Cloudflare | Terminado en Cloudflare |
| cloudflared corre en | Terminal del dev | Servicio systemd en VPS |

### Comandos útiles

```bash
# Validar configuración del túnel
cloudflared tunnel ingress validate

# Verificar que el túnel está corriendo
cloudflared tunnel info 00cbc17e-2070-42b8-8a49-83728afd1273

# Logs del túnel
journalctl -u cloudflared -f

# Iniciar en desarrollo (manual)
scripts/start-tunnel.sh
```

### Crear un túnel nuevo (si necesitás otro)

```bash
# 1. Login en Cloudflare
cloudflared tunnel login

# 2. Crear túnel
cloudflared tunnel create <nombre>

# 3. Configurar ingress rules
# 4. Route DNS
cloudflared tunnel route dns <tunnel-id> <hostname>
```

---

## 6. Variables de Entorno

### Estructura

| Archivo | Propósito | ¿Se commitea? |
|---|---|---|
| `env.example` | Nombres de variables sin valores sensibles | Sí |
| `.env` | Valores reales del desarrollador | **Nunca** |
| `.env.test.local` | Variables exclusivas de testing | Opcional |

### Variables críticas por categoría

#### Base de datos

```env
DATABASE_URL=postgresql://veterinaria_v2:YOUR_DB_PASSWORD@localhost:5444/core_db
COMMUNITY_DATABASE_URL=postgresql://veterinaria_v2:YOUR_DB_PASSWORD@localhost:5435/community_db
REDIS_URL=redis://localhost:6379
RABBITMQ_URL=amqp://veterinaria_v2:YOUR_DB_PASSWORD@localhost:5672/
```

**Nota Docker:** En desarrollo, usa `localhost` con puertos mapeados. En producción (dentro de Docker), los `env.py` de Alembic leen estas variables automáticamente y se conectan por nombre de servicio.

#### JWT

```env
JWT_SECRET=<generar con: openssl rand -base64 64>
JWT_REFRESH_SECRET=<generar con: openssl rand -base64 64>
```

#### Mercado Pago

```env
# App 1: Suscripciones de plataforma (el desarrollador cobra)
MP_PLATFORM_ACCESS_TOKEN=APP_USR-...
MP_PLATFORM_WEBHOOK_SECRET=...

# App 2: Checkout por tenant (el veterinario cobra)
MP_OAUTH_APP_ID=...
MP_OAUTH_CLIENT_SECRET=APP_USR-...
```

#### Servicios externos

```env
MAILJET_API_KEY=...          # Emails transaccionales
CLOUDINARY_API_KEY=...       # Fotos y documentos
B2_KEY_ID=...                # Backups
GEMINI_API_KEY=...           # LLM para chat IA
ENCRYPTION_KEY=<hex 32>      # Cifrado de tokens MP
```

#### Admin

```env
SUPER_ADMIN_EMAIL=...        # Login del subsistema administrador
SUPER_ADMIN_PASSWORD=...
ADMIN_ROUTE_PATH=/access_role/admin/developer
```

### Regla para agentes de IA

> **Nunca** modificar ni eliminar variables existentes en `.env`. Solo agregar nuevas,
> y avisar explícitamente al desarrollador cuáles se agregaron.

---

## 7. Operaciones Comunes

### Migraciones de base de datos

```bash
# Ambas bases (desarrollo)
scripts/migrate.sh

# Solo core_db
cd backend && alembic upgrade head

# Solo community_db
cd backend && alembic -c community_alembic.ini upgrade head

# Crear nueva migración (core_db)
cd backend && alembic revision --autogenerate -m "descripción"

# Crear nueva migración (community_db)
cd backend && alembic -c community_alembic.ini revision --autogenerate -m "descripción"
```

### Tests

```bash
# Unitarios backend
make test-unit

# Integración backend
make test-integration

# Unitarios frontend
cd frontend && npm run test

# E2E (requiere stack completo levantado)
make test-e2e

# Linting
make lint

# Formateo
make format
```

### Backups

```bash
# Backup manual (desde el admin panel o por script)
scripts/ops/backup-manual.sh

# Restaurar desde backup
scripts/ops/restore-backup.sh <timestamp>

# Verificar backups en B2
rclone ls b2backup:vet-app-butcket/backups/
```

### Logs

```bash
# Todos los servicios
docker compose logs -f

# Solo backend
docker compose logs -f backend

# RabbitMQ management UI
# Abrir http://localhost:15672 (usuario: veterinaria_v2 / pass: YOUR_DB_PASSWORD)
```

### Reset de base de datos

```bash
# Limpiar y recrear desde cero
make reset
# Equivale a: docker compose down -v && make up && make seed
```

---

## 8. Troubleshooting

### Backend no arranca

**Síntoma:** `docker compose logs backend` muestra error de conexión a DB.

**Causa común:** Las DBs no están saludables aún.

```bash
# Verificar healthchecks
docker compose ps

# Esperar a que estén healthy, luego reiniciar backend
docker compose restart backend
```

### Workers/RabbitMQ no conecta

**Síntoma:** Errores de timeout en logs del backend.

**Solución:** Si estás en desarrollo y no necesitas workers:
```bash
# Agregar al .env
DISABLE_WORKERS=1
```

### Migraciones de community_db fallan

**Síntoma:** `alembic -c community_alembic.ini upgrade head` falla con "connection refused".

**Causa:** community_db no está corriendo o el puerto es incorrecto.

```bash
# Verificar que community_db está corriendo
docker compose ps community_db

# Probar conexión manualmente
psql postgresql://veterinaria_v2:YOUR_DB_PASSWORD@localhost:5435/community_db -c "SELECT 1"
```

### Frontend no conecta al backend

**Síntoma:** Errores CORS en la consola del navegador.

**Solución:** Verificar que CORS_ORIGINS en `.env` incluye `http://localhost:5173`.

### Cloudflare Tunnel no conecta

**Síntoma:** `dev-api.artisandevs.site` retorna error.

```bash
# Verificar configuración
cloudflared tunnel ingress validate

# Verificar que el túnel existe
cloudflared tunnel list

# Reiniciar tunnel
scripts/start-tunnel.sh
```

### Fastembed tarda la primera vez

**Síntoma:** El backend se demora en arrancar la primera vez que se usa el RAG.

**Explicación:** Fastembed descarga el modelo ONNX `all-MiniLM-L6-v2` (~90MB). Las siguientes veces se carga desde caché local.

### RabbitMQ Management UI

Acceder a `http://localhost:15672`:
- Usuario: `veterinaria_v2`
- Password: `YOUR_DB_PASSWORD`

Desde ahí podés ver las colas, mensajes pendientes, y consumidores activos.

---

## Checklist de Producción

Antes del primer deploy real, verificar cada ítem de `docs/milestones/preproduccion.md`.
Las tareas de este checklist están registradas en el backlog como Sprint 12 (TASK-102 a TASK-127).

Resumen de lo crítico:

- [ ] Secrets rotados (no reusar los de dev)
- [ ] DNS configurado en Cloudflare apuntando al VPS (veterinaria.artisandevs.site)
- [ ] Nginx configurado en `/home/ec2-user/global/nginx/conf.d/veterinaria.conf`
- [ ] cloudflared corriendo como servicio systemd en el VPS
- [ ] CI/CD publicando imágenes y deployando automáticamente
- [ ] E2E suite pasando contra staging
- [ ] Load test ejecutado
- [ ] Backup restore probado
- [ ] Monitoring y alerting configurados
- [ ] Runbook documentado
