# Allmons wild distribution

Rebuilds `src/data/wild_encounters.json` so every non-legendary, non-mythical National Dex species (931 of 1025) appears in Kanto, Johto, or Sinnoh wild tables.

- Common land slots keep FRLG / HGSS / DPPt route identity.
- Rare land slots, surf, fishing, rock smash, and DexNav `hidden_mons` cover the rest of the dex.
- Ultra Beasts and Paradox Pokémon are included (they are not legendary/mythical). Legendaries and mythicals stay out for later statics/quests.
- Input snapshot: `vanilla_wild_encounters.json` (Hoenn + FRLG Kanto/Sevii). Johto/Sinnoh maps: `locations.txt`.

```
python3 tools/allmons/build_wild_encounters.py
python3 tools/wild_encounters/wild_encounters_to_header.py
make BUILD=firered
```
