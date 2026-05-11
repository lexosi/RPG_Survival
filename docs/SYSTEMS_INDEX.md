# 🗂️ SYSTEMS_INDEX — Catálogo autoritativo de los 72 sistemas

> **Fuente única de verdad para `SYS-xxx`.** Todo doc que referencie un sistema debe coincidir con esta tabla. Si hay conflicto entre este archivo y otro, **gana este**.
>
> Para implementación detallada (qué hace Python vs Verse) → `CONCEPT.md` §8.2.
> Para descripciones largas → `CONCEPT.md` §10.

---

## 🧭 Índice

1. [Convenciones](#1-convenciones)
2. [Tabla maestra](#2-tabla-maestra)
3. [Vistas filtradas](#3-vistas-filtradas)
4. [Cobertura JSONs ↔ carpetas](#4-cobertura-jsons--carpetas)
5. [Reglas de mantenimiento](#5-reglas-de-mantenimiento)

---

## 1. Convenciones

| Campo | Significado |
|---|---|
| **ID** | `SYS-xxx` único, inmutable. Nunca se reordena ni se reusa. |
| **Categoría** | Bucket de §10 del CONCEPT (Core, Companions, Progression…). |
| **Fase** | F0/F1/F2/F3/F4/F5. Cuándo se implementa. |
| **JSON principal** | Archivo data-driven. `—` si no aplica. |
| **Verse principal** | Archivo runtime. `—` si no aplica. |
| **Sprint que lo crea** | `SPR-xxx` que lo entrega por primera vez. `TBD` si aún no asignado. |
| **Persistencia** | Bucket weak_map (`Core/Inventory/Progress/Economy`) o `—`. |
| **Estado** | `🟢 listo` / `🟡 parcial` / `🔴 pendiente` / `⚫ no empieza`. |

---

## 2. Tabla maestra

### 2.1 Core gameplay (SYS-001 → SYS-009)

| ID | Sistema | Cat | Fase | JSON principal | Verse principal | Sprint | Persist | Estado |
|---|---|---|---|---|---|---|---|---|
| SYS-001 | Player Stats | Core | F1 | `data/progression/player_stats_base.json` | `Systems/Player/PlayerStats.verse` | TBD | Core | ⚫ |
| SYS-002 | Inventory | Core | F1 | `data/items/equipment.json`, `data/items/resources.json`, `data/items/consumables.json` | `Systems/Player/PlayerInventory.verse`, `Systems/UI/InventoryUI.verse` | TBD | Inventory | ⚫ |
| SYS-003 | Resource Gathering | Core | F1 | `data/items/resources.json` | `Systems/World/ResourceNodes.verse` | TBD | — (drops van a Inventory via SYS-002) | ⚫ |
| SYS-004 | Crafting | Core | F1 | `data/items/recipes.json` | `Systems/UI/CraftingUI.verse` (lógica core en Inventory) | TBD | — (timers en Economy via SYS-063) | ⚫ |
| SYS-005 | Base Building | Core | F1 | `data/base/building_pieces.json` | `Devices/BasePlot.verse` (lógica upgrade en SYS-060 BaseUpgrades, building core inline) | TBD | Economy | ⚫ |
| SYS-006 | Combat | Core | F1 | `data/combat/damage_formulas.json` ⚠️ | `Systems/Combat/CombatCore.verse`, `Systems/Combat/DamageCalculator.verse` | TBD | — | ⚫ |
| SYS-007 | Zone Unlock | Core | F1 | `data/zones/zone_definitions.json`, `data/zones/unlock_gates.json` | `Systems/World/ZoneManager.verse`, `Devices/ZonePortal.verse`, `Generated/Zones_Generated.verse` | TBD | — (inferido de Base Level + quests) | ⚫ |
| SYS-008 | Day/Night + Weather | Core | F1 | `data/world/day_night_cycle.json` ⚠️ | `Systems/World/DayNightCycle.verse` | TBD | — | ⚫ |
| SYS-009 | Death Penalty + Protection | Core | F1 | `data/economy/death_protection.json` ⚠️ | `Systems/Player/PlayerDeathHandler.verse` | TBD | Core (`DeathProtection_ExpiresAt`) | ⚫ |

### 2.2 Companions (SYS-010 → SYS-015)

| ID | Sistema | Cat | Fase | JSON principal | Verse principal | Sprint | Persist | Estado |
|---|---|---|---|---|---|---|---|---|
| SYS-010 | Companion Core | Companions | F2 | `data/companions/companions_base.json`, `variants.json` | `Systems/Companions/CompanionCore.verse` | TBD | Inventory | ⚫ |
| SYS-011 | Rarity Tiers | Companions | F2 | `data/companions/rarities.json` ⚠️ | (parte de CompanionCore) | TBD | — | ⚫ |
| SYS-012 | Variants | Companions | F2 | `data/companions/variants.json` | (parte de CompanionCore) | TBD | Inventory | ⚫ |
| SYS-013 | Evolution | Companions | F2 | `data/companions/evolutions.json` | (parte de CompanionCore) | TBD | Inventory | ⚫ |
| SYS-014 | Companion Behavior | Companions | F2 | `data/companions/behaviors.json` ⚠️ | `Systems/Companions/CompanionBehavior.verse`, `Systems/Companions/CompanionAssignment.verse` | TBD | — | ⚫ |
| SYS-015 | Collection Dex | Companions | F2 | `data/companions/dex_rewards.json` | `Systems/Companions/CollectionDex.verse`, `Systems/UI/DexUI.verse` | TBD | Inventory | ⚫ |

### 2.3 Progression (SYS-016 → SYS-022)

| ID | Sistema | Cat | Fase | JSON principal | Verse principal | Sprint | Persist | Estado |
|---|---|---|---|---|---|---|---|---|
| SYS-016 | XP & Levels | Progression | F1 | `data/progression/xp_curves.json` ⚠️ | `Systems/Player/PlayerProgression.verse` | TBD | Core | ⚫ |
| SYS-017 | Skill Points | Progression | F1 | `data/progression/skill_points.json` ⚠️ | (parte de Progression) | TBD | Core | ⚫ |
| SYS-018 | Skill Trees | Progression | F2 | `data/progression/skill_trees.json` | `Systems/Player/PlayerSkillTree.verse` | TBD | Core (`SkillPoints_Spent`) | ⚫ |
| SYS-019 | Active Abilities | Progression | F2 | `data/progression/abilities.json` ⚠️ | `Systems/Combat/AbilityExecutor.verse` (parte de Combat) | TBD | — (cooldowns runtime-only) | ⚫ |
| SYS-020 | Rebirth System | Progression | F1 | `data/progression/rebirth_rewards.json` | `Systems/Player/PlayerRebirth.verse` | TBD | Core (`RebirthCount`, `Rebirth_PermBonuses`) | ⚫ |
| SYS-021 | Achievements | Progression | F2 | `data/progression/achievements.json` | `Systems/LiveOps/AchievementEngine.verse` | SPR-074, SPR-075, SPR-076 | Progress (bitfield 256) | ⚫ |
| SYS-022 | Battle Pass | Progression | F3 | `data/progression/battle_pass_seasons/season_XX.json`, `data/progression/battle_pass_seasons/season_01.json`, `data/progression/battle_pass_seasons/season_02.json` | `Systems/LiveOps/BattlePass.verse` | TBD | Progress | ⚫ |

### 2.4 Equipment (SYS-023 → SYS-028)

| ID | Sistema | Cat | Fase | JSON principal | Verse principal | Sprint | Persist | Estado |
|---|---|---|---|---|---|---|---|---|
| SYS-023 | Equipment Slots | Equipment | F3 | `data/items/equipment_slots.json` | `Systems/Equipment/EquipmentSlots.verse` | TBD | Inventory | ⚫ |
| SYS-024 | Equipment Stats | Equipment | F3 | (stats inline en equipment.json, ver SYS-002) | (parte de Slots) | TBD | Inventory | ⚫ |
| SYS-025 | Equipment Leveling | Equipment | F3 | `data/items/equipment_leveling.json` | `Systems/Equipment/EquipmentLeveling.verse` | TBD | Inventory | ⚫ |
| SYS-026 | Protectors | Equipment | F3 | `data/items/protectors.json` | `Systems/Equipment/ProtectorService.verse` | TBD | Inventory | ⚫ |
| SYS-027 | Set Bonuses | Equipment | F3 | `data/items/sets.json` | `Systems/Equipment/SetBonuses.verse` | TBD | — | ⚫ |
| SYS-028 | Reroll Stats | Equipment | F3 | `data/items/reroll.json` | `Systems/Equipment/RerollService.verse` | TBD | Inventory | ⚫ |

### 2.5 Economy (SYS-029 → SYS-038)

| ID | Sistema | Cat | Fase | JSON principal | Verse principal | Sprint | Persist | Estado |
|---|---|---|---|---|---|---|---|---|
| SYS-029 | Gold | Economy | F1 ⚙️ | `data/economy/gold.json` ⚠️, `data/economy/currency_caps.json` | `Systems/Economy/CurrencyManager.verse` | TBD | Core (`Gold`, `Gold_Overflow`) | ⚫ |
| SYS-030 | Gems | Economy | F1 ⚙️ | `data/economy/gems.json` ⚠️ | (parte de CurrencyManager) | TBD | Core (`Gems`) + Economy (lifetime stats) | ⚫ |
| SYS-031 | V-Bucks Integration | Economy | F3 | `data/economy/vbucks_offers.json` ⚠️ | `Systems/Economy/PurchaseService.verse` | TBD | Economy (bundles bitfield) | ⚫ |
| SYS-032 | Shop System | Economy | F3 | `data/economy/shop.json` ⚠️ | `Systems/Economy/ShopSystem.verse`, `Systems/UI/ShopUI.verse` | TBD | — | ⚫ |
| SYS-033 | Rotating Session Shop | Economy | F3 | `data/economy/shop_rotations.json` | `Systems/Economy/RotatingShop.verse` | TBD | — | ⚫ |
| SYS-034 | Lootboxes (Almas) | Economy | F3 | `data/items/lootboxes.json` | `Systems/Economy/LootboxSystem.verse` | TBD | Economy (lifetime spent) | ⚫ |
| SYS-035 | Pity System | Economy | F3 | `data/economy/pity_config.json` | `Systems/Economy/PitySystem.verse` | TBD | Economy (PityCounters) | ⚫ |
| SYS-036 | Trading Same-Session | Economy | F3 | (flags inline en items) | `Systems/Economy/TradeSystem.verse` | TBD | Economy (rate-limit) | ⚫ |
| SYS-037 | Auction Same-Session | Economy | F3 | `data/economy/auction_config.json` ⚠️ | `Systems/Economy/AuctionSystem.verse` | TBD | Economy (active listings) | ⚫ |
| SYS-038 | Universal Obtainability Flag | Economy | F1 ⚙️ | (flags inline en cada item JSON) | (validado en Python build-time) | TBD | — | ⚫ |

### 2.6 Live Ops (SYS-039 → SYS-046)

| ID | Sistema | Cat | Fase | JSON principal | Verse principal | Sprint | Persist | Estado |
|---|---|---|---|---|---|---|---|---|
| SYS-039 | Quest System | LiveOps | F1 | `data/quests/tutorial_chain.json`, `data/quests/daily_pool.json`, `data/quests/weekly_pool.json` | `Systems/Quests/QuestEngine.verse`, `Systems/Quests/DailyQuestRotator.verse`, `Systems/Quests/WeeklyQuestRotator.verse` | TBD | Progress (ActiveQuests, CompletedQuests, Daily/Weekly) | ⚫ |
| SYS-040 | Daily Login | LiveOps | F4 | `data/progression/daily_login.json` ⚠️ | `Systems/LiveOps/DailyLoginRewards.verse` | TBD | Progress (streak + claimed bitfield) | ⚫ |
| SYS-041 | Time Played Rewards | LiveOps | F4 | `data/progression/time_played.json` ⚠️ | `Systems/LiveOps/TimePlayedRewards.verse` | TBD | Progress (today claimed bitfield) | ⚫ |
| SYS-042 | Hourly Boss Event | LiveOps | F4 → F5 ⚙️ | `data/events/hourly_boss.json` | `Systems/World/HourlyBossPortal.verse`, `Systems/World/BossEncounters.verse`, `Devices/HourlyBossTrigger.verse` | TBD | — | ⚫ |
| SYS-043 | Long Events | LiveOps | F3 | `data/events/seasonal_events.json` | `Systems/LiveOps/EventManager.verse` | TBD | — | ⚫ |
| SYS-044 | Short Events / Admin Abuse | LiveOps | F3 | `data/events/admin_commands.json` ⚠️ | `Systems/LiveOps/EventManager.verse` (usa Core/AdminCommands.verse de SYS-070) | TBD | — | ⚫ |
| SYS-045 | Code Redemption | LiveOps | F3 | `data/events/codes_pool.json` | `Systems/LiveOps/CodeRedemption.verse` | TBD | Progress (CodesRedeemed) | ⚫ |
| SYS-046 | Seasonal Content Framework | LiveOps | F4 | `data/seasons/season_XX.json` ⚠️, `data/seasons/season_01.json` | `Systems/LiveOps/SeasonManager.verse` | TBD | — | ⚫ |

### 2.7 Social (SYS-047 → SYS-050)

| ID | Sistema | Cat | Fase | JSON principal | Verse principal | Sprint | Persist | Estado |
|---|---|---|---|---|---|---|---|---|
| SYS-047 | Leaderboards | Social | F5 | `data/social/leaderboards.json` ⚠️ | `Systems/Social/LeaderboardSync.verse` | TBD | Progress (`LeaderboardScore_*` por stat) | ⚫ |
| SYS-048 | Social Display | Social | F3 | `data/social/displays.json` ⚠️ | `Systems/Social/SocialDisplay.verse` | TBD | — (deriva de RebirthCount + Dex %) | ⚫ |
| SYS-049 | Activity Log UI | Social | F1 | `data/ui/activity_log.json` ⚠️ | `Systems/Social/ActivityLogUI.verse`, `Systems/UI/HUDController.verse` (cross-cutting con SYS-050 + SYS-057) | TBD | — (runtime only, no persist) | ⚫ |
| SYS-050 | Notifications System | Social | F1 | `data/ui/notifications.json` ⚠️ | `Systems/UI/NotificationPool.verse` | TBD | — | ⚫ |

### 2.8 Quality of Life (SYS-051 → SYS-058)

| ID | Sistema | Cat | Fase | JSON principal | Verse principal | Sprint | Persist | Estado |
|---|---|---|---|---|---|---|---|---|
| SYS-051 | Auto-Sell Filters | QoL | F3 | `data/ui/auto_sell_config.json` ⚠️ | (parte de InventoryUI) | TBD | — (config cliente, runtime) | ⚫ |
| SYS-052 | Pre-Inventory Filter | QoL | F3 | `data/ui/pre_inventory_filter.json` ⚠️ | (parte de InventoryUI) | TBD | — (config cliente, runtime) | ⚫ |
| SYS-053 | Visual Compare | QoL | F3 | — | (parte de InventoryUI) | TBD | — | ⚫ |
| SYS-054 | Idle Summary | QoL | F3 | — | `Systems/UI/IdleSummaryUI.verse` | TBD | — | ⚫ |
| SYS-055 | Search/Filter | QoL | F3 | — | (parte de InventoryUI/DexUI) | TBD | — | ⚫ |
| SYS-056 | Hotkeys / Radial Menu | QoL | F3 | `data/ui/hotkeys.json` ⚠️ | (parte de HUDController) | TBD | — | ⚫ |
| SYS-057 | Error Handling UI | QoL | F1 ⚙️ | `data/ui/error_messages.json` ⚠️ | (parte de HUDController) | TBD | — | ⚫ |
| SYS-058 | Rate Limiting | QoL | F1 ⚙️ | `data/ui/rate_limits.json` ⚠️ | (cross-cutting) | TBD | — | ⚫ |

### 2.9 Base persistente (SYS-059 → SYS-063)

| ID | Sistema | Cat | Fase | JSON principal | Verse principal | Sprint | Persist | Estado |
|---|---|---|---|---|---|---|---|---|
| SYS-059 | Base Level | Base | F4 | `data/base/base_levels.json` | `Systems/Base/BaseLevelManager.verse` | TBD | Core (`BaseLevel`, `BaseXP`) | ⚫ |
| SYS-060 | Base Upgrades | Base | F4 | `data/base/base_upgrades.json` | `Systems/Base/BaseUpgrades.verse`, `Systems/UI/BasePanelUI.verse` | TBD | Economy (BaseUpgrades[]) | ⚫ |
| SYS-061 | Passive Generators | Base | F4 | `data/base/generators.json` ⚠️ | `Systems/Base/PassiveGenerators.verse` | TBD | Economy (Generators_State_Pool) | ⚫ |
| SYS-062 | Offline Production | Base | F4 | `data/base/offline_config.json` ⚠️ | `Systems/Base/OfflineCalculator.verse` | TBD | Economy (OfflineCap_LastClaim_Epoch) + Core (LastLogout_Epoch) | ⚫ |
| SYS-063 | Crafting Timers | Base | F4 | `data/items/crafting_timers.json` ⚠️ | `Systems/Base/CraftingTimers.verse` | TBD | Economy (ActiveCrafts) | ⚫ |

### 2.10 Onboarding (SYS-064 → SYS-066)

| ID | Sistema | Cat | Fase | JSON principal | Verse principal | Sprint | Persist | Estado |
|---|---|---|---|---|---|---|---|---|
| SYS-064 | First Minute Hook | Onboarding | F1 | `data/onboarding/first_minute.json` ⚠️ | (cross-cutting con UI/Quests) | TBD | — | ⚫ |
| SYS-065 | Tutorial Chain | Onboarding | F1 | `data/quests/tutorial_chain.json` | `Systems/Quests/TutorialChain.verse` | TBD | Progress (Tutorial_CurrentStep, Tutorial_Completed, FirstRebirth_Done) | ⚫ |
| SYS-066 | Contextual Tutorials | Onboarding | F4 | `data/onboarding/contextual_tutorials.json` ⚠️ | (parte de QuestEngine) | TBD | Progress (flags via CompletedQuests) | ⚫ |

### 2.11 Sistemas técnicos (SYS-067 → SYS-072)

| ID | Sistema | Cat | Fase | JSON principal | Verse principal | Sprint | Persist | Estado |
|---|---|---|---|---|---|---|---|---|
| SYS-067 | BigNumbers Integration | Tech | F0 | — | `Core/BigNumbers.verse` | TBD | — | ⚫ |
| SYS-068 | Time Sync (UTC) | Tech | F0 | — | `Core/TimeSync.verse` | SPR-007 | — | ⚫ |
| SYS-069 | Persistence Layer | Tech | F0 | (schemas en Verse) | `Core/PersistenceLayer.verse` | SPR-008 | Core+Inv+Prog+Econ | ⚫ |
| SYS-070 | Admin Panel | Tech | F0 | `data/admin/admin_config.json` ⚠️ | `Devices/AdminPanel.verse`, `Core/AdminCommands.verse` | SPR-010 | — | ⚫ |
| SYS-071 | Test/QA Framework | Tech | F0 | `data/admin/test_flags.json` ⚠️ | (test_devices) | TBD | — | ⚫ |
| SYS-072 | Module Registry | Tech | F0 | `data/architecture/modules_manifest.json`, `data/architecture/events_catalog.json` | `Core/ModuleRegistry.verse`, `Core/EventBus.verse`, `Core/Logger.verse`, `Generated/ModuleRegistryConstants.verse`, `Generated/EventBusConstants.verse`, `Generated/EventPayloads_Generated.verse` | SPR-005, SPR-006, SPR-009 | — | ⚫ |
| SYS-073 | Game Manager (root device) | Tech | F1 | — | `Devices/GameManager.verse` | TBD | — | ⚫ |

### 2.12 Cross-cutting & infraestructura visible (sin SYS-XXX)

Entries sin numeración SYS porque NO son sistemas del juego con scope acotado — son cross-cutting (Generated), assets standalone (Maps), o docs canónicos. Mantienen formato 9-col para que validador/parser SYSTEMS_INDEX las procese uniformemente.

| ID | Sistema | Cat | Fase | JSON principal | Verse principal | Sprint | Persist | Estado |
|---|---|---|---|---|---|---|---|---|
| — | Balance Curves (Generated) | Tech-CC | F1 | (from BALANCE_FORMULAS.md) | `Generated/BalanceCurves_Generated.verse` | SPR-134 | — | ⚫ |
| — | Theme Constants (Generated) | Tech-CC | F3 | (from data/theme/) | `Generated/ThemeConstants_Generated.verse` | SPR-170 | — | ⚫ |
| — | Localization | Tech-CC | F3 | `data/theme/localization_keys.json` | (consumido vía ThemeConstants_Generated) | TBD | — | ⚫ |
| — | HOWTO New Map (doc canónico) | Docs | F5 | — | `docs/HOWTO_NEW_MAP.md` | SPR-203 | — | ⚫ |

> **Leyenda ⚠️**: JSON declarado en §8.2 del CONCEPT pero **carpeta o archivo no presente** en §11.1. Riesgo de fallo del validador. Ver §4 de este doc.

---

## 3. Vistas filtradas

### 3.1 Por fase

> **Fuente autoritativa: `CONCEPT.md` §12.2.** Esta tabla es vista derivada. Si discrepa con CONCEPT → gana CONCEPT.
>
> **Leyenda ⚙️**: el sistema aparece anticipado en una fase anterior con scope reducido (ej: currencies básicas en F1 sin shop, error UI mínima en F1). El **scope completo** se entrega en la fase oficial del CONCEPT. Marcado para que la IA no asuma que está "todo hecho" cuando se cierre F1.

| Fase | Nombre (CONCEPT §12.2) | Sistemas |
|---|---|---|
| **F0** | Foundation | SYS-067, SYS-068, SYS-069, SYS-070, SYS-071, SYS-072 |
| **F1** | MVP playable | SYS-001 → SYS-009, SYS-016, SYS-017, SYS-020, SYS-039 (parcial), SYS-064, SYS-065 |
| **F1 ⚙️ anticipados** | (scope reducido) | SYS-029, SYS-030 (currencies sin shop), SYS-038 (validador desde día 1), SYS-049, SYS-050 (notif/log mínimos para tutorial), SYS-057, SYS-058 (error UI + rate limits cross-cutting) |
| **F2** | Companions & Collection | SYS-010 → SYS-015, SYS-018, SYS-019, SYS-021, SYS-049, SYS-050 (full scope) |
| **F3** | Economy & Equipment | SYS-022, SYS-023 → SYS-028, SYS-029, SYS-030 (full scope), SYS-031, SYS-032 → SYS-038, SYS-051 → SYS-058 (full scope) |
| **F4** | Base persistente & Live Ops básicas | SYS-040 → SYS-046, SYS-059 → SYS-063, SYS-066 |
| **F5** | Hourly Boss + Social + Polish | SYS-042 (extendido), SYS-047, SYS-048 + polish global + segundo mapa |

### 3.2 Por bucket de persistencia

> **Fuente autoritativa: `PERSISTENCE_MAP.md` §3–§6 (schemas) y §7 (cálculo real).** Esta tabla es vista derivada. Si discrepa con PERSISTENCE_MAP → gana PERSISTENCE_MAP.
>
> **Cap duro de UEFN**: 128 KB por weak_map. Total disponible: 4 × 128 = 512 KB.

| Bucket | Uso real (typical / worst) | Sistemas que escriben |
|---|---|---|
| **PlayerCore_Map** | **568 B / 1.05 KB** (0.80% del cap) | SYS-001 (Player Stats), SYS-009 (Death Protection expiry), SYS-016 (XP), SYS-017 (Skill Points), SYS-020 (Rebirth count), SYS-029 (Gold), SYS-030 (Gems), SYS-059 (Base Level) |
| **PlayerInventory_Map** | **3.5 KB / 10.2 KB** (7.9% del cap) | SYS-002 (Inventory), SYS-010 (Companions owned), SYS-012 (Variants), SYS-013 (Evolution), SYS-015 (Dex), SYS-023 (Equipment Slots), SYS-024 (Equipment Stats), SYS-025 (Equipment Leveling tier), SYS-028 (Reroll counter) |
| **PlayerProgress_Map** | **776 B / 1.78 KB** (1.4% del cap) | SYS-021 (Achievements bitfield), SYS-022 (Battle Pass), SYS-039 (Quests), SYS-040 (Daily Login), SYS-041 (Time Played), SYS-045 (Codes Redeemed), SYS-047 (Leaderboard scores), SYS-065 (Tutorial), SYS-066 (Contextual Tutorials triggered) |
| **PlayerEconomy_Map** | **400 B / 1 KB** (0.7% del cap) | SYS-005 (Base building pieces), SYS-031 (V-Bucks bundles detected), SYS-034 (Lootbox lifetime stats), SYS-035 (Pity counters), SYS-036 (Trade rate-limit), SYS-037 (Auction listings), SYS-060 (Base upgrades permanentes), SYS-061 (Generators state), SYS-062 (Offline cap last claim), SYS-063 (Active crafts) |

**Cómo leer la tabla**:
- **Uso real** = "cuánto consume hoy con los schemas actuales" (`PERSISTENCE_MAP.md` §7.1). Lo que se serializa de verdad.
- **% del cap** = uso real / 128 KB. Indicador defensivo: alerta si supera 50% (validador SPR-136 lo verifica).
- Margen vs cap = "cuánto espacio queda para crecer". Hoy ~99% libre en todos los buckets — heredado de optimizaciones aplicadas (bitfields, int IDs, sparse representation).

**Notas clave**:
- **`PlayerCore` concentra escrituras frecuentes** (gold/gems/xp cambian a cada rato) — diseño deliberado, ver PERSISTENCE_MAP §2 "Por qué esta distribución".
- **`PlayerInventory` es el bucket más pesado** (~10.2 KB worst real), pero solo usa **7.9% de su cap**. El Dex de 300 entries va aquí (PERSISTENCE_MAP §4.1) con bitfield de variantes ya optimizado.
- **`PlayerEconomy` mezcla compras V-Bucks (sensible) con cosas de baja frecuencia** (base upgrades, pity, listings).
- **Margen real consolidado**: ~5.2 KB típicos vs 512 KB total → **>98% libre en uso normal**. Worst-case ~14 KB → **>97% libre**. Sin riesgo de 128 KB ni de cerca.
- **El SYS-018 Skill Trees** distribuye datos: árbol asignado en PlayerCore (`SkillPoints_Spent:[]SkillPointEntry`), no requiere bucket aparte.
- **SYS-007 Zone Unlock**: zonas desbloqueadas se infieren de `Base Level` y quests completadas — no campo dedicado.

### 3.3 Sistemas sin JSON (lógica pura Verse)

SYS-053, SYS-054, SYS-055, SYS-067, SYS-068, SYS-072.

### 3.4 Sistemas sin Verse (build-time only)

SYS-038 (validador Python).

---

## 4. Cobertura JSONs ↔ carpetas

### 4.1 Auditoría: archivos declarados vs carpetas en CONCEPT §11.1

**JSONs declarados en §8.2 del CONCEPT que NO tienen carpeta o archivo en §11.1:**

| JSON declarado | Carpeta declarada en §11.1 | Problema |
|---|---|---|
| `data/combat/damage_formulas.json` | ❌ no existe `data/combat/` | Falta carpeta entera |
| `data/economy/death_protection.json` | ✅ `data/economy/` | Falta archivo |
| `data/world/day_night_cycle.json` | ❌ no existe `data/world/` | Falta carpeta entera |
| `data/companions/rarities.json` | ✅ `data/companions/` | Falta archivo |
| `data/companions/behaviors.json` | ✅ `data/companions/` | Falta archivo |
| `data/progression/xp_curves.json` | ✅ `data/progression/` | Falta archivo |
| `data/progression/skill_points.json` | ✅ `data/progression/` | Falta archivo |
| `data/progression/abilities.json` | ✅ `data/progression/` | Falta archivo |
| `data/progression/achievements.json` | ✅ `data/progression/` (canónico — `FOLDER_STRUCTURE_TRUTH.md` §3 línea 461 resuelve la contradicción histórica entre CONCEPT §11.1 y §8.2 a favor de `data/progression/`) | Falta archivo |
| `data/progression/daily_login.json` | ✅ `data/progression/` | Falta archivo |
| `data/progression/time_played.json` | ✅ `data/progression/` | Falta archivo |
| `data/progression/player_stats_base.json` | ✅ `data/progression/` | Falta archivo (schema en `JSON_SCHEMAS.md` §44, Auditoría 2 — m2) |
| `data/economy/gold.json` | ✅ `data/economy/` | Falta archivo |
| `data/economy/gems.json` | ✅ `data/economy/` | Falta archivo |
| `data/economy/vbucks_offers.json` | ✅ `data/economy/` | Falta archivo |
| `data/economy/shop.json` | ⚠️ §11.1 menciona `prices.json` y `shop_rotations.json`, no `shop.json` | **Inconsistencia naming** |
| `data/economy/auction_config.json` | ✅ `data/economy/` | Falta archivo |
| `data/items/recipes.json` | ❌ no listado en §11.1 | Falta archivo |
| `data/items/protectors.json` | ❌ no listado en §11.1 | Falta archivo |
| `data/items/sets.json` | ❌ no listado en §11.1 | Falta archivo |
| `data/items/reroll.json` | ❌ no listado en §11.1 | Falta archivo |
| `data/items/equipment_slots.json` | ❌ no listado en §11.1 | Falta archivo |
| `data/items/equipment_leveling.json` | ❌ no listado en §11.1 | Falta archivo |
| `data/items/crafting_timers.json` | ❌ no listado en §11.1 | Falta archivo |
| `data/base/building_pieces.json` | ❌ no listado en §11.1 | Falta archivo |
| `data/base/generators.json` | ❌ no listado en §11.1 | Falta archivo |
| `data/base/offline_config.json` | ❌ no listado en §11.1 | Falta archivo |
| `data/events/admin_commands.json` | ❌ no listado en §11.1 | Falta archivo |
| `data/seasons/season_XX.json` | ❌ no existe `data/seasons/` | Falta carpeta entera |
| `data/social/leaderboards.json` | ❌ no existe `data/social/` | Falta carpeta entera |
| `data/social/displays.json` | ❌ no existe `data/social/` | Falta carpeta entera |
| `data/ui/*.json` (8 archivos) | ❌ no existe `data/ui/` | Falta carpeta entera |
| `data/onboarding/*.json` (2 archivos) | ❌ no existe `data/onboarding/` | Falta carpeta entera |
| `data/admin/*.json` (2 archivos) | ❌ no existe `data/admin/` | Falta carpeta entera |
| `data/architecture/modules_manifest.json` | ❌ no existe `data/architecture/` | **Falta carpeta entera** (Auditoría 2 — C1) |
| `data/architecture/events_catalog.json` | ❌ no existe `data/architecture/` | **Falta carpeta entera** (Auditoría 2 — C3) |

> Esta auditoría es **input directo** para `FOLDER_STRUCTURE_TRUTH.md` (próximo doc). El validador `scripts/build/01_validate_jsons.py` (SPR-003) debe contemplar estas rutas.

### 4.2 Carpetas faltantes (resumen)

```
data/combat/
data/world/
data/seasons/
data/social/
data/ui/
data/onboarding/
data/admin/
data/architecture/   ← Auditoría 2 — C1+C3 (modules_manifest.json + events_catalog.json)
```

**8 carpetas críticas no existen** en la estructura declarada del CONCEPT §11.1.

---

## 5. Reglas de mantenimiento

1. **Inmutabilidad de IDs**: una vez asignado `SYS-xxx`, nunca se reordena, renombra ni reusa. Si un sistema se descarta → se marca `🚫 deprecated` pero **no se borra la fila**.
2. **Adición de sistemas**: nuevos sistemas reciben el siguiente ID libre (`SYS-073`, `SYS-074`…), nunca rellenan huecos.
3. **Jerarquía de fuentes** (en caso de conflicto):
   - Para **buckets de persistencia** (columna `Persist`, §3.2) → **`PERSISTENCE_MAP.md` §3–§6 manda**. Esta tabla es vista derivada.
   - Para **fases** (columna `Fase`, §3.1) → **`CONCEPT.md` §12.2 manda**. Esta tabla refleja el roadmap oficial.
   - Para **rutas de archivos** (columnas JSON / Verse principal) → **`FOLDER_STRUCTURE_TRUTH.md` manda**.
   - Para **descripciones cortas y catálogo** (nombre, categoría) → **este doc manda** sobre CONCEPT §8.2 y §10.
4. **Sprint asignado**: cuando un SPR-xxx implemente un sistema, se actualiza columna `Sprint` y `Estado`.
5. **Cambio de fase**: requiere entrada en `CHANGELOG.md` y nota en `DECISIONS_LOG.md` (cuando exista).

---

**Total: 72 sistemas. Cobertura JSON: 62. Cobertura Verse: 66. Sistemas en F0: 6. Sistemas con riesgo de carpeta faltante: 37.**
