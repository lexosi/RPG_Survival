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
# Funciones Load/Save — paso 3e: 8 funciones (4 Load + 4 Save).
# Patrón Load: <computes> default, con Logger.LogWarn en validaciones.
# Patrón Save: <transacts>, sin Logger, con if-wrap consumiendo <decides>.
# Validaciones por bucket según campos respectivos.
# =====================================================================

# --- PlayerCore ---

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

SavePlayerCore<public>(InPlayer:player, Data:PlayerCore_V1)<transacts>:void=
    if (set PlayerCoreMap[InPlayer] = PlayerCore{V1 := option{Data}}) {}

# --- PlayerInventory ---

LoadPlayerInventory<public>(InPlayer:player):PlayerInventory_V1=
    var InvData:PlayerInventory_V1 = PlayerInventory_V1{}
    if (Existing := PlayerInventoryMap[InPlayer]):
        if (V1Data := Existing.V1?):
            set InvData = V1Data
    var SafeMaxSlots:int = InvData.MaxSlots
    if (SafeMaxSlots < 1):
        Logger.LogWarn("PersistenceLayer", "PlayerInventory.MaxSlots menor que 1, corrigiendo a 20")
        set SafeMaxSlots = 20
    if (SafeMaxSlots > MAX_INVENTORY_SLOTS):
        Logger.LogWarn("PersistenceLayer", "PlayerInventory.MaxSlots excede cap, capping")
        set SafeMaxSlots = MAX_INVENTORY_SLOTS
    var SafeSlotsUsed:int = InvData.SlotsUsed
    if (SafeSlotsUsed < 0):
        Logger.LogWarn("PersistenceLayer", "PlayerInventory.SlotsUsed negativo, corrigiendo a 0")
        set SafeSlotsUsed = 0
    if (SafeSlotsUsed > SafeMaxSlots):
        Logger.LogWarn("PersistenceLayer", "PlayerInventory.SlotsUsed mayor que MaxSlots, capping")
        set SafeSlotsUsed = SafeMaxSlots
    PlayerInventory_V1{SlotsUsed := SafeSlotsUsed, MaxSlots := SafeMaxSlots}

SavePlayerInventory<public>(InPlayer:player, Data:PlayerInventory_V1)<transacts>:void=
    if (set PlayerInventoryMap[InPlayer] = PlayerInventory{V1 := option{Data}}) {}

# --- PlayerProgress ---

LoadPlayerProgress<public>(InPlayer:player):PlayerProgress_V1=
    var ProgData:PlayerProgress_V1 = PlayerProgress_V1{}
    if (Existing := PlayerProgressMap[InPlayer]):
        if (V1Data := Existing.V1?):
            set ProgData = V1Data
    var SafeQuestsCompleted:int = ProgData.QuestsCompleted
    if (SafeQuestsCompleted < 0):
        Logger.LogWarn("PersistenceLayer", "PlayerProgress.QuestsCompleted negativo, corrigiendo a 0")
        set SafeQuestsCompleted = 0
    if (SafeQuestsCompleted > MAX_REASONABLE_QUESTS):
        Logger.LogWarn("PersistenceLayer", "PlayerProgress.QuestsCompleted excede cap, capping")
        set SafeQuestsCompleted = MAX_REASONABLE_QUESTS
    PlayerProgress_V1{QuestsCompleted := SafeQuestsCompleted, Tutorial_Completed := ProgData.Tutorial_Completed}

SavePlayerProgress<public>(InPlayer:player, Data:PlayerProgress_V1)<transacts>:void=
    if (set PlayerProgressMap[InPlayer] = PlayerProgress{V1 := option{Data}}) {}

# --- PlayerEconomy ---

LoadPlayerEconomy<public>(InPlayer:player):PlayerEconomy_V1=
    var EconData:PlayerEconomy_V1 = PlayerEconomy_V1{}
    if (Existing := PlayerEconomyMap[InPlayer]):
        if (V1Data := Existing.V1?):
            set EconData = V1Data
    var SafeVBucks:int = EconData.VBucks_Entitlements
    if (SafeVBucks < 0):
        Logger.LogWarn("PersistenceLayer", "PlayerEconomy.VBucks_Entitlements negativo, corrigiendo a 0")
        set SafeVBucks = 0
    if (SafeVBucks > MAX_REASONABLE_VBUCKS):
        Logger.LogWarn("PersistenceLayer", "PlayerEconomy.VBucks_Entitlements excede cap, capping")
        set SafeVBucks = MAX_REASONABLE_VBUCKS
    var SafeBaseLevel:int = EconData.BaseLevel
    if (SafeBaseLevel < 1):
        Logger.LogWarn("PersistenceLayer", "PlayerEconomy.BaseLevel menor que 1, corrigiendo a 1")
        set SafeBaseLevel = 1
    if (SafeBaseLevel > MAX_BASE_LEVEL):
        Logger.LogWarn("PersistenceLayer", "PlayerEconomy.BaseLevel excede cap, capping")
        set SafeBaseLevel = MAX_BASE_LEVEL
    PlayerEconomy_V1{VBucks_Entitlements := SafeVBucks, BaseLevel := SafeBaseLevel}

SavePlayerEconomy<public>(InPlayer:player, Data:PlayerEconomy_V1)<transacts>:void=
    if (set PlayerEconomyMap[InPlayer] = PlayerEconomy{V1 := option{Data}}) {}
