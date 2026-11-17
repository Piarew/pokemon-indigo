#!/usr/bin/env python3
"""Replace FRLG Kanto maps with Heart & Soul HGSS Kanto (Cinnabar in-place pattern).

Keeps FireRed MAP_* ids and *_Frlg folders. Swaps layout to LAYOUT_*_HNS,
rewrites connections/warp coords, copies missing layouts/tilesets.
See documentation/import-johto-hs2.md (Kanto remap).
"""
from __future__ import annotations

import json
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import import_johto_hs2 as hs  # noqa: E402

HNS = hs.HNS

OUTDOOR_PAIRS = [
    ("PalletTown_hns", "PalletTown_Frlg"),
    ("ViridianCity_hns", "ViridianCity_Frlg"),
    ("PewterCity_hns", "PewterCity_Frlg"),
    ("CeruleanCity_hns", "CeruleanCity_Frlg"),
    ("VermilionCity_hns", "VermilionCity_Frlg"),
    ("LavenderTown_hns", "LavenderTown_Frlg"),
    ("CeladonCity_hns", "CeladonCity_Frlg"),
    ("SaffronCity_hns", "SaffronCity_Frlg"),
    ("FuchsiaCity_hns", "FuchsiaCity_Frlg"),
    ("CinnabarIsland_hns", "CinnabarIsland_Frlg"),
    ("IndigoPlateau_hns", "IndigoPlateau_Exterior_Frlg"),
    ("Route1_hns", "Route1_Frlg"),
    ("Route2_hns", "Route2_Frlg"),
    ("Route3_hns", "Route3_Frlg"),
    ("Route4_hns", "Route4_Frlg"),
    ("Route5_hns", "Route5_Frlg"),
    ("Route6_hns", "Route6_Frlg"),
    ("Route7_hns", "Route7_Frlg"),
    ("Route8_hns", "Route8_Frlg"),
    ("Route9_hns", "Route9_Frlg"),
    ("Route10_hns", "Route10_Frlg"),
    ("Route11_hns", "Route11_Frlg"),
    ("Route12_hns", "Route12_Frlg"),
    ("Route13_hns", "Route13_Frlg"),
    ("Route14_hns", "Route14_Frlg"),
    ("Route15_hns", "Route15_Frlg"),
    ("Route16_hns", "Route16_Frlg"),
    ("Route17_hns", "Route17_Frlg"),
    ("Route18_hns", "Route18_Frlg"),
    ("Route19_hns", "Route19_Frlg"),
    ("Route20_hns", "Route20_Frlg"),
    ("Route21_hns", "Route21_North_Frlg"),
    ("Route22_hns", "Route22_Frlg"),
    ("Route23_hns", "Route23_Frlg"),
    ("Route24_hns", "Route24_Frlg"),
    ("Route25_hns", "Route25_Frlg"),
]

# Pokemon Centers stay FRLG (1F+2F cable club), matching Cinnabar.
INTERIOR_PAIRS = [
    ("PalletTown_RedsHouse_1F_hns", "PalletTown_PlayersHouse_1F_Frlg"),
    ("PalletTown_RedsHouse_2F_hns", "PalletTown_PlayersHouse_2F_Frlg"),
    ("PalletTown_House2_hns", "PalletTown_RivalsHouse_Frlg"),
    ("PalletTown_Lab_hns", "PalletTown_ProfessorOaksLab_Frlg"),
    ("ViridianCity_Mart_hns", "ViridianCity_Mart_Frlg"),
    ("ViridianCity_House1_hns", "ViridianCity_House_Frlg"),
    ("ViridianCity_House2_hns", "ViridianCity_School_Frlg"),
    ("ViridianCity_Gym_hns", "ViridianCity_Gym_Frlg"),
    ("PewterCity_Mart_hns", "PewterCity_Mart_Frlg"),
    ("PewterCity_House1_hns", "PewterCity_House1_Frlg"),
    ("PewterCity_House2_hns", "PewterCity_House2_Frlg"),
    ("PewterCity_Gym_hns", "PewterCity_Gym_Frlg"),
    ("PewterCity_Museum_1F_hns", "PewterCity_Museum_1F_Frlg"),
    ("PewterCity_Museum_2F_hns", "PewterCity_Museum_2F_Frlg"),
    ("CeruleanCity_Mart_hns", "CeruleanCity_Mart_Frlg"),
    ("CeruleanCity_House1_hns", "CeruleanCity_House1_Frlg"),
    ("CeruleanCity_House2_hns", "CeruleanCity_House2_Frlg"),
    ("CeruleanCity_House3_hns", "CeruleanCity_House3_Frlg"),
    ("CeruleanCity_BikeShop_hns", "CeruleanCity_BikeShop_Frlg"),
    ("CeruleanCity_Gym_hns", "CeruleanCity_Gym_Frlg"),
    ("VermilionCity_Mart_hns", "VermilionCity_Mart_Frlg"),
    ("VermilionCity_Gym_hns", "VermilionCity_Gym_Frlg"),
    ("VermilionCity_FanClub_hns", "VermilionCity_PokemonFanClub_Frlg"),
    ("VermilionCity_House1_hns", "VermilionCity_House1_Frlg"),
    ("VermilionCity_House2_hns", "VermilionCity_House2_Frlg"),
    ("VermilionCity_House3_hns", "VermilionCity_House3_Frlg"),
    ("LavenderTown_Mart_hns", "LavenderTown_Mart_Frlg"),
    ("LavenderTown_House1_hns", "LavenderTown_House1_Frlg"),
    ("LavenderTown_House2_hns", "LavenderTown_House2_Frlg"),
    ("LavenderTown_SoulHouse_hns", "LavenderTown_VolunteerPokemonHouse_Frlg"),
    ("CeladonCity_House1_hns", "CeladonCity_Restaurant_Frlg"),
    ("CeladonCity_House2_hns", "CeladonCity_House1_Frlg"),
    ("CeladonCity_Apartments_1F_hns", "CeladonCity_Condominiums_1F_Frlg"),
    ("CeladonCity_Apartments_2F_hns", "CeladonCity_Condominiums_2F_Frlg"),
    ("CeladonCity_Apartments_3F_hns", "CeladonCity_Condominiums_3F_Frlg"),
    ("CeladonCity_Apartments_RoofDay_hns", "CeladonCity_Condominiums_Roof_Frlg"),
    ("CeladonCity_Apartments_RoofHouse_hns", "CeladonCity_Condominiums_RoofRoom_Frlg"),
    ("CeladonCity_GameCorner_hns", "CeladonCity_GameCorner_Frlg"),
    ("CeladonCity_DepartmentStore_1F_hns", "CeladonCity_DepartmentStore_1F_Frlg"),
    ("CeladonCity_DepartmentStore_2F_hns", "CeladonCity_DepartmentStore_2F_Frlg"),
    ("CeladonCity_DepartmentStore_3F_hns", "CeladonCity_DepartmentStore_3F_Frlg"),
    ("CeladonCity_DepartmentStore_4F_hns", "CeladonCity_DepartmentStore_4F_Frlg"),
    ("CeladonCity_DepartmentStore_5F_hns", "CeladonCity_DepartmentStore_5F_Frlg"),
    ("CeladonCity_DepartmentStore_RoofDay_hns", "CeladonCity_DepartmentStore_Roof_Frlg"),
    ("CeladonCity_Gym_hns", "CeladonCity_Gym_Frlg"),
    ("SaffronCity_Mart_hns", "SaffronCity_Mart_Frlg"),
    ("SaffronCity_FightingDojo_hns", "SaffronCity_Dojo_Frlg"),
    ("SaffronCity_Gym_hns", "SaffronCity_Gym_Frlg"),
    ("SaffronCity_CopyCatsHouse_1F_hns", "SaffronCity_CopycatsHouse_1F_Frlg"),
    ("SaffronCity_CopyCatsHouse_2F_hns", "SaffronCity_CopycatsHouse_2F_Frlg"),
    ("SaffronCity_House1_hns", "SaffronCity_MrPsychicsHouse_Frlg"),
    ("FuchsiaCity_Mart_hns", "FuchsiaCity_Mart_Frlg"),
    ("FuchsiaCity_House1_hns", "FuchsiaCity_House1_Frlg"),
    ("FuchsiaCity_House2_hns", "FuchsiaCity_House2_Frlg"),
    ("FuchsiaCity_Gym_hns", "FuchsiaCity_Gym_Frlg"),
    ("FuchsiaCity_Route15_Gate_hns", "Route15_WestEntrance_1F_Frlg"),
    ("FuchsiaCity_Route19_Gate_hns", "Route19_UnusedHouse_Frlg"),
    ("Gate_Route2_ViridianForest_hns", "Route2_ViridianForest_SouthEntrance_Frlg"),
    ("Gate_ViridianForest_Route2_hns", "Route2_ViridianForest_NorthEntrance_Frlg"),
    ("Gate_Route2_hns", "Route2_EastBuilding_Frlg"),
    ("Route2_House_hns", "Route2_House_Frlg"),
    ("Route5_House_hns", "Route5_PokemonDayCare_Frlg"),
    ("Route5_TunnelEntrance_hns", "UndergroundPath_NorthEntrance_Frlg"),
    ("Gate_SaffronCity_Route5_hns", "Route5_SouthEntrance_Frlg"),
    ("Gate_SaffronCity_Route6_hns", "Route6_NorthEntrance_Frlg"),
    ("Route6_TunnelEntrance_hns", "UndergroundPath_SouthEntrance_Frlg"),
    ("Gate_SaffronCity_Route7_hns", "Route7_EastEntrance_Frlg"),
    ("Route7_TunnelEntrance_hns", "UndergroundPath_WestEntrance_Frlg"),
    ("SaffronCity_Tunnel_NS_hns", "UndergroundPath_NorthSouthTunnel_Frlg"),
    ("SaffronCity_Tunnel_SW_hns", "UndergroundPath_EastWestTunnel_Frlg"),
    ("Gate_SaffronCity_Route8_hns", "Route8_WestEntrance_Frlg"),
    ("Route8_TunnelEntrance_hns", "UndergroundPath_EastEntrance_Frlg"),
    ("Route10_PowerPlantEntrance_hns", "PowerPlant_Frlg"),
    ("Route16_House_hns", "Route16_House_Frlg"),
    ("Gate_CeladonCity_Route16_hns", "Route16_NorthEntrance_1F_Frlg"),
    ("Gate_FuchsiaCity_Route18_hns", "Route18_EastEntrance_1F_Frlg"),
    ("Route12_House_hns", "Route12_FishingHouse_Frlg"),
    ("Route4_PokemonCenter_hns", "Route4_PokemonCenter_1F_Frlg"),
    ("Route9_PokemonCenter_hns", "Route10_PokemonCenter_1F_Frlg"),
    # Route 25 Sea Cottage was converted to a Magnet Train station on
    # LAYOUT_GOLDENROD_CITY_TRAIN_STATION_HNS. Do not restage the FRLG cottage.
]

DUNGEON_PAIRS = [
    ("ViridianForest_hns", "ViridianForest_Frlg"),
    ("MtMoon_Cave_hns", "MtMoon_1F_Frlg"),
    ("RockTunnel_1F_hns", "RockTunnel_1F_Frlg"),
    ("RockTunnel_B1F_hns", "RockTunnel_B1F_Frlg"),
    ("CeruleanCave_1F_hns", "CeruleanCave_1F_Frlg"),
    ("CeruleanCave_B1F_hns", "CeruleanCave_B1F_Frlg"),
    ("CeruleanCave_B2F_hns", "CeruleanCave_2F_Frlg"),
    ("DiglettsCave_EntranceNorth_hns", "DiglettsCave_NorthEntrance_Frlg"),
    ("DiglettsCave_EntranceSouth_hns", "DiglettsCave_SouthEntrance_Frlg"),
    ("DiglettsCave_Tunnel_hns", "DiglettsCave_B1F_Frlg"),
    ("SeafoamIslands_1F_hns", "SeafoamIslands_1F_Frlg"),
    ("SeafoamIslands_B1F_hns", "SeafoamIslands_B1F_Frlg"),
]

EXTRA_IMPORTS = [
    ("LavenderTown_RadioStation_hns", "gMapGroup_IndoorLavender_Frlg"),
    ("LavenderTown_House3_hns", "gMapGroup_IndoorLavender_Frlg"),
    ("VermilionCity_PortOutside_hns", "gMapGroup_IndoorVermilion_Frlg"),
    ("VermilionCity_PortInside_hns", "gMapGroup_IndoorVermilion_Frlg"),
    ("MtMoon_Outside_hns", "gMapGroup_Dungeons_Frlg"),
    ("MtMoon_Shop_hns", "gMapGroup_IndoorRoute4_Frlg"),
    ("Route19_Cave_hns", "gMapGroup_Dungeons_Frlg"),
    ("SaffronCity_TrainStation_hns", "gMapGroup_IndoorSaffron_Frlg"),
    ("SaffronCity_FightingDojoVIP_hns", "gMapGroup_IndoorSaffron_Frlg"),
    ("SeafoamIslands_Gym_hns", "gMapGroup_Dungeons_Frlg"),
    ("Route10_PowerPlantBackRoom_hns", "gMapGroup_IndoorRoute10_Frlg"),
]

EXPLICIT = {
    "MAP_PALLET_TOWN_REDS_HOUSE_1F_HNS": "MAP_PALLET_TOWN_PLAYERS_HOUSE_1F",
    "MAP_PALLET_TOWN_REDS_HOUSE_2F_HNS": "MAP_PALLET_TOWN_PLAYERS_HOUSE_2F",
    "MAP_PALLET_TOWN_HOUSE2_HNS": "MAP_PALLET_TOWN_RIVALS_HOUSE",
    "MAP_PALLET_TOWN_LAB_HNS": "MAP_PALLET_TOWN_PROFESSOR_OAKS_LAB",
    "MAP_VIRIDIAN_CITY_POKEMON_CENTER_HNS": "MAP_VIRIDIAN_CITY_POKEMON_CENTER_1F",
    "MAP_VIRIDIAN_CITY_HOUSE1_HNS": "MAP_VIRIDIAN_CITY_HOUSE",
    "MAP_LILYCOVE_CITY_CONTEST_LOBBY_HNS": "MAP_VIRIDIAN_CITY_SCHOOL",
    "MAP_ROUTE21_HNS": "MAP_ROUTE21_NORTH",
    "MAP_ROUTE22_HNS": "MAP_ROUTE22",
    "MAP_ROUTE23_HNS": "MAP_ROUTE23",
    "MAP_INDIGO_PLATEAU_HNS": "MAP_INDIGO_PLATEAU_EXTERIOR",
    "MAP_INDIGO_PLATEAU_POKEMON_CENTER_HNS": "MAP_INDIGO_PLATEAU_POKEMON_CENTER_1F",
    "MAP_CINNABAR_ISLAND_POKEMON_CENTER_HNS": "MAP_CINNABAR_ISLAND_POKEMON_CENTER_1F",
    "MAP_PEWTER_CITY_POKEMON_CENTER_HNS": "MAP_PEWTER_CITY_POKEMON_CENTER_1F",
    "MAP_CERULEAN_CITY_POKEMON_CENTER_HNS": "MAP_CERULEAN_CITY_POKEMON_CENTER_1F",
    "MAP_VERMILION_CITY_POKEMON_CENTER_HNS": "MAP_VERMILION_CITY_POKEMON_CENTER_1F",
    "MAP_LAVENDER_TOWN_POKEMON_CENTER_HNS": "MAP_LAVENDER_TOWN_POKEMON_CENTER_1F",
    "MAP_CELADON_CITY_POKEMON_CENTER_HNS": "MAP_CELADON_CITY_POKEMON_CENTER_1F",
    "MAP_SAFFRON_CITY_POKEMON_CENTER_HNS": "MAP_SAFFRON_CITY_POKEMON_CENTER_1F",
    "MAP_FUCHSIA_CITY_POKEMON_CENTER_HNS": "MAP_FUCHSIA_CITY_POKEMON_CENTER_1F",
    "MAP_VERMILION_CITY_FAN_CLUB_HNS": "MAP_VERMILION_CITY_POKEMON_FAN_CLUB",
    "MAP_DIGLETTS_CAVE_ENTRANCE_SOUTH_HNS": "MAP_DIGLETTS_CAVE_SOUTH_ENTRANCE",
    "MAP_DIGLETTS_CAVE_ENTRANCE_NORTH_HNS": "MAP_DIGLETTS_CAVE_NORTH_ENTRANCE",
    "MAP_DIGLETTS_CAVE_TUNNEL_HNS": "MAP_DIGLETTS_CAVE_B1F",
    "MAP_LAVENDER_TOWN_SOUL_HOUSE_HNS": "MAP_LAVENDER_TOWN_VOLUNTEER_POKEMON_HOUSE",
    "MAP_CELADON_CITY_APARTMENTS_1F_HNS": "MAP_CELADON_CITY_CONDOMINIUMS_1F",
    "MAP_CELADON_CITY_APARTMENTS_2F_HNS": "MAP_CELADON_CITY_CONDOMINIUMS_2F",
    "MAP_CELADON_CITY_APARTMENTS_3F_HNS": "MAP_CELADON_CITY_CONDOMINIUMS_3F",
    "MAP_CELADON_CITY_APARTMENTS_ROOF_DAY_HNS": "MAP_CELADON_CITY_CONDOMINIUMS_ROOF",
    "MAP_CELADON_CITY_APARTMENTS_ROOF_HOUSE_HNS": "MAP_CELADON_CITY_CONDOMINIUMS_ROOF_ROOM",
    "MAP_CELADON_CITY_HOUSE2_HNS": "MAP_CELADON_CITY_HOUSE1",
    "MAP_CELADON_CITY_DEPARTMENT_STORE_ROOF_DAY_HNS": "MAP_CELADON_CITY_DEPARTMENT_STORE_ROOF",
    "MAP_SAFFRON_CITY_FIGHTING_DOJO_HNS": "MAP_SAFFRON_CITY_DOJO",
    "MAP_SAFFRON_CITY_COPY_CATS_HOUSE_1F_HNS": "MAP_SAFFRON_CITY_COPYCATS_HOUSE_1F",
    "MAP_SAFFRON_CITY_COPY_CATS_HOUSE_2F_HNS": "MAP_SAFFRON_CITY_COPYCATS_HOUSE_2F",
    "MAP_SAFFRON_CITY_SILPH_CO_HNS": "MAP_SILPH_CO_1F",
    "MAP_SAFFRON_CITY_HOUSE1_HNS": "MAP_SAFFRON_CITY_MR_PSYCHICS_HOUSE",
    "MAP_FUCHSIA_CITY_SAFARI_ZONE_ENTRANCE_HNS": "MAP_FUCHSIA_CITY_SAFARI_ZONE_ENTRANCE",
    "MAP_GATE_SAFFRON_CITY_ROUTE5_HNS": "MAP_ROUTE5_SOUTH_ENTRANCE",
    "MAP_GATE_SAFFRON_CITY_ROUTE6_HNS": "MAP_ROUTE6_NORTH_ENTRANCE",
    "MAP_GATE_SAFFRON_CITY_ROUTE7_HNS": "MAP_ROUTE7_EAST_ENTRANCE",
    "MAP_GATE_SAFFRON_CITY_ROUTE8_HNS": "MAP_ROUTE8_WEST_ENTRANCE",
    "MAP_GATE_ROUTE2_VIRIDIAN_FOREST_HNS": "MAP_ROUTE2_VIRIDIAN_FOREST_SOUTH_ENTRANCE",
    "MAP_GATE_VIRIDIAN_FOREST_ROUTE2_HNS": "MAP_ROUTE2_VIRIDIAN_FOREST_NORTH_ENTRANCE",
    "MAP_GATE_ROUTE2_HNS": "MAP_ROUTE2_EAST_BUILDING",
    "MAP_MT_MOON_CAVE_HNS": "MAP_MT_MOON_1F",
    "MAP_ROUTE4_POKEMON_CENTER_HNS": "MAP_ROUTE4_POKEMON_CENTER_1F",
    "MAP_ROUTE5_HOUSE_HNS": "MAP_ROUTE5_POKEMON_DAY_CARE",
    "MAP_ROUTE5_TUNNEL_ENTRANCE_HNS": "MAP_UNDERGROUND_PATH_NORTH_ENTRANCE",
    "MAP_ROUTE6_TUNNEL_ENTRANCE_HNS": "MAP_UNDERGROUND_PATH_SOUTH_ENTRANCE",
    "MAP_ROUTE7_TUNNEL_ENTRANCE_HNS": "MAP_UNDERGROUND_PATH_WEST_ENTRANCE",
    "MAP_ROUTE8_TUNNEL_ENTRANCE_HNS": "MAP_UNDERGROUND_PATH_EAST_ENTRANCE",
    "MAP_SAFFRON_CITY_TUNNEL_NS_HNS": "MAP_UNDERGROUND_PATH_NORTH_SOUTH_TUNNEL",
    "MAP_SAFFRON_CITY_TUNNEL_SW_HNS": "MAP_UNDERGROUND_PATH_EAST_WEST_TUNNEL",
    "MAP_ROUTE9_POKEMON_CENTER_HNS": "MAP_ROUTE10_POKEMON_CENTER_1F",
    "MAP_ROCK_TUNNEL_B1F_HNS": "MAP_ROCK_TUNNEL_1F",
    "MAP_ROCK_TUNNEL_1F_HNS": "MAP_ROCK_TUNNEL_B1F",
    "MAP_ROUTE10_POWER_PLANT_ENTRANCE_HNS": "MAP_POWER_PLANT",
    "MAP_GATE_CELADON_CITY_ROUTE16_HNS": "MAP_ROUTE16_NORTH_ENTRANCE_1F",
    "MAP_GATE_FUCHSIA_CITY_ROUTE18_HNS": "MAP_ROUTE18_EAST_ENTRANCE_1F",
    "MAP_FUCHSIA_CITY_ROUTE15_GATE_HNS": "MAP_ROUTE15_WEST_ENTRANCE_1F",
    "MAP_ROUTE12_HOUSE_HNS": "MAP_ROUTE12_FISHING_HOUSE",
    "MAP_ROUTE25_BILLS_HOUSE_HNS": "MAP_ROUTE25_SEA_COTTAGE",
    "MAP_SEAFOAM_ISLANDS_1F_HNS": "MAP_SEAFOAM_ISLANDS_1F",
    "MAP_CERULEAN_CAVE_1F_HNS": "MAP_CERULEAN_CAVE_1F",
    "MAP_CERULEAN_CAVE_B1F_HNS": "MAP_CERULEAN_CAVE_B1F",
    "MAP_CERULEAN_CAVE_B2F_HNS": "MAP_CERULEAN_CAVE_2F",
    "MAP_VIRIDIAN_FOREST_HNS": "MAP_VIRIDIAN_FOREST",
    "MAP_VICTORY_ROAD_KANTO_1F_HNS": "MAP_VICTORY_ROAD_KANTO_1F_HNS",
    "MAP_RECEPTION_GATE_HNS": "MAP_RECEPTION_GATE_HNS",
    "MAP_ROUTE26NORTH_HNS": "MAP_ROUTE26NORTH_HNS",
    "MAP_ROUTE26_HNS": "MAP_ROUTE26_HNS",
}

DROP_PREFIXES = (
    "MAP_NEW_BARK_TOWN",
    "MAP_TEST_",
    "MAP_TIN_TOWER_ROOF",
    "MAP_LILYCOVE_CITY_CONTEST",
)

# Pallet outdoor stays MAP_PALLET_TOWN on LAYOUT_PALLET_TOWN_HNS (same 24×20
# doors). Keep the Indigo preview objects. The HnS lab is the FRLG 13×14
# aisle shifted by (+7, +8): door (6,12)→(13,20), Oak (6,3)→(13,11).
KEEP_FRLG_OBJECTS = {"PalletTown_Frlg"}
PALLET_LAB_FRLG = "PalletTown_ProfessorOaksLab_Frlg"
PALLET_LAB_DX = 7
PALLET_LAB_DY = 8
OBJECT_CAP = 16
FIELD_TEMP_FLAGS = [f"FLAG_TEMP_{n:X}" for n in range(0x11, 0x1F)]
FIELD_GFX_MAP = {
    "OBJ_EVENT_GFX_CUTTABLE_TREE_HNS": ("OBJ_EVENT_GFX_CUTTABLE_TREE_FRLG", "EventScript_CutTree"),
    "OBJ_EVENT_GFX_CUTTABLE_TREE_FRLG": ("OBJ_EVENT_GFX_CUTTABLE_TREE_FRLG", "EventScript_CutTree"),
    "OBJ_EVENT_GFX_CUTTABLE_TREE": ("OBJ_EVENT_GFX_CUTTABLE_TREE_FRLG", "EventScript_CutTree"),
    "OBJ_EVENT_GFX_BREAKABLE_ROCK_HNS": ("OBJ_EVENT_GFX_BREAKABLE_ROCK_FRLG", "EventScript_RockSmash"),
    "OBJ_EVENT_GFX_BREAKABLE_ROCK_FRLG": ("OBJ_EVENT_GFX_BREAKABLE_ROCK_FRLG", "EventScript_RockSmash"),
    "OBJ_EVENT_GFX_BREAKABLE_ROCK": ("OBJ_EVENT_GFX_BREAKABLE_ROCK_FRLG", "EventScript_RockSmash"),
    "OBJ_EVENT_GFX_PUSHABLE_BOULDER_HNS": ("OBJ_EVENT_GFX_PUSHABLE_BOULDER_FRLG", "EventScript_StrengthBoulder"),
    "OBJ_EVENT_GFX_PUSHABLE_BOULDER_FRLG": ("OBJ_EVENT_GFX_PUSHABLE_BOULDER_FRLG", "EventScript_StrengthBoulder"),
    "OBJ_EVENT_GFX_PUSHABLE_BOULDER": ("OBJ_EVENT_GFX_PUSHABLE_BOULDER_FRLG", "EventScript_StrengthBoulder"),
}
GFX_FAMILY_ALIAS = {
    "OFFICER": "POLICEMAN",
    "BOY_2": "YOUNGSTER",
    "FISHERMAN": "FISHER",
    "OLD_MAN_1": "OLD_MAN",
    "OLD_MAN_2": "OLD_MAN",
    "LT_SURGE": "SURGE",
}

HEAL_FROM_HNS_WARP = {
    "HEAL_LOCATION_PALLET_TOWN": ("PalletTown_hns", "MAP_PALLET_TOWN_REDS_HOUSE_1F_HNS"),
    "HEAL_LOCATION_VIRIDIAN_CITY": ("ViridianCity_hns", "MAP_VIRIDIAN_CITY_POKEMON_CENTER_HNS"),
    "HEAL_LOCATION_PEWTER_CITY": ("PewterCity_hns", "MAP_PEWTER_CITY_POKEMON_CENTER_HNS"),
    "HEAL_LOCATION_CERULEAN_CITY": ("CeruleanCity_hns", "MAP_CERULEAN_CITY_POKEMON_CENTER_HNS"),
    "HEAL_LOCATION_LAVENDER_TOWN": ("LavenderTown_hns", "MAP_LAVENDER_TOWN_POKEMON_CENTER_HNS"),
    "HEAL_LOCATION_VERMILION_CITY": ("VermilionCity_hns", "MAP_VERMILION_CITY_POKEMON_CENTER_HNS"),
    "HEAL_LOCATION_CELADON_CITY": ("CeladonCity_hns", "MAP_CELADON_CITY_POKEMON_CENTER_HNS"),
    "HEAL_LOCATION_FUCHSIA_CITY": ("FuchsiaCity_hns", "MAP_FUCHSIA_CITY_POKEMON_CENTER_HNS"),
    "HEAL_LOCATION_SAFFRON_CITY": ("SaffronCity_hns", "MAP_SAFFRON_CITY_POKEMON_CENTER_HNS"),
    "HEAL_LOCATION_INDIGO_PLATEAU": ("IndigoPlateau_hns", "MAP_INDIGO_PLATEAU_POKEMON_CENTER_HNS"),
    "HEAL_LOCATION_ROUTE4": ("Route4_hns", "MAP_ROUTE4_POKEMON_CENTER_HNS"),
    "HEAL_LOCATION_ROUTE10": ("Route10_hns", "MAP_ROUTE9_POKEMON_CENTER_HNS"),
}

INDIGO_MAP_IDS: dict[str, str] = {}


def dump(path: Path, data) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n")


def load_indigo_ids() -> dict[str, str]:
    ids = {}
    for path in (ROOT / "data/maps").glob("*/map.json"):
        data = json.loads(path.read_text())
        ids[data["id"]] = path.parent.name
    return ids


def remap_dest(dest: str | None) -> str | None:
    if not dest:
        return None
    if dest in EXPLICIT:
        return EXPLICIT[dest]
    if any(dest.startswith(prefix) for prefix in DROP_PREFIXES):
        return None
    if dest in INDIGO_MAP_IDS:
        return dest
    if dest.endswith("_HNS"):
        base = dest[: -len("_HNS")]
        if base in INDIGO_MAP_IDS:
            return base
        for suffix in ("_1F", "_EXTERIOR"):
            if base + suffix in INDIGO_MAP_IDS:
                return base + suffix
    return None


def ensure_hns_folders(folders: list[str]) -> None:
    missing = [folder for folder in folders if not (HNS / "data/maps" / folder / "map.json").exists()]
    if not missing:
        return
    paths = []
    for folder in missing:
        paths.append(f"data/maps/{folder}")
        paths.append(f"data/layouts/{folder}")
    print("sparse-checkout add", len(missing), "HnS folders")
    subprocess.check_call(["git", "-C", str(HNS), "sparse-checkout", "add", *paths])


def layout_size(hns_layouts: dict, folder: str) -> tuple[int, int]:
    entry = hns_layouts.get(folder)
    if not entry:
        return (999, 999)
    return int(entry.get("width", 999)), int(entry.get("height", 999))


def in_bounds(x, y, width, height) -> bool:
    return 0 <= int(x) < width and 0 <= int(y) < height


def load_original_map(folder: str) -> dict:
    try:
        raw = subprocess.check_output(
            ["git", "-C", str(ROOT), "show", f"HEAD:data/maps/{folder}/map.json"],
            stderr=subprocess.DEVNULL,
        )
        return json.loads(raw)
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        return json.loads((ROOT / "data/maps" / folder / "map.json").read_text())


def gfx_family(gfx: str) -> str:
    name = gfx.replace("OBJ_EVENT_GFX_", "")
    if "SPECIES_" in name:
        name = name.split("SPECIES_")[-1]
    if name.endswith("_HNS"):
        name = name[: -len("_HNS")]
    if name.endswith("_FRLG"):
        name = name[: -len("_FRLG")]
    return GFX_FAMILY_ALIAS.get(name, name)


def script_key(script: str | None) -> str:
    if not script or script in ("0", "0x0", "NULL"):
        return ""
    if "_EventScript_" in script:
        return script.split("_EventScript_")[-1].lower()
    return script.lower()


def is_field_gfx(gfx: str) -> bool:
    return any(token in gfx for token in ("CUTTABLE_TREE", "BREAKABLE_ROCK", "PUSHABLE_BOULDER"))


def skip_hns_object(gfx: str) -> bool:
    if gfx.startswith("OBJ_EVENT_GFX_MON_BASE"):
        return True
    if "SMALL_LIGHT" in gfx or "WHIRLPOOL" in gfx or "TOWER_BEAM" in gfx:
        return True
    if gfx == "OBJ_EVENT_GFX_BERRY_TREE":
        return True
    return False


def collision_grid(layout_entry: dict | None) -> tuple[int, int, list[int]] | None:
    if not layout_entry:
        return None
    path = ROOT / layout_entry.get("blockdata_filepath", "")
    if not path.exists():
        path = HNS / layout_entry.get("blockdata_filepath", "")
    if not path.exists():
        return None
    width = int(layout_entry["width"])
    height = int(layout_entry["height"])
    data = path.read_bytes()
    tiles = list(struct.unpack("<" + "H" * (len(data) // 2), data))
    return width, height, tiles


def tile_blocked(grid, x, y) -> bool:
    if not grid:
        return False
    width, height, tiles = grid
    if not (0 <= int(x) < width and 0 <= int(y) < height):
        return True
    return bool((tiles[int(y) * width + int(x)] >> 10) & 0x3)


# Round 2x2 trees / hedges in kanto_general_hns and the Johto outdoor generals.
# HnS map.bin leaves a few of these walkable (Route 1 (12,7) and (12,17) are
# tree trunks with collision 0). FRLG only reads map.bin bits 10-11, so those
# tiles are passable. Bake collision onto every outdoor cell that uses them.
OUTDOOR_TREE_PRIMARIES = {
    "gTileset_Kanto_General_Hns",
    "gTileset_Johto_General_Hns",
    "gTileset_Johto_South_Hns",
    "gTileset_Johto_NorthEast_Hns",
    "gTileset_Johto_NorthWest_Hns",
}
# Primary metatile ids 18-39 are the round tree / cliff cluster in kanto_general
# (and the matching Johto generals). 121 is the hedge row.
OUTDOOR_TREE_METATILES = frozenset(range(18, 40)) | {121}


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


def nudge_walkable(grid, x, y, avoid_aisle=False) -> tuple[int, int]:
    if not grid:
        return int(x), int(y)
    width, height, _ = grid
    start = (int(x), int(y))

    def ok(px, py):
        if not in_bounds(px, py, width, height) or tile_blocked(grid, px, py):
            return False
        if avoid_aisle and px in (12, 13, 14) and py >= 18:
            return False
        return True

    if ok(*start):
        return start
    for radius in range(1, 12):
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if max(abs(dx), abs(dy)) != radius:
                    continue
                cand = (start[0] + dx, start[1] + dy)
                if ok(*cand):
                    return cand
    return start


def merge_warps(frlg_warps: list | None, hns_warps: list | None, width: int, height: int) -> list:
    used = set()
    dest_xy: dict[str, tuple] = {}
    out = []
    for frlg in frlg_warps or []:
        rewritten = dict(frlg)
        dest = frlg.get("dest_map")
        match = None
        for index, hns in enumerate(hns_warps or []):
            if index in used:
                continue
            if remap_dest(hns.get("dest_map")) == dest:
                match = index
                break
        if match is not None:
            used.add(match)
            hns = hns_warps[match]
            rewritten["x"] = hns["x"]
            rewritten["y"] = hns["y"]
            rewritten["elevation"] = hns.get("elevation", 0)
            dest_xy.setdefault(dest, (hns["x"], hns["y"], hns.get("elevation", 0)))
            out.append(rewritten)
        elif dest in dest_xy:
            x, y, elev = dest_xy[dest]
            rewritten["x"] = x
            rewritten["y"] = y
            rewritten["elevation"] = elev
            out.append(rewritten)
        elif in_bounds(frlg.get("x", 0), frlg.get("y", 0), width, height) and dest and any(
            token in dest
            for token in ("SS_ANNE", "POKEMON_TOWER", "SILPH_CO", "SAFARI_ZONE", "ROCKET", "POKEMON_MANSION")
        ):
            out.append(rewritten)
    for index, hns in enumerate(hns_warps or []):
        if index in used:
            continue
        dest = remap_dest(hns.get("dest_map"))
        if not dest:
            continue
        extra = dict(hns)
        extra["dest_map"] = dest
        extra["dest_warp_id"] = str(hns.get("dest_warp_id", "0"))
        extra.setdefault("elevation", 0)
        extra.setdefault("type", "warp")
        extra.pop("kind", None)
        out.append(extra)
    return out


def rewrite_connections(hns_conns: list | None) -> list | None:
    out = []
    for conn in hns_conns or []:
        dest = remap_dest(conn.get("map"))
        if not dest:
            continue
        out.append({"map": dest, "offset": conn.get("offset", 0), "direction": conn["direction"]})
    return out or None


def clip_events(events: list | None, width: int, height: int, xkey="x", ykey="y") -> list:
    kept = []
    for event in events or []:
        if in_bounds(event.get(xkey, 0), event.get(ykey, 0), width, height):
            kept.append(event)
    return kept


def match_score(frlg: dict, hns: dict) -> int:
    score = 0
    fs, hs = script_key(frlg.get("script")), script_key(hns.get("script"))
    if fs and fs == hs:
        score += 100
    elif fs and hs and (fs in hs or hs in fs):
        score += 55
    fl = (frlg.get("local_id") or "").replace("LOCALID_", "")
    hl = (hns.get("local_id") or "").replace("LOCALID_", "").replace("_HNS", "")
    if fl and hl and (fl == hl or fl in hl or hl in fl):
        score += 80
    ff, hf = gfx_family(frlg.get("graphics_id", "")), gfx_family(hns.get("graphics_id", ""))
    if ff and ff == hf:
        score += 50
    ft = frlg.get("trainer_type", "TRAINER_TYPE_NONE")
    ht = hns.get("trainer_type", "TRAINER_TYPE_NONE")
    if ft == ht and ft != "TRAINER_TYPE_NONE":
        score += 20
    return score


def field_object_from_hns(hns_obj: dict, flag: str) -> dict:
    gfx = hns_obj.get("graphics_id", "")
    mapped, script = FIELD_GFX_MAP.get(gfx, ("OBJ_EVENT_GFX_CUTTABLE_TREE_FRLG", "EventScript_CutTree"))
    if "BREAKABLE_ROCK" in gfx:
        mapped, script = FIELD_GFX_MAP.get(gfx, ("OBJ_EVENT_GFX_BREAKABLE_ROCK_FRLG", "EventScript_RockSmash"))
    if "PUSHABLE_BOULDER" in gfx:
        mapped, script = FIELD_GFX_MAP.get(gfx, ("OBJ_EVENT_GFX_PUSHABLE_BOULDER_FRLG", "EventScript_StrengthBoulder"))
    out = {
        "type": "object",
        "graphics_id": mapped,
        "x": hns_obj["x"],
        "y": hns_obj["y"],
        "elevation": hns_obj.get("elevation", 3),
        "movement_type": "MOVEMENT_TYPE_FACE_DOWN",
        "movement_range_x": 1,
        "movement_range_y": 1,
        "trainer_type": "TRAINER_TYPE_NONE",
        "trainer_sight_or_berry_tree_id": "0",
        "script": script,
        "flag": flag,
    }
    if "local_id" in hns_obj:
        out = {"local_id": hns_obj["local_id"], **out}
    return out


def restage_lab_objects(frlg_objects: list, grid) -> list:
    furniture = ("OBJ_EVENT_GFX_ITEM_BALL", "OBJ_EVENT_GFX_POKEDEX")
    out = []
    for obj in frlg_objects or []:
        if obj.get("type") == "clone":
            continue
        rewritten = dict(obj)
        rewritten["x"] = int(obj.get("x", 0)) + PALLET_LAB_DX
        rewritten["y"] = int(obj.get("y", 0)) + PALLET_LAB_DY
        gfx = obj.get("graphics_id", "")
        if gfx not in furniture:
            rewritten["x"], rewritten["y"] = nudge_walkable(
                grid, rewritten["x"], rewritten["y"], avoid_aisle=True
            )
        out.append(rewritten)
    return out[:OBJECT_CAP]


def restage_objects(frlg_objects: list | None, hns_objects: list | None, frlg_folder: str, grid) -> list:
    original = [dict(obj) for obj in (frlg_objects or [])]
    if frlg_folder == PALLET_LAB_FRLG:
        return restage_lab_objects(original, grid)
    if frlg_folder in KEEP_FRLG_OBJECTS:
        return original[:OBJECT_CAP]

    hns_list = hns_objects or []
    field = []
    for index, hns_obj in enumerate(hns_list):
        gfx = hns_obj.get("graphics_id", "")
        if is_field_gfx(gfx):
            flag = FIELD_TEMP_FLAGS[len(field) % len(FIELD_TEMP_FLAGS)]
            field.append(field_object_from_hns(hns_obj, flag))

    frlg_npcs = [
        obj
        for obj in original
        if obj.get("type") != "clone" and not is_field_gfx(obj.get("graphics_id", ""))
    ]
    hns_npcs = [
        (index, obj)
        for index, obj in enumerate(hns_list)
        if not is_field_gfx(obj.get("graphics_id", ""))
    ]
    pairs = []
    for fi, frlg in enumerate(frlg_npcs):
        for hi, hns in hns_npcs:
            score = match_score(frlg, hns)
            if score >= 50:
                pairs.append((score, fi, hi))
    pairs.sort(reverse=True)
    used_f, used_h = set(), set()
    restaged = []
    for score, fi, hi in pairs:
        if fi in used_f or hi in used_h:
            continue
        used_f.add(fi)
        used_h.add(hi)
        frlg = dict(frlg_npcs[fi])
        hns = next(obj for index, obj in hns_npcs if index == hi)
        frlg["x"] = hns["x"]
        frlg["y"] = hns["y"]
        frlg["elevation"] = hns.get("elevation", frlg.get("elevation", 3))
        frlg["movement_type"] = hns.get("movement_type", frlg.get("movement_type"))
        frlg["movement_range_x"] = hns.get("movement_range_x", frlg.get("movement_range_x", 0))
        frlg["movement_range_y"] = hns.get("movement_range_y", frlg.get("movement_range_y", 0))
        restaged.append(frlg)

    leftovers = []
    for fi, frlg in enumerate(frlg_npcs):
        if fi in used_f:
            continue
        leftover = dict(frlg)
        if tile_blocked(grid, leftover.get("x", 0), leftover.get("y", 0)):
            leftover["x"], leftover["y"] = nudge_walkable(grid, leftover.get("x", 0), leftover.get("y", 0))
        leftovers.append(leftover)

    combined = restaged + leftovers + field
    combined.sort(key=lambda obj: (0 if obj.get("local_id") else 1, 0 if is_field_gfx(obj.get("graphics_id", "")) else 1))
    return combined[:OBJECT_CAP]


def restage_coord_events(frlg_coords: list | None, hns_coords: list | None, frlg_folder: str, width: int, height: int) -> list:
    original = [dict(ev) for ev in (frlg_coords or [])]
    if frlg_folder == PALLET_LAB_FRLG:
        out = []
        for ev in original:
            rewritten = dict(ev)
            rewritten["x"] = int(ev.get("x", 0)) + PALLET_LAB_DX
            rewritten["y"] = int(ev.get("y", 0)) + PALLET_LAB_DY
            out.append(rewritten)
        return out
    hns_list = list(hns_coords or [])
    used = set()
    out = []
    for ev in original:
        match = None
        key = ev.get("script")
        for index, hns in enumerate(hns_list):
            if index in used:
                continue
            if hns.get("script") == key:
                match = index
                break
        if match is not None:
            used.add(match)
            rewritten = dict(ev)
            rewritten["x"] = hns_list[match]["x"]
            rewritten["y"] = hns_list[match]["y"]
            rewritten["elevation"] = hns_list[match].get("elevation", ev.get("elevation", 0))
            out.append(rewritten)
        elif in_bounds(ev.get("x", 0), ev.get("y", 0), width, height):
            out.append(ev)
    return out


def restage_bg_events(frlg_bg: list | None, hns_bg: list | None, frlg_folder: str, width: int, height: int) -> list:
    original = [dict(ev) for ev in (frlg_bg or [])]
    if frlg_folder == PALLET_LAB_FRLG:
        out = []
        for ev in original:
            rewritten = dict(ev)
            rewritten["x"] = int(ev.get("x", 0)) + PALLET_LAB_DX
            rewritten["y"] = int(ev.get("y", 0)) + PALLET_LAB_DY
            out.append(rewritten)
        return out
    hns_list = [ev for ev in (hns_bg or []) if ev.get("type") != "hidden_item"]
    used = set()
    out = []
    unmatched = []
    for ev in original:
        if ev.get("type") == "hidden_item":
            if in_bounds(ev.get("x", 0), ev.get("y", 0), width, height):
                out.append(ev)
            continue
        match = None
        key = script_key(ev.get("script"))
        for index, hns in enumerate(hns_list):
            if index in used:
                continue
            if script_key(hns.get("script")) == key and key:
                match = index
                break
        if match is not None:
            used.add(match)
            rewritten = dict(ev)
            rewritten["x"] = hns_list[match]["x"]
            rewritten["y"] = hns_list[match]["y"]
            rewritten["elevation"] = hns_list[match].get("elevation", ev.get("elevation", 0))
            out.append(rewritten)
        else:
            unmatched.append(ev)
    leftover_hns = [hns for index, hns in enumerate(hns_list) if index not in used]
    paired = min(len(unmatched), len(leftover_hns))
    for ev, hns in zip(unmatched[:paired], leftover_hns[:paired]):
        rewritten = dict(ev)
        rewritten["x"] = hns["x"]
        rewritten["y"] = hns["y"]
        rewritten["elevation"] = hns.get("elevation", ev.get("elevation", 0))
        out.append(rewritten)
    for ev in unmatched[paired:]:
        if in_bounds(ev.get("x", 0), ev.get("y", 0), width, height):
            out.append(ev)
    return out


def remap_inplace(hns_folder: str, frlg_folder: str, hns_layouts: dict) -> None:
    hns = json.loads((HNS / "data/maps" / hns_folder / "map.json").read_text())
    dest_path = ROOT / "data/maps" / frlg_folder / "map.json"
    live = json.loads(dest_path.read_text())
    original = load_original_map(frlg_folder)
    width, height = layout_size(hns_layouts, hns_folder)
    grid = collision_grid(hns_layouts.get(hns_folder))
    live["layout"] = hns["layout"]
    live["connections"] = rewrite_connections(hns.get("connections"))
    live["warp_events"] = merge_warps(original.get("warp_events"), hns.get("warp_events"), width, height)
    live["object_events"] = restage_objects(
        original.get("object_events"), hns.get("object_events"), frlg_folder, grid
    )
    live["coord_events"] = restage_coord_events(
        original.get("coord_events"), hns.get("coord_events"), frlg_folder, width, height
    )
    live["bg_events"] = restage_bg_events(
        original.get("bg_events"), hns.get("bg_events"), frlg_folder, width, height
    )
    dump(dest_path, live)


def patch_pallet_intro_scripts() -> None:
    outdoor = ROOT / "data/maps/PalletTown_Frlg/scripts.inc"
    text = outdoor.read_text()
    text = text.replace(
        "warp MAP_PALLET_TOWN_PROFESSOR_OAKS_LAB, 6, 12",
        "warp MAP_PALLET_TOWN_PROFESSOR_OAKS_LAB, 13, 20",
    )
    outdoor.write_text(text)

    lab = ROOT / "data/maps/PalletTown_ProfessorOaksLab_Frlg/scripts.inc"
    text = lab.read_text()
    replacements = (
        ("setobjectxyperm LOCALID_OAKS_LAB_PROF_OAK, 6, 11", "setobjectxyperm LOCALID_OAKS_LAB_PROF_OAK, 13, 19"),
        ("setobjectxyperm LOCALID_OAKS_LAB_PROF_OAK, 6, 3", "setobjectxyperm LOCALID_OAKS_LAB_PROF_OAK, 13, 11"),
        ("setobjectxyperm LOCALID_OAKS_LAB_RIVAL, 5, 10", "setobjectxyperm LOCALID_OAKS_LAB_RIVAL, 12, 18"),
        ("setobjectxyperm LOCALID_OAKS_LAB_RIVAL, 6, 10", "setobjectxyperm LOCALID_OAKS_LAB_RIVAL, 13, 18"),
    )
    for old, new in replacements:
        text = text.replace(old, new)
    lab.write_text(text)


def disconnect_route21_south() -> None:
    path = ROOT / "data/maps/Route21_South_Frlg/map.json"
    data = json.loads(path.read_text())
    data["connections"] = None
    dump(path, data)


def retarget_indigo_pc() -> None:
    path = ROOT / "data/maps/IndigoPlateau_PokemonCenter_1F_Frlg/map.json"
    data = json.loads(path.read_text())
    for warp in data.get("warp_events") or []:
        if warp.get("dest_map") == "MAP_INDIGO_PLATEAU_HNS":
            warp["dest_map"] = "MAP_INDIGO_PLATEAU_EXTERIOR"
    dump(path, data)


def update_heals() -> None:
    path = ROOT / "src/data/heal_locations.json"
    data = json.loads(path.read_text())
    for entry in data["heal_locations"]:
        spec = HEAL_FROM_HNS_WARP.get(entry["id"])
        if not spec:
            continue
        folder, dest = spec
        hns = json.loads((HNS / "data/maps" / folder / "map.json").read_text())
        for warp in hns.get("warp_events") or []:
            if warp.get("dest_map") == dest:
                entry["x"] = warp["x"]
                entry["y"] = warp["y"] + 1
                break
    dump(path, data)


def splice_extra_groups(extras: list[tuple[str, str]]) -> None:
    path = ROOT / "data/maps/map_groups.json"
    data = json.loads(path.read_text())
    for folder, group in extras:
        if group not in data:
            raise SystemExit(f"missing map group {group}")
        if folder not in data[group]:
            data[group].append(folder)
        if len(data[group]) > 256:
            raise SystemExit(f"{group} exceeds MAP_NUM cap")
    dump(path, data)


def patch_extra_scripts(folders: list[str]) -> None:
    path = ROOT / "data/event_scripts.s"
    text = path.read_text()
    missing = [
        f'\t.include "data/maps/{folder}/scripts.inc"'
        for folder in folders
        if f"data/maps/{folder}/scripts.inc" not in text
    ]
    if not missing:
        return
    needle = '\t.include "data/maps/PalletTown_ProfessorOaksLab_Frlg/scripts.inc"\n'
    if needle not in text:
        raise SystemExit("Could not splice extra scripts into event_scripts.s")
    path.write_text(text.replace(needle, needle + "\n".join(missing) + "\n", 1))


def layouts_by_folder(raw: list[dict]) -> dict[str, dict]:
    out = {}
    for entry in raw:
        border = entry.get("border_filepath", "")
        if border.startswith("data/layouts/") and border.endswith("/border.bin"):
            out[border[len("data/layouts/") : -len("/border.bin")]] = entry
    return out


def main() -> None:
    global INDIGO_MAP_IDS
    restage_only = "--restage-only" in sys.argv
    bake_only = "--bake-collision" in sys.argv
    if bake_only:
        bake_hns_collision()
        return
    if not (HNS / "data/maps/PalletTown_hns/map.json").exists():
        raise SystemExit(f"HnS checkout missing Pallet at {HNS}")

    pairs = OUTDOOR_PAIRS + INTERIOR_PAIRS + DUNGEON_PAIRS
    extra_folders = [folder for folder, _ in EXTRA_IMPORTS]
    all_hns = [h for h, _ in pairs] + extra_folders
    ensure_hns_folders(all_hns)

    missing = [folder for folder in all_hns if not (HNS / "data/maps" / folder / "map.json").exists()]
    if missing:
        raise SystemExit("HnS maps still missing: " + ", ".join(missing))

    hns_layout_list = json.loads((HNS / "data/layouts/layouts.json").read_text())["layouts"]
    hns_layouts = layouts_by_folder(hns_layout_list)

    if not restage_only:
        hs.TILESETS = hs.collect_tilesets(all_hns, hns_layout_list)
        for kind, folder, *_ in hs.TILESETS:
            hs.copy_tileset(kind, folder)

        new_layouts = [hs.copy_layout(folder, hns_layout_list) for folder in all_hns]
        hs.splice_layouts(new_layouts)
        hs.patch_tileset_sources()

    INDIGO_MAP_IDS = load_indigo_ids()
    hs.MAPS = extra_folders
    hs.load_imported_ids()
    hs.WARP_REMAP.update({key: value for key, value in EXPLICIT.items() if value})
    hs.CONNECTION_REMAP.update({key: value for key, value in EXPLICIT.items() if value})
    hs.EXTERNAL_MAP_IDS.update(INDIGO_MAP_IDS.keys())
    hs.IMPORTED_MAP_IDS.update(INDIGO_MAP_IDS.keys())

    if not restage_only:
        rewritten = []
        for folder in extra_folders:
            if (ROOT / "data/maps" / folder / "map.json").exists():
                continue
            rewritten.append(hs.rewrite_map(folder))
        if rewritten:
            hs.write_shared_stubs(rewritten)
            splice_extra_groups(EXTRA_IMPORTS)
            patch_extra_scripts(extra_folders)

    INDIGO_MAP_IDS = load_indigo_ids()

    skipped = []
    for hns_folder, frlg_folder in pairs:
        dest = ROOT / "data/maps" / frlg_folder / "map.json"
        if not dest.exists():
            skipped.append(frlg_folder)
            continue
        remap_inplace(hns_folder, frlg_folder, hns_layouts)
    if skipped:
        print("skipped missing FRLG maps:", ", ".join(skipped))

    disconnect_route21_south()
    retarget_indigo_pc()
    update_heals()
    patch_pallet_intro_scripts()
    bake_hns_collision()
    print("Remapped", len(pairs) - len(skipped), "in-place maps;", len(extra_folders), "extra imports")


if __name__ == "__main__":
    main()
