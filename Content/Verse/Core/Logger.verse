# ============================================================
# Logger.verse — Core module (SPR-006 + SPR-006-FIX-1)
# Arquitectura: module namespace (no class, no constructor, no state).
# Refactor SPR-006-FIX-1: class<concrete> top-level + metodos con
# effects propagaba transacts (err 3512) y visibility inconsistente
# (err 3593). module: resuelve ambos.
# Acceso: using { Verse.Core.Logger } luego Logger.LogXxx(...)
# Spec: docs/SPRINTS_BACKLOG.md SPR-006
# API:  docs/API_REFERENCE_GENERATED.md §3.2
# Patron canonico: docs/VERSE_SYNTAX_GUIDE.md §2 (post SPR-006-FIX-1)
# Sin dependencias compile-time (Capa 0 puro).
# Deuda diferida: prefix timestamp UTC (requiere TimeSync, romperia
# Capa 0 → no se hara aqui, se hara en LoggerEnhanced o helper externo).
# ============================================================

using { /Verse.org/Simulation }

Logger<public> := module:

    # Flag de debug. Cambiar a false para builds de produccion (silencia LogDebug).
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