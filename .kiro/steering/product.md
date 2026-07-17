---
inclusion: always
---

# Producto — Veterinaria V2

Plataforma SaaS multitenant de gestión y administración veterinaria, fullstack, con un agente
de IA (RAG) integrado que conoce todos los datos cargados por cada tenant y actúa como su
fuente de verdad conversacional. Es un producto profesional pensado para venderse por
suscripción a veterinarias reales en Argentina — no un MVP descartable ni un proyecto de curso.

Fuente completa y autoritativa: `docs/decisions/` (ADRs) y el histórico de decisiones del
proyecto. Este archivo es un resumen orientador; ante cualquier duda de detalle, leer el ADR
correspondiente en vez de asumir a partir de este resumen.

## Los tres subsistemas

1. **Sistema de Usuario** (veterinario/veterinaria): gestión completa — clientes, mascotas,
   historial clínico, caja, tienda, precios, configuración, chat con IA.
2. **Sistema de Cliente** (dueño de la mascota): portal de solo lectura vía código único, para
   ver/descargar facturación y prescripciones de sus mascotas.
3. **Sistema de Administrador** (operador de la plataforma): oculto, no enlazado públicamente.
   Gestiona usuarios, suscripciones, bloqueos y backups.

Solo los dos primeros se comunican en el landing. El tercero nunca se menciona públicamente.

## Principios no negociables

- Mobile-first, responsive en toda la app.
- Soft-delete siempre — nada se borra físicamente, todo vía `deleted_at`.
- UUIDv7 como identificador público de toda entidad, expuesto tal cual (sin hash).
- Un documento (factura, prescripción) se genera una sola vez y se cachea; solo se regenera si
  cambiaron los datos que lo originaron.
- El `.env` real del desarrollador es intocable: nunca se modifica ni se elimina una variable
  existente. Variables nuevas se agregan y se avisa explícitamente. Variables de testing van
  solo en `.env.test.local`.
- Sin venta de datos a terceros con fines publicitarios. Una eventual monetización de datos
  agregados/anonimizados para ML es ítem de Fase 2 sujeto a revisión legal (Ley 25.326).
- Diseño visual a medida, coherente entre los tres subsistemas — nunca genérico.

## Planes y monetización

| Plan | Precio (ARS) | Incluye |
|---|---|---|
| Mensual | $35.000/mes | Uso ilimitado del sistema, 1 backup semanal, 200 requests/mes al chat IA |
| Semestral | $180.000 | Todo lo anterior + 500 requests/mes, acceso prioritario |
| Anual | $420.000 (12 meses + 3 de regalo) | Requests ilimitados al agente, atención prioritaria, facturación electrónica AFIP incluida |

Cobro vía Mercado Pago Preapproval (recurrente automático).

## Roadmap

- **v1 (MVP):** todo lo descrito en `docs/decisions/` y el modelo de dominio actual.
- **Fase 2:** mensajes directos en Comunidad, múltiples usuarios/empleados por compañía (rol
  `staff` funcional), multi-moneda, monetización de datos para ML (requiere revisión legal
  previa), trazabilidad de lote/paquete abierto en stock.

## Preguntas abiertas (no asumir una respuesta, preguntar al desarrollador)

- TOTP opcional para el admin: propuesto, no confirmado.
- Campo `marcado_como_incobrable`: mencionado, no decidido.
