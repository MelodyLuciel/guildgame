#!/usr/bin/env python3
import warnings
import random

warnings.filterwarnings("ignore", message="unknown terminal capability:.*ssupm")

from blessed import Terminal
import modules.adventurerGeneration as ag
import modules.questGeneration as qg
import modules.armory as ar
import modules.randomEvents as re
import modules.facilities as fc
import modules.raidBoss as rb
import modules.tabs as tabs
import modules.menu as mn

term = Terminal()

if term.height < 25 or term.width < 60:
    with term.fullscreen():
        print(term.clear)
        print(term.bold_red("⚠  TERMINAL TOO SMALL  ⚠"))
        print()
        print(f"Detected: {term.width} × {term.height}")
        print(f"Minimum required: 60 × 25")
        print()
        print("Please enlarge your terminal window,")
        print("reduce font size, or use fullscreen mode.")
        print()
        print(term.italic("Press any key to continue anyway..."))
        term.inkey()

# --- GAME STATE ---
guildRoster = []
guildBank = 250
selectedIndex = 0
renown = 0
month = 1

benchRecruit = ag.generateAdventurer(renown)
questSlots = [
    qg.generateQuest("breadwinner", renown),
    qg.generateQuest("benchmark", renown),
    qg.generateQuest("highstakes", renown),
]
selectedQuestIndex = 0
taggedQuestSlot = None
currentDay = 1
daysLeft = 30
taxQuota = ag.getRenownCfg(renown)["tax"]
# upkeep per rank in ag.upkeepByRank
rerollsLeft = 5
actionMessage = "Guild ledger opened. Use Space to advance days."
currentTab = 1
facilities = {"hotSprings": {"level": 0, "active": True}, "trainingGrounds": {"level": 0, "active": True}}
facilityNames = ["hotSprings", "trainingGrounds"]
facilityDisplayNames = {"hotSprings": "Hot Springs", "trainingGrounds": "Training Grounds"}
selectedFacilityIndex = 0
monthStats = {}
eventsFiredThisMonth = set()
partyQuest = qg.generatePartyQuest(renown)
partySize = 2
partyMembers = []
guildArmory = {"weapon": [], "armor": [], "talisman": [], "relic": []}
armoryCategoryIndex = 0
armoryCategories = ["weapon", "armor", "talisman", "relic"]
selectedGearIndex = 0

raidBoss = None
raidStatus = "inactive"
raidPrepDaysLeft = 0
raidResult = None


def handleMonthEnd():
    global renown, month, currentDay, daysLeft, taxQuota, guildBank, monthStats, eventsFiredThisMonth

    met = guildBank >= taxQuota
    if met:
        renown += 1
    else:
        renown = max(0, renown - 1)
        penalty = taxQuota // 2
        guildBank -= penalty

    recapData = {
        "month": month,
        "taxQuota": taxQuota,
        "metQuota": met,
        "newRenown": renown,
        "newTitle": ag.getRenownCfg(renown)["title"],
        "daysPassed": monthStats.get("daysPassed", 0),
        "questIncome": monthStats.get("questIncome", 0),
        "questsSucceeded": monthStats.get("questsSucceeded", 0),
        "questsFailed": monthStats.get("questsFailed", 0),
        "heroUpkeep": monthStats.get("heroUpkeep", 0),
        "facilityUpkeep": monthStats.get("facilityUpkeep", 0),
        "facilitySoaks": monthStats.get("facilitySoaks", 0),
        "heroGearPurchases": monthStats.get("heroGearPurchases", 0),
        "eventsTriggered": monthStats.get("eventsTriggered", 0),
        "eventGoldImpact": monthStats.get("eventGoldImpact", 0),
        "guildBank": guildBank,
    }
    tabs.showMonthlyRecap(recapData)

    month += 1
    currentDay = 1
    daysLeft = 30
    taxQuota = ag.getRenownCfg(renown)["tax"]
    monthStats = {}
    eventsFiredThisMonth.clear()



# --- MAIN LOOP ---
with term.cbreak(), term.hidden_cursor():
    while True:
        print(term.clear)

        tabs.renderTabBar(currentTab, renown)
        tabs.renderStatusBar(guildBank, currentDay, daysLeft, renown, guildRoster, taxQuota)

        if currentTab == 1:
            tabs.renderRecruitTab(benchRecruit, guildRoster, guildBank, rerollsLeft, renown)
        elif currentTab == 2:
            tabs.renderQuestTab(questSlots, selectedQuestIndex, taggedQuestSlot, partyQuest, partySize, partyMembers)
        elif currentTab == 3:
            tabs.renderRosterTab(guildRoster, selectedIndex, renown, partyMembers, partySize, facilities)
        elif currentTab == 4:
            tabs.renderAccountantTab(guildBank, renown, month, daysLeft, taxQuota, guildRoster)
        elif currentTab == 5:
            tabs.renderArmoryTab(guildArmory, armoryCategoryIndex, guildRoster, selectedIndex, guildBank, renown, selectedGearIndex)
        elif currentTab == 6:
            tabs.renderFacilitiesTab(facilities, guildBank, renown, selectedFacilityIndex)
        elif currentTab == 7:
            tabs.renderRaidTab(raidBoss, raidStatus, guildRoster, raidResult)

        # --- BOTTOM PANEL ---
        if renown >= 5 and raidBoss is None:
            raidBoss = rb.generateBoss(renown)

        with term.location(0, term.height - 4):
            print(term.italic_white(f"LOG: {actionMessage}"))
        with term.location(0, term.height - 3):
            controls = ["[SPACE] Advance Day"]
            if currentTab == 1:
                controls.append("[A] Hire Recruit")
                controls.append("[R] Re-roll")
            if currentTab == 2:
                controls.append("[Q] Tag Quest")
                controls.append("[P] Party Size")
                controls.append("[UP/DOWN] Browse")
            if currentTab == 3:
                controls.append("[Q] Assign Hero")
                controls.append("[P] Party Toggle")
                controls.append("[S] Send Party")
                controls.append("[C] Clear Party")
                controls.append("[E] Extend")
                controls.append("[T] Terminate/Dismiss")
                controls.append("[UP/DOWN] Navigate")
            if currentTab == 5:
                controls.append("[B] Buy Gear")
                controls.append("[A] Assign to Hero")
                controls.append("[U] Unassign")
                controls.append("[P] Hero Purchase")
                controls.append("[LEFT/RIGHT] Category")
                controls.append("[[/] ] Gear")
                controls.append("[UP/DOWN] Hero")
            if currentTab == 6:
                controls.append("[U] Upgrade")
                controls.append("[T] Toggle Active")
                controls.append("[LEFT/RIGHT] Facility")
            if currentTab == 7:
                if raidStatus == "inactive":
                    controls.append("[R] Initiate Raid")
                elif raidStatus == "prepping":
                    controls.append("[C] Cancel Prep")
                elif raidStatus == "done":
                    controls.append("[V] View Log")
                    controls.append("[R] New Raid")
            controls.append("[`] Menu")
            controlLine = "  |  ".join(controls)
            if len(controlLine) > term.width:
                mid = len(controls) // 2
                print("  |  ".join(controls[:mid]))
                with term.location(0, term.height - 2):
                    print("  |  ".join(controls[mid:]))
            else:
                print(controlLine)

        key = term.inkey()

        if key == '`':
            gs = {
                "guildRoster": guildRoster,
                "guildBank": guildBank,
                "selectedIndex": selectedIndex,
                "renown": renown,
                "month": month,
                "benchRecruit": benchRecruit,
                "questSlots": questSlots,
                "selectedQuestIndex": selectedQuestIndex,
                "taggedQuestSlot": taggedQuestSlot,
                "currentDay": currentDay,
                "daysLeft": daysLeft,
                "rerollsLeft": rerollsLeft,
                "currentTab": currentTab,
                "facilities": facilities,
                "selectedFacilityIndex": selectedFacilityIndex,
                "monthStats": monthStats,
                "eventsFiredThisMonth": eventsFiredThisMonth,
                "partyQuest": partyQuest,
                "partySize": partySize,
                "partyMembers": partyMembers,
                "guildArmory": guildArmory,
                "armoryCategoryIndex": armoryCategoryIndex,
                "selectedGearIndex": selectedGearIndex,
                "raidBoss": raidBoss,
                "raidStatus": raidStatus,
                "raidPrepDaysLeft": raidPrepDaysLeft,
                "raidResult": raidResult,
            }
            action = mn.showMainMenu(gs)
            if action == "quit":
                print(term.clear)
                print("Thanks for playing!")
                break
            elif action == "load":
                guildRoster = gs["guildRoster"]
                guildBank = gs["guildBank"]
                selectedIndex = gs["selectedIndex"]
                renown = gs["renown"]
                month = gs["month"]
                benchRecruit = gs["benchRecruit"]
                questSlots = gs["questSlots"]
                selectedQuestIndex = gs["selectedQuestIndex"]
                taggedQuestSlot = gs["taggedQuestSlot"]
                currentDay = gs["currentDay"]
                daysLeft = gs["daysLeft"]
                rerollsLeft = gs["rerollsLeft"]
                currentTab = gs["currentTab"]
                facilities = gs["facilities"]
                selectedFacilityIndex = gs["selectedFacilityIndex"]
                monthStats = gs["monthStats"]
                eventsFiredThisMonth = gs["eventsFiredThisMonth"]
                partyQuest = gs["partyQuest"]
                partySize = gs["partySize"]
                partyMembers = gs["partyMembers"]
                guildArmory = gs["guildArmory"]
                armoryCategoryIndex = gs["armoryCategoryIndex"]
                selectedGearIndex = gs["selectedGearIndex"]
                raidBoss = gs["raidBoss"]
                raidStatus = gs["raidStatus"]
                raidPrepDaysLeft = gs["raidPrepDaysLeft"]
                raidResult = gs["raidResult"]
                taxQuota = ag.getRenownCfg(renown)["tax"]
                actionMessage = "Game loaded."
            continue

        if key == '1':
            currentTab = 1
        elif key == '2':
            currentTab = 2
        elif key == '3':
            currentTab = 3
        elif key == '4':
            currentTab = 4
        elif key == '5':
            currentTab = 5
        elif key == '6':
            currentTab = 6
        elif key == '7' and renown >= 5:
            currentTab = 7

        elif key == ' ':
            if not tabs.confirmAdvance():
                actionMessage = "Day advancement cancelled."
                continue

            currentDay += 1
            daysLeft -= 1
            benchRecruit = ag.generateAdventurer(renown)
            rerollsLeft = 5
            totalUpkeep = ag.getTotalUpkeep(guildRoster)
            guildBank = guildBank - totalUpkeep

            monthStats["heroUpkeep"] = monthStats.get("heroUpkeep", 0) + totalUpkeep
            monthStats["daysPassed"] = monthStats.get("daysPassed", 0) + 1

            daySummaryLogs = [f"Paid {totalUpkeep}g in total hero upkeep."]

            # --- RESOLVE PARTY QUESTS (all members together) ---
            resolvedPartyQuests = set()
            for hero in guildRoster:
                pq = hero.get('partyQuest')
                if pq is None or hero['status'] != "On Mission":
                    continue
                qid = id(pq)
                if qid in resolvedPartyQuests:
                    continue
                hero['missionDaysLeft'] = hero.get('missionDaysLeft', 2) - 1
                if hero['missionDaysLeft'] > 0:
                    continue
                resolvedPartyQuests.add(qid)
                party = [h for h in guildRoster if h.get('partyQuest') is pq]
                relevantStat = pq['statNeeded']
                combinedStat = 0
                for pm in party:
                    penalty = ag.getStressPenalty(pm['stress'])
                    gearBonus = ar.calculateGearBonus(pm, relevantStat)
                    injuryPenalty = ag.getInjuryPenalty(pm)
                    combinedStat += pm['stats'][relevantStat] + gearBonus - penalty - injuryPenalty
                combinedStat += ag.getSynergyBonus(party, relevantStat)
                partySizeActual = len(party)
                mult = qg.partySizeMult.get(partySizeActual, {"diff": 1.3, "reward": 1.8})
                scaledDifficulty = int(pq['difficulty'] * mult['diff'])
                diceRoll = random.randint(1, 20)
                success = (combinedStat + (diceRoll // 2)) >= scaledDifficulty
                if success:
                    reward = int(pq['reward'] * mult['reward'])
                    heroesShare = int(reward * 0.40)
                    guildProfit = reward - heroesShare
                    guildBank += guildProfit
                    shareEach = heroesShare // partySizeActual
                    for pm in party:
                        pm['gold'] += shareEach
                        pm['stress'] = min(100, pm['stress'] + 20)
                        pm['status'] = "Available"
                        del pm['partyQuest']
                        pm.pop('missionDaysLeft', None)
                    monthStats["questIncome"] = monthStats.get("questIncome", 0) + guildProfit
                    monthStats["questsSucceeded"] = monthStats.get("questsSucceeded", 0) + 1
                    names = ", ".join(pm['name'] for pm in party)
                    daySummaryLogs.append(f"[PARTY] {pq['name']} SUCCESS! {names} earned {guildProfit}g net!")
                else:
                    injuredNames = []
                    for pm in party:
                        cost = ag.getFailureCost(pm)
                        guildBank -= cost
                        pm['stress'] = min(100, pm['stress'] + 30)
                        ag.applyInjury(pm)
                        if pm.get('injuredDaysLeft', 0) > 0:
                            injuredNames.append(pm['name'])
                        pm['status'] = "Available"
                        del pm['partyQuest']
                        pm.pop('missionDaysLeft', None)
                        monthStats["questIncome"] = monthStats.get("questIncome", 0) - cost
                    monthStats["questsFailed"] = monthStats.get("questsFailed", 0) + 1
                    names = ", ".join(pm['name'] for pm in party)
                    log = f"[PARTY] {pq['name']} FAILED! {names} — "
                    if injuredNames:
                        log += f"INJURED: {', '.join(injuredNames)}. "
                    log += f"Medical bills: {sum(ag.getFailureCost(pm) for pm in party)}g."
                    daySummaryLogs.append(log)

            # --- RESOLVE REGULAR QUESTS ---
            for hero in guildRoster:
                if hero['status'] != "On Mission":
                    continue
                if hero.get('partyQuest'):
                    continue
                hero['missionDaysLeft'] = hero.get('missionDaysLeft', 1) - 1
                if hero['missionDaysLeft'] > 0:
                    continue
                quest = hero['currentQuest']
                relevantStat = quest['statNeeded']

                penalty = ag.getStressPenalty(hero['stress'])
                gearBonus = ar.calculateGearBonus(hero, relevantStat)
                injuryPenalty = ag.getInjuryPenalty(hero)
                effectiveStat = hero['stats'][relevantStat] + gearBonus - penalty - injuryPenalty
                effectiveLuck = hero['stats']['LCK'] - penalty - injuryPenalty

                luckBonus = effectiveLuck // 3
                diceRoll = random.randint(1, 20) + luckBonus

                if (effectiveStat + (diceRoll // 2)) >= quest['difficulty']:
                    totalPayout = quest['reward']
                    heroCut = int(totalPayout * 0.40)
                    supplyCost = int(totalPayout * 0.20)
                    guildProfit = totalPayout - (heroCut + supplyCost)

                    hero['gold'] += heroCut
                    guildBank += guildProfit
                    hero['stress'] = min(100, hero['stress'] + 20)
                    monthStats["questIncome"] = monthStats.get("questIncome", 0) + guildProfit
                    monthStats["questsSucceeded"] = monthStats.get("questsSucceeded", 0) + 1
                    daySummaryLogs.append(f"[SUCCESS] {hero['name']} brought home {guildProfit}g net!")
                else:
                    recoveryCost = ag.getFailureCost(hero)
                    guildBank = guildBank - recoveryCost
                    hero['stress'] = min(100, hero['stress'] + 30)
                    ag.applyInjury(hero)
                    monthStats["questIncome"] = monthStats.get("questIncome", 0) - recoveryCost
                    monthStats["questsFailed"] = monthStats.get("questsFailed", 0) + 1
                    injuryStr = " [INJURED]" if hero.get('injuredDaysLeft', 0) > 0 else ""
                    daySummaryLogs.append(f"[CRITICAL FAILURE] {hero['name']} failed! Medical bill: -{recoveryCost}g.{injuryStr}")

                hero['status'] = "Available"
                hero.pop('missionDaysLeft', None)

            # --- CLEANUP QUEST SLOTS ---
            for hero in guildRoster:
                if hero.get('questSlot') is not None:
                    slot = hero['questSlot']
                    if questSlots[slot]['type'] in ("benchmark", "highstakes"):
                        questSlots[slot] = qg.generateQuest(questSlots[slot]['type'], renown)
                    hero['questSlot'] = None
                    hero.pop('currentQuest', None)

            facilityLogs = fc.applyFacility(facilities, guildRoster)
            daySummaryLogs.extend(f"[FACILITY] {log}" for log in facilityLogs)

            facilityCost = fc.totalUpkeep(facilities)
            if facilityCost > 0:
                guildBank -= facilityCost
                monthStats["facilityUpkeep"] = monthStats.get("facilityUpkeep", 0) + facilityCost
                daySummaryLogs.append(f"[FACILITY] Facility upkeep: -{facilityCost}g")
            monthStats["facilitySoaks"] = monthStats.get("facilitySoaks", 0) + len(facilityLogs)

            trainingLogs = fc.applyTrainingGrounds(facilities, guildRoster)
            daySummaryLogs.extend(f"[TRAINING] {log}" for log in trainingLogs)
            monthStats["trainingGains"] = monthStats.get("trainingGains", 0) + len(trainingLogs)

            # --- RESOLVE RAID (prep complete) ---
            if raidStatus == "prepping":
                raidPrepDaysLeft -= 1
                if raidPrepDaysLeft <= 0:
                    raidResult = rb.resolveRaid(raidBoss, guildRoster)
                    if raidResult["success"]:
                        guildBank += raidResult["goldReward"]
                        for hero in guildRoster:
                            hero["stress"] = min(100, hero["stress"] + 25)
                            hero["status"] = "Available"
                        guildArmory["relic"].clear()
                        guildArmory["relic"].append({
                            "name": raidResult["relic"],
                            "stat": "ALL",
                            "bonus": 2,
                            "slot": "relic",
                            "tier": "relic",
                            "guildCost": 0,
                            "heroCost": 0,
                        })
                        monthStats["questIncome"] = monthStats.get("questIncome", 0) + raidResult["goldReward"]
                        monthStats["questsSucceeded"] = monthStats.get("questsSucceeded", 0) + 1
                        daySummaryLogs.append(f"[RAID] ★ {raidBoss['name']} DEFEATED! +{raidResult['goldReward']}g, Relic: {raidResult['relic']}!")
                    else:
                        for hero in guildRoster:
                            hero["stress"] = min(100, hero["stress"] + 40)
                            if hero["name"] in raidResult["injuredHeroes"]:
                                hero["injuredDaysLeft"] = 2
                            hero["status"] = "Available"
                        guildBank -= raidResult["failureCost"]
                        monthStats["questIncome"] = monthStats.get("questIncome", 0) - raidResult["failureCost"]
                        monthStats["questsFailed"] = monthStats.get("questsFailed", 0) + 1
                        daySummaryLogs.append(f"[RAID] ✖ {raidBoss['name']} VICTORIOUS! Lost {raidResult['failureCost']}g.")
                    raidStatus = "done"
                    daySummaryLogs.append("  Press [V] on Raid tab to view full combat log.")

            for hero in guildRoster:
                if hero['status'] != "On Mission":
                    hero['stress'] = max(0, hero['stress'] - 15)

            for hero in guildRoster:
                ag.tickInjury(hero)

            for hero in guildRoster:
                if hero['status'] not in ("On Mission", "Preparing for Raid"):
                    hero['contractDaysLeft'] -= 1
                    if hero['contractDaysLeft'] <= 0:
                        hero['contractDaysLeft'] = 0
                        hero['status'] = "Contract Expired"

            event = re.checkForEvent(renown, eventsFiredThisMonth)
            if event is not None:
                if event["name"] == "City Festival":
                    cost = (renown + 1) * 100
                    if renown >= 5:
                        event = {**event, "choices": [c for c in event["choices"] if c["key"] != "a"]}
                    else:
                        choices = []
                        for c in event["choices"]:
                            if c["key"] == "a":
                                choices.append({
                                    **c, "label": f"Donate {cost}g (Renown +1)",
                                    "effects": [{"type": "gold", "value": -cost}, {"type": "renown", "value": 1}],
                                })
                            else:
                                choices.append(c)
                        event = {**event, "choices": choices}
                choice = tabs.showEventPopup(event)
                gs = {
                    "guildBank": guildBank,
                    "renown": renown,
                    "daysLeft": daysLeft,
                    "guildRoster": guildRoster,
                    "guildArmory": guildArmory,
                }
                eventsFiredThisMonth.add(event["name"])
                eventLogs = re.resolveEffects(choice["effects"], gs)
                guildBank = gs["guildBank"]
                renown = gs["renown"]
                daysLeft = gs["daysLeft"]
                monthStats["eventsTriggered"] = monthStats.get("eventsTriggered", 0) + 1
                for ef in choice["effects"]:
                    if ef["type"] == "gold":
                        monthStats["eventGoldImpact"] = monthStats.get("eventGoldImpact", 0) + ef["value"]
                daySummaryLogs.append(f"[EVENT] {event['name']}: {choice['result']}")
                daySummaryLogs.extend(f"  {log}" for log in eventLogs)

            partyQuest = qg.generatePartyQuest(renown)
            partyMembers = []

            actionMessage = f"Day {currentDay} began. Last day summary logged."
            tabs.showDayResults(daySummaryLogs)

            if daysLeft <= 0:
                handleMonthEnd()

        elif key.lower() == 'a' and currentTab == 1:
            maxH = ag.getRenownCfg(renown)["maxHeroes"]
            if len(guildRoster) < maxH and guildBank >= benchRecruit['hiringFee']:
                guildRoster.append(benchRecruit)
                guildBank -= benchRecruit['hiringFee']
                actionMessage = f"Hired {benchRecruit['name']}!"
                benchRecruit = ag.generateAdventurer(renown)
            else:
                actionMessage = "Your barracks are full!" if len(guildRoster) >= ag.getRenownCfg(renown)["maxHeroes"] else "Not enough gold in the vault to hire this recruit!"

        elif key.lower() == 'r' and currentTab == 1:
            if rerollsLeft > 0:
                benchRecruit = ag.generateAdventurer(renown)
                rerollsLeft -= 1
                actionMessage = f"Recruit pool refreshed. ({rerollsLeft}/5 re-rolls left today)"
            else:
                actionMessage = "No re-rolls left for today! Advance the day to refresh."

        elif key.name == 'KEY_UP':
            if currentTab == 2:
                selectedQuestIndex = max(0, selectedQuestIndex - 1)
            elif currentTab == 3 and len(guildRoster) > 0:
                selectedIndex = max(0, selectedIndex - 1)
            elif currentTab == 5 and len(guildRoster) > 0:
                selectedIndex = max(0, selectedIndex - 1)

        elif key.name == 'KEY_DOWN':
            if currentTab == 2:
                selectedQuestIndex = min(2, selectedQuestIndex + 1)
            elif currentTab == 3 and len(guildRoster) > 0:
                selectedIndex = min(len(guildRoster) - 1, selectedIndex + 1)
            elif currentTab == 5 and len(guildRoster) > 0:
                selectedIndex = min(len(guildRoster) - 1, selectedIndex + 1)

        elif key.name == 'KEY_LEFT' and currentTab == 5:
            armoryCategoryIndex = max(0, armoryCategoryIndex - 1)
            cat = armoryCategories[armoryCategoryIndex]
            selectedGearIndex = max(0, min(selectedGearIndex, len(guildArmory[cat]) - 1))
            actionMessage = "Switched armory category."

        elif key.name == 'KEY_RIGHT' and currentTab == 5:
            armoryCategoryIndex = min(3, armoryCategoryIndex + 1)
            cat = armoryCategories[armoryCategoryIndex]
            selectedGearIndex = max(0, min(selectedGearIndex, len(guildArmory[cat]) - 1))
            actionMessage = "Switched armory category."

        elif key.name == 'KEY_LEFT' and currentTab == 6:
            selectedFacilityIndex = max(0, selectedFacilityIndex - 1)
            actionMessage = f"Selected {facilityDisplayNames[facilityNames[selectedFacilityIndex]]}."

        elif key.name == 'KEY_RIGHT' and currentTab == 6:
            selectedFacilityIndex = min(len(facilityNames) - 1, selectedFacilityIndex + 1)
            actionMessage = f"Selected {facilityDisplayNames[facilityNames[selectedFacilityIndex]]}."

        elif key == '[' and currentTab == 5:
            cat = armoryCategories[armoryCategoryIndex]
            if len(guildArmory[cat]) > 0:
                selectedGearIndex = max(0, selectedGearIndex - 1)
                actionMessage = "Moved to previous gear."
            else:
                actionMessage = "No gear in this category."

        elif key == ']' and currentTab == 5:
            cat = armoryCategories[armoryCategoryIndex]
            if len(guildArmory[cat]) > 0:
                selectedGearIndex = min(len(guildArmory[cat]) - 1, selectedGearIndex + 1)
                actionMessage = "Moved to next gear."
            else:
                actionMessage = "No gear in this category."

        elif key.lower() == 'p' and currentTab == 2:
            partySize = [2, 3, 4][([2, 3, 4].index(partySize) + 1) % 3]
            actionMessage = f"Party expedition size set to {partySize}."

        elif key.lower() == 'p' and currentTab == 3:
            if len(guildRoster) > 0:
                idx = selectedIndex
                if idx in partyMembers:
                    partyMembers.remove(idx)
                    actionMessage = f"{guildRoster[idx]['name']} removed from party."
                else:
                    if len(partyMembers) < partySize:
                        partyMembers.append(idx)
                        actionMessage = f"{guildRoster[idx]['name']} added to party ({len(partyMembers)}/{partySize})."
                    else:
                        actionMessage = f"Party is full ({partySize}/{partySize}). Use [C] to clear."
            else:
                actionMessage = "No heroes in roster to add."

        elif key.lower() == 's' and currentTab == 3:
            if len(partyMembers) == partySize:
                for idx in partyMembers:
                    hero = guildRoster[idx]
                    hero['status'] = "On Mission"
                    hero['missionDaysLeft'] = 2
                    hero['partyQuest'] = partyQuest
                names = ", ".join(guildRoster[idx]['name'] for idx in partyMembers)
                actionMessage = f"Party sent! {names} departed on {partyQuest['name']} (2 days)."
                partyMembers = []
            else:
                actionMessage = f"Need exactly {partySize} heroes in party (have {len(partyMembers)}). Use [P] to toggle."

        elif key.lower() == 'c' and currentTab == 3:
            if partyMembers:
                partyMembers = []
                actionMessage = "Party selection cleared."
            else:
                actionMessage = "No party to clear."

        elif key.lower() == 'q' and currentTab == 2:
            quest = questSlots[selectedQuestIndex]
            if quest['status'] == "available":
                if taggedQuestSlot == selectedQuestIndex:
                    taggedQuestSlot = None
                    actionMessage = f"Untagged '{quest['name']}'."
                else:
                    taggedQuestSlot = selectedQuestIndex
                    actionMessage = f"Tagged '{quest['name']}' for assignment. Head to Roster (tab 3) to assign a hero."
            elif quest['status'] == "contracted":
                actionMessage = "This quest has already been contracted."
            else:
                actionMessage = "Unknown quest status."

        elif key.lower() == 'q' and currentTab == 3:
            if len(guildRoster) > 0:
                worker = guildRoster[selectedIndex]
                if worker['status'] == "Available":
                    if taggedQuestSlot is not None:
                        quest = questSlots[taggedQuestSlot]
                        if quest['status'] == "available":
                            worker['currentQuest'] = {
                                "name": quest['name'],
                                "statNeeded": quest['statNeeded'],
                                "difficulty": quest['difficulty'],
                                "reward": quest['reward'],
                            }
                            worker['questSlot'] = taggedQuestSlot
                            worker['status'] = "On Mission"
                            worker['missionDaysLeft'] = 1
                            quest['status'] = "contracted"
                            quest['contracted_by'] = worker['name']
                            if quest['type'] == "breadwinner":
                                questSlots[taggedQuestSlot] = qg.generateQuest("breadwinner", renown)
                            taggedQuestSlot = None
                            actionMessage = f"{worker['name']} signed '{quest['name']}'!"
                        else:
                            actionMessage = "That quest is no longer available!"
                            taggedQuestSlot = None
                    else:
                        actionMessage = "Tag a quest first on the Bulletin (tab 2)!"
                else:
                    actionMessage = f"{worker['name']} is already away or unavailable today!"
            else:
                actionMessage = "You don't have any adventurers in your roster to send!"

        elif key.lower() == 'e' and currentTab == 3:
            if len(guildRoster) > 0:
                worker = guildRoster[selectedIndex]
                if worker['status'] == "Contract Expired":
                    cost = ag.extendCost(worker)
                    if guildBank >= cost:
                        tabs.drawPopup([
                            "",
                            f"   Extend {worker['name']}'s contract?   ",
                            f"   Cost: {cost}g   ",
                            "",
                            "     [Y] Yes     [N] Cancel      ",
                            "",
                        ])
                        confirm = term.inkey()
                        if confirm.lower() == 'y':
                            guildBank -= cost
                            cMin, cMax = ag.contractRanges[worker['rank']]
                            worker['contractDays'] = random.randint(cMin, cMax)
                            worker['contractDaysLeft'] = worker['contractDays']
                            worker['status'] = "Available"
                            actionMessage = f"{worker['name']}'s contract extended for {cost}g!"
                        else:
                            actionMessage = "Contract extension cancelled."
                    else:
                        actionMessage = f"Not enough gold to extend {worker['name']}'s contract! Need {cost}g."
                else:
                    actionMessage = f"{worker['name']}'s contract is still active ({worker['contractDaysLeft']} days left)."
            else:
                actionMessage = "No adventurer to extend."

        elif key.lower() == 't' and currentTab == 3:
            if len(guildRoster) > 0:
                worker = guildRoster[selectedIndex]
                if worker['status'] == "Contract Expired":
                    tabs.drawPopup([
                        "",
                        f"   Dismiss {worker['name']}?   ",
                        "   No compensation needed.   ",
                        "",
                        "     [Y] Yes     [N] Cancel      ",
                        "",
                    ])
                    confirm = term.inkey()
                    if confirm.lower() == 'y':
                        lostGear = []
                        for slot, gear in worker.get('equipment', {}).items():
                            if gear is not None:
                                if gear.get('heroOwned'):
                                    lostGear.append(gear['name'])
                                else:
                                    guildArmory[slot].append(gear)
                                worker['equipment'][slot] = None
                        msg = f"{worker['name']} dismissed (contract expired)."
                        if lostGear:
                            msg += f" They took their gear: {', '.join(lostGear)}."
                        actionMessage = msg
                        guildRoster.pop(selectedIndex)
                        if selectedIndex >= len(guildRoster):
                            selectedIndex = max(0, len(guildRoster) - 1)
                    else:
                        actionMessage = "Dismissal cancelled."
                elif worker['status'] == "Available":
                    cost = ag.terminateCost(worker)
                    tabs.drawPopup([
                        "",
                        f"   Terminate {worker['name']}?   ",
                        f"   Compensation: {cost}g   ",
                        "",
                        "     [Y] Yes     [N] Cancel      ",
                        "",
                    ])
                    confirm = term.inkey()
                    if confirm.lower() == 'y':
                        if guildBank >= cost:
                            guildBank -= cost
                            lostGear = []
                            for slot, gear in worker.get('equipment', {}).items():
                                if gear is not None:
                                    if gear.get('heroOwned'):
                                        lostGear.append(gear['name'])
                                    else:
                                        guildArmory[slot].append(gear)
                                    worker['equipment'][slot] = None
                            msg = f"{worker['name']} terminated. Paid {cost}g compensation."
                            if lostGear:
                                msg += f" They took their gear: {', '.join(lostGear)}."
                            actionMessage = msg
                            guildRoster.pop(selectedIndex)
                            if selectedIndex >= len(guildRoster):
                                selectedIndex = max(0, len(guildRoster) - 1)
                        else:
                            actionMessage = f"Not enough gold to terminate {worker['name']}! Need {cost}g."
                    else:
                        actionMessage = "Termination cancelled."
                else:
                    actionMessage = f"{worker['name']} is away on a mission — can't terminate right now."
            else:
                actionMessage = "No adventurer to dismiss."

        elif key.lower() == 'b' and currentTab == 5:
            cat = armoryCategories[armoryCategoryIndex]
            if cat == "relic":
                actionMessage = "Relics cannot be bought — earn them by defeating the Raid Boss (Tab 7)."
                continue
            maxSlots = ar.getMaxSlots(renown)[cat]
            if len(guildArmory[cat]) < maxSlots:
                tiers = ar.getAvailableTiers(renown)
                tier = random.choice(tiers)
                gear = ar.generateGear(cat, tier)
                if guildBank >= gear['guildCost']:
                    guildBank -= gear['guildCost']
                    guildArmory[cat].append(gear)
                    actionMessage = f"Purchased {gear['name']} for {gear['guildCost']}g!"
                else:
                    actionMessage = f"Not enough gold! {gear['name']} costs {gear['guildCost']}g."
            else:
                actionMessage = f"Armory {cat} slots full! ({len(guildArmory[cat])}/{maxSlots})"

        elif key.lower() == 'a' and currentTab == 5:
            cat = armoryCategories[armoryCategoryIndex]
            if len(guildArmory[cat]) > 0 and len(guildRoster) > 0:
                hero = guildRoster[selectedIndex]
                if hero['equipment'][cat] is None:
                    gear = guildArmory[cat][selectedGearIndex]
                    hero['equipment'][cat] = gear
                    guildArmory[cat].pop(selectedGearIndex)
                    selectedGearIndex = max(0, min(selectedGearIndex, len(guildArmory[cat]) - 1))
                    actionMessage = f"Assigned {gear['name']} to {hero['name']}."
                else:
                    actionMessage = f"{hero['name']}'s {cat} slot is already occupied!"
            else:
                actionMessage = "No gear to assign or no heroes in roster."

        elif key.lower() == 'u' and currentTab == 5:
            cat = armoryCategories[armoryCategoryIndex]
            if len(guildRoster) > 0:
                hero = guildRoster[selectedIndex]
                if hero['equipment'][cat] is not None:
                    gear = hero['equipment'][cat]
                    if gear.get('heroOwned'):
                        actionMessage = f"Can't unassign — {gear['name']} belongs to {hero['name']} now."
                        continue
                    hero['equipment'][cat] = None
                    guildArmory[cat].append(gear)
                    actionMessage = f"Unassigned {gear['name']} from {hero['name']}."
                else:
                    actionMessage = f"{hero['name']} has no {cat} equipped."
            else:
                actionMessage = "No heroes in roster."

        elif key.lower() == 'p' and currentTab == 5:
            cat = armoryCategories[armoryCategoryIndex]
            if cat == "relic":
                actionMessage = "Relics cannot be purchased by heroes — they belong to the guild."
                continue
            if len(guildRoster) > 0:
                hero = guildRoster[selectedIndex]
                gear = hero['equipment'][cat]
                if gear is not None:
                    if gear.get('heroOwned'):
                        actionMessage = f"This {gear['name']} already belongs to {hero['name']}!"
                        continue
                    if hero['gold'] >= gear['heroCost']:
                        hero['gold'] -= gear['heroCost']
                        guildBank += gear['heroCost']
                        gear['heroOwned'] = True
                        monthStats["heroGearPurchases"] = monthStats.get("heroGearPurchases", 0) + 1
                        actionMessage = f"{hero['name']} purchased {gear['name']} for {gear['heroCost']}g! It's theirs forever."
                    else:
                        actionMessage = f"{hero['name']} only has {hero['gold']}g — needs {gear['heroCost']}g to purchase."
                else:
                    actionMessage = f"{hero['name']} has no {cat} equipped to purchase."
            else:
                actionMessage = "No heroes in roster."

        elif key.lower() == 'u' and currentTab == 6:
            name = facilityNames[selectedFacilityIndex]
            displayName = facilityDisplayNames[name]
            if fc.canUpgrade(facilities, name, renown, guildBank):
                cost = fc.upgradeCost(facilities, name)
                facilities[name]["level"] += 1
                facilities[name]["active"] = True
                guildBank -= cost
                nl = fc.getLevelInfo(facilities, name)
                actionMessage = f"{displayName} upgraded to level {nl['level']}! {nl['desc']}"
            else:
                nl = fc.nextLevel(facilities, name)
                if nl is None:
                    actionMessage = f"{displayName} is already at maximum level!"
                elif renown < nl["renownReq"]:
                    actionMessage = f"Need renown {nl['renownReq']} to upgrade (currently {renown})."
                else:
                    actionMessage = f"Not enough gold! Need {nl['cost']}g."

        elif key.lower() == 't' and currentTab == 6:
            name = facilityNames[selectedFacilityIndex]
            displayName = facilityDisplayNames[name]
            if facilities[name]["level"] == 0:
                actionMessage = f"{displayName} is not built yet. Upgrade to level 1 first."
            else:
                was = facilities[name]["active"]
                facilities[name]["active"] = not was
                actionMessage = f"{displayName} toggled {'OFF' if was else 'ON'}."

        elif key.lower() == 'r' and currentTab == 7:
            if raidStatus == "inactive":
                ready = sum(1 for h in guildRoster if h["status"] == "Available")
                if len(guildRoster) == 7 and ready == 7:
                    if raidBoss is None:
                        raidBoss = rb.generateBoss(renown)
                    raidStatus = "prepping"
                    raidPrepDaysLeft = 1
                    for hero in guildRoster:
                        hero["status"] = "Preparing for Raid"
                    actionMessage = f"Raid preparations begun! Heroes locked in for {raidPrepDaysLeft} day."
                else:
                    actionMessage = "Need exactly 7/7 available heroes to initiate a raid."
            elif raidStatus == "done":
                raidBoss = rb.generateBoss(renown)
                raidStatus = "inactive"
                raidResult = None
                actionMessage = "New raid boss generated. Prepare your roster."
            else:
                actionMessage = "Raid is already in progress."

        elif key.lower() == 'c' and currentTab == 7:
            if raidStatus == "prepping":
                raidStatus = "inactive"
                for hero in guildRoster:
                    if hero["status"] == "Preparing for Raid":
                        hero["status"] = "Available"
                actionMessage = "Raid preparations cancelled. Heroes released."
            else:
                actionMessage = "Nothing to cancel."

        elif key.lower() == 'v' and currentTab == 7:
            if raidResult is not None:
                tabs.showRaidResultPopup(raidResult)
            else:
                actionMessage = "No raid log available."


        else:
            actionMessage = "Unknown command."
