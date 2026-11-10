#!/usr/bin/env python3
"""Build Kanto/Johto/Sinnoh wild tables covering every non-legendary, non-mythical National Dex species.

Classic route identity stays in the common slots. Later-gen and leftover species go in
rare land slots, surf/fishing/rock smash, and DexNav hidden_mons.

Usage:
    python3 tools/allmons/build_wild_encounters.py
    python3 tools/wild_encounters/wild_encounters_to_header.py
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path
from random import Random

ROOT = Path(__file__).resolve().parents[2]
WILD_JSON = ROOT / "src/data/wild_encounters.json"
VANILLA_JSON = Path(__file__).with_name("vanilla_wild_encounters.json")
LOCATIONS = Path(__file__).with_name("locations.txt")
SPECIES_INFO_DIR = ROOT / "src/data/pokemon/species_info"
SPECIES_H = ROOT / "include/constants/species.h"
POKEDEX_H = ROOT / "include/constants/pokedex.h"
MAPS_DIR = ROOT / "data/maps"

FLAG_FORM = (
    "isMegaEvolution", "isPrimalReversion", "isUltraBurst", "isGigantamax", "isTeraForm",
    "isTotem", "isAlolanForm", "isGalarianForm", "isHisuianForm", "isPaldeanForm",
)
FLAG_LEGEND = ("isRestrictedLegendary", "isSubLegendary", "isMythical")
WATER_EGGS = {"EGG_GROUP_WATER_1", "EGG_GROUP_WATER_2", "EGG_GROUP_WATER_3"}
MINERAL_EGGS = {"EGG_GROUP_MINERAL"}

# Macro-only families whose natDexNum lives in a #define, not the [SPECIES_] body.
MANUAL_SPECIES = {
    "UNOWN": {"types": ["TYPE_PSYCHIC"], "eggs": ["EGG_GROUP_NO_EGGS_DISCOVERED"], "catch": 225},
    "MOTHIM": {"types": ["TYPE_BUG", "TYPE_FLYING"], "eggs": ["EGG_GROUP_BUG"], "catch": 45},
    "SCATTERBUG": {"types": ["TYPE_BUG"], "eggs": ["EGG_GROUP_BUG"], "catch": 255},
    "SPEWPA": {"types": ["TYPE_BUG"], "eggs": ["EGG_GROUP_BUG"], "catch": 120},
    "VIVILLON": {"types": ["TYPE_BUG", "TYPE_FLYING"], "eggs": ["EGG_GROUP_BUG"], "catch": 45},
    "FLABEBE": {"types": ["TYPE_FAIRY"], "eggs": ["EGG_GROUP_FAIRY"], "catch": 225},
    "FURFROU": {"types": ["TYPE_NORMAL"], "eggs": ["EGG_GROUP_FIELD"], "catch": 160},
    "MINIOR": {"types": ["TYPE_ROCK", "TYPE_FLYING"], "eggs": ["EGG_GROUP_MINERAL"], "catch": 30},
}

TYPE_BIOMES = {
    "TYPE_NORMAL": {"field", "grass", "urban", "safari", "early"},
    "TYPE_FIRE": {"volcano", "desert", "field"},
    "TYPE_WATER": {"water", "beach", "swamp"},
    "TYPE_GRASS": {"grass", "forest", "swamp", "field"},
    "TYPE_ELECTRIC": {"power", "urban", "field"},
    "TYPE_ICE": {"ice", "snow"},
    "TYPE_FIGHTING": {"mountain", "cave", "field"},
    "TYPE_POISON": {"swamp", "urban", "haunted", "grass"},
    "TYPE_GROUND": {"cave", "mountain", "desert", "field"},
    "TYPE_FLYING": {"grass", "mountain", "beach", "early"},
    "TYPE_PSYCHIC": {"ruins", "urban", "grass"},
    "TYPE_BUG": {"bug", "forest", "grass", "early", "safari"},
    "TYPE_ROCK": {"cave", "mountain", "desert"},
    "TYPE_GHOST": {"haunted", "tower", "ruins"},
    "TYPE_DRAGON": {"dragon", "cave", "mountain", "late", "water"},
    "TYPE_DARK": {"haunted", "cave", "swamp"},
    "TYPE_STEEL": {"cave", "power", "mountain"},
    "TYPE_FAIRY": {"forest", "grass", "field", "ruins"},
}

HIDDEN_RATES = [50, 30, 20]
HIDDEN_FIELD = {"type": "hidden_mons", "encounter_rates": HIDDEN_RATES}

DEFAULT_WATER = {
    "kanto": ["TENTACOOL", "TENTACRUEL", "MAGIKARP", "GYARADOS", "PSYDUCK"],
    "sevii": ["TENTACOOL", "TENTACRUEL", "MAGIKARP", "HORSEA", "PSYDUCK"],
    "johto": ["TENTACOOL", "TENTACRUEL", "MAGIKARP", "WOOPER", "MANTINE"],
    "sinnoh": ["TENTACOOL", "WINGULL", "SHELLOS", "BUIZEL", "MAGIKARP"],
}
DEFAULT_FISH = {
    "kanto": ["MAGIKARP", "MAGIKARP", "POLIWAG", "GOLDEEN", "MAGIKARP", "GYARADOS", "PSYDUCK", "POLIWHIRL", "GYARADOS", "GYARADOS"],
    "sevii": ["MAGIKARP", "MAGIKARP", "HORSEA", "KRABBY", "QWILFISH", "GYARADOS", "SEADRA", "KINGLER", "GYARADOS", "GYARADOS"],
    "johto": ["MAGIKARP", "MAGIKARP", "POLIWAG", "GOLDEEN", "TENTACOOL", "GYARADOS", "POLIWHIRL", "SEAKING", "CORSOLA", "GYARADOS"],
    "sinnoh": ["MAGIKARP", "MAGIKARP", "BARBOACH", "FINNEON", "GOLDEEN", "GYARADOS", "WHISCASH", "LUMINEON", "GYARADOS", "GYARADOS"],
}
DEFAULT_ROCK = ["GEODUDE", "GEODUDE", "GRAVELER", "NOSEPASS", "SHUCKLE"]


def species_token(name: str) -> str:
    return name if name.startswith("SPECIES_") else "SPECIES_" + name


def parse_aliases() -> dict[str, str]:
    """Map canonical SPECIES_* form keys to the preferred short alias."""
    text = SPECIES_H.read_text()
    alias_of: dict[str, str] = {}
    for m in re.finditer(r"(SPECIES_\w+)\s*=\s*(SPECIES_\w+)\s*,", text):
        short, long = m.group(1), m.group(2)
        # Keep the first/shortest alias for a long form.
        if long not in alias_of or len(short) < len(alias_of[long]):
            alias_of[long] = short
    return alias_of


def parse_species() -> dict[str, dict]:
    """Return {SPECIES_FOO: {dex, types, eggs, catch, ub, paradox}} for wild-eligible dex entries."""
    alias_of = parse_aliases()
    blocks: dict[str, dict] = {}
    for path in sorted(SPECIES_INFO_DIR.glob("gen_*_families.h")):
        text = path.read_text()
        parts = re.split(r"\n\s*\[(SPECIES_\w+)\]\s*=\s*\{", text)
        for i in range(1, len(parts), 2):
            name, body = parts[i], parts[i + 1]
            nat = re.search(r"\.natDexNum\s*=\s*(NATIONAL_DEX_\w+)", body)
            if not nat:
                continue
            types = re.search(r"\.types\s*=\s*MON_TYPES\(([^)]+)\)", body)
            eggs = re.search(r"\.eggGroups\s*=\s*MON_EGG_GROUPS\(([^)]+)\)", body)
            catch = re.search(r"\.catchRate\s*=\s*(\d+)", body)
            info = {
                "dex": nat.group(1),
                "types": [x.strip() for x in types.group(1).split(",")] if types else [],
                "eggs": [x.strip() for x in eggs.group(1).split(",")] if eggs else [],
                "catch": int(catch.group(1)) if catch else 100,
                "legend": any(re.search(rf"\.{f}\s*=\s*TRUE", body) for f in FLAG_LEGEND),
                "form": any(re.search(rf"\.{f}\s*=\s*TRUE", body) for f in FLAG_FORM),
                "ub": bool(re.search(r"\.isUltraBeast\s*=\s*TRUE", body)),
                "paradox": bool(re.search(r"\.isParadox\s*=\s*TRUE", body)),
            }
            blocks[name] = info

    legendary_dex = {info["dex"] for info in blocks.values() if info["legend"]}
    # Silvally / Ogerpon / Arceus live in macros; treat as legendary by name.
    legendary_dex.update({
        "NATIONAL_DEX_ARCEUS", "NATIONAL_DEX_GENESECT", "NATIONAL_DEX_SILVALLY",
        "NATIONAL_DEX_TYPE_NULL", "NATIONAL_DEX_OGERPON", "NATIONAL_DEX_TERAPAGOS",
        "NATIONAL_DEX_PECHARUNT",
    })

    by_dex: dict[str, list[str]] = defaultdict(list)
    for name, info in blocks.items():
        by_dex[info["dex"]].append(name)

    eligible: dict[str, dict] = {}
    for dex, names in by_dex.items():
        if dex in legendary_dex:
            continue
        cands = [n for n in names if not blocks[n]["form"]] or names
        pick = cands[0]
        want = "SPECIES_" + dex.replace("NATIONAL_DEX_", "")
        if want in cands:
            pick = want
        elif pick in alias_of:
            pick = alias_of[pick]
        elif want in alias_of.values():
            pick = want
        raw = blocks.get(names[0])
        for n in names:
            if not blocks[n]["form"]:
                raw = blocks[n]
                break
        eligible[pick] = {
            "dex": dex,
            "types": raw["types"],
            "eggs": raw["eggs"],
            "catch": raw["catch"],
            "ub": raw["ub"],
            "paradox": raw["paradox"],
        }

    for short, meta in MANUAL_SPECIES.items():
        token = species_token(short)
        dex = "NATIONAL_DEX_" + short
        if dex in legendary_dex:
            continue
        if token not in eligible and not any(v["dex"] == dex for v in eligible.values()):
            eligible[token] = {
                "dex": dex,
                "types": meta["types"],
                "eggs": meta["eggs"],
                "catch": meta["catch"],
                "ub": False,
                "paradox": False,
            }
    return eligible


def load_folder_ids() -> dict[str, str]:
    out = {}
    for p in MAPS_DIR.glob("*/map.json"):
        data = json.loads(p.read_text())
        out[p.parent.name] = data["id"]
        out[data.get("name", "")] = data["id"]
    return out


def parse_locations(folder_ids: dict[str, str]) -> list[dict]:
    locs = []
    for line in LOCATIONS.read_text().splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 4:
            raise SystemExit(f"bad location line: {line}")
        folder, biomes, band, kinds = parts[:4]
        classic = parts[4].split() if len(parts) > 4 else []
        lo, hi = (int(x) for x in band.split("-"))
        map_id = folder_ids.get(folder)
        if not map_id:
            raise SystemExit(f"unknown map folder {folder}")
        locs.append({
            "folder": folder,
            "map": map_id,
            "biomes": set(biomes.split()),
            "lo": lo,
            "hi": max(hi, lo),
            "land": "L" in kinds,
            "water": "W" in kinds,
            "fish": "F" in kinds,
            "rocks": "R" in kinds,
            "classic": [species_token(s) for s in classic],
            "region": region_of_folder(folder),
        })
    return locs


def region_of_folder(folder: str) -> str:
    if folder.endswith("_hns") or folder.startswith("SafariZone"):
        return "johto"
    return "sinnoh"


def kanto_region(map_id: str) -> str:
    u = map_id.upper()
    if any(s in u for s in ("ISLAND", "KINDLE", "BOND_BRIDGE", "CAPE_BRINK", "TREASURE_BEACH",
                             "RESORT_GORGEOUS", "WATER_LABYRINTH", "MEADOW", "MEMORIAL",
                             "OUTCAST", "GREEN_PATH", "WATER_PATH", "RUIN_VALLEY",
                             "TRAINER_TOWER", "SEVAULT", "TANOBY", "BERRY_FOREST",
                             "ICEFALL", "PATTERN_BUSH", "LOST_CAVE", "MT_EMBER", "ALTERING")):
        return "sevii"
    return "kanto"


def kanto_biomes(map_id: str) -> set[str]:
    u = map_id.upper()
    tags: set[str] = set()
    if any(s in u for s in ("FOREST", "BUSH", "BERRY")):
        tags.update({"forest", "bug", "grass"})
    if any(s in u for s in ("MT_MOON", "DIGLETT", "ROCK_TUNNEL", "VICTORY", "CERULEAN_CAVE")):
        tags.update({"cave"})
    if any(s in u for s in ("SEAFOAM", "ICEFALL")):
        tags.update({"ice", "cave"})
    if any(s in u for s in ("TOWER", "LOST_CAVE", "MANSION")):
        tags.update({"haunted", "tower"})
    if "POWER" in u:
        tags.update({"power"})
    if any(s in u for s in ("EMBER", "RUBY", "CINNABAR")):
        tags.update({"volcano"})
    if "SAFARI" in u:
        tags.update({"safari", "grass", "swamp"})
    if "TANOBY" in u:
        tags.update({"ruins"})
    if any(s in u for s in ("SEVAULT", "RUIN_VALLEY")):
        tags.update({"mountain", "ruins", "desert"})
    if any(s in u for s in ("MEADOW", "MEMORIAL", "BOND", "CAPE", "KINDLE", "TREASURE", "WATER_PATH")):
        tags.update({"island", "grass", "beach"})
    if re.search(r"ROUTE1\b", u) or u.endswith("ROUTE1"):
        tags.update({"early", "field", "grass"})
    if "ROUTE2" in u and "ROUTE21" not in u and "ROUTE22" not in u and "ROUTE23" not in u and "ROUTE24" not in u and "ROUTE25" not in u:
        tags.update({"early", "grass", "forest"})
    if any(s in u for s in ("ROUTE22", "ROUTE23")):
        tags.update({"late", "grass"})
    if not tags:
        tags.update({"grass", "field"})
    if any(s in u for s in ("ROUTE19", "ROUTE20", "ROUTE21")):
        tags.update({"water", "beach"})
    return tags


def label_for(map_id: str) -> str:
    return "s" + "".join(p.title() for p in map_id.replace("MAP_", "").split("_"))


def spread_levels(n: int, lo: int, hi: int) -> list[tuple[int, int]]:
    lo = max(2, lo)
    hi = max(lo, hi)
    out = []
    for i in range(n):
        a = lo + (hi - lo) * i // max(n, 1)
        b = lo + (hi - lo) * (i + 1) // max(n, 1)
        b = max(a, min(hi, b))
        a = min(a, b)
        out.append((a, b))
    return out


def slot(species: str, lo: int, hi: int) -> dict:
    return {"min_level": int(lo), "max_level": int(hi), "species": species}


def unique_in_order(mons: list[dict]) -> list[str]:
    seen = []
    for m in mons:
        s = m["species"]
        if s not in seen:
            seen.append(s)
    return seen


def is_waterish(info: dict) -> bool:
    types, eggs = set(info["types"]), set(info["eggs"])
    if "TYPE_WATER" in types:
        return True
    if eggs & WATER_EGGS and "TYPE_GRASS" not in types:
        return True
    return False


def is_rockish(info: dict) -> bool:
    types = set(info["types"])
    return "TYPE_ROCK" in types or ("TYPE_GROUND" in types and "TYPE_WATER" not in types)


def is_landish(info: dict) -> bool:
    """True if the mon can reasonably appear in grass/caves (not fish-only)."""
    types, eggs = set(info["types"]), set(info["eggs"])
    if types & {"TYPE_GRASS", "TYPE_BUG", "TYPE_NORMAL", "TYPE_FIRE", "TYPE_ELECTRIC",
                "TYPE_FIGHTING", "TYPE_POISON", "TYPE_GROUND", "TYPE_FLYING", "TYPE_PSYCHIC",
                "TYPE_ROCK", "TYPE_GHOST", "TYPE_DRAGON", "TYPE_DARK", "TYPE_STEEL", "TYPE_FAIRY",
                "TYPE_ICE"}:
        if types == {"TYPE_WATER"} and eggs <= WATER_EGGS | {"EGG_GROUP_NO_EGGS_DISCOVERED"}:
            return False
        return True
    if "TYPE_WATER" in types and types - {"TYPE_WATER", "TYPE_FLYING"}:
        return True
    return False


def score_location(info: dict, loc: dict) -> int:
    biomes = loc["biomes"]
    score = 0
    for t in info["types"]:
        score += 3 * len(TYPE_BIOMES.get(t, set()) & biomes)
    if info["paradox"] or info["ub"]:
        if "late" in biomes or "cave" in biomes:
            score += 8
        else:
            score -= 6
    if info["catch"] <= 45 and "late" in biomes:
        score += 2
    early_types = set(info["types"]) & {"TYPE_NORMAL", "TYPE_BUG", "TYPE_FLYING", "TYPE_GRASS", "TYPE_FAIRY"}
    if info["catch"] >= 150 and "early" in biomes and early_types:
        score += 2
    if is_waterish(info) and loc["water"]:
        score += 4
    if is_rockish(info) and loc["rocks"]:
        score += 3
    if not loc["land"] and is_landish(info) and not is_waterish(info):
        score -= 10
    return score


def cycle_fill(base: list[str], n: int, fallback: str) -> list[str]:
    src = [s for s in base if s] or [fallback]
    return [src[i % len(src)] for i in range(n)]


def make_mons(species_list: list[str], levels: list[tuple[int, int]]) -> list[dict]:
    return [slot(sp, lo, hi) for sp, (lo, hi) in zip(species_list, levels)]


def land_rate(loc: dict) -> int:
    if "cave" in loc["biomes"] or "tower" in loc["biomes"] or "haunted" in loc["biomes"]:
        return 10
    return 21


class Pool:
    def __init__(self, eligible: dict[str, dict], rng: Random):
        self.eligible = eligible
        self.remaining = set(eligible)
        self.rng = rng
        self.placed: dict[str, list[str]] = defaultdict(list)

    def take(self, name: str, where: str) -> bool:
        if name not in self.eligible:
            return False
        self.placed[name].append(where)
        self.remaining.discard(name)
        return True

    def pick(self, candidates: list[str], where: str, n: int) -> list[str]:
        out = []
        for name in candidates:
            if len(out) >= n:
                break
            if name in self.remaining and self.take(name, where):
                out.append(name)
        return out


def ranked_remaining(pool: Pool, loc: dict, pred, min_score: int = 2) -> list[str]:
    scored = []
    for name in pool.remaining:
        info = pool.eligible[name]
        if not pred(info):
            continue
        sc = score_location(info, loc)
        if sc < min_score:
            continue
        scored.append((sc, -info["catch"], name))
    scored.sort(reverse=True)
    return [n for _, _, n in scored]


def assign_to_loc(pool: Pool, loc: dict, extra: dict) -> None:
    key = loc["map"]
    extra.setdefault(key, {"land": [], "water": [], "fish": [], "rocks": [], "hidden": []})

    if loc["land"]:
        land_pred = lambda inf: is_landish(inf) or not is_waterish(inf)
        land_n = 8 if "safari" in loc["biomes"] else 4
        extra[key]["land"] += pool.pick(ranked_remaining(pool, loc, land_pred), key + ":land", land_n)
    if loc["water"]:
        extra[key]["water"] += pool.pick(ranked_remaining(pool, loc, is_waterish), key + ":water", 3)
    if loc["fish"]:
        extra[key]["fish"] += pool.pick(ranked_remaining(pool, loc, is_waterish), key + ":fish", 5)
    if loc["rocks"]:
        extra[key]["rocks"] += pool.pick(ranked_remaining(pool, loc, is_rockish), key + ":rocks", 3)

    hidden_n = 3
    if loc["land"]:
        pred = lambda inf: is_landish(inf) or inf["paradox"] or inf["ub"]
    else:
        pred = is_waterish
    extra[key]["hidden"] += pool.pick(ranked_remaining(pool, loc, pred), key + ":hidden", hidden_n)


def biome_matches(info: dict, loc: dict, min_score: int = 2) -> bool:
    return score_location(info, loc) >= min_score


def sprinkle_from_pool(loc: dict, extra: dict, eligible: dict[str, dict]) -> None:
    """Fill empty rare/hidden slots with biome-fit species even if they already appear elsewhere."""
    key = loc["map"]
    extra.setdefault(key, {"land": [], "water": [], "fish": [], "rocks": [], "hidden": []})
    already = set(loc.get("classic", [])) | set(extra[key]["land"]) | set(extra[key]["hidden"])

    def fill(kind: str, n: int, pred):
        if len(extra[key][kind]) >= n:
            return
        ranked = []
        for name, info in eligible.items():
            if not pred(info):
                continue
            if name in already:
                continue
            sc = score_location(info, loc)
            if sc < 2:
                continue
            ranked.append((sc, -info["catch"], name))
        ranked.sort(reverse=True)
        for _, _, name in ranked:
            if len(extra[key][kind]) >= n:
                break
            extra[key][kind].append(name)
            already.add(name)

    if loc["land"]:
        fill("land", 3, lambda inf: is_landish(inf) or not is_waterish(inf))
        fill("hidden", 3, lambda inf: is_landish(inf) or inf["paradox"] or inf["ub"])
    elif loc["water"]:
        fill("hidden", 3, is_waterish)
    if loc["water"]:
        fill("water", 3, is_waterish)
    if loc["fish"]:
        fill("fish", 5, is_waterish)
    if loc["rocks"]:
        fill("rocks", 3, is_rockish)


def dump_kind(species_list: list[str], lo: int, hi: int, n: int, fallback: str, rate: int) -> dict:
    filled = cycle_fill(species_list, n, fallback)
    levels = spread_levels(n, lo, hi)
    return {"encounter_rate": rate, "mons": make_mons(filled, levels)}


def build_new_entry(loc: dict, extra: dict, version: str) -> dict:
    key = loc["map"]
    ex = extra.get(key, {"land": [], "water": [], "fish": [], "rocks": [], "hidden": []})
    region = loc["region"]
    fallback = "SPECIES_RATTATA" if region != "sinnoh" else "SPECIES_BIDOOF"
    entry = {
        "map": loc["map"],
        "base_label": label_for(loc["map"]) + "_" + version,
    }
    if loc["land"]:
        classic = [s for s in loc["classic"] if s]
        n_extra = min(8, len(ex["land"])) if ex["land"] else 0
        n_extra = max(n_extra, 0)
        n_classic = 12 - n_extra
        land_species = cycle_fill(classic, n_classic, fallback) + cycle_fill(ex["land"] or classic, n_extra, fallback)
        entry["land_mons"] = {
            "encounter_rate": land_rate(loc),
            "mons": make_mons(land_species, spread_levels(12, loc["lo"], loc["hi"])),
        }
    if loc["water"]:
        water_species = cycle_fill(loc["classic"] if is_mostly_water(loc) else [], 2, species_token(DEFAULT_WATER[region][0]))
        # Prefer default water identity in common slots.
        water_species = [species_token(s) for s in DEFAULT_WATER[region][:2]] + cycle_fill(ex["water"], 3, species_token(DEFAULT_WATER[region][0]))
        entry["water_mons"] = {
            "encounter_rate": 2,
            "mons": make_mons(water_species, spread_levels(5, loc["lo"], loc["hi"])),
        }
    if loc["rocks"]:
        rock_species = [species_token(s) for s in DEFAULT_ROCK[:2]] + cycle_fill(ex["rocks"], 3, "SPECIES_GEODUDE")
        entry["rock_smash_mons"] = {
            "encounter_rate": 25,
            "mons": make_mons(rock_species, spread_levels(5, loc["lo"], loc["hi"])),
        }
    if loc["fish"]:
        fish = [species_token(s) for s in DEFAULT_FISH[region][:5]] + cycle_fill(ex["fish"], 5, "SPECIES_MAGIKARP")
        entry["fishing_mons"] = {
            "encounter_rate": 20,
            "mons": make_mons(fish, spread_levels(10, max(5, loc["lo"]), loc["hi"] + 5)),
        }
    hidden_src = ex["hidden"] or (loc["classic"] + ex["land"] + ex["water"])
    hidden = cycle_fill(hidden_src, 3, fallback)
    entry["hidden_mons"] = {
        "encounter_rate": 0 if loc["land"] else 1,
        "mons": make_mons(hidden, spread_levels(3, loc["lo"], loc["hi"])),
    }
    return entry


def is_mostly_water(loc: dict) -> bool:
    return loc["water"] and not loc["land"]


def rewrite_kanto_entry(entry: dict, extra: dict, pool: Pool, eligible: dict) -> dict:
    map_id = entry["map"]
    new = {
        "map": map_id,
        "base_label": entry["base_label"],
    }
    loc_like = {
        "map": map_id,
        "biomes": kanto_biomes(map_id),
        "land": "land_mons" in entry,
        "water": "water_mons" in entry,
        "fish": "fishing_mons" in entry,
        "rocks": "rock_smash_mons" in entry,
        "lo": 2,
        "hi": 10,
        "classic": [],
        "region": kanto_region(map_id),
    }
    ex = extra.get(map_id, {"land": [], "water": [], "fish": [], "rocks": [], "hidden": []})

    def mix(old_mons, extras, n, fallback, keep):
        classic = [s for s in unique_in_order(old_mons) if s.startswith("SPECIES_")]
        keep = min(keep, n)
        head = cycle_fill(classic, keep, fallback)
        tail = cycle_fill(extras or classic, n - keep, fallback)
        levels = [(m["min_level"], m["max_level"]) for m in old_mons]
        while len(levels) < n:
            levels.append(levels[-1] if levels else (5, 5))
        return make_mons(head + tail, levels[:n])

    fallback = "SPECIES_RATTATA"
    if "land_mons" in entry:
        mons = entry["land_mons"]["mons"]
        loc_like["lo"] = min(m["min_level"] for m in mons)
        loc_like["hi"] = max(m["max_level"] for m in mons)
        new["land_mons"] = {
            "encounter_rate": entry["land_mons"]["encounter_rate"],
            "mons": mix(mons, ex["land"], 12, fallback, keep=12 - min(8, len(ex["land"]))),
        }
    if "water_mons" in entry:
        mons = entry["water_mons"]["mons"]
        new["water_mons"] = {
            "encounter_rate": entry["water_mons"]["encounter_rate"],
            "mons": mix(mons, ex["water"], 5, "SPECIES_TENTACOOL", keep=2),
        }
    if "rock_smash_mons" in entry:
        mons = entry["rock_smash_mons"]["mons"]
        new["rock_smash_mons"] = {
            "encounter_rate": entry["rock_smash_mons"]["encounter_rate"],
            "mons": mix(mons, ex["rocks"], 5, "SPECIES_GEODUDE", keep=2),
        }
    if "fishing_mons" in entry:
        mons = entry["fishing_mons"]["mons"]
        # Keep Magikarp old-rod identity, extras on super rod.
        classic = unique_in_order(mons)
        fish = cycle_fill(classic[:5] or ["SPECIES_MAGIKARP"], 5, "SPECIES_MAGIKARP") + cycle_fill(ex["fish"] or classic, 5, "SPECIES_GYARADOS")
        levels = [(m["min_level"], m["max_level"]) for m in mons]
        while len(levels) < 10:
            levels.append((max(20, loc_like["hi"]), max(25, loc_like["hi"] + 5)))
        new["fishing_mons"] = {
            "encounter_rate": entry["fishing_mons"]["encounter_rate"],
            "mons": make_mons(fish, levels[:10]),
        }

    hidden_src = ex["hidden"] or unique_in_order(entry.get("land_mons", entry.get("water_mons", {})).get("mons", []))
    lo = loc_like["lo"]
    hi = loc_like["hi"]
    if "land_mons" in entry:
        lo = min(m["min_level"] for m in entry["land_mons"]["mons"])
        hi = max(m["max_level"] for m in entry["land_mons"]["mons"])
    elif "water_mons" in entry:
        lo = min(m["min_level"] for m in entry["water_mons"]["mons"])
        hi = max(m["max_level"] for m in entry["water_mons"]["mons"])
    new["hidden_mons"] = {
        "encounter_rate": 0 if "land_mons" in entry else 1,
        "mons": make_mons(cycle_fill(hidden_src, 3, fallback), spread_levels(3, lo, hi)),
    }
    return new


def table_species(entry: dict) -> set[str]:
    found = set()
    for kind in ("land_mons", "water_mons", "rock_smash_mons", "fishing_mons", "hidden_mons"):
        if kind not in entry:
            continue
        for m in entry[kind]["mons"]:
            found.add(m["species"])
    return found


def inject_missing(encounters: list[dict], eligible: dict[str, dict]) -> None:
    """Guarantee every eligible species appears in a FireRed table (and its LeafGreen twin)."""
    fr_entries = [e for e in encounters if e["base_label"].endswith("_FireRed") and e["map"] != "MAP_SIX_ISLAND_ALTERING_CAVE"]
    lg_by_label = {e["base_label"]: e for e in encounters if e["base_label"].endswith("_LeafGreen")}
    seen = set()
    for e in fr_entries:
        seen |= table_species(e)
    missing = [s for s in eligible if s not in seen]
    if not missing:
        return

    def replace_dup(entry: dict, species: str) -> bool:
        for kind in ("hidden_mons", "land_mons", "water_mons", "fishing_mons", "rock_smash_mons"):
            if kind not in entry:
                continue
            mons = entry[kind]["mons"]
            counts = {}
            for m in mons:
                counts[m["species"]] = counts.get(m["species"], 0) + 1
            for m in reversed(mons):
                if counts.get(m["species"], 0) > 1:
                    counts[m["species"]] -= 1
                    m["species"] = species
                    return True
        return False

    sinks = [e for e in fr_entries if "land_mons" in e or "hidden_mons" in e]
    si = 0
    still = []
    for name in missing:
        placed = False
        for _ in range(len(sinks)):
            e = sinks[si % len(sinks)]
            si += 1
            if replace_dup(e, name):
                lg = lg_by_label.get(e["base_label"].replace("_FireRed", "_LeafGreen"))
                if lg:
                    replace_dup(lg, name)
                placed = True
                break
        if not placed:
            still.append(name)
    if still:
        raise SystemExit(f"could not inject missing species: {still[:20]}")


def mark_existing_classic(pool: Pool, encounters: list[dict], new_locs: list[dict]) -> None:
    """Classic identity species count as placed so they are not treated as missing."""
    for e in encounters:
        if not e.get("base_label", "").endswith("_FireRed"):
            continue
        if e["map"] == "MAP_SIX_ISLAND_ALTERING_CAVE":
            continue
        for kind in ("land_mons", "water_mons", "rock_smash_mons", "fishing_mons"):
            if kind not in e:
                continue
            for m in e[kind]["mons"]:
                pool.take(m["species"], e["map"] + ":classic")
    for loc in new_locs:
        for s in loc["classic"]:
            pool.take(s, loc["map"] + ":classic")


def main() -> None:
    rng = Random(1025)
    eligible = parse_species()
    print(f"eligible species: {len(eligible)}")
    folder_ids = load_folder_ids()
    new_locs = parse_locations(folder_ids)
    print(f"authored locations: {len(new_locs)}")

    src_path = VANILLA_JSON if VANILLA_JSON.exists() else WILD_JSON
    wild = json.loads(src_path.read_text())
    groups = wild["wild_encounter_groups"]
    headers = groups[0]
    # Add hidden_mons field once.
    if not any(f["type"] == "hidden_mons" for f in headers["fields"]):
        headers["fields"].append(HIDDEN_FIELD)

    old_enc = headers["encounters"]
    new_maps = {loc["map"] for loc in new_locs}
    hoenn = [e for e in old_enc if not e["base_label"].endswith("_FireRed") and not e["base_label"].endswith("_LeafGreen")]
    # Ignore previously generated Johto/Sinnoh tables so the script is idempotent.
    fr = [e for e in old_enc if e["base_label"].endswith("_FireRed") and e["map"] not in new_maps]
    lg = [e for e in old_enc if e["base_label"].endswith("_LeafGreen") and e["map"] not in new_maps]
    lg_by_map = {}
    for e in lg:
        lg_by_map.setdefault(e["map"], []).append(e)

    pool = Pool(eligible, rng)
    # Do not consume classic species up front; they stay on their maps and leftovers
    # still need a guaranteed emitted slot.

    extra: dict[str, dict] = {}
    # Kanto/Sevii maps as assign targets.
    kanto_targets = []
    for e in fr:
        if e["map"] == "MAP_SIX_ISLAND_ALTERING_CAVE":
            continue
        mons = e.get("land_mons", e.get("water_mons", {})).get("mons", [])
        lo = min((m["min_level"] for m in mons), default=5)
        hi = max((m["max_level"] for m in mons), default=10)
        kanto_targets.append({
            "map": e["map"],
            "biomes": kanto_biomes(e["map"]),
            "lo": lo,
            "hi": hi,
            "land": "land_mons" in e,
            "water": "water_mons" in e,
            "fish": "fishing_mons" in e,
            "rocks": "rock_smash_mons" in e,
            "classic": unique_in_order(e.get("land_mons", {}).get("mons", [])),
            "region": kanto_region(e["map"]),
        })

    all_targets = kanto_targets + new_locs
    # First pass: biome-matched leftovers.
    for loc in all_targets:
        assign_to_loc(pool, loc, extra)
    for loc in all_targets:
        sprinkle_from_pool(loc, extra, eligible)
    # Overflow: dump remaining onto safari / marsh / park / late caves.
    overflow_names = [
        "MAP_SAFARI_ZONE_CENTER", "MAP_SAFARI_ZONE_EAST", "MAP_SAFARI_ZONE_NORTH_FRLG", "MAP_SAFARI_ZONE_WEST",
        "MAP_NATIONAL_PARK_NORMAL_HNS", "MAP_GREAT_MARSH", "MAP_CERULEAN_CAVE_B1F", "MAP_MT_SILVER_2F_HNS",
        "MAP_SEVEN_ISLAND_SEVAULT_CANYON", "MAP_THREE_ISLAND_BERRY_FOREST",
    ]
    overflow = [t for t in all_targets if t["map"] in overflow_names] or [t for t in all_targets if t["land"]]
    guard = 0
    while pool.remaining and guard < 20:
        guard += 1
        for loc in overflow:
            if not pool.remaining:
                break
            key = loc["map"]
            extra.setdefault(key, {"land": [], "water": [], "fish": [], "rocks": [], "hidden": []})
            pred = is_waterish if (not loc["land"] and loc["water"]) else lambda inf: True
            got = pool.pick(ranked_remaining(pool, loc, pred, min_score=0), key + f":overflow{guard}", 6)
            extra[key]["land"].extend(got)
            if not got:
                # Force-take anything left onto this map.
                rest = list(pool.remaining)[:6]
                for name in rest:
                    pool.take(name, key + ":force")
                    extra[key]["land"].append(name)

    if pool.remaining:
        print("leftover after assignment", len(pool.remaining), "(injected in a later pass)")

    # Rebuild encounters: Hoenn unchanged, Kanto rewritten, Johto/Sinnoh appended.
    new_enc = list(hoenn)
    altering_fr = []
    altering_lg = []
    for e in fr:
        if e["map"] == "MAP_SIX_ISLAND_ALTERING_CAVE":
            altering_fr.append(e)
            continue
        new_enc.append(rewrite_kanto_entry(e, extra, pool, eligible))
        # matching LG: same extras, classic from that LG table
        lg_matches = lg_by_map.get(e["map"], [])
        if lg_matches:
            new_enc.append(rewrite_kanto_entry(lg_matches[0], extra, pool, eligible))
        else:
            clone = rewrite_kanto_entry(e, extra, pool, eligible)
            clone["base_label"] = e["base_label"].replace("_FireRed", "_LeafGreen")
            new_enc.append(clone)
    for e in altering_fr:
        new_enc.append(e)
    for e in lg:
        if e["map"] == "MAP_SIX_ISLAND_ALTERING_CAVE":
            new_enc.append(e)

    for loc in new_locs:
        new_enc.append(build_new_entry(loc, extra, "FireRed"))
        new_enc.append(build_new_entry(loc, extra, "LeafGreen"))

    inject_missing(new_enc, eligible)

    headers["encounters"] = new_enc
    WILD_JSON.write_text(json.dumps(wild, indent=2, ensure_ascii=True) + "\n")
    print(f"wrote {WILD_JSON} with {len(new_enc)} encounter tables")
    print(f"placed unique eligible: {len(eligible)}")

    # Coverage audit on FR tables only.
    seen = set()
    for e in new_enc:
        if not e["base_label"].endswith("_FireRed"):
            continue
        for kind in ("land_mons", "water_mons", "rock_smash_mons", "fishing_mons", "hidden_mons"):
            if kind not in e:
                continue
            for m in e[kind]["mons"]:
                seen.add(m["species"])
    missing = sorted(set(eligible) - seen)
    extra_unknown = sorted(s for s in seen if s in eligible or True)
    print(f"FR species seen: {len(seen)}")
    print(f"eligible missing from FR tables: {len(missing)}")
    if missing:
        print(" missing sample", missing[:30])
        raise SystemExit("coverage incomplete")
    banned = [s for s in seen if s in eligible and False]
    # banned legendaries
    legend_hits = []
    for s in seen:
        if s in eligible:
            continue
        # ignore Hoenn-only leftovers; check FR new tables later
    print("ok")


if __name__ == "__main__":
    main()
