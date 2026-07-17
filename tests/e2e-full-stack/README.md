# E2E Full-Stack Tests

Tests end-to-end que cubren los flows principales de Veter usando Playwright + el stack completo (frontend + backend + base de datos + Redis).

## Requisitos

- Node.js >= 18
- Docker y docker-compose (para levantar infraestructura)
- Backend corriendo en `http://localhost:8000`
- Frontend corriendo en `http://localhost:5173`
- Redis en `localhost:6379`
- PostgreSQL (core_db) en `localhost:5444`

## Instalación

```bash
cd tests/e2e-full-stack
npm install
npx playwright install chromium
```

## Variables de entorno

| Variable               | Default                    | Descripción                            |
|------------------------|----------------------------|----------------------------------------|
| `PLAYWRIGHT_BASE_URL`  | `http://localhost:5173`    | URL del frontend                       |
| `PLAYWRIGHT_API_URL`   | `http://localhost:8000`    | URL de la API del backend              |
| `PLAYWRIGHT_REDIS_HOST`| `localhost`                | Host de Redis                          |
| `PLAYWRIGHT_REDIS_PORT`| `6379`                     | Puerto de Redis                        |

## Ejecución

### Modo interactivo (con UI de Playwright)

```bash
npx playwright test --ui
```

### Headless (CI)

```bash
npx playwright test
```

### Un solo archivo

```bash
npx playwright test test-registro-onboarding.spec.ts
```

### Con servidores automáticos

Playwright puede levantar el frontend y backend automáticamente si los
`webServer` del config están configurados. Para esto, los directorios
`../backend` y `../frontend` deben tener las dependencias instaladas.

## Tests incluidos

| Archivo                              | Descripción                                                              |
|--------------------------------------|--------------------------------------------------------------------------|
| `test-registro-onboarding.spec.ts`   | Registro, activación, login, onboarding wizard y dashboard home          |
| `test-consulta-factura.spec.ts`      | Creación de cliente, mascota, consulta con procedimientos y factura PDF  |
| `test-tienda-pago.spec.ts`           | Creación de venta en tienda y verificación del movimiento de caja        |
| `test-aislamiento-tenant.spec.ts`    | Verifica que Tenant B no pueda acceder a datos de Tenant A               |
| `test-chat-ia.spec.ts`               | Acceso al chat, envío de mensaje y verificación de respuesta/UI          |

## Notas

- Los tests de registro leen el código de activación directamente de Redis
  (db=2, clave `activation:{email}`).
- Los tests que necesitan datos previos los crean vía API en el `beforeEach`
  o setup.
- Los tests están diseñados para ejecutarse en paralelo usando emails
  únicos por test (`Date.now()` + random).
