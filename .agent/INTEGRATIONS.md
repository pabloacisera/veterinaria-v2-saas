# INTEGRATIONS.md — Guía de integraciones externas para el agente

> Leé este documento completo antes de tocar cualquier módulo de infraestructura o de
> integraciones externas. Cada sección describe cómo funciona el servicio, qué variables
> del `.env` usa, cómo integrarlo correctamente en FastAPI, y qué errores evitar.
>
> Este documento NO reemplaza a SPECS.md — lo complementa con detalles técnicos de
> implementación que SPECS.md no cubre.

---

## ÍNDICE

1. Cloudflare Tunnel
2. Mercado Pago — App 1 (Suscripciones de plataforma)
3. Mercado Pago — App 2 (Checkout OAuth por tenant)
4. Cloudinary
5. Mailjet
6. Backblaze B2 + rclone (backups)
7. RAG: sentence-transformers + pgvector
8. Google OAuth2
9. AfipSDK (facturación electrónica)
10. RabbitMQ (colas)
11. Redis (caché y borradores)

---

## 1. Cloudflare Tunnel

### Qué hace en este proyecto

Es el único punto de entrada público al backend en desarrollo y en producción. No hay puertos
expuestos al exterior. El túnel ya fue creado por el desarrollador.

### Variables del `.env`

```
CLOUDFLARE_TUNNEL_ID=00cbc17e-2070-42b8-8a49-83728afd1273
DEV_TUNNEL_URL=https://dev-api.artisandevs.site
BACKEND_URL=https://dev-api.artisandevs.site
```

### Archivo de configuración (ya creado por el desarrollador)

Vive en `~/.cloudflared/config.yml` (fuera del repositorio, en la máquina del desarrollador):

```yaml
tunnel: 00cbc17e-2070-42b8-8a49-83728afd1273
credentials-file: /home/kscod/.cloudflared/00cbc17e-2070-42b8-8a49-83728afd1273.json

ingress:
  - hostname: dev-api.artisandevs.site
    service: http://localhost:8000       # FastAPI local, sin Caddy en desarrollo
  - service: http_status:404            # catch-all OBLIGATORIO — sin esto cloudflared falla
```

### Script de inicio

`scripts/start-tunnel.sh` debe ejecutar:

```bash
cloudflared tunnel run --config ~/.cloudflared/config.yml 00cbc17e-2070-42b8-8a49-83728afd1273
```

### Reglas

- El catch-all `- service: http_status:404` es **obligatorio** como último ingress rule.
- El túnel apunta a `localhost:8000` (FastAPI) directamente. **No existe Caddy en desarrollo.**
- Caddy se introduce solo al Dockerizar para producción.
- Para validar la config antes de levantar: `cloudflared tunnel ingress validate`

---

## 2. Mercado Pago — App 1 (Suscripciones de plataforma)

### Qué hace

Los veterinarios le pagan al desarrollador por usar el SaaS. Cobro recurrente (Preapproval).
Estas son las credenciales **propias del desarrollador**, fijas en `.env`.

### Variables del `.env`

```
MP_PLATFORM_ENV=sandbox
MP_PLATFORM_ACCESS_TOKEN=APP_USR-7751308267833414-...
MP_PLATFORM_PUBLIC_KEY=APP_USR-bda41691-...
MP_PLATFORM_WEBHOOK_SECRET=80504fba296a842df...
MP_PLATFORM_SUCCESS_URL=http://localhost:5173/configuracion/subscripcion?status=success
MP_PLATFORM_FAILURE_URL=http://localhost:5173/configuracion/subscripcion?status=failure
MP_PLATFORM_PENDING_URL=http://localhost:5173/configuracion/subscripcion?status=pending
```

### SDK

```bash
pip install mercadopago
```

```python
import mercadopago

sdk = mercadopago.SDK(os.getenv("MP_PLATFORM_ACCESS_TOKEN"))
```

### Flujo de Preapproval (suscripción recurrente)

```python
# Crear plan de suscripción (se hace una sola vez por plan, no por usuario)
preapproval_plan = sdk.preapproval_plan().create({
    "reason": "Plan Mensual VeterinariaV2",
    "auto_recurring": {
        "frequency": 1,
        "frequency_type": "months",
        "transaction_amount": 35000,
        "currency_id": "ARS"
    },
    "back_url": os.getenv("MP_PLATFORM_SUCCESS_URL"),
    "status": "active"
})

# Suscribir a un usuario a un plan
preapproval = sdk.preapproval().create({
    "preapproval_plan_id": plan_id,
    "reason": "Plan Mensual VeterinariaV2",
    "payer_email": user_email,
    "auto_recurring": {
        "frequency": 1,
        "frequency_type": "months",
        "transaction_amount": 35000,
        "currency_id": "ARS",
        "start_date": datetime.now(timezone.utc).isoformat(),
        "end_date": (datetime.now(timezone.utc) + timedelta(days=365)).isoformat()
    },
    "back_url": os.getenv("MP_PLATFORM_SUCCESS_URL"),
    "status": "pending"
})
# preapproval["response"]["init_point"] → URL a la que redirigís al usuario para que autorice
```

### Webhook endpoint

Ruta FastAPI: `POST /api/v1/webhooks/mp/platform`

```python
@router.post("/webhooks/mp/platform")
async def webhook_platform(request: Request):
    # 1. Responder 200 INMEDIATAMENTE antes de procesar
    # MP espera respuesta en menos de 22 segundos o reintenta
    body = await request.json()
    # 2. Encolar en q.mp-webhooks para procesamiento async
    await queue.publish("q.mp-webhooks", {
        "source": "platform",
        "data": body
    })
    return {"status": "ok"}
```

### Verificación de firma del webhook

```python
import hmac, hashlib

def verify_mp_signature(x_signature: str, x_request_id: str, data_id: str, secret: str) -> bool:
    manifest = f"id:{data_id};request-id:{x_request_id};"
    expected = hmac.new(secret.encode(), manifest.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, x_signature.split("v1=")[1])
```

### Idempotencia obligatoria

Siempre verificar si el `payment_id` ya fue procesado antes de actualizar estado. Guardar
`payment_id` en tabla `mp_webhook_events` con un índice único. Si ya existe → responder 200
sin reprocesar.

---

## 3. Mercado Pago — App 2 (Checkout OAuth por tenant)

### Qué hace

Cada veterinaria conecta **su propia cuenta** de Mercado Pago desde Configuración → Mercado
Pago. El backend obtiene el `access_token` de ese tenant vía OAuth y lo guarda cifrado en
`core_db`. Ese token se usa para crear QRs dinámicos y transferencias en nombre de la
veterinaria.

### Variables del `.env`

```
MP_OAUTH_APP_ID=3629510206646986
MP_OAUTH_CLIENT_SECRET=APP_USR-3629510206646986-...
MP_OAUTH_REDIRECT_URI=https://dev-api.artisandevs.site/api/v1/mercadopago/oauth/callback
MP_OAUTH_WEBHOOK_URL=https://dev-api.artisandevs.site/api/v1/webhooks/mp/tenant
```

### Tabla en core_db

```sql
CREATE TABLE tenant_mp_credentials (
    id UUID PRIMARY KEY DEFAULT gen_ulid(),
    company_id UUID NOT NULL REFERENCES companies(id),
    access_token TEXT NOT NULL,        -- cifrado con ENCRYPTION_KEY
    refresh_token TEXT,                 -- cifrado
    token_expires_at TIMESTAMPTZ,
    mp_user_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(company_id)
);
```

### Flujo OAuth completo

**Paso 1: El veterinario hace clic en "Conectar Mercado Pago"**

El backend redirige al usuario a:

```python
auth_url = (
    f"https://auth.mercadopago.com/authorization"
    f"?client_id={os.getenv('MP_OAUTH_APP_ID')}"
    f"&response_type=code"
    f"&platform_id=mp"
    f"&redirect_uri={os.getenv('MP_OAUTH_REDIRECT_URI')}"
    f"&state={company_id}"  # Para identificar al tenant en el callback
)
```

**Paso 2: MP redirige al callback con un `code`**

```python
@router.get("/api/v1/mercadopago/oauth/callback")
async def mp_oauth_callback(code: str, state: str):  # state = company_id
    # Intercambiar code por access_token
    response = requests.post(
        "https://api.mercadopago.com/oauth/token",
        data={
            "client_id": os.getenv("MP_OAUTH_APP_ID"),
            "client_secret": os.getenv("MP_OAUTH_CLIENT_SECRET"),
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": os.getenv("MP_OAUTH_REDIRECT_URI")
        }
    )
    tokens = response.json()
    # Cifrar y guardar en tenant_mp_credentials
    encrypted_token = encrypt(tokens["access_token"])
    await save_tenant_credentials(company_id=state, access_token=encrypted_token, ...)
```

**Paso 3: Crear QR dinámico usando el token del tenant**

```python
def get_tenant_sdk(company_id: str) -> mercadopago.SDK:
    credentials = await get_tenant_credentials(company_id)
    decrypted_token = decrypt(credentials.access_token)
    return mercadopago.SDK(decrypted_token)

# Crear QR dinámico (orden)
tenant_sdk = get_tenant_sdk(company_id)
order = tenant_sdk.order().create({
    "external_reference": company_id,   # CRÍTICO: identifica al tenant en el webhook
    "title": f"Factura #{factura_id}",
    "total_amount": monto,
    "items": [{
        "title": descripcion,
        "unit_price": monto,
        "quantity": 1,
        "unit_measure": "unit"
    }],
    "notification_url": os.getenv("MP_OAUTH_WEBHOOK_URL")
})
# order["response"]["qr_data"] → string del QR para mostrar en frontend
```

### Webhook endpoint de tenant

Ruta FastAPI: `POST /api/v1/webhooks/mp/tenant`

```python
@router.post("/webhooks/mp/tenant")
async def webhook_tenant(request: Request):
    body = await request.json()
    # Extraer external_reference (= company_id) para identificar al tenant
    await queue.publish("q.mp-webhooks", {
        "source": "tenant",
        "data": body
    })
    return {"status": "ok"}
```

### Worker del webhook (procesamiento async en q.mp-webhooks)

```python
async def process_mp_webhook(message: dict):
    source = message["source"]
    data = message["data"]

    if source == "tenant":
        payment_id = data.get("data", {}).get("id")
        # Verificar idempotencia
        if await webhook_already_processed(payment_id):
            return
        # Consultar el pago para obtener external_reference
        # (el body del webhook no siempre trae todos los datos)
        payment = tenant_sdk.payment().get(payment_id)
        company_id = payment["response"]["external_reference"]
        status = payment["response"]["status"]  # "approved", "pending", etc.
        if status == "approved":
            await update_caja_status(company_id, payment_id, "pagado")
        await mark_webhook_processed(payment_id)
```

### Cifrado de tokens

```python
from cryptography.fernet import Fernet
import base64, os

key = base64.urlsafe_b64encode(bytes.fromhex(os.getenv("ENCRYPTION_KEY")))
fernet = Fernet(key)

def encrypt(text: str) -> str:
    return fernet.encrypt(text.encode()).decode()

def decrypt(text: str) -> str:
    return fernet.decrypt(text.encode()).decode()
```

---

## 4. Cloudinary

### Qué hace

Almacena fotos de mascotas y documentos generados (facturas, prescripciones, exports xlsx).
**Principio: generar una vez, cachear, no regenerar salvo que los datos cambien.**

### Variables del `.env`

```
CLOUDINARY_CLOUD_NAME=drbwb3a7r
CLOUDINARY_API_KEY=741755541482749
CLOUDINARY_API_SECRET=URqLboQPMnFxkE_l12ls8wk55e8
CLOUDINARY_ROOT_FOLDER=veterinaria.v2
```

### SDK

```bash
pip install cloudinary
```

```python
import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)
```

### Estructura de carpetas (no negociable)

```
veterinaria.v2/{company_id}/{consulta_id}/imgs/   → fotos de la consulta
veterinaria.v2/{company_id}/{consulta_id}/docs/   → facturas y prescripciones de la consulta
veterinaria.v2/{company_id}/{tienda_id}/docs/      → facturas de ventas de tienda
```

### Subir un documento

```python
def upload_document(file_bytes: bytes, company_id: str, entity_id: str,
                    entity_type: str, filename: str) -> dict:
    folder = f"veterinaria.v2/{company_id}/{entity_id}/docs"
    result = cloudinary.uploader.upload(
        file_bytes,
        folder=folder,
        public_id=filename,
        resource_type="raw",        # Para PDFs y no-imágenes
        overwrite=False             # Nunca sobreescribir — versionar en DB
    )
    return {
        "public_id": result["public_id"],
        "secure_url": result["secure_url"]
    }
```

### Subir una imagen (mascota)

```python
def upload_image(file_bytes: bytes, company_id: str, mascota_id: str) -> dict:
    folder = f"veterinaria.v2/{company_id}/mascotas/{mascota_id}"
    result = cloudinary.uploader.upload(
        file_bytes,
        folder=folder,
        resource_type="image",
        transformation=[{"width": 800, "crop": "limit"}]  # Limitar tamaño
    )
    return {"public_id": result["public_id"], "secure_url": result["secure_url"]}
```

### Lógica de versionado de documentos

Antes de subir cualquier documento, siempre verificar en la tabla `documentos_generados`:

```python
async def get_or_generate_document(entity_id: str, tipo: str) -> str:
    doc = await repo.get_current_version(entity_id, tipo)

    if doc and not doc.requiere_regeneracion:
        # Ya existe y está vigente → devolver URL de Cloudinary directamente
        return doc.cloudinary_public_id

    # Necesita generarse o regenerarse
    file_bytes = await generate_pdf(entity_id, tipo)
    new_version = (doc.version + 1) if doc else 1
    filename = f"{tipo}_v{new_version}_{entity_id}"

    upload_result = upload_document(file_bytes, company_id, entity_id, tipo, filename)

    if doc:
        await repo.mark_old_version(doc.id)

    await repo.create_version(
        entity_id=entity_id,
        tipo=tipo,
        version=new_version,
        cloudinary_public_id=upload_result["public_id"],
        es_version_actual=True,
        requiere_regeneracion=False
    )
    return upload_result["public_id"]
```

---

## 5. Mailjet

### Qué hace

Envía todos los emails del sistema: activación de cuenta, código de acceso al cliente,
alertas de stock/suscripción, notificaciones de seguridad del admin.

### Variables del `.env`

```
MAILJET_API_KEY=b68f0742ae60b60db1af99378f8118cd
MAILJET_API_SECRET=a06976b29966fda1115c6ca5e63f077b
MAILJET_FROM_EMAIL=no-reply@artisandevs.site
MAILJET_FROM_NAME=Soporte Artisandevs
MAILJET_SUPPORT_EMAIL=contacto-vet@artisandevs.site
```

### SDK

```bash
pip install mailjet-rest
```

```python
from mailjet_rest import Client

mailjet = Client(
    auth=(os.getenv("MAILJET_API_KEY"), os.getenv("MAILJET_API_SECRET")),
    version="v3.1"    # SIEMPRE v3.1, no v3
)
```

### Limitaciones críticas a conocer

- **Plan gratuito: 6.000 emails/mes, pero máximo 200 por DÍA.** En producción con muchos
  tenants activos puede quedarse corto. Monitorear y alertar antes de alcanzar el límite.
- Mailjet **no soporta** el parámetro `send_at` para emails transaccionales (solo para
  campañas). Si necesitás envío diferido, hacelo con un delay en la cola `q.emails`.
- **Usar siempre Send API v3.1**, no v3. La v3.1 da mejor feedback de errores.

### Envío de email con template

```python
def send_email(to_email: str, to_name: str, template_id: int, variables: dict) -> bool:
    data = {
        "Messages": [{
            "From": {
                "Email": os.getenv("MAILJET_FROM_EMAIL"),
                "Name": os.getenv("MAILJET_FROM_NAME")
            },
            "To": [{"Email": to_email, "Name": to_name}],
            "TemplateID": template_id,
            "TemplateLanguage": True,   # OBLIGATORIO para que funcionen las variables
            "Variables": variables
        }]
    }
    result = mailjet.send.create(data=data)
    return result.status_code == 200
```

### Templates necesarios (crear en el panel de Mailjet)

Crear cada template en Mailjet Dashboard → Transactional → My Templates. Anotar el ID
numérico que Mailjet asigna y guardarlo en constantes del código (no en `.env`):

| Constante | Uso | Variables principales |
|---|---|---|
| `TEMPLATE_ACTIVACION_CUENTA` | Link de activación al registrarse manualmente | `activation_url`, `user_name` |
| `TEMPLATE_CODIGO_CLIENTE` | Código de acceso al portal del cliente | `access_code`, `client_name`, `company_name` |
| `TEMPLATE_RESET_ADMIN` | Link de reset de contraseña del admin | `reset_url`, `ip_address` |
| `TEMPLATE_CAMBIO_PASSWORD` | Aviso de que la contraseña fue cambiada | `ip_address`, `timestamp` |
| `TEMPLATE_STOCK_BAJO` | Alerta de insumo con stock bajo | `insumo_nombre`, `stock_actual`, `company_name` |
| `TEMPLATE_SUSCRIPCION_VENCE` | Aviso de suscripción próxima a vencer | `dias_restantes`, `plan_nombre`, `renewal_url` |
| `TEMPLATE_BIENVENIDA` | Email de bienvenida al registrarse | `user_name`, `onboarding_url` |

### Worker del queue

```python
async def process_email_job(job: dict):
    await send_email(
        to_email=job["to_email"],
        to_name=job["to_name"],
        template_id=job["template_id"],
        variables=job["variables"]
    )
```

---

## 6. Backblaze B2 + rclone (backups)

### Qué hace

Almacena los backups cifrados de `core_db` y `community_db` de forma automática (cron
semanal) y manual (botón del admin).

### Variables del `.env`

```
B2_KEY_ID=005e9811ff6e3da0000000001
B2_APPLICATION_KEY=K005/F624kLggdI8OfD6dG77bAa/tuQ
B2_BUCKET_NAME=vet-app-butcket
B2_ENDPOINT=s3.us-east-005.backblazeb2.com
```

### Instalación de rclone (en el servidor/VPS)

```bash
curl https://rclone.org/install.sh | sudo bash
```

### Configuración de rclone (una sola vez, en el servidor)

```bash
rclone config create b2backup b2 \
  account "$B2_KEY_ID" \
  key "$B2_APPLICATION_KEY"
```

Esto crea `~/.config/rclone/rclone.conf`. El agente debe generar este archivo
programáticamente en el script de backup si no existe.

### Script de backup (`scripts/backup.sh`)

```bash
#!/bin/bash
set -e

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/tmp/backups/$TIMESTAMP"
mkdir -p "$BACKUP_DIR"

# Dump de core_db
pg_dump "$DATABASE_URL" | gzip > "$BACKUP_DIR/core_db_$TIMESTAMP.sql.gz"

# Dump de community_db
pg_dump "$COMMUNITY_DATABASE_URL" | gzip > "$BACKUP_DIR/community_db_$TIMESTAMP.sql.gz"

# Subir a B2 con --fast-list (reduce llamadas a la API de B2)
rclone sync "$BACKUP_DIR" "b2backup:$B2_BUCKET_NAME/backups/$TIMESTAMP" \
  --fast-list \
  --transfers 10 \
  --b2-hard-delete

# Limpiar temporales
rm -rf "$BACKUP_DIR"

echo "Backup completado: $TIMESTAMP"
```

### Worker del queue (llamado desde el cron y desde el admin)

```python
async def process_backup_job(job: dict):
    import subprocess
    result = subprocess.run(
        ["bash", "scripts/backup.sh"],
        env={**os.environ},
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        await log_error("backup_service", result.stderr)
        raise Exception(f"Backup falló: {result.stderr}")
    await log_backup_success(result.stdout)
```

### Retención de backups

Configurar en el panel de Backblaze B2: retener versiones por 30 días, luego eliminar
automáticamente. Esto evita que el bucket crezca indefinidamente.

---

## 7. RAG: sentence-transformers + pgvector

### Qué hace

Convierte los datos del tenant (clientes, mascotas, historial, precios) en embeddings
vectoriales y los guarda en `core_db` con pgvector para búsqueda semántica. El agente de
IA usa estos embeddings para responder preguntas sobre los datos de la empresa.

### Variables del `.env`

```
EMBEDDINGS_MODEL=sentence-transformers/all-MiniLM-L6-v2
VECTOR_DIMENSION=384    # CRITICO: all-MiniLM-L6-v2 produce 384 dimensiones, NO 768
```

### Instalacion

```bash
pip install fastembed pgvector langchain langchain-community
```

### Inicializacion del modelo (cargar una sola vez al arrancar FastAPI)

```python
from fastembed import TextEmbedding
from functools import lru_cache

@lru_cache(maxsize=1)
def get_embedding_model() -> TextEmbedding:
    model_name = os.getenv("EMBEDDINGS_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    return TextEmbedding(model_name=model_name)

def generate_embedding(text: str) -> list[float]:
    model = get_embedding_model()
    embedding = list(model.embed([text]))[0]
    return embedding.tolist()
```

### Tabla de embeddings en core_db

```sql
-- Habilitar extensión (en la primera migración de Alembic)
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tabla de embeddings RAG
CREATE TABLE rag_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_ulid(),
    company_id UUID NOT NULL,
    entidad_tipo VARCHAR(50) NOT NULL,   -- 'cliente', 'mascota', 'consulta', 'insumo', etc.
    entidad_id UUID NOT NULL,
    contenido TEXT NOT NULL,             -- El texto que fue embebido
    embedding vector(384),               -- VECTOR_DIMENSION = 384
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índice HNSW para búsqueda aproximada rápida
CREATE INDEX ON rag_embeddings
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- RLS
ALTER TABLE rag_embeddings ENABLE ROW LEVEL SECURITY;
CREATE POLICY rag_tenant_isolation ON rag_embeddings
    USING (company_id = current_setting('app.current_company_id')::UUID);
```

### Sincronización del RAG (worker de q.rag-sync)

```python
async def sync_rag_for_entity(job: dict):
    """
    Se encola cada vez que se crea/modifica: cliente, mascota,
    consulta, insumo, precio, factura.
    """
    company_id = job["company_id"]
    entity_type = job["entity_type"]
    entity_id = job["entity_id"]
    text = job["text"]  # El texto preparado para embebido

    embedding = generate_embedding(text)

    await repo.upsert_embedding(
        company_id=company_id,
        entidad_tipo=entity_type,
        entidad_id=entity_id,
        contenido=text,
        embedding=embedding
    )
```

### Búsqueda semántica (para el chat del agente)

```python
async def search_similar(query: str, company_id: str, limit: int = 5) -> list[dict]:
    query_embedding = generate_embedding(query)

    # Búsqueda por similitud coseno
    results = await db.fetch_all("""
        SELECT entidad_tipo, entidad_id, contenido,
               1 - (embedding <=> $1::vector) AS similarity
        FROM rag_embeddings
        WHERE company_id = $2
        ORDER BY embedding <=> $1::vector
        LIMIT $3
    """, query_embedding, company_id, limit)

    return [dict(r) for r in results]
```

### Cuota de requests al RAG

La cuota se cuenta en Redis (DB 2) por CUIT de la compañía. Ver SPECS.md sección 4.7.

```python
async def check_rag_quota(company_cuit: str, plan: str) -> bool:
    limits = {"mensual": 200, "semestral": 500, "anual": -1}  # -1 = ilimitado
    limit = limits.get(plan, 0)
    if limit == -1:
        return True

    key = f"rag:quota:{company_cuit}:{datetime.now().strftime('%Y-%m')}"
    current = await redis.incr(key)
    if current == 1:
        await redis.expire(key, 60 * 60 * 24 * 31)  # TTL de 31 días

    return current <= limit
```

---

## 8. Google OAuth2

### Qué hace

Login/registro con cuenta de Google para los usuarios (veterinarios). No aplica al portal
de clientes ni al admin.

### Variables del `.env`

```
GOOGLE_CLIENT_ID=772227615773-dlav5bdvldpccm61q7rdrrcrg7g953kk.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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
GOOGLE_CALLBACK_URL=https://dev-api.artisandevs.site/api/v1/auth/google/callback
```

### SDK

```bash
pip install authlib httpx
```

### Implementación con Authlib (recomendado sobre implementación manual)

```python
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config

config = Config(".env")
oauth = OAuth(config)

oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"}
)

@router.get("/auth/google")
async def google_login(request: Request):
    redirect_uri = os.getenv("GOOGLE_CALLBACK_URL")
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/auth/google/callback")
async def google_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get("userinfo")
    # user_info contiene: email, name, picture, sub (Google ID)

    existing_user = await user_repo.find_by_email(user_info["email"])

    if existing_user:
        if existing_user.auth_method != "google":
            raise HTTPException(400, "Este email ya está registrado con otro método")
        # Login → emitir JWT
        return create_tokens(existing_user)
    else:
        # Registro → crear usuario con isActive=True
        new_user = await user_repo.create_google_user(
            email=user_info["email"],
            name=user_info["name"],
            google_id=user_info["sub"],
            is_active=True,
            auth_method="google"
        )
        return create_tokens(new_user)
```

### Regla de unicidad de método de auth

Un email registrado manualmente no puede loguarse con Google y viceversa. La tabla `users`
debe tener un campo `auth_method: Enum("manual", "google")`. Si el email existe con otro
método, devolver HTTP 400 con mensaje claro.

---

## 9. AfipSDK (facturación electrónica)

### Variables del `.env`

```
AFIPSDK_ACCESS_TOKEN=nrt0xgwGHPPLgfnqJkwN6EIW0B8gmS0U9tf1TFq5yETn4QTjLpAxQzCLRAYyrYdz
```

### Estado en el roadmap

**Solo disponible para plan Anual.** No implementar en v1. Dejar preparada la interfaz
`InfrastructureInterface.generate_afip_invoice()` en la capa de infrastructure con una
implementación stub que lanza `NotImplementedError`. Cuando llegue el momento, registrar
un ADR antes de implementar y consultar la documentación actualizada de AfipSDK.com.

---

## 10. RabbitMQ (colas)

### Variables del `.env`

```
RABBITMQ_URL=amqp://veterinaria_v2:YOUR_DB_PASSWORD@localhost:5672/
```

### SDK

```bash
pip install aio-pika
```

### Colas definidas (no crear otras sin ADR)

| Cola | Productor | Consumidor |
|---|---|---|
| `q.backups` | cron semanal + admin | worker de backup |
| `q.emails` | cualquier módulo del backend | worker de Mailjet |
| `q.pdf-generation` | flujo de consulta + tienda | worker de generación de PDF |
| `q.mp-webhooks` | endpoints de webhook de MP | worker de procesamiento de pago |
| `q.rag-sync` | cualquier create/update de entidad | worker de embeddings |
| `q.social-notifications` | módulo de comunidad | worker de notificaciones sociales |
| `q.notificaciones` | módulo de stock, crons de suscripción | worker de alertas internas |

### Patrón de publicación

```python
import aio_pika, json

async def publish(queue_name: str, payload: dict):
    connection = await aio_pika.connect_robust(os.getenv("RABBITMQ_URL"))
    async with connection:
        channel = await connection.channel()
        await channel.declare_queue(queue_name, durable=True)
        await channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(payload).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            ),
            routing_key=queue_name
        )
```

---

## 11. Redis (caché y borradores)

### Variables del `.env`

```
REDIS_URL=redis://localhost:6379
```

### SDK

```bash
pip install redis[asyncio]
```

### Bases lógicas (no mezclar)

| Base | Uso | TTL |
|---|---|---|
| DB 0 | Sesiones / JWT blacklist | Igual al refresh_token (7d) |
| DB 1 | Borradores de formularios multi-step | 24 horas |
| DB 2 | Caché de conversación reciente del agente | 1 hora |
| DB 3 | Rate limit y caché de la comunidad | Variable |

```python
import redis.asyncio as redis

# Conexión por base lógica
def get_redis(db: int = 0):
    return redis.from_url(os.getenv("REDIS_URL"), db=db)

sessions_redis = get_redis(db=0)
drafts_redis = get_redis(db=1)
ai_cache_redis = get_redis(db=2)
social_redis = get_redis(db=3)
```

### Borradores de formularios multi-step

```python
async def save_draft(user_id: str, form_type: str, step: int, data: dict):
    key = f"draft:{form_type}:{user_id}"
    await drafts_redis.hset(key, step, json.dumps(data))
    await drafts_redis.expire(key, 86400)  # 24 horas

async def get_draft(user_id: str, form_type: str) -> dict:
    key = f"draft:{form_type}:{user_id}"
    raw = await drafts_redis.hgetall(key)
    return {int(k): json.loads(v) for k, v in raw.items()}

async def clear_draft(user_id: str, form_type: str):
    key = f"draft:{form_type}:{user_id}"
    await drafts_redis.delete(key)
```

### JWT blacklist (logout / cambio de contraseña)

```python
async def blacklist_token(jti: str, expires_in_seconds: int):
    await sessions_redis.setex(f"blacklist:{jti}", expires_in_seconds, "1")

async def is_blacklisted(jti: str) -> bool:
    return await sessions_redis.exists(f"blacklist:{jti}") > 0
```
