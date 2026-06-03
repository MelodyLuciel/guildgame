import json
import os
import sys
from blessed import Terminal
from modules import tabs

term = Terminal()

SAVE_DIR = os.path.join(os.path.expanduser("~"), ".guildgame")
NUM_SLOTS = 3


def _savePath(slot):
    return os.path.join(SAVE_DIR, f"slot{slot}.json")


def saveGame(state, slot):
    os.makedirs(SAVE_DIR, exist_ok=True)
    data = {"version": 1}
    for k, v in state.items():
        if isinstance(v, set):
            data[k] = list(v)
        else:
            data[k] = v
    with open(_savePath(slot), "w") as f:
        json.dump(data, f, indent=2)


def loadGame(slot):
    path = _savePath(slot)
    if not os.path.exists(path):
        return None
    with open(path) as f:
        data = json.load(f)
    for k, v in data.items():
        if k == "version":
            continue
        if isinstance(v, list) and k in (
            "partyMembers", "eventsFiredThisMonth", "resolvedPartyQuests",
        ):
            data[k] = set(v)
        elif k == "eventsFiredThisMonth":
            data[k] = set(v)
    return data


def getSlotPreview(slot):
    path = _savePath(slot)
    if not os.path.exists(path):
        return "(empty)"
    try:
        with open(path) as f:
            data = json.load(f)
        day = data.get("currentDay", 0)
        month = data.get("month", 0)
        renown = data.get("renown", 0)
        return f"Month {month}, Day {day}, Renown {renown}"
    except Exception:
        return "(corrupted)"


def _pickSlot(title):
    while True:
        previews = [getSlotPreview(i + 1) for i in range(NUM_SLOTS)]
        lines = [
            f"          ═══ {title} ═══          ",
            "",
        ]
        for i, preview in enumerate(previews):
            lines.append(f"  [{i + 1}]  Slot {i + 1}: {preview}")
        lines.extend([
            "",
            "  [Esc]  Back                    ",
            "",
        ])
        tabs.drawPopup(lines)
        key = term.inkey().lower()
        if key in ('1', '2', '3'):
            return int(key)
        if key == '\x1b':
            return None


def showMainMenu(gs):
    while True:
        lines = [
            "          ═══ MENU ═══          ",
            "",
            "  [S]  Save Game                ",
            "  [L]  Load Game                ",
            "  [X]  Quit Game                ",
            "  [Esc]  Close                  ",
            "",
        ]
        tabs.drawPopup(lines)
        key = term.inkey().lower()

        if key == 's':
            slot = _pickSlot("SAVE GAME")
            if slot is not None:
                try:
                    saveGame(gs, slot)
                    tabs.drawPopup(["", "  Game saved!  ", "", "  Press any key...  "])
                    term.inkey()
                except (OSError, json.JSONEncodeError) as e:
                    tabs.drawPopup(["", f"  Save failed: {e}  ", "", "  Press any key...  "])
                    term.inkey()

        elif key == 'l':
            slot = _pickSlot("LOAD GAME")
            if slot is not None:
                try:
                    data = loadGame(slot)
                    if data is None:
                        tabs.drawPopup(["", "  No save in this slot.  ", "", "  Press any key...  "])
                        term.inkey()
                        continue
                    gs.clear()
                    gs.update(data)
                    gs["actionMessage"] = "Game loaded."
                    return "load"
                except (OSError, json.JSONDecodeError) as e:
                    tabs.drawPopup(["", f"  Load failed: {e}  ", "", "  Press any key...  "])
                    term.inkey()

        elif key == 'x':
            lines = [
                "",
                "   Really quit?   ",
                "   Unsaved progress will be lost.   ",
                "",
                "     [Y] Yes     [N] Cancel      ",
                "",
            ]
            tabs.drawPopup(lines)
            confirm = term.inkey().lower()
            if confirm == 'y':
                return "quit"

        elif key == '\x1b':
            return "continue"
