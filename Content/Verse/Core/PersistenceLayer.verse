using { /Verse.org/Simulation }
using { /UnrealEngine.com/Temporary/Diagnostics }

# =====================================================================
# Bucket 1: PlayerCore — currencies, level, XP, stats base
# Schema completo en docs/PERSISTENCE_MAP.md §3
# =====================================================================

PlayerCore_V1<public> := struct<persistable>:
    Gold:int = 0
    Level:int = 1
    XP:int = 0

PlayerCore<public> := class<final><persistable>:
    V1:?PlayerCore_V1 = false

var PlayerCoreMap:weak_map(player, PlayerCore) = map{}

# =====================================================================
# Bucket 2: PlayerInventory — items, equipped, companions, Dex, bank
# Schema completo en docs/PERSISTENCE_MAP.md §4
# El más pesado de los 4 buckets. Vigilar tamaño siempre.
# =====================================================================

PlayerInventory_V1<public> := struct<persistable>:
    SlotsUsed:int = 0
    MaxSlots:int = 20

PlayerInventory<public> := class<final><persistable>:
    V1:?PlayerInventory_V1 = false

var PlayerInventoryMap:weak_map(player, PlayerInventory) = map{}

# =====================================================================
# Bucket 3: PlayerProgress — quests, achievements, BP progress, daily
# login, codes redeemed, time played, tutorial state, leaderboards
# Schema completo en docs/PERSISTENCE_MAP.md §5
# =====================================================================

PlayerProgress_V1<public> := struct<persistable>:
    QuestsCompleted:int = 0
    Tutorial_Completed:logic = false

PlayerProgress<public> := class<final><persistable>:
    V1:?PlayerProgress_V1 = false

var PlayerProgressMap:weak_map(player, PlayerProgress) = map{}

# =====================================================================
# Bucket 4: PlayerEconomy — V-Bucks entitlements, base upgrades,
# pity counters, trade history, active crafts
# Schema completo en docs/PERSISTENCE_MAP.md §6
# =====================================================================

PlayerEconomy_V1<public> := struct<persistable>:
    VBucks_Entitlements:int = 0
    BaseLevel:int = 1

PlayerEconomy<public> := class<final><persistable>:
    V1:?PlayerEconomy_V1 = false

var PlayerEconomyMap:weak_map(player, PlayerEconomy) = map{}

# =====================================================================
# Funciones Load/Save — paso 3a: solo LoadPlayerCore mínimo.
# Sin Logger. Sin <transacts>. Sin validación defensiva.
# Aísla técnicamente acceso weak_map + option-unwrap.
# Variable local nombrada CoreData para evitar colisión con namespace Core.
# =====================================================================

LoadPlayerCore<public>(InPlayer:player):PlayerCore_V1=
    var CoreData:PlayerCore_V1 = PlayerCore_V1{}
    if (Existing := PlayerCoreMap[InPlayer]):
        if (V1Data := Existing.V1?):
            set CoreData = V1Data
    CoreData
