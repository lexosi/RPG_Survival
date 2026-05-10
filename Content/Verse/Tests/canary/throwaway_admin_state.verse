# AUTO-GENERATED throwaway — SPR-010 Step 0 (P1 validation v3, post-investigación L4)
# Propósito: validar patrón canónico Core stateless + Device state-bearing
# (VERSE_SYNTAX_GUIDE §2.4-bis) con API real player_reference_device (B1.1-fix)
# usando patrón failable Epic-confirmed (option-wrapper, NO return/fail).
#
# Si compila → patrón vigente para SPR-010 implementación real.
# Si falla → escalar a Claude (web).
#
# Refs:
# - VERSE_SYNTAX_GUIDE §1 lección 17 + §2.4-bis (a actualizar con lección 18 nueva post-L4)
# - API_REFERENCE_GENERATED.md §3.7
# - CHANGELOG entrada B1.1-fix
# - Foro Epic: https://forums.unrealengine.com/t/has-anyone-successfully-written-a-failable-function-in-verse/1160379
# - Verse.digest 40.30-CL-53276632

using { /Fortnite.com/Devices }
using { /Verse.org/Simulation }

# AdminCommands stateless — namespace puro. Refs como param, no state interno.
# Patrón canónico §2.4-bis "Core stateless + Device state-bearing".
ThrowawayAdminCommands<public> := module:

    # Failable predicate. Succeeds si alguno de Refs reference Agent.
    # Patrón Epic-confirmed: option-wrapper var + for con failable filter + propagation con `?`.
    # NO usar `return`/`fail` (prohibidos en <decides> por design — lenient eval).
    IsAdmin<public>(Refs:[]player_reference_device, Agent:agent)<transacts><decides>:void=
        var Found:logic = false
        for (Ref:Refs, Ref.IsReferenced[Agent], not Found?):
            set Found = true
        Found?

    # Wrapper non-failable. Útil cuando caller necesita logic en lugar de <decides>.
    # Patrón trivial sobre IsAdmin failable: sin var/set para evitar no_rollback effect (err 3512).
    IsAdminLogic<public>(Refs:[]player_reference_device, Agent:agent):logic=
        if (IsAdmin[Refs, Agent]) { true } else { false }

# Device wrapper — state vive aquí, NO top-level (lección 5: var top-level SOLO weak_map).
throwaway_admin_canary_device := class<concrete>(creative_device):

    @editable CanaryRefs:[]player_reference_device = array{}

    OnBegin<override>()<suspends>:void=
        # Throwaway de validación de sintaxis (no runtime behavior).
        # NO Print() dentro de failure contexts (if con condición failable) — Print es no_rollback,
        # llamarlo desde failure context = err 3512. Patrón canónico Epic: usar log_channel + log.Print
        # (Incredulous_Hulk, foro Apr 2023). Para throwaway lo evitamos completamente.
        Print("[CANARY] Device OnBegin, refs configurados: {CanaryRefs.Length}")
        # Validamos que las firmas de IsAdmin failable + IsAdminLogic non-failable compilan.
        # Bloques de if/else vacíos {} son legales y no requieren Print interno.
        if (Players := Self.GetPlayspace().GetPlayers(); FirstP := Players[0]):
            # Check failable IsAdmin: si succeeds o fails, no Print interno.
            if (ThrowawayAdminCommands.IsAdmin[CanaryRefs, FirstP]) {} else {}
            # IsAdminLogic devuelve :logic. Almacenar en var, no usar en failure context interno.
            ResultLogic:logic = ThrowawayAdminCommands.IsAdminLogic(CanaryRefs, FirstP)
            # Si quisiéramos Print del resultado, sería desde un log.Print no Print directo.
            # Throwaway omite ese paso: la firma compila = patrón canónico §2.4-bis validado.
            Print("[CANARY] Smoke check completado, IsAdminLogic devolvió logic value (no se imprime — Print + failure context)")
        else:
            Print("[CANARY] No hay players en playspace, skip smoke test")