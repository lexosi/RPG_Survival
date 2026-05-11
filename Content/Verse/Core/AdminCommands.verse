# Core/AdminCommands.verse — SPR-010 (SYS-070)
#
# Patrón canónico §2.4-bis "Core stateless + Device state-bearing".
# Validado empíricamente CANARY_VALIDATION_LOG.md entry 001 v5 PASS
# (hash 7c8d437ba5e2614cdde0219a4f25420e034fbbed843caef654b58f2d4a37b1fd,
# build UEFN ++Fortnite+Release-40.30-CL-53276632).
#
# State (Refs) vive en admin_panel_device (@editable). Este módulo es
# stateless puro: recibe Refs como param a todas sus funciones públicas.
# Lección 5: var top-level SOLO weak_map → state NO puede vivir aquí.
#
# Refs:
# - docs/VERSE_SYNTAX_GUIDE.md §1 lecciones 17/18/19/20 + §2.4-bis
# - docs/API_REFERENCE_GENERATED.md §3.7
# - docs/MODULES_DEPENDENCY_GRAPH.md §4.6
# - docs/CHANGELOG.md entrada B1.1-fix

using { /Fortnite.com/Devices }
using { /Verse.org/Simulation }

AdminCommands<public> := module:

    # Failable predicate. Succeeds si alguno de Refs reference Agent.
    # Patrón Epic-confirmed: option-wrapper var + for failable filter + propagation `?`.
    # NO usar return/fail (lección 18: prohibidos en <decides> por lenient eval).
    IsAdmin<public>(Refs:[]player_reference_device, Agent:agent)<transacts><decides>:void=
        var Found:logic = false
        for (Ref:Refs, Ref.IsReferenced[Agent], not Found?):
            set Found = true
        Found?

    # Wrapper non-failable. Útil cuando caller necesita :logic en lugar de <decides>.
    # Patrón trivial sobre IsAdmin failable: SIN var/set (lección 20: funciones :logic
    # que mutan var propagan no_rollback effect → err 3512 al llamarlas desde <transacts>).
    IsAdminLogic<public>(Refs:[]player_reference_device, Agent:agent):logic=
        if (IsAdmin[Refs, Agent]) { true } else { false }

    # Stub F0 — scope F1 cuando haya commands reales (give-gold, teleport, etc.).
    # Si fail IsAdmin, loguea intento + ignora silenciosamente. Si succeeds,
    # dispatch a handler por Command. Firma estable para no romper callers futuros.
    # NO implementar handler logic hasta SPR específico F1+.
    ExecuteCommand<public>(Refs:[]player_reference_device, Agent:agent, Command:string, Args:[]string):void=
        # TODO SPR-F1: dispatch handler por Command + Args. Por ahora no-op.
        # Validación IsAdmin se hará aquí cuando se implementen los handlers.
        # No usar Print() desde failure context — usar log_channel pattern (lección 19).
        if (IsAdmin[Refs, Agent]) {} else {}
