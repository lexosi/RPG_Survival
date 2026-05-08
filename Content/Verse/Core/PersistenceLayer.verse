using { /Verse.org/Simulation }
using { /UnrealEngine.com/Temporary/Diagnostics }
using { Verse.Core.Logger }

# =====================================================================
# Constantes de validación defensiva (PERSISTENCE_MAP §10.1)
# F1+ probable mover a Generated/ cuando Python exporte desde
# data/economy/balance_caps.json. Por ahora locales en este módulo.
# =====================================================================

MAX_REASONABLE_GOLD:int = 1000000000
MAX_LEVEL:int = 1000
MAX_REASONABLE_VBUCKS:int = 100000
MAX_BASE_LEVEL:int = 100
MAX_REASONABLE_QUESTS:int = 10000
MAX_INVENTORY_SLOTS:int = 500

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
# Funciones Load/Save — paso 3c: LoadPlayerCore con Logger.LogWarn.
# Logger solo se llama cuando una validación detecta corrupción real
# (no en path normal). Función sigue SIN <transacts> (validado 3b).
# =====================================================================

LoadPlayerCore<public>(InPlayer:player):PlayerCore_V1=
    var CoreData:PlayerCore_V1 = PlayerCore_V1{}
    if (Existing := PlayerCoreMap[InPlayer]):
        if (V1Data := Existing.V1?):
            set CoreData = V1Data
    var SafeGold:int = CoreData.Gold
    if (SafeGold < 0):
        Logger.LogWarn("PersistenceLayer", "PlayerCore.Gold negativo, corrigiendo a 0")
        set SafeGold = 0
    if (SafeGold > MAX_REASONABLE_GOLD):
        Logger.LogWarn("PersistenceLayer", "PlayerCore.Gold excede cap, capping")
        set SafeGold = MAX_REASONABLE_GOLD
    var SafeLevel:int = CoreData.Level
    if (SafeLevel < 1):
        Logger.LogWarn("PersistenceLayer", "PlayerCore.Level menor que 1, corrigiendo a 1")
        set SafeLevel = 1
    if (SafeLevel > MAX_LEVEL):
        Logger.LogWarn("PersistenceLayer", "PlayerCore.Level excede cap, capping")
        set SafeLevel = MAX_LEVEL
    var SafeXP:int = CoreData.XP
    if (SafeXP < 0):
        Logger.LogWarn("PersistenceLayer", "PlayerCore.XP negativo, corrigiendo a 0")
        set SafeXP = 0
    PlayerCore_V1{Gold := SafeGold, Level := SafeLevel, XP := SafeXP}
