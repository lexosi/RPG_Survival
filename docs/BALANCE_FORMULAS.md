# ⚖️ BALANCE_FORMULAS — Fórmulas de balance del juego

> **Documento crítico. Centraliza TODOS los números, curvas y fórmulas del juego con su justificación.**
>
> Los números viven en JSONs (data layer). **El "por qué" del número vive aquí.**
>
> **Cualquier IA que ajuste balance, drop rates, costes o curvas DEBE consultar este doc antes.**
> **Cuando un valor cambie, se actualiza aquí y en su JSON correspondiente, en el mismo sprint.**

---

## 🧭 Índice

1. [Filosofía de balance](#1-filosofía-de-balance)
2. [Constantes globales](#2-constantes-globales)
3. [Curvas de XP y niveles](#3-curvas-de-xp-y-niveles)
4. [Curva de rebirth](#4-curva-de-rebirth)
5. [Curva de Base Level](#5-curva-de-base-level)
6. [Drop rates de rarezas](#6-drop-rates-de-rarezas)
7. [Stats por rareza (companions)](#7-stats-por-rareza-companions)
8. [Equipment leveling (fail-rates)](#8-equipment-leveling-fail-rates)
9. [Reroll: curva exponencial de coste](#9-reroll-curva-exponencial-de-coste)
10. [Skill points por nivel](#10-skill-points-por-nivel)
11. [Pity system: pulls hasta garantía](#11-pity-system-pulls-hasta-garantía)
12. [Economía: ratios de generación](#12-economía-ratios-de-generación)
13. [Death penalty: % perdido](#13-death-penalty--perdido)
14. [Offline production](#14-offline-production)
15. [Crafting timers](#15-crafting-timers)
16. [Battle Pass: XP por nivel](#16-battle-pass-xp-por-nivel)
17. [Daily/Weekly: gemas otorgadas](#17-dailyweekly-gemas-otorgadas)
18. [Daily Login: progresión 28 días](#18-daily-login-progresión-28-días)
19. [Hourly Boss: dificultad y rewards](#19-hourly-boss-dificultad-y-rewards)
20. [Set Bonuses: progresión](#20-set-bonuses-progresión)
21. [Verificación cruzada de balance](#21-verificación-cruzada-de-balance)
22. [Cómo proponer un cambio de balance](#22-cómo-proponer-un-cambio-de-balance)

---

## 1. Filosofía de balance

### 1.1 Principios

1. **Cada decisión de balance tiene una hipótesis explícita**. No se ajustan números "porque sí".
2. **Siempre hay un eje al que sirve la fórmula**: retención, conversión F2P→pagador, sensación de progreso, dificultad, anti-exploit.
3. **Curvas exponenciales por defecto** para idle/tycoon: lineal aburre rápido.
4. **Primer feedback en <30 segundos**, primer hito en <2 minutos, primer rebirth en <30 minutos.
5. **Whale-friendly sin ser whale-only**: el F2P llega al endgame, solo más lento.
6. **Anti-exploit con caps razonables**, no anti-jugador.
7. **Redondeo determinista `Floor()`** cuando una fórmula float aterriza en un campo persistente int (ej. stats de player con `per_level: float` → stat int en PlayerCore). Truncamiento, no `Round()` ni redondeo bancario. Razones: determinista cliente/servidor, monotónico, mismo coste en Verse. Spec en `JSON_SCHEMAS.md` §44.3 + §44.4.

### 1.2 Los 4 relojes (CONCEPT 3.2)

| Reloj | Ritmo | Métrica de éxito |
|---|---|---|
| Sesión | 5–10 min | Mejora visible al menos 1× cada 10 min |
| Día | 30–90 min | +3 niveles, 1 ayudante raro |
| Semana | 5–10 h | Completar zona, derrotar boss |
| Mes | 30–50 h | Hacer rebirth, "todo cambia" |

**Las fórmulas se calibran contra estos ritmos**, no en absoluto.

### 1.3 Ejes de progresión (CONCEPT 3.3)

| Eje | Resetea con rebirth | Función balance |
|---|---|---|
| Player Level | Sí (con bonus) | Power ramping de la run |
| Rebirth Count | Nunca | Meta-progresión |
| Base Level | Nunca | Eje permanente, gate maestro |

---

## 2. Constantes globales

> **Estas constantes son referenciadas por múltiples sistemas.**

### 2.1 Caps de seguridad (anti-exploit)

| Constante | Valor | Justificación |
|---|---|---|
| `MAX_LEVEL` | 200 | Cap razonable que prevent integer issues. Más allá, BigNumbers. |
| `MAX_REASONABLE_GOLD` | 9_000_000_000_000_000_000 | Cerca de int64 max. Por encima, overflow string. |
| `MAX_REASONABLE_GEMS` | 999_999_999 | ~1B gemas. Cap defensivo. |
| `MAX_REBIRTH_COUNT` | 1000 | Endgame ultra-tardío. Por encima, prestige system. |
| `MAX_BASE_LEVEL` | 100 | Eje permanente, escalado lento. |
| `MAX_DEX_ENTRIES` | 300 | Companions × variantes principales. Cap del PERSISTENCE_MAP 4.2. |
| `MAX_ACHIEVEMENTS` | 256 | Limit del bitfield (PERSISTENCE_MAP 5.1). |
| `MAX_BP_LEVELS` | 100 | Niveles del Battle Pass por season (SYS-022). Cap técnico real: 192 (3×bitfield 64). Diseño actual: 100. |
| `MAX_INVENTORY_SLOTS` | 200 | Limit razonable. Default inicio: 50. |
| `MAX_BANK_SLOTS` | 500 | Limit razonable. Default inicio: 100. |
| `MAX_OFFLINE_HOURS` | 168 | 7 días. Más, no hay sesión que justifique. |

### 2.2 Tiempos de referencia

| Constante | Valor | Justificación |
|---|---|---|
| `TIME_FIRST_FEEDBACK_SEC` | 10 | Hook de primer minuto debe dispararse en ≤10s |
| `TIME_FIRST_REBIRTH_MIN_TARGET` | 30 | Decisión cerrada CONCEPT 14.3 |
| `TIME_FIRST_REBIRTH_MAX_TARGET` | 45 | Tope: si pasa, tutorial está mal calibrado |
| `SESSION_AVG_TARGET_MIN` | 60 | Sesión típica objetivo (CONCEPT 1.3) |
| `HOURLY_BOSS_WINDOW_SEC` | 120 | Decisión cerrada CONCEPT 14.7 |
| `SHOP_ROTATION_MIN` | 30 | Decisión cerrada CONCEPT 14.7 |

### 2.3 Multiplicadores económicos

| Constante | Valor | Justificación |
|---|---|---|
| `XP_BOOST_PASSIVE_MAX` | 2.0 | Cap stack de boosts XP (anti-paywall) |
| `GOLD_DEATH_LOSS_PERCENT` | 0.10 | 10% del gold no depositado. Suficiente sting sin frustración. |
| `XP_DEATH_LOSS_PERCENT` | 0.05 | 5% del XP del nivel actual. Solo nivel actual, no acumulado. |
| `AUCTION_COMMISSION_PERCENT` | 0.05 | 5% del precio. Estándar industria. |
| `REBIRTH_BONUS_PER_REBIRTH` | 0.02 | +2% stat permanente por rebirth. Stack hasta r100 = +200%. |

---

## 3. Curvas de XP y niveles

> **Sistema**: SYS-016 XP & Levels
> **JSON**: `data/progression/xp_curves.json`

### 3.1 Fórmula del Player Level

**Tipo**: exponencial suave.

```
xp_required(level) = BASE × level^EXPONENT

BASE = 100
EXPONENT = 1.6
```

### 3.2 Tabla de referencia

| Nivel | XP requerido | XP acumulado | Tiempo estimado (min) |
|---|---|---|---|
| 1→2 | 100 | 100 | ~1 |
| 5→6 | 1,103 | 2,800 | ~5 |
| 10→11 | 3,981 | 14,500 | ~15 |
| 20→21 | 12,126 | 100,000 | ~50 |
| 50→51 | 51,962 | 950,000 | ~5 h |
| 100→101 | 158,489 | 4.5M | ~25 h |
| 200→201 | 502,377 | 24M | ~100 h |

### 3.3 Hipótesis

- **Nivel 5 en ~5 min**: el jugador siente progreso rápido inicial.
- **Nivel 20 cabe en una sesión típica** (~50 min): hito significativo por sesión.
- **Nivel 50 ≈ momento natural de primer rebirth opcional** (no obligatorio, ya completó tutorial).
- **Nivel 100+ es endgame**: requiere meta-progresión (skill points, rebirth bonuses).

### 3.4 Ganancia de XP por fuente

| Fuente | XP base | Notas |
|---|---|---|
| Resource gather (común) | 5 | Multiplicado por tier de resource |
| Resource gather (raro) | 25 | |
| Kill enemigo común | 10 | |
| Kill mini-boss | 200 | |
| Kill boss zona | 1,000 | |
| Quest completar | 50–500 | Según categoría |
| Tutorial quest | +20% bonus | Onboarding agradable |

---

## 4. Curva de rebirth

> **Sistema**: SYS-020 Rebirth System
> **JSON**: `data/progression/rebirth_rewards.json`
> **Decisión cerrada**: CONCEPT 14.3

### 4.1 Curva objetivo (tiempos cumulativos)

| Rebirth # | Tiempo acumulado objetivo | Multiplicador XP necesario |
|---|---|---|
| r1 | 30 min | 1× (baseline) |
| r2 | 1.5 h | 1.5× |
| r3 | 3 h | 1.8× |
| r5 | 3–4 h | 2.5× |
| r10 | 10 h | 5× |
| r25 | 30 h | 15× |
| r50 | 80 h | 40× |
| r100 | 200 h | 100× |
| r1000 | "infinity" | con BigNumbers |

### 4.2 Fórmula

```
rebirth_xp_required(n) = REBIRTH_BASE × n^REBIRTH_EXPONENT × current_max_level_xp

REBIRTH_BASE = 1.0
REBIRTH_EXPONENT = 1.4
```

### 4.3 Recompensas permanentes por rebirth

| Rebirth # | Recompensa permanente |
|---|---|
| r1 | +5% XP gain global |
| r5 | Slot extra de companion activo |
| r10 | +10% gold gain global |
| r25 | Acceso a zona "Rebirth Ascended" |
| r50 | +1 skill point por nivel |
| r100 | Título exclusivo "Eternal" + cosmético |

### 4.4 Hipótesis

- **r1 a 30 min**: el jugador toca el loop completo antes de comprometerse.
- **r5–r10 en una sesión larga de fin de semana**: hook para la primera semana.
- **r25 = jugador retenido a 1 mes**.
- **r100 = whale o ultra-engaged a 6 meses**.

---

## 5. Curva de Base Level

> **Sistema**: SYS-059 Base Level
> **JSON**: `data/base/base_levels.json`
> **Eje permanente, NO se resetea con rebirth.**

### 5.1 Filosofía

Base Level es el **eje maestro de progresión global**. Crece más lento que Player Level pero NUNCA se pierde. Es el gate de zonas, quests y eventos.

### 5.2 Fórmula

```
base_xp_required(bl) = BASE_LVL_BASE × bl^BASE_LVL_EXPONENT

BASE_LVL_BASE = 500
BASE_LVL_EXPONENT = 1.8
```

### 5.3 Tabla de referencia

| Base Level | XP requerido | Tiempo estimado total | Unlocks notables |
|---|---|---|---|
| 1 | 0 | 0 | Inicial. Tutorial. |
| 5 | 6,300 | ~3 h | Bank persistente |
| 10 | 31,500 | ~10 h | Offline production 12h |
| 25 | 218,750 | ~50 h | Auction local |
| 50 | 1,118,033 | ~150 h | Offline production 48h, eficiencia 60% |
| 100 | 6,309,573 | ~600 h | Endgame: "Base Master" |

### 5.4 XP gain de base

| Fuente | Base XP base |
|---|---|
| Quest completada | +50 base XP |
| Boss derrotado | +500 base XP |
| Crafting completado | +25 base XP |
| Upgrade construido | +200 base XP × tier |
| First rebirth | +1,000 base XP (one-time) |

---

## 6. Drop rates de rarezas

> **Sistema**: SYS-011 Rarity Tiers + SYS-034 Lootboxes
> **JSON**: `data/items/lootboxes.json`
> **Decisión cerrada**: CONCEPT 14.5

### 6.1 Tabla canónica de drop rates

| Rareza | Drop rate (lootbox premium) | Hex color |
|---|---|---|
| Common | 60.00% | `#9CA3AF` |
| Uncommon | 25.00% | `#22C55E` |
| Rare | 10.00% | `#3B82F6` |
| Epic | 3.50% | `#A855F7` |
| Legendary | 1.00% | `#F97316` |
| Mythic | 0.40% | `#EF4444` |
| Secret | 0.09% | `#000000` (iridiscente) |
| Admin | 0.01% | `#FCD34D` |
| **Total** | **100.00%** | |

### 6.2 Tabla por tipo de lootbox

| Lootbox type | Common | Uncommon | Rare | Epic | Legendary | Mythic | Secret | Admin |
|---|---|---|---|---|---|---|---|---|
| **basic** | 75% | 20% | 4.5% | 0.5% | 0% | 0% | 0% | 0% |
| **premium** | 60% | 25% | 10% | 3.5% | 1.0% | 0.40% | 0.09% | 0.01% |
| **event** | 40% | 30% | 18% | 8% | 3% | 0.9% | 0.1% | 0% |
| **mythic** | 0% | 0% | 30% | 40% | 20% | 8% | 1.8% | 0.2% |
| **secret** | 0% | 0% | 0% | 30% | 40% | 20% | 9% | 1% |

### 6.3 Hipótesis

- **Premium ratio Mythic 0.4%**: ~250 pulls esperado para un Mythic. Pity en 80 (sección 11) lo contiene.
- **Secret 0.09%**: 1 de cada ~1100 pulls. Es el "Holy Grail" de comunidad.
- **Admin 0.01%**: leyenda. Comunidad lo recordará.

---

## 7. Stats por rareza (companions)

> **Sistema**: SYS-010 Companion Core
> **JSON**: `data/companions/companions_base.json`

### 7.1 Multiplicadores base por rareza

```
multiplier(rarity) = 1 + (rarity - 1) × 0.5
```

| Rareza | Multiplicador stat base |
|---|---|
| Common (1) | 1.0× |
| Uncommon (2) | 1.5× |
| Rare (3) | 2.0× |
| Epic (4) | 2.5× |
| Legendary (5) | 3.0× |
| Mythic (6) | 3.5× |
| Secret (7) | 5.0× (jump intencional) |
| Admin (8) | 10.0× (jump masivo, son legendary memorable) |

### 7.2 Stats base orientativos (Common)

| Stat | Common base |
|---|---|
| HP | 50 |
| ATK | 10 |
| DEF | 5 |
| Speed | 8 |

Para un Mythic: HP=175, ATK=35, DEF=17, Speed=28.
Para un Secret: HP=250, ATK=50, DEF=25, Speed=40.

### 7.3 Multiplicadores por variante

| Variante | Multiplicador stat |
|---|---|
| Normal (0) | 1.0× |
| Oro (1) | 1.5× |
| Diamante (2) | 2.5× |
| Arcoiris (3) | 5.0× |
| Hacker (event) | 4.0× + glitch effect |
| Lava (event) | 4.0× + burn DOT |

**Stat final** = `base × rarity_multiplier × variant_multiplier`.

Ejemplo: Mythic Diamante = `50 × 3.5 × 2.5 = 437.5 HP`.

---

## 8. Equipment leveling (fail-rates)

> **Sistema**: SYS-025 Equipment Leveling
> **JSON**: `data/items/equipment_leveling.json`
> **Decisión cerrada**: CONCEPT 14.6 (T1→T2 100%, T9→T10 5%)

### 8.1 Tabla de fail-rates (sin protector)

| Tier | Success rate | Fail rate | Destroy on fail |
|---|---|---|---|
| 1→2 | 100% | 0% | No (no failure possible) |
| 2→3 | 95% | 5% | No (downgrade -1) |
| 3→4 | 85% | 15% | No (downgrade -1) |
| 4→5 | 70% | 30% | No (downgrade -1) |
| 5→6 | 55% | 45% | Sí (con prob 50% del 45%) |
| 6→7 | 40% | 60% | Sí (con prob 60%) |
| 7→8 | 25% | 75% | Sí (con prob 70%) |
| 8→9 | 12% | 88% | Sí (con prob 80%) |
| 9→10 | 5% | 95% | Sí (con prob 90%) |

### 8.2 Costes por tier (gold)

```
cost(t) = BASE_COST × FACTOR^t

BASE_COST = 1,000
FACTOR = 1.8
```

| Tier | Gold cost |
|---|---|
| 1→2 | 1,000 |
| 5→6 | 18,895 |
| 9→10 | 219,902 |

### 8.3 Protectores: probabilidad de salvar

| Protector | Prob. salvar fallo |
|---|---|
| Bronce | 60% |
| Plata | 80% |
| Oro | 95% |
| Diamante | 100% (siempre salva) |

### 8.4 Hipótesis

- **T6+ es donde el sistema "pica"**: probabilidad real de éxito sin protector cae brutalmente.
- **Diamante es el "seguro premium"**: lo compran whales o se gana en eventos largos.
- **T10 es prestigio puro**: ~5% raw → ~80% con protector Oro. Caro pero alcanzable.

---

## 9. Reroll: curva exponencial de coste

> **Sistema**: SYS-028 Reroll Stats
> **JSON**: `data/items/reroll.json`

### 9.1 Fórmula

```
reroll_cost(n) = BASE × (1 + n)^EXPONENT

BASE_COST_GOLD = 500
EXPONENT = 1.5
n = número de rerolls previos del MISMO item
```

### 9.2 Tabla

| Reroll # | Coste gold |
|---|---|
| 1 (n=0) | 500 |
| 2 (n=1) | 1,414 |
| 3 (n=2) | 2,598 |
| 5 (n=4) | 5,590 |
| 10 (n=9) | 15,811 |
| 20 (n=19) | 43,470 |
| 50 (n=49) | 175,000 |
| 100 (n=99) | 500,000 |

### 9.3 Hipótesis

- **Primer reroll barato**: anima a probar el sistema.
- **Curva exponencial moderada (1.5)**: no demasiado punitiva.
- **Reroll #50 ≈ "stop loss" implícito**: quien gasta 175K en 1 item, ya sabe lo que hace.

---

## 10. Skill points por nivel

> **Sistema**: SYS-017 Skill Points
> **JSON**: `data/progression/skill_points.json`

### 10.1 Fórmula

```
skill_points_total(level) = level × 1 + bonus_milestones

milestone_bonuses = {
  10: +2,
  25: +3,
  50: +5,
  100: +10
}
```

### 10.2 Tabla acumulativa

| Nivel | SP normal | SP bonus | Total SP |
|---|---|---|---|
| 10 | 10 | 2 | 12 |
| 25 | 25 | 5 | 30 |
| 50 | 50 | 10 | 60 |
| 100 | 100 | 20 | 120 |
| 200 | 200 | 20 | 220 |

### 10.3 Coste de skills

```
skill_cost(rank) = BASE_COST × (rank + 1)
```

Skills tienen 1–10 ranks. Coste total para maxear un skill de 5 ranks: 1+2+3+4+5 = 15 SP.

### 10.4 Hipótesis

- **Jugador a nivel 50** = 60 SP, suficiente para ~4 skills maxeadas en 1 tree o spread en varias.
- **Milestones marcan progresión**: nivel 25, 50, 100 son hitos visibles.
- **Rebirth +50 bonus**: un rebirth da +1 SP por nivel, acelera la 2ª run.

---

## 11. Pity system: pulls hasta garantía

> **Sistema**: SYS-035 Pity System
> **JSON**: `data/economy/pity_config.json`

### 11.1 Tabla por (alma_type, rarity_target)

| Alma type | Rareza objetivo | Pulls hasta garantía |
|---|---|---|
| basic | rare | 30 |
| basic | epic | 100 |
| premium | epic | 25 |
| premium | legendary | 80 |
| premium | mythic | 250 |
| premium | secret | 1,500 |
| event | legendary | 50 |
| event | mythic | 150 |
| mythic | mythic | 30 |
| mythic | secret | 200 |
| secret | secret | 50 |

### 11.2 Mecánica

- Cada pull SIN obtener la rareza objetivo: counter += 1
- Al obtener la rareza objetivo (por drop o por garantía): counter = 0
- Counters separados por (alma_type, rarity_target)

### 11.3 Hipótesis

- **Premium Mythic con pity 250**: un whale dedicado puede garantizarlo. Coste estimado: 250 × 100 gemas/lootbox = 25K gemas. ~$50 si comprara directo.
- **Secret pity 1500**: legendaria garantía pero realista para super-engaged.
- **Pity per-rareza**: incentiva diversificar entre tipos de almas.

---

## 12. Economía: ratios de generación

### 12.1 Gold

| Fuente | Gold base | Notas |
|---|---|---|
| Resource gather (basic) | 1–5 | Por nodo |
| Resource gather (rare) | 10–25 | |
| Sell common item | 5 | |
| Sell rare item | 100 | |
| Sell epic item | 1,000 | |
| Sell legendary item | 10,000 | |
| Daily quest avg | 500 | |
| Weekly quest avg | 2,500 | |
| Boss drop | 1,000–10,000 | Según boss |

### 12.2 Gems

| Fuente | Gems base |
|---|---|
| Daily quest avg | 5 |
| Weekly quest avg | 25 |
| Achievement | 10–100 |
| Daily login (avg) | 3 (milestones: 25–50) |
| Boss drop | 1–10 |
| First rebirth | 100 (one-time) |
| Rebirth #N+1 | 50 + 5×N |
| Time played 30 min | 1 |
| Time played 60 min | 3 |

### 12.3 Tasa esperada de gems

| Engagement | Gems/día estimadas |
|---|---|
| Casual (login + 1 daily) | ~10 |
| Engaged (logged in, 3 dailies, 1 weekly partial) | ~40 |
| Hardcore (todo dailies + weeklies + achievements) | ~150 |

**Lootbox premium = 100 gems**:
- Casual: 1 lootbox cada 10 días.
- Engaged: 1 cada 2.5 días.
- Hardcore: 1.5 al día.

---

## 13. Death penalty: % perdido

> **Sistema**: SYS-009 Death Penalty
> **Decisión cerrada**: CONCEPT 14.4

### 13.1 Fórmulas

```
gold_lost = current_gold_not_in_bank × GOLD_DEATH_LOSS_PERCENT
xp_lost = xp_in_current_level × XP_DEATH_LOSS_PERCENT

GOLD_DEATH_LOSS_PERCENT = 0.10
XP_DEATH_LOSS_PERCENT = 0.05
```

### 13.2 Lo que NO se pierde (regla cerrada)

- ❌ Gemas (NUNCA)
- ❌ Companions (incluyendo activos)
- ❌ Items del inventario
- ❌ Quests progress
- ❌ Equipment equipado o no

### 13.3 Protectores de death penalty

| Tier | Duración | Cost gems | Cost gold |
|---|---|---|---|
| Bronce | 1 hora | 5 | 5,000 |
| Plata | 24 horas | 50 | 50,000 |
| Oro | 7 días | 250 | 250,000 |
| Diamante | Permanente | 5,000 | (no comprable con gold) |

---

## 14. Offline production

> **Sistema**: SYS-062 Offline Production
> **JSON**: `data/base/offline_config.json`
> **Decisión cerrada**: CONCEPT 14.8

### 14.1 Fórmula

```
offline_production = generator_rate × min(elapsed_time, max_offline_hours) × efficiency
```

### 14.2 Caps y eficiencia por base level

| Base Level | Max offline hours | Efficiency |
|---|---|---|
| 1 | 4 | 30% |
| 5 | 6 | 40% |
| 10 | 12 | 50% |
| 25 | 24 | 60% |
| 50 | 48 | 80% |
| 100 | 72 | 100% |

### 14.3 Hipótesis

- **Onboarding (BL 1–10)**: poco offline, fuerza play activo.
- **BL 25 con 24h al 60%**: jugador casual diario obtiene rendimiento.
- **BL 100 al 100%**: endgame full passive viable, pero llegar es endgame de ~600h.

---

## 15. Crafting timers

> **Sistema**: SYS-063 Crafting Timers
> **JSON**: `data/items/crafting_timers.json`
> **Decisión cerrada**: tiempos NO se capean offline (CONCEPT 14.8)

### 15.1 Tabla orientativa

| Categoría | Recipe ejemplo | Tiempo |
|---|---|---|
| Forge basic | Sword T1 | 5 min |
| Forge medium | Sword T5 | 1 hora |
| Forge advanced | Sword T8 | 12 horas |
| Forge endgame | Sword T10 | 3 días |
| Alchemy basic | Potion HP | 2 min |
| Alchemy medium | Buff XP 1h | 30 min |
| Alchemy advanced | Buff perm 24h | 6 horas |
| Hatchery common | Egg companion common | 10 min |
| Hatchery rare | Egg companion rare | 2 horas |
| Hatchery legendary | Egg companion legendary | 1 día |

### 15.2 Hipótesis

- **Recipes cortas para variedad de gameplay** (agregan a sesión).
- **Recipes largas como "set and forget"** (incentivan login al día siguiente).
- **3 días tope para forge T10**: es el tier más prestigioso, espera dramática.

---

## 16. Battle Pass: XP por nivel

> **Sistema**: SYS-022 Battle Pass
> **JSON**: `data/progression/battle_pass_seasons/season_NN.json`

### 16.1 Fórmula

```
bp_xp_per_level = 1000 (constante, no exponencial)
total_levels = 100
total_bp_xp_season = 100,000
```

### 16.2 Duración objetivo de season

| Engagement | Tiempo a nivel 100 BP |
|---|---|
| Casual (1h/día) | ~75 días (full season) |
| Engaged (2h/día) | ~40 días |
| Hardcore (4h+/día) | ~20 días |

### 16.3 BP XP gain

| Fuente | BP XP base |
|---|---|
| Daily quest | +200 |
| Weekly quest | +1,000 |
| Achievement | +500 |
| Boss kill | +500 |
| Resource milestone | +50 |

### 16.4 Hipótesis

- **Lineal y predecible**: jugadores planifican su BP.
- **Casual completa season en 75 días**: tight pero alcanzable. F2P-friendly.
- **Premium price ~750 gems o ~950 V-Bucks**: alineado con industria.

---

## 17. Daily/Weekly: gemas otorgadas

> **Sistema**: SYS-039 Quest System
> **Decisión cerrada**: 3 dailies, 9 weeklies (CONCEPT 14.7)

### 17.1 Distribución

| Quest pool | # quests | Gems por quest | Gems totales | XP del BP |
|---|---|---|---|---|
| Daily | 3 | 5 | 15 gems | +600 BP XP |
| Weekly | 9 | 25 | 225 gems | +9,000 BP XP |

### 17.2 Por semana (todo completado)

- 7 días × 3 dailies × 5 gems = **105 gems/semana de dailies**
- 9 weeklies × 25 gems = **225 gems/semana de weeklies**
- **Total**: ~330 gems/semana = ~1,320 gems/mes

### 17.3 Hipótesis

- **3 dailies = ~15 min de juego**: digestible diariamente.
- **9 weeklies = ~3 horas spread**: incentivo para 3-4 sesiones/semana.
- **1,320 gems/mes**: 13 lootboxes premium, ~3-4 ayudantes Rare+.

---

## 18. Daily Login: progresión 28 días

> **Sistema**: SYS-040 Daily Login
> **JSON**: `data/progression/daily_login.json`

### 18.1 Tabla de recompensas

| Día | Recompensa | Es milestone |
|---|---|---|
| 1 | 50 gold | No |
| 2 | 100 gold | No |
| 3 | 1 lootbox basic | No |
| 4 | 5 gems | No |
| 5 | 200 gold | No |
| 6 | 1 lootbox basic | No |
| 7 | **25 gems + 1 lootbox premium** | ✅ |
| 8–13 | progresión similar | No |
| 14 | **50 gems + 2 lootboxes premium** | ✅ |
| 15–20 | progresión similar | No |
| 21 | **100 gems + companion guaranteed Epic+** | ✅ |
| 22–27 | progresión similar | No |
| 28 | **300 gems + companion guaranteed Legendary + cosmético exclusivo** | ✅ |

### 18.2 Hipótesis

- **Milestones cada 7 días**: sensación de "vale la pena seguir"
- **Día 28 climax**: companion legendary + cosmético crea urgencia para no perder streak
- **Rescue con gemas**: 10 gemas/día perdido (CONCEPT 14.7 implícito)

---

## 19. Hourly Boss: dificultad y rewards

> **Sistema**: SYS-042 Hourly Boss Event
> **JSON**: `data/events/hourly_boss.json`

### 19.1 Estructura de rewards

| Tier de boss | Player level requerido | Rewards |
|---|---|---|
| Boss tier 1 | nivel 5+ | 100 gold + 5 gems + 50% chance lootbox basic |
| Boss tier 2 | nivel 20+ | 1,000 gold + 15 gems + 1 lootbox premium |
| Boss tier 3 | nivel 50+ | 10,000 gold + 50 gems + 30% chance Mythic companion |
| Boss tier 4 | nivel 100+ | 100,000 gold + 200 gems + 5% chance Secret |

### 19.2 Mecánica

- **Portal abre HH:00, ventana 2 min**
- **Teleport masivo HH:02** a arena cooperativa
- **Fight time: 5–10 min**
- **1 intento por hora por jugador**

### 19.3 Hipótesis

- **Boss tier 3 a partir nivel 50** = punto donde Mythic empieza a ser realista.
- **Recompensas también dropean en otras fuentes** (CONCEPT 14.7): no es exclusiva.

---

## 20. Set Bonuses: progresión

> **Sistema**: SYS-027 Set Bonuses
> **JSON**: `data/items/sets.json`

### 20.1 Patrón estándar

| Piezas equipadas | Bonus |
|---|---|
| 2 piezas | +5% stat principal del set |
| 3 piezas | +10% stat principal + nuevo efecto |
| 4 piezas | +20% stat principal + efecto mejorado |
| 6 piezas (full set) | +50% stat principal + efecto único set |

### 20.2 Ejemplo: Set "Dragon Slayer" (6 piezas)

- 2p: +5% damage vs dragones
- 3p: +10% damage + dragones dropean +1 item
- 4p: +20% damage + chance crit doble
- 6p: +50% damage + special skill "Dragon Roar"

### 20.3 Hipótesis

- **6p como aspiration goal**: difícil completar pero siempre visible.
- **Cada tier de bonus es notable**, no solo +1% más.

---

## 21. Verificación cruzada de balance

> **Antes de ajustar números, verifica que estos invariantes se cumplen.**

### 21.1 Invariantes económicos

- ✅ **Whale gasta gemas** → no rompe economía F2P (no acumula ventaja permanente injusta).
- ✅ **F2P puede llegar a r5 en ~3-4 h** sin pagar.
- ✅ **Drop rates suman 100%** en cada lootbox.
- ✅ **Pity garantiza** sin hacer pity la única vía.
- ✅ **No hay "tampoco vale la pena jugar"**: cada día/semana hay algo nuevo si vuelves.

### 21.2 Invariantes de progresión

- ✅ **Cada nivel siente progreso** (al menos 1 stat sube o desbloqueo).
- ✅ **Rebirth siempre > Power Level previo**: la 2ª run es más fácil que la 1ª gracias a meta-progresión.
- ✅ **Base Level NUNCA tiene downside**: solo añade, nunca quita.
- ✅ **Dailies son siempre cumplibles en el día** (ningún daily requiere >30 min).

### 21.3 Invariantes anti-frustración

- ✅ **Death no pierde nada permanente** (gemas, companions, items, quests).
- ✅ **No hay "nivel mínimo para jugar X"** sin alternativa de farm.
- ✅ **Cada error de UX tiene mensaje claro** (sin gemas, item bloqueado, etc.).
- ✅ **Sin walls aleatorios**: todo gate tiene gate alternativo si el RNG no coopera.

### 21.4 Sanity checks numéricos

- ✅ XP del nivel N+1 > XP del nivel N
- ✅ Coste reroll N+1 > Coste reroll N
- ✅ Tier upgrade success rate decrece con tier
- ✅ Pity guarantee >> drop rate × razonable_pulls
- ✅ Premium drop rates suman 100% exactamente (con float tolerance ±0.001)

---

## 22. Cómo proponer un cambio de balance

### 22.1 Workflow obligatorio

1. **Identifica el sistema afectado** (SYS-xxx).
2. **Lee la sección correspondiente** de este documento.
3. **Propón el cambio CON HIPÓTESIS**: qué eje afecta, qué métrica esperas mover.
4. **Verifica invariantes** sección 21.
5. **Actualiza JSON correspondiente** + esta sección de este documento.
6. **Documenta en CHANGELOG.md** el cambio + justificación.
7. **Commit con mensaje claro**: `BALANCE: <SYS-xxx> ajuste de <fórmula> de X a Y, razón: ...`

### 22.2 Plantilla de propuesta

```markdown
## Propuesta de cambio de balance — YYYY-MM-DD

### Sistema afectado
SYS-xxx ([nombre])

### Cambio propuesto
ANTES: [valor actual]
DESPUÉS: [valor nuevo]

### Hipótesis
[Por qué este cambio. Qué métrica esperas mover. Cuál es el eje (retención, conversión, sensación, etc).]

### Impacto esperado en jugadores
- F2P: [...]
- Casual: [...]
- Whale: [...]

### Invariantes verificados
- [✅] Drop rates suman 100%
- [✅] Curva sigue siendo monótona
- [✅] No rompe sistemas dependientes
- [...]

### Archivos que cambian
- `data/.../*.json`: [campos modificados]
- `BALANCE_FORMULAS.md`: sección X.Y

### Métricas para validar éxito
- [Métrica 1: cómo medirla, cuánto ha de cambiar para considerar éxito]
- [Métrica 2: ...]

### Plan de rollback si falla
[Cómo revertir si los datos reales muestran que el cambio empeoró las cosas]
```

### 22.3 Triggers para revisión obligatoria de balance

Revisa este documento cuando:
- Cierres una fase (F0, F1, F2...)
- Se publique una season nueva (Battle Pass)
- Datos reales contradigan una hipótesis del documento
- Una mecánica nueva interactúe con varias existentes
- Comunidad reporte feedback consistente sobre dificultad/coste

---

## 📌 Resumen ejecutivo

```
🎯 ESTE DOCUMENTO ES LA FUENTE DE VERDAD del POR QUÉ de cada número.

🔑 PRINCIPIOS:
   1. Cada número tiene una hipótesis explícita.
   2. Curvas exponenciales por defecto en idle/tycoon.
   3. F2P viable, whale-friendly, sin pay-to-win narrativo.
   4. Rebirths frecuentes y rápidos. r1 en 30 min.
   5. Anti-exploit con caps razonables, no anti-jugador.

📋 ANTES DE AJUSTAR UN NÚMERO:
   1. Lee la sección correspondiente.
   2. Verifica invariantes (sección 21).
   3. Actualiza JSON + esta doc.
   4. Documenta en CHANGELOG.

⚠️ NUNCA AJUSTES UN NÚMERO SIN:
   - Hipótesis explícita
   - Verificación de invariantes
   - Plan de rollback
   - Mención en CHANGELOG
```

---

**Fin del documento.**

> Este documento se actualiza al cierre de cada fase (mínimo) y cuando datos reales contradigan hipótesis.
> **Cualquier IA que ajuste balance DEBE consultar este doc antes.**
