---
inclusion: always
---

# Stack tecnológico — Veterinaria V2

FastAPI es el único backend: no hay microservicio separado para el RAG (vive como módulo
dentro del mismo proceso, ver `architecture-decisions.md` → RAG). JavaScript/TypeScript/Go
solo se usan como scripts puntuales o microservicios futuros, y únicamente si la decisión
queda justificada como ADR — no por preferencia, no por defecto.

## Backend (`backend/`)

- **Framework:** FastAPI + Uvicorn (ASGI)
- **DB drivers:** asyncpg, psycopg2-binary; ORM/migraciones: SQLAlchemy 2.x + Alembic
  (dos sets de migraciones: `alembic/` para `core_db`, `community_alembic/` para `community_db`)
- **Auth:** python-jose / PyJWT, passlib + bcrypt, Authlib (Google OAuth2)
- **Validación:** Pydantic v2 (con extra `email`)
- **Colas:** aio-pika (RabbitMQ)
- **Cache/sesiones:** redis (asyncio)
- **RAG:** sentence-transformers, torch, pgvector, LangChain (+ langchain-openai,
  langchain-google-genai, langchain-groq — multi-proveedor de LLM)
- **Documentos:** reportlab (PDF), cloudinary (storage de imágenes/docs)
- **Pagos:** mercadopago SDK
- **Cripto:** cryptography (cifrado de tokens de terceros en DB)
- **Analítica:** pandas, numpy (exports del admin, y a futuro RAG/analítica avanzada)
- **Testing:** pytest, pytest-asyncio, ruff (lint), estructura `unit/ integration/ contract/`

## Frontend (`frontend/`)

- **Framework:** React + Vite + TypeScript
- **Estado servidor:** @tanstack/react-query
- **Routing:** react-router-dom
- **Estilos:** Tailwind CSS + PostCSS
- **Validación:** Zod (cliente) — nunca se confía solo en esto, Pydantic valida siempre en
  backend también
- **Testing:** vitest + @testing-library/react + jsdom
- **Lint:** eslint + typescript-eslint

## Infraestructura (`infra/`, raíz)

- **Orquestación:** Docker Compose (`docker-compose.yml`, `.prod.yml`, `.test.yml`)
- **Reverse proxy:** Caddy (no Nginx — ver ADR-006). `auto_https` desactivado en producción
  porque Cloudflare termina el TLS.
- **Entrada pública:** Cloudflare Tunnel (`cloudflared`) — sin puertos expuestos en el VPS.
  No hay Caddy en desarrollo, solo en producción.
- **Bases de datos:** Postgres + pgvector (`core_db`), Postgres (`community_db`) — nunca se
  tocan en la misma transacción ni con joins directos entre sí.
- **Broker:** RabbitMQ, un solo broker con colas nombradas por dominio (no crear brokers ni
  colas nuevas sin ADR).
- **Backups:** Backblaze B2 (S3-compatible) + restic/rclone, cifrados e incrementales.
- **Producción:** VPS Contabo.

## Comandos de entorno

```bash
make up / make dev / make seed / make test / make lint / make format / make tunnel
# o directamente:
scripts/dev-up.sh · scripts/dev-reset-db.sh · scripts/seed-test-data.sh
scripts/start-tunnel.sh · scripts/start-all.sh
scripts/test-unit.sh · scripts/test-integration.sh · scripts/test-e2e.sh
```

No asumir que el entorno ya está levantado — levantarlo con estos scripts antes de correr o
probar algo.

## CI/CD (`.github/workflows/`)

1. Unit + integration tests en cada push.
2. E2E (Playwright) antes de mergear a `main`.
3. Code Review Agent en cada PR: `static-review.sh` (8 validaciones estáticas: Clean
   Architecture, secrets, UUIDv7, soft-delete, migraciones seguras, tests, docker-compose
   válido) + AI Review (Groq `llama-3.1-70b-versatile`) contra `SPECS.md`/`SKILLS.md`.
