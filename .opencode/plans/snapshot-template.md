# Template: Snapshot de un subsistema

> Usar este template cuando el usuario pida "una foto" / "snapshot" / "documentar el estado"
> de un subsistema. El output va a `docs/snapshots/<nombre>.md`, NO a `plans/`.

## Estructura obligatoria

```markdown
# Snapshot: [Nombre del subsistema]

> **Fecha:** YYYY-MM-DD
> **Commit:** <hash del commit actual>
> **Estado:** funcional / parcial / degradado

[Descripción breve de qué hace este subsistema y por qué importa]

---

## 1. Archivos del sistema

| Capa | Archivo | Responsabilidad |
|------|---------|-----------------|
| Router | `backend/src/interfaces/routers/X.py` | Endpoints |
| Service | `backend/src/infrastructure/services/X.py` | Lógica de negocio |
| ... | ... | ... |

## 2. Configuración

### Variables de entorno (.env)
```
VARIABLE=value
```

### Configuración específica
Redis, middleware, puertos, etc.

## 3. Flujos

### 3.1 Nombre del flujo
```
1. VERBO /path
   Body: { ... }
   Respuesta: 200 { ... }
```

## 4. Invariantes críticos

### 4.1 Nombre del invariante
```python
# CORRECTO
código correcto

# INCORRECTO
código incorrecto
```

Explicación de por qué.

## 5. Comandos de verificación

```bash
curl -s -X POST http://localhost:8000/api/v1/... \
  -H "Content-Type: application/json" \
  -d '{...}'
```

## 6. Checklist de restauración

Si [subsistema] se rompe, revisar en este orden:
1. [Archivo primario] — [Qué verificar]
2. [Siguiente] — [Qué verificar]
```

## Ejemplo completo

Ver `docs/snapshots/auth-system.md` — snapshot real del sistema de autenticación.

## Reglas

- Los snapshots son **inmutables** una vez creados.
- Si el subsistema cambia, crear un NUEVO snapshot, no editar el viejo.
- Renombrar el viejo con sufijo `-v1`, `-v2`, etc.
- Incluir el hash del commit actual en el header.
- Incluir SOLO lo necesario para restaurar — no documentar todo el código, solo lo crítico.
