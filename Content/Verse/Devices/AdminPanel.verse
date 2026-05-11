# Devices/AdminPanel.verse — SPR-010 (SYS-070)
#
# Device state-bearing del patrón §2.4-bis "Core stateless + Device state-bearing".
# State (AdminRefs) vive aquí como @editable, configurado en editor UEFN.
# Multi-admin = array de player_reference_device, 1 por admin permanente.
#
# F0 scope: solo identifica admins en OnBegin + Print debug. UI real (botones,
# input commands) en SPR F1+. ExecuteCommand stub en AdminCommands.
#
# Trampas documentadas (lección 17, API_REFERENCE §3.7):
# - Clear() limpia state device entero, NO unregister selectivo.
# - Activate() ends round/game, NO activate-reference.
# Ninguna se invoca en F0.
#
# Lección 19: Print() es no_rollback, NO usable en failure contexts.
# Para checks failable usamos pattern `if (cond[]) {} else {}` + Print fuera.

using { /Fortnite.com/Devices }
using { /Verse.org/Simulation }
using { /UnrealEngine.com/Temporary/Diagnostics }
using { /lexosi@fortnite.com/RPG_Survival/Verse/Core }

admin_panel_device := class<concrete>(creative_device):

    # Array de player_reference_device configurados en editor (1 por admin).
    # @editable: UEFN expone esto en Details panel del device en el level.
    @editable AdminRefs:[]player_reference_device = array{}

    OnBegin<override>()<suspends>:void=
        Print("[AdminPanel] OnBegin, AdminRefs configurados: {AdminRefs.Length}")
        # Smoke check: para cada player del playspace al inicio, identifica admin.
        # Pattern Epic-confirmed v5 PASS: option-wrapper + check failable + branches vacíos.
        for (P:Self.GetPlayspace().GetPlayers()):
            if (AdminCommands.IsAdmin[AdminRefs, P]) {} else {}
            # IsAdminLogic devuelve :logic, almacenable fuera de failure context.
            IsAdmin:logic = AdminCommands.IsAdminLogic(AdminRefs, P)
            IsAdminStr:string = if (IsAdmin?) { "true" } else { "false" }
            Print("[AdminPanel] Player evaluated, IsAdmin = {IsAdminStr}")
