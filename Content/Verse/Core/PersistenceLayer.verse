using { /Verse.org/Simulation }
using { /UnrealEngine.com/Temporary/Diagnostics }

# === V1 schema (struct contenedor de datos) ===
PlayerCore_V1<public> := struct<persistable>:
    Gold:int = 0
    Level:int = 1
    XP:int = 0

# === Wrapper option-version (patrón Epic 8/8/2025) ===
PlayerCore<public> := class<final><persistable>:
    V1:?PlayerCore_V1 = false

# === Weak_map persistente top-level (visibilidad <internal> default) ===
var PlayerCoreMap:weak_map(player, PlayerCore) = map{}
