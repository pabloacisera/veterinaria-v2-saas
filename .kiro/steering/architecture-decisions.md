---
inclusion: auto
name: architecture-decisions
description: Índice de decisiones arquitectónicas ya tomadas (ADR). Usar antes de proponer una alternativa de infraestructura, librería o patrón, o cuando la tarea toque multitenancy, RLS, colas, backups, reverse proxy, RAG, IDs públicos o autenticación — para no re-discutir algo ya decidido y registrado.
---

# Índice de decisiones arquitectónicas

> Resumen de referencia rápida. El detalle completo, contexto y alternativas evaluadas viven
> en `docs/decisions/ADR-XXX.json` — leer el ADR completo antes de proponer cambiar algo acá
> listado. Si una tarea toca alguno de estos temas, la decisión ya está tomada: no
> re-proponerla sin una razón nueva y concreta, y sin registrar un ADR que la reemplace.

| ADR | Estado | Decisión |
|---|---|---|
| ADR-001 | aceptada | Multitenancy: shared schema en `core_db` + RLS de Postgres vía `SET LOCAL app.current_company_id`, derivado del JWT. No schema-per-tenant ni database-per-tenant. |
| ADR-002 | aceptada | RAG: solo pgvector sobre `core_db`. Sin ChromaDB ni vector store administrado separado. |
| ADR-003 | aceptada | Colas: un solo broker RabbitMQ, múltiples colas por dominio. No BullMQ, no brokers separados por dominio. |
| ADR-004 | aceptada | Backups: Backblaze B2 + restic/rclone, cifrados, incrementales, vía cron semanal o botón manual. (Reemplaza y consolida ADR-010.) |
| ADR-005 | aceptada | HTTPS para webhooks de MP: Cloudflare Named Tunnel. ngrok descartado del stack. |
| ADR-006 | aceptada | Reverse proxy: Caddy, no Nginx. `auto_https` desactivado en prod (Cloudflare termina TLS). Rate limiting de borde vive en Cloudflare, no en Caddy. |
| ADR-007 | aceptada | n8n eliminado del stack. Notificaciones resueltas directo en backend + `q.notificaciones`/`q.emails` + crons existentes. |
| ADR-008 | aceptada | Frontend: Feature-Sliced Design (no Atomic Design, no estructura por tipo de archivo). |
| ADR-009 | aceptada | IDs públicos: UUIDv7, no hashids ni UUIDv4 random (ordenable por tiempo, mejor índice). |
| ADR-010 | **reemplazada por ADR-004** | (Duplicaba el detalle de implementación de rclone, ya consolidado en ADR-004.) |
| ADR-011 | aceptada | Toggle de IVA: columna `iva_enabled` en `companies`, no tabla separada (hasta que haya >5-6 settings generales). |
| ADR-012 | aceptada | Activación de cuenta: código numérico de 6 dígitos vía email + Redis (TTL 15 min), no link con token JWT — por restricción de no poder configurar templates de Mailjet vía `.env`. |
| ADR-013 | aceptada | Refresh token migrado a httpOnly cookie + `SameSite=Lax` (+ `Secure` en prod), ya no en `localStorage` (mitigación de XSS). Access token sigue en memoria. |
| ADR-014 | aceptada | Embeddings: fastembed (ONNX) en lugar de sentence-transformers + torch (~2GB → ~90MB). Mismo modelo `all-MiniLM-L6-v2`, mismas 384 dimensiones, cero migración de DB. |

## Reglas derivadas que aplican transversalmente

- No crear una base de datos, cola, broker o herramienta de infraestructura nueva sin un ADR
  que lo justifique con un problema concreto (ver ADR-003, ADR-007).
- No traer una herramienta de orquestación de workflows externa (el caso n8n, ADR-007) para
  algo resoluble con RabbitMQ + Mailjet + crons.
- Antes de tocar el modelo de autenticación/tokens, revisar ADR-012 y ADR-013 juntas — están
  relacionadas (activación de cuenta y manejo de sesión).
