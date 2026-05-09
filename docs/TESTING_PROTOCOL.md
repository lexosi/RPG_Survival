# 🧪 TESTING_PROTOCOL — Sistema de validación para Verse

> **Verse no tiene pytest. Esta es la solución pragmática: `test_device.verse` temporales.**
> Lo más cercano a unit tests posible en UEFN.

---

## 🧭 Índice

1. [Filosofía del testing en UEFN](#1-filosofía-del-testing-en-uefn)
2. [Tipos de test](#2-tipos-de-test)
3. [Plantilla de test_device](#3-plantilla-de-test_device)
4. [Sprints de tipo SPR-TEST](#4-sprints-de-tipo-spr-test)
5. [Smoke test obligatorio antes de publish](#5-smoke-test-obligatorio-antes-de-publish)
6. [Testing de persistencia](#6-testing-de-persistencia)
7. [Testing de UI](#7-testing-de-ui)
8. [Testing móvil](#8-testing-móvil)
9. [Test cleanup](#9-test-cleanup)
10. [Tests estáticos Python (scripts/build/)](#10-tests-estáticos-python-scriptsbuild)

---

## 1. Filosofía del testing en UEFN

### 1.1 Realidad

- ❌ **No hay pytest, JUnit, Jest, ni framework standard de tests para código Verse en sí.**
- ✅ **Sí hay `unittest` stdlib para tests Python de scripts en `scripts/build/`** (introducido SPR-009 F-C-3b). Ver §10. Aplica a validadores, exporters, transformers — NO a código Verse.
- ❌ **No hay runner standalone CLI que ejecute tests sin UEFN abierto** (toolchain UEFN/Verse no expone build+test headless documentado).
- ❌ **No hay mocking puro de devices Fortnite.**
- ✅ **Tooling oficial Epic complementario** (no sustituye al device casero, pero usar):
  - **Multiplayer Previewing** ([dev.epicgames.com — Multiplayer Previewing](https://dev.epicgames.com/documentation/en-us/uefn/test-multiplayer-with-multiplayer-previewing-in-unreal-editor-for-fortnite)) — sesión local con N test players sin Push Changes.
  - **Sentry Device** — captura errores Verse en sesión live para debugging.
  - **Mobile Preview** ([dev.epicgames.com — Mobile Preview](https://dev.epicgames.com/documentation/en-us/fortnite/mobile-preview-session-in-unreal-editor-for-fortnite)) — perfil/layout móvil sin device físico (ver §8).
- ✅ Sí podemos: **crear un device temporal que instancia las clases nuevas y valida comportamiento.**

### 1.2 La regla de oro

> **Cada SPR-xxx que añade clase/lógica viene acompañado de un SPR-TEST-xxx que crea un test_device temporal.**

### 1.3 Lifecycle del test_device

```
1. SPR-xxx implementa la feature
   → archivos en Content/Verse/Systems/...

2. SPR-TEST-xxx implementa el test
   → archivo en Content/Verse/Tests/test_device_SPRxxx.verse

3. Tú (humano) instancias el test_device en UEFN
   → arrastras al level desde Content Browser

4. Tú ejecutas Push Changes y entras en sesión live
   → el test_device hace su trabajo automáticamente (o vía botón)

5. Tú verificas el output (HUD, console log)
   → ✅ PASS / ❌ FAIL

6. Tú borras el test_device del level
   → pero el archivo .verse se queda en Content/Verse/Tests/

7. Antes de publish: borras todos los test_devices del level
   → los archivos .verse pueden quedar en el proyecto
```

---

## 2. Tipos de test

### 2.1 Smoke Test
**Objetivo**: ¿se instancia sin crashear?

> **Acceso a Core**: 5 de los 6 módulos Core (Logger, TimeSync, PersistenceLayer, BigNumbers, AdminCommands) son singletons top-level (decisión D-A7). Se acceden por `using { /<ProjectName>/Core/<Modulo> }`, **NO** por `@editable`. Las constantes/vars module-scoped que mantienen las instancias se inicializan al cargar el módulo Verse, antes de que el editor instancie cualquier `creative_device` y por tanto antes de que cualquier `OnBegin` corra (afirmación de proceso interno del proyecto — sin cita literal Epic sobre orden exacto module-init vs OnBegin; comportamiento consistente con cómo Verse describe module-scoped variables en [Constants and Variables in Verse](https://dev.epicgames.com/documentation/en-us/fortnite/constants-and-variables-in-verse)).
>
> **Excepción D-A11 (post-SPR-009 F-C resolution)**: **EventBus es un `creative_device`**, NO singleton top-level. El test_device que necesite emitir/consumir eventos accede al EventBus vía `@editable Bus:event_bus_device = event_bus_device{}` (drag&drop la instancia en UEFN al editar el test_device). Razón: `event(t){}` top-level falla con err 3512 (lección 16 VERSE_SYNTAX_GUIDE). Detalle en `MODULES_DEPENDENCY_GRAPH.md` §2.1 + §4.2 + `BOOTSTRAP_PIPELINE.md` §11 + `API_REFERENCE_GENERATED.md` §3.5.

```verse
# /Content/Verse/Tests/test_device_SPR005.verse
using { /Fortnite.com/Devices }
using { /Verse.org/Simulation }
using { /UnrealEngine.com/Temporary/Diagnostics }
using { /<ProjectName>/Core/Logger }

test_device_SPR005 := class(creative_device):

    OnBegin<override>()<suspends>:void=
        # Smoke: simplemente llamar funciones públicas del singleton Logger
        Logger.LogInfo("test_device_SPR005", "Smoke test starting")
        Logger.LogDebug("test", "Debug message")
        Logger.LogWarn("test", "Warn message")
        Logger.LogError("test", "Error message")
        Logger.LogInfo("test_device_SPR005", "✅ Smoke test PASS")
```

### 2.2 Unit Test (lógica pura)
**Objetivo**: ¿la función devuelve lo esperado?

```verse
# /Content/Verse/Tests/test_device_SPR007.verse
using { /Fortnite.com/Devices }
using { /Verse.org/Simulation }
using { /UnrealEngine.com/Temporary/Diagnostics }
using { /<ProjectName>/Core/TimeSync }

test_device_SPR007 := class(creative_device):

    OnBegin<override>()<suspends>:void=
        # Test 1: GetUTCNow devuelve valor positivo
        Now := TimeSync.GetUTCNow()
        if (Now > 0):
            Print("✅ Test 1 PASS: GetUTCNow > 0")
        else:
            Print("❌ Test 1 FAIL: GetUTCNow returned {Now}")

        # Test 2: GetSecondsUntilNextHour devuelve 0-3600
        Secs := TimeSync.GetSecondsUntilNextHour()
        if (Secs >= 0 and Secs <= 3600):
            Print("✅ Test 2 PASS: SecondsUntilNextHour = {Secs}")
        else:
            Print("❌ Test 2 FAIL: SecondsUntilNextHour = {Secs}")

        # Test 3: IsInWindow consistencia
        Now2 := TimeSync.GetUTCNow()
        InWin := TimeSync.IsInWindow(Now2 - 100, 200)
        if (InWin):
            Print("✅ Test 3 PASS: IsInWindow detected correctly")
        else:
            Print("❌ Test 3 FAIL: IsInWindow not detecting")
```

### 2.3 Integration Test
**Objetivo**: ¿dos sistemas interactúan bien?

> **Acceso a Systems gameplay (Capa 2+)**: NO se inyectan por `@editable`. Se resuelven por lookup runtime vía `ModuleRegistry.GetPlayerStats()` (decisión D-A7 + workaround C2). Detalle en `MODULES_DEPENDENCY_GRAPH.md` §4.7.
>
> **Acceso a EventBus**: SÍ por `@editable Bus:event_bus_device = event_bus_device{}` (excepción D-A11 — EventBus es `creative_device`, no singleton top-level). Drag&drop la instancia de EventBusDevice del nivel en UEFN al instanciar el test_device.
>
> **Patrón consumer canónico**: `event(t)` builtin Verse v1 NO implementa `subscribable` — `.Subscribe(handler)` y `.Unsubscribe(handler)` **no existen**. Único mecanismo de consumo = `Await()`. Listener persistente = `spawn { ListenerFn() } ; Sleep(0.0)` post-spawn + `ListenerFn()<suspends>:void= loop { Payload := Bus.<Evento>.Await() ; <handler>(Payload) }`. `Sleep(0.0)` post-spawn obligatorio (evita race Signal-antes-de-Await). `Signal()` síncrono. Detalle en `VERSE_SYNTAX_GUIDE.md` §1 lección 16.

```verse
# /Content/Verse/Tests/test_device_SPR011.verse
using { /Fortnite.com/Devices }
using { /Verse.org/Simulation }
using { /UnrealEngine.com/Temporary/Diagnostics }
using { /<ProjectName>/Core/Logger }
using { /<ProjectName>/Core/ModuleRegistry }
using { /<ProjectName>/Generated/EventBusDevice }
using { /<ProjectName>/Generated/EventPayloads_Generated }

test_device_SPR011 := class(creative_device):

    # Drag & drop la instancia de EventBusDevice del nivel en UEFN al editar este test_device.
    @editable Bus:event_bus_device = event_bus_device{}

    var Received:logic = false

    OnBegin<override>()<suspends>:void=
        # Test: cuando PlayerStats sube nivel, Bus.LevelUp se dispara

        # Setup: spawn listener que escucha LevelUp en bucle hasta recibir
        spawn { ListenLevelUp() }
        Sleep(0.0)  # OBLIGATORIO — cede control al scheduler para que el spawned task entre en Await
                    # ANTES de que se emita el primer Signal. Sin él, race condition silenciosa.

        # Obtener un player real del playspace (1er jugador conectado).
        # Patrón canónico Epic: Self.GetPlayspace().GetPlayers()[0].
        # Si el test corre antes de que entre algún jugador, abortamos.
        AllPlayers := GetPlayspace().GetPlayers()
        if (TestPlayer := AllPlayers[0]):
            # Act: simulate level up vía lookup runtime
            if (PlayerStats := ModuleRegistry.GetPlayerStats[]):
                PlayerStats.SimulateLevelUp(TestPlayer)
            else:
                Logger.LogError("test_device_SPR011", "PlayerStats no registrado en Registry")
                return
        else:
            Logger.LogError("test_device_SPR011", "❌ No hay jugadores en el playspace — entra en sesión live antes de instanciar el test")
            return

        # Assert
        Sleep(0.5)  # esperar a que el evento se propague (Signal síncrono, pero damos margen extra)
        if (Received?):
            Logger.LogInfo("test_device_SPR011", "✅ Integration PASS")
        else:
            Logger.LogError("test_device_SPR011", "❌ Integration FAIL: handler no recibió evento")

    ListenLevelUp()<suspends>:void=
        # Loop persistente. En este test solo necesitamos UNA emisión, pero el patrón
        # canónico es loop{} para listener vivo. Salimos tras la primera asignación
        # de Received para evitar que el spawned task se quede bloqueado en futuros tests.
        loop:
            Payload := Bus.LevelUp.Await()
            # Payload.Player es player nativo Verse — el Logger lo formatea por defecto.
            Logger.LogInfo("test_device_SPR011", "Got level_up: {Payload.OldLevel}->{Payload.NewLevel}")
            set Received = true
            break  # cerrar loop tras primera ocurrencia (test one-shot)
```

### 2.4 Persistence Test
**Objetivo**: ¿los datos sobreviven a logout/login?

Ver sección 6 más abajo, requiere protocolo especial.

### 2.5 Performance Test
**Objetivo**: ¿una operación masiva se ejecuta en tiempo razonable?

```verse
test_device_SPR050 := class(creative_device):
    OnBegin<override>()<suspends>:void=
        # Obtener jugador de prueba del playspace
        if (TestPlayer := GetPlayspace().GetPlayers()[0]):
            # Crear 300 entries en Dex y medir
            Start := GetSimulationElapsedTime()

            for (i := 0..299):
                DexService.AddEntry(TestPlayer, i)

            Elapsed := GetSimulationElapsedTime() - Start
            if (Elapsed < 1.0):
                Print("✅ Perf PASS: 300 inserts en {Elapsed}s")
            else:
                Print("⚠️ Perf SLOW: 300 inserts tomaron {Elapsed}s")
        else:
            Print("❌ No hay jugador en playspace — entra en sesión live")
```

---

## 3. Plantilla de test_device

### 3.1 Plantilla base

```verse
# /Content/Verse/Tests/test_device_SPRxxx.verse
# TEMPORARY TEST DEVICE — borrar del level antes de publish.

using { /Fortnite.com/Devices }
using { /Verse.org/Simulation }
using { /UnrealEngine.com/Temporary/Diagnostics }

# Importa el sistema bajo test
# NOTA: <ProjectName> = nombre del proyecto UEFN (root real del path Verse).
# Sustituir por el nombre real al instanciar la plantilla.
using { /<ProjectName>/Systems/Player }
using { /<ProjectName>/Core }

test_device_SPRxxx := class(creative_device):
    # === EDITABLE REFERENCES ===
    # Drag & drop estos en UEFN al instanciar el test_device
    @editable HUDDisplay:hud_message_device = hud_message_device{}

    # === TEST CONFIG ===
    @editable RunOnBegin:logic = true
    @editable ManualTriggerButton:button_device = button_device{}

    # === TEST STATE ===
    var TestsPassed:int = 0
    var TestsFailed:int = 0

    OnBegin<override>()<suspends>:void=
        # Subscribe al botón para tests manuales
        ManualTriggerButton.InteractedWithEvent.Subscribe(OnButtonPressed)

        if (RunOnBegin):
            RunAllTests()

    OnButtonPressed(Agent:agent):void=
        spawn{ RunAllTests() }

    RunAllTests()<suspends>:void=
        set TestsPassed = 0
        set TestsFailed = 0

        Print("====== STARTING TESTS FOR SPR-XXX ======")

        Test1_CanInstantiate()
        Test2_BasicFunction()
        Test3_EdgeCases()
        # ... más tests ...

        Print("====== RESULTS ======")
        Print("✅ Passed: {TestsPassed}")
        Print("❌ Failed: {TestsFailed}")

        if (TestsFailed = 0):
            HUDDisplay.SetText(MakeMessage("ALL TESTS PASS"))
        else:
            HUDDisplay.SetText(MakeMessage("FAILED: {TestsFailed} tests"))

    Test1_CanInstantiate():void=
        # ... lógica del test ...
        if (condition_pass):
            set TestsPassed += 1
            Print("✅ Test1 PASS")
        else:
            set TestsFailed += 1
            Print("❌ Test1 FAIL: <razón>")

    Test2_BasicFunction():void=
        # ...
        Pass

    Test3_EdgeCases():void=
        # ...
        Pass
```

### 3.2 Helper functions reutilizables

Mantener en `Content/Verse/Tests/test_helpers.verse`:

```verse
test_helpers := module:
    AssertEqual<public>(Expected:int, Actual:int, TestName:string):logic=
        if (Expected = Actual):
            Print("✅ {TestName} PASS: {Actual}")
            return true
        else:
            Print("❌ {TestName} FAIL: expected {Expected}, got {Actual}")
            return false

    AssertTrue<public>(Condition:logic, TestName:string):logic=
        if (Condition):
            Print("✅ {TestName} PASS")
            return true
        else:
            Print("❌ {TestName} FAIL")
            return false

    AssertNotEmpty<public>(Arr:[]int, TestName:string):logic=
        if (Arr.Length > 0):
            Print("✅ {TestName} PASS: array has {Arr.Length} elements")
            return true
        else:
            Print("❌ {TestName} FAIL: array empty")
            return false

    # Helper para construir `message` desde string literal (Verse no expone constructor directo).
    # Verse exige el specifier `<localizes>` en cualquier función que devuelva `message`.
    # Ver doc oficial: https://dev.epicgames.com/documentation/en-us/fortnite/string-and-message-types-in-verse
    MakeMessage<public><localizes>(Text:string):message = "{Text}"
```

> **Nota sobre `MakeMessage`**: las plantillas §3.1 y §6 invocan `MakeMessage("...")` para construir el `message` que `hud_message_device.SetText` espera. **No es función built-in Verse** — debe declararse con specifier `<localizes>` como en el bloque anterior y vivir en `test_helpers.verse` (importable desde cualquier `test_device_SPRxxx.verse`).

---

## 4. Sprints de tipo SPR-TEST

### 4.1 Naming convention

- Sprint principal: `SPR-005` (Module Registry)
- Sprint test asociado: `SPR-005-T` (Test for Module Registry)

### 4.2 Plantilla de sprint test

```markdown
### SPR-XXX-T — Test del SPR-XXX

- **Fase**: misma que SPR-XXX
- **Sistema(s)**: SYS-xxx (testing of)
- **Dependencias**: SPR-XXX completo
- **Tipo**: verse-test
- **Tiempo estimado**: 30 min - 1h
- **Archivos a crear**:
  - `Content/Verse/Tests/test_device_SPRxxx.verse`
- **Tests a implementar**:
  - [ ] Smoke test (instanciar + llamar funciones públicas)
  - [ ] Unit test 1: [comportamiento concreto]
  - [ ] Unit test 2: [edge case]
  - [ ] Integration test (si aplica): [interacción con otro sistema]
- **Done criteria**:
  - [ ] Compila sin warnings
  - [ ] Test_device se puede instanciar en level
  - [ ] Al ejecutar, todos los tests salen ✅
  - [ ] HUD muestra "ALL TESTS PASS" o lista de fallos
  - [ ] Test_device se puede borrar sin afectar al sistema bajo test
```

### 4.3 Cuándo es obligatorio SPR-TEST

| Tipo de SPR | ¿SPR-TEST obligatorio? |
|---|---|
| Verse: nueva clase pública | ✅ SÍ |
| Verse: módulo de Core/ | ✅ SÍ |
| Verse: lógica de persistencia | ✅✅ SÍ + persistence test |
| Verse: nueva UI | ✅ SÍ + manual visual test |
| Python: pipeline build | ✅ SÍ (test del script python con dummy data) |
| JSON: solo data | ❌ NO (validación con script Python ya tiene SPR-003) |
| Verse: cambio menor | ❌ NO (smoke test del existente vale) |

---

## 5. Smoke test obligatorio antes de publish

### 5.1 El smoke_test_master

Mantener un device permanente que ejecuta TODOS los smoke tests al inicio:

```verse
# /Content/Verse/Tests/smoke_test_master.verse
# Permanent test device. Solo ejecuta SMOKE tests al iniciar.
# NO se borra antes de publish (es safe, solo loggea).

smoke_test_master := class(creative_device):
    @editable RunOnPublish:logic = false  # ⚠️ Desactivar antes de publish

    OnBegin<override>()<suspends>:void=
        if (RunOnPublish):
            Print("====== SMOKE TESTS START ======")

            # Llamar a todos los smoke tests
            SmokeSPR005.RunSmokeTest()
            SmokeSPR006.RunSmokeTest()
            SmokeSPR007.RunSmokeTest()
            # ... etc ...

            Print("====== SMOKE TESTS DONE ======")
```

### 5.2 Checklist pre-publish

```
[ ] Smoke test master ejecuta sin errors
[ ] Mobile Preview no crashea
[ ] Logout + login persiste datos correctamente
[ ] Todos los test_devices SPR-xxx-T borrados del level
[ ] Sin warnings de compilación Verse
[ ] Memory budget dentro de threshold (Python script lo verifica)
[ ] Activity Log UI no satura
[ ] Eventos hora-en-punto disparan correctamente (esperar 1 ciclo)
```

---

## 6. Testing de persistencia

### 6.1 Protocolo de persistence test

Es **el más complejo** porque requiere logout + login.

> **Acceso a Core**: `PersistenceLayer.verse` no usa `module:` wrapper (weak_maps obligatorios top-level — lección 5 VERSE_SYNTAX_GUIDE). Sus símbolos viven en el scope de la carpeta `Verse/Core/`. Imports: dotted moderno para Logger, path absoluto a CARPETA para tipos/funciones de PersistenceLayer. Funciones top-level se llaman SIN prefijo `Persistence.`. Spec en `VERSE_SYNTAX_GUIDE.md` §2.4 + `API_REFERENCE_GENERATED.md` §3.4.

> **Plantilla actualizada SPR-008 (2026-05-08)**. Versión real validada con build UEFN limpio + test in-session PASS. Mirror del archivo `Content/Verse/Tests/test_persistence_SPR008.verse`.

```verse
using { /Fortnite.com/Devices }
using { /Verse.org/Simulation }
using { /UnrealEngine.com/Temporary/Diagnostics }
using { /UnrealEngine.com/Temporary/UI }
using { Verse.Core.Logger }
using { /lexosi@fortnite.com/RPG_Survival/Verse/Core }

test_persistence_SPR008 := class(creative_device):

    @editable WriteButton:button_device = button_device{}
    @editable ReadButton:button_device = button_device{}
    @editable HUD:hud_message_device = hud_message_device{}

    OnBegin<override>()<suspends>:void=
        Logger.LogInfo("test_persistence_SPR008", "Device iniciado. Pulsar Write → logout → login → Read.")
        WriteButton.InteractedWithEvent.Subscribe(WriteTestData)
        ReadButton.InteractedWithEvent.Subscribe(ReadAndVerify)

    WriteTestData(Agent:agent):void=
        if (P := player[Agent]):
            # Reasignación struct entera (structs immutable — set Var.Field = X falla con err 3509).
            # SPR-008 mínimo: solo Gold/Level/XP en PlayerCore_V1 (sin Gems).
            TestData:PlayerCore_V1 = PlayerCore_V1{Gold := 12345, Level := 42, XP := 67890}
            SavePlayerCore(P, TestData)
            Logger.LogInfo("test_persistence_SPR008", "WRITE — Gold=12345, Level=42, XP=67890")
            HUD.SetText(MakeMessage("Datos escritos. Logout completo + login + pulsar Read."))
        else:
            Logger.LogError("test_persistence_SPR008", "WRITE — Agent no es player válido")
            HUD.SetText(MakeMessage("ERROR: agent no es player"))

    ReadAndVerify(Agent:agent):void=
        if (P := player[Agent]):
            # LoadPlayerCore retorna versión activa (V1), no wrapper.
            LoadedData:PlayerCore_V1 = LoadPlayerCore(P)
            var Failures:int = 0
            if (LoadedData.Gold <> 12345):
                set Failures = Failures + 1
                Logger.LogError("test_persistence_SPR008", "Gold mismatch")
            if (LoadedData.Level <> 42):
                set Failures = Failures + 1
                Logger.LogError("test_persistence_SPR008", "Level mismatch")
            if (LoadedData.XP <> 67890):
                set Failures = Failures + 1
                Logger.LogError("test_persistence_SPR008", "XP mismatch")
            if (Failures = 0):
                HUD.SetText(MakeMessage("PERSISTENCE PASS"))
            else:
                HUD.SetText(MakeMessage("PERSISTENCE FAIL: {Failures} mismatches"))
        else:
            Logger.LogError("test_persistence_SPR008", "READ — Agent no es player válido")
            HUD.SetText(MakeMessage("ERROR: agent no es player"))

    MakeMessage<localizes>(Text:string):message = "{Text}"
```

### 6.2 Procedimiento manual

1. Instanciar `test_persistence_SPR008` en level
2. Conectar 2 buttons (Write + Read) y 1 HUD message
3. Push Changes
4. Entrar a sesión live
5. Pulsar **Write** button → ver mensaje
6. **Cerrar sesión completamente** (salir del juego, no solo del level)
7. **Volver a entrar**
8. Pulsar **Read** button
9. Ver si HUD dice ✅ PASS o ❌ FAIL

Si pasa → la persistencia funciona end-to-end.

### 6.3 ⚠️ Limitaciones

- No se puede automatizar el logout. Requiere acción humana.
- Solo se puede testear con **una cuenta** a la vez.
- Para testing multi-jugador, repetir manual.

---

## 7. Testing de UI

### 7.1 No se puede automatizar

UI requiere ojo humano. **Sí podemos hacer**:

- **Visual checklist** en cada SPR-TEST de UI
- **Comparación side-by-side** con UI_UX_STYLE_GUIDE.md
- **Mobile Preview** obligatorio

### 7.2 Plantilla visual checklist

```markdown
## Visual checklist para SPR-XXX-T (UI)

### Desktop preview
- [ ] Colores match con UI_UX_STYLE_GUIDE
- [ ] Tipografía legible
- [ ] Padding/spacing consistente
- [ ] Fade times correctos
- [ ] Sin overlap con HUD del juego
- [ ] Sin solapes con notification log

### Mobile preview (CRITICAL)
- [ ] Tap targets ≥ 44px
- [ ] Texto legible sin zoom
- [ ] Layout no se rompe en 380px width
- [ ] Botones no muy juntos (mis-click prevention)
- [ ] Performance >50fps con UI abierta
```

---

## 8. Testing móvil

### 8.1 Workflow obligatorio

```
1. Implementar feature
2. Test in-session desktop primero (PC UEFN)
3. Push Changes
4. Open Mobile Preview (UEFN > Mobile Preview)
5. Test todas las interacciones touch
6. Verificar fps con Stats > FPS
7. Si fps cae >20%: optimizar antes de continuar
```

### 8.2 Métricas mínimas

| Métrica | Mínimo aceptable |
|---|---|
| FPS estable | ≥30 (≥45 ideal) |
| Tap response time | ≤100ms |
| Memoria runtime | ≤2GB |
| Texturas en memoria | ≤512MB |

---

## 9. Test cleanup

### 9.1 Antes de publish

**OBLIGATORIO**: borrar todos los test_devices del level.

#### Cómo hacerlo rápido

```python
# scripts/build/cleanup_tests.py
# Borra todos los actors del level cuyo nombre empiece con "test_device_"
#
# REQUISITO: UEFN debe exponer el Python Editor Script Plugin con la subsystem
# `unreal.EditorActorSubsystem`. UEFN solo expone un subset del Python API de UE5
# standalone — validar empíricamente antes de depender de este script. Si la
# subsystem no está disponible, ver §9.1.1 (fallback manual).

import unreal

def cleanup_test_devices():
    actor_sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    all_actors = actor_sub.get_all_level_actors()

    test_actors = [a for a in all_actors if a.get_actor_label().startswith("test_device_")]

    for actor in test_actors:
        unreal.log(f"Removing test device: {actor.get_actor_label()}")
        actor_sub.destroy_actor(actor)

    unreal.log(f"Cleanup done. Removed {len(test_actors)} test devices.")

if __name__ == "__main__":
    cleanup_test_devices()
```

Ejecutar antes de publish: `Tools > Execute Python Script > cleanup_tests.py`.

#### 9.1.1 Fallback manual (si UEFN no expone EditorActorSubsystem)

1. En UEFN World Outliner, filtra por `test_device_` en la barra de búsqueda.
2. Selecciona todos los resultados (Ctrl+A en la lista filtrada).
3. Tecla `Delete` para borrarlos del level.
4. Verifica que el filtro vuelve vacío antes de Push Changes.

Documentar en postmortem si el script Python falla por API no expuesta — ajustar §9.1 al script soportado realmente por UEFN.

### 9.2 Los archivos de test se quedan

- Los `test_device_SPRxxx.verse` permanecen en `Content/Verse/Tests/`. No afectan al juego publicado (no están instanciados en level). Sirven para regression testing futuro.
- Los tests Python en `scripts/build/tests/` permanecen siempre. Se ejecutan en pre-commit / on-demand. NO requieren cleanup. Ver §10.

### 9.3 Versionado Git

Carpeta `Content/Verse/Tests/` se commitea normal en Git. Es código del proyecto.

---

## 10. Tests estáticos Python (scripts/build/)

### 10.1 Filosofía

> **Tests Python validan outputs de scripts en `scripts/build/`. Test_devices Verse validan runtime in-session. Son complementarios, no excluyentes.**

Introducidos en SPR-009 F-C-3b para cubrir un gap: el exporter `02_export_constants_to_verse.py` puede regresar silenciosamente (renombrar evento, perder visibility specifier, romper idempotencia) y solo se detectaría en build UEFN posterior — caro de diagnosticar. Test estático Python = primera línea de defensa, ejecuta en milisegundos sin UEFN abierto.

### 10.2 Cuándo crear test Python (vs test_device Verse)

| Si el sprint... | Tipo de test |
|---|---|
| Implementa script en `scripts/build/` (validador, exporter, transformer) | **Test Python** |
| Implementa clase/módulo Verse con lógica runtime | **test_device Verse** (§3) |
| Implementa script Python que genera Verse | **Ambos** — Python valida output estático, test_device valida runtime |
| Modifica schema JSON existente | **Test Python** (validador) |
| Modifica weak_map persistence | **test_device Verse** (§6) |

### 10.3 Framework

- **Stdlib `unittest`**. NO pytest. NO deps externas. Razón: cero requirements.txt overhead, alineado con resto proyecto.
- Patrón: `class TestX(unittest.TestCase)` con métodos `test_<aspecto>`.
- Invocación: `python -m unittest scripts.build.tests.test_<name> -v`.

### 10.4 Estructura de archivos canónica

```
scripts/build/tests/
├── __init__.py                              # vacío, marca package
├── fixtures/
│   └── <thing>_expected_contract.json       # contrato semántico esperado
├── test_<thing>.py                          # test runner unittest
└── test_<otra_cosa>.py
```

**Reglas**:
- `__init__.py` vacío (no docstring, no código).
- Fixtures como JSON con campo `_doc` describiendo el contrato + campos `_*` meta + lista `expected_*`.
- Test runners: 1 por unidad bajo test (1 exporter = 1 file).
- NO golden-files completos `.verse`/`.json` checked-in. Usar **contratos semánticos** (lista `[(name, type, visibility), ...]`) — frágiles solo a cambios contractuales reales, no cosméticos.

### 10.5 Naming

| Item | Convención |
|---|---|
| Test file | `test_<unit_under_test>.py` (ej. `test_exporter_event_bus.py`) |
| Test class | `class Test<UnitUnderTest>(unittest.TestCase)` (ej. `TestExporterEventBus`) |
| Test method | `test_<aspecto_específico>` (ej. `test_idempotency`) |
| Fixture | `<unit>_expected_contract.json` (ej. `event_bus_expected_contract.json`) |

### 10.6 Cobertura mínima recomendada para tests de exporters

1. **Estructura**: declaration root presente e intacta (class/struct/module top-level).
2. **Contrato**: cada item esperado presente con nombre + tipo + visibility correctos.
3. **Count match**: número de items generados == número esperado en contrato.
4. **No drift positivo**: no hay items generados fuera del contrato.
5. **Idempotencia**: re-ejecutar exporter 2× consecutivas produce mismo hash SHA256.

### 10.7 Cuándo correr

| Trigger | Comando |
|---|---|
| Pre-commit (candidato hook futuro) | `python -m unittest discover scripts/build/tests/ -v` |
| Manual on-demand durante debugging | `python -m unittest scripts.build.tests.test_<name> -v` |
| **OBLIGATORIO** tras editar cualquier script en `scripts/build/` | full discover antes de commit |
| Tras regenerar archivos `Generated/` | full discover (cubre idempotencia) |

### 10.8 Lifecycle de un test Python

```
1. SPR-xxx implementa/modifica script en scripts/build/
2. Crear/actualizar fixture de contrato esperado en scripts/build/tests/fixtures/
3. Crear/actualizar test runner en scripts/build/tests/test_<name>.py
4. Ejecutar: python -m unittest scripts.build.tests.test_<name> -v
5. Si todos PASS → commit junto con el script editado
6. Si algún FAIL → diagnosticar:
   - ¿Bug en script? → arreglar script.
   - ¿Drift legítimo en contrato? → actualizar fixture, NO el test.
   - ¿Bug en test? → arreglar test, NO silenciar el FAIL.
```

### 10.9 Ejemplo de referencia (canónico)

`scripts/build/tests/test_exporter_event_bus.py` (introducido F-C-3b, SPR-009):

- 5 tests cubren `02_export_constants_to_verse.py::export_event_bus()`.
- Fixture: `fixtures/event_bus_expected_contract.json` (9 eventos, contrato semántico).
- Cobertura: class declaration + count + contrato per-event + drift positivo + idempotencia.
- Runtime: ~0.13s.
- Sin deps externas.

**Replicar este patrón para futuros tests** de validadores/exporters/transformers en `scripts/build/`.

### 10.10 Limitaciones reconocidas

- NO valida compilación Verse — eso es test_device runtime in-session (§3) o build UEFN.
- NO valida schema JSON catalog — eso es `01_validate_jsons.py` separado.
- NO valida reglas semánticas cross-archivo (ej. event referenciado en código Verse pero ausente en catalog) — futuro test integrador, scope distinto.
- Idempotencia detecta determinismo, no correctness. Un exporter idempotentemente buggy seguirá pasando.

---

## 📌 Resumen ejecutivo

```
1. CADA SPR-xxx → tiene SPR-xxx-T asociado (con excepciones de la tabla 4.3)
2. SPR-xxx-T crea test_device_SPRxxx.verse en Content/Verse/Tests/
3. TÚ instancias el device en level, pulsas botones, ves HUD result
4. Antes de publish: borras devices del level con cleanup_tests.py
5. Smoke test master se queda permanente, valida que todo arranca
6. Sprints que tocan scripts/build/ → tests Python unittest (§10) complementan los test_devices Verse

NO HAY UNIT TESTS PARA VERSE COMO PYTEST. Para Python build scripts SÍ — ver §10.
```

---

**Fin del documento.**
