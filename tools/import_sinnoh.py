#!/usr/bin/env python3
"""Copy Sinnoh maps from LiderMorti00/Sinnoh-pokeemerald-expansion and rewrite them.

Source (outside this repo): /home/piarew/sinnoh-pokeemerald-expansion
Rewrite: map.json region REGION_KANTO, layout_version frlg, FRLG metatile attributes,
namespaced tilesets copied as-is (Emerald 512/6 counts via usesEmeraldCounts).
Does not patch tools/mapjson/mapjson.cpp.
"""
from __future__ import annotations

import json
import re
import shutil
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = Path("/home/piarew/sinnoh-pokeemerald-expansion")

# Source Sinnoh groups to copy (keep source names). Hoenn/FRLG groups are skipped.
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

GROUP_PARENT_MAPSEC = {
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

OUTDOOR_GROUPS = {
    "gMapGroup_SinnohTownsRoutes",
    "gMapGroup_SpecialAreasSinnoh",
    "gMapGroup_DungeonsSinnoh",
}

# Source tileset symbol -> (kind, src_folder, dest_folder, dest_symbol).
# Snapshot Emerald-block tilesets under Sinnoh names so FRLG attrs do not
# overwrite stock folders. New source tilesets keep their original ids.
SNAPSHOT_MAP: dict[str, tuple[str, str, str, str]] = {
    "gTileset_General": ("primary", "general", "sinnoh_general", "gTileset_Sinnoh_General"),
    "gTileset_Petalburg": ("secondary", "petalburg", "sinnoh_petalburg", "gTileset_Sinnoh_Petalburg"),
    "gTileset_Building": ("primary", "building", "sinnoh_building", "gTileset_Sinnoh_Building"),
    "gTileset_BrendansMaysHouse": (
        "secondary",
        "brendans_mays_house",
        "sinnoh_brendans_mays_house",
        "gTileset_Sinnoh_BrendansMaysHouse",
    ),
    "gTileset_GenericBuilding": (
        "secondary",
        "generic_building",
        "sinnoh_generic_building",
        "gTileset_Sinnoh_GenericBuilding",
    ),
}

GFX_MAP = {
    "OBJ_EVENT_GFX_SINNOH_MIDDLE_AGED_WOMAN": "OBJ_EVENT_GFX_WOMAN_2_FRLG",
    "OBJ_EVENT_GFX_SINNOH_COLLECTOR": "OBJ_EVENT_GFX_FAT_MAN_FRLG",
    "OBJ_EVENT_GFX_SINNOH_GUITARIST": "OBJ_EVENT_GFX_ROCKER",
    "OBJ_EVENT_GFX_SINNOH_BARRY": "OBJ_EVENT_GFX_BLUE",
    "OBJ_EVENT_GFX_SINNOH_BREEDER_M": "OBJ_EVENT_GFX_YOUNGSTER_FRLG",
    "OBJ_EVENT_GFX_SINNOH_BREEDER_F": "OBJ_EVENT_GFX_LASS_FRLG",
    "OBJ_EVENT_GFX_SINNOH_LASS": "OBJ_EVENT_GFX_LASS_FRLG",
    "OBJ_EVENT_GFX_SINNOH_ROWAN": "OBJ_EVENT_GFX_PROF_OAK",
    "OBJ_EVENT_GFX_SINNOH_POKEFAN_F": "OBJ_EVENT_GFX_WOMAN_1_FRLG",
    "OBJ_EVENT_GFX_SINNOH_POKEFAN_M": "OBJ_EVENT_GFX_FAT_MAN_FRLG",
    "OBJ_EVENT_GFX_SINNOH_HIKER": "OBJ_EVENT_GFX_HIKER_FRLG",
    "OBJ_EVENT_GFX_SINNOH_BUG_CATCHER": "OBJ_EVENT_GFX_BUG_CATCHER_FRLG",
    "OBJ_EVENT_GFX_SINNOH_ACE_TRAINER_M": "OBJ_EVENT_GFX_COOLTRAINER_M",
    "OBJ_EVENT_GFX_SINNOH_ACE_TRAINER_F": "OBJ_EVENT_GFX_COOLTRAINER_F",
    "OBJ_EVENT_GFX_SINNOH_BEAUTY": "OBJ_EVENT_GFX_BEAUTY_FRLG",
    "OBJ_EVENT_GFX_SINNOH_GENTLEMAN": "OBJ_EVENT_GFX_GENTLEMAN_FRLG",
    "OBJ_EVENT_GFX_SINNOH_POLICEMAN": "OBJ_EVENT_GFX_POLICEMAN",
    "OBJ_EVENT_GFX_SINNOH_SCIENTIST_M": "OBJ_EVENT_GFX_SCIENTIST",
    "OBJ_EVENT_GFX_SINNOH_SCIENTIST_F": "OBJ_EVENT_GFX_SCIENTIST",
    "OBJ_EVENT_GFX_SINNOH_WORKER": "OBJ_EVENT_GFX_WORKER_M",
    "OBJ_EVENT_GFX_SINNOH_CYNTHIA": "OBJ_EVENT_GFX_LEAF",
    "OBJ_EVENT_GFX_SINNOH_NURSE": "OBJ_EVENT_GFX_NURSE_FRLG",
    "OBJ_EVENT_GFX_SINNOH_ICE_ROCK": "OBJ_EVENT_GFX_BREAKABLE_ROCK_FRLG",
    "OBJ_EVENT_GFX_SINNOH_MOSS_ROCK": "OBJ_EVENT_GFX_BREAKABLE_ROCK_FRLG",
}

MUSIC_MAP = {
    "MUS_DPP_TWINLEAF": "MUS_RG_PALLET",
    "MUS_DPP_ROUTE201": "MUS_RG_ROUTE1",
    "MUS_LITTLEROOT_TEST": "MUS_RG_PALLET",
}

# League / Victory Road keep the Kanto ids. Mansion is namespaced.
MAPSEC_REMAP = {
    "MAPSEC_POKEMON_MANSION": "MAPSEC_SINNOH_POKEMON_MANSION",
}

FOLDER_MAPSEC: dict[str, str] = {}

# Shared Kanto ids: do not add fly/heal rows that would steal Pallet-side League/VR.
HEAL_SKIP_MAPSECS = {"MAPSEC_POKEMON_LEAGUE", "MAPSEC_VICTORY_ROAD"}

KEEP_SCRIPTS = {
    "EventScript_CutTree",
    "EventScript_RockSmash",
    "EventScript_StrengthBoulder",
    "BerryTreeScript",
    "0x0",
    "0",
    "NULL",
}

# Encounter-type bits in FRLG 32-bit packing. Behavior IDs stay Emerald
# (stock general_frlg / pallet_town_frlg do the same; MetatileBehavior_*
# always compares against MB_* from metatile_behaviors.h).
LAND_ENCOUNTER = {0x02, 0x03, 0xC9}  # tall/long grass, cycling-road grass
WATER_ENCOUNTER = {0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x2C, 0x2D, 0x50, 0x51, 0x52, 0x53}

# 86 unique Sinnoh names (source 87 minus shared League, mansion namespaced).
SINNOH_MAPSECS = [
    ("MAPSEC_TWINLEAF_TOWN", "TWINLEAF TOWN"),
    ("MAPSEC_SANDGEM_TOWN", "SANDGEM TOWN"),
    ("MAPSEC_JUBILIFE_CITY", "JUBILIFE CITY"),
    ("MAPSEC_OREBURGH_CITY", "OREBURGH CITY"),
    ("MAPSEC_FLOAROMA_TOWN", "FLOAROMA TOWN"),
    ("MAPSEC_ETERNA_CITY", "ETERNA CITY"),
    ("MAPSEC_HEARTHOME_CITY", "HEARTHOME CITY"),
    ("MAPSEC_SOLACEON_TOWN", "SOLACEON TOWN"),
    ("MAPSEC_CELESTIC_TOWN", "CELESTIC TOWN"),
    ("MAPSEC_VEILSTONE_CITY", "VEILSTONE CITY"),
    ("MAPSEC_PASTORIA_CITY", "PASTORIA CITY"),
    ("MAPSEC_CANALAVE_CITY", "CANALAVE CITY"),
    ("MAPSEC_SNOWPOINT_CITY", "SNOWPOINT CITY"),
    ("MAPSEC_SUNYSHORE_CITY", "SUNYSHORE CITY"),
    ("MAPSEC_ROUTE_201", "ROUTE 201"),
    ("MAPSEC_ROUTE_202", "ROUTE 202"),
    ("MAPSEC_ROUTE_203", "ROUTE 203"),
    ("MAPSEC_ROUTE_204", "ROUTE 204"),
    ("MAPSEC_ROUTE_205", "ROUTE 205"),
    ("MAPSEC_ROUTE_206", "ROUTE 206"),
    ("MAPSEC_ROUTE_207", "ROUTE 207"),
    ("MAPSEC_ROUTE_208", "ROUTE 208"),
    ("MAPSEC_ROUTE_209", "ROUTE 209"),
    ("MAPSEC_ROUTE_210", "ROUTE 210"),
    ("MAPSEC_ROUTE_211", "ROUTE 211"),
    ("MAPSEC_ROUTE_212", "ROUTE 212"),
    ("MAPSEC_ROUTE_213", "ROUTE 213"),
    ("MAPSEC_ROUTE_214", "ROUTE 214"),
    ("MAPSEC_ROUTE_215", "ROUTE 215"),
    ("MAPSEC_ROUTE_216", "ROUTE 216"),
    ("MAPSEC_ROUTE_217", "ROUTE 217"),
    ("MAPSEC_ROUTE_218", "ROUTE 218"),
    ("MAPSEC_ROUTE_219", "ROUTE 219"),
    ("MAPSEC_ROUTE_220", "ROUTE 220"),
    ("MAPSEC_ROUTE_221", "ROUTE 221"),
    ("MAPSEC_ROUTE_222", "ROUTE 222"),
    ("MAPSEC_ROUTE_223", "ROUTE 223"),
    ("MAPSEC_ROUTE_224", "ROUTE 224"),
    ("MAPSEC_ROUTE_225", "ROUTE 225"),
    ("MAPSEC_ROUTE_226", "ROUTE 226"),
    ("MAPSEC_ROUTE_227", "ROUTE 227"),
    ("MAPSEC_ROUTE_228", "ROUTE 228"),
    ("MAPSEC_ROUTE_229", "ROUTE 229"),
    ("MAPSEC_ROUTE_230", "ROUTE 230"),
    ("MAPSEC_FIGHT_AREA", "FIGHT AREA"),
    ("MAPSEC_SURVIVAL_AREA", "SURVIVAL AREA"),
    ("MAPSEC_RESORT_AREA", "RESORT AREA"),
    ("MAPSEC_LAKE_VERITY", "LAKE VERITY"),
    ("MAPSEC_LAKE_VALOR", "LAKE VALOR"),
    ("MAPSEC_LAKE_ACUITY", "LAKE ACUITY"),
    ("MAPSEC_OREBURGH_GATE", "OREBURGH GATE"),
    ("MAPSEC_OREBURGH_MINE", "OREBURGH MINE"),
    ("MAPSEC_RAVAGED_PATH", "RAVAGED PATH"),
    ("MAPSEC_FLOAROMA_MEADOW", "FLOAROMA MEADOW"),
    ("MAPSEC_VALLEY_WINDWORKS", "VALLEY WINDWORKS"),
    ("MAPSEC_FUEGO_IRONWORKS", "FUEGO IRONWORKS"),
    ("MAPSEC_ETERNA_FOREST", "ETERNA FOREST"),
    ("MAPSEC_OLD_CHATEAU", "OLD CHATEAU"),
    ("MAPSEC_WAYWARD_CAVE", "WAYWARD CAVE"),
    ("MAPSEC_MT_CORONET", "MT. CORONET"),
    ("MAPSEC_MT_STARK", "MT. STARK"),
    ("MAPSEC_IRON_ISLAND", "IRON ISLAND"),
    ("MAPSEC_VERITY_LAKEFRONT", "VERITY LAKEFRONT"),
    ("MAPSEC_VALOR_LAKEFRONT", "VALOR LAKEFRONT"),
    ("MAPSEC_ACUITY_LAKEFRONT", "ACUITY LAKEFRONT"),
    ("MAPSEC_SOLACEON_RUINS", "SOLACEON RUINS"),
    ("MAPSEC_GREAT_MARSH", "GREAT MARSH"),
    ("MAPSEC_TROPHY_GARDEN", "TROPHY GARDEN"),
    ("MAPSEC_SINNOH_POKEMON_MANSION", "POKéMON MANSION"),
    ("MAPSEC_AMITY_SQUARE", "AMITY SQUARE"),
    ("MAPSEC_GALACTIC_HQ", "GALACTIC HQ"),
    ("MAPSEC_LOST_TOWER", "LOST TOWER"),
    ("MAPSEC_SNOWPOINT_TEMPLE", "SNOWPOINT TEMPLE"),
    ("MAPSEC_SPEAR_PILLAR", "SPEAR PILLAR"),
    ("MAPSEC_HALL_OF_ORIGIN", "HALL OF ORIGIN"),
    ("MAPSEC_SENDOFF_SPRING", "SENDOFF SPRING"),
    ("MAPSEC_TURNBACK_CAVE", "TURNBACK CAVE"),
    ("MAPSEC_SPRING_PATH", "SPRING PATH"),
    ("MAPSEC_FULLMOON_ISLAND", "FULLMOON ISLAND"),
    ("MAPSEC_NEWMOON_ISLAND", "NEWMOON ISLAND"),
    ("MAPSEC_SEABREAK_PATH", "SEABREAK PATH"),
    ("MAPSEC_FLOWER_PARADISE", "FLOWER PARADISE"),
    ("MAPSEC_MANIAC_TUNNEL", "MANIAC TUNNEL"),
    ("MAPSEC_IRON_RUINS", "IRON RUINS"),
    ("MAPSEC_ICEBERG_RUINS", "ICEBERG RUINS"),
    ("MAPSEC_ROCK_PEAK_RUINS", "ROCK PEAK RUINS"),
]

MAPS: list[str] = []
TILESETS: list[tuple[str, str, str, str, bool]] = []
IMPORTED_MAP_IDS: set[str] = set()
SINNOH_GROUPS: dict[str, list[str]] = {}
FOLDER_GROUP: dict[str, str] = {}
VALID_MAPSECS: set[str] = set()
SRC_TILESET_FOLDERS: dict[str, tuple[str, str]] = {}
FRLG_TILESET_SYMBOLS: set[str] = set()


def flatten_maps(groups: dict[str, list[str]]) -> list[str]:
    seen: set[str] = set()
    maps: list[str] = []
    for folders in groups.values():
        for folder in folders:
            if folder not in seen:
                seen.add(folder)
                maps.append(folder)
    return maps


def load_sinnoh_groups() -> dict[str, list[str]]:
    src = json.loads((SRC / "data/maps/map_groups.json").read_text())
    groups: dict[str, list[str]] = {}
    FOLDER_GROUP.clear()
    for name in SINNOH_GROUP_KEYS:
        folders = list(dict.fromkeys(src[name]))
        groups[name] = folders
        for folder in folders:
            FOLDER_GROUP[folder] = name
    return groups


def parse_src_tileset_folders() -> dict[str, tuple[str, str]]:
    text = (SRC / "src/data/tilesets/graphics.h").read_text()
    pat = re.compile(
        r'gTilesetTiles_(\w+)\[\] = INC(?:GFX|BIN)_U32\("data/tilesets/(primary|secondary)/([^"]+?)/'
    )
    found = {match.group(1): (match.group(2), match.group(3)) for match in pat.finditer(text)}
    found.setdefault("General", ("primary", "general"))
    found.setdefault("Building", ("primary", "building"))
    return found


def parse_frlg_tileset_symbols() -> set[str]:
    text = (ROOT / "src/data/tilesets/headers.h").read_text()
    frlg = text.split("#else", 1)[1] if "#else" in text else text
    return set(re.findall(r"const struct Tileset (gTileset_\w+) =", frlg))


def load_valid_mapsecs() -> set[str]:
    data = json.loads((ROOT / "src/data/region_map/region_map_sections.json").read_text())
    return {entry["id"] for entry in data["map_sections"]} | {
        "MAPSEC_POKEMON_LEAGUE",
        "MAPSEC_VICTORY_ROAD",
        "MAPSEC_SINNOH_POKEMON_MANSION",
    }


def stem_to_snake(stem: str) -> str:
    snake = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", stem)
    snake = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", snake)
    return snake.lower()


def resolve_tileset(symbol: str) -> tuple[str, str, str, str, bool]:
    if symbol in SNAPSHOT_MAP:
        kind, src_folder, dest_folder, dest_symbol = SNAPSHOT_MAP[symbol]
        return kind, src_folder, dest_folder, dest_symbol, kind == "secondary"
    if not symbol.startswith("gTileset_"):
        raise SystemExit(f"unexpected tileset {symbol}")
    stem = symbol[len("gTileset_") :]
    if stem in SRC_TILESET_FOLDERS:
        kind, src_folder = SRC_TILESET_FOLDERS[stem]
    else:
        kind = "primary" if stem in {"General", "Building"} else "secondary"
        src_folder = stem_to_snake(stem)
    if symbol in FRLG_TILESET_SYMBOLS:
        return kind, src_folder, src_folder, symbol, kind == "secondary"
    dest_folder = src_folder
    dest_symbol = symbol
    dest_headers = (ROOT / "src/data/tilesets/headers.h").read_text()
    if f"{symbol} =" in dest_headers:
        dest_folder = "sinnoh_" + src_folder
        dest_symbol = "gTileset_Sinnoh_" + stem
    SNAPSHOT_MAP[symbol] = (kind, src_folder, dest_folder, dest_symbol)
    return kind, src_folder, dest_folder, dest_symbol, kind == "secondary"


def is_indoor_building(folder: str) -> bool:
    group = FOLDER_GROUP.get(folder, "")
    return group.startswith("gMapGroup_Indoor")


def outdoor_map_type(folder: str, src_type: str) -> str:
    if src_type not in ("MAP_TYPE_NONE",):
        return src_type
    if any(part in folder for part in ("Town", "City", "League", "Area")):
        return "MAP_TYPE_TOWN" if "City" not in folder else "MAP_TYPE_CITY"
    return "MAP_TYPE_ROUTE"


def resolve_mapsec(folder: str, src_mapsec: str) -> str:
    mapsec = MAPSEC_REMAP.get(src_mapsec, src_mapsec)
    if folder in FOLDER_MAPSEC:
        return FOLDER_MAPSEC[folder]
    if mapsec in VALID_MAPSECS:
        return mapsec
    group = FOLDER_GROUP.get(folder, "")
    if group in GROUP_PARENT_MAPSEC:
        return GROUP_PARENT_MAPSEC[group]
    matches = [name for name in sorted(FOLDER_MAPSEC, key=len, reverse=True) if folder.startswith(name)]
    if matches:
        return FOLDER_MAPSEC[matches[0]]
    raise SystemExit(f"{folder}: cannot assign MAPSEC from {src_mapsec}")


def allowed_dest(map_id: str) -> bool:
    return map_id in IMPORTED_MAP_IDS


def rewrite_connections(connections: list | None) -> list | None:
    if not connections:
        return None
    out = []
    for conn in connections:
        dest = conn.get("map")
        if not allowed_dest(dest):
            continue
        out.append(dict(conn))
    return out or None


def rewrite_warps(warps: list | None) -> list:
    out = []
    for warp in warps or []:
        dest = warp.get("dest_map")
        if not allowed_dest(dest):
            continue
        out.append(dict(warp))
    return out


def convert_attributes(src: Path, dest: Path) -> None:
    data = src.read_bytes()
    n_meta = (dest.parent / "metatiles.bin").stat().st_size // 16
    if len(data) == n_meta * 4:
        dest.write_bytes(data)
        return
    if len(data) != n_meta * 2:
        raise SystemExit(f"{src}: size {len(data)} does not match {n_meta} metatiles")
    out = []
    for (attr,) in struct.iter_unpack("<H", data):
        em_behavior = attr & 0x00FF
        layer = (attr & 0xF000) >> 12
        packed = em_behavior | ((layer & 0x3) << 29)
        if em_behavior in LAND_ENCOUNTER:
            packed |= (1 << 24) | (1 << 9)
        elif em_behavior in WATER_ENCOUNTER:
            packed |= (2 << 24) | (2 << 9)
        out.append(packed)
    dest.write_bytes(struct.pack("<" + "I" * len(out), *out))


def copy_tileset(kind: str, src_folder: str, dest_folder: str) -> None:
    src = SRC / "data/tilesets" / kind / src_folder
    dest = ROOT / "data/tilesets" / kind / dest_folder
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest, ignore=shutil.ignore_patterns("*.pla", "anim"))
    convert_attributes(src / "metatile_attributes.bin", dest / "metatile_attributes.bin")


def pal_files(kind: str, folder: str) -> list[str]:
    pals = sorted((ROOT / "data/tilesets" / kind / folder / "palettes").glob("*.pal"))
    names = [p.name for p in pals if re.fullmatch(r"\d{2}\.pal", p.name)]
    return names[:16]


def gfx_symbol(src_id: str) -> str | None:
    if src_id.startswith("OBJ_EVENT_GFX_MON_BASE"):
        return None
    if src_id.startswith("OBJ_EVENT_GFX_VAR_"):
        return None
    if src_id.startswith("OBJ_EVENT_GFX_SINNOH_MON_"):
        return None
    if src_id.startswith("OBJ_EVENT_GFX_SINNOH_"):
        return GFX_MAP.get(src_id, "OBJ_EVENT_GFX_YOUNGSTER_FRLG")
    return GFX_MAP.get(src_id, src_id)


def stub_music(song: str) -> str:
    if song in MUSIC_MAP:
        return MUSIC_MAP[song]
    if song.startswith("MUS_DPP_") and "ROUTE" in song:
        return "MUS_RG_ROUTE1"
    if song.startswith("MUS_DPP_") and ("CENTER" in song or "MART" in song):
        return "MUS_RG_POKE_CENTER"
    if song.startswith("MUS_DPP_") and "GYM" in song:
        return "MUS_RG_GYM"
    if song.startswith("MUS_DPP_") and any(
        part in song
        for part in ("CAVE", "GATE", "MINE", "FOREST", "RUIN", "TEMPLE", "PATH", "CHATEAU", "LAKE")
    ):
        return "MUS_RG_MT_MOON"
    if song.startswith("MUS_DPP_") and ("VICTORY" in song or "LEAGUE" in song):
        return "MUS_RG_VICTORY_ROAD"
    if song.startswith("MUS_DPP_") and "GALACTIC" in song:
        return "MUS_RG_ROCKET_HIDEOUT"
    if song.startswith("MUS_DPP_"):
        return "MUS_RG_PALLET"
    if song.startswith("MUS_LITTLEROOT"):
        return "MUS_RG_PALLET"
    return song


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
    out = {
        "type": "object",
        "graphics_id": gfx,
        "x": obj["x"],
        "y": obj["y"],
        "elevation": obj.get("elevation", 0),
        "movement_type": obj.get("movement_type", "MOVEMENT_TYPE_NONE"),
        "movement_range_x": obj.get("movement_range_x", 0),
        "movement_range_y": obj.get("movement_range_y", 0),
        "trainer_type": "TRAINER_TYPE_NONE",
        "trainer_sight_or_berry_tree_id": "0",
        "script": script,
        "flag": flag if flag is not None else "0",
    }
    if "local_id" in obj:
        out = {"local_id": obj["local_id"], **out}
    return out


def rewrite_tileset_symbol(symbol: str | None) -> str | None:
    if not symbol:
        return symbol
    return resolve_tileset(symbol)[3]


def rewrite_map(folder: str) -> dict:
    src = json.loads((SRC / "data/maps" / folder / "map.json").read_text())
    indoor = is_indoor_building(folder)
    map_type = src.get("map_type", "MAP_TYPE_INDOOR")
    if indoor:
        map_type = "MAP_TYPE_INDOOR"
    elif FOLDER_GROUP.get(folder) == "gMapGroup_DungeonsSinnoh" and map_type == "MAP_TYPE_NONE":
        map_type = "MAP_TYPE_UNDERGROUND"
    else:
        map_type = outdoor_map_type(folder, map_type)
    objects = []
    for obj in src.get("object_events") or []:
        rewritten = rewrite_object(obj)
        if rewritten:
            objects.append(rewritten)
    warps = rewrite_warps(src.get("warp_events"))
    connections = rewrite_connections(src.get("connections"))
    bg_events = []
    for bg in src.get("bg_events") or []:
        if bg.get("type") == "hidden_item":
            continue
        if bg.get("type") == "sign":
            bg_events.append(
                {
                    "type": "sign",
                    "x": bg["x"],
                    "y": bg["y"],
                    "elevation": bg.get("elevation", 0),
                    "player_facing_dir": bg.get("player_facing_dir", "BG_EVENT_PLAYER_FACING_ANY"),
                    "script": bg.get("script") if bg.get("script") not in (None, "NULL") else "0x0",
                }
            )
    mapsec = resolve_mapsec(folder, src.get("region_map_section", "MAPSEC_NONE"))
    rewritten = {
        "id": src["id"],
        "name": src["name"],
        "layout": src["layout"],
        "music": stub_music(src.get("music", "MUS_RG_PALLET")),
        "region": "REGION_KANTO",
        "region_map_section": mapsec,
        "requires_flash": src.get("requires_flash", False),
        "weather": src.get("weather", "WEATHER_NONE"),
        "map_type": map_type,
        "allow_cycling": src.get("allow_cycling", not indoor),
        "allow_escaping": src.get("allow_escaping", False),
        "allow_running": src.get("allow_running", True),
        "show_map_name": False if indoor else bool(src.get("show_map_name", True)),
        "floor_number": 0,
        "battle_scene": src.get("battle_scene", "MAP_BATTLE_SCENE_NORMAL"),
        "connections": connections,
        "object_events": objects,
        "warp_events": warps,
        "coord_events": [],
        "bg_events": bg_events,
    }
    dest_dir = ROOT / "data/maps" / folder
    dest_dir.mkdir(parents=True, exist_ok=True)
    (dest_dir / "map.json").write_text(json.dumps(rewritten, indent=2) + "\n")
    write_stub_scripts(dest_dir / "scripts.inc", src["name"])
    return rewritten


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
        if "Sinnoh_stubs" in path.name:
            continue
        try:
            text = path.read_text(errors="replace")
        except OSError:
            continue
        for line in text.splitlines():
            if line.endswith("::") and not line[:1].isspace():
                labels.add(line[:-2])
    return labels


def write_stub_scripts(path: Path, map_name: str) -> None:
    path.write_text(f"{map_name}_MapScripts::\n\t.byte 0\n")


def write_shared_stubs(maps: list[dict]) -> None:
    existing = existing_script_labels()
    to_stub = [
        name
        for name in collect_all_scripts(maps)
        if name not in existing and not name.startswith("Common_EventScript_")
    ]
    path = ROOT / "data/maps/Sinnoh_stubs.inc"
    lines = ["@ Shared stubs for imported Sinnoh maps.", ""]
    for script in to_stub:
        lines += [
            f"{script}::",
            "\tmsgbox " + script + "_Text, MSGBOX_NPC",
            "\tend",
            "",
            f"{script}_Text:",
            '\t.string "Hello!$"',
            "",
        ]
    path.write_text("\n".join(lines))


def copy_layout(folder: str, layouts_by_border: dict) -> dict:
    src = SRC / "data/layouts" / folder
    dest = ROOT / "data/layouts" / folder
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src / "map.bin", dest / "map.bin")
    shutil.copy2(src / "border.bin", dest / "border.bin")
    layout = layouts_by_border.get(f"data/layouts/{folder}/border.bin")
    if layout is None:
        raise SystemExit(f"No source layout for {folder}")
    layout = dict(layout)
    layout.pop("game_version", None)
    layout["layout_version"] = "frlg"
    layout["border_width"] = 2
    layout["border_height"] = 2
    layout["primary_tileset"] = rewrite_tileset_symbol(layout.get("primary_tileset"))
    layout["secondary_tileset"] = rewrite_tileset_symbol(layout.get("secondary_tileset"))
    return layout


def collect_tilesets(
    map_folders: list[str],
    layouts_by_border: dict,
    skip_stock_frlg: bool = True,
) -> list[tuple[str, str, str, str, bool]]:
    tilesets: list[tuple[str, str, str, str, bool]] = []
    seen: set[str] = set()
    for folder in map_folders:
        entry = layouts_by_border.get(f"data/layouts/{folder}/border.bin")
        if entry is None:
            raise SystemExit(f"No source layout for {folder}")
        for key in ("primary_tileset", "secondary_tileset"):
            symbol = entry.get(key)
            if not symbol or symbol in seen:
                continue
            seen.add(symbol)
            kind, src_folder, dest_folder, dest_symbol, secondary = resolve_tileset(symbol)
            if skip_stock_frlg and dest_symbol in FRLG_TILESET_SYMBOLS and dest_symbol == symbol:
                src_attr = SRC / "data/tilesets" / kind / src_folder / "metatile_attributes.bin"
                # Unique Sinnoh tilesets are registered in the FRLG block after the
                # first import; still reconvert those (source attrs stay Emerald 16-bit).
                if not src_attr.exists() or src_attr.stat().st_size != (
                    (src_attr.parent / "metatiles.bin").stat().st_size // 16 * 2
                ):
                    continue
            tilesets.append((kind, src_folder, dest_folder, dest_symbol, secondary))
    return tilesets


def splice_layouts(new_layouts: list[dict]) -> None:
    path = ROOT / "data/layouts/layouts.json"
    data = json.loads(path.read_text())
    existing = {entry.get("id") for entry in data["layouts"]}
    to_add = [entry for entry in new_layouts if entry["id"] not in existing]
    if not to_add:
        return
    blob = json.dumps(to_add, indent=2)
    inner = blob[1:-1].strip()
    text = path.read_text()
    needle = "\n  ]\n}\n"
    if not text.endswith(needle) and text.endswith("\n  ]\n}"):
        needle = "\n  ]\n}"
    if needle not in text:
        data["layouts"].extend(to_add)
        path.write_text(json.dumps(data, indent=2) + "\n")
        return
    text = text[: -len(needle)] + ",\n" + inner + needle
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text)


def splice_map_groups() -> None:
    path = ROOT / "data/maps/map_groups.json"
    data = json.loads(path.read_text())
    order = data["group_order"]
    for name, folders in SINNOH_GROUPS.items():
        if name not in order:
            order.append(name)
        data[name] = folders
        if len(folders) > 256:
            raise SystemExit(f"{name} has {len(folders)} maps; MAP_NUM is u8")
    path.write_text(json.dumps(data, indent=2) + "\n")


def insert_before_endif(path: Path, block: str) -> None:
    text = path.read_text()
    needle = "#endif // IS_FRLG"
    if needle not in text:
        raise SystemExit(f"{path}: missing {needle}")
    path.write_text(text.replace(needle, block.rstrip() + "\n\n" + needle, 1))


def tileset_graphics_block(kind: str, folder: str, stem: str, secondary: bool) -> str:
    pals = pal_files(kind, folder)
    pal_lines = ",\n".join(
        f'    INCGFX_U16("data/tilesets/{kind}/{folder}/palettes/{name}", ".gbapal")' for name in pals
    )
    aligned = " ALIGNED(4)" if not secondary else ""
    ext = ".4bpp.fastSmol" if secondary else ".4bpp.smol"
    return (
        f"const u16{aligned} gTilesetPalettes_{stem}[][16] =\n"
        "{\n"
        f"{pal_lines},\n"
        "};\n\n"
        f'const u32 gTilesetTiles_{stem}[] = INCGFX_U32("data/tilesets/{kind}/{folder}/tiles.png", "{ext}");\n'
    )


def tileset_header_block(symbol: str, stem: str, secondary: bool) -> str:
    secondary_c = "TRUE" if secondary else "FALSE"
    return (
        f"const struct Tileset {symbol} =\n"
        "{\n"
        "    .isCompressed = TRUE,\n"
        f"    .isSecondary = {secondary_c},\n"
        f"    .tiles = gTilesetTiles_{stem},\n"
        f"    .palettes = gTilesetPalettes_{stem},\n"
        f"    .metatiles = gMetatiles_{stem},\n"
        f"    .metatileAttributes = gMetatileAttributes_{stem},\n"
        "    .callback = NULL,\n"
        "    .usesEmeraldCounts = TRUE,\n"
        "};\n"
    )


def tileset_metatile_block(kind: str, folder: str, stem: str) -> str:
    return (
        f'const u16 gMetatiles_{stem}[] = INCBIN_U16("data/tilesets/{kind}/{folder}/metatiles.bin");\n'
        f'const u16 gMetatileAttributes_{stem}[] = INCBIN_U16("data/tilesets/{kind}/{folder}/metatile_attributes.bin");\n'
    )


def patch_tileset_sources() -> None:
    gfx_blocks = []
    header_blocks = []
    meta_blocks = []
    externs = []
    graphics_text = (ROOT / "src/data/tilesets/graphics.h").read_text()
    headers_text = (ROOT / "src/data/tilesets/headers.h").read_text()
    metatiles_text = (ROOT / "src/data/tilesets/metatiles.h").read_text()
    tilesets_h_text = (ROOT / "include/tilesets.h").read_text()
    for kind, src_folder, dest_folder, symbol, secondary in TILESETS:
        stem = symbol[len("gTileset_") :]
        if f"gTilesetTiles_{stem}" not in graphics_text:
            gfx_blocks.append(tileset_graphics_block(kind, dest_folder, stem, secondary))
        if f"{symbol} =" not in headers_text:
            header_blocks.append(tileset_header_block(symbol, stem, secondary))
        if f"gMetatiles_{stem}" not in metatiles_text:
            meta_blocks.append(tileset_metatile_block(kind, dest_folder, stem))
        if f"extern const struct Tileset {symbol};" not in tilesets_h_text:
            externs.append(f"extern const struct Tileset {symbol};")
    if gfx_blocks:
        insert_before_endif(ROOT / "src/data/tilesets/graphics.h", "\n".join(gfx_blocks))
    if header_blocks:
        insert_before_endif(ROOT / "src/data/tilesets/headers.h", "\n".join(header_blocks))
    if meta_blocks:
        insert_before_endif(ROOT / "src/data/tilesets/metatiles.h", "\n".join(meta_blocks))
    if externs:
        tilesets_h = ROOT / "include/tilesets.h"
        text = tilesets_h.read_text()
        text = text.replace(
            "#endif //GUARD_tilesets_H",
            "\n".join(externs) + "\n\n#endif //GUARD_tilesets_H",
            1,
        )
        tilesets_h.write_text(text)


def patch_event_scripts() -> None:
    path = ROOT / "data/event_scripts.s"
    text = path.read_text()
    missing = [
        f'\t.include "data/maps/{folder}/scripts.inc"'
        for folder in MAPS
        if f"data/maps/{folder}/scripts.inc" not in text
    ]
    stub_include = '\t.include "data/maps/Sinnoh_stubs.inc"'
    if stub_include.strip() not in text:
        missing.append(stub_include)
    if not missing:
        return
    needle = '\t.include "data/maps/Johto_hns_stubs.inc"\n'
    if needle not in text:
        raise SystemExit("Could not splice event_scripts.s")
    path.write_text(text.replace(needle, needle + "\n".join(missing) + "\n", 1))


def patch_heal_locations() -> None:
    path = ROOT / "src/data/heal_locations.json"
    data = json.loads(path.read_text())
    existing = {entry.get("id") for entry in data["heal_locations"]}
    added = False
    for heal in discover_heals():
        if heal["id"] in existing:
            continue
        data["heal_locations"].append(
            {
                "id": heal["id"],
                "map": heal["map"],
                "x": heal["x"],
                "y": heal["y"],
                "respawn_x": heal["respawn_x"],
                "respawn_y": heal["respawn_y"],
                "respawn_map": heal["respawn_map"],
                "respawn_npc": heal["respawn_npc"],
            }
        )
        existing.add(heal["id"])
        added = True
    if added:
        path.write_text(json.dumps(data, indent=2) + "\n")


def patch_mapsecs() -> None:
    path = ROOT / "src/data/region_map/region_map_sections.json"
    data = json.loads(path.read_text())
    existing = {entry.get("id") for entry in data["map_sections"]}
    if "MAPSEC_TWINLEAF_TOWN" in existing:
        return
    if len(SINNOH_MAPSECS) != 86:
        raise SystemExit(f"expected 86 Sinnoh MAPSECs, got {len(SINNOH_MAPSECS)}")
    for mapsec_id, name in SINNOH_MAPSECS:
        if mapsec_id in existing:
            raise SystemExit(f"MAPSEC already present: {mapsec_id}")
        data["map_sections"].append({"id": mapsec_id, "name": name})
    path.write_text(json.dumps(data, indent=2) + "\n")
    constants = ROOT / "src/data/region_map/region_map_sections.constants.json.txt"
    text = constants.read_text()
    if "SINNOH_MAPSEC_START" in text:
        return
    block = (
        "\n#define SINNOH_MAPSEC_START  MAPSEC_TWINLEAF_TOWN\n"
        "#define SINNOH_MAPSEC_END    MAPSEC_ROCK_PEAK_RUINS\n"
        "#define SINNOH_MAPSEC_COUNT (SINNOH_MAPSEC_END - SINNOH_MAPSEC_START + 1)\n"
    )
    needle = "#define JOHTO_MAPSEC_COUNT (JOHTO_MAPSEC_END - JOHTO_MAPSEC_START + 1)\n"
    if needle not in text:
        raise SystemExit("Could not splice Sinnoh MAPSEC constants")
    constants.write_text(text.replace(needle, needle + block, 1))


def patch_regions() -> None:
    path = ROOT / "include/regions.h"
    text = path.read_text()
    if "SINNOH_MAPSEC_START" in text:
        return
    old = (
        "    if (sectionId >= JOHTO_MAPSEC_START && sectionId <= JOHTO_MAPSEC_END)\n"
        "        return REGION_JOHTO;\n"
        "    if (sectionId >= KANTO_MAPSEC_START && sectionId < MAPSEC_SPECIAL_AREA)\n"
        "        return REGION_KANTO;\n"
        "    return REGION_NONE;\n"
    )
    new = (
        "    if (sectionId >= JOHTO_MAPSEC_START && sectionId <= JOHTO_MAPSEC_END)\n"
        "        return REGION_JOHTO;\n"
        "    if (sectionId >= SINNOH_MAPSEC_START && sectionId <= SINNOH_MAPSEC_END)\n"
        "        return REGION_SINNOH;\n"
        "    if (sectionId >= KANTO_MAPSEC_START && sectionId < MAPSEC_SPECIAL_AREA)\n"
        "        return REGION_KANTO;\n"
        "    return REGION_NONE;\n"
    )
    if old not in text:
        raise SystemExit("Could not splice GetRegionForSectionId")
    path.write_text(text.replace(old, new, 1))


def smap_heal_block() -> str:
    rows = []
    for heal in discover_heals():
        rows.append(
            f"    [{heal['mapsec']}] = {{MAP_GROUP({heal['map']}), MAP_NUM({heal['map']}), {heal['id']}}},"
        )
    rows.append(
        "    [MAPSEC_ROCK_PEAK_RUINS] = {MAP_GROUP(MAP_TWINLEAF_TOWN), MAP_NUM(MAP_TWINLEAF_TOWN), HEAL_LOCATION_NONE},"
    )
    return "\n".join(rows)


def patch_smap_heal_locations(text: str) -> str:
    block = smap_heal_block()
    twin_only = (
        "    [MAPSEC_TWINLEAF_TOWN] = {MAP_GROUP(MAP_TWINLEAF_TOWN), MAP_NUM(MAP_TWINLEAF_TOWN), HEAL_LOCATION_TWINLEAF_TOWN},\n"
        "};"
    )
    if twin_only in text:
        return text.replace(twin_only, block + "\n};", 1)
    if "[MAPSEC_ROCK_PEAK_RUINS]" in text:
        return text
    needle = (
        "    [MAPSEC_EMBER_SPA] = {MAP_GROUP(MAP_PALLET_TOWN), MAP_NUM(MAP_PALLET_TOWN), HEAL_LOCATION_NONE},\n"
        "};"
    )
    if needle not in text:
        raise SystemExit("Could not splice sMapHealLocations")
    insert = (
        "    [MAPSEC_EMBER_SPA] = {MAP_GROUP(MAP_PALLET_TOWN), MAP_NUM(MAP_PALLET_TOWN), HEAL_LOCATION_NONE},\n"
        + block
        + "\n};"
    )
    return text.replace(needle, insert, 1)


def patch_region_map() -> None:
    path = ROOT / "src/region_map.c"
    text = path.read_text()
    if "case REGION_SINNOH:" not in text:
        old_type = (
            "    case REGION_JOHTO:\n"
            "        // Stub until Johto region-map art exists.\n"
            "        return REGION_MAP_KANTO;\n"
            "    default:\n"
            "        return REGION_MAP_KANTO;\n"
        )
        new_type = (
            "    case REGION_JOHTO:\n"
            "        // Stub until Johto region-map art exists.\n"
            "        return REGION_MAP_KANTO;\n"
            "    case REGION_SINNOH:\n"
            "        // Stub until Sinnoh region-map art exists.\n"
            "        return REGION_MAP_KANTO;\n"
            "    default:\n"
            "        return REGION_MAP_KANTO;\n"
        )
        if old_type not in text:
            raise SystemExit("Could not splice GetRegionMapType")
        text = text.replace(old_type, new_type, 1)
        old_sec = (
            "    case REGION_JOHTO:\n"
            "        // Stub grid until a Johto section layout exists.\n"
            "        return sRegionMapSections_Kanto[y][x];\n"
            "    default:\n"
            "            return sRegionMapSections_Kanto[y][x];\n"
        )
        new_sec = (
            "    case REGION_JOHTO:\n"
            "        // Stub grid until a Johto section layout exists.\n"
            "        return sRegionMapSections_Kanto[y][x];\n"
            "    case REGION_SINNOH:\n"
            "        // Stub grid until a Sinnoh section layout exists.\n"
            "        return sRegionMapSections_Kanto[y][x];\n"
            "    default:\n"
            "            return sRegionMapSections_Kanto[y][x];\n"
        )
        if old_sec not in text:
            raise SystemExit("Could not splice GetMapSecIdAt")
        text = text.replace(old_sec, new_sec, 1)
    text = patch_smap_heal_locations(text)
    path.write_text(text)


def load_imported_ids() -> None:
    IMPORTED_MAP_IDS.clear()
    for folder in MAPS:
        src = json.loads((SRC / "data/maps" / folder / "map.json").read_text())
        IMPORTED_MAP_IDS.add(src["id"])


def fill_folder_mapsec() -> None:
    FOLDER_MAPSEC.clear()
    for folder in MAPS:
        if FOLDER_GROUP.get(folder) not in OUTDOOR_GROUPS:
            continue
        src = json.loads((SRC / "data/maps" / folder / "map.json").read_text())
        mapsec = MAPSEC_REMAP.get(
            src.get("region_map_section", "MAPSEC_NONE"),
            src.get("region_map_section", "MAPSEC_NONE"),
        )
        if mapsec in VALID_MAPSECS:
            FOLDER_MAPSEC[folder] = mapsec


def is_pokemon_center_1f(map_id: str) -> bool:
    return bool(map_id) and (
        map_id.endswith("_POKEMON_CENTER_1F") or map_id.endswith("_POKEMON_CENTER_F1")
    )


def discover_heals() -> list[dict]:
    heals = [
        {
            "id": "HEAL_LOCATION_TWINLEAF_TOWN",
            "mapsec": "MAPSEC_TWINLEAF_TOWN",
            "map": "MAP_TWINLEAF_TOWN",
            "x": 16,
            "y": 19,
            "respawn_x": 2,
            "respawn_y": 7,
            "respawn_map": "MAP_TWINLEAF_TOWN_MAIN_HOUSE_1F",
            "respawn_npc": "0",
        }
    ]
    seen = {"HEAL_LOCATION_TWINLEAF_TOWN"}
    for folder in MAPS:
        if FOLDER_GROUP.get(folder) != "gMapGroup_SinnohTownsRoutes":
            continue
        src = json.loads((SRC / "data/maps" / folder / "map.json").read_text())
        mapsec = resolve_mapsec(folder, src.get("region_map_section", "MAPSEC_NONE"))
        if mapsec in HEAL_SKIP_MAPSECS:
            continue
        hits = [
            warp
            for warp in (src.get("warp_events") or [])
            if is_pokemon_center_1f(warp.get("dest_map", ""))
        ]
        if not hits:
            continue
        door = hits[0]
        heal_id = "HEAL_LOCATION_" + mapsec[len("MAPSEC_") :]
        if heal_id in seen:
            continue
        seen.add(heal_id)
        heals.append(
            {
                "id": heal_id,
                "mapsec": mapsec,
                "map": src["id"],
                "x": door["x"],
                "y": door["y"] + 1,
                "respawn_x": 7,
                "respawn_y": 4,
                "respawn_map": door["dest_map"],
                "respawn_npc": "0",
            }
        )
    return heals


def main() -> None:
    global MAPS, TILESETS, SINNOH_GROUPS, SRC_TILESET_FOLDERS, FRLG_TILESET_SYMBOLS, VALID_MAPSECS
    if not (SRC / "data/maps/TwinleafTown/map.json").exists():
        raise SystemExit(f"Sinnoh checkout missing at {SRC}")
    SINNOH_GROUPS = load_sinnoh_groups()
    SRC_TILESET_FOLDERS = parse_src_tileset_folders()
    FRLG_TILESET_SYMBOLS = parse_frlg_tileset_symbols()
    VALID_MAPSECS = load_valid_mapsecs()
    MAPS = flatten_maps(SINNOH_GROUPS)
    missing = [folder for folder in MAPS if not (SRC / "data/maps" / folder / "map.json").exists()]
    if missing:
        raise SystemExit("Sinnoh maps missing: " + ", ".join(missing))
    src_layouts = json.loads((SRC / "data/layouts/layouts.json").read_text())["layouts"]
    layouts_by_border = {entry.get("border_filepath"): entry for entry in src_layouts}
    TILESETS = collect_tilesets(MAPS, layouts_by_border)
    missing_ts = [
        f"{kind}/{src_folder}"
        for kind, src_folder, *_ in TILESETS
        if not (SRC / "data/tilesets" / kind / src_folder / "metatiles.bin").exists()
    ]
    if missing_ts:
        raise SystemExit("Sinnoh tilesets missing: " + ", ".join(missing_ts))
    load_imported_ids()
    fill_folder_mapsec()
    patch_mapsecs()
    patch_regions()
    patch_region_map()
    for kind, src_folder, dest_folder, *_ in TILESETS:
        copy_tileset(kind, src_folder, dest_folder)
    new_layouts = []
    rewritten = []
    for folder in MAPS:
        rewritten.append(rewrite_map(folder))
        new_layouts.append(copy_layout(folder, layouts_by_border))
    write_shared_stubs(rewritten)
    splice_layouts(new_layouts)
    splice_map_groups()
    patch_tileset_sources()
    patch_event_scripts()
    patch_heal_locations()
    print("Imported", len(MAPS), "maps in", len(SINNOH_GROUPS), "groups")
    for name, folders in SINNOH_GROUPS.items():
        print(f"  {name}: {len(folders)}")
    print("Tilesets:")
    for kind, src_folder, dest_folder, symbol, _ in TILESETS:
        print(f"  {symbol} <- {kind}/{src_folder} as {kind}/{dest_folder}")


def reconvert_attributes() -> None:
    """Rewrite imported tileset attributes only (keep Emerald MB_* IDs)."""
    global MAPS, TILESETS, SINNOH_GROUPS, SRC_TILESET_FOLDERS, FRLG_TILESET_SYMBOLS, VALID_MAPSECS
    SINNOH_GROUPS = load_sinnoh_groups()
    SRC_TILESET_FOLDERS = parse_src_tileset_folders()
    FRLG_TILESET_SYMBOLS = parse_frlg_tileset_symbols()
    VALID_MAPSECS = load_valid_mapsecs()
    MAPS = flatten_maps(SINNOH_GROUPS)
    src_layouts = json.loads((SRC / "data/layouts/layouts.json").read_text())["layouts"]
    layouts_by_border = {entry.get("border_filepath"): entry for entry in src_layouts}
    TILESETS = collect_tilesets(MAPS, layouts_by_border)
    for kind, src_folder, dest_folder, symbol, _ in TILESETS:
        src = SRC / "data/tilesets" / kind / src_folder / "metatile_attributes.bin"
        dest = ROOT / "data/tilesets" / kind / dest_folder / "metatile_attributes.bin"
        convert_attributes(src, dest)
        print(f"  reconverted {symbol} <- {kind}/{src_folder}")
    print("Reconverted", len(TILESETS), "tilesets")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--attrs-only":
        reconvert_attributes()
    else:
        main()
