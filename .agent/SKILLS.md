# SKILLS.md — Instrucciones operativas para agentes

> Este documento es para CUALQUIER agente de IA (Claude u otro) que vaya a trabajar en este
> código. Léelo completo antes de tocar una sola línea. `SPECS.md` te dice **qué** es el
> sistema; este documento te dice **cómo** trabajar en él.

---

## 1. Rol que debés asumir

Sos un **ingeniero de software senior**, con conocimiento profundo y amplio de desarrollo
fullstack, DevOps y análisis de datos. Este es un proyecto de software **profesional**, no un
proyecto de curso ni un prototipo descartable — se va a vender a clientes reales. Tratalo con
ese nivel de rigor: pensá en mantenibilidad, en el próximo desarrollador (humano o agente) que
va a leer tu código, y en que cada decisión quede justificada y documentada.

El conocimiento de análisis de datos importa especialmente porque a futuro el proyecto va a
usar las tablas de cada tenant con pandas/numpy para mejorar el RAG y para features de
analítica — diseñá el modelo de datos pensando también en que sea consultable/exportable
limpiamente, no solo en que funcione para la UI de hoy.

---

## 2. Orden de lectura obligatorio antes de empezar

1. `SPECS.md` completo.
2. Los ADRs en `docs/decisions/` relevantes a lo que vayas a tocar (filtrá por tema, no hace
   falta leer los 40 si vas a tocar solo el módulo de caja, pero sí leé los que mencionen esa
   área).
3. El código existente del módulo que vayas a modificar — nunca asumas cómo está hecho algo,
   leelo.
4. Si tu tarea está en `docs/tasks/backlog.json`, leé también sus `dependencias` y
   `decisiones_relacionadas` antes de arrancar.

---

## 3. Convenciones de código

- **Backend:** Clean Architecture por capas (`domain/`, `application/`, `infrastructure/`,
  `interfaces/`). El `domain/` nunca importa de `infrastructure/` ni de `interfaces/`. Si estás
  por hacer ese import, parate — significa que la lógica está en la capa equivocada.
- **Frontend:** Feature-Sliced Design. Las dependencias van siempre hacia adentro:
  `shared → entities → features → widgets → pages → app`. Nunca al revés.
- **Naming:** español para conceptos de dominio que el desarrollador usa en su día a día
  (cliente, mascota, consulta, insumo, caja), inglés para términos puramente técnicos
  (repository, service, handler). Si dudás, mirá cómo está nombrado algo similar en el código
  ya existente y seguí ese patrón, no inventes uno nuevo.
- **IDs:** UUIDv7 siempre, expuestos directos en API/URLs. Nunca secuenciales, nunca hasheados.

---

## 4. Cómo actualizar `docs/`

Nunca edites a mano los archivos JSON de `docs/decisions/`, `docs/tasks/backlog.json` o
`docs/errors/errors.log.json`. Usá los scripts:

```bash
scripts/decision.sh nueva "Título de la decisión"   # crea un ADR-XXX.json con el formato correcto
scripts/task.sh nueva "Título de la tarea"             # agrega una entrada a backlog.json
scripts/task.sh cerrar TASK-XXX                          # marca una tarea como completada
                                                            # (falla si no tiene tests_relacionados)
scripts/error.sh nuevo "módulo" "descripción del error"     # agrega entrada a errors.log.json
```

Si tomaste una decisión técnica relevante (elegir una librería, cambiar un patrón, resolver un
trade-off), **registrala como ADR antes de seguir codeando**, no después. La trazabilidad solo
sirve si es contemporánea a la decisión, no reconstruida de memoria al final.

---

## 5. Cómo correr el entorno local

```bash
scripts/dev-up.sh          # levanta todo el stack (docker compose)
scripts/dev-reset-db.sh     # si necesitás una base limpia
scripts/seed-test-data.sh    # carga datos de prueba (incluye la plantilla de insumos/precios)
scripts/start-tunnel.sh       # solo si vas a probar algo que dependa de webhooks de Mercado Pago
scripts/start-all.sh           # backend + tunnel + frontend juntos
```

No asumas que el entorno ya está levantado. Si vas a correr o probar algo, levantalo vos mismo
con estos scripts.

---

## 6. Reglas no negociables

1. **El `.env` real del desarrollador nunca se modifica ni se elimina.** Si necesitás una
   variable nueva, la *agregás* (nunca reemplazás una existente) y se lo informás
   explícitamente al desarrollador en tu respuesta — no asumas que está bien, avisá. Cualquier
   variable que solo necesite el entorno de testing va en `.env.test.local`, nunca en el `.env`
   real.
2. **Soft-delete siempre.** Nunca un `DELETE` físico sobre datos de negocio. Siempre
   `deleted_at` / flag equivalente.
3. **RLS siempre.** Ninguna tabla tenant-scoped se crea sin su política de RLS correspondiente,
   sin excepción, aunque "total confianza en que el código siempre filtra por `company_id`".
4. **UUIDv7 siempre**, nunca IDs secuenciales expuestos, nunca hashids.
5. **`core_db` y `community_db` nunca se tocan en la misma transacción ni con joins directos.**
   Si una feature necesita datos de ambas, se resuelve a nivel de aplicación (dos queries,
   combinadas en el caso de uso), nunca con un link de base de datos entre ellas.
6. **No agregues infraestructura nueva (otra base, otra cola, otro broker, otra herramienta)
   sin antes registrar un ADR que lo justifique.** "Podría ser útil" no es justificación
   suficiente — necesita un problema concreto que las herramientas actuales no resuelven.
7. **No reproduzcas el error de n8n.** Antes de traer una herramienta de orquestación/workflow
   externa para algo que el backend puede resolver con lo que ya existe (RabbitMQ + Mailjet +
   crons), resolvelo con lo que ya existe.
8. **Un documento (factura, prescripción) se genera una sola vez.** Antes de generar uno nuevo,
   verificá si ya existe una versión vigente (`es_version_actual = true`) en
   `documentos_generados` y si `requiere_regeneracion` es `false` — en ese caso, solo se sirve
   el existente desde Cloudinary, no se regenera.

---

## 7. Checklist antes de marcar una tarea como completada

- [ ] ¿Tiene tests (unit y, si corresponde, integración)? ¿Están listados en
      `tests_relacionados`?
- [ ] ¿Respeta RLS si tocó una tabla tenant-scoped?
- [ ] ¿Usa soft-delete si implica borrado?
- [ ] ¿Tocaste el `.env`? Si agregaste una variable nueva, ¿la documentaste y avisaste?
- [ ] ¿Tomaste alguna decisión técnica no trivial? ¿Quedó como ADR?
- [ ] ¿El código sigue la capa/carpeta correcta según la arquitectura (Clean Architecture /
      FSD)?
- [ ] ¿Actualizaste `SPECS.md` si tu cambio modifica algo que el documento describe?

## 8. Gestión de tokens y límite de sesión
 
### Tokens
- Antes de arrancar una tarea, leer **solo** los archivos relevantes a esa tarea.
  No leer todo el código base en cada sesión — es el mayor consumo innecesario de tokens.
- Usar `docs/tasks/backlog.json` como memoria persistente entre sesiones. Cada tarea debe
  tener su estado actualizado antes de cerrar la sesión.
- Al terminar cualquier bloque de trabajo, escribir en el JSON de la tarea exactamente dónde
  se paró, qué falta, y qué decisiones quedaron pendientes. La próxima sesión arranca leyendo
  eso, no releyendo todo desde cero.
### Límite de sesión
- A las **4 horas** de sesión activa, detener el trabajo nuevo.
- Antes de cerrar: actualizar el estado de todas las tareas tocadas, registrar errores
  abiertos en `errors.log.json`, y dejar un comentario en la tarea indicando el punto exacto
  de continuación.
- No intentar terminar apresuradamente antes del límite — es mejor parar limpio que dejar
  código a medias sin documentar.
- La próxima sesión arranca con: leer `backlog.json` → identificar tarea en curso → leer
  solo los archivos de esa tarea → continuar.