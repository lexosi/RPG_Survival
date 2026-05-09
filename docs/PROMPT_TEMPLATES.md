# 📋 PROMPT_TEMPLATES — Plantillas listas para copiar

> **Plantillas estandarizadas para los tipos más comunes de petición a Opus y DeepSeek.**
> Pegar, rellenar los `[CORCHETES]`, enviar.

---

## 🧭 Índice

### Para OPUS (Director)
1. [Briefing matinal](#1-briefing-matinal-a-opus)
2. [Diseño de sistema nuevo](#2-diseño-de-sistema-nuevo)
3. [Diagnóstico de bug profundo](#3-diagnóstico-de-bug-profundo)
4. [Review de cambio de persistencia](#4-review-de-cambio-de-persistencia)
5. [Decisión arquitectónica](#5-decisión-arquitectónica)
6. [Cierre de fase](#6-cierre-de-fase)
7. [Escalado desde DeepSeek](#7-escalado-desde-deepseek)

### Para DEEPSEEK (Ejecutor)
8. [Implementar SPR Verse simple](#8-implementar-spr-verse-simple)
9. [Implementar SPR Verse complejo](#9-implementar-spr-verse-complejo)
10. [Implementar script Python build](#10-implementar-script-python-build)
11. [Crear/modificar JSON masivo](#11-crearmodificar-json-masivo)
12. [Crear test_device](#12-crear-test_device)
13. [Corregir error de compilación](#13-corregir-error-de-compilación)
14. [Refactor mecánico](#14-refactor-mecánico)
15. [Generar boilerplate](#15-generar-boilerplate)

### Plantillas auxiliares
16. [Reportar Done Criteria](#16-reportar-done-criteria-deepseek--tú)
17. [Postmortem rápido](#17-postmortem-rápido)
18. [Daily Log](#18-daily-log)

---

# 🎩 PARA OPUS (Director)

## 1. Briefing matinal a Opus

```
Buenos días Opus. Briefing matinal del día [FECHA].

📋 ESTADO ACTUAL:
- Fase activa: [F0/F1/F2/...]
- Último sprint completado: SPR-[XXX]
- Sprints pendientes en fase: [SPR-XXX, SPR-XXY, SPR-XXZ]

📒 DAILY LOG DE AYER:
[pega aquí el Daily Log de ayer, o "primer día" si no hay]

🎯 OBJETIVO DE HOY:
[lo que quieras conseguir; si no sabes, di "tú decides"]

⏰ TIEMPO DISPONIBLE:
[ej: "4 horas con interrupciones" o "todo el día"]

🤔 BLOQUEOS QUE TENGO:
[si hay alguno; si no hay, "ninguno"]

📤 ARCHIVOS RELEVANTES:
[adjunta los archivos modificados recientemente, o "ninguno especial"]

Tarea:
1. Analiza dependencias entre sistemas pendientes
2. Dame plan del día con 5-7 sprints SPR-XXX detallados
3. Para cada SPR: spec completa según CONCEPT.md sección 13.2
4. Para cada SPR: archivos exactos que DeepSeek necesita ver
5. Para cada SPR: Done Criteria explícitas
6. Para cada SPR: tiempo estimado (en bloques de 1.5h)
7. Marca cuáles necesitan SPR-XXX-T (test) asociado
8. Si algún SPR es "demasiado complejo" para DeepSeek → primero intenta dividirlo. Si dividirlo no resuelve (sigue requiriendo 3+ escaladas, hot-fix, o restricciones cruzadas), márcalo como `[OPUS-EXEC]` según WORKFLOW §3.4-bis y lo ejecutas tú directo.
9. Para cada SPR del plan, indica explícitamente: ejecutor = `DeepSeek-Pro` / `DeepSeek-Flash` / `OPUS-EXEC` / `Tú-manual`.

```

---

## 2. Diseño de sistema nuevo

```
Opus, necesito diseñar SYS-[XXX]: [Nombre del sistema].

📚 CONTEXTO:
- Lo que ya hay: [sistemas relacionados ya implementados]
- Lo que necesito que haga: [descripción funcional]
- Restricciones que aplican: [4 weak_maps, mobile-first, etc.]

🎯 DECISIONES A TOMAR:
- [ ] Schema de persistencia (¿qué se guarda y dónde?)
- [ ] APIs públicas (qué expone a otros sistemas)
- [ ] Eventos que emite/escucha (EventBus)
- [ ] Datos en JSON vs hardcoded
- [ ] UI necesaria (consultar UI_UX_STYLE_GUIDE)

🔗 SISTEMAS RELACIONADOS:
- SYS-[XXX]: [cómo interactúa]
- SYS-[YYY]: [cómo interactúa]

Tarea:
1. Diseña arquitectura del sistema
2. Define schema persistence (validar contra PERSISTENCE_MAP)
3. Define APIs públicas (a añadir a API_REFERENCE_GENERATED.md)
4. Define eventos
5. Decide qué va en JSON vs Verse manual
6. Lista los SPR-XXX necesarios para implementarlo (con dependencias)
7. Estima tiempo total
```

---

## 3. Diagnóstico de bug profundo

```
🐛 BUG QUE NO ENTIENDO. Necesito diagnóstico.

📋 SÍNTOMAS:
[descripción exacta de qué pasa]

🔄 PASOS PARA REPRODUCIR:
1. [paso 1]
2. [paso 2]
3. [paso 3] → bug aparece

💻 OUTPUT/ERROR:
[pegar consola, stack trace, o screenshot descrito]

📂 ARCHIVOS RELEVANTES:
[adjuntar los .verse implicados]

🤔 LO QUE HE PROBADO:
- [intento 1]: [resultado]
- [intento 2]: [resultado]

🤖 LO QUE DICE DEEPSEEK:
[si hay diagnóstico previo de DeepSeek, pegarlo; si no, "no consultado"]

Tarea:
1. Diagnostica causa raíz (no síntoma)
2. Si requiere cambio en otro sistema, dilo
3. Propón fix mínimo
4. Si requiere fix grande, propón cómo dividirlo en sprints
5. Identifica si este patrón puede aparecer en otros sitios
```

---

## 4. Review de cambio de persistencia

```
🚨 CAMBIO EN PERSISTENCIA. Necesito review antes de implementar.

📋 CAMBIO PROPUESTO:
[describir qué quieres cambiar/añadir]

🎯 RAZÓN:
[por qué hace falta este cambio]

📂 ESQUEMA ACTUAL (relevante):
[pegar la struct/class actual de PlayerCore/Inventory/Progress/Economy]

✨ ESQUEMA PROPUESTO:
[cómo quedaría tras el cambio]

🤔 MIS DUDAS:
- [duda 1]
- [duda 2]

Tarea:
1. Verifica contra PERSISTENCE_MAP.md sección 1 (reglas inquebrantables)
2. Calcula impacto en bytes (worst-case scenario)
3. Verifica que NO renombra/elimina/cambia tipo
4. Confirma que campos nuevos tienen default values
5. Sugiere si necesita migración (Schema Version increment)
6. Si OK, dame el código exacto a implementar
7. Si NO OK, explica qué cambiar
8. Actualiza PERSISTENCE_MAP.md con los nuevos campos
```

---

## 5. Decisión arquitectónica

```
🤔 DECISIÓN ARQUITECTÓNICA pendiente.

📋 EL DILEMA:
Tengo que decidir entre [opción A] y [opción B] para implementar [feature].

OPCIÓN A: [descripción]
PROS:
- [pro 1]
- [pro 2]
CONTRAS:
- [contra 1]

OPCIÓN B: [descripción]
PROS:
- [pro 1]
CONTRAS:
- [contra 1]

📚 CONTEXTO RELEVANTE:
[lo que importa para la decisión: usuarios afectados, dependencias, performance, etc.]

📂 SISTEMAS AFECTADOS:
- SYS-[XXX]: [cómo afecta]
- SYS-[YYY]: [cómo afecta]

Tarea:
1. Analiza ambas opciones contra restricciones de UEFN/mobile/persistencia
2. Considera deuda técnica futura
3. Recomienda una con justificación clara
4. Si hay opción C que no consideré, propónla
5. Si decides cambiar el approach, actualiza CONCEPT.md sección 14 (decisiones)
6. Si afecta SPR-XXX pendientes, ajusta su spec
```

---

## 6. Cierre de fase

```
🏁 FASE [F0/F1/F2/...] TERMINADA.

📋 SPRINTS COMPLETADOS:
- ✅ SPR-001: [...]
- ✅ SPR-002: [...]
- ...

✅ DONE CRITERIA DE FASE (de CONCEPT.md sección 12):
[copiar Done Criteria de la fase y marcar ✅/❌]

🎯 ESTADO REAL:
- Lo que funciona: [lista]
- Lo que está incompleto: [lista]
- Bugs conocidos: [lista]

📊 MÉTRICAS:
- Tiempo total invertido: [horas]
- Sprints originales planificados: [N]
- Sprints reales: [N+ extras]
- Tokens consumidos: ~[XK]

Tarea:
1. Verifica que todos los Done Criteria están ✅
2. Si algo no está, decide: bloquear paso a fase siguiente o aceptar deuda
3. Actualiza CONCEPT.md sección 12 con estado real
4. Genera plan de Fase [siguiente]
5. git tag de cierre de fase: dame el comando exacto
```

---

## 7. Escalado desde DeepSeek

```
🚨 ESCALADO DE DEEPSEEK A OPUS

📋 CONTEXTO:
- Sprint en progreso: SPR-[XXX]
- Estado: [bloqueado / en bucle / decisión necesaria]

❓ RAZÓN DEL ESCALADO:
[Pegar lo que dijo DeepSeek o "DeepSeek lleva 3 intentos fallidos"]

📂 ESTADO ACTUAL DEL CÓDIGO:
[pegar archivo afectado completo]

💬 LO QUE HA HECHO DEEPSEEK:
[resumen de los intentos]

⏱️ TIEMPO INVERTIDO EN BLOQUEO:
[X minutos]

🤔 LA PREGUNTA CONCRETA:
[la duda exacta que necesita Opus]

Tarea:
1. Resuelve la duda con respuesta concreta
2. Si requiere actualizar CONCEPT.md / PERSISTENCE_MAP / otro doc, hazlo
3. Si hay que reescribir el sprint, dame la spec nueva
4. Si hay que abortar el sprint, dilo claro y explica por qué
5. Identifica el patrón para evitarlo en sprints futuros
```

---

# ⚡ PARA DEEPSEEK (Ejecutor)

## 8. Implementar SPR Verse simple

```
🎯 PROYECTO: UEFN Survival Tycoon Modular Map.

🔒 REGLAS INNEGOCIABLES:
1. Verse: SOLO 4 weak_maps persistentes, máx 128 KB c/u. NUNCA renombrar/eliminar/cambiar tipo de campos publicados.
2. Datos en JSON, nunca hardcoded en Verse. Verse = lógica. Python = build/config. JSON = contenido.
3. Mobile-first: optimizar siempre.
4. NO inventar APIs. Si no está en API_REFERENCE_GENERATED.md, STOP y reporta.
5. Si toca arquitectura/persistencia/UI no especificada → STOP y escala a Opus.

🌐 IDIOMA: Español España.

📦 SPRINT: SPR-[XXX] — [Título]

## Especificación
[pegar lo que dijo Opus en briefing]

## Done Criteria
- [ ] [criterio 1]
- [ ] [criterio 2]
- [ ] Compila sin warnings
- [ ] Test in-session pasa con test_device

## Archivos de contexto
[pegar archivos relevantes]

## Tu tarea
1. Implementa el sprint completo
2. Reporta archivos creados/modificados con path absoluto
3. Marca cada Done Criteria como ✅/❌/⚠️ con justificación
4. Si hay decisión arquitectónica no clara → STOP y reporta
5. Si necesitas API no documentada → STOP y reporta

GO.
```

---

## 9. Implementar SPR Verse complejo

```
🎯 PROYECTO: UEFN Survival Tycoon Modular Map.

🔒 REGLAS INNEGOCIABLES:
1. Verse: SOLO 4 weak_maps persistentes, máx 128 KB c/u. NUNCA renombrar/eliminar/cambiar tipo de campos publicados.
2. Datos en JSON, nunca hardcoded en Verse. Verse = lógica. Python = build/config.
3. Mobile-first.
4. NO inventar APIs. Si no está en API_REFERENCE_GENERATED.md, STOP.
5. Si toca arquitectura/persistencia/UI no especificada → STOP y escala.

📚 CONTEXTO OBLIGATORIO (lee antes de implementar):
- CONCEPT.md secciones 5, 6, 7, 8 (incluidas abajo)
- API_REFERENCE_GENERATED.md (incluido abajo)
- PERSISTENCE_MAP.md (incluido abajo)
- UI_UX_STYLE_GUIDE.md (si toca UI - incluido abajo)

[pegar las secciones relevantes y archivos auxiliares]

📦 SPRINT: SPR-[XXX] — [Título]
Tipo: [verse-system / verse-feature / verse-integration]
Tiempo estimado: [Xh]

## Especificación detallada
[pegar lo que dijo Opus, idealmente con diagramas o pseudocódigo]

## Sub-tareas (si aplica)
1. [sub-tarea 1]
2. [sub-tarea 2]
3. [sub-tarea 3]

## Done Criteria explícitas
- [ ] [criterio 1: archivo X existe en path Y]
- [ ] [criterio 2: función Z implementada con signatura ABC]
- [ ] [criterio 3: integración con SYS-XXX funciona]
- [ ] Compila sin warnings
- [ ] No toca persistencia (o si toca: PERSISTENCE_MAP validado)

## Restricciones específicas para este sprint
- NO añadir campos a [estructura X] (toca SPR-YYY)
- NO modificar [módulo Z]
- USAR [patrón A], no [patrón B]

## Tu tarea
1. Lee TODO el contexto
2. Implementa el sprint COMPLETO
3. Reporta:
   - Archivos creados con path absoluto + número de líneas
   - Archivos modificados con resumen del cambio
   - Done Criteria: ✅/❌/⚠️ con justificación
   - Si modificaste API pública: lista para actualizar API_REFERENCE_GENERATED.md
4. Si encuentras decisión no obvia → STOP y reporta
5. Si necesitas API no documentada → STOP y reporta
6. Si tu solución supera 1.5h estimadas → STOP, divide en sub-sprints

GO.
```

---

## 10. Implementar script Python build

```
🎯 PROYECTO: UEFN Survival Tycoon Modular Map.

🔒 REGLAS PYTHON:
1. Source of truth = JSON. Generated/ = inmutable.
2. Idempotente: ejecutar N veces da mismo resultado.
3. Sin lógica de gameplay. Solo transformar.
4. Try/except defensivo. Editor no crashea si script falla.
5. Type hints + docstrings Google-style.

📚 CONTEXTO:
- BOOTSTRAP_PIPELINE.md sección 3 (transformers) y sección 8 (plantillas)
[pegar las secciones]

📦 SPRINT: SPR-[XXX] — [Título del script]
Tipo: python-build

## Tarea
Crear script `scripts/build/[NN]_[nombre].py` que:
- Lee: [JSON fuente con path]
- Genera: [archivo destino]
- Valida: [reglas a verificar antes de generar]

## Schema del JSON fuente
[pegar estructura esperada del JSON]

## Schema del Verse generado (si aplica)
[pegar cómo debe verse el output]

## Done Criteria
- [ ] Script existe en path correcto
- [ ] Importa correctamente (test: python -c "import scripts.build.NN_xxx")
- [ ] Ejecuta sin errores con dummy data
- [ ] Genera archivo destino con header de warning
- [ ] Es idempotente (probado ejecutando 3 veces)
- [ ] Tiene try/except top-level

## Tu tarea
1. Implementa siguiendo plantilla de BOOTSTRAP_PIPELINE.md sección 8
2. Incluye type hints y docstrings
3. Reporta archivo creado + ejemplo de output

GO.
```

---

## 11. Crear/modificar JSON masivo

```
🎯 PROYECTO: UEFN Survival Tycoon Modular Map.

📦 TAREA: poblar [archivo JSON].

📋 CONTEXTO:
- Schema esperado: [pegar schema/ejemplo de 2-3 entries existentes]
- Sistema afectado: SYS-[XXX]
- Archivo: `data/[ruta]/[archivo].json`

## Necesito que añadas
[descripción: cuántas entries, qué tipo, con qué características]

Ej: "50 companions más con rareza Common-Rare, distribuidos como 30 Common, 15 Uncommon, 5 Rare. Stats balanceados según fórmula:
- HP base = 50 + (rarity × 25)
- ATK base = 10 + (rarity × 5)
- DEF base = 5 + (rarity × 3)
- Speed base = 8 + (rarity × 2)"

## Restricciones
- IDs deben ser únicos y NO colisionar con existentes (último ID actual: [N])
- Names en UPPER_SNAKE_CASE
- Display names en español, evocadores
- Mesh paths placeholder: `Content/Assets/Meshes/Companions/[name].fbx`
- Validar que pasa `01_validate_jsons.py` (esquema en BOOTSTRAP_PIPELINE.md sección 2.3)

## Done Criteria
- [ ] N entries añadidas
- [ ] IDs únicos
- [ ] Stats siguen fórmula
- [ ] JSON válido (parse OK)
- [ ] Pasaría validación

## Tu tarea
Genera el contenido a añadir. Solo el JSON nuevo, no me devuelvas el archivo entero.

GO.
```

---

## 12. Crear test_device

```
🎯 PROYECTO: UEFN Survival Tycoon Modular Map.

📚 CONTEXTO: TESTING_PROTOCOL.md sección 3 (plantilla test_device)
[pegar sección si necesario]

📦 SPRINT: SPR-[XXX]-T — Test del SPR-[XXX]

## Sistema bajo test
Sistema implementado en SPR-[XXX]: [breve descripción]
Archivos:
[pegar archivos del sistema]

APIs públicas a testear (de API_REFERENCE_GENERATED.md):
- [Función1(...)]: [qué hace]
- [Función2(...)]: [qué hace]

## Tests a implementar
1. **Smoke test**: instanciar y llamar funciones públicas sin crashear
2. **Unit test 1**: [comportamiento concreto]
3. **Unit test 2**: [edge case]
4. **Integration test (si aplica)**: interacción con [otro sistema]

> **Si el sprint toca scripts/build/** (validador, exporter, transformer Python): adicionalmente crear test estático Python en `scripts/build/tests/test_<name>.py` siguiendo el patrón canónico de `TESTING_PROTOCOL.md` §10 (introducido SPR-009 F-C-3b). El test_device Verse y el test Python son complementarios: el primero valida runtime in-session, el segundo valida output del script en milisegundos sin UEFN abierto. Ejemplo de referencia: `scripts/build/tests/test_exporter_event_bus.py` (5 tests, fixture JSON, runtime ~0.13s, sin deps externas).

## Done Criteria
- [ ] Archivo creado en `Content/Verse/Tests/test_device_SPRxxx.verse`
- [ ] Compila sin warnings
- [ ] Es instanciable como creative_device
- [ ] Tiene HUDDisplay editable para mostrar resultados
- [ ] RunOnBegin flag opcional
- [ ] ManualTriggerButton para re-ejecutar
- [ ] Cada test reporta ✅/❌ con razón
- [ ] Final reporta total Passed/Failed
- [ ] Si el sprint tocó `scripts/build/`: test Python adicional en `scripts/build/tests/test_<name>.py` con `python -m unittest scripts.build.tests.test_<name> -v` PASS (ver TESTING_PROTOCOL.md §10)

## Tu tarea
1. Sigue plantilla TESTING_PROTOCOL.md sección 3.1
2. Implementa los 4 tests listados
3. No inventes APIs, usa solo las del sistema bajo test
4. Reporta archivo creado

GO.
```

---

## 13. Corregir error de compilación

```
🚨 ERROR DE COMPILACIÓN

## Error
[pegar error completo de UEFN console, sin truncar]

## Archivo afectado
Path: [path absoluto]
Línea reportada: [número]

## Archivo en estado actual
[pegar archivo COMPLETO]

## Cambios recientes
- [qué se modificó en el último sprint]
- [qué archivos relacionados se tocaron]

## Tu tarea
1. Diagnostica causa raíz (no síntoma derivado)
2. Propón fix mínimo (solo el error reportado, no refactor)
3. Si hay 2+ errores, identifica cuál es root cause
4. Si la causa requiere tocar otro archivo, dilo
5. Si no estás seguro, di "STOP, escalo a Opus" en vez de inventar
6. Devuelve solo el str_replace exacto a hacer (no archivo entero)

GO.
```

---

## 14. Refactor mecánico

```
🔄 REFACTOR

## Tarea
[descripción del refactor: ej "renombrar todas las llamadas a OldFunc() a NewFunc() en Systems/"]

## Archivos afectados (lista)
[lista de archivos a modificar]

## Reglas
- NO cambies lógica, solo nombres/imports
- NO toques archivos en Generated/ (regenerados desde Python)
- NO añadas funcionalidad nueva
- Si ves un bug evidente, repórtalo pero NO lo arregles aquí

## Done Criteria
- [ ] Todos los archivos listados modificados
- [ ] Compila tras el refactor
- [ ] No quedan referencias a [nombre viejo]
- [ ] Diff es solo cambios mecánicos (no lógica)

## Tu tarea
1. Aplica el refactor en cada archivo listado
2. Reporta archivos modificados con resumen del cambio
3. Si encuentras casos edge, repórtalos antes de aplicar

GO.
```

---

## 15. Generar boilerplate

```
📦 BOILERPLATE para [tipo: nuevo módulo Verse / nuevo device / nuevo script Python].

## Especificación
- Nombre: [name]
- Path: [path absoluto]
- Tipo: [class / module / device / script]
- Imports necesarios: [lista]

## Estructura esperada
[describir qué funciones/secciones debe tener]

## Plantilla a seguir
[indicar archivo similar existente como referencia, o pegar plantilla]

## Done Criteria
- [ ] Archivo creado en path correcto
- [ ] Compila sin warnings
- [ ] Tiene comentarios descriptivos
- [ ] Imports correctos

## Tu tarea
Crea el archivo. Solo boilerplate, sin lógica real (eso vendrá en sprint posterior).

GO.
```

---

# 📤 PLANTILLAS AUXILIARES

## 16. Reportar Done Criteria (DeepSeek → Tú)

DeepSeek debería usar esta plantilla al terminar:

```
✅ SPR-[XXX]: COMPLETADO

## Archivos creados
- `[path absoluto]` ([N] líneas)
  - Resumen: [qué hace]

## Archivos modificados
- `[path]`
  - Cambio: [resumen del diff]

## Done Criteria
- [✅] [criterio 1]
- [✅] [criterio 2]
- [⚠️] [criterio 3] — Razón: [explicación]
- [❌] [criterio 4] — Razón: [bloqueado por X]

## Notas relevantes
- Decisión menor tomada: [qué decidí cuando había ambigüedad menor]
- Patrón usado: [si seguí algún patrón específico de CONCEPT.md]

## API pública añadida/modificada
- `Module.Función(args):tipo` — [breve descripción]
[para que tú actualices API_REFERENCE_GENERATED.md]

## Próximo paso para ti
1. Copia archivos a UEFN project
2. Build Verse Code (Ctrl+Shift+B)
3. Push Changes
4. Ejecuta test_device (si SPR-XXX-T existe)
5. Verifica Mobile Preview
6. Marca ✅ en Daily Log
```

---

## 17. Postmortem rápido

```
# POSTMORTEM — [YYYY-MM-DD] — [Título de 1 línea]

## Síntoma
[Qué viste: 1-3 líneas]

## Causa raíz
[Qué causó realmente: 1-3 líneas]

## Resolución
[Cómo se solucionó: 1-3 líneas]

## Tiempo perdido
[X minutos / horas]

## Cómo prevenirlo
[Cambio concreto al workflow / docs / hábitos]

## Cambios necesarios a docs
- [ ] EMERGENCY_ROLLBACK.md sección X
- [ ] PROMPT.md regla Y
- [ ] (otros)
```

---

## 18. Daily Log

```
# Daily Log — [YYYY-MM-DD]

## 🎯 Plan del día (de briefing Opus)
- SPR-XXX: [título]
- SPR-XXY: [título]
- ...

## ✅ Sprints completados
- ✅ SPR-XXX — [breve]
  - Archivos: [paths]
  - Done: 100%
  - Notas: [si algo importante]

## ⚠️ Sprints incompletos
- ⚠️ SPR-XXY — [qué falta]
  - Razón: [por qué]
  - Próximo paso: [mañana]

## 🐛 Bugs encontrados
- [bug] → [resolución / pendiente]

## 💡 Decisiones tomadas
- [decisión, registrar en CONCEPT.md sección 14 si aplica]

## 🚧 Bloqueos para mañana
- [si hay]

## ⏱️ Tiempo
- Total: Xh
- Con Opus: Xmin
- Con DeepSeek: Xh
- Testing UEFN: Xmin

## 💰 Tokens (aprox)
- Opus: ~XK
- DeepSeek Pro: ~XK
- DeepSeek Flash: ~XK
- Coste día: $X

## 📝 Notas
- [cualquier cosa para mañana]
```

---

## 📌 Cómo usar este archivo

### Workflow recomendado

1. **Tienes una tarea** → busca la plantilla más parecida
2. **Copia la plantilla** entera
3. **Rellena los `[CORCHETES]`** con tu contexto
4. **Pega en chat** correspondiente (Opus o DeepSeek)
5. **Si la respuesta no es la esperada**, ajusta la plantilla y guarda la versión mejorada aquí

### Mantener este archivo vivo

- Cada vez que escribas un prompt 3+ veces parecidos → conviértelo en plantilla aquí
- Cada vez que una plantilla falle → mejórala
- Una vez al mes: revisa si hay plantillas obsoletas que borrar

---

**Fin del documento.**
