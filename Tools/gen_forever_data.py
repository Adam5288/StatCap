# -*- coding: utf-8 -*-
"""Write StatCapData_Forever.lua: which talent tree every Forever talent sits in, in the tree
order Era's tabSpec uses, plus Forever's own level-60 stat lists for the trees whose launch
guides agree on one (SPECS below). Run it without arguments; it has no options.

The talents come from one JSON file, talentTree = { CLASS: { talent name: tree 1-3 } } with
_tree_order naming each class's trees. Since 8 Nov 2026 that is Forever's talents after the
2-4 Nov 2026 rework: Wowhead's Forever talent data file, identical in name and tree to Icy
Veins' calculator files (3 Nov) for eight classes; for Shaman Icy Veins' file predates the
4 Nov changes and Wowhead's is used. The 21 Sep 2026 harvest it replaced (Icy Veins'
calculator, one file per class) stays next to it. StatCap reads the points spent per tree off
the game's own tree headings first; this list decides only on a client that offers none.

The stat lists come from the guide harvest of 5 Nov 2026 (CoachProbe/forever_guides/2026-11-05,
one JSON per class + SUMMARY.md). A tree gets a list here only when two or more independent
level-60 lists agree on its order; every other tree keeps Era's list as a stand-in, which the
addon labels as such. Importing this file writes nothing: the tests read SPECS from it."""
import io
import json
import os

SRC = "C:/Users/Adamr/CoachProbe/forever_talents"
MAP = os.path.join(SRC, "talent_tree-2026-11-08.json")
# Next to this folder's parent, wherever the repo lives.
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "StatCapData_Forever.lua")

CLASSES = ["WARRIOR", "PALADIN", "HUNTER", "ROGUE", "PRIEST", "SHAMAN", "MAGE", "WARLOCK", "DRUID"]
# The first word of each tree's name, in Era's tabSpec order (StatCapData_Era.lua): the file's
# tree numbers must mean the same trees.
ERA = {
    "WARRIOR": ["Arms", "Fury", "Protection"],
    "PALADIN": ["Holy", "Protection", "Retribution"],
    "HUNTER": ["Beast", "Marksmanship", "Survival"],
    "ROGUE": ["Assassination", "Combat", "Subtlety"],
    "PRIEST": ["Discipline", "Holy", "Shadow"],
    "SHAMAN": ["Elemental", "Enhancement", "Restoration"],
    "MAGE": ["Arcane", "Fire", "Frost"],
    "WARLOCK": ["Affliction", "Demonology", "Destruction"],
    "DRUID": ["Balance", "Feral", "Restoration"],
}
# The trees by the exact names the addon looks a list up under (Era's specOrder): a list
# filed under any other name would never be found, and the tree would quietly keep the stand-in.
TREES = {
    "WARRIOR": ["Arms", "Fury", "Protection"],
    "PALADIN": ["Holy", "Protection", "Retribution"],
    "HUNTER": ["Beast Mastery", "Marksmanship", "Survival"],
    "ROGUE": ["Assassination", "Combat", "Subtlety"],
    "PRIEST": ["Discipline", "Holy", "Shadow"],
    "SHAMAN": ["Elemental", "Enhancement", "Restoration"],
    "MAGE": ["Arcane", "Fire", "Frost"],
    "WARLOCK": ["Affliction", "Demonology", "Destruction"],
    "DRUID": ["Balance", "Feral (Cat)", "Feral (Bear)", "Restoration"],
}

# ---------------------------------------------------------------------------------------
# Forever's own level-60 stat lists.
#
# Rules: a row is a stat name the engine knows. SCORED are the names its item scorer counts
# on an item (priced in BUDGET in StatCap.lua and read off the item); SHOWN_ONLY are ranked by
# the guides but counted on no item yet - the row is there so the order is true, and the panel
# prints your own number next to it. Spell Piercing is Forever's name for spell penetration
# (its character sheet and item texts say so); the Classic name is priced but read off no item.
# No cap number goes in here (the bars read the caps from the game's own text), no talent
# name and no site name: the notes are read by players.
#
# How each order was put together (per-source orders: forever_guides/2026-11-05/<class>.json):
# only level-60 ranked lists count; a stat is a row when at least two of them rank it; the
# order is the one most of them agree on, and where they split the note says so. Weapon
# damage is no row (the engine counts it for melee and hunters by itself). A stat one list
# alone ranks is left out, and so are Spirit and Stamina trailing at the very end of a damage
# list. Two builds step outside these rules, and say so at their entry: Arms (its last row)
# and Protection Paladin (its three sources rank different things, so the order below the top
# three is a reading of them, not a count).
# ---------------------------------------------------------------------------------------
SCORED = {
    "Strength", "Agility", "Stamina", "Intellect", "Spirit", "Attack Power", "Hit", "Crit",
    "Spell Hit", "Spell Crit", "Spell Damage", "Healing Power", "MP5", "Armor", "Defense",
    "Dodge", "Parry", "Block", "Block Value",
}
SHOWN_ONLY = {"Expertise", "Haste", "Spell Haste", "Spell Piercing"}

SOURCE = "Stat priority: Forever's launch guides, read 5 Nov 2026."
# Every launch guide says this about its own level-60 list.
UNTESTED = " The guides themselves call this order untested at level 60."
HIT = "Hit first, up to the cap on the hit bar"
SPELL_HIT = "Spell hit first, up to the cap on the hit bar"

_HUNTER_RANGED = {
    "stats": ["Hit", "Crit", "Agility", "Intellect", "Attack Power"],
    "notes": HIT + ", then crit, then agility: two of the three guides place crit above agility, the third gives "
             "crit no place. Intellect ranks above attack power.",
}
_MAGE_HASTE = {
    "stats": ["Spell Hit", "Spell Damage", "Spell Crit", "Spell Haste", "Intellect", "Spirit"],
    "notes": SPELL_HIT + ", then spell damage, then crit. Two of the three guides rank haste above intellect; "
             "spirit comes last.",
}

SPECS = {
    "WARRIOR": {
        # Three lists: Hit > Expertise > Crit > Strength (two), Hit > Crit > Expertise > Strength (one).
        # Two of them go on below Strength: Agility > Haste in one, Haste > Agility in the other. Attack
        # Power is ranked by one list only (last of these) and named under Strength in a second one's
        # stat table: kept as the last row, because it is what Strength gives and a stat that is no row
        # counts for next to nothing on an item.
        "Arms": {
            "stats": ["Hit", "Expertise", "Crit", "Strength", "Agility", "Haste", "Attack Power"],
            "notes": HIT + ", then expertise and crit - the guides differ on which of the two leads - then strength. "
                     "Agility and haste follow, and the guides differ on which of those two leads as well. Attack "
                     "power closes the list; one guide ranks it.",
        },
    },
    "PALADIN": {
        # Stamina, Defense and Spell Damage head all three sources (one ranks Hit between them);
        # the rest follows the balanced profile of one, with Intellect and Strength as a second ranks them.
        "Protection": {
            "stats": ["Stamina", "Defense", "Spell Damage", "Hit", "Armor", "Intellect", "Strength"],
            "notes": "Stamina, Defense and spell damage sit at or near the top of every launch guide, though not in the "
                     "same order. Hit and armor follow where a guide ranks them; intellect and strength close the list, "
                     "and the guides differ on which of the two is worth more.",
        },
    },
    "HUNTER": {
        # Hit > Crit > Agility in two lists, Hit > Agility in the third (it places no crit); Intellect above
        # Attack Power. The same third list is why Survival's note carries the same sentence.
        "Beast Mastery": _HUNTER_RANGED,
        "Marksmanship": _HUNTER_RANGED,
        # Hit > Crit > Agility > Attack Power in two; Strength against Intellect goes both ways.
        "Survival": {
            "stats": ["Hit", "Crit", "Agility", "Attack Power"],
            "notes": HIT + ", then crit, then agility, then attack power: two of the three guides place crit above "
                     "agility, the third gives crit no place. The guides place strength and intellect differently, so "
                     "neither is ranked here.",
        },
    },
    "PRIEST": {
        # Hit > Spell Damage > Crit in two of three (the third swaps the last two); Intellect > Spirit.
        "Shadow": {
            "stats": ["Spell Hit", "Spell Damage", "Spell Crit", "Intellect", "Spirit"],
            "notes": SPELL_HIT + ", then spell damage, then crit - one guide swaps those two - then intellect, then spirit.",
        },
    },
    "SHAMAN": {
        # Enhancement has NO list on purpose, see HELD_BACK.
        # Two lists, the same order; one of them adds Haste after Crit.
        "Restoration": {
            "stats": ["Healing Power", "Spell Crit", "Intellect", "Spirit", "MP5"],
            "notes": "Healing power first, then crit, then intellect, then spirit, then MP5.",
        },
    },
    "MAGE": {
        # Fire and Arcane: Hit > Spell Damage > Crit in all three; Haste above Intellect in two.
        "Arcane": _MAGE_HASTE,
        "Fire": _MAGE_HASTE,
        # Frost: Hit > Spell Damage > Crit in two of three (the third swaps the last two); Haste in one only.
        "Frost": {
            "stats": ["Spell Hit", "Spell Damage", "Spell Crit", "Intellect", "Spirit"],
            "notes": SPELL_HIT + ", then spell damage, then crit - one guide swaps those two - then intellect, then spirit.",
        },
    },
    "WARLOCK": {
        # Two lists identical to the last row; the third only moves Hit to the front.
        "Demonology": {
            "stats": ["Spell Damage", "Spell Hit", "Spell Crit", "Spell Haste", "Spell Piercing", "Intellect", "Spirit"],
            "notes": "Spell damage first, then spell hit, then crit, then haste, then spell piercing, intellect and "
                     "spirit. One guide puts hit ahead of spell damage until the hit bar is full.",
        },
        # Two lists identical to the last row; the third has Hit first and Haste above Crit.
        "Destruction": {
            "stats": ["Spell Damage", "Spell Crit", "Spell Hit", "Spell Haste", "Spell Piercing", "Intellect", "Spirit"],
            "notes": "Spell damage first, then crit, then spell hit, then haste, then spell piercing, intellect and "
                     "spirit. One guide puts hit first and haste ahead of crit.",
        },
    },
}

# Agreed in the harvest, but not shipped: the reason, so nobody builds it from the same data.
HELD_BACK = {
    ("SHAMAN", "Enhancement"):
        "The 5 Nov guides rank Intellect above Strength. On 6 Nov 2026 Blizzard announced hotfixes for 10 Nov "
        "that make Strength Enhancement's strongest stat; the guides were last touched 3-4 Nov. Build it from "
        "the first harvest after the guides follow that change.",
}


def lua_str(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def lua_key(s):
    return s if s.replace("_", "a").isalnum() and not s[0].isdigit() else "[" + lua_str(s) + "]"


def no_twice(pairs):
    """A JSON object whose key comes twice is an error, not 'the last one wins'."""
    seen = {}
    for k, v in pairs:
        if k in seen:
            raise SystemExit("%s: %r appears twice" % (MAP, k))
        seen[k] = v
    return seen


def spec_lines():
    """The F.specs block. Classes in CLASSES order, trees by name; every list is checked."""
    for cls in SPECS:
        if cls not in CLASSES:
            raise SystemExit("SPECS: no class %r" % cls)
    out = ["F.specs = {"]
    for cls in CLASSES:
        if cls not in SPECS:
            continue
        out.append("  %s = {" % cls)
        for name in sorted(SPECS[cls]):
            if (cls, name) in HELD_BACK:
                raise SystemExit("%s %s is held back and has a list" % (cls, name))
            if name not in TREES[cls]:
                raise SystemExit("%s: no tree %r" % (cls, name))
            e = SPECS[cls][name]
            stats = e["stats"]
            for st in stats:
                if st not in SCORED and st not in SHOWN_ONLY:
                    raise SystemExit("%s %s: the engine has no stat %r" % (cls, name, st))
            if len(set(stats)) != len(stats) or not 1 <= len(stats) <= 8:   # 8 rows fit the panel
                raise SystemExit("%s %s: %d rows, or one twice" % (cls, name, len(stats)))
            out.append("    %s = {" % lua_key(name))
            out.append("      stats = { %s }," % ", ".join(lua_str(st) for st in stats))
            out.append("      notes = %s," % lua_str(e["notes"] + UNTESTED))
            out.append("      source = %s," % lua_str(SOURCE))
            out.append("    },")
        out.append("  },")
    out.append("}")
    return out


def main():
    data = json.load(io.open(MAP, encoding="utf-8"), object_pairs_hook=no_twice)
    order = data.get("_tree_order", {})
    trees = data["talentTree"]
    if sorted(trees) != sorted(CLASSES):
        raise SystemExit("classes in %s: %s" % (MAP, sorted(trees)))

    out = []
    out.append('''--[[ StatCapData_Forever.lua
     WORLD OF WARCRAFT: FOREVER data. Loaded only by the Forever TOC. Pure tables.

     Forever has one specialization per class (all named after the class, read off the beta,
     build 69977) and its three classic talent trees live inside ONE trait tree, so the game
     cannot be asked which tree you play. StatCap reads the points spent in each tree off the
     game's own tree headings (the talent window's three trait groups) and counts by talent
     name only on a client that offers no such counts. Which tree a talent sits in: Forever's
     talents after the 2-4 Nov 2026 rework, from Wowhead's Forever talent data and Icy Veins'
     calculator (read 8 Nov 2026; for Shaman Wowhead's alone, Icy Veins' file predating the
     4 Nov changes). The order of the trees is Era's (StatCapData_Era.lua tabSpec), so tree 1
     of a paladin is Holy everywhere.

     Generated by gen_forever_data.py - edit the generator, not this file.
]]--

local ADDON, ns = ...
ns.Data = ns.Data or {}
local D = ns.Data

D.forever = D.forever or {}
local F = D.forever

-- [CLASS] = { [talent name] = tree (1, 2 or 3) }
F.talentTree = {''')

    total = 0
    for cls in CLASSES:
        named = [n.split()[0] for n in order.get(cls, [])]
        if named != ERA[cls]:
            raise SystemExit("%s: the file's trees %s are not Era's %s" % (cls, order.get(cls), ERA[cls]))
        seen = {}
        for name, tree in trees[cls].items():
            name = name.strip()
            if tree not in (1, 2, 3):
                raise SystemExit("%s %s: tree %r" % (cls, name, tree))
            if name in seen and seen[name] != tree:
                raise SystemExit("talent in two trees: %s %s" % (cls, name))
            seen[name] = tree
        total += len(seen)
        out.append("  %s = {" % cls)
        for name in sorted(seen):
            out.append("    [%s] = %d," % (lua_str(name), seen[name]))
        out.append("  },")
    out.append("}")

    out.append('''
-- Forever's own level-60 stat lists, for the trees whose launch guides agree on an order
-- (read 5 Nov 2026). Same shape as Era's spec entries; only the fields given here replace
-- Era's. A tree that is not in here keeps Era's list as a stand-in, and the panel says so.
-- Expertise, Haste, Spell Haste and Spell Piercing are rows no item is counted for yet.''')
    out.extend(spec_lines())
    out.append("")

    lists = sum(len(v) for v in SPECS.values())
    io.open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(out))
    print("wrote %s: %d talents, %d stat lists" % (OUT, total, lists))


if __name__ == "__main__":
    main()
