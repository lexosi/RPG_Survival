# 📐 JSON_SCHEMAS — Schemas formales de todos los JSONs del proyecto

> **Documento crítico. Fuente de verdad para validación de JSONs.**
>
> Cada JSON del proyecto tiene aquí su schema formal: campos obligatorios, tipos, rangos, restricciones cruzadas.
>
> **Cualquier IA que cree o edite JSONs DEBE consultar este doc antes.**
> **El validador `scripts/build/01_validate_jsons.py` debe implementar TODAS estas reglas.**

---

## 🧭 Índice

1. [Convenciones generales](#1-convenciones-generales)
2. [Reglas inquebrantables](#2-reglas-inquebrantables)
3. [Schema: companions_base.json](#3-schema-companions_basejson)
4. [Schema: variants.json](#4-schema-variantsjson)
5. [Schema: dex_rewards.json](#5-schema-dex_rewardsjson)
6. [Schema: equipment.json](#6-schema-equipmentjson)
7. [Schema: equipment_slots.json](#7-schema-equipment_slotsjson)
8. [Schema: equipment_leveling.json](#8-schema-equipment_levelingjson)
9. [Schema: protectors.json](#9-schema-protectorsjson)
10. [Schema: sets.json](#10-schema-setsjson)
11. [Schema: reroll.json](#11-schema-rerolljson)
12. [Schema: lootboxes.json](#12-schema-lootboxesjson)
13. [Schema: pity_config.json](#13-schema-pity_configjson)
14. [Schema: prices.json](#14-schema-pricesjson) 🚫 **REMOVIDO** — fusionado en `shop.json` (ver §15)
15. [Schema: shop.json](#15-schema-shopjson) ⭐ ahora incluye precios
16. [Schema: shop_rotations.json](#16-schema-shop_rotationsjson)
17. [Schema: vbucks_offers.json](#17-schema-vbucks_offersjson)
18. [Schema: gold.json + gems.json](#18-schema-goldjson--gemsjson)
19. [Schema: auction_config.json](#19-schema-auction_configjson)
20. [Schema: quests/*.json](#20-schema-questsjson)
21. [Schema: tutorial_chain.json](#21-schema-tutorial_chainjson)
22. [Schema: daily_login.json](#22-schema-daily_loginjson)
23. [Schema: time_played.json](#23-schema-time_playedjson)
24. [Schema: xp_curves.json](#24-schema-xp_curvesjson)
25. [Schema: skill_points.json + skill_trees.json](#25-schema-skill_pointsjson--skill_treesjson)
26. [Schema: abilities.json](#26-schema-abilitiesjson)
27. [Schema: rebirth_rewards.json](#27-schema-rebirth_rewardsjson)
28. [Schema: achievements.json](#28-schema-achievementsjson)
29. [Schema: battle_pass_seasons/season_XX.json](#29-schema-battle_pass_seasonsseason_xxjson)
30. [Schema: zone_definitions.json + unlock_gates.json](#30-schema-zone_definitionsjson--unlock_gatesjson)
31. [Schema: base_levels.json + base_upgrades.json](#31-schema-base_levelsjson--base_upgradesjson)
32. [Schema: generators.json + offline_config.json](#32-schema-generatorsjson--offline_configjson)
33. [Schema: crafting_timers.json](#33-schema-crafting_timersjson)
34. [Schema: hourly_boss.json](#34-schema-hourly_bossjson)
35. [Schema: seasonal_events.json](#35-schema-seasonal_eventsjson)
36. [Schema: codes_pool.json](#36-schema-codes_pooljson)
37. [Schema: admin_commands.json](#37-schema-admin_commandsjson)
38. [Schema: theme_config.json](#38-schema-theme_configjson)
39. [Schema: localization_keys.json](#39-schema-localization_keysjson)
40. [Schema: leaderboards.json + displays.json](#40-schema-leaderboardsjson--displaysjson)
41. [Schema: UI configs (activity_log, notifications, etc.)](#41-schema-ui-configs)
42. [Schema: events_catalog.json](#42-schema-events_catalogjson)
43. [Schema: modules_manifest.json](#43-schema-modules_manifestjson)
44. [Schema: player_stats_base.json](#44-schema-player_stats_basejson)
45. [Validación cruzada (referential integrity)](#45-validación-cruzada-referential-integrity)
46. [Cómo extender este documento](#46-cómo-extender-este-documento)

---

## 1. Convenciones generales

### 1.1 Notación de campos

```
field_name: type [REQUIRED|OPTIONAL] [range] — descripción
```

Ejemplos:

```
id: int [REQUIRED] [1..9999] — ID único del companion
display_name_key: string [REQUIRED] — clave de localización
base_hp: int [REQUIRED] [1..100000] — HP base, antes de variantes
tradable: bool [OPTIONAL, default=true] — si false, NUNCA tradable
```

### 1.2 Tipos permitidos

| Tipo | Notación | Ejemplo |
|---|---|---|
| Entero | `int` | `42` |
| Float | `float` | `3.14` |
| String | `string` | `"DRAGON_FIRE"` |
| Boolean | `bool` | `true` |
| Array de tipo X | `[]X` | `[1, 2, 3]` |
| Objeto anidado | `object` | `{ "key": "value" }` |
| Diccionario | `map<K, V>` | `{"common": 0.6, "rare": 0.1}` |
| Enum | `enum<X, Y, Z>` | `"common"` ∈ `{common, rare, ...}` |

### 1.3 Convención de naming

| Concepto | Convención | Ejemplo |
|---|---|---|
| **Archivos JSON** | `snake_case.json` | `companions_base.json` |
| **Claves JSON** | `snake_case` | `"base_hp": 100` |
| **IDs internos (string)** | `UPPER_SNAKE_CASE` | `"DRAGON_FIRE"` |
| **IDs numéricos** | `int` (compactos) | `1, 2, 3...` |
| **Claves de localización** | `dotted.lowercase` | `"companion.dragon_fire.name"` |
| **Comentarios** | `_comment_*` o `_doc` | `"_comment_id": "..."` |

### 1.4 Header obligatorio en todos los JSONs

Cada archivo JSON DEBE tener al inicio:

```json
{
  "_schema_version": 1,
  "_doc": "Descripción breve del archivo y referencia al SYS-xxx.",
  "_validation": "scripts/build/01_validate_jsons.py debe pasar antes de commit.",
  ...resto...
}
```

---

## 2. Reglas inquebrantables

> **Estas reglas aplican a TODOS los JSONs sin excepción.**

1. **IDs numéricos jamás se renumeran.** Una vez asignado un ID, es para siempre. Renumerar rompe persistencia (los jugadores tienen `ItemEntry.ItemID = 47` en weak_map).
2. **IDs deben ser únicos** dentro de su namespace (companion ID único entre companions, item ID único entre items, etc.).
3. **Los nombres internos (`UPPER_SNAKE_CASE`) jamás se renombran tras publish.** Mismo motivo que IDs.
4. **Los display names usan claves de localización**, nunca strings hardcodeados en el JSON principal.
5. **Todo precio/coste/recompensa va en JSON**, jamás hardcodeado en Verse.
6. **Todo flag de tradabilidad** (`tradable: bool`) debe estar declarado explícitamente en items que puedan tradearse o no.
7. **Items pagados con V-Bucks SIEMPRE tienen `tradable: false`** (regla cerrada en CONCEPT.md sección 14.2).
8. **Drop rates deben sumar exactamente 1.0** (con tolerancia ±0.001) en distribuciones probabilísticas.
9. **JSON estricto**: comas finales prohibidas, comentarios solo vía `_comment_*` keys.
10. **Encoding**: UTF-8 sin BOM siempre.
11. **Indentación**: 2 espacios.

---

## 3. Schema: companions_base.json

**Ubicación**: `data/companions/companions_base.json`
**Sistema**: SYS-010 Companion Core
**Generado a Verse**: `Content/Verse/Generated/Companions_Generated.verse`

### 3.1 Schema

```
{
  _schema_version: int [REQUIRED] [=1]
  _doc: string [REQUIRED]
  companions: []CompanionDef [REQUIRED] [length 1..9999]
}

CompanionDef := {
  id: int [REQUIRED] [1..9999] — ID único, no renumerar
  name: string [REQUIRED] [UPPER_SNAKE_CASE, length 3..40] — nombre interno, no renombrar
  display_name_key: string [REQUIRED] [pattern: "companion.*.name"]
  description_key: string [REQUIRED] [pattern: "companion.*.description"]
  rarity: int [REQUIRED] [1..8] — 1=Common, 2=Uncommon, 3=Rare, 4=Epic, 5=Legendary, 6=Mythic, 7=Secret, 8=Admin
  base_hp: int [REQUIRED] [1..100000]
  base_atk: int [REQUIRED] [1..100000]
  base_def: int [REQUIRED] [0..100000]
  base_speed: int [REQUIRED] [1..1000]
  category: enum<gather, combat, support, hybrid> [REQUIRED]
  obtainable_from: ObtainableSources [REQUIRED] — ver sección 42 (universal obtainability)
  mesh_path: string [REQUIRED] [pattern: "Content/Assets/Meshes/Companions/*.fbx"]
  icon_path: string [REQUIRED] [pattern: "Content/Assets/Icons/Companions/*.png"]
  tradable: bool [REQUIRED]
  vbucks_only: bool [OPTIONAL, default=false] — si true, tradable DEBE ser false
  evolution_chain: []int [OPTIONAL, default=[]] — IDs de companions a los que evoluciona
  passive_bonus: object [OPTIONAL] — bonus pasivo cuando está activo
}

ObtainableSources := {
  lootbox_premium: { drop_rate: float [0..1] } [OPTIONAL]
  boss_drops: []string [OPTIONAL] — IDs de bosses (UPPER_SNAKE_CASE)
  events: []string [OPTIONAL] — IDs de eventos
  battle_pass: { season: int, level: int, premium: bool } [OPTIONAL]
  shop: { price_gems: int, price_vbucks: int } [OPTIONAL]
  quest_reward: []int [OPTIONAL] — IDs de quests que dan este companion
}
```

### 3.2 Validaciones cruzadas

- ✅ `id` único entre todos los companions
- ✅ `name` único entre todos los companions
- ✅ Si `vbucks_only == true`, entonces `tradable == false`
- ✅ Si `obtainable_from` solo contiene `vbucks` source, entonces `tradable == false`
- ✅ Cada `evolution_chain[i]` debe existir como otro companion ID
- ✅ Cada `boss_drops[i]` debe existir en `data/world/bosses.json`
- ✅ Si `obtainable_from.battle_pass`, debe existir `season` en `battle_pass_seasons/`
- ✅ Cada companion debe tener AL MENOS UNA fuente en `obtainable_from` (regla SYS-038)

### 3.3 Ejemplo válido

```json
{
  "id": 1,
  "name": "DRAGON_FIRE",
  "display_name_key": "companion.dragon_fire.name",
  "description_key": "companion.dragon_fire.description",
  "rarity": 5,
  "base_hp": 100,
  "base_atk": 25,
  "base_def": 15,
  "base_speed": 12,
  "category": "combat",
  "obtainable_from": {
    "lootbox_premium": { "drop_rate": 0.05 },
    "boss_drops": ["FOREST_DRAGON_BOSS"],
    "events": ["FIRE_FESTIVAL_2026"],
    "battle_pass": { "season": 1, "level": 50, "premium": true }
  },
  "mesh_path": "Content/Assets/Meshes/Companions/dragon_fire.fbx",
  "icon_path": "Content/Assets/Icons/Companions/dragon_fire.png",
  "tradable": true,
  "evolution_chain": [101, 102]
}
```

---

## 4. Schema: variants.json

**Ubicación**: `data/companions/variants.json`
**Sistema**: SYS-012 Variants

### 4.1 Schema

```
{
  variants: []VariantDef [REQUIRED]
}

VariantDef := {
  id: int [REQUIRED] [0..255] — 0=Normal, 1=Oro, 2=Diamante, 3=Arcoiris, 4+=evento
  name: string [REQUIRED] [UPPER_SNAKE_CASE]
  display_name_key: string [REQUIRED]
  stat_multiplier: float [REQUIRED] [1.0..10.0] — multiplica todos los stats base
  unique_effect_key: string [OPTIONAL] — clave de efecto único en runtime
  visual_overlay: enum<none, gold, diamond, rainbow, glitch, lava, custom> [REQUIRED]
  is_event_only: bool [REQUIRED]
  event_id: string [OPTIONAL] — solo si is_event_only=true
  drop_rate_modifier: float [OPTIONAL, default=1.0] — multiplica drop rate base
  tradable: bool [REQUIRED]
}
```

### 4.2 Validaciones

- ✅ `id` único
- ✅ Si `is_event_only == true`, entonces `event_id` debe existir y referenciar evento válido
- ✅ Variant `id=0` (Normal) debe existir y tener `stat_multiplier=1.0`

---

## 5. Schema: dex_rewards.json

**Ubicación**: `data/companions/dex_rewards.json`
**Sistema**: SYS-015 Collection Dex

### 5.1 Schema

```
{
  rewards_by_completion: []DexReward [REQUIRED]
}

DexReward := {
  threshold_percent: float [REQUIRED] [0.0..100.0] — % de Dex completada
  reward_type: enum<gems, gold, lootbox, companion, title, cosmetic> [REQUIRED]
  reward_id: int [OPTIONAL] — ID del reward (si type lo requiere)
  amount: int [OPTIONAL] [1..*] — cantidad si gems/gold/lootbox
  display_name_key: string [REQUIRED]
}
```

### 5.2 Validaciones

- ✅ `threshold_percent` ordenados ascendentemente
- ✅ Sin duplicados de `threshold_percent`
- ✅ Si `reward_type == "companion"`, `reward_id` debe existir en `companions_base.json`

---

## 6. Schema: equipment.json

**Ubicación**: `data/items/equipment.json`
**Sistema**: SYS-024 Equipment Stats

### 6.1 Schema

```
{
  equipment: []EquipmentItem [REQUIRED]
}

EquipmentItem := {
  id: int [REQUIRED] [10000..99999] — range específico para equipo
  name: string [REQUIRED] [UPPER_SNAKE_CASE]
  display_name_key: string [REQUIRED]
  description_key: string [REQUIRED]
  slot: enum<ring, amulet, bracelet, talisman, charm, relic> [REQUIRED]
  rarity: int [REQUIRED] [1..8]
  base_stats: StatBlock [REQUIRED]
  set_id: int [OPTIONAL] — referencia a sets.json
  obtainable_from: ObtainableSources [REQUIRED]
  tradable: bool [REQUIRED]
  vbucks_only: bool [OPTIONAL, default=false]
  icon_path: string [REQUIRED]
}

StatBlock := {
  hp: int [OPTIONAL, default=0]
  atk: int [OPTIONAL, default=0]
  def: int [OPTIONAL, default=0]
  speed: int [OPTIONAL, default=0]
  intelligence: int [OPTIONAL, default=0]
  luck: int [OPTIONAL, default=0]
  crit_chance: float [OPTIONAL, default=0.0] [0.0..1.0]
  crit_damage: float [OPTIONAL, default=0.0] [0.0..10.0]
}
```

### 6.2 Validaciones

- ✅ `id` en rango 10000..99999 (equipo separado de companions/consumibles)
- ✅ Al menos 1 stat > 0 en `base_stats`
- ✅ `slot` debe coincidir con `equipment_slots.json`
- ✅ Si `set_id` definido, debe existir en `sets.json`

---

## 7. Schema: equipment_slots.json

**Ubicación**: `data/items/equipment_slots.json`
**Sistema**: SYS-023 Equipment Slots

### 7.1 Schema

```
{
  slots: []SlotDef [REQUIRED] [length=6] — 6 slots fijos
}

SlotDef := {
  id: int [REQUIRED] [0..5] — IDs fijos 0..5
  name: enum<ring, amulet, bracelet, talisman, charm, relic> [REQUIRED]
  display_name_key: string [REQUIRED]
  icon_path: string [REQUIRED]
  unlock_level: int [REQUIRED] [1..*] — nivel de jugador para desbloquear ese slot
}
```

### 7.2 Validaciones

- ✅ Exactamente 6 slots
- ✅ IDs 0..5 sin gaps
- ✅ Cada `name` único

---

## 8. Schema: equipment_leveling.json

**Ubicación**: `data/items/equipment_leveling.json`
**Sistema**: SYS-025 Equipment Leveling

### 8.1 Schema

```
{
  tier_progression: []TierEntry [REQUIRED] [length=10]
}

TierEntry := {
  from_tier: int [REQUIRED] [1..9]
  to_tier: int [REQUIRED] [2..10]
  success_rate: float [REQUIRED] [0.0..1.0] — probabilidad de éxito
  cost_gold: int [REQUIRED] [0..*]
  cost_materials: []MaterialCost [OPTIONAL]
  destroy_on_fail: bool [REQUIRED]
  protector_bronze_save: bool [OPTIONAL, default=true]
  protector_silver_save: bool [OPTIONAL, default=true]
  protector_gold_save: bool [OPTIONAL, default=true]
  protector_diamond_save: bool [OPTIONAL, default=true]
}

MaterialCost := {
  material_id: int [REQUIRED]
  quantity: int [REQUIRED] [1..*]
}
```

### 8.2 Validaciones

- ✅ `to_tier == from_tier + 1` siempre
- ✅ Cubre 1→2 hasta 9→10 (9 entradas)
- ✅ `success_rate` decrece monótonamente con tier (T1→T2 ≥ T9→T10)
- ✅ T1→T2 debería ser 100% (decisión cerrada CONCEPT 14.6)
- ✅ T9→T10 debería ser ~5%

---

## 9. Schema: protectors.json

**Ubicación**: `data/items/protectors.json`
**Sistema**: SYS-026 Protectors

### 9.1 Schema

```
{
  protectors: []ProtectorDef [REQUIRED]
}

ProtectorDef := {
  id: int [REQUIRED]
  name: string [REQUIRED] [UPPER_SNAKE_CASE]
  display_name_key: string [REQUIRED]
  tier: enum<bronze, silver, gold, diamond> [REQUIRED]
  consumable: bool [REQUIRED]
  duration_seconds: int [OPTIONAL] — solo si consumable=false (permanente o temporal)
  price_gold: int [OPTIONAL]
  price_gems: int [OPTIONAL]
  obtainable_from: ObtainableSources [REQUIRED]
}
```

### 9.2 Validaciones

- ✅ Si `consumable == false`, `duration_seconds` definido o -1 (permanente)
- ✅ Al menos un precio definido O al menos una source no-shop

---

## 10. Schema: sets.json

**Ubicación**: `data/items/sets.json`
**Sistema**: SYS-027 Set Bonuses

### 10.1 Schema

```
{
  sets: []SetDef [REQUIRED]
}

SetDef := {
  id: int [REQUIRED]
  name: string [REQUIRED] [UPPER_SNAKE_CASE]
  display_name_key: string [REQUIRED]
  pieces_required: []SetTier [REQUIRED] — bonuses por # piezas
}

SetTier := {
  pieces: int [REQUIRED] [2..6]
  bonus_stats: StatBlock [REQUIRED]
  bonus_description_key: string [REQUIRED]
}
```

### 10.2 Validaciones

- ✅ `pieces` ordenados ascendente sin gaps (ej: [2, 3, 4] o [2, 4, 6])
- ✅ Bonuses crecen con piezas

---

## 11. Schema: reroll.json

**Ubicación**: `data/items/reroll.json`
**Sistema**: SYS-028 Reroll Stats

### 11.1 Schema

```
{
  reroll_curve: RerollCurve [REQUIRED]
  reroll_pools: []RerollPool [REQUIRED]
}

RerollCurve := {
  base_cost_gold: int [REQUIRED] [1..*]
  exponent: float [REQUIRED] [1.0..3.0] — coste = base × (1 + rolls)^exponent
  cost_currency: enum<gold, gems> [REQUIRED]
}

RerollPool := {
  rarity: int [REQUIRED] [1..8]
  stat_min: int [REQUIRED]
  stat_max: int [REQUIRED]
  weighted_distribution: []float [REQUIRED] — probabilidades para cada stat range
}
```

### 11.2 Validaciones

- ✅ `stat_max > stat_min`
- ✅ `weighted_distribution` suma 1.0 (±0.001)

---

## 12. Schema: lootboxes.json

**Ubicación**: `data/items/lootboxes.json`
**Sistema**: SYS-034 Lootboxes (Almas)

### 12.1 Schema

```
{
  lootboxes: []LootboxDef [REQUIRED]
}

LootboxDef := {
  id: int [REQUIRED]
  name: string [REQUIRED] [UPPER_SNAKE_CASE]
  display_name_key: string [REQUIRED]
  alma_type: enum<basic, premium, event, mythic, secret> [REQUIRED]
  price_gems: int [REQUIRED] [1..*] — solo gemas, NUNCA V-Bucks (regla cerrada)
  drop_rates: DropRates [REQUIRED]
  pool: []int [REQUIRED] — IDs de companions/items posibles
  pity_eligible: bool [REQUIRED]
}

DropRates := {
  common: float [REQUIRED] [0..1]
  uncommon: float [REQUIRED] [0..1]
  rare: float [REQUIRED] [0..1]
  epic: float [REQUIRED] [0..1]
  legendary: float [REQUIRED] [0..1]
  mythic: float [REQUIRED] [0..1]
  secret: float [OPTIONAL, default=0]
  admin: float [OPTIONAL, default=0]
}
```

### 12.2 Validaciones

- ✅ Suma de todos los drop rates = 1.0 (±0.001)
- ✅ `price_gems > 0` y NUNCA `price_vbucks` (regla CONCEPT 14.2)
- ✅ `pool` no vacío
- ✅ Cada companion/item del pool debe existir
- ✅ Drop rates orientativos (CONCEPT 14.5):
  - Common ~60%, Uncommon ~25%, Rare ~10%, Epic ~3.5%, Legendary ~1%, Mythic ~0.4%, Secret ~0.09%, Admin ~0.01%

---

## 13. Schema: pity_config.json

**Ubicación**: `data/economy/pity_config.json`
**Sistema**: SYS-035 Pity System

### 13.1 Schema

```
{
  pity_rules: []PityRule [REQUIRED]
}

PityRule := {
  alma_type: enum<basic, premium, event, mythic, secret> [REQUIRED]
  rarity_target: int [REQUIRED] [3..8]
  pulls_until_guarantee: int [REQUIRED] [1..1000]
  reset_on_target_hit: bool [REQUIRED, default=true]
}
```

### 13.2 Validaciones

- ✅ Combinación `(alma_type, rarity_target)` única
- ✅ `pulls_until_guarantee` razonable (ej: Mythic ~80, Secret ~500)

---

## 14. Schema: prices.json

> 🚫 **REMOVIDO en v2.0 (changelog: dedupe shop/prices).**
>
> **Motivo**: tener precios en archivo separado obligaba a `price_ref` cross-file y duplicaba lookups en runtime. Ahora cada `ShopItem` declara sus precios inline.
>
> **Migración**: lo que antes iba en `prices.json:PriceEntry` (`price_gold`, `price_gems`, `price_vbucks`, `discount_percent`, `available_from`, `available_until`) ahora va **dentro de cada `ShopItem`** del schema §15 (`shop.json`).
>
> **NO crear este archivo.** El validador (`scripts/build/01_validate_jsons.py`, SPR-003) debe fallar si encuentra `data/economy/prices.json`.
>
> **Sección reservada**: el ID §14 se mantiene para no renumerar anchors. Esta sección se borrará por completo cuando se haga la próxima reorganización mayor del documento.

---

## 15. Schema: shop.json

**Ubicación**: `data/economy/shop.json`
**Sistema**: SYS-032 Shop System (catálogo unificado: items + precios + rotación)

### 15.1 Schema

```
{
  shop_categories: []ShopCategory [REQUIRED]
  shop_items: []ShopItem [REQUIRED]
}

ShopCategory := {
  id: int [REQUIRED]
  name_key: string [REQUIRED] — clave de localization_keys.json
  icon_path: string [REQUIRED]
  display_order: int [REQUIRED]
}

ShopItem := {
  id: int [REQUIRED]
  category_id: int [REQUIRED] — FK a ShopCategory.id
  item_ref: string [REQUIRED] — formato "companion:N", "equipment:N", "consumable:N", "lootbox:N"

  # === PRECIOS (al menos uno obligatorio) ===
  price_gold: int [OPTIONAL]
  price_gems: int [OPTIONAL]
  price_vbucks: int [OPTIONAL]
  discount_percent: float [OPTIONAL, default=0.0] [0..100]

  # === DISPONIBILIDAD ===
  available_from: int [OPTIONAL] — epoch UTC; 0 = siempre disponible
  available_until: int [OPTIONAL] — epoch UTC; 0 = sin expiración

  # === DISPLAY ===
  featured: bool [OPTIONAL, default=false]
  rotation_slot: enum<permanent, slot_a, slot_b, both, none> [REQUIRED]
}
```

### 15.2 Validaciones

- ✅ Cada `ShopItem` tiene **al menos un campo de precio** definido (`price_gold`, `price_gems` o `price_vbucks` > 0).
- ✅ `item_ref` apunta a item/companion/lootbox existente en su JSON correspondiente.
- ✅ Si `price_vbucks > 0`, el item referenciado debe tener `tradable: false` en su definición (anti-cashout).
- ✅ `category_id` existe en `shop_categories[]`.
- ✅ `rotation_slot ≠ permanent` ⇒ debe aparecer en `shop_rotations.json:rotation_pools` correspondiente.
- ✅ `available_from < available_until` cuando ambos están definidos.
- ✅ `discount_percent` ∈ [0, 100].

### 15.3 Ejemplo válido

```json
{
  "shop_categories": [
    { "id": 1, "name_key": "shop.cat.companions", "icon_path": "/Game/UI/Icons/cat_companion.png", "display_order": 1 }
  ],
  "shop_items": [
    {
      "id": 5001,
      "category_id": 1,
      "item_ref": "companion:42",
      "price_gems": 500,
      "price_vbucks": 200,
      "rotation_slot": "permanent",
      "featured": true
    },
    {
      "id": 5002,
      "category_id": 1,
      "item_ref": "lootbox:3",
      "price_gold": 10000,
      "discount_percent": 20.0,
      "available_until": 1735689600,
      "rotation_slot": "slot_a"
    }
  ]
}
```

---

## 16. Schema: shop_rotations.json

**Ubicación**: `data/economy/shop_rotations.json`
**Sistema**: SYS-033 Rotating Session Shop

### 16.1 Schema

```
{
  rotation_config: {
    rotation_minutes: int [REQUIRED, default=30] — cada 30 min sincronizado UTC
    slot_a_offset_minutes: int [REQUIRED, default=0]
    slot_b_offset_minutes: int [REQUIRED, default=30]
  }
  rotation_pools: {
    slot_a: []int [REQUIRED] — IDs de shop_items con rotation_slot in [slot_a, both]
    slot_b: []int [REQUIRED]
  }
}
```

### 16.2 Validaciones

- ✅ `rotation_minutes` divide 60 (15, 20, 30, 60)
- ✅ Cada item de los pools tiene `rotation_slot` compatible

---

## 17. Schema: vbucks_offers.json

**Ubicación**: `data/economy/vbucks_offers.json`
**Sistema**: SYS-031 V-Bucks Integration

### 17.1 Schema

```
{
  entitlements: []EntitlementDef [REQUIRED]
}

EntitlementDef := {
  entitlement_id: string [REQUIRED] — ID dado por Epic en Creator Portal
  display_name_key: string [REQUIRED]
  vbucks_price: int [REQUIRED] [1..*]
  rewards: []EntitlementReward [REQUIRED]
  is_founder_pack: bool [OPTIONAL, default=false]
  is_battle_pass: bool [OPTIONAL, default=false]
  one_time_purchase: bool [REQUIRED]
  consequential_to_gameplay: bool [REQUIRED] — REGLA EPIC v39.00. true si la entitlement otorga ventaja gameplay (companion premium, equipment, gem packs, BP). false solo para cosméticos puros (skins de UI, títulos, auras visuales). Mapea al campo `ConsequentialToGameplay` del Verse Offer.
}

EntitlementReward := {
  reward_type: enum<companion, equipment, gems, cosmetic, title> [REQUIRED]
  reward_id: int [OPTIONAL]
  amount: int [OPTIONAL]
}
```

### 17.2 Validaciones

- ✅ `entitlement_id` único
- ✅ Cada `reward_id` apunta a item/companion existente
- ✅ Items de rewards deben tener `tradable: false` (regla CONCEPT 14.2)
- ✅ **`consequential_to_gameplay` es REQUIRED** — el validador falla la build si falta. Sin él, la oferta no es publicable según política Epic v39.00+.
- ✅ Si `reward_type` ∈ {`companion`, `equipment`, `gems`} → `consequential_to_gameplay` debe ser `true` (advertencia si está en `false`).
- ✅ Si todos los rewards son `cosmetic` o `title` → `consequential_to_gameplay` puede ser `false` (cosmético puro).
- ✅ Si `is_battle_pass: true` → `consequential_to_gameplay` debe ser `true` (los BP del proyecto otorgan rewards gameplay).

### 17.3 Política Epic In-Island Transactions (compliance)

> **Fuente**: https://dev.epicgames.com/documentation/en-us/fortnite/in-island-transactions-overview-in-fortnite + release notes v39.00 (enero 2026).

- **Refund window**: Epic permite iniciar refunds masivos vía Creator Portal hasta **20 días después de la compra**. Items entregados **NO se revocan automáticamente** — el jugador conserva el item incluso si Epic refunda. Diseño defensivo: para entitlements de alto valor, considerar entrega progresiva o fraccionar en múltiples drops. **No diseñar mecánicas que asuman irreversibilidad económica antes de los 20 días.**
- **Reporting de denuncias**: Epic notifica si la tasa de denuncias por oferta supera la media. Mantener `display_name_key` y rewards alineados — engaño = denuncias = visibilidad afectada.
- **`ConsequentialToGameplay = True`** se comprueba en revisión Epic. Etiquetar mal una entitlement como `false` cuando da ventaja gameplay = oferta rechazada en publish.

---

## 18. Schema: gold.json + gems.json

**Ubicación**: `data/economy/gold.json`, `data/economy/gems.json`
**Sistemas**: SYS-029, SYS-030

### 18.1 Schema gold.json

```
{
  config: {
    starting_amount: int [REQUIRED, default=100]
    max_carry_no_bank: int [REQUIRED, default=10000]
    death_loss_percent: float [REQUIRED] [0..1, default=0.1] — % perdido al morir si no depositado
    bank_unlock_base_level: int [REQUIRED, default=2]
  }
  display: {
    icon_path: string [REQUIRED]
    color_hex: string [REQUIRED, default="#FCD34D"]
  }
}
```

### 18.2 Schema gems.json

```
{
  config: {
    starting_amount: int [REQUIRED, default=0]
    convertible_to_vbucks: bool [REQUIRED, =false] — REGLA CERRADA: gemas se queman
    convertible_from_vbucks: bool [REQUIRED, =false]
    max_amount: int [OPTIONAL, default=999999999]
  }
  generation_ratios: {
    passive_offline_per_hour: float [REQUIRED] [0..*]
    quest_daily: int [REQUIRED]
    quest_weekly: int [REQUIRED]
    achievement: int [REQUIRED]
    boss_drop: int [REQUIRED]
  }
  display: {
    icon_path: string [REQUIRED]
    color_hex: string [REQUIRED, default="#10B981"]
  }
}
```

### 18.3 Validaciones gems

- ✅ `convertible_to_vbucks == false` (REGLA INVIOLABLE)
- ✅ `convertible_from_vbucks == false` (REGLA INVIOLABLE)

---

## 19. Schema: auction_config.json

**Ubicación**: `data/economy/auction_config.json`
**Sistema**: SYS-037 Auction Same-Session

### 19.1 Schema

```
{
  config: {
    npc_vendor_name_key: string [REQUIRED]
    commission_percent: float [REQUIRED] [0..0.5]
    max_listings_per_player: int [REQUIRED] [1..50]
    min_price_gold: int [REQUIRED] [1..*]
    max_price_gold: int [REQUIRED]
    listing_duration_seconds: int [REQUIRED] — solo válido en sesión, expira al cerrar
    allow_gem_listings: bool [REQUIRED, default=false]
  }
  blacklist_item_types: []string [OPTIONAL] — categorías que NO se pueden listar
}
```

### 19.2 Validaciones

- ✅ Items con `tradable: false` automáticamente blacklisted
- ✅ V-Bucks items NUNCA listables

---

## 20. Schema: quests/*.json

**Ubicación**: `data/quests/*.json` (varios archivos: tutorial_chain.json, daily_pool.json, weekly_pool.json, story_chains.json)
**Sistema**: SYS-039 Quest System

### 20.1 Schema base de Quest

```
{
  quests: []QuestDef [REQUIRED]
}

QuestDef := {
  id: int [REQUIRED] — ID único globalmente entre todas las quests
  name: string [REQUIRED] [UPPER_SNAKE_CASE]
  display_name_key: string [REQUIRED]
  description_key: string [REQUIRED]
  category: enum<tutorial, daily, weekly, story, achievement, event> [REQUIRED]
  prerequisites: []int [OPTIONAL, default=[]] — IDs de quests previas requeridas
  objective: QuestObjective [REQUIRED]
  rewards: []QuestReward [REQUIRED]
  time_limit_seconds: int [OPTIONAL] — 0 o ausente = sin límite
  repeatable: bool [REQUIRED]
  reset_period: enum<none, daily, weekly, monthly> [REQUIRED]
  required_level: int [OPTIONAL, default=1]
  required_base_level: int [OPTIONAL, default=1]
}

QuestObjective := {
  type: enum<gather, kill, craft, level_up, collect_companion, complete_zone, spend_gold, spend_gems, login, time_played, custom> [REQUIRED]
  target_id: int [OPTIONAL] — ID del item/companion/zone target
  amount: int [REQUIRED] [1..*]
  custom_trigger_key: string [OPTIONAL] — solo si type=custom
}

QuestReward := {
  reward_type: enum<gold, gems, xp, bp_xp, item, companion, lootbox> [REQUIRED]
  reward_id: int [OPTIONAL]
  amount: int [REQUIRED]
}
```

### 20.2 Validaciones cruzadas

- ✅ `id` único globalmente entre TODOS los archivos de quests
- ✅ Cada `prerequisites[i]` debe existir como otra quest
- ✅ `target_id` debe existir según `type` (ej: `kill` → enemy ID, `gather` → resource ID)
- ✅ Si `category == "tutorial"`, `repeatable == false` y `reset_period == "none"`
- ✅ Si `category == "daily"`, `reset_period == "daily"`
- ✅ No ciclos en `prerequisites` (DAG)

---

## 21. Schema: tutorial_chain.json

**Ubicación**: `data/quests/tutorial_chain.json`
**Sistema**: SYS-065 Tutorial Chain

### 21.1 Schema

Hereda de quests/*.json pero con restricciones extra:

```
{
  tutorial_quests: []QuestDef [REQUIRED] [length=15]
  config: {
    skippable_for_admins: bool [REQUIRED, default=true]
    completion_unlocks_first_rebirth: bool [REQUIRED, =true]
  }
}
```

### 21.2 Validaciones

- ✅ Exactamente 15 quests (decisión cerrada CONCEPT 14.3)
- ✅ Todas con `category="tutorial"`
- ✅ Cadena lineal: cada quest tiene exactamente 1 prerequisite (excepto la primera)
- ✅ Última quest completa = unlock de rebirth (gate del primer rebirth)

---

## 22. Schema: daily_login.json

**Ubicación**: `data/progression/daily_login.json`
**Sistema**: SYS-040 Daily Login

### 22.1 Schema

```
{
  config: {
    cycle_days: int [REQUIRED, default=28]
    reset_timezone: enum<UTC> [REQUIRED, =UTC]
    rescue_with_gems_enabled: bool [REQUIRED]
    rescue_cost_per_day_gems: int [REQUIRED, default=10]
  }
  rewards: []DailyLoginReward [REQUIRED] [length=28]
}

DailyLoginReward := {
  day: int [REQUIRED] [1..28]
  reward_type: enum<gold, gems, xp, item, companion, lootbox, cosmetic> [REQUIRED]
  reward_id: int [OPTIONAL]
  amount: int [REQUIRED]
  is_milestone: bool [OPTIONAL, default=false] — días 7, 14, 21, 28 son milestones
}
```

### 22.2 Validaciones

- ✅ Exactamente 28 días
- ✅ Días 7, 14, 21, 28 con `is_milestone=true`
- ✅ Recompensas crecen progresivamente (la del día 28 > día 1)

---

## 23. Schema: time_played.json

**Ubicación**: `data/progression/time_played.json`
**Sistema**: SYS-041 Time Played Rewards

### 23.1 Schema

```
{
  thresholds: []TimeThreshold [REQUIRED]
  config: {
    reset_period: enum<daily, weekly> [REQUIRED, default=daily]
  }
}

TimeThreshold := {
  minutes: int [REQUIRED] [1..*]
  reward_type: enum<gold, gems, xp, item> [REQUIRED]
  amount: int [REQUIRED]
}
```

### 23.2 Validaciones

- ✅ `minutes` ordenados ascendentes
- ✅ Sin duplicados

---

## 24. Schema: xp_curves.json

**Ubicación**: `data/progression/xp_curves.json`
**Sistema**: SYS-016 XP & Levels

### 24.1 Schema

```
{
  player_xp_curve: XPCurve [REQUIRED]
  base_xp_curve: XPCurve [REQUIRED]
  bp_xp_curve: XPCurve [REQUIRED]
}

XPCurve := {
  formula: enum<exponential, polynomial, custom> [REQUIRED]
  base: int [REQUIRED] — XP del nivel 1→2
  exponent: float [OPTIONAL] — para exponential: xp = base × level^exponent
  polynomial_coefficients: []float [OPTIONAL] — para polynomial
  max_level: int [REQUIRED] [1..1000]
  custom_levels: map<int, int> [OPTIONAL] — overrides específicos por nivel
}
```

### 24.2 Validaciones

- ✅ XP requerido crece monótonamente con nivel
- ✅ `max_level >= 1`
- ✅ Si `formula == "exponential"`, `exponent` requerido
- ✅ Si `formula == "polynomial"`, `polynomial_coefficients` requerido

---

## 25. Schema: skill_points.json + skill_trees.json

**Ubicación**: `data/progression/skill_points.json`, `data/progression/skill_trees.json`
**Sistemas**: SYS-017, SYS-018

### 25.1 Schema skill_points.json

```
{
  formula: {
    points_per_level: int [REQUIRED, default=1]
    bonus_at_milestone_levels: map<int, int> [OPTIONAL] — ej: {10: 2, 25: 3, 50: 5}
  }
}
```

### 25.2 Schema skill_trees.json

```
{
  trees: []SkillTree [REQUIRED] [length=5]
}

SkillTree := {
  id: int [REQUIRED] [1..5]
  name: enum<combat, gathering, survival, collector, economy> [REQUIRED]
  display_name_key: string [REQUIRED]
  icon_path: string [REQUIRED]
  skills: []SkillNode [REQUIRED]
}

SkillNode := {
  id: int [REQUIRED] — único globalmente
  tree_id: int [REQUIRED]
  display_name_key: string [REQUIRED]
  description_key: string [REQUIRED]
  max_rank: int [REQUIRED] [1..10]
  cost_per_rank: []int [REQUIRED] — coste de skill points para cada rank
  prerequisites: []int [OPTIONAL] — IDs de otros skills (mismo o cualquier tree)
  effect_type: enum<stat_modifier, ability_unlock, passive, special> [REQUIRED]
  effect_value_per_rank: []float [REQUIRED] — valor del efecto por rank
  effect_target: string [REQUIRED] — ej: "player.atk", "gather.speed"
}
```

### 25.3 Validaciones

- ✅ Exactamente 5 trees (decisión cerrada CONCEPT 14.3)
- ✅ Trees: combate, recolección, supervivencia, coleccionista, economía
- ✅ `cost_per_rank.length == max_rank`
- ✅ `effect_value_per_rank.length == max_rank`
- ✅ No ciclos en prerequisites (DAG)
- ✅ **Coherencia persistencia (C4)**: cada `SkillNode.id` debe ser único globalmente (cross-tree). El validador debe verificar que no hay 2 SkillNode con mismo `id` en todo el catálogo. La persistencia usa `SkillPointEntry{SkillID, Rank}` indexado por este id global (ver `PERSISTENCE_MAP.md` §3.1). IDs no necesitan ser contiguos.
- ✅ **Validación cross-rank**: para cada entrada de `SkillPoints_Spent` en runtime, verificar `1 <= Rank <= max_rank` del SkillNode correspondiente. Si un patch reduce `max_rank` de un skill, el load defensivo debe clampar el rank persistido al nuevo máximo.

---

## 26. Schema: abilities.json

**Ubicación**: `data/progression/abilities.json`
**Sistema**: SYS-019 Active Abilities

### 26.1 Schema

```
{
  abilities: []AbilityDef [REQUIRED]
}

AbilityDef := {
  id: int [REQUIRED]
  name: string [REQUIRED] [UPPER_SNAKE_CASE]
  display_name_key: string [REQUIRED]
  description_key: string [REQUIRED]
  unlock_zone_id: int [OPTIONAL] — desbloqueada al entrar a zone
  unlock_skill_id: int [OPTIONAL] — desbloqueada por skill tree
  cooldown_seconds: float [REQUIRED] [0..600]
  cost_stamina: int [OPTIONAL, default=0]
  effect_type: enum<damage, heal, dash, buff, debuff, summon, special> [REQUIRED]
  effect_params: object [REQUIRED] — específico de effect_type
  vfx_trigger_key: string [OPTIONAL]
}
```

---

## 27. Schema: rebirth_rewards.json

**Ubicación**: `data/progression/rebirth_rewards.json`
**Sistema**: SYS-020 Rebirth System

### 27.1 Schema

```
{
  rebirth_curve: {
    formula: enum<exponential, custom> [REQUIRED]
    base_minutes_to_first: int [REQUIRED, default=30]
    target_minutes_at: map<int, int> [REQUIRED] — ej: {1:30, 5:240, 10:600, 25:1800, 50:4800}
  }
  permanent_rewards: []RebirthReward [REQUIRED]
}

RebirthReward := {
  rebirth_count: int [REQUIRED] [1..*] — el rebirth en el que se otorga
  reward_type: enum<stat_bonus, ability_unlock, slot_unlock, multiplier, cosmetic, title> [REQUIRED]
  reward_id: int [OPTIONAL]
  amount: float [OPTIONAL]
  description_key: string [REQUIRED]
}
```

### 27.2 Validaciones

- ✅ Curva monótona creciente (rebirth N+1 toma más tiempo que N)
- ✅ Coincide con CONCEPT 14.3: r1~30min, r5~3-4h, r10~10h, r25~30h, r50~80h, r100~200h

---

## 28. Schema: achievements.json

**Ubicación**: `data/progression/achievements.json`
**Sistema**: SYS-021 Achievements

### 28.1 Schema

```
{
  achievements: []AchievementDef [REQUIRED] [length 1..256]
}

AchievementDef := {
  id: int [REQUIRED] [0..255] — bitfield index, max 256 achievements
  name: string [REQUIRED] [UPPER_SNAKE_CASE]
  display_name_key: string [REQUIRED]
  description_key: string [REQUIRED]
  icon_path: string [REQUIRED]
  category: enum<combat, exploration, collection, economy, social, secret> [REQUIRED]
  criteria: AchievementCriteria [REQUIRED]
  rewards: []QuestReward [OPTIONAL]
  hidden: bool [OPTIONAL, default=false]
}

AchievementCriteria := {
  type: enum<reach_level, kill_count, gather_count, collect_companions, complete_quest, custom> [REQUIRED]
  amount: int [OPTIONAL]
  target_id: int [OPTIONAL]
  custom_trigger_key: string [OPTIONAL]
}
```

### 28.2 Validaciones

- ✅ Máximo 256 achievements (limit del bitfield en PlayerProgress, ver PERSISTENCE_MAP 5.1)
- ✅ `id` único en rango [0, 255]

---

## 29. Schema: battle_pass_seasons/season_XX.json

**Ubicación**: `data/progression/battle_pass_seasons/season_NN.json` (NN = 01, 02...)
**Sistema**: SYS-022 Battle Pass

### 29.1 Schema

```
{
  season_id: int [REQUIRED] [1..*]
  display_name_key: string [REQUIRED]
  start_epoch_utc: int [REQUIRED]
  end_epoch_utc: int [REQUIRED]
  total_levels: int [REQUIRED, default=100]
  premium_price_gems: int [OPTIONAL]
  premium_price_vbucks: int [OPTIONAL]
  xp_curve_ref: string [REQUIRED] — clave en xp_curves.json
  free_track: []BPLevelReward [REQUIRED]
  premium_track: []BPLevelReward [REQUIRED]
}

BPLevelReward := {
  level: int [REQUIRED] [1..total_levels]
  reward_type: enum<gold, gems, xp, item, companion, lootbox, cosmetic, title> [REQUIRED]
  reward_id: int [OPTIONAL]
  amount: int [REQUIRED]
}
```

### 29.2 Validaciones

- ✅ `end_epoch_utc > start_epoch_utc`
- ✅ `free_track.length <= total_levels` y `premium_track.length <= total_levels`
- ✅ Sin duplicados de `level` en cada track
- ✅ Si `premium_price_vbucks > 0`, las recompensas premium tienen `tradable: false`
- ✅ `total_levels <= 192` (cap impuesto por bitfields BP en PlayerProgress, ver `PERSISTENCE_MAP.md` §5.1). Para >192 niveles habría que añadir un 4º bitfield.
- ✅ `total_levels <= MAX_BP_LEVELS` (ver `BALANCE_FORMULAS.md` §2.1, default `100`). Cap de diseño, no técnico.

---

## 30. Schema: zone_definitions.json + unlock_gates.json

**Ubicación**: `data/zones/zone_definitions.json`, `data/zones/unlock_gates.json`
**Sistema**: SYS-007 Zone Unlock

### 30.1 Schema zone_definitions.json

```
{
  zones: []ZoneDef [REQUIRED]
}

ZoneDef := {
  id: int [REQUIRED]
  name: string [REQUIRED] [UPPER_SNAKE_CASE]
  display_name_key: string [REQUIRED]
  width: float [REQUIRED] [100..50000] — en unidades UE
  height: float [REQUIRED] [100..50000]
  origin: { x: float, y: float, z: float } [REQUIRED]
  resource_nodes: []ResourceNodeSpec [REQUIRED]
  prop_density: float [REQUIRED] [0..1]
  min_node_distance: float [REQUIRED] [50..1000]
  enemy_spawns: []EnemySpawnSpec [OPTIONAL]
  ambient_track_key: string [OPTIONAL]
  is_starting_zone: bool [REQUIRED]
}

ResourceNodeSpec := {
  resource_id: int [REQUIRED]
  spawn_count: int [REQUIRED]
  respawn_seconds: int [REQUIRED]
}

EnemySpawnSpec := {
  enemy_id: int [REQUIRED]
  spawn_count: int [REQUIRED]
  patrol_radius: float [OPTIONAL]
}
```

### 30.2 Schema unlock_gates.json

```
{
  gates: []ZoneGate [REQUIRED]
}

ZoneGate := {
  zone_id: int [REQUIRED]
  required_base_level: int [OPTIONAL]
  required_player_level: int [OPTIONAL]
  required_quests_completed: []int [OPTIONAL]
  required_boss_defeated: int [OPTIONAL]
  required_resources: []MaterialCost [OPTIONAL]
}
```

### 30.3 Validaciones

- ✅ Exactamente 1 zone con `is_starting_zone == true`
- ✅ `required_*` cumple al menos UNA condición (no gate vacío)

---

## 31. Schema: base_levels.json + base_upgrades.json

**Ubicación**: `data/base/base_levels.json`, `data/base/base_upgrades.json`
**Sistemas**: SYS-059, SYS-060

### 31.1 Schema base_levels.json

```
{
  base_xp_curve: XPCurve [REQUIRED]
  unlocks_per_level: map<int, BaseLevelUnlocks> [OPTIONAL]
}

BaseLevelUnlocks := {
  unlocks_zones: []int [OPTIONAL]
  unlocks_quests: []int [OPTIONAL]
  unlocks_upgrades: []int [OPTIONAL]
  unlocks_features: []string [OPTIONAL]
}
```

### 31.2 Schema base_upgrades.json

```
{
  upgrades: []BaseUpgrade [REQUIRED]
}

BaseUpgrade := {
  id: int [REQUIRED]
  name: string [REQUIRED] [UPPER_SNAKE_CASE]
  display_name_key: string [REQUIRED]
  description_key: string [REQUIRED]
  category: enum<logistics, passive, generator, defensive, aesthetic> [REQUIRED]
  max_tier: int [REQUIRED] [1..20]
  cost_per_tier: []UpgradeCost [REQUIRED]
  effect_per_tier: []float [REQUIRED]
  effect_target: string [REQUIRED] — ej: "inventory.max_slots", "generator.gold.rate"
  prerequisites: []int [OPTIONAL]
  required_base_level: []int [REQUIRED] — required_base_level[t] = base level para tier t
}

UpgradeCost := {
  gold: int [OPTIONAL]
  gems: int [OPTIONAL]
  materials: []MaterialCost [OPTIONAL]
  time_seconds: int [OPTIONAL] — crafting timer si aplica
}
```

### 31.3 Validaciones

- ✅ `cost_per_tier.length == max_tier`
- ✅ `effect_per_tier.length == max_tier`
- ✅ `required_base_level.length == max_tier`
- ✅ Costes monótonos crecientes
- ✅ Effects monótonos crecientes (más tier = más efecto)

---

## 32. Schema: generators.json + offline_config.json

**Ubicación**: `data/base/generators.json`, `data/base/offline_config.json`
**Sistemas**: SYS-061, SYS-062

### 32.1 Schema generators.json

```
{
  generators: []GeneratorDef [REQUIRED]
}

GeneratorDef := {
  id: int [REQUIRED]
  name: string [REQUIRED] [UPPER_SNAKE_CASE]
  resource_type: enum<gold, gems, materials, custom> [REQUIRED]
  resource_id: int [OPTIONAL] — solo si resource_type == materials/custom
  base_rate_per_hour: float [REQUIRED] [0..*]
  upgrade_id: int [REQUIRED] — referencia a base_upgrades.json para escalarlo
  upgrade_rate_multiplier_per_tier: []float [REQUIRED]
}
```

### 32.2 Schema offline_config.json

```
{
  offline_caps: []OfflineCap [REQUIRED] — caps por base level
}

OfflineCap := {
  base_level: int [REQUIRED]
  max_offline_hours: int [REQUIRED] [1..168] — hasta 7 días máx
  efficiency_percent: float [REQUIRED] [0.0..1.0] — 0.3..0.8 según CONCEPT 14.8
}
```

### 32.3 Validaciones

- ✅ Caps monótonos crecientes con base_level
- ✅ Efficiency monótona creciente con base_level
- ✅ CONCEPT 14.8: base lvl 10 → 12h, base lvl 50 → 48h, eficiencia 30%-80%

---

## 33. Schema: crafting_timers.json

**Ubicación**: `data/items/crafting_timers.json`
**Sistema**: SYS-063 Crafting Timers

### 33.1 Schema

```
{
  recipes: []CraftingRecipe [REQUIRED]
}

CraftingRecipe := {
  id: int [REQUIRED]
  name: string [REQUIRED] [UPPER_SNAKE_CASE]
  display_name_key: string [REQUIRED]
  category: enum<forge, alchemy, hatchery, custom> [REQUIRED]
  inputs: []MaterialCost [REQUIRED]
  output_item_id: int [REQUIRED]
  output_quantity: int [REQUIRED, default=1]
  craft_time_seconds: int [REQUIRED] [1..604800] — máx 7 días
  required_base_level: int [OPTIONAL, default=1]
  required_upgrades: []int [OPTIONAL]
}
```

### 33.2 Validaciones

- ✅ `craft_time_seconds > 0`
- ✅ Tiempo offline NO se capea (decisión cerrada CONCEPT 14.8)
- ✅ Inputs no vacío

---

## 34. Schema: hourly_boss.json

**Ubicación**: `data/events/hourly_boss.json`
**Sistema**: SYS-042 Hourly Boss Event

### 34.1 Schema

```
{
  config: {
    portal_open_minute: int [REQUIRED, default=0] — minuto de la hora en que abre
    portal_window_seconds: int [REQUIRED, default=120] — 2 min ventana
    teleport_delay_seconds: int [REQUIRED, default=0] — desde que se cierra
    max_attempts_per_hour: int [REQUIRED, default=1]
    arena_level_path: string [REQUIRED]
  }
  bosses_rotation: []HourlyBoss [REQUIRED]
  rotation_strategy: enum<sequential, random, time_based> [REQUIRED]
}

HourlyBoss := {
  boss_id: int [REQUIRED]
  display_name_key: string [REQUIRED]
  required_player_level: int [OPTIONAL, default=1]
  required_base_level: int [OPTIONAL, default=1]
  required_quests: []int [OPTIONAL]
  rewards: []QuestReward [REQUIRED]
}
```

### 34.2 Validaciones

- ✅ `portal_window_seconds <= 600` (max 10 min razonable)
- ✅ Recompensas también deben ser dropeables en otras fuentes (CONCEPT 14.7)

---

## 35. Schema: seasonal_events.json

**Ubicación**: `data/events/seasonal_events.json`
**Sistema**: SYS-043 Long Events

### 35.1 Schema

```
{
  events: []SeasonalEvent [REQUIRED]
}

SeasonalEvent := {
  id: string [REQUIRED] [UPPER_SNAKE_CASE]
  display_name_key: string [REQUIRED]
  start_epoch_utc: int [REQUIRED]
  end_epoch_utc: int [REQUIRED]
  exclusive_companions: []int [OPTIONAL]
  exclusive_zones: []int [OPTIONAL]
  exclusive_quests: []int [OPTIONAL]
  shop_extras: []int [OPTIONAL] — IDs de shop_items extra
  banner_path: string [OPTIONAL]
  active_by_default: bool [REQUIRED, default=false]
}
```

### 35.2 Validaciones

- ✅ `end > start`
- ✅ Eventos no se solapan (warning, no error)

---

## 36. Schema: codes_pool.json

**Ubicación**: `data/events/codes_pool.json`
**Sistema**: SYS-045 Code Redemption

### 36.1 Schema

```
{
  codes: []CodeDef [REQUIRED]
}

CodeDef := {
  id: int [REQUIRED]
  code_string: string [REQUIRED] [UPPERCASE, length 4..20] — el código que escribe el jugador
  type: enum<public_unlimited, public_limited, single_use, time_limited> [REQUIRED]
  max_redemptions: int [OPTIONAL] — null para unlimited
  expires_at_epoch_utc: int [OPTIONAL] — null para never
  rewards: []QuestReward [REQUIRED]
  active_by_default: bool [REQUIRED, default=false]
  display_name_key: string [OPTIONAL]
}
```

### 36.2 Validaciones

- ✅ `code_string` único (case-insensitive)
- ✅ `code_string` solo A-Z y 0-9 (no caracteres especiales)
- ✅ Si `type == "single_use"`, `max_redemptions == 1`
- ✅ Si `type == "time_limited"`, `expires_at_epoch_utc` requerido

---

## 37. Schema: admin_commands.json

**Ubicación**: `data/admin/admin_config.json`, `data/admin/test_flags.json`
**Sistemas**: SYS-070, SYS-071

> **Decisión cerrada (Auditoría retrospectiva — Bloque 1)**: `admin_player_ids` **eliminado** del schema. La API Verse de `player` no expone `GetID()`/`GetName()`/`GetAccountID()` (fuente oficial: [dev.epicgames.com — player class](https://dev.epicgames.com/documentation/en-us/fortnite/verse-api/versedotorg/simulation/player) — único método público documentado: `IsActive[]`). La identificación de admins se hace vía `player_reference_device` configurado en editor UEFN con las cuentas admin (comprobado en runtime con `AdminRef.IsRegistered[Agent]`). Este JSON solo lleva el **catálogo de comandos y metadata**. Detalle del patrón en `CONCEPT.md` SPR-010 + `GLOSSARY.md` "Admin (player ID)".

### 37.1 Schema admin_config.json

```
{
  commands: []AdminCommand [REQUIRED]
}

AdminCommand := {
  id: string [REQUIRED] [snake_case]
  display_name: string [REQUIRED]
  args: []AdminArg [OPTIONAL]
  category: enum<currency, items, quests, events, debug, persistence> [REQUIRED]
  log_to_console: bool [REQUIRED, default=true]
  requires_confirmation: bool [REQUIRED, default=false]
}

AdminArg := {
  name: string [REQUIRED]
  type: enum<int, string, bool, player_ref> [REQUIRED]
  required: bool [REQUIRED]
}
```

### 37.2 Validaciones

- ✅ `commands` no vacío
- ✅ `id` único por entry
- ✅ Comandos peligrosos (reset_data, etc.) tienen `requires_confirmation: true`

> **Nota**: la asignación de qué cuentas Epic son admin **no se valida en este JSON**. Se configura en editor UEFN: cada `player_reference_device` instanciado y configurado con la cuenta admin que registra es el source of truth. El validador Python solo comprueba que existe **al menos un** `player_reference_device` con tag `admin` en el level cuando `data/admin/admin_config.json` define comandos (chequeo en `01_validate_jsons.py` cruzado con el dump del level UEFN, si está disponible — opcional, warning si falta).

---

## 38. Schema: theme_config.json

**Ubicación**: `data/theme/theme_config.json`
**Sistema**: SYS-046 Seasonal Content Framework

### 38.1 Schema

```
{
  active_theme: string [REQUIRED] — clave en themes
  themes: map<string, ThemeDef> [REQUIRED]
}

ThemeDef := {
  display_name_key: string [REQUIRED]
  hub_mesh_path: string [REQUIRED]
  skybox_material_path: string [REQUIRED]
  ambient_track_key: string [REQUIRED]
  color_palette_overrides: map<string, string> [OPTIONAL] — overrides de UI_UX_STYLE_GUIDE
  asset_swap_rules: []AssetSwapRule [REQUIRED]
  exclusive_companions: []int [OPTIONAL]
  exclusive_items: []int [OPTIONAL]
}

AssetSwapRule := {
  pattern: string [REQUIRED] — glob pattern, ej: "Content/Assets/Trees/*.fbx"
  replacement_folder: string [REQUIRED] — ej: "Content/Assets/Trees_Halloween/"
}
```

### 38.2 Validaciones

- ✅ `active_theme` debe existir en `themes` map
- ✅ Cada `replacement_folder` debe existir en disco al ejecutar pipeline

---

## 39. Schema: localization_keys.json

**Ubicación**: `data/theme/localization_keys.json` (o `data/localization/`)

### 39.1 Schema

```
{
  keys: map<string, LocalizationEntry> [REQUIRED]
}

LocalizationEntry := {
  en: string [REQUIRED]
  es: string [REQUIRED]
  fr: string [OPTIONAL]
  de: string [OPTIONAL]
  it: string [OPTIONAL]
  pt: string [OPTIONAL]
  ja: string [OPTIONAL]
  ko: string [OPTIONAL]
  zh_cn: string [OPTIONAL]
  zh_tw: string [OPTIONAL]
  ru: string [OPTIONAL]
  ar: string [OPTIONAL]
  pl: string [OPTIONAL]
  tr: string [OPTIONAL]
}
```

### 39.2 Validaciones

- ✅ Cada `display_name_key`, `description_key` referenciada en cualquier JSON debe existir aquí
- ✅ Mínimo `en` y `es` definidos (idiomas obligatorios)

---

## 40. Schema: leaderboards.json + displays.json

**Ubicación**: `data/social/leaderboards.json`, `data/social/displays.json`
**Sistemas**: SYS-047, SYS-048

### 40.1 Schema leaderboards.json

```
{
  leaderboards: []LeaderboardDef [REQUIRED]
}

LeaderboardDef := {
  id: string [REQUIRED] [snake_case]
  display_name_key: string [REQUIRED]
  stat_tracked: enum<level, rebirth_count, base_level, dex_completion, gold_lifetime, kills, etc> [REQUIRED]
  scope: enum<global, session, weekly, monthly> [REQUIRED]
  sort_order: enum<desc, asc> [REQUIRED]
  display_top_n: int [REQUIRED, default=100]
}
```

### 40.2 Schema displays.json

```
{
  social_displays: []SocialDisplay [REQUIRED]
}

SocialDisplay := {
  id: int [REQUIRED]
  type: enum<pet, aura, title, badge> [REQUIRED]
  display_name_key: string [REQUIRED]
  unlock_condition: UnlockCondition [REQUIRED]
  visual_path: string [OPTIONAL]
}

UnlockCondition := {
  type: enum<rebirth_count, dex_percent, achievement, purchase, free> [REQUIRED]
  value: int [OPTIONAL]
  achievement_id: int [OPTIONAL]
}
```

---

## 41. Schema: UI configs

**Ubicación**: `data/ui/*.json`
**Sistemas**: SYS-049, SYS-050, SYS-051, SYS-052, SYS-056, SYS-057, SYS-058

### 41.1 activity_log.json

```
{
  config: {
    max_lines_visible: int [REQUIRED, default=4]
    auto_fade_seconds: float [REQUIRED, default=5.0]
    width_desktop_px: int [REQUIRED, default=320]
    width_mobile_px: int [REQUIRED, default=280]
  }
  categories: []ActivityCategory [REQUIRED]
}

ActivityCategory := {
  id: string [REQUIRED] [snake_case]
  display_name_key: string [OPTIONAL]
  border_color_hex: string [REQUIRED]
  icon_prefix: string [OPTIONAL]
}
```

### 41.2 notifications.json

```
{
  config: {
    pool_size: int [REQUIRED, default=10] — # de hud_message_devices reusables
    queue_max: int [REQUIRED, default=20]
  }
  priorities: []NotificationPriority [REQUIRED]
}

NotificationPriority := {
  level: enum<low, medium, high, critical> [REQUIRED]
  cooldown_ms: int [REQUIRED]
  preempts_lower: bool [REQUIRED]
}
```

### 41.3 auto_sell_config.json

```
{
  filters: []AutoSellFilter [REQUIRED]
}

AutoSellFilter := {
  id: int [REQUIRED]
  display_name_key: string [REQUIRED]
  by_rarity: []int [OPTIONAL]
  by_type: []string [OPTIONAL]
  whitelist_ids: []int [OPTIONAL]
  enabled_by_default: bool [REQUIRED, default=false]
}
```

### 41.4 hotkeys.json

```
{
  hotkeys: []HotkeyDef [REQUIRED]
  radial_menu_mobile: []RadialEntry [REQUIRED]
}

HotkeyDef := {
  action_id: string [REQUIRED]
  default_key: string [REQUIRED]
  customizable: bool [REQUIRED]
}

RadialEntry := {
  position: int [REQUIRED] [0..7] — 8 posiciones radial
  action_id: string [REQUIRED]
  icon_path: string [REQUIRED]
}
```

### 41.5 error_messages.json

```
{
  messages: map<string, string> [REQUIRED] — error_id → display_name_key
}
```

### 41.6 rate_limits.json

```
{
  rate_limits: []RateLimitDef [REQUIRED]
}

RateLimitDef := {
  action_id: string [REQUIRED]
  cooldown_ms: int [REQUIRED]
  max_per_minute: int [OPTIONAL]
}
```

---

## 42. Schema: events_catalog.json

> **Decisión cerrada (Auditoría 2 — C3 + Auditoría regresión bloque 5 — H4)**: catálogo declarativo de eventos cross-system del proyecto. Source of truth del EventBus tipado. Genera `Generated/EventPayloads_Generated.verse` (structs de payloads) y `Generated/EventBusDevice.verse` (`event_bus_device := class<concrete>(creative_device)` con propiedades `event(t)` tipadas — patrón H4 post-F-C-2 SPR-009, NO singleton top-level). Detalle de la generación en `BOOTSTRAP_PIPELINE.md` §11. **Catalog JSON inmutable post-H4**: el schema (id, verse_struct_name, verse_event_name, emitters, subscribers, payload_fields) sigue válido — solo cambió el archivo Verse generado y su patrón de instanciación. Decisión D-A11 en `CHANGELOG.md`.

**Path**: `data/architecture/events_catalog.json`

**Por qué no usamos strings con `Payload:any`**: Verse SÍ tiene tipo `any` ([dev.epicgames.com — Any in Verse](https://dev.epicgames.com/documentation/en-us/fortnite/any-in-verse): *"Verse has a special type, any, that is the supertype of all types"*) pero es supertipo opaco con operaciones muy limitadas — sin acceso tipado a campos del payload no encaja en handlers de events. Verse SÍ tiene `event<native>(t:type)` parametric type compile-time (ver `Verse.digest`). Cada evento del proyecto recibe un struct de payload propio + una instancia `event(payload_t)` única en el EventBus central. Type-safety garantizada por compilador, sin string-magic.

### 42.1 Estructura

```json
{
  "_schema_version": 1,
  "_doc": "Catálogo declarativo de eventos cross-system. Cada entrada genera un struct Verse + una instancia event(t) en EventBus.",
  "_validation": "scripts/build/01_validate_jsons.py debe pasar antes de commit.",

  "events": [
    {
      "id": "player_stats_changed",
      "verse_struct_name": "player_stats_changed_payload",
      "verse_event_name": "PlayerStatsChanged",
      "emitters": ["PlayerStats"],
      "subscribers": ["HUDController", "AchievementEngine", "SocialDisplay"],
      "payload_fields": [
        {"name": "Player", "type": "player", "_doc": "referencia nativa Verse al jugador afectado — usable como key directo en weak_map de persistencia"},
        {"name": "Stat", "type": "string", "_doc": "nombre del stat: 'HP_Max', 'Strength', etc."},
        {"name": "OldValue", "type": "int"},
        {"name": "NewValue", "type": "int"}
      ],
      "_doc": "Emitido cuando un stat efectivo del jugador cambia (post-buff, post-equipment)."
    },
    {
      "id": "level_up",
      "verse_struct_name": "level_up_payload",
      "verse_event_name": "LevelUp",
      "emitters": ["PlayerProgression"],
      "subscribers": ["HUDController", "Notifications", "BattlePass", "AchievementEngine"],
      "payload_fields": [
        {"name": "Player", "type": "player"},
        {"name": "OldLevel", "type": "int"},
        {"name": "NewLevel", "type": "int"}
      ]
    }
  ]
}
```

### 42.2 Reglas del schema

| Campo | Tipo | Reglas |
|---|---|---|
| `id` | string | snake_case único, inmutable. Identificador conceptual del evento. |
| `verse_struct_name` | string | snake_case + `_payload`. Nombre del struct Verse generado. Debe ser único en todo el proyecto. |
| `verse_event_name` | string | PascalCase. Nombre de la propiedad en `event_bus_device` (post-H4 SPR-009; antes `event_bus_module` pre-H4). Único en el bus. |
| `emitters` | string[] | Lista de Systems que emiten. Validador comprueba que existan en el manifest de módulos. |
| `subscribers` | string[] | Lista de Systems que se suscriben. Solo informativo (Verse no impone restricción). |
| `payload_fields` | object[] | Mínimo 1 campo. Si el evento es "fire-and-forget puro" → 1 campo dummy `Timestamp:int`. |

**Tipos permitidos en `payload_fields[].type`** (subset Verse-serializable + casos especiales):

| Tipo JSON | Tipo Verse generado | Notas |
|---|---|---|
| `"int"` | `int` | int64 nativo ([dev.epicgames.com — int in Verse](https://dev.epicgames.com/documentation/en-us/fortnite/int-in-verse)). Epic ha anunciado migración futura a int de tamaño arbitrario sin fecha; cuando ocurra, las suposiciones de width int64 deberán re-evaluarse. |
| `"float"` | `float` | |
| `"string"` | `string` | |
| `"logic"` | `logic` | bool de Verse |
| `"player"` | `player` | tipo nativo Verse — agente de jugador |
| `"agent"` | `agent` | supertipo de player; usar si emisor puede ser NPC |
| `"int_array"` | `[]int` | |
| `"string_array"` | `[]string` | |

**Prohibido**: structs anidados, mapas, optionals (los payloads deben ser planos). Si necesitas anidamiento real → divide en múltiples eventos o usa IDs en lugar de structs.

**Regla canónica del proyecto (Auditoría retro Bloque 1, B1.2)**: para identificar al jugador afectado por un evento, usar SIEMPRE `{"name": "Player", "type": "player"}` (o `"type": "agent"` si el actor puede ser NPC). **NUNCA** usar `{"name": "PlayerID", "type": "int"}` — la API Verse pública de `player` no expone método estable que devuelva un identificador serializable (`GetID()`/`GetName()`/`GetAccountID()` no existen en la doc oficial; ver [dev.epicgames.com — player class](https://dev.epicgames.com/documentation/en-us/fortnite/verse-api/versedotorg/simulation/player) + feature request abierta [forums — Get player name in Verse](https://forums.unrealengine.com/t/feature-request-get-player-name-in-verse/1378109)), por lo que ningún emisor puede poblar un int identificador. Como bonus, `player` es la key directa del `weak_map` de persistencia → suscriptores hacen `Persistence.LoadPlayerCore(Payload.Player)` sin lookup. Validador `01_validate_jsons.py` debe rechazar payloads que tengan campo nombrado `*ID` con `type: "int"` cuando el contexto sugiera identificador de jugador (heurística: nombre `PlayerID` exacto → exit 1).

### 42.3 Validaciones cruzadas

`01_validate_jsons.py` debe verificar:

1. `id` único en todo el catálogo.
2. `verse_struct_name` único.
3. `verse_event_name` único.
4. Cada `emitters[i]` existe en `modules_manifest.json` o es Core conocido.
5. Cada `payload_fields[i].type` está en la lista de tipos permitidos.
6. Cada `payload_fields[i].name` es PascalCase.
7. Sin duplicados de `name` dentro del mismo `payload_fields`.
8. **(Auditoría retro B1.2)** Ningún campo con `name == "PlayerID"`. Mensaje de error: `"Use {name: 'Player', type: 'player'} en lugar de {name: 'PlayerID', type: 'int'} — la API Verse pública de player no expone getter de identidad estable serializable. Ver JSON_SCHEMAS.md §42.2 + GLOSSARY.md 'Admin (player ID)'."`. Bloquea merge.

Drift entre catálogo y código real → exit 1 → no merge.

### 42.4 Política de cambios

**Añadir un evento nuevo**: solo añadir entrada al JSON. Regenerar. Los Systems que emitan/escuchen actualizan su `.verse` para usarlo.

**Cambiar payload de evento existente**:
- Añadir campo nuevo → seguro si todos los emisores se actualizan al rellenarlo.
- Renombrar campo → **rompe** todos los suscriptores. Tratamiento equivalente a renombrar weak_map (ver `EMERGENCY_ROLLBACK.md`).
- Eliminar campo → **rompe**. Marcar como `<deprecated>` mínimo 1 release antes de eliminar.

**Renombrar evento**: equivale a evento nuevo + deprecar el viejo. Coexistir 1 release. Los emisores emiten en ambos durante migración.

---

## 43. Schema: modules_manifest.json

> **Decisión cerrada (Auditoría 2 — C1)**: catálogo declarativo de Systems registrables en `ModuleRegistry`. Source of truth del Registry. Genera `Generated/ModuleRegistryConstants.verse` con un par tipado `RegisterX`/`GetX` por sistema. Detalle de la generación en `BOOTSTRAP_PIPELINE.md` §10.

**Path**: `data/architecture/modules_manifest.json`

**Por qué hace falta**: los parametric types de Verse se resuelven en compile-time ([dev.epicgames.com — Parametric Types in Verse](https://dev.epicgames.com/documentation/en-us/fortnite/parametric-types-in-verse)) — no hay lookup runtime de tipos ni `GetModule<T>()` genérico instanciable en runtime. La solución es declarar en JSON qué Systems se registran, y que Python genere getters tipados estáticos. Detalle del workaround en `MODULES_DEPENDENCY_GRAPH.md` §4.7 + `BOOTSTRAP_PIPELINE.md` §10.2.

### 43.1 Estructura

```json
{
  "_schema_version": 1,
  "_doc": "Lista de Systems registrables en ModuleRegistry. SOLO Systems Capa 2+. Los Core no van aquí.",
  "_validation": "scripts/build/01_validate_jsons.py debe pasar antes de commit.",

  "registrable_systems": [
    {
      "id": "player_stats",
      "module_name": "player_stats_module",
      "verse_path": "/<ProjectName>/Systems/Player/PlayerStats",
      "layer": 2,
      "phase": "F1",
      "_comment": "Stats base del jugador. Se registra en GameManager.OnBegin."
    },
    {
      "id": "player_inventory",
      "module_name": "player_inventory_module",
      "verse_path": "/<ProjectName>/Systems/Player/PlayerInventory",
      "layer": 2,
      "phase": "F1"
    },
    {
      "id": "currency_manager",
      "module_name": "currency_manager_module",
      "verse_path": "/<ProjectName>/Systems/Economy/CurrencyManager",
      "layer": 2,
      "phase": "F3"
    }
  ]
}
```

### 43.2 Reglas del schema

| Campo | Tipo | Reglas |
|---|---|---|
| `id` | string | snake_case único, inmutable. Usado para nombrar getter (`GetPlayerStats`). |
| `module_name` | string | `<id>_module`. Tipo Verse del Systems. Debe coincidir con declaración en `.verse` real. |
| `verse_path` | string | Path Verse completo. Validador `dependency_cycle_check.py` lo verifica. |
| `layer` | int | 2, 3 o 4. Capa 0/1/5 prohibido (Core/Generated/Devices no se registran). |
| `phase` | string | F1–F5. Sirve para que el generador comente en qué fase aparece. |
| `_comment` | string | OPCIONAL. Documentación opcional del entry. |

### 43.3 Validaciones cruzadas

`01_validate_jsons.py` debe verificar:

1. `id` único en todo el manifest.
2. `module_name` único.
3. `verse_path` apunta a un `.verse` que existe (chequeo cross-FS).
4. `module_name` declarado en el manifest aparece en el `.verse` correspondiente como `<id>_module := class<concrete>:`. El specifier `<concrete>` es obligatorio porque el Systems se instancia con archetype `<id>_module{}` en `OnBegin` del device antes de registrarse en el Registry. Coherente con el patrón canónico Core (Auditoría 3 — H3.1). Detalle en `MODULES_DEPENDENCY_GRAPH.md` §2.1.
5. Si `layer == 2`, `phase` debe ser F1 o F2.
6. Si `layer == 3`, `phase` debe ser F1, F2 o F3.
7. Si `layer == 4`, `phase` puede ser F2–F5.
8. **NO se permite registrar Core** (Logger, EventBus, TimeSync, PersistenceLayer, BigNumbers, AdminCommands) — son singletons top-level estáticos accedidos por `using {}` directo. Validador rechaza si aparecen en el manifest.

Drift entre manifest y código real → exit 1 → no merge.

### 43.4 Política de cambios

**Añadir un sistema nuevo**: añadir entrada al JSON. Regenerar. El Systems debe llamar `Registry.Register<NombreSistema>(SelfModule)` en su `Init()`.

**Cambiar `id` de un sistema** (rename): equivale a sistema nuevo + deprecar el viejo. Mantener ambos getters en el código generado durante 1 release.

**Eliminar un sistema**: remover del manifest tras confirmar que ningún consumidor llama a `Registry.GetX()` de él.

**Cambiar `layer` o `phase`**: solo afecta a la documentación generada, no rompe nada en runtime.

---

## 44. Schema: player_stats_base.json

> **Decisión cerrada (Auditoría 2 — m2)**: schema declarativo de los stats base del jugador. Source of truth de los valores iniciales y las fórmulas de crecimiento por nivel para los 6 stats persistidos en PlayerCore (`HP_Max`, `Stamina_Max`, `Strength`, `Speed`, `Intelligence`, `Luck`). Genera `Generated/PlayerStats_Generated.verse` (constantes inmutables consumidas por SYS-001 PlayerStats).

**Path**: `data/progression/player_stats_base.json`
**Sistema**: SYS-001 Player Stats
**Sprint**: SPR-011 (schema + JSON), SPR-012 (consumo Verse)

### 44.1 Schema

```
{
  base_values: BaseStats [REQUIRED] — valores nivel 1
  growth: map<string, GrowthCurve> [REQUIRED] — una entrada por stat
  caps: map<string, int> [OPTIONAL] — cap por stat (overrideable)
}

BaseStats := {
  HP_Max: int [REQUIRED] [1..]
  Stamina_Max: int [REQUIRED] [1..]
  Strength: int [REQUIRED] [1..]
  Speed: int [REQUIRED] [1..]
  Intelligence: int [REQUIRED] [1..]
  Luck: int [REQUIRED] [1..]
}

GrowthCurve := {
  formula: enum<linear, exponential, polynomial, custom> [REQUIRED]
  per_level: float [REQUIRED] — valor sumado/multiplicado por nivel (depende de formula)
  exponent: float [OPTIONAL] — para exponential: stat = base + per_level × level^exponent
  polynomial_coefficients: []float [OPTIONAL] — para polynomial
  custom_levels: map<int, int> [OPTIONAL] — overrides específicos por nivel
}
```

### 44.2 Ejemplo

```json
{
  "base_values": {
    "HP_Max": 100,
    "Stamina_Max": 100,
    "Strength": 10,
    "Speed": 10,
    "Intelligence": 10,
    "Luck": 10
  },
  "growth": {
    "HP_Max":      {"formula": "linear",      "per_level": 10},
    "Stamina_Max": {"formula": "linear",      "per_level": 5},
    "Strength":    {"formula": "polynomial",  "per_level": 1, "polynomial_coefficients": [1.0, 0.5, 0.05]},
    "Speed":       {"formula": "linear",      "per_level": 0.5},
    "Intelligence":{"formula": "linear",      "per_level": 1},
    "Luck":        {"formula": "linear",      "per_level": 0.2}
  },
  "caps": {
    "Speed": 100,
    "Luck": 200
  }
}
```

### 44.3 Validaciones

- ✅ Las 6 keys de `base_values` (HP_Max, Stamina_Max, Strength, Speed, Intelligence, Luck) son REQUIRED y exhaustivas — ni más ni menos.
- ✅ `growth` debe tener exactamente las mismas 6 keys que `base_values`.
- ✅ Si `formula == "exponential"`, `exponent` REQUIRED.
- ✅ Si `formula == "polynomial"`, `polynomial_coefficients` REQUIRED (length ≥ 1).
- ✅ Stats crecen monótonamente (validador comprueba primer y último nivel del rango aplicable).
- ✅ `caps[stat]` (si existe) debe ser ≥ valor del stat al `max_level` del jugador (lookup desde `xp_curves.json:player_xp_curve.max_level`). Si no, warning.
- ✅ **Regla de redondeo (decisión cerrada Auditoría 3 — H2.3)**: el cálculo `growth_at_level` produce `float` (porque `per_level: float` admite valores como `0.5` o `0.2` en Speed/Luck), pero los 6 stats persistidos en `PlayerCore` son `int`. El stat persistido se computa siempre como `Floor(base + growth_at_level)` — truncamiento, NO redondeo bancario ni `Round()`. Razones: (1) determinista en cliente y servidor (mismo resultado bit-a-bit), (2) monotónica (stat[level=N+1] ≥ stat[level=N] siempre), (3) imposible "saltar" un valor por redondeo upward, (4) coste mínimo (1 instrucción Verse), (5) coherente con el patrón ya usado en BALANCE para `XP curve` y `cost_per_rank`. Aplicar `Floor()` **solo al persistir / exponer** — los cálculos intermedios (multipliers de equipment, flat_bonuses de skills) se hacen en `float` para preservar precisión y se truncan únicamente al escribir en `PlayerCore.<Stat>`.

### 44.4 Coherencia cross-doc

- Los 6 stats declarados aquí **deben coincidir exactamente** con los campos `HP_Max:int`, `Stamina_Max:int`, `Strength:int`, `Speed:int`, `Intelligence:int`, `Luck:int` de `PlayerCore` en `PERSISTENCE_MAP.md` §3.1. Cambio aquí ↔ cambio allí + Schema Version bump.
- Cualquier modificador de stat (skill trees, equipment, buffs) opera **encima** de estos valores base. La fórmula canónica es:

  ```
  # Cálculo intermedio (todo en float — preserva precisión):
  effective_stat_float = (base + growth_at_level) × multipliers + flat_bonuses

  # Persistencia / exposición a UI / runtime checks (truncado a int):
  PlayerCore.<Stat> = Floor(effective_stat_float)
  ```

  Detalle de `multipliers` y `flat_bonuses` por skill/equipment/buff en `BALANCE_FORMULAS.md`. La regla `Floor()` está documentada en §44.3.
- **Caps interaction**: si `caps[stat]` existe, se aplica DESPUÉS del `Floor()`: `final = Min(Floor(effective_stat_float), caps[stat])`. Esto evita perder margen útil por redondeo previo al cap.

### 44.5 Política de cambios

- **Añadir un stat nuevo** (séptimo): rompe PlayerCore schema → bump de Schema Version + entrada CHANGELOG `Persistence`. Cambio coordinado en `PERSISTENCE_MAP.md` §3.1.
- **Cambiar `base_values`**: solo afecta a jugadores nuevos que arrancan tras el cambio. Jugadores existentes mantienen valores en su PlayerCore (no se recomputa). Si se quiere recomputar, requiere migración deliberada.
- **Cambiar `growth`**: aplica retroactivamente al recalcular stats efectivos en cada level up futuro. Stats persistidos pueden quedar fuera de curva temporalmente.

---

## 45. Validación cruzada (referential integrity)

> **El validador `01_validate_jsons.py` debe implementar TODAS estas comprobaciones cross-file.**

### 45.1 Tabla de referencias

| Campo | Apunta a |
|---|---|
| `companion.evolution_chain[i]` | `companions_base.json:companions[].id` |
| `companion.obtainable_from.boss_drops[i]` | `world/bosses.json:bosses[].id` |
| `companion.obtainable_from.battle_pass.season` | `battle_pass_seasons/season_NN.json:season_id` |
| `equipment.set_id` | `sets.json:sets[].id` |
| `equipment.slot` | `equipment_slots.json:slots[].name` |
| `quest.prerequisites[i]` | `quests/*.json:quests[].id` |
| `quest.target_id` (según type) | items/companions/zones/etc. |
| `shop_item.item_ref` | items, companions, consumables, lootboxes |
| `shop_item.category_id` | `shop.json:shop_categories[].id` |
| `vbucks_offer.rewards[].reward_id` | items/companions |
| `lootbox.pool[i]` | items/companions |
| `pity_rule.alma_type + rarity_target` | combinación válida en `lootboxes.json:drop_rates` |
| `base_upgrade.prerequisites[i]` | `base_upgrades.json:upgrades[].id` |
| `base_upgrade.required_base_level[t]` | rango razonable de `base_levels.json` |
| `generator.upgrade_id` | `base_upgrades.json:upgrades[].id` |
| `code.rewards[].reward_id` | items/companions |
| `bp_level_reward.reward_id` | items/companions |
| `achievement.criteria.target_id` | según `criteria.type` |
| `zone_gate.required_quests_completed[i]` | `quests/*.json:quests[].id` |
| `zone_gate.required_boss_defeated` | `world/bosses.json:bosses[].id` |
| `theme.exclusive_companions[i]` | `companions_base.json:companions[].id` |
| `display_name_key`, `description_key` (cualquiera) | `localization_keys.json:keys` |

### 42.2 Reglas de integridad global

1. **No huérfanos**: cualquier ID referenciado debe existir.
2. **No duplicados de ID**: dentro de su namespace.
3. **Sin ciclos en DAGs**: prerequisites de quests, prerequisites de skills, prerequisites de upgrades, evolution_chains.
4. **Universal Obtainability (SYS-038)**: cada companion/equipment "ganable" tiene al menos UNA `obtainable_from` source.
5. **Tradabilidad consistente**: items con `vbucks_only: true` o pagados solo en V-Bucks → `tradable: false`.
6. **Localización completa**: cada `*_key` referenciada existe en `localization_keys.json` con al menos `en` y `es`.
7. **Drop rates suman 1.0**: en cada lootbox y en cualquier distribución probabilística.
8. **Schema versions consistentes**: si un archivo cambia su schema, su `_schema_version` se incrementa.

---

## 46. Cómo extender este documento

### 46.1 Cuando añades un sistema nuevo

1. **Identifica el SYS-xxx** en CONCEPT.md sección 10.
2. **Decide la ruta del JSON** según estructura en CONCEPT.md sección 11.1.
3. **Añade nueva sección aquí** siguiendo el formato de las anteriores.
4. **Actualiza el índice** (sección 0).
5. **Añade reglas de validación cruzada** en sección 42.1 si aplica.
6. **Actualiza `01_validate_jsons.py`** con las nuevas validaciones.

### 46.2 Cuando modificas un schema existente

1. **Incrementa `_schema_version`** en el JSON afectado.
2. **Marca campos deprecados** con `_deprecated: true` en lugar de borrarlos.
3. **Actualiza este documento** indicando el cambio.
4. **Crea sprint de migración** si rompe compatibilidad con persistencia.

### 46.3 Plantilla de nueva sección

```markdown
## NN. Schema: nombre_archivo.json

**Ubicación**: `data/categoria/nombre_archivo.json`
**Sistema**: SYS-XXX

### NN.1 Schema

\`\`\`
{
  campo1: tipo [REQUIRED|OPTIONAL] [rango] — descripción
  ...
}
\`\`\`

### NN.2 Validaciones

- ✅ Validación 1
- ✅ Validación 2

### NN.3 Ejemplo válido

\`\`\`json
{ ... }
\`\`\`
```

---

## 📌 Resumen ejecutivo

```
🎯 ESTE DOCUMENTO ES LA FUENTE DE VERDAD de schemas JSON.

🔑 REGLAS DE ORO:
   1. IDs nunca se renumeran ni renombran tras publish.
   2. Localización: todo display_name_key apunta a localization_keys.json.
   3. Tradabilidad: V-Bucks → tradable: false. Sin excepciones.
   4. Drop rates: suman 1.0 ±0.001.
   5. _schema_version se incrementa en cada cambio de schema.

📋 ANTES DE CREAR/EDITAR UN JSON:
   1. Lee la sección de su schema aquí.
   2. Verifica integridad cruzada (sección 42).
   3. Añade _comment_* keys para documentar inline.
   4. Ejecuta 01_validate_jsons.py.

⚠️ SI EL VALIDADOR FALLA:
   - Lee el error completo.
   - Si la regla está aquí pero NO en validate_jsons.py → añadir a script.
   - Si la regla NO está aquí → es decisión nueva, escalar a Opus.
```

---

**Fin del documento.**

> Este documento se actualiza cada vez que se añade un sistema o cambia un schema.
> **Cualquier IA que toque JSONs DEBE consultar este doc antes.**
