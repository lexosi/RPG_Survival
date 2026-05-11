# Tests/test_admin_smoke.verse — SPR-010-T (SYS-070 smoke)
#
# Smoke test runtime para AdminCommands + AdminPanel. Instanciable en level UEFN.
# Configurar 1+ player_reference_device en este device (TestRefs) + jugar in-session.
#
# Done criteria validables en runtime:
# - Con TestRefs configurado a tu player → log "IsAdminLogic = true"
# - Sin TestRefs (array vacío) → log "IsAdminLogic = false"
# - Build UEFN sin warnings
# - Mobile Preview NO crashea
#
# NO es unit test (UEFN no expone framework). Es smoke device verifyando
# wiring de signatures + comportamiento end-to-end en build real.
#
# Versión simplificada per spec WARNING: evita var class-field + set dentro
# de for-loop (riesgo lección 20 no_rollback effect cross-context). Usa solo
# branches vacíos failable + IsAdminLogic non-failable + Print fuera de
# failure context (lección 19).

using { /Fortnite.com/Devices }
using { /Verse.org/Simulation }
using { /UnrealEngine.com/Temporary/Diagnostics }
using { /lexosi@fortnite.com/RPG_Survival/Verse/Core }

test_admin_smoke_device := class<concrete>(creative_device):

    # Test fixture: instancia 1 o más player_reference_device del editor aquí.
    # Para test "admin path" → asignar 1 ref con tu agent configurado.
    # Para test "non-admin path" → dejar array vacío.
    @editable TestRefs:[]player_reference_device = array{}

    OnBegin<override>()<suspends>:void=
        Print("[test_admin_smoke] OnBegin, TestRefs.Length = {TestRefs.Length}")
        for (P:Self.GetPlayspace().GetPlayers()):
            # Check failable IsAdmin: branches vacíos (Print desde failure context = err 3512).
            if (AdminCommands.IsAdmin[TestRefs, P]) {} else {}
            # IsAdminLogic devuelve :logic, almacenable fuera de failure context.
            IsAdminLogicResult:logic = AdminCommands.IsAdminLogic(TestRefs, P)
            IsAdminLogicStr:string = if (IsAdminLogicResult?) { "true" } else { "false" }
            Print("[test_admin_smoke] Player evaluated, IsAdminLogic = {IsAdminLogicStr}")
