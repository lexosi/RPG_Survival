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

---

## 1. Filosofía del testing en UEFN

### 1.1 Realidad

- ❌ **No hay pytest, JUnit, Jest, ni framework standard de tests para Verse.**
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

> **Acceso a Core**: los 6 módulos Core (Logger, EventBus, TimeSync, PersistenceLayer, BigNumbers, AdminCommands) son singletons top-level (decisión D-A7). Se acceden por `using { /<ProjectName>/Core/<Modulo> }`, **NO** por `@editable`. Las constantes/vars module-scoped que mantienen las instancias se inicializan al cargar el módulo Verse, antes de que el editor instancie cualquier `creative_device` y por tanto antes de que cualquier `OnBegin` corra (afirmación de proceso interno del proyecto — sin cita literal Epic sobre orden exacto module-init vs OnBegin; comportamiento consistente con cómo Verse describe module-scoped variables en [Constants and Variables in Verse](https://dev.epicgames.com/documentation/en-us/fortnite/constants-and-variables-in-verse)). Detalle en `MODULES_DEPENDENCY_GRAPH.md` §2.1 + `API_REFERENCE_GENERATED.md` §3.

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

```verse
# /Content/Verse/Tests/test_device_SPR011.verse
using { /Fortnite.com/Devices }
using { /Verse.org/Simulation }
using { /UnrealEngine.com/Temporary/Diagnostics }
using { /<ProjectName>/Core/Logger }
using { /<ProjectName>/Core/ModuleRegistry }
using { /<ProjectName>/Generated/EventBusConstants }
using { /<ProjectName>/Generated/EventPayloads_Generated }

test_device_SPR011 := class(creative_device):

    var Received:logic = false

    OnLevelUp(Payload:level_up_payload):void=
        set Received = true
        # Payload.Player es player nativo Verse — el Logger lo formatea por defecto.
        Logger.LogInfo("test_device_SPR011", "Got level_up: {Payload.OldLevel}->{Payload.NewLevel}")

    OnBegin<override>()<suspends>:void=
        # Test: cuando PlayerStats sube nivel, EventBus.LevelUp se dispara

        # Setup: subscribe handler tipado al evento generado
        EventBus.LevelUp.Subscribe(OnLevelUp)

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
        Sleep(0.5)  # esperar a que el evento se propague
        if (Received?):
            Logger.LogInfo("test_device_SPR011", "✅ Integration PASS")
        else:
            Logger.LogError("test_device_SPR011", "❌ Integration FAIL: handler no recibió evento")
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

> **Acceso a Core (D-A7)**: `PersistenceLayer` es singleton top-level — NO `@editable`. Se accede por `using { /<ProjectName>/Core/PersistenceLayer }` y se llama `Persistence.LoadPlayerCore(InPlayer)` / `SavePlayerCore(InPlayer, Data)` (firmas reales de `API_REFERENCE_GENERATED.md` §3.4 — no hay setters granulares por campo, se carga el struct, se modifica, se guarda).

```verse
using { /Fortnite.com/Devices }
using { /Verse.org/Simulation }
using { /UnrealEngine.com/Temporary/Diagnostics }
using { /<ProjectName>/Core/Logger }
using { /<ProjectName>/Core/PersistenceLayer }

test_persistence_SPR008 := class(creative_device):
    @editable WriteButton:button_device = button_device{}
    @editable ReadButton:button_device = button_device{}
    @editable HUD:hud_message_device = hud_message_device{}

    OnBegin<override>()<suspends>:void=
        WriteButton.InteractedWithEvent.Subscribe(WriteTestData)
        ReadButton.InteractedWithEvent.Subscribe(ReadAndVerify)

    WriteTestData(Agent:agent):void=
        # Castear agent → player (los botones emiten agent; weak_map necesita player)
        if (P := player[Agent]):
            # Cargar struct, modificar, guardar (no hay setters granulares)
            var Core:PlayerCore = Persistence.LoadPlayerCore(P)
            set Core.Gold = 12345
            set Core.Gems = 678
            set Core.Level = 42
            Persistence.SavePlayerCore(P, Core)
            HUD.SetText(MakeMessage("Datos escritos. Cierra sesión y vuelve a entrar."))
        else:
            Logger.LogError("test_persistence_SPR008", "Agent no es player válido")

    ReadAndVerify(Agent:agent):void=
        if (P := player[Agent]):
            Core := Persistence.LoadPlayerCore(P)

            var Failures:int = 0
            if (Core.Gold <> 12345): set Failures += 1
            if (Core.Gems <> 678): set Failures += 1
            if (Core.Level <> 42): set Failures += 1

            if (Failures = 0):
                HUD.SetText(MakeMessage("✅ Persistence PASS"))
            else:
                HUD.SetText(MakeMessage("❌ Persistence FAIL: {Failures} mismatches"))
        else:
            Logger.LogError("test_persistence_SPR008", "Agent no es player válido")
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

### 9.2 Los archivos `.verse` se quedan

- Los `test_device_SPRxxx.verse` permanecen en `Content/Verse/Tests/`.
- No afectan al juego publicado (no están instanciados en level).
- Sirven para **regression testing** futuro.

### 9.3 Versionado Git

Carpeta `Content/Verse/Tests/` se commitea normal en Git. Es código del proyecto.

---

## 📌 Resumen ejecutivo

```
1. CADA SPR-xxx → tiene SPR-xxx-T asociado (con excepciones de la tabla 4.3)
2. SPR-xxx-T crea test_device_SPRxxx.verse en Content/Verse/Tests/
3. TÚ instancias el device en level, pulsas botones, ves HUD result
4. Antes de publish: borras devices del level con cleanup_tests.py
5. Smoke test master se queda permanente, valida que todo arranca

NO HAY UNIT TESTS COMO PYTEST. Esto es lo más cerca posible.
```

---

**Fin del documento.**
