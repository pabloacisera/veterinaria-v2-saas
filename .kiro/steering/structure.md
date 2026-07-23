---
inclusion: always
---

# Estructura del proyecto — Veterinaria V2

## Monorepo (raíz)

```
docs/                → decisions/ (ADRs), tasks/ (backlog.json), errors/ (errors.log.json),
                       milestones/
backend/             → FastAPI, Clean Architecture
frontend/            → React + Feature-Sliced Design
infra/                → Caddyfile, postgres init SQL, githooks
tests/                → solo e2e full-stack (Playwright)
scripts/              → .sh de soporte (dev, ops, utils)
.env                  → real, nunca se commitea, nunca se modifica por agentes
.env.example           → nombres de variables sin valores
.env.test.local        → variables exclusivas de testing
docker-compose.yml / .prod.yml / .test.yml
.github/workflows/
```

## Backend — Clean Architecture por capas

```
backend/src/
  domain/            → entidades, value objects, reglas de negocio puras (sin framework)
    entities/ repositories/ services/ tests/
  application/       → casos de uso (use cases), orquestación
    services/ use_cases/
  infrastructure/    → repositorios concretos (Postgres, Redis, RabbitMQ), clientes externos
    auth/ queue/ rag/ repositories/ services/
  interfaces/         → routers FastAPI, schemas Pydantic, middleware
    middleware/ routers/ schemas/
  tests/              → unit/ integration/ contract/ fixtures/
```

**Regla dura:** `domain/` nunca importa de `infrastructure/` ni de `interfaces/`. Las
dependencias siempre apuntan hacia adentro. Si estás por hacer ese import, la lógica está en
la capa equivocada.

## Frontend — Feature-Sliced Design

```
frontend/src/
  app/       → configuración global, providers, router
  pages/     → composición a nivel de ruta
  widgets/   → bloques grandes reutilizables (TablaClientes, WizardConsulta, ChatPanel)
  features/  → interacciones de negocio: admin, auth, cash, chat, client-portal, clients,
               community, consultations (+steps), documents, onboarding (+steps), pets, store
               (+steps), subscriptions, supplies
  entities/  → conceptos de negocio: admin, auth, cash, chat, client, client-portal, company,
               consultation, document, pet, store, subscription, supply
  shared/    → UI kit, hooks, utils — sin lógica de negocio
```

**Dependencias unidireccionales:** `shared → entities → features → widgets → pages → app`.
Ningún módulo importa de una capa superior a la suya.

## Convenciones de naming

- **Español** para conceptos de dominio de uso diario del veterinario (cliente, mascota,
  consulta, insumo, caja).
- **Inglés** para términos puramente técnicos (repository, service, handler).
- Si hay duda, seguir el patrón ya existente en código similar — no inventar uno nuevo.
- **IDs:** UUIDv7 siempre, expuestos directos en API/URLs. Nunca secuenciales, nunca hasheados.

## Sistema de documentación y trazabilidad (`docs/`)

- `docs/decisions/ADR-XXX.json` — decisiones técnicas (Architecture Decision Records).
- `docs/tasks/backlog.json` — tareas, organizadas en `sprints` + lista plana `tareas`. Cada
  tarea tiene `id`, `titulo`, `estado` (`completada`/`pendiente`/`diferida`), `prioridad`,
  `dependencias`, `decisiones_relacionadas`, `tests_relacionados`.
- `docs/errors/errors.log.json` — log de errores/incidencias detectadas y su resolución
  (append-only).
- `docs/milestones/` — hitos narrativos (ej. `preproduccion.md`).

**Nunca editar a mano estos JSON.** Usar los scripts:

```bash
scripts/decision.sh nueva "Título"      # crea ADR-XXX.json
scripts/task.sh nueva "Título"          # agrega tarea a backlog.json
scripts/task.sh cerrar TASK-XXX          # marca completada (falla sin tests_relacionados)
scripts/error.sh nuevo "módulo" "desc"    # agrega entrada a errors.log.json
```

Una decisión técnica relevante se registra como ADR **antes** de seguir codeando, no después.
