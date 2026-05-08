using { Core }

# =====================================================================
# test_persistence_SPR008.verse — TEMPORARY TEST DEVICE.
# Borrar del level antes de publish público.
#
# Test in-session de persistencia para SPR-008 (PersistenceLayer).
# Protocolo: Write button → logout completo → login → Read button → HUD result.
#
# Drift fix vs TESTING_PROTOCOL §6.1: usa imports dotted (post-SPR-211),
# funciones top-level directas (sin module wrapper Persistence.),
# tipo PlayerCore_V1 (versión activa, no wrapper PlayerCore),
# reasignación struct entera (structs immutable).
# =====================================================================

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
            # Construir struct con valores conocidos. Reasignación entera (structs immutable).
            TestData:PlayerCore_V1 = PlayerCore_V1{Gold := 12345, Level := 42, XP := 67890}
            # Save es <transacts>. La llamada puede ser failable (set weak_map propaga decides).
            # Probar primero con paréntesis. Si build falla aquí con err 3512, cambiar a corchetes [].
            SavePlayerCore(P, TestData)
            Logger.LogInfo("test_persistence_SPR008", "WRITE — Gold=12345, Level=42, XP=67890. Cierra sesión y vuelve a entrar.")
            HUD.SetText(MakeMessage("Datos escritos. Logout completo + login + pulsar Read."))
        else:
            Logger.LogError("test_persistence_SPR008", "WRITE — Agent no es player válido")
            HUD.SetText(MakeMessage("ERROR: agent no es player"))

    ReadAndVerify(Agent:agent):void=
        if (P := player[Agent]):
            LoadedData:PlayerCore_V1 = LoadPlayerCore(P)
            Logger.LogInfo("test_persistence_SPR008", "READ — Gold={LoadedData.Gold}, Level={LoadedData.Level}, XP={LoadedData.XP}")
            var Failures:int = 0
            if (LoadedData.Gold <> 12345):
                set Failures = Failures + 1
                Logger.LogError("test_persistence_SPR008", "Gold mismatch: esperado 12345, leído {LoadedData.Gold}")
            if (LoadedData.Level <> 42):
                set Failures = Failures + 1
                Logger.LogError("test_persistence_SPR008", "Level mismatch: esperado 42, leído {LoadedData.Level}")
            if (LoadedData.XP <> 67890):
                set Failures = Failures + 1
                Logger.LogError("test_persistence_SPR008", "XP mismatch: esperado 67890, leído {LoadedData.XP}")
            if (Failures = 0):
                Logger.LogInfo("test_persistence_SPR008", "PERSISTENCE PASS — todos los valores match")
                HUD.SetText(MakeMessage("PERSISTENCE PASS"))
            else:
                Logger.LogError("test_persistence_SPR008", "PERSISTENCE FAIL — {Failures} mismatches")
                HUD.SetText(MakeMessage("PERSISTENCE FAIL: {Failures} mismatches"))
        else:
            Logger.LogError("test_persistence_SPR008", "READ — Agent no es player válido")
            HUD.SetText(MakeMessage("ERROR: agent no es player"))

    MakeMessage<localizes>(Text:string):message = "{Text}"
