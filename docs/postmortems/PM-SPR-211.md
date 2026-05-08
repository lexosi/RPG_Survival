# POSTMORTEM — 2026-05-07 — Verse Syntax Drift (SPR-211)

## 📋 Resumen ejecutivo (TL;DR)

Build Verse Code en UEFN tras cierre de SPR-007 reveló que `Core/TimeSync.verse` no compilaba. 1h+ de debugging interactivo descubrió **13 lecciones críticas de sintaxis Verse moderna** que invalidan partes de docs autoritativos del proyecto (MODULES_DEPENDENCY_GRAPH H3.1, GLOSSARY "Singleton top-level", API_REFERENCE §3, BOOTSTRAP §10/§11, CHANGELOG D-02). Refactor 5 archivos Verse a patrones canónicos modernos validados con build real, creación de `docs/VERSE_SYNTAX_GUIDE.md` como fuente única, audit de 8 docs autoritativos.

## 🔥 Síntoma

Tras cierre limpio de SPR-006 (Logger) + SPR-007 (TimeSync) y commit `c1c1f62`, Build Verse Code en UEFN reportó múltiples errores en cascada:

- `vErr:S26: Missing label in path following "/"` en imports `using { /<ProjectName>/Core/Logger }`.
- Err `3512` en construcción top-level `Logger : logger_module = logger_module{}` (archetype instantiation has 'transacts' effect, not allowed by context).
- Err `3593` (Definition more accessible than its dependencies) en cadenas de visibility.
- Err `3547` (Expected a type, got archetype constructor instead) en structs literal top-level.
- Err `3558` (external{} only valid in .digest files) al intentar workaround vía external.
- `Floor(x)` con `<decides>` rechazado — call signature error.

Los 5 archivos Verse modificados (Logger, TimeSync, Companions/Items/Quests_Generated) habían sido escritos siguiendo plantillas y patrones de los docs autoritativos del proyecto. Compilación falló en TODOS.

## 🔍 Causa raíz

**Drift acumulado entre sintaxis Verse moderna (UEFN Release 40.30) y docs autoritativos del proyecto basados en sintaxis vieja** (probablemente UEFN < 40, Verse pre-modules-namespace o pre-effect-propagation enforcement).

Las decisiones cerradas en auditorías previas (Auditoría 2 — C1 "Singletons top-level con `class<concrete>`", Auditoría 3 — H3.1 "specifier `<concrete>` obligatorio") asumían un modelo de Verse en el que clases con `<concrete>` instanciables top-level eran el patrón canónico para Cores singletons. Ese modelo **ya no es válido en Verse moderno**: los métodos `<decides>` propagan el efecto `<transacts>` al class instance, y el contexto top-level de un module Verse es `<computes>` puro — la construcción `class_t{}` top-level falla.

Solución vigente (validada con build real): **`Module<public> := module:` namespace**, no class. Sin archetype, sin construcción.

Adicionalmente:
- Path canónico Verse moderno **incluye** `Verse/`: `/lexosi@fortnite.com/RPG_Survival/Verse/Core/Logger`. La afirmación de docs viejos *"`Content/Verse/` no aparece en el path"* es falsa.
- Sintaxis dotted relative **es válida** y preferida (VS Code Quick Fix la ofrece): `using { Verse.Core.Logger }`. La afirmación de CHANGELOG D-02 que la marcaba inválida es obsoleta.
- Funciones failable se llaman con `[]`, no `()`.
- `return X` no existe — última expresión del bloque = retorno.
- `var` top-level admite SOLO `weak_map`.
- Structs literal top-level `NAME := struct_t{...}` también propagan `transacts` (mismo err 3512 que classes).

## ⏱️ Timeline

- **Sesión Opus 4.7 web (2026-05-07 mañana–tarde)**: 6 sprints cerrados (SPR-210, SPR-209, SPR-003, SPR-004, SPR-006, SPR-007). Tag `SPR-007` en HEAD master, commit `c1c1f62`.
- **Build UEFN post-SPR-007**: TimeSync.verse no compila. Múltiples errors en cascada.
- **+15 min**: Logger también afectado (mismo patrón class<concrete>).
- **+30 min**: Generated files también afectados (struct literal top-level → 3512+3547).
- **+45 min**: imports `<ProjectName>` literal → vErr:S26.
- **+1h**: 13 lecciones identificadas + validadas iterando con build real.
- **+1h 30 min**: 5 archivos Verse refactoreados a patrones canónicos. Build limpio.
- **2026-05-07 tarde** (esta sesión SPR-211): handoff a Claude Code para audit + refactor docs + generator + postmortem.

## 🛠️ Resolución

### Refactor Verse (5 archivos)

| Archivo | Patrón anterior (rompe) | Patrón vigente (compila) |
|---|---|---|
| `Core/Logger.verse` | `logger_module := class<concrete>:` + `Logger : logger_module = logger_module{}` | `Logger<public> := module:` |
| `Core/TimeSync.verse` | `timesync_module := class<concrete>:` con `<decides>` methods | `TimeSync<public> := module:` con funciones `<decides>:int=` y `<decides>:void=` (predicados) |
| `Generated/Companions_Generated.verse` | `COMPANION_DRAGON_FIRE := companion_def{...}` top-level | `GetCompanionDragonFire<public>():companion_def= companion_def{ID := 1, ...}` (Patrón 3) |
| `Generated/Items_Generated.verse` | idem | idem con `GetItem*()` |
| `Generated/Quests_Generated.verse` | idem | idem con `GetQuest*()` |

### Refactor generator script

`scripts/build/02_export_constants_to_verse.py`: funciones `export_companions/items/quests` reescritas para emitir Patrón 3 (struct `<public>` + module `<public>` + funciones getter `Get{Singular}{PascalCase}`). Helper `_to_pascal_case` añadido. Header generado incluye nota refactor SPR-211.

Verificación idempotencia: backup de los 3 archivos validados manualmente, regenerar con script, `git diff --no-index` → 0 diff semántico (modulo CRLF normalization, que git absorbe en commit).

### Audit docs autoritativos

8 docs corregidos:
1. `CHANGELOG.md` — D-02 marcada obsoleta + entry SPR-211 nueva.
2. `MODULES_DEPENDENCY_GRAPH.md` — disclaimer top-of-doc + Logger ejemplo refactoreado + §4.1 nota.
3. `GLOSSARY.md` — Logger/TimeSync entries actualizadas + entrada legacy "Singleton top-level" reemplazada por "Module namespace pattern" + nueva entrada "Generated data getter pattern".
4. `API_REFERENCE_GENERATED.md` — §3 cabecera + §3.2/§3.3 Logger/TimeSync arch nota.
5. `BOOTSTRAP_PIPELINE.md` — header disclaimer + §1.3 ejemplo + §6.1 anti-patrón fix + §9.1 plantilla refactor + plantilla Python emit.
6. `CONCEPT.md` — disclaimer en §sprints F0 + SPR-006/007 done criteria actualizado.
7. `SPRINTS_BACKLOG.md` — SPR-006/007 marcados done + entry SPR-211 nuevo + Notas SPR-211 + total recalibrado a 208.
8. `PROMPT.md` — sección "Verse syntax rules" añadida + referencia VERSE_SYNTAX_GUIDE.md como autoridad.

### Doc nuevo

`docs/VERSE_SYNTAX_GUIDE.md` — fuente única de sintaxis Verse moderna. Estructura §1–§9: 13 lecciones, 3 patrones canónicos, anti-patrones tabulados con error codes, imports/paths, failable context, state mutable, effects (TBD), validación (workflow + tabla error codes), referencias cruzadas.

## ⏳ Tiempo perdido

~3h reales: 1h debugging build UEFN + 1.5h refactor Verse + handoff de docs (sesión SPR-211 actual ~2h adicionales).

## 💔 Impacto

- **A jugadores**: ninguno (proyecto F0, sin publish).
- **A datos**: ninguno (Verse compile-time, no runtime data).
- **A workflow**: alto — todos los SPRs F0 que asumían patrón "Singleton top-level con class<concrete>" deben re-evaluarse contra build UEFN real durante implementación. SPR-005, SPR-008, SPR-009, SPR-010 quedan como casos pendientes; el patrón concreto se valida sprint por sprint. Caso "Core con state mutable" (SPR-008 PersistenceLayer con weak_maps) queda como caso de estudio para `VERSE_SYNTAX_GUIDE.md` §2.4.

## ✅ Cómo prevenirlo (accionable)

- [x] **`docs/VERSE_SYNTAX_GUIDE.md` como fuente única**. Cualquier doc autoritativo que contradiga la guide está obsoleto. Consultar SIEMPRE antes de emitir Verse.
- [x] **PROMPT.md sección "Verse syntax rules"**. Reglas operativas mínimas + obligación de consultar guide.
- [x] **Generator script regenera Patrón 3** sin posibilidad de emitir patrón legacy.
- [ ] **Validador `validate_verse_syntax.py` (próximo sprint TBD)**: grep estático contra anti-patrones (`class<concrete>:` + métodos `<decides>` top-level, `NAME := struct_t{...}` top-level dentro module, `return ` en cuerpo de función Verse, `<ProjectName>` literal en imports) antes de Build UEFN. Pre-commit hook bloqueante.
- [ ] **Re-validar guide cada update mayor de UEFN** (release notes Epic). Tabla de versión UEFN → patrón vigente en guide §9.
- [ ] **SPR-008 (PersistenceLayer) como caso de estudio**: documentar approach final en guide §2.4 una vez build UEFN valide patrón con weak_maps + funciones load/save.

## 📝 Cambios necesarios a docs

- [x] `docs/VERSE_SYNTAX_GUIDE.md` — creado.
- [x] `docs/CHANGELOG.md` — D-02 marcada obsoleta + entry SPR-211.
- [x] `docs/MODULES_DEPENDENCY_GRAPH.md` — disclaimer + Logger ejemplo + §4.1.
- [x] `docs/GLOSSARY.md` — Logger/TimeSync + Module namespace pattern + Generated data getter pattern.
- [x] `docs/API_REFERENCE_GENERATED.md` — §3 cabecera + §3.2/§3.3.
- [x] `docs/BOOTSTRAP_PIPELINE.md` — header + §1.3 + §6.1 + §9.1 + plantilla Python emit.
- [x] `docs/CONCEPT.md` — disclaimer §sprints F0 + SPR-006/007 done.
- [x] `docs/SPRINTS_BACKLOG.md` — SPR-006/007 done + SPR-211 entry + Notas SPR-211.
- [x] `docs/PROMPT.md` — sección Verse syntax rules.
- [x] `docs/POSTMORTEMS_INDEX.md` — entry PM-SPR-211 (esta sesión).
- [x] `docs/DAILY_LOG.md` — entry 2026-05-07 (esta sesión).

## 🧠 Lecciones aprendidas

1. **Validar contra build real, no contra docs viejos**. Los docs autoritativos del proyecto reflejan decisiones de un punto en el tiempo; las plataformas (UEFN, Verse) evolucionan. Cualquier patrón Verse declarado "canónico" en doc debe revalidarse periódicamente contra Build UEFN actual.
2. **Auditorías de drift sintáctico tienen ROI alto**. SPR-211 invalida 3 entradas previas de auditorías (Audit 2 — C1, Audit 3 — H3.1) que parecían sólidas. Sin SPR-211, los SPR-008+ habrían fallado en build con la misma cascada de errores.
3. **Caveat de specifiers de efecto**: `<decides>`, `<transacts>`, `<computes>`, `<allocates>`, `<varies>` propagan reglas que cambian en qué contextos un constructor puede aparecer. La regla "top-level es `<computes>` puro" es la pieza que rompe el patrón class<concrete> + métodos failable.
4. **Drift detectable estáticamente**: muchas de las lecciones (1, 3, 5, 6, 8, 11, 12) son grep-able. Validador estático antes de Build UEFN sería ROI alto.
5. **VS Code Quick Fix es señal**: cuando Quick Fix sugiere "Use relative path" produciendo dotted relative, **eso es Verse moderno hablando**. Confiar en Quick Fix > confiar en docs viejos del proyecto.

## 🔗 Referencias

- Sprint afectado: SPR-211 (este sprint), SPR-006, SPR-007 (validados retroactivamente).
- Commits relevantes: `c1c1f62` (HEAD pre-SPR-211, los 5 archivos Verse modified pero sin commit), commit SPR-211 atomic pendiente humano.
- Doc nuevo: `docs/VERSE_SYNTAX_GUIDE.md`.
- Postmortems relacionados: ninguno previo (PM-SPR-211 es el primer postmortem del índice).
- Auditorías invalidadas: Auditoría 2 — C1 (en parte), Auditoría 3 — H3.1.
