# 🕸️ MODULES_DEPENDENCY_GRAPH — Grafo de dependencias entre módulos Verse

> **Quién depende de quién. Qué se rompe si tocas X.**
>
> Cada módulo lista: **qué importa** (deps directas) y **quién lo importa** (consumidores). Si tocas un módulo Core, miras quién lo consume antes de cambiar firma. Si añades un módulo, declaras sus deps aquí ANTES de escribir código.
>
> Fuente única para `using { /<ProjectName>/<Folder>/<Module> }` (módulos del proyecto) y `using { /Verse.org/... }`, `using { /Fortnite.com/... }`, `using { /UnrealEngine.com/... }` (módulos de plataforma). Si código real diverge → este doc gana o se actualiza por sprint.
>
> **Decisión cerrada (paths)**: el root del path Verse = nombre del proyecto UEFN (visible en `/localhost/<ProjectName>/...` durante desarrollo). Sustituir `<ProjectName>` por el nombre real al crear el proyecto. **Separadores siempre `/`, nunca `.`. La carpeta `Content/Verse/` NO aparece en el path** — el root Verse del proyecto se mapea directamente al inicio del path.
>
> **Decisión cerrada (arquitectura Core, Auditoría 2 — C1)**: los 6 módulos Core (Logger, EventBus, TimeSync, PersistenceLayer, BigNumbers, AdminCommands) + ModuleRegistry son **singletons top-level estáticos**, NO `creative_device`, NO se auto-registran. Verse los inicializa antes de cualquier `OnBegin`. Acceso por `using { /<ProjectName>/Core/<Modulo> }`. ModuleRegistry sirve solo a Systems gameplay (Capa 2+) para resolver lookup runtime y evitar ciclos de import compile-time. Detalle en §2.1 + §4.7.
>
> **Decisión cerrada (EventBus tipado, Auditoría 2 — C3)**: el EventBus operativo se **genera** desde `data/architecture/events_catalog.json`, componiendo instancias `event(payload_t)` nativas de Verse. Type-safety compile-time. Sin string-magic. Detalle en §4.2 + §11.2 + `BOOTSTRAP_PIPELINE.md` §11.
>
> ⚠️ **SPR-211 (2026-05-07) — sintaxis Verse moderna**: este doc fue auditado contra build UEFN real. Algunas afirmaciones quedaron obsoletas. Autoridad sintáctica vigente: `docs/VERSE_SYNTAX_GUIDE.md`. Cambios principales:
> - **Patrón Singleton `<x>_module := class<concrete>:` ya NO aplica a Cores sin state** (Logger, TimeSync). Falla con err 3512 (lección 8 de la guide). Patrón vigente: `Module<public> := module:` (namespace, sin archetype). Las menciones de `logger_module := class<concrete>:` en este doc están obsoletas.
> - **Path canónico SÍ incluye `Verse/`**: `/lexosi@fortnite.com/RPG_Survival/Verse/Core/Logger`. La afirmación de §1.4 *"`Content/Verse/` NO aparece en el path"* es obsoleta.
> - **Sintaxis dotted relative SÍ válida** (preferida en VS Code Quick Fix): `using { Verse.Core.Logger }`.
> - Cores con state mutable (PersistenceLayer SPR-008) — patrón TBD, ver `VERSE_SYNTAX_GUIDE.md` §2.4.

---

## 🧭 Índice

1. [Reglas del grafo](#1-reglas-del-grafo)
2. [Capas y orden de carga](#2-capas-y-orden-de-carga)
3. [Grafo visual de capas](#3-grafo-visual-de-capas)
4. [Capa 0 — Core (transversales)](#4-capa-0--core-transversales)
5. [Capa 1 — Generated](#5-capa-1--generated)
6. [Capa 2 — Systems base](#6-capa-2--systems-base)
7. [Capa 3 — Systems gameplay](#7-capa-3--systems-gameplay)
8. [Capa 4 — UI + LiveOps + Social](#8-capa-4--ui--liveops--social)
9. [Capa 5 — Devices](#9-capa-5--devices)
10. [Reglas de cambio anti-rotura](#10-reglas-de-cambio-anti-rotura)
11. [Análisis de impacto rápido](#11-análisis-de-impacto-rápido)

---

## 1. Reglas del grafo

### 1.1 Principios inquebrantables

1. **Acíclico**: ningún ciclo. Si A → B, entonces B no puede → A. Verificado por el script validador (§10.3).
2. **Capa N solo importa capas 0 → N-1**, **nunca** capas N+ (o iguales en algunos casos restringidos).
3. **Generated/ es solo lectura para Systems**. Nunca un Systems modifica un Generated.
4. **Core/ no importa nada de Systems/ ni Devices/**. Nunca.
5. **Devices/ es la capa más alta**. Nadie importa Devices.

### 1.2 Notación

- **`→`** : "importa" / "depende de" (compile-time)
- **`⇒`** : "emite evento que escucha" (runtime, vía EventBus, **no es dep compile-time**)
- **`📥`** : consumidores (quién depende de mí)
- **`📤`** : dependencias (a quién dependo)
- **`🔒`** : dependencia obligatoria (rompe build sin ella)
- **`🔓`** : dependencia opcional (graceful degradation)
- **`⚡`** : dependencia runtime-only (vía Module Registry lookup, no import)

### 1.3 Capas

| # | Nombre | Carpeta | Regla |
|---|---|---|---|
| 0 | Core | `Content/Verse/Core/` | No importa de ninguna capa. |
| 1 | Generated | `Content/Verse/Generated/` | Importa solo Capa 0. |
| 2 | Systems base | `Systems/Player/`, `Systems/World/`, `Systems/Combat/`, `Systems/Economy/`, `Systems/Equipment/`, `Systems/Companions/`, `Systems/Quests/`, `Systems/Base/` | Importa Capas 0–1. **Limited cross-imports** entre subcarpetas. |
| 3 | Systems gameplay top | (mismo nivel que 2 pero compuesto) | Importa 0–2. |
| 4 | UI + LiveOps + Social | `Systems/UI/`, `Systems/LiveOps/`, `Systems/Social/` | Importa 0–3. |
| 5 | Devices | `Devices/` | Importa cualquier capa, nadie lo importa. |

### 1.4 Sintaxis canónica de paths Verse (regla maestra)

> ⚠️ **OBSOLETO post-SPR-211 (2026-05-07)**. Este §1.4 entero está desactualizado. Autoridad sintáctica vigente: `docs/VERSE_SYNTAX_GUIDE.md` §1 (lecciones 1, 2, 14). Resumen del cambio:
>
> - Path canónico real **incluye** `Verse/`: `/lexosi@fortnite.com/RPG_Survival/Verse/Core/Logger`.
> - Sintaxis dotted relative SÍ válida y preferida (VS Code Quick Fix la ofrece): `using { Verse.Core.Logger }`.
> - Placeholder `<ProjectName>` LITERAL falla con `vErr:S26`.
> - Archivos sin `module:` wrapper exportan al scope de la **carpeta padre**, no al nombre del archivo (lección 14).
>
> Cuerpo de §1.4 conservado abajo por trazabilidad histórica. **NO usar como referencia operativa**.

> **Decisión cerrada.** Toda referencia a paths Verse del proyecto sigue esta regla. Validador `dependency_cycle_check.py` falla la build si ve `/Game.Content.Verse...` (path antiguo incorrecto).

**Forma correcta**:

```verse
# Plataforma (módulos de Epic, siempre tal cual)
using { /Fortnite.com/Devices }
using { /Verse.org/Simulation }
using { /UnrealEngine.com/Temporary/Diagnostics }

# Módulos del proyecto (root = nombre del proyecto UEFN)
using { /<ProjectName>/Core }
using { /<ProjectName>/Generated }
using { /<ProjectName>/Systems/Player }
using { /<ProjectName>/Systems/Companions }
using { /<ProjectName>/Devices }
```

**Reglas duras**:

| Regla | Aplica |
|---|---|
| Separador es `/`, **nunca `.`** | siempre |
| Root del path = `<ProjectName>` (nombre del proyecto UEFN) | módulos propios |
| `Content/Verse/` **NO aparece** en el path | el root Verse se mapea directo |
| Durante desarrollo en editor el path real es `/localhost/<ProjectName>/...` | autocompletado del editor |
| Forma corta `using { module_name }` solo si `.verse` está en mismo directorio | excepción |
| Submódulos: `using { /<ProjectName>/A/B }` o `using { /<ProjectName>/A.B }` (notación punto **dentro de** un identificador después del `/`, no como separador de path) | nested |

**Forma incorrecta** (rechazada por compilador, captura del foro: *"Invalid access of internal module"*):

```verse
using { /Game.Content.Verse.Generated.Companions_Generated }   # ❌ sintaxis inventada
using { /Localhost/MyProject/Sub1.Sub2 }                       # ❌ dotted path como separador
using { Sub1.Sub2 }                                            # ❌ sin barra inicial
```

**Sustitución del placeholder**: cuando el proyecto UEFN real esté creado, ejecutar:

```bash
# scripts/tools/replace_project_name.py — placeholder a generar
# Reemplaza /<ProjectName>/ por el nombre real en todos los .verse y docs.
python scripts/tools/replace_project_name.py --name=MyActualProjectName
```

(Script a crear como sub-tarea de SPR-001.)

**Fuente oficial**: https://dev.epicgames.com/documentation/en-us/fortnite/modules-and-paths-in-verse — *"To import modules from other Verse files, you can use either a local path such as `using { /YourVerseFolder/your_module }`"*.

---

## 2. Capas y orden de carga

### 2.1 Cómo inicializa Verse (no lo decidimos nosotros)

> **Decisión cerrada (Auditoría 2 — C1)**. Verse inicializa **todas** las constantes a nivel de módulo (`Logger : logger_module = logger_module{}`, `Global : global = global{}`, etc.) **antes** de que cualquier `OnBegin` de `creative_device` se ejecute. No hay "orden de carga" que el desarrollador controle — el compilador resuelve el grafo de inicialización por las dependencias declaradas en compile-time (`using {}` + referencias a constantes top-level).
>
> Fuente oficial: [Constants and Variables in Verse — Epic Dev Docs](https://dev.epicgames.com/documentation/en-us/fortnite/constants-and-variables-in-verse). Patrón singleton oficial: [forums.unrealengine.com — singletons in Verse](https://forums.unrealengine.com/t/i-came-up-with-a-way-to-make-singletons-in-verse/1139453).

> **Specifier `<concrete>` obligatorio (decisión cerrada Auditoría 3 — H3.1)**: el tipo `<x>_module` que se instancia con archetype vacío (`<x>_module{}`) DEBE declararse como `class<concrete>:`, no como `class:` ni como `module:`. Razón ([dev.epicgames.com — Class in Verse](https://dev.epicgames.com/documentation/en-us/fortnite/class-in-verse)): *"When a class has the concrete specifier, it is possible to construct it with an empty archetype, such as cat{}. This means that every field of the class must have a default value."* Sin `<concrete>` el constructor `<x>_module{}` no compila garantizadamente. Aplica a (1) los 6 Core (Logger, EventBus, TimeSync, PersistenceLayer, BigNumbers, AdminCommands) + ModuleRegistry — singletons top-level, y (2) los Systems registrables Capa 2+ (PlayerStats, PlayerInventory, CurrencyManager, etc.) — se instancian con `<id>_module{}` en `OnBegin` del device antes de registrarse en el Registry. NO confundir con `module := module:` (palabra reservada de namespace, distinta sintaxis sin archetype).

#### Implicación arquitectónica

**Los 6 módulos Core son singletons estáticos top-level. NO heredan de `creative_device`. NO se registran en `ModuleRegistry`. Se acceden directamente con `using { /<ProjectName>/Core/<NombreModulo> }`.**

```verse
# Patrón canónico vigente (post SPR-211) para Core sin state
# Archivo: Content/Verse/Core/Logger.verse

using { /Verse.org/Simulation }

Logger<public> := module:

    LogInfo<public>(Module:string, Message:string):void=
        Print("[INFO][{Module}] {Message}")
    # ... resto de niveles
```

Cualquier consumidor:

```verse
using { Verse.Core.Logger }

# uso directo, sin Registry, sin lookup
Logger.LogInfo("PlayerStats", "Cargando datos")
```

> **SPR-211**: el patrón legacy `logger_module := class<concrete>:` + `Logger : logger_module = logger_module{}` falla con err 3512 (clases con métodos `<decides>` propagan `<transacts>` al instance, top-level es `<computes>` puro). Solución vigente arriba: `Module<public> := module:` namespace, sin archetype. Aplica a Cores sin state mutable (Logger, TimeSync). Caso "Core con state" (PersistenceLayer SPR-008) queda TBD — ver `VERSE_SYNTAX_GUIDE.md` §2.4.

#### Orden CONCEPTUAL (no operativo) de los Core

Este orden refleja **dependencias compile-time** entre Core, no orden de ejecución (Verse lo decide solo). Sirve como mapa mental para el desarrollador:

| # | Módulo Core | Depende compile-time de | Por qué |
|---|---|---|---|
| 1 | `Logger` | nada | base de logging, sin dependencias |
| 2 | `EventBus` | `Logger` | loguea suscripciones/emisiones |
| 3 | `TimeSync` | `Logger` | loguea drift y warnings |
| 4 | `PersistenceLayer` | `Logger` | loguea load/save y validación defensiva |
| 5 | `BigNumbers` | `Logger` | loguea overflow al rango int64 |
| 6 | `AdminCommands` | `Logger`, `PersistenceLayer`, `EventBus` | loguea ejecuciones, persiste flags admin, emite events |
| 7 | `ModuleRegistry` | `Logger` | servicio de **lookup runtime para Systems**, NO orquestador de Core |

**Crítico**: ModuleRegistry NO inicializa los Core. Verse lo hace por sí mismo. ModuleRegistry solo expone `GetSystem<T>()` para Systems gameplay (Capa 2+) que necesitan resolver dependencias circulares de import (ver §4.7).

#### Capas superiores (orden de uso, no de carga)

```
Capa 1 — Generated      → constantes inmutables, sin lógica, leídas por Capa 2+
Capa 2 — Systems base   → PlayerStats, PlayerInventory, etc. Se registran en ModuleRegistry.
Capa 3 — Systems top    → PlayerProgression, ShopSystem, etc. Se registran.
Capa 4 — UI/LiveOps     → consumen Systems vía Registry o import directo.
Capa 5 — Devices        → creative_device instanciados en UEFN editor. OnBegin = entry point.
```

`Devices/GameManager.verse` es el **entry point del juego**: su `OnBegin` arranca la lógica de Systems registrándolos en `ModuleRegistry` y disparando eventos `game_started`. Los Core ya están vivos cuando `OnBegin` corre.

### 2.2 Race conditions evitadas

- ✅ Core son singletons top-level → vivos antes que cualquier Systems los necesite.
- ✅ `Generated/*` son constantes inmutables → vivas antes que cualquier Systems las lea (Capa 1 inicializa antes que Capa 2 por dependencia compile-time).
- ✅ `PlayerStats` lee `Generated/PlayerStats_Generated.verse` → Generated existe en compile-time.
- ✅ `AchievementEngine` se suscribe a eventos en su propio `Init()` (llamado por GameManager) → no hay deps compile-time hacia los emisores, solo runtime via `EventBus.<Evento>.Subscribe(handler_tipado)` por evento (un `Subscribe` por cada `event(payload_t)` del catálogo, ver §11.2).
- ⚠️ **Lo único que sí controlamos**: el orden en que `GameManager.OnBegin` llama a `Init()` de los Systems. Documentado en `BOOTSTRAP_PIPELINE.md` §pipeline-runtime.

---

## 3. Grafo visual de capas

```
┌─────────────────────────────────────────────────────────────┐
│ Capa 5 — DEVICES                                            │
│   GameManager  AdminPanel  ZonePortal  HourlyBossTrigger    │
│                BasePlot                                     │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────┴──────────────────────────────────┐
│ Capa 4 — UI + LiveOps + Social                              │
│   HUDController  InventoryUI  DexUI  ShopUI  CraftingUI     │
│   BasePanelUI  IdleSummaryUI  NotificationPool              │
│   BattlePass  DailyLoginRewards  TimePlayedRewards          │
│   EventManager  CodeRedemption  SeasonManager               │
│   AchievementEngine  LeaderboardSync  SocialDisplay         │
│   ActivityLogUI                                             │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────┴──────────────────────────────────┐
│ Capa 3 — Systems gameplay top                               │
│   PlayerProgression  PlayerRebirth  PlayerSkillTree         │
│   CombatCore  ShopSystem  RotatingShop  PurchaseService     │
│   LootboxSystem  PitySystem  TradeSystem  AuctionSystem     │
│   ZoneManager  BossEncounters  HourlyBossPortal             │
│   QuestEngine  TutorialChain  DailyQuestRotator             │
│   WeeklyQuestRotator  CompanionAssignment  CollectionDex    │
│   EquipmentLeveling  ProtectorService  SetBonuses           │
│   RerollService  BaseLevelManager  BaseUpgrades             │
│   PassiveGenerators  OfflineCalculator  CraftingTimers      │
│   DayNightCycle                                             │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────┴──────────────────────────────────┐
│ Capa 2 — Systems base                                       │
│   PlayerStats  PlayerInventory  PlayerDeathHandler          │
│   CompanionCore  CompanionBehavior  EquipmentSlots          │
│   DamageCalculator  AbilityExecutor  ResourceNodes          │
│   CurrencyManager                                           │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────┴──────────────────────────────────┐
│ Capa 1 — Generated (constantes, sin lógica)                 │
│   Companions_Generated  Items_Generated  Prices_Generated   │
│   Quests_Generated  ThemeConstants_Generated                │
│   ModuleRegistryConstants  BalanceCurves_Generated          │
│   PlayerStats_Generated  SkillTree_Generated                │
│   BattlePass_Generated  Zones_Generated                     │
│   Achievements_Generated  Localization_Generated            │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────┴──────────────────────────────────┐
│ Capa 0 — Core (transversales)                               │
│   Logger  EventBus  TimeSync  PersistenceLayer              │
│   BigNumbers  AdminCommands  ModuleRegistry                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Capa 0 — Core (transversales)

### 4.1 `Core/Logger.verse` (SYS-072, SPR-006)

- 📤 Deps: ninguna
- 📥 Consumidores: **TODOS los demás módulos** (cross-cutting)
- 🔒 obligatorio
- ⚠️ **Cambio crítico**: cualquier modificación de firma rompe todo. Solo añadir métodos, nunca quitar/renombrar.
- 🏗️ **Arquitectura (post-SPR-211)**: `Logger<public> := module:` (namespace top-level, sin class, sin archetype), NO `creative_device`, NO se registra en `ModuleRegistry`. Verse inicializa el module antes de cualquier `OnBegin`. Acceso directo por `using { Verse.Core.Logger }` (dotted relative) o path absoluto `/lexosi@fortnite.com/RPG_Survival/Verse/Core/Logger`. El patrón legacy `Logger : logger_module = logger_module{}` falla con err 3512 — ver `VERSE_SYNTAX_GUIDE.md` §1 lección 8.

### 4.2 `Core/EventBus.verse` (SYS-072, SPR-009)

- 📤 Deps: ninguna en compile-time como módulo source-controlled (el archivo manual). El **EventBus operativo** vive en `Generated/EventBusConstants.verse` que importa `Generated/EventPayloads_Generated.verse`.
- 📥 Consumidores: ~40 módulos que emiten/escuchan eventos (importan `Generated/EventBusConstants` directamente).
- ⚡ **Las dependencias runtime de eventos NO se reflejan aquí** (ver §11.2).
- 🏗️ **Arquitectura (C1 + C3)**: el "EventBus" del proyecto es un singleton top-level **generado** desde `data/architecture/events_catalog.json`. Compone instancias `event(payload_t)` nativas de Verse (parametric type compile-time, ver `Verse.digest`). Type-safety garantizada por compilador. Sin string-magic, sin `Payload:any`. Detalle del patrón en `BOOTSTRAP_PIPELINE.md` §11. Schema del catálogo en `JSON_SCHEMAS.md` §42.

### 4.3 `Core/TimeSync.verse` (SYS-068, SPR-007)

- 📤 Deps: `Logger` 🔒
- 📥 Consumidores: `RotatingShop`, `DailyLoginRewards`, `TimePlayedRewards`, `HourlyBossPortal`, `EventManager`, `SeasonManager`, `OfflineCalculator`, `CraftingTimers`, `BattlePass`
- 🏗️ **Arquitectura**: singleton top-level. Mismo patrón que Logger (§4.1).

### 4.4 `Core/PersistenceLayer.verse` (SYS-069, SPR-008)

- ✅ **SPR-008 implementado 2026-05-08**. 4 buckets + 8 funciones Load/Save. Build UEFN limpio + test in-session PASS.
- 📤 Deps: `Logger` 🔒
- 📥 Consumidores (escriben weak_maps): **24 módulos** (ver `PERSISTENCE_MAP.md`)
- ⚠️ **Cambio crítico**: añadir campo a un weak_map = solo opcional con default. Renombrar/eliminar = banea el mapa (ver `EMERGENCY_ROLLBACK.md`).
- 🏗️ **Arquitectura**: los 4 `weak_map` son variables `var` top-level (sin `module:` wrapper — weak_maps no compilan dentro de module, lección 5 VERSE_SYNTAX_GUIDE). El archivo expone tipos y funciones directos al scope de la carpeta `Verse/Core/`. Spec autoritativa del patrón en `VERSE_SYNTAX_GUIDE.md` §2.4.
- 📦 **Import desde callers**: `using { /lexosi@fortnite.com/RPG_Survival/Verse/Core }` (path a la CARPETA, no al archivo). Importar `Verse.Core.PersistenceLayer` falla con err 3506/3587 (lección 14).

### 4.5 `Core/BigNumbers.verse` (SYS-067)

- 📤 Deps: `Logger` 🔒
- 📥 Consumidores: `CurrencyManager`, `PassiveGenerators`, `OfflineCalculator`, `BattlePass`, `PlayerProgression`
- 🏗️ **Arquitectura**: wrapper de la lib comunidad. Funciones puras (`FromInt`, `Add`, etc.) accesibles vía `using`. Sin estado, no necesita singleton — pero se documenta como Core porque pertenece a Capa 0.

### 4.6 `Core/AdminCommands.verse` (SYS-070, SPR-010)

- 📤 Deps: `Logger` 🔒, `PersistenceLayer` 🔒, `EventBus` 🔒
- 📥 Consumidores: `Devices/AdminPanel`, `EventManager` (admin abuse)
- 🏗️ **Arquitectura**: singleton top-level. Mismo patrón que Logger (§4.1).

### 4.7 `Core/ModuleRegistry.verse` (SYS-072, SPR-005)

- 📤 Deps: `Logger` 🔒, `Generated/ModuleRegistryConstants` 🔒
- 📥 Consumidores: **Systems gameplay (Capa 2+)** que necesitan resolver dependencias cruzadas sin import compile-time circular. NO los Core.
- 🏗️ **Arquitectura**: singleton top-level. Mismo patrón que Logger (§4.1).

#### Qué hace y qué NO hace

| Hace | NO hace |
|---|---|
| Servicio de **lookup runtime** entre Systems gameplay | NO inicializa los Core (Verse los inicializa por sí mismo) |
| Resuelve "necesito B desde A pero importarlo crearía ciclo" | NO orquesta orden de carga (no existe orden controlable en Verse) |
| Permite que `creative_device` registre Systems en `OnBegin` | NO registra los 6 Core (acceso directo por `using {}`) |
| Expone getters tipados generados (`Registry.GetPlayerStats()`) | NO expone genérico `<T>` (Verse no soporta reflexión runtime) |

#### Por qué hace falta Registry si Verse ya tiene `using {}`

Para evitar **ciclos de import compile-time** entre Systems gameplay. Ejemplo:

- `PlayerProgression` necesita llamar a `BattlePass.AddXP()` cuando el jugador sube de nivel.
- `BattlePass` necesita leer `PlayerProgression.GetLevel()` para validar claims.
- Si ambos hacen `using {}` cruzado → ciclo de import → no compila.

Solución: uno (o ambos) usa `Registry.GetBattlePass()?.AddXP(...)` en runtime → cero deps compile-time entre ellos.

#### Workaround a la limitación de Verse (no soporta `<T>` runtime)

Verse no permite `GetModule<T>()` con tipo dinámico. Solución:

1. JSON manifest: `data/architecture/modules_manifest.json` declara qué Systems se registran.
2. Python (SPR-005): lee el manifest y genera `Generated/ModuleRegistryConstants.verse` con:
   - Un `enum module_id` con un valor por sistema registrable.
   - Getters tipados estáticos: `GetPlayerStats():?player_stats_module`, `GetBattlePass():?battle_pass_module`, etc.
3. Cada `creative_device` que arranca un Systems llama `Registry.RegisterPlayerStats(SelfModule)` en su `OnBegin`.

Detalle técnico completo en `BOOTSTRAP_PIPELINE.md` (sección "Patrón Core estático vs Systems registrables").

#### Estado en bootstrap

Cuando `Devices/GameManager.OnBegin` corre:

- Los 6 Core ya están **vivos** (Verse los inicializó top-level).
- `ModuleRegistry` ya existe pero **vacío** (su mapa interno de Systems está sin entries).
- GameManager dispara la fase de registro: cada Systems hace su `Init()` y se registra.
- Tras fase de registro → eventos `game_started` → Systems empiezan a operar.

---

## 5. Capa 1 — Generated

> **Solo constantes, ninguna lógica. Solo dependen de Core. Nadie los modifica a mano.**

| Archivo | Generado desde | Consumidores |
|---|---|---|
| `Companions_Generated.verse` | `data/companions/*.json` | `CompanionCore`, `CollectionDex`, `LootboxSystem` |
| `Items_Generated.verse` | `data/items/*.json` | `PlayerInventory`, `EquipmentSlots`, `ShopSystem`, `CraftingTimers` |
| `Prices_Generated.verse` | `data/economy/shop.json`, `pity_config.json`, `gold.json`, `gems.json` | `ShopSystem`, `PurchaseService`, `LootboxSystem`, `PitySystem`, `CurrencyManager` |
| `Quests_Generated.verse` | `data/quests/*.json` | `QuestEngine`, `TutorialChain`, `DailyQuestRotator`, `WeeklyQuestRotator` |
| `ThemeConstants_Generated.verse` | `data/theme/theme_config.json` | `SeasonManager`, `HUDController` (colores) |
| `ModuleRegistryConstants.verse` | módulos activos del proyecto | `ModuleRegistry` |
| `BalanceCurves_Generated.verse` | `BALANCE_FORMULAS.md` (SPR-134) | `PlayerProgression`, `BaseLevelManager`, `BattlePass`, `RerollService`, `EquipmentLeveling`, `PitySystem` |
| `PlayerStats_Generated.verse` | `data/progression/player_stats_base.json` | `PlayerStats` |
| `SkillTree_Generated.verse` | `data/progression/skill_trees.json` | `PlayerSkillTree` |
| `BattlePass_Generated.verse` | `data/progression/battle_pass_seasons/season_XX.json` | `BattlePass` |
| `Zones_Generated.verse` | `data/zones/*.json` | `ZoneManager`, `Devices/ZonePortal` |
| `Achievements_Generated.verse` | `data/progression/achievements.json` | `AchievementEngine` |
| `Localization_Generated.verse` | `data/theme/localization_keys.json` | `HUDController`, `NotificationPool` |

---

## 6. Capa 2 — Systems base

### 6.1 `Systems/Player/PlayerStats.verse` (SYS-001)

- 📤 Deps:
  - `Logger` 🔒
  - `PersistenceLayer` 🔒 (PlayerCore_Map)
  - `EventBus` 🔒 (emite `player_stats_changed`)
  - `Generated/PlayerStats_Generated` 🔒 (constantes base)
  - `BigNumbers` 🔓 (HP > 1M)
- 📥 Consumidores: `CombatCore`, `DamageCalculator`, `PlayerProgression`, `PlayerRebirth`, `PlayerSkillTree`, `EquipmentSlots`, `HUDController`

### 6.2 `Systems/Player/PlayerInventory.verse` (SYS-002)

- 📤 Deps:
  - `Logger` 🔒
  - `PersistenceLayer` 🔒 (PlayerInventory_Map)
  - `EventBus` 🔒 (emite `inventory_changed`, `item_acquired`)
  - `Generated/Items_Generated` 🔒
- 📥 Consumidores: `ResourceNodes`, `ShopSystem`, `LootboxSystem`, `EquipmentSlots`, `TradeSystem`, `AuctionSystem`, `CraftingTimers`, `InventoryUI`, `QuestEngine` (validar requisitos)

### 6.3 `Systems/Player/PlayerDeathHandler.verse` (SYS-009)

- 📤 Deps:
  - `Logger` 🔒, `PersistenceLayer` 🔒 (PlayerEconomy_Map), `EventBus` 🔒
  - `PlayerStats` 🔒, `CurrencyManager` 🔒
- 📥 Consumidores: `CombatCore` (trigger al morir)

### 6.4 `Systems/Companions/CompanionCore.verse` (SYS-010, SYS-011, SYS-012, SYS-013)

- 📤 Deps:
  - `Logger` 🔒, `PersistenceLayer` 🔒 (PlayerInventory_Map), `EventBus` 🔒
  - `Generated/Companions_Generated` 🔒
  - `BigNumbers` 🔓 (stats × variants × multipliers pueden crecer)
- 📥 Consumidores: `CompanionBehavior`, `CompanionAssignment`, `CollectionDex`, `LootboxSystem`, `DexUI`

### 6.5 `Systems/Companions/CompanionBehavior.verse` (SYS-014)

- 📤 Deps: `Logger` 🔒, `EventBus` 🔒, `CompanionCore` 🔒
- 📥 Consumidores: `CompanionAssignment`, `PassiveGenerators` (gathering pasivo)

### 6.6 `Systems/Equipment/EquipmentSlots.verse` (SYS-023, SYS-024)

- 📤 Deps:
  - `Logger` 🔒, `PersistenceLayer` 🔒 (PlayerInventory_Map), `EventBus` 🔒
  - `PlayerInventory` 🔒, `PlayerStats` 🔒 (aplicar stats)
  - `Generated/Items_Generated` 🔒
- 📥 Consumidores: `EquipmentLeveling`, `ProtectorService`, `SetBonuses`, `RerollService`, `InventoryUI`

### 6.7 `Systems/Combat/DamageCalculator.verse` (SYS-006)

- 📤 Deps:
  - `Logger` 🔒
  - `PlayerStats` 🔒, `EquipmentSlots` 🔓 (stats de equipo)
  - `Generated/BalanceCurves_Generated` 🔒
- 📥 Consumidores: `CombatCore`, `BossEncounters`

### 6.8 `Systems/Combat/AbilityExecutor.verse` (SYS-019)

- 📤 Deps:
  - `Logger` 🔒, `EventBus` 🔒, `TimeSync` 🔒 (cooldowns)
  - `PlayerStats` 🔒
- 📥 Consumidores: `CombatCore`, `PlayerSkillTree`

### 6.9 `Systems/World/ResourceNodes.verse` (SYS-003)

- 📤 Deps:
  - `Logger` 🔒, `EventBus` 🔒
  - `PlayerInventory` 🔒
  - `Generated/Items_Generated` 🔒
- 📥 Consumidores: `ZoneManager` (poblar zonas)

### 6.10 `Systems/Economy/CurrencyManager.verse` (SYS-029, SYS-030)

- 📤 Deps:
  - `Logger` 🔒, `PersistenceLayer` 🔒 (PlayerEconomy_Map), `EventBus` 🔒
  - `Generated/Prices_Generated` 🔒
  - `BigNumbers` 🔒 (gold y gems pueden ser sextillones)
- 📥 Consumidores: `ShopSystem`, `PurchaseService`, `LootboxSystem`, `RerollService`, `EquipmentLeveling`, `BattlePass` (claims), `DailyLoginRewards`, `PlayerDeathHandler`, `PassiveGenerators`, `OfflineCalculator`, `AuctionSystem`, `TradeSystem`

---

## 7. Capa 3 — Systems gameplay

### 7.1 `Systems/Player/PlayerProgression.verse` (SYS-016, SYS-017)

- 📤 Deps:
  - `Logger` 🔒, `PersistenceLayer` 🔒 (PlayerProgress_Map), `EventBus` 🔒
  - `PlayerStats` 🔒
  - `Generated/BalanceCurves_Generated` 🔒 (curva XP)
  - `BigNumbers` 🔓
- 📥 Consumidores: `PlayerSkillTree`, `PlayerRebirth`, `BattlePass`, `QuestEngine`, `HUDController`

### 7.2 `Systems/Player/PlayerRebirth.verse` (SYS-020)

- 📤 Deps:
  - `Logger` 🔒, `PersistenceLayer` 🔒 (PlayerProgress_Map), `EventBus` 🔒
  - `PlayerProgression` 🔒, `PlayerStats` 🔒, `PlayerInventory` 🔒, `CurrencyManager` 🔒
  - `Generated/BalanceCurves_Generated` 🔒
- 📥 Consumidores: `QuestEngine` (gating), `HUDController`

### 7.3 `Systems/Player/PlayerSkillTree.verse` (SYS-018)

- 📤 Deps:
  - `Logger` 🔒, `PersistenceLayer` 🔒 (PlayerProgress_Map), `EventBus` 🔒
  - `PlayerStats` 🔒, `PlayerProgression` 🔒
  - `Generated/SkillTree_Generated` 🔒
- 📥 Consumidores: `AbilityExecutor`, `CombatCore` (modifiers)

### 7.4 `Systems/Combat/CombatCore.verse` (SYS-006)

- 📤 Deps:
  - `Logger` 🔒, `EventBus` 🔒
  - `DamageCalculator` 🔒, `AbilityExecutor` 🔒
  - `PlayerStats` 🔒, `PlayerDeathHandler` 🔒
- 📥 Consumidores: `BossEncounters`, `HUDController`

### 7.5 `Systems/Economy/ShopSystem.verse` (SYS-032)

- 📤 Deps:
  - `Logger` 🔒, `EventBus` 🔒
  - `CurrencyManager` 🔒, `PurchaseService` 🔒, `PlayerInventory` 🔒
  - `Generated/Prices_Generated` 🔒, `Generated/Items_Generated` 🔒
- 📥 Consumidores: `RotatingShop`, `ShopUI`

### 7.6 `Systems/Economy/RotatingShop.verse` (SYS-033)

- 📤 Deps: `Logger` 🔒, `TimeSync` 🔒, `ShopSystem` 🔒, `EventBus` 🔒
- 📥 Consumidores: `ShopUI`

### 7.7 `Systems/Economy/PurchaseService.verse` (SYS-031)

- 📤 Deps:
  - `Logger` 🔒, `EventBus` 🔒
  - `CurrencyManager` 🔒
- 📥 Consumidores: `ShopSystem`, `BattlePass` (premium unlock), `LootboxSystem`

### 7.8 `Systems/Economy/LootboxSystem.verse` (SYS-034)

- 📤 Deps:
  - `Logger` 🔒, `EventBus` 🔒
  - `CurrencyManager` 🔒, `PurchaseService` 🔒, `PlayerInventory` 🔒
  - `CompanionCore` 🔒 (entregar companion)
  - `PitySystem` 🔒
  - `Generated/Companions_Generated` 🔒, `Generated/Prices_Generated` 🔒
- 📥 Consumidores: `ShopUI`

### 7.9 `Systems/Economy/PitySystem.verse` (SYS-035)

- 📤 Deps:
  - `Logger` 🔒, `PersistenceLayer` 🔒 (PlayerEconomy_Map), `EventBus` 🔒
  - `Generated/Prices_Generated` 🔒 (pity_config)
- 📥 Consumidores: `LootboxSystem`

### 7.10 `Systems/Economy/TradeSystem.verse` (SYS-036)

- 📤 Deps:
  - `Logger` 🔒, `EventBus` 🔒, `TimeSync` 🔒 (lock 5s)
  - `PlayerInventory` 🔒, `CurrencyManager` 🔒
- 📥 Consumidores: `HUDController`

### 7.11 `Systems/Economy/AuctionSystem.verse` (SYS-037)

- 📤 Deps:
  - `Logger` 🔒, `EventBus` 🔒
  - `PlayerInventory` 🔒, `CurrencyManager` 🔒
- 📥 Consumidores: `HUDController`

### 7.12 `Systems/Equipment/EquipmentLeveling.verse` (SYS-025)

- 📤 Deps:
  - `Logger` 🔒, `EventBus` 🔒
  - `EquipmentSlots` 🔒, `CurrencyManager` 🔒, `ProtectorService` 🔓
  - `Generated/BalanceCurves_Generated` 🔒
- 📥 Consumidores: `InventoryUI`

### 7.13 `Systems/Equipment/ProtectorService.verse` (SYS-026)

- 📤 Deps:
  - `Logger` 🔒, `EventBus` 🔒
  - `PlayerInventory` 🔒
- 📥 Consumidores: `EquipmentLeveling`

### 7.14 `Systems/Equipment/SetBonuses.verse` (SYS-027)

- 📤 Deps:
  - `Logger` 🔒, `EventBus` 🔒
  - `EquipmentSlots` 🔒, `PlayerStats` 🔒
- 📥 Consumidores: `InventoryUI`

### 7.15 `Systems/Equipment/RerollService.verse` (SYS-028)

- 📤 Deps:
  - `Logger` 🔒, `PersistenceLayer` 🔒 (PlayerInventory_Map), `EventBus` 🔒
  - `EquipmentSlots` 🔒, `CurrencyManager` 🔒
  - `Generated/BalanceCurves_Generated` 🔒
- 📥 Consumidores: `InventoryUI`

### 7.16 `Systems/Companions/CompanionAssignment.verse` (SYS-014)

- 📤 Deps:
  - `Logger` 🔒, `EventBus` 🔒
  - `CompanionCore` 🔒, `CompanionBehavior` 🔒
- 📥 Consumidores: `PassiveGenerators`, `BasePanelUI`

### 7.17 `Systems/Companions/CollectionDex.verse` (SYS-015)

- 📤 Deps:
  - `Logger` 🔒, `PersistenceLayer` 🔒 (PlayerProgress_Map, **bitmask packing**), `EventBus` 🔒
  - `CompanionCore` 🔒
  - `Generated/Companions_Generated` 🔒
- 📥 Consumidores: `DexUI`, `SocialDisplay` (% completion)

### 7.18 `Systems/World/ZoneManager.verse` (SYS-007)

- 📤 Deps:
  - `Logger` 🔒, `PersistenceLayer` 🔒 (PlayerProgress_Map), `EventBus` 🔒
  - `BaseLevelManager` 🔒 (gating)
  - `Generated/Zones_Generated` 🔒
- 📥 Consumidores: `Devices/ZonePortal`, `ResourceNodes`, `BossEncounters`

### 7.19 `Systems/World/BossEncounters.verse` (SYS-042)

- 📤 Deps:
  - `Logger` 🔒, `EventBus` 🔒
  - `CombatCore` 🔒, `DamageCalculator` 🔒
  - `ZoneManager` 🔓
- 📥 Consumidores: `HourlyBossPortal`, `Devices/HourlyBossTrigger`

### 7.20 `Systems/World/HourlyBossPortal.verse` (SYS-042)

- 📤 Deps:
  - `Logger` 🔒, `EventBus` 🔒, `TimeSync` 🔒 (sync UTC)
  - `BossEncounters` 🔒
- 📥 Consumidores: `Devices/HourlyBossTrigger`

### 7.21 `Systems/World/DayNightCycle.verse` (SYS-008)

- 📤 Deps:
  - `Logger` 🔒, `EventBus` 🔒, `TimeSync` 🔒
- 📥 Consumidores: `ResourceNodes` (modifiers nocturnos), `HUDController` (UI clima)

### 7.22 `Systems/Quests/QuestEngine.verse` (SYS-039, SYS-066)

- 📤 Deps:
  - `Logger` 🔒, `PersistenceLayer` 🔒 (PlayerProgress_Map), `EventBus` 🔒
  - `PlayerInventory` 🔓, `PlayerProgression` 🔓, `CurrencyManager` 🔓
  - `Generated/Quests_Generated` 🔒
- 📥 Consumidores: `TutorialChain`, `DailyQuestRotator`, `WeeklyQuestRotator`, `HUDController`

### 7.23 `Systems/Quests/TutorialChain.verse` (SYS-065)

- 📤 Deps: `Logger` 🔒, `EventBus` 🔒, `QuestEngine` 🔒
- 📥 Consumidores: `HUDController`

### 7.24 `Systems/Quests/DailyQuestRotator.verse` (SYS-039)

- 📤 Deps: `Logger` 🔒, `TimeSync` 🔒, `QuestEngine` 🔒
- 📥 Consumidores: `HUDController`

### 7.25 `Systems/Quests/WeeklyQuestRotator.verse` (SYS-039)

- 📤 Deps: `Logger` 🔒, `TimeSync` 🔒, `QuestEngine` 🔒
- 📥 Consumidores: `HUDController`

### 7.26 `Systems/Base/BaseLevelManager.verse` (SYS-059)

- 📤 Deps:
  - `Logger` 🔒, `PersistenceLayer` 🔒 (PlayerProgress_Map), `EventBus` 🔒
  - `Generated/BalanceCurves_Generated` 🔒
- 📥 Consumidores: `BaseUpgrades`, `ZoneManager`, `QuestEngine`, `BossEncounters` (gating)

### 7.27 `Systems/Base/BaseUpgrades.verse` (SYS-005, SYS-060)

- 📤 Deps:
  - `Logger` 🔒, `PersistenceLayer` 🔒 (PlayerProgress_Map), `EventBus` 🔒
  - `BaseLevelManager` 🔒, `CurrencyManager` 🔒
- 📥 Consumidores: `PassiveGenerators`, `OfflineCalculator`, `BasePanelUI`

### 7.28 `Systems/Base/PassiveGenerators.verse` (SYS-061)

- 📤 Deps:
  - `Logger` 🔒, `PersistenceLayer` 🔒 (PlayerEconomy_Map), `EventBus` 🔒
  - `BigNumbers` 🔒
  - `BaseUpgrades` 🔒, `CurrencyManager` 🔒, `CompanionAssignment` 🔓
- 📥 Consumidores: `OfflineCalculator`, `IdleSummaryUI`

### 7.29 `Systems/Base/OfflineCalculator.verse` (SYS-062)

- 📤 Deps:
  - `Logger` 🔒, `PersistenceLayer` 🔒, `EventBus` 🔒, `TimeSync` 🔒
  - `BigNumbers` 🔒
  - `PassiveGenerators` 🔒, `BaseUpgrades` 🔒, `CurrencyManager` 🔒
- 📥 Consumidores: `IdleSummaryUI`

### 7.30 `Systems/Base/CraftingTimers.verse` (SYS-063)

- 📤 Deps:
  - `Logger` 🔒, `PersistenceLayer` 🔒 (PlayerInventory_Map), `EventBus` 🔒, `TimeSync` 🔒
  - `PlayerInventory` 🔒
- 📥 Consumidores: `IdleSummaryUI`, `CraftingUI`

---

## 8. Capa 4 — UI + LiveOps + Social

### 8.1 LiveOps

| Módulo | Deps clave | Consumidores |
|---|---|---|
| `BattlePass.verse` (SYS-022) | `Logger`, `Persistence` (PlayerProgress), `EventBus`, `TimeSync`, `PlayerProgression`, `CurrencyManager`, `PurchaseService`, `Generated/BattlePass_Generated`, `BigNumbers` | `HUDController`, `IdleSummaryUI` |
| `DailyLoginRewards.verse` (SYS-040) | `Logger`, `Persistence`, `EventBus`, `TimeSync`, `CurrencyManager`, `PurchaseService` (rescue) | `HUDController` |
| `TimePlayedRewards.verse` (SYS-041) | `Logger`, `Persistence`, `EventBus`, `TimeSync`, `CurrencyManager` | `HUDController` |
| `EventManager.verse` (SYS-043, SYS-044) | `Logger`, `EventBus`, `TimeSync`, `AdminCommands`, `ZoneManager` 🔓, `CompanionCore` 🔓 | `Devices/HourlyBossTrigger`, `Devices/AdminPanel` |
| `CodeRedemption.verse` (SYS-045) | `Logger`, `Persistence`, `EventBus`, `PlayerInventory`, `CurrencyManager` | `HUDController` |
| `SeasonManager.verse` (SYS-046) | `Logger`, `EventBus`, `TimeSync`, `Generated/ThemeConstants_Generated` | `HUDController`, `BattlePass` 🔓 |
| `AchievementEngine.verse` (SYS-021) | `Logger`, `Persistence`, `EventBus` (escucha **muchos** events runtime), `Generated/Achievements_Generated` | `HUDController`, `SocialDisplay` |

### 8.2 Social

| Módulo | Deps clave | Consumidores |
|---|---|---|
| `LeaderboardSync.verse` (SYS-047) | `Logger`, `EventBus`, `TimeSync`, `PlayerProgression` 🔓, `PlayerRebirth` 🔓, `CollectionDex` 🔓 | `HUDController` |
| `SocialDisplay.verse` (SYS-048) | `Logger`, `Persistence` (PlayerProgress), `EventBus`, `PlayerRebirth` 🔓, `CollectionDex` 🔓, `AchievementEngine` 🔓 | `HUDController` |
| `ActivityLogUI.verse` (SYS-049) | `Logger`, `EventBus` (escucha eventos cosméticos), `Generated/Localization_Generated` | `HUDController` |

### 8.3 UI

| Módulo | Deps clave | Consumidores |
|---|---|---|
| `HUDController.verse` (SYS-049, SYS-050, SYS-057) | `Logger`, `EventBus`, **muchos** systems via runtime lookup ⚡, `Generated/ThemeConstants_Generated`, `Generated/Localization_Generated` | `Devices/GameManager` |
| `NotificationPool.verse` (SYS-050) | `Logger`, `EventBus`, `Generated/Localization_Generated` | `HUDController` |
| `InventoryUI.verse` (SYS-002, SYS-051–055) | `Logger`, `EventBus`, `PlayerInventory`, `EquipmentSlots`, `EquipmentLeveling`, `ProtectorService`, `SetBonuses`, `RerollService` | `HUDController` |
| `DexUI.verse` (SYS-015, SYS-055) | `Logger`, `EventBus`, `CollectionDex`, `CompanionCore` | `HUDController` |
| `ShopUI.verse` (SYS-032) | `Logger`, `EventBus`, `ShopSystem`, `RotatingShop`, `LootboxSystem`, `PurchaseService` | `HUDController` |
| `BasePanelUI.verse` (SYS-060) | `Logger`, `EventBus`, `BaseUpgrades`, `BaseLevelManager`, `CompanionAssignment` | `HUDController` |
| `IdleSummaryUI.verse` (SYS-054) | `Logger`, `EventBus`, `OfflineCalculator`, `PassiveGenerators`, `CraftingTimers` | `HUDController` |
| `CraftingUI.verse` (SYS-004) | `Logger`, `EventBus`, `PlayerInventory`, `CraftingTimers` | `HUDController` |

---

## 9. Capa 5 — Devices

> **Devices son instanciables desde UEFN editor. Importan TODO lo que necesitan. Nadie los importa.**

### 9.1 `Devices/GameManager.verse`

- Root device, **entry point del juego** (su `OnBegin` orquesta el `Init()` de cada Systems gameplay y los registra en `ModuleRegistry`).
- 📤 Deps: `ModuleRegistry` 🔒, `HUDController` 🔒, **todos los Systems vía registro runtime** (orden de `Init()` documentado en §2.1; los Core ya están vivos top-level antes de que `OnBegin` corra)
- 📥 Consumidores: nadie. **Punto de entrada del juego**.

### 9.2 `Devices/AdminPanel.verse` (SYS-070, SPR-010)

- 📤 Deps: `AdminCommands` 🔒, `EventManager` 🔒 (admin abuse)
- 📥 Consumidores: nadie.

### 9.3 `Devices/ZonePortal.verse` (SYS-007)

- 📤 Deps: `ZoneManager` 🔒, `Generated/Zones_Generated` 🔒
- 📥 Consumidores: nadie.

### 9.4 `Devices/HourlyBossTrigger.verse` (SYS-042)

- 📤 Deps: `HourlyBossPortal` 🔒, `BossEncounters` 🔒, `EventManager` 🔓
- 📥 Consumidores: nadie.

### 9.5 `Devices/BasePlot.verse` (SYS-005)

- 📤 Deps: `BaseUpgrades` 🔒, `BaseLevelManager` 🔒, `Persistence` 🔒
- 📥 Consumidores: nadie.

---

## 10. Reglas de cambio anti-rotura

### 10.1 Reglas inquebrantables

1. **Añadir parámetro a función pública** → solo si tiene default. Si no, rompes a todos los consumidores.
2. **Renombrar función pública** → ❌ jamás. Crear nueva función + marcar antigua `<deprecated>` durante 2 sprints, luego borrar.
3. **Cambiar tipo de retorno** → ❌ jamás. Crear función nueva con sufijo `_v2`.
4. **Mover módulo entre capas** → requiere validar que no rompe acíclico (script §10.3).
5. **Añadir dep nueva** → declarar aquí ANTES de añadir el `import`. Si crea ciclo → rediseño.

### 10.2 Antes de tocar un módulo

```
1. ¿En qué capa está? (§3 grafo visual)
2. Lista de consumidores 📥 → todos los que rompo si cambio firma
3. Lista de deps 📤 → todos los que necesito que existan
4. ¿Mi cambio crea ciclo? → ejecutar script validador (§10.3)
5. ¿Es un Core? → cambio crítico, requiere review extra (ver PROMPT.md §4)
```

### 10.3 Script validador de ciclos

**Path**: `scripts/tools/dependency_cycle_check.py`

```python
#!/usr/bin/env python3
"""
dependency_cycle_check.py — detecta ciclos en deps Verse.

Lee imports de los .verse files y construye un grafo dirigido.
Si hay ciclos → exit 1.
Si una capa N importa de capa N+ → exit 2.
"""

import re
import sys
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[2]
VERSE_ROOT = ROOT / "Content" / "Verse"

# Mapeo carpeta → capa
LAYER = {
    "Core": 0,
    "Generated": 1,
    "Systems/Player": 2, "Systems/Companions": 2, "Systems/Combat": 2,
    "Systems/Economy": 2, "Systems/Equipment": 2, "Systems/World": 2,
    "Systems/Quests": 2, "Systems/Base": 2,
    "Systems/UI": 4, "Systems/LiveOps": 4, "Systems/Social": 4,
    "Devices": 5,
}

def get_layer(path: Path) -> int:
    rel = path.relative_to(VERSE_ROOT).as_posix()
    for prefix, layer in LAYER.items():
        if rel.startswith(prefix + "/") or rel.startswith(prefix):
            return layer
    return -1

IMPORT_RE = re.compile(r"^\s*using\s*\{\s*([\w\./]+)\s*\}", re.MULTILINE)

# Patrones de path INVÁLIDOS que el validador debe rechazar
INVALID_PATH_PATTERNS = [
    re.compile(r"/Game\.Content\.Verse"),  # path antiguo incorrecto del proyecto
    re.compile(r"^\s*using\s*\{\s*[A-Za-z][\w]*\."),  # dotted path sin barra inicial
]

def collect_deps() -> dict[str, set[str]]:
    deps = defaultdict(set)
    for vf in VERSE_ROOT.rglob("*.verse"):
        text = vf.read_text(encoding="utf-8", errors="ignore")
        mod = vf.stem
        for m in IMPORT_RE.finditer(text):
            deps[mod].add(m.group(1).split("/")[-1])
    return deps

def check_invalid_paths() -> list[tuple[str, int, str]]:
    """Detecta paths Verse con sintaxis inválida. Ver §1.4."""
    violations = []
    for vf in VERSE_ROOT.rglob("*.verse"):
        text = vf.read_text(encoding="utf-8", errors="ignore")
        for lineno, line in enumerate(text.splitlines(), start=1):
            for pat in INVALID_PATH_PATTERNS:
                if pat.search(line):
                    violations.append((str(vf), lineno, line.strip()))
                    break
    return violations

def has_cycle(deps: dict[str, set[str]]) -> list[str]:
    WHITE, GRAY, BLACK = 0, 1, 2
    color = defaultdict(lambda: WHITE)
    cycle_path = []

    def dfs(n: str, stack: list[str]) -> bool:
        color[n] = GRAY
        stack.append(n)
        for m in deps.get(n, []):
            if color[m] == GRAY:
                cycle_path.extend(stack[stack.index(m):] + [m])
                return True
            if color[m] == WHITE and dfs(m, stack):
                return True
        stack.pop()
        color[n] = BLACK
        return False

    for node in list(deps.keys()):
        if color[node] == WHITE:
            if dfs(node, []):
                return cycle_path
    return []

def check_layer_violation(deps: dict[str, set[str]]) -> list[tuple[str, str]]:
    # Necesita resolver módulo → path (omitido por brevedad)
    # Aquí sólo bocetado — se completa en SPR específico
    return []

if __name__ == "__main__":
    deps = collect_deps()
    print(f"📋 {len(deps)} módulos analizados")

    # 1) Paths inválidos (regla §1.4)
    invalid = check_invalid_paths()
    if invalid:
        print(f"❌ {len(invalid)} path(s) Verse INVÁLIDOS detectados:")
        for path, lineno, line in invalid:
            print(f"  {path}:{lineno}  →  {line}")
        print("Ver MODULES_DEPENDENCY_GRAPH.md §1.4 para sintaxis canónica.")
        sys.exit(3)

    # 2) Ciclos
    cycle = has_cycle(deps)
    if cycle:
        print(f"❌ CICLO detectado: {' → '.join(cycle)}")
        sys.exit(1)
    print("✅ Sin ciclos, paths OK")
    sys.exit(0)
```

Hook pre-commit + CI step. Drift no merge-eable.

---

## 11. Análisis de impacto rápido

### 11.1 Top 10 módulos más críticos (más consumidores)

| Módulo | Capa | Consumidores | Impacto si se rompe |
|---|---|---|---|
| `Logger` | 0 | ~83 (todos) | catastrófico |
| `EventBus` | 0 | ~50 | catastrófico |
| `PersistenceLayer` | 0 | 24 | catastrófico (data loss) |
| `TimeSync` | 0 | 9 | features sync UTC rotas |
| `PlayerStats` | 2 | 7 | combat + progression rotos |
| `CurrencyManager` | 2 | 12 | economy rota |
| `PlayerInventory` | 2 | 10 | items + crafting rotos |
| `EquipmentSlots` | 2 | 5 | equipment chain roto |
| `CompanionCore` | 2 | 5 | companions + Dex rotos |
| `Generated/BalanceCurves_Generated` | 1 | 6 | curvas mal calibradas |

### 11.2 Eventos runtime (no compile-time deps)

> **Decisión cerrada (Auditoría 2 — C3)**: con el EventBus tipado generado, los payloads SÍ son compile-time. Cambiar la firma de un payload (struct field) **rompe compilación** en todos los suscriptores — ya no es bug silencioso.
>
> **Decisión cerrada (Auditoría retrospectiva — Bloque 1, B1.2)**: el campo identificador del jugador en payloads es `Player:player` (tipo nativo Verse), **NO** `PlayerID:int`. Razón: la API Verse pública de `player` no expone `GetID()` ni getter de identidad estable, por lo que un emisor no puede poblar un `int`. Además `player` es la key directa del `weak_map` de persistencia → los suscriptores pueden hacer `Persistence.LoadPlayerCore(Payload.Player)` sin lookup intermedio. Coherente con D-A13.
>
> Catálogo declarativo en `data/architecture/events_catalog.json` (schema en `JSON_SCHEMAS.md` §42). Genera `Generated/EventPayloads_Generated.verse` + `Generated/EventBusConstants.verse`. Patrón completo en `BOOTSTRAP_PIPELINE.md` §11.

Los más críticos (no romper firma del payload):

| Evento (id) | Nombre Verse en EventBus | Struct payload | Emitido por | Escuchado por |
|---|---|---|---|---|
| `player_stats_changed` | `EventBus.PlayerStatsChanged` | `player_stats_changed_payload{Player, Stat, OldValue, NewValue}` | PlayerStats | HUD, Achievement, SocialDisplay |
| `inventory_changed` | `EventBus.InventoryChanged` | `inventory_changed_payload{Player, ItemID, Delta}` | PlayerInventory | InventoryUI, AutoSell, Quest, Achievement |
| `level_up` | `EventBus.LevelUp` | `level_up_payload{Player, OldLevel, NewLevel}` | PlayerProgression | HUD, Notif, BattlePass, Achievement |
| `currency_spent` | `EventBus.CurrencySpent` | `currency_spent_payload{Player, Currency, Amount, Source}` | CurrencyManager | Audit, Achievement, Quest |
| `companion_acquired` | `EventBus.CompanionAcquired` | `companion_acquired_payload{Player, CompanionID, Rarity, Variant}` | LootboxSystem, ResourceNodes | CollectionDex, Achievement, Notif, SocialDisplay |
| `quest_completed` | `EventBus.QuestCompleted` | `quest_completed_payload{Player, QuestID, Rewards}` | QuestEngine | Notif, Achievement, BattlePass |
| `rebirth_done` | `EventBus.RebirthDone` | `rebirth_done_payload{Player, RebirthCount}` | PlayerRebirth | SocialDisplay, Achievement, Leaderboard |
| `zone_unlocked` | `EventBus.ZoneUnlocked` | `zone_unlocked_payload{Player, ZoneID}` | ZoneManager | Achievement, Notif, Quest |
| `boss_defeated` | `EventBus.BossDefeated` | `boss_defeated_payload{Player, BossID, Time}` | BossEncounters | Achievement, Notif, Leaderboard |

> **Si añades un campo a un payload**: seguro si todos los emisores se actualizan al rellenarlo en la misma PR.
> **Si renombras o eliminas un campo**: los suscriptores fallan compilación inmediatamente (mejor que el patrón viejo). Tratamiento: deprecar 1 release antes de eliminar (ver `JSON_SCHEMAS.md` §42.4).

### 11.3 Módulos seguros de tocar (1 o 0 consumidores)

`IdleSummaryUI`, `CraftingUI`, `BasePanelUI`, `ActivityLogUI`, `DexUI`, `ShopUI`, `InventoryUI` — son hojas del grafo. Cambiarlos solo afecta a sí mismos + HUDController.

---

**Total: 83 módulos analizados, 5 capas, 0 ciclos por diseño, ~50 eventos runtime catalogados.**
