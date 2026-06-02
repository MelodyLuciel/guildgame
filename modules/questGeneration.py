import random
from modules import adventurerGeneration as ag

questPrefix = ["The Forgotten", "The Sunken", "The Cursed", "The Hidden", "The Golden", "The Haunted"]
questLocations = ["Crypt", "Grotto", "Catacombs", "Tower", "Ruins", "Forest", "Vault"]
questSuffix = ["of Shadows", "of the Deep", "of Doom", "of Gold", "of the Moon", "of the Ancestors"]

partyQuestPrefix = ["Grand", "United", "Allied", "Combined", "Joint"]
partyQuestSuffix = ["Expedition", "Campaign", "Venture", "Crusade", "Endeavour"]

partySizeMult = {
    2: {"diff": 1.3, "reward": 1.8},
    3: {"diff": 2.0, "reward": 3.5},
    4: {"diff": 2.8, "reward": 5.5},
}

def generateQuest(slotType, renown):
    config = {
        "breadwinner": {"diff": (5, 10), "mult": (8, 14), "rec": "E-D"},
        "benchmark":   {"diff": (10, 15), "mult": (14, 20), "rec": "C-B"},
        "highstakes":  {"diff": (14, 18), "mult": (20, 30), "rec": "A-S"},
    }
    cfg = config[slotType]
    questName = f"{random.choice(questPrefix)} {random.choice(questLocations)} {random.choice(questSuffix)}"
    requiredStat = random.choice(["STR", "INT", "DEX", "FTH"])
    baseDifficulty = random.randint(*cfg["diff"])
    difficulty = baseDifficulty + renown * 3
    goldReward = int(baseDifficulty * random.randint(*cfg["mult"]) * ag.getRenownCfg(renown)["questMult"])
    return {
        "name": questName,
        "statNeeded": requiredStat,
        "difficulty": difficulty,
        "reward": goldReward,
        "type": slotType,
        "status": "available",
        "recommended": cfg["rec"],
        "contracted_by": None
    }

def generatePartyQuest(renown):
    name = f"{random.choice(partyQuestPrefix)} {random.choice(questLocations)} {random.choice(partyQuestSuffix)}"
    requiredStat = random.choice(["STR", "INT", "DEX", "FTH"])
    baseDifficulty = random.randint(20, 25)
    difficulty = baseDifficulty + renown * 3
    goldReward = int(baseDifficulty * random.randint(25, 35) * ag.getRenownCfg(renown)["questMult"])
    return {
        "name": name,
        "statNeeded": requiredStat,
        "difficulty": difficulty,
        "reward": goldReward,
        "type": "party",
        "status": "available",
    }
