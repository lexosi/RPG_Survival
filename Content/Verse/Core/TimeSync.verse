# ============================================================
# TimeSync.verse — Core module (SPR-007)
# Arquitectura: module namespace (sin state, sin constructor).
# Acceso: using { Verse.Core.TimeSync } luego TimeSync.GetXxx[...]
# Spec: docs/SPRINTS_BACKLOG.md SPR-007
# Patron canonico: docs/MODULES_DEPENDENCY_GRAPH.md §2.1
# Deps compile-time: Logger
#
# CAMBIO ARQUITECTONICO (SPR-007 build pass):
# Verse NO permite class<concrete> top-level con metodos <decides><transacts>
# (effect propaga al class y la construccion top-level es <computes>).
# Solucion: TimeSync es module: namespace de funciones puras.
# Sin state mutable -> sin necesidad de class.
# ============================================================

using { /Verse.org/Simulation }
using { Verse.Core.Logger }

TimeSync<public> := module:

    # Devuelve simulation elapsed time como int (segundos desde inicio sesion).
    GetUTCNow<public>()<decides>:int=
        Elapsed:float = GetSimulationElapsedTime()
        Floor[Elapsed]

    # Segundos restantes hasta proxima HH:00:00 (relativo a inicio sesion).
    GetSecondsUntilNextHour<public>()<decides>:int=
        Now := TimeSync.GetUTCNow[]
        SecondsIntoCurrentHour := Mod[Now, 3600]
        3600 - SecondsIntoCurrentHour

    # True si "ahora" cae dentro de [Start, Start+Duration) en simulation time.
    IsInWindow<public>(StartEpoch:int, DurationSeconds:int)<decides>:void=
        Now := TimeSync.GetUTCNow[]
        Now >= StartEpoch
        Now < StartEpoch + DurationSeconds