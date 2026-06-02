import random

tierConfig = {
    "iron":    {"bonus": 2,  "guildCost": 150,  "heroCost": 200},
    "steel":   {"bonus": 4,  "guildCost": 450,  "heroCost": 600},
    "mythril": {"bonus": 6,  "guildCost": 1200, "heroCost": 1600},
}

tierPrefixes = {
    "iron":    "Iron",
    "steel":   "Steel",
    "mythril": "Mythril",
}

slotConfig = {
    "weapon": {
        "bases": ["Claymore", "Longsword", "Dagger", "Staff", "Bow", "Greataxe", "Spear", "Mace", "Sabre", "Wand"],
        "suffixes": ["of Power", "of the Wolf", "of Kings", "of Accuracy", "of Light", "of the Void", "of the Ancients"],
        "stats": ["STR", "INT"],
    },
    "armor": {
        "bases": ["Chestplate", "Greaves", "Helm", "Gauntlets", "Pauldrons", "Cuirass", "Bracers", "Sabatons"],
        "suffixes": ["of Protection", "of the Bear", "of Warding", "of Fortitude", "of the Guardian", "of Will"],
        "stats": ["DEX", "FTH"],
    },
    "talisman": {
        "bases": ["Charm", "Amulet", "Ring", "Pendant", "Sigil", "Talisman", "Brooch", "Crest"],
        "suffixes": ["of Luck", "of Fate", "of Fortune", "of the Winds", "of Insight", "of the Seer"],
        "stats": ["LCK"],
    },
}

availableTiersByRenown = [
    ["iron"],
    ["iron"],
    ["iron", "steel"],
    ["iron", "steel"],
    ["iron", "steel", "mythril"],
    ["iron", "steel", "mythril"],
]

armorySlotConfig = [
    {"weapon": 2, "armor": 2, "talisman": 2, "relic": 1},
    {"weapon": 2, "armor": 2, "talisman": 2, "relic": 1},
    {"weapon": 3, "armor": 3, "talisman": 3, "relic": 1},
    {"weapon": 3, "armor": 3, "talisman": 3, "relic": 1},
    {"weapon": 4, "armor": 4, "talisman": 4, "relic": 1},
    {"weapon": 4, "armor": 4, "talisman": 4, "relic": 1},
]

def getAvailableTiers(renown):
    return availableTiersByRenown[min(renown, 5)]

def getMaxSlots(renown):
    return armorySlotConfig[min(renown, 5)]

def generateGear(slot, tier, usedNames=None):
    if usedNames is None:
        usedNames = set()

    prefix = tierPrefixes[tier]
    cfg = slotConfig[slot]
    base = random.choice(cfg["bases"])
    suffix = random.choice(cfg["suffixes"])
    stat = random.choice(cfg["stats"])

    name = f"{prefix} {base} {suffix}"
    attempts = 0
    while name in usedNames and attempts < 20:
        base = random.choice(cfg["bases"])
        suffix = random.choice(cfg["suffixes"])
        name = f"{prefix} {base} {suffix}"
        attempts += 1

    t = tierConfig[tier]
    return {
        "name": name,
        "slot": slot,
        "stat": stat,
        "bonus": t["bonus"],
        "tier": tier,
        "guildCost": t["guildCost"],
        "heroCost": t["heroCost"],
    }

def formatGearBonus(gear):
    return f"+{gear['bonus']} {gear['stat']}"

def calculateGearBonus(hero, stat):
    total = 0
    for gear in hero.get('equipment', {}).values():
        if gear and (gear['stat'] == stat or gear.get('stat') == 'ALL'):
            total += gear['bonus']
    return total
