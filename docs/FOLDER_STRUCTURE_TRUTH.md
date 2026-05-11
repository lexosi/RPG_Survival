# 🌳 FOLDER_STRUCTURE_TRUTH — Árbol único autoritativo del proyecto

> **Fuente única de verdad para rutas y nombres de archivo.** Si cualquier otro doc (`CONCEPT.md` §11, `SYSTEMS_INDEX.md`, `SPRINTS_BACKLOG.md`, etc.) discrepa con este → **gana este**.
>
> Este doc resuelve las 35 rutas inconsistentes detectadas en `SYSTEMS_INDEX.md` §4.

---

## 🧭 Índice

1. [Reglas globales](#1-reglas-globales)
2. [Árbol completo del proyecto](#2-árbol-completo-del-proyecto)
3. [Carpeta `data/` autoritativa](#3-carpeta-data-autoritativa)
4. [Carpeta `Content/Verse/` autoritativa](#4-carpeta-contentverse-autoritativa)
5. [Carpeta `scripts/` autoritativa](#5-carpeta-scripts-autoritativa)
6. [Carpeta `docs/` autoritativa](#6-carpeta-docs-autoritativa)
7. [Discrepancias resueltas vs CONCEPT §11](#7-discrepancias-resueltas-vs-concept-11)
8. [Script validador (Python)](#8-script-validador-python)
9. [Reglas de cambio](#9-reglas-de-cambio)

---

## 1. Reglas globales

### 1.1 Naming

| Tipo | Convención | Ejemplo |
|---|---|---|
| Carpetas data/ | `snake_case` | `data/companions/`, `data/economy/` |
| JSON | `snake_case.json` | `companions_base.json` |
| Carpetas Verse | `PascalCase` | `Core/`, `Systems/Player/` |
| Verse runtime | `PascalCase.verse` | `PlayerStats.verse` |
| Verse generado | `*_Generated.verse` (regla general) + 2 excepciones arquitectónicas: `ModuleRegistryConstants.verse` (C1) y `EventBusDevice.verse` (C3 + H4) | `Companions_Generated.verse`, `ModuleRegistryConstants.verse`, `EventBusDevice.verse` |
| Python | `NN_snake_case.py` (build) o `snake_case.py` (tools) | `01_validate_jsons.py`, `texture_audit.py` |
| Markdown | `SCREAMING_SNAKE.md` | `CONCEPT.md`, `SYSTEMS_INDEX.md` |
| Devices | `PascalCase.verse` | `BasePlot.verse` |
| Daily logs | `DL_YYYY-MM-DD_SPR-<tokens>_<autor>.md` (regex `^DL_\d{4}-\d{2}-\d{2}_SPR-[\w+\-]+_[a-z0-9]+\.md$`) | `DL_2026-05-06_SPR-001+FIX1_lexosi.md`, `DL_2026-05-06_SPR-001+FIX1+002_lexosi.md` |
| Postmortems | `PM-<id>.md` (regex `^PM-[A-Za-z0-9_-]+\.md$`) — solo en `docs/postmortems/`. Permite mayús/minús/dígitos/`-`/`_`. Ver §6.3 | `PM-SPR-009-blocked.md`, `PM-RECOVERY-2026-05-08.md`, `PM-SPR-211.md` |
| Tests Verse | `test_<snake>.verse` (regex `^test_[A-Za-z0-9_]+\.verse$`) — solo en `Content/Verse/Tests/`. Permite mayús en sufijos tipo `_SPR008`. Ver §4.2 | `test_event_bus_smoke.verse`, `test_persistence_SPR008.verse` |
| Throwaways canary | `throwaway_<snake>.verse` (regex `^throwaway_[A-Za-z0-9_]+\.verse$`) — solo en `Content/Verse/Tests/canary/`. Audit trail empírico P5 (validación primitiva Verse). Ver §4.2.1 | `throwaway_admin_state.verse` |
| Tests pytest | `test_<snake>.py` o `__init__.py` (regex `^test_[a-z][a-z0-9_]*\.py$\|^__init__\.py$`) — solo en `scripts/build/tests/`. Fixtures bajo `fixtures/` siguen regla `data` (snake_case JSON). Ver §5.2 | `test_exporter_event_bus.py`, `__init__.py`, `fixtures/event_bus_expected_contract.json` |

> **Nota sobre excepciones de Verse generado (Auditoría 3 — H3.6 + Auditoría regresión bloque 5 — H4 SPR-009)**: la lista de excepciones canónicas son ÚNICAMENTE `ModuleRegistryConstants.verse` y `EventBusDevice.verse` (decisiones D-A10 + D-A11, Auditoría 2 — C1+C3 + Auditoría regresión bloque 5 — H4). El nombre anterior `EventBusConstants.verse` queda obsoleto post-F-C-2 SPR-009 — el archivo se renombró a `EventBusDevice.verse` reflejando que el patrón vigente es `event_bus_device := class<concrete>(creative_device)` (no singleton top-level con `event_bus_module`). Verdad operativa en la regex de §8.2 línea 522. Coherente con `BOOTSTRAP_PIPELINE.md` §4.4 + `VERSE_SYNTAX_GUIDE.md` §1 lección 16. Cualquier otro archivo en `Generated/` DEBE llevar sufijo `_Generated`.

### 1.2 Reglas de path

- **Toda ruta que aparece en JSONs, Verse o Python referencia rutas DECLARADAS aquí.**
- **No se inventa carpetas en runtime ni se asume estructura.**
- **El validador (§8) falla la build si hay drift.**

### 1.3 Carpetas que NO deben existir

- ❌ `data/social/leaderboards/` (anidamiento innecesario — `leaderboards.json` plano dentro de `data/social/` es lo correcto, ver §3.1)
- ❌ Cualquier subcarpeta no listada en §3, §4, §5, §6

> **Nota (Auditoría 3 — H3.2)**: `data/world/` se eliminó antes de esta lista por contradecir §3.1 (donde la carpeta sí existe legítimamente con `day_night_cycle.json` para SYS-008) y §7.1 (resolución cerrada *"Crear `data/world/`. Carpeta válida."*). El comentario legacy *"data/world/ → reemplazada por contenido directo en JSONs específicos"* era de una versión anterior del doc, antes de SPR-070+.

---

## 2. Árbol completo del proyecto

```
ProjectRoot/
├── Content/
│   ├── Assets/                  ← Assets binarios (UEFN)
│   │   ├── Meshes/              (.fbx custom, ≤500 verts mobile)
│   │   ├── Textures/            (≤512×512, potencia de 2)
│   │   ├── Audio/
│   │   ├── Materials/
│   │   └── ScenegraphPrefabs/  ← convención del proyecto (no canon UEFN documentado)
│   ├── Maps/
│   │   └── Main.umap
│   └── Verse/                   ← ver §4
│
├── Plugins/                     ← UEFN plugins (usualmente vacío)
│
├── data/                        ← ver §3 (JSONs editables)
│
├── scripts/                     ← ver §5 (Python build/tools)
│
├── docs/                        ← ver §6 (documentación .md)
│
├── tests/                       ← outputs de test_devices, reportes
│   └── reports/
│
├── .gitignore
├── .gitattributes
└── README.md                    ← apunta a docs/
```

**Convención top-level**: `Content/`, `Plugins/`, `data/`, `scripts/`, `docs/`, `tests/`. **Nada más.**

> **Nota sobre `Content/Verse/`**: Epic no documenta literalmente `Content/Verse/` como ruta canónica con ese nombre, pero UEFN crea esa subcarpeta automáticamente al añadir un primer archivo `.verse` (sistema de módulos basado en filesystem, ver [dev.epicgames.com — Programming with Verse in UEFN](https://dev.epicgames.com/documentation/en-us/fortnite/programming-with-verse-in-unreal-editor-for-fortnite)). En este doc se trata como convención del editor UEFN por defecto.

---

## 3. Carpeta `data/` autoritativa

### 3.1 Árbol completo

```
data/
├── admin/                                   ⭐ NUEVA carpeta
│   ├── admin_config.json                    ← SYS-070
│   └── test_flags.json                      ← SYS-071
│
├── architecture/                            ⭐ NUEVA carpeta (Auditoría 2 — C1+C3)
│   ├── modules_manifest.json                ← SYS-072 (Auditoría 2 — C1; ver JSON_SCHEMAS §43)
│   └── events_catalog.json                  ← SYS-072 (Auditoría 2 — C3; ver JSON_SCHEMAS §42)
│
├── base/
│   ├── building_pieces.json                 ← SYS-005
│   ├── base_levels.json                     ← SYS-059
│   ├── base_upgrades.json                   ← SYS-060
│   ├── generators.json                      ← SYS-061
│   └── offline_config.json                  ← SYS-062
│
├── combat/                                  ⭐ NUEVA carpeta
│   └── damage_formulas.json                 ← SYS-006
│
├── companions/
│   ├── companions_base.json                 ← SYS-010
│   ├── rarities.json                        ← SYS-011
│   ├── variants.json                        ← SYS-012
│   ├── evolutions.json                      ← SYS-013
│   ├── behaviors.json                       ← SYS-014
│   └── dex_rewards.json                     ← SYS-015
│
├── economy/
│   ├── gold.json                            ← SYS-029
│   ├── gems.json                            ← SYS-030
│   ├── currency_caps.json                   ← SYS-029, SYS-030 (caps anti-exploit)
│   ├── vbucks_offers.json                   ← SYS-031
│   ├── shop.json                            ← SYS-032 (sustituye `prices.json`)
│   ├── shop_rotations.json                  ← SYS-033
│   ├── pity_config.json                     ← SYS-035
│   ├── auction_config.json                  ← SYS-037
│   └── death_protection.json                ← SYS-009
│
├── events/
│   ├── hourly_boss.json                     ← SYS-042
│   ├── seasonal_events.json                 ← SYS-043
│   ├── admin_commands.json                  ← SYS-044
│   └── codes_pool.json                      ← SYS-045
│
├── items/
│   ├── resources.json                       ← SYS-003
│   ├── consumables.json                     ← SYS-002
│   ├── recipes.json                         ← SYS-004
│   ├── equipment.json                       ← SYS-024
│   ├── equipment_slots.json                 ← SYS-023
│   ├── equipment_leveling.json              ← SYS-025
│   ├── protectors.json                      ← SYS-026
│   ├── sets.json                            ← SYS-027
│   ├── reroll.json                          ← SYS-028
│   ├── lootboxes.json                       ← SYS-034
│   └── crafting_timers.json                 ← SYS-063
│
├── onboarding/                              ⭐ NUEVA carpeta
│   ├── first_minute.json                    ← SYS-064
│   └── contextual_tutorials.json            ← SYS-066
│
├── progression/
│   ├── player_stats_base.json               ← SYS-001
│   ├── xp_curves.json                       ← SYS-016
│   ├── skill_points.json                    ← SYS-017
│   ├── skill_trees.json                     ← SYS-018
│   ├── abilities.json                       ← SYS-019
│   ├── rebirth_rewards.json                 ← SYS-020
│   ├── achievements.json                    ← SYS-021 ⚠️ MOVIDO desde data/quests/
│   ├── daily_login.json                     ← SYS-040
│   ├── time_played.json                     ← SYS-041
│   └── battle_pass_seasons/
│       ├── season_01.json                   ← SYS-022
│       ├── season_02.json                   (futuro)
│       └── ...
│
├── quests/
│   ├── tutorial_chain.json                  ← SYS-039, SYS-065
│   ├── daily_pool.json                      ← SYS-039
│   └── weekly_pool.json                     ← SYS-039
│
├── seasons/                                 ⭐ NUEVA carpeta
│   ├── season_01.json                       ← SYS-046
│   └── ...
│
├── social/                                  ⭐ NUEVA carpeta
│   ├── leaderboards.json                    ← SYS-047
│   └── displays.json                        ← SYS-048
│
├── theme/
│   ├── theme_config.json                    ← THE switch (cambia mapa entero)
│   └── localization_keys.json
│
├── ui/                                      ⭐ NUEVA carpeta
│   ├── activity_log.json                    ← SYS-049
│   ├── notifications.json                   ← SYS-050
│   ├── auto_sell_config.json                ← SYS-051
│   ├── pre_inventory_filter.json            ← SYS-052
│   ├── hotkeys.json                         ← SYS-056
│   ├── error_messages.json                  ← SYS-057
│   └── rate_limits.json                     ← SYS-058
│
├── world/                                   ⭐ NUEVA carpeta
│   └── day_night_cycle.json                 ← SYS-008
│
└── zones/
    ├── zone_definitions.json                ← SYS-007
    └── unlock_gates.json                    ← SYS-007
```

### 3.2 Resumen de cobertura

| Carpeta | Archivos | Sistemas cubiertos |
|---|---|---|
| `admin/` | 2 | SYS-070, SYS-071 |
| `base/` | 5 | SYS-005, SYS-059–062 |
| `combat/` | 1 | SYS-006 |
| `companions/` | 6 | SYS-010–015 |
| `economy/` | 9 | SYS-009, SYS-029–037 |
| `events/` | 4 | SYS-042–045 |
| `items/` | 11 | SYS-002–004, SYS-023–028, SYS-034, SYS-063 |
| `onboarding/` | 2 | SYS-064, SYS-066 |
| `progression/` | 9 + carpeta `battle_pass_seasons/` | SYS-001, SYS-016–022, SYS-040, SYS-041 |
| `quests/` | 3 | SYS-039, SYS-065 |
| `seasons/` | N | SYS-046 |
| `social/` | 2 | SYS-047, SYS-048 |
| `theme/` | 2 | (transversal) |
| `ui/` | 7 | SYS-049–052, SYS-056–058 |
| `world/` | 1 | SYS-008 |
| `zones/` | 2 | SYS-007 |
| **TOTAL** | **66+ JSONs en 16 carpetas** | **60 sistemas data-driven cubiertos** |

> Sistemas sin JSON (lógica pura Verse): SYS-053, SYS-054, SYS-055, SYS-067, SYS-068, SYS-072. Son 6, coinciden con `SYSTEMS_INDEX.md` §3.3.
> Sistema sin Verse (build-time only): SYS-038.

---

## 4. Carpeta `Content/Verse/` autoritativa

```
Content/Verse/
├── Core/                                    ← módulos transversales
│   ├── ModuleRegistry.verse                 ← SYS-072 (SPR-005)
│   ├── PersistenceLayer.verse               ← SYS-069 (SPR-008)
│   ├── TimeSync.verse                       ← SYS-068 (SPR-007)
│   ├── BigNumbers.verse                     ← SYS-067
│   ├── Logger.verse                         ← SYS-072 (SPR-006)
│   ├── EventBus.verse                       ← SYS-072 (SPR-009)
│   └── AdminCommands.verse                  ← SYS-070 (SPR-010)
│
├── Generated/                               ← OUTPUT de Python — NO editar manualmente
│   ├── Companions_Generated.verse           ← from data/companions/
│   ├── Items_Generated.verse                ← from data/items/
│   ├── Prices_Generated.verse               ← from data/economy/
│   ├── Quests_Generated.verse               ← from data/quests/
│   ├── ThemeConstants_Generated.verse       ← from data/theme/
│   ├── ModuleRegistryConstants.verse        ← from data/architecture/modules_manifest.json (Auditoría 2 — C1; SPR-005 + SPR-004 ext)
│   ├── EventBusDevice.verse                 ← from data/architecture/events_catalog.json (Auditoría 2 — C3 + H4 post-F-C-2; SPR-009 + SPR-004 ext)
│   ├── EventPayloads_Generated.verse        ← from data/architecture/events_catalog.json (Auditoría 2 — C3; SPR-009 + SPR-004 ext)
│   ├── BalanceCurves_Generated.verse        ← from BALANCE_FORMULAS.md (SPR-134)
│   ├── PlayerStats_Generated.verse          ← from data/progression/player_stats_base.json
│   ├── SkillTree_Generated.verse            ← from data/progression/skill_trees.json
│   ├── BattlePass_Generated.verse           ← from data/progression/battle_pass_seasons/
│   ├── Zones_Generated.verse                ← from data/zones/
│   ├── Achievements_Generated.verse         ← from data/progression/achievements.json
│   └── Localization_Generated.verse         ← from data/theme/localization_keys.json
│
├── Systems/
│   ├── Player/
│   │   ├── PlayerStats.verse                ← SYS-001
│   │   ├── PlayerInventory.verse            ← SYS-002
│   │   ├── PlayerProgression.verse          ← SYS-016, SYS-017
│   │   ├── PlayerSkillTree.verse            ← SYS-018
│   │   ├── PlayerRebirth.verse              ← SYS-020
│   │   └── PlayerDeathHandler.verse         ← SYS-009
│   │
│   ├── Companions/
│   │   ├── CompanionCore.verse              ← SYS-010, SYS-011, SYS-012, SYS-013
│   │   ├── CompanionBehavior.verse          ← SYS-014
│   │   ├── CompanionAssignment.verse        ← SYS-014
│   │   └── CollectionDex.verse              ← SYS-015
│   │
│   ├── Combat/
│   │   ├── CombatCore.verse                 ← SYS-006
│   │   ├── DamageCalculator.verse           ← SYS-006
│   │   └── AbilityExecutor.verse            ← SYS-019
│   │
│   ├── Economy/
│   │   ├── CurrencyManager.verse            ← SYS-029, SYS-030
│   │   ├── ShopSystem.verse                 ← SYS-032
│   │   ├── RotatingShop.verse               ← SYS-033
│   │   ├── PurchaseService.verse            ← SYS-031 (abstrae gems/vbucks/in-game)
│   │   ├── LootboxSystem.verse              ← SYS-034
│   │   ├── PitySystem.verse                 ← SYS-035
│   │   ├── TradeSystem.verse                ← SYS-036
│   │   └── AuctionSystem.verse              ← SYS-037
│   │
│   ├── Equipment/
│   │   ├── EquipmentSlots.verse             ← SYS-023, SYS-024
│   │   ├── EquipmentLeveling.verse          ← SYS-025
│   │   ├── ProtectorService.verse           ← SYS-026
│   │   ├── SetBonuses.verse                 ← SYS-027
│   │   └── RerollService.verse              ← SYS-028
│   │
│   ├── Quests/
│   │   ├── QuestEngine.verse                ← SYS-039, SYS-066
│   │   ├── DailyQuestRotator.verse          ← SYS-039
│   │   ├── WeeklyQuestRotator.verse         ← SYS-039
│   │   └── TutorialChain.verse              ← SYS-065
│   │
│   ├── Base/
│   │   ├── BaseLevelManager.verse           ← SYS-059
│   │   ├── BaseUpgrades.verse               ← SYS-005, SYS-060
│   │   ├── PassiveGenerators.verse          ← SYS-061
│   │   ├── OfflineCalculator.verse          ← SYS-062
│   │   └── CraftingTimers.verse             ← SYS-063
│   │
│   ├── World/
│   │   ├── ZoneManager.verse                ← SYS-007
│   │   ├── ResourceNodes.verse              ← SYS-003
│   │   ├── BossEncounters.verse             ← SYS-042
│   │   ├── HourlyBossPortal.verse           ← SYS-042
│   │   └── DayNightCycle.verse              ← SYS-008 ⭐ NUEVO (faltaba en `CONCEPT.md` §11.2)
│   │
│   ├── LiveOps/
│   │   ├── EventManager.verse               ← SYS-043, SYS-044
│   │   ├── DailyLoginRewards.verse          ← SYS-040
│   │   ├── TimePlayedRewards.verse          ← SYS-041
│   │   ├── BattlePass.verse                 ← SYS-022
│   │   ├── CodeRedemption.verse             ← SYS-045
│   │   ├── SeasonManager.verse              ← SYS-046
│   │   └── AchievementEngine.verse          ← SYS-021 ⭐ NUEVO (faltaba en `CONCEPT.md` §11.2)
│   │
│   ├── Social/
│   │   ├── LeaderboardSync.verse            ← SYS-047
│   │   ├── SocialDisplay.verse              ← SYS-048
│   │   └── ActivityLogUI.verse              ← SYS-049
│   │
│   └── UI/
│       ├── HUDController.verse              ← SYS-049, SYS-050, SYS-057
│       ├── NotificationPool.verse           ← SYS-050
│       ├── InventoryUI.verse                ← SYS-002, SYS-051–055
│       ├── DexUI.verse                      ← SYS-015, SYS-055
│       ├── ShopUI.verse                     ← SYS-032
│       ├── BasePanelUI.verse                ← SYS-060
│       ├── IdleSummaryUI.verse              ← SYS-054
│       └── CraftingUI.verse                 ← SYS-004 ⭐ NUEVO (faltaba en `CONCEPT.md` §11.2)
│
├── Devices/                                 ← Verse devices instanciables en UEFN editor
│   ├── GameManager.verse                    (root device, entry point: orquesta Init de Systems en OnBegin)
│   ├── ZonePortal.verse                     ← SYS-007
│   ├── HourlyBossTrigger.verse              ← SYS-042
│   ├── BasePlot.verse                       ← SYS-005
│   └── AdminPanel.verse                     ← SYS-070
│
└── Tests/                                   ← smoke tests Verse (ver §4.2)
```

### 4.1 Resumen Verse

| Subcarpeta | Archivos |
|---|---|
| `Core/` | 7 |
| `Generated/` | 13 |
| `Systems/Player/` | 6 |
| `Systems/Companions/` | 4 |
| `Systems/Combat/` | 3 |
| `Systems/Economy/` | 8 |
| `Systems/Equipment/` | 5 |
| `Systems/Quests/` | 4 |
| `Systems/Base/` | 5 |
| `Systems/World/` | 5 |
| `Systems/LiveOps/` | 7 |
| `Systems/Social/` | 3 |
| `Systems/UI/` | 8 |
| `Devices/` | 5 |
| `Tests/` | N (smoke tests, ver §4.2) |
| **TOTAL** | **83 archivos `.verse` runtime + N smoke tests** |

> §11.2 del CONCEPT enumeraba 60 archivos. Este árbol añade 3 que faltaban: `DayNightCycle.verse`, `AchievementEngine.verse`, `CraftingUI.verse`. El resto de los 20 nuevos son archivos `Generated/` adicionales (ver `BOOTSTRAP_PIPELINE.md` para por qué hacen falta).

### 4.2 Carpeta `Content/Verse/Tests/`

- **Propósito**: smoke tests Verse en runtime UEFN (no son tests unitarios — UEFN no expone framework). Verifican wiring crítico: bus de eventos vivo, persistencia idempotente, etc.
- **Naming canónico** (raíz `Tests/`): `test_<snake>.verse` — regex `^test_[A-Za-z0-9_]+\.verse$` (mayús permitidas en sufijos tipo `_SPR008` para trazabilidad cross-sprint).
- **Validador (§8)**: trata `Content/Verse/Tests/` como zona regulada. La raíz usa regla `Verse_tests`; la subcarpeta `canary/` usa regla `Verse_canary` (§4.2.1). Archivos que matchean el regex correspondiente se consideran implícitamente declarados (no aparecen en `UNDECLARED`).
- **Archivos actuales en raíz**: `test_event_bus_smoke.verse` (SPR-009 F-C smoke EventBus), `test_persistence_SPR008.verse` (SPR-008 persistencia idempotente).

### 4.2.1 Subcarpeta `Content/Verse/Tests/canary/`

- **Propósito**: throwaways de validación empírica de primitivas Verse (API real, sintaxis bordes, comportamiento failure contexts). Audit trail vivo de la lección de proceso **P5** (CHANGELOG B1.1-fix L4). NO son scratch — son evidencia commiteada de qué falló y qué pasó al canonizar cada lección.
- **Naming canónico**: `throwaway_<snake>.verse` — regex `^throwaway_[A-Za-z0-9_]+\.verse$`. Topic en snake_case identifica la primitiva validada.
- **Diferencia con `Tests/` raíz**: smoke tests (`test_*.verse`) verifican wiring runtime persistente. Canary throwaways (`throwaway_*.verse`) documentan empíricamente decisiones canónicas (lección 5, §2.4-bis, etc.) y se cross-referencian desde `CANARY_VALIDATION_LOG.md` con hash SHA-256.
- **Validador (§8)**: zona regulada con regla `Verse_canary` propia (distinta de `Verse_tests`). Archivos que matchean el regex se consideran implícitamente declarados.
- **Archivos actuales**: `throwaway_admin_state.verse` (SPR-010 Step 0 → v5 PASS, valida patrón canónico §2.4-bis "Core stateless + Device state-bearing", hash anchor `7c8d437b...`).
- **Política de retención**: los throwaways canary NO se borran. Vivirán indefinidamente como audit trail empírico. Si una lección queda obsoleta (cambio de API Verse upstream), el throwaway permanece + se añade entry nueva en `CANARY_VALIDATION_LOG.md` documentando la regresión.

---

## 5. Carpeta `scripts/` autoritativa

```
scripts/
├── init_unreal.py                           ← invocado al abrir UEFN (ver §5.1: requiere Startup Scripts si se mantiene en `scripts/`)
│
├── build/                                   ← pipeline ordenado (sufijo NN_)
│   ├── 00_validate_structure.py             ← este doc §8 (validador estructural — primer step)
│   ├── 01_validate_jsons.py                 ← SPR-003
│   ├── 02_export_constants_to_verse.py      ← SPR-004 (incluye BalanceCurves SPR-134)
│   ├── 03_generate_companion_prefabs.py     ← (TBD F2)
│   ├── 04_generate_zone_layouts.py          ← SPR-041 (Poisson disk)
│   ├── 05_apply_theme_pack.py               ← SPR-170 (bulk swap)
│   ├── 06_check_memory_budget.py            ← SPR-136
│   ├── 07_run_full_pipeline.py              ← SPR-174 (orquestador)
│   └── tests/                               ← golden contract pytest tests (ver §5.2)
│
├── tools/                                   ← scripts ad-hoc, sin orden
│   ├── balance_curve_visualizer.py          ← from BALANCE_FORMULAS.md
│   ├── close_sprint.py                      ← SPR-207 (genera/actualiza daily log al cerrar SPR; uso manual, ver WORKFLOW §3 Fase 4)
│   ├── dependency_cycle_check.py            ← SPR-205 (validador de ciclos en deps Verse, spec en MODULES §10.3)
│   ├── new_map_scaffolder.py                ← SPR-199
│   ├── localization_exporter.py             ← (TBD)
│   └── texture_audit.py                     ← SPR-195
│
├── maintenance/                             ← scripts mantenimiento recurrente productivo (D-A14: NO ad-hoc, ver §5.3)
│   └── check_orphan_files.ps1               ← detecta archivos huérfanos no referenciados en TRUTH/SYSTEMS_INDEX
│
└── utils/                                   ← libs internas reusables
    ├── unreal_helpers.py
    └── json_helpers.py
```

### 5.1 Reglas

- **`build/`**: scripts numerados se ejecutan en orden por el orquestador. Nunca añadir un `02b_` o `03_5_` — re-numerar si hace falta.
- **`build/tests/`**: subdir pytest (golden contracts, ver §5.2). NO se orquesta dentro del pipeline `build/`; se ejecuta vía `pytest scripts/build/tests/` standalone o en CI.
- **`tools/`**: ad-hoc, no se orquestan. Decisión D-A14: scripts one-shot o uso manual puntual.
- **`maintenance/`**: scripts de mantenimiento recurrente **productivo** (NO ad-hoc — ver §5.3). Distinción canónica D-A14 frente a `tools/`.
- **`utils/`**: importables desde build, tools y maintenance.
- **Cada script Python tiene `if __name__ == "__main__":`** para ser ejecutable standalone Y desde UEFN.
- **`init_unreal.py` (auto-load Python en UEFN)**: el plugin Python de Unreal Engine auto-carga `init_unreal.py` SOLO si está en `Content/Python/` ([dev.epicgames.com — Scripting the Unreal Editor using Python](https://dev.epicgames.com/documentation/en-us/unreal-engine/scripting-the-unreal-editor-using-python)). Mantenerlo en `scripts/` (decisión actual del proyecto, fuera de canon UE) requiere registro manual en `Project Settings → Plugins → Python → Startup Scripts` apuntando a `scripts/init_unreal.py`. Validar empíricamente que UEFN expone el Python Editor Script Plugin con el mismo workflow que UE estándar — si no, mover a `Content/Python/init_unreal.py` o aceptar que el script no corre al abrir el editor.

### 5.2 Carpeta `scripts/build/tests/`

- **Propósito**: golden contract tests pytest sobre los exporters de `build/` (validan que el output Verse generado coincide con un fixture esperado byte-a-byte modulo header). Promovido en SPR-009 F-C-3 (event bus exporter).
- **Naming canónico**: `test_<snake>.py` (regex `^test_[a-z][a-z0-9_]*\.py$`) o `__init__.py`. Fixtures bajo `fixtures/` siguen regla `data` (snake_case `*.json`).
- **Validador (§8)**: ruta `scripts/build/tests/` se enruta a regla `scripts_build_tests`; `scripts/build/tests/fixtures/` se enruta a regla `data`. Archivos que matchean se consideran implícitamente declarados (no aparecen en `UNDECLARED`).
- **Archivos actuales**: `__init__.py`, `test_exporter_event_bus.py`, `fixtures/event_bus_expected_contract.json` (SPR-009 F-C-3).

### 5.3 Carpeta `scripts/maintenance/`

- **Propósito**: scripts de mantenimiento **recurrente productivo** del repositorio — distintos de `tools/` (ad-hoc, D-A14). Ejemplo paradigmático: detección de archivos huérfanos pre-SPR para evitar drift acumulado.
- **Distinción D-A14 vs `tools/`**:
  - `tools/`: one-shot o uso manual puntual (ej. `texture_audit.py`, `balance_curve_visualizer.py`, `new_map_scaffolder.py`).
  - `maintenance/`: invocados en hooks pre-flight de cada SPR o en cron CI semanal/mensual (recurrente sistemático).
- **Naming**: `<snake_case>.{py,ps1}`. PowerShell admitido para integración Windows-first del proyecto.
- **Archivos actuales**: `check_orphan_files.ps1` (detecta archivos en disco no referenciados en TRUTH §3-§6 ni en SYSTEMS_INDEX.md).

---

## 6. Carpeta `docs/` autoritativa

```
docs/
├── CONCEPT.md                               ← maestro
├── PROMPT.md                                ← system prompt agnóstico
├── PROMPT_TEMPLATES.md
├── README.md                                ← (también top-level apunta aquí)
│
├── WORKFLOW.md
├── DEEPSEEK_CAPSULE.md
│
├── SYSTEMS_INDEX.md                         ⭐ NUEVO
├── SPRINTS_BACKLOG.md                       ⭐ NUEVO
├── FOLDER_STRUCTURE_TRUTH.md                ⭐ NUEVO (este doc)
├── MODULES_DEPENDENCY_GRAPH.md              ⭐ pendiente (4/4)
│
├── PERSISTENCE_MAP.md
├── BOOTSTRAP_PIPELINE.md
├── API_REFERENCE_GENERATED.md
├── JSON_SCHEMAS.md
├── BALANCE_FORMULAS.md
├── VERSE_SYNTAX_GUIDE.md                    ← lecciones empíricas sintaxis Verse (compilador UEFN)
│
├── UI_UX_STYLE_GUIDE.md
├── TESTING_PROTOCOL.md
├── EMERGENCY_ROLLBACK.md
├── GLOSSARY.md
│
├── CHANGELOG.md
├── DAILY_LOG.md                             ← plantilla canónica + instructivo del flujo (NO archivo vivo, ver §6.2)
├── POSTMORTEMS_INDEX.md                     ← índice de postmortems (ver §6.3 + carpeta postmortems/)
├── CANARY_VALIDATION_LOG.md                 ← log de throwaways canary (audit trail empírico P5, ver §4.2.1)
│
├── dailylog/                                ← un archivo por día (output de scripts/tools/close_sprint.py)
│   ├── .gitkeep
│   └── DL_YYYY-MM-DD_SPR-<tokens>_<autor>.md
│
├── postmortems/                             ← retrospectivas de incidentes (ver §6.3)
│   └── PM-<id>.md                           ← naming PM-<ID>.md (regex en §1.1 fila Postmortems)
│
└── HOWTO_NEW_MAP.md                         ← SPR-203 (futuro)
```

### 6.1 Reglas

- **Todos los docs en `SCREAMING_SNAKE.md`** (excepto `README.md` por convención).
- **Top-level `README.md`** es el único duplicado; el resto vive solo en `docs/`.
- **Docs futuros** se añaden aquí, no en raíz.

### 6.2 Carpeta `docs/dailylog/`

- **Naming canónico** de cada archivo: `DL_YYYY-MM-DD_SPR-<tokens>_<autor>.md` — regex `^DL_\d{4}-\d{2}-\d{2}_SPR-[\w+\-]+_[a-z0-9]+\.md$`.
- **`<tokens>`**: lista de segmentos unidos por `+`. Cada segmento es el número de un sprint (`001`, `002`) o un marcador de hotfix (`FIX1`, `FIX2`) relativo al sprint base anterior. Ejemplos: `SPR-001`, `SPR-001+FIX1`, `SPR-001+002`, `SPR-001+FIX1+002`.
- **`<autor>`**: nickname lowercase (regex `^[a-z0-9]+$`) leído de `.dailylog_user` (gitignored).
- **Generación**: única fuente válida es `scripts/tools/close_sprint.py` (ver §5 + WORKFLOW §3 Fase 4). El humano NO crea daily logs a mano salvo retroactivos puntuales.
- **Idempotencia**: regenerar el daily log de un día ya cerrado no duplica entradas; solo refresca los bloques marcados `<!-- BEGIN AUTO:... -->` y preserva el bloque `<!-- BEGIN MANUAL --> ... <!-- END MANUAL -->`.
- **Histórico**: NO se mueve, NO se archiva. Cada día queda persistido como un archivo independiente en esta carpeta.
- **`.gitkeep`** garantiza que la carpeta se trackee aunque esté vacía. El validador estructural (§8) ignora `.gitkeep` para `BAD_NAMING` y `UNDECLARED`.
- **Excepción de naming pattern para validador**: archivos `DL_*.md` aquí cumplen su propia regla (regex de §1.1 fila *Daily logs*), NO la regla `docs` genérica (`SCREAMING_SNAKE.md`). El validador de §8 debe contemplarlo si se extiende a esta carpeta — hasta entonces, los daily logs caen en `UNDECLARED` y solo son warning. Bug conocido: SPR-001-FIX-2 (parser TRUTH) lo aborda.

### 6.3 Carpeta `docs/postmortems/`

- **Propósito**: retrospectivas de **incidentes** — bloqueos no triviales, recoveries de sesión perdida, regresiones inesperadas. Distintos de los daily logs (rutinarios, automáticos) y del `POSTMORTEMS_INDEX.md` (índice de entradas, vive en `docs/` raíz).
- **Naming canónico**: `PM-<id>.md` — regex `^PM-[A-Za-z0-9_-]+\.md$`. `<id>` admite mayús/minús/dígitos/`-`/`_`. Ejemplos commiteados: `PM-SPR-009-blocked.md`, `PM-RECOVERY-2026-05-08.md`, `PM-SPR-211.md`.
- **Generación**: humano. NO automatizado. Se redacta al cerrar el incidente y se referencia desde `POSTMORTEMS_INDEX.md` y desde el daily log de la fecha en que se cerró.
- **Validador (§8)**: ruta `docs/postmortems/` se enruta a regla `docs_postmortems`; archivos que matchean el regex se consideran implícitamente declarados (no aparecen en `UNDECLARED`, no caen en `BAD_NAMING` por la regla `docs` genérica).
- **Histórico**: NO se mueve, NO se archiva. Cada postmortem queda persistido como un archivo independiente en esta carpeta.

---

## 7. Discrepancias resueltas vs CONCEPT §11

### 7.1 Resoluciones decididas

| Punto | CONCEPT §11 dice | SYSTEMS §8.2 dice | **Resuelto a** | Motivo |
|---|---|---|---|---|
| `achievements.json` | `data/quests/` | `data/progression/` | **`data/progression/achievements.json`** | Achievements son progresión permanente del jugador, no quests rotativas. |
| Shop pricing | `data/economy/prices.json` | `data/economy/shop.json` | **`data/economy/shop.json`** | Más amplio (items + precios + filtros + flags). `prices.json` se elimina. |
| `data/world/` | no existe | `data/world/day_night_cycle.json` | **Crear `data/world/`** con ese único archivo | SYS-008 necesita JSON. Carpeta válida. |
| `data/combat/` | no existe | `data/combat/damage_formulas.json` | **Crear `data/combat/`** | SYS-006 necesita JSON. Carpeta válida. |
| `data/seasons/` | no existe | `data/seasons/season_XX.json` | **Crear `data/seasons/`** | SYS-046 necesita estructura específica. |
| `data/social/` | no existe | `data/social/*.json` | **Crear `data/social/`** | SYS-047, SYS-048 lo necesitan. |
| `data/ui/` | no existe | `data/ui/*.json` | **Crear `data/ui/`** | 7 sistemas QoL/HUD lo necesitan. |
| `data/onboarding/` | no existe | `data/onboarding/*.json` | **Crear `data/onboarding/`** | SYS-064, SYS-066 lo necesitan. |
| `data/admin/` | no existe | `data/admin/*.json` | **Crear `data/admin/`** | SYS-070, SYS-071 lo necesitan. |
| `data/architecture/` | no existe | `data/architecture/modules_manifest.json`, `data/architecture/events_catalog.json` | **Crear `data/architecture/`** | Auditoría 2 — C1+C3. SYS-072 lo necesita (Registry + EventBus tipados). |
| `Verse/Systems/UI/CraftingUI.verse` | no existe | implícito en SPR-028 | **Añadido** | Crafting necesita UI propia. |
| `Verse/Systems/World/DayNightCycle.verse` | no existe | implícito | **Añadido** | SYS-008 necesita módulo dedicado. |
| `Verse/Systems/LiveOps/AchievementEngine.verse` | no existe | implícito | **Añadido** | SYS-021 necesita módulo dedicado. |

### 7.2 Acción consecuente

**`CONCEPT.md` §11.1 y §11.2 deben actualizarse** para coincidir con este doc en próxima entrada de `CHANGELOG.md`. Hasta entonces, **este doc gana** por regla de §0 supra.

---

## 8. Script validador (Python)

**Path**: `scripts/build/00_validate_structure.py`
**Sprint**: forma parte de SPR-001 (scaffolding) y SPR-003 (validador).
**Cuándo se ejecuta**: paso 0 del pipeline (antes de validar JSONs). Invocado automáticamente por el orquestador `07_run_full_pipeline.py` (BOOTSTRAP §7.2). También usable como pre-commit hook.

> **Decisión cerrada (Auditoría 3 — H3.7)**: el script vive en `scripts/build/` (NO en `tools/`) porque es parte del pipeline ordenado y debe correr automáticamente como primer step. Los scripts en `tools/` son ad-hoc y no se orquestan.

### 8.1 Especificación funcional

1. **Lee este archivo** (`docs/FOLDER_STRUCTURE_TRUTH.md`).
2. **Extrae todos los paths declarados** de §3, §4, §5, §6 (parsing de árboles markdown). Solo procesa bloques `` ``` `` desnudos (sin lenguaje); los bloques `` ```python ``, `` ```bash ``, etc. se ignoran para evitar parsear líneas de código como paths fantasma.
3. **Compara con el filesystem real** del repo.
4. **Reporta**:
   - ❌ archivos declarados aquí pero **ausentes** en disco → `MISSING`
   - ⚠️ archivos en disco no declarados aquí → `UNDECLARED`
   - ❌ archivos en `data/`, `Content/Verse/Systems/`, `Content/Verse/Devices/` con naming incorrecto → `BAD_NAMING`
5. **Exit code**: 0 si todo OK, 1 si hay `MISSING`, 2 si hay `BAD_NAMING`. `UNDECLARED` solo warning (puede ser scratch).
6. **Flags**:
   - `--strict`: tratar `UNDECLARED` como error (exit 3).
   - `--allow-missing`: degradar `MISSING` a warning (exit 0). **Uso típico**: SPR-001 (scaffolding inicial — el repo está casi vacío y MISSING es esperado por diseño) y cualquier sprint scaffolding donde el árbol se construye gradualmente. **NO usar en CI ni post-F0**: el orquestador `07_run_full_pipeline.py` y el pre-commit hook deben correr SIN este flag (un MISSING en F1+ sí es regresión).

### 8.2 Implementación de referencia

```python
#!/usr/bin/env python3
"""
00_validate_structure.py — valida que el filesystem coincide con
docs/FOLDER_STRUCTURE_TRUTH.md.

Uso:
    python scripts/build/00_validate_structure.py [--strict]

Exit codes:
    0 — OK
    1 — archivos declarados ausentes
    2 — naming incorrecto detectado
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TRUTH = ROOT / "docs" / "FOLDER_STRUCTURE_TRUTH.md"

# Regex de naming (extracto — implementación real path-aware en scripts/build/00_validate_structure.py)
NAMING_RULES = {
    "data": re.compile(r"^[a-z][a-z0-9_]*\.json$"),
    "Verse": re.compile(r"^[A-Z][A-Za-z0-9]*\.verse$"),
    "Verse_tests": re.compile(r"^test_[A-Za-z0-9_]+\.verse$"),
    "Verse_canary": re.compile(r"^throwaway_[A-Za-z0-9_]+\.verse$"),
    "Generated": re.compile(r"^[A-Z][A-Za-z0-9]*_Generated\.verse$|^ModuleRegistryConstants\.verse$|^EventBusDevice\.verse$"),
    "scripts_build": re.compile(r"^\d{2}_[a-z][a-z0-9_]*\.py$"),
    "scripts_build_tests": re.compile(r"^test_[a-z][a-z0-9_]*\.py$|^__init__\.py$"),
    "docs": re.compile(r"^[A-Z][A-Z0-9_]*\.md$|^README\.md$"),
    "docs_dailylog": re.compile(r"^DL_\d{4}-\d{2}-\d{2}_SPR-[\w+\-]+_[a-z0-9]+\.md$"),
    "docs_postmortems": re.compile(r"^PM-[A-Za-z0-9_-]+\.md$"),
}
# Path-aware rule selection: docs_rule_for() / scripts_build_rule_for() / verse_tests_rule_for()
# definidos en el script real para enrutar zonas reguladas a la regla correcta según subpath.

def parse_truth_paths(md_text: str) -> set[str]:
    """Extrae paths de los bloques ``` SIN lenguaje de §3, §4, §5, §6.

    IMPORTANTE: solo procesa bloques `` ``` `` "desnudos" (sin lenguaje tras
    los backticks). Bloques `` ```python ``, `` ```bash ``, `` ```gitignore ``
    se ignoran — sus líneas pueden contener tokens con `.` (ej. `paths.add(full)`)
    que el parser confundiría con archivos.
    """
    paths = set()
    in_tree = False
    current_indent = []  # stack de (indent, name)
    for line in md_text.splitlines():
        if line.startswith("```"):
            # Solo entrar en modo árbol si el fence es desnudo (` ``` ` exacto, sin lenguaje)
            fence_lang = line[3:].strip()
            if not in_tree and fence_lang == "":
                in_tree = True
                current_indent = []
            elif in_tree:
                in_tree = False
                current_indent = []
            # Si fence con lenguaje y no estábamos in_tree → ignorar (no entrar)
            continue
        if not in_tree:
            continue
        # Limpia caracteres de árbol
        cleaned = re.sub(r"^[│├└─\s]+", "", line)
        if not cleaned or cleaned.startswith("#") or cleaned.startswith("←"):
            continue
        # Indent count
        indent = len(line) - len(line.lstrip("│├└─ "))
        # Nombre = primer token
        name = cleaned.split()[0].rstrip("/")
        # Pop stack hasta encontrar parent
        while current_indent and current_indent[-1][0] >= indent:
            current_indent.pop()
        full = "/".join(p[1] for p in current_indent) + ("/" if current_indent else "") + name
        current_indent.append((indent, name))
        # Solo registramos archivos (con extensión) o carpetas listadas como parents
        if "." in name:
            paths.add(full)
    return paths

def validate(strict: bool = False, allow_missing: bool = False) -> int:
    if not TRUTH.exists():
        print(f"❌ No existe {TRUTH}", file=sys.stderr)
        return 1

    declared = parse_truth_paths(TRUTH.read_text(encoding="utf-8"))
    print(f"📋 {len(declared)} paths declarados en TRUTH")

    missing, bad_naming, undeclared = [], [], []

    # 1) MISSING: declarados que no existen
    for rel in declared:
        if not (ROOT / rel).exists():
            missing.append(rel)

    # 2) BAD_NAMING: archivos del repo en zonas reguladas
    for folder, rule_key in [
        ("data", "data"),
        ("Content/Verse/Systems", "Verse"),
        ("Content/Verse/Core", "Verse"),
        ("Content/Verse/Devices", "Verse"),
        ("Content/Verse/Generated", "Generated"),
        ("scripts/build", "scripts_build"),
        ("docs", "docs"),
    ]:
        base = ROOT / folder
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if p.is_file():
                if not NAMING_RULES[rule_key].match(p.name):
                    bad_naming.append(str(p.relative_to(ROOT)))

    # 3) UNDECLARED: warning
    for folder in ["data", "Content/Verse", "scripts", "docs"]:
        base = ROOT / folder
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if p.is_file():
                rel = str(p.relative_to(ROOT))
                if rel not in declared:
                    undeclared.append(rel)

    # Reporte
    if missing:
        label = "⚠️  MISSING (ignorado por --allow-missing)" if allow_missing else "❌ MISSING"
        print(f"\n{label} ({len(missing)}):")
        for m in missing[:20]:
            print(f"   {m}")
        if len(missing) > 20:
            print(f"   ... y {len(missing) - 20} más")
    if bad_naming:
        print(f"\n❌ BAD_NAMING ({len(bad_naming)}):")
        for b in bad_naming:
            print(f"   {b}")
    if undeclared:
        print(f"\n⚠️  UNDECLARED ({len(undeclared)}):")
        for u in undeclared[:20]:
            print(f"   {u}")
        if len(undeclared) > 20:
            print(f"   ... y {len(undeclared) - 20} más")

    if missing and not allow_missing:
        return 1
    if bad_naming:
        return 2
    if strict and undeclared:
        return 3
    if missing and allow_missing:
        print(f"\n✅ OK (relajado: {len(missing)} missing ignorados — uso F0 / scaffolding)")
    else:
        print("\n✅ OK — estructura coincide con TRUTH")
    return 0

if __name__ == "__main__":
    sys.exit(validate(
        strict="--strict" in sys.argv,
        allow_missing="--allow-missing" in sys.argv,
    ))
```

### 8.3 Integración con pipeline

- **Orquestador (`07_run_full_pipeline.py`)**: invoca `00_validate_structure.py` como **primer step** de `STEPS` antes que `01_validate_jsons.py` (BOOTSTRAP_PIPELINE.md §7.2). Si exit ≠ 0, aborta el pipeline entero antes de generar nada — protege contra drift estructural propagado a artifacts.
- **Hook pre-commit**: `pre-commit` runs `00_validate_structure.py` → bloquea commit si exit ≠ 0. Captura drift antes de que llegue a CI.
- **CI**: corre el pipeline completo (`07_run_full_pipeline.py`), por lo que el validador estructural ya es step 0 implícito.
- **UEFN**: `init_unreal.py` lo invoca al abrir el editor → muestra banner si falla. **Requiere que `init_unreal.py` esté efectivamente registrado** (ver §5.1) — si está en `scripts/` sin Startup Scripts configurado, este hook no corre.
- **Excepción F0 (SPR-001 → SPR-009)**: durante el scaffolding inicial el árbol se construye gradualmente y `MISSING` es esperado por diseño (~209 archivos missing tras SPR-001 — los crean SPR-002+). Usar `python scripts/build/00_validate_structure.py --allow-missing` durante F0. A partir de SPR-010 (cierre de F0), el validador debe pasar SIN flag (exit 0 limpio sobre el árbol completo de F0). Pre-commit hook se activa SIN `--allow-missing` desde SPR-010 en adelante.

---

## 9. Reglas de cambio

1. **Cualquier nueva carpeta o archivo se declara aquí PRIMERO**, antes de crearlo en disco.
2. **Eliminar** un path requiere entrada en `CHANGELOG.md` con motivo + referencia a sprint.
3. **Renombrar** = eliminar + añadir, ambos documentados.
4. **Discrepancia con CONCEPT.md** se resuelve actualizando CONCEPT, no este doc.
5. **El validador (§8) corre en pre-commit** — drift no merge-eable.

---

**Total: 16 carpetas `data/`, 14 subcarpetas Verse, 4 subcarpetas `scripts/`. 66+ JSONs, 83 `.verse`, 17 scripts Python (1 `init_unreal` + 8 `build/` + 6 `tools/` + 2 `utils/`). 0 ambigüedades conocidas tras Auditoría retrospectiva Bloque 3 (mayo 2026; sumado `dependency_cycle_check.py` formalizado vía SPR-205) + Bloque 4 (mayo 2026; sumado `close_sprint.py` formalizado vía SPR-207, sistema dailylog).**
