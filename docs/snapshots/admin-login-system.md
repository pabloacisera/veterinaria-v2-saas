# Snapshot: Sistema de Login del Administrador

> **Fecha:** 2026-07-29
> **Estado:** funcional (testeado con curl)

Este documento captura el estado correcto del sistema de autenticacion del administrador.
Si algo se rompe en el futuro, este snapshot es la referencia para restaurar.

**IMPORTANTE:** El sistema de admin es completamente independiente del auth de usuario.
Token distinto (`admin_token`), storage distinto (localStorage, no cookies del auth principal),
rutas distintas (`/access_role/...`), redirect distinto (al login de admin, nunca al de usuario).

---

## 1. Archivos del sistema

| Capa | Archivo | Responsabilidad |
|------|---------|-----------------|
| Router | `backend/src/interfaces/routers/admin.py` | Endpoints: login, logout, reset/request, reset/confirm, companias CRUD, exportar, backup. Prefijo dinamico via `ADMIN_ROUTE_PATH` |
| Use Case | `backend/src/application/use_cases/admin.py` | AdminLoginUseCase, RequestAdminResetUseCase, ConfirmAdminResetUseCase, ListCompaniesUseCase, BlockCompanyUseCase, GrantFreeSubscriptionUseCase, ExportCompaniesUseCase |
| Service | `backend/src/infrastructure/auth/cookie_service.py` | `set_admin_token_cookie()`, `clear_admin_token_cookie()` — cookie scoped al prefijo admin |
| Service | `backend/src/infrastructure/auth/jwt.py` | `JWTService.create_tokens()` — genera access_token con payload `{sub: "admin", company_id: "admin"}` |
| Dependency | `backend/src/infrastructure/di.py` | `get_container()` resuelve AdminLoginUseCase con sus dependencias |
| Page | `frontend/src/pages/AdminLogin.tsx` | Wrapper que renderiza `<AdminLogin />` |
| Page | `frontend/src/pages/AdminDashboard.tsx` | Dashboard con sidebar (companias, backups, exportar), guarda con check de `admin_token` en localStorage |
| Feature | `frontend/src/features/admin/AdminLogin.tsx` | Formulario de login: email + password, guarda `data.access_token` en localStorage como `admin_token` |
| Feature | `frontend/src/features/admin/adminApi.ts` | Cliente HTTP dedicado: `BASE_URL = "/access_role"`, lee `admin_token` de localStorage, redirige a login admin en 401 |
| Feature | `frontend/src/features/admin/api.ts` | Funciones de API (fetchCompanias, blockCompania, exportCompanias, etc.) usando `adminApi` |
| Hook | `frontend/src/shared/hooks/useAdmin.ts` | React Query hooks: useCompanias, useBlockCompania, useUnblockCompania, useGrantFreeSubscription, useBackupHistorial, useTriggerBackup |
| Config | `frontend/vite.config.ts` | Proxy `/access_role` → `localhost:8000` (bypass para navegacion HTML, proxea API calls) |
| Config | `.env` | `SUPER_ADMIN_EMAIL`, `SUPER_ADMIN_PASSWORD`, `ADMIN_ROUTE_PATH`, `JWT_SECRET` |

---

## 2. Configuracion

### 2.1 Variables de entorno (.env)

```
SUPER_ADMIN_EMAIL=<email del admin>
SUPER_ADMIN_PASSWORD=<password del admin>
ADMIN_ROUTE_PATH=/access_role/admin/developer
JWT_SECRET=<hex string>
JWT_EXPIRES_IN=15m
FRONTEND_URL=http://localhost:5173
```

### 2.2 Prefijo de rutas del admin

El prefijo se lee de `ADMIN_ROUTE_PATH` (default: `/access_role/admin/developer`).
Todos los endpoints del admin viven bajo este prefijo. NO usa `/api/v1/`.

### 2.3 Dependencia `require_admin`

Definida en `backend/src/interfaces/routers/admin.py`. Se inyecta como `Depends(require_admin)` en todos los endpoints protegidos. Orden de busqueda del token:

1. Cookie `admin_access_token` (path scoped al prefijo admin)
2. Header `Authorization: Bearer <token>`

Si no encuentra token → 401. Si el payload no tiene `sub == "admin"` → 403.

### 2.4 Cookie del admin

| Cookie | Path | Max-Age | Secure | HttpOnly | SameSite |
|--------|------|---------|--------|----------|----------|
| `admin_access_token` | `/access_role/admin/developer` | 900s (15 min) | true | true | lax |

**CRITICO:** El path de la cookie es el valor de `ADMIN_ROUTE_PATH`. Solo se envia en requests a rutas bajo ese prefijo. Es independiente de la cookie `access_token` del auth de usuario (que tiene `path=/`).

### 2.5 JWT payload del admin

```json
{
  "sub": "admin",
  "company_id": "admin",
  "exp": "<now + 15 min>",
  "iat": "<now>",
  "type": "access"
}
```

No hay refresh token para admin. La sesion dura 15 minutos y luego requiere re-login.

### 2.6 Vite proxy

```typescript
"/access_role": {
  target: "http://localhost:8000",
  changeOrigin: true,
  bypass(req) {
    // Si el browser navega (Accept: text/html) → SPA routing (no proxea)
    // Si es una API call (Accept: application/json) → proxea a backend
    const accept = req.headers["accept"] || "";
    if (accept.includes("text/html")) {
      return req.url;
    }
  },
}
```

Esto permite que `fetch("/access_role/admin/developer/login")` llegue al backend, pero navegar a `/access_role/admin/developer` en el browser cargue el SPA.

### 2.7 Rutas frontend (React Router)

```
/access_role/admin/developer           → AdminLoginPage (formulario)
/access_role/admin/developer/dashboard → AdminDashboard (panel protegido)
```

---

## 3. Flujos

### 3.1 Login del administrador

```
1. El admin navega a /access_role/admin/developer
   → React Router renderiza AdminLoginPage → <AdminLogin />

2. POST /access_role/admin/developer/login
   Body: { "email": "<SUPER_ADMIN_EMAIL>", "password": "<SUPER_ADMIN_PASSWORD>" }
   
   Backend (AdminLoginUseCase):
   - Compara email/password contra env vars (no hay tabla de admins)
   - Si no coincide → 401 "Credenciales de administrador inválidas"
   - Si coincide → JWTService.create_tokens(user_id="admin", company_id="admin")
   
   Respuesta PLANA: {
     "access_token": "eyJ...",
     "token_type": "bearer",
     "expires_in": 900,
     "message": "Autenticación exitosa"
   }
   
   Headers: Set-Cookie: admin_access_token=eyJ...; Path=/access_role/admin/developer; HttpOnly; Secure; SameSite=Lax

3. Frontend (AdminLogin.tsx):
   - Guarda data.access_token en localStorage como "admin_token"
   - navigate("/access_role/admin/developer/dashboard")
```

### 3.2 Acceso al dashboard (proteccion client-side)

```
1. AdminDashboard.tsx → useEffect verifica localStorage.getItem("admin_token")
   - Si no existe → navigate("/access_role/admin/developer")
   
2. Cada API call usa adminApi.ts:
   - Lee "admin_token" de localStorage
   - Lo envia como "Authorization: Bearer <token>"
   - Si el backend responde 401 → limpia localStorage → redirige al login admin
```

### 3.3 Verificacion server-side (require_admin)

```
1. Busca cookie "admin_access_token" en el request
2. Si no hay cookie, busca header "Authorization: Bearer <token>"
3. Si no hay token → 401 "Token de administrador requerido"
4. jwt_service.decode_access_token(token):
   - Valida firma HS256 con JWT_SECRET
   - Valida expiracion
5. Verifica payload["sub"] == "admin"
   - Si no → 403 "Acceso solo para administradores"
6. Setea request.state.user_id = "admin", request.state.company_id = "admin"
```

### 3.4 Logout

```
1. Frontend: handleLogout()
   - fetch("/access_role/admin/developer/logout", { method: "POST" })
   - localStorage.removeItem("admin_token")
   - navigate("/access_role/admin/developer")

2. Backend: POST /access_role/admin/developer/logout
   - Limpia cookie admin_access_token
   - Retorna { "message": "Sesión cerrada" }
```

### 3.5 Reset de password (flujo completo)

```
1. POST /access_role/admin/developer/reset/request
   - Rate limit: max 3 por hora por IP
   - Invalida tokens activos previos
   - Genera token_raw (token_urlsafe 32), guarda hash SHA-256 en DB
   - Envia email al SUPER_ADMIN_EMAIL con link de reset (token en URL)
   - Expira en 15 minutos

2. POST /access_role/admin/developer/reset/confirm
   Body: { "token": "<token_raw>", "new_password": "<nueva>" }
   - Hashea token_raw, busca en DB
   - Si valido → actualiza os.environ["SUPER_ADMIN_PASSWORD"] en runtime
   - Marca token como usado
```

---

## 4. Invariantes criticos

### 4.1 Credenciales en variables de entorno (no en DB)

El admin NO tiene un registro en la tabla `users`. Las credenciales viven exclusivamente en `SUPER_ADMIN_EMAIL` y `SUPER_ADMIN_PASSWORD` del `.env`. La comparacion es directa (`==`), no hay hash de password.

### 4.2 Respuesta PLANA del login

El endpoint `/login` retorna un JSON plano:
```json
{"access_token": "jwt-string", "token_type": "bearer", "expires_in": 900, "message": "..."}
```

El frontend espera `data.access_token` como string JWT directo. Si se anida (ej: `data.access_token.access_token`), el frontend se rompe.

### 4.3 BASE_URL de adminApi.ts es `/access_role` (NO `/api/v1`)

```typescript
const BASE_URL = "/access_role";
```

Las funciones en `api.ts` usan paths como `/admin/developer/companias`. La URL final queda:
`/access_role/admin/developer/companias` → proxy de Vite lo envia a `localhost:8000`.

### 4.4 Token en localStorage, NO en cookie (frontend)

El frontend guarda y lee `admin_token` de `localStorage`. La cookie `admin_access_token` existe como backup server-side (dual auth), pero el frontend usa exclusivamente `Authorization: Bearer` via localStorage.

### 4.5 Independencia total del auth de usuario

| Aspecto | Auth usuario | Auth admin |
|---------|-------------|-----------|
| Prefijo | `/api/v1/auth/` | `/access_role/admin/developer/` |
| Token key (localStorage) | N/A (cookie) | `admin_token` |
| Cookie | `access_token` (path `/`) | `admin_access_token` (path `/access_role/...`) |
| JWT sub | UUID del user | `"admin"` |
| JWT company_id | UUID de la company | `"admin"` |
| Refresh token | Si (cookie httpOnly) | No |
| Middleware | `AuthMiddleware` | `require_admin` (Depends) |
| Redirect en 401 | `/login` | `/access_role/admin/developer` |

### 4.6 Vite proxy bypass

La regla de bypass en `vite.config.ts` es critica: si se elimina, navegar a `/access_role/admin/developer` en el browser haria un proxy al backend (que no sirve HTML) y la pagina no cargaria. El bypass detecta `Accept: text/html` y deja que Vite sirva el SPA.

### 4.7 Sin refresh token

El admin no tiene refresh token. `create_tokens()` genera uno, pero el router lo descarta — solo usa `token_data["access_token"]` y `token_data["expires_in"]`. La sesion expira a los 15 minutos sin posibilidad de extension silenciosa.

---

## 5. Comandos de verificacion

```bash
# 1. Login del admin (requiere .env cargado con SUPER_ADMIN_EMAIL y SUPER_ADMIN_PASSWORD)
curl -s -X POST http://localhost:8000/access_role/admin/developer/login \
  -H "Content-Type: application/json" \
  -d '{"email":"<SUPER_ADMIN_EMAIL>","password":"<SUPER_ADMIN_PASSWORD>"}'
# Esperar: {"access_token":"eyJ...","token_type":"bearer","expires_in":900,"message":"Autenticación exitosa"}

# 2. Credenciales invalidas → 401
curl -s -o /dev/null -w "HTTP %{http_code}" \
  -X POST http://localhost:8000/access_role/admin/developer/login \
  -H "Content-Type: application/json" \
  -d '{"email":"wrong@test.com","password":"wrong"}'
# Esperar: HTTP 401

# 3. Acceder a endpoint protegido con token
TOKEN=$(curl -s -X POST http://localhost:8000/access_role/admin/developer/login \
  -H "Content-Type: application/json" \
  -d '{"email":"<SUPER_ADMIN_EMAIL>","password":"<SUPER_ADMIN_PASSWORD>"}' | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

curl -s http://localhost:8000/access_role/admin/developer/companias \
  -H "Authorization: Bearer $TOKEN"
# Esperar: {"items":[...],"total":...,"page":1,"page_size":20}

# 4. Sin token → 401
curl -s -o /dev/null -w "HTTP %{http_code}" \
  http://localhost:8000/access_role/admin/developer/companias
# Esperar: HTTP 401

# 5. Token de usuario normal → 403 (sub != "admin")
# Usar un access_token de /api/v1/auth/login (sub = UUID de user)
curl -s -o /dev/null -w "HTTP %{http_code}" \
  http://localhost:8000/access_role/admin/developer/companias \
  -H "Authorization: Bearer <USER_ACCESS_TOKEN>"
# Esperar: HTTP 403

# 6. Logout
curl -s -X POST http://localhost:8000/access_role/admin/developer/logout
# Esperar: {"message":"Sesión cerrada"}

# 7. Verificar cookie en la respuesta del login (verbose)
curl -v -X POST http://localhost:8000/access_role/admin/developer/login \
  -H "Content-Type: application/json" \
  -d '{"email":"<SUPER_ADMIN_EMAIL>","password":"<SUPER_ADMIN_PASSWORD>"}' 2>&1 | grep Set-Cookie
# Esperar: Set-Cookie: admin_access_token=eyJ...; HttpOnly; Path=/access_role/admin/developer; SameSite=lax; Secure
```

---

## 6. Checklist de restauracion

Si el login de admin se rompe, revisar en este orden:

1. **`.env`** — Verificar que `SUPER_ADMIN_EMAIL`, `SUPER_ADMIN_PASSWORD` y `ADMIN_ROUTE_PATH` existen y tienen valores. Verificar `JWT_SECRET`.
2. **`admin.py` (router)** — Verificar que `ADMIN_PREFIX` se lee correctamente de env. Verificar que el endpoint `/login` aplana la respuesta (`flat_response`).
3. **`admin.py` (use case)** — Verificar que `AdminLoginUseCase.execute()` compara contra `os.getenv()` y llama a `jwt_service.create_tokens(user_id="admin", company_id="admin")`.
4. **`jwt.py`** — Verificar que `create_tokens()` acepta strings (no solo UUID) para `user_id` y `company_id` (se castea con `str()`).
5. **`cookie_service.py`** — Verificar que `set_admin_token_cookie()` usa el prefijo de env como path de la cookie.
6. **`vite.config.ts`** — Verificar que el proxy para `/access_role` existe y tiene el bypass para `text/html`. Sin esto, la SPA no carga en la ruta del admin.
7. **`AdminLogin.tsx`** — Verificar que guarda `data.access_token` (string directo) en `localStorage` como key `admin_token`. Verificar que hace fetch a `${ADMIN_BASE}/login` donde `ADMIN_BASE = "/access_role/admin/developer"`.
8. **`adminApi.ts`** — Verificar que `BASE_URL = "/access_role"` y que lee `admin_token` de localStorage. Verificar redirect a `/access_role/admin/developer` en 401.
9. **`App.tsx`** — Verificar que las rutas `/access_role/admin/developer` y `/access_role/admin/developer/dashboard` estan registradas en React Router.
10. **`AdminDashboard.tsx`** — Verificar el useEffect que chequea `admin_token` en localStorage y redirige si no existe.
