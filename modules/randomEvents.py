import random

EVENTS = [
    {
        "name": "City Festival",
        "category": "civic",
        "rarity": "common",
        "minRenown": 0,
        "flavor": "The city announces a grand festival! The guild master's herald requests a contribution to fund the celebrations.",
        "choices": [
            {"key": "a", "label": "Donate 100g (Renown +1)", "effects": [{"type": "gold", "value": -100}, {"type": "renown", "value": 1}], "result": "Your generosity is celebrated across the city! Renown +1."},
            {"key": "b", "label": "Politely decline", "effects": [], "result": "The festival goes on without fanfare for your guild."},
            {"key": "c", "label": "Volunteer your heroes (all +10 stress)", "effects": [{"type": "stress_all", "value": 10}], "result": "Your heroes work the stalls and performances. The city adores you, but your team is worn out."},
        ]
    },
    {
        "name": "Royal Tax Edict",
        "category": "civic",
        "rarity": "common",
        "minRenown": 1,
        "flavor": "A royal messenger arrives with grim news: wartime taxes are being levied. The month is shortened by 3 days unless you pay a 300g exemption fee.",
        "choices": [
            {"key": "a", "label": "Pay 300g exemption fee", "effects": [{"type": "gold", "value": -300}], "result": "The messenger accepts the gold and rides off. Your schedule remains intact."},
            {"key": "b", "label": "Endure the edict (-3 days)", "effects": [{"type": "daysLeft", "value": -3}], "result": "The tax edict stands. You lose 3 days from the month."},
            {"key": "c", "label": "Appeal with renown (Renown -1, no gold cost)", "effects": [{"type": "renown", "value": -1}], "result": "You pull strings at court. Renown -1, but the deadline holds."},
        ]
    },
    {
        "name": "Wandering Minstrel",
        "category": "civic",
        "rarity": "common",
        "minRenown": 0,
        "flavor": "A travelling minstrel offers to perform for your guild hall, lifting spirits but asking for a generous tip.",
        "choices": [
            {"key": "a", "label": "Pay 50g for a performance (-10 stress all)", "effects": [{"type": "gold", "value": -50}, {"type": "stress_all", "value": -10}], "result": "The minstrel's ballads soothe your heroes. Everyone's stress drops by 10."},
            {"key": "b", "label": "Offer 25g for a short tune (-5 stress all)", "effects": [{"type": "gold", "value": -25}, {"type": "stress_all", "value": -5}], "result": "A quick tune and a tale — your heroes seem a bit lighter."},
            {"key": "c", "label": "Turn them away", "effects": [], "result": "The minstrel shrugs and moves on."},
        ]
    },
    {
        "name": "Monster Raid",
        "category": "wild",
        "rarity": "common",
        "minRenown": 0,
        "flavor": "A monster prowls the outskirts! The townsfolk beg your guild for help. You could send your strongest hero or pay to hire mercenaries.",
        "choices": [
            {"key": "a", "label": "Send strongest hero (+20 stress, +150g reward)", "effects": [{"type": "stress_hero_max", "value": 20}, {"type": "gold", "value": 150}], "result": "Your finest adventurer slays the beast! The town rewards you with 150g."},
            {"key": "b", "label": "Hire mercenaries (100g cost)", "effects": [{"type": "gold", "value": -100}], "result": "The mercenaries handle it efficiently. No glory, but no casualties."},
            {"key": "c", "label": "Ignore the threat (Renown -1)", "effects": [{"type": "renown", "value": -1}], "result": "Word spreads that your guild did nothing. Renown -1."},
        ]
    },
    {
        "name": "Rare Herb Discovery",
        "category": "wild",
        "rarity": "common",
        "minRenown": 0,
        "flavor": "Your adventurers discover a patch of rare medicinal herbs in the wilds. They could be used to treat stress or sold for gold.",
        "choices": [
            {"key": "a", "label": "Brew soothing tonics (-15 stress to all)", "effects": [{"type": "stress_all", "value": -15}], "result": "The herbal tonics work wonders. Everyone's stress drops."},
            {"key": "b", "label": "Sell to the apothecary (+200g)", "effects": [{"type": "gold", "value": 200}], "result": "The apothecary pays handsomely for fresh herbs. +200g."},
        ]
    },
    {
        "name": "Rival Guild Sabotage",
        "category": "guild",
        "rarity": "uncommon",
        "minRenown": 2,
        "flavor": "A rival guild has sabotaged your armory! The lockbox was picked — you can investigate or cut your losses.",
        "choices": [
            {"key": "a", "label": "Investigate (150g, recover 1 stolen item)", "effects": [{"type": "gold", "value": -150}, {"type": "armory_restore", "value": 1}], "result": "Your investigators track down the culprit and recover a piece of gear!"},
            {"key": "b", "label": "Accept the loss (lose 1 random armory item)", "effects": [{"type": "armory_lose", "value": 1}], "result": "One of your armory items is gone. You'll need to replace it."},
            {"key": "c", "label": "Pay a bounty on the rival (200g, Renown +1)", "effects": [{"type": "gold", "value": -200}, {"type": "renown", "value": 1}], "result": "The rival guild is publicly shamed. Renown +1, but it cost you."},
        ]
    },
    {
        "name": "Wandering Adventurer",
        "category": "guild",
        "rarity": "uncommon",
        "minRenown": 0,
        "flavor": "A down-on-their-luck adventurer seeks shelter at your guild. They have talent but need a break.",
        "choices": [
            {"key": "a", "label": "Offer a contract (free E-rank hero)", "effects": [{"type": "roster_add", "value": "E"}], "result": "The grateful adventurer signs on. A new E-rank hero joins your roster for free!"},
            {"key": "b", "label": "Give them 50g and send them off", "effects": [{"type": "gold", "value": -50}], "result": "They thank you for the kindness and continue their journey."},
            {"key": "c", "label": "Turn them away", "effects": [], "result": "They leave, disappointed. Life on the road is harsh."},
        ]
    },
    {
        "name": "Hero's Past",
        "category": "character",
        "rarity": "uncommon",
        "minRenown": 1,
        "flavor": "A shadow from one of your hero's past emerges! An old rival challenges them to a duel. Pride (and your hero's performance) is on the line.",
        "choices": [
            {"key": "a", "label": "Allow the duel (+15 stress to that hero)", "effects": [{"type": "stress_hero_random", "value": 15}], "result": "The duel is fierce but your hero prevails. Their stress climbs, but their spirit remains unbroken."},
            {"key": "b", "label": "Pay off the rival (100g)", "effects": [{"type": "gold", "value": -100}], "result": "Gold silences the challenger. The matter is settled quietly."},
            {"key": "c", "label": "Intervene with authority (Renown -1)", "effects": [{"type": "renown", "value": -1}], "result": "You pull rank to squash the conflict. Renown -1 for the political embarrassment."},
        ]
    },
]

def checkForEvent(renown, eventsFiredThisMonth=None):
    baseChance = 0.25 + (renown * 0.02)
    if random.random() > baseChance:
        return None
    eligible = [e for e in EVENTS if e["minRenown"] <= renown]
    if eventsFiredThisMonth:
        eligible = [e for e in eligible if e["name"] not in eventsFiredThisMonth]
    if not eligible:
        return None
    return random.choice(eligible)

def resolveEffects(effects, gs):
    logs = []
    for ef in effects:
        t = ef["type"]
        v = ef["value"]
        if t == "gold":
            gs["guildBank"] += v
            logs.append(f"Guild gold {'+' if v >= 0 else ''}{v}g")
        elif t == "renown":
            gs["renown"] = max(0, min(5, gs["renown"] + v))
            logs.append(f"Renown {'+' if v >= 0 else ''}{v}")
        elif t == "daysLeft":
            gs["daysLeft"] += v
            logs.append(f"Deadline {'extended by' if v >= 0 else 'shortened by'} {abs(v)} day(s)")
        elif t == "stress_all":
            for hero in gs["guildRoster"]:
                hero["stress"] = max(0, min(100, hero["stress"] + v))
            logs.append(f"All heroes stress {'+' if v >= 0 else ''}{v}")
        elif t == "stress_hero_random":
            if gs["guildRoster"]:
                hero = random.choice(gs["guildRoster"])
                hero["stress"] = max(0, min(100, hero["stress"] + v))
                logs.append(f"{hero['name']} stress {'+' if v >= 0 else ''}{v}")
        elif t == "stress_hero_max":
            if gs["guildRoster"]:
                hero = max(gs["guildRoster"], key=lambda h: h["stats"]["STR"] + h["stats"]["INT"] + h["stats"]["DEX"] + h["stats"]["FTH"])
                hero["stress"] = max(0, min(100, hero["stress"] + v))
                logs.append(f"{hero['name']} (strongest hero) stress {'+' if v >= 0 else ''}{v}")
        elif t == "armory_restore":
            total = sum(len(items) for items in gs["guildArmory"].values())
            if total == 0:
                logs.append("Nothing to restore — armory was empty.")
            else:
                logs.append("Recovered an armory item (no effect — armory untouched).")
        elif t == "armory_lose":
            cats = [c for c, items in gs["guildArmory"].items() if items]
            if cats:
                cat = random.choice(cats)
                lost = gs["guildArmory"][cat].pop(0)
                logs.append(f"Lost {lost['name']} from armory!")
            else:
                logs.append("Armory was already empty — no loss.")
        elif t == "roster_add":
            from modules import adventurerGeneration as ag
            rank = v
            newHero = ag.generateAdventurer(gs["renown"])
            newHero["rank"] = rank
            newHero["hiringFee"] = 0
            newHero["contractDays"] = 10
            newHero["contractDaysLeft"] = 10
            gs["guildRoster"].append(newHero)
            logs.append(f"{newHero['name']} ({rank}-rank) joins the guild for free!")
    return logs
