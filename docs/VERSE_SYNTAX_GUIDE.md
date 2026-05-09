# Verse Syntax Guide — RPG_Survival

> **Fuente única de verdad** para sintaxis Verse moderna en este proyecto.
> Cualquier doc autoritativo que contradiga este documento está OBSOLETO.
> Última actualización: 2026-05-09 (SPR-009 F-C-4-L1b — lección 16 + sub-corolarios A-D, post-H4).

---

## §1 Reglas inquebrantables (las 16 lecciones)

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

### Lección 14 — Archivos sin `module:` wrapper exportan al scope de la CARPETA padre

`PersistenceLayer.verse` con declaraciones top-level (sin `module:`) hace que sus tipos sean miembros de **`Verse/Core/`** (la carpeta), NO de `Verse/Core/PersistenceLayer/`.

```verse
# ❌ Falla con err 3506: "Unknown member 'PersistenceLayer' in 'Core'"
# Falla con err 3587: "The identifier 'PersistenceLayer' does not refer to a logical scope"
using { Verse.Core.PersistenceLayer }

# ✅ Funciona — importa toda la carpeta Core
using { /lexosi@fortnite.com/RPG_Survival/Verse/Core }
# o equivalente:
using { Verse.Core }
```

**Implicación**: Cores con state mutable (PersistenceLayer SPR-008) que NO pueden envolverse en `module:` (lección 5: weak_maps obligatorios top-level) comparten scope con otros Cores de la misma carpeta. Logger/TimeSync (que SÍ usan `module:`) tienen namespace propio y se importan dotted.

### Lección 15 — `set weak_map[K] = V` propaga `<decides>`

Escribir a weak_map es failable (la key puede no existir). Propaga `<decides>` al contexto.

```verse
# ❌ Falla con err 3512: "decides effect not allowed"
SavePlayerCore<public>(P:player, D:PlayerCore_V1)<transacts>:void=
    set PlayerCoreMap[P] = PlayerCore{V1 := option{D}}

# ✅ Funciona — if consume <decides>
SavePlayerCore<public>(P:player, D:PlayerCore_V1)<transacts>:void=
    if (set PlayerCoreMap[P] = PlayerCore{V1 := option{D}}) {}
```

El bloque `{}` vacío del `if` es intencional: no hace nada en éxito (la asignación ya ocurrió en la condición). En fallo improbable (key inválida), no se asigna y la función retorna sin error.

### Lección 16 — `event(t){}` literal top-level dentro de module/file scope falla 3512

`event(t)` es builtin Verse v1 (= `class(signalable(t), awaitable(t))`, ver `Verse.digest`). Construir una instancia `event(payload_t){}` como propiedad top-level (sea en file scope sin module wrapper, sea dentro de `module:`, sea como propiedad de `class<concrete>:` top-level sin `creative_device`) propaga `<transacts>` al contexto top-level `<computes>` puro y falla con err `3512`.

**Mismo patrón que lección 11** (struct literal top-level), pero aplicado a la primitiva `event(t)`.

```verse
# ❌ ROMPE con err 3512 (validado SPR-009 F-B investigación H1-H3)
LevelUp<public>:event(level_up_payload) = event(level_up_payload){}

# ❌ ROMPE igual dentro de module: (no resuelve)
LevelUp<public>:event(level_up_payload) = event(level_up_payload){}

# ❌ ROMPE igual dentro de class<concrete>: top-level (sin creative_device parent)
event_bus_module := class<concrete>:
    LevelUp<public>:event(level_up_payload) = event(level_up_payload){}
EventBus<public>:event_bus_module = event_bus_module{}

# ✅ FUNCIONA — class<concrete>(creative_device) (validado SPR-009 F-C-2/F-C-3a)
event_bus_device<public> := class<concrete>(creative_device):
    LevelUp<public>:event(level_up_payload) = event(level_up_payload){}
```

**Razón**: `creative_device` parent class redirige el contexto de instanciación al runtime de UEFN (el actor del nivel), no al top-level Verse `<computes>`. La propagación de `<transacts>` desde la inicialización de `event(t){}` se absorbe en el lifecycle del device.

**Implicación operativa**: el "EventBus singleton top-level" canonizado en versiones tempranas de los docs (BOOTSTRAP §11.5 v0, API §3.5 v0) **NO es viable**. Patrón vigente: `event_bus_device := class<concrete>(creative_device)` instanciado en Main.umap, referenciado desde otros devices vía `@editable Bus:event_bus_device`. Detalle en `BOOTSTRAP_PIPELINE.md` §11 (refactor F-C-4-L1 SPR-009).

#### Sub-corolario A — `event(t)` builtin NO implementa `subscribable`

En Verse v1 la primitiva `event<native>(t:type)<computes> := class(signalable(t), awaitable(t))` **NO incluye `subscribable`** (`Verse.digest`, validado runtime SPR-009 F-C-3a). Métodos `.Subscribe(handler)` / `.Unsubscribe(handler)` **no existen** sobre instancias `event(t)`. El único mecanismo de consumo es `Await()`.

#### Sub-corolario B — patrón consumer canónico = `spawn{}` + `Await()` loop

Sin `Subscribe`, el listener persistente se construye así:

```verse
OnBegin<override>()<suspends>:void=
    spawn { ListenLevelUp() }
    Sleep(0.0)  # OBLIGATORIO — ver sub-corolario C

ListenLevelUp()<suspends>:void=
    loop:
        Payload := Bus.LevelUp.Await()
        # ...handler logic...
```

#### Sub-corolario C — `Sleep(0.0)` post-`spawn{}` evita race silenciosa

El task lanzado con `spawn{}` no entra en `Await()` instantáneamente — necesita ceder control al scheduler. Si el `Signal` ocurre antes de que el spawned task alcance la primitiva `Await()`, el evento se pierde **silenciosamente** (no hay queue interna). `Sleep(0.0)` cede el control y garantiza que el spawned task esté en `Await` cuando vuelva el flujo principal. Validado SPR-009 F-C-3a runtime debug.

#### Sub-corolario D — `Signal()` es síncrono en Verse v1

`Bus.<Evento>.Signal(payload)` resume **dentro** de la llamada a Signal todos los `Await` suspendidos pendientes, **antes** de que Signal retorne. NO es fire-and-forget asíncrono. Implicación: el orden de logs "Handler invoked" → "Step N — Signal emitted" demuestra ejecución sincrónica del handler. Validado SPR-009 F-C-3a.

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

### §2.4 Core con state mutable (caso de estudio: PersistenceLayer SPR-008)

> Validado con build UEFN limpio + test in-session PASS (2026-05-08).

#### Patrón canónico

Para Cores que necesitan state persistente (`weak_map`), NO se puede usar `Module<public> := module:` (lección 5: weak_maps DEBEN ir top-level, no dentro de module). Patrón validado:

```verse
# Content/Verse/Core/PersistenceLayer.verse
using { /Verse.org/Simulation }
using { /UnrealEngine.com/Temporary/Diagnostics }
using { Verse.Core.Logger }

# Constantes de validación (top-level, sin 'var')
MAX_REASONABLE_GOLD:int = 1000000000

# Schema V1 (struct persistable)
PlayerCore_V1<public> := struct<persistable>:
    Gold:int = 0
    Level:int = 1
    XP:int = 0

# Wrapper option-version (class<final><persistable>)
PlayerCore<public> := class<final><persistable>:
    V1:?PlayerCore_V1 = false

# Weak_map top-level (única var top-level legal — lección 5)
var PlayerCoreMap:weak_map(player, PlayerCore) = map{}

# Load (effect <computes> default — Logger compatible)
LoadPlayerCore<public>(InPlayer:player):PlayerCore_V1=
    var CoreData:PlayerCore_V1 = PlayerCore_V1{}
    if (Existing := PlayerCoreMap[InPlayer]):
        if (V1Data := Existing.V1?):
            set CoreData = V1Data
    var SafeGold:int = CoreData.Gold
    if (SafeGold < 0):
        Logger.LogWarn("PersistenceLayer", "Gold negativo, corrigiendo")
        set SafeGold = 0
    if (SafeGold > MAX_REASONABLE_GOLD):
        Logger.LogWarn("PersistenceLayer", "Gold excede cap")
        set SafeGold = MAX_REASONABLE_GOLD
    PlayerCore_V1{Gold := SafeGold, Level := CoreData.Level, XP := CoreData.XP}

# Save (effect <transacts> — Logger INCOMPATIBLE, sin logging)
SavePlayerCore<public>(InPlayer:player, Data:PlayerCore_V1)<transacts>:void=
    if (set PlayerCoreMap[InPlayer] = PlayerCore{V1 := option{Data}}) {}
```

#### Reglas validadas (consolidan lecciones 5/8/14/15)

1. **Weak_maps top-level OBLIGATORIO** sin `module:` wrapper (lección 5).
2. **Constantes int top-level** SIN `var` permitidas (`MAX_X:int = N`).
3. **Acceso weak_map**: `if (Existing := MapName[Key])` SIN `?`. El access propaga `<decides>` que el `if` consume.
4. **Option-unwrap**: `if (V1Data := Existing.V1?)` CON `?`.
5. **Reasignación struct entera**: `set Var = NewStruct{...}`. NO `set Var.Field = X` (err 3509 — structs immutable).
6. **Vars locales mutables**: `var X:int = 0` + `set X = ...` permitido en función.
7. **Load sin `<transacts>`**: contexto `<computes>` default permite `Logger.LogWarn`.
8. **Save con `<transacts>`**: Logger INCOMPATIBLE (lección 9 nueva). Save silencioso.
9. **Save necesita if-wrap**: `if (set Map[K] = V) {}` consume `<decides>` propagado por weak_map write.
10. **Option literal**: `option{Data}` válido para construir option poblada.
11. **Archetype constructor como retorno**: `PlayerCore_V1{Field := SafeVar}` última línea OK en función `<computes>`.
12. **Import desde caller**: usar path absoluto a CARPETA, no a archivo (lección 14):
    - ✅ `using { /lexosi@fortnite.com/RPG_Survival/Verse/Core }`
    - ❌ `using { Verse.Core.PersistenceLayer }` (err 3506/3587)

#### Caller consume símbolos directos (sin prefijo)

```verse
# Desde Systems/Player/PlayerStats.verse
using { /lexosi@fortnite.com/RPG_Survival/Verse/Core }

OnPlayerSpawn(P:player):void=
    Core := LoadPlayerCore(P)         # Sin prefijo PersistenceLayer.
    NewCore := PlayerCore_V1{Gold := Core.Gold + 100, Level := Core.Level, XP := Core.XP}
    SavePlayerCore(P, NewCore)        # Save es <transacts>:void — llamada directa, sin if-wrap
```

#### Limitaciones reconocidas

- **Sin namespace propio**: símbolos de PersistenceLayer (`PlayerCore_V1`, `LoadPlayerCore`, etc.) comparten scope con Logger/TimeSync. Sin colisión actual pero vigilar futuro.
- **Save no loggea errors**: incompatibilidad effects `<transacts>` + `<no_rollback>` interno del Logger. Si SPR posterior necesita logging desde Save, opciones: (a) llamar Logger ANTES del set en caller, (b) wrapper `SavePlayerCore_Loud` que loggea antes.

#### Referencias

- Daily log: `docs/dailylog/DL_2026-05-08_SPR-008_lexosi.md`.
- Postmortem (si aplica): no requerido — SPR cerró sin incidentes graves.
- Test validation: `Content/Verse/Tests/test_persistence_SPR008.verse` con HUD PASS.

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
| `using { Verse.Core.PersistenceLayer }` (archivo sin module:) | `3506` + `3587` | 14 | `using { /lexosi@fortnite.com/RPG_Survival/Verse/Core }` (path a CARPETA) |
| `set weak_map[K] = V` directo en `<transacts>` | `3512` ('decides effect not allowed') | 15 | Envolver en `if (set Map[K] = V) {}` |
| `event(t){}` literal top-level / dentro module / dentro class<concrete>: sin creative_device | `3512` | 16 | `class<concrete>(creative_device)` con event(t) como propiedad |
| `Bus.<Evento>.Subscribe(handler)` sobre `event(t)` builtin Verse v1 | unknown identifier | 16 | `spawn { loop { Payload := Bus.<Evento>.Await() ; handler(Payload) } }` + `Sleep(0.0)` post-spawn |

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

### Reglas validadas SPR-008

| Effect | Compatible con `<computes>` default | Compatible con `<transacts>` |
|---|---|---|
| Logger.LogWarn / LogError / LogInfo | ✅ Sí | ❌ NO (err 3512 'no_rollback effect not allowed') |
| `set weak_map[K] = V` | Propaga `<decides>` al caller | Propaga `<decides>` al caller |
| Archetype constructor `T{...}` | ✅ OK como retorno | ✅ OK |
| `var Local:int = 0` + `set Local = X` | ✅ OK en función | ✅ OK en función |

**Implicación operativa**: funciones `<transacts>` (típicamente Save de persistencia) NO pueden loggear errores. Validación + logging va en `<computes>` default (típicamente Load).

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
