# =====================================================================
# test_event_bus_smoke.verse — TEMPORARY TEST DEVICE.
# Borrar del level antes de publish público.
#
# Smoke test runtime de EventBus post-H4 (creative_device pattern).
# Valida: spawn monitor + Await() + Signal end-to-end con 1 evento (LevelUp).
#
# Patrón Verse v1: event(t) builtin implementa awaitable + signalable, NO
# subscribable. Consumer usa spawn{ Await() }, no .Subscribe(). Ver
# investigación F-B SPR-009 + F-C-3a-fix en POSTMORTEMS_INDEX.md.
#
# Race condition crítica: Sleep(0.0) post-spawn cede tick scheduler para
# garantizar monitor suspended en Await ANTES del Signal. Sin él, Signal
# se pierde porque task no está aún esperando.
#
# Anomalía documentada (resolverá F-C-4): TESTING_PROTOCOL §2.1 dice los Cores son
# singletons top-level (D-A7) accedidos via using, NO via @editable. EventBus post-H4
# es excepción — patrón H4 obliga @editable porque event_bus_device es creative_device,
# NO singleton top-level. Ver POSTMORTEMS_INDEX.md PM-SPR-009-blocked.
#
# Protocolo manual: instanciar test_event_bus_smoke + event_bus_device en mapa,
# conectar @editable Bus → event_bus_device, entrar sesión live, observar Logger.
# =====================================================================

using { /Fortnite.com/Devices }
using { /Verse.org/Simulation }
using { /UnrealEngine.com/Temporary/Diagnostics }
using { Verse.Core.Logger }
using { /lexosi@fortnite.com/RPG_Survival/Verse/Generated }
using { /lexosi@fortnite.com/RPG_Survival/Verse/Core }

test_event_bus_smoke := class(creative_device):

    # Excepción D-A7: ver header. event_bus_device NO es singleton top-level.
    @editable Bus:event_bus_device = event_bus_device{}

    # Tracker: handler recibió el evento?
    var Received<private>:logic = false

    # Monitor task: 1-shot await del Signal del Bus.
    # Patrón Verse v1: event(t) implementa awaitable, NO subscribable.
    # Consumer obligado a Await() en spawn{}, no .Subscribe().
    MonitorLevelUp()<suspends>:void =
        Payload := Bus.LevelUp.Await()
        set Received = true
        Logger.LogInfo("test_event_bus_smoke", "✅ Handler invoked, OldLevel={Payload.OldLevel} NewLevel={Payload.NewLevel}")

    OnBegin<override>()<suspends>:void =
        Logger.LogInfo("test_event_bus_smoke", "Smoke test starting...")

        # Step 1: Spawn monitor task que esperará Signal del Bus.
        spawn{ MonitorLevelUp() }
        Logger.LogInfo("test_event_bus_smoke", "Step 1 — Monitor spawned, awaiting Signal")

        # Step 2: Sleep(0.0) cede tick → garantiza monitor suspended en Await ANTES del Signal.
        # Sin este sleep, race condition: Signal antes de Await → evento perdido.
        Sleep(0.0)

        # Step 3: Obtener un player real del playspace para el payload
        AllPlayers := GetPlayspace().GetPlayers()
        if (TestPlayer := AllPlayers[0]):
            # Step 4: Signal el evento con payload sintético
            TestPayload := level_up_payload{
                Player := TestPlayer,
                OldLevel := 9,
                NewLevel := 10
            }
            Bus.LevelUp.Signal(TestPayload)
            Logger.LogInfo("test_event_bus_smoke", "Step 4 — Signal emitted")

            # Step 5: Verificar handler corrió (esperar propagación)
            Sleep(0.5)
            if (Received?):
                Logger.LogInfo("test_event_bus_smoke", "✅ SMOKE TEST PASS")
            else:
                Logger.LogError("test_event_bus_smoke", "❌ SMOKE TEST FAIL: monitor no recibió Signal (race condition?)")
        else:
            Logger.LogError("test_event_bus_smoke", "❌ No hay jugadores en playspace — entra en sesión live antes de instanciar el test")
