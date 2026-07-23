# Snapshot: Sistema de Autenticacion

> **Fecha:** 2026-07-23
> **Commit:** 3baf841
> **Estado:** funcional (testeado E2E con curl)

Este documento captura el estado correcto del sistema de autenticacion. Si algo se rompe en el futuro, este snapshot es la referencia para restaurar.

---

## 1. Archivos del sistema

| Capa | Archivo | Responsabilidad |
|------|---------|-----------------|
| Router | `backend/src/interfaces/routers/auth.py` | Endpoints: register, login, activate, refresh, me, logout, google |
| Router | `backend/src/interfaces/routers/google_callback.py` | Callback de Google OAuth + configuracion OAuth |
| Middleware | `backend/src/interfaces/middleware/auth.py` | Validacion de tokens, paths publicos, bloqueo por suscripcion |
| Use Case | `backend/src/application/use_cases/auth.py` | RegisterUserUseCase, LoginUseCase, ActivateUserUseCase, RefreshTokenUseCase, GoogleAuthUseCase |
| Service | `backend/src/infrastructure/services/session_service.py` | Crear/validar/revocar sesiones en Redis |
| Service | `backend/src/infrastructure/auth/cookie_service.py` | Setear/limpiar cookies httponly |
| Service | `backend/src/infrastructure/services/activation_service.py` | Codigos de activacion (Redis db=2) |
| DI | `backend/src/infrastructure/di.py` | `get_container()` (async, DEBE usar await) |
| Domain | `backend/src/domain/entities/user.py` | Entity User, AuthMethod enum, UserRole enum |
| Config | `.env` | Variables de entorno relacionadas |

---

## 2. Configuracion

### 2.1 Variables de entorno (.env)

```
REDIS_URL=redis://localhost:6379
DATABASE_URL=postgresql://veterinaria_v2:YOUR_DB_PASSWORD@localhost:5444/core_db
JWT_SECRET=<hex string>
JWT_EXPIRES_IN=15m
JWT_REFRESH_SECRET=<hex string>
JWT_REFRESH_EXPIRES_IN=7d
GOOGLE_CLIENT_ID=<string>
GOOGLE_CLIENT_SECRET=<string>
GOOGLE_CALLBACK_URL=https://dev-api.artisandevs.site/api/v1/auth/google/callback
FRONTEND_URL=http://localhost:5173
NODE_ENV=production
```

### 2.2 Orden de middleware (main.py)

El orden importa. Se aplican en orden inverso al registro (ultimo registrado = primero en ejecutar):

```python
app.add_middleware(RLSMiddleware)          # 1ro: Row-Level Security
app.add_middleware(RAGQuotaMiddleware)     # 2do: Quota de RAG
app.add_middleware(AuthMiddleware)         # 3ro: Autenticacion
app.add_middleware(CORSMiddleware, ...)    # 4to: CORS
app.add_middleware(SessionMiddleware, ...) # 5to: Sessiones Starlette
```

### 2.3 Paths publicos (sin auth)

Definidos en `middleware/auth.py`:

```python
PUBLIC_PATHS = {
    "/api/v1/auth/register",
    "/api/v1/auth/login",
    "/api/v1/auth/activate",
    "/api/v1/auth/refresh",
    "/api/v1/auth/google",
    "/api/v1/auth/google/callback",
    "/api/v1/webhooks/mp/platform",
    "/api/v1/webhooks/mp/tenant",
    "/api/v1/mercadopago/oauth/callback",
    "/api/v1/cliente",
    "/health",
    "/docs",
    "/openapi.json",
    "/redoc",
}
```

**NOTA:** `/api/v1/auth/me` y `/api/v1/auth/logout` NO estan en PUBLIC_PATHS. Requieren token valido.

### 2.4 Cookies

| Cookie | Path | Max-Age | Secure | HttpOnly | SameSite |
|--------|------|---------|--------|----------|----------|
| `access_token` | `/` | `JWT_EXPIRES_IN` (900s) | true | true | lax |
| `refresh_token` | `/api/v1/auth/refresh` | `JWT_REFRESH_EXPIRES_IN` (604800s) | true | true | lax |

**CRITICO:** `refresh_token` tiene `path=/api/v1/auth/refresh`, NO `/`. Si se cambia a `/`, el refresh token se envia en todas las requests, lo cual es un riesgo de seguridad.

**CRITICO:** `secure=true` solo funciona con HTTPS. Para testing local con HTTP, usar `Authorization: Bearer <token>` en vez de cookies.

### 2.5 Redis

| DB | Uso | Keys |
|----|-----|------|
| db=0 | Sesiones | `session:{access_token}` (hash: user_id, company_id, TTL=15m) |
| db=0 | Refresh tokens | `refresh:{refresh_token}` (value: "user_id:company_id", TTL=7d) |
| db=2 | Codigo de activacion | `activation:{email}` (value: codigo 6 digitos, TTL=15m) |

---

## 3. Flujos

### 3.1 Registro + Activacion + Login

```
1. POST /api/v1/auth/register
   Body: { name, email, password, company_name, cuit }
   Respuesta: 201 { id, email, name, message }
   Efecto: Crea user (is_active=false), company, subscription (trial), envia codigo por email

2. POST /api/v1/auth/activate
   Body: { email, code }
   Respuesta: 200 { message }
   Efecto: user.is_active = true

3. POST /api/v1/auth/login
   Body: { email, password }
   Respuesta: 200 { access_token, token_type, expires_in }
   Headers: Set-Cookie: access_token=...; Path=/; HttpOnly; Secure
             Set-Cookie: refresh_token=...; Path=/api/v1/auth/refresh; HttpOnly; Secure
   Efecto: Crea sesion en Redis (db=0)
```

### 3.2 Consulta de perfil

```
4. GET /api/v1/auth/me
   Header: Authorization: Bearer <access_token>
   Respuesta: 200 { email, name, company_id }
   Error: 401 si no hay token o token invalido
```

### 3.3 Refresh

```
5. POST /api/v1/auth/refresh
   Cookie: refresh_token=<token>
   Respuesta: 200 { access_token, token_type, expires_in }
   Efecto: Reviega refresh token viejo, crea sesion nueva
```

### 3.4 Logout

```
6. POST /api/v1/auth/logout
   Header: Authorization: Bearer <token>
   Cookie: refresh_token=<token>
   Respuesta: 200 { message }
   Efecto: Borra sesion y refresh token de Redis, limpia cookies
```

### 3.5 Google OAuth

```
1. GET /api/v1/auth/google
   Redirige a: accounts.google.com/oauth2/v2/auth?client_id=...&redirect_uri=...&scope=openid+email+profile

2. Google redirige a: /api/v1/auth/google/callback?code=...&state=...
   Backend: Intercambia code por token, obtiene userinfo
   Si el email ya existe con auth_method=google -> crea sesion
   Si el email es nuevo -> crea company + user (auth_method=google, is_active=true) + sesion
   Respuesta: Set-Cookie (access_token + refresh_token)
   En produccion: RedirectResponse a FRONTEND_URL/login?google=success#access_token=...
   En desarrollo: JSONResponse con los tokens
```

---

## 4. Invariantes criticas

Estas son las reglas que SIEMPRE deben cumplirse. Si se rompen, el auth deja de funcionar.

### 4.1 `get_container()` SIEMPRE con `await`

```python
# CORRECTO
container = await get_container()

# INCORRECTO - causa RuntimeWarning y 401 en todos los endpoints
container = get_container()
```

`get_container()` es `async def`. Sin `await`, devuelve un coroutine object en vez del container real. Este fue el bug que se arreglo el 2026-07-23.

### 4.2 `AuthMethod` enum values

```python
class AuthMethod(str, Enum):
    MANUAL = "manual"
    GOOGLE = "google"
```

El use case `LoginUseCase` rechaza usuarios con `auth_method != MANUAL`. El use case `GoogleAuthUseCase` rechaza usuarios con `auth_method != GOOGLE`. No mezclar.

### 4.3 Validacion de password

`LoginUseCase` valida:
1. Email existe en la DB
2. `auth_method == MANUAL` (si es GOOGLE, rechaza)
3. `is_active == True` (si no, rechaza con "Cuenta no activada")
4. Password hash matchea

### 4.4 Refresh token flow

`RefreshTokenUseCase`:
1. Valida el refresh token en Redis (db=0, key `refresh:{token}`)
2. Busca el user por ID
3. Revierta el refresh token viejo
4. Crea sesion nueva (nuevo access_token + nuevo refresh_token)

### 4.5 Google OAuth - usuario nuevo vs existente

`GoogleAuthUseCase`:
- Si el email ya existe con `auth_method=google` -> crea sesion
- Si el email ya existe con `auth_method=manual` -> ERROR "Este email ya esta registrado con otro metodo"
- Si el email es nuevo -> crea company + user + sesion

---

## 5. Comandos de verificacion

```bash
# 1. Register
curl -s -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","email":"test@test.com","password":"Test1234!","company_name":"Test Vet","cuit":"20-12345678-9"}'

# 2. Get activation code from Redis
docker exec vet-redis redis-cli -n 2 GET "activation:test@test.com"

# 3. Activate
curl -s -X POST http://localhost:8000/api/v1/auth/activate \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","code":"<CODE>"}'

# 4. Login
curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"Test1234!"}'

# 5. GET /me with Bearer token
curl -s http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <ACCESS_TOKEN>"

# 6. Refresh
curl -s -X POST http://localhost:8000/api/v1/auth/refresh \
  -b "refresh_token=<REFRESH_TOKEN>"

# 7. Logout
curl -s -X POST http://localhost:8000/api/v1/auth/logout \
  -H "Authorization: Bearer <TOKEN>" \
  -b "refresh_token=<REFRESH_TOKEN>"

# 8. No token -> expect 401
curl -s -o /dev/null -w "HTTP %{http_code}" http://localhost:8000/api/v1/auth/me
```

---

## 6. Checklist de restauracion

Si el auth se rompe, revisar en este orden:

1. **`auth.py` (router)** - Verificar que `get_container()` tiene `await`
2. **`middleware/auth.py`** - Verificar que el endpoint esta en `PUBLIC_PATHS` o que el token se valida correctamente
3. **`session_service.py`** - Verificar Redis db=0 esta corriendo y las keys existen
4. **`cookie_service.py`** - Verificar paths de cookies (`/` para access, `/api/v1/auth/refresh` para refresh)
5. **`.env`** - Verificar `JWT_SECRET`, `JWT_EXPIRES_IN`, `JWT_REFRESH_EXPIRES_IN`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
6. **`main.py`** - Verificar orden de middleware (AuthMiddleware despues de CORS)
7. **Redis** - Verificar que db=0 y db=2 estan accesibles
8. **DB** - Verificar que la tabla `users` existe y tiene los campos `auth_method`, `is_active`, `google_id`
