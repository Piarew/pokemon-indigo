#!/usr/bin/env python3
"""Import Johto (HnS, including Kanto) and Sinnoh maps into an Emerald build.

Sources (outside this repo):
  /home/piarew/pokehns-expansion
  /home/piarew/sinnoh-pokeemerald-expansion

Rewrite for pokeemerald (`make`, MAP_VERSION=emerald):
  map.json region REGION_HOENN
  layout_version emerald
  Emerald 2-byte metatile attributes (no FRLG 32-bit packing)
  HnS 640-metatile primaries flagged usesFrlgCounts
  Sinnoh tilesets that would overwrite stock Emerald tilesets are namespaced
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HNS = Path("/home/piarew/pokehns-expansion")
SINNOH = Path("/home/piarew/sinnoh-pokeemerald-expansion")

SKIP_GROUP_SUBSTR = ("Alola", "Sinjoh", "IndoorDynamic", "BattleTent")
SKIP_MAP_SUBSTR = (
    "BattleTent",
    "TrainerHill",
    "ContestHall",
    "LilycoveCity_Contest",
    "UnusedContest",
    "TradeCenter",
    "BattleColosseum",
    "TestMap",
    "Trees_hns",
    "Saffron_Temp",
    "SouthernIsland",
    "FarawayIsland",
    "BirthIsland",
    "BattleFrontier",
)
SINNOH_GROUP_KEYS = [
    "gMapGroup_SinnohTownsRoutes",
    "gMapGroup_SpecialAreasSinnoh",
    "gMapGroup_DungeonsSinnoh",
    "gMapGroup_IndoorSinnoh",
    "gMapGroup_IndoorTwinleaf",
    "gMapGroup_IndoorSandgem",
    "gMapGroup_IndoorJubilife",
    "gMapGroup_IndoorOreburgh",
    "gMapGroup_IndoorFloaroma",
    "gMapGroup_IndoorEterna",
    "gMapGroup_IndoorHearthome",
    "gMapGroup_IndoorSolaceon",
    "gMapGroup_IndoorVeilstone",
    "gMapGroup_IndoorPastoria",
    "gMapGroup_IndoorCelestic",
    "gMapGroup_IndoorCanalave",
    "gMapGroup_IndoorSnowpoint",
    "gMapGroup_IndoorSunyshore",
    "gMapGroup_IndoorPokemonLeague",
    "gMapGroup_IndoorFightArea",
    "gMapGroup_IndoorSurvivalArea",
    "gMapGroup_IndoorResortArea",
]
SINNOH_GROUP_PARENT_MAPSEC = {
    "gMapGroup_IndoorTwinleaf": "MAPSEC_TWINLEAF_TOWN",
    "gMapGroup_IndoorSandgem": "MAPSEC_SANDGEM_TOWN",
    "gMapGroup_IndoorJubilife": "MAPSEC_JUBILIFE_CITY",
    "gMapGroup_IndoorOreburgh": "MAPSEC_OREBURGH_CITY",
    "gMapGroup_IndoorFloaroma": "MAPSEC_FLOAROMA_TOWN",
    "gMapGroup_IndoorEterna": "MAPSEC_ETERNA_CITY",
    "gMapGroup_IndoorHearthome": "MAPSEC_HEARTHOME_CITY",
    "gMapGroup_IndoorSolaceon": "MAPSEC_SOLACEON_TOWN",
    "gMapGroup_IndoorVeilstone": "MAPSEC_VEILSTONE_CITY",
    "gMapGroup_IndoorPastoria": "MAPSEC_PASTORIA_CITY",
    "gMapGroup_IndoorCelestic": "MAPSEC_CELESTIC_TOWN",
    "gMapGroup_IndoorCanalave": "MAPSEC_CANALAVE_CITY",
    "gMapGroup_IndoorSnowpoint": "MAPSEC_SNOWPOINT_CITY",
    "gMapGroup_IndoorSunyshore": "MAPSEC_SUNYSHORE_CITY",
    "gMapGroup_IndoorPokemonLeague": "MAPSEC_POKEMON_LEAGUE",
    "gMapGroup_IndoorFightArea": "MAPSEC_FIGHT_AREA",
    "gMapGroup_IndoorSurvivalArea": "MAPSEC_SURVIVAL_AREA",
    "gMapGroup_IndoorResortArea": "MAPSEC_RESORT_AREA",
}
SINNOH_OUTDOOR_GROUPS = {
    "gMapGroup_SinnohTownsRoutes",
    "gMapGroup_SpecialAreasSinnoh",
    "gMapGroup_DungeonsSinnoh",
}
MAPSEC_REMAP = {
    "MAPSEC_VICTORY_ROAD_HNS": "MAPSEC_VICTORY_ROAD",
    "MAPSEC_POKEMON_MANSION": "MAPSEC_SINNOH_POKEMON_MANSION",
}
KEEP_SCRIPTS = {
    "EventScript_CutTree",
    "EventScript_RockSmash",
    "EventScript_StrengthBoulder",
    "BerryTreeScript",
    "0x0",
    "0",
    "NULL",
}
GFX_MAP = {
    "OBJ_EVENT_GFX_FAT_MAN_HNS": "OBJ_EVENT_GFX_FAT_MAN",
    "OBJ_EVENT_GFX_LASS_HNS": "OBJ_EVENT_GFX_LASS",
    "OBJ_EVENT_GFX_SILVER_HNS": "OBJ_EVENT_GFX_RIVAL_BRENDAN_NORMAL",
    "OBJ_EVENT_GFX_MOM_HNS": "OBJ_EVENT_GFX_WOMAN_2",
    "OBJ_EVENT_GFX_WOMAN_1_HNS": "OBJ_EVENT_GFX_WOMAN_1",
    "OBJ_EVENT_GFX_WOMAN_2_HNS": "OBJ_EVENT_GFX_WOMAN_2",
    "OBJ_EVENT_GFX_WOMAN_3_HNS": "OBJ_EVENT_GFX_WOMAN_3",
    "OBJ_EVENT_GFX_LITTLE_BOY_HNS": "OBJ_EVENT_GFX_LITTLE_BOY",
    "OBJ_EVENT_GFX_SCIENTIST_M_HNS": "OBJ_EVENT_GFX_SCIENTIST_1",
    "OBJ_EVENT_GFX_SCIENTIST_F_HNS": "OBJ_EVENT_GFX_SCIENTIST_1",
    "OBJ_EVENT_GFX_ELM_HNS": "OBJ_EVENT_GFX_PROF_BIRCH",
    "OBJ_EVENT_GFX_OFFICER_HNS": "OBJ_EVENT_GFX_POLICEMAN",
    "OBJ_EVENT_GFX_OLD_MAN_HNS": "OBJ_EVENT_GFX_OLD_MAN",
    "OBJ_EVENT_GFX_OLD_MAN_2_HNS": "OBJ_EVENT_GFX_EXPERT_M",
    "OBJ_EVENT_GFX_YOUNGSTER_HNS": "OBJ_EVENT_GFX_YOUNGSTER",
    "OBJ_EVENT_GFX_BOY_2_HNS": "OBJ_EVENT_GFX_BOY_2",
    "OBJ_EVENT_GFX_COOLTRAINER_F_HNS": "OBJ_EVENT_GFX_WOMAN_5",
    "OBJ_EVENT_GFX_COOLTRAINER_M_HNS": "OBJ_EVENT_GFX_MAN_3",
    "OBJ_EVENT_GFX_ROCKER_HNS": "OBJ_EVENT_GFX_MANIAC",
    "OBJ_EVENT_GFX_PSYCHIC_M_HNS": "OBJ_EVENT_GFX_PSYCHIC_M",
    "OBJ_EVENT_GFX_FISHERMAN_HNS": "OBJ_EVENT_GFX_FISHERMAN",
    "OBJ_EVENT_GFX_ITEM_BALL_HNS": "OBJ_EVENT_GFX_ITEM_BALL",
    "OBJ_EVENT_GFX_CUTTABLE_TREE_HNS": "OBJ_EVENT_GFX_CUTTABLE_TREE",
    "OBJ_EVENT_GFX_BREAKABLE_ROCK_HNS": "OBJ_EVENT_GFX_BREAKABLE_ROCK",
    "OBJ_EVENT_GFX_SMALL_LIGHT_HNS": "OBJ_EVENT_GFX_LIGHT_SPRITE",
    "OBJ_EVENT_GFX_ARCHER_HNS": "OBJ_EVENT_GFX_AQUA_MEMBER_M",
    "OBJ_EVENT_GFX_ROCKET_M_HNS": "OBJ_EVENT_GFX_AQUA_MEMBER_M",
    "OBJ_EVENT_GFX_ROCKET_F_HNS": "OBJ_EVENT_GFX_AQUA_MEMBER_F",
    "OBJ_EVENT_GFX_HIKER_HNS": "OBJ_EVENT_GFX_HIKER",
    "OBJ_EVENT_GFX_CAMPER_HNS": "OBJ_EVENT_GFX_CAMPER",
    "OBJ_EVENT_GFX_PICNICKER_HNS": "OBJ_EVENT_GFX_PICNICKER",
    "OBJ_EVENT_GFX_SWIMMER_F_HNS": "OBJ_EVENT_GFX_SWIMMER_F",
    "OBJ_EVENT_GFX_SWIMMER_M_HNS": "OBJ_EVENT_GFX_SWIMMER_M",
    "OBJ_EVENT_GFX_SUPER_NERD_HNS": "OBJ_EVENT_GFX_MANIAC",
    "OBJ_EVENT_GFX_BATTLE_GIRL_HNS": "OBJ_EVENT_GFX_WOMAN_5",
    "OBJ_EVENT_GFX_TWIN_HNS": "OBJ_EVENT_GFX_TWIN",
    "OBJ_EVENT_GFX_WHIRLPOOL_HNS": "OBJ_EVENT_GFX_LIGHT_SPRITE",
    "OBJ_EVENT_GFX_NO_TAIL_SLOWPOKE_HNS": "OBJ_EVENT_GFX_ITEM_BALL",
    "OBJ_EVENT_GFX_SAGE_HNS": "OBJ_EVENT_GFX_EXPERT_M",
    "OBJ_EVENT_GFX_SAILOR_HNS": "OBJ_EVENT_GFX_SAILOR",
    "OBJ_EVENT_GFX_BALDING_MAN_HNS": "OBJ_EVENT_GFX_FAT_MAN",
    "OBJ_EVENT_GFX_BLACK_BELT_HNS": "OBJ_EVENT_GFX_BLACK_BELT",
    "OBJ_EVENT_GFX_BEAUTY_HNS": "OBJ_EVENT_GFX_BEAUTY",
    "OBJ_EVENT_GFX_BUG_CATCHER_HNS": "OBJ_EVENT_GFX_BUG_CATCHER",
    "OBJ_EVENT_GFX_EUSINE_HNS": "OBJ_EVENT_GFX_GENTLEMAN",
    "OBJ_EVENT_GFX_ENGINEER_HNS": "OBJ_EVENT_GFX_CAMPER",
    "OBJ_EVENT_GFX_WORKER_M_HNS": "OBJ_EVENT_GFX_CAMPER",
    "OBJ_EVENT_GFX_WORKER_F_HNS": "OBJ_EVENT_GFX_PICNICKER",
    "OBJ_EVENT_GFX_KIMONO_HNS": "OBJ_EVENT_GFX_BEAUTY",
    "OBJ_EVENT_GFX_KURT_HNS": "OBJ_EVENT_GFX_EXPERT_M",
    "OBJ_EVENT_GFX_ATTENDANT_F_HNS": "OBJ_EVENT_GFX_LINK_RECEPTIONIST",
    "OBJ_EVENT_GFX_FIREBREATHER_HNS": "OBJ_EVENT_GFX_HIKER",
    "OBJ_EVENT_GFX_JUGGLER_HNS": "OBJ_EVENT_GFX_MANIAC",
    "OBJ_EVENT_GFX_GENTLEMAN_HNS": "OBJ_EVENT_GFX_GENTLEMAN",
    "OBJ_EVENT_GFX_LEGENDARY_SHADOW_HNS": "OBJ_EVENT_GFX_LIGHT_SPRITE",
    "OBJ_EVENT_GFX_LANCE_HNS": "OBJ_EVENT_GFX_DRAKE",
    "OBJ_EVENT_GFX_SHINY_GYARADOS_HNS": "OBJ_EVENT_GFX_GYARADOS_FRONT",
    "OBJ_EVENT_GFX_PRYCE_HNS": "OBJ_EVENT_GFX_EXPERT_M",
    "OBJ_EVENT_GFX_NURSE_HNS": "OBJ_EVENT_GFX_NURSE",
    "OBJ_EVENT_GFX_NURSE_CHANSEY_HNS": "OBJ_EVENT_GFX_CHANSEY",
    "OBJ_EVENT_GFX_MART_EMPLOYEE_HNS": "OBJ_EVENT_GFX_MART_EMPLOYEE",
    "OBJ_EVENT_GFX_OLD_WOMAN_HNS": "OBJ_EVENT_GFX_OLD_WOMAN",
    "OBJ_EVENT_GFX_PUSHABLE_BOULDER_HNS": "OBJ_EVENT_GFX_PUSHABLE_BOULDER",
    "OBJ_EVENT_GFX_TOWER_BEAM_HNS": "OBJ_EVENT_GFX_LIGHT_SPRITE",
    "OBJ_EVENT_GFX_GYM_GUY_HNS": "OBJ_EVENT_GFX_SCOTT",
    "OBJ_EVENT_GFX_GIOVANNI_HNS": "OBJ_EVENT_GFX_MAXIE",
    "OBJ_EVENT_GFX_BILL_HNS": "OBJ_EVENT_GFX_SCOTT",
    "OBJ_EVENT_GFX_LITTLE_GIRL_HNS": "OBJ_EVENT_GFX_LITTLE_GIRL",
    "OBJ_EVENT_GFX_CHANNELER_HNS": "OBJ_EVENT_GFX_HEX_MANIAC",
    "OBJ_EVENT_GFX_CAPTAIN_HNS": "OBJ_EVENT_GFX_SAILOR",
    "OBJ_EVENT_GFX_CHEF_HNS": "OBJ_EVENT_GFX_COOK",
    "OBJ_EVENT_GFX_BIKER_HNS": "OBJ_EVENT_GFX_RUNNING_TRIATHLETE_M",
    "OBJ_EVENT_GFX_SINNOH_MIDDLE_AGED_WOMAN": "OBJ_EVENT_GFX_WOMAN_2",
    "OBJ_EVENT_GFX_SINNOH_COLLECTOR": "OBJ_EVENT_GFX_FAT_MAN",
    "OBJ_EVENT_GFX_SINNOH_GUITARIST": "OBJ_EVENT_GFX_MANIAC",
    "OBJ_EVENT_GFX_SINNOH_BARRY": "OBJ_EVENT_GFX_RIVAL_BRENDAN_NORMAL",
    "OBJ_EVENT_GFX_SINNOH_BREEDER_M": "OBJ_EVENT_GFX_YOUNGSTER",
    "OBJ_EVENT_GFX_SINNOH_BREEDER_F": "OBJ_EVENT_GFX_LASS",
    "OBJ_EVENT_GFX_SINNOH_LASS": "OBJ_EVENT_GFX_LASS",
    "OBJ_EVENT_GFX_SINNOH_ROWAN": "OBJ_EVENT_GFX_PROF_BIRCH",
    "OBJ_EVENT_GFX_SINNOH_POKEFAN_F": "OBJ_EVENT_GFX_POKEFAN_F",
    "OBJ_EVENT_GFX_SINNOH_POKEFAN_M": "OBJ_EVENT_GFX_POKEFAN_M",
    "OBJ_EVENT_GFX_SINNOH_HIKER": "OBJ_EVENT_GFX_HIKER",
    "OBJ_EVENT_GFX_SINNOH_BUG_CATCHER": "OBJ_EVENT_GFX_BUG_CATCHER",
    "OBJ_EVENT_GFX_SINNOH_ACE_TRAINER_M": "OBJ_EVENT_GFX_MAN_3",
    "OBJ_EVENT_GFX_SINNOH_ACE_TRAINER_F": "OBJ_EVENT_GFX_WOMAN_5",
    "OBJ_EVENT_GFX_SINNOH_BEAUTY": "OBJ_EVENT_GFX_BEAUTY",
    "OBJ_EVENT_GFX_SINNOH_GENTLEMAN": "OBJ_EVENT_GFX_GENTLEMAN",
    "OBJ_EVENT_GFX_SINNOH_POLICEMAN": "OBJ_EVENT_GFX_POLICEMAN",
    "OBJ_EVENT_GFX_SINNOH_SCIENTIST_M": "OBJ_EVENT_GFX_SCIENTIST_1",
    "OBJ_EVENT_GFX_SINNOH_SCIENTIST_F": "OBJ_EVENT_GFX_SCIENTIST_1",
    "OBJ_EVENT_GFX_SINNOH_WORKER": "OBJ_EVENT_GFX_CAMPER",
    "OBJ_EVENT_GFX_SINNOH_CYNTHIA": "OBJ_EVENT_GFX_LEAF",
    "OBJ_EVENT_GFX_SINNOH_NURSE": "OBJ_EVENT_GFX_NURSE",
    "OBJ_EVENT_GFX_SINNOH_ICE_ROCK": "OBJ_EVENT_GFX_BREAKABLE_ROCK",
    "OBJ_EVENT_GFX_SINNOH_MOSS_ROCK": "OBJ_EVENT_GFX_BREAKABLE_ROCK",
}
MOVEMENT_MAP = {"MOVEMENT_TYPE_TOWER_BEAM": "MOVEMENT_TYPE_NONE"}
WEATHER_MAP = {"WEATHER_LEAVES": "WEATHER_NONE"}
OUTDOOR_TREE_PRIMARIES = {
    "gTileset_Kanto_General_Hns",
    "gTileset_Johto_General_Hns",
    "gTileset_Johto_South_Hns",
    "gTileset_Johto_NorthEast_Hns",
    "gTileset_Johto_NorthWest_Hns",
}
OUTDOOR_TREE_METATILES = frozenset(range(18, 40)) | {121}

VALID_GFX: set[str] = set()
VALID_MUSIC: set[str] = set()
VALID_MOVEMENT: set[str] = set()
VALID_MAPSECS: set[str] = set()
IMPORTED_MAP_IDS: set[str] = set()
TILESET_SNAPSHOT: dict[str, str] = {}
EXISTING_TILESET_SYMBOLS: set[str] = set()


def load_constants() -> None:
    gfx_text = (ROOT / "include/constants/event_objects.h").read_text()
    VALID_GFX.update(re.findall(r"OBJ_EVENT_GFX_[A-Z0-9_]+", gfx_text))
    songs = (ROOT / "include/constants/songs.h").read_text()
    VALID_MUSIC.update(re.findall(r"#define (MUS_[A-Z0-9_]+)\s", songs))
    movement = (ROOT / "include/constants/event_object_movement.h").read_text()
    VALID_MOVEMENT.update(re.findall(r"#define (MOVEMENT_TYPE_[A-Z0-9_]+)\s", movement))
    headers = (ROOT / "src/data/tilesets/headers.h").read_text()
    EXISTING_TILESET_SYMBOLS.update(re.findall(r"const struct Tileset (gTileset_\w+) =", headers))
    refresh_mapsecs()


def refresh_mapsecs() -> None:
    data = json.loads((ROOT / "src/data/region_map/region_map_sections.json").read_text())
    VALID_MAPSECS.clear()
    VALID_MAPSECS.update(entry["id"] for entry in data["map_sections"])
    VALID_MAPSECS.update({"MAPSEC_NONE", "MAPSEC_COUNT", "MAPSEC_KANTO_VICTORY_ROAD"})


def skip_map(folder: str) -> bool:
    return any(part in folder for part in SKIP_MAP_SUBSTR)


def hns_groups() -> dict[str, list[str]]:
    src = json.loads((HNS / "data/maps/map_groups.json").read_text())
    groups: dict[str, list[str]] = {}
    for name in src["group_order"]:
        if not name.endswith("_Hns"):
            continue
        if any(part in name for part in SKIP_GROUP_SUBSTR):
            continue
        folders = [folder for folder in src[name] if not skip_map(folder)]
        if folders:
            groups[name] = folders
    return groups


def sinnoh_groups() -> dict[str, list[str]]:
    src = json.loads((SINNOH / "data/maps/map_groups.json").read_text())
    groups: dict[str, list[str]] = {}
    for name in SINNOH_GROUP_KEYS:
        folders = list(dict.fromkeys(src[name]))
        groups[name] = folders
    return groups


def flatten_maps(groups: dict[str, list[str]]) -> list[str]:
    seen: set[str] = set()
    maps: list[str] = []
    for folders in groups.values():
        for folder in folders:
            if folder not in seen:
                seen.add(folder)
                maps.append(folder)
    return maps


def parse_tileset_folders(src_root: Path) -> dict[str, tuple[str, str]]:
    text = (src_root / "src/data/tilesets/graphics.h").read_text()
    pat = re.compile(
        r'gTilesetTiles_(\w+)\[\] = INC(?:GFX|BIN)_U32\("data/tilesets/(primary|secondary)/([^"/]+)/'
    )
    return {match.group(1): (match.group(2), match.group(3)) for match in pat.finditer(text)}


def stem_to_snake(stem: str) -> str:
    snake = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", stem)
    snake = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", snake)
    return snake.lower()


def resolve_tileset(symbol: str, src_root: Path, namespace: str | None) -> tuple[str, str, str, str, bool]:
    if symbol in TILESET_SNAPSHOT:
        dest_symbol = TILESET_SNAPSHOT[symbol]
        stem = dest_symbol[len("gTileset_") :]
        folders = parse_tileset_folders(src_root)
        src_stem = symbol[len("gTileset_") :]
        if src_stem in folders:
            kind, src_folder = folders[src_stem]
        else:
            kind = "secondary"
            src_folder = stem_to_snake(src_stem)
        dest_folder = stem_to_snake(stem)
        return kind, src_folder, dest_folder, dest_symbol, kind == "secondary"
    if not symbol.startswith("gTileset_"):
        raise SystemExit(f"unexpected tileset {symbol}")
    stem = symbol[len("gTileset_") :]
    folders = parse_tileset_folders(src_root)
    if stem in folders:
        kind, src_folder = folders[stem]
    else:
        kind = "primary" if stem in {"General", "Building"} else "secondary"
        src_folder = stem_to_snake(stem)
    dest_symbol = symbol
    dest_folder = src_folder
    if symbol in EXISTING_TILESET_SYMBOLS:
        prefix = namespace or "Hns"
        dest_symbol = f"gTileset_{prefix}_{stem}"
        dest_folder = f"{prefix.lower()}_{src_folder}"
    TILESET_SNAPSHOT[symbol] = dest_symbol
    return kind, src_folder, dest_folder, dest_symbol, kind == "secondary"


def rewrite_tileset_symbol(symbol: str | None, src_root: Path, namespace: str | None) -> str | None:
    if not symbol:
        return symbol
    return resolve_tileset(symbol, src_root, namespace)[3]


def pal_files(kind: str, folder: str) -> list[str]:
    pals = sorted((ROOT / "data/tilesets" / kind / folder / "palettes").glob("*.pal"))
    names = [p.name for p in pals if re.fullmatch(r"\d{2}\.pal", p.name)]
    return names[:16]


def copy_tileset(src_root: Path, kind: str, src_folder: str, dest_folder: str) -> None:
    src = src_root / "data/tilesets" / kind / src_folder
    dest = ROOT / "data/tilesets" / kind / dest_folder
    if not src.exists():
        raise SystemExit(f"missing tileset {src}")
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest, ignore=shutil.ignore_patterns("*.pla", "anim"))


def gfx_symbol(src_id: str) -> str | None:
    if src_id.startswith(("OBJ_EVENT_GFX_MON_BASE", "OBJ_EVENT_GFX_VAR_", "OBJ_EVENT_GFX_SINNOH_MON_")):
        return None
    mapped = GFX_MAP.get(src_id, src_id)
    if mapped in VALID_GFX:
        return mapped
    if "CUTTABLE_TREE" in src_id:
        return "OBJ_EVENT_GFX_CUTTABLE_TREE"
    if "BREAKABLE_ROCK" in src_id:
        return "OBJ_EVENT_GFX_BREAKABLE_ROCK"
    if "PUSHABLE_BOULDER" in src_id:
        return "OBJ_EVENT_GFX_PUSHABLE_BOULDER"
    if "ITEM_BALL" in src_id or src_id.endswith("_POKE_BALL"):
        return "OBJ_EVENT_GFX_ITEM_BALL"
    if "NURSE" in src_id:
        return "OBJ_EVENT_GFX_NURSE"
    if "BERRY_TREE" in src_id:
        return "OBJ_EVENT_GFX_BERRY_TREE"
    return "OBJ_EVENT_GFX_NINJA_BOY"


def stub_music(song: str) -> str:
    if song in VALID_MUSIC and not song.startswith(("MUS_HG_", "MUS_DPP_")):
        return song
    if "GYM" in song:
        pick = "MUS_GYM"
    elif "CENTER" in song or "MART" in song:
        pick = "MUS_POKE_CENTER"
    elif "LAB" in song:
        pick = "MUS_BIRCH_LAB"
    elif any(part in song for part in ("CAVE", "TOWER", "WELL", "PATH", "DEN", "RUIN", "FOREST", "PARK", "MINE", "GATE", "TEMPLE", "LAKE", "HIDEOUT")):
        pick = "MUS_CAVE_OF_ORIGIN"
    elif "ROUTE" in song:
        pick = "MUS_ROUTE101"
    elif "GAME_CORNER" in song or "CASINO" in song:
        pick = "MUS_GAME_CORNER"
    elif "VICTORY" in song or "LEAGUE" in song:
        pick = "MUS_VICTORY_ROAD"
    elif "SURF" in song:
        pick = "MUS_SURF"
    else:
        pick = "MUS_LITTLEROOT"
    return pick if pick in VALID_MUSIC else "MUS_LITTLEROOT"


def rewrite_object(obj: dict) -> dict | None:
    gfx = gfx_symbol(obj.get("graphics_id", ""))
    if gfx is None:
        return None
    flag = obj.get("flag", "0")
    if isinstance(flag, str) and flag.startswith("FLAG_") and flag not in {"FLAG_TEMP_1", "FLAG_TEMP_11"}:
        flag = "0"
    script = obj.get("script", "0x0")
    if script in (None, "NULL", "0"):
        script = "0x0"
    if gfx == "OBJ_EVENT_GFX_BERRY_TREE":
        script = "0x0"
    movement = obj.get("movement_type", "MOVEMENT_TYPE_NONE")
    movement = MOVEMENT_MAP.get(movement, movement)
    if movement not in VALID_MOVEMENT:
        movement = "MOVEMENT_TYPE_NONE"
    return {
        "type": "object",
        "graphics_id": gfx,
        "x": obj["x"],
        "y": obj["y"],
        "elevation": obj.get("elevation", 0),
        "movement_type": movement,
        "movement_range_x": obj.get("movement_range_x", 0),
        "movement_range_y": obj.get("movement_range_y", 0),
        "trainer_type": "TRAINER_TYPE_NONE",
        "trainer_sight_or_berry_tree_id": "0",
        "script": script,
        "flag": flag if flag is not None else "0",
    }


def rewrite_connections(connections: list | None) -> list | None:
    if not connections:
        return None
    out = [dict(conn) for conn in connections if conn.get("map") in IMPORTED_MAP_IDS]
    return out or None


def rewrite_warps(warps: list | None) -> list:
    out = []
    for warp in warps or []:
        dest = warp.get("dest_map")
        if dest not in IMPORTED_MAP_IDS:
            continue
        rewritten = dict(warp)
        rewritten.pop("local_id", None)
        out.append(rewritten)
    return out


def resolve_mapsec(folder: str, src_mapsec: str, group: str) -> str:
    mapsec = MAPSEC_REMAP.get(src_mapsec, src_mapsec)
    if mapsec in VALID_MAPSECS:
        return mapsec
    if group in SINNOH_GROUP_PARENT_MAPSEC:
        parent = SINNOH_GROUP_PARENT_MAPSEC[group]
        if parent in VALID_MAPSECS:
            return parent
    return "MAPSEC_NONE"


def layouts_by_id(src_root: Path) -> dict[str, dict]:
    data = json.loads((src_root / "data/layouts/layouts.json").read_text())
    return {entry["id"]: entry for entry in data["layouts"] if entry.get("id")}


def layouts_by_border(src_root: Path) -> dict[str, dict]:
    data = json.loads((src_root / "data/layouts/layouts.json").read_text())
    return {entry.get("border_filepath"): entry for entry in data["layouts"] if entry.get("border_filepath")}


def load_imported_ids(src_root: Path, folders: list[str]) -> None:
    for folder in folders:
        src = json.loads((src_root / "data/maps" / folder / "map.json").read_text())
        IMPORTED_MAP_IDS.add(src["id"])


def is_indoor(map_type: str, group: str) -> bool:
    if group.startswith("gMapGroup_Indoor"):
        return True
    return map_type in ("MAP_TYPE_NONE", "MAP_TYPE_INDOOR")


def rewrite_map(src_root: Path, folder: str, group: str, namespace: str | None) -> dict:
    src = json.loads((src_root / "data/maps" / folder / "map.json").read_text())
    map_type = src.get("map_type", "MAP_TYPE_INDOOR")
    indoor = is_indoor(map_type, group)
    if indoor:
        map_type = "MAP_TYPE_INDOOR"
    elif map_type == "MAP_TYPE_NONE":
        map_type = "MAP_TYPE_ROUTE"
    objects = []
    for obj in src.get("object_events") or []:
        rewritten = rewrite_object(obj)
        if rewritten:
            objects.append(rewritten)
        if len(objects) >= 16:
            break
    weather = src.get("weather", "WEATHER_NONE")
    weather = WEATHER_MAP.get(weather, weather)
    rewritten = {
        "id": src["id"],
        "name": src["name"],
        "layout": src["layout"],
        "music": stub_music(src.get("music", "MUS_LITTLEROOT")),
        "region": "REGION_HOENN",
        "region_map_section": resolve_mapsec(folder, src.get("region_map_section", "MAPSEC_NONE"), group),
        "requires_flash": src.get("requires_flash", False),
        "weather": weather,
        "map_type": map_type,
        "allow_cycling": src.get("allow_cycling", not indoor),
        "allow_escaping": src.get("allow_escaping", False),
        "allow_running": src.get("allow_running", True),
        "show_map_name": False if indoor else bool(src.get("show_map_name", True)),
        "battle_scene": src.get("battle_scene", "MAP_BATTLE_SCENE_NORMAL"),
        "connections": rewrite_connections(src.get("connections")),
        "object_events": objects,
        "warp_events": rewrite_warps(src.get("warp_events")),
        "coord_events": [],
        "bg_events": [
            {
                "type": "sign",
                "x": bg["x"],
                "y": bg["y"],
                "elevation": bg.get("elevation", 0),
                "player_facing_dir": bg.get("player_facing_dir", "BG_EVENT_PLAYER_FACING_ANY"),
                "script": bg.get("script") if bg.get("script") not in (None, "NULL") else "0x0",
            }
            for bg in src.get("bg_events") or []
            if bg.get("type") == "sign"
        ],
    }
    dest_dir = ROOT / "data/maps" / folder
    dest_dir.mkdir(parents=True, exist_ok=True)
    (dest_dir / "map.json").write_text(json.dumps(rewritten, indent=2) + "\n")
    (dest_dir / "scripts.inc").write_text(f"{src['name']}_MapScripts::\n\t.byte 0\n")
    return rewritten


def copy_layout(src_root: Path, folder: str, by_id: dict[str, dict], namespace: str | None) -> dict:
    src_map = json.loads((src_root / "data/maps" / folder / "map.json").read_text())
    layout = by_id.get(src_map["layout"])
    if layout is None:
        by_border = layouts_by_border(src_root)
        layout = by_border.get(f"data/layouts/{folder}/border.bin")
    if layout is None:
        raise SystemExit(f"No layout for {folder} ({src_map.get('layout')})")
    border = Path(layout["border_filepath"])
    src_dir = src_root / border.parent
    dest_dir = ROOT / border.parent
    dest_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_dir / "map.bin", dest_dir / "map.bin")
    shutil.copy2(src_dir / "border.bin", dest_dir / "border.bin")
    entry = dict(layout)
    entry.pop("game_version", None)
    entry["layout_version"] = "emerald"
    entry.pop("border_width", None)
    entry.pop("border_height", None)
    entry["primary_tileset"] = rewrite_tileset_symbol(entry.get("primary_tileset"), src_root, namespace)
    entry["secondary_tileset"] = rewrite_tileset_symbol(entry.get("secondary_tileset"), src_root, namespace)
    return entry


def collect_tilesets(src_root: Path, folders: list[str], by_id: dict[str, dict], namespace: str | None) -> list[tuple[str, str, str, str, bool]]:
    tilesets: list[tuple[str, str, str, str, bool]] = []
    seen: set[str] = set()
    for folder in folders:
        src_map = json.loads((src_root / "data/maps" / folder / "map.json").read_text())
        layout = by_id.get(src_map["layout"])
        if layout is None:
            layout = layouts_by_border(src_root).get(f"data/layouts/{folder}/border.bin")
        if layout is None:
            raise SystemExit(f"No layout for tilesets on {folder}")
        for key in ("primary_tileset", "secondary_tileset"):
            symbol = layout.get(key)
            if not symbol or symbol in seen:
                continue
            seen.add(symbol)
            tilesets.append(resolve_tileset(symbol, src_root, namespace))
    return tilesets


def splice_layouts(new_layouts: list[dict]) -> None:
    path = ROOT / "data/layouts/layouts.json"
    data = json.loads(path.read_text())
    existing = {entry.get("id") for entry in data["layouts"]}
    to_add = [entry for entry in new_layouts if entry["id"] not in existing]
    if not to_add:
        return
    data["layouts"].extend(to_add)
    path.write_text(json.dumps(data, indent=2) + "\n")


def splice_map_groups(groups: dict[str, list[str]]) -> None:
    path = ROOT / "data/maps/map_groups.json"
    data = json.loads(path.read_text())
    order = data["group_order"]
    for name, folders in groups.items():
        if name not in order:
            order.append(name)
        data[name] = folders
        if len(folders) > 256:
            raise SystemExit(f"{name} has {len(folders)} maps; MAP_NUM is u8")
    path.write_text(json.dumps(data, indent=2) + "\n")


def insert_in_emerald_block(path: Path, block: str) -> None:
    text = path.read_text()
    needle = "\n#else\n"
    if needle not in text:
        raise SystemExit(f"{path}: missing #else")
    path.write_text(text.replace(needle, "\n" + block.rstrip() + "\n" + needle, 1))


def tileset_graphics_block(kind: str, folder: str, stem: str, secondary: bool) -> str:
    pals = pal_files(kind, folder)
    pal_lines = ",\n".join(
        f'    INCGFX_U16("data/tilesets/{kind}/{folder}/palettes/{name}", ".gbapal")' for name in pals
    )
    ext = ".4bpp.fastSmol" if secondary else ".4bpp.smol"
    return (
        f"const u16 gTilesetPalettes_{stem}[][16] =\n"
        "{\n"
        f"{pal_lines},\n"
        "};\n\n"
        f'const u32 gTilesetTiles_{stem}[] = INCGFX_U32("data/tilesets/{kind}/{folder}/tiles.png", "{ext}");\n'
    )


def tileset_header_block(symbol: str, stem: str, secondary: bool, uses_frlg_counts: bool) -> str:
    lines = [
        f"const struct Tileset {symbol} =",
        "{",
        "    .isCompressed = TRUE,",
        f"    .isSecondary = {'TRUE' if secondary else 'FALSE'},",
        f"    .tiles = gTilesetTiles_{stem},",
        f"    .palettes = gTilesetPalettes_{stem},",
        f"    .metatiles = gMetatiles_{stem},",
        f"    .metatileAttributes = gMetatileAttributes_{stem},",
        "    .callback = NULL,",
    ]
    if uses_frlg_counts:
        lines.append("    .usesFrlgCounts = TRUE,")
    lines.append("};")
    return "\n".join(lines) + "\n"


def tileset_metatile_block(kind: str, folder: str, stem: str) -> str:
    return (
        f'const u16 gMetatiles_{stem}[] = INCBIN_U16("data/tilesets/{kind}/{folder}/metatiles.bin");\n'
        f'const u16 gMetatileAttributes_{stem}[] = INCBIN_U16("data/tilesets/{kind}/{folder}/metatile_attributes.bin");\n'
    )


def patch_tileset_sources(tilesets: list[tuple[str, str, str, str, bool]]) -> None:
    gfx_blocks = []
    header_blocks = []
    meta_blocks = []
    externs = []
    graphics_text = (ROOT / "src/data/tilesets/graphics.h").read_text()
    headers_text = (ROOT / "src/data/tilesets/headers.h").read_text()
    metatiles_text = (ROOT / "src/data/tilesets/metatiles.h").read_text()
    tilesets_h_text = (ROOT / "include/tilesets.h").read_text()
    for kind, src_folder, dest_folder, symbol, secondary in tilesets:
        stem = symbol[len("gTileset_") :]
        dest = ROOT / "data/tilesets" / kind / dest_folder
        n_meta = (dest / "metatiles.bin").stat().st_size // 16
        uses_frlg = (not secondary) and n_meta > 512
        if f"gTilesetTiles_{stem}" not in graphics_text:
            gfx_blocks.append(tileset_graphics_block(kind, dest_folder, stem, secondary))
        if f"{symbol} =" not in headers_text:
            header_blocks.append(tileset_header_block(symbol, stem, secondary, uses_frlg))
        if f"gMetatiles_{stem}" not in metatiles_text:
            meta_blocks.append(tileset_metatile_block(kind, dest_folder, stem))
        if f"extern const struct Tileset {symbol};" not in tilesets_h_text:
            externs.append(f"extern const struct Tileset {symbol};")
        EXISTING_TILESET_SYMBOLS.add(symbol)
    if gfx_blocks:
        insert_in_emerald_block(ROOT / "src/data/tilesets/graphics.h", "\n".join(gfx_blocks))
    if header_blocks:
        insert_in_emerald_block(ROOT / "src/data/tilesets/headers.h", "\n".join(header_blocks))
    if meta_blocks:
        insert_in_emerald_block(ROOT / "src/data/tilesets/metatiles.h", "\n".join(meta_blocks))
    if externs:
        tilesets_h = ROOT / "include/tilesets.h"
        text = tilesets_h.read_text()
        tilesets_h.write_text(
            text.replace(
                "#endif //GUARD_tilesets_H",
                "\n".join(externs) + "\n\n#endif //GUARD_tilesets_H",
                1,
            )
        )


def collect_all_scripts(maps: list[dict]) -> list[str]:
    names = []
    seen = set()
    for map_data in maps:
        for obj in map_data.get("object_events") or []:
            names.append(obj.get("script"))
        for bg in map_data.get("bg_events") or []:
            names.append(bg.get("script"))
    out = []
    for name in names:
        if not name or name in KEEP_SCRIPTS or name in seen:
            continue
        seen.add(name)
        out.append(name)
    return out


def existing_script_labels() -> set[str]:
    labels: set[str] = set()
    for path in list((ROOT / "data").rglob("*.inc")) + list((ROOT / "data").rglob("*.s")):
        # FRLG-only scripts are not assembled into the Emerald ROM.
        if "_Frlg" in path.name or path.name.endswith("_frlg.inc"):
            continue
        try:
            text = path.read_text(errors="replace")
        except OSError:
            continue
        for line in text.splitlines():
            if line.endswith("::") and not line[:1].isspace():
                labels.add(line[:-2])
    return labels


def write_shared_stubs(maps: list[dict], path: Path, title: str) -> None:
    existing = existing_script_labels()
    to_stub = [
        name
        for name in collect_all_scripts(maps)
        if name not in existing and not name.startswith("Common_EventScript_")
    ]
    lines = [f"@ {title}", ""]
    for script in to_stub:
        lines += [
            f"{script}::",
            f"\tmsgbox {script}_Text, MSGBOX_NPC",
            "\tend",
            "",
            f"{script}_Text:",
            '\t.string "Hello!$"',
            "",
        ]
    path.write_text("\n".join(lines))


def patch_event_scripts(folders: list[str], stub_rel: str) -> None:
    path = ROOT / "data/event_scripts.s"
    text = path.read_text()
    missing = [
        f'\t.include "data/maps/{folder}/scripts.inc"'
        for folder in folders
        if f"data/maps/{folder}/scripts.inc" not in text
    ]
    stub_include = f'\t.include "{stub_rel}"'
    if stub_include.strip() not in text:
        missing.append(stub_include)
    if not missing:
        return
    # Splice after the last Emerald map include, before `.if IS_FRLG`.
    needle = '\t.include "data/maps/Route124_DivingTreasureHuntersHouse/scripts.inc"\n'
    if needle not in text:
        raise SystemExit("Could not splice event_scripts.s")
    path.write_text(text.replace(needle, needle + "\n".join(missing) + "\n", 1))


def import_region(src_root: Path, groups: dict[str, list[str]], namespace: str | None, stub_name: str, stub_title: str) -> None:
    folders = flatten_maps(groups)
    print(f"importing {len(folders)} maps from {src_root.name}")
    load_imported_ids(src_root, folders)
    by_id = layouts_by_id(src_root)
    folder_group = {folder: group for group, maps in groups.items() for folder in maps}
    tilesets = collect_tilesets(src_root, folders, by_id, namespace)
    for kind, src_folder, dest_folder, symbol, _secondary in tilesets:
        copy_tileset(src_root, kind, src_folder, dest_folder)
        print(f"  tileset {symbol} <- {kind}/{src_folder}")
    patch_tileset_sources(tilesets)
    layouts = []
    maps = []
    for folder in folders:
        layouts.append(copy_layout(src_root, folder, by_id, namespace))
        maps.append(rewrite_map(src_root, folder, folder_group[folder], namespace))
    splice_layouts(layouts)
    splice_map_groups(groups)
    stub_path = ROOT / "data/maps" / stub_name
    write_shared_stubs(maps, stub_path, stub_title)
    patch_event_scripts(folders, f"data/maps/{stub_name}")
    print(f"  copied {len(maps)} maps, {len(tilesets)} tilesets")


def bake_hns_collision() -> None:
    layouts = json.loads((ROOT / "data/layouts/layouts.json").read_text())["layouts"]
    files = 0
    cells = 0
    for entry in layouts:
        if entry.get("primary_tileset") not in OUTDOOR_TREE_PRIMARIES:
            continue
        path = ROOT / entry.get("blockdata_filepath", "")
        if not path.exists():
            continue
        width = int(entry["width"])
        height = int(entry["height"])
        data = bytearray(path.read_bytes())
        n = width * height
        if len(data) < n * 2:
            continue
        changed = 0
        for i in range(n):
            tile = data[i * 2] | (data[i * 2 + 1] << 8)
            metatile = tile & 0x3FF
            collision = (tile >> 10) & 0x3
            elevation = (tile >> 12) & 0xF
            if metatile >= 640 or metatile not in OUTDOOR_TREE_METATILES:
                continue
            if collision or elevation == 1:
                continue
            tile = (tile & ~0x0C00) | (1 << 10)
            if elevation in (3, 4):
                tile = (tile & 0x0FFF) | (0 << 12)
            data[i * 2] = tile & 0xFF
            data[i * 2 + 1] = (tile >> 8) & 0xFF
            changed += 1
        if changed:
            path.write_bytes(data)
            files += 1
            cells += changed
    print(f"baked collision on {cells} tree tiles in {files} layouts")


def install_mapsecs() -> list[str]:
    old = json.loads((ROOT / "src/data/region_map/region_map_sections.json").read_text())
    old_ids = {entry["id"] for entry in old["map_sections"]}
    blob = subprocess.check_output(
        ["git", "show", "indigo-story:src/data/region_map/region_map_sections.json"],
        cwd=ROOT,
    )
    (ROOT / "src/data/region_map/region_map_sections.json").write_bytes(blob)
    constants = ROOT / "src/data/region_map/region_map_sections.constants.json.txt"
    text = constants.read_text()
    if "JOHTO_MAPSEC_START" not in text:
        block = (
            "\n#define JOHTO_MAPSEC_START  MAPSEC_NEW_BARK_TOWN\n"
            "#define JOHTO_MAPSEC_END    MAPSEC_EMBEDDED_TOWER\n"
            "#define JOHTO_MAPSEC_COUNT (JOHTO_MAPSEC_END - JOHTO_MAPSEC_START + 1)\n"
            "\n#define SINNOH_MAPSEC_START  MAPSEC_TWINLEAF_TOWN\n"
            "#define SINNOH_MAPSEC_END    MAPSEC_ROCK_PEAK_RUINS\n"
            "#define SINNOH_MAPSEC_COUNT (SINNOH_MAPSEC_END - SINNOH_MAPSEC_START + 1)\n"
            "\n#define MAPSEC_KANTO_VICTORY_ROAD MAPSEC_VICTORY_ROAD\n"
        )
        needle = "#define KANTO_MAPSEC_COUNT (KANTO_MAPSEC_END - KANTO_MAPSEC_START + 1)\n"
        if needle not in text:
            raise SystemExit("Could not splice MAPSEC constants")
        constants.write_text(text.replace(needle, needle + block, 1))
    refresh_mapsecs()
    deleted = sorted(old_ids - VALID_MAPSECS)
    rewritten = 0
    for path in (ROOT / "data/maps").glob("*/map.json"):
        data = json.loads(path.read_text())
        mapsec = data.get("region_map_section")
        if mapsec and mapsec not in VALID_MAPSECS:
            data["region_map_section"] = "MAPSEC_NONE"
            path.write_text(json.dumps(data, indent=2) + "\n")
            rewritten += 1
    print(f"installed MAPSECs; rewrote {rewritten} leftover map.json sections")
    path = ROOT / "include/regions.h"
    text = path.read_text()
    if "JOHTO_MAPSEC_START" not in text:
        old = (
            "static inline enum Region GetRegionForSectionId(u32 sectionId)\n"
            "{\n"
            "    if (sectionId >= KANTO_MAPSEC_START && sectionId < MAPSEC_SPECIAL_AREA)\n"
            "        return REGION_KANTO;\n"
            "    return REGION_HOENN;\n"
            "}\n"
        )
        new = (
            "#include \"constants/region_map_sections.h\"\n\n"
            "static inline enum Region GetRegionForSectionId(u32 sectionId)\n"
            "{\n"
            "    if (sectionId >= JOHTO_MAPSEC_START && sectionId <= JOHTO_MAPSEC_END)\n"
            "        return REGION_JOHTO;\n"
            "    if (sectionId >= SINNOH_MAPSEC_START && sectionId <= SINNOH_MAPSEC_END)\n"
            "        return REGION_SINNOH;\n"
            "    if (sectionId >= KANTO_MAPSEC_START && sectionId < MAPSEC_SPECIAL_AREA)\n"
            "        return REGION_KANTO;\n"
            "    return REGION_NONE;\n"
            "}\n"
        )
        if old not in text:
            raise SystemExit("Could not splice include/regions.h")
        path.write_text(text.replace(old, new, 1))
    return deleted


def stub_deleted_mapsecs(deleted: list[str]) -> None:
    if not deleted:
        return
    pattern = re.compile(r"\b(" + "|".join(re.escape(name) for name in deleted) + r")\b")
    roots = [ROOT / "src", ROOT / "include"]
    skip_names = {"region_map_sections.h", "region_map_sections.json", "region_map_sections.json.txt"}
    for root in roots:
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix not in {".c", ".h"}:
                continue
            if path.name in skip_names:
                continue
            text = path.read_text(errors="replace")
            new = pattern.sub("MAPSEC_NONE", text)
            if new != text:
                path.write_text(new)
                print(f"  stubbed MAPSECs in {path.relative_to(ROOT)}")


def patch_region_map_type() -> None:
    path = ROOT / "src/region_map.c"
    text = path.read_text()
    if "case REGION_JOHTO:" in text:
        return
    text = text.replace(
        "    case REGION_HOENN:\n"
        "    default:\n"
        "        return REGION_MAP_HOENN;\n",
        "    case REGION_JOHTO:\n"
        "    case REGION_SINNOH:\n"
        "        return REGION_MAP_KANTO;\n"
        "    case REGION_HOENN:\n"
        "    default:\n"
        "        return REGION_MAP_HOENN;\n",
        1,
    )
    text = text.replace(
        "    case REGION_HOENN:\n"
        "    default:\n"
        "            return sRegionMap_MapSectionLayout[y][x];\n",
        "    case REGION_JOHTO:\n"
        "    case REGION_SINNOH:\n"
        "            return sRegionMapSections_Kanto[y][x];\n"
        "    case REGION_HOENN:\n"
        "    default:\n"
        "            return sRegionMap_MapSectionLayout[y][x];\n",
        1,
    )
    path.write_text(text)


def main(argv: list[str]) -> None:
    load_constants()
    mode = argv[1] if len(argv) > 1 else "all"
    if mode in {"all", "mapsecs"}:
        deleted = install_mapsecs()
        stub_deleted_mapsecs(deleted)
        patch_region_map_type()
        load_constants()
    if mode in {"all", "johto"}:
        import_region(HNS, hns_groups(), None, "Johto_hns_stubs.inc", "Shared stubs for imported HnS maps.")
    if mode in {"all", "sinnoh"}:
        import_region(SINNOH, sinnoh_groups(), "Sinnoh", "Sinnoh_stubs.inc", "Shared stubs for imported Sinnoh maps.")
    if mode in {"all", "johto", "collision"}:
        bake_hns_collision()


if __name__ == "__main__":
    main(sys.argv)
