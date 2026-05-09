# 🏃 SPRINTS_BACKLOG — Backlog completo del proyecto

> **Fuente única de verdad para `SPR-xxx`.** ~203 sprints. Cada uno cabe en 1–2 h reales.
>
> Detalle de plantilla y filosofía → `CONCEPT.md` §13.1, §13.2.
> Mapeo sistema ↔ JSON ↔ Verse → `SYSTEMS_INDEX.md`.
>
> **Decisión cerrada (Auditoría 2 — C1)**: los 6 Core son singletons top-level estáticos. NO se auto-registran en `ModuleRegistry`. Por tanto **SPR-006/007/008/009/010 NO dependen de SPR-005** — solo dependen entre sí por usos compile-time de `using {}`. Detalle en `MODULES_DEPENDENCY_GRAPH.md` §2.1 + §4.7. SPR-005 (Registry) sigue en F0 pero su utilidad real arranca en F1 con los primeros Systems gameplay.
>
> **Decisión cerrada (Auditoría 2 — M1)**: SPR-134 originalmente generaba TODAS las curvas de balance, pero SPR-044/SPR-048 (F1) lo necesitan en F1. Split: **SPR-204** (nuevo, F1) genera curvas mínimas F1 (XP + rebirth thresholds); SPR-134 (F3) reducido a curvas F3+ (pity, reroll, equipment leveling, base level). Detalle en §10.

---

## 🧭 Índice

1. [Convenciones del backlog](#1-convenciones-del-backlog)
2. [Estado global](#2-estado-global)
3. [Fase 0 — Foundation (SPR-001 → SPR-010)](#3-fase-0--foundation)
4. [Fase 1 — MVP Playable (SPR-011 → SPR-050)](#4-fase-1--mvp-playable)
5. [Fase 2 — Companions & Collection (SPR-051 → SPR-083)](#5-fase-2--companions--collection)
6. [Fase 3 — Economy & Equipment (SPR-084 → SPR-136)](#6-fase-3--economy--equipment)
7. [Fase 4 — Base persistente & Live Ops (SPR-137 → SPR-176)](#7-fase-4--base-persistente--live-ops)
8. [Fase 5 — Hourly Boss + Social + Polish (SPR-177 → SPR-203)](#8-fase-5--hourly-boss--social--polish)
9. [Reglas de mantenimiento](#9-reglas-de-mantenimiento)

---

## 1. Convenciones del backlog

| Campo | Significado |
|---|---|
| **ID** | `SPR-xxx` único, inmutable. Nunca se reordena. |
| **Fase** | F0–F5. Coincide con `CONCEPT.md` §12.2. |
| **SYS** | Sistema(s) que toca, ref a `SYSTEMS_INDEX.md`. |
| **Tipo** | `verse` / `python` / `json` / `design` / `asset` / `docs` / `test`. |
| **Deps** | Sprints que deben estar `🟢 done` antes. |
| **Tiempo** | 1h / 1.5h / 2h. |
| **Estado** | `⚫ no empieza` / `🔴 pendiente` / `🟡 en curso` / `🟢 done` / `🚫 bloqueado`. |

**Done universal**: compila sin warnings + test in-session pasa + git commit con tag `SPR-xxx`.

---

## 2. Estado global

| Fase | Sprints | Tiempo total | Estado |
|---|---|---|---|
| **F0** | SPR-001 → SPR-010 (10) | ~15 h | ⚫ |
| **F1** | SPR-011 → SPR-050 (40) | ~60 h | ⚫ |
| **F2** | SPR-051 → SPR-083 (33) | ~50 h | ⚫ |
| **F3** | SPR-084 → SPR-136 (53) | ~80 h | ⚫ |
| **F4** | SPR-137 → SPR-176 (40) | ~60 h | ⚫ |
| **F5** | SPR-177 → SPR-203 (27) | ~40 h | ⚫ |
| **TOTAL** | **203 sprints** | **~305 h** | ⚫ |

---

## 3. Fase 0 — Foundation

> Motor base. Sin gameplay. Al terminar F0 hay persistencia + time sync + admin panel + module registry funcionando con módulos dummy.

| ID | Título | SYS | Tipo | Deps | Archivos clave | Tiempo |
|---|---|---|---|---|---|---|
| SPR-001 🟢 done | Setup repo, carpetas, .gitignore UEFN, .gitattributes, init_unreal.py, validador estructura | — | scaffolding+python | — | estructura completa según `FOLDER_STRUCTURE_TRUTH.md` (16 carpetas data/, 14 subcarpetas Verse, 4 subcarpetas scripts/), `README.md` **de raíz del repo** (apunta a `docs/` — NO sobrescribir `docs/README.md` que ya existe con 240 líneas), `.gitignore` (contenido en `EMERGENCY_ROLLBACK.md` §2.2 — copiar verbatim + añadir excepción `!.gitkeep` al final para que git trackee carpetas vacías), **`.gitattributes`** (estándar UEFN+Verse: `* text=auto eol=lf`, `*.verse text eol=lf`, `*.json text eol=lf`, `*.py text eol=lf`, `*.md text eol=lf`, `*.umap binary`, `*.uasset binary`, `*.png binary`, `*.jpg binary`, `*.fbx binary`), **`scripts/init_unreal.py`** (D-A6 — prepuebla `actor_sub`, `asset_sub`, `level_sub` siguiendo convención UEFN-TOOLBELT; contenido mínimo: `actor_sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)` + análogos para `asset_sub`/`level_sub`), `scripts/build/00_validate_structure.py` (copiado de FOLDER_STRUCTURE_TRUTH §8.2 — primer step del orquestador; **2 líneas defensa**: skip `.gitkeep` en chequeos `BAD_NAMING` y `UNDECLARED`), `.gitkeep` en cada carpeta vacía del árbol (estándar git para trackear estructura). **Nota crítica sobre validador**: tras SPR-001 el validador detectará ~204 archivos `MISSING` (correcto por diseño — los crean SPR-002+). Usar `python scripts/build/00_validate_structure.py --allow-missing` durante F0 → exit 0 esperado. Done F0 (línea 75) sí requiere exit 0 SIN flag al cierre de SPR-010. | 1.5h |
| SPR-002 | JSON schemas base + ejemplos | — | json+design | SPR-001 | `data/companions/companions_base.json`, `data/items/equipment.json`, `data/quests/tutorial_chain.json`, `data/theme/theme_config.json` | 2h |
| SPR-003 | Python validador de JSONs | — | python | SPR-002 | `scripts/build/01_validate_jsons.py` | 1.5h |
| SPR-004 | Python exporter constantes Verse (datos + arquitectura: Registry y EventBus) | — | python | SPR-002, SPR-003 | `scripts/build/02_export_constants_to_verse.py` (genera 12 archivos en `Generated/`: `Companions_Generated.verse`, `Items_Generated.verse`, `Prices_Generated.verse`, `Quests_Generated.verse`, `BattlePass_Generated.verse`, `PlayerStats_Generated.verse`, `SkillTree_Generated.verse`, `Achievements_Generated.verse`, `Localization_Generated.verse`, `ModuleRegistryConstants.verse`, `EventBusConstants.verse`, `EventPayloads_Generated.verse`. NO genera `ThemeConstants_Generated.verse` — eso lo hace `05_apply_theme_pack.py` SPR-170. NO genera `Zones_Generated.verse` — eso lo hace `04_generate_zone_layouts.py` SPR-041. `BalanceCurves_Generated.verse` queda fuera de SPR-004 base — SPR-204 lo añade en F1 con scope mínimo, SPR-134 lo extiende en F3 con scope completo) | 3h |
| SPR-005 | Verse Module Registry (lookup runtime para Systems Capa 2+; **NO orquesta Core**) | SYS-072 | verse | SPR-001, SPR-004, SPR-006 | `Content/Verse/Core/ModuleRegistry.verse` + `Generated/ModuleRegistryConstants.verse` (generado por SPR-004 ext, workaround `<T>`, ver MODULES §4.7) | 1.5h |
| SPR-006 🟢 done | Verse Logger (module namespace top-level — refactor SPR-211) | SYS-072 | verse | SPR-001 | `Core/Logger.verse` | 1h |
| SPR-007 🟢 done | Verse Time Sync UTC (module namespace, funciones `<decides>` — refactor SPR-211) | SYS-068 | verse | SPR-006 | `Core/TimeSync.verse` | 1.5h |
| SPR-008 🟢 done | Verse Persistence Layer (4 weak_maps) — done 2026-05-08 | SYS-069 | verse | SPR-006 | `Core/PersistenceLayer.verse`, `Tests/test_persistence_SPR008.verse` | 2h (real ~5h) |
| SPR-009 🟢 done | Verse Event Bus interno (creative_device + 2 generados desde `events_catalog.json` — patrón H4 post-F-C-2) | SYS-072 | verse | SPR-004, SPR-006 | `Core/EventBus.verse` (placeholder) + `Generated/EventBusDevice.verse` (creative_device generado por SPR-004 ext) + `Generated/EventPayloads_Generated.verse` (generado por SPR-004 ext) + `Tests/test_event_bus_smoke.verse` (smoke runtime) + `scripts/build/tests/test_exporter_event_bus.py` (golden contract 5 tests) | 1.5h (real ~6h con F-A rollback + F-B investigación + F-C refactor + F-C-3 tests) |
| SPR-010 | Verse Admin Commands + Panel | SYS-070 | verse+ui | SPR-006, SPR-008, SPR-009 | `Core/AdminCommands.verse`, `Devices/AdminPanel.verse` | 2h |

**Done F0**: 4 weak_maps cargan/guardan sin errores entre sesiones, admin panel solo visible si `AdminCommands.IsAdmin(Agent)` devuelve true (mecanismo `player_reference_device` configurado en editor — D-A13, no `player.GetID()` que no existe en Verse), log en HUD muestra ✅. Registry instanciado y verificado con módulos dummy de Systems (NO con Core — los Core son singletons top-level y no se registran). **Validador estructura**: `python scripts/build/00_validate_structure.py` (SIN flags) debe pasar con exit 0 al cierre de F0 (todos los archivos del árbol F0 existen, incluido `Content/Maps/Main.umap` creado por SPR-206). Durante SPR-001..SPR-009 + SPR-205 + SPR-206 el validador se corre con `--allow-missing` (auditoría retrospectiva — Bloque 5).

**Notas C1 + C3 (Auditoría 2)**:
- **SPR-005 ahora depende de SPR-006 y SPR-004**. El Registry usa Logger compile-time y `Generated/ModuleRegistryConstants.verse` (producido por SPR-004 ext). SPR-006 + SPR-004 entregan antes para desbloquear SPR-005.
- **SPR-007/008 dependen solo de SPR-006**. Cada uno usa Logger por `using {}`. NO usan Registry (los Core no se registran).
- **SPR-009 depende de SPR-004 y SPR-006** (C3 + H4): el EventBus operativo son 2 archivos generados (`EventBusDevice.verse` + `EventPayloads_Generated.verse`) producidos por SPR-004 ext desde `data/architecture/events_catalog.json`. **`EventBusDevice.verse` es un `creative_device`, NO singleton top-level** — patrón H4 forzado por err 3512 al instanciar `event(t){}` top-level (lección 16 VERSE_SYNTAX_GUIDE). Decisión D-A11 (excepción a D-A7). El `Core/EventBus.verse` source-controlled queda como placeholder mínimo. Detalle del patrón en `BOOTSTRAP_PIPELINE.md` §11. **Cierre 2026-05-08 (HEAD `6c90e45`)**: smoke runtime PASS, golden contract 5 tests PASS. Tags vivos: `SPR-009-blocked-2026-05-09` (fase 1 bloqueada), pendiente `SPR-009-resolved` al cerrar F-C-6.
- **SPR-004 absorbió las 3 funciones export de arquitectura** (`export_module_registry`, `export_event_payloads`, `export_event_bus`). Tiempo recalibrado 2h → 3h. Plantillas en `BOOTSTRAP_PIPELINE.md` §10.5 + §11.6.
- **SPR-010 (AdminCommands) depende de SPR-006, SPR-008, SPR-009**. No de SPR-005. AdminCommands no es un Systems registrable.
- **SPR-005/007/008/009 paralelizables** una vez SPR-004 + SPR-006 estén done.

**Notas SPR-211 (sintaxis Verse moderna)**:
- **SPR-006 / SPR-007 ya validados con build UEFN** usando patrón `Module<public> := module:` (namespace top-level). Patrón legacy `<x>_module := class<concrete>:` + `Singleton : x_module = x_module{}` falla con err 3512 en Verse moderno.
- **SPR-005 / SPR-009 / SPR-010**: el patrón concreto debe re-evaluarse durante implementación contra build UEFN real. Las plantillas legacy en CONCEPT/MODULES/BOOTSTRAP están marcadas como obsoletas (cross-ref a la guide).
- Autoridad sintáctica vigente: `docs/VERSE_SYNTAX_GUIDE.md`.

**Notas SPR-008 (cierre 2026-05-08)**:
- PersistenceLayer.verse con 4 buckets + 8 funciones validadas. Test in-session PASS. Caso de estudio §2.4 del VERSE_SYNTAX_GUIDE rellenado con patrón canónico.
- 2 lecciones nuevas añadidas al guide (14: file scope vs module scope; 15: set weak_map propaga decides).
- Tag final: `SPR-008`. Tags incrementales (debugging path): `SPR-008-step1` a `SPR-008-step3.5a`.

---

## 4. Fase 1 — MVP Playable

> Loop core publicable. Farmear → construir → combatir → subir nivel → primer rebirth → tutorial.

### 4.1 Player core (SPR-011 → SPR-018)

| ID | Título | SYS | Tipo | Deps | Archivos clave | Tiempo |
|---|---|---|---|---|---|---|
| SPR-011 | Schema y JSON `player_stats_base.json` | SYS-001 | json | SPR-002 | `data/progression/player_stats_base.json` | 1h |
| SPR-012 | PlayerStats.verse — HP, stamina, regen | SYS-001 | verse | SPR-008, SPR-011 | `Systems/Player/PlayerStats.verse` | 2h |
| SPR-013 | PlayerStats persistencia + load defensive | SYS-001, SYS-069 | verse | SPR-012 | (modifica PlayerStats + PersistenceLayer) | 1.5h |
| SPR-014 | Schemas inventory: resources/consumables | SYS-002 | json | SPR-002 | `data/items/resources.json`, `data/items/consumables.json` | 1.5h |
| SPR-015 | PlayerInventory.verse — slots + categorías | SYS-002 | verse | SPR-013, SPR-014 | `Systems/Player/PlayerInventory.verse` | 2h |
| SPR-016 | Inventory drag&drop + stack inteligente | SYS-002 | verse+ui | SPR-015 | (modifica PlayerInventory + UI) | 2h |
| SPR-017 | Inventory persistencia weak_map | SYS-002, SYS-069 | verse | SPR-016 | (modifica) | 1.5h |
| SPR-018 | InventoryUI básica (mobile-first) | SYS-002 | verse+ui | SPR-016 | `Systems/UI/InventoryUI.verse` | 2h |

### 4.2 Resource gathering + tools (SPR-019 → SPR-024)

| ID | Título | SYS | Tipo | Deps | Archivos clave | Tiempo |
|---|---|---|---|---|---|---|
| SPR-019 | Schema resources + drop rates | SYS-003 | json | SPR-014 | `data/items/resources.json` (extendido) | 1h |
| SPR-020 | ResourceNodes.verse — interaction trigger | SYS-003 | verse | SPR-015 | `Systems/World/ResourceNodes.verse` | 2h |
| SPR-021 | Tools system (chop/mine/harvest) | SYS-003 | verse | SPR-020 | (modifica ResourceNodes + Inventory) | 2h |
| SPR-022 | Tool wear & upgrade | SYS-003 | verse | SPR-021 | (modifica) | 1.5h |
| SPR-023 | Drop on resource → inventory flow | SYS-003 | verse+test | SPR-021 | test_device | 1h |
| SPR-024 | Visual feedback + sounds resource gathering | SYS-003 | asset+verse | SPR-021 | (UEFN) | 1.5h |

### 4.3 Crafting básico (SPR-025 → SPR-030)

| ID | Título | SYS | Tipo | Deps | Archivos clave | Tiempo |
|---|---|---|---|---|---|---|
| SPR-025 | Schema `recipes.json` | SYS-004 | json | SPR-002 | `data/items/recipes.json` | 1h |
| SPR-026 | Crafting validator (Python) | SYS-004 | python | SPR-003, SPR-025 | (extiende validate_jsons) | 1h |
| SPR-027 | Crafting executor en Verse | SYS-004 | verse | SPR-015, SPR-025 | (parte de Inventory) | 2h |
| SPR-028 | UI de crafting (recipe list + craft button) | SYS-004 | verse+ui | SPR-027 | `Systems/UI/CraftingUI.verse` | 2h |
| SPR-029 | Validación de requisitos visual | SYS-004 | verse | SPR-028 | (modifica CraftingUI) | 1h |
| SPR-030 | Test_device crafting flow completo | SYS-004 | test | SPR-028 | test_device | 1h |

### 4.4 Base building (SPR-031 → SPR-034)

| ID | Título | SYS | Tipo | Deps | Archivos clave | Tiempo |
|---|---|---|---|---|---|---|
| SPR-031 | Schema `building_pieces.json` | SYS-005 | json | SPR-002 | `data/base/building_pieces.json` | 1h |
| SPR-032 | BasePlot device + placement system | SYS-005 | verse | SPR-008 | `Devices/BasePlot.verse` | 2h |
| SPR-033 | Base pieces snap + upgrades | SYS-005 | verse | SPR-032 | `Systems/Base/BaseUpgrades.verse` | 2h |
| SPR-034 | Persistencia base pieces (sobrevive rebirth) | SYS-005, SYS-069 | verse | SPR-033 | (modifica) | 1.5h |

### 4.5 Combat core (SPR-035 → SPR-038)

| ID | Título | SYS | Tipo | Deps | Archivos clave | Tiempo |
|---|---|---|---|---|---|---|
| SPR-035 | Schema `damage_formulas.json` (en `data/combat/`) | SYS-006 | json | SPR-002 | `data/combat/damage_formulas.json` | 1.5h |
| SPR-036 | DamageCalculator.verse | SYS-006 | verse | SPR-012, SPR-035 | `Systems/Combat/DamageCalculator.verse` | 2h |
| SPR-037 | CombatCore.verse + hit detection | SYS-006 | verse | SPR-036 | `Systems/Combat/CombatCore.verse` | 2h |
| SPR-038 | Death flow + respawn básico | SYS-006, SYS-009 | verse | SPR-037 | (parte de CombatCore + PlayerDeathHandler.verse) | 1.5h |

### 4.6 Zone unlock + 1ª zona (SPR-039 → SPR-042)

| ID | Título | SYS | Tipo | Deps | Archivos clave | Tiempo |
|---|---|---|---|---|---|---|
| SPR-039 | Schemas `zone_definitions.json` + `unlock_gates.json` | SYS-007 | json | SPR-002 | `data/zones/*.json` | 1.5h |
| SPR-040 | ZoneManager.verse + ZonePortal device | SYS-007 | verse | SPR-008, SPR-039 | `Systems/World/ZoneManager.verse`, `Devices/ZonePortal.verse` | 2h |
| SPR-041 | Python `04_generate_zone_layouts.py` (Poisson disk) | SYS-007 | python | SPR-040 | `scripts/build/04_generate_zone_layouts.py` | 2h |
| SPR-042 | Zona inicial poblada + test | SYS-007 | asset+test | SPR-041 | (UEFN) | 2h |

### 4.7 XP, Levels, Skill Points (SPR-043 → SPR-046)

| ID | Título | SYS | Tipo | Deps | Archivos clave | Tiempo |
|---|---|---|---|---|---|---|
| SPR-043 | Schemas `xp_curves.json` + `skill_points.json` | SYS-016, SYS-017 | json | SPR-002 | `data/progression/*.json` | 1h |
| SPR-044 | PlayerProgression.verse — XP gain + level up | SYS-016 | verse | SPR-012, SPR-043, SPR-204 | `Systems/Player/PlayerProgression.verse` | 2h |
| SPR-045 | Skill points distribución básica | SYS-017 | verse | SPR-044 | (parte de Progression) | 1.5h |
| SPR-046 | Level up notification + UI | SYS-016, SYS-050 | verse+ui | SPR-044 | (parte de HUD) | 1h |

### 4.8 Rebirth + Tutorial + First Minute Hook (SPR-047 → SPR-050)

| ID | Título | SYS | Tipo | Deps | Archivos clave | Tiempo |
|---|---|---|---|---|---|---|
| SPR-047 | Schema `rebirth_rewards.json` | SYS-020 | json | SPR-002 | `data/progression/rebirth_rewards.json` | 1h |
| SPR-048 | PlayerRebirth.verse — flow completo | SYS-020 | verse | SPR-044, SPR-047, SPR-204 | `Systems/Player/PlayerRebirth.verse` | 2h |
| SPR-049 | Tutorial chain (15 quests) + QuestEngine v1 | SYS-039, SYS-065 | verse+json | SPR-008 | `data/quests/tutorial_chain.json`, `Systems/Quests/QuestEngine.verse`, `TutorialChain.verse` | 2h |
| SPR-050 | First Minute Hook — spawn impactante | SYS-064 | verse+asset | SPR-049 | `data/onboarding/first_minute.json` | 2h |

**Done F1**: jugador puede entrar, completar tutorial, hacer 1 rebirth, todo persiste tras logout. Mapa publicable.

---

## 5. Fase 2 — Companions & Collection

> Ayudantes, Dex, skill trees, achievements, notif log. Profundidad core.

### 5.1 Companion core (SPR-051 → SPR-058)

| ID | Título | SYS | Tipo | Deps | Archivos clave | Tiempo |
|---|---|---|---|---|---|---|
| SPR-051 | Schema `companions_base.json` (300+ entradas) | SYS-010 | json | SPR-002 | `data/companions/companions_base.json` | 2h |
| SPR-052 | Schema `rarities.json` + `variants.json` | SYS-011, SYS-012 | json | SPR-051 | `data/companions/rarities.json`, `variants.json` | 1.5h |
| SPR-053 | CompanionCore.verse — clase base + stats | SYS-010 | verse | SPR-008, SPR-051 | `Systems/Companions/CompanionCore.verse` | 2h |
| SPR-054 | Variants multiplicadores + display | SYS-012 | verse | SPR-053 | (parte de CompanionCore) | 1.5h |
| SPR-055 | Schema `evolutions.json` + Evolution logic | SYS-013 | json+verse | SPR-053 | `data/companions/evolutions.json` | 2h |
| SPR-056 | Schema `behaviors.json` + CompanionBehavior.verse | SYS-014 | json+verse | SPR-053 | `Systems/Companions/CompanionBehavior.verse` | 2h |
| SPR-057 | Companion follow/attack/gather AI | SYS-014 | verse | SPR-056 | (modifica) | 2h |
| SPR-058 | CompanionAssignment.verse (asignar a tareas) | SYS-014 | verse | SPR-057 | `Systems/Companions/CompanionAssignment.verse` | 1.5h |

### 5.2 Collection Dex (SPR-059 → SPR-063)

| ID | Título | SYS | Tipo | Deps | Archivos clave | Tiempo |
|---|---|---|---|---|---|---|
| SPR-059 | Schema `dex_rewards.json` | SYS-015 | json | SPR-051 | `data/companions/dex_rewards.json` | 1h |
| SPR-060 | CollectionDex.verse — bitmask packing (5×int64) | SYS-015 | verse | SPR-008, SPR-053 | `Systems/Companions/CollectionDex.verse` | 2h |
| SPR-061 | DexUI con filtros + missing-only | SYS-015, SYS-055 | verse+ui | SPR-060 | `Systems/UI/DexUI.verse` | 2h |
| SPR-062 | Recompensas por % completado | SYS-015 | verse | SPR-060 | (modifica CollectionDex) | 1h |
| SPR-063 | Test_device Dex flow completo | SYS-015 | test | SPR-062 | test_device | 1h |

### 5.3 Skill Trees + Active Abilities (SPR-064 → SPR-070)

| ID | Título | SYS | Tipo | Deps | Archivos clave | Tiempo |
|---|---|---|---|---|---|---|
| SPR-064 | Schema `skill_trees.json` (5 ramas) | SYS-018 | json | SPR-043 | `data/progression/skill_trees.json` | 2h |
| SPR-065 | PlayerSkillTree.verse — estructura + persist | SYS-018 | verse | SPR-008, SPR-064 | `Systems/Player/PlayerSkillTree.verse` | 2h |
| SPR-066 | Skill tree UI con prerequisitos | SYS-018 | verse+ui | SPR-065 | (parte de UI) | 2h |
| SPR-067 | Aplicación de efectos pasivos a stats | SYS-018 | verse | SPR-065 | (modifica) | 1.5h |
| SPR-068 | Schema `abilities.json` | SYS-019 | json | SPR-064 | `data/progression/abilities.json` | 1h |
| SPR-069 | AbilityExecutor.verse — cooldowns + casts | SYS-019 | verse | SPR-068 | `Systems/Combat/AbilityExecutor.verse` | 2h |
| SPR-070 | Active abilities desbloqueables por zona | SYS-019 | verse | SPR-069, SPR-040 | (modifica) | 1.5h |

### 5.4 Day/Night, Achievements, Activity Log (SPR-071 → SPR-079)

| ID | Título | SYS | Tipo | Deps | Archivos clave | Tiempo |
|---|---|---|---|---|---|---|
| SPR-071 | Schema `day_night_cycle.json` (en `data/world/`) | SYS-008 | json | SPR-002 | `data/world/day_night_cycle.json` | 1h |
| SPR-072 | DayNight cycle + skybox swap | SYS-008 | verse+asset | SPR-071 | (TBD module) | 2h |
| SPR-073 | Spawns nocturnos + recurso modifiers | SYS-008 | verse | SPR-072 | (modifica ResourceNodes) | 1.5h |
| SPR-074 | Schema `achievements.json` (en `data/progression/`) | SYS-021 | json | SPR-043 | `data/progression/achievements.json` | 1.5h |
| SPR-075 | Achievement engine — detección de criterios | SYS-021 | verse | SPR-074, SPR-009 | (TBD module) | 2h |
| SPR-076 | Achievement UI + notification | SYS-021, SYS-050 | verse+ui | SPR-075 | (parte de UI) | 1h |
| SPR-077 | Schema `activity_log.json` (en `data/ui/`) | SYS-049 | json | SPR-002 | `data/ui/activity_log.json` | 1h |
| SPR-078 | ActivityLogUI.verse — 4 líneas + fade | SYS-049 | verse+ui | SPR-077 | `Systems/Social/ActivityLogUI.verse` | 2h |
| SPR-079 | NotificationPool + queue + sounds | SYS-050 | verse+ui | SPR-009 | `Systems/UI/NotificationPool.verse`, `data/ui/notifications.json` | 2h |

### 5.5 Death penalty completo + QoL F2 (SPR-080 → SPR-083)

| ID | Título | SYS | Tipo | Deps | Archivos clave | Tiempo |
|---|---|---|---|---|---|---|
| SPR-080 | Schema `death_protection.json` (en `data/economy/`) | SYS-009 | json | SPR-002 | `data/economy/death_protection.json` | 1h |
| SPR-081 | PlayerDeathHandler.verse — % loss + protection | SYS-009 | verse | SPR-038, SPR-080 | `Systems/Player/PlayerDeathHandler.verse` | 2h |
| SPR-082 | Schema `error_messages.json` + Error UI | SYS-057 | json+verse | SPR-002 | `data/ui/error_messages.json` | 1.5h |
| SPR-083 | Schema `rate_limits.json` + Rate limiting cross-cutting | SYS-058 | json+verse | SPR-002 | `data/ui/rate_limits.json` | 1.5h |

**Done F2**: 30+ companions invocables, Dex tracking 300, skill trees aplicables, achievements detectados, log visible.

---

## 6. Fase 3 — Economy & Equipment

> Battle Pass, equipo, shop, lootboxes, pity, trade, auction, todos los QoL.

### 6.1 Currencies (SPR-084 → SPR-088)

| ID | Título | SYS | Tipo | Deps | Archivos clave | Tiempo |
|---|---|---|---|---|---|---|
| SPR-084 | Schemas `gold.json` + `gems.json` | SYS-029, SYS-030 | json | SPR-002 | `data/economy/gold.json`, `gems.json` | 1h |
| SPR-085 | CurrencyManager.verse — gold + gems | SYS-029, SYS-030 | verse | SPR-008, SPR-084 | `Systems/Economy/CurrencyManager.verse` | 2h |
| SPR-086 | Currency caps + persistencia + transactions log | SYS-029, SYS-030 | verse | SPR-085 | (modifica) | 1.5h |
| SPR-087 | Schema `vbucks_offers.json` + entitlements detection | SYS-031 | json+verse | SPR-085 | `data/economy/vbucks_offers.json` | 2h |
| SPR-088 | PurchaseService.verse — abstrae gems/vbucks/in-game | SYS-031 | verse | SPR-087 | `Systems/Economy/PurchaseService.verse` | 2h |

### 6.2 Equipment (SPR-089 → SPR-099)

| ID | Título | SYS | Tipo | Deps | Archivos clave | Tiempo |
|---|---|---|---|---|---|---|
| SPR-089 | Schema `equipment_slots.json` (6 ranuras) | SYS-023 | json | SPR-002 | `data/items/equipment_slots.json` | 1h |
| SPR-090 | EquipmentSlots.verse — equip/unequip | SYS-023 | verse | SPR-015, SPR-089 | `Systems/Equipment/EquipmentSlots.verse` | 2h |
| SPR-091 | Schema `equipment.json` extendido (stats por rareza) | SYS-024 | json | SPR-051 | `data/items/equipment.json` | 1.5h |
| SPR-092 | Calcular stats efectivas + aplicar al jugador | SYS-024 | verse | SPR-090, SPR-091 | (modifica EquipmentSlots) | 2h |
| SPR-093 | Schema `equipment_leveling.json` (fail-rates tier 1–10) | SYS-025 | json | SPR-091 | `data/items/equipment_leveling.json` | 1h |
| SPR-094 | EquipmentLeveling.verse — roll + apply | SYS-025 | verse | SPR-092, SPR-093 | `Systems/Equipment/EquipmentLeveling.verse` | 2h |
| SPR-095 | Schema `protectors.json` + ProtectorService | SYS-026 | json+verse | SPR-094 | `data/items/protectors.json`, `Systems/Equipment/ProtectorService.verse` | 2h |
| SPR-096 | Schema `sets.json` + SetBonuses.verse | SYS-027 | json+verse | SPR-092 | `data/items/sets.json`, `Systems/Equipment/SetBonuses.verse` | 2h |
| SPR-097 | Schema `reroll.json` (curva exponencial) | SYS-028 | json | SPR-091 | `data/items/reroll.json` | 1h |
| SPR-098 | RerollService.verse — coste escalable | SYS-028 | verse | SPR-097 | `Systems/Equipment/RerollService.verse` | 1.5h |
| SPR-099 | Equipment UI completa (slots + compare) | SYS-023, SYS-053 | verse+ui | SPR-094, SPR-096 | (parte de InventoryUI) | 2h |

### 6.3 Shop + Rotating + Lootboxes + Pity (SPR-100 → SPR-110)

| ID | Título | SYS | Tipo | Deps | Archivos clave | Tiempo |
|---|---|---|---|---|---|---|
| SPR-100 | Schema `shop.json` (TODOS los items + precios) | SYS-032 | json | SPR-088 | `data/economy/shop.json` | 2h |
| SPR-101 | ShopSystem.verse + UI básica | SYS-032 | verse+ui | SPR-100 | `Systems/Economy/ShopSystem.verse`, `Systems/UI/ShopUI.verse` | 2h |
| SPR-102 | Validación universal obtainability | SYS-038 | python | SPR-100 | (extiende validate_jsons) | 1.5h |
| SPR-103 | Schema `shop_rotations.json` + RotatingShop | SYS-033 | json+verse | SPR-101, SPR-007 | `data/economy/shop_rotations.json`, `Systems/Economy/RotatingShop.verse` | 2h |
| SPR-104 | Schema `lootboxes.json` (Almas) | SYS-034 | json | SPR-100 | `data/items/lootboxes.json` | 1.5h |
| SPR-105 | LootboxSystem.verse — pull logic + rates | SYS-034 | verse | SPR-104 | `Systems/Economy/LootboxSystem.verse` | 2h |
| SPR-106 | Schema `pity_config.json` | SYS-035 | json | SPR-104 | `data/economy/pity_config.json` | 1h |
| SPR-107 | PitySystem.verse — counters por (alma, rarity) | SYS-035 | verse | SPR-105, SPR-106 | `Systems/Economy/PitySystem.verse` | 2h |
| SPR-108 | Lootbox open animation + reveal UI | SYS-034 | verse+ui+asset | SPR-107 | (parte de UI) | 2h |
| SPR-109 | Test_device pity flow exhaustivo | SYS-035 | test | SPR-107 | test_device | 1.5h |
| SPR-110 | Drop rates visibles (transparencia) | SYS-034 | verse+ui | SPR-105 | (modifica ShopUI) | 1h |

### 6.4 Trading + Auction (SPR-111 → SPR-115)

| ID | Título | SYS | Tipo | Deps | Archivos clave | Tiempo |
|---|---|---|---|---|---|---|
| SPR-111 | Tradability flags por item + validador | SYS-036 | json+python | SPR-091 | (extiende validate_jsons) | 1h |
| SPR-112 | TradeSystem.verse — UI + lock 5s + double confirm | SYS-036 | verse+ui | SPR-088, SPR-111 | `Systems/Economy/TradeSystem.verse` | 2h |
| SPR-113 | Schema `auction_config.json` + NPC vendor | SYS-037 | json | SPR-002 | `data/economy/auction_config.json` | 1.5h |
| SPR-114 | AuctionSystem.verse — listings + comisión | SYS-037 | verse | SPR-088, SPR-113 | `Systems/Economy/AuctionSystem.verse` | 2h |
| SPR-115 | Auction UI + asset NPC vendor | SYS-037 | verse+ui+asset | SPR-114 | (UEFN) | 2h |

### 6.5 Battle Pass (SPR-116 → SPR-122)

| ID | Título | SYS | Tipo | Deps | Archivos clave | Tiempo |
|---|---|---|---|---|---|---|
| SPR-116 | Schema `season_01.json` (100 niveles × 2 tracks) | SYS-022 | json | SPR-002 | `data/progression/battle_pass_seasons/season_01.json` | 2h |
| SPR-117 | BattlePass.verse — XP separado + persistencia | SYS-022 | verse | SPR-008, SPR-116 | `Systems/LiveOps/BattlePass.verse` | 2h |
| SPR-118 | BP claim rewards (free + premium) | SYS-022 | verse | SPR-117, SPR-088 | (modifica BattlePass) | 1.5h |
| SPR-119 | BP UI track visualization | SYS-022 | verse+ui | SPR-118 | (parte de UI) | 2h |
| SPR-120 | BP XP gain hooks (todas las fuentes) | SYS-022 | verse | SPR-117 | (cross-cutting) | 1.5h |
| SPR-121 | BP premium unlock flow | SYS-022, SYS-031 | verse | SPR-117, SPR-088 | (modifica) | 1h |
| SPR-122 | Test_device BP completo | SYS-022 | test | SPR-121 | test_device | 1h |

### 6.6 QoL F3 (SPR-123 → SPR-130)

| ID | Título | SYS | Tipo | Deps | Archivos clave | Tiempo |
|---|---|---|---|---|---|---|
| SPR-123 | Schema `auto_sell_config.json` + Auto-sell logic | SYS-051 | json+verse | SPR-015 | `data/ui/auto_sell_config.json` | 1.5h |
| SPR-124 | Schema `pre_inventory_filter.json` + filter | SYS-052 | json+verse | SPR-015 | `data/ui/pre_inventory_filter.json` | 1.5h |
| SPR-125 | Visual Compare UI | SYS-053 | verse+ui | SPR-099 | (parte de InventoryUI) | 1.5h |
| SPR-126 | Idle Summary screen | SYS-054 | verse+ui | SPR-008 | `Systems/UI/IdleSummaryUI.verse` | 2h |
| SPR-127 | Search/Filter inventory + Dex | SYS-055 | verse | SPR-061 | (modifica InventoryUI/DexUI) | 1.5h |
| SPR-128 | Schema `hotkeys.json` + Radial menu mobile | SYS-056 | json+verse+ui | SPR-002 | `data/ui/hotkeys.json` | 2h |
| SPR-129 | HUDController.verse — central HUD | SYS-049, SYS-050, SYS-057 | verse+ui | SPR-018, SPR-079 | `Systems/UI/HUDController.verse` | 2h |
| SPR-130 | Mobile audit pass — touch areas + scaling | — | verse+ui | SPR-129 | (cross-cutting) | 2h |

### 6.7 Polish economy + integration (SPR-131 → SPR-136)

| ID | Título | SYS | Tipo | Deps | Archivos clave | Tiempo |
|---|---|---|---|---|---|---|
| SPR-131 | Universal Obtainability completo (todos los items) | SYS-038 | json+python | SPR-102 | (extiende validate) | 2h |
| SPR-132 | Currency caps anti-exploit | SYS-029, SYS-030 | verse | SPR-086 | (modifica CurrencyManager) | 1h |
| SPR-133 | Transaction log persistente para audit | SYS-029, SYS-030 | verse | SPR-086 | (modifica) | 1.5h |
| SPR-134 | BalanceFormulas exporter Python — curvas F3+ (pity, reroll, equipment leveling, base level) | — | python | SPR-004, SPR-204 | `scripts/build/02_export_constants_to_verse.py` extendido | 2h |
| SPR-135 | Test_device economy flow end-to-end | SYS-032, SYS-034, SYS-035 | test | SPR-107, SPR-118 | test_device | 2h |
| SPR-136 | Memory budget check pass — todos los buckets | SYS-069 | python+verse | SPR-008 | `scripts/build/06_check_memory_budget.py` | 2h |

**Done F3**: shop con rotación funcionando, BP claim, equipo + leveling + protectors, lootboxes con pity, trade & auction same-session, todos los QoL.

---

## 7. Fase 4 — Base persistente & Live Ops

> Daily login, time played, base, generadores offline, eventos, códigos, seasonal.

### 7.1 Base level + upgrades (SPR-137 → SPR-143)

| ID | Título | SYS | Tipo | Deps | Archivos clave | Tiempo |
|---|---|---|---|---|---|---|
| SPR-137 | Schema `base_levels.json` (curva XP base) | SYS-059 | json | SPR-002 | `data/base/base_levels.json` | 1h |
| SPR-138 | BaseLevelManager.verse — XP base, gates | SYS-059 | verse | SPR-008, SPR-137 | `Systems/Base/BaseLevelManager.verse` | 2h |
| SPR-139 | Schema `base_upgrades.json` extendido | SYS-060 | json | SPR-031 | `data/base/base_upgrades.json` | 2h |
| SPR-140 | BaseUpgrades.verse — efectos aplicables | SYS-060 | verse | SPR-138, SPR-139 | (modifica BaseUpgrades.verse) | 2h |
| SPR-141 | Base UI panel + tier visualization | SYS-060 | verse+ui | SPR-140 | `Systems/UI/BasePanelUI.verse` | 2h |
| SPR-142 | Gating de zonas/quests/boss por base level | SYS-007, SYS-039, SYS-059 | verse | SPR-138 | (cross-cutting) | 1.5h |
| SPR-143 | Test_device base progression | SYS-059, SYS-060 | test | SPR-141 | test_device | 1h |

### 7.2 Generadores + offline + crafting timers (SPR-144 → SPR-150)

| ID | Título | SYS | Tipo | Deps | Archivos clave | Tiempo |
|---|---|---|---|---|---|---|
| SPR-144 | Schema `generators.json` (en `data/base/`) | SYS-061 | json | SPR-002 | `data/base/generators.json` | 1h |
| SPR-145 | PassiveGenerators.verse — tick rate + caps | SYS-061 | verse | SPR-140, SPR-144 | `Systems/Base/PassiveGenerators.verse` | 2h |
| SPR-146 | Schema `offline_config.json` (caps + eficiencias) | SYS-062 | json | SPR-002 | `data/base/offline_config.json` | 1h |
| SPR-147 | OfflineCalculator.verse — login delta calc | SYS-062 | verse | SPR-008, SPR-145, SPR-146 | `Systems/Base/OfflineCalculator.verse` | 2h |
| SPR-148 | Idle Summary integra producción offline | SYS-054, SYS-062 | verse | SPR-126, SPR-147 | (modifica IdleSummaryUI) | 1h |
| SPR-149 | Schema `crafting_timers.json` + CraftingTimers.verse | SYS-063 | json+verse | SPR-027, SPR-008 | `data/items/crafting_timers.json`, `Systems/Base/CraftingTimers.verse` | 2h |
| SPR-150 | Crafting timers persistencia 100% offline | SYS-063 | verse | SPR-149 | (modifica) | 1.5h |

### 7.3 Daily login + time played (SPR-151 → SPR-156)

| ID | Título | SYS | Tipo | Deps | Archivos clave | Tiempo |
|---|---|---|---|---|---|---|
| SPR-151 | Schema `daily_login.json` (28 días + streak) | SYS-040 | json | SPR-002 | `data/progression/daily_login.json` | 1h |
| SPR-152 | DailyLoginRewards.verse — streak + reset UTC | SYS-040 | verse | SPR-007, SPR-151 | `Systems/LiveOps/DailyLoginRewards.verse` | 2h |
| SPR-153 | Daily login rescue con gemas | SYS-040 | verse | SPR-152, SPR-088 | (modifica) | 1h |
| SPR-154 | Schema `time_played.json` (15/30/60 min) | SYS-041 | json | SPR-002 | `data/progression/time_played.json` | 1h |
| SPR-155 | TimePlayedRewards.verse — session tracking | SYS-041 | verse | SPR-154 | `Systems/LiveOps/TimePlayedRewards.verse` | 2h |
| SPR-156 | Daily quest pool + WeeklyQuestRotator | SYS-039 | verse+json | SPR-049 | `data/quests/daily_pool.json`, `weekly_pool.json`, `Systems/Quests/DailyQuestRotator.verse`, `WeeklyQuestRotator.verse` | 2h |

### 7.4 Long events + admin abuse + codes (SPR-157 → SPR-167)

| ID | Título | SYS | Tipo | Deps | Archivos clave | Tiempo |
|---|---|---|---|---|---|---|
| SPR-157 | Schema `seasonal_events.json` | SYS-043 | json | SPR-002 | `data/events/seasonal_events.json` | 1.5h |
| SPR-158 | EventManager.verse — activate/deactivate events | SYS-043 | verse | SPR-009, SPR-157 | `Systems/LiveOps/EventManager.verse` | 2h |
| SPR-159 | Long event content hooks (zone/companion/quest) | SYS-043 | verse | SPR-158 | (cross-cutting) | 2h |
| SPR-160 | Schema `admin_commands.json` (en `data/events/`) | SYS-044 | json | SPR-002 | `data/events/admin_commands.json` | 1h |
| SPR-161 | Admin abuse panel — drop boost, spawn masivo | SYS-044, SYS-070 | verse+ui | SPR-010, SPR-160 | (modifica AdminPanel) | 2h |
| SPR-162 | Admin command logging (audit) | SYS-044, SYS-070 | verse | SPR-161 | (modifica) | 1h |
| SPR-163 | Schema `codes_pool.json` (pre-pool grande) | SYS-045 | json | SPR-002 | `data/events/codes_pool.json` | 1.5h |
| SPR-164 | CodeRedemption.verse — validate + reward | SYS-045 | verse | SPR-008, SPR-163 | `Systems/LiveOps/CodeRedemption.verse` | 2h |
| SPR-165 | Code redemption UI + persist redenciones | SYS-045 | verse+ui | SPR-164 | (parte de UI) | 1.5h |
| SPR-166 | Test_device codes flow (público/único/limitado) | SYS-045 | test | SPR-164 | test_device | 1h |
| SPR-167 | Admin trigger event device | SYS-044 | verse+device | SPR-161 | `Devices/HourlyBossTrigger.verse` (placeholder evento) | 1h |

### 7.5 Seasonal framework + Contextual tutorials (SPR-168 → SPR-176)

| ID | Título | SYS | Tipo | Deps | Archivos clave | Tiempo |
|---|---|---|---|---|---|---|
| SPR-168 | Schema `season_XX.json` (en `data/seasons/`) | SYS-046 | json | SPR-002 | `data/seasons/season_01.json` | 2h |
| SPR-169 | SeasonManager.verse — load season actual | SYS-046 | verse | SPR-009, SPR-168 | `Systems/LiveOps/SeasonManager.verse` | 2h |
| SPR-170 | Theme swap masivo (Python `05_apply_theme_pack.py`) | SYS-046 | python | SPR-004 | `scripts/build/05_apply_theme_pack.py` | 2h |
| SPR-171 | Asset variants por season (asistido Python) | SYS-046 | python+asset | SPR-170 | (extiende `scripts/build/05_apply_theme_pack.py` con función `apply_seasonal_asset_variants()`; carpetas `Content/Assets/<theme>_<season>/` por convención) | 2h |
| SPR-172 | Schema `contextual_tutorials.json` | SYS-066 | json | SPR-002 | `data/onboarding/contextual_tutorials.json` | 1h |
| SPR-173 | Contextual tutorials triggers (auction/lootbox/trade) | SYS-066 | verse | SPR-049, SPR-172 | (parte de QuestEngine) | 1.5h |
| SPR-174 | Pipeline orquestador `07_run_full_pipeline.py` (incluye `00_validate_structure.py` como primer step) | — | python | SPR-001, SPR-003 → SPR-170 | `scripts/build/07_run_full_pipeline.py` | 2h |
| SPR-175 | Memory budget check + warnings extendido | SYS-069 | python | SPR-136, SPR-174 | (extiende) | 1.5h |
| SPR-176 | Test_device season switching end-to-end | SYS-046 | test | SPR-170, SPR-171 | test_device | 1.5h |

**Done F4**: base con generadores offline, daily login, time played, eventos largos activables, códigos canjeables, theme swap masivo funcional.

---

## 8. Fase 5 — Hourly Boss + Social + Polish

> Endgame, social display, leaderboards globales, optimización móvil deep, segundo mapa.

### 8.1 Hourly Boss completo (SPR-177 → SPR-184)

| ID | Título | SYS | Tipo | Deps | Archivos clave | Tiempo |
|---|---|---|---|---|---|---|
| SPR-177 | Schema `hourly_boss.json` (requisitos + recompensas) | SYS-042 | json | SPR-002 | `data/events/hourly_boss.json` | 1.5h |
| SPR-178 | HourlyBossPortal.verse — sync UTC + ventana 2 min | SYS-042 | verse | SPR-007, SPR-177 | `Systems/World/HourlyBossPortal.verse`, `Devices/HourlyBossTrigger.verse` | 2h |
| SPR-179 | Teleport masivo a arena + matchmaking | SYS-042 | verse | SPR-178 | (modifica) | 2h |
| SPR-180 | BossEncounters.verse — fight loop cooperativo | SYS-042 | verse | SPR-037, SPR-179 | `Systems/World/BossEncounters.verse` | 2h |
| SPR-181 | Boss arena asset (UEFN editor) | SYS-042 | asset | SPR-180 | (UEFN) | 2h |
| SPR-182 | Boss rewards drop + scoreboard | SYS-042 | verse | SPR-180 | (modifica) | 1.5h |
| SPR-183 | Boss event timer UI (countdown global) | SYS-042 | verse+ui | SPR-178 | (parte de HUD) | 1h |
| SPR-184 | Test_device hourly boss completo | SYS-042 | test | SPR-182 | test_device | 1.5h |

### 8.2 Social: Leaderboards + Display (SPR-185 → SPR-191)

| ID | Título | SYS | Tipo | Deps | Archivos clave | Tiempo |
|---|---|---|---|---|---|---|
| SPR-185 | Schema `leaderboards.json` (en `data/social/`) | SYS-047 | json | SPR-002 | `data/social/leaderboards.json` | 1h |
| SPR-186 | LeaderboardSync.verse — leaderboard_device integration | SYS-047 | verse | SPR-185 | `Systems/Social/LeaderboardSync.verse` | 2h |
| SPR-187 | Leaderboard UI in-session + global | SYS-047 | verse+ui | SPR-186 | (parte de UI) | 1.5h |
| SPR-188 | Schema `displays.json` (en `data/social/`) | SYS-048 | json | SPR-002 | `data/social/displays.json` | 1h |
| SPR-189 | SocialDisplay.verse — pet/aura/título | SYS-048 | verse+asset | SPR-008, SPR-188 | `Systems/Social/SocialDisplay.verse` | 2h |
| SPR-190 | Display visible socialmente in-session | SYS-048 | verse | SPR-189 | (modifica) | 1.5h |
| SPR-191 | Achievements/Dex display unlocks | SYS-048, SYS-021, SYS-015 | verse | SPR-189, SPR-075 | (cross-cutting) | 1h |

### 8.3 Polish móvil + performance (SPR-192 → SPR-198)

| ID | Título | SYS | Tipo | Deps | Archivos clave | Tiempo |
|---|---|---|---|---|---|---|
| SPR-192 | Spatial Profiler audit completo | — | profiling | SPR-130 | reporte | 2h |
| SPR-193 | LOD audit todos los meshes custom | — | asset | SPR-192 | (UEFN) | 2h |
| SPR-194 | HISM conversion props repetidos | — | asset+python | SPR-193 | (UEFN + script) | 2h |
| SPR-195 | Texture compression audit ≤512×512 | — | asset+python | SPR-194 | `scripts/tools/texture_audit.py` | 1.5h |
| SPR-196 | Notification pool tuning anti-spam | SYS-050 | verse | SPR-079 | (modifica) | 1h |
| SPR-197 | Mobile UI second pass (touch areas, fonts) | — | verse+ui | SPR-130 | (cross-cutting) | 2h |
| SPR-198 | Mobile preview test cycle full | — | test | SPR-197 | reporte | 1.5h |

### 8.4 Segundo mapa con la máquina (SPR-199 → SPR-203)

| ID | Título | SYS | Tipo | Deps | Archivos clave | Tiempo |
|---|---|---|---|---|---|---|
| SPR-199 | Scaffolder Python — clone para nuevo mapa | — | python | SPR-174 | `scripts/tools/new_map_scaffolder.py` | 2h |
| SPR-200 | Mapa 2: nuevo theme JSON + assets | — | json+asset | SPR-199 | `data/theme/theme_config.json` (mapa 2) | 2h |
| SPR-201 | Mapa 2: bulk swap meshes/materiales | SYS-046 | python | SPR-170, SPR-200 | (run pipeline) | 1.5h |
| SPR-202 | Mapa 2: validación pipeline end-to-end | — | test | SPR-201 | reporte | 1.5h |
| SPR-203 | Documentación final: cómo hacer mapa N+1 en <8h | — | docs | SPR-202 | `docs/HOWTO_NEW_MAP.md` | 2h |

**Done F5**: hourly boss live, leaderboards globales, social display, mobile optimization a target, **segundo mapa publicado en <8h** (validación de la "máquina modular").

---

## 9. Reglas de mantenimiento

1. **Inmutabilidad de IDs**: una vez asignado `SPR-xxx`, nunca se reordena ni reusa.
2. **Adición**: nuevos sprints reciben siguiente ID libre (`SPR-204+`), no rellenan huecos.
3. **Descarte**: se marca `🚫 deprecated` con motivo y fecha. **No se borra la fila.**
4. **Refactor**: si un sprint crece >2h, se divide en `SPR-XXXa`, `SPR-XXXb` (sub-sprints) o se generan IDs nuevos.
5. **Done**: actualizar `Estado` cada vez que se cierra. Logear en `DAILY_LOG.md` y `CHANGELOG.md`.
6. **Coherencia con SYSTEMS_INDEX**: cada vez que un SPR-xxx implementa un SYS-xxx, actualizar columna `Sprint` en `SYSTEMS_INDEX.md`.

---

## 10. Sprints añadidos post-planning

> **Sprints creados después del planning original (SPR-001..SPR-203). Por regla 2 de §9 ("Adición"), reciben IDs ≥ SPR-204 y NO se reordenan en las secciones F0–F5.**
>
> **Nota de lectura**: cada sprint aquí declara su fase funcional en la columna `Fase`. La fase indica cuándo se ejecuta en el roadmap, no su posición visual en este doc. Las deps cross-fase se resuelven respetando esta tabla.

| ID | Título | SYS | Fase | Tipo | Deps | Archivos clave | Tiempo | Motivo |
|---|---|---|---|---|---|---|---|---|
| SPR-204 | BalanceCurves_Generated mínimo (XP curve + rebirth thresholds) | SYS-016, SYS-020 | F1 | python | SPR-004, SPR-043, SPR-047 | `scripts/build/02_export_constants_to_verse.py` extendido (función `export_balance_curves_minimal()`); genera `Generated/BalanceCurves_Generated.verse` con solo las 2 curvas críticas F1 | 1h | **Auditoría 2 — M1**. SPR-044 y SPR-048 (F1) declaran `BalanceCurves_Generated 🔒` como dep, pero el exporter completo (SPR-134) está en F3. Split: las 2 curvas F1 críticas (XP + rebirth) se generan ahora; el resto (pity, reroll, equipment leveling, base level) sigue en SPR-134 con scope reducido. |
| SPR-205 | Validador de ciclos de dependencias Verse | — | F0 | python | SPR-001, SPR-003 | `scripts/tools/dependency_cycle_check.py` (spec ya escrita en `MODULES_DEPENDENCY_GRAPH.md` §10.3 — copiar verbatim). Lee `using {}` de los `.verse`, construye grafo dirigido, falla si detecta (a) ciclos compile-time, (b) imports de capa N hacia capa N+, (c) paths inválidos `/Game.Content.Verse...`. Exit codes: 1=ciclo, 2=violación capas, 3=path inválido. **Pre-commit hook** invoca el script bloqueando commit si exit ≠ 0. NO entra en orquestador `07_run_full_pipeline.py` (es validador estructural transversal, no parte del pipeline data→verse). | 1h | **Auditoría retrospectiva — Bloque 3 (B3.3)**. Script huérfano: especificado con código completo en MODULES §10.3, referenciado en CHANGELOG (Auditoría 1) y MODULES §1.4 como "validador" existente, pero sin SPR asignado y sin entrada en `FOLDER_STRUCTURE_TRUTH.md` §5. SPR-205 lo formaliza como tarea F0 (no bloquea ningún SPR de F0–F1 porque no es dep de ningún sistema gameplay; sí debe correr como pre-commit antes del primer commit que añada `using {}` cross-Verse — práctica recomendada desde SPR-005 en adelante). |
| SPR-206 | Crear `Main.umap` inicial vacío en UEFN editor + commit | — | F0 | uefn-manual | SPR-001 | `Content/Maps/Main.umap` | 0.5h | **Stress test pre-SPR-001 (mayo 2026, hueco D3)**. El `.umap` es binario UEFN, no creable desde Python/CLI ni desde scripts del orquestador. Requiere abrir UEFN editor, crear nuevo nivel vacío, guardar como `Main.umap` en `Content/Maps/`, commit manual. Sprint sin código — pasos: (1) abrir proyecto en UEFN, (2) File → New Level → Empty Level, (3) Save As → `Content/Maps/Main.umap`, (4) `git add Content/Maps/Main.umap && git commit -m "✅ SPR-206: Main.umap inicial"`. NO entra en orquestador. Necesario para Done F0 (sin .umap, el validador estructural reportaría MISSING al cierre de F0). |
| SPR-207 🟢 done | Sistema dailylog: `close_sprint.py` + carpeta `docs/dailylog/` + reescritura `DAILY_LOG.md` | — | F0 | python+docs | SPR-001 | `scripts/tools/close_sprint.py` (idempotente, cross-platform, parsea `SPRINTS_BACKLOG.md` + git para extraer datos auto, preserva bloque MANUAL entre ejecuciones), `docs/dailylog/.gitkeep`, `docs/dailylog/DL_2026-05-06_SPR-001+FIX1_lexosi.md` (DL retroactivo del día), `docs/DAILY_LOG.md` (reescrito como plantilla canónica + instructivo del flujo, NO archivo vivo), `.dailylog_user` añadido a `.gitignore`. Decisión arquitectónica reflejada en `CONCEPT.md` §14.11, `FOLDER_STRUCTURE_TRUTH.md` §1.1 + §5 + §6 + §6.2, `WORKFLOW.md` §3 Fase 4 + §5. Trigger: B (script Python invocado a mano tras `git tag`); A descartado (no hay hook git nativo local para creación de tags), C descartado (acopla a aider). | 1.5h | **Decisión cerrada 2026-05-06 (cierre SPR-001 + hotfix SPR-001-FIX-1)**. Antes existía `docs/DAILY_LOG.md` como archivo vivo y `docs/daily_logs/` (plural, NO declarado en TRUTH — contradicción) como carpeta-archivo. Sustituido por sistema único: archivo por día en `docs/dailylog/` (singular), naming `DL_*`, generación automática del 80% del contenido vía script, autor por `.dailylog_user` local. Cero edición manual de los DL salvo bloque MANUAL al final. Idempotencia obligatoria. |

### 10.X Cierre del sistema dailylog (SPR-207-FIX-2 → SPR-209)

| ID | Título | SYS | Tipo | Deps | Archivos clave | Tiempo |
|---|---|---|---|---|---|---|
| SPR-207-FIX-2 | close_sprint.py duplicate-detection scope fix | — | python fix | SPR-207 | `scripts/tools/close_sprint.py` | 30-45min |
| SPR-207-FIX-3 | close_sprint.py normalización IDs con guiones | — | python fix | SPR-207 | `scripts/tools/close_sprint.py` | 20-30min |
| SPR-207-FIX-4 | close_sprint.py cierre interactivo (energía/tiempo prompts) | — | python+docs | SPR-207-FIX-2, SPR-207-FIX-3 | `scripts/tools/close_sprint.py`, `docs/WORKFLOW.md` §3 Fase 4, `docs/DAILY_LOG.md` plantilla, `docs/CONCEPT.md` §14.11 | 1h-1h30 |
| SPR-208 | Bloque AUTO docs_changed en DL (whitelist 21 docs autoritativos, leída de .aider.conf.yml) | — | python+docs | SPR-207-FIX-4 | `scripts/tools/close_sprint.py`, `docs/DAILY_LOG.md` plantilla, `.aider.conf.yml` (lectura) | 45min-1h |
| SPR-209 | Regla PowerShell-first toolchain | — | docs+verificación | — | `docs/PROMPT.md`, `docs/DEEPSEEK_CAPSULE.md`, `docs/WORKFLOW.md`, `scripts/tools/_throwaway/.gitkeep`, `.gitignore` | 30-45min |
| SPR-210 | Auditoría drift documental contra fuentes oficiales Epic — fixes aplicados | — | docs+audit | — | `docs/PERSISTENCE_MAP.md`, `docs/API_REFERENCE_GENERATED.md`, `docs/EMERGENCY_ROLLBACK.md`, `docs/FOLDER_STRUCTURE_TRUTH.md`, `docs/JSON_SCHEMAS.md`, `docs/TESTING_PROTOCOL.md`, `docs/WORKFLOW.md` | retroactivo |
| SPR-211 🟢 done | Verse syntax audit + drift fix (13 lecciones validadas con build UEFN, refactor 5 archivos Verse + generator script, audit 8 docs autoritativos) | — | docs+verse+python | SPR-006, SPR-007 | `docs/VERSE_SYNTAX_GUIDE.md` (NUEVO), `Content/Verse/Core/Logger.verse`, `Content/Verse/Core/TimeSync.verse`, `Content/Verse/Generated/Companions_Generated.verse`, `Content/Verse/Generated/Items_Generated.verse`, `Content/Verse/Generated/Quests_Generated.verse`, `scripts/build/02_export_constants_to_verse.py`, `docs/CHANGELOG.md`, `docs/MODULES_DEPENDENCY_GRAPH.md`, `docs/GLOSSARY.md`, `docs/API_REFERENCE_GENERATED.md`, `docs/BOOTSTRAP_PIPELINE.md`, `docs/CONCEPT.md`, `docs/SPRINTS_BACKLOG.md`, `docs/PROMPT.md`, `docs/postmortems/PM-SPR-211.md` (NUEVO), `docs/POSTMORTEMS_INDEX.md`, `docs/DAILY_LOG.md` | 2026-05-07 |

**Notas críticas**:
- SPR-209 va PRIMERO en plan diario (regla preventiva, evita que Claude Code/DeepSeek generen one-liners PowerShell-rotos en SPR-207-FIX-4 y SPR-208).
- Triada FIX-2/FIX-3/FIX-4 + SPR-208 = cierre completo deuda técnica del sistema dailylog SPR-207.
- Ejecutor recomendado: SPR-207-FIX-2 y FIX-3 → DeepSeek-Flash (bugs simples). SPR-207-FIX-4, SPR-208, SPR-209 → Claude Code (toca varios docs autoritativos + edge cases + commits controlados).
- Severidad: SPR-207-FIX-4 alta (cada cierre falla actualmente), resto media.
- SPR-210 ejecutado retroactivamente 2026-05-07 mañana. Tipo: auditoría drift contra fuentes oficiales Epic vía `AUDIT_PROMPT.md`. 7 docs autoritativos modificados (502 líneas, mayoría PERSISTENCE_MAP).
- **SPR-211 ejecutado 2026-05-07 tarde** tras detección durante Build UEFN post-SPR-007 de 13 lecciones críticas de sintaxis Verse moderna que invalidan partes de docs autoritativos. Refactor de 5 archivos Verse (Logger, TimeSync, 3 Generated) a patrones canónicos modernos validados con build real. Crear `VERSE_SYNTAX_GUIDE.md` como fuente única. Auditoría 8 docs (CHANGELOG D-02 corregida, MODULES/GLOSSARY/API_REFERENCE/BOOTSTRAP refactor de patrones obsoletos, CONCEPT/SPRINTS_BACKLOG done de SPR-006/007 actualizado, PROMPT.md sección Verse syntax rules nueva). Postmortem PM-SPR-211. Caso "Core con state mutable" (SPR-008) queda TBD en guide §2.4. Detalle en `docs/postmortems/PM-SPR-211.md`.

**Total: 208 sprints (203 originales + 5 añadidos: SPR-204 en Auditoría 2 + SPR-205 en Auditoría retrospectiva Bloque 3 + SPR-206 en stress test pre-SPR-001 + SPR-207 en cierre SPR-001 día 2026-05-06 sistema dailylog + SPR-211 en build UEFN día 2026-05-07). Tiempo estimado: ~310 h. Granularidad: 0.5h–2h por sprint.**
