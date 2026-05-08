# Verse Syntax Guide — RPG_Survival

> **Fuente única de verdad** para sintaxis Verse moderna en este proyecto.
> Cualquier doc autoritativo que contradiga este documento está OBSOLETO.
> Última actualización: 2026-05-07 (SPR-211).

---

## §1 Reglas inquebrantables (las 13 lecciones)

### Lección 1 — `<ProjectName>` placeholder LITERAL

`using { /<ProjectName>/Core/Logger }` falla con `vErr:S26: Missing label in path following "/"`.

Path canónico real (Verse moderno) incluye `Verse/`:

```
/lexosi@fortnite.com/RPG_Survival/Verse/Core/Logger
```

Alternativa moderna preferida (la que ofrece VS Code Quick Fix → "Use relative path"):

```verse
using { Verse.Core.Logger }
```

### Lección 2 — CHANGELOG D-02 OBSOLETO

Entry D-02 declaraba:

1. Sintaxis dotted relative inválida.
2. Path canónico sin `Verse/`.

Ambos puntos son falsos hoy. Verse moderno acepta dotted. El path canónico SÍ incluye `Verse/`.

### Lección 3 — `return` no existe

Verse usa última expresión del bloque como retorno.

```verse
# ❌ MAL
F():int=
    return 42

# ✅ BIEN
F():int=
    42
```

### Lección 4 — `<decides>` cambia tipo retorno (failable)

Para predicados failable: tipo de retorno `:void=` y condiciones como statements separados (cada una succeed o fail).

```verse
IsInWindow<public>(StartEpoch:int, DurationSeconds:int)<decides>:void=
    Now := TimeSync.GetUTCNow[]
    Now >= StartEpoch
    Now < StartEpoch + DurationSeconds
```

### Lección 5 — `var` top-level SOLO `weak_map`

Errores `3593` + `3512`: *"Module-scoped 'var' must have 'weak_map' type"*.

State mutable normal (`var int`, `var float`, `var string`, etc.) **NO** se permite top-level. Va dentro de class instances.

### Lección 6 — Failable calls con `[]`

Funciones `<decides>` se invocan con `[]`, no `()`.

```verse
# ✅
N := Floor[Elapsed]
M := Mod[Now, 3600]

# ❌
N := Floor(Elapsed)   # call signature error
```

### Lección 7 — `<concrete>` + expuesto = `<public>` consistente

Si una función `<public>` retorna o expone un tipo, ese tipo también debe ser `<public>`. Error `3593`: *"Definition X is more accessible than its dependencies"*.

### Lección 8 — `class<concrete>` top-level + métodos failable/effects = INCOMPATIBLE

- Top-level Verse es contexto `<computes>` puro.
- Métodos `<decides>` propagan `<transacts>` al class instance.
- Construcción top-level `MyClass : my_class = my_class{}` falla con err `3512`.
- `external{}` solo válido en archivos `.digest` (err `3558`).

**Solución para Cores sin state**: usar `Module<public> := module:` (namespace), no class.

### Lección 9 — struct `{...}` literal = archetype constructor

`companion_def{ID := 1, ...}` con args estilo `:=` ES un archetype constructor → propaga `transacts`. Err `3547` + `3512` combo.

### Lección 10 — Args struct usan `:=` con espacios

Sintaxis canónica: `companion_def{ID := 1, Rarity := 5}` (con espacios alrededor del `:=`). Sin espacios funciona pero no canónico.

### Lección 11 — structs literal top-level dentro de module PROPAGAN transacts

`NAME<public>:type = type{...}` top-level dentro de un module **falla con err 3512** igual que classes. **Cambiar visibility NO resuelve** (validado).

Solución: instanciar dentro de funciones getter (`<computes>` por defecto).

### Lección 12 — Patrón canónico "constantes" generadas = funciones

```verse
# ❌ ANTES (rompe con 3512)
COMPANION_DRAGON_FIRE<public>:companion_def = companion_def{ID := 1, ...}

# ✅ AHORA
GetCompanionDragonFire<public>():companion_def=
    companion_def{ID := 1, ...}
```

Naming: `Get{Singular}{PascalCaseName}()`. Snake_case → PascalCase.

### Lección 13 — Type definitions expuestas vía module = `<public>`

Si `Module<public>:` expone función con tipo de retorno `[]companion_def`, el `companion_def` debe ser `<public>`. Si no, err `3593`.

---

## §2 Patrones canónicos verificados

### §2.1 Core sin state (módulo namespace)

```verse
# Logger.verse
using { /Verse.org/Simulation }

Logger<public> := module:

    DEBUG_ENABLED<public>:logic = true

    LogDebug<public>(Module:string, Message:string):void=
        if (DEBUG_ENABLED?):
            Print("[DEBUG][{Module}] {Message}")

    LogInfo<public>(Module:string, Message:string):void=
        Print("[INFO][{Module}] {Message}")

    LogWarn<public>(Module:string, Message:string):void=
        Print("[WARN][{Module}] {Message}")

    LogError<public>(Module:string, Message:string):void=
        Print("[ERROR][{Module}] {Message}")
```

### §2.2 Core sin state con failable functions

```verse
# TimeSync.verse
using { /Verse.org/Simulation }
using { Verse.Core.Logger }

TimeSync<public> := module:

    GetUTCNow<public>()<decides>:int=
        Elapsed:float = GetSimulationElapsedTime()
        Floor[Elapsed]

    GetSecondsUntilNextHour<public>()<decides>:int=
        Now := TimeSync.GetUTCNow[]
        SecondsIntoCurrentHour := Mod[Now, 3600]
        3600 - SecondsIntoCurrentHour

    IsInWindow<public>(StartEpoch:int, DurationSeconds:int)<decides>:void=
        Now := TimeSync.GetUTCNow[]
        Now >= StartEpoch
        Now < StartEpoch + DurationSeconds
```

### §2.3 Generated data files (struct + getters)

```verse
# Companions_Generated.verse
companion_def<public> := struct:
    ID:int
    Rarity:int
    BaseHP:int
    BaseAtk:int
    BaseDef:int
    BaseSpeed:int

Companions_Generated<public> := module:

    GetCompanionDragonFire<public>():companion_def=
        companion_def{ID := 1, Rarity := 5, BaseHP := 100, BaseAtk := 25, BaseDef := 15, BaseSpeed := 12}

    GetAllCompanions<public>():[]companion_def=
        array{ GetCompanionDragonFire() }
```

### §2.4 Core con state mutable (PENDIENTE — TBD SPR-008+)

> Bloqueado. PersistenceLayer (SPR-008) será caso de estudio. Posibles approaches:
> - `weak_map` top-level (única var top-level legal — lección 5).
> - State dentro de class instances no expuestas top-level.
> - Singleton vía `creative_device` si todo lo demás falla (último recurso, rompe Capa 0).
>
> Cuando SPR-008 valide approach → actualizar esta sección.

---

## §3 Anti-patrones (con error codes y fix)

| Anti-patrón | Error | Lección | Fix |
|---|---|---|---|
| `using { /<ProjectName>/Core/X }` | `vErr:S26` | 1 | `using { Verse.Core.X }` o path real con `Verse/` |
| `class<concrete>:` top-level con métodos `<decides>` | `3512` | 8 | `Module<public> := module:` (namespace) |
| `Singleton : sing_module = sing_module{}` top-level | `3512` + `3593` | 7, 8 | Eliminar singleton, usar module namespace |
| `return X` en función | parse error | 3 | Última expresión del bloque |
| `Floor(x)` con `<decides>` | call signature error | 6 | `Floor[x]` |
| `var int = 0` top-level | `3593` + `3512` | 5 | Solo `weak_map` top-level, resto en class instance |
| `NAME := struct_def{...}` top-level dentro module | `3547` + `3512` | 9, 10, 11 | Función getter (Patrón 3) |
| `NAME<public>:type = type{...}` top-level dentro module | `3512` | 11 | Función getter (Patrón 3) |
| Module function retorna tipo no `<public>` | `3593` | 7, 13 | Marcar tipo `<public>` |

---

## §4 Imports y paths

- Path canónico Verse moderno **incluye** `Verse/`:
  `/lexosi@fortnite.com/RPG_Survival/Verse/Core/Logger`
- Sintaxis dotted relative SÍ válida y preferida:
  `using { Verse.Core.Logger }`
- `<ProjectName>` es placeholder literal en docs viejos — **NO interpretar**.
- VS Code Quick Fix "Use relative path" produce dotted válido.

---

## §5 Failable context

- `<decides>` marca función failable.
- Llamar con `[]` no `()`: `GetUTCNow[]`, `Floor[x]`, `Mod[x, y]`.
- Predicados failable: `:void=` con condiciones como statements separados (cada uno succeed/fail).
- Ejemplo:

```verse
IsValid<public>(N:int)<decides>:void=
    N > 0
    N < 100
```

---

## §6 State mutable

- **Top-level**: SOLO `weak_map`. Cualquier otro `var int`, `var float`, `var string`, etc. → err `3593` + `3512`.
- **Dentro de class instances**: cualquier `var Type = init` permitido.
- **Dentro de module**: validar caso por caso. State en module-scope con tipos no-`weak_map` probable rechazado igual que top-level (lección 5 generaliza).

---

## §7 Effects (TBD — investigar)

Effects conocidos:

| Effect | Significado |
|---|---|
| `<computes>` | default top-level. Pure computation. |
| `<transacts>` | Propagado por archetype instantiation (`{...}`). |
| `<decides>` | Failable. |
| `<allocates>` | Instance allocation (clases con state). |
| `<varies>` | Non-deterministic (TBD). |

> Reglas exactas de propagación de efectos: TBD. Bloqueado hasta SPR siguiente investigue casos edge. Por ahora: si error `3512` aparece, mover construcción a function getter (lecciones 11+12).

---

## §8 Validación (workflow)

1. Editor en VS Code muestra squiggles rojos en tiempo real (lint).
2. UEFN → Tools → Verse → **Build Verse Code** ejecuta compilación real.
3. Build OUTPUT panel muestra "Compiled successfully" o lista errores.
4. **Plugin recomendado VS Code**: `usernamehw.errorlens` muestra errores inline.
5. Atajo `Ctrl+Shift+M` abre Problems panel con todos los errores agrupados.
6. Filtrar Problems por path `/lexosi@fortnite.com/RPG_Survival/Verse/` para ignorar errores de `Verse.digest.verse` (Epic, no nuestros).

### Errores típicos y traducción

| Código | Mensaje típico | Causa real |
|---|---|---|
| `3510` | "function returns X, but argument is Y" | Tipo inconsistente o cascade de error previo |
| `3512` | "archetype instantiation has 'transacts' effect, not allowed by context" | Lección 8/11 — class/struct construido top-level |
| `3547` | "Expected a type, got archetype constructor instead" | Lección 9 — struct literal donde se esperaba tipo |
| `3558` | "external{} only valid in .digest files" | Intento de usar external fuera de digest |
| `3593` | "Definition X is more accessible than its dependencies" | Lección 7/13 — visibility inconsistente |
| `vErr:S26` | "Missing label in path following /" | Lección 1 — placeholder `<ProjectName>` no interpretado |

---

## §9 Referencias cruzadas

- Spec sprint refactor: `docs/SPRINTS_BACKLOG.md` SPR-211
- Postmortem: `docs/POSTMORTEMS_INDEX.md` PM-SPR-211
- Daily Log día descubrimiento: `docs/DAILY_LOG.md` 2026-05-07
- Patrón generator script: `scripts/build/02_export_constants_to_verse.py` (post SPR-211 update)
