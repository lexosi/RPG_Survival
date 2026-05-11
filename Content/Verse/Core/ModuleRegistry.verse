# ============================================================
# ModuleRegistry.verse — Core module (placeholder F-CLEAN-P1, 2026-05-11)
# Arquitectura: module namespace (consistente con Logger/TimeSync).
# Acceso: using { Verse.Core.ModuleRegistry } luego ModuleRegistry.GetXxx[...]
# Spec: docs/SPRINTS_BACKLOG.md SPR-005
# Patrón canónico: docs/MODULES_DEPENDENCY_GRAPH.md §2.1 + §4 (Registry section)
# Deps compile-time: Logger
# Deps compile-time pendientes F1: Generated/ModuleRegistryConstants.verse
#
# ESTADO PLACEHOLDER (F-CLEAN-P1 2026-05-11):
# SPR-005 marcado 🟢 done en SPRINTS_BACKLOG pero archivo nunca materializado
# en disco — drift histórico de cierre sprint. F-CLEAN-P1 lo materializa
# como mínimo viable.
#
# Implementación real depende de SPR-004 ext (Generated/ModuleRegistryConstants
# producido por exporter Python desde data/architecture/modules_manifest.json).
# Hasta que SPR-004 ext entregue, Registry es API stub que devuelve nullopt.
#
# Cuando se implemente real: importar ModuleRegistryConstants + funciones
# RegisterXxx<public>/GetXxx<public> tipadas por sistema (no genéricas — Verse
# v1 no soporta <T> runtime). Detalle MODULES §4.x.
# ============================================================

using { /Verse.org/Simulation }
using { Verse.Core.Logger }

ModuleRegistry<public> := module:

    # Stub placeholder. SPR-004 ext + SPR-005 real expandirá.
    # Devuelve nullopt — ningún módulo registrado aún (consistente con
    # estado F0 pre-Systems gameplay Capa 2+).
    IsInitialized<public>():logic=
        false
