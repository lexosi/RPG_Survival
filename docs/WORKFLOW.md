# 🔄 WORKFLOW — Sistema de trabajo diario

> **Cómo se ejecuta este proyecto cada día.**
> Director (Opus) → Filtro (Tú) → Ejecutor (DeepSeek V4-Pro)
> **Pegar/leer este doc al inicio de cada sesión.**

---

## 🧭 Índice

1. [Roles y responsabilidades](#1-roles-y-responsabilidades)
2. [Setup inicial (una sola vez)](#2-setup-inicial-una-sola-vez)
3. [Flujo diario detallado](#3-flujo-diario-detallado)
4. [Cuándo usar cada modelo](#4-cuándo-usar-cada-modelo)
5. [Daily Log (sistema)](#5-daily-log-sistema)
6. [Budget tracking de tokens](#6-budget-tracking-de-tokens)
7. [Reglas de comunicación entre modelos](#7-reglas-de-comunicación-entre-modelos)
8. [Cuándo escalar de DeepSeek a Opus](#8-cuándo-escalar-de-deepseek-a-opus)
9. [Bugs conocidos y trampas de DeepSeek V4-Pro](#9-bugs-conocidos-y-trampas-de-deepseek-v4-pro)

---

## 1. Roles y responsabilidades

### 🎩 OPUS (Claude Opus 4.7) — Director / Arquitecto

**Cuándo se usa**: 1-2 veces al día, sesiones de 30-60 min.

**Responsabilidades**:
- Diseñar arquitectura
- Planificar sprints del día (briefing matinal)
- Resolver dudas técnicas complejas
- Revisar decisiones controvertidas
- Actualizar CONCEPT.md y docs maestros
- Diagnosticar bugs profundos
- Validar schemas de persistencia
- Coordinar entre múltiples sistemas

**No hace** (delega a DeepSeek):
- Escribir código rutinario
- Corregir errores de sintaxis
- Generar boilerplate
- Implementar JSONs largos
- Refactors mecánicos

### 🧑 TÚ — Puente / Filtro / Tester

**Cuándo se usa**: todo el día.

**Responsabilidades**:
- Mover archivos entre Opus, DeepSeek, VS Code, UEFN
- Ejecutar `Build Verse Code` y `Push Changes` en UEFN
- Testear in-session
- Reportar fallos a Opus (si es complejo) o DeepSeek (si es simple)
- Decidir cuándo escalar
- Mantener Daily Log
- Aprobar/rechazar Done Criteria reportadas

**No haces**:
- Programar tú mismo (a menos que quieras)
- Corregir errores triviales (eso lo hace DeepSeek)
- Diseñar arquitectura (eso lo hace Opus)

### ⚡ DEEPSEEK V4-PRO — Ejecutor

**Cuándo se usa**: la mayor parte del día.

**Responsabilidades**:
- Escribir código Verse según especificación de Opus
- Escribir scripts Python según especificación
- Crear/editar JSONs con contenido
- Corregir errores de sintaxis
- Implementar sprints SPR-xxx pre-diseñados
- Escribir test_devices temporales (ver TESTING_PROTOCOL.md)
- Reportar Done Criteria al terminar
- Hacer refactors mecánicos especificados

**No hace**:
- Decidir arquitectura
- Cambiar schema de persistencia sin Opus
- Tocar Verse para cosas que deberían ser Python
- Inventar APIs que no estén en API_REFERENCE_GENERATED.md
- Tomar decisiones de diseño no explícitas

---

## 2. Setup inicial (una sola vez)

### 2.1 Configurar acceso a DeepSeek V4-Pro

#### Opción A: Vía Claude Code (recomendado)

DeepSeek V4-Pro es **compatible con Claude Code** (mismo endpoint Anthropic).

```bash
export ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic
export ANTHROPIC_AUTH_TOKEN=tu_deepseek_api_key

# Modelos disponibles:
# - deepseek-v4-pro
# - deepseek-v4-flash (más barato, casi igual de bueno)

claude --model deepseek-v4-pro
```

#### Opción B: API directa (chat web/scripts propios)

- Endpoint: `https://api.deepseek.com/v1/chat/completions`
- Compatible con OpenAI ChatCompletions API
- Modelos: `deepseek-v4-pro`, `deepseek-v4-flash`
- Modos: Non-Thinking / Thinking / Thinking-Max
- **1M tokens de contexto** (cabe CONCEPT.md + auxiliares + sprint sin problema)

### 2.2 Configurar el proyecto en Opus

En claude.ai, crear proyecto "Survival Tycoon UEFN" con:
- **Instructions** (system prompt): pegar `PROMPT.md` completo
- **Knowledge files** (subir todos):
  - `CONCEPT.md`
  - `PERSISTENCE_MAP.md`
  - `API_REFERENCE_GENERATED.md`
  - `UI_UX_STYLE_GUIDE.md`
  - `TESTING_PROTOCOL.md`
  - `BOOTSTRAP_PIPELINE.md`
  - `WORKFLOW.md` (este)

### 2.3 Configurar el proyecto en DeepSeek

Crear "Custom Instructions" o equivalent con:
- Pegar `DEEPSEEK_CAPSULE.md` (la cápsula corta de 5 líneas)
- Si la plataforma soporta archivos: subir `CONCEPT.md`, `API_REFERENCE_GENERATED.md`, `PERSISTENCE_MAP.md` al menos

---

## 3. Flujo diario detallado

### 3.1 Visión general (1 día tipo)

```
   ┌────────────────────────────────────────────────────────┐
   │  FASE 1: BRIEFING MATINAL (15-30 min con OPUS)         │
   │  • Tú: pegas Daily Log de ayer                          │
   │  • Tú: pegas estado actual de archivos clave           │
   │  • Opus: analiza dependencias                           │
   │  • Opus: diseña 5-7 sprints SPR-xxx para hoy           │
   │  • Opus: define contexto necesario para cada sprint     │
   │  • Tú: confirmas plan o ajustas                         │
   └────────────────────┬───────────────────────────────────┘
                        │
                        ▼
   ┌────────────────────────────────────────────────────────┐
   │  FASE 2: EJECUCIÓN EN CADENA (con DEEPSEEK)             │
   │  REPETIR POR CADA SPR-xxx:                              │
   │  • Tú: abres chat nuevo en DeepSeek                     │
   │  • Tú: pegas DEEPSEEK_CAPSULE                           │
   │  • Tú: pegas la spec del SPR-xxx (copiada de Opus)      │
   │  • Tú: pegas archivos de "Contexto necesario"           │
   │  • DeepSeek: implementa                                 │
   │  • Tú: copias resultado a VS Code/UEFN                 │
   │  • Tú: Build Verse Code, Push Changes, test            │
   │  • Tú: marcas Done Criteria como ✅ o ❌                │
   │  • Si falla: reportas y DeepSeek corrige                │
   │  • Si bloqueo grave: escalas a Opus                     │
   └────────────────────┬───────────────────────────────────┘
                        │
                        ▼
   ┌────────────────────────────────────────────────────────┐
   │  FASE 3: TESTING & VALIDACIÓN (cuando aplique)          │
   │  • Test_device temporal (ver TESTING_PROTOCOL.md)       │
   │  • Mobile Preview                                       │
   │  • Verificar persistencia (logout + login)              │
   └────────────────────┬───────────────────────────────────┘
                        │
                        ▼
   ┌────────────────────────────────────────────────────────┐
   │  FASE 4: CIERRE DE CADA SPRINT (no fin de día)          │
   │  • DeepSeek/aider: hace commit final del sprint         │
   │  • Tú: `git tag SPR-XXX <sha>` (el humano taggea)        │
   │  • Tú: `python scripts/tools/close_sprint.py SPR-XXX`   │
   │       → genera/actualiza docs/dailylog/DL_<hoy>_*.md     │
   │  • Tú: completas el bloque MANUAL del DL en VS Code     │
   │       (energía, bloqueos, decisiones, notas mañana)      │
   │  • Tú: marcas SPR-XXX como 🟢 done en SPRINTS_BACKLOG    │
   │  • Tú: commit Git docs/dailylog/* + cambios al backlog   │
   │  • Si quedaron sprints sin cerrar: notar en MANUAL       │
   └────────────────────────────────────────────────────────┘
```

> **Nota sobre Fase 3 — testing**: los 3 checkpoints (test_device temporal, Mobile Preview, verificar persistencia) son **regla obligatoria del proyecto**, no requisito Epic. Mobile Preview es una **feature opcional documentada por Epic** ([dev.epicgames.com — Mobile Preview](https://dev.epicgames.com/documentation/en-us/fortnite/mobile-preview-session-in-unreal-editor-for-fortnite)) que el proyecto convierte en checkpoint obligatorio antes de Push Changes para captar regresiones de UI/perf en mobile pre-publish. Detalle del protocolo y razones en `TESTING_PROTOCOL.md` §8.

> **Cierre por sprint, no por día**: el daily log se crea/actualiza cada vez que se taggea un SPR. Si cierras 3 SPR el mismo día, el script renombra el archivo único del día sumando segmentos (ej. `SPR-001` → `SPR-001+002` → `SPR-001+002+003`). Idempotente: reejecutar para un SPR ya registrado solo refresca los bloques AUTO. **Detalle del flujo, naming y plantilla**: `DAILY_LOG.md`.

### 3.2 Briefing matinal con Opus — Plantilla del prompt

```
Buenos días Opus. Briefing matinal del día [FECHA].

📋 ESTADO ACTUAL DEL PROYECTO:
- Última fase activa: [F0/F1/F2/...]
- Último sprint completado: SPR-xxx
- Sprints pendientes de fase actual: [lista]

📒 DAILY LOG DE AYER:
[pega aquí el log de ayer]

🎯 OBJETIVO DE HOY (opcional):
[lo que quieras conseguir hoy, ej: "terminar SYS-001 y SYS-002"]

⏰ TIEMPO DISPONIBLE:
[ej: "tengo 4 horas con interrupciones"]

🤔 BLOQUEOS QUE TENGO:
[si hay alguno]

📤 ARCHIVOS RELEVANTES ACTUALES:
[adjunta los .verse, .py, .json más recientemente modificados]

Tarea: dame el plan de hoy con 5-7 sprints SPR-xxx detallados.
Para cada uno:
- Spec completa siguiendo plantilla CONCEPT.md sección 13.2
- Archivos exactos que DeepSeek necesita ver
- Done Criteria explícitas
- Tiempo estimado
- Cuándo se considera "demasiado complejo para DeepSeek" y debe escalar a ti
```

### 3.3 Pasaje del sprint a DeepSeek — Plantilla

```
[PEGAR DEEPSEEK_CAPSULE AQUÍ - 5 líneas]

📦 SPRINT SPR-XXX: [Título]

## Especificación
[Pegar tal cual lo que dijo Opus]

## Done Criteria
- [ ] Criterio 1
- [ ] Criterio 2
- [ ] Compila sin warnings
- [ ] Test in-session pasa (con test_device)

## Archivos de contexto
[Pegar tal cual los archivos que Opus dijo]

## Tu tarea
1. Implementa el sprint completo.
2. Reporta los archivos creados/modificados con paths absolutos.
3. Marca cada Done Criteria como ✅ o ❌ con justificación.
4. Si encuentras algo que requiere decisión arquitectónica, STOP y pregunta. No improvises.
5. Si necesitas APIs no documentadas en API_REFERENCE_GENERATED.md, STOP y reporta.
```

### 3.4 Cuándo NO usar DeepSeek y volver a Opus

DeepSeek está fenomenal para ejecutar, pero **deja claro estos límites**:

| Situación | Quién la maneja |
|---|---|
| "Necesito decidir entre dos arquitecturas" | Opus |
| "Este sistema toca 4 weak_maps a la vez" | Opus revisa, DeepSeek ejecuta |
| "Voy a cambiar un schema de persistencia" | Opus diseña + valida, DeepSeek ejecuta |
| "Hay un bug que no sé reproducir" | Opus diagnostica |
| "Necesito modificar CONCEPT.md o PROMPT.md" | Opus |
| "Hay que diseñar la UI de un sistema nuevo" | Opus + UI_UX_STYLE_GUIDE |
| "Implementar SPR-xxx ya especificado" | DeepSeek |
| "Cambiar valores de un JSON" | DeepSeek |
| "Corregir error de sintaxis" | DeepSeek |
| "Crear test_device para SYS-xxx" | DeepSeek |
| "SPR con 3+ escaladas previsibles, hot-fix crítico, o sprint pequeño con muchas restricciones cruzadas" | Opus implementa directo |

#### 3.4-bis Criterios para que Opus implemente directo (saltarse DeepSeek)

Opus se queda con el sprint cuando **el coste de iteración Opus↔DeepSeek↔tú supera el ahorro de tokens**. Triggers concretos:

1. **3+ escaladas previsibles**: Opus ve en briefing que el SPR va a chocar varias veces (persistencia + UI nueva + API no documentada).
2. **Hot-fix crítico**: build roto en producción, ventana de tiempo <30 min, no hay margen para round-trip humano.
3. **Sprint pequeño hiper-restringido**: <50 líneas pero con 5+ restricciones cruzadas que DeepSeek tiende a ignorar (`WORKFLOW §9.2`).
4. **SPR mixto persistencia + lógica nueva**: el coste de validar a posteriori lo que escribió DeepSeek > coste de escribirlo Opus directamente.
5. **Sprint de meta-tooling**: scripts que tocan los propios docs autoritativos (CONCEPT.md, PERSISTENCE_MAP.md, schemas).

Cuando Opus marca un SPR como "lo hago yo":

- Se etiqueta en briefing como `[OPUS-EXEC]`
- Se reporta en Daily Log con tokens reales
- Si supera $0.50 en una sesión → revisar si el sprint estaba mal dimensionado

### 3.5 Verificadores throwaway

Cuando un sprint requiere validar algo con un script Python ad-hoc (ej: validar 4 JSONs recién creados, comprobar un encoding, etc.):

1. **NUNCA `python -c "..."`**. PowerShell rompe escapado.
2. **Crear script en `scripts/tools/_throwaway/_verify_<spr>.py`**. La carpeta está en `.gitignore` (excepto `.gitkeep`).
3. **Plantilla cabecera estándar**:

   ```python
   """Throwaway verifier para SPR-XXX. Safe to delete after use. NOT committed."""
   import sys
   sys.stdout.reconfigure(encoding="utf-8")  # PS encoding defense
   # tu código aquí
   ```

4. **Ejecutar**: `python scripts/tools/_throwaway/_verify_<spr>.py`
5. **Confirmar visualmente `Running ...` + output literal en consola** antes de creer cualquier resultado. NO confiar en "✅ todo OK" de Aider/DeepSeek sin ver ejecución real.
6. **NO commitear**. La carpeta está gitignored. Si Aider intenta commitear el verifier, abortar y usar `--no-auto-commits`.

**Lección operacional 2026-05-06**: Aider/DeepSeek alucinan outputs sin ejecutar. Regla: solo creer lo que veas en consola con tus ojos.

---

---

## 4. Cuándo usar cada modelo

### 4.1 Tabla de decisión rápida

| Tipo de tarea | Modelo | Coste relativo |
|---|---|---|
| Diseñar arquitectura nueva | Opus 4.7 | 💰💰💰💰 |
| Briefing matinal | Opus 4.7 | 💰💰💰 |
| Implementar SPR-xxx ya especificado | DeepSeek V4-Pro | 💰 |
| Corregir error de sintaxis | DeepSeek V4-Flash | 💰 |
| Generar JSON con N entradas | DeepSeek V4-Flash | 💰 |
| Refactor mecánico | DeepSeek V4-Pro | 💰 |
| Diagnóstico bug complejo | Opus 4.7 | 💰💰💰💰 |
| Diagnóstico bug simple | DeepSeek V4-Pro | 💰 |
| Decisión sobre persistencia | Opus 4.7 (siempre) | 💰💰💰 |
| Decisión sobre UI | Opus + UI_UX_STYLE_GUIDE | 💰💰💰 |
| Generar boilerplate Python | DeepSeek V4-Flash | 💰 |
| Validador de schemas Python | DeepSeek V4-Pro | 💰 |
| Revisión final antes de publish | Opus 4.7 | 💰💰💰💰 |
| SPR `[OPUS-EXEC]` (criterios §3.4-bis) | Opus 4.7 | 💰💰💰 |
| Hot-fix crítico build roto | Opus 4.7 | 💰💰💰 |

### 4.2 DeepSeek V4-Pro vs V4-Flash

**V4-Pro** (default ejecutor):
- 1.6T params, 49B activos
- Mejor en agentic largos y multi-step
- Codeforces 3206 (top tier)
- $3.48/M output tokens

**V4-Flash** (para tareas simples):
- 284B params, 13B activos
- 12.4× más barato que Pro
- Casi igual de bueno en tareas simples
- $0.28/M output tokens

**Regla**: para SPR-xxx normales usa **Pro**. Para correcciones triviales y JSONs, usa **Flash**.

---

## 5. Daily Log (sistema)

> **El sistema dailylog está descrito en detalle en `DAILY_LOG.md`** (plantilla canónica + instructivo). Esta sección es el resumen operativo para el flujo diario.

### 5.1 Resumen

- **Ubicación**: `docs/dailylog/` (NO `docs/daily_logs/` — sistema viejo, eliminado el 2026-05-06).
- **Generación**: `python scripts/tools/close_sprint.py [SPR-XXX]` tras cada `git tag SPR-XXX`.
- **Naming**: `DL_YYYY-MM-DD_SPR-<tokens>_<autor>.md`. Tokens unidos por `+` (ej. `SPR-001+FIX1+002`).
- **Autor**: `.dailylog_user` en raíz, gitignored. Primer arranque pide nickname una vez.
- **Idempotente**: re-ejecutar para un SPR ya registrado solo refresca bloques AUTO; preserva el bloque MANUAL.

### 5.2 Bloques de un DL

- **Bloques AUTO** (regenerados cada ejecución del script): metadata de sprints cerrados, commits del día, archivos tocados, estado del repo. NO editar a mano.
- **Bloque MANUAL** (preservado entre ejecuciones): energía/foco subjetivo, tiempo real, bloqueos, bugs, decisiones, notas para mañana, misceláneas. Lo rellena el humano en VS Code.

### 5.3 Por qué NO hay plantilla viva en este doc

La plantilla canónica vive en `DAILY_LOG.md` §7 y la materializa el script. Cualquier cambio de formato se hace en una sola fuente: el script + `DAILY_LOG.md`. Ver ejemplo real en `docs/dailylog/DL_2026-05-06_SPR-001+FIX1_lexosi.md`.

---

## 6. Budget tracking de tokens

### 6.1 Estimaciones por tipo de tarea

| Tarea | Tokens input típicos | Tokens output típicos | Modelo recomendado | Coste aprox |
|---|---|---|---|---|
| Briefing matinal | 30K | 5K | Opus | $0.15 |
| Implementar SPR Verse simple (~100 líneas) | 15K | 3K | DeepSeek Pro | $0.03 |
| Implementar SPR Verse complejo (~300 líneas) | 25K | 8K | DeepSeek Pro | $0.07 |
| Generar JSON 50 entries | 5K | 4K | DeepSeek Flash | $0.002 |
| Corregir error sintaxis | 8K | 1K | DeepSeek Flash | $0.001 |
| Diagnóstico bug complejo | 40K | 10K | Opus | $0.30 |
| Revisión completa antes de publish | 60K | 8K | Opus | $0.30 |

### 6.2 Presupuesto diario realista

| Intensidad | Tokens/día | Coste estimado |
|---|---|---|
| Día tranquilo (1-2 sprints) | 100K total | $0.30-0.50 |
| Día normal (4-6 sprints) | 300K total | $0.80-1.50 |
| Día intenso (briefing + 7-8 sprints + bug) | 600K total | $2-3 |
| Día con refactor grande | 1M total | $4-6 |

### 6.3 Optimizaciones de coste

1. **Caché de prompts**: DeepSeek cobra el cache hit a 20% del precio normal. Si pegas siempre los mismos archivos al inicio (CONCEPT.md, etc.), aprovechas.
2. **DeepSeek-Flash para todo lo trivial**: 12× más barato que Pro, casi igual de bueno en tareas simples.
3. **Solo abre Opus cuando sea necesario**: NO uses Opus para cosas que DeepSeek hace igual de bien.
4. **Cierra chats de DeepSeek frecuentemente** para evitar el bug del `reasoning_content` (sección 9.1).

---

## 7. Reglas de comunicación entre modelos

### 7.1 Lo que Opus le dice a DeepSeek (vía ti)

Opus debe darte **especificaciones quirúrgicas**, no descripciones vagas. Plantilla obligatoria:

```markdown
## SPR-XXX: [Título exacto]

### Contexto mínimo necesario
- CONCEPT.md sección X.Y
- API_REFERENCE_GENERATED.md (si toca módulos Core/)
- PERSISTENCE_MAP.md (si toca persistencia)
- UI_UX_STYLE_GUIDE.md (si toca UI)
- Archivos a leer: [paths exactos]

### Especificación
[Aquí Opus describe paso a paso qué hay que hacer, sin ambigüedad]

### Done Criteria explícitos
- [ ] El archivo X existe en path Y
- [ ] La función Z está implementada con signatura: ...
- [ ] Tests: el test_device_TestXxx instancia la clase y reporta OK

### Restricciones específicas para este sprint
- NO añadir campos a PlayerCore (toca SPR-YYY)
- NO modificar persistencia
- USAR EventBus, no llamadas directas
- Seguir UI_UX_STYLE_GUIDE colores y tamaños

### Estimación tiempo: 1h
### Si DeepSeek se bloquea: escalar a Opus.
```

### 7.2 Lo que DeepSeek le reporta a ti

```markdown
## SPR-XXX: COMPLETADO

### Archivos creados
- `Content/Verse/Core/Logger.verse` (78 líneas)
- `Content/Verse/Generated/Logger_Generated.verse` (12 líneas)

### Archivos modificados
- `Content/Verse/Core/ModuleRegistry.verse` (añadido import de Logger)

### Done Criteria
- [✅] Logger.verse existe y compila
- [✅] Niveles Debug/Info/Warn/Error implementados
- [✅] DEBUG flag funciona como esperado
- [⚠️] Test in-session NO ejecutado por mí (requiere UEFN)

### Notas
- Implementé `log_with_module_prefix()` como helper privado.
- Usé failable function pattern para evitar excepciones.
- No tuve que tocar persistencia.

### Próximo paso para ti
1. Copia los archivos a tu UEFN project
2. Build Verse Code (Ctrl+Shift+B)
3. Push Changes
4. Crear test_device_TestLogger según TESTING_PROTOCOL.md
5. Ejecutar test in-session
```

### 7.3 Lo que tú le dices a DeepSeek si hay error

```markdown
## SPR-XXX: ERROR EN BUILD

Compilando di este error:

[pegar error completo de UEFN]

Archivo afectado: [path]
Línea: [número]

Por favor:
1. Diagnostica
2. Propón fix mínimo
3. Si es algo no obvio, di que escalemos a Opus
```

---

## 8. Cuándo escalar de DeepSeek a Opus

### 8.1 Triggers automáticos de escalado

DeepSeek **debe escalar** (decirte "esto es para Opus") en estos casos:

1. **Decisión arquitectónica no especificada**
   > "El sprint dice 'usa Logger' pero hay 2 patrones posibles. ¿Cuál?"

2. **Cambio de schema de persistencia**
   > "Para hacer esto necesitaría añadir un campo a PlayerCore. STOP."

3. **API no documentada en API_REFERENCE_GENERATED.md**
   > "Necesito X pero no está en la API ref. ¿Existe? STOP."

4. **Conflicto entre docs**
   > "CONCEPT.md sección 14.3 dice X, pero el sprint dice Y. ¿Cuál sigo?"

5. **Bug que no entiende**
   > "Reproduzco el bug pero no veo causa. STOP, escalo."

6. **Sprint que toma >2h estimadas**
   > "Esto da para 4h, no 2h. STOP, hay que dividir."

7. **Diseño UI nuevo no en UI_UX_STYLE_GUIDE**
   > "El sprint pide UI con flujo X, pero no está en style guide. STOP."

### 8.2 Plantilla de escalado a Opus

```markdown
🚨 ESCALADO DE DEEPSEEK A OPUS

## Contexto
SPR-XXX en progreso. DeepSeek bloqueado.

## Razón del escalado
[copiar lo que dice DeepSeek]

## Lo que ha hecho DeepSeek hasta ahora
[archivos modificados, estado actual]

## Pregunta concreta para ti
[la duda exacta]

## Tiempo invertido en bloqueo
[X minutos]

Por favor:
1. Resuelve la duda con respuesta concreta
2. Si requiere actualizar CONCEPT.md o PERSISTENCE_MAP.md, hazlo
3. Si hay que modificar el sprint, dame la nueva spec para DeepSeek
4. Si hay que abortar el sprint, dilo claro
```

---

## 9. Bugs conocidos y trampas de DeepSeek V4-Pro

### 9.1 ⚠️ Bug del `reasoning_content` en multi-turn

**Síntoma**: en chats largos con thinking mode activo, da error 400 al continuar la conversación.

**Causa**: DeepSeek no maneja bien el `reasoning_content` en mensajes anteriores cuando vuelves a llamar.

**Workarounds (elegir uno)**:

1. **Reiniciar chat frecuentemente** (recomendado): cada 3-4 sprints abrir chat nuevo. Pegar capsule + contexto otra vez. Más limpio.
2. **Desactivar thinking mode** entre turnos para tareas que no lo necesitan.
3. **Usar la última versión del SDK** (deepseek-encoding) que filtra el reasoning_content.

**Mi recomendación**: 1 chat de DeepSeek por SPR-xxx. Cuando termina el sprint, cierras chat. Es más limpio para todos.

### 9.2 Trampa: instrucciones complejas multi-constraint

DeepSeek V4-Pro a veces **ignora restricciones secundarias** cuando las instrucciones son largas con muchas reglas.

**Mitigación**: la cápsula `DEEPSEEK_CAPSULE.md` contiene las 5 reglas más importantes. Pegarla SIEMPRE primero. Si Opus añade restricciones extra, **listarlas como bullet points numerados** al final.

**Corolario**: si en briefing detectas que un SPR cae en este patrón (5+ restricciones cruzadas) y no se puede dividir limpiamente, márcalo `[OPUS-EXEC]` (WORKFLOW §3.4-bis). Es más barato que pagar 3 iteraciones DeepSeek + escalado.

### 9.3 Trampa: HLE knowledge gaps

DeepSeek tiene gaps en factual knowledge (37.7% HLE vs 40% Opus, 44% Gemini). Para preguntas factuales sobre Verse APIs específicas, **siempre referenciar API_REFERENCE_GENERATED.md** en el prompt.

### 9.4 Trampa: agentic largo

Los benchmarks muestran que DeepSeek pierde calidad en sesiones agentic muy largas (más de 10 mensajes en chain).

**Mitigación**:
- Mantener cada sprint en un chat separado (max 5-7 turnos por chat)
- No pedirle "haz todos estos sprints" en un solo chat — uno cada vez

### 9.5 ✅ Lo que DeepSeek hace MEJOR que Opus

- **Terminal-Bench 2.0**: 67.9 vs 65.4 → **mejor en comandos terminal y systems-level**
- **LiveCodeBench**: 93.5 vs 88.8 → **mejor en algoritmos puros**
- **Codeforces**: 3206 → **mejor en problemas competitivos**
- **Coste**: 7× más barato

**Conclusión**: para código Verse/Python rutinario, DeepSeek es mejor coste-beneficio. Para arquitectura y decisiones complejas, Opus.

### 9.6 Cosas que DeepSeek puede inventar (vigilar)

- **Verse APIs que no existen** (sobre todo en módulos UEFN específicos). → Solución: API_REFERENCE_GENERATED.md.
- **Funciones de Python en módulo `unreal`** que no están en UEFN. → Solución: lista de APIs verificadas en CONCEPT.md sección 6.
- **Patrones de persistencia que rompen UEFN**. → Solución: PERSISTENCE_MAP.md como referencia obligatoria.

---

## 📌 Resumen ejecutivo del workflow

```
1️⃣ Briefing matinal con OPUS (15-30 min, $0.15)
2️⃣ Sprints uno-a-uno con DEEPSEEK (chat por sprint, $0.03-0.07/each)
3️⃣ TÚ haces el puente: copy/paste/test
4️⃣ Cierre del día: Daily Log + Git commit (5-10 min)

DURANTE EL DÍA, ESCALAR A OPUS si:
   - Decisión arquitectónica
   - Schema de persistencia
   - UI no en style guide
   - Bug profundo
   - Conflicto entre docs
```

---

**Fin del documento.**
