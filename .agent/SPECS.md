# SPECS.md — Sistema de Gestión Veterinaria Multitenant con IA

> **Estado:** vivo, en desarrollo. Este documento se actualiza cada vez que se toma una decisión
> nueva que lo modifique. Toda decisión técnica relevante debe quedar registrada también como
> ADR en `docs/decisions/` (ver sección 11). Si hay conflicto entre este documento y un ADR más
> reciente, gana el ADR más reciente hasta que este archivo se actualice.

- **Versión:** 1.2
- **Última actualización:** 2026-06-25
- **Audiencia:** cualquier agente de IA o desarrollador humano que trabaje en este código.

---

## 1. Visión general del producto

### 1.1 Qué es el sistema

Plataforma SaaS multitenant de gestión y administración veterinaria, fullstack, con un agente
de IA (RAG) integrado que conoce todos los datos cargados por cada tenant y actúa como su
fuente de verdad conversacional. No es un curso ni un MVP descartable: es un producto
profesional pensado para venderse por suscripción a veterinarias reales en Argentina.

### 1.2 Los tres subsistemas

1. **Sistema de Usuario** (el veterinario/la veterinaria): gestión completa — clientes,
   mascotas, historial clínico, caja, tienda, precios, configuración, chat con IA.
2. **Sistema de Cliente** (el dueño de la mascota): portal de solo lectura accesible por un
   código único, para ver/descargar facturación y prescripciones de sus mascotas.
3. **Sistema de Administrador** (el desarrollador/operador de la plataforma): oculto, no
   enlazado desde ningún lugar público. Gestiona usuarios, suscripciones, bloqueos y backups.

Solo los dos primeros se comunican en el landing. El tercero no se menciona públicamente.

### 1.3 Principios de diseño transversales (no negociables)

- **Mobile-first, responsive** en toda la app.
- **Soft-delete siempre.** Nada se borra físicamente; todo se oculta vía flag (`deleted_at`).
- **UUIDv7** como identificador público de toda entidad (ordenable por tiempo, no secuencial,
  no se hashea ni se traduce — se expone tal cual).
- **No se procesa lo mismo dos veces.** Documentos (facturas, prescripciones) se generan una
  sola vez y se cachean; solo se regeneran si los datos que los originan cambiaron.
- **El `.env` del desarrollador es intocable.** Ningún agente modifica ni elimina variables
  existentes en el `.env` real, bajo ninguna circunstancia. Variables nuevas se *agregan*,
  nunca se reemplazan, y se le avisa explícitamente al desarrollador. Cualquier variable
  necesaria solo para testing vive en `.env.test.local`, nunca mezclada con el `.env` real.
- **Sin venta de datos a terceros con fines publicitarios dentro del producto.** (Una eventual
  monetización de datos agregados/anonimizados para ML es un ítem de roadmap de Fase 2 sujeto
  a revisión legal — ver sección 13).
- **Diseño visual a medida**, nunca genérico. Coherencia visual entre los tres subsistemas.
  Estilo moderno pero formal — es una herramienta de gestión, no un producto lúdico.

---

## 2. Arquitectura general

### 2.1 Estructura de carpetas (monorepo)

```
.agent/             → SPECS.md, SKILLS.md (lo que lee cualquier agente antes de tocar código)
docs/                → decisions/ (ADRs), tasks/ (backlog.json), errors/ (errors.log.json)
backend/             → FastAPI, clean architecture
frontend/             → React + Feature-Sliced Design
infra/                → Dockerfiles, Caddyfile, docker-compose.yml de soporte
logs/
tests/                → solo e2e full-stack (ver sección 10)
scripts/              → .sh de soporte (ver sección 12)
.env                  → real, nunca se commitea, nunca se modifica por agentes
.env.example           → nombres de variables sin valores (ver Anexo B)
.env.test.local        → variables exclusivas de testing
README.md
docker-compose.yml
.github/workflows/
```

### 2.2 Arquitectura backend

**FastAPI como único backend**, sin microservicio separado para el RAG (decisión confirmada:
el RAG con LangChain vive dentro del mismo proceso/codebase de FastAPI, como un módulo más).
JavaScript/TypeScript/Go solo se usan como scripts puntuales o microservicios futuros, y
únicamente si la decisión queda justificada como ADR — no por preferencia, no por defecto.

Clean Architecture por capas:

```
  backend/
    src/
      domain/          → entidades, value objects, reglas de negocio puras (sin framework)
      application/      → casos de uso (use cases), orquestación
      infrastructure/    → repositorios concretos (Postgres, Redis, RabbitMQ), clientes de
                          servicios externos (MP, Cloudinary, Mailjet, B2, AFIP)
      interfaces/         → routers FastAPI, schemas Pydantic, websockets
      tests/             → unit/, integration/, contract/
```

Regla dura: el `domain/` no importa nada de `infrastructure/` ni de `interfaces/`. Las
dependencias siempre apuntan hacia adentro.

### 2.3 Arquitectura frontend (Feature-Sliced Design)

```
frontend/src/
  app/       → configuración global, providers, router
  pages/     → composición a nivel de ruta
  widgets/   → bloques grandes reutilizables (TablaClientes, WizardConsulta, ChatPanel)
  features/  → interacciones de negocio (CrearCliente, GenerarFactura, PublicarEnComunidad)
  entities/  → conceptos de negocio (Cliente, Mascota, Consulta, Insumo, Compañía)
  shared/    → UI kit, utils, sin lógica de negocio (modales reutilizables, inputs, etc.)
```

Dependencias unidireccionales: `shared → entities → features → widgets → pages → app`.
Ningún módulo importa de una capa superior a la suya.

### 2.4 Multitenancy: shared schema + Row-Level Security de Postgres

Una única base de datos (`core_db`), todas las tablas tenant-scoped llevan `company_id`.
Postgres RLS filtra automáticamente por `company_id` a nivel de motor de base de datos (no
solo en el código de la aplicación), seteado vía `SET LOCAL app.current_company_id = '<uuid>'`
al inicio de cada transacción, derivado del JWT de la sesión. Esto da una segunda barrera de
aislamiento aunque un desarrollador (humano o agente) olvide filtrar por `company_id` en una
query — la base de datos igual no devuelve filas de otro tenant.

### 2.5 Bases de datos

| Base | Contenido | Por qué separada |
|---|---|---|
| `core_db` (Postgres + pgvector) | Compañías, usuarios, clientes, mascotas, historial, precios, insumos, caja, facturación, suscripciones, embeddings del RAG | Aislamiento estricto por tenant vía RLS |
| `community_db` (Postgres) | Publicaciones, comentarios, likes (mensajes directos: Fase 2) | Naturaleza inter-tenant (cruza compañías), incompatible con el diseño de RLS de `core_db` |

No se crean más bases que estas dos sin un ADR que lo justifique.

### 2.6 Colas (RabbitMQ — un solo broker, múltiples colas)

- `q.backups` — jobs de backup (automático por cron + manual del admin)
- `q.emails` — todo envío vía Mailjet
- `q.pdf-generation` — generación de facturas/prescripciones
- `q.mp-webhooks` — procesamiento async de notificaciones de Mercado Pago
- `q.rag-sync` — generación/actualización de embeddings
- `q.notificaciones` — alertas internas (stock bajo, deuda, suscripción por vencer) que antes
  se pensaron vía n8n; ahora viven acá directamente (ver ADR-007, n8n fue descartado)

### 2.7 Cache (Redis — una instancia, bases lógicas separadas)

- DB 0: sesiones / JWT blacklist
- DB 1: borradores de formularios multi-step (consulta, venta, alta de cliente/mascota) — TTL
- DB 2: caché de conversación reciente del agente de IA
- DB 3: caché/rate-limit de la mini red social

### 2.8 Crons (livianos: solo encolan trabajo)

- `cron-backup-weekly` → encola `q.backups` (más botón manual del admin que encola lo mismo)
- `cron-subscription-billing` → dispara cobro de suscripciones vía MP Preapproval
- `cron-subscription-expiry-check` → marca cuentas vencidas/bloqueadas según gracia
- `cron-mp-pending-reconciliation` → fallback: consulta la API de MP por pagos `pending` viejos
  por si se perdió un webhook

### 2.9 Infraestructura y flujo de red

```
Cliente (navegador)
   → Cloudflare (DNS + Tunnel, rate limiting/WAF de borde)
   → cloudflared (agente, conexión saliente, sin puertos públicos expuestos en el VPS)
   → Caddy (reverse proxy interno, sin TLS propio — Cloudflare ya terminó el TLS)
   → Frontend (React build estático) / Backend (FastAPI)
   → Postgres (core_db, community_db) / Redis / RabbitMQ — nunca expuestos fuera de la red
     interna de Docker
```

- **Producción:** VPS Contabo, Docker Compose, túnel de Cloudflare hacia el puerto interno de
  Caddy. Postgres y Redis nunca tienen un puerto publicado hacia el host.
- **Desarrollo:** cloudflared apunta directamente a `localhost:8000` (FastAPI), sin Caddy.
  Caddy no existe en desarrollo — se introduce solo al Dockerizar para producción.
- **Escalado horizontal futuro:** Caddy soporta múltiples upstreams del backend con balanceo de
  carga nativo (`reverse_proxy backend1:8000 backend2:8000 ...`). No se implementa ahora —
  un solo réplica de backend alcanza para el volumen inicial de usuarios — pero el diseño no
  lo bloquea.
- **Rate limiting:** en el borde de Cloudflare (anti-flood genérico), no en Caddy ni en el
  backend a nivel de infraestructura. El backend sí aplica rate limit de **negocio** (cupo de
  requests al RAG según plan, contado por CUIT — ver sección 7).
- **Caché de Caddy:** no se usa.

---

## 3. Modelo de dominio (entidades principales)

### 3.1 Compañía (cuenta veterinaria / tenant)

Datos obligatorios: nombre de empresa, **CUIT** (obligatorio — sin CUIT válido el sistema no
funciona, es la clave canónica del tenant), nombre del profesional, matrícula. Opcionales:
dirección, sitio web, teléfono, email (recomendado para Mercado Pago).

Cada compañía tiene un usuario `admin` (el dueño/owner) desde el día uno. El modelo de datos
ya contempla `compañía → N usuarios` con un campo `rol` (`admin` | `staff`), aunque hoy solo
`admin` tiene funcionalidad real — `staff` queda reservado para Fase 2 (empleados múltiples).

### 3.2 Cliente

Obligatorios: nombre y apellido, DNI o CUIT (validado por algoritmo módulo 11, ver sección 7.1),
email. Opcionales: dirección, teléfono, ciudad.

**Restricción de unicidad:** no puede haber dos clientes de la misma compañía con el mismo
nombre + mismo DNI/CUIT (ambas condiciones a la vez).

**Flujo de creación:** wizard con validación bloqueante — si falta un campo obligatorio, modal
de advertencia indicando cuál falta, no se permite avanzar.

### 3.3 Mascota

Puede o no tener dueño (cliente). Si tiene, se busca/selecciona de los clientes existentes de
la compañía. Si no, se continúa el formulario sin dueño ("mascota rápida" — reutiliza el mismo
formulario con el buscador de cliente desactivado).

Campos: nombre (puede ser desconocido), raza (obligatoria si se puede determinar), sexo
(obligatorio), edad (opcional), peso (opcional, recomendado), observaciones (opcional),
fotografías (opcional, **máximo 3** en esta sección, vía Cloudinary).

**Restricción de unicidad:** sí puede haber dos mascotas con mismo nombre y raza, pero no con
el mismo dueño simultáneamente.

### 3.4 Historial / Consulta

Núcleo del sistema. Se crea sobre una mascota (buscador/selector, igual que clientes). Campos:

- Motivo de consulta (obligatorio)
- Fecha (la del sistema, no editable)
- Diagnóstico del profesional (obligatorio)
- Tratamiento (opcional — indicación a mediano/largo plazo, ej. "1 pastilla cada 12hs x 3 días")
- Procedimiento(s) (opcional, puede haber más de uno en la misma consulta — ej. inyección)
- Insumos usados (opcional, ligados a procedimiento y/o tratamiento — ver sección 3.5)

De una consulta completa pueden surgir hasta dos documentos generados on-demand:
- **Prescripción**: si hay tratamiento.
- **Factura**: si hubo procedimientos y/o insumos facturables.

Ambos se generan una sola vez y se cachean (ver sección 4.8).

**Formulario por steps:** (1) mascota + dolencia, (2) procedimiento/tratamiento/insumos,
(3) prescripción + facturación. Borrador persistido en Redis (DB 1) mientras no se confirme,
permite ir y volver entre pasos sin perder datos, o limpiar todo y empezar de cero.

### 3.5 Insumos y Precios

**Modelo de stock — unidad base única:** cada insumo define una unidad base (la más pequeña
posible, ej. "pastilla", "ml"). El stock siempre se trackea en esa unidad. Las presentaciones
de compra (ej. "caja de 3 blísters de 12 pastillas") son solo factores de conversión usados al
cargar stock — el sistema convierte automáticamente a unidad base. No se trackea trazabilidad
de paquete/lote individual abierto (decisión explícita para mantener el modelo simple).

Insumos: nombre/marca, descripción, precio unitario, unidad de medida de venta.
Procedimientos: nombre (vacunación, cirugía, baño, desparasitación, etc.) y precio.

Carga: manual (formulario) o vía xlsx (botones "subir" / "descargar plantilla" / "exportar").
La plantilla de prueba (insumos + precios) vive en `backend/src/tests/fixtures/` y se usa para
sembrar datos de desarrollo/test vía `scripts/seed-test-data.sh`.

**Stock insuficiente:** modal de advertencia indicando la cantidad insuficiente; el insumo no
se puede agregar a la etapa de preparación de venta/consulta en esa cantidad. El sistema ofrece
ajustar automáticamente a la cantidad disponible como alternativa.

### 3.6 Caja

Registra ingresos/egresos en efectivo y movimientos derivados de consultas/ventas. Estados:
`pagado` | `pendiente`. Un movimiento `pendiente` (transferencia o QR) solo cambia de estado por
(a) confirmación automática vía webhook de Mercado Pago, o (b) cambio manual del usuario. **No
expira automáticamente** — puede quedar pendiente indefinidamente, es decisión del usuario.

Buscador y filtros por monto, fecha, estado. No editable directamente por el usuario fuera de
los flujos de consulta/venta/cambio manual de estado.

### 3.7 Tienda

Venta de insumos independiente de una consulta (ej. comida, collar). Mismo patrón de wizard
por steps + borrador en Redis: (1) datos del comprador, (2) insumos/productos, (3) método de
pago + facturación. IVA 21% incluido por defecto (toggle en configuración para desactivarlo si
la facturación es puramente interna).

### 3.8 Suscripciones y planes

| Plan | Precio (ARS) | Incluye |
|---|---|---|
| Mensual | $35.000/mes | Uso ilimitado del sistema de gestión, 1 backup semanal, 200 requests/mes al chat IA, soporte en horario de oficina |
| Semestral | $180.000 | Todo lo anterior + 500 requests/mes, acceso prioritario a features |
| Anual | $420.000 (equivale a 12 meses + 3 de regalo = 15 meses) | Todo lo anterior, requests ilimitados al agente, atención prioritaria, **facturación electrónica AFIP incluida** (ver sección 7.3) |

Sin plan "test" (se eliminó: el sandbox de Mercado Pago ya cumple ese rol en desarrollo).

Cobro: Preapproval (recurrente automático) de Mercado Pago para semestral/anual; mensual se
cobra mes a mes de la misma forma.

### 3.9 Comunidad (mini red social entre veterinarias)

**V1:** publicaciones, comentarios, likes — funcional. Compañías con `invisible = true` en
configuración no participan (no publican, no son contactables).
**Mensajes Directos (MD):** mostrados en la UI con estado "Próximamente" (no implementado en
v1, ver roadmap sección 13).

### 3.10 Reglas de unicidad — resumen

- Cliente: único por (compañía, nombre+apellido, DNI/CUIT)
- Mascota: única por (compañía, dueño, nombre, raza) si tiene dueño; sin esa restricción si no
  tiene dueño
- Compañía: única por CUIT a nivel de toda la plataforma

---

## 4. Flujos principales

### 4.1 Autenticación

- Registro manual: usuario, email, password, repassword. Email único en toda la plataforma.
  `isActive = false` hasta confirmar vía código de 6 dígitos enviado por email (codigo generado
  aleatoriamente, persistido en Redis con TTL 15 minutos, ver ADR-012).
- Registro/login con Google: si el email no existe, se crea con `isActive = true` siempre. Un
  email registrado manualmente no puede loguearse luego con Google y viceversa (un solo método
  por cuenta).
- JWT: `access_token` 30 minutos, `refresh_token` 7 días.
- Cada request valida token activo; si expiró, se exige refresh.

### 4.2 Onboarding / primera configuración

Recomendado al usuario en este orden: (1) elegir plan o trial de 3 días, (2) configurar
parámetros básicos + modelo de LLM + conectar Mercado Pago, (3) cargar precios e insumos
(sin esto el sistema no puede facturar ni saber valores), (4) recién ahí cargar clientes,
mascotas y empezar a operar día a día.

### 4.3 Flujo de consulta médica — ver sección 3.4 (detalle de steps/stages)

### 4.4 Flujo de venta en tienda — ver sección 3.7 (mismo patrón de steps + borrador en Redis)

### 4.5 Flujo de pago — suscripción (plataforma)

Integración Mercado Pago **propia del desarrollador** (App 1, credenciales en `.env`).
Checkout Pro sandbox. Vive en `payments/platform_subscriptions/` en el backend.

### 4.6 Flujo de pago — cliente final de la veterinaria

Tres métodos: efectivo, transferencia, QR dinámico. Integración Mercado Pago **vía OAuth por
tenant** (App 2 — cada veterinaria conecta su propia cuenta desde configuración). Vive en
`payments/tenant_checkout/`.

Flujo QR/transferencia:
1. Se genera la factura (consulta o venta) con método de pago QR/transferencia.
2. En caja aparece el movimiento por el monto neto total con estado `pendiente`.
3. Si es QR: botón/link para visualizar el QR dinámico generado con el `access_token` del
   tenant (obtenido vía OAuth y guardado en `tenant_mp_credentials`).
4. Al confirmarse el pago (webhook de MP, idempotente por `payment_id`), el estado cambia a
   `pagado` automáticamente. Fallback: cambio manual por el usuario, o el cron de
   reconciliación si el webhook se perdió.

### 4.7 Flujo de chat / agente IA

RAG sobre pgvector, alimentado por todos los datos cargados por el tenant (clientes, mascotas,
historial, precios, facturación). Si no hay datos cargados, el agente puede responder pero debe
aclarar que lo hace sin contexto específico de la empresa. Respuesta en streaming, mostrada con
efecto máquina de escribir en el frontend; un helper limpia el markdown de la respuesta y lo
renderiza como HTML. Conversaciones persistidas en `core_db` + caché reciente en Redis (DB 2).
Cupo de requests por plan, contado por **CUIT de la compañía** (clave canónica e inmutable del
tenant — sin CUIT, no hay cupo ni sistema).

### 4.8 Generación y versionado de documentos (factura, prescripción, exports)

**Principio: se genera una vez, se cachea en Cloudinary, las siguientes veces solo se pide y
se sirve.** Solo se regenera si los datos que originaron el documento cambiaron.

Tabla `documentos_generados`: `id`, `tipo` (factura | prescripción | export_xlsx),
`entidad_origen_id` (consulta_id o tienda_id), `version` (entero incremental),
`cloudinary_public_id`, `es_version_actual` (bool), `requiere_regeneracion` (bool),
`generado_en`.

- Al crear la consulta/venta: se genera el documento, se sube, `version = 1`,
  `es_version_actual = true`.
- Al editar datos que afectan ese documento: se marca `requiere_regeneracion = true`.
- Al pedir la descarga: si `requiere_regeneracion = true`, se regenera, se sube como
  `version + 1`, la anterior pasa a `es_version_actual = false`. Siempre se sirve la última.

### 4.9 Código de acceso del cliente

Se genera automáticamente la primera vez que una mascota de ese cliente genera una consulta.
Mínimo 12 caracteres alfanuméricos, único, vincula (compañía, cliente). Solo el usuario puede
regenerarlo, se envía por mail vía Mailjet.

### 4.10 Flujo de backup

Automático (cron semanal → `q.backups` → sube a Backblaze B2, cifrado con `restic`/`rclone`).
Manual disponible para el admin en cualquier momento, mismo mecanismo, on-demand.

---

## 5. Integraciones externas

### 5.1 Mercado Pago

**Dos apps, dos integraciones completamente independientes:**

**App 1 — Suscripciones de plataforma (usuario → desarrollador):**
- Credenciales fijas en `.env` (`MP_PLATFORM_ACCESS_TOKEN`, `MP_PLATFORM_PUBLIC_KEY`).
- El desarrollador cobra al veterinario por usar el SaaS.
- Checkout Pro con Preapproval (cobro recurrente).
- Webhook en `MP_PLATFORM_WEBHOOK_SECRET` → `/api/v1/webhooks/mp/platform`.

**App 2 — Checkout de tenants (cliente → veterinaria):**
- El veterinario conecta **su propia cuenta de Mercado Pago** desde Configuración → Mercado Pago.
- El backend redirige al veterinario a la URL de autorización OAuth de MP:
  `https://auth.mercadopago.com/authorization?client_id={MP_OAUTH_APP_ID}&response_type=code&platform_id=mp&redirect_uri={MP_OAUTH_REDIRECT_URI}`
- MP devuelve un `code` al callback `/api/v1/mercadopago/oauth/callback`.
- El backend intercambia ese `code` por el `access_token` del veterinario y lo guarda
  **cifrado** en la tabla `tenant_mp_credentials` de `core_db`. **Nunca en `.env`.**
- Para crear un QR o una transferencia, el backend usa el `access_token` de ese tenant
  específico, obtenido de `tenant_mp_credentials`.
- El webhook de confirmación llega a `/api/v1/webhooks/mp/tenant`. El backend identifica
  a qué tenant pertenece el pago via el campo `external_reference` de la orden/pago,
  que el backend setea con el `company_id` al momento de crear el QR o la transferencia.
  Con ese `company_id` actualiza el estado del movimiento en caja a `pagado`.

Webhooks procesados de forma idempotente (dedupe por `payment_id`) vía `q.mp-webhooks`,
con reconciliación de fallback por cron (`cron-mp-pending-reconciliation`).

### 5.2 Cloudinary

Carpeta raíz `veterinaria.v2`, estructura:
```
veterinaria.v2/{tenantId}/{consultaId}/imgs/
veterinaria.v2/{tenantId}/{consultaId}/docs/
veterinaria.v2/{tenantId}/{tiendaId}/docs/
```
Cuenta nueva creada por el desarrollador. Límite de 3 fotos por mascota.

### 5.3 Mailjet

Casos de uso: link de activación de cuenta, reenvío de código de acceso del cliente,
notificaciones de stock/deuda/suscripción (vía `q.emails`), confirmaciones de seguridad
(cambio de contraseña del admin). Configuración + servicio + templates centralizados.

### 5.4 Backblaze B2

Backups cifrados, incrementales, vía `restic`/`rclone`. Bucket privado, application key con
permisos acotados (no master key).

### 5.5 AFIP / Facturación electrónica

Vía **AfipSDK** (o equivalente), no integración directa con el webservice SOAP de AFIP. Add-on
opcional, **no incluido por defecto** salvo en plan Anual (`facturacion_electronica_incluida:
boolean` por plan, no hardcodeado). La factura interna siempre debe verse profesional.

### 5.6 LLMs

Múltiples proveedores soportados (OpenAI, Gemini, Groq), seleccionables por el usuario en
configuración. LangChain como capa de abstracción.

### 5.7 n8n — **descartado**

Ver ADR-007. Reemplazado por lógica directa en backend + `q.notificaciones` + `q.emails`.

---

## 6. Seguridad

### 6.1 JWT

`access_token`: 30 minutos. `refresh_token`: 7 días. Invalidación de todas las sesiones
activas al cambiar contraseña del admin.

### 6.2 Acceso del subsistema Administrador

- Usuario y contraseña fija (no autoregistro).
- Ruta no enlazada: `/access_role/admin/developer`.
- Recuperación por token-link: 15 minutos, hash SHA-256, invalidado en POST, un token activo
  a la vez, rate limit 3/hora, log de IP/user-agent, mail de aviso al completar.
- TOTP (segundo factor): pendiente de confirmación del desarrollador.

### 6.3 RLS y aislamiento entre tenants — ver sección 2.4

### 6.4 Manejo de IDs

UUIDv7 en toda la plataforma, expuestos directamente en API/URLs.

### 6.5 Validación de inputs

Zod en frontend, Pydantic en backend. Nunca se confía solo en validación de cliente.

### 6.6 Rate limiting

Cloudflare (borde, anti-flood genérico) + backend (cupo de negocio por CUIT/plan).

---

## 7. Reglas de negocio específicas (Argentina)

### 7.1 Validación de CUIT/DNI

Algoritmo módulo 11 sobre los primeros 10 dígitos del CUIT:
- Pesos: `[5, 4, 3, 2, 7, 6, 5, 4, 3, 2]`
- `suma = Σ(dígito_i × peso_i)`, `resto = suma % 11`, `verificador = 11 - resto`
- Si `verificador == 11` → dígito verificador es `0`
- Si `verificador == 10` → combinación inválida para ese prefijo
- Prefijos válidos: `20/23/24/25` (persona física), `27/28`, `30/33/34` (persona jurídica)
- DNI = 8 dígitos centrales del CUIT (rellenar con 0 a la izquierda si tiene 7 dígitos)

Implementado como función pura en `domain/`, sin llamadas externas.

### 7.2 IVA 21%

Toggle en configuración/general, **activado por defecto**. Advertido en landing y onboarding.

### 7.3 Planes y precios — ver sección 3.8

### 7.4 Política de "pendiente" en caja — sin expiración automática (ver sección 3.6)

---

## 8. Subsistema Cliente (portal del dueño de mascota)

Acceso vía código único (ver 4.9). Permisos: solo lectura — visualizar/descargar facturación
(pagada y pendiente) y prescripciones de sus mascotas. Si hay facturación pendiente por
transferencia/QR, tiene acceso al alias/CBU o QR correspondiente.

---

## 9. Subsistema Administrador

Alcance: ver usuarios registrados, plan elegido, inicio/fin de suscripción; bloquear/desbloquear
por CUIT; otorgar suscripción gratuita; generar backups manuales/masivos; exportar datos con
pandas/numpy. Ver sección 6.2 para seguridad de acceso.

---

## 10. Testing

### 10.1 Pirámide de testing

- **Unitarios** — en cada commit
- **Integración** — en cada PR
- **Contrato** (mocks de servicios externos) — en cada PR
- **E2E** (Playwright, flujo completo) — antes de cada merge a `main`

### 10.2 Estructura de carpetas

```
backend/src/tests/  unit/  integration/  contract/  fixtures/
frontend/src/tests/  unit/  e2e/
tests/               e2e-full-stack/
```

### 10.3 CI (GitHub Actions)

Workflow 1: unit + integration en cada push. Workflow 2: e2e antes de mergear a `main`.
Workflow 3: code review (AI agent) en cada PR.

### 10.4 Code Review Agent

Un agente de IA revisa cada PR automáticamente. Flujo:

1. **Static Review** (`.github/scripts/static-review.sh`): 8 validaciones estáticas
   - Clean Architecture (backend + frontend)
   - No secrets hardcoded, .env no commiteado
   - UUIDv7, soft-delete, migrations seguras
   - Tests presentes, docker-compose válido

2. **AI Review** (Groq API — `llama-3.3-70b-versatile`): análisis semántico del diff contra
   SPECS.md + SKILLS.md. Evalúa arquitectura, seguridad, lógica, convenciones.

3. **Veredicto**: PASS o FAIL. Si hay errores críticos → el job falla → no se permite merge.

El resultado se postea como comentario en el PR. El secret `GROQ_API_KEY` debe estar
configurado en el repo.

### 10.5 Vínculo con tareas

Campo `tests_relacionados: []` en cada tarea. Sin tests → estado `en_revision`, no `completada`.

---

## 11. Documentación y trazabilidad

### 11.1 Sistema docs/

ADRs en `docs/decisions/`, tareas en `docs/tasks/backlog.json`, errores en
`docs/errors/errors.log.json` (append-only). Ver formatos en versión anterior de este doc.

### 11.2 Automatización

Pre-commit hook valida JSON Schema. CLI `scripts/task.sh` / `scripts/decision.sh` para agregar
entradas.

### 11.3 Cuándo se escribe cada cosa

- SPECS.md / SKILLS.md → antes de la primera línea de código; se actualizan con cada decisión.
- docs/ → continuo, en tiempo real.
- Docs para humanos → incremental por feature, pulido final antes de cada release.

---

## 12. Scripts (`scripts/`)

```
dev-up.sh / dev-down.sh / dev-reset-db.sh
seed-test-data.sh / migrate.sh / create-admin.sh
backup-manual.sh / restore-backup.sh
start-tunnel.sh / start-all.sh
test-unit.sh / test-integration.sh / test-e2e.sh
lint.sh / format.sh / deploy.sh / logs.sh
task.sh / decision.sh / error.sh
validate-env.sh
```

---

## 13. Roadmap / Fases

### 13.1 v1 (MVP)

Todo lo descrito en este documento salvo lo listado en 13.2.

### 13.2 Fase 2

- Mensajes Directos en Comunidad
- Múltiples usuarios/empleados por compañía (rol `staff` funcional)
- Multi-moneda
- Monetización de datos para ML (requiere revisión legal previa — Ley 25.326)
- Trazabilidad de lote/paquete abierto en stock

---

## 14. Preguntas abiertas

- TOTP opcional para el admin: propuesto, no confirmado.
- Campo `marcado_como_incobrable`: mencionado, no decidido.

---

## Anexo A — Glosario

- **Tenant / Compañía:** una veterinaria en la plataforma.
- **RLS:** Row-Level Security de Postgres.
- **Unidad base:** unidad mínima de stock de un insumo.
- **ADR:** Architecture Decision Record.
- **tenant_mp_credentials:** tabla en `core_db` que guarda el `access_token` de MP de cada
  veterinaria que conectó su cuenta, cifrado con `ENCRYPTION_KEY`.

## Anexo B — Variables de entorno

Ver `.env.example` en la raíz del proyecto.
