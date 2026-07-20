# Veterinaria V2 — Sistema de Gestión Veterinaria Multitenant con IA

Plataforma SaaS multitenant de gestión y administración veterinaria, fullstack, con un agente de IA (RAG) integrado.

## Estructura del Monorepo

```
.agent/             → SPECS.md, SKILLS.md, INTEGRATIONS.md
docs/               → decisions/ (ADRs), tasks/ (backlog.json), errors/ (errors.log.json)
backend/            → FastAPI, Clean Architecture
frontend/           → React + Feature-Sliced Design
infra/              → Caddyfile, docker-compose de soporte
logs/
tests/              → E2E full-stack (Playwright)
scripts/            → Scripts de soporte (.sh)
.env                → Real, nunca se commitea, nunca se modifica por agentes
env.example         → Nombres de variables sin valores
.env.test.local     → Variables exclusivas de testing
docker-compose.yml  → Orquestación principal
.github/workflows/  → CI/CD
```

## Requisitos Previos

- Docker y Docker Compose
- cloudflared (para túnel de desarrollo)
- Python 3.11+
- Node.js 20+
- pnpm (recomendado) o npm

## Puesta en Marcha Rápida

### Con Makefile (recomendado)

```bash
make up       # Levanta DBs + migraciones
make seed     # Datos de prueba (opcional primera vez)
make dev      # Backend + frontend + túnel
```

### Sin Makefile

```bash
# 1. Levantar infraestructura base (DBs, Redis, RabbitMQ)
scripts/dev-up.sh

# 2. Ejecutar migraciones
scripts/migrate.sh

# 3. Sembrar datos de prueba
scripts/seed-test-data.sh

# 4. Levantar backend + frontend + túnel
scripts/start-all.sh
```

## Comandos Principales

### Makefile (atajos para el día a día)

| Comando | Qué hace |
|---------|----------|
| `make up` | Levanta DBs + migraciones |
| `make down` | Baja contenedores |
| `make migrate` | Ejecuta migraciones Alembic |
| `make seed` | Carga datos de prueba |
| `make reset` | Resetea base de datos |
| `make clear` | Limpia todos los datos (tablas + Redis) |
| `make test` | Tests unitarios + integración |
| `make lint` | Linting (ruff + eslint) |
| `make format` | Formateo (black + prettier) |
| `make tunnel` | Inicia cloudflared tunnel |
| `make dev` | Backend + frontend + túnel |

### Scripts Directos

| Script | Descripción |
|--------|-------------|
| `scripts/dev-up.sh` | Levanta stack completo con Docker Compose |
| `scripts/dev-down.sh` | Para y limpia contenedores |
| `scripts/migrate.sh` | Ejecuta migraciones Alembic |
| `scripts/seed-test-data.sh` | Carga datos de prueba |
| `scripts/dev-clear-data.sh` | Limpia todas las tablas y Redis |
| `scripts/test-unit.sh` | Tests unitarios |
| `scripts/test-integration.sh` | Tests de integración |
| `scripts/test-e2e.sh` | Tests E2E con Playwright |
| `scripts/lint.sh` | Linting |
| `scripts/format.sh` | Formateo |
| `scripts/task.sh` | CLI para gestionar backlog |
| `scripts/decision.sh` | CLI para crear ADRs |
| `scripts/error.sh` | CLI para registrar errores |
| `scripts/utils/*` | Scripts auxiliares (clean ports, create admin, etc.) |
| `scripts/ops/*` | Scripts de deploy y backups |

## Documentación Clave

- **DEPLOY.md** — Guía completa de desarrollo y producción (`DEPLOY.md`)
- **SPECS.md** — Especificación completa del sistema (`.agent/SPECS.md`)
- **SKILLS.md** — Instrucciones operativas para agentes (`.agent/SKILLS.md`)
- **INTEGRATIONS.md** — Guía técnica de integraciones externas (`.agent/INTEGRATIONS.md`)
- **ADRs** — Decisiones de arquitectura en `docs/decisions/`

## Variables de Entorno

Copiar `env.example` a `.env` y completar valores reales:

```bash
cp env.example .env
# Editar .env con valores reales
```

**Nunca** commitear `.env` real. Variables solo para testing van en `.env.test.local`.

## Arquitectura

### Backend (FastAPI - Clean Architecture)
```
backend/src/
  domain/          → Entidades, value objects, reglas de negocio puras
  application/     → Casos de uso (use cases), orquestación
  infrastructure/  → Repositorios (Postgres, Redis, RabbitMQ), clientes externos
  interfaces/      → Routers FastAPI, schemas Pydantic, websockets
  tests/           → unit/, integration/, contract/
```

### Frontend (React - Feature-Sliced Design)
```
frontend/src/
  app/       → Configuración global, providers, router
 
 
  pages/     → Composición a nivel de ruta
  widgets/   → Bloques grandes reutilizables
  features/  → Interacciones de negocio
  entities/  → Conceptos de negocio
  shared/    → UI kit, utils, sin lógica de negocio
```

### Bases de Datos
- `core_db` (Postgres + pgvector) — Datos tenant-scoped con RLS
- `community_db` (Postgres) — Datos inter-tenant (comunidad)

### Colas (RabbitMQ)
- `q.backups`, `q.emails`, `q.pdf-generation`, `q.mp-webhooks`, `q.rag-sync`, `q.social-notifications`, `q.notificaciones`

### Cache (Redis - bases lógicas)
- DB 0: Sesiones / JWT blacklist
- DB 1: Borradores formularios multi-step
- DB 2: Caché conversación agente IA
- DB 3: Rate limit y caché comunidad

## Principios No Negociables

1. **Soft-delete siempre** — `deleted_at`, nunca `DELETE` físico
2. **RLS siempre** — Políticas en toda tabla tenant-scoped
3. **UUIDv7 siempre** — IDs públicos, ordenables por tiempo
4. **Generar una vez, cachear** — Documentos (facturas, prescripciones) se regeneran solo si cambian datos origen
5. **`.env` intocable** — Agentes solo agregan variables, nunca modifican/eliminan existentes
6. **Sin n8n** — Orquestación con RabbitMQ + crons + workers directos

## Testing

Pirámide: Unitarios → Integración → Contrato → E2E full-stack (Playwright)

CI: Unit + Integration en cada push | E2E antes de merge a `main`

## Licencia

Proprietario — Desarrollo interno para comercialización SaaS.