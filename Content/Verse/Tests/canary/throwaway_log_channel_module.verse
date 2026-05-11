# AUTO-GENERATED throwaway — F-CLEAN-LOGGER-FIX pre-refactor v3 plan B1a (2026-05-11)
# Objetivo v3: validar plan B1a (Logger device pattern) tras v1 + v2 FAIL:
#   - log{} archetype DENTRO creative_device (parent absorbe <transacts>,
#     mismo mecanismo que H4 EventBus device validado SPR-009)
#   - Métodos device invocan LogInstance.Print() incluyendo failable context
#
# Historial cadena:
# v1 hash 35F6E8D80FF... FAIL Escenario A — log{} dentro module: propaga transacts
# v2 hash B57675478E4... FAIL Escenario A — log{} top-level también propaga transacts
# v3 (esta) — log{} dentro creative_device → expected PASS por precedente H4
#
# Si v3 PASS → Logger.verse refactor procede plan B1a (breaking change consumers).
# Si v3 FAIL inesperado → STOP total, plan C necesario.
#
# Refs:
# - VERSE_SYNTAX_GUIDE §1 lección 16 (event(t){} top-level falla por mismo mecanismo)
# - CHANGELOG D-A11 (EventBus device excepción canónica)
# - HANDOFF v3.1 §4.4 drift §2.4 #7

using { /Verse.org/Simulation }
using { /UnrealEngine.com/Temporary/Diagnostics }
using { /Fortnite.com/Devices }

rpg_log_channel := class(log_channel){}

logger_device_test := class<concrete>(creative_device):

    LogInstance:log = log{ Channel := rpg_log_channel }

    # Escenario A — invocación normal desde method del device.
    TestNormalContext<public>():void=
        LogInstance.Print("scenario A: device pattern OK")

    # Escenario B — failable context desde method <suspends> del device.
    # Si compila → Logger device invocable desde decides/failable functions.
    # Cierra restricción lección 19 vía device parent que absorbe <transacts>.
    TestFailableContext<public>(X:?int)<suspends>:void=
        if (Val := X?):
            LogInstance.Print("scenario B: failable from device OK, val={Val}")
