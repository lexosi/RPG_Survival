# 🔌 API_REFERENCE_GENERATED — Referencia de APIs públicas

> **Documento auto-mantenido. Lista todas las funciones públicas del proyecto.**
> **DeepSeek y otras IAs ejecutoras DEBEN consultar esto antes de llamar a cualquier función.**
> Si una API no está aquí, **no existe en el proyecto** (todavía).
>
> **Decisión cerrada (Auditoría 2 — C1)**: los Core son singletons top-level estáticos. Acceso por `using { /<ProjectName>/Core/<Modulo> }` directo, NO via `Registry.GetModule<T>()`. ModuleRegistry sirve solo a Systems gameplay (Capa 2+) y expone **getters tipados estáticos generados** desde JSON manifest (no genérico `<T>` runtime — Verse no soporta reflexión). Detalle en `MODULES_DEPENDENCY_GRAPH.md` §4.7.
>
> **Decisión cerrada (Auditoría 2 — C3)**: el EventBus operativo es **generado** desde `data/architecture/events_catalog.json`, componiendo instancias `event(payload_t)` nativas de Verse. Type-safety compile-time. Sin string-magic. NO usar `Payload:any`. Detalle en §3.5 + `BOOTSTRAP_PIPELINE.md` §11.

---

## 🧭 Índice

1. [Cómo se mantiene este doc](#1-cómo-se-mantiene-este-doc)
2. [Convenciones de notación](#2-convenciones-de-notación)
3. [Core/](#3-core)
4. [Systems/Player/](#4-systemsplayer)
5. [Systems/Companions/](#5-systemscompanions)
6. [Systems/Economy/](#6-systemseconomy)
7. [Systems/Quests/](#7-systemsquests)
8. [Systems/Base/](#8-systemsbase)
9. [Systems/UI/](#9-systemsui)
10. [Devices/](#10-devices)

---

## 1. Cómo se mantiene este doc

### 1.1 Actualización obligatoria

**Cada vez que un sprint añade/modifica/elimina una función pública**, este doc se actualiza.

### 1.2 Quién lo actualiza

- **DeepSeek**: al terminar un sprint, reporta las funciones públicas creadas/modificadas/eliminadas.
- **Tú**: copias ese cambio aquí.
- **Opus**: en la sesión siguiente, valida que está bien y completa lo que falte.

### 1.3 Auto-generación con Python (recomendado)

Existe `scripts/tools/generate_api_reference.py` que parsea `.verse` files y extrae signatures públicas.

Ejecutar tras cada sprint mayor:

```bash
python scripts/tools/generate_api_reference.py
```

Esto regenera la sección 3 en adelante automáticamente desde el código real. **Source of truth = código**, este doc = **vista derivada**.

---

## 2. Convenciones de notación

### 2.1 Formato de cada función

```
### NombreFuncion(Param1:tipo, Param2:tipo)<specifiers>:tipo_retorno

**Ubicación**: `Content/Verse/Path/Module.verse:LineN`
**Estado**: ✅ Implementada / 🚧 En desarrollo / ⚠️ Deprecada
**Descripción**: qué hace en una línea.
**Ejemplo de uso**:
```verse
Result := Logger.LogInfo("MiModulo", "mensaje")
```
```

### 2.2 Specifiers Verse

**Access specifiers** ([dev.epicgames.com — Access Specifier](https://dev.epicgames.com/documentation/en-us/fortnite/access-specifier)):

- `<public>` — acceso sin restricción (visible desde cualquier contexto)
- `<internal>` — acceso limitado al módulo actual (default si no se especifica)
- `<protected>` — acceso limitado a la clase actual y sus subclases
- `<private>` — acceso limitado al scope inmediato de declaración

**Effect / behavior specifiers**:

- `<suspends>` — función async, requiere `spawn{}` o llamarse desde otra `<suspends>`
- `<transacts>` — puede ser parte de transacción rollback-able
- `<decides>` — expresión failable; requiere contexto de fallo (`if`, `?`)
- `<override>` — sobrescribe método de clase padre o de interface implementada
- `<final>` — la clase no admite subclases (obligatorio en `class<persistable>`)
- `<concrete>` — la clase admite construcción con archetype vacío `{}`

---

## 3. Core/

> **Módulos transversales del proyecto. Los más usados.**

> **Patrón canónico Core (post-SPR-211)**: los Cores SIN state mutable (Logger, TimeSync, BigNumbers) declaran `Module<public> := module:` (namespace top-level, sin class, sin archetype). Acceso por `using { Verse.Core.<Modulo> }` o path absoluto `/lexosi@fortnite.com/RPG_Survival/Verse/Core/<Modulo>`. Spec completa en `docs/VERSE_SYNTAX_GUIDE.md` §2.1 + §1 lecciones 8/11.
>
> ⚠️ **Patrón legacy obsoleto**: H3.1 (Auditoría 3) documentaba `<x>_module := class<concrete>:` + `<X> : <x>_module = <x>_module{}`. Falla con err 3512 en Verse moderno (UEFN ≥40.30): los métodos `<decides>` propagan `<transacts>` al class, y la construcción top-level es contexto `<computes>` puro. Validado en SPR-007 build UEFN. Para Cores con state mutable (PersistenceLayer SPR-008) y Systems registrables Capa 2+ — patrón TBD, ver `VERSE_SYNTAX_GUIDE.md` §2.4 + §6.

### 3.1 ModuleRegistry.verse

> **Arquitectura (Auditoría 2 — C1)**: singleton top-level. Sirve **solo a Systems gameplay (Capa 2+)** para resolver lookup runtime sin ciclos compile-time. Los 6 Core (Logger, EventBus, TimeSync, PersistenceLayer, BigNumbers, AdminCommands) **NO se registran aquí** — se acceden directamente por `using {}`.
>
> **Workaround a la falta de reflexión runtime en Verse**: en lugar de `GetModule<T>()` genérico (que Verse no soporta), se generan **getters tipados estáticos** desde `data/architecture/modules_manifest.json` por Python (SPR-005). El `.verse` resultante (`Generated/ModuleRegistryConstants.verse`) expone un getter por sistema registrable.

#### Registry:module_registry (instancia singleton)
**Ubicación**: `Content/Verse/Core/ModuleRegistry.verse`
**Estado**: 🚧 Pendiente SPR-005
**Descripción**: instancia top-level del registry. Acceso vía `using { /<ProjectName>/Core/ModuleRegistry }` y luego `Registry.GetXxx()`.

#### RegisterPlayerStats(Module:player_stats_module):void
**Estado**: 🚧 Pendiente SPR-005
**Descripción**: registra la instancia de PlayerStats. Llamada típicamente desde `GameManager.OnBegin()` durante la fase de Init.

#### GetPlayerStats():?player_stats_module
**Estado**: 🚧 Pendiente SPR-005
**Descripción**: devuelve la instancia registrada o `false` si aún no se registró. **Patrón de uso**:
```verse
if (PStats := Registry.GetPlayerStats()?):
    PStats.AddXP(Player, 100)
```

#### Patrón general (un par Register/Get por Systems registrable)
**Estado**: 🚧 Pendiente SPR-005
**Descripción**: cada sistema registrable en `modules_manifest.json` recibe su par `RegisterXxx(Module)` + `GetXxx():?xxx_module` autogenerado. La lista completa se materializa cuando el manifest se cierre (durante SPR-005). Sistemas anticipados: `PlayerStats`, `PlayerInventory`, `PlayerProgression`, `CompanionCore`, `CurrencyManager`, `BattlePass`, etc. Ver `MODULES_DEPENDENCY_GRAPH.md` §6–§8 para lista completa.

#### ❌ Funciones que NO existen (no implementar)
- ~~`Init():void`~~ — Verse inicializa el singleton solo (top-level), no hay `Init()`.
- ~~`Register<T>(ModuleInstance:T):void`~~ — genérico runtime no viable en Verse.
- ~~`GetModule<T>():?T`~~ — sustituido por getters tipados (`GetPlayerStats()`, etc.).

---

### 3.2 Logger.verse

> **Arquitectura (post-SPR-211)**: `Logger<public> := module:` (namespace top-level). Acceso por `using { Verse.Core.Logger }` y luego `Logger.LogXxx(...)`. NO se registra en ModuleRegistry. Ver `VERSE_SYNTAX_GUIDE.md` §2.1 para patrón canónico completo.

#### LogDebug(Module:string, Message:string):void
**Ubicación**: `Content/Verse/Core/Logger.verse`
**Estado**: 🚧 Pendiente SPR-006
**Descripción**: log nivel debug. Solo printea si flag DEBUG está activa.
**Ejemplo**:
```verse
Logger.LogDebug("PlayerStats", "Recalculating stats for player {Player}")
```

#### LogInfo(Module:string, Message:string):void
**Estado**: 🚧 Pendiente SPR-006
**Descripción**: log nivel info, siempre se printea.

#### LogWarn(Module:string, Message:string):void
**Estado**: 🚧 Pendiente SPR-006
**Descripción**: log nivel warning, contexto importante.

#### LogError(Module:string, Message:string):void
**Estado**: 🚧 Pendiente SPR-006
**Descripción**: log nivel error, problema serio.

---

### 3.3 TimeSync.verse

> **Arquitectura (post-SPR-211)**: `TimeSync<public> := module:` (namespace top-level). Acceso por `using { Verse.Core.TimeSync }`. Funciones failable se llaman con `[]`: `TimeSync.GetUTCNow[]`. Ver `VERSE_SYNTAX_GUIDE.md` §2.2.

#### GetUTCNow()&lt;decides&gt;:int
**Ubicación**: `Content/Verse/Core/TimeSync.verse`
**Estado**: ✅ Implementada SPR-007 (refactor SPR-211)
**Descripción**: devuelve simulation elapsed time como int (segundos desde inicio de sesión). Failable (puede fallar si `Floor[]` no resuelve). Llamada: `Now := TimeSync.GetUTCNow[]`.

#### GetSecondsUntilNextHour()&lt;decides&gt;:int
**Estado**: ✅ Implementada SPR-007
**Descripción**: segundos restantes hasta la próxima HH:00:00. Llamada: `S := TimeSync.GetSecondsUntilNextHour[]`.

#### IsInWindow(StartEpoch:int, DurationSeconds:int)&lt;decides&gt;:void
**Estado**: ✅ Implementada SPR-007
**Descripción**: predicado failable — succeed si `Now ∈ [StartEpoch, StartEpoch+DurationSeconds)`, fail otherwise. Tipo de retorno `:void` con condiciones-statement (lección 4 de la guide). Uso: `if (TimeSync.IsInWindow[Start, Dur]):`.

#### GetSimulationStartTime():int
**Estado**: 🚧 Pendiente (post SPR-007 — diferida a anchor diferido cuando se necesite epoch UTC absoluto, no solo elapsed).

---

### 3.4 PersistenceLayer.verse

> **⚠️ ANTES DE TOCAR ESTE MÓDULO, LEER PERSISTENCE_MAP.md ENTERO.**
>
> **Acceso desde callers**: usar path absoluto a la CARPETA `Core` (no al archivo `PersistenceLayer`):
> ```verse
> using { /lexosi@fortnite.com/RPG_Survival/Verse/Core }
> ```
> Razón: `PersistenceLayer.verse` no usa `module:` wrapper (los weak_maps deben ir top-level — lección 5 del VERSE_SYNTAX_GUIDE). Sus tipos son miembros directos del scope `Core`. Importar `Verse.Core.PersistenceLayer` falla con err 3506/3587 (lección 14). Spec en VERSE_SYNTAX_GUIDE §2.4.

#### var PlayerCoreMap:weak_map(player, PlayerCore) = map{}
**Ubicación**: `Content/Verse/Core/PersistenceLayer.verse`
**Estado**: ✅ Implementada SPR-008 (2026-05-08)
**Descripción**: weak_map persistente del 1er bucket. Schema en PERSISTENCE_MAP sección 3. Variable `var` top-level (requerido por Verse para persistencia). Visibilidad por defecto `<internal>` — los consumidores externos acceden vía `LoadPlayerCore()` / `SavePlayerCore()`.

#### var PlayerInventoryMap:weak_map(player, PlayerInventory) = map{}
**Estado**: ✅ Implementada SPR-008 (2026-05-08)
**Descripción**: 2º weak_map. Schema en PERSISTENCE_MAP sección 4. Mismo patrón de declaración que `PlayerCoreMap`.

#### var PlayerProgressMap:weak_map(player, PlayerProgress) = map{}
**Estado**: ✅ Implementada SPR-008 (2026-05-08)
**Descripción**: 3er weak_map. Schema en PERSISTENCE_MAP sección 5. Mismo patrón de declaración que `PlayerCoreMap`.

#### var PlayerEconomyMap:weak_map(player, PlayerEconomy) = map{}
**Estado**: ✅ Implementada SPR-008 (2026-05-08)
**Descripción**: 4º weak_map. Schema en PERSISTENCE_MAP sección 6. Mismo patrón de declaración que `PlayerCoreMap`.

#### LoadPlayerCore<public>(InPlayer:player):PlayerCore_V1
**Estado**: ✅ Implementada SPR-008 (2026-05-08)
**Descripción**: carga datos del jugador, aplica validación defensiva (PERSISTENCE_MAP §10.1). Retorna versión activa (`PlayerCore_V1`), no wrapper. Effect `<computes>` default (Logger compatible).

#### SavePlayerCore<public>(InPlayer:player, Data:PlayerCore_V1)<transacts>:void
**Estado**: ✅ Implementada SPR-008 (2026-05-08)
**Descripción**: guarda datos del jugador. Acepta versión activa (`PlayerCore_V1`), internamente envuelve en option-version (`PlayerCore{V1 := option{Data}}`). Effect `<transacts>` (Logger INCOMPATIBLE — Save silencioso).

#### LoadPlayerInventory<public>(InPlayer:player):PlayerInventory_V1
**Estado**: ✅ Implementada SPR-008 (2026-05-08)

#### SavePlayerInventory<public>(InPlayer:player, Data:PlayerInventory_V1)<transacts>:void
**Estado**: ✅ Implementada SPR-008 (2026-05-08)

#### LoadPlayerProgress<public>(InPlayer:player):PlayerProgress_V1
**Estado**: ✅ Implementada SPR-008 (2026-05-08)

#### SavePlayerProgress<public>(InPlayer:player, Data:PlayerProgress_V1)<transacts>:void
**Estado**: ✅ Implementada SPR-008 (2026-05-08)

#### LoadPlayerEconomy<public>(InPlayer:player):PlayerEconomy_V1
**Estado**: ✅ Implementada SPR-008 (2026-05-08)

#### SavePlayerEconomy<public>(InPlayer:player, Data:PlayerEconomy_V1)<transacts>:void
**Estado**: ✅ Implementada SPR-008 (2026-05-08)

#### LoadPlayerData / SavePlayerData (wrappers agregadores)
**Estado**: 🚧 Pendiente sprint futuro (NO implementados en SPR-008)
**Descripción**: wrappers agregadores que invocarían las 4 funciones individuales en secuencia. SPR-008 entregó solo las 8 funciones por bucket. Si un consumidor (ej. GameManager OnPlayerSpawn) necesita carga/save full, llama las 4 funciones directamente. Decisión SPR-008: posponer wrappers hasta confirmar caso de uso real — en la mayoría de flows se carga/guarda solo el bucket relevante.

---

### 3.5 EventBus.verse + EventBusConstants.verse (generado)

> **Arquitectura (C1 + C3)**: el EventBus operativo es un **singleton top-level generado** (`Generated/EventBusConstants.verse`) compuesto de instancias `event(payload_t)` nativas de Verse. Acceso por `using { /<ProjectName>/Generated/EventBusConstants }` y `using { /<ProjectName>/Generated/EventPayloads_Generated }`. NO usa strings. NO usa `Payload:any`.
>
> Source of truth del catálogo: `data/architecture/events_catalog.json` (schema en `JSON_SCHEMAS.md` §42). Plantilla y patrón en `BOOTSTRAP_PIPELINE.md` §11.

#### EventBus:event_bus_module (singleton generado)
**Ubicación**: `Content/Verse/Generated/EventBusConstants.verse`
**Estado**: 🚧 Pendiente SPR-009 (Verse base) + extensión Python en SPR-004 (export catalog → Verse)
**Descripción**: instancia top-level del bus. Acceso vía `using { /<ProjectName>/Generated/EventBusConstants }` y luego `EventBus.<NombreEvento>`.

#### EventBus.<NombreEvento>:event(<nombre_evento>_payload)
**Estado**: 🚧 Pendiente SPR-009
**Descripción**: una propiedad por evento del catálogo. Cada propiedad es una instancia `event(t)` nativa de Verse, que implementa `signalable`, `awaitable` y `subscribable`. Lista completa de eventos en `MODULES_DEPENDENCY_GRAPH.md` §11.2.

**Métodos disponibles en cada `event(t)` (provistos por Verse nativo, no por nosotros)**:

```verse
# Emitir evento (InPlayer es la referencia nativa Verse del jugador)
EventBus.LevelUp.Signal(level_up_payload{
    Player := InPlayer
    OldLevel := 9
    NewLevel := 10
})

# Suscribirse (handler con firma tipada)
EventBus.LevelUp.Subscribe(MyHandler)

MyHandler(Payload:level_up_payload):void=
    # Payload.Player es player nativo — usable como key de weak_map directamente
    Print("Player reached lvl {Payload.NewLevel}")

# Cancelar suscripción
EventBus.LevelUp.Unsubscribe(MyHandler)

# Esperar evento (corutina suspende hasta emisión)
Payload := EventBus.LevelUp.Await()
```

#### Payloads (structs generados)
**Ubicación**: `Content/Verse/Generated/EventPayloads_Generated.verse`
**Estado**: 🚧 Pendiente SPR-009
**Descripción**: un struct por cada evento. Campos públicos planos (sin anidación). Constructores con defaults para `int`, `float`, `string`, `logic`, arrays. Tipos `player`/`agent` requieren rellenarse en construcción.

#### ❌ Funciones que NO existen (no implementar)
- ~~`Subscribe(EventName:string, Handler:type{_(Payload:any):void}):void`~~ — `any` SÍ existe en Verse como supertipo opaco ([dev.epicgames.com — Any in Verse](https://dev.epicgames.com/documentation/en-us/fortnite/any-in-verse): *"Verse has a special type, any, that is the supertype of all types"*) pero soporta operaciones muy limitadas y no encaja en handlers tipados de events. Sustituido por `EventBus.<Evento>.Subscribe(handler_tipado)` con struct payload concreto.
- ~~`Emit(EventName:string, Payload:any):void`~~ — sustituido por `EventBus.<Evento>.Signal(payload_struct)`.
- ~~`Unsubscribe(EventName:string, Handler:...)`~~ — sustituido por `EventBus.<Evento>.Unsubscribe(handler)`.

---

### 3.6 BigNumbers.verse

> **Arquitectura (C1)**: módulo de funciones puras (sin estado). Acceso por `using { /<ProjectName>/Core/BigNumbers }`. No requiere singleton.

#### BigNumber := struct:
```verse
BigNumber := struct:
    Mantissa:float
    Exponent:int
```
**Ubicación**: `Content/Verse/Core/BigNumbers.verse`
**Estado**: 🚧 Pendiente sprint posterior

#### BigNumber.FromInt(Value:int):BigNumber
#### BigNumber.FromString(Str:string):BigNumber
#### BigNumber.Add(A:BigNumber, B:BigNumber):BigNumber
#### BigNumber.Multiply(A:BigNumber, B:BigNumber):BigNumber
#### BigNumber.Compare(A:BigNumber, B:BigNumber):int
#### BigNumber.ToDisplayString(N:BigNumber):string

---

### 3.7 AdminCommands.verse

> **Arquitectura (C1)**: singleton top-level. Acceso por `using { /<ProjectName>/Core/AdminCommands }`.
>
> **Identificación de admin (Auditoría retrospectiva — Bloque 1)**: la API Verse pública de `player` no expone método estable que devuelva un identificador serializable (`GetID()`/`GetName()`/`GetAccountID()` no existen en la doc oficial; `IsActive[]` es el método público confirmado para validación de scope). Fuente: [dev.epicgames.com — player class](https://dev.epicgames.com/documentation/en-us/fortnite/verse-api/versedotorg/simulation/player) + feature request abierta [forums — Get player name in Verse](https://forums.unrealengine.com/t/feature-request-get-player-name-in-verse/1378109). Identificación se hace por uno o varios `player_reference_device` configurados en editor UEFN. El módulo `AdminCommands` recibe el array de refs vía función `Init` (la sostiene `Devices/AdminPanel.verse` con `@editable AdminRefs:[]player_reference_device = array{}`) y comprueba `Ref.IsRegistered[Agent]` en runtime. Detalle en `CONCEPT.md` SPR-010 + `GLOSSARY.md` "Admin (player ID)" + `JSON_SCHEMAS.md` §37.

#### Init(Refs:[]player_reference_device):void
**Ubicación**: `Content/Verse/Core/AdminCommands.verse`
**Estado**: 🚧 Pendiente SPR-010
**Descripción**: inyecta el array de `player_reference_device` que `AdminPanel` mantiene como `@editable`. Llamado una vez desde `AdminPanel.OnBegin` antes de habilitar la UI.

#### IsAdmin(Agent:agent):logic
**Ubicación**: `Content/Verse/Core/AdminCommands.verse`
**Estado**: 🚧 Pendiente SPR-010
**Descripción**: true si **alguno** de los `player_reference_device` registrados vía `Init` tiene `IsRegistered[Agent]`. Toma `agent` (no `player`) porque los eventos de devices Fortnite emiten `agent` y el caller no necesita castearlo a `player`. Implementación interna usa `for (Ref:Refs) { if (Ref.IsRegistered[Agent]) { return true } }; return false`.

#### ExecuteCommand(Agent:agent, Command:string, Args:[]string):void
**Estado**: 🚧 Pendiente SPR-010
**Descripción**: ejecuta comando admin si `IsAdmin(Agent)` es true. Si no, loggea intento + ignora.

#### ❌ Funciones que NO existen (no implementar)
- ~~`IsAdmin(InPlayer:player):logic` con check tipo `InPlayer.GetID() == ADMIN_ID_HARDCODED`~~ — la API Verse pública de `player` no expone `GetID()` ni getter de identidad estable serializable (ver cabecera §3.7). Workaround canónico = `player_reference_device.IsRegistered[Agent]`.

---

## 4. Systems/Player/

🚧 Pendiente. Se completa al implementar Fase 1.

Funciones esperadas:
- `PlayerStats.GetHP(InPlayer:player):int`
- `PlayerStats.SetHP(InPlayer:player, Value:int):void`
- `PlayerStats.GetGold(InPlayer:player):int`
- `PlayerStats.AddGold(InPlayer:player, Amount:int):void`
- `PlayerInventory.GetItem(InPlayer:player, ItemID:int):?ItemEntry`
- `PlayerInventory.AddItem(InPlayer:player, ItemID:int, Quantity:int):logic`
- `PlayerInventory.RemoveItem(InPlayer:player, ItemID:int, Quantity:int):logic`
- `PlayerProgression.GainXP(InPlayer:player, Amount:int):void`
- `PlayerProgression.GetLevel(InPlayer:player):int`
- `PlayerSkillTree.SpendPoint(InPlayer:player, Branch:int, Skill:int):logic`
- `PlayerRebirth.CanRebirth(InPlayer:player):logic`
- `PlayerRebirth.ExecuteRebirth(InPlayer:player):void`
- `PlayerDeathHandler.OnPlayerDied(InPlayer:player):void`

---

## 5. Systems/Companions/

🚧 Pendiente. Se completa al implementar Fase 2.

Funciones esperadas:
- `CompanionCore.SpawnCompanion(InPlayer:player, CompanionID:int, Variant:int):logic`
- `CompanionCore.GetActive(InPlayer:player):[]CompanionEntry`
- `CompanionBehavior.AssignToTask(InPlayer:player, CompanionInstance:int, TaskID:int):logic`
- `CompanionAssignment.Unassign(InPlayer:player, CompanionInstance:int):void`
- `CollectionDex.RecordSeen(InPlayer:player, CompanionID:int, Variant:int):void`
- `CollectionDex.GetCompletionPercent(InPlayer:player):float`

---

## 6. Systems/Economy/

🚧 Pendiente. Se completa al implementar Fase 3.

Funciones esperadas:
- `CurrencyManager.GetGold(InPlayer:player):int`
- `CurrencyManager.GetGems(InPlayer:player):int`
- `CurrencyManager.SpendGold(InPlayer:player, Amount:int):logic`
- `CurrencyManager.SpendGems(InPlayer:player, Amount:int):logic`
- `ShopSystem.GetCurrentRotation():[]ShopItem`
- `ShopSystem.PurchaseItem(InPlayer:player, ItemID:int, PaymentMethod:int):logic`
- `RotatingShop.GetCurrentSlot():int`
- `PurchaseService.ResolveEntitlement(InPlayer:player, EntitlementID:int):void`
- `LootboxSystem.OpenLootbox(InPlayer:player, LootboxID:int):?CompanionEntry`
- `PitySystem.IncrementCounter(InPlayer:player, SoulType:int, Rarity:int):int`
- `PitySystem.ShouldGuarantee(InPlayer:player, SoulType:int, Rarity:int):logic`
- `TradeSystem.InitiateTrade(InitiatorPlayer:player, TargetPlayer:player):logic`
- `AuctionSystem.ListItem(InPlayer:player, ItemID:int, Price:int):logic`

---

## 7. Systems/Quests/

🚧 Pendiente.

Funciones esperadas:
- `QuestEngine.StartQuest(InPlayer:player, QuestID:int):logic`
- `QuestEngine.UpdateProgress(InPlayer:player, QuestID:int, Delta:int):void`
- `QuestEngine.ClaimReward(InPlayer:player, QuestID:int):logic`
- `DailyQuestRotator.GetCurrentDailies():[]int`
- `WeeklyQuestRotator.GetCurrentWeeklies():[]int`
- `TutorialChain.GetCurrentStep(InPlayer:player):int`
- `TutorialChain.AdvanceStep(InPlayer:player):void`

---

## 8. Systems/Base/

🚧 Pendiente. Se completa al implementar Fase 4.

Funciones esperadas:
- `BaseLevelManager.GetLevel(InPlayer:player):int`
- `BaseLevelManager.GainBaseXP(InPlayer:player, Amount:int):void`
- `BaseUpgrades.UnlockUpgrade(InPlayer:player, UpgradeID:int):logic`
- `BaseUpgrades.GetTier(InPlayer:player, UpgradeID:int):int`
- `PassiveGenerators.Tick(InPlayer:player):void`
- `OfflineCalculator.CalculateOfflineProduction(InPlayer:player, ElapsedSeconds:int):OfflineResult`
- `CraftingTimers.StartCraft(InPlayer:player, RecipeID:int):logic`
- `CraftingTimers.GetReadyCrafts(InPlayer:player):[]int`

---

## 9. Systems/UI/

🚧 Pendiente.

Funciones esperadas:
- `HUDController.ShowMessage(InPlayer:player, Message:string, Category:int):void`
- `NotificationPool.GetAvailableDevice():?hud_message_device`
- `ActivityLogUI.AddEntry(InPlayer:player, Message:string, Category:int):void`
- `InventoryUI.OpenForPlayer(InPlayer:player):void`
- `DexUI.OpenForPlayer(InPlayer:player):void`
- `ShopUI.OpenForPlayer(InPlayer:player):void`
- `BasePanelUI.OpenForPlayer(InPlayer:player):void`
- `IdleSummaryUI.ShowSummary(InPlayer:player, Result:OfflineResult):void`

---

## 10. Devices/

🚧 Pendiente. Devices instanciables en UEFN editor.

Devices esperados:
- `GameManager` — root device. Entry point del juego: en su `OnBegin` orquesta `Init()` de los Systems gameplay y los registra en `ModuleRegistry`. Los 6 Core ya están vivos (top-level) cuando `OnBegin` corre.
- `ZonePortal` — portal de zona con gate
- `HourlyBossTrigger` — gestiona evento por hora
- `BasePlot` — plot persistente del jugador
- `AdminPanel` — UI restringida por player ID

---

## 📌 Para DeepSeek y otras IAs ejecutoras

**REGLAS DE USO**:

1. **Antes de llamar a una función**, verifica que está aquí.
2. **Si la función no está**, NO la inventes. Reporta a Opus para añadirla.
3. **Si una función está marcada 🚧 Pendiente**, NO la uses todavía (no existe).
4. **Si necesitas extender una función**, propón cambio en sprint, no improvises.
5. **Si encuentras inconsistencia** entre este doc y el código real, reporta a Opus.

---

**Fin del documento.**
