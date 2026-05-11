# ============================================================
# BigNumbers.verse — Core module (placeholder F-CLEAN-P1, 2026-05-11)
# Arquitectura: module namespace (consistente con Logger/TimeSync — module:
# validado empíricamente vs class<concrete>: que falla top-level).
# Acceso: using { Verse.Core.BigNumbers } luego BigNumbers.Format(N)
# Spec: docs/CONCEPT.md §SYS-067 — wrap de lib comunidad para aritmética grande
# Patrón canónico: docs/MODULES_DEPENDENCY_GRAPH.md §4.5
# Deps compile-time: Logger (loguea overflow al rango int64)
#
# ESTADO PLACEHOLDER (F-CLEAN-P1 2026-05-11):
# Archivo declarado en docs autoritativos (TRUTH §4, MODULES §4.5) pero
# NUNCA materializado en disco — drift histórico (SYS-067 sin SPR asignado).
# F-CLEAN-P1 lo materializa como mínimo viable para que F0 cierre limpio.
# Implementación real pendiente — SPR futuro asignar SYS-067 cuando algún
# sistema gameplay necesite aritmética grande (HP > 1M, gold sextillones).
#
# Cuando se implemente real: añadir wrap de big_int library + ToString
# formatting + overflow detection logueando con Logger.LogWarn.
# ============================================================

using { /Verse.org/Simulation }
using { Verse.Core.Logger }

BigNumbers<public> := module:

    # Stub placeholder. Devuelve representación trivial del int.
    # SPR futuro reemplaza con wrap real (BigInteger arithmetic + thousands separator).
    Format<public>(N:int):string=
        "{N}"
