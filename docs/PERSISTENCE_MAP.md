# 💾 PERSISTENCE_MAP — Diccionario de los 4 weak_maps

> **⚠️ DOCUMENTO CRÍTICO. Leer ANTES de tocar cualquier estructura persistente.**
>
> En UEFN, si te pasas de los **128 KB por persistable** o si intentas **cambiar el nombre/tipo** de una variable en código ya publicado, **corrompes los datos de todos los jugadores** y Epic puede bloquear tu actualización. Este espacio es **finito y sagrado**.

> **Fuentes oficiales canónicas** (consultadas para este doc):
> - Anuncio Epic 8/8/2025 — límite 2→4 weak_maps + nuevo patrón de versionado: https://forums.unrealengine.com/t/limit-on-number-of-verse-persistent-weak-maps-increased/2635179
> - Doc Epic — Constants and Variables in Verse (límite 128 KB): https://dev.epicgames.com/documentation/en-us/fortnite/constants-and-variables-in-verse
> - Doc Epic — Struct in Verse (immutabilidad post-publish): https://dev.epicgames.com/documentation/en-us/fortnite/struct-in-verse
> - Doc Epic — Option in Verse (option es persistable si su valor lo es): https://dev.epicgames.com/documentation/en-us/fortnite/option-in-verse
> - Doc Epic — Verse Persistence Best Practices: https://dev.epicgames.com/documentation/en-us/fortnite/verse-persistence-best-practices

---

## 🧭 Índice

1. [Reglas inquebrantables de persistencia](#1-reglas-inquebrantables-de-persistencia)
2. [Distribución de los 4 weak_maps](#2-distribución-de-los-4-weak_maps)
3. [Schema completo: PlayerCore](#3-schema-completo-playercore)
4. [Schema completo: PlayerInventory](#4-schema-completo-playerinventory)
5. [Schema completo: PlayerProgress](#5-schema-completo-playerprogress)
6. [Schema completo: PlayerEconomy](#6-schema-completo-playereconomy)
7. [Cálculo worst-case por weak_map](#7-cálculo-worst-case-por-weak_map)
8. [Protocolo de migración (option-version pattern)](#8-protocolo-de-migración-option-version-pattern)
9. [Tamaño de tipos en Verse Persistence](#9-tamaño-de-tipos-en-verse-persistence)
10. [Validación defensiva al cargar](#10-validación-defensiva-al-cargar)
11. [Checklist antes de publicar update](#11-checklist-antes-de-publicar-update)
12. [Cuándo NO añadir un weak_map adicional](#12-cuándo-no-añadir-un-weak_map-adicional)

---

## 1. Reglas inquebrantables de persistencia

### Las 5 reglas que NUNCA se rompen

1. **Máximo 4 weak_maps persistentes por isla**. Punto final. (Epic anuncio 8/8/2025: subieron de 2 a 4 — son el techo absoluto, no se pueden añadir más).
2. **Máximo 128 KB por persistable**. Si te pasas, Epic bloquea publish. (Doc oficial Epic — `Constants and Variables in Verse`. Nota: Flak/Epic confirmó en agosto 2025 que el cap subió, pero **no publicaron el nuevo número**; diseñamos contra 128 KB documentados).
3. **Para evolucionar el schema, usa el patrón option-version**, no el patrón "añadir campos + Version int". Cada versión es un struct independiente envuelto en un campo `option`. Ver §8. (Recomendación oficial Epic, 8/8/2025: el patrón viejo "tends to accumulate legacy data that may never be referenced again").
4. **Backwards compatibility OBLIGATORIA** entre versiones publicadas. Epic enforza esto al publicar. Structs persistables son **inmutables tras publish** (doc oficial: "You cannot alter a persistable struct once you've published your island").
5. **No mover archivos `.verse` con persistencia entre carpetas** sin pasar por el protocolo de migración (sección 8).

### Lo que pasa si rompes alguna

| Violación | Consecuencia |
|---|---|
| 5º weak_map | No compila. UEFN te bloquea. |
| 128 KB+ en runtime | Crash silencioso al guardar. Datos perdidos. |
| Renombrar campo de struct publicado | Epic bloquea publish del update. No puedes lanzar. |
| Eliminar campo de struct publicado | Epic bloquea publish del update. No puedes lanzar. |
| Cambiar tipo (int → float) en campo publicado | Epic bloquea publish. |
| Mover archivo .verse con persistencia | Datos de jugadores se pierden silenciosamente. |

---

## 2. Distribución de los 4 weak_maps

```
┌─────────────────────────────────────────────────────────────────┐
│ weak_map #1: PlayerCore         ~568 B típico, ~1.05 KB worst  │
│   gold, gemas, XP, level, rebirth, skill points, stats          │
├─────────────────────────────────────────────────────────────────┤
│ weak_map #2: PlayerInventory    ~3.5 KB típico, ~10.2 KB worst │
│   inventario, equipo, ayudantes equipados, Dex                  │
├─────────────────────────────────────────────────────────────────┤
│ weak_map #3: PlayerProgress     ~700 B típico, ~1.78 KB worst  │
│   quests, achievements, BP progress, daily login, codes         │
├─────────────────────────────────────────────────────────────────┤
│ weak_map #4: PlayerEconomy      ~400 B típico, ~1 KB worst     │
│   compras V-Bucks, trade history, base upgrades, pity counters  │
└─────────────────────────────────────────────────────────────────┘
                  TOTAL: ~5.2 KB típico / ~14 KB worst
```

> **Fuente canónica de tamaños**: §7.1 (resumen consolidado). Esta vista §2 refleja los mismos números — si hay drift, **§7.1 es el source of truth**.

**Margen de seguridad real**: ~5.2 KB típicos vs 512 KB total disponible (4 × 128 KB) → **>98% libre en uso normal**.

**Worst-case real**: ~14 KB vs 512 KB → **>97% libre incluso con jugador 100% completista**. Margen abismal — heredado de optimizaciones aplicadas (bitfields para achievements/BP/daily, int IDs en lugar de strings, stats calculadas no almacenadas, sparse representation de SkillPoints_Spent post-C4).

### Por qué esta distribución y no otra

- **Acoplamiento por frecuencia de escritura**: gold/gemas/xp se escriben a cada rato → todo en `PlayerCore`. Inventario cambia menos frecuentemente. Quests cambian a otro ritmo.
- **Acoplamiento por tipo de gameplay**: `PlayerEconomy` separado porque mezcla compras V-Bucks (sensible) con base upgrades (estructura grande, rara escritura).
- **Aislamiento de riesgo**: si una corrupción ocurre, afecta a 1 weak_map, no a todo.

### Por qué NO reservar buckets vacíos

El anuncio oficial Epic 8/8/2025 justifica el subir el límite así: *"If you've been running into the data cap on a single weak_map, an option is to split your data across multiple weak_maps."* Los 4 buckets son para **partir datos reales**, no para reservar capacidad futura. Reservar buckets vacíos no aporta nada porque (a) cada bucket existente tiene >90% libre, y (b) los 4 son el techo absoluto. Detalle completo en §12.

---

## 3. Schema completo: PlayerCore

> **Ubicación**: `Content/Verse/Core/PersistenceLayer.verse`
> **Frecuencia de escritura**: alta (cada minuto durante gameplay activo)

> **Patrón canónico de declaración (oficial Epic, 8/8/2025)**: los 4 buckets root persistentes se declaran como `<NombreBucket> := class<final><persistable>:` con campos `option` por versión. El specifier `<final>` es **obligatorio** porque las clases persistables no pueden tener subclases ([dev.epicgames.com — Class in Verse](https://dev.epicgames.com/documentation/en-us/fortnite/class-in-verse)). Las entries internas (SkillPointEntry, ItemEntry, CompanionEntry, BaseUpgradeEntry, etc.) se declaran como `struct<persistable>` — los structs no soportan herencia, por lo que `<final>` no aplica ni es válido en ellas.

### 3.1 Estructura raíz (option-version pattern)

```verse
# Wrapper raíz del bucket. Contiene una option por cada versión publicada.
# Solo UNA option está poblada en cada momento (tras migración).
PlayerCore := class<final><persistable>:
    V1:?PlayerCore_V1 = false  # esquema inicial (publicado en F0)
    # V2:?PlayerCore_V2 = false  # se añade SOLO cuando hay que migrar
```

### 3.2 Estructura de versión activa: PlayerCore_V1

```verse
# Entry de un skill aprendido. (Auditoría 2 — C4): un entry por cada skill con rank ≥ 1.
# Skills no aprendidos NO aparecen en el array (rank implícito = 0).
SkillPointEntry := struct<persistable>:
    SkillID:int = 0                  # 4 B   (id global del skill, ver schema en `JSON_SCHEMAS.md` §25.2)
    Rank:int = 0                     # 4 B   (rank actual, 1..max_rank del skill)

PlayerCore_V1 := class<final><persistable>:
    # === CORE CURRENCIES ===
    Gold:int = 0                     # 8 B   (int64 nativo, hasta 9.2 quintillones — uso BigNumbers para mayores)
    Gold_Overflow:string = ""        # ~16 B (string para overflow tipo "1.5e21" cuando supera int64)
    Gems:int = 0                     # 8 B   (gemas, premium currency jugable)

    # === CORE PROGRESSION ===
    XP:int = 0                       # 8 B   (XP del personaje, sube niveles)
    Level:int = 1                    # 4 B   (nivel actual)
    SkillPoints_Available:int = 0    # 4 B   (puntos sin gastar)
    SkillPoints_Spent:[]SkillPointEntry = array{} # 4 B header + 8 B × N entries (1 entry por skill con rank≥1)

    # === REBIRTH ===
    RebirthCount:int = 0             # 4 B   (cuántos rebirths ha hecho)
    Rebirth_PermBonuses:[]int = array{} # ~50 B (array de IDs de bonuses permanentes ganados)

    # === BASE LEVEL (eje permanente, nunca se resetea) ===
    BaseLevel:int = 1                # 4 B
    BaseXP:int = 0                   # 8 B

    # === PLAYER STATS (calculadas pero cacheadas) ===
    HP_Max:int = 100                 # 4 B
    Stamina_Max:int = 100            # 4 B
    Strength:int = 10                # 4 B
    Speed:int = 10                   # 4 B
    Intelligence:int = 10            # 4 B
    Luck:int = 10                    # 4 B

    # === DEATH PROTECTION ===
    DeathProtection_ExpiresAt:int = 0 # 8 B (epoch UTC; 0 = no tiene; -1 = permanente)

    # === LAST SESSION ===
    LastLogout_Epoch:int = 0         # 8 B (para offline production)
    LastLogin_Epoch:int = 0          # 8 B
    TotalPlayTime_Seconds:int = 0    # 8 B (tiempo total acumulado)
```

> **Nota**: el campo `Version:int` que aparecía en revisiones anteriores de este doc **se elimina**. La versión está implícita en qué `option` está poblada (`V1`, `V2`, etc.). Esto evita acumular legacy data — recomendación oficial Epic 8/8/2025.

### 3.3 Tamaño calculado

> **Notas C4 (Auditoría 2)**: `SkillPoints_Spent` cambió de `[]int` a `[]SkillPointEntry`. Cada entry son 8 B (4 SkillID + 4 Rank). Worst-case asumido: ~100 skills definidos en `skill_trees.json` con jugador end-game que ha invertido en ~80 → 80 × 8 B = 640 B. Para jugador típico mid-game: ~30 skills aprendidos → 30 × 8 B = 240 B.

| Concepto | Bytes |
|---|---|
| Wrapper option header (V1 poblada) | ~12 |
| Currencies (Gold + Overflow + Gems) | 32 |
| Progression (XP, Level, SkillPoints_Available) | 16 |
| Progression (SkillPoints_Spent typical 30 entries × 8 B + 4 B header) | 244 |
| Rebirth (Count + PermBonuses worst-case 50 entradas × 4 B) | 204 |
| Base (Level + XP) | 12 |
| Stats (6 ints) | 24 |
| Death Protection | 8 |
| Last Session (3 timestamps) | 24 |
| **Total typical** (30 skills aprendidos) | **~576 B** |
| **Total worst-case** (80 skills aprendidos, 50 perm bonuses, overflow) | **~1.06 KB** |

### 3.4 Margen de PlayerCore

- **Uso real**: ~1.06 KB worst-case (post-C4)
- **Disponible**: 128 KB = 131,072 B
- **% usado**: 0.81%
- **Conclusión**: PlayerCore sigue con muchísimo margen. C4 incrementa uso típico de 340 B → 576 B (+69%), worst-case de 600 B → 1.06 KB (+76%), pero el bucket está infrautilizado (>99%). Sin riesgo.

---

## 4. Schema completo: PlayerInventory

> **Ubicación**: `Content/Verse/Core/PersistenceLayer.verse`
> **Frecuencia de escritura**: media (cada loot, cada compra, cada equip)
> **⚠️ ESTE ES EL WEAK_MAP MÁS PESADO. Vigilar siempre.**

### 4.1 Estructura raíz (option-version pattern)

```verse
PlayerInventory := class<final><persistable>:
    V1:?PlayerInventory_V1 = false
    # V2:?PlayerInventory_V2 = false  # se añade cuando haya que migrar
```

### 4.2 Estructura de versión activa: PlayerInventory_V1

```verse
ItemEntry := struct<persistable>:
    ItemID:int = 0                   # 4 B   (ID compacto, no string)
    Quantity:int = 0                 # 4 B   (cantidad o nivel para items unique)
    Variant:int = 0                  # 4 B   (0=normal, 1=oro, 2=diamante, 3=arcoiris, 4+=evento)
    Tier:int = 0                     # 4 B   (tier para equipo levellable, 0 si N/A)
    Rolls:int = 0                    # 4 B   (rerolls ya gastados, para curva exponencial)

CompanionEntry := struct<persistable>:
    CompanionID:int = 0              # 4 B
    Variant:int = 0                  # 4 B
    Level:int = 1                    # 4 B
    XP:int = 0                       # 8 B
    Evolution:int = 0                # 4 B   (etapa de evolución)
    AssignedTask:int = 0             # 4 B   (0=ninguna, 1=gather, 2=combat, etc.)
    PerSlotData:int = 0              # 4 B   (flags compactos)

DexEntry := struct<persistable>:
    CompanionID:int = 0              # 4 B
    VariantsBitfield:int = 0         # 4 B   (cada bit = 1 variante poseída; soporta 32 variantes)
    FirstSeen_Epoch:int = 0          # 8 B

EquippedItem := struct<persistable>:
    SlotID:int = 0                   # 4 B   (0-5, 6 ranuras)
    ItemID:int = 0                   # 4 B
    Variant:int = 0                  # 4 B
    Tier:int = 0                     # 4 B

PlayerInventory_V1 := class<final><persistable>:
    # === INVENTORY (items consumibles, recursos, materiales) ===
    Items:[]ItemEntry = array{}      # 24 B × N items distintos
    Items_MaxSlots:int = 50          # 4 B   (sube con base upgrades)

    # === EQUIPPED (6 ranuras de equipo invisible) ===
    Equipped:[]EquippedItem = array{} # 16 B × 6 = 96 B max

    # === COMPANIONS owned ===
    Companions:[]CompanionEntry = array{} # 32 B × N companions
    Companions_MaxSlots:int = 10     # 4 B
    Companions_Active:[]int = array{} # 4 B × hasta 5 slots activos

    # === DEX (collection book) ===
    Dex:[]DexEntry = array{}         # 16 B × N companions únicos vistos

    # === BANK (recursos guardados separados del inventario) ===
    BankItems:[]ItemEntry = array{}  # 24 B × N (más grande, sube con base)
    BankMaxSlots:int = 100           # 4 B
```

### 4.3 Tamaño calculado worst-case

**Asunción**: jugador completista que tiene de TODO.

| Concepto | Cantidad | Bytes/u | Total |
|---|---|---|---|
| Wrapper option + maxslots | — | — | 28 B |
| Items (50 slots máx) | 50 entries | 24 | 1,200 B |
| Equipped (6 ranuras) | 6 | 16 | 96 B |
| Companions (digamos 50 capturas distintas en backpack) | 50 | 32 | 1,600 B |
| Companions Active (5 max) | 5 | 4 | 20 B |
| **Dex (300 entries posibles)** | **300** | **16** | **4,800 B** |
| Bank (100 slots) | 100 | 24 | 2,400 B |
| **Total typical** (jugador medio: ~30 items, 20 companions, 100 Dex, 50 bank) | | | **~3,512 B** |
| **Total worst-case** (completista absoluto) | | | **~10,212 B** |

### 4.4 Margen de PlayerInventory

- **Uso typical**: ~3.5 KB
- **Uso worst-case**: ~10.2 KB
- **Disponible**: 128 KB
- **% usado worst**: 7.9%
- **Conclusión**: aún con 300 entries de Dex completas y máximo equipo, queda 92% libre. Margen para crecimiento futuro.

### 4.5 Optimizaciones aplicadas (importantes)

1. **Bitfield para variantes en Dex**: en vez de un array de booleans (1 B cada uno = 4 B por variante × 32 variantes = 128 B), usamos 1 int de 32 bits = **4 B total**. Ahorro 32×.
2. **IDs como int, no string**: `ItemID:int` en vez de `ItemID:string`. Strings persistentes ocupan ~16 B base + length. Ints son siempre 4-8 B.
3. **Stats calculadas, no almacenadas en cada item**: el daño/defensa de un item se calcula en runtime desde JSON (data layer), no se guarda. Solo guardamos qué item tiene, qué tier, qué variante.
4. **Quantity y Level mergeable**: para items consumibles `Quantity` indica cantidad. Para items unique `Quantity` se interpreta como Level. Mismo campo, doble uso.

---

## 5. Schema completo: PlayerProgress

> **Ubicación**: `Content/Verse/Core/PersistenceLayer.verse`
> **Frecuencia de escritura**: media-alta (cada quest progress, cada daily)

### 5.1 Estructura raíz (option-version pattern)

```verse
PlayerProgress := class<final><persistable>:
    V1:?PlayerProgress_V1 = false
    # V2:?PlayerProgress_V2 = false  # se añade cuando haya que migrar
```

### 5.2 Estructura de versión activa: PlayerProgress_V1

```verse
QuestProgress := struct<persistable>:
    QuestID:int = 0                  # 4 B
    State:int = 0                    # 4 B (0=available, 1=active, 2=completed, 3=claimed)
    ProgressCounter:int = 0          # 4 B
    StartedAt_Epoch:int = 0          # 8 B

PlayerProgress_V1 := class<final><persistable>:
    # === ACTIVE QUESTS ===
    ActiveQuests:[]QuestProgress = array{} # 20 B × N (max ~10 simultáneas)

    # === COMPLETED QUESTS (solo IDs, no progress) ===
    CompletedQuests:[]int = array{}  # 4 B × N

    # === DAILY/WEEKLY ===
    Daily_LastReset_Epoch:int = 0    # 8 B
    Daily_CurrentQuests:[]int = array{} # 4 B × 3
    Daily_Completed:[]int = array{}  # 4 B × 3
    Weekly_LastReset_Epoch:int = 0   # 8 B
    Weekly_CurrentQuests:[]int = array{} # 4 B × 9
    Weekly_Completed:[]int = array{} # 4 B × 9

    # === DAILY LOGIN ===
    DailyLogin_Streak:int = 0        # 4 B
    DailyLogin_LastClaim_Epoch:int = 0 # 8 B
    DailyLogin_ClaimedDays:int = 0   # 4 B (bitfield 28 días)

    # === ACHIEVEMENTS (bitfield para hasta 256 achievements) ===
    Achievements_Bitfield_A:int = 0  # 8 B (64 bits)
    Achievements_Bitfield_B:int = 0  # 8 B
    Achievements_Bitfield_C:int = 0  # 8 B
    Achievements_Bitfield_D:int = 0  # 8 B
    # → 256 achievements totales con solo 32 B

    # === BATTLE PASS (100 niveles según SYS-022 / BALANCE_FORMULAS §total_levels=100) ===
    BP_Season:int = 0                # 4 B  (qué season)
    BP_XP:int = 0                    # 8 B
    BP_Level:int = 0                 # 4 B
    BP_HasPremium:logic = false      # 1 B
    # Bitfields de claims: 3 × 64 bits = 192 niveles soportados (cap real: MAX_BP_LEVELS=100, ver BALANCE_FORMULAS §2.1).
    # Diseño "3 ints" elegido para dar margen de N seasons con BP largos sin migración futura.
    BP_FreeRewardsClaimed_A:int = 0  # 8 B  (niveles 1..64)
    BP_FreeRewardsClaimed_B:int = 0  # 8 B  (niveles 65..128)
    BP_FreeRewardsClaimed_C:int = 0  # 8 B  (niveles 129..192)
    BP_PremiumRewardsClaimed_A:int = 0 # 8 B  (niveles 1..64)
    BP_PremiumRewardsClaimed_B:int = 0 # 8 B  (niveles 65..128)
    BP_PremiumRewardsClaimed_C:int = 0 # 8 B  (niveles 129..192)

    # === CODES REDEEMED ===
    CodesRedeemed:[]int = array{}    # 4 B × N (IDs de códigos canjeados)

    # === TIME PLAYED REWARDS ===
    TimePlayed_TodayClaimed:int = 0  # 4 B (bitfield: bit por threshold reclamado hoy)
    TimePlayed_LastReset_Epoch:int = 0 # 8 B

    # === TUTORIAL ===
    Tutorial_CurrentStep:int = 0     # 4 B
    Tutorial_Completed:logic = false # 1 B
    FirstRebirth_Done:logic = false  # 1 B (gate del tutorial chain)

    # === LEADERBOARDS (SYS-047) ===
    # Best-score por stat trackeada. Cross-session se aproxima vía persistencia
    # (Epic no expone API para listar jugadores fuera de sesión actual).
    # Cada slot es un int64 → mismo valor cabe BigNumber serializado.
    # Convención: slot 0 = max rebirth, 1 = max base level, 2 = max Dex %,
    # 3 = max gold lifetime, 4..7 = reservados para event leaderboards.
    LeaderboardScore_0:int = 0       # 8 B
    LeaderboardScore_1:int = 0       # 8 B
    LeaderboardScore_2:int = 0       # 8 B
    LeaderboardScore_3:int = 0       # 8 B
    LeaderboardScore_4:int = 0       # 8 B
    LeaderboardScore_5:int = 0       # 8 B
    LeaderboardScore_6:int = 0       # 8 B
    LeaderboardScore_7:int = 0       # 8 B
    LeaderboardScore_LastUpdate_Epoch:int = 0 # 8 B
```

### 5.3 Tamaño calculado worst-case

| Concepto | Bytes |
|---|---|
| Wrapper option | ~12 |
| Active Quests (max ~10) | 200 |
| Completed Quests worst-case (200 quests totales en juego) | 800 |
| Daily/Weekly (3 + 9 quests × 4 B + completion arrays) | 100 |
| Daily Login (streak + claimed bitfield) | 16 |
| Achievements (256 con 32 B) | 32 |
| Battle Pass (season + xp + level + flags + 6 × 64-bit bitfields para 100 niveles) | 65 |
| CodesRedeemed (worst-case 100 códigos) | 400 |
| Time Played | 12 |
| Tutorial flags | 6 |
| Leaderboards (8 slots × 8 B + last-update epoch) | 72 |
| **Total typical** (~50 quests done, ~10 codes, 4 leaderboards activos) | **~784 B** |
| **Total worst-case** (200 quests, 100 codes, 8 leaderboards completista) | **~1,790 B** |

### 5.4 Margen de PlayerProgress

- **Uso worst**: ~1.78 KB
- **% usado**: 1.4%
- **Conclusión**: enorme margen. Achievement bitfields y BP bitfields son brutalmente eficientes. Leaderboards añaden 72 B fijos sin impacto.

---

## 6. Schema completo: PlayerEconomy

> **Ubicación**: `Content/Verse/Core/PersistenceLayer.verse`
> **Frecuencia de escritura**: baja-media (cada compra, cada upgrade de base, cada pull de lootbox)

### 6.1 Estructura raíz (option-version pattern)

```verse
PlayerEconomy := class<final><persistable>:
    V1:?PlayerEconomy_V1 = false
    # V2:?PlayerEconomy_V2 = false  # se añade cuando haya que migrar
```

### 6.2 Estructura de versión activa: PlayerEconomy_V1

```verse
BaseUpgradeEntry := struct<persistable>:
    UpgradeID:int = 0                # 4 B
    Tier:int = 0                     # 4 B

PityCounter := struct<persistable>:
    SoulType:int = 0                 # 4 B (qué tipo de alma)
    Rarity:int = 0                   # 4 B (qué rareza objetivo)
    PullsSinceLast:int = 0           # 4 B (counter actual)

ActiveCraft := struct<persistable>:
    RecipeID:int = 0                 # 4 B
    StartedAt_Epoch:int = 0          # 8 B
    FinishesAt_Epoch:int = 0         # 8 B

PlayerEconomy_V1 := class<final><persistable>:
    # === V-BUCKS ENTITLEMENTS DETECTED ===
    VBucks_PurchasedBundles_Bitfield_A:int = 0 # 8 B (64 founder packs/bundles)
    VBucks_PurchasedBundles_Bitfield_B:int = 0 # 8 B
    VBucks_TotalSpent_Estimated:int = 0  # 8 B (para analytics, no para gameplay)

    # === GEMS LIFETIME (analytics) ===
    Gems_LifetimeEarned:int = 0      # 8 B
    Gems_LifetimeSpent:int = 0       # 8 B

    # === BASE UPGRADES (PERMANENTES, sobreviven a rebirth) ===
    BaseUpgrades:[]BaseUpgradeEntry = array{} # 8 B × N (worst ~50 upgrades distintas)

    # === GENERADORES PASIVOS - estado ===
    Generators_State_Pool:[]int = array{} # 4 B × N (recursos acumulados sin reclamar)
    OfflineCap_LastClaim_Epoch:int = 0 # 8 B

    # === ACTIVE CRAFTS (timers) ===
    ActiveCrafts:[]ActiveCraft = array{} # 20 B × N (max ~5 simultáneos)

    # === TRADE/AUCTION HISTORY (limitado) ===
    Auction_ActiveListings:[]int = array{} # 4 B × max 5 (configurable por upgrade)
    Trade_LastTradeEpoch:int = 0     # 8 B (para cooldown)
    Trade_TodayCount:int = 0         # 4 B (rate limit)

    # === PITY COUNTERS (lootboxes) ===
    PityCounters:[]PityCounter = array{} # 12 B × N
    # 5 tipos de almas × 5 rarezas con pity = 25 entries × 12 B = 300 B max

    # === DEATH PROTECTION HISTORY ===
    DeathProtection_TotalUses:int = 0 # 4 B (analytics)
```

### 6.3 Tamaño calculado worst-case

| Concepto | Bytes |
|---|---|
| Wrapper option | ~12 |
| V-Bucks bitfields + spent | 24 |
| Gems lifetime | 16 |
| Base Upgrades (50 distintas worst) | 400 |
| Generators state | 40 |
| Active Crafts (5) | 100 |
| Auction listings (5) | 20 |
| Trade rate limits | 12 |
| Pity Counters (25 max) | 300 |
| Death Protection | 4 |
| **Total typical** | **~410 B** |
| **Total worst-case** | **~928 B** |

### 6.4 Margen de PlayerEconomy

- **Uso worst**: ~1 KB
- **% usado**: 0.7%
- **Conclusión**: enorme margen.

---

## 7. Cálculo worst-case por weak_map

### 7.1 Resumen consolidado

| weak_map | Typical | Worst-case | Disponible | % usado worst |
|---|---|---|---|---|
| PlayerCore | 576 B | 1.06 KB | 128 KB | **0.81%** |
| PlayerInventory | 3.5 KB | 10.2 KB | 128 KB | **7.9%** |
| PlayerProgress | 784 B | 1.79 KB | 128 KB | **1.4%** |
| PlayerEconomy | 410 B | 0.93 KB | 128 KB | **0.7%** |
| **TOTAL** | **~5.3 KB** | **~14 KB** | **512 KB** | **2.7%** |

> Diferencias mínimas (+8–16 B por bucket) frente a tablas de revisiones anteriores: la migración a option-version añade el header de la `option` raíz en cada bucket. Impacto despreciable.

### 7.2 Conclusiones críticas

1. **Vamos extremadamente holgados** en todos los weak_maps. Tenemos margen para 5-10x crecimiento sin tocar arquitectura.
2. **PlayerInventory es el cuello de botella futuro** si crecemos: dex de 300 entries × 16 B = 4.8 KB es el item más pesado. Si llegamos a 1000 entries, sigue siendo solo 16 KB.
3. **No hay riesgo real de superar 128 KB** con estas estructuras.
4. **Usar bitfields** ha sido clave: achievements, BP rewards, daily login son enormemente compactos así.

### 7.3 Worst-case extremo del Dex (SYS-015)

> Tu pregunta original: "300 entradas del Dex"

**Análisis**:

| Aproximación | Bytes/entrada | Total 300 entries |
|---|---|---|
| **Naive** (string ID + booleans por variante + timestamps) | ~80 B | 24,000 B (24 KB) |
| **Optimizado nuestro** (int ID + bitfield + 1 timestamp) | 16 B | 4,800 B (4.8 KB) |
| **Hyper-optimizado** (solo bitfield 32 bits per companion, sin timestamp) | 8 B | 2,400 B (2.4 KB) |

Hemos elegido el **optimizado**, que da margen para 8000 entries del Dex en 128 KB. Suficiente para 27 mapas distintos con 300 entradas cada uno → **mucho más de lo que vamos a hacer en años**.

### 7.4 Regla canónica: bitmasking obligatorio para flags booleanos

> **Cualquier campo persistente que represente un conjunto de N booleanos DEBE empaquetarse en bitfield(s) de int64.**
> Esta regla aplica desde el día 1 a TODO sistema que persista flags. Es la razón principal por la que vamos extremadamente holgados.

#### Cuándo aplicar

Si un sistema necesita persistir **"cuáles de N entidades el jugador ha hecho/visto/conseguido/poseído"**, usar bitfield siempre que `N <= 1024` aproximadamente.

#### Aritmética de capacidad

| Bits por int64 | N booleanos por int | Bytes |
|---|---|---|
| 64 | 64 flags | 8 B |
| 128 (2 ints) | 128 flags | 16 B |
| 192 (3 ints) | 192 flags | 24 B |
| 256 (4 ints) | 256 flags | 32 B |
| 512 (8 ints) | 512 flags | 64 B |

**Comparativa con array naive** (1 byte por bool):
- 256 achievements naive = 256 B → bitfield = **32 B** (8× ahorro).
- 100 niveles BP naive = 100 B → bitfield = **16 B** (6× ahorro, pero soporta hasta 192 niveles con 24 B).
- 320 companions naive = 320 B → bitfield = **40 B** (8× ahorro).

#### Aplicaciones canónicas en el proyecto

| Sistema | Campo | Tamaño con bitfield |
|---|---|---|
| SYS-021 Achievements | `Achievements_Bitfield_A/B/C/D` (4 ints) | 32 B para 256 achievements |
| SYS-022 Battle Pass | `BP_FreeRewardsClaimed_A/B/C` + premium (6 ints) | 48 B para 192 niveles |
| SYS-040 Daily Login | `DailyLogin_ClaimedDays` (1 int) | 4 B para 28 días |
| SYS-015 Dex variants | `DexEntry.VariantsBitfield` (1 int por entry) | 4 B para 32 variantes por entry |
| SYS-031 V-Bucks | `VBucks_PurchasedBundles_Bitfield_A/B` (2 ints) | 16 B para 128 bundles |
| SYS-041 Time Played | `TimePlayed_TodayClaimed` (1 int) | 4 B para 64 thresholds diarios |

#### Operaciones obligatorias (helper functions)

Cada bitfield debe tener helpers en Verse para evitar errores de bit shifting manual:

```verse
# Idiomas Verse - patrón canónico (a definir en Core/PersistenceLayer.verse o similar)

SetBit<public>(Bitfield:int, BitIndex:int):int =
    Bitfield.BitwiseOr(1.LeftShift(BitIndex))

ClearBit<public>(Bitfield:int, BitIndex:int):int =
    Bitfield.BitwiseAnd(1.LeftShift(BitIndex).BitwiseNot())

IsBitSet<public>(Bitfield:int, BitIndex:int):logic =
    Bitfield.BitwiseAnd(1.LeftShift(BitIndex)) <> 0

CountSetBits<public>(Bitfield:int):int =
    # popcount — útil para "% completion" del Dex/Achievements
    ...
```

#### Cuándo NO usar bitfield

- **N grande con datos ricos por entrada** (no solo bool): usar array de structs (caso `Companions:[]CompanionEntry` que necesita level, XP, evolution, etc.).
- **N variable y desconocido en compile-time** (caso `CodesRedeemed:[]int` — el jugador podría redimir cualquier subset de un pool de N códigos): usar array de IDs.
- **N pequeño (≤4 flags)**: cuesta más documentar el bitfield que usar 4 logic individuales (caso de `Tutorial_Completed:logic`, `BP_HasPremium:logic`).

#### Anti-patrón a evitar

❌ **Persistir array de bool por entry** cuando solo hay flag binario:
```verse
DexSeen:[]logic = array{}    # 1 B × 300 = 300 B desperdiciados
```

✅ **Bitfield empaquetado**:
```verse
DexSeen_Bitfield_A:int = 0   # bits 0..63
DexSeen_Bitfield_B:int = 0   # bits 64..127
DexSeen_Bitfield_C:int = 0   # bits 128..191
DexSeen_Bitfield_D:int = 0   # bits 192..255
DexSeen_Bitfield_E:int = 0   # bits 256..319
# Total: 40 B para 320 flags
```

> ⚠️ **Si SPR-008 (PersistenceLayer) o sprints posteriores omiten esta regla**, el validador de tamaño (`scripts/build/06_check_memory_budget.py`, SPR-136) debe alertar cuando un weak_map use >50% de su cap. **Threshold defensivo, no técnico**: con la regla aplicada nunca pasamos del 10%.

---

## 8. Protocolo de migración (option-version pattern)

> **Patrón oficial Epic, recomendado desde 8/8/2025.**
> Reemplaza al patrón viejo "Version:int + añadir campos al mismo struct".
> Razón oficial: *"the previously suggested approach of keeping a version field and adding new fields over time tends to accumulate legacy data that may never be referenced again. The option-field pattern avoids that."* — anuncio Epic 8/8/2025.

### 8.1 Filosofía

> **Cada versión del schema vive en su propio struct independiente.**
> **El bucket raíz contiene una option por cada versión publicada.**
> **Tras migrar todos los jugadores a Vn, se pone V(n-1) = false y deja de serializarse.**
> **Nunca se renombra. Nunca se elimina. Nunca se cambia tipo dentro de una versión publicada.**

### 8.2 Estructura del patrón

Cada bucket raíz tiene esta forma:

```verse
PlayerCore := class<final><persistable>:
    V1:?PlayerCore_V1 = false    # versión inicial, publicada en F0
    V2:?PlayerCore_V2 = false    # añadida en update X
    V3:?PlayerCore_V3 = false    # añadida en update Y
    # ... etc
```

Donde:
- `?Tipo` es la sintaxis Verse para `option(Tipo)`.
- `false` es el valor "vacío" de una option (equivalente a `none`).
- En cada momento, **solo una `Vn` está poblada**: la versión actual del jugador.

> **Por qué funciona**: `option` es persistable si su valor lo es (doc oficial Epic — `Option in Verse`). Una option vacía ocupa ~4 B; una poblada ocupa 4 B + sizeof(struct).

### 8.3 Cuándo y cómo añadir una versión nueva

**EJEMPLO**: añadir `PrestigeCount:int` a PlayerCore (era V1, pasa a V2).

**Paso 1** — Definir el nuevo struct copiando el anterior y añadiendo el campo:

```verse
PlayerCore_V2 := class<final><persistable>:
    # === todos los campos de V1 ===
    Gold:int = 0
    Gold_Overflow:string = ""
    Gems:int = 0
    XP:int = 0
    Level:int = 1
    # ... resto de campos V1 ...

    # === ADDED IN V2 ===
    PrestigeCount:int = 0
```

**Paso 2** — Añadir la option al bucket raíz, dejando V1 intacto:

```verse
PlayerCore := class<final><persistable>:
    V1:?PlayerCore_V1 = false  # ← se mantiene tal cual hasta migración completa
    V2:?PlayerCore_V2 = false  # ← AÑADIDO
```

**Paso 3** — Función de migración V1 → V2:

```verse
MigrateV1ToV2<public>(Old:PlayerCore_V1):PlayerCore_V2 =
    return PlayerCore_V2:
        Gold := Old.Gold
        Gold_Overflow := Old.Gold_Overflow
        Gems := Old.Gems
        XP := Old.XP
        Level := Old.Level
        # ... copiar resto de campos ...
        PrestigeCount := 0  # default para jugadores que vienen de V1
```

**Paso 4** — Lógica de carga: si el jugador trae V1, migrar y vaciar V1:

```verse
LoadPlayerCore(InPlayer:player)<transacts>:PlayerCore_V2 =
    if (Existing := PlayerCore_Map[InPlayer]?):
        # Caso: jugador ya en V2 (post-update)
        if (V2_Data := Existing.V2?):
            return V2_Data

        # Caso: jugador en V1 (pre-update) → migrar
        if (V1_Data := Existing.V1?):
            Migrated := MigrateV1ToV2(V1_Data)
            # Persistir como V2 y vaciar V1
            set PlayerCore_Map[InPlayer] = PlayerCore:
                V1 := false       # ← se vacía: ya no se serializa
                V2 := option{Migrated}
            return Migrated

    # Jugador completamente nuevo
    return PlayerCore_V2{}
```

### 8.4 Ventaja oficial vs. patrón viejo

| Aspecto | Patrón viejo (Version + add fields) | Patrón option-version (oficial Epic) |
|---|---|---|
| Schema crece con cada update | ✅ Sí, acumula campos legacy | ❌ No, V(n-1) se vacía tras migrar |
| Tamaño persistente tras 5 updates | crece linealmente | constante (solo Vn poblada) |
| Trazabilidad de versiones | ambigua (Version int) | explícita (qué option está poblada) |
| Permite cambiar tipo de campo | ❌ no (mismo struct) | ✅ sí (Vn+1 puede cambiar tipo) |
| Recomendado por Epic | ❌ marcado obsoleto 8/8/2025 | ✅ patrón oficial vigente |

### 8.5 Caso especial: deprecar un campo

Patrón viejo: dejar el campo y marcarlo `# DEPRECATED`. **Con option-version ya no hace falta**:

1. Define `Vn+1` SIN el campo.
2. Migra todos los jugadores a `Vn+1`.
3. Cuando el último jugador haya migrado (semanas/meses), `Vn` queda vacío en todos.
4. **NO borres el `class Vn` del código**: es parte del schema publicado. Pero ya no consume bytes.

### 8.6 Caso especial: cambiar tipo

> "Quiero cambiar `Gold:int` a `Gold:string` para soportar números enormes."

**Solución option-version**:

```verse
PlayerCore_V2 := class<final><persistable>:
    # ... campos no afectados ...
    Gold:string = ""   # ← cambió de int a string en V2
```

La función `MigrateV1ToV2` convierte int → string. Imposible con el patrón viejo, trivial con option-version.

### 8.7 Caso compuesto: BigNumber (mantener int + string overflow)

Para gold/currencies que pueden desbordar int64, podemos seguir usando el patrón existente del campo doble dentro de la misma versión:

```verse
PlayerCore_V1 := class<final><persistable>:
    Gold:int = 0
    Gold_Overflow:string = ""   # vacío salvo overflow
```

```verse
GetEffectiveGold(InCore:PlayerCore_V1):BigNumber =
    if (InCore.Gold_Overflow.Length > 0):
        return BigNumber.FromString(InCore.Gold_Overflow)
    else:
        return BigNumber.FromInt(InCore.Gold)
```

Esto es independiente del versionado: válido dentro de cualquier `Vn`.

### 8.8 Mover archivo `.verse` con persistencia

**NO HACERLO sin protocolo**. Mover el archivo cambia el path del módulo y rompe la deserialización.

Si es absolutamente necesario:

1. **Antes de mover**: hacer publish de una `Vn+1` "puente" que sea idéntica a `Vn`.
2. **Esperar a que la mayoría de jugadores entre** y se actualice (1-2 semanas).
3. **Mover el archivo** y publicar.
4. **Verificar en sesión live** que los datos no se han perdido (con cuenta de testing que tenga datos).

**Más simple**: NO mover. Decidir bien la ubicación del archivo desde el día 1.

### 8.9 Checklist de seguridad antes de publicar update

- [ ] ¿He añadido una nueva `Vn+1` en lugar de modificar `Vn`?
- [ ] ¿`Vn` queda intacto (mismos campos, mismos tipos, mismo orden)?
- [ ] ¿La función `MigrateVnToVn+1` cubre TODOS los campos viejos con default razonable para los nuevos?
- [ ] ¿`LoadPlayer*()` maneja los casos: `Vn+1` poblada, `Vn` poblada (migrar), ambas vacías (nuevo jugador)?
- [ ] ¿Se prueba en una sesión con cuenta que tenga datos `Vn`?
- [ ] ¿Tras migrar, se setea `Vn := false` en el wrapper?

---

## 9. Tamaño de tipos en Verse Persistence

### 9.1 Tipos primitivos

| Tipo | Bytes | Notas |
|---|---|---|
| `int` | 8 | Verse ints son int64 nativos |
| `float` | 8 | float64 |
| `logic` | 1 | bool |
| `string` | ~16 + length | header + UTF-8 bytes |
| `int (compactado)` | 4 | usar para IDs si están < 2^31 |
| `?T` (option vacía) | ~4 | discriminator |
| `?T` (option poblada) | 4 + sizeof(T) | discriminator + valor |

### 9.2 Estructuras

| Tipo | Bytes |
|---|---|
| `[]int` (array vacío) | ~16 |
| `[]int` (con N elementos) | 16 + 8 × N |
| `[]struct` (con N elementos) | 16 + sizeof(struct) × N |
| `tuple(int, int)` | 16 |
| `option(int)` | 12 (4 de discriminator + 8 del int) |
| `map[int]int` (vacío) | ~24 |
| `map[int]int` (con N entradas) | 24 + 16 × N |

### 9.3 Reglas de oro de tamaño

1. **Nunca uses `string` para IDs**. Usa `int`.
2. **Nunca uses `[]bool` para flags**. Usa `int` como bitfield.
3. **Nunca uses `map` si un `[]struct` ordenado lo hace**. Maps tienen overhead.
4. **Stats calculadas no se guardan**. Se computan en runtime desde data layer (JSONs).
5. **Timestamps siempre como `int` epoch**, no como struct de fecha.
6. **Versiones viejas (option-version pattern)** ocupan ~4 B cuando están vacías. No te preocupes por ellas tras migrar.

---

## 10. Validación defensiva al cargar

### 10.1 Patrón obligatorio (con option-version)

```verse
# Sintaxis validada SPR-008 con build UEFN limpio + test in-session PASS.
# Diferencias vs versión previa de este doc:
# - Sin <transacts> (Load es <computes> default — permite Logger).
# - Sin '?' tras MapName[InPlayer] (acceso weak_map propaga <decides> que el if consume).
# - var local nombrada CoreData (no Core) para evitar colisión con namespace Verse/Core.
# - set CoreData.Field = X NO funciona (structs immutable). Reasignar struct entera al final.

LoadPlayerCore<public>(InPlayer:player):PlayerCore_V1=
    var CoreData:PlayerCore_V1 = PlayerCore_V1{}
    if (Existing := PlayerCoreMap[InPlayer]):
        if (V1Data := Existing.V1?):
            set CoreData = V1Data

    # === VALIDACIONES DEFENSIVAS ===
    # Reasignación entera al final (structs immutable — err 3509 si 'set Var.Field = X')

    var SafeGold:int = CoreData.Gold
    if (SafeGold < 0):
        Logger.LogWarn("PersistenceLayer", "PlayerCore.Gold negativo, corrigiendo a 0")
        set SafeGold = 0
    if (SafeGold > MAX_REASONABLE_GOLD):
        Logger.LogWarn("PersistenceLayer", "PlayerCore.Gold excede cap, capping")
        set SafeGold = MAX_REASONABLE_GOLD

    var SafeLevel:int = CoreData.Level
    if (SafeLevel < 1):
        Logger.LogWarn("PersistenceLayer", "PlayerCore.Level menor que 1, corrigiendo")
        set SafeLevel = 1
    if (SafeLevel > MAX_LEVEL):
        Logger.LogWarn("PersistenceLayer", "PlayerCore.Level excede cap, capping")
        set SafeLevel = MAX_LEVEL

    var SafeXP:int = CoreData.XP
    if (SafeXP < 0):
        Logger.LogWarn("PersistenceLayer", "PlayerCore.XP negativo, corrigiendo a 0")
        set SafeXP = 0

    PlayerCore_V1{Gold := SafeGold, Level := SafeLevel, XP := SafeXP}

# Save (sin Logger — incompatible con <transacts>).
# 'if (set ...) {}' wrapper consume <decides> propagado por escritura weak_map (lección 15).

SavePlayerCore<public>(InPlayer:player, Data:PlayerCore_V1)<transacts>:void=
    if (set PlayerCoreMap[InPlayer] = PlayerCore{V1 := option{Data}}) {}
```

### 10.2 Por qué esto es crítico

- Un bug en código viejo puede haber dejado datos malos guardados.
- Un exploit puede haber metido valores imposibles.
- Una corrupción en serialization de Epic puede dar valores raros.
- **Sin validación defensiva, el bug se propaga para siempre**.

### 10.3 Logger en lugar de crash

**NUNCA hacer `Verse failure / panic`** por datos malos. Siempre **corregir y loggear**. El jugador no debería notar que sus datos estaban corruptos: debería ver gameplay funcional con sus datos válidos.

---

## 11. Checklist antes de publicar update

> **Pegar esto antes de cada Push Changes que toque persistencia.**

```
SCHEMA SAFETY (option-version pattern):
[ ] Si hay cambio de schema, he añadido una nueva Vn+1 (NO he modificado Vn)
[ ] Vn queda 100% intacto (mismos campos, tipos, orden, defaults)
[ ] He añadido la option `Vn+1:?TipoVn+1 = false` al bucket raíz
[ ] Existe función MigrateVnToVn+1 que cubre todos los campos
[ ] LoadPlayer*() prioriza Vn+1, hace fallback a Vn (migrar), default si nada

LEGACY (regla absoluta):
[ ] No he renombrado ningún campo dentro de un Vn ya publicado
[ ] No he eliminado ningún campo dentro de un Vn ya publicado
[ ] No he cambiado el tipo de ningún campo dentro de un Vn ya publicado
[ ] No he movido archivos .verse con persistencia

TAMAÑO:
[ ] Estimación de bytes de cada weak_map sigue dentro de 50% de margen
[ ] No he añadido strings grandes (>50 chars típicos)
[ ] No he añadido arrays sin cap razonable
[ ] He usado bitfields donde corresponde

VALIDACIÓN:
[ ] LoadPlayer*() tiene validación defensiva para campos nuevos en Vn+1
[ ] Caps razonables aplicados (MAX_GOLD, MAX_LEVEL, etc.)
[ ] Logger.Warn cuando se corrige valor inválido

TESTING:
[ ] Probado en sesión live con cuenta de testing en Vn (datos viejos)
[ ] La cuenta migra correctamente a Vn+1
[ ] Tras migración, Vn queda vacío en el wrapper
[ ] Una cuenta nueva crea directamente Vn+1
[ ] Mobile Preview sigue funcionando
```

---

## 12. Cuándo NO añadir un weak_map adicional

> **Heurística canónica para evitar agotar los 4 buckets prematuramente.**

### 12.1 El recurso escaso es el NÚMERO de buckets, no los KB

Epic subió el límite de 2→4 weak_maps el 8/8/2025 con una motivación explícita: *"If you've been running into the data cap on a single weak_map, an option is to split your data across multiple weak_maps."*

Es decir, los 4 buckets son para **partir datos cuando excedan 128 KB en uno solo**, no para tener reservas vacías. Una vez asignados los 4, no se pueden añadir más nunca: son el techo absoluto.

### 12.2 Reglas de decisión

**Cuándo NO crear un bucket nuevo (= caso por defecto)**:
- Hay >50% libre en algún bucket existente cuyo dominio temático encaja.
- El sistema futuro tiene tamaño esperado <50 KB.
- El sistema futuro encaja por frecuencia de escritura con un bucket existente.

**Cuándo SÍ crear un bucket nuevo (= caso excepcional)**:
- Dominio ortogonal a los 4 actuales **Y** tamaño esperado >50 KB.
- Frecuencia de escritura incompatible con cualquier bucket existente (ej: write-cada-segundo vs. write-cada-hora).
- Un bucket existente está en >70% de uso y el nuevo sistema lo llevaría al cap.

### 12.3 Ejemplos concretos

| Sistema futuro | ¿Bucket nuevo? | Justificación |
|---|---|---|
| Sistema de mascotas adicional (nuevo tipo de companion) | ❌ no | encaja en `PlayerInventory.Companions` |
| Histórico de combates (1 evento por kill) | ❌ no | usar bitfield/contador agregado en `PlayerProgress`, no log evento por evento |
| Replay completo de 50 partidas (vídeo/serializado) | ✅ sí, si >50 KB | dominio ortogonal, peso real |
| UGC: el jugador construye estructuras complejas | ✅ sí, si >50 KB | dominio ortogonal, peso real |
| Sistema de chat persistente entre sesiones | ❌ no | usar `PlayerProgress.CodesRedeemed`-style array de IDs si hay pocos mensajes |
| Nuevo tipo de currency | ❌ no | añadir campo a `PlayerCore_Vn+1` (option-version) |

### 12.4 Antes de proponer bucket nuevo

Pregunta obligatoria: **¿estoy proponiendo bucket nuevo porque el dominio es realmente ortogonal y pesa >50 KB, o porque "queda más limpio" o "por si acaso"?**

Si la respuesta es la segunda, la respuesta es no. La limpieza estética del schema no justifica gastar uno de los 4 cupos absolutos.

---

**Fin del documento.**

> Este documento se actualiza cada vez que cambia un schema de persistencia.
> **Cualquier IA que toque persistencia DEBE consultar este doc antes.**
> **Patrón canónico vigente: option-version (Epic 8/8/2025).**
