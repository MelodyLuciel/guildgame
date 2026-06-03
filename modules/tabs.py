import re
import sys
import textwrap
from blessed import Terminal
import modules.adventurerGeneration as ag
import modules.armory as ar
import modules.facilities as fc
from modules.questGeneration import partySizeMult

term = Terminal()

rankColors = {
    "E": term.dimgray,
    "D": term.white,
    "C": term.green,
    "B": term.cyan,
    "A": term.yellow,
    "S": term.bold_magenta,
}

stressColors = {
    "Rested": term.dimgray,
    "Strained": term.yellow,
    "Fatigued": term.bold_yellow,
    "Exhausted": term.bold_red,
    "Broken": term.bold_magenta,
}

def renderTabBar(currentTab, renown=0):
    with term.location(0, 0):
        labels = ["Recruitment", "Quest Board", "Guild Roster", "Accountant", "Armory", "Facilities"]
        if renown >= 5:
            labels.append("Raid")
        parts = []
        for i, label in enumerate(labels):
            num = i + 1
            if currentTab == num:
                parts.append(f"{term.bold_white(f'[{num}]')} {term.bold_underline(label)}")
            else:
                parts.append(f"{term.dimgray(f'[{num}]')} {label}")
        print("  ".join(parts))

def renderStatusBar(guildBank, currentDay, daysLeft, renown, guildRoster, taxQuota):
    with term.location(0, 1):
        cfg = ag.getRenownCfg(renown)
        title = cfg["title"]
        maxH = cfg["maxHeroes"]
        status = f"Gold: {term.bold_yellow(str(guildBank))}g  |  Day {currentDay}/{daysLeft}  |  Renown: {renown} ({title})  |  Heroes: {len(guildRoster)}/{maxH}  |  Tax: {taxQuota}g"
        print(term.cyan(status))

def renderRecruitTab(benchRecruit, guildRoster, guildBank, rerollsLeft, renown):
    with term.location(0, 2):
        print(term.bold_cyan("=== RECRUITMENT BENCH ==="))
    with term.location(0, 3):
        rank = benchRecruit['rank']
        color = rankColors[rank]
        passiveText = ag.formatPassiveText(benchRecruit['surname'])
        print(f"Name:   {benchRecruit['name']}  {color(f'[{rank}]')}")
        print(f"Race:   {benchRecruit['race']} | Class: {benchRecruit['class']}")
        print(f"Stats:  STR:{benchRecruit['stats']['STR']} | INT:{benchRecruit['stats']['INT']} | DEX:{benchRecruit['stats']['DEX']} | FTH:{benchRecruit['stats']['FTH']}")
        print(f"LCK:    {benchRecruit['stats']['LCK']}")
        print(f"Passive: {term.italic(passiveText)}")
        print(f"Cost:   {term.bold_red(str(benchRecruit['hiringFee']))} gold to hire")
        print()
        maxH = ag.getRenownCfg(renown)["maxHeroes"]
        if guildBank >= benchRecruit['hiringFee'] and len(guildRoster) < maxH:
            print(term.bold_green("[A] Hire this Recruit"))
        else:
            reason = "roster full" if len(guildRoster) >= maxH else "insufficient gold"
            print(term.dimgray(f"[A] Hire this Recruit ({reason})"))
        reroll_text = f"[R] Re-roll Recruit ({rerollsLeft}/5 remaining)"
        print(term.bold_white(reroll_text) if rerollsLeft > 0 else term.dimgray(reroll_text))

def renderQuestTab(questSlots, selectedQuestIndex, taggedQuestSlot, partyQuest, partySize, partyMembers):
    with term.location(0, 2):
        print(term.bold_yellow("=== TRI-CONTRACT BULLETIN ==="))
    with term.location(0, 3):
        typeLabels = {"breadwinner": "★ Breadwinner", "benchmark": "◆ Benchmark", "highstakes": "▲ High Stakes"}
        typeColors = {"breadwinner": term.green, "benchmark": term.cyan, "highstakes": term.bold_red}

        for i, quest in enumerate(questSlots):
            prefix = term.bold_yellow("> ") if i == selectedQuestIndex else "  "
            typeLabel = typeLabels[quest['type']]
            typeColor = typeColors[quest['type']]
            rec = quest['recommended']

            tag = ""
            if taggedQuestSlot == i:
                tag = f"  {term.bold_white('[TAGGED]')}"
            elif quest['status'] == "contracted":
                tag = f"  {term.dimgray('[CONTRACTED]')}"

            print(f"{prefix}{typeColor(typeLabel)} ({rec}){tag}")
            print(f"   {quest['name']}")
            status_color = term.green if quest['status'] == "available" else term.dimgray
            print(f"   {quest['statNeeded']} (Difficulty: {quest['difficulty']})  |  Reward: {term.bold_yellow(str(quest['reward']))}g  |  {status_color(quest['status'].upper())}")
            print()

        # --- PARTY EXPEDITION SLOT ---
        mult = partySizeMult.get(partySize, {"diff": 1.3, "reward": 1.8})
        scaledDiff = int(partyQuest['difficulty'] * mult['diff'])
        scaledReward = int(partyQuest['reward'] * mult['reward'])
        print(term.bold_magenta("✦ PARTY EXPEDITION"))
        print(f"   {partyQuest['name']}  —  {partyQuest['statNeeded']}")
        print(f"   Difficulty: {term.bold_yellow(str(scaledDiff))} ({partySize}P)  |  Reward: {term.bold_yellow(str(scaledReward))}g  |  {term.cyan('2 days')}")
        print(f"   Size: {partySize}  [P]cycle 2/3/4  (2P: 1.3×  |  3P: 2.0×  |  4P: 2.8×)")
        if partyMembers:
            inParty = len(partyMembers)
            names = ", ".join(f"#{i+1}" for i in partyMembers)
            status = term.bold_green if inParty == partySize else term.yellow
            print(f"   {status(f'Party: {inParty}/{partySize} selected')} — head to Roster (tab 3) to toggle with [P]")
        else:
            print(f"   {term.dimgray('Press [P] to set size, then go to Roster (tab 3) to pick heroes.')}")
        print()

def renderRosterTab(guildRoster, selectedIndex, renown, partyMembers=None, partySize=2, facilities=None):
    with term.location(0, 2):
        print(term.bold_green(f"=== GUILD ROSTER ({len(guildRoster)}/{ag.getRenownCfg(renown)['maxHeroes']}) ==="))

    if not guildRoster:
        with term.location(0, 3):
            print(term.italic("No adventurers hired yet! Visit the Recruitment tab (press 1)."))
        return

    if partyMembers is None:
        partyMembers = []

    partyActive = len(partyMembers) > 0
    cols = 2 if len(guildRoster) > 5 and term.width >= 90 else 1
    perCol = (len(guildRoster) + cols - 1) // cols
    xOff = [0, 78]

    maxContentBottom = term.height - 6
    maxRows = max(1, (maxContentBottom - 3) // 6) if perCol > 0 else 1
    truncated = perCol > maxRows
    if truncated:
        perCol = maxRows

    for row in range(perCol):
        for col in range(cols):
            idx = col * perCol + row
            if idx >= len(guildRoster):
                continue
            hero = guildRoster[idx]
            x = xOff[col]
            y = 3 + row * 6
            prefix = term.bold_yellow("> ") if idx == selectedIndex else "  "
            status_color = term.green if hero['status'] == "Available" else term.bold_red
            rank_color = rankColors.get(hero['rank'], term.white)
            rank_tag = rank_color(f"[{hero['rank']}]")
            passiveText = ag.formatPassiveText(hero.get('surname', ''))
            stress = hero['stress']
            penalty = ag.getStressPenalty(stress)
            label = ag.getStressLabel(stress)
            sColor = stressColors[label]
            bar = ag.stressBar(stress)
            penStr = f" (-{penalty})" if penalty > 0 else ""
            inParty = idx in partyMembers
            partyTag = term.bold_cyan(" ★ Party") if inParty else ""
            partyHint = term.dimgray(" [P]") if partyActive and not inParty and hero['status'] == "Available" else ""

            with term.location(x, y):
                print(f"{prefix}{idx + 1}. {hero['name']} ({hero['class']}) {rank_tag} - {status_color(hero['status'])}{partyTag}{partyHint}")
            with term.location(x, y + 1):
                print(f"   STR:{hero['stats']['STR']} | INT:{hero['stats']['INT']} | DEX:{hero['stats']['DEX']} | FTH:{hero['stats']['FTH']} | LCK:{hero['stats']['LCK']}")
            with term.location(x, y + 2):
                print(f"   Passive: {term.italic(passiveText)}")
            with term.location(x, y + 3):
                injuryFlag = term.bold_red(f" | INJURED (-3 all stats, {hero['injuredDaysLeft']}d)") if hero.get('injuredDaysLeft', 0) > 0 else ""
                print(f"   Stress: {sColor(bar)} {stress}/100 ({label}{penStr}){injuryFlag}")
            with term.location(x, y + 4):
                trainingStr = ""
                if facilities and hero.get('idleDays', 0) > 0:
                    tgLevel = facilities.get("trainingGrounds", {}).get("level", 0)
                    if tgLevel > 0 and fc.isActive(facilities, "trainingGrounds"):
                        interval = fc.facilityConfig["trainingGrounds"]["levels"][tgLevel]["interval"]
                        trainingStr = f"  |  Training: {hero['idleDays']}/{interval}d"
                if hero['status'] == "Contract Expired":
                    print(f"   {term.bold_red('CONTRACT EXPIRED')} — {term.bold_cyan('[E]')} Extend {ag.extendCost(hero)}g | {term.bold_red('[T]')} Dismiss (free){trainingStr}")
                elif hero['contractDaysLeft'] <= 3:
                    print(f"   Contract: {term.bold_yellow(str(hero['contractDaysLeft']))}/{hero['contractDays']} days left{trainingStr}")
                else:
                    print(f"   Contract: {hero['contractDaysLeft']}/{hero['contractDays']} days left{trainingStr}")

    if truncated:
        with term.location(0, maxContentBottom - 1):
            print(term.dimgray(f"... ({len(guildRoster)} heroes total — enlarge terminal or scroll to see all)"))

def renderAccountantTab(guildBank, renown, month, daysLeft, taxQuota, guildRoster):
    with term.location(0, 2):
        print(term.bold_magenta("=== GUILD ACCOUNTANT ==="))
    with term.location(0, 3):
        cfg = ag.getRenownCfg(renown)
        totalUpkeep = ag.getTotalUpkeep(guildRoster)
        projectedTax = taxQuota - guildBank
        neededPerDay = max(0, projectedTax // daysLeft) if daysLeft > 0 else 0

        print(f"Guild Renown:     {renown} ({cfg['title']})")
        print(f"Month:            {month}")
        print(f"Vault Balance:    {term.bold_yellow(str(guildBank))} gold")
        print(f"Daily Upkeep:     {totalUpkeep}g (per rank: E=5 D=8 C=12 B=18 A=28 S=45)")
        print(f"Days Remaining:   {daysLeft}")
        print(f"Tax Quota:        {taxQuota}g")
        print(f"Hero Slots:       {len(guildRoster)}/{cfg['maxHeroes']}")
        print(f"Available Ranks:  {'/'.join(cfg['ranks'])}")
        print(f"Quest Mult:       {cfg['questMult']}x")
        print(f"Gold to Quota:    {projectedTax}g remaining")
        print(f"Needed / Day:     ~{neededPerDay}g to meet quota")
        print()
        if guildBank >= taxQuota:
            print(term.bold_green("The guild is on track to meet the tax quota!"))
        elif neededPerDay <= 30:
            print(term.yellow("Manageable — keep sending heroes on quests."))
        else:
            print(term.bold_red("Tight margins! Consider hiring stronger heroes."))

def renderArmoryTab(guildArmory, armoryCategoryIndex, guildRoster, selectedIndex, guildBank, renown, selectedGearIndex=0):
    catLabels = ["weapon", "armor", "talisman", "relic"]
    displayLabels = ["Weapons", "Armor", "Talismans", "Relics"]
    cat = catLabels[armoryCategoryIndex]
    catLabel = displayLabels[armoryCategoryIndex]
    maxSlots = ar.getMaxSlots(renown)[cat]
    slotsUsed = len(guildArmory[cat])

    with term.location(0, 2):
        print(term.bold_yellow(f"=== GUILD ARMORY — {catLabel} ==="))
    with term.location(0, 3):
        fullSlots = f"{slotsUsed}/{maxSlots}"
        print(f"Slots: {term.bold_white(fullSlots)}  |  Guild Gold: {term.bold_yellow(str(guildBank))}g")

        catDisplay = []
        for i in range(4):
            label = displayLabels[i]
            if i == armoryCategoryIndex:
                catDisplay.append(f"{term.bold_white(f'<< {label} >>')}")
            else:
                catDisplay.append(f"{term.dimgray(label)}")
        print("  ".join(catDisplay))

        print()
        if cat == "relic":
            if slotsUsed == 0:
                print(term.italic("No relics owned. Defeat the Raid Boss (Tab 7) to earn one."))
            else:
                for idx, gear in enumerate(guildArmory[cat]):
                    prefix = term.bold_yellow("> ") if idx == selectedGearIndex else "  "
                    bonusText = ar.formatGearBonus(gear)
                    print(f"{prefix}{gear['name']}  [{bonusText}]  {term.bold_magenta('Raid Reward')}")
        else:
            if slotsUsed == 0:
                print(term.italic("No gear in this category. Press [B] to buy."))
            else:
                for idx, gear in enumerate(guildArmory[cat]):
                    prefix = term.bold_yellow("> ") if idx == selectedGearIndex else "  "
                    bonusText = ar.formatGearBonus(gear)
                    print(f"{prefix}{gear['name']}  [{bonusText}]  {term.bold_red(str(gear['guildCost']))}g")
        print()
        if cat != "relic" and slotsUsed < maxSlots:
            tiers = ar.getAvailableTiers(renown)
            sampleTier = tiers[-1]
            sampleGuildCost = ar.tierConfig[sampleTier]["guildCost"]
            print(f"[B] Buy a random item ({sampleGuildCost}g–{ar.tierConfig['mythril']['guildCost']}g)")

    if guildRoster:
        with term.location(0, 3 + 4 + slotsUsed + 4):
            print(term.bold_cyan("── SELECTED HERO ──"))
        with term.location(0, 3 + 4 + slotsUsed + 5):
            hero = guildRoster[selectedIndex]
            rank_color = rankColors.get(hero['rank'], term.white)
            rank_tag = rank_color(f"[{hero['rank']}]")
            print(f"{hero['name']} ({hero['class']}) {rank_tag} — Personal gold: {term.bold_yellow(str(hero['gold']))}g")

            for slot in catLabels:
                gear = hero['equipment'].get(slot)
                slotLabel = slot.capitalize()
                if gear:
                    bonusText = ar.formatGearBonus(gear)
                    if slot == "relic":
                        print(f"  {slotLabel}: [{gear['name']}  {bonusText}]  [U]nassign")
                    else:
                        print(f"  {slotLabel}: [{gear['name']}  {bonusText}]  [U]nassign | [P]urchase {gear['heroCost']}g")
                else:
                    action = ""
                    if slot == cat:
                        action = "  [A]ssign from armory"
                    elif slot == "relic" and cat == "relic":
                        action = "  [A]ssign from armory"
                    print(f"  {slotLabel}: [Empty]{action}")

def renderFacilitiesTab(facilities, guildBank, renown, selectedFacilityIndex=0):
    name = fc.FACILITY_NAMES[selectedFacilityIndex]
    cfg = fc.facilityConfig[name]
    displayName = cfg["name"]
    info = fc.getLevelInfo(facilities, name)
    nl = fc.nextLevel(facilities, name)
    active = fc.isActive(facilities, name)
    upkeep = info["dailyUpkeep"] if active else 0

    with term.location(0, 2):
        print(term.bold_cyan("=== GUILD FACILITIES ==="))
    with term.location(0, 3):
        switcher = []
        for i, fname in enumerate(fc.FACILITY_NAMES):
            label = fc.facilityConfig[fname]["name"]
            if i == selectedFacilityIndex:
                switcher.append(f"{term.bold_white(f'<< {label} >>')}")
            else:
                switcher.append(f"{term.dimgray(label)}")
        print("  ".join(switcher))

        badge = term.bold_green(" [ACTIVE]") if active else term.dimgray(" [INACTIVE]")
        nameFmt = term.bold_white if active else term.dimgray
        print(f"{nameFmt(displayName)}  —  Level {info['level']}{badge}")
        print(f"Effect:       {term.bold_white(info['desc']) if active else term.dimgray(info['desc'])}")
        if info["level"] > 0 and active:
            print(f"Daily Upkeep: {term.bold_yellow(f'{upkeep}g')}")
        elif info["level"] > 0 and not active:
            print(f"Daily Upkeep: {term.bold_green('0g (inactive)')}")
        print()
        if nl is not None:
            renownStr = f" (need {term.bold_yellow(str(nl['renownReq']))} renown)" if nl["renownReq"] > 0 else ""
            canAfford = guildBank >= nl["cost"]
            affordStr = term.bold_green(str(nl["cost"])) if canAfford else term.bold_red(str(nl["cost"]))
            print(f"Next Level:   Level {nl['level']} — {affordStr}g{renownStr}")
            print(f"              {nl['desc']}")
            if fc.canUpgrade(facilities, name, renown, guildBank):
                print()
                print(term.bold_green("[U] Upgrade Facility"))
            elif guildBank < nl["cost"]:
                print()
                print(term.dimgray("[U] Upgrade Facility (insufficient gold)"))
            elif renown < nl["renownReq"]:
                print()
                print(term.dimgray(f"[U] Upgrade Facility (need renown {nl['renownReq']})"))
        else:
            print(term.bold_yellow("MAX LEVEL — All upgrades complete!"))
        if info["level"] > 0:
            print()
            print(term.dimgray("[T] Toggle Active/Inactive"))

def showEventPopup(event):
    choiceLines = []
    for c in event["choices"]:
        keyLabel = c["key"].upper()
        choiceLines.append(f"  {term.bold_white(f'[{keyLabel}]')} {c['label']}")
    wrappedFlavor = textwrap.wrap(event["flavor"], width=72)
    lines = [term.bold_yellow(" ═══ RANDOM EVENT ═══ "), ""]
    lines.extend(wrappedFlavor)
    lines.append("")
    lines.extend(choiceLines)
    lines.extend(["", term.bold_white("Make your choice..."), ""])
    drawPopup(lines)
    while True:
        key = term.inkey().lower()
        for c in event["choices"]:
            if key == c["key"]:
                return c
        if key == '\x1b':
            return event["choices"][1]

def _visLen(s):
    return len(re.sub(r'\x1b\[[0-9;]*m', '', s))

def drawPopup(lines):
    width = 80
    inner = width - 4
    height = len(lines) + 2
    startX = max(0, (term.width - width) // 2)
    startY = max(0, (term.height - height) // 2)
    with term.location(startX, startY):
        print("┌" + "─" * (width - 2) + "┐")
    for i, line in enumerate(lines):
        with term.location(startX, startY + 1 + i):
            vlen = _visLen(line)
            if vlen < inner:
                left = (inner - vlen) // 2
                right = inner - vlen - left
                print("│ " + " " * left + line + " " * right + " │")
            else:
                print("│ " + line + " │")
    with term.location(startX, startY + height - 1):
        print("└" + "─" * (width - 2) + "┘")
    sys.stdout.flush()

def confirmAdvance():
    drawPopup([
        "",
        "   ═══ ADVANCE TO NEXT DAY ═══   ",
        "",
        "     [Y] Yes     [N] Cancel      ",
        "",
    ])
    while True:
        key = term.inkey()
        if key.lower() == 'y':
            return True
        elif key.lower() == 'n':
            return False

def showDayResults(summaryLines):
    display = ["   ═══ DAY SUMMARY ═══   ", ""]
    for line in summaryLines:
        if len(line) > 72:
            display.extend(textwrap.wrap(line, width=72))
        else:
            display.append(line)
    display.extend(["", "   Press any key to continue...   "])
    drawPopup(display)
    term.inkey()

def showMonthlyRecap(d):
    lines = [f"   ★ MONTH {d['month']} COMPLETE! ★   ", ""]
    if d["metQuota"]:
        newCfg = ag.getRenownCfg(d["newRenown"])
        lines.append(f"  Tax quota {d['taxQuota']}g:  {term.bold_green('MET')}")
        lines.append(f"  Renown ▲ {term.bold_yellow(str(d['newRenown']))}  —  {newCfg['title']}")
        lines.append(f"  Next quota: {term.bold_yellow(str(newCfg['tax']))}g")
    else:
        newCfg = ag.getRenownCfg(d["newRenown"])
        penalty = d["taxQuota"] // 2
        lines.append(f"  Tax quota {d['taxQuota']}g:  {term.bold_red('FAILED')}")
        lines.append(f"  Renown ▼ {term.bold_yellow(str(d['newRenown']))}  —  {newCfg['title']}")
        lines.append(f"  Penalty:  {term.bold_red(f'-{penalty}g')} withdrawn")
    lines.append("")
    lines.append(f"  Days passed:       {d['daysPassed']}")
    lines.append(f"  Quests succeeded:  {d['questsSucceeded']}")
    lines.append(f"  Quests failed:     {d['questsFailed']}")
    qi = d["questIncome"]
    lines.append(f"  Quest income:      {term.bold_green(f'+{qi}g') if qi >= 0 else term.bold_red(f'{qi}g')}")
    lines.append(f"  Hero upkeep:       {term.bold_red(f'-{d["heroUpkeep"]}g')}")
    if d["facilityUpkeep"]:
        lines.append(f"  Facility upkeep:   {term.bold_red(f'-{d["facilityUpkeep"]}g')}")
    if d["facilitySoaks"]:
        lines.append(f"  Facility soaks:    {d['facilitySoaks']}")
    if d.get("trainingGains"):
        lines.append(f"  Stat gains:        {d['trainingGains']}")
    lines.append(f"  Hero gear bought:  {d['heroGearPurchases']}")
    lines.append(f"  Events triggered:  {d['eventsTriggered']}")
    ei = d["eventGoldImpact"]
    if ei:
        lines.append(f"  Event gold impact: {term.bold_green(f'+{ei}g') if ei >= 0 else term.bold_red(f'{ei}g')}")
    lines.append(f"  Treasury:          {term.bold_yellow(f'{d["guildBank"]}g')}")
    lines.append("")
    lines.append(f"  {term.bold_white('Press any key to continue...')}")
    drawPopup(lines)
    term.inkey()

def renderRaidTab(raidBoss, raidStatus, guildRoster, raidResult):
    with term.location(0, 2):
        print(term.bold_red("=== RAID EXPEDITION ==="))
    if raidBoss is None:
        with term.location(0, 3):
            print(term.italic("Reach Renown 5 to challenge the raid boss."))
        return
    with term.location(0, 3):
        print(f"Boss:        {term.bold_white(raidBoss['name'])}")
        print(f"Stat Focus:  {raidBoss['statNeeded']}")
        print(f"Waves:       {raidBoss['numWaves']}  |  Boss Phases: {raidBoss['numPhases']}")
        print()
        if raidStatus == "inactive":
            ready = sum(1 for h in guildRoster if h["status"] == "Available")
            total = len(guildRoster)
            if total == 7 and ready == 7:
                print(term.bold_green(f"Party Ready: {ready}/{total} heroes"))
                print()
                print(term.bold_green("[R] Initiate Raid — 1 day prep"))
            else:
                print(term.yellow(f"Party Ready: {ready}/{total} heroes  (need 7/7 available)"))
                reasons = []
                if total < 7:
                    reasons.append(f"need {7 - total} more heroes")
                elif ready < 7:
                    busy = total - ready
                    reasons.append(f"{busy} hero(es) unavailable (on mission / expired)")
                print(term.dimgray(f"  {'; '.join(reasons)}"))
        elif raidStatus == "prepping":
            print(f"Status:      {term.bold_yellow('PREPPING — 1 DAY REMAINING')}")
            print(f"Heroes Locked: {term.bold_white('7/7')}")
            print(term.dimgray("  Contracts paused during preparation"))
            print()
            print(term.dimgray("[C] Cancel Prep"))
        elif raidStatus == "done":
            if raidResult and raidResult["success"]:
                print(f"Outcome:     {term.bold_green('VICTORY')}")
                print(f"Gold Earned: {term.bold_yellow(f'+{raidResult["goldReward"]}g')}")
                if raidResult.get("relic"):
                    print(f"Relic:       {term.bold_magenta(raidResult['relic'])}")
            elif raidResult and not raidResult["success"]:
                print(f"Outcome:     {term.bold_red('DEFEAT')}")
                print(f"Gold Lost:   {term.bold_red(f'-{raidResult["failureCost"]}g')}")
                if raidResult.get("injuredHeroes"):
                    print(f"Injured:     {term.bold_red(', '.join(raidResult['injuredHeroes']))}")
            print()
            print(term.dimgray("[V] View Raid Log  |  [R] New Raid (generates new boss)"))

def showRaidResultPopup(result):
    lines = []
    if result["success"]:
        lines.append(f"     ★ RAID VICTORY — {result['relic']} ACQUIRED! ★     ")
    else:
        lines.append("        ✖ RAID DEFEATED — CASUALTIES REPORTED ✖        ")
    lines.append("")
    for entry in result["log"]:
        t = entry["type"]
        text = entry.get("text", "")
        if t in ("enter", "victory", "defeat"):
            wrapped = textwrap.wrap(text, width=72)
            lines.extend(wrapped)
            lines.append("")
        elif t == "phase_intro":
            lines.append(term.bold_yellow(f"  ⚔ {text}"))
            lines.append("")
        elif t == "wave":
            label = "WAVE CLEARED" if entry["won"] else "WAVE SURVIVED"
            color = term.bold_green if entry["won"] else term.bold_yellow
            wrapped = textwrap.wrap(text, width=68)
            lines.append(f"  {color(f'[{label}]')}")
            lines.extend(f"    {w}" for w in wrapped)
            lines.append("")
        elif t == "round":
            hpBar = _hpBar(entry["partyHP"], entry["maxPartyHP"])
            bossBar = _hpBar(entry["bossHP"], entry["maxBossHP"])
            lines.append(f"  Round {entry['round']}:  Party {hpBar}  |  Boss {bossBar}")
    if result["success"]:
        lines.append(f"  {term.bold_yellow(f'Reward: {result["goldReward"]}g + {result["relic"]}')}")
    else:
        if result.get("injuredHeroes"):
            lines.append(f"  {term.bold_red(f'Injured: {", ".join(result["injuredHeroes"])}')}")
        lines.append(f"  {term.bold_red(f'Gold lost: {result["failureCost"]}g')}")
    lines.append("")
    lines.append("  Press any key to continue...")
    drawPopup(lines)
    term.inkey()

def _hpBar(current, maximum):
    if maximum == 0:
        return " " * 11
    ratio = current / maximum
    filled = max(0, min(10, int(ratio * 10)))
    bar = "█" * filled + "░" * (10 - filled)
    return f"{bar} {current:>4}/{maximum}"
