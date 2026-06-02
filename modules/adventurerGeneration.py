import random

firstNames = [
    "Grim", "Swift", "Sun", "Shadow", "Iron", "Moss", "Pale", "Deep", "Blood", "Cloud",
    "Storm", "Ash", "Frost", "Stone", "Dawn", "Night", "Wild", "Thorn", "Birch", "Coal",
    "Ember", "Creek", "Sage", "Vale", "Peak", "Dust", "Fern", "Lark", "Wren", "Oak",
]
lastNames = [
    "blade", "weaver", "shield", "watcher", "seer", "heart", "fury", "stalker", "bane", "song",
    "wind", "thorn", "crest", "mane", "pelt", "root", "wing", "scale", "mark", "fang",
    "fell", "vale", "drift", "wood", "haze", "quill", "brim", "shard", "dusk", "briar",
]
classes = ["Warrior", "Mage", "Priest", "Thief"]
races = ["Human", "Elf", "Dwarf", "Halfling", "Orc", "Goblin", "Lizardfolk", "Gnome", "Catfolk", "Merfolk"]

surnamePassives = {
    "blade":   {"STR": 1, "DEX": 1},
    "weaver":  {"INT": 1, "FTH": 1},
    "shield":  {"STR": 1, "FTH": 1},
    "watcher": {"DEX": 1, "LCK": 1},
    "seer":    {"FTH": 2},
    "heart":   {"LCK": 2},
    "fury":    {"STR": 2},
    "stalker": {"DEX": 2},
    "bane":    {"STR": 1, "INT": 1},
    "song":    {"FTH": 1, "LCK": 1},
    "wind":    {"DEX": 1},
    "thorn":   {"STR": 1, "LCK": 1},
    "crest":   {"STR": 1, "FTH": 1},
    "mane":    {"INT": 1, "LCK": 1},
    "pelt":    {"LCK": 2},
    "root":    {"FTH": 1},
    "wing":    {"DEX": 1, "INT": 1},
    "scale":   {"STR": 2},
    "mark":    {"INT": 1, "LCK": 1},
    "fang":    {"STR": 1},
    "fell":    {"STR": 1, "LCK": 1},
    "vale":    {"INT": 1, "FTH": 1},
    "drift":   {"DEX": 1},
    "wood":    {"INT": 1},
    "haze":    {"LCK": 1},
    "quill":   {"INT": 1, "FTH": 1},
    "brim":    {"STR": 1},
    "shard":   {"STR": 1, "DEX": 1},
    "dusk":    {"DEX": 1, "LCK": 1},
    "briar":   {"DEX": 1, "FTH": 1},
}

def formatPassiveText(name):
    mods = surnamePassives.get(name, {})
    parts = [f"{stat}{val:+d}" for stat, val in mods.items()]
    return ", ".join(parts) if parts else "none"

rankConfig = [
    ("E", 30, 39, 0.4),
    ("D", 40, 49, 0.7),
    ("C", 50, 59, 1.0),
    ("B", 60, 69, 1.8),
    ("A", 70, 79, 3.5),
    ("S", 80, 90, 6.0),
]
rankWeights = [30, 25, 20, 15, 7, 3]

renownConfig = [
    {"title": "Fresh Charter",     "tax": 600,  "ranks": ["E", "D", "C"],       "maxHeroes": 5, "questMult": 1.0},
    {"title": "Established Guild", "tax": 800,  "ranks": ["E", "D", "C", "B"],  "maxHeroes": 5, "questMult": 1.2},
    {"title": "Notable Company",   "tax": 1100, "ranks": ["D", "C", "B", "A"],  "maxHeroes": 6, "questMult": 1.5},
    {"title": "Renowned Order",    "tax": 1500, "ranks": ["C", "B", "A"],        "maxHeroes": 6, "questMult": 1.8},
    {"title": "Legendary Fellowship", "tax": 2000, "ranks": ["B", "A", "S"],    "maxHeroes": 7, "questMult": 2.2},
    {"title": "Mythic Circle",     "tax": 2500, "ranks": ["A", "S"],             "maxHeroes": 7, "questMult": 2.5},
]

upkeepByRank = {"E": 5, "D": 8, "C": 12, "B": 18, "A": 28, "S": 45}
failureCostByRank = {"E": 50, "D": 100, "C": 150, "B": 250, "A": 400, "S": 600}

def getUpkeep(hero):
    return upkeepByRank.get(hero['rank'], 10)

def getFailureCost(hero):
    return failureCostByRank.get(hero['rank'], 100)

def getTotalUpkeep(guildRoster):
    return sum(getUpkeep(h) for h in guildRoster)

def getRenownCfg(renown):
    return renownConfig[min(renown, 5)]

contractRanges = {"E": (12, 14), "D": (10, 12), "C": (9, 11), "B": (8, 10), "A": (6, 8), "S": (5, 7)}

synergyPairs = {
    ("blade", "shield"): "STR",
    ("fury", "bane"): "STR",
    ("thorn", "briar"): "STR",
    ("weaver", "seer"): "INT",
    ("root", "wood"): "INT",
    ("mark", "shard"): "INT",
    ("heart", "song"): "FTH",
    ("crest", "mane"): "FTH",
    ("vale", "fell"): "FTH",
    ("fang", "scale"): "DEX",
    ("watcher", "stalker"): "DEX",
    ("wind", "drift"): "DEX",
    ("pelt", "wing"): "DEX",
}

def getSynergyBonus(party, statNeeded):
    bonus = 0
    for i in range(len(party)):
        for j in range(i + 1, len(party)):
            s1 = party[i].get('surname', '')
            s2 = party[j].get('surname', '')
            pair = synergyPairs.get((s1, s2))
            if pair is None:
                pair = synergyPairs.get((s2, s1))
            if pair == statNeeded:
                bonus += 2
    return bonus

def generateAdventurer(renown):
    firstName = random.choice(firstNames)
    lastName = random.choice(lastNames)
    fullName = firstName + lastName

    allowed = getRenownCfg(renown)["ranks"]
    filteredConfig = []
    filteredWeights = []
    for (r, tMin, tMax, cMult), w in zip(rankConfig, rankWeights):
        if r in allowed:
            filteredConfig.append((r, tMin, tMax, cMult))
            filteredWeights.append(w)

    rankName, targetMin, targetMax, costMult = random.choices(
        filteredConfig, weights=filteredWeights, k=1
    )[0]

    target = random.randint(targetMin, targetMax)
    stats = [6] * 5
    remaining = target - 30
    while remaining > 0:
        i = random.randrange(5)
        if stats[i] < 18:
            stats[i] += 1
            remaining -= 1
    random.shuffle(stats)

    passive = surnamePassives.get(lastName, {})
    for stat, val in passive.items():
        idx = {"STR": 0, "INT": 1, "DEX": 2, "FTH": 3, "LCK": 4}[stat]
        stats[idx] = min(18, stats[idx] + val)

    cMin, cMax = contractRanges[rankName]
    contractDays = random.randint(cMin, cMax)

    return {
        "name": fullName,
        "surname": lastName,
        "race": random.choice(races),
        "class": random.choice(classes),
        "rank": rankName,
        "gold": random.randint(10, 50),
        "hiringFee": int(target * costMult),
        "status": "Available",
        "stats": {
            "STR": stats[0],
            "INT": stats[1],
            "DEX": stats[2],
            "FTH": stats[3],
            "LCK": stats[4]
        },
        "contractDays": contractDays,
        "contractDaysLeft": contractDays,
        "contractExtended": False,
        "stress": 0,
        "equipment": {"weapon": None, "armor": None, "talisman": None, "relic": None}
    }

def extendCost(hero):
    return int(hero['hiringFee'] * 0.3)

def terminateCost(hero):
    return int(hero['hiringFee'] * 0.75)

def getStressPenalty(stress):
    if stress >= 90:
        return 4
    if stress >= 70:
        return 3
    if stress >= 50:
        return 2
    if stress >= 30:
        return 1
    return 0

def getStressLabel(stress):
    if stress >= 90:
        return "Broken"
    if stress >= 70:
        return "Exhausted"
    if stress >= 50:
        return "Fatigued"
    if stress >= 30:
        return "Strained"
    return "Rested"

def stressBar(stress):
    filled = stress // 10
    return "█" * filled + "░" * (10 - filled)

def getInjuryPenalty(hero):
    return 3 if hero.get('injuredDaysLeft', 0) > 0 else 0

def applyInjury(hero):
    if random.random() < 0.30:
        hero['injuredDaysLeft'] = 2

def tickInjury(hero):
    if hero.get('injuredDaysLeft', 0) > 0:
        hero['injuredDaysLeft'] -= 1
