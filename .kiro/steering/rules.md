---
inclusion: always
---

# Reglas no negociables

1. **El `.env` real nunca se modifica ni se elimina.** Variables nuevas se agregan (nunca
   reemplazan una existente) y se avisa explícitamente en la respuesta. Variables solo para
   testing van en `.env.test.local`, nunca en el `.env` real.
2. **Soft-delete siempre.** Nunca un `DELETE` físico sobre datos de negocio — siempre
   `deleted_at` o flag equivalente.
3. **RLS siempre.** Ninguna tabla tenant-scoped se crea sin su política de RLS de Postgres
   correspondiente, sin excepción.
4. **UUIDv7 siempre**, nunca IDs secuenciales expuestos, nunca hashids.
5. **`core_db` y `community_db` nunca se tocan en la misma transacción ni con joins directos.**
   Si una feature necesita datos de ambas, se resuelve a nivel de aplicación (dos queries
   combinadas en el caso de uso).
6. **No agregar infraestructura nueva** (otra base, otra cola, otro broker, otra herramienta)
   **sin un ADR que lo justifique.** "Podría ser útil" no alcanza — necesita un problema
   concreto que lo existente no resuelve.
7. **No repetir el error de n8n** (ver ADR-007): antes de traer una herramienta de
   orquestación externa, resolver con lo que ya existe (RabbitMQ + Mailjet + crons).
8. **Un documento (factura, prescripción) se genera una sola vez.** Verificar si ya existe una
   versión vigente (`es_version_actual = true`) en `documentos_generados` y si
   `requiere_regeneracion` es `false` antes de regenerar.
9. **No romper flujos existentes.** Si arreglar algo implica cambiar código que ya funciona,
   se debe pedir autorización expresa del usuario antes de hacer el cambio. Primero se informa
   qué flujos existentes se verán afectados y cómo, y solo se procede tras aprobación explícita.
   Nunca asumir que un cambio es "seguro" sin comunicarlo.

## Checklist antes de marcar una tarea como completada

- [ ] ¿Tiene tests (unit y, si corresponde, integración)? ¿Listados en `tests_relacionados`?
- [ ] ¿Respeta RLS si tocó una tabla tenant-scoped?
- [ ] ¿Usa soft-delete si implica borrado?
- [ ] ¿Tocó el `.env`? Si agregó una variable, ¿la documentó y avisó?
- [ ] ¿Tomó alguna decisión técnica no trivial? ¿Quedó como ADR?
- [ ] ¿El código sigue la capa/carpeta correcta (Clean Architecture / FSD)?
- [ ] ¿Actualizó los steering/docs si el cambio modifica algo que describen?
- [ ] ¿El cambio toca código que ya funciona? Si sí, ¿informó los flujos afectados y obtuvo autorización?

## Orden de lectura antes de tocar código

1. Steering `product.md` / `tech.md` / `structure.md` (siempre cargados).
2. Los ADR en `docs/decisions/` relevantes al área que se va a tocar — no hace falta leer
   todos, sí los que mencionen esa área (ver `architecture-decisions.md` como índice rápido).
3. El código existente del módulo a modificar — nunca asumir cómo está hecho algo.
4. Si la tarea viene de `docs/tasks/backlog.json`, leer también sus `dependencias` y
   `decisiones_relacionadas` antes de arrancar.

## Gestión de sesión

- Leer solo los archivos relevantes a la tarea en curso — no releer todo el código base en
  cada sesión.
- Al cerrar cualquier bloque de trabajo: dejar registrado dónde se paró, qué falta, y qué
  decisiones quedaron pendientes (en la spec/task correspondiente).
- A las ~4 horas de sesión activa, cerrar limpio en vez de forzar un cierre apresurado sin
  documentar.

## Snapshots del sistema

Cuando el desarrollador pida un snapshot de un subsistema ("sacá una foto", "hacé un
snapshot", "documentá el estado de [X]"), crear `docs/snapshots/<nombre>.md` con estas 6
secciones:

1. **Archivos del sistema** — Tabla: Capa | Archivo | Responsabilidad
2. **Configuración** — Env vars, middleware, Redis, DB
3. **Flujos** — Paso a paso con requests/curl de ejemplo
4. **Invariantes críticos** — Reglas que nunca deben romperse
5. **Comandos de verificación** — Curl commands para testear
6. **Checklist de restauración** — Orden de revisión si se rompe

Usar `docs/snapshots/auth-system.md` como referencia del formato.

**Regla:** Los snapshots son inmutables. Si el subsistema cambia, crear un NUEVO snapshot
(no editar el existente). Renombrar el viejo con sufijo `-v1`, `-v2`, etc.

## Limpieza de ramas después de un merge

Después de que un PR se mergea a `main`, borrar la rama tanto local como en remote:

```bash
git branch -d <nombre-rama>
git push origin --delete <nombre-rama>
```

No esperar a que el usuario pida borrarlas — las ramas merged son basura. Su código ya
está en main. Dejarlas genera confusión.

Excepción: si el usuario pide conservar una rama explícitamente, no borrarla.
