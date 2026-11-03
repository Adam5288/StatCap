# StatCap

*StatCap was called StatCoach until version 1.2.0.*

**Live stat priority, cap coach and gear compare — one addon for five clients: Classic Era, Burning Crusade Classic (Anniversary), Mists of Pandaria Classic, retail and World of Warcraft: Forever.**

StatCap reads your class, spec and level *live* and tells you which stats to favour right now, how far you are from the caps that actually matter, and whether the item under your cursor is a real upgrade — using cap-aware math instead of Pawn's flat weights.

---

## What it does

- **Priority list, live.** Detects your class/spec (most-points talent tab on TBC, the real spec on retail) and shows the correct stat order for your current context. Stats you've already capped sink to the bottom so the top of the list is always what to chase next.
- **Cap coach.** Bars for the caps that matter to your role, showing your current value and how much you still need. On TBC: Melee/Ranged special hit (9%), Spell hit (16%), Expertise (26 skill), Tank Defense (490). Classic Era and Forever coach hit from the weapon skill in your hands, plus weapon skill and Defense; Mists uses the game's own hit and expertise numbers; retail has no hard caps, so it shows your secondaries instead. **Talent and racial hit are read from your live character**, so the "to cap" number is true for *your* build, not a generic table.
- **Trade advisor.** A one-line "NOW:" call on what to favour or trade toward this moment (e.g. *"Below Hit cap — favour Hit, even trading AP for it"* → *"Hit capped. Now favour Expertise"*).
- **Cap-aware gear compare.** Hover any item and StatCap adds one line to the tooltip — it only speaks up on **upgrades** (percent gain), staying quiet on sidegrades and downgrades. It parses the real tooltip, so it counts **socketed gems and Equip effects** that stat-only addons miss, is **armor-type aware**, and scores **weapon DPS by role** (a warrior's bow is a stat-stick, not a weapon).
- **Bag upgrade badge.** A green `+` (or gold `++` for a big jump) on bag items that beat what you're wearing. Works in Baganator, Bagnon and the default bags.
- **Gems & Enchants popups.** Per socket colour and per slot, with real in-game icons and the Wowhead-standard choice for your spec (plus a cheaper alternative while leveling/pre-raid).
- **3-tier context (TBC).** Leveling → Pre-raid → Endgame, switchable, because the right priorities change as you gear up.
- **Movable window**, minimap button, ESC to close, adjustable scale, and a right-click settings menu.

## Why it's different from Pawn

Pawn multiplies each stat by a fixed weight. StatCap knows your **caps** and your **live character**: once you're hit-capped, more hit is worth ~0 and the score reflects that instantly. It answers *"which stat should I favour or trade toward now?"* — a question a flat weight can't. The two work well side by side.

## Usage

| Command | Effect |
|---|---|
| `/statcap` or `/stc` | Toggle the window |
| `/stc reset` | Reset window position |
| `/stc tooltip` | Toggle the tooltip upgrade line |
| `/stc bag` | Bag-badge diagnostic |
| `/stc minimap` | Show/hide the minimap button |

- **Left-click** the minimap button to toggle the window; **right-click** for settings; **drag** to move it.
- Click the **"i"** button in the window for spec and cap notes.

## Install

Drop the `StatCap` folder into your client's AddOns directory:

```
World of Warcraft\_classic_era_\Interface\AddOns\      (Classic Era)
World of Warcraft\_anniversary_\Interface\AddOns\      (Burning Crusade Classic)
World of Warcraft\_classic_\Interface\AddOns\          (Mists of Pandaria Classic)
World of Warcraft\_retail_\Interface\AddOns\           (retail)
World of Warcraft\_forever_\Interface\AddOns\          (World of Warcraft: Forever)
```

Then restart the client. Requires an **English client** (talent names and tooltip parsing are English).

Released builds are on [CurseForge](https://www.curseforge.com/wow/addons/statcoach) and [Wago](https://addons.wago.io/addons/statcoach), one package per client.

## Repository layout

One source tree serves every client. Each package carries only its own client's TOC:

| File | Used by |
|---|---|
| `StatCap.toc` | Burning Crusade Classic (`## Interface: 20506`) |
| `StatCap_Vanilla.toc` | Classic Era (`## Interface: 11509`) |
| `StatCap_Mists.toc` | Mists of Pandaria Classic (`## Interface: 50504`) |
| `StatCap_Mainline.toc` | Retail (`## Interface: 120007, 120100, 120105`) |
| `StatCap_Forever.toc` | World of Warcraft: Forever (`## Interface: 16001`), shipped as `StatCap.toc` in the Forever package |
| `StatCap.lua` | All logic, every client |
| `StatCapData.lua` | TBC data: 27 specs, caps, gems, enchants; every TOC loads it |
| `StatCapData_Retail.lua` | Retail data: 39 specs |
| `StatCapData_Era.lua` | Classic Era stat lists per talent tree |
| `StatCapData_Mists.lua` | Mists of Pandaria Classic stat lists per specialization |
| `StatCapData_Forever.lua` | Forever: which tree each talent sits in, plus Forever's own lists |
| `StatCoach/` | Settings-only folder that ships next to StatCap (StatCap was called StatCoach until 1.2.0): one TOC per client, no code, written by `Tools/make_stub.py` |
| `Libs/` | LibStub, CallbackHandler, LibDataBroker, LibDBIcon (minimap button) |

Which TOC loads which data file: TBC loads `StatCapData.lua` only; retail adds `StatCapData_Retail.lua`; Classic Era adds `StatCapData_Era.lua`; Mists adds `StatCapData_Mists.lua`; Forever adds the retail, Era and Forever files.

## Contributing

Pull requests are welcome — bug fixes, spec-data corrections and integrations especially.

A few things worth knowing before you open one:

- **Say what you measured.** Stat priorities and cap numbers in this addon are meant to be verifiable. A PR that changes a number is much easier to merge with a source or an in-game reading attached.
- **Every client.** If a change touches shared logic in `StatCap.lua`, say which client(s) you tested it on. An API from one client can break another.
- **Keep it English.** UI strings and code are English throughout.
- **One idea per PR.** Easier to review, easier to revert.

Open an issue first if you want to discuss a larger feature before building it.

**Contributions and the licence.** StatCap is released under the licence below. By
opening a pull request you confirm that the work is yours to give, and you grant
permission for it to be included in StatCap and released under that same licence. You
keep the copyright to what you wrote — this only covers the permission needed to ship it
as part of the addon, and you will be credited in the changelog.

## Notes

- Stat priorities for all 27 TBC specs are cross-checked against Wowhead, Icy Veins and Warcraft Tavern guides; retail covers all 39 specs.
- Stat *weights* for gear scoring are a curated first pass — tuned per role/spec and improving over time.
- The only bundled libraries are LibStub, CallbackHandler, LibDataBroker and LibDBIcon, all embedded under `Libs/`. No other dependencies.

## Licence

All rights reserved. The source is public so it can be read, discussed and improved through pull requests; it is not licensed for redistribution or for republishing as a separate addon.
