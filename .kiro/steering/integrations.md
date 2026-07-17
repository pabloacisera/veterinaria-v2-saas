---
inclusion: auto
name: integrations
description: Integraciones externas del backend — Mercado Pago (plataforma y OAuth por tenant), Cloudflare Tunnel, Cloudinary, Mailjet, Backblaze B2, RAG (pgvector/LangChain), Google OAuth2, AfipSDK, RabbitMQ, Redis. Usar cuando se cree, modifique o depure código que hable con alguno de estos servicios externos, o webhooks relacionados.
---

# Integraciones externas

> Los nombres de variables de entorno se listan sin valores. Los valores reales viven
> únicamente en `.env` (nunca en este archivo ni en ningún steering — ver nota de seguridad
> al final).

## 1. Cloudflare Tunnel

Único punto de entrada público, en desarrollo y producción. Sin puertos expuestos.
Variables: `CLOUDFLARE_TUNNEL_ID`, `DEV_TUNNEL_URL`, `BACKEND_URL`. Config en
`~/.cloudflared/config.yml` (fuera del repo). El catch-all `service: http_status:404` es
obligatorio como última ingress rule. En desarrollo apunta directo a `localhost:8000`
(sin Caddy). Caddy solo existe en producción.

## 2. Mercado Pago — App 1 (suscripciones de plataforma)

El desarrollador cobra al veterinario por el SaaS. Checkout Pro + Preapproval (recurrente).
Variables: `MP_PLATFORM_ENV`, `MP_PLATFORM_ACCESS_TOKEN`, `MP_PLATFORM_PUBLIC_KEY`,
`MP_PLATFORM_WEBHOOK_SECRET`, `MP_PLATFORM_SUCCESS_URL/FAILURE_URL/PENDING_URL`.
Webhook: `POST /api/v1/webhooks/mp/platform` — responder 200 inmediatamente y encolar en
`q.mp-webhooks` (MP reintenta si no responde en <22s). Verificar firma HMAC-SHA256 del
webhook siempre. Idempotencia obligatoria por `payment_id` (tabla `mp_webhook_events`,
índice único).

## 3. Mercado Pago — App 2 (checkout OAuth por tenant)

Cada veterinaria conecta su propia cuenta MP desde Configuración. Variables:
`MP_OAUTH_APP_ID`, `MP_OAUTH_CLIENT_SECRET`, `MP_OAUTH_REDIRECT_URI`, `MP_OAUTH_WEBHOOK_URL`.
Flujo: redirect a `auth.mercadopago.com/authorization` con `state=company_id` → callback
`/api/v1/mercadopago/oauth/callback` intercambia `code` por `access_token` → se cifra y
guarda en `tenant_mp_credentials` (**nunca en `.env`**). El `access_token` de cada tenant se
usa para crear QRs/transferencias en su nombre. El webhook de confirmación
(`/api/v1/webhooks/mp/tenant`) identifica el tenant vía `external_reference` (seteado con
`company_id` al crear la orden). Con eso actualiza el movimiento en caja a `pagado`.
Fallback si se pierde el webhook: `cron-mp-pending-reconciliation`.

## 4. Cloudinary

Carpeta raíz `veterinaria.v2/{tenantId}/{consultaId|tiendaId}/{imgs|docs}/`. Máximo 3 fotos
por mascota.

## 5. Mailjet

Casos de uso: activación de cuenta (código de 6 dígitos, no link — ver ADR-012), reenvío de
código de acceso del cliente, notificaciones de stock/deuda/suscripción (vía `q.emails`),
confirmaciones de seguridad.

## 6. Backblaze B2 + restic/rclone

Backups cifrados incrementales. Bucket privado, application key con permisos acotados (nunca
master key). Automatizado vía `cron-backup-weekly` → `q.backups`, o botón manual del admin.

## 7. RAG — sentence-transformers + pgvector

Embeddings generados y guardados en `core_db` (tabla `rag_embeddings`, columna vectorial).
Se encola en `q.rag-sync` en cada create/update de: cliente, mascota, consulta, insumo,
precio, factura. Búsqueda semántica por similitud coseno (`embedding <=> query_embedding`).
Cuota de requests contada en Redis DB 2 por **CUIT de la compañía** (200/500/ilimitado según
plan mensual/semestral/anual).

## 8. Google OAuth2

Login/registro solo para veterinarios (no aplica a portal cliente ni admin). Vía Authlib.
Variables: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_CALLBACK_URL`. Regla de
unicidad: un email registrado manualmente no puede loguearse luego con Google y viceversa
(campo `auth_method` en `users`, HTTP 400 si no coincide).

## 9. AfipSDK (facturación electrónica)

Variable: `AFIPSDK_ACCESS_TOKEN`. **No implementar en v1** — solo plan Anual, a futuro. Dejar
`InfrastructureInterface.generate_afip_invoice()` como stub `NotImplementedError`. Registrar
un ADR antes de implementar cuando llegue el momento, y consultar la documentación
actualizada de AfipSDK (puede haber cambiado).

## 10. RabbitMQ

Un solo broker, colas nombradas por dominio — no crear otras sin ADR: `q.backups`,
`q.emails`, `q.pdf-generation`, `q.mp-webhooks`, `q.rag-sync`, `q.social-notifications`,
`q.notificaciones`. Publicación vía `aio-pika`, mensajes `PERSISTENT`.

## 11. Redis

Una instancia, 4 bases lógicas — no mezclar: DB 0 sesiones/JWT blacklist, DB 1 borradores de
formularios multi-step (TTL 24h), DB 2 caché de conversación del agente IA (TTL 1h), DB 3
rate-limit/caché de comunidad.

---

## Nota de seguridad

Nunca pegar valores reales de API keys, tokens o secrets en este archivo ni en ningún otro
steering — los steering forman parte del código base y suelen commitearse. Los valores viven
solo en `.env` (no versionado). Si necesitás el valor real de una variable durante desarrollo,
pedíselo al desarrollador o leé el `.env` local directamente, nunca lo escribas en Markdown.
