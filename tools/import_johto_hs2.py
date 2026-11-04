#!/usr/bin/env python3
"""Copy Johto maps from Heart & Soul 2.0 and rewrite them for pokeemerald-expansion.

HnS source (outside this repo): ../pokehns-expansion
Rewrite: map.json region REGION_KANTO, layout_version frlg, FRLG metatile attributes.
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
HNS = Path("/home/piarew/pokehns-expansion")
sys.path.insert(0, str(ROOT / "migration_scripts"))
import frlg_metatile_behavior_converter as conv  # noqa: E402

OUTDOOR_MAPS = [
    "NewBarkTown_hns",
    "CherrygroveCity_hns",
    "VioletCity_hns",
    "AzaleaTown_hns",
    "GoldenrodCity_hns",
    "EcruteakCity_hns",
    "OlivineCity_hns",
    "CianwoodCity_hns",
    "SafariZoneGate_hns",
    "Mahoganytown_hns",
    "BlackthornCity_hns",
    "Route29_hns",
    "Route30_hns",
    "Route31_hns",
    "Route32_hns",
    "Route33_hns",
    "Route34_hns",
    "Route35_hns",
    "Route36_hns",
    "Route37_hns",
    "Route38_hns",
    "Route39_hns",
    "Route40_hns",
    "Route41_hns",
    "Route42_hns",
    "Route43_hns",
    "Route44_hns",
    "Route45_hns",
    "Route46_hns",
    "Route47_hns",
    "Route48_hns",
    "Route26_hns",
    "Route26North_hns",
    "Route27_hns",
    "Route28_hns",
    "Route23_hns",
    "IndigoPlateau_hns",
    "LakeOfRage_hns",
]

INDOOR_GROUP_RENAMES = [
    ("gMapGroup_IndoorNewBark_Hns", "gMapGroup_IndoorNewBark_Johto"),
    ("gMapGroup_IndoorCherrygrove_Hns", "gMapGroup_IndoorCherrygrove_Johto"),
    ("gMapGroup_IndoorViolet_Hns", "gMapGroup_IndoorViolet_Johto"),
    ("gMapGroup_IndoorAzalea_Hns", "gMapGroup_IndoorAzalea_Johto"),
    ("gMapGroup_IndoorGoldenrod_Hns", "gMapGroup_IndoorGoldenrod_Johto"),
    ("gMapGroup_IndoorEcruteak_Hns", "gMapGroup_IndoorEcruteak_Johto"),
    ("gMapGroup_IndoorOlivine_Hns", "gMapGroup_IndoorOlivine_Johto"),
    ("gMapGroup_IndoorCianwood_Hns", "gMapGroup_IndoorCianwood_Johto"),
    ("gMapGroup_IndoorMahogany_Hns", "gMapGroup_IndoorMahogany_Johto"),
    ("gMapGroup_IndoorBlackthorn_Hns", "gMapGroup_IndoorBlackthorn_Johto"),
    ("gMapGroup_IndoorJohtoRoutes_Hns", "gMapGroup_IndoorJohtoRoutes_Johto"),
]

SKIP_INDOOR_SUBSTR = ("BattleTent", "TrainerHill", "Contest")
KANTO_DUNGEON_PREFIXES = (
    "ViridianForest",
    "MtMoon",
    "RockTunnel",
    "CeruleanCave",
    "DiglettsCave",
    "SeafoamIslands",
    "Route19_Cave",
)
SKIP_DUNGEON_MAPS = {"LakeOfRage_hns", "LakeOfRageLowTide_hns"}

MAPS: list[str] = []
TILESETS: list[tuple[str, str, str, str, bool]] = []
JOHT_GROUPS: dict[str, list[str]] = {}

GFX_MAP = {
    "OBJ_EVENT_GFX_FAT_MAN_HNS": "OBJ_EVENT_GFX_FAT_MAN_FRLG",
    "OBJ_EVENT_GFX_LASS_HNS": "OBJ_EVENT_GFX_LASS_FRLG",
    "OBJ_EVENT_GFX_SILVER_HNS": "OBJ_EVENT_GFX_BLUE",
    "OBJ_EVENT_GFX_MOM_HNS": "OBJ_EVENT_GFX_MOM_FRLG",
    "OBJ_EVENT_GFX_WOMAN_1_HNS": "OBJ_EVENT_GFX_WOMAN_1_FRLG",
    "OBJ_EVENT_GFX_WOMAN_2_HNS": "OBJ_EVENT_GFX_WOMAN_2_FRLG",
    "OBJ_EVENT_GFX_WOMAN_3_HNS": "OBJ_EVENT_GFX_WOMAN_3_FRLG",
    "OBJ_EVENT_GFX_LITTLE_BOY_HNS": "OBJ_EVENT_GFX_LITTLE_BOY_FRLG",
    "OBJ_EVENT_GFX_SCIENTIST_M_HNS": "OBJ_EVENT_GFX_SCIENTIST",
    "OBJ_EVENT_GFX_SCIENTIST_F_HNS": "OBJ_EVENT_GFX_SCIENTIST",
    "OBJ_EVENT_GFX_ELM_HNS": "OBJ_EVENT_GFX_PROF_OAK",
    "OBJ_EVENT_GFX_OFFICER_HNS": "OBJ_EVENT_GFX_POLICEMAN",
    "OBJ_EVENT_GFX_OLD_MAN_HNS": "OBJ_EVENT_GFX_OLD_MAN_1",
    "OBJ_EVENT_GFX_OLD_MAN_2_HNS": "OBJ_EVENT_GFX_OLD_MAN_2",
    "OBJ_EVENT_GFX_YOUNGSTER_HNS": "OBJ_EVENT_GFX_YOUNGSTER_FRLG",
    "OBJ_EVENT_GFX_BOY_2_HNS": "OBJ_EVENT_GFX_YOUNGSTER_FRLG",
    "OBJ_EVENT_GFX_COOLTRAINER_F_HNS": "OBJ_EVENT_GFX_COOLTRAINER_F",
    "OBJ_EVENT_GFX_COOLTRAINER_M_HNS": "OBJ_EVENT_GFX_COOLTRAINER_M",
    "OBJ_EVENT_GFX_ROCKER_HNS": "OBJ_EVENT_GFX_ROCKER",
    "OBJ_EVENT_GFX_PSYCHIC_M_HNS": "OBJ_EVENT_GFX_PSYCHIC_M",
    "OBJ_EVENT_GFX_FISHERMAN_HNS": "OBJ_EVENT_GFX_FISHER",
    "OBJ_EVENT_GFX_ITEM_BALL_HNS": "OBJ_EVENT_GFX_ITEM_BALL",
    "OBJ_EVENT_GFX_CUTTABLE_TREE_HNS": "OBJ_EVENT_GFX_CUTTABLE_TREE_FRLG",
    "OBJ_EVENT_GFX_BREAKABLE_ROCK_HNS": "OBJ_EVENT_GFX_BREAKABLE_ROCK_FRLG",
    "OBJ_EVENT_GFX_POKE_BALL": "OBJ_EVENT_GFX_POKE_BALL",
    "OBJ_EVENT_GFX_BERRY_TREE": "OBJ_EVENT_GFX_BERRY_TREE",
    "OBJ_EVENT_GFX_SMALL_LIGHT_HNS": "OBJ_EVENT_GFX_LIGHT_SPRITE",
    "OBJ_EVENT_GFX_ARCHER_HNS": "OBJ_EVENT_GFX_ROCKET_M",
    "OBJ_EVENT_GFX_ROCKET_M_HNS": "OBJ_EVENT_GFX_ROCKET_M",
    "OBJ_EVENT_GFX_ROCKET_F_HNS": "OBJ_EVENT_GFX_ROCKET_F",
    "OBJ_EVENT_GFX_HIKER_HNS": "OBJ_EVENT_GFX_HIKER_FRLG",
    "OBJ_EVENT_GFX_CAMPER_HNS": "OBJ_EVENT_GFX_CAMPER_FRLG",
    "OBJ_EVENT_GFX_PICNICKER_HNS": "OBJ_EVENT_GFX_PICNICKER_FRLG",
    "OBJ_EVENT_GFX_SWIMMER_F_HNS": "OBJ_EVENT_GFX_SWIMMER_F_WATER",
    "OBJ_EVENT_GFX_SWIMMER_M_HNS": "OBJ_EVENT_GFX_SWIMMER_M_WATER",
    "OBJ_EVENT_GFX_SUPER_NERD_HNS": "OBJ_EVENT_GFX_SCIENTIST",
    "OBJ_EVENT_GFX_BATTLE_GIRL_HNS": "OBJ_EVENT_GFX_COOLTRAINER_F",
    "OBJ_EVENT_GFX_TWIN_HNS": "OBJ_EVENT_GFX_TWIN",
    "OBJ_EVENT_GFX_WHIRLPOOL_HNS": "OBJ_EVENT_GFX_LIGHT_SPRITE",
    "OBJ_EVENT_GFX_NO_TAIL_SLOWPOKE_HNS": "OBJ_EVENT_GFX_SLOWPOKE",
    "OBJ_EVENT_GFX_SAGE_HNS": "OBJ_EVENT_GFX_OLD_MAN_2",
    "OBJ_EVENT_GFX_SAILOR_HNS": "OBJ_EVENT_GFX_SAILOR_FRLG",
    "OBJ_EVENT_GFX_BALDING_MAN_HNS": "OBJ_EVENT_GFX_BALDING_MAN",
    "OBJ_EVENT_GFX_BLACK_BELT_HNS": "OBJ_EVENT_GFX_BLACK_BELT_FRLG",
    "OBJ_EVENT_GFX_BEAUTY_HNS": "OBJ_EVENT_GFX_BEAUTY_FRLG",
    "OBJ_EVENT_GFX_BUG_CATCHER_HNS": "OBJ_EVENT_GFX_BUG_CATCHER_FRLG",
    "OBJ_EVENT_GFX_EUSINE_HNS": "OBJ_EVENT_GFX_GENTLEMAN_FRLG",
    "OBJ_EVENT_GFX_ENGINEER_HNS": "OBJ_EVENT_GFX_WORKER_M",
    "OBJ_EVENT_GFX_WORKER_M_HNS": "OBJ_EVENT_GFX_WORKER_M",
    "OBJ_EVENT_GFX_WORKER_F_HNS": "OBJ_EVENT_GFX_WORKER_F",
    "OBJ_EVENT_GFX_KIMONO_HNS": "OBJ_EVENT_GFX_BEAUTY_FRLG",
    "OBJ_EVENT_GFX_KURT_HNS": "OBJ_EVENT_GFX_OLD_MAN_2",
    "OBJ_EVENT_GFX_ATTENDANT_F_HNS": "OBJ_EVENT_GFX_WOMAN_1_FRLG",
    "OBJ_EVENT_GFX_FIREBREATHER_HNS": "OBJ_EVENT_GFX_HIKER_FRLG",
    "OBJ_EVENT_GFX_JUGGLER_HNS": "OBJ_EVENT_GFX_ROCKER",
    "OBJ_EVENT_GFX_GENTLEMAN_HNS": "OBJ_EVENT_GFX_GENTLEMAN_FRLG",
    "OBJ_EVENT_GFX_LEGENDARY_SHADOW_HNS": "OBJ_EVENT_GFX_LIGHT_SPRITE",
    "OBJ_EVENT_GFX_LANCE_HNS": "OBJ_EVENT_GFX_LANCE",
    "OBJ_EVENT_GFX_SHINY_GYARADOS_HNS": "OBJ_EVENT_GFX_SUDOWOODO",
    "OBJ_EVENT_GFX_PRYCE_HNS": "OBJ_EVENT_GFX_OLD_MAN_2",
    "OBJ_EVENT_GFX_NURSE_HNS": "OBJ_EVENT_GFX_NURSE_FRLG",
    "OBJ_EVENT_GFX_NURSE_CHANSEY_HNS": "OBJ_EVENT_GFX_CHANSEY",
    "OBJ_EVENT_GFX_MART_EMPLOYEE_HNS": "OBJ_EVENT_GFX_MART_EMPLOYEE",
    "OBJ_EVENT_GFX_OLD_WOMAN_HNS": "OBJ_EVENT_GFX_OLD_WOMAN_FRLG",
    "OBJ_EVENT_GFX_PUSHABLE_BOULDER_HNS": "OBJ_EVENT_GFX_PUSHABLE_BOULDER_FRLG",
    "OBJ_EVENT_GFX_TOWER_BEAM_HNS": "OBJ_EVENT_GFX_LIGHT_SPRITE",
    "OBJ_EVENT_GFX_GYM_GUY_HNS": "OBJ_EVENT_GFX_GYM_GUY",
    "OBJ_EVENT_GFX_GIOVANNI_HNS": "OBJ_EVENT_GFX_GIOVANNI",
    "OBJ_EVENT_GFX_BILL_HNS": "OBJ_EVENT_GFX_BILL",
    "OBJ_EVENT_GFX_LITTLE_GIRL_HNS": "OBJ_EVENT_GFX_LITTLE_GIRL_FRLG",
    "OBJ_EVENT_GFX_CHANNELER_HNS": "OBJ_EVENT_GFX_CHANNELER",
    "OBJ_EVENT_GFX_CAPTAIN_HNS": "OBJ_EVENT_GFX_CAPTAIN",
    "OBJ_EVENT_GFX_CHEF_HNS": "OBJ_EVENT_GFX_CHEF",
    "OBJ_EVENT_GFX_BIKER_HNS": "OBJ_EVENT_GFX_BIKER",
}

MUSIC_MAP = {
    "MUS_HG_NEW_BARK": "MUS_RG_PALLET",
    "MUS_HG_ROUTE29": "MUS_RG_ROUTE1",
    "MUS_HG_ROUTE26": "MUS_RG_ROUTE1",
    "MUS_HG_ROUTE30": "MUS_RG_ROUTE1",
    "MUS_HG_ROUTE34": "MUS_RG_ROUTE1",
    "MUS_HG_ROUTE38": "MUS_RG_ROUTE1",
    "MUS_HG_ROUTE42": "MUS_RG_ROUTE1",
    "MUS_HG_ROUTE47": "MUS_RG_ROUTE1",
    "MUS_HG_ELM_LAB": "MUS_RG_OAK_LAB",
    "MUS_HG_CHERRYGROVE": "MUS_RG_PEWTER",
    "MUS_HG_VIOLET": "MUS_RG_PEWTER",
    "MUS_HG_AZALEA": "MUS_RG_PEWTER",
    "MUS_HG_GOLDENROD": "MUS_RG_CELADON",
    "MUS_HG_ECRUTEAK": "MUS_RG_PEWTER",
    "MUS_HG_CIANWOOD": "MUS_RG_PEWTER",
    "MUS_HG_SAFARI_ZONE_GATE": "MUS_RG_PEWTER",
    "MUS_HG_SAFARI_ZONE": "MUS_RG_ROUTE1",
    "MUS_HG_POKE_CENTER": "MUS_RG_POKE_CENTER",
    "MUS_HG_POKE_MART": "MUS_RG_POKE_CENTER",
    "MUS_HG_GYM": "MUS_RG_GYM",
    "MUS_HG_UNION_CAVE": "MUS_RG_MT_MOON",
    "MUS_HG_ICE_PATH": "MUS_RG_MT_MOON",
    "MUS_HG_BELL_TOWER": "MUS_RG_MT_MOON",
    "MUS_HG_LIGHTHOUSE": "MUS_RG_SS_ANNE",
    "MUS_HG_RUINS_OF_ALPH": "MUS_RG_MT_MOON",
    "MUS_HG_GAME_CORNER": "MUS_RG_GAME_CORNER",
    "MUS_HG_POKEMON_LEAGUE": "MUS_RG_VICTORY_ROAD",
    "MUS_HG_VICTORY_ROAD": "MUS_RG_VICTORY_ROAD",
    "MUS_HG_ROUTE3": "MUS_RG_ROUTE3",
}

MAPSEC_REMAP = {
    "MAPSEC_VICTORY_ROAD_HNS": "MAPSEC_VICTORY_ROAD",
}

FOLDER_MAPSEC = {
    "Route23_hns": "MAPSEC_ROUTE_23",
    "VictoryRoadKanto_1F_hns": "MAPSEC_VICTORY_ROAD",
    "VictoryRoadKanto_B1F_hns": "MAPSEC_VICTORY_ROAD",
    "VictoryRoadKanto_B2F_hns": "MAPSEC_VICTORY_ROAD",
}

CONNECTION_REMAP = {}

WARP_REMAP = {
    "MAP_INDIGO_PLATEAU_POKEMON_CENTER_HNS": "MAP_INDIGO_PLATEAU_POKEMON_CENTER_1F",
    "MAP_ROUTE22_HNS": "MAP_ROUTE22",
}

EXTERNAL_MAP_IDS = {
    "MAP_ROUTE22",
    "MAP_INDIGO_PLATEAU_POKEMON_CENTER_1F",
}

CONNECTION_OFFSET_OVERRIDE = {}

KEEP_SCRIPTS = {
    "EventScript_CutTree",
    "EventScript_RockSmash",
    "EventScript_StrengthBoulder",
    "BerryTreeScript",
    "0x0",
    "0",
    "NULL",
}

MOVEMENT_MAP = {
    "MOVEMENT_TYPE_TOWER_BEAM": "MOVEMENT_TYPE_NONE",
}

WEATHER_MAP = {
    "WEATHER_LEAVES": "WEATHER_NONE",
}

WATER_FRLG = {0x10, 0x11, 0x12, 0x13, 0x15, 0x16, 0x17, 0x1A, 0x1B, 0x50, 0x51, 0x52, 0x53}
LAND_FRLG = {0x02}

IMPORTED_MAP_IDS: set[str] = set()


def allowed_dest(map_id: str) -> bool:
    return map_id in IMPORTED_MAP_IDS or map_id in EXTERNAL_MAP_IDS


def rewrite_connections(src_id: str, connections: list | None) -> list | None:
    if not connections:
        return None
    out = []
    for conn in connections:
        dest = CONNECTION_REMAP.get(conn.get("map"), conn.get("map"))
        if not allowed_dest(dest):
            continue
        rewritten = dict(conn)
        rewritten["map"] = dest
        key = (src_id, conn.get("direction"), dest)
        if key in CONNECTION_OFFSET_OVERRIDE:
            rewritten["offset"] = CONNECTION_OFFSET_OVERRIDE[key]
        out.append(rewritten)
    return out or None


def rewrite_warps(warps: list | None) -> list:
    out = []
    for warp in warps or []:
        dest = WARP_REMAP.get(warp.get("dest_map"), warp.get("dest_map"))
        if not allowed_dest(dest):
            continue
        rewritten = dict(warp)
        rewritten["dest_map"] = dest
        out.append(rewritten)
    return out


def skip_indoor_map(folder: str) -> bool:
    return any(part in folder for part in SKIP_INDOOR_SUBSTR)


def johto_map_groups() -> dict[str, list[str]]:
    hns = json.loads((HNS / "data/maps/map_groups.json").read_text())
    groups: dict[str, list[str]] = {"gMapGroup_TownsAndRoutes_Johto": list(OUTDOOR_MAPS)}
    for src_name, dest_name in INDOOR_GROUP_RENAMES:
        groups[dest_name] = [folder for folder in hns[src_name] if not skip_indoor_map(folder)]
    dungeons = []
    for folder in hns["gMapGroup_Dungeons_Hns"]:
        if folder in SKIP_DUNGEON_MAPS or folder.startswith(KANTO_DUNGEON_PREFIXES):
            continue
        dungeons.append(folder)
    groups["gMapGroup_Dungeons_Johto"] = dungeons
    groups["gMapGroup_SafariZone_Johto"] = [
        folder
        for folder in hns["gMapGroup_SpecialArea_Hns"]
        if "SafariZone" in folder and "Fuchsia" not in folder
    ]
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


def parse_hns_tileset_folders() -> dict[str, tuple[str, str]]:
    text = (HNS / "src/data/tilesets/graphics.h").read_text()
    pat = re.compile(
        r'gTilesetTiles_(\w+)\[\] = INCBIN_U32\("data/tilesets/(primary|secondary)/([^/]+)/'
    )
    return {match.group(1): (match.group(2), match.group(3)) for match in pat.finditer(text)}


def collect_tilesets(map_folders: list[str], hns_layouts: list[dict]) -> list[tuple[str, str, str, str, bool]]:
    folder_of_stem = parse_hns_tileset_folders()
    by_path = {entry.get("border_filepath"): entry for entry in hns_layouts}
    tilesets: list[tuple[str, str, str, str, bool]] = []
    seen: set[str] = set()
    for folder in map_folders:
        entry = by_path.get(f"data/layouts/{folder}/border.bin")
        if entry is None:
            raise SystemExit(f"No HnS layout for {folder}")
        for key in ("primary_tileset", "secondary_tileset"):
            symbol = entry.get(key)
            if not symbol or symbol in seen:
                continue
            seen.add(symbol)
            if not symbol.startswith("gTileset_"):
                raise SystemExit(f"{folder}: unexpected tileset {symbol}")
            stem = symbol[len("gTileset_") :]
            if stem not in folder_of_stem:
                raise SystemExit(f"{folder}: no HnS folder for {symbol}")
            kind, ts_folder = folder_of_stem[stem]
            tilesets.append((kind, ts_folder, symbol, stem, kind == "secondary"))
    return tilesets


def emerald_to_frlg_behavior():
    table = {}
    name_to_frlg = {name: code for code, name in conv.FRLG_BEHAVIORS.items()}
    for frlg_name, em_name in conv.FRLG_TO_EMERALD.items():
        table[conv.EMERALD_BEHAVIORS[em_name]] = name_to_frlg[frlg_name]
    return table


EMERALD_TO_FRLG = emerald_to_frlg_behavior()


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
        frlg_behavior = EMERALD_TO_FRLG.get(em_behavior, em_behavior)
        packed = frlg_behavior | ((layer & 0x3) << 29)
        if frlg_behavior in LAND_FRLG:
            packed |= 1 << 24
        elif frlg_behavior in WATER_FRLG:
            packed |= 2 << 24
        out.append(packed)
    dest.write_bytes(struct.pack("<" + "I" * len(out), *out))


def copy_tileset(kind: str, folder: str) -> None:
    src = HNS / "data/tilesets" / kind / folder
    dest = ROOT / "data/tilesets" / kind / folder
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest, ignore=shutil.ignore_patterns("*.pla", "anim"))
    convert_attributes(src / "metatile_attributes.bin", dest / "metatile_attributes.bin")


def pal_files(kind: str, folder: str) -> list[str]:
    pals = sorted((ROOT / "data/tilesets" / kind / folder / "palettes").glob("*.pal"))
    names = [p.name for p in pals if re.fullmatch(r"\d{2}\.pal", p.name)]
    return names[:16]


def gfx_symbol(hns_id: str) -> str | None:
    if hns_id.startswith("OBJ_EVENT_GFX_MON_BASE"):
        return None
    if hns_id.startswith("OBJ_EVENT_GFX_VAR_"):
        return None
    return GFX_MAP.get(hns_id, "OBJ_EVENT_GFX_YOUNGSTER_FRLG")


def stub_music(song: str) -> str:
    if song in MUSIC_MAP:
        return MUSIC_MAP[song]
    if song.startswith("MUS_HG_") and "LAB" in song:
        return "MUS_RG_OAK_LAB"
    if song.startswith("MUS_HG_") and ("CENTER" in song or "MART" in song):
        return "MUS_RG_POKE_CENTER"
    if song.startswith("MUS_HG_") and "GYM" in song:
        return "MUS_RG_GYM"
    if song.startswith("MUS_HG_") and "GAME_CORNER" in song:
        return "MUS_RG_GAME_CORNER"
    if song.startswith("MUS_HG_") and "ROUTE" in song:
        return "MUS_RG_ROUTE1"
    if song.startswith("MUS_HG_") and any(
        part in song for part in ("CAVE", "TOWER", "WELL", "PATH", "DEN", "RUIN", "FOREST", "PARK")
    ):
        return "MUS_RG_MT_MOON"
    if song.startswith("MUS_HG_"):
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
    if gfx == "OBJ_EVENT_GFX_BERRY_TREE":
        script = "0x0"
    movement = obj.get("movement_type", "MOVEMENT_TYPE_NONE")
    movement = MOVEMENT_MAP.get(movement, movement)
    out = {
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
    if "local_id" in obj:
        out = {"local_id": obj["local_id"], **out}
    return out


def rewrite_map(folder: str) -> dict:
    src = json.loads((HNS / "data/maps" / folder / "map.json").read_text())
    map_type = src.get("map_type", "MAP_TYPE_INDOOR")
    building = map_type in ("MAP_TYPE_NONE", "MAP_TYPE_INDOOR")
    if building:
        map_type = "MAP_TYPE_INDOOR"
    indoor = building
    objects = []
    for obj in src.get("object_events") or []:
        rewritten = rewrite_object(obj)
        if rewritten:
            objects.append(rewritten)
    warps = rewrite_warps(src.get("warp_events"))
    connections = rewrite_connections(src["id"], src.get("connections"))
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
    mapsec = src["region_map_section"]
    mapsec = MAPSEC_REMAP.get(mapsec, mapsec)
    mapsec = FOLDER_MAPSEC.get(folder, mapsec)
    rewritten = {
        "id": src["id"],
        "name": src["name"],
        "layout": src["layout"],
        "music": stub_music(src.get("music", "MUS_RG_PALLET")),
        "region": "REGION_KANTO",
        "region_map_section": mapsec,
        "requires_flash": src.get("requires_flash", False),
        "weather": WEATHER_MAP.get(src.get("weather", "WEATHER_NONE"), src.get("weather", "WEATHER_NONE")),
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
    write_stub_scripts(dest_dir / "scripts.inc", src["name"], rewritten)
    return rewritten


def script_prefix(map_name: str) -> str:
    name = map_name.replace("_hns", "")
    if name.startswith("NewBarkTown"):
        return "NewBarkTown"
    return name


def collect_scripts(map_data: dict) -> list[str]:
    names = []
    for obj in map_data.get("object_events") or []:
        names.append(obj.get("script"))
    for bg in map_data.get("bg_events") or []:
        names.append(bg.get("script"))
    prefix = script_prefix(map_data["name"]).lower()
    out = []
    seen = set()
    for name in names:
        if not name or name in KEEP_SCRIPTS or name in seen:
            continue
        if not name.lower().startswith(prefix):
            continue
        seen.add(name)
        out.append(name)
    return out


def write_stub_scripts(path: Path, map_name: str, map_data: dict) -> None:
    path.write_text(f"{map_name}_MapScripts::\n\t.byte 0\n")


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
    for path in (ROOT / "data").rglob("*.inc"):
        if "_hns" in path.name or any("_hns" in part for part in path.parts):
            continue
        try:
            text = path.read_text(errors="replace")
        except OSError:
            continue
        for line in text.splitlines():
            if line.endswith("::") and not line[:1].isspace():
                labels.add(line[:-2])
    return labels


def write_shared_stubs(maps: list[dict]) -> None:
    existing = existing_script_labels()
    to_stub = [name for name in collect_all_scripts(maps) if name not in existing]
    path = ROOT / "data/maps/Johto_hns_stubs.inc"
    lines = ["@ Shared stubs for imported HnS Johto maps.", ""]
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


def copy_layout(folder: str, layouts_by_id: dict) -> dict:
    src = HNS / "data/layouts" / folder
    dest = ROOT / "data/layouts" / folder
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src / "map.bin", dest / "map.bin")
    shutil.copy2(src / "border.bin", dest / "border.bin")
    layout = None
    for entry in layouts_by_id:
        if entry.get("border_filepath") == f"data/layouts/{folder}/border.bin":
            layout = dict(entry)
            break
    if layout is None:
        raise SystemExit(f"No HnS layout for {folder}")
    layout.pop("game_version", None)
    layout["layout_version"] = "frlg"
    layout["border_width"] = 2
    layout["border_height"] = 2
    return layout


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
    for name, folders in JOHT_GROUPS.items():
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
    for kind, folder, symbol, stem, secondary in TILESETS:
        if f"gTilesetTiles_{stem}" not in graphics_text:
            gfx_blocks.append(tileset_graphics_block(kind, folder, stem, secondary))
        if f"{symbol} =" not in headers_text:
            header_blocks.append(tileset_header_block(symbol, stem, secondary))
        if f"gMetatiles_{stem}" not in metatiles_text:
            meta_blocks.append(tileset_metatile_block(kind, folder, stem))
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
    stub_include = '\t.include "data/maps/Johto_hns_stubs.inc"'
    if stub_include.strip() not in text:
        missing.append(stub_include)
    if not missing:
        return
    needle = '\t.include "data/maps/NewBarkTown_House2_hns/scripts.inc"\n'
    if needle not in text:
        needle = '\t.include "data/maps/PalletTown_ProfessorOaksLab_Frlg/scripts.inc"\n'
    if needle not in text:
        raise SystemExit("Could not splice event_scripts.s")
    path.write_text(text.replace(needle, needle + "\n".join(missing) + "\n", 1))


def patch_kanto_border() -> None:
    viridian = ROOT / "data/maps/ViridianCity_Frlg/map.json"
    data = json.loads(viridian.read_text())
    for conn in data.get("connections") or []:
        if conn.get("direction") == "left":
            conn["map"] = "MAP_ROUTE22"
            conn["offset"] = 10
    viridian.write_text(json.dumps(data, indent=2) + "\n")
    route22 = ROOT / "data/maps/Route22_Frlg/map.json"
    data = json.loads(route22.read_text())
    for warp in data.get("warp_events") or []:
        if warp.get("dest_map") in ("MAP_ROUTE22_NORTH_ENTRANCE", "MAP_RECEPTION_GATE_HNS"):
            warp["dest_map"] = "MAP_RECEPTION_GATE_HNS"
            warp["dest_warp_id"] = "4"
    route22.write_text(json.dumps(data, indent=2) + "\n")
    indigo_pc = ROOT / "data/maps/IndigoPlateau_PokemonCenter_1F_Frlg/map.json"
    data = json.loads(indigo_pc.read_text())
    for warp in data.get("warp_events") or []:
        if warp.get("dest_map") == "MAP_INDIGO_PLATEAU_EXTERIOR":
            warp["dest_map"] = "MAP_INDIGO_PLATEAU_HNS"
    indigo_pc.write_text(json.dumps(data, indent=2) + "\n")


def patch_heal_locations() -> None:
    path = ROOT / "src/data/heal_locations.json"
    data = json.loads(path.read_text())
    if any(entry.get("id") == "HEAL_LOCATION_NEW_BARK_TOWN" for entry in data["heal_locations"]):
        return
    data["heal_locations"].append(
        {
            "id": "HEAL_LOCATION_NEW_BARK_TOWN",
            "map": "MAP_NEW_BARK_TOWN_HNS",
            "x": 20,
            "y": 12,
            "respawn_x": 9,
            "respawn_y": 7,
            "respawn_map": "MAP_NEW_BARK_TOWN_PLAYERS_HOUSE_1F_HNS",
            "respawn_npc": "0",
        }
    )
    path.write_text(json.dumps(data, indent=2) + "\n")


def load_imported_ids() -> None:
    IMPORTED_MAP_IDS.clear()
    for folder in MAPS:
        src = json.loads((HNS / "data/maps" / folder / "map.json").read_text())
        IMPORTED_MAP_IDS.add(src["id"])


def main() -> None:
    global MAPS, TILESETS, JOHT_GROUPS
    if not (HNS / "data/maps/NewBarkTown_hns/map.json").exists():
        raise SystemExit(f"HnS checkout missing at {HNS}")
    JOHT_GROUPS = johto_map_groups()
    MAPS = flatten_maps(JOHT_GROUPS)
    missing = [folder for folder in MAPS if not (HNS / "data/maps" / folder / "map.json").exists()]
    if missing:
        raise SystemExit("HnS maps missing: " + ", ".join(missing))
    hns_layouts = json.loads((HNS / "data/layouts/layouts.json").read_text())["layouts"]
    TILESETS = collect_tilesets(MAPS, hns_layouts)
    missing_ts = [
        f"{kind}/{folder}"
        for kind, folder, *_ in TILESETS
        if not (HNS / "data/tilesets" / kind / folder / "metatiles.bin").exists()
    ]
    if missing_ts:
        raise SystemExit("HnS tilesets missing: " + ", ".join(missing_ts))
    load_imported_ids()
    for kind, folder, *_ in TILESETS:
        copy_tileset(kind, folder)
    new_layouts = []
    rewritten = []
    for folder in MAPS:
        rewritten.append(rewrite_map(folder))
        new_layouts.append(copy_layout(folder, hns_layouts))
    write_shared_stubs(rewritten)
    splice_layouts(new_layouts)
    splice_map_groups()
    patch_tileset_sources()
    patch_event_scripts()
    patch_heal_locations()
    patch_kanto_border()
    print("Imported", len(MAPS), "maps in", len(JOHT_GROUPS), "groups")
    for name, folders in JOHT_GROUPS.items():
        print(f"  {name}: {len(folders)}")


if __name__ == "__main__":
    main()
