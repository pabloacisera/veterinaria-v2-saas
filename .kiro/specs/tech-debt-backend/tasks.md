# Tasks — Deuda técnica de backend (diferida)

> Migrado desde `docs/tasks/backlog.json` — 3 tareas en estado `diferida` (no canceladas,
> pospuestas conscientemente). No tienen `design.md`/`requirements.md` propio porque son
> ítems puntuales de refactor/cobertura, no features nuevas. Revisar antes de cada sprint de
> hardening si alguna pasa a estar lista para tomarse.

- [ ] 1. Split `admin.py` (232 líneas) — extraer lógica compartida de listado/export — `TASK-076`
- [ ] 2. Aumentar cobertura de tests unitarios para use cases que no cubren todos los branches — `TASK-080`
- [ ] 3. Tests de integración para flujos críticos faltantes — `TASK-081`

## Contexto

Estas tres tareas quedaron explícitamente diferidas en `backlog.json` en lugar de
completarse o cancelarse — respetar esa distinción al retomarlas: no son bugs urgentes, son
mejoras de mantenibilidad y cobertura conscientemente pospuestas frente a prioridades de
producto. Antes de tomarlas, confirmar con el desarrollador si siguen siendo prioridad o si
el checklist de `production-hardening` (Sección 6, validación contra entorno real) las vuelve
más urgentes de lo que eran al diferirlas.
