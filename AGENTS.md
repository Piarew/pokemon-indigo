# Pokémon Indigo — agent rules

FireRed expansion hack. Product ROM: `make BUILD=firered` → `pokefirered.gba`. Playable regions: Kanto + Johto + Sinnoh. Hoenn is never playable.

Private notes live in gitignored `documentation/`. This file is the committed contract.

## Git

- **Trunk:** `master` is the only long-lived branch. Origin: `https://github.com/Piarew/pokemon-indigo.git`. Default branch is `master`.
- **Upstream:** `https://github.com/rh-hideout/pokeemerald-expansion.git`. Merge `upstream/master` into `master` when picking up RHH. Never push to upstream.
- **Do not** recreate long-lived `qol`, `map-polish`, `import-johto-hs2`, or `import-sinnoh`. Those histories already live on `master`. Leave `origin/prune` alone (unmerged spike-era audio work).
- **Branch first.** Start from up-to-date `master`. Create the topic branch *before* the first edit. Do not accumulate uncommitted work on `master` or on an unrelated existing branch (for example `indigo-story`).
- **Topic prefixes:**
  - `map/<slug>` — `map.bin`, layouts, tileset collision, warps
  - `feat/<slug>` — engine, QoL, UI
  - `data/<slug>` — wilds, trainers, items, species tables
  - `fix/<slug>` — bugs
  - `region/<slug>` — enabling, swapping, or importing a region (Sevii → Hoenn, new home region, bulk map-group include)
  - `upstream/<date>` — RHH merges
- **Separate branch for region work.** Enabling a region, swapping a home region, or mixing FRLG/Emerald map groups is its own `region/<slug>` branch. Do not fold that into a story, sprite, or QoL branch. If the plan changes mid-work (drop Sevii, import Hoenn), commit or stash the current branch, then start a new `region/<slug>` from `master`. Do not keep both experiments as one dirty tree.
- **Commit often.** One concern per commit. Commit at each testable increment — engine include, map enablement, runtime NULL/MAPSEC guard, script change, tileset wiring — not after the whole experiment is “done.” A ROM that boots is a commit. A black-screen fix is a commit. A revert of a content pass is a commit. Do not mix map.bin polish, engine/QoL, data tables, and region enablement in the same commit.
- **Push the topic branch** after every commit, or at least after every increment the user can test. Waiting until land is how mixed WIP gets trapped. This environment can `git push` via `gh` as Piarew.
- **Land:** only after the user asks. Fast-forward `master` to the topic branch, delete the topic branch, `git push origin master`. Delete the remote topic branch if it was pushed. One-commit chores may land directly on `master`.
- **Never force-push `master`.**
- Do not commit gitignored docs, `all_learnables.json`, or `"64x64 Trainer Sprites/"`.

## Maps

- Do not attempt custom edits to existing maps. That includes metatile painting, grass and path autotiles, building placement or restamps, connecting-map alignment, and copying metatiles from another town onto a map that already has a layout.
- Imported maps stay as imported. If asked to redesign, restyle, clean up, or convert an existing map, refuse and cite this rule.

## Build

- `make BUILD=firered` keeps `MAP_VERSION` even with extra make goals. `make firered` also works if it is the only goal.
- `make release` is the ship build (debug off, `DISABLED_ON_RELEASE` features off).

## Script dialogue

FireRed msgboxes are two lines. Instant text speed is the default, so a third line is unreadable.

- At most two lines per A-button continue.
- `\n` starts the second line of the current box.
- `\p` waits for A (the ▼ prompt), clears the box, and starts a new one.
- Do not use `\l` in player-facing script text. `\l` waits, then scrolls the first line away. Instant speed plus a held A skips that scroll, so the player never sees the line.
- Pattern:

```
	.string "First line of this box.\n"
	.string "Second line of this box.\p"
	.string "Next box, first line.\n"
	.string "Next box, second line.$"
```

- One-line boxes are fine: `.string "Go on.$"`
- Dynmultichoice labels, item names, and other single-line UI strings stay one line.
- When a sentence would need a third line, end the box with `\p` and continue in a new box. Break at a phrase boundary, not mid-word.
- The same two-line rule applies to C `_()` strings shown in a msgbox.
