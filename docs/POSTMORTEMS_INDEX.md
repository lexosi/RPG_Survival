# 🪦 POSTMORTEMS_INDEX — Índice de postmortems

> **Registro de todas las crisis del proyecto y aprendizajes.**
>
> **Cuándo escribir un postmortem**: cualquier crisis que cueste >30 min recuperar.
>
> **Plantilla canónica** en `EMERGENCY_ROLLBACK.md` sección 11.2 y `PROMPT_TEMPLATES.md` sección 17.

---

## 🧭 Índice

1. [Filosofía de los postmortems](#1-filosofía-de-los-postmortems)
2. [Cuándo escribir uno](#2-cuándo-escribir-uno)
3. [Estructura del archivo](#3-estructura-del-archivo)
4. [Plantilla canónica](#4-plantilla-canónica)
5. [Índice de postmortems](#5-índice-de-postmortems)
6. [Patrones detectados](#6-patrones-detectados)
7. [Revisión mensual](#7-revisión-mensual)

---

## 1. Filosofía de los postmortems

### 1.1 Por qué existen

> **Un error sin postmortem se repite. Un error con postmortem se convierte en lección permanente.**

Los postmortems no son sobre **culpa**, son sobre **causa raíz** y **prevención**. Cada uno es una pieza de conocimiento que el equipo (tú + IAs) consulta antes de cometer el mismo error.

### 1.2 Principios

1. **Causa raíz, no síntoma.** "El editor crasheó" no es causa raíz. "Verse ciclo infinito en `OnBegin` por await sin timeout" sí lo es.
2. **Prevención accionable.** Si la prevención es "tener cuidado" → falló el postmortem. Debe ser un cambio concreto a workflow, doc, o hábito.
3. **Sin culpa, con responsabilidad.** "DeepSeek inventó una API" → el problema es que el workflow no protegió contra eso (cápsula insuficiente, API_REFERENCE no consultado).
4. **Postmortem rápido**. Escribirlo dentro de 24h del incidente. Si esperas, los detalles se pierden.

### 1.3 Contra qué nos protegen

| Crisis | Cómo el postmortem ayuda |
|---|---|
| Editor crash recurrente | Identifica el patrón de código que lo causa |
| Persistencia corrupta | Documenta el cambio de schema que lo provocó |
| DeepSeek en bucle | Identifica gap en cápsula o spec del sprint |
| Pérdida de trabajo | Refuerza hábito de commit frecuente |
| Bug que vuelve a aparecer | El postmortem antiguo lo identifica y previene |

---

## 2. Cuándo escribir uno

### 2.1 Triggers obligatorios

- ✅ Cualquier crisis que cueste **>30 min recuperar**.
- ✅ Cualquier **persistencia corrupta** (incluso en cuenta-test).
- ✅ Cualquier **publish bloqueado** por Epic.
- ✅ Cualquier **regresión** de feature ya publicada.
- ✅ Cualquier **sprint cancelado** después de 1+ horas de trabajo.
- ✅ Cualquier **bug que reaparece** tras "estar arreglado".
- ✅ Cualquier **decisión arquitectónica errónea** descubierta después.

### 2.2 Triggers opcionales (recomendados)

- 🟡 Sprints que pasan de 2× la estimación inicial (postmortem ligero, "lessons learned").
- 🟡 Patrones de errores repetidos (3+ veces el mismo tipo).
- 🟡 Conflictos entre docs descubiertos en práctica.

### 2.3 NO escribir postmortem para

- ❌ Bug normal que se arregla en <30 min.
- ❌ Errores de tipeo.
- ❌ Compilation errors triviales (typo de nombre).
- ❌ "DeepSeek se equivocó pero lo arreglé en un turno."

---

## 3. Estructura del archivo

### 3.1 Ubicación

```
docs/postmortems/
├── README.md (este archivo, o link a este)
├── 2026-05-15_persistence_corrupted_test_account.md
├── 2026-05-22_editor_wouldnt_open.md
├── 2026-06-03_deepseek_api_invented.md
└── ...
```

### 3.2 Convención de naming

```
YYYY-MM-DD_descripcion_corta_snake_case.md
```

Ejemplos:
- `2026-05-15_persistence_corrupted_test_account.md`
- `2026-06-12_publish_blocked_renamed_field.md`
- `2026-07-01_mobile_fps_drop_after_companions_release.md`

### 3.3 Estructura interna del archivo

Ver sección 4 para plantilla completa.

---

## 4. Plantilla canónica

```markdown
# POSTMORTEM — YYYY-MM-DD — <Título descriptivo>

## 📋 Resumen ejecutivo (TL;DR)
[1-2 frases. Qué pasó, qué causó, qué se hizo.]

## 🔥 Síntoma
[Qué se observó. Errores específicos, mensajes, comportamiento.]

## 🔍 Causa raíz
[Qué causó realmente. NO el síntoma. La causa de la causa.]

## ⏱️ Timeline
- **HH:MM** — [Evento]: [descripción]
- **HH:MM** — [Detección]: cómo se detectó el problema
- **HH:MM** — [Hipótesis 1]: [qué se intentó, resultado]
- **HH:MM** — [Resolución]: [qué funcionó]

## 🛠️ Resolución
[Cómo se solucionó. Pasos concretos. Comandos ejecutados.]

## ⏳ Tiempo perdido
[X minutos / horas]

## 💔 Impacto
- **A jugadores**: [si aplica]
- **A datos**: [si aplica, persistencia afectada]
- **A workflow**: [tiempo perdido del equipo]

## ✅ Cómo prevenirlo (accionable)
[Cambios concretos. NO "tener cuidado". Cambios reales:]
- [ ] Actualizar `WORKFLOW.md` sección X con regla nueva
- [ ] Añadir validación al `01_validate_jsons.py` para detectar patrón
- [ ] Añadir advertencia a la `DEEPSEEK_CAPSULE.md`
- [ ] Crear test_device para regresión

## 📝 Cambios necesarios a docs
- [ ] `EMERGENCY_ROLLBACK.md` sección X — añadir nuevo escenario
- [ ] `PROMPT.md` regla N — refinar
- [ ] `PERSISTENCE_MAP.md` — clarificar [...]
- [ ] (otros)

## 🧠 Lecciones aprendidas
[Insights generales. Cosas a tener en mente para el futuro.]

## 🔗 Referencias
- Sprint afectado: SPR-XXX
- Commits relevantes: `<sha1>`, `<sha2>`
- Issues GitHub (si aplica): #N
- Postmortems relacionados: [enlaces]
```

### 4.1 Plantilla rápida (para crisis pequeñas)

Si la crisis es <1h pero relevante:

```markdown
# POSTMORTEM RÁPIDO — YYYY-MM-DD — <Título>

## Síntoma
[Qué viste]

## Causa raíz
[Qué pasó realmente]

## Resolución
[Cómo se arregló]

## Tiempo perdido
[X minutos]

## Cómo prevenirlo
[Cambio concreto]

## Cambios a docs
- [ ] [si aplica]
```

---

## 5. Índice de postmortems

> **Tabla de todos los postmortems escritos. Mantener ordenada cronológicamente DESC (más reciente primero).**

| Fecha | Título | Categoría | Tiempo perdido | Sprint | Doc afectado | Archivo |
|---|---|---|---|---|---|---|
| 2026-05-07 | Verse Syntax Drift — 5 archivos no compilaban, docs autoritativos obsoletos | Build/Compile + Documentation | ~3h | SPR-211 (corrige drift de Audit 2 — C1 + Audit 3 — H3.1) | `VERSE_SYNTAX_GUIDE.md` (nuevo) + 8 docs auditados (CHANGELOG, MODULES, GLOSSARY, API_REFERENCE, BOOTSTRAP, CONCEPT, SPRINTS_BACKLOG, PROMPT) + 5 archivos Verse refactoreados + generator script | [PM-SPR-211.md](postmortems/PM-SPR-211.md) |

### 5.1 Categorías estándar

- **Persistence** — corrupción, schema breaks, datos perdidos
- **Build/Compile** — errores Verse, build pipeline roto
- **Editor/UEFN** — crashes del editor, problemas del entorno
- **Deploy/Publish** — bloqueos de Epic, push changes problemáticos
- **AI workflow** — DeepSeek bucles, malentendidos, contexto perdido
- **Performance** — fps drops, memory leaks, mobile issues
- **Logic/Game** — bugs de gameplay, balance roto en producción
- **Documentation** — conflictos entre docs, info obsoleta

### 5.2 Cómo añadir entrada

1. Crear archivo `docs/postmortems/YYYY-MM-DD_titulo.md` con plantilla sección 4.
2. Añadir fila a tabla 5 con datos del postmortem.
3. Si hay patrones detectados → añadir a sección 6.
4. Commit con mensaje: `POSTMORTEM: YYYY-MM-DD <titulo>`.

---

## 6. Patrones detectados

> **Cuando 3+ postmortems comparten causa similar → patrón sistémico → cambio profundo.**

### 6.1 Tabla de patrones

| Patrón | Postmortems implicados | Acción tomada | Estado |
|---|---|---|---|
| _vacío_ | — | — | — |

### 6.2 Plantilla de patrón

```markdown
### Patrón: <Nombre descriptivo>

**Frecuencia**: N postmortems en M meses

**Causa común**: [...]

**Postmortems implicados**:
- [enlace 1]
- [enlace 2]
- [enlace 3]

**Acción sistémica tomada**:
- [Cambio 1 a workflow/doc/proceso]
- [Cambio 2]

**Métrica de éxito**:
- [Cómo medir si la acción funciona: ej "no más postmortems de este tipo en 3 meses"]

**Estado**: [En progreso | Resuelto | Monitoreando]
```

### 6.3 Patrones esperables (anticipados)

Sin tener postmortems aún, anticipo posibles patrones futuros:

- **DeepSeek inventa APIs Verse** → mitigar con API_REFERENCE_GENERATED.md más estricta + cápsula reforzada.
- **Schema rename accidental** → mitigar con git pre-commit hook que valide PERSISTENCE_MAP.
- **Pérdida de trabajo por no commit** → mitigar con auto-commit cada hora.
- **Mobile FPS drops post-feature** → mitigar con Mobile Preview obligatorio en done criteria.

---

## 7. Revisión mensual

### 7.1 Frecuencia

**Una vez al mes** (último viernes), revisar la carpeta `docs/postmortems/` y este índice.

### 7.2 Checklist de revisión

```
[ ] Listar postmortems del mes
[ ] Identificar patrones (3+ similares = patrón)
[ ] Si hay patrón nuevo → añadir a sección 6
[ ] Verificar que las "acciones de prevención" se ejecutaron
[ ] Verificar que los cambios a docs prometidos se hicieron
[ ] Identificar si algún workflow ha de cambiar profundamente
[ ] Decidir si tags/branches/automation se ha de añadir
[ ] Actualizar este índice con notas
```

### 7.3 Métricas a trackear

| Métrica | Objetivo |
|---|---|
| **Postmortems/mes** | Tendencia decreciente con el tiempo |
| **Tiempo total perdido en crisis/mes** | Decreciente |
| **% postmortems que generan cambio a docs** | ≥80% |
| **Patrones identificados sin acción** | 0 |
| **Crisis "evitadas por postmortem previo"** | (anecdotal pero útil) |

### 7.4 Reporte de revisión mensual

```markdown
# Revisión postmortems — YYYY-MM

## Postmortems este mes: N
- [enlace 1]
- [enlace 2]

## Tiempo total perdido: X horas

## Patrones detectados:
- [Patrón nuevo si aplica]

## Acciones tomadas en respuesta:
- [Cambio 1]
- [Cambio 2]

## Acciones pendientes de meses anteriores:
- [...]

## Tendencia comparada con mes anterior: [↑/↓/=]

## Recomendaciones:
- [...]
```

---

## 📌 Resumen ejecutivo

```
🎯 ESTE DOCUMENTO ES EL REGISTRO de todas las crisis del proyecto.

🔑 CUÁNDO ESCRIBIR POSTMORTEM:
   - Cualquier crisis >30 min de recuperación
   - Persistencia corrupta (incluso cuenta-test)
   - Publish bloqueado por Epic
   - Regresión de feature ya publicada
   - Bug que reaparece tras "arreglado"

🔑 ESTRUCTURA OBLIGATORIA:
   - Síntoma (qué)
   - Causa raíz (por qué REAL)
   - Resolución (cómo)
   - Cómo prevenirlo (accionable, NO "tener cuidado")
   - Cambios a docs

🔑 REVISIÓN MENSUAL OBLIGATORIA:
   - 3+ postmortems similares = patrón = cambio sistémico
   - Verificar que prevenciones prometidas se ejecutaron

⚠️ POSTMORTEM SIN ACCIÓN ACCIONABLE = POSTMORTEM INÚTIL.
```

---

**Fin del documento.**

> Este documento se actualiza cada vez que se escribe un postmortem nuevo o se hace revisión mensual.
