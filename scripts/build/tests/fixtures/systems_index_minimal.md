### 2.1 Core gameplay (SYS-001 → SYS-009)

| ID | Sistema | Cat | Fase | JSON principal | Verse principal | Sprint | Persist | Estado |
|---|---|---|---|---|---|---|---|---|
| SYS-001 | Player Stats | Core | F1 | `data/progression/player_stats_base.json` | `Systems/Player/PlayerStats.verse` | TBD | Core | ⚫ |
| SYS-002 | Inventory | Core | F1 | `data/items/equipment.json`, `resources.json`, `consumables.json` | `Systems/Player/PlayerInventory.verse` | TBD | Inventory | ⚫ |
| SYS-004 | Crafting | Core | F1 | `data/items/recipes.json` | (parte de Inventory) | TBD | — | ⚫ |
| SYS-008 | Day/Night | Core | F1 | `data/world/day_night_cycle.json` | (TBD) | TBD | — | ⚫ |

### 2.5 Economy (SYS-029 → SYS-038)

| ID | Sistema | Cat | Fase | JSON principal | Verse principal | Sprint | Persist | Estado |
|---|---|---|---|---|---|---|---|---|
| SYS-029 | Gold | Economy | F1 ⚙️ | `data/economy/gold.json` ⚠️ | `Systems/Economy/CurrencyManager.verse` | TBD | Core | ⚫ |

### 2.6 Live Ops (SYS-039 → SYS-046)

| ID | Sistema | Cat | Fase | JSON principal | Verse principal | Sprint | Persist | Estado |
|---|---|---|---|---|---|---|---|---|
| SYS-042 | Hourly Boss | LiveOps | F4 → F5 ⚙️ | `data/events/hourly_boss.json` | `Systems/World/HourlyBossPortal.verse`, `BossEncounters.verse` | TBD | — | ⚫ |
