import random

facilityConfig = {
    "hotSprings": {
        "name": "Hot Springs",
        "levels": [
            {"level": 0, "cost": 0,   "renownReq": 0, "heroesSoaked": 0, "stressReduction": 0,  "dailyUpkeep": 0,  "desc": "Locked"},
            {"level": 1, "cost": 300, "renownReq": 0, "heroesSoaked": 1, "stressReduction": 5,  "dailyUpkeep": 5,  "desc": "-5 stress/turn for 1 hero"},
            {"level": 2, "cost": 600, "renownReq": 2, "heroesSoaked": 1, "stressReduction": 10, "dailyUpkeep": 10, "desc": "-10 stress/turn for 1 hero"},
            {"level": 3, "cost": 1000,"renownReq": 4, "heroesSoaked": 2, "stressReduction": 10, "dailyUpkeep": 15, "desc": "-10 stress/turn for 2 heroes"},
        ],
    },
    "trainingGrounds": {
        "name": "Training Grounds",
        "levels": [
            {"level": 0, "cost": 0,   "renownReq": 0, "interval": 0, "dailyUpkeep": 0,  "desc": "Locked"},
            {"level": 1, "cost": 400, "renownReq": 1, "interval": 5, "dailyUpkeep": 8,  "desc": "+1 random stat per 5 idle days"},
            {"level": 2, "cost": 700, "renownReq": 3, "interval": 3, "dailyUpkeep": 15, "desc": "+1 random stat per 3 idle days"},
            {"level": 3, "cost": 1200,"renownReq": 5, "interval": 2, "dailyUpkeep": 25, "desc": "+1 random stat per 2 idle days"},
        ],
    },
}

FACILITY_NAMES = ["hotSprings", "trainingGrounds"]

def getLevelInfo(facilities, name):
    level = facilities[name]["level"]
    return facilityConfig[name]["levels"][level]

def nextLevel(facilities, name):
    current = facilities[name]["level"]
    levels = facilityConfig[name]["levels"]
    if current + 1 < len(levels):
        return levels[current + 1]
    return None

def canUpgrade(facilities, name, renown, guildBank):
    nl = nextLevel(facilities, name)
    if nl is None:
        return False
    if renown < nl["renownReq"]:
        return False
    if guildBank < nl["cost"]:
        return False
    return True

def upgradeCost(facilities, name):
    nl = nextLevel(facilities, name)
    return nl["cost"] if nl else 0

def isActive(facilities, name):
    return facilities[name].get("active", False) and getLevelInfo(facilities, name)["level"] > 0

def totalUpkeep(facilities):
    total = 0
    for name, state in facilities.items():
        if state.get("active", False):
            info = getLevelInfo(facilities, name)
            total += info["dailyUpkeep"]
    return total

def applyFacility(facilities, guildRoster):
    if not isActive(facilities, "hotSprings"):
        return []
    info = getLevelInfo(facilities, "hotSprings")
    eligible = [h for h in guildRoster if h["status"] != "On Mission"]
    eligible.sort(key=lambda h: h["stress"], reverse=True)
    count = min(info["heroesSoaked"], len(eligible))
    logs = []
    for i in range(count):
        hero = eligible[i]
        hero["stress"] = max(0, hero["stress"] - info["stressReduction"])
        logs.append(f"{hero['name']} soaked in Hot Springs (-{info['stressReduction']} stress)")
    return logs

def applyTrainingGrounds(facilities, guildRoster):
    if not isActive(facilities, "trainingGrounds"):
        return []
    info = getLevelInfo(facilities, "trainingGrounds")
    interval = info["interval"]
    if interval == 0:
        return []
    logs = []
    for hero in guildRoster:
        if hero["status"] == "On Mission":
            continue
        hero["idleDays"] = hero.get("idleDays", 0) + 1
        if hero["idleDays"] >= interval:
            statKeys = ["STR", "INT", "DEX", "FTH", "LCK"]
            chosen = random.choice(statKeys)
            hero["stats"][chosen] += 1
            hero["idleDays"] -= interval
            logs.append(f"{hero['name']} trained {chosen} (+1, now {hero['stats'][chosen]})")
    return logs

def formatEffect(facilities, name):
    info = getLevelInfo(facilities, name)
    if info["level"] == 0:
        return "Not built yet"
    return info["desc"]
