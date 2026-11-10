# Pokémon Indigo — agent rules

FireRed expansion hack. Product ROM: `make BUILD=firered` → `pokefirered.gba`. Playable regions: Kanto + Johto + Sinnoh. Hoenn is never playable.

Private notes live in gitignored `documentation/`. This file is the committed contract.

## Git

- **Trunk:** `master` is the only long-lived branch. Origin: `https://github.com/Piarew/pokemon-indigo.git`. Default branch is `master`.
- **Upstream:** `https://github.com/rh-hideout/pokeemerald-expansion.git`. Merge `upstream/master` into `master` when picking up RHH. Never push to upstream.
- **Do not** recreate long-lived `qol`, `map-polish`, `import-johto-hs2`, or `import-sinnoh`. Those histories already live on `master`. Leave `origin/prune` alone (unmerged spike-era audio work).
- **Start work** from up-to-date `master`. For anything more than a one-commit chore, create a short-lived topic branch:
  - `map/<slug>` — `map.bin`, layouts, tileset collision, warps
  - `feat/<slug>` — engine, QoL, UI
  - `data/<slug>` — wilds, trainers, items, species tables
  - `fix/<slug>` — bugs
  - `upstream/<date>` — RHH merges
- **Land:** fast-forward `master` to the topic branch, delete the topic branch, `git push origin master`. Delete the remote topic branch if it was pushed. One-commit chores may land directly on `master`.
- **Never force-push `master`.**
- One concern per commit. Do not mix map.bin polish with engine/QoL/data in the same commit.
- After a finished task, push. This environment can `git push` via `gh` as Piarew.

## Build

- `make BUILD=firered` keeps `MAP_VERSION` even with extra make goals. `make firered` also works if it is the only goal.
- `make release` is the ship build (debug off, `DISABLED_ON_RELEASE` features off).
