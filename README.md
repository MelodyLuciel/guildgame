# GuildGame

A terminal-based guild management RPG built with Python and the `blessed` library. Recruit adventurers, send them on quests, manage contracts and stress, and grow your guild's renown to survive the crown's ever-increasing tax quotas.

## Running the Game

```bash
pip install blessed
python game.py
```

---

## Features

### Tabbed Interface
Press `1`–`7` to switch between seven panels:

| Key |     Tab      |                    Description                          |
|-----|--------------|---------------------------------------------------------|
| `1` | Recruitment  | Browse and hire the daily recruit                       |
| `2` | Quest Board  | Browse 3 contract tiers and tag one for assignment      |
| `3` | Guild Roster | View heroes, send them on quests, manage contracts      |
| `4` | Accountant   | Financial overview, renown status, quota projections    |
| `5` | Armory       | Buy gear, assign/unassign to heroes, hero purchases     |
| `6` | Facilities   | Build and upgrade guild facilities (Hot Springs, etc.)  |
| `7` | Raid         | Initiate endgame raid expedition (Renown 5)             |

### Adventurer Ranks (E → S)
Six rank tiers with weighted rarity. Higher ranks have better stats but cost more to hire and terminate.

| Rank | Stat Total | Hire Cost Mult | Weight | Contract Length |
|------|------------|----------------|--------|-----------------|
| E    | 30–39      | 0.4×           | 30%    | 12–14 days      |
| D    | 40–49      | 0.7×           | 25%    | 10–12 days      |
| C    | 50–59      | 1.0×           | 20%    | 9–11 days       |
| B    | 60–69      | 1.8×           | 15%    | 8–10 days       |
| A    | 70–79      | 3.5×           | 7%     | 6–8 days        |
| S    | 80–90      | 6.0×           | 3%     | 5–7 days        |

Available ranks are gated by guild renown — you won't see A/S ranks at low renown.

### Surname Passive System
Each of the 30 last names grants a unique stat bonus (+1 or +2 to specific stats), displayed on both the Recruit and Roster tabs. The same rank doesn't mean the same hero — a "fury" hero hits harder, a "weaver" hero leans magical.

### Tri-Contract Bulletin (Quest Board)
Three quest slots, browsed with `↑`/`↓`:

| Slot |      Type     |    Difficulty   | Reward | Recommended Rank |
|------|---------------|-----------------|--------|------------------|
| 1    |★ Breadwinner | Low (5–10)      | Low     |      E–D         |
| 2    |◆ Benchmark   | Medium (10–15)  | Medium |      C–B         |
| 3    |▲ High Stakes  | High (14–18)    | High   |      A–S         |

**Assignment flow:**
1. Quest Board — press `Q` to tag a quest
2. Roster — select a hero, press `Q` to assign them
3. Breadwinner quests regenerate instantly; Benchmark/High Stakes free up when the hero returns

### Contract System
Hired adventurers serve fixed-term contracts. When a contract expires you can:
- `E` — Extend (pay 30% of hiring fee to re-sign for full duration)
- `T` — Dismiss for free (expired contracts only)

Active contracts can be:
- `T` — Terminated early (pay 75% of hiring fee as compensation)

Contracts tick down each day. Heroes on missions don't tick down until they return.

### Renown & Progression
Every 30 days the crown collects taxes. Meeting the quota increases renown; failing costs 1 renown + 50% of the quota as a gold penalty.

| Renown |        Title         | Tax Quota | Available Ranks | Max Heroes | Quest Mult |
|--------|----------------------|-----------|-----------------|------------|------------|
| 0      | Fresh Charter        |    600g   | E, D, C         | 5          | 1.0×       |
| 1      | Established Guild    |    800g   | E, D, C, B      | 5          | 1.2×       |
| 2      | Notable Company      |   1100g   | D, C, B, A      | 6          | 1.5×       |
| 3      | Renowned Order       |   1500g   | C, B, A         | 6          | 1.8×       |
| 4      | Legendary Fellowship |   2000g   | B, A, S         | 7          | 2.2×       |
| 5      | Mythic Circle        |   2500g   | A, S            | 7          | 2.5×       |

### Stress System
Heroes accumulate stress from quests:
- **Success:** +20 stress
- **Failure:** +30 stress
- **Rest day (idle):** -15 stress recovery

| Stress |   Label   | Stat Penalty |
|--------|-----------|--------------|
| 0–29   | Rested    | None         |
| 30–49  | Strained  | -1           |
| 50–69  | Fatigued  | -2           |
| 70–89  | Exhausted | -3           |
| 90–100 | Broken    | -4           |

Stress penalties reduce effective stats for quest checks, including luck. Stress is displayed as a visual bar in the roster tab.

### Recruitment
- `R` — Re-roll the daily recruit (5 per day, resets each day)
- Available ranks are filtered by current renown level
- `A` — Hire the shown recruit (if roster isn't full)

### Confirmation & Results Popups
- Space prompts a confirmation popup before each day advance
- After advancing, a results popup shows mission outcomes, upkeep costs, and gold changes
- All popups are 80 characters wide with text wrapping — long descriptions never overflow
- Month-end shows a detailed recap screen with income, expenses, quest success rate, and renown changes

### Guild Armory (Tab 5)
A gear system with four categories — Weapons, Armor, Talismans, and Relics — each granting stat bonuses to heroes.

**Gear Tiers (gated by renown):**
- **Iron** (+2) — renown 0–1, 150g guild cost
- **Steel** (+4) — renown 2–3, 450g guild cost
- **Mythril** (+6) — renown 4–5, 1200g guild cost
- **Relic** (+2 ALL stats) — raid reward only, cannot be bought

**Armory slots** scale per category (2/3/4 at renown 0–1/2–3/4–5). Relics are limited to 1 slot. Buy gear with guild gold, then assign it to heroes. Gear bonuses stack onto the relevant quest stat during resolution.

**Actions:**
- `←`/`→` — Switch gear category (4 categories)
- `[`/`]` — Select gear item
- `A` — Assign selected gear to selected hero (guild stock → hero equipment)
- `U` — Unassign gear from hero (hero equipment → guild stock; blocked on hero-owned gear)
- `P` — Hero purchases equipped gear with personal gold (gear stays equipped, marked hero-owned; relics cannot be purchased)

**Hero-owned gear:** Selling gear to a hero gives the guild instant gold, but the gear is permanently bound to that hero. If they later leave the guild via dismissal or termination, any hero-owned gear leaves with them — it's gone from the armory for good. This creates a strategic trade-off: quick gold now vs. long-term equipment flexibility.

### Random Periodic Events
Each day after advancing, there's a ~25–35% chance (scaling with renown) that a random event triggers. Each event presents an interactive choice with lasting consequences.

| Category      | Events                                                                 |
|---------------|------------------------------------------------------------------------|
| **Civic**     | City Festival, Royal Tax Edict, Wandering Minstrel                     |
| **Wild**      | Monster Raid, Rare Herb Discovery                                      |
| **Guild**     | Rival Guild Sabotage, Wandering Adventurer                             |
| **Character** | Hero's Past                                                             |

Events can modify gold, renown, stress, the tax deadline, armory stock, or even grant free heroes. Some events are gated by minimum renown.

### Guild Facilities (Tab 6)
Upgradable buildings that provide passive bonuses each day. Currently one facility:

#### Hot Springs
Passively reduces stress for the most stressed idle heroes each day. Automatically targets the highest-stress heroes — no manual tagging needed.

| Level | Cost  | Upkeep/Day | Renown Required | Effect                         |
|-------|-------|------------|-----------------|--------------------------------|
| 0     | —     | —          | —               | Locked                         |
| 1     | 300g  | 5g         | 0               | -5 stress/turn to 1 hero       |
| 2     | 600g  | 10g        | 2               | -10 stress/turn to 1 hero      |
| 3     | 1000g | 15g        | 4               | -10 stress/turn to 2 heroes    |

#### Training Grounds
Passively grants stat progression for idle heroes. Heroes accumulate training days each day they're not on a mission. When idle days reach the interval threshold, they gain +1 to a random stat (STR/INT/DEX/FTH/LCK) — stats can exceed the normal 18 cap.

| Level | Cost  | Upkeep/Day | Renown Required | Effect                         |
|-------|-------|------------|-----------------|--------------------------------|
| 0     | —     | —          | —               | Locked                         |
| 1     | 400g  | 8g         | 1               | +1 random stat per 5 idle days |
| 2     | 700g  | 15g        | 3               | +1 random stat per 3 idle days |
| 3     | 1200g | 25g        | 5               | +1 random stat per 2 idle days |

Upgrade with `[U]` on the Facilities tab. Toggle active/inactive with `[T]` — inactive facilities cost no upkeep but provide no benefit. Use `←`/`→` to switch between facilities. Soak applies before the natural -15 daily stress recovery, so effects stack.

### Economy
- Gold can go negative — no safety floor
- Heroes earn a personal 40% cut (heroCut) of quest rewards, stored in their personal gold
- **Rank-based daily upkeep** (E=5g, D=8g, C=12g, B=18g, A=28g, S=45g) — higher-ranked heroes cost significantly more to maintain
- Tax quota scales with renown each month
- **Quest difficulty scales with renown** (+3 per renown level) — at higher renown, even S-rank heroes face real failure risk
- **Tiered failure costs** (E=50g, D=100g, C=150g, B=250g, A=400g, S=600g) — losing an S-rank hero on a mission is expensive

---

### Raid Expedition (Tab 7)
An endgame capstone available at Renown 5 (Mythic Circle). Requires a full roster of 7 heroes to initiate.

**Flow:**
1. **Prep** — Press `[R]` on the Raid tab. All heroes are locked into "Preparing for Raid" status for 1 day. Contracts pause. Cancel with `[C]`.
2. **Resolve** — Advancing the day after prep triggers auto-resolution. The simulation runs through dungeon waves (1-3) followed by boss phases (2-3) with round-by-round tug-of-war combat.
3. **Victory** — Massive gold reward + a unique Relic (+2 ALL stats, equippable via Armory tab).
4. **Defeat** — Heavy gold penalty + 30% injury chance per hero.

**Boss Themes:** Crimson Colossus (STR), Void Lich (FTH), Storm Tyrant (DEX) — randomly selected each raid. Stats, synergy, gear, stress, and injuries all factor into the combined stat check.

---

### Save & Load

Press `` ` `` (backtick) at any time to open the menu with three options:

- **`[S]` Save Game** — Saves your current progress to one of 3 slots. Save files are stored in `~/.guildgame/`.
- **`[L]` Load Game** — Loads from a selected slot. Slot previews show the month, day, and renown so you can pick the right one.
- **`[X]` Quit Game** — Confirmation dialog before exiting. Unsaved progress is lost.

All save slots are independent — you can maintain multiple parallel campaigns.

---

## Controls Reference

|   Key   |   Context   |                      Action                      |
|---------|-------------|--------------------------------------------------|
| `1`–`7` | Global      | Switch tabs                                      |
| `` ` `` | Global      | Open menu (Save / Load / Quit)                   |
| `Space` | Global      | Advance one day (with confirmation)              |
| `X`     | Global      | Quit game                                        |
| `A`     | Recruitment | Hire the displayed recruit                       |
| `R`     | Recruitment | Re-roll recruit (5/day)                          |
| `↑`/`↓` | Quest Board | Browse quest slots                               |
| `Q`     | Quest Board | Tag/untag quest for assignment                   |
| `↑`/`↓` | Roster      | Select hero                                      |
| `Q`     | Roster      | Assign tagged quest to selected hero             |
| `E`     | Roster      | Extend expired contract                          |
| `T`     | Roster      | Terminate active contract / Dismiss expired hero |
| `←`/`→` | Armory      | Switch gear category                             |
| `[`/`]` | Armory      | Select gear item                                 |
| `A`     | Armory      | Assign selected gear to hero                     |
| `U`     | Armory      | Unassign gear from hero                          |
| `P`     | Armory      | Hero purchases equipped gear (personal gold)     |
| `B`     | Armory      | Buy random gear for current category             |
| `↑`/`↓` | Armory      | Select hero                                      |
| `←`/`→` | Facilities  | Switch between facilities                         |
| `U`     | Facilities  | Upgrade selected facility                        |
| `T`     | Facilities  | Toggle selected facility active/inactive (no upkeep when off) |
| `R`     | Raid        | Initiate raid prep / Generate new boss           |
| `C`     | Raid        | Cancel raid prep                                 |
| `V`     | Raid        | View raid combat log                             |

---

## Bug Fixes

### Gear lost when dismissing a hero
Equipment assigned to a hero from the armory was permanently lost when that hero was dismissed or terminated. Fixed — gear is now automatically returned to the armory when a hero leaves the guild. Gear that was purchased by the hero (via personal gold) is kept by the hero and not returned.

### Popup text overflow and box alignment
Event descriptions and day summary text could extend horizontally beyond the popup box borders, making them unreadable on narrower screens. Fixed — all popup text is now wrapped at 72 characters. Additionally, formatted text (colored/bold) was causing the popup right border to misalign due to invisible escape codes; box centering now correctly measures visible character width.

### Gear selection always picked the first item
When assigning gear from the armory, the `A` key always equipped the first item purchased instead of the one highlighted with `[`/`]`. Fixed — assign now uses the actively selected gear index.

### Status bar didn't reflect tax edict day reduction
The Royal Tax Edict event could subtract 3 days from the month via `daysLeft`, but the status bar hardcoded `/30` rather than reading the actual `daysLeft` value. Fixed — `renderStatusBar` now receives and displays the real remaining days.

### Terminal size clipping
The UI assumed a minimum terminal size of 158×35 rows, causing tabs, status bar, and controls to clip out of view on smaller laptop screens. Fixed — the layout now compacts the header and footer (removing 3 rows of wasted gaps), adapts controls to terminal width (auto-split into multiple rows when too long), and truncates the roster tab when space is limited. Minimum supported size is 60×25. A startup warning prompts the user to enlarge their terminal if below the minimum.

---

Built with [blessed](https://pypi.org/project/blessed/)  •  Python 3
