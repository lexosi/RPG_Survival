# 📝 CHANGELOG — Registro de cambios del proyecto

> **Registro consolidado de TODOS los cambios significativos del proyecto.**
>
> Sigue el formato [Keep a Changelog](https://keepachangelog.com/) adaptado a este workflow.
>
> **Se actualiza al cierre de cada sprint, fase, o cambio relevante de doc/balance/persistencia.**

---

## 🧭 Cómo usar este CHANGELOG

### Reglas de actualización

1. **Cada sprint completado** → entrada en `[Unreleased]` con SPR-ID.
2. **Cada cierre de fase** → mover entradas de `[Unreleased]` a sección de versión.
3. **Cada cambio de balance** → entrada en sección **Balance**, referenciar BALANCE_FORMULAS.md.
4. **Cada cambio de persistencia** → entrada en sección **Persistence** + bump de Schema Version.
5. **Cada decisión nueva en CONCEPT.md sección 14** → entrada en **Decisions**.

### Categorías por entrada

- **Added**: nuevas features, sistemas, archivos, sprints completados.
- **Changed**: cambios en features existentes, refactors, ajustes.
- **Deprecated**: features/campos marcados para retirada (no eliminados todavía).
- **Removed**: features/archivos eliminados.
- **Fixed**: bugs corregidos.
- **Security**: cambios de seguridad (admin commands, validaciones).
- **Balance**: ajustes de números/curvas/drop rates.
- **Persistence**: cambios de schema persistente. **Siempre con Schema Version bump.**
- **Decisions**: decisiones cerradas nuevas (van también a CONCEPT.md sección 14).
- **Docs**: cambios solo de documentación.

### Convenciones de versionado

- **v0.X**: pre-release, fases F0–F4.
- **v1.0**: primer publish público (cierre F1, MVP playable).
- **v1.X**: features post-MVP (F2, F3, F4).
- **v2.0**: cambio mayor (F5 + segundo mapa con la máquina).
- **Tags Git**: `vX.Y.Z` por release, `day-YYYY-MM-DD` daily, `pre-<descripcion>` antes de cambios delicados.

---

## [Unreleased] — En desarrollo activo

> **Sección donde se acumulan cambios del sprint en curso.**
> **Mover a versión correspondiente al cerrar fase.**

### SPR-211 — Verse syntax audit + drift fix (2026-05-07)

> **Contexto**: durante Build Verse Code post-SPR-007 emergieron 13 lecciones críticas de sintaxis Verse moderna que invalidan partes de docs autoritativos del proyecto. Refactor 5 archivos Verse (Logger, TimeSync, 3 Generated) a patrones canónicos modernos. Auditoría 8 docs.

#### Added
- `docs/VERSE_SYNTAX_GUIDE.md` — fuente única para sintaxis Verse moderna (13 lecciones + 3 patrones canónicos + tabla anti-patrones + tabla error codes).
- `docs/postmortems/PM-SPR-211.md` — postmortem drift acumulado.

#### Changed
- `Content/Verse/Core/Logger.verse` — refactor `class<concrete>` top-level → `module:` namespace (lección 8).
- `Content/Verse/Core/TimeSync.verse` — refactor a `module:` namespace + funciones `<decides>:void=` con condiciones como statements separados (lección 4).
- `Content/Verse/Generated/Companions_Generated.verse` — constantes nombradas `COMPANION_X := companion_def{...}` reemplazadas por funciones getter `GetCompanionX():companion_def= companion_def{...}` (lecciones 11+12).
- `Content/Verse/Generated/Items_Generated.verse` — idem.
- `Content/Verse/Generated/Quests_Generated.verse` — idem.
- `scripts/build/02_export_constants_to_verse.py` — `export_companions/items/quests` emiten Patrón 3 (struct `<public>` + module `<public>` + funciones getter `Get{Singular}{PascalCase}`). Helper `_to_pascal_case` añadido. Header generado incluye nota refactor SPR-211.

#### Fixed
- **D-02 (corregida)** — entry mayo 2026 marcaba sintaxis dotted como inválida y declaraba paths sin `Verse/`. Ambas afirmaciones falsas hoy. Verse moderno acepta `using { Verse.Core.Logger }` (sintaxis dotted relative — VS Code Quick Fix la ofrece). Path canónico real **incluye** `Verse/`: `/lexosi@fortnite.com/RPG_Survival/Verse/Core/Logger`. Ver `VERSE_SYNTAX_GUIDE.md` §1 lección 1+2 + §4.

#### Lecciones (13)
Validadas con build UEFN real. Lista completa en `VERSE_SYNTAX_GUIDE.md` §1. Resumen:
1. `<ProjectName>` es placeholder LITERAL — vErr:S26 si no se sustituye.
2. CHANGELOG D-02 obsoleto (corregido aquí).
3. `return X` no existe en Verse — última expresión = retorno.
4. `<decides>:void=` con condiciones-statement para predicados failable.
5. `var` top-level SOLO `weak_map`.
6. Failable calls usan `[]` no `()`.
7. `<concrete>` + función `<public>` exige tipo expuesto `<public>`.
8. `class<concrete>` top-level + métodos `<decides>` = err 3512.
9. Struct `{...}` literal = archetype constructor (propaga transacts).
10. Args struct usan `:=` con espacios.
11. Structs literal top-level dentro de module → err 3512.
12. Patrón canónico "constantes" generadas = funciones getter.
13. Type definitions expuestas vía module = `<public>`.

#### Notas operativas
- Patrón Singleton `<x>_module := class<concrete>:` documentado en H3.1 (auditoría 3) **es ahora obsoleto para Cores sin state**. Patrón vigente: `Module<public> := module:` (namespace). Caso "Core con state mutable" (PersistenceLayer SPR-008) queda TBD en `VERSE_SYNTAX_GUIDE.md` §2.4 — caso de estudio.
- Build UEFN: 5 archivos compilan limpios tras refactor (validado humano).

### Stress test pre-SPR-074 — Sistema de Milestones (mayo 2026, prueba modular arquitectónica)

> **Contexto**: stress test ejecutado con instancia fresca de Opus 4.7, aplicando protocolo anti-falso-positivo, pidiendo "añadir sistema de milestones (alcanza nivel 50, 1M oro, 10 rebirths)" sin contexto previo de las auditorías ni del histórico del proyecto. **Resultado clave**: la IA fresca dedujo correctamente que NO hay que crear SYS nuevo — el sistema solicitado YA está canonizado como SYS-021 Achievements (CONCEPT §6.3 línea 819: "Permanentes, hitos del juego"). Validación de modularidad arquitectónica: ✅ **aprobada con nota alta** — los conceptos del proyecto están suficientemente definidos para que IAs sin contexto previo lleguen a la misma decisión que un dev del proyecto.

#### Decisiones derivadas del stress test
- **D-A15** (decisión arquitectónica nueva, post-stress test): **añadir evento `EventBus.CurrencyEarned` al catálogo `events_catalog.json`** (SYS-072). Razón: SYS-021 Achievements requiere semántica de **lifetime-earned** ("acumula 1M oro" = lifetime, no current balance), y el catálogo actual solo tiene `CurrencySpent` (cubre quemas). Otros sistemas futuros también lo necesitan (leaderboards `gold_lifetime` ya en JSON_SCHEMAS §47, stats display, BP track de monedas, etc.). Coherente con D-A14 (event-driven puro) + D-A8 (single source of truth — el counter lo mantiene CurrencyManager, no AchievementEngine). Trade-offs descartados: opción B (counter duplicado en AchievementEngine) viola D-A8; opción C (API directa GetLifetimeEarned) rompe pureza event-driven y crea dep compile-time AchievementEngine → CurrencyManager. Implementación: añadir entrada al catálogo en SPR-074 (junto con extensión enum H4) — el EventBus generado por SPR-004 ext incluirá automáticamente el payload. Emisor: CurrencyManager (SYS-029/SYS-030). Suscriptores actuales: AchievementEngine (SPR-075), Leaderboards (SPR-189). Payload propuesto: `{Player:player, Currency:string, Amount:int, Source:string}`.

#### Fixed (drift cleanup post-stress test, hallazgos H1-H3)
- **H1 (drift SYSTEMS_INDEX.md)** — línea 71 columna "Verse principal" para SYS-021 decía `(TBD)`. Realmente está canonizado en `FOLDER_STRUCTURE_TRUTH.md` §3 línea 326 (en árbol oficial de carpetas Verse) como `Systems/LiveOps/AchievementEngine.verse`. Drift de doc — la canonización ocurrió en una auditoría previa pero SYSTEMS_INDEX no se actualizó. Reescrita la celda con el path canónico. Sin este fix, una IA leyendo SYSTEMS_INDEX como source of truth habría inventado un path nuevo o pedido decisión humana innecesaria.
- **H2 (drift SYSTEMS_INDEX.md)** — §4.1 fila `data/progression/achievements.json` marcaba **"Contradicción"** entre CONCEPT §11.1 (`data/quests/`) y §8.2 (`data/progression/`). La contradicción ya estaba resuelta en `FOLDER_STRUCTURE_TRUTH.md` §3 línea 461 a favor de `data/progression/` (canónico). Drift de doc — la resolución se aplicó en FOLDER pero SYSTEMS_INDEX siguió marcándola como activa. Reescrita la celda: removido marcador ⚠️/Contradicción, añadida nota de resolución apuntando al doc canónico.
- **H3 (drift SYSTEMS_INDEX.md)** — línea 71 columna "Sprint" para SYS-021 decía `TBD`. Realmente ya está asignado a SPR-074 (schema), SPR-075 (engine), SPR-076 (UI) en `SPRINTS_BACKLOG.md` §5.4 líneas 221-223. Drift de doc — la asignación se aplicó en SPRINTS_BACKLOG pero SYSTEMS_INDEX no se actualizó. Reescrita la celda con la lista de los 3 sprints.

#### Pendientes para SPR-074 (NO fixeados ahora — son trabajo del sprint)
- **H4 (extensión enum)** — `JSON_SCHEMAS.md` §28 línea 1154 enum `criteria.type` no cubre `currency_threshold` ni `rebirth_count` nativamente. Forzaría a usar `type=custom` con `custom_trigger_key` para los casos canónicos del juego (CONCEPT §14.3 menciona rebirth count como métrica core). Coherencia con `quest.objective.type` (§ línea 861) que ya tiene `spend_gold/spend_gems` nativos. **Decisión**: extensión cabe DENTRO de SPR-074 (la tarea es "schema achievements.json"), no merece SPR propio.
- **H5 (resuelto por D-A15)** — falta evento `CurrencyEarned` en catálogo. Resuelto arquitectónicamente vía D-A15. Implementación práctica entra en SPR-074 (catálogo) + SPR-075 (suscripción).

#### Hallazgos del stress test (validan calidad del proyecto)
- **0 hallazgos inventados** por la IA fresca.
- **0 alucinaciones** de convenciones, decisiones o paths.
- **🟢 10 decisiones documentadas** con cita literal de doc + sección + línea.
- **🟡 3 inferencias justificadas** con razonamiento explícito (1 fue reclasificada a 🟢 al re-verificar literal en JSON_SCHEMAS).
- **🔴 0 bloqueadores genuinos**: todos los huecos son resolubles dentro de los SPR existentes o vía decisión arquitectónica menor (D-A15).
- **5 hallazgos colaterales reales** (H1-H5): 3 fixeados (drift docs), 1 resuelto vía D-A15, 1 trabajo de SPR-074.
- **Caso crítico evitado**: NO crear SYS-073 "Milestones" duplicando SYS-021. Una IA mediocre lo habría hecho. La arquitectura está suficientemente definida para que la respuesta correcta sea inevitable.
- **Veredicto**: arquitectura modular **confirmada con nota alta**. Stress test validó tanto la documentación (auto-suficiente) como la separación de conceptos (SYS-021 ya cubre milestones).

#### Docs (resumen archivos tocados)
- 2 docs autoritativos modificados:
  - `SYSTEMS_INDEX.md` (línea 71 Verse + Sprint, §4.1 fila achievements.json)
  - `CHANGELOG.md` (esta entrada + decisión D-A15)
- Pipeline data→Verse: **sin cambios estructurales** todavía. SPR-074/SPR-004 implementarán D-A15 cuando se ejecuten.
- Schema de persistencia: **sin cambios**.
- **Conclusión**: este stress test fue diferente al pre-SPR-001 — verificó arquitectura conceptual (¿el catálogo de sistemas cubre el caso?) en vez de scaffolding técnico. La métrica clave: la IA fresca llegó autónomamente a "no crear SYS nuevo" = arquitectura modular real. Recomendación: repetir tipo de stress test (añadir feature aleatoria) en cierre de cada fase para detectar deriva conceptual.

---

### Stress test pre-SPR-001 (mayo 2026, prueba modular ejecutiva)

> ⚠️ **Nota retrospectiva**: este stress test fue ejecutado **incorrectamente como sprint real** — se le pidió a la instancia de Opus que *ejecutara* SPR-001 (generando tarball funcional) cuando el plan correcto era solo *validar* la ejecutabilidad de SPR-001 (output textual). El tarball generado **NO se aplicó al repo** y se descartó. La fase de ejecución real de los 206 sprints está reservada para DeepSeek V4 Pro + Aider en conversaciones futuras dedicadas. Sin embargo, **los aprendizajes documentales del stress test SÍ se conservaron y aplicaron** a los docs autoritativos (SPR-001 ampliado, SPR-206 nuevo, etc.) — esos fixes son válidos independientemente de que el código se haya descartado.

> **Contexto**: tras los 5 bloques de auditoría retrospectiva, se ejecutó un stress test con instancia fresca de IA: ejecución completa de SPR-001 sin contexto previo de las auditorías. Aplicado protocolo anti-falso-positivo. La IA completó SPR-001 autónomamente con criterio sano, detectó **4 deudas técnicas reales** que las auditorías no vieron, y entregó tarball funcional. Validación de modularidad arquitectónica: ✅ aprobada.

#### Fixed (post-stress test)
- **SPR-001 columna "Archivos clave" ampliada**: añadidos archivos que estaban en árbol FOLDER pero sin SPR asignado:
  - **`scripts/init_unreal.py`** — declarado en FOLDER §5 + D-A6 ("SPR-001 debe incluir scaffolding de init_unreal.py") pero NO listado en SPR-001. Hueco de planning detectado por la IA en bloqueador B5. Añadido contenido mínimo (prepuebla `actor_sub`/`asset_sub`/`level_sub` siguiendo convención UEFN-TOOLBELT, alineado con CONCEPT §6.3).
  - **`.gitattributes`** — declarado en FOLDER §2 pero sin SPR. Hueco B6. Añadido contenido estándar UEFN+Verse (text=auto eol=lf para fuentes, binary para .umap/.uasset/.png/.jpg/.fbx). Crítico para devs cross-platform Windows/Mac/Linux.
  - **`.gitkeep` en cada carpeta vacía** — convención git estándar, formalizada en SPR-001 (B1 stress test). Excepción `!.gitkeep` añadida al final del `.gitignore` (verbatim §2.2 + esta línea adicional) para que git trackee la estructura.
  - **2 líneas defensa en `00_validate_structure.py`**: skip de `.gitkeep` en chequeos `BAD_NAMING` y `UNDECLARED` (sin esto, los markers `.gitkeep` requeridos romperían el script). Desviación verbatim mínima documentada en SPR-001.
- **Creado SPR-206 "Crear Main.umap inicial vacío en UEFN editor"** en F0 (0.5h). Hueco D3 detectado en stress test: el `.umap` es binario UEFN no creable desde Python/CLI ni orquestador — requiere abrir UEFN editor, File→New Level→Empty Level, Save As. Sprint manual sin código. Necesario para Done F0 (sin .umap, el validador reportaría MISSING al cierre F0). Total sprints proyecto: **205 → 206**. Tiempo estimado: 307h → 307.5h.
- **Done F0 actualizado**: añadido criterio explícito `Content/Maps/Main.umap` debe existir + lista de sprints que corren con `--allow-missing` (SPR-001..SPR-009 + SPR-205 + SPR-206).

#### Verified — no se aplica fix (deudas técnicas no bloqueantes)
- **D1 (parser ruido)** — el parser `parse_truth_paths()` recoge 7 falsos positivos cosméticos (`1.`, `2.`, `seasons/...` placeholders de listas markdown). Ya documentado en Bloque 5 como "verificación residual no bloqueante". Re-confirmado por la IA fresca en su ejecución (reportó 2 ruidos en MISSING). **No fixeado**: bug cosmético sin impacto operativo, fix opcional en sprint dedicado o aprovechando SPR-003 cuando se trabaje el validador de JSONs.
- **D4 (pre-commit hook NO instalado)** — comportamiento esperado y documentado en `FOLDER_STRUCTURE_TRUTH.md` §8.3 + Bloque 5: pre-commit se activa SIN `--allow-missing` al cierre de SPR-010 (Done F0). Durante F0 el hook está desactivado o configurado con flag laxo. Sin cambio.

#### Hallazgos del stress test (validan calidad del proyecto)
- **0 hallazgos inventados** por la IA fresca.
- **0 alucinaciones** de convenciones, decisiones o paths.
- **2 falsos positivos correctamente auto-resueltos** (C1: SPR-001+SPR-003 coherentes; C2: HOWTO_NEW_MAP.md futuro esperado).
- **1 hallazgo menor real** (C3: PROMPT §1 exige 5 docs siempre — para scaffolding puro sobra MODULES; refinar post-F0).
- **4 deudas técnicas reales detectadas** (D1-D4): 1 cosmética + 2 fixeadas como SPR-001 ampliado + 1 nueva (SPR-206) + 1 esperada (D4).
- **Decisiones autónomas razonables**: `.gitkeep` strategy, idioma español autonomo en README raíz (alineado con convención del proyecto), excepción `!.gitkeep` en `.gitignore`, modificación defensiva del validador (2 líneas).
- **Veredicto**: arquitectura modular **confirmada**. Proyecto auto-suficiente para que IAs ejecutoras frescas (DeepSeek u otras) trabajen sprints sin intervención humana excepto en bloqueadores genuinos.

#### Docs (resumen archivos tocados)
- 2 docs autoritativos modificados:
  - `SPRINTS_BACKLOG.md` (SPR-001 Archivos clave ampliados + Done F0 actualizado + nuevo SPR-206 + total 205→206)
  - `CHANGELOG.md` (esta entrada)
- **Conclusión stress test**: el método de auditoría retrospectiva (5 bloques) es **complementario, no sustitutivo**, del stress test ejecutivo. Las auditorías ven inconsistencias dentro de los 22 docs; el stress test ve huecos en cómo aplicar los docs a una tarea real. Recomendación: repetir stress test al cierre de cada fase (F0 done, F1 done, etc.) con un sprint random como prueba.

---

### Auditoría retrospectiva — Bloque 5 (mayo 2026, pre-flight SPR-001 dry-run)

#### Fixed
- **B5.1 (Auditoría retrospectiva — Bloque 5)** — `SPRINTS_BACKLOG.md` línea 64 SPR-001 done criteria ambiguo sobre cuál `README.md` crear. El proyecto tiene **2 README.md**: uno en raíz del repo (apunta a `docs/`, ver `FOLDER_STRUCTURE_TRUTH.md` línea 83) y otro en `docs/` (ya existe — 240 líneas con índice de los 22 docs autoritativos). Sin clarificación, DeepSeek podría sobrescribir el README de docs/ por accidente al ejecutar SPR-001. Reescrita la columna Archivos clave: *"`README.md` **de raíz del repo** (apunta a `docs/` — NO sobrescribir `docs/README.md` que ya existe con 240 líneas)"*. Adicionalmente añadida ref explícita a `EMERGENCY_ROLLBACK.md` §2.2 para el contenido del `.gitignore` (antes implícito) y nota crítica sobre comportamiento del validador (B5.2).
- **B5.2 (Auditoría retrospectiva — Bloque 5)** — añadido flag **`--allow-missing`** al script `scripts/build/00_validate_structure.py` (`FOLDER_STRUCTURE_TRUTH.md` §8.2). Sin el flag, el validador habría fallado por diseño en SPR-001: tras crear solo carpetas + `.gitignore` + `README.md` + el propio script, el parser detecta ~209 `MISSING` (todos los .json/.verse/.py que aún no existen porque los crean SPR-002+). Exit code 1 = ❌ FAIL — bloquearía pre-commit hooks y orquestador desde SPR-001. **Solución**: `--allow-missing` degrada `MISSING` a warning y devuelve exit 0. Documentado en §8.1 (spec funcional) y §8.3 (integración pipeline) que el flag se usa SOLO durante F0 scaffolding (SPR-001..SPR-009) — a partir de SPR-010 el validador corre sin flags y debe pasar limpio. Pre-commit hook se activa SIN `--allow-missing` desde SPR-010. `Done F0` actualizado para reflejar el criterio de exit 0 limpio al cierre de F0.
- **B5.3 (Auditoría retrospectiva — Bloque 5)** — corregido **bug real** en parser `parse_truth_paths()` del script validador (`FOLDER_STRUCTURE_TRUTH.md` §8.2). El parser procesaba **TODOS los bloques `` ``` ``** del `FOLDER_STRUCTURE_TRUTH.md` sin filtrar por lenguaje. El bloque `` ```python `` de §8.2 (el propio script) tiene líneas como `paths.add(full)`, `missing.append(rel)`, `sys.exit(validate(...))` que el parser interpretaba como **paths fantasma** (porque tienen `.`). Verificación: simulación con script viejo reportaba 210 paths con falsos positivos `.append(rel)`, `.add(full)`, `.exit(validate)`. Tras el fix (filtrar fence: solo procesar bloques `` ``` `` desnudos sin lenguaje), simulación reporta 206 paths reales y **0 falsos positivos Python**. El docstring viejo decía *"de §3, §4, §5, §6"* pero el código no cumplía esa restricción — ahora docstring + código alineados. Severidad **alta**: sin el fix, el validador habría reportado missing fantasmas que DeepSeek no podría crear (ej. `/scripts/build/missing.append(rel)` no es un archivo real). Hubiera bloqueado SPR-010 done aunque toda la estructura F0 estuviera bien.

#### Verified — no se aplica fix (3 falsos positivos descartados)
- **B5-FP1** — sospecha "el validador no encuentra `scripts/tools/dependency_cycle_check.py` en SPR-001 (no es parte de F0 scaffolding directo)". Re-verificación: **falso positivo**. SPR-205 está en F0 pero NO es dep de SPR-001 — es script independiente que se materializa cuando SPR-205 se ejecute. Mientras tanto, el validador lo reporta como `MISSING` igual que los otros 209 archivos del árbol que aún no existen. Con `--allow-missing` (B5.2) el flag aplica a TODOS los missing por igual, incluido este. Sin cambio adicional.
- **B5-FP2** — sospecha "el script `00_validate_structure.py` requiere que TODOS los docs/ existan al ejecutarse (no solo TRUTH)". Re-verificación contra línea 521-522 del script: **falso positivo**. El script SOLO lee `docs/FOLDER_STRUCTURE_TRUTH.md` (línea 522: `TRUTH = ROOT / "docs" / "FOLDER_STRUCTURE_TRUTH.md"`). No requiere los otros 21 docs. SPR-001 debe copiar al menos ese archivo a `docs/` (junto con el resto de docs autoritativos por completitud, pero técnicamente solo TRUTH es bloqueante). Sin cambio.
- **B5-FP3** — sospecha "regex `NAMING_RULES['Generated']` rechaza algún archivo válido del Generated/". Re-verificación: probada la regex `^[A-Z][A-Za-z0-9]*_Generated\.verse$|^ModuleRegistryConstants\.verse$|^EventBusConstants\.verse$` contra los 15 archivos del árbol §4: **15/15 matches** (Companions, Items, Prices, Quests, BattlePass, PlayerStats, SkillTree, Achievements, Localization, BalanceCurves, Zones, ThemeConstants, EventPayloads coinciden con el patrón `*_Generated.verse`; ModuleRegistryConstants y EventBusConstants tienen alternativa explícita en la regex). Sin cambio.

#### Verificación residual (no bloqueante)
- El parser fixeado todavía recoge 7 falsos positivos menores tipo `1.`, `2.`, `...` (números de lista markdown y placeholders) — no afectan a la operativa real porque (a) durante F0 se usa `--allow-missing`, (b) en F1+ los paths fantasma `1./2./3.` no causan colisión con archivos reales (no existen como missing relevantes operacionalmente). Bug menor documentado pero no fixeado en este bloque para no introducir cambios fuera de scope.

#### Cross-checks ejecutados
1. **Script Python compila sin errores sintácticos** (verificado con `compile(code, ..., 'exec')` tras el fix).
2. **Parser fixeado: 0 falsos positivos Python** en simulación (antes: 7+ líneas de código Python interpretadas como paths).
3. **Regex `Generated`: 15/15 archivos del árbol §4 matchean** correctamente.
4. **`.gitignore` content**: existe en `EMERGENCY_ROLLBACK.md` §2.2 (verbatim copyable, 12 reglas).
5. **README ambigüedad**: confirmados 2 archivos (raíz + docs/), el de docs/ ya existe con 240 líneas.

#### Docs (resumen archivos tocados)
- 3 docs autoritativos modificados:
  - `FOLDER_STRUCTURE_TRUTH.md` (§8.1 spec añade flag, §8.2 parser fixeado + flag --allow-missing en validate(), §8.3 integración añade nota F0)
  - `SPRINTS_BACKLOG.md` (SPR-001 Archivos clave clarificado + Done F0 añade criterio validador)
  - `CHANGELOG.md` (esta entrada)
- Pipeline data→Verse: **sin cambios estructurales**.
- Schema de persistencia: **sin cambios**.
- **Conclusión Bloque 5**: detectados **3 hallazgos confirmados** + 1 bug **real de código** en el script validador (B5.3 — el más crítico). Sin estos fixes, SPR-001 habría: (1) sobrescrito un README existente, (2) fallado el validador por diseño en exit 1, (3) reportado paths fantasma Python como missing. El proyecto está **listo para arrancar SPR-001** tras aplicar este bloque.

---

### Auditoría retrospectiva — Bloque 4 (mayo 2026, cross-doc references)

#### Fixed
- **B4.1 (Auditoría retrospectiva — Bloque 4)** — `SPRINTS_BACKLOG.md` §10 línea 478 referencia ambigua `§9.2` que NO existe como header en el doc. §9 ("Reglas de mantenimiento") tiene una lista numerada con items 1, 2, 3, 4, 5, 6 — **no sub-secciones markdown**. La ref `§9.2` parecía apuntar a un sub-header inexistente. Reescrita como *"Por regla 2 de §9 (\"Adición\")"* — cita explícita del item de lista + título del item. Aclara que es un item dentro de §9, no un §9.2 independiente.
- **B4.2 (Auditoría retrospectiva — Bloque 4)** — `FOLDER_STRUCTURE_TRUTH.md` líneas 317, 326, 341 (3 ocurrencias) decían *"⭐ NUEVO (faltaba en §11.2)"* sin precisar el doc. **Ambiguo**: §11.2 existe en 2 docs (CONCEPT.md §11.2 = "Layout de carpeta Verse"; MODULES_DEPENDENCY_GRAPH.md §11.2 = "Eventos runtime"). Por contexto (archivos `.verse` que faltaban en el árbol de carpetas) la ref correcta es CONCEPT. Clarificadas las 3 ocurrencias a *"faltaba en `CONCEPT.md` §11.2"*. Sin el fix, DeepSeek o un humano leyendo FOLDER podría asumir que faltaba en MODULES §11.2 (Eventos runtime, no relacionado con archivos Verse).
- **B4.3 (Auditoría retrospectiva — Bloque 4)** — `PERSISTENCE_MAP.md` línea 94 (`SkillPointEntry.SkillID`) tenía comentario *"(id global del skill, ver skill_trees.json §25.2)"* que sugería que `§25.2` era una sub-sección del **JSON file** (lo cual no tiene sentido — los JSONs no tienen secciones markdown). La sección §25.2 vive en `JSON_SCHEMAS.md` ("Schema skill_trees.json"). Reescrito a *"ver schema en `JSON_SCHEMAS.md` §25.2"*. Severidad baja (comentario en código), pero clarifica para el lector.

#### Verified — no se aplica fix (6 falsos positivos descartados con evidencia)
- **B4-FP1** — sospecha "SYS-073 y SYS-074 referenciados pero no declarados en SYSTEMS_INDEX (2 IDs huérfanos)". Re-verificación contra `SYSTEMS_INDEX.md` §289: **falso positivo**. Ambos IDs aparecen únicamente como **ejemplos hipotéticos** en la regla *"Adición de sistemas: nuevos sistemas reciben el siguiente ID libre (`SYS-073`, `SYS-074`…), nunca rellenan huecos."*. No son referencias a sistemas reales. Sin cambio.
- **B4-FP2** — sospecha "archivos `ARCHITECTURE.md` y `SPRINTS.md` referenciados pero no existen". Re-verificación contra `CHANGELOG.md` §583/§595/§608 + `CONCEPT.md` §996/§998: **falso positivo**. Ambos archivos eran "fantasma" históricos del planning original — ya fueron eliminados en una auditoría previa (S12 según CHANGELOG) y todas las referencias actuales son **explícitamente didácticas** (notas que dicen *"sustituye al fantasma `ARCHITECTURE.md`"*). El histórico se mantiene en CHANGELOG. Sin cambio.
- **B4-FP3** — sospecha "archivo `SCREAMING_SNAKE.md` referenciado pero no existe". Re-verificación contra `FOLDER_STRUCTURE_TRUTH.md` §35 + §449: **falso positivo**. SCREAMING_SNAKE no es un archivo — es la **convención de naming** (`SCREAMING_SNAKE_CASE`) usada para nombrar markdown files del proyecto (todos en mayúsculas con guion bajo, ej. `CONCEPT.md`, `PERSISTENCE_MAP.md`). Los backticks lo envuelven sintácticamente como si fuera archivo, pero el contexto deja claro que es naming style. Sin cambio.
- **B4-FP4** — sospecha "archivo `DECISIONS_LOG.md` referenciado pero no existe". Re-verificación contra `SYSTEMS_INDEX.md` §296: **falso positivo**. La ref está marcada explícitamente con disclaimer *"y nota en `DECISIONS_LOG.md` (cuando exista)"*. Es un placeholder para futuro. Sin cambio.
- **B4-FP5** — sospecha "varias refs `§X.Y` cross-doc apuntan a headers que no existen". Re-verificación con script Python parseando los 22 docs y comparando refs vs headers reales: **0 refs cross-doc huérfanas detectadas**. Las 7 refs marcadas inicialmente como huérfanas por mi script eran falsos positivos del regex (headers `§10`, `§9`, `§14`, `§2`, `§3` standalone sin sub-numeración existen y son válidos). Sin cambio.
- **B4-FP6** — sospecha "PROMPT.md §15 y §16 referencian secciones que no existen". Re-verificación: **falso positivo**. PROMPT.md menciona "*§15 Convenciones técnicas*" y "*§16 Glosario*" en una **lista de secciones de CONCEPT.md** dentro de la sección *"Lee primero `CONCEPT.md` §14"*. Los headers existen en CONCEPT (líneas 1480 §15, 1521 §16). El doc precedente queda implícito en el contexto del párrafo. Posible mejora estilística (poner el nombre del doc en cada bullet) pero no error funcional. Sin cambio.

#### Cross-checks ejecutados
1. **205 SPRs declarados en `SPRINTS_BACKLOG.md` ↔ 205 SPRs referenciados en docs**: 1:1 perfecto, 0 huérfanos, 0 huérfanas.
2. **72 SYSs declarados en `SYSTEMS_INDEX.md` ↔ 72 SYSs reales referenciados** (descartados los 2 ejemplos hipotéticos).
3. **22 archivos `.md` referenciados ↔ existen en disco**: 100% (descartados los 4 falsos positivos arriba).
4. **Refs `archivo.md §X.Y` → headers reales**: 0 huérfanas tras filtro de falsos positivos del regex.
5. **Refs internas `§X.Y` → headers del propio doc**: 1 hallazgo (B4.1), resto verified como cross-doc legítimos.

#### Docs (resumen archivos tocados)
- 4 docs autoritativos modificados:
  - `SPRINTS_BACKLOG.md` (§10 línea 478)
  - `FOLDER_STRUCTURE_TRUTH.md` (líneas 317, 326, 341 — 3 ocurrencias)
  - `PERSISTENCE_MAP.md` (línea 94 comentario SkillID)
  - `CHANGELOG.md` (esta entrada)
- Pipeline data→Verse: **sin cambios**.
- Schema de persistencia: **sin cambios**.
- **Conclusión Bloque 4**: detectados 3 hallazgos confirmados de **ambigüedad documental** (refs sin doc explícito o atribución a item inexistente). Severidad media-baja — ningún hallazgo bloquearía compilación, pero todos pueden generar confusión a DeepSeek u otro lector que intente seguir las referencias literalmente. 6 falsos positivos descartados con evidencia. Cross-doc references al 100% coherentes tras los fixes.

---

### Auditoría retrospectiva — Bloque 3 (mayo 2026, estructura de carpetas, pipelines y DevOps)

#### Fixed
- **B3.1 (Auditoría retrospectiva — Bloque 3)** — `dependency_cycle_check.py` formalizado en `FOLDER_STRUCTURE_TRUTH.md` §5 árbol oficial de scripts. Estaba especificado con código completo (~80 líneas) en `MODULES_DEPENDENCY_GRAPH.md` §10.3, declarado en path `scripts/tools/dependency_cycle_check.py`, mencionado como "validador" en `CHANGELOG.md` Added (auditoría regresión bloque 1) y en `MODULES_DEPENDENCY_GRAPH.md` §1.4, pero **NO aparecía en el árbol oficial** ni tenía SPR asignado. Era un script "fantasma" — todos asumían que existía pero nadie lo iba a construir. Añadida entrada en árbol con cross-ref a SPR-205 + MODULES §10.3. Conteo de scripts en cierre §9 actualizado: **15 → 16** (1 init + 8 build + **5** tools + 2 utils). Afirmación de cierre H3.8 recalibrada para reflejar Auditoría retrospectiva.
- **B3.2 (Auditoría retrospectiva — Bloque 3)** — `SPRINTS_BACKLOG.md` línea 399 SPR-171 "Asset variants por season" tenía la columna **Archivos clave incorrecta**: declaraba `scripts/tools/new_map_scaffolder.py`, que es el script de SPR-199 ("Scaffolder Python — clone para nuevo mapa") con propósito completamente diferente (clonar el proyecto entero a un mapa nuevo). Un script no puede ser scaffolder de mapa nuevo Y al mismo tiempo asset variants por season. Reescrita columna: el trabajo pertenece a `scripts/build/05_apply_theme_pack.py` extendido con función `apply_seasonal_asset_variants()`, sin crear script nuevo + convención de carpetas `Content/Assets/<theme>_<season>/`. Coherente con la dep declarada (SPR-170 que es dueño de `05_apply_theme_pack.py`).
- **B3.3 (Auditoría retrospectiva — Bloque 3)** — creado **SPR-205** "Validador de ciclos de dependencias Verse" en F0. Formaliza el script `dependency_cycle_check.py` que estaba huérfano (B3.1). Spec ya escrita en `MODULES_DEPENDENCY_GRAPH.md` §10.3 (~80 líneas Python) — el sprint solo necesita copiar verbatim + integrar como pre-commit hook. NO entra en orquestador `07_run_full_pipeline.py` porque es validador estructural transversal, no parte del pipeline data→verse. Total sprints proyecto: **204 → 205**. Tiempo estimado total: 306 h → 307 h (+1 h). Documentado el motivo del split en columna `Motivo` de la tabla §10.
- **B3.4 (Auditoría retrospectiva — Bloque 3)** — `SPRINTS_BACKLOG.md` línea 67 SPR-004 "Python exporter constantes Verse" tenía la columna **Archivos clave incompleta + incorrecta**:
  - Decía: *"genera `Generated/{Companions,Items,Prices,Quests,ThemeConstants}_Generated.verse` + `ModuleRegistryConstants.verse` + `EventBusConstants.verse` + `EventPayloads_Generated.verse`"* — total 7 archivos.
  - **Realidad según `BOOTSTRAP_PIPELINE.md` §4.3 tabla atribución + `FOLDER_STRUCTURE_TRUTH.md` §4 árbol Generated/**: SPR-004 (`02_export_constants_to_verse.py`) genera **12 archivos**, no 7. Faltaban 5 (`BattlePass_Generated`, `PlayerStats_Generated`, `SkillTree_Generated`, `Achievements_Generated`, `Localization_Generated`).
  - Adicionalmente, `ThemeConstants_Generated.verse` lo genera `05_apply_theme_pack.py` (= SPR-170), **NO** `02_export_constants_to_verse.py` (= SPR-004) — atribución incorrecta confirmada contra BOOTSTRAP §333.
  - Reescrita la columna con los 12 archivos correctos + notas explícitas sobre los 3 archivos que NO genera SPR-004 (`ThemeConstants_Generated` → SPR-170, `Zones_Generated` → SPR-041, `BalanceCurves_Generated` → SPR-204 en F1 y SPR-134 extendido en F3).
  - Sin el fix, SPR-004 habría implementado solo 6 funciones de export y habrían faltado 5 → cascada de fallos compile-time en SPR-011+ (PlayerStats, BP, achievements, etc. no podrían importar sus constantes).

#### Verified — no se aplica fix (4 falsos positivos descartados)
- **B3-FP1** — sospecha "scripts `02a_export_companions.py` y `02b_export_items.py` referenciados en BOOTSTRAP pero no en árbol". Re-verificación contra `BOOTSTRAP_PIPELINE.md` §4.2 línea 315: **falso positivo**. Esos nombres aparecen únicamente en una nota hipotética *"Cuándo refactorizar a múltiples scripts: si en F4–F5 el export tarda >30 s consistentemente, dividir en `02a_export_companions.py`, `02b_export_items.py`, etc."* — son ejemplos de un futuro split contingente, NO scripts declarados que existan. Sin cambio.
- **B3-FP2** — sospecha "el orquestador `07_run_full_pipeline.py` no incluye `dependency_cycle_check.py`". Re-verificación: **falso positivo intencional**. El orquestador ejecuta el pipeline `data → JSON → Verse` (steps 0-6 son validate_structure → validate_jsons → export → procedural → theme → memory). `dependency_cycle_check.py` valida estructura `.verse` (using {} cross-imports), que es ortogonal al pipeline data→verse. Pertenece al pre-commit hook + CI lateral, no al orquestador. Documentado en SPR-205 done criteria. Sin cambio en orquestador.
- **B3-FP3** — sospecha "los 15 archivos `Generated/` de `FOLDER_STRUCTURE_TRUTH.md` §4 no coinciden con los 15 declarados en `BOOTSTRAP_PIPELINE.md` §4.3". Re-verificación con grep + diff: **coinciden 1:1** los 15 nombres entre los 2 docs (Achievements, BalanceCurves, BattlePass, Companions, EventBusConstants, EventPayloads, Items, Localization, ModuleRegistryConstants, PlayerStats, Prices, Quests, SkillTree, ThemeConstants, Zones). Sin cambio.
- **B3-FP4** — sospecha "paths `data/economy/{gold,gems,pity_config}.json` referenciados en BOOTSTRAP §322 no existen en árbol". Re-verificación contra `FOLDER_STRUCTURE_TRUTH.md` §3 árbol data/economy/: **los 4 paths existen** (shop.json, gold.json, gems.json, pity_config.json). Adicionalmente, `SPRINTS_BACKLOG.md` declara los SPRs que los crean (SPR-084 para gold/gems, SPR-106 para pity_config). Sin cambio.

#### Docs (resumen archivos tocados)
- 3 docs autoritativos modificados:
  - `FOLDER_STRUCTURE_TRUTH.md` (§5 árbol scripts/tools/ + §9 cierre conteo 15→16)
  - `SPRINTS_BACKLOG.md` (SPR-004 Archivos clave + SPR-171 Archivos clave + nuevo SPR-205 + total 204→205)
  - `CHANGELOG.md` (esta entrada)
- Pipeline data→Verse: **sin cambios estructurales** (los 15 artifacts Generated/ y la atribución por script siguen siendo los mismos — los fixes corrigen las **descripciones** en SPRINTS_BACKLOG, no la realidad del pipeline en BOOTSTRAP).
- Schema de persistencia: **sin cambios**.
- **Conclusión Bloque 3**: detectados 4 hallazgos confirmados de **inconsistencias entre el plan de sprints (SPRINTS_BACKLOG) y la realidad técnica del pipeline (BOOTSTRAP + FOLDER_STRUCTURE)**. Sin estas correcciones, SPR-004 habría implementado un exporter incompleto, SPR-171 habría modificado el script equivocado, y SPR-205 (validador crítico de ciclos de deps) **no se habría ejecutado nunca** porque no tenía SPR asignado. Tras los fixes, el plan de sprints está 100% alineado con el pipeline real.

---

### Auditoría retrospectiva — Bloque 2 (mayo 2026, tipos de persistencia y datos)

#### Análisis de Impacto post-B2.1 (control de daños)

Tras corregir la sintaxis `weak_map[player]struct<persistable>` → `weak_map(player, T)` con clase persistable, se hizo un escaneo cruzado en TODAS las plantillas de código de auditorías 1, 2, 3 + protocolo de tests + plantillas de prompt + cápsula DeepSeek + JSONs schemas. Hallazgos:

#### Fixed (post-B2.1)
- **B2.2 (Análisis de Impacto B2.1)** — `TESTING_PROTOCOL.md` §6.1 plantilla `test_persistence_SPR008` reescrita completa. Tres errores acumulados detectados:
  1. **Violación D-A7**: `@editable Persistence:persistence_layer = persistence_layer{}` inyectaba el Core como dependencia editable, contradiciendo la decisión de que los 6 Core son singletons top-level accedidos por `using {}` directo (cerrado en H1.1 para las plantillas §2.1/§2.2/§2.3 pero olvidado en §6.1).
  2. **Funciones inexistentes**: las llamadas `Persistence.SetGold(Agent, ...)`, `Persistence.SetGems(Agent, ...)`, `Persistence.SetLevel(Agent, ...)`, `Persistence.GetGold(Agent)` etc. **NO EXISTEN** en `API_REFERENCE_GENERATED.md` §3.4. Las APIs reales son `LoadPlayerCore(InPlayer:player)<transacts>:PlayerCore` + `SavePlayerCore(InPlayer:player, Data:PlayerCore)<transacts>:void` — no hay setters/getters granulares por campo, se carga el struct completo, se modifica el campo, se guarda completo.
  3. **Falta cast `agent → player`**: los botones (`InteractedWithEvent`) emiten `agent`, pero `weak_map` necesita `player` como key. La plantilla vieja pasaba `agent` directo a las funciones inventadas, ocultando el problema. Reescrito con `if (P := player[Agent]):` (patrón canónico oficial Epic confirmado por: [romeroblueprints — UEFN Verse: Introduction to Persistence](https://romeroblueprints.blogspot.com/2026/02/uefn-verse-introduction-to-persistence.html), confirmado en X/Twitter por testers Epic). El cast es failable (`<decides>`).
  Plantilla nueva: importa `Logger` + `PersistenceLayer` por `using {}` directo, castea agent→player con `if (P := player[Agent]):`, llama a `Persistence.LoadPlayerCore(P)` → modifica struct → `Persistence.SavePlayerCore(P, Core)`. Coherente con D-A7 + APIs reales del proyecto.
- **B2.3 (Análisis de Impacto B2.1)** — `SPRINTS_BACKLOG.md` línea 75 (Done F0) corregida residual de B1.1: *"admin panel responde solo a player ID configurado"* → *"admin panel solo visible si `AdminCommands.IsAdmin(Agent)` devuelve true (mecanismo `player_reference_device` configurado en editor — D-A13, no `player.GetID()` que no existe en Verse)"*. Era el último residuo del patrón viejo `player.GetID() == ADMIN_ID_HARDCODED` que se escapó de B1.1.

#### Verified — no se aplica fix (4 falsos positivos descartados)
- **B2-IMP-FP1** — sospecha "ocurrencias de `weak_map[player]...` con corchetes en otros docs". Re-verificación con `grep -rn 'weak_map\['` en los 22 docs: solo 2 ocurrencias, **ambas didácticas explícitas** (CHANGELOG B2.1 narrando el bug, CONCEPT §7.2 línea 445 con la advertencia "NO usar `weak_map[K]V`"). **0 ocurrencias del patrón en código real, ejemplos, o plantillas**. Sin cambio.
- **B2-IMP-FP2** — sospecha "PERSISTENCE_MAP §10.1 ejemplo `PlayerCore_Map[InPlayer]?` usa corchetes incorrectos". Re-verificación: **falso positivo**. La sintaxis distingue (a) DECLARAR tipo: `weak_map(K, V)` con paréntesis, (b) ACCEDER valor: `MapVar[Key]` con corchetes (subscript operator, igual que `map`). Confirmado oficial Epic v25.20: *"X := if (Y := GlobalInt[GetSession()]) then Y + 1 else 0"* ([Patch Notes for Creative, UEFN v25.20](https://fortnitenews.com/patch-notes-for-creative-uefn-v25-20/)). Acceso `PlayerCore_Map[InPlayer]?` es **correcto**. Sin cambio.
- **B2-IMP-FP3** — sospecha "alguna declaración de tipo `:weak_map(...)` con error sintáctico". Re-verificación con grep `weak_map\(`: **8 ocurrencias totales en el proyecto**, todas correctas:
  - `API_REFERENCE_GENERATED.md` × 4: `var <Name>_Map:weak_map(player, <T>) = map{}` para cada uno de los 4 buckets.
  - `CONCEPT.md` × 1: patrón canónico documentado (post-fix B2.1).
  - `CHANGELOG.md` × 3: citas explicativas con sintaxis correcta.
  Sin cambio. La auditoría 1 (sintaxis Verse) y auditoría 3 (consistencia) tenían cero menciones de tipo declaration, solo prosa narrativa que usa "weak_map" como concepto.
- **B2-IMP-FP4** — sospecha "DEEPSEEK_CAPSULE.md o PROMPT_TEMPLATES.md tienen ejemplos sintácticos incorrectos para guiar a la IA ejecutora". Re-verificación con grep: **0 ejemplos de código** con declaración weak_map en estos archivos. Solo prosa narrativa "4 weak_maps × 128 KB". Sin cambio.

#### Docs (resumen archivos tocados)
- 3 docs autoritativos modificados:
  - `TESTING_PROTOCOL.md` (§6.1 plantilla `test_persistence_SPR008` reescrita)
  - `SPRINTS_BACKLOG.md` (línea 75 Done F0)
  - `CHANGELOG.md` (esta entrada)
- Schema de persistencia: **sin cambios**.
- **Conclusión Análisis de Impacto B2.1**: el fix B2.1 reveló 2 hallazgos colaterales (B2.2 + B2.3) que no eran de sintaxis weak_map sino derivados — un test que llamaba a APIs inventadas (B2.2) y un residuo B1.1 que se escapó (B2.3). Sin estas correcciones, SPR-008-T habría fallado compilación garantizada y el done de F0 habría sido ambiguo. Verificado contra docs oficiales Epic en cada paso del análisis.

---

#### Fixed
- **B2.1 (Auditoría retrospectiva — Bloque 2)** — corregida sintaxis incorrecta `weak_map[player]struct<persistable>` en `CONCEPT.md` §7.2 línea 445. La sintaxis canónica oficial Epic es `weak_map(K, V)` con paréntesis y coma ([Constants and Variables in Verse](https://dev.epicgames.com/documentation/en-us/fortnite/constants-and-variables-in-verse): *"var MySavedPlayerData:weak_map(player, int) = map{}"*) — `weak_map[K]V` con corchetes es sintaxis de `map`, NO de `weak_map`. Adicionalmente, la nota decía "struct<persistable>" cuando en este proyecto los 4 buckets root son `class<final><persistable>` (los structs solo se usan para entries internas — H2.1 ya documentó esa distinción). Reescrito el bullet completo con sintaxis correcta + clarificación sobre qué tipos están permitidos como `<V>` (class persistable, struct persistable, primitivos) + cross-ref a PERSISTENCE_MAP §3 y API_REFERENCE §3.4. Severidad baja (prosa explicativa, no código ejecutable), pero clarifica para DeepSeek u otra IA ejecutora que pudiera copiar el patrón al implementar SPR-008.

#### Verified — no se aplica fix (8 falsos positivos descartados con evidencia oficial)
- **B2-FP1** — sospecha "alguno de los 4 buckets root usa tipos no persistibles". Re-verificación contra dump completo de PERSISTENCE_MAP §3-§6: los tipos usados son `int`, `string`, `logic`, `[]int`, `[]<struct<persistable>>` × 9 entry types. **TODOS persistibles oficialmente** según docs Epic:
  - `int` ([dev.epicgames.com — Int in Verse](https://dev.epicgames.com/documentation/en-us/fortnite/int-in-verse): *"Integer values are persistable"*)
  - `string` ([dev.epicgames.com — String in Verse](https://dev.epicgames.com/documentation/en-us/fortnite/string-in-verse): *"String, char, and char32 values are all persistable"*)
  - `logic` ([dev.epicgames.com — Logic in Verse](https://dev.epicgames.com/documentation/en-us/fortnite/logic-in-verse): *"Logic values are persistable"*)
  - Arrays de tipos persistibles → automáticamente persistibles. Sin cambio.
- **B2-FP2** — sospecha "los 4 buckets root tienen `var` infiltrados (prohibido por regla 'Does not have variable members')". Re-verificación con grep `var ` dentro de cada bloque `class<final><persistable>` o `struct<persistable>`: **0 ocurrencias**. Las 4 clases root y las 9 structs entry usan exclusivamente declaraciones `Field:type = default` sin `var`. La regla oficial Epic ([Class in Verse](https://dev.epicgames.com/documentation/en-us/fortnite/class-in-verse): *"Only contains members that are also persistable. Does not have variable members."*) se respeta al 100%. Sin cambio.
- **B2-FP3** — sospecha "campos persistables sin default value provocan fallo de archetype construction `<X>{}`". Re-verificación parseando los 4 buckets + 9 entries con script Python: **TODOS los campos tienen default value explícito**. El patrón `LoadPlayerCore` usa `var Core:PlayerCore = PlayerCore{}` (PERSISTENCE_MAP §10.1) → requiere defaults para todos los campos del archetype, requisito cumplido. Sin cambio.
- **B2-FP4** — sospecha "los 4 buckets root no llevan `<final>` (specifier obligatorio para clases persistables)". Re-verificación contra H2.1 (Auditoría regresión bloque 2): **ya cerrado**. Las 7 ocurrencias (4 root + 3 ejemplos en §8) llevan `<final>` desde H2.1. Patrón canónico oficial Epic `class<final><persistable>:` aplicado. Sin cambio.
- **B2-FP5** — sospecha "métodos definidos dentro de clases/structs persistables (potencial restricción)". Re-verificación con grep buscando `Func(.*).*=` dentro de bloques persistables: **0 métodos**. Las 4 clases root y las 9 structs son contenedores de datos puros — todas las operaciones (Load/Save/validación) están en el módulo `PersistenceLayer` por funciones libres que reciben/devuelven la struct. Patrón coherente con el ejemplo oficial Epic `player_profile_data` (que tampoco define métodos). Sin cambio.
- **B2-FP6** — sospecha "alguna entry interna sin `<persistable>` rompe la cadena (la regla 'Only contains members that are also persistable' es transitiva)". Re-verificación: las 9 entries (`SkillPointEntry`, `ItemEntry`, `CompanionEntry`, `DexEntry`, `EquippedItem`, `QuestProgress`, `BaseUpgradeEntry`, `PityCounter`, `ActiveCraft`) **TODAS llevan `struct<persistable>:`** explícitamente. Cero rupturas de la cadena de persistabilidad. Sin cambio.
- **B2-FP7** — sospecha "el límite de 2 weak_maps por isla está superado (proyecto declara 4)". Re-verificación contra anuncio oficial Epic ([forums.unrealengine.com — Limit On Number of Verse Persistent weak_maps Increased](https://forums.unrealengine.com/t/limit-on-number-of-verse-persistent-weak-maps-increased/2635179), agosto 2025): *"The limit on persistent weak_maps per island has been increased from 2 to 4."*. El proyecto usa **exactamente 4** (PlayerCore, PlayerInventory, PlayerProgress, PlayerEconomy) → aprovecha el límite máximo permitido. Cumple regla. Sin cambio.
- **B2-FP8** — sospecha "tamaño de algún bucket excede los 128 KB de Epic". Re-verificación contra PERSISTENCE_MAP §7.1 worst-case consolidado:
  - PlayerCore worst: 1.05 KB (0.80% de 128 KB)
  - PlayerInventory worst: 10.2 KB (7.9% de 128 KB) — el más pesado
  - PlayerProgress worst: 1.78 KB (1.4% de 128 KB)
  - PlayerEconomy worst: 1 KB (0.7% de 128 KB)
  Total worst: ~14 KB de los 512 KB disponibles (4 buckets × 128 KB). **2.7% usado.** Margen >97% en todos los buckets. Sin riesgo de superar cap. Sin cambio.

#### Docs (resumen archivos tocados)
- 2 docs autoritativos modificados:
  - `CONCEPT.md` (§7.2 línea 445 — sintaxis weak_map corregida)
  - `CHANGELOG.md` (esta entrada)
- Schema de persistencia: **sin cambios** (alineado al 100% con requisitos oficiales Epic 2026 — confirmado por 8 verificaciones cruzadas).
- **Conclusión Bloque 2**: la capa de persistencia del proyecto está alineada con la realidad de la API UEFN al 100%. Cero alucinaciones de tipos detectadas en estructuras `class<final><persistable>` ni `struct<persistable>`. La nota incorrecta en CONCEPT §7.2 era prosa documental obsoleta de iteraciones tempranas, antes de que H2.1 formalizara la distinción class vs struct y el patrón canónico Epic. Cero impacto en código ejecutable.

---

### Auditoría retrospectiva — Bloque 1 (mayo 2026, sanity check pre-Sprint 1)

#### Fixed
- **B1.2 (Auditoría retrospectiva — Bloque 1, control de daños)** — eliminado el campo `PlayerID:int` de **TODOS los payloads del EventBus** (9 eventos del catálogo) y reemplazado por `Player:player`. Cascada lógica del fix B1.1: si `player.GetID()` no existe en la API Verse, ningún emisor puede poblar un campo `int` identificador. Detectado en análisis de impacto post-B1.1. Sin el fix, los 9 eventos habrían sido **inutilizables en runtime**: `EventBus.LevelUp.Signal`, `PlayerStatsChanged`, `InventoryChanged`, `CurrencySpent`, `CompanionAcquired`, `QuestCompleted`, `RebirthDone`, `ZoneUnlocked`, `BossDefeated` (= ~80% de los handlers cross-system del proyecto, todos los Achievement, BattlePass, HUD, Notif, Quest progress).
  - **Beneficio colateral**: `Player:player` es key directa del `weak_map` de persistencia → suscriptores hacen `Persistence.LoadPlayerCore(Payload.Player)` sin lookup intermedio. Type-safety mejorada (imposible enviar int random como ID).
  - `MODULES_DEPENDENCY_GRAPH.md` §11.2 — los 9 payloads de la tabla reescritos con `{Player, ...}` en lugar de `{PlayerID, ...}`. Añadida nota canónica B1.2 al inicio referenciando D-A14.
  - `JSON_SCHEMAS.md` §42.1 — los 2 ejemplos del catálogo (`player_stats_changed`, `level_up`) reescritos con `{"name": "Player", "type": "player"}`. §42.2 — añadida regla canónica del proyecto prohibiendo `PlayerID:int`. §42.3 — añadida validación cruzada #8 (validador rechaza payloads con `name == "PlayerID"`, mensaje de error explícito apuntando a docs).
  - `BOOTSTRAP_PIPELINE.md` §11.3 — ejemplo del catalog reescrito. §11.4 — los 2 structs ejemplares (`level_up_payload`, `player_stats_changed_payload`) reescritos con `Player<public>:player` (sin default literal — Verse no permite default para tipos no-construibles vacíos; el transformer Python en §11.6 ya gestiona el caso correctamente porque `DEFAULT_MAP` omite `player`/`agent`). §11.7 — emisor + handler ejemplares reescritos. §6.3 — el `GiveReward(PlayerID, ...)` también unificado a `GiveReward(Player, ...)` por consistencia documental.
  - `API_REFERENCE_GENERATED.md` §3.5 — bloque "Métodos disponibles en cada `event(t)`" reescrito (Signal/Subscribe/Await ejemplares). §3.2 ejemplo Logger ajustado.
  - `TESTING_PROTOCOL.md` §2.3 — `test_device_SPR011` reescrito al patrón canónico `Self.GetPlayspace().GetPlayers()[0]` para obtener el jugador real. Eliminado el placeholder ambiguo `player_test_id`. §2.5 perf test (`test_device_SPR050`) ajustado al mismo patrón.
- **B1.1 (Auditoría retrospectiva — Bloque 1)** — eliminado el patrón inválido `player.GetID()` en 3 docs (5 ocurrencias) + ajustada la firma del API. La API Verse de `player` **no expone** `GetID()`, `GetName()` ni `GetAccountID()` — único método público documentado: `IsActive[]`. Fuente oficial: [dev.epicgames.com — verse-api/versedotorg/simulation/player](https://dev.epicgames.com/documentation/en-us/fortnite/verse-api/versedotorg/simulation/player) + feature request abierta y no implementada desde nov 2023 ([forums.unrealengine.com — Get player name in Verse](https://forums.unrealengine.com/t/feature-request-get-player-name-in-verse/1378109)). Sin el fix, SPR-010 (Admin Commands) habría fallado compilación garantizada.
  - `CONCEPT.md` §5.4 tabla "Lo que sí se puede pero con trampas" → fila Admin commands reescrita: `player_reference_device` + `IsRegistered[Agent]`.
  - `CONCEPT.md` §13.3 SPR-010 done criteria expandido de 4 a 6 bullets: añadidos `@editable AdminRefs:[]player_reference_device = array{}` en `AdminPanel.verse` + función `IsAdmin(Agent:agent):logic` que itera refs. Notas renombradas a "C1 + Auditoría retro Bloque 1".
  - `GLOSSARY.md` entrada "Admin (player ID)" reescrita con la fuente oficial + descripción del mecanismo `player_reference_device` + nota explícita de que `data/admin/admin_config.json` deja de almacenar IDs.
  - `JSON_SCHEMAS.md` §37 `admin_commands.json`: campo `admin_player_ids: []string [REQUIRED]` **eliminado** del schema. Validación 37.2 `admin_player_ids no vacío en producción` eliminada y sustituida por chequeo opcional cruzado contra dump del level UEFN buscando al menos un `player_reference_device` con tag `admin`. Nota canónica añadida arriba de §37.1.
  - `API_REFERENCE_GENERATED.md` §3.7 AdminCommands: firma `IsAdmin(InPlayer:player):logic` cambiada a `IsAdmin(Agent:agent):logic` (el caller no necesita castear desde `agent` → `player`). Añadida `Init(Refs:[]player_reference_device):void` (inyección desde `AdminPanel`). `ExecuteCommand` también pasa de `player` a `agent`. Añadida sección "Funciones que NO existen" con tachado del patrón viejo.

#### Decisions
- **D-A14 (Auditoría retrospectiva — Bloque 1, B1.2)**: campo identificador del jugador en payloads del EventBus es **siempre** `Player:player` (tipo nativo Verse), nunca `PlayerID:int`. Razón: la API Verse pública de `player` no expone `GetID()`/`GetName()`/`GetAccountID()` — los emisores no pueden poblar un int identificador. Bonus: `player` es la key directa del `weak_map` de persistencia, los suscriptores hacen lookup directo sin paso intermedio. Validador `01_validate_jsons.py` rechaza el patrón viejo (regla §42.3 #8). Aplica también a logs y tests: usar `Self.GetPlayspace().GetPlayers()` para obtener `player` reales en runtime.
- **D-A13 (Auditoría retrospectiva — Bloque 1)**: identificación de admin se realiza por uno o varios `player_reference_device` configurados en editor UEFN con las cuentas autorizadas. `AdminPanel.verse` los expone como `@editable AdminRefs:[]player_reference_device = array{}` y los inyecta a `AdminCommands` vía `Init(Refs)`. El check runtime es `for (Ref:AdminRefs) { if (Ref.IsRegistered[Agent]) { return true } }`. Razón: la API Verse pública de `player` no expone identidad estable (`GetID`/`GetName`/`GetAccountID` no documentados, no implementados — confirmado contra docs oficiales Epic + feature request abierta desde nov 2023). Patrón canónico oficial Epic para identificar jugadores específicos en runtime es `player_reference_device`.

#### Verified — no se aplica fix
- **B1-FP4 (control de daños)** — sospecha "los `weak_map(player, T)` de persistencia podrían también requerir cambio". Re-verificación contra `PERSISTENCE_MAP.md` §3.1/§4.1/§5.1/§6.1 + `API_REFERENCE_GENERATED.md` §3.4: **falso positivo**. Los 4 `weak_map` ya usan `player` como key (tipo nativo Verse) — la firma canónica oficial Epic es `var <Name>:weak_map(player, <T>) = map{}` ([Constants and Variables in Verse](https://dev.epicgames.com/documentation/en-us/fortnite/constants-and-variables-in-verse)). Las 12 funciones públicas (`LoadPlayerCore(InPlayer:player)`, `SavePlayerCore(InPlayer:player, Data)`, etc.) ya toman `player` como parámetro. Cero impacto de B1.1/B1.2 en la capa de persistencia. La persistencia estaba alineada con la realidad de la API desde el inicio.
- **B1-FP5 (control de daños)** — sospecha "comandos admin que reciben target player podrían usar int identificador". Re-verificación: los comandos admin se ejecutan dentro de Verse runtime con referencias `player`/`agent` reales (botón presionado por jugador → recibe agent del evento; targeteado vía `player_reference_device` configurado en editor). En ningún punto del flujo admin se necesita un `int` ID. Funciones tipo `AdminCommand.GiveGold(Target:agent, Amount:int)` toman `agent`, no int. Sin cambio.
- **B1-FP1** — sospecha "uso incorrecto de `GetSimulationElapsedTime()` en firmas/contextos prohibidos". Re-verificación contra D-01 + grep en los 22 docs: **0 usos incorrectos** tras D-01. Todas las ocurrencias actuales están bajo `OnBegin<override>()<suspends>:void` u otros contextos válidos del namespace `/Verse.org/Simulation`. Sin cambio.
- **B1-FP2** — sospecha "herencia múltiple prohibida usada en algún sitio". Re-verificación contra MODULES_DEPENDENCY_GRAPH §2.1 + grep `class\(.*,.*\)`: **0 violaciones**. Solo se usa 1 superclase (`creative_device`) + N interfaces, que es lo que la spec Verse permite ([Class in Verse](https://dev.epicgames.com/documentation/en-us/fortnite/class-in-verse)). Sin cambio.
- **B1-FP3** — sospecha "inicializadores de archetype `<modulo>_module{}` sin `<concrete>`". Re-verificación contra H3.1 (Auditoría 3): **ya cerrado**. Todos los `<x>_module := class<concrete>:` tienen el specifier obligatorio. Sin cambio.

#### Docs (resumen archivos tocados)
- 8 docs autoritativos modificados (B1.1 + B1.2 combinados):
  - `CONCEPT.md` (2 ocurrencias B1.1: §5.4 + §13.3 SPR-010)
  - `GLOSSARY.md` (1 entrada B1.1 reescrita)
  - `JSON_SCHEMAS.md` (B1.1 §37 + B1.2 §42.1/§42.2/§42.3 — 5 sub-secciones tocadas)
  - `API_REFERENCE_GENERATED.md` (B1.1 §3.7 firmas + B1.2 §3.5 ejemplo + §3.2 ejemplo Logger)
  - `MODULES_DEPENDENCY_GRAPH.md` (B1.2 §11.2 — 9 payloads reescritos + nota canónica)
  - `BOOTSTRAP_PIPELINE.md` (B1.2 §11.3 + §11.4 + §11.7 + §6.3 — 4 sub-secciones)
  - `TESTING_PROTOCOL.md` (B1.2 §2.3 + §2.5 — 2 plantillas de test reescritas)
  - `CHANGELOG.md` (esta entrada)
- Schema de persistencia: **sin cambios** (la persistencia ya usaba `player` nativo, FP4 verificado).
- Schema events_catalog.json: **estructura sin cambios** (los tipos `"player"`/`"agent"` ya estaban permitidos en §42.2). Solo cambia el contenido del catálogo runtime al regenerar.
- Pendiente: validar Bloque 2 cuando el usuario confirme.

---

### Added
- **Validador de paths Verse inválidos** en `dependency_cycle_check.py`. Detecta `/Game.Content.Verse...` (path antiguo) y dotted-paths sin barra. Falla la build con `exit 3`. Ver `MODULES_DEPENDENCY_GRAPH.md` §1.4 + §10.3.
- **Sección §1.4 en `MODULES_DEPENDENCY_GRAPH.md`**: regla canónica de sintaxis de paths Verse del proyecto. Decisión cerrada.
- **`CONCEPT.md` §5.7 In-Island Transactions**: nueva sección con restricciones de la API V-Bucks (refund window 20 días, revenue split, `ConsequentialToGameplay`, sales finales).
- **Campo `consequential_to_gameplay` REQUIRED en `vbucks_offers.json`** (`JSON_SCHEMAS.md` §17). Validador debe fallar si falta. Reglas cruzadas: rewards gameplay → `true`; cosméticos puros → `false` permitido.
- **Sección §17.3 política IIT** en `JSON_SCHEMAS.md` con refund window, reporting de denuncias, compliance.
- **Campos `LeaderboardScore_0..7` + `LeaderboardScore_LastUpdate_Epoch`** en PlayerProgress (`PERSISTENCE_MAP.md` §5.1). +72 B fijos. Habilita SYS-047 con cross-session aproximado.
- **Entradas glossary**: `LeaderboardScore`, `ConsequentialToGameplay`. Aumentadas: `In-Island Transactions`, `Entitlement`.

### Changed
- **SYSTEMS_INDEX SYS-047 bucket**: `—` → `Progress (LeaderboardScore_* por stat)`. Tabla §3.2 PlayerProgress refleja nuevo consumidor + tamaños actualizados (720 B → 776 B típico, 1.7 KB → 1.78 KB worst).
- **CONCEPT §14.2 Monetización**: añadidas reglas sobre `consequential_to_gameplay` y refund window de 20 días aplicada al diseño económico.

### Fixed
- **H3.8 (auditoría regresión bloque 3, mayo 2026)** — actualizada afirmación de cierre en `FOLDER_STRUCTURE_TRUTH.md` §9 que decía *"0 ambigüedades"* sin calificación temporal. Era falsa al detectar la auditoría (H3.2, H3.5, H3.6 eran ambigüedades internas del propio doc). Tras aplicar todos los fixes del Bloque 3, sí queda en cero ambigüedades conocidas — pero la afirmación absoluta sin fecha era frágil (cualquier futuro patch podría reintroducir drift). Adicionalmente, la cifra "11 scripts Python build/tools" estaba desactualizada — el conteo real post-H3.7 es 15 scripts (1 `init_unreal.py` + 8 en `build/` + 4 en `tools/` + 2 en `utils/`). Reescrita la línea de cierre con: (1) conteo desglosado correcto de scripts, (2) afirmación calibrada *"0 ambigüedades conocidas tras Auditoría 3 (mayo 2026)"* — verdad presente, deja margen para futuras auditorías. Cierra Bloque 3 de la Auditoría 3.
- **H3.7 (auditoría regresión bloque 3, mayo 2026)** — integrado el validador estructural en el orquestador como **primer step automático**. Antes vivía en `scripts/tools/folder_structure_validator.py` (categoría "ad-hoc, no orquestado" según FOLDER_STRUCTURE §5.1). El orquestador `07_run_full_pipeline.py` (BOOTSTRAP §7.2) NO lo invocaba, mientras que FOLDER_STRUCTURE §8.3 prometía *"CI: primer step antes de build Verse"*. Drift entre promesa y realidad: drift estructural podía propagarse a artifacts sin detección. **Decisión cerrada (Opción A)**: mover el script a `scripts/build/00_validate_structure.py` (prefijo `00_` lo coloca antes de `01_validate_jsons.py`), añadirlo al `STEPS` del orquestador. Cambios aplicados: (1) `FOLDER_STRUCTURE_TRUTH.md` §5 árbol scripts: movido `folder_structure_validator.py` de `tools/` → `build/00_validate_structure.py`; (2) §8 cabecera path actualizado + nota explícita de la decisión H3.7; (3) §8.2 código de referencia comentario actualizado; (4) §8.3 reescrita: orquestador como ruta principal + pre-commit hook + UEFN init + CI implícito vía pipeline; (5) `BOOTSTRAP_PIPELINE.md` §7.1 diagrama ASCII: añadido bloque "VALIDAR ESTRUCTURA / 00_validate_structure" antes del "VALIDAR JSONS"; (6) §7.2 `STEPS` array: `00_validate_structure.py` añadido al inicio + comentario "ejecuta los pasos 0-6"; (7) `SPRINTS_BACKLOG.md` SPR-001 path actualizado a `scripts/build/00_validate_structure.py` con nota "primer step del orquestador"; (8) SPR-174 (orquestador) añadida dep explícita a SPR-001 (necesita el validador existir) + descripción ampliada para mencionar el primer step; (9) `GLOSSARY.md` entrada FOLDER_STRUCTURE path actualizado + cross-ref a BOOTSTRAP §7.2. Garantía operativa: ningún build pasa con drift estructural sin detección.
- **H3.6 (auditoría regresión bloque 3, mayo 2026)** — añadida mención de excepciones canónicas al naming "Verse generado" en `FOLDER_STRUCTURE_TRUTH.md` §1.1 (tabla de convenciones). La fila anterior decía solo `*_Generated.verse` sin mencionar excepciones, mientras que la regex del validador en §8.2 línea 522 (`r"^[A-Z][A-Za-z0-9]*_Generated\.verse$|^ModuleRegistryConstants\.verse$|^EventBusConstants\.verse$"`) sí las incluye. Drift textual: lectores que solo leían §1.1 creían que TODOS los archivos en `Generated/` debían llevar sufijo `_Generated`, y al toparse con `ModuleRegistryConstants.verse` (sin sufijo) lo interpretarían como violación. Reescrita la fila con la regla general + las 2 excepciones explícitas (`ModuleRegistryConstants.verse` C1, `EventBusConstants.verse` C3). Añadida nota al pie de la tabla con cross-ref a §8.2 (regex operativa) + `BOOTSTRAP_PIPELINE.md` §4.4 + decisión D-A10. Texto y regex ahora convergen.
- **H3.5 (auditoría regresión bloque 3, mayo 2026)** — corregidas las "Excepciones" del patrón naming `_Generated.verse` en `BOOTSTRAP_PIPELINE.md` §4.4. La lista anterior contenía 2 entradas con dos errores: (1) `ThemeConstants_Generated.verse` etiquetada como excepción cuando NO lo es (sí lleva sufijo `_Generated`; el prefijo es solo nombre semántico del contenido — pertenece a la regla normal); (2) `EventBusConstants.verse` (excepción real introducida en Auditoría 2 — C3) NO estaba listada. La incoherencia confundía a lectores: creían que `ThemeConstants` era un caso especial cuando no lo es, y desconocían que `EventBusConstants` sí lo era. Reescrita la lista de excepciones canónicas: SOLO `ModuleRegistryConstants.verse` (SPR-005, C1) y `EventBusConstants.verse` (SPR-009, C3). Añadida nota explícita aclarando que `ThemeConstants_Generated.verse` NO es excepción. Añadida cross-ref a `FOLDER_STRUCTURE_TRUTH.md` §8.2 línea 522 (regex validador) que es la verdad operativa — coincide ahora con esta lista textual. Coherente con D-A10 (Auditoría 2 — C3) registrada en sección Decisions del CHANGELOG.
- **H3.4 (auditoría regresión bloque 3, mayo 2026)** — completada tabla "Tipos de artifacts esperados" en `BOOTSTRAP_PIPELINE.md` §4.3 que listaba solo **7 archivos** generados cuando `FOLDER_STRUCTURE_TRUTH.md` §4 árbol Generated/ tiene **15**. Faltaban 8: `ModuleRegistryConstants.verse` (Auditoría 2 — C1), `EventBusConstants.verse` (C3), `EventPayloads_Generated.verse` (C3), `BalanceCurves_Generated.verse` (SPR-134, único caso de source en markdown en lugar de JSON), `PlayerStats_Generated.verse`, `SkillTree_Generated.verse`, `Achievements_Generated.verse`, `Localization_Generated.verse`. Drift causaba que lectores del doc (incluida IA generadora de transformers) asumieran que solo 7 artifacts existían — bloqueante para entender SPR-004 ext (que ya en H1.4 enumeraba los 15 en CONCEPT/SPRINTS_BACKLOG). Tabla reescrita completa con los 15, columna "Source" generalizada (ya no "Source JSON" porque BalanceCurves viene de markdown). Añadida leyenda con ⚙️ (artifacts arquitectónicos C1+C3, excepciones de naming canónicas) y 📐 (BalanceCurves único caso markdown→verse). Añadida nota de cierre con desglose por script generador: 12 artifacts vía `02_export_constants_to_verse.py` (script central) + 1 vía `04_generate_zone_layouts.py` + 1 vía `05_apply_theme_pack.py` + 1 caso especial. Coherente con FOLDER_STRUCTURE §4.1 resumen (15 archivos en Generated/).
- **H3.3 (auditoría regresión bloque 3, mayo 2026)** — corregida redirección obsoleta en `BOOTSTRAP_PIPELINE.md` §2.1 que decía *"Ver CONCEPT.md sección 11.1 para el árbol completo"*. Pero `CONCEPT.md:1018` declara explícitamente que §11.1 es vista resumida y obsoleta, y que `FOLDER_STRUCTURE_TRUTH.md` es el doc autoritativo para la estructura del proyecto. Ergo BOOTSTRAP enviaba al lector (y a cualquier transformer Python que lo siguiera) a una fuente desactualizada con paths potencialmente incorrectos. Reescrita §2.1 apuntando a `FOLDER_STRUCTURE_TRUTH.md` §3 con nota explícita de que el árbol legacy en CONCEPT §11.1 NO debe usarse como fuente. Adicionalmente, en §4.3 nota lateral *"Por qué uno y no varios"* se eliminó la mención obsoleta a CONCEPT §11.1 manteniendo solo el alineamiento con FOLDER_STRUCTURE §5 + SPR-004 ext (las dos fuentes vivas).
- **H3.2 (auditoría regresión bloque 3, mayo 2026)** — eliminada contradicción interna en `FOLDER_STRUCTURE_TRUTH.md` §1.3 (Carpetas que NO deben existir). La entrada *"❌ data/world/ → reemplazada por contenido directo en JSONs específicos"* contradecía §3.1 (que sí lista `data/world/day_night_cycle.json` como carpeta válida con estrella ⭐ NUEVA) y §7.1 (resolución decidida *"Crear `data/world/`. Carpeta válida. SYS-008 necesita JSON."*). Eliminada la entrada errónea de §1.3. Añadida nota explicativa apuntando a §3.1 + §7.1 como fuentes autoritativas y aclarando que el comentario legacy era de versión anterior del doc, pre-SPR-070+. La carpeta es legítima por SYS-008 (Day/Night Cycle). El `folder_structure_validator.py` ya no recibe señales contradictorias entre §1.3 y §3.1.
- **H3.1 (auditoría regresión bloque 3, mayo 2026)** — añadido specifier `<concrete>` a TODOS los singletons del proyecto. **Hallazgo crítico bloqueante**: el patrón canónico oficial Epic ([Class in Verse](https://dev.epicgames.com/documentation/en-us/fortnite/class-in-verse): *"When a class has the concrete specifier, it is possible to construct it with an empty archetype, such as cat{}. This means that every field of the class must have a default value."*) exige `<concrete>` en cualquier clase instanciada con archetype vacío `<x>_module{}`. El proyecto NO lo aplicaba en ningún sitio (cero ocurrencias de `<concrete>` antes del fix), lo que bloqueaba SPR-005 a SPR-010 (Registry, Logger, TimeSync, PersistenceLayer, EventBus, AdminCommands) y todos los Systems registrables Capa 2+ (SPR-011+). Fixes aplicados: (1) `BOOTSTRAP_PIPELINE.md` §10.4 plantilla `module_registry := class<concrete>:`, (2) §10.5 transformer Python emite `class<concrete>:`, (3) §11.5 plantilla `event_bus_module := class<concrete>:`, (4) §11.6 transformer Python emite `class<concrete>:`, (5) `CONCEPT.md` SPR-009 placeholder declarable como `event_bus_module := class<concrete>:`, (6) `MODULES_DEPENDENCY_GRAPH.md` §2.1 nota canónica con cita Epic + scope ampliado a Systems registrables Capa 2+ + ejemplo Logger corregido (era `logger_module := module:`, incorrecto — `module` es namespace sin archetype, distinto sintáctica de `class<concrete>` instanciable), (7) `GLOSSARY.md` entrada "Singleton top-level" reescrita con patrón canónico `<x>_module := class<concrete>:` y aclaración module vs class, (8) `API_REFERENCE_GENERATED.md` §3 cabecera con nota canónica + alcance Systems, (9) `JSON_SCHEMAS.md` §43 validación cruzada: el manifest exige que `module_name` declarado aparezca en el `.verse` correspondiente como `<id>_module := class<concrete>:` (antes admitía `module:` o `class:` plano — incorrecto). Patrón final canónico: `<Nombre> : <nombre>_module = <nombre>_module{}` con tipo `<nombre>_module := class<concrete>:`. Aclaración importante (NO confundir): `<X>_module := class<concrete>:` (instanciable, archetype vacío) NO es `module := module:` (palabra reservada de namespace, sin archetype). Hallazgo bonus integrado: corregida inconsistencia previa en MODULES §2.1 que mezclaba ambos patrones en el mismo ejemplo. Risk Sprint 1 mitigado: SPR-005 a SPR-010 ya pueden compilar.
- **H2.6 (auditoría regresión bloque 2, mayo 2026)** — añadida entrada al diagnóstico común de errores Verse en `EMERGENCY_ROLLBACK.md` §5.3. Tras el fix H2.1 (clases persistables ahora con `<final>`), el modo de fallo simétrico (regresión accidental por olvidar `<final>` en una `class<persistable>` nueva) no estaba catalogado. Nueva fila: *"Persistable class must be final / warning de subclase potencial en class<persistable>"* → causa: falta `<final>`, patrón canónico `<Bucket> := class<final><persistable>:`, aclara que aplica solo a class y no a struct, ref a `PERSISTENCE_MAP.md` §3 cabecera. Cierra Bloque 2.
- **H2.4 (auditoría regresión bloque 2, mayo 2026)** — sincronizados los tamaños de los 4 weak_maps en `PERSISTENCE_MAP.md` §2 que mostraban números pre-optimización contradictorios con §7.1 (drift de 8-25× según bucket: PlayerCore decía "~12 KB típico" cuando son 568 B; PlayerInventory decía "~30 KB" cuando son 3.5 KB; etc.). Reescritos los 4 valores del diagrama ASCII para coincidir con §7.1, total `~5.2 KB típico / ~14 KB worst` (antes "~67 KB / ~230 KB"). Añadida nota explícita en §2: *"Fuente canónica de tamaños: §7.1. Si hay drift, §7.1 es source of truth"*. Texto explicativo actualizado: "86% libre" → ">98% libre" (uso normal), "55% libre" → ">97% libre" (worst-case). **Efecto colateral**: `SYSTEMS_INDEX.md` §3.2 tenía tabla con dos columnas ("Presupuesto reservado §2" + "Uso real §7"), donde la primera columna era el drift mismo. Eliminada la columna "Presupuesto reservado" — los números pre-optimización no aportaban como "presupuesto futuro" (interpretación retrospectiva inventada al consolidar la tabla); ahora la tabla muestra solo "Uso real (typical / worst) + % del cap". Notas explicativas reescritas. Coherente con la regla de §188: "Si discrepa con PERSISTENCE_MAP → gana PERSISTENCE_MAP".
- **H2.3 (auditoría regresión bloque 2, mayo 2026)** — añadida regla canónica de redondeo `Floor()` en `JSON_SCHEMAS.md` §44.3 (validaciones) y §44.4 (coherencia cross-doc) para resolver el drift de tipos float→int entre `player_stats_base.json` y `PlayerCore`. El JSON declara `per_level: float` (necesario porque Speed=`0.5`, Luck=`0.2`) pero los 6 stats persistidos (`HP_Max`, `Stamina_Max`, `Strength`, `Speed`, `Intelligence`, `Luck`) son `int` en `PERSISTENCE_MAP.md` §3.1. Antes del fix no había regla explícita, lo que generaba ambigüedad determinista (¿`Floor`/`Round`/`Trunc`?) entre cliente/servidor. Decisión: `Floor(base + growth_at_level)` al persistir, `float` en cálculos intermedios (multipliers, flat_bonuses), `Min(Floor(...), caps[stat])` cuando hay cap. Razones: (1) determinista, (2) monotónica (stat lvl N+1 ≥ stat lvl N siempre), (3) coste mínimo, (4) coherente con BALANCE para xp_curve y cost_per_rank. Añadido principio rector #7 en `BALANCE_FORMULAS.md` §1.1 con cross-ref a §44.3/§44.4.
- **H2.2 (auditoría regresión bloque 2, mayo 2026)** — corregidas las **4 declaraciones de weak_map** persistentes en `API_REFERENCE_GENERATED.md` §3.4. Antes faltaban tanto el specifier `var` como el inicializador `= map{}`, contradiciendo el patrón canónico oficial Epic ([Constants and Variables in Verse](https://dev.epicgames.com/documentation/en-us/fortnite/constants-and-variables-in-verse): *"var MySavedPlayerData:weak_map(player, int) = map{}"*). Reescritas las 4 firmas como `var <Name>_Map:weak_map(player, <T>) = map{}`. La descripción de cada firma ahora aclara: (1) son `var` requeridas por Verse para persistencia, (2) visibilidad por defecto `<internal>` (sin `<public>`) coherente con la decisión de exponer solo `Load*/Save*` al exterior — `MODULES_DEPENDENCY_GRAPH.md` §4.4, (3) los consumidores externos acceden vía las funciones públicas, no leen el map directamente. Corrige asunción incorrecta en SPR-008 antes de implementación.
- **H2.1 (auditoría regresión bloque 2, mayo 2026)** — añadido specifier `<final>` faltante a las **7 ocurrencias** de `class<persistable>` en `PERSISTENCE_MAP.md`: 4 buckets root (`PlayerCore` §3.1, `PlayerInventory` §4.1, `PlayerProgress` §5.1, `PlayerEconomy` §6.1) + 3 ejemplos en §8 (versionado, deprecar, cambio de tipo). Patrón canónico oficial: `class<final><persistable>:`. Razón: las clases persistables NO pueden tener subclases por spec Verse, y por tanto requieren `<final>` ([dev.epicgames.com — Class in Verse](https://dev.epicgames.com/documentation/en-us/fortnite/class-in-verse): *"Defined with the persistable specifier. Defined with the final specifier, because persistable classes cannot have subclasses"*). Confirmado por 3 ejemplos oficiales adicionales (Using Persistable Data in Verse, Make Your Own In-Game Leaderboard, Persistent Player Statistics). Sin el specifier el compilador UEFN emite warning post-v31 (deprecación silenciosa) o futuro fallo. Bloqueante para SPR-008. Añadida nota canónica al inicio de `PERSISTENCE_MAP.md` §3 explicando el patrón y aclarando que `<final>` SOLO aplica a `class<persistable>` (no a `struct<persistable>` — los structs no soportan herencia).
  - Closes H2.5 parcial: clarificación del scope de D-A2 (entries internas struct vs root buckets class) registrada en sección Decisions.
- **H1.5 (auditoría regresión bloque 1, mayo 2026)** — eliminada nota legacy "Pendiente C3 secundario" en `API_REFERENCE_GENERATED.md` §3.4 que decía "Hay decisión pendiente sobre cómo distinguir 'primer login sin datos guardados' del default vacío. Posible solución: usar `<decides>` con primer-login flag. Se cierra en patches posteriores junto con el resto del C3." Reemplazada por nota positiva canónica que apunta al patrón existente. Re-verificación contra `PERSISTENCE_MAP.md` §8.3 (versionado schema) + §10 (validación defensiva): el patrón actual retorna `Player<X>{}` cuando el `weak_map` no tiene entrada y aplica validación defensiva siempre — el "default vacío" es semánticamente válido por diseño. La distinción "primera vez" se hace con campos persistentes explícitos (`Tutorial_Completed`, `FirstRebirth_Done` ya en schema PlayerProgress). Conclusión: el sub-hito que planteaba la nota fue descartado durante el patch C3 (no requería resolución), pero la nota olvidó actualizarse. Marcado como **falso positivo cerrado por re-verificación** — no se abre Cn nuevo.
- **H1.4 (auditoría regresión bloque 1, mayo 2026)** — recalibrados SPR-004 / SPR-005 / SPR-009 en `CONCEPT.md` §sprints + `SPRINTS_BACKLOG.md` §3 (F0) tras cierre de C1 (Registry generado) + C3 (EventBus generado). Cambios:
  - **SPR-004**: tiempo 2h → 3h. Done expandido para enumerar 3 funciones export de arquitectura (`export_module_registry` desde `modules_manifest.json`, `export_event_payloads` + `export_event_bus` desde `events_catalog.json`) además del export de datos (companions/items/etc.). Refs a plantillas `BOOTSTRAP_PIPELINE.md` §10.5 + §11.6. Archivo único `02_export_constants_to_verse.py` produce los 8+ archivos en `Content/Verse/Generated/`.
  - **SPR-005**: dep añadida SPR-004 (necesita `Generated/ModuleRegistryConstants.verse`). `Archivos:` reformateado como lista enumerando source-controlled vs generado. Tiempo sin cambios (1.5h).
  - **SPR-009**: dep añadida SPR-004. Tiempo 1h → 1.5h. `Archivos:` lista 3 entradas (placeholder `Core/EventBus.verse` + 2 generados). Done ya alineado con C3 desde H1.3 — eliminadas las marcas `⚠️ pendiente recalibrar en H1.4`. La generación Python sigue pertenecienciendo a SPR-004 (no se cuenta dos veces).
  - **Notas F0 del backlog**: bloque "Notas C1 (Auditoría 2)" → "Notas C1 + C3 (Auditoría 2)". 4 bullets → 6 bullets reflejando deps reales.
- **H1.3 (auditoría regresión bloque 1, mayo 2026)** — reescrito el bloque Done + Notas de **SPR-009 en `CONCEPT.md`** que estaba desactualizado tras el cierre de C3. Eliminadas las firmas legacy `Subscribe(event_name, handler)` / `Emit(event_name, payload)` y la nota "C3 cabo suelto pendiente — se cierra en patches posteriores" (C3 está cerrado en CHANGELOG:329). Done ahora incluye 6 criterios alineados con el patrón canónico C3: placeholder en `Core/EventBus.verse`, generación de `Generated/EventBusConstants.verse` + `Generated/EventPayloads_Generated.verse` desde `data/architecture/events_catalog.json`, patrón `EventBus.<Evento>.Signal/Subscribe/Unsubscribe/Await` sobre `event(payload_t)` nativo, type-safety compile-time, prohibición explícita de strings/`Payload:any`. Notas renombradas a "C1 + C3" con refs a BOOTSTRAP §11 + JSON_SCHEMAS §42 + MODULES §11.2. Marcadas con `⚠️ pendiente recalibrar en H1.4` las casillas `Tiempo` y `Archivos` (que son scope de H1.4, no de H1.3).
- **H1.2 (auditoría regresión bloque 1, mayo 2026)** — corregida prosa legacy `EventBus.Subscribe()` en `MODULES_DEPENDENCY_GRAPH.md` §2.2 línea 184 que sobrevivió al patch C3. Reescrita a `EventBus.<Evento>.Subscribe(handler_tipado)` con referencia explícita al catálogo §11.2. Cierre parcial previo en TESTING_PROTOCOL.md §2.3 documentado en H1.1. Pendiente cierre completo de H1.3 para CONCEPT.md:1327 (Done de SPR-009 con firmas legacy `Subscribe(event_name, handler)`/`Emit(event_name, payload)` — se aborda como hallazgo separado por solapamiento).
- **H1.1 (auditoría regresión bloque 1, mayo 2026)** — eliminadas 4 inyecciones `@editable` de Core en plantillas de `TESTING_PROTOCOL.md` §2.1, §2.2, §2.3 que contradecían D-A7. Las 3 plantillas (Smoke / Unit / Integration) reescritas para acceder a Core vía `using { /<ProjectName>/Core/<Modulo> }` directo. La plantilla §2.3 además se migró al patrón EventBus C3 (`EventBus.LevelUp.Subscribe(handler_tipado)` + `level_up_payload`) y al lookup runtime para Systems gameplay (`ModuleRegistry.GetPlayerStats[]`). Se añaden notas explicativas en §2.1 y §2.3 referenciando MODULES_DEPENDENCY_GRAPH §2.1/§4.7 y API_REFERENCE §3.
  - Closes parcial: H1.2 en TESTING_PROTOCOL §2.3 (resto de docs sin tocar todavía).
- **D-01 (auditoría mayo 2026)** — `GetSimulation()` → `GetSimulationElapsedTime()` en `CONCEPT.md` (5 ocurrencias en §5.6, §7.2, §8 SYS-068 tabla, §11 anti-patrones, §14.10) y `GLOSSARY.md` (TimeSync). Función oficial: `/Verse.org/Simulation` namespace, devuelve `float` segundos desde inicio. Para epoch UTC absoluto hay que combinar con anchor capturado en `OnBegin`.
  - Fuente: https://dev.epicgames.com/documentation/en-us/fortnite/verse-api/versedotorg/simulation/getsimulationelapsedtime
- **D-02 (auditoría mayo 2026)** — paths Verse `/Game.Content.Verse.X.Y.Z` reemplazados por sintaxis canónica `/<ProjectName>/X/Y` en `MODULES_DEPENDENCY_GRAPH.md` (header), `BOOTSTRAP_PIPELINE.md` (§5.1, §6.1), `TESTING_PROTOCOL.md` (§3.1 plantilla `test_device`).
  - Sintaxis incorrecta usaba puntos como separadores y prefijo inventado. La forma correcta usa `/` y el nombre del proyecto UEFN como root.
  - Placeholder `<ProjectName>` documentado: se sustituye al instanciar el proyecto UEFN real (script `replace_project_name.py` a generar en SPR-001).
  - Fuente: https://dev.epicgames.com/documentation/en-us/fortnite/modules-and-paths-in-verse
  - ⚠️ **OBSOLETO post-SPR-211**: ambas afirmaciones de D-02 desactualizadas. (1) Sintaxis dotted relative SÍ válida hoy en Verse moderno (VS Code Quick Fix la ofrece como preferida): `using { Verse.Core.Logger }`. (2) Path canónico real **incluye** `Verse/`: `/lexosi@fortnite.com/RPG_Survival/Verse/Core/Logger`. Ver `VERSE_SYNTAX_GUIDE.md` §1 lección 1+2 + §4. Entry D-02 conservada por trazabilidad histórica; usar VERSE_SYNTAX_GUIDE como autoridad.
- **D-04 (auditoría mayo 2026)** — claim "leaderboard_device da rankings cross-session" corregido en `CONCEPT.md` (§5.4 tabla, §7.2 bullet, §8 SYS-047 row, §...) y `SYSTEMS_INDEX.md` SYS-047. Realidad: el device es UI, no fuente cross-session. Datos globales se aproximan vía Verse Persistence (`LeaderboardScore_*`). Epic no expone API para listar jugadores fuera de sesión actual.
  - Fuente: https://dev.epicgames.com/documentation/en-us/fortnite/make-your-own-ingame-leaderboard-in-verse
- **D-05 (auditoría mayo 2026)** — falta del flag `ConsequentialToGameplay` (regla Epic v39.00) cubierta. Schema actualizado, validaciones añadidas, decisión documentada en CONCEPT §14.2.
  - Fuente: https://dev.epicgames.com/documentation/en-us/fortnite/in-island-transactions-overview-in-fortnite + release notes v39.00
- **D-06 (auditoría mayo 2026)** — refund window de 20 días no documentada → ahora en CONCEPT §5.7 + GLOSSARY + JSON_SCHEMAS §17.3. Regla de diseño: items high-value no convertibles antes de día 21 desde compra.
  - Fuente: https://www.fortnite.com/news/tools-for-in-island-transactions-now-available-to-fortnite-developers
- **D-09 (auditoría mayo 2026)** — afirmación "HUD Messages: solo 3 primeros funcionan" matizada en `CONCEPT.md` §5.4 (tabla notificaciones) y §7.4. La causa real es múltiple: pool >3 instancias + coexistencia con custom UI canvas + regresión v31.00 con `Hide(Agent)`. Estrategia "pool de 3 + fallback a custom widgets" se mantiene como correcta.
  - Fuentes: forums.unrealengine.com/t/hud-message-devices-not-showing-messagf/2280787 + .../major-verse-uefn-hud-message-device-will-not-function-when-custom-ui-is-being-displayed-to-the-player/747312
- **D-11 (auditoría mayo 2026)** — `actor_sub` / `asset_sub` / `level_sub` aclarados en `CONCEPT.md` §6.3: no son built-ins UEFN, son convención `init_unreal.py` (UEFN-TOOLBELT / UEFN-MCP-Server). Añadidos equivalentes manuales para que un script funcione sin el framework. SPR-001 debe incluir scaffolding de `init_unreal.py`.

### Verified — no se aplica fix (afirmación correcta confirmada contra fuentes)
- **D-08** — el "99% crash" de `GetSession() + weak_map` en juegos con rondas no es folclore: es **cita literal del título del bug report en foros oficiales Epic Developer Community**. Sólo se añadió la fuente para futuras referencias y se documentó que el proyecto es sin rondas (loop idle/RPG), por lo que la limitación no aplica directamente.
  - Fuente: forums.unrealengine.com/t/weak-map-with-getsession-is-broken-and-does-not-persist-between-rounds-and-crashes/1263028
- **D-10** — Physics APIs en Verse llegan en **v39.50 (19 feb 2026)** como afirma el proyecto. v39.00 trajo Physics tooling (Add Physics, Chaos Visual Debugger) pero las **APIs Verse** de manipulación de props, puzzles, destrucción son v39.50. Texto del proyecto correcto, sin cambio.
  - Fuente: sesamedisk.com/uefn-2026-game-development-revolution/ (review v39.50, 24 mar 2026)
- **D-12** — Python 3.11 experimental en UEFN v40.00 (abril 2026) confirmado correcto. Sin cambio.

### Persistence
- **PlayerProgress: +72 B fijos** (8 slots `LeaderboardScore_*` × 8 B + 1 epoch update). Schema sigue **Version=1** (cambio aplicado antes de SPR-008, no hay datos persistidos en producción). Margen del bucket sigue >98% libre.

### Decisions
- **D-A1**: root del path Verse del proyecto = nombre del proyecto UEFN. Separadores siempre `/`, nunca `.`. La carpeta `Content/Verse/` no aparece en el path (root Verse se mapea directo). Ver `MODULES_DEPENDENCY_GRAPH.md` §1.4.
- **D-A2 (rechazada, scope: entries internas)**: cambiar `struct<persistable>` → `class<persistable>` en las **entries internas** de los buckets persistentes (`SkillPointEntry`, `ItemEntry`, `CompanionEntry`, `DexEntry`, `EquippedItem`, `QuestProgress`, `BaseUpgradeEntry`, `PityCounter`, `ActiveCraft`). Verificación contra docs oficiales (https://dev.epicgames.com/documentation/en-us/fortnite/struct-in-verse) confirma que `struct<persistable>` es sintaxis válida y oficialmente recomendada para schemas constantes pequeños sin herencia. Se mantienen las entries como struct. **Nota de scope**: esta decisión NO aplica a los 4 buckets root (`PlayerCore`, `PlayerInventory`, `PlayerProgress`, `PlayerEconomy`), que SIEMPRE han sido `class<final><persistable>` por requisito oficial Epic ([Class in Verse](https://dev.epicgames.com/documentation/en-us/fortnite/class-in-verse) — las clases persistables deben ser `<final>` porque no soportan subclases). Ver fix H2.1 que añade el `<final>` faltante a los 4 root + 3 ejemplos.
- **D-A3**: `LeaderboardScore` cacheado en PlayerProgress como 8 slots fijos `int` (no array dinámico ni map). Razones: (1) acceso O(1), (2) tamaño determinista, (3) no necesita schema migration cuando se añade un leaderboard nuevo (se mapea a un slot reservado). Convención de slots documentada en el schema.
- **D-A4**: `consequential_to_gameplay` es REQUIRED en cada entitlement (no opcional con default). Razón: es un compromiso compliance público con Epic — debe ser una decisión explícita por entitlement, no un default invisible.
- **D-A5**: regla de diseño económico aplicada al refund window: ninguna mecánica que asuma irreversibilidad económica antes de 21 días desde la compra V-Bucks (companions premium no se pueden disolver en gems hasta día 21, etc.). Aplicar en SYS-031, SYS-024 (equipment leveling con items de V-Bucks), SYS-035 (pity).
- **D-A6**: SPR-001 debe incluir scaffolding de `init_unreal.py` que prepuebla `actor_sub`, `asset_sub`, `level_sub`. Todos los scripts `scripts/build/` y `scripts/tools/` asumen estas variables disponibles. Sin `init_unreal.py` el dev tiene que importarlas manualmente.

---

## 🔧 Auditoría 2 — C1 (mayo 2026, viabilidad lógica e integración)

> **Crítico C1: bootstrap circular `ModuleRegistry ↔ Logger`** detectado en auditoría 2. Tras re-verificación contra Verse oficial, parcialmente falso positivo: **no hay ciclo runtime** (Verse inicializa constantes top-level antes de OnBegin). Sí había **contradicciones documentales tri-vía** entre 3 docs autoritativos. Cerrado con refactor arquitectónico.

### Changed
- **`MODULES_DEPENDENCY_GRAPH.md` §2.1** reescrita completa. Antes: pseudo-orden de carga inventado controlado por ModuleRegistry. Ahora: explica cómo Verse inicializa de verdad (constantes top-level antes de cualquier `OnBegin`) + tabla de dependencias compile-time entre Core + qué controla el dev (orden de `Init()` de Systems en GameManager, no carga de Core).
- **`MODULES_DEPENDENCY_GRAPH.md` §4.1–§4.7** cada módulo Core (Logger, EventBus, TimeSync, PersistenceLayer, BigNumbers, AdminCommands, ModuleRegistry) recibe nota 🏗️ **Arquitectura: singleton top-level**. §4.7 ModuleRegistry refactor mayor: tabla "Hace / NO hace", justificación del workaround a la falta de reflexión runtime, estado en bootstrap.
- **`SPRINTS_BACKLOG.md` §3 (tabla F0)** deps reescritas: SPR-005 (Registry) ahora depende de SPR-006 (Logger), no al revés. SPR-007/008/009 simplificados a `deps: SPR-006` (cada Core usa Logger por `using {}`, NO usa Registry). SPR-010 = `SPR-006, SPR-008, SPR-009`. SPR-005/007/008/009 paralelizables tras SPR-006.
- **`CONCEPT.md` §13.3** mismas correcciones de deps + cabecera con jerarquía: SPRINTS_BACKLOG gana ante discrepancia. §6.11 + §8.2 descripción SYS-072 reescrita ("lookup runtime para Systems gameplay, NO orquesta Core"). §11.1 línea GameManager aclarada como "entry point: orquesta Init de Systems".
- **`API_REFERENCE_GENERATED.md` §3.1 ModuleRegistry** refactor mayor. Eliminadas 3 funciones inventadas (`Init()`, `Register<T>()`, `GetModule<T>()` — Verse no soporta `<T>` runtime). Reemplazadas por: instancia singleton + par tipado `RegisterPlayerStats`/`GetPlayerStats` como ejemplo + sección "Funciones que NO existen" con strikethrough. §3.2–§3.7 cada Core con nota arquitectura. §10 GameManager clarificado.
- **`BOOTSTRAP_PIPELINE.md`** añadida **§10 nueva** (8 sub-secciones): "Patrón Core estático vs Systems registrables". Incluye spec del JSON manifest `data/architecture/modules_manifest.json`, plantilla del Verse generado (`ModuleRegistryConstants.verse`), plantilla del transformer Python (`export_module_registry()`), patrón de uso runtime, criterios inclusión/exclusión, validación CI.
- **`GLOSSARY.md`** entradas reescritas: `ModuleRegistry` ("orquesta init centralizado" → "lookup runtime para Systems gameplay"), `Logger`/`EventBus`/`TimeSync`/`BigNumbers`/`PersistenceLayer` con nota arquitectura singleton top-level. EventBus marca pendiente C3 (firma actual con `any` no compila).

### Added
- **3 entradas nuevas en `GLOSSARY.md`**: `Singleton top-level (Verse)` (patrón canónico Verse con ref oficial), `Systems registrables` (criterios inclusión/exclusión en Registry), `modules_manifest.json` (definición del JSON manifest declarativo).
- **Spec del JSON manifest** `data/architecture/modules_manifest.json` (BOOTSTRAP_PIPELINE §10.3) con schema completo, validaciones cruzadas, ejemplo.
- **Plantilla del transformer** `export_module_registry()` en BOOTSTRAP_PIPELINE §10.5 — código Python idempotente listo para SPR-005.
- **Plantilla Verse** `ModuleRegistryConstants.verse` en BOOTSTRAP_PIPELINE §10.4 — código real del archivo generado, con setters/getters tipados.

### Fixed
- **C1.1** — Contradicción tri-vía entre `MODULES_DEPENDENCY_GRAPH.md` §2.1 (Logger arranca primero), §4.7 (ModuleRegistry → Deps: Logger 🔒), `SPRINTS_BACKLOG.md` SPR-006 (Logger deps SPR-005 Registry). Resuelta: Logger no depende de Registry; Registry usa Logger por `using {}`. SPR-006 entrega antes y desbloquea el resto de Core.
- **C1.2** — `ModuleRegistry.Init()`/`Register<T>()`/`GetModule<T>()` declaradas en API_REFERENCE como pendientes pero **no son viables en Verse** (no hay reflexión runtime). Sustituidas por getters tipados estáticos generados desde JSON manifest.
- **C1.3** — Descripciones SYS-072 en CONCEPT §6.11 ("registra en init central; orden de carga predecible") y §8.2 ("init centralizado") contradicen modelo Verse real. Reescritas como "lookup runtime para Systems gameplay (Capa 2+); NO orquesta Core".

### Verified — no se aplica fix (afirmación correcta confirmada contra fuentes)
- **C1-FP1** — sospecha inicial "ciclo de bootstrap runtime Logger ↔ ModuleRegistry". Re-verificación contra Epic dev docs: **falso positivo**. Verse inicializa todas las constantes a nivel de módulo **antes** de cualquier `OnBegin`. No hay ciclo runtime posible. El "ciclo" diagnosticado fue inferencia importada de paradigmas tipo Spring/DI; Verse no usa self-registration.
  - Fuente 1: https://dev.epicgames.com/documentation/en-us/fortnite/constants-and-variables-in-verse
  - Fuente 2: https://forums.unrealengine.com/t/i-came-up-with-a-way-to-make-singletons-in-verse/1139453 (patrón singleton oficial de la comunidad)
- **C1-FP2** — sospecha "hay que reordenar SPR-005 ↔ SPR-006 (renumerar IDs)". Re-verificación: regla del proyecto declara IDs inmutables (SPRINTS_BACKLOG §9.1). Resuelto **sin renumerar**: solo se ajustan deps. SPR-005 sigue siendo Registry, SPR-006 sigue siendo Logger.
- **C1-FP3** — sospecha "Logger es dep de TODOS los demás módulos (~83) — cifra exagerada" en GLOSSARY. Re-verificación contra MODULES §11.1 v2: cifra **confirmada** (~83 = todos los módulos del proyecto). Sin cambio.
- **C1-FP4** — sospecha "PersistenceLayer dep de 24 módulos — número desactualizado" en GLOSSARY. Re-verificación contra MODULES §4.4 v2: cifra **confirmada**. Sin cambio.
- **C1-FP5** — sospecha "GetSimulationElapsedTime() en TimeSync GLOSSARY puede no ser API real Verse 2026". Re-verificación contra Epic dev docs: **API real, namespace `/Verse.org/Simulation`, devuelve float segundos**. Sin cambio.
  - Fuente: https://dev.epicgames.com/documentation/en-us/fortnite/verse-api/versedotorg/simulation/getsimulationelapsedtime

### Decisions
- **D-A7 (Auditoría 2 — C1)**: los 6 módulos Core (Logger, EventBus, TimeSync, PersistenceLayer, BigNumbers, AdminCommands) + ModuleRegistry son **singletons top-level estáticos** declarados como `<Modulo> : <modulo>_module = <modulo>_module{}`. NO heredan de `creative_device`. NO se auto-registran. Verse los inicializa antes de cualquier `OnBegin`. Acceso por `using { /<ProjectName>/Core/<Modulo> }` directo. ModuleRegistry sirve **únicamente** a Systems gameplay (Capa 2+) que necesitan resolver lookup runtime para evitar ciclos compile-time entre sí. Workaround a la falta de reflexión runtime de Verse: getters tipados estáticos (`GetPlayerStats():?player_stats_module`) generados desde `data/architecture/modules_manifest.json` por Python en SPR-005. Detalle completo en MODULES §4.7 + BOOTSTRAP §10. **Razón aplicada**: alinea el diseño con el modelo de inicialización real de Verse (sources oficiales Epic confirmadas), elimina contradicciones documentales tri-vía detectadas en auditoría 2, mantiene tipado fuerte en consumidores y permite paralelizar SPR-005/007/008/009 tras SPR-006.

### Docs (resumen archivos tocados)
- 6 docs autoritativos modificados para C1:
  - `MODULES_DEPENDENCY_GRAPH.md` (828 → 919 líneas, +91)
  - `SPRINTS_BACKLOG.md` (465 → 472 líneas, +7)
  - `CONCEPT.md` (1520 → 1533 líneas, +13)
  - `API_REFERENCE_GENERATED.md` (371 → 406 líneas, +35)
  - `BOOTSTRAP_PIPELINE.md` (808 → 1063 líneas, +255 — nueva §10 completa)
  - `GLOSSARY.md` (478 → 487 líneas, +9)
- Schema de persistencia: **sin cambios** (Schema Version sigue v1).
- Auditoría 2 detectó 4 críticos (C1, C2, C3, C4) y 3 medios. Este patch cierra C1. Pendientes: C2 (Registry workaround spec — parcialmente cerrado en BOOTSTRAP §10), C3 (EventBus tipado), C4 (SkillPoints_Spent schema).

---

## 🔧 Auditoría 2 — C3 (mayo 2026, EventBus type-safe)

> **Crítico C3: `Subscribe(EventName:string, Handler:type{_(Payload:any):void}):void` — `any` no existe en Verse.** Tras re-verificación contra `Verse.digest`, descubierto que Verse YA tiene `event<native>(t:type)` parametric type compile-time como primitiva nativa (con interfaces `signalable`/`awaitable`/`subscribable`). El plan original (EventBus custom con `map<string, []handler>`) se sustituye por composición de `event(payload_t)` nativos sobre un `event_bus_module` generado.

### Changed
- **`MODULES_DEPENDENCY_GRAPH.md` cabecera**: añadida 3ª decisión cerrada (EventBus tipado C3).
- **`MODULES_DEPENDENCY_GRAPH.md` §4.2 EventBus** reescrita completa. Antes: "singleton top-level con Logger 🔒". Ahora: "EventBus operativo generado desde events_catalog.json, compone instancias `event(payload_t)` nativas". Deps refactor.
- **`MODULES_DEPENDENCY_GRAPH.md` §11.2 catálogo eventos** reescrito. Tabla con 9 eventos ahora incluye `verse_event_name` (`EventBus.LevelUp`) + `verse_struct_name` (`level_up_payload{...}`). Nota explicativa: payloads SÍ son compile-time bajo el nuevo modelo, no más bugs silenciosos.
- **`API_REFERENCE_GENERATED.md` cabecera**: añadida decisión cerrada C3.
- **`API_REFERENCE_GENERATED.md` §3.5 EventBus** refactor mayor. Eliminadas 3 firmas inválidas con `Payload:any`. Reemplazadas por: documentación del singleton generado + ejemplo de `Signal()`/`Subscribe()`/`Unsubscribe()`/`Await()` nativos sobre instancias `event(payload_t)`. Sección "Funciones que NO existen" con strikethrough.
- **`GLOSSARY.md` `### EventBus`** reescrito completo. Quitada nota "pendiente C3". Ahora declara patrón cerrado.

### Added
- **`JSON_SCHEMAS.md` §42 nueva**: spec completa de `events_catalog.json` con 4 sub-secciones (estructura, reglas de campos, validaciones cruzadas, política de cambios). Tabla de tipos JSON → Verse permitidos. Tipos prohibidos documentados (sin nesting, sin maps, sin optionals — flat structs).
- **`BOOTSTRAP_PIPELINE.md` §11 nueva** (10 sub-secciones): "EventBus tipado generado". Incluye justificación arquitectónica (`event(t)` nativo de Verse), spec del catalog JSON, plantillas de los 2 archivos generados (`EventPayloads_Generated.verse` + `EventBusConstants.verse`), plantilla del transformer Python, patrón de uso (Signal/Subscribe/Await/Unsubscribe), criterios inclusión/exclusión, validación CI, tabla comparativa "plan original vs plan final".
- **2 entradas nuevas en `GLOSSARY.md`**: `### events_catalog.json` (definición + schema ref), `### event(t) — primitiva nativa Verse` (documentación de `Verse.digest` con fuente).

### Fixed
- **C3.1** — `EventBus.Subscribe(string, Handler{_(Payload:any):void})` no compila (`any` no existe en Verse). Sustituido por `EventBus.<Evento>.Subscribe(handler_tipado)` sobre `event(payload_t)` nativo.
- **C3.2** — `EventBus.Emit(string, any)` no compila. Sustituido por `EventBus.<Evento>.Signal(payload_struct)`.
- **C3.3** — los payloads en §11.2 estaban descritos como pseudo-objetos JSON-style (`{player_id, stat, old, new}`) sin tipo Verse claro. Ahora son structs Verse generados desde `events_catalog.json` con tipos explícitos por campo.

### Verified — no se aplica fix (afirmación correcta confirmada contra fuentes)
- **C3-FP1** — sospecha "construir EventBus desde cero con map interno". Re-verificación contra `Verse.digest`: **falso positivo**. Verse YA tiene `event<native>(t:type)<computes> := class(signalable(t), awaitable(t))` como primitiva. Construir map custom sería reinventar la rueda con peor type-safety. El bus se simplifica radicalmente (composición de primitivas nativas en lugar de implementación custom).
  - Fuente: https://forums.unrealengine.com/t/multicast-delegate-equivalent-in-uefn-verse/1232137 (extracto de `Verse.digest` del foro oficial Epic)
- **C3-FP2** — sospecha "plantilla `Subscribe_<EventName>` / `Emit_<EventName>` (un wrapper por evento)". Re-verificación: **falso positivo**. Innecesario. Las instancias `event(t)` ya exponen `.Signal()`/`.Subscribe()`/`.Await()` nativamente. La plantilla final solo declara la propiedad, no genera wrappers.

### Decisions
- **D-A8 (Auditoría 2 — C3)**: el EventBus del proyecto se construye **componiendo** instancias `event(payload_t)` nativas de Verse, una por cada evento del catálogo `data/architecture/events_catalog.json`. NO es un map custom. NO usa string keys. NO usa `Payload:any`. La generación produce 2 archivos: `EventPayloads_Generated.verse` (structs payloads) + `EventBusConstants.verse` (singleton `EventBus` con propiedades `event(t)` tipadas). Type-safety garantizada por compilador. Cambios en payload struct → compile error inmediato en suscriptores (mejora vs el patrón runtime original). Soporte `await` nativo (las instancias `event(t)` son `awaitable`). **Razón aplicada**: alinea el diseño con primitivas Verse reales (sources oficiales Epic confirmadas), elimina string-magic, reduce LOC del bus de ~200 a ~9 (resto declarativo en JSON), y proporciona type-safety compile-time imposible en el plan original.

### Docs (resumen archivos tocados)
- 6 docs autoritativos modificados para C3:
  - `JSON_SCHEMAS.md` (1893 → ~1995 líneas, +~100 — nueva §42 events_catalog)
  - `BOOTSTRAP_PIPELINE.md` (1063 → ~1290 líneas, +~227 — nueva §11 EventBus tipado)
  - `MODULES_DEPENDENCY_GRAPH.md` cabecera + §4.2 + §11.2 reescritos
  - `API_REFERENCE_GENERATED.md` cabecera + §3.5 reescritos
  - `GLOSSARY.md` (487 → ~492 líneas, +5 — entrada EventBus reescrita + 2 entradas nuevas)
- Schema de persistencia: **sin cambios**.
- C2 (manifest cross-doc sync) y C4 (SkillPoints_Spent schema) siguen pendientes.

---

## 🔧 Auditoría 2 — C4 (mayo 2026, SkillPoints_Spent schema)

> **Crítico C4: `SkillPoints_Spent:[]int = array{}` no representa correctamente `(skill_id, rank)` por entrada.** El JSON declara `SkillNode.id` global + `max_rank: 1..10` por skill, pero la persistencia plana `[]int` requiere convenciones implícitas no documentadas (¿indexado por skill_id? ¿total por tree?). Refactor a `[]SkillPointEntry := struct<persistable>{SkillID, Rank}`.

### Changed
- **`PERSISTENCE_MAP.md` §3.1 PlayerCore**: campo `SkillPoints_Spent:[]int` → `SkillPoints_Spent:[]SkillPointEntry`. Comentario actualizado (1 entry por skill con rank≥1, skills no aprendidos NO aparecen).
- **`PERSISTENCE_MAP.md` §3.2 cálculo bytes**: recalculado típico 340 B → 568 B (+67%), worst-case 600 B → 1.05 KB (+75%). Asumido worst-case ~80 skills aprendidos × 8 B.
- **`PERSISTENCE_MAP.md` §3.3 margen**: actualizado 0.45% → 0.80% del cap. Sigue infrautilizado (>99% libre).
- **`PERSISTENCE_MAP.md` §7.1 tabla resumen consolidada**: PlayerCore typical 340 B → 568 B, worst 600 B → 1.05 KB, % usado 0.45% → 0.80%. TOTAL ~5 KB → ~5.2 KB.
- **`SYSTEMS_INDEX.md` §3.2 tabla cobertura buckets**: PlayerCore_Map cifras actualizadas.
- **`JSON_SCHEMAS.md` §25.3 validaciones skill_trees.json**: añadidas 2 validaciones nuevas para coherencia con persistencia (unicidad global de SkillNode.id, clamp defensivo de rank si max_rank se reduce en un patch).

### Added
- **`PERSISTENCE_MAP.md` §3.1**: nuevo struct `SkillPointEntry := struct<persistable>{SkillID:int, Rank:int}` declarado antes de PlayerCore. Patrón coherente con `ItemEntry`, `CompanionEntry`, etc.
- **`GLOSSARY.md` `### SkillPointEntry`** (entrada nueva): definición del struct + convenciones de uso + tamaño + clamp defensivo.

### Fixed
- **C4.1** — `SkillPoints_Spent:[]int = array{}` ambiguo (sin documentar si indexado por skill_id, por tree, o lista de IDs gastados). Sustituido por `[]SkillPointEntry` auto-documentado.
- **C4.2** — comentario del schema viejo decía "5 ramas × N puntos cada una" sin definir `N`. Eliminado, reemplazado por comentario preciso.

### Verified — no se aplica fix (afirmación correcta confirmada contra fuentes)
- **C4-FP1** — sospecha "sistema de respec requiere schema dinámico". Re-verificación: **falso positivo**. No hay mecánica de respec documentada en CONCEPT, BALANCE_FORMULAS, ni SYSTEMS_INDEX. El refactor sigue siendo válido pero por otra razón (auto-documentación + IDs no contiguos).
- **C4-FP2** — sospecha "cambio de schema requiere bump de Schema Version". Re-verificación: **falso positivo**. No hay datos persistidos en producción todavía (pre-SPR-008). Schema sigue v1, sin bump (mismo argumento aplicado en C1).
- **C4-FP3** — sospecha "interpretación 'indexado por skill_id' funciona técnicamente con `[]int`". Re-verificación parcial: **funciona solo si los IDs son contiguos desde 0/1, lo cual el schema NO exige** (`SkillNode.id` está marcado como "único globalmente", no contiguo). Hallazgo sigue válido por robustez frente a IDs no contiguos.

### Decisions
- **D-A9 (Auditoría 2 — C4)**: `SkillPoints_Spent` se persiste como `[]SkillPointEntry := struct<persistable>{SkillID:int, Rank:int}`. Razones: (1) auto-documentado (no requiere convenciones implícitas sobre orden/indexado), (2) robusto a IDs de skills no contiguos (el schema permite IDs únicos globalmente sin garantía de contigüidad), (3) coherente con el patrón ya usado en el proyecto (`ItemEntry`, `CompanionEntry`, `BaseUpgradeEntry`), (4) skills no aprendidos NO ocupan bytes (sparse representation), (5) coste mínimo (8 B por entry, worst-case ~640 B end-game vs los 20 B del modelo viejo — incremento absorbido fácilmente por el 99.55% libre del bucket PlayerCore). Convención runtime: si un patch reduce `max_rank` de un skill, el load defensivo clampa el rank persistido al nuevo máximo (validación documentada en `JSON_SCHEMAS.md` §25.3).

### Docs (resumen archivos tocados)
- 4 docs autoritativos modificados para C4:
  - `PERSISTENCE_MAP.md` (§3.1 + §3.2 + §3.3 + §7.1)
  - `SYSTEMS_INDEX.md` (§3.2 cifras buckets)
  - `JSON_SCHEMAS.md` (§25.3 validaciones)
  - `GLOSSARY.md` (1 entrada nueva)
- Schema de persistencia: **Schema Version sigue v1** (cambio aplicado pre-SPR-008, sin datos en producción).
- C2 (manifest cross-doc sync) sigue pendiente.

---

## 🔧 Auditoría 2 — C2 (mayo 2026, sync cross-doc del manifest C1+C3)

> **Crítico C2: spec del JSON manifest del Registry incompleta entre docs.** Tras los patches C1 y C3, la decisión arquitectónica quedó documentada en `MODULES_DEPENDENCY_GRAPH` + `BOOTSTRAP_PIPELINE`, pero los docs satélite (JSON_SCHEMAS, FOLDER_STRUCTURE_TRUTH, SYSTEMS_INDEX) quedaron desincronizados. Patch de sincronización cross-doc.

### Changed
- **`JSON_SCHEMAS.md` índice**: añadidas entradas faltantes §42 (events_catalog) y §43 (modules_manifest) que quedaron sin reflejarse en el índice tras C3+C2. Renumerado §44 (Validación cruzada) y §45 (Cómo extender).
- **`JSON_SCHEMAS.md` sub-secciones §44 y §45**: corregido bug residual de numeración interna (§42.1 → §44.1 en Validación cruzada; §43.1/.2/.3 → §45.1/.2/.3 en Cómo extender). Detectado durante el patch — limpieza cosmética de paso.
- **`FOLDER_STRUCTURE_TRUTH.md` §3.1 árbol data/**: añadida `data/architecture/` con 2 archivos (`modules_manifest.json` + `events_catalog.json`) entre `admin/` y `base/`.
- **`FOLDER_STRUCTURE_TRUTH.md` §3.1 árbol Generated/**: añadidos `EventBusConstants.verse` + `EventPayloads_Generated.verse`. Comentarios actualizados para los 3 archivos arquitectónicos generados, todos con referencia al JSON fuente.
- **`FOLDER_STRUCTURE_TRUTH.md` §validador NAMING_RULES**: regex `Generated` extendida para reconocer `EventBusConstants.verse` como excepción válida (junto a `ModuleRegistryConstants.verse`). `EventPayloads_Generated.verse` ya cumple el patrón principal.
- **`FOLDER_STRUCTURE_TRUTH.md` §7.1 tabla cobertura**: añadida fila para `data/architecture/`.
- **`SYSTEMS_INDEX.md` SYS-072 fila**: columna `JSON principal` ahora apunta a los 2 JSONs arquitectónicos. Columna `Verse principal` lista los 6 archivos Verse asociados (3 Core source-controlled + 3 Generated).
- **`SYSTEMS_INDEX.md` §4.1 tabla cobertura**: 2 nuevas filas para los JSONs arquitectónicos.
- **`SYSTEMS_INDEX.md` §4.2 carpetas faltantes**: añadida `data/architecture/`. Conteo subido de 7 → 8.
- **`SYSTEMS_INDEX.md` total final**: cobertura JSON 60 → 62, sistemas con riesgo 35 → 37.

### Added
- **`JSON_SCHEMAS.md` §43 nueva**: spec completa de `modules_manifest.json` con 4 sub-secciones (estructura, reglas de campos, validaciones cruzadas, política de cambios). Incluye regla nueva: **NO se permite registrar Core en el manifest** (validador rechaza si aparecen Logger, EventBus, etc.).

### Verified — no se aplica fix (afirmación correcta confirmada contra fuentes)
- **C2-FP1** — sospecha "renombrar `EventBusConstants.verse` → `EventBusConstants_Generated.verse` para uniformidad". Re-verificación: **falso positivo**. Crearía nombre redundante. La regex de FOLDER_STRUCTURE_TRUTH ya tiene patrón explícito para excepciones (`ModuleRegistryConstants` ya está). Extender excepciones es lo correcto, no renombrar. Patrón consistente: archivos generados que NO son tablas-de-datos (es decir, son arquitectura/runtime) llevan nombres semánticos sin sufijo `_Generated`.
- **C2-FP2** — sospecha "SPR-009 EventBus debería depender de SPR-002/003 (JSON validation + validador)". Re-verificación: **falso positivo**. SPR-009 entrega `Core/EventBus.verse` source-controlled. La generación de `EventBusConstants.verse` desde catalog es una extensión de SPR-004 (exporter Python), no de SPR-009. Las deps actuales del backlog son coherentes.

### Decisions
- **D-A10 (Auditoría 2 — C2)**: regla de naming para Verse generado **arquitectónico** (Registry, EventBus): nombres semánticos sin sufijo `_Generated` (ej. `ModuleRegistryConstants.verse`, `EventBusConstants.verse`). Para Verse generado **de contenido/datos** (companions, items, etc.): sufijo `_Generated` obligatorio (ej. `Companions_Generated.verse`, `EventPayloads_Generated.verse`). Justificación: los archivos arquitectónicos exponen tipos/instancias que el código consumidor importa con nombre semántico (`EventBus`, `Registry`); los archivos de datos exponen colecciones con sufijo claro de origen. La regex del validador (`FOLDER_STRUCTURE_TRUTH.md` §validador) lista las excepciones explícitamente — añadir cada excepción nueva al regex es parte del done de cualquier nuevo SPR que cree un Verse arquitectónico generado.

### Docs (resumen archivos tocados)
- 3 docs autoritativos modificados para C2:
  - `JSON_SCHEMAS.md` (1995 → 2076 líneas, +81 — nueva §43 modules_manifest + cleanup numeración)
  - `FOLDER_STRUCTURE_TRUTH.md` (646 → 651 líneas, +5 — árbol data/ + Generated/ + regex + cobertura)
  - `SYSTEMS_INDEX.md` (297 → 300 líneas, +3 — SYS-072 fila + cobertura)
- Schema de persistencia: **sin cambios**.
- **C1, C2, C3, C4 cerrados.** Faltan medios M1, M3 + menores m2, Cn1.

---

## 🔧 Auditoría 2 — M1 (mayo 2026, split SPR-134 BalanceCurves)

> **Medio M1: SPR-044 (PlayerProgression, F1) y SPR-048 (PlayerRebirth, F1) declaran `Generated/BalanceCurves_Generated.verse 🔒` como dep compile-time, pero el exporter (SPR-134) está en F3.** Bloqueo temporal real. Resuelto con split: nuevo SPR-204 (F1) entrega curvas mínimas (XP + rebirth thresholds); SPR-134 (F3) reducido a curvas F3+.

### Changed
- **`SPRINTS_BACKLOG.md` cabecera**: añadida nota M1 explicando el split.
- **`SPRINTS_BACKLOG.md` SPR-044 deps**: `SPR-012, SPR-043` → `SPR-012, SPR-043, SPR-204`.
- **`SPRINTS_BACKLOG.md` SPR-048 deps**: `SPR-044, SPR-047` → `SPR-044, SPR-047, SPR-204`.
- **`SPRINTS_BACKLOG.md` SPR-134**: scope reducido a "curvas F3+ (pity, reroll, equipment leveling, base level)" + dep nueva `SPR-204`. Tiempo estimado mantiene 2h (el scope reducido se compensa con el trabajo de coordinación con SPR-204).
- **`SPRINTS_BACKLOG.md` total final**: 203 → 204 sprints. Tiempo: ~305h → ~306h.

### Added
- **`SPRINTS_BACKLOG.md` §10 nueva**: "Sprints añadidos post-planning". Sección destinada a IDs ≥ SPR-204 que no encajan visualmente en F0–F5 pero declaran su fase funcional. Aclaración explícita: la fase indica cuándo se ejecuta, no posición visual en el doc.
- **SPR-204 (nuevo)**: "BalanceCurves_Generated mínimo (XP curve + rebirth thresholds)". Fase F1. Deps: SPR-004, SPR-043, SPR-047. Tipo: python. Tiempo: 1h. Genera `Generated/BalanceCurves_Generated.verse` con las 2 curvas críticas para F1, dejando el resto a SPR-134.

### Verified — no se aplica fix (afirmación correcta confirmada contra fuentes)
- **M1-FP1** — sospecha "splittear como SPR-134a / SPR-134b". Re-verificación contra SPRINTS_BACKLOG §9.4 (regla refactor): la regla permite ambas opciones (sub-sprints **o** IDs nuevos). Para este caso, **ID nuevo es preferible** porque (1) `SPR-134a/b` sugiere relación secuencial — aquí queremos cosas en fases distintas, (2) el patrón de sub-sprints es para "sprint que crece >2h", no para "split por fase". ID nuevo independiente es más limpio.
- **M1-FP2** — sospecha "adelantar SPR-134 entero a F1". Re-verificación: arrastra trabajo F3 cuyas dependencias (`pity_config.json`, `reroll.json`, `equipment_leveling.json`) aún no existen en F1. Mal scope. SPR-204 con scope mínimo es lo correcto.
- **M1-FP3** — sospecha "permitir hardcoded constants en SPR-044 con TODO migración a SPR-134". Re-verificación: contradice regla "JSON-first / no hardcode en Verse" del proyecto. SPR-204 mantiene la convención.

### Decisions
- **D-A11 (Auditoría 2 — M1)**: el exporter de curvas de balance se split en 2 sprints por necesidad temporal. **SPR-204 (F1)**: curvas mínimas requeridas por F1 (XP curve + rebirth thresholds). **SPR-134 (F3)**: curvas restantes (pity, reroll, equipment leveling, base level). Ambos contribuyen al mismo `Generated/BalanceCurves_Generated.verse` — SPR-204 lo crea con 2 secciones, SPR-134 lo extiende con las 4 restantes. **Razón aplicada**: respeta regla "JSON-first" sin bloquear F1 por trabajo F3, mantiene el patrón generador único (un único `.verse` por concepto), y minimiza el scope adelantado al estrictamente necesario para desbloquear F1.

### Docs (resumen archivos tocados)
- 1 doc autoritativo modificado para M1:
  - `SPRINTS_BACKLOG.md` (472 → 488 líneas, +16 — cabecera + 3 SPRs ajustados + §10 nueva con SPR-204)
- Schema de persistencia: **sin cambios**.
- **C1, C2, C3, C4, M1 cerrados.** Faltan: M3, m2, Cn1.

---

## 🔧 Auditoría 2 — M3 + m2 + Cn1 (mayo 2026, cierre final)

> **Patch consolidado de los 3 hallazgos restantes**: M3 (LoadPlayerData wrapper), m2 (schema player_stats_base), Cn1 (FOLDER_STRUCTURE_TRUTH:341 init central). Patches pequeños agrupados.

### Changed
- **`API_REFERENCE_GENERATED.md` §3.4** (M3): añadidos 2 wrappers agregadores `LoadPlayerData(InPlayer)` y `SavePlayerData(InPlayer)` que invocan las 4 funciones específicas en secuencia. Mantienen las 4 individuales para acceso lazy/selectivo. Nota explícita sobre el coste de Save full (4 weak_map writes consecutivos).
- **`CONCEPT.md` §13.3 SPR-008 done** (M3): done criteria reescrito. Antes: solo `LoadPlayerData/SavePlayerData`. Ahora: 4 funciones individuales + 2 wrappers agregadores explícitos. Nota M3 explicativa.
- **`FOLDER_STRUCTURE_TRUTH.md` línea 341** (Cn1): `GameManager.verse (root device, init central)` → `GameManager.verse (root device, entry point: orquesta Init de Systems en OnBegin)`. Aclaración consistente con CONCEPT §11.1 + API_REFERENCE §10 + MODULES §9.1 v2.
- **`SYSTEMS_INDEX.md` §4.1** (m2): entry de `player_stats_base.json` actualizada con ref al schema recién creado en `JSON_SCHEMAS.md` §44.
- **`JSON_SCHEMAS.md` índice**: añadida entrada §44 player_stats_base. Renumerados §45 (Validación cruzada) y §46 (Cómo extender).
- **`JSON_SCHEMAS.md` sub-secciones §45 y §46**: renumeradas internamente (`§44.1 Tabla referencias` → `§45.1`, `§45.1/2/3` → `§46.1/2/3`).

### Added
- **`JSON_SCHEMAS.md` §44 nueva** (m2): spec completa de `player_stats_base.json` con 5 sub-secciones (schema, ejemplo concreto con 6 stats, validaciones, coherencia cross-doc con `PERSISTENCE_MAP.md` §3.1, política de cambios). Confirma los 6 stats del proyecto (HP_Max, Stamina_Max, Strength, Speed, Intelligence, Luck) como REQUIRED y exhaustivos.

### Verified — no se aplica fix (afirmación correcta confirmada contra fuentes)
- **M3-FP1** — sospecha "eliminar las 4 funciones separadas, dejar solo `LoadPlayerData` agregador". Re-verificación: **falso positivo**. Las 4 individuales son necesarias para (1) lazy loading (ej. `AdminPanel` solo necesita PlayerCore), (2) save selectivo tras cambio puntual (más eficiente que Save full). Mantener ambas formas es lo correcto.
- **m2-FP1** — sospecha "añadir validación cruzada player_stats_base ↔ PlayerCore en JSON_SCHEMAS §45". Re-verificación: innecesario. Los 6 campos son los mismos por construcción (`PlayerStats_Generated.verse` lee del JSON; `PlayerCore` los persiste). Sin duplicación de datos → sin riesgo de drift cross-file. La coherencia se documenta en §44.4 narrativamente, sin necesitar entry en tabla §45.1.
- **Cn1-FP1** — sospecha "hay más menciones residuales del modelo viejo en otros docs satélite". Re-verificación con grep `init central` + `init centralizado` + `self-register` + `orquesta Core` + `orden de carga predecible` en los 22 docs: **0 ocurrencias residuales** tras este patch. Auditoría 2 cerrada limpiamente.

### Decisions
- **D-A12 (Auditoría 2 — M3)**: `PersistenceLayer` expone **6 funciones de Load + 6 de Save**: las 4 funciones individuales tipadas (`LoadPlayerCore` etc.) por bucket + 2 wrappers agregadores (`LoadPlayerData` / `SavePlayerData`). Razón: balance entre conveniencia (1 call desde GameManager.OnPlayerSpawn) y eficiencia (acceso lazy/selectivo cuando solo hace falta 1 bucket). Los wrappers SON el patrón recomendado para spawn/logout; las individuales para writes incrementales y reads parciales.

### Docs (resumen archivos tocados)
- 6 docs autoritativos modificados para M3 + m2 + Cn1:
  - `API_REFERENCE_GENERATED.md` (437 → 444 líneas, +7 — 2 wrappers en §3.4)
  - `JSON_SCHEMAS.md` (2076 → ~2185 líneas, +~109 — nueva §44 player_stats_base + renumeración §45/§46)
  - `FOLDER_STRUCTURE_TRUTH.md` (651 → 651 líneas, sin Δ — clarificación en línea 341)
  - `CONCEPT.md` (1533 → 1535 líneas, +2 — SPR-008 done)
  - `SYSTEMS_INDEX.md` (300 → 300 líneas, sin Δ — actualización en línea 241)
  - `CHANGELOG.md` (esta entrada)
- Schema de persistencia: **sin cambios**.
- **TODOS los hallazgos de Auditoría 2 cerrados**: ✅ C1 ✅ C2 ✅ C3 ✅ C4 ✅ M1 ✅ M3 ✅ m2 ✅ Cn1. Falsos positivos descartados: M2, m1.

---

## ✅ Cierre Auditoría 2 (mayo 2026, viabilidad lógica e integración)

**Estado**: completa. **9 hallazgos evaluados (4 críticos + 3 medios + 2 menores), 8 aplicados (C1, C2, C3, C4, M1, M3, m2, Cn1) y 2 verificados como falsos positivos sin necesidad de fix (M2 BigNumbers etiquetas, m1 BaseLevel/BaseUpgrades). 5 decisiones nuevas registradas (D-A7 a D-A12). Schema Version sin bump. Total docs autoritativos modificados: 9 únicos (algunos tocados múltiples veces).**

**Falsos positivos descartados durante el proceso**: 14 documentados con re-verificación oficial Epic + protocolo anti-falso-positivo aplicado en cada patch. Lección: ~30% del bruto detectado eran falsos positivos — coherente con el 25% de Auditoría 1.

**Próximo**: Auditoría 3 (rendimiento + economía + compliance Epic IIT). El proyecto está libre de errores de sintaxis y tiene arquitectura lógicamente viable. Auditoría 3 evaluará exploits matemáticos, riesgos de rechazo en publicación Epic y cuellos de botella runtime con múltiples Companions/teleports.

---

## ✅ Cierre Auditoría 1 (mayo 2026, viabilidad técnica)

**Estado**: completa. **12 desviaciones evaluadas, 7 aplicadas (D-01, D-02, D-04, D-05, D-06, D-09, D-11), 5 verificadas como ya correctas (D-03, D-08, D-10, D-12) o aclaradas con fuente añadida sin cambio de afirmación. 6 decisiones nuevas registradas (D-A1 a D-A6). Schema Version sin bump.**

Próximo: Auditoría 2 (lógica de integración), Auditoría 3 (rendimiento + economía + compliance).

---

## [v0.0] — 2026-05-XX — Bootstrap de documentación

> **Estado inicial del proyecto: solo documentación. No hay código todavía.**

### Added
- Sistema de documentación completo (12+ archivos).
- `CONCEPT.md` — documento maestro con visión, sistemas, fases, sprints, decisiones cerradas.
- `PROMPT.md` — prompt agnóstico de modelo IA.
- `WORKFLOW.md` — workflow Opus + Tú + DeepSeek.
- `PROMPT_TEMPLATES.md` — plantillas listas para copiar.
- `DEEPSEEK_CAPSULE.md` — cápsula corta para DeepSeek.
- `API_REFERENCE_GENERATED.md` — placeholder de APIs públicas (todas 🚧 pendientes).
- `BOOTSTRAP_PIPELINE.md` — pipeline JSON → Python → Verse.
- `PERSISTENCE_MAP.md` — schemas de los 4 weak_maps.
- `UI_UX_STYLE_GUIDE.md` — paleta, tipografía, mobile rules, Activity Log specs.
- `TESTING_PROTOCOL.md` — sistema de test_devices temporales.
- `EMERGENCY_ROLLBACK.md` — protocolos de emergencia.
- `README.md` — índice de documentación.
- `JSON_SCHEMAS.md` — schemas formales de TODOS los JSONs del proyecto.
- `BALANCE_FORMULAS.md` — fórmulas y curvas de balance con justificación.
- `GLOSSARY.md` — glosario standalone.
- `CHANGELOG.md` — este documento.
- `POSTMORTEMS_INDEX.md` — índice de postmortems (vacío inicialmente).
- `DAILY_LOG.md` — log activo del día actual.

### Decisions (de CONCEPT.md sección 14)
- **Género**: Survival Tycoon con coleccionismo de ayudantes. Solo PvE.
- **Multiplayer**: 1–8 jugadores por sesión.
- **Plataforma**: Fortnite (PC, consola, móvil) vía UEFN.
- **Modelo monetización**: Dual-currency (Gemas + V-Bucks). Gemas no se convierten a V-Bucks.
- **Regla universal**: casi todo lo comprable también es ganable.
- **Items pagados con V-Bucks**: NUNCA tradables.
- **Lootboxes**: solo gemas, drop rates visibles, pity por (alma_type, rarity_target).
- **Trading**: directo same-session + auction same-session (NPC vendor).
- **Rebirth rápido**: primer rebirth en 20–30 min.
- **Skill points**: 5 ramas (Combate, Recolección, Supervivencia, Coleccionista, Economía).
- **Death penalty**: pierdes % XP del nivel actual + % gold no depositado. NO pierdes gemas, ayudantes, items, quests.
- **Rarezas (8 tiers)**: Common, Uncommon, Rare, Epic, Legendary, Mythic, Secret, Admin.
- **Equipment**: 6 ranuras invisibles. Tiers 1–10 con fail-rate progresivo.
- **Daily quests**: 3. **Weekly quests**: 9. Reset UTC.
- **Hourly boss**: HH:00, ventana 2 min, teleport HH:02.
- **Shop session**: rotación cada 30 min sincronizada UTC.
- **Base level**: eje permanente, NO se resetea con rebirth.
- **Persistencia**: 4 weak_maps × 128 KB (PlayerCore, PlayerInventory, PlayerProgress, PlayerEconomy).
- **Optimización móvil**: World Partition + HLODs + 512×512 max textures + LODs + HISM + 1 mat per mesh.

### Docs
- Estructura de carpetas definida en CONCEPT.md sección 11.
- Catálogo de 72 sistemas (SYS-001 a SYS-072) en CONCEPT.md sección 10.
- Plan por fases F0 a F5 en CONCEPT.md sección 12.
- Backlog inicial Fase 0 (SPR-001 a SPR-010) en CONCEPT.md sección 13.

---

## [v0.0.1-docs] — 2026-05-05 — Refactor mayor de documentación (sin código todavía)

> **Trabajo de auditoría y consolidación de docs antes de empezar SPR-001.**
> **No hay código nuevo.** Solo cambios en `.md`. Cero riesgo runtime.

### Added
- **`SYSTEMS_INDEX.md`** — catálogo autoritativo de los 72 `SYS-xxx` con fase, JSON, Verse principal, sprint asignado, bucket de persistencia, estado.
- **`SPRINTS_BACKLOG.md`** — backlog completo `SPR-001` a `SPR-203` distribuido en F0–F5, con dependencias declaradas, archivos a tocar y tiempos estimados.
- **`FOLDER_STRUCTURE_TRUTH.md`** — árbol único autoritativo de `data/`, `Content/Verse/`, `scripts/`, `docs/`. Resuelve 35 rutas inconsistentes detectadas en auditoría. Incluye spec de validador Python (`scripts/tools/folder_structure_validator.py`) y reglas de naming.
- **`MODULES_DEPENDENCY_GRAPH.md`** — grafo de capas (0→5) entre los 83 módulos Verse, deps `📤` y consumidores `📥` por módulo, top 10 críticos, eventos runtime catalogados, validador Python de ciclos.
- **`PROMPT.md` §Tu rol** — tabla de jerarquía de fuentes (10 docs autoritativos por área).

### Changed
- **`README.md`** — actualizado de "11 docs" a 22 docs reales con mapa mental + tabla de mantenimiento + lista alfabética. Aclarado en §Quick start §4 que el validador es spec, no archivo existente (M22).
- **`PROMPT.md`** — cabecera ampliada con 5 docs obligatorios + 5 secundarios. Tipos de petición reescritos (lee SPRINTS_BACKLOG, cruza con SYSTEMS_INDEX/FOLDER_STRUCTURE_TRUTH/MODULES_DEPENDENCY_GRAPH/PERSISTENCE_MAP en lugar de "CONCEPT §9"). Workflow ASCII actualizado. Frases-tipo con refs corregidas. Frase nueva para conflictos entre docs.
- **`CONCEPT.md` §11.1** — listado de `docs/` ampliado de 5 a 20 entradas reales. Eliminados archivos fantasma `ARCHITECTURE.md` y `SPRINTS.md`. Añadida nota redirect a `FOLDER_STRUCTURE_TRUTH.md` como fuente autoritativa.
- **`SYSTEMS_INDEX.md` §3.1** — fases recalibradas según `CONCEPT.md` §12.2 (era la fuente correcta). Cambios: SYS-008 F2→F1, SYS-023→028 F2→F3, SYS-032→035 F2→F3, SYS-040,041 F2→F4, SYS-042 F2→F4/F5, SYS-047 F2→F5, SYS-051→056 F2→F3, SYS-059→063 F1/F2→F4, SYS-066 F2→F4. Leyenda ⚙️ para sistemas anticipados con scope reducido.
- **`SYSTEMS_INDEX.md` §3.2** — buckets de persistencia recalibrados según `PERSISTENCE_MAP.md` §3–§6 (autoritativo). Cambios principales: SYS-015 Dex Progress→Inventory, SYS-016 XP / SYS-017 Skill Points / SYS-020 Rebirth / SYS-029 Gold / SYS-030 Gems / SYS-059 Base Level → Core (no Progress/Economy). SYS-005 Base Building / SYS-060 Upgrades / SYS-061 Generators / SYS-063 Crafting Timers → Economy. Tabla con 4 columnas (presupuesto reservado vs uso real calculado).
- **`JSON_SCHEMAS.md` §29.2 Battle Pass** — validación obsoleta `if total_levels > 64` reemplazada por cap dual: `<=192` (técnico) y `<=MAX_BP_LEVELS` (diseño).
- **`BOOTSTRAP_PIPELINE.md` §4.3** — confirmado script único `02_export_constants_to_verse.py` con funciones internas (no múltiples scripts). Tabla actualizada. STEPS del orquestador consolidado.
- **`BOOTSTRAP_PIPELINE.md` §4.4** — patrón de naming `*_Generated.verse` formalizado como decisión cerrada con regla canónica + lista de excepciones documentadas (`ModuleRegistryConstants.verse`).
- **`MODULES_DEPENDENCY_GRAPH.md`** — sintaxis de imports corregida: `import { X } from /Verse.org/...` → `using { /Verse.org/... }` (S8).
- **`SPRINTS_BACKLOG.md` SPR-001** — incluye explícitamente la materialización del validador `scripts/tools/folder_structure_validator.py`. Tiempo 1h → 1.5h.

### Removed
- **`JSON_SCHEMAS.md` §14 prices.json** — convertido en tombstone redirect. Esquema fusionado en `shop.json` (§15) para eliminar `price_ref` cross-file.
- **`prices.json` como archivo independiente** — ya no debe crearse. El validador (SPR-003) debe fallar si lo encuentra.
- **Referencias fantasma en `CONCEPT.md` §11.1** — `ARCHITECTURE.md` (a generar en fase técnica) y `SPRINTS.md` (extracto del backlog) eliminados; sus funciones las cumplen `MODULES_DEPENDENCY_GRAPH.md` y `SPRINTS_BACKLOG.md` respectivamente.

### Fixed
- **C1** — Conflicto de fases entre CONCEPT §12.2 y SYSTEMS_INDEX. Aplicada jerarquía: CONCEPT manda en fases. 13 sistemas reasignados.
- **C2** — Conflicto de buckets entre PERSISTENCE_MAP y SYSTEMS_INDEX. Aplicada jerarquía: PERSISTENCE_MAP manda en buckets. 12 sistemas reasignados.
- **C4** — `prices.json` separado eliminado de JSON_SCHEMAS y BOOTSTRAP_PIPELINE.
- **C5** — Naming Verse generados unificado a `*_Generated.verse` en BOOTSTRAP_PIPELINE (16 refs), JSON_SCHEMAS (1 ref), WORKFLOW (1 ref).
- **C6** — Pipeline `02_export_*` consolidado a un único `02_export_constants_to_verse.py`.
- **S7** — BP bitfield 64 niveles ampliado a 192 (3 ints `_A`/`_B`/`_C` para free + 3 para premium). Soporta los 100 niveles del diseño con 92 de margen. `MAX_BP_LEVELS=100` añadido a `BALANCE_FORMULAS.md` §2.1.
- **S8** — Sintaxis Verse `import { X } from` (incorrecta) → `using { /path }` (correcta).
- **S9** — Pesos de buckets en SYSTEMS_INDEX §3.2 distinguen ahora **presupuesto reservado** (PERSISTENCE_MAP §2) de **uso real calculado** (PERSISTENCE_MAP §7). Margen consolidado 99% libre típico / 97% worst-case.
- **S10** — PROMPT.md no mencionaba los 4 docs autoritativos nuevos. Cabecera, tipos de petición, workflow, referencias, frases-tipo y inicio de sesión actualizados.
- **S11** — `glossary.md` (minúsculas) → `GLOSSARY.md` (mayúsculas, real en disco). Linux es case-sensitive.
- **S12** — Archivos fantasma `ARCHITECTURE.md` y `SPRINTS.md` eliminados de CONCEPT §11.1.
- **M22** — README aclaraba que el validador `folder_structure_validator.py` debía ejecutarse cuando aún era código de referencia, no archivo en disco.

### Persistence
- ✨ **Schema Version SIN bump** — los cambios de bucket en `SYSTEMS_INDEX.md` §3.2 son re-clasificaciones documentales. Los schemas reales en `PERSISTENCE_MAP.md` §3–§6 NO han cambiado. Backwards-compat preservada al 100%.
- **BP bitfield ampliado** en `PERSISTENCE_MAP.md` §5.1: `BP_FreeRewardsClaimed` (1 int) → `BP_FreeRewardsClaimed_A/_B/_C` (3 ints), idem premium. **Cambio aplicado antes de SPR-008** (Persistence Layer aún no implementada). No hay datos persistidos que migrar. Schema Version inicial seguirá siendo 1.

### Docs
- Auditoría completa cruzando 22 docs. **23 inconsistencias detectadas, 13 críticas/serias resueltas, 10 menores skipped o pendientes** (ver detalle en respuestas de la sesión).
- Establecida **jerarquía de fuentes** explícita en `PROMPT.md` y reglas de mantenimiento en cada doc autoritativo (§5 de SYSTEMS_INDEX, §9 de FOLDER_STRUCTURE_TRUTH, §10 de MODULES_DEPENDENCY_GRAPH).

### Decisions
- **Naming archivos generados Verse**: `*_Generated.verse` (decisión cerrada, ver `BOOTSTRAP_PIPELINE.md` §4.4). Excepción documentada: `ModuleRegistryConstants.verse`.
- **Pipeline export**: un único script `02_export_constants_to_verse.py` con funciones internas. Re-evaluar al cierre de F3 si tarda >30s.
- **Jerarquía de fuentes**: en conflicto entre docs, gana el más específico, no CONCEPT. CONCEPT se actualiza después.
- **`prices.json` eliminado**: precios viven inline en `ShopItem` de `shop.json`.

---

## [v0.0.2] — 2026-05-07 — SPR-209: PowerShell-first toolchain rule

### Added
- Sección `PROMPT.md §6` con reglas duras: NO `python -c`, NO `&&`, NO heredocs. Renumeradas §7+ en cascada (§6 Lenguaje → §7, §7 Cuando crear archivos → §8).
- Línea en `DEEPSEEK_CAPSULE.md` con regla shell condensada (regla 6 en cápsula corta).
- Sección `WORKFLOW.md §3.5` "Verificadores throwaway" con plantilla canónica.
- Carpeta `scripts/tools/_throwaway/` con `.gitkeep`. Gitignored (excepto `.gitkeep`).

### Decisions
- **D-A14 (SPR-209)**: PowerShell exclusivo asumido en toda recomendación de comandos. Verificadores ad-hoc viven en `_throwaway/` gitignored. Motivación: 2 días de fricción por one-liners rotos (auditoría empírica en cierre SPR-002 2026-05-06 tarde).

---

## [v0.1] — Pendiente — Cierre de Fase 0 (Foundation)

> **Sistemas core técnicos: Module Registry, Logger, TimeSync, PersistenceLayer, EventBus, AdminCommands.**

### Sprints planificados (de CONCEPT 13.3)
- [ ] SPR-001 — Setup del repo y carpetas
- [ ] SPR-002 — JSON schemas base
- [ ] SPR-003 — Python: validador de JSONs
- [ ] SPR-004 — Python: exporter a constantes Verse
- [ ] SPR-005 — Verse: Module Registry
- [ ] SPR-006 — Verse: Logger
- [ ] SPR-007 — Verse: Time Sync (UTC)
- [ ] SPR-008 — Verse: Persistence Layer
- [ ] SPR-009 — Verse: Event Bus interno
- [ ] SPR-010 — Verse: Admin Commands

### Sprints de test asociados (TESTING_PROTOCOL 4.3)
- [ ] SPR-005-T — Test Module Registry
- [ ] SPR-006-T — Test Logger
- [ ] SPR-007-T — Test TimeSync
- [ ] SPR-008-T — Test PersistenceLayer (incluye persistence test logout/login)
- [ ] SPR-009-T — Test EventBus
- [ ] SPR-010-T — Test AdminCommands

### Persistence (al completar SPR-008)
- [ ] Schema Version inicial: 1
- [ ] PlayerCore schema publicado (PERSISTENCE_MAP sección 3)
- [ ] PlayerInventory schema publicado (sección 4)
- [ ] PlayerProgress schema publicado (sección 5)
- [ ] PlayerEconomy schema publicado (sección 6)

### Done Criteria de Fase 0
- [ ] Build Verse Code OK sin warnings
- [ ] Smoke test master ejecuta y todos los smoke tests pasan
- [ ] Persistence test pasa logout/login
- [ ] Mobile Preview no crashea
- [ ] Pipeline Python ejecuta idempotentemente
- [ ] Git tag `v0.1-foundation-complete`

---

## [v1.0] — Pendiente — Cierre de Fase 1 (MVP playable)

> **Loop core: farmear, construir, combatir, subir nivel, primer rebirth, tutorial. PUBLICABLE.**

### Sistemas incluidos
SYS-001 a SYS-009 + SYS-016 + SYS-017 + SYS-020 + SYS-039 (parcial) + SYS-064 + SYS-065.

### Sprints estimados
SPR-011 a SPR-050 (~40 sprints).

### Done Criteria de Fase 1
- [ ] Loop core jugable end-to-end (farmear → mejorar → combatir → subir nivel → rebirth)
- [ ] Tutorial chain de 15 quests funcional
- [ ] First Minute Hook implementado
- [ ] Primer rebirth en 20–30 min para tester nuevo
- [ ] Mobile Preview FPS ≥30
- [ ] Persistence test exhaustivo (logout/login en cada checkpoint)
- [ ] Smoke test master ejecuta sin errors
- [ ] Memory budget dentro de threshold
- [ ] Git tag `v1.0-mvp` + Push Changes a Creator Portal
- [ ] **PUBLICABLE**

---

## [v2.0] — Pendiente — Companions & Collection (Fase 2)

> **Ayudantes coleccionables, Dex, skill trees completos.**

### Sistemas incluidos
SYS-010 a SYS-015 + SYS-018 + SYS-019 + SYS-021 + SYS-049 + SYS-050.

---

## [v3.0] — Pendiente — Economy & Equipment (Fase 3)

> **Battle Pass, equipo invisible, lootboxes, pity, trade, auction, todos los QoL.**

### Sistemas incluidos
SYS-022 a SYS-038 + SYS-051 a SYS-058.

---

## [v4.0] — Pendiente — Base persistente & Live Ops (Fase 4)

> **Daily login, time played, base completa, generadores offline, eventos, códigos, seasonal.**

### Sistemas incluidos
SYS-040 a SYS-046 + SYS-059 a SYS-063 + SYS-066.

---

## [v5.0] — Pendiente — Hourly Boss + Social + Polish (Fase 5)

> **Endgame, social display, leaderboards globales, segundo mapa con la máquina.**

### Sistemas incluidos
SYS-042 + SYS-047 + SYS-048 + polish global.

### Hito clave
- [ ] **Segundo mapa** producido cambiando solo JSONs y assets.
- [ ] Tiempo de producción del segundo mapa: ≤ 4 semanas.

---

## 📋 Plantilla de entrada (copiar para nuevos cambios)

```markdown
## [vX.Y.Z] — YYYY-MM-DD — <Título de la versión>

### Added
- SPR-XXX — Descripción del sprint completado. Archivos: `[paths]`.
- SPR-XXY — Descripción.

### Changed
- Refactor de `<archivo>` para [...]. Razón: [...]. (SPR-XXX)

### Fixed
- Bug donde [...]. Causa: [...]. Fix: [...]. (Postmortem ref: `docs/postmortems/YYYY-MM-DD_titulo.md`)

### Balance
- Ajuste de drop rate [rareza] de X% a Y%. Razón: [hipótesis]. (BALANCE_FORMULAS sección N.M)
- Cambio de coste reroll. Razón: [hipótesis].

### Persistence
- ✨ **Schema Version bump 1 → 2.**
- Añadido campo `PlayerCore.NewField:int = 0` con default. Backwards-compat OK.
- Validación defensiva añadida en `LoadPlayerCore`.

### Decisions
- Decisión nueva: [...]. Razón: [...]. (Reflejado en CONCEPT.md sección 14.X)

### Docs
- Actualizado JSON_SCHEMAS.md sección N para reflejar [cambio].
- Añadida sección N.M en BALANCE_FORMULAS.md.

### Removed
- ⚠️ Eliminado `<archivo>`. Razón: [...]. **Verificar que no rompe nada.**

### Deprecated
- Campo `OldField` en PlayerCore marcado como DEPRECATED v3. No escribir, solo leer para migración.
```

---

## 🔧 Mantenimiento de este CHANGELOG

### Frecuencia mínima de actualización
- **Por sprint**: 1 entrada en `[Unreleased]`.
- **Por cierre de fase**: mover `[Unreleased]` → versión, generar tag Git.
- **Por cambio delicado**: entrada inmediata + commit con `CHANGELOG: <descripcion>`.

### Quién lo actualiza
- **DeepSeek**: añade entrada al terminar un sprint (parte de done criteria).
- **Tú**: revisas la entrada al hacer commit del sprint.
- **Opus**: valida CHANGELOG al cierre de fase (auditar que todo está reflejado).

### Cómo verificar que CHANGELOG está sincronizado
```bash
# Comparar últimos commits con entradas del CHANGELOG
git log --oneline | head -20

# Si hay commits sin entrada en CHANGELOG → añadirlas
```

### Anti-patrón: no escribir en CHANGELOG
Si pasan 3+ sprints sin entrada → el CHANGELOG pierde su valor. **Disciplina o no sirve.**

---

## 📌 Resumen ejecutivo

```
🎯 ESTE DOCUMENTO ES EL REGISTRO CONSOLIDADO de cambios.

🔑 ACTUALIZACIÓN OBLIGATORIA:
   - Por sprint completado → entrada en [Unreleased]
   - Por cierre de fase → mover a versión + tag Git
   - Por cambio de balance → sección Balance + ref a BALANCE_FORMULAS.md
   - Por cambio de persistencia → sección Persistence + Schema Version bump

📋 CATEGORÍAS:
   Added / Changed / Deprecated / Removed / Fixed / Security
   Balance / Persistence / Decisions / Docs

⚠️ SI 3+ SPRINTS SIN ENTRADA → SISTEMA ROTO. ARREGLAR.
```

---

**Fin del documento.**

> Mantenido vivo. Cualquier cambio significativo del proyecto debe reflejarse aquí.
