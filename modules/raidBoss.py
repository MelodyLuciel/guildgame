import random
from modules import adventurerGeneration as ag

bossThemes = [
    {
        "name": "Crimson Colossus",
        "statNeeded": "STR",
        "flavor": {
            "enter": [
                "The earth trembles as a towering giant of molten stone rises from the caldera.",
                "Searing heat washes over the party as the Colossus takes its first thundering step.",
            ],
            "wave_success": [
                "Lava hounds scatter as the party cuts through their ranks.",
                "The party dodges a rain of molten debris and pushes deeper into the crater.",
                "Fire-elementals crumble to ash beneath the heroes' coordinated assault.",
            ],
            "wave_failure": [
                "The party is battered by a surge of lava hounds but forces through.",
                "Molten debris catches two heroes off guard — they shake it off and press on.",
                "The heat is overwhelming; the party takes heavy hits but refuses to fall.",
            ],
            "phase_intro": [
                "The Colossus slams its fists together, sending a shockwave across the peak!",
                "With a deafening roar, the giant's chest ignites — the true battle begins!",
                "Cracks spread across the Colossus's form as a blinding light erupts from within!",
                "The ground splits as the Colossus drives its fists into the earth, summoning a ring of fire!",
                "The giant's eyes glow white-hot as it enters a frenzied state — steel yourself!",
            ],
            "victory": [
                "The Colossus crumbles into a mountain of slag. The guild has felled a legend!",
                "With a final thunderous crash, the Crimson Colossus collapses. Victory is yours!",
            ],
            "defeat": [
                "The party lies scattered among the rubble. The Colossus stands immovable.",
                "One by one, the heroes fall. The mountain claims another would-be legend.",
            ],
        },
    },
    {
        "name": "Void Lich",
        "statNeeded": "FTH",
        "flavor": {
            "enter": [
                "An ancient crypt exhales a breath of decay as the party descends into darkness.",
                "Bones crunch underfoot as the heroes venture into the Lich's Domain.",
            ],
            "wave_success": [
                "Skeletal legions shatter under the party's blessed weapons.",
                "The heroes dispel a wave of wraiths with holy light and cold steel.",
                "Necrotic traps are dismantled one by one — the party advances unchallenged.",
            ],
            "wave_failure": [
                "A phalanx of bone knights pushes the party back, but they hold the line.",
                "Wraiths phase through armor, draining strength — the party grits their teeth.",
                "The crypt's curses sap the heroes' vitality, but they press deeper into the dark.",
            ],
            "phase_intro": [
                "The Lich rises from its throne of bone, a sphere of void pulsing in its chest!",
                "Reality warps as the Lich speaks a Word of Unmaking — the second phase begins!",
                "The Lich's form shatters into a swarm of shadow, reassembling in a flash of violet light!",
                "Skeletal hands erupt from the ground as the Lich chants an incantation of pure entropy!",
                "The temperature plummets as the Lich draws the very warmth from the air — phase shift!",
            ],
            "victory": [
                "The Lich's phylactery cracks, then explodes in a pillar of white light. The undead horde crumbles to dust.",
                "With a final scream that shakes the crypt, the Void Lich is undone. The guild prevails!",
            ],
            "defeat": [
                "The Lich's laughter echoes through the crypt as the last hero falls to their knees.",
                "Darkness consumes the expedition. The Lich remains — ancient, patient, victorious.",
            ],
        },
    },
    {
        "name": "Storm Tyrant",
        "statNeeded": "DEX",
        "flavor": {
            "enter": [
                "A fortress of roiling clouds swirls atop the mountain peak — the Storm Tyrant's lair.",
                "Lightning splits the sky as the party ascends into the heart of the tempest.",
            ],
            "wave_success": [
                "Wind elementals are scattered by precise arrows and rapid strikes.",
                "The party weaves through lightning strikes, closing in on the Tyrant's perch.",
                "Gusts of cyclone-force wind are countered by the heroes' unwavering footing.",
            ],
            "wave_failure": [
                "The party is battered by hail and gale-force winds but pushes through the squall.",
                "A lightning bolt grazes the flank — the heroes are slowed but not stopped.",
                "Cyclones force the party to take cover, costing them valuable energy.",
            ],
            "phase_intro": [
                "The clouds part to reveal the Storm Tyrant, crackling with raw elemental fury!",
                "The Tyrant roars, and the sky answers — lightning rains down as the true fight begins!",
                "Eyes blazing with stormfire, the Tyrant descends from the tempest's core!",
                "A deafening thunderclap heralds the Tyrant's next form — the winds themselves become weapons!",
                "The sky darkens as the Tyrant summons a vortex of lightning and hail — brace for impact!",
            ],
            "victory": [
                "The storm dissipates. The Tyrant plummets from the sky, defeated. The skies clear in tribute.",
                "With a final thunderclap, the Storm Tyrant falls. The guild has tamed the tempest!",
            ],
            "defeat": [
                "The storm howls in triumph as the last hero is struck down by lightning.",
                "The Tempest claims another challenger. The Tyrant rules the skies unchallenged.",
            ],
        },
    },
]

relicNames = [
    "Relic of the Sun", "Relic of the Moon", "Relic of the Deep",
    "Relic of the Ancients", "Relic of the Forgotten",
]

def generateBoss(renown=5):
    theme = random.choice(bossThemes)
    numWaves = random.randint(1, 3)
    numPhases = random.randint(2, 3)
    baseHP = 70 + renown * 10
    baseATK = 20 + renown * 2
    phases = []
    for i in range(numPhases):
        mult = 1.0 + i * 0.5
        phases.append({
            "name": f"Phase {i + 1}",
            "hp": int(baseHP * mult),
            "atk": int(baseATK + i * 5),
        })
    goldReward = 5000 + renown * 1000
    return {
        "name": theme["name"],
        "statNeeded": theme["statNeeded"],
        "flavor": theme["flavor"],
        "numWaves": numWaves,
        "phases": phases,
        "numPhases": numPhases,
        "goldReward": goldReward * numPhases,
        "relic": random.choice(relicNames),
    }

def getPartyHP(guildRoster):
    total = 0
    for hero in guildRoster:
        total += 50 + hero["stats"]["LCK"] * 2
    return total

def getCombinedStat(guildRoster, statNeeded):
    total = 0
    for hero in guildRoster:
        penalty = ag.getStressPenalty(hero["stress"])
        gearBonus = 0
        for slot, gear in hero.get("equipment", {}).items():
            if gear is not None and (gear.get("stat") == statNeeded or gear.get("stat") == "ALL"):
                gearBonus += gear["bonus"]
        injuryPenalty = ag.getInjuryPenalty(hero)
        total += hero["stats"][statNeeded] + gearBonus - penalty - injuryPenalty
    synergyBonus = ag.getSynergyBonus(guildRoster, statNeeded)
    return total + synergyBonus

def resolveRaid(boss, guildRoster):
    combinedStat = getCombinedStat(guildRoster, boss["statNeeded"])
    partyHP = getPartyHP(guildRoster)
    maxPartyHP = partyHP
    log = []

    theme = boss["flavor"]

    log.append({"type": "enter", "text": random.choice(theme["enter"])})

    roundsPerPhase = 3
    totalCombatRounds = boss["numPhases"] * roundsPerPhase
    heroDmgPerRound = max(1, combinedStat // totalCombatRounds)
    failed = False

    for wave in range(boss["numWaves"]):
        waveDifficulty = 40 + wave * 10 + boss["numPhases"] * 5
        success = combinedStat >= waveDifficulty
        if success:
            log.append({"type": "wave", "wave": wave + 1, "won": True, "text": random.choice(theme["wave_success"])})
        else:
            log.append({"type": "wave", "wave": wave + 1, "won": False, "text": random.choice(theme["wave_failure"])})
            partyHP -= 30 + boss["numPhases"] * 5
            if partyHP <= 0:
                failed = True
                break

    if not failed:
        phaseTexts = random.sample(theme["phase_intro"], boss["numPhases"])
        for phaseIdx, phase in enumerate(boss["phases"]):
            log.append({"type": "phase_intro", "phase": phaseIdx + 1, "text": phaseTexts[phaseIdx]})
            phaseHP = phase["hp"]
            phaseAtk = phase["atk"]
            for r in range(roundsPerPhase):
                phaseHP -= heroDmgPerRound
                partyHP -= phaseAtk
                log.append({
                    "type": "round",
                    "phase": phaseIdx + 1,
                    "round": r + 1,
                    "bossHP": max(0, phaseHP),
                    "partyHP": max(0, partyHP),
                    "maxBossHP": phase["hp"],
                    "maxPartyHP": maxPartyHP,
                })
                if partyHP <= 0:
                    failed = True
                    break
            if failed:
                break

    injuredHeroes = []
    if failed:
        log.append({"type": "defeat", "text": random.choice(theme["defeat"])})
        for hero in guildRoster:
            if random.random() < 0.30:
                injuredHeroes.append(hero["name"])
        failureCost = sum(ag.getFailureCost(h) for h in guildRoster)
        return {
            "success": False,
            "log": log,
            "injuredHeroes": injuredHeroes,
            "failureCost": failureCost,
            "goldReward": 0,
            "relic": None,
        }
    else:
        log.append({"type": "victory", "text": random.choice(theme["victory"])})
        return {
            "success": True,
            "log": log,
            "injuredHeroes": [],
            "failureCost": 0,
            "goldReward": boss["goldReward"],
            "relic": boss["relic"],
        }
