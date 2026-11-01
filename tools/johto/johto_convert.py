#!/usr/bin/env python3
"""Translate GSC/Crystal Johto map images (Bulbapedia archives) into FRLG-tileset layouts.

Same pipeline as tools/cherrygrove/convert_cherrygrove.py, generalised:
  * 1 GSC 16x16 px cell -> 1 FRLG metatile (same pixel scale).
  * Every distinct cell across all source images has a global id (cells.json, built by
    tools/johto/cells.py); CLASS below labels each id with a semantic class by hand.
  * Classes are drawn with gTileset_General_Frlg + one FRLG secondary tileset per map.
  * Mountains and sand paths use a tiler *learned from the existing FRLG maps*
    (learn_tiles.Learned): for each cell the metatile FRLG itself uses most often for the
    same neighbourhood shape.  Forest/grey path/sea use the hand-written Cherrygrove rules.
  * Buildings are copied verbatim (incl. collision/elevation) out of existing FRLG maps.
  * Collision/elevation for every other metatile = its most common value in FRLG layouts.

Usage: python3 tools/johto/johto_convert.py [MapName ...]      (default: all maps)
Writes data/layouts/<Map>/{map.bin,border.bin}, data/maps/<Map>/{map.json,scripts.inc}
and tools/johto/out/<Map>_semantic.txt.
"""
import collections, json, os, struct, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'cherrygrove'))
from fr_render import REPO, Tilesets
from tsdir import tileset_dir
from learn_tiles import Learned, frlg_layouts
from families import mountain_family

SRC_DIR = os.environ.get('JOHTO_SRC', '/workspace/johto_src')

# ------------------------------------------------------------------ semantic classes
# T forest tree | U lone small tree/bush | P path | G lawn | F flowers | H tall grass
# W water | R rocks in water | B0..B3 2x2 boulder (TL,TR,BL,BR) | M mountain/cliff mass
# C cave mouth | L ledge (jump south) | VL / VR vertical ledge line on the left / right side
# S sign | X building/gate (must be covered by a stamped FRLG building or xfill)
CLASS = {}
def _set(cls, *ids):
    for i in ids:
        assert i not in CLASS, i
        CLASS[i] = cls
_set('T', 0, 8, 15, 70, 71, 76)
_set('U', 88, 89)
_set('P', 1)
_set('G', 16)
_set('F', 31, 35, 102, 106)
_set('H', 82)
_set('W', 5, 6, 7, 22, 38, 39, 47, 48, 93, 94, 95, 96, 97, 101, 146)
_set('R', 27)
_set('B0', 23, 139); _set('B1', 24, 140); _set('B2', 25, 141); _set('B3', 26, 142)
_set('M', 37, 40, 41, 42, 43, 45, 46, 49, 63, 64, 65, 90, 91, 92, 107, 108, 110,
     138, 143, 144, 145, 147, 155, 156)
_set('C', 44, 109)
_set('X', 121, 122)   # Route 32/36 gate side wall (phase 5)
_set('L', 62, 69, 84, 85, 87)
_set('VR', 81, 114)
_set('VL', 86)
_set('S', 36, 83)
_set('X', 2, 3, 4, 9, 10, 11, 12, 13, 14, 17, 18, 19, 20, 21, 28, 29, 30, 32, 33, 34,
     50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 66, 67, 68, 72, 73, 74, 75, 77, 78,
     79, 80, 98, 99, 100, 103, 104, 105, 111, 112, 113, 115, 116, 117, 118, 119, 120,
     123, 124, 125, 126, 130, 131, 132, 133, 134, 135, 137, 148, 149, 150, 151, 152, 153,
     154, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177,
     178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195)
# phase 3 (Ecruteak, New Bark, Routes 26-28, Mt. Silver exterior)
_set('W', 129, 230)                      # pier edge over water, whirlpool (no FRLG whirlpool -> water)
_set('VR', 136, 304)                     # walkable left, rock line right
_set('VL', 299)                          # rock line left, walkable right
_set('M', 231, 232, 233, 238, 239, 248, 249, 262, *range(273, 283), 312, 313, 314)
_set('G', 243, *range(266, 271), *range(305, 311))   # lawn, pond rims
_set('T', 234, 283)
_set('X', *range(196, 230), 235, 236, 237, 240, 241, 242, 244, 245, 246, 247,
     *range(250, 256), 258, 259, 260, *range(285, 299))
_set('L', 256, 263, 264, 265, 271, 272, 300, 301, 302, 303, 311)
_set('S', 257, 284)
_set('H', 261)

# ------------------------------------------------------------------ FRLG metatiles
FOREST_TOP, FOREST_BOT, FOREST_TRUNK = (0x01C, 0x01D), (0x014, 0x015), (0x024, 0x025)
FOREST_TOP_L, FOREST_TOP_R = 0x01E, 0x01F
FOREST_BOT_L, FOREST_BOT_R = 0x016, 0x017
FOREST_TRUNK_L, FOREST_TRUNK_R = 0x026, 0x027
BUSH = 0x005
GRASS = (0x008, 0x009, 0x010, 0x011)
TALL_GRASS = 0x00D
FLOWER = 0x004
SIGN = 0x002
LEDGE, LEDGE_END_L, LEDGE_END_R = 0x087, 0x0B0, 0x0B1
LEDGE_EAST, LEDGE_WEST = 0x086, 0x085      # vertical rock-line ledges (jump east / west)
CAVE = 0x0A9
GREY_PATH = {'C': 0x16E, 'T': 0x166, 'B': 0x176, 'L': 0x16D, 'R': 0x16F,
             'TL': 0x165, 'TR': 0x167, 'BL': 0x175, 'BR': 0x177,
             'iUR': 0x196, 'iUL': 0x195, 'iDR': 0x19E, 'iDL': 0x19D}
SAND_PATH = {0x0D3, 0x0D4, 0x0D5, 0x0DB, 0x0DC, 0x0DD, 0x0E3, 0x0E4, 0x0E5,
             0x102, 0x103, 0x104, 0x105}
SEA = {'C': 0x12B, 'T': 0x123, 'L': 0x12A, 'R': 0x12C, 'TL': 0x120, 'TR': 0x121,
       'iUL': 0x131, 'iUR': 0x130}
SHORE_BELOW_WATER = 0x133
WATER_ROCK = ((0x110, 0x111), (0x118, 0x119))
ELEV3 = 0x3000   # elevation 3, collision 0
BORDER_FOREST = (0x01C, 0x01D, 0x014, 0x015)   # Viridian/Pewter border
BORDER_ROCK = (0x071,) * 4                       # Route 22 / Lavender / Route 3 border

# ------------------------------------------------------------------ building templates
# name: (layout, layout w, layout h, x0, y0, w, h)   door offset is detected from behaviour
TEMPLATES = {
    'pewter_house': ('PewterCity_Frlg', 48, 40, 32, 8, 5, 4),
    'pewter_gym':   ('PewterCity_Frlg', 48, 40, 12, 12, 7, 5),   # all primary metatiles
    'pewter_mart':  ('PewterCity_Frlg', 48, 40, 26, 15, 4, 4),
    'pewter_pc':    ('PewterCity_Frlg', 48, 40, 15, 22, 5, 4),
    'vir_house':    ('ViridianCity_Frlg', 48, 40, 24, 8, 5, 4),
    'vir_mart':     ('ViridianCity_Frlg', 48, 40, 34, 16, 4, 4),
    'vir_pc':       ('ViridianCity_Frlg', 48, 40, 24, 23, 5, 4),
    'vir_gym':      ('ViridianCity_Frlg', 48, 40, 33, 6, 6, 5),
    'lav_house':    ('LavenderTown_Frlg', 24, 20, 8, 8, 5, 4),
    'lav_tower':    ('LavenderTown_Frlg', 24, 20, 15, 0, 7, 7),
    'lav_mart':     ('LavenderTown_Frlg', 24, 20, 18, 12, 4, 4),
    'lav_pc':       ('LavenderTown_Frlg', 24, 20, 4, 2, 5, 4),
    'fu_house':     ('FuchsiaCity_Frlg', 48, 40, 32, 28, 5, 4),
    'fu_gym':       ('FuchsiaCity_Frlg', 48, 40, 6, 28, 7, 5),
    'fu_safari':    ('FuchsiaCity_Frlg', 48, 40, 22, 0, 6, 6),
    'fu_warden':    ('FuchsiaCity_Frlg', 48, 40, 26, 12, 6, 5),
    'pal_house':    ('PalletTown_Frlg', 24, 20, 5, 3, 5, 5),
    'pal_lab':      ('PalletTown_Frlg', 24, 20, 13, 9, 7, 5),
}
DOOR_BEHAVIORS = {0x60, 0x69}

# ------------------------------------------------------------------ per-map configuration
BASE = 'https://archives.bulbagarden.net/media/upload/'
TOWN = dict(map_type='MAP_TYPE_TOWN', music='MUS_RG_PEWTER', path='grey')
ROUTE = dict(map_type='MAP_TYPE_ROUTE', music='MUS_RG_ROUTE1', path='sand')
MAPS = {
    'BlackthornCity': dict(TOWN, src='Blackthorn_City_GSC.png', url=BASE + 'f/fa/Blackthorn_City_GSC.png',
        secondary='gTileset_PewterCity', border=BORDER_ROCK, music='MUS_RG_CINNABAR', xfill='P',
        buildings=[('pewter_gym', 15, 7), ('pewter_house', 12, 18), ('pewter_house', 28, 20),
                   ('pewter_house', 8, 28), ('pewter_mart', 13, 26), ('pewter_pc', 19, 26)],
        # west: walkable link to Route 44 (rows 28-29 line up with R44 rows 10-11), user decision phase 5
        overrides=[((0, 28), (1, 29), 'P')],
        signs={(21, 3): 'DRAGONS_DEN', (17, 13): 'GYM', (34, 24): 'CITY', (5, 25): 'MOVE_DELETER',
               (7, 31): 'TRAINER_TIPS'},
        connections=[('MAP_ROUTE44', 18, 'left')]),
    'MahoganyTown': dict(TOWN, src='Mahogany_Town_GSC.png', url=BASE + '0/03/Mahogany_Town_GSC.png',
        secondary='gTileset_ViridianCity', border=BORDER_ROCK, music='MUS_RG_LAVENDER', xfill='P',
        buildings=[('vir_gym', 4, 9), ('vir_pc', 13, 10), ('vir_mart', 10, 4), ('vir_house', 15, 4)],
        # top: Route 43 gate straddles the map edge -> opened up as path (no gate interior)
        overrides=[((8, 0), (11, 1), 'P')],
        signs={(1, 5): 'CITY', (9, 7): 'SHOP', (3, 13): 'GYM'},
        connections=[('MAP_ROUTE42', 0, 'left'), ('MAP_ROUTE44', 0, 'right'), ('MAP_ROUTE43', 0, 'up')]),
    'VioletCity': dict(TOWN, src='Violet_City_C.png', url=BASE + 'e/e8/Violet_City_C.png',
        secondary='gTileset_LavenderTown', border=BORDER_FOREST, xfill='G',
        buildings=[('lav_tower', 20, 0), ('lav_house', 1, 12), ('lav_mart', 8, 14), ('pewter_gym', 15, 13),
                   ('lav_house', 28, 14), ('lav_pc', 30, 22), ('lav_house', 19, 26), ('lav_house', 1, 26)],
        # east edge: Route 31 gate doorway -> path; sign under the SW house moved next to it
        overrides=[((39, 24), (39, 25), 'P'), ((2, 26), (2, 26), 'P'), ((2, 30), (2, 30), 'S'), ((13, 17), (13, 17), 'S')],
        signs={(24, 8): 'SPROUT_TOWER', (13, 17): 'GYM', (27, 17): 'SCHOOL', (24, 20): 'CITY',
               (2, 30): 'TRAINER_TIPS', (4, 30): 'HOUSE'},
        connections=[('MAP_ROUTE31', 18, 'right'), ('MAP_ROUTE36', 0, 'left')]),
    'Route29': dict(ROUTE, src='Johto_Route_29_GSC.png', url=BASE + 'c/ce/Johto_Route_29_GSC.png',
        secondary='gTileset_ViridianCity', border=BORDER_FOREST, xfill='G',
        buildings=[('vir_house', 26, 0)],   # Route 46 gatehouse -> house stand-in
        overrides=[],
        signs={(3, 5): 'R29_W', (51, 7): 'R29_E'},
        connections=[('MAP_CHERRYGROVE_CITY', 0, 'left'), ('MAP_NEW_BARK_TOWN', 0, 'right')]),
    'Route30': dict(ROUTE, src='Johto_Route_30_GSC.png', url=BASE + 'c/c5/Johto_Route_30_GSC.png',
        secondary='gTileset_ViridianCity', border=BORDER_FOREST, xfill='G',
        buildings=[('vir_house', 15, 2), ('vir_house', 6, 36)],   # Mr. Pokemon's house, berry house
        overrides=[((14, 6), (14, 6), 'S')],   # sign displaced by the taller FRLG house
        signs={(14, 6): 'MR_POKEMON', (3, 21): 'R30', (13, 29): 'TRAINER_TIPS', (9, 43): 'BERRY_HOUSE'},
        connections=[('MAP_CHERRYGROVE_CITY', -10, 'down'), ('MAP_ROUTE31', -20, 'up')]),
    'Route31': dict(ROUTE, src='Johto_Route_31_GSC.png', url=BASE + '6/62/Johto_Route_31_GSC.png',
        secondary='gTileset_ViridianCity', border=BORDER_FOREST, xfill='G',
        buildings=[],
        # west: Violet gate straddles the map edge -> roof rows become forest, walk rows path
        overrides=[((0, 4), (3, 5), 'T'), ((0, 6), (4, 7), 'P')],
        signs={(7, 5): 'R31', (31, 5): 'DARK_CAVE'},
        connections=[('MAP_ROUTE30', 20, 'down'), ('MAP_VIOLET_CITY', -18, 'left')]),
    'Route42': dict(ROUTE, src='Johto_Route_42_GSC.png', url=BASE + '4/4a/Johto_Route_42_GSC.png',
        secondary='gTileset_ViridianCity', border=BORDER_ROCK, music='MUS_RG_ROUTE3', xfill='G',
        buildings=[],
        overrides=[((0, 8), (0, 9), 'P')],   # Ecruteak gate doorway
        signs={(7, 5): 'MT_MORTAR', (4, 10): 'R42', (45, 9): 'MT_MORTAR', (54, 8): 'R42'},
        connections=[('MAP_MAHOGANY_TOWN', 0, 'right'), ('MAP_ECRUTEAK_CITY', -18, 'left')]),
    'Route43': dict(ROUTE, src='Johto_Route_43_C.png', url=BASE + '4/4a/Johto_Route_43_C.png',
        secondary='gTileset_ViridianCity', border=BORDER_FOREST, music='MUS_RG_ROUTE3', xfill='P',
        buildings=[('vir_house', 15, 32)],   # toll gatehouse -> house stand-in
        overrides=[((8, 51), (11, 53), 'P')],   # Mahogany gate straddles the edge -> path
        signs={(13, 3): 'LAKE_OF_RAGE', (16, 38): 'R43', (11, 49): 'TRAINER_TIPS'},
        connections=[('MAP_MAHOGANY_TOWN', 0, 'down')]),
    'Route44': dict(ROUTE, src='Johto_Route_44_GSC.png', url=BASE + '7/7d/Johto_Route_44_GSC.png',
        secondary='gTileset_ViridianCity', border=BORDER_ROCK, music='MUS_RG_ROUTE3', xfill='G',
        buildings=[],
        # east: walkable link to Blackthorn (rows 10-11 -> Blackthorn rows 28-29); Ice Path stays optional
        overrides=[((58, 10), (59, 11), 'P')],
        signs={(6, 10): 'R44', (53, 7): 'ICE_PATH'},
        connections=[('MAP_MAHOGANY_TOWN', 0, 'left'), ('MAP_BLACKTHORN_CITY', -18, 'right')]),
    # ---------------------------------------------------------------- phase 3
    'EcruteakCity': dict(TOWN, src='Ecruteak_City_C.png', url=BASE + '0/0e/Ecruteak_City_C.png',
        secondary='gTileset_FuchsiaCity', border=BORDER_FOREST, music='MUS_RG_FUCHSIA', xfill='P',
        buildings=[('fu_safari', 3, 1),      # Burned Tower exterior stand-in (interior TODO)
                   ('fu_warden', 16, 7),     # Tin Tower entrance building
                   ('fu_house', 11, 8), ('fu_house', 15, 0),   # house, Wise Trio house
                   ('fu_house', 35, 4),      # Bell (Tin) Tower stand-in (tower TODO)
                   ('fu_house', 4, 14), ('fu_house', 12, 14),
                   ('fu_house', 4, 18),      # Lugia speech house (2-tall in GSC, sits on the road)
                   ('fu_gym', 3, 23), ('fu_house', 12, 24), ('vir_pc', 21, 24), ('fu_house', 28, 24),
                   ('fu_house', 22, 18),     # Dance Theater stand-in
                   ('vir_mart', 28, 18)],
        overrides=[((15, 4), (21, 5), 'P'),          # Wise Trio house front
                   ((36, 0), (39, 3), 'T'), ((34, 8), (39, 8), 'P'),   # Tin Tower column
                   ((36, 24), (39, 25), 'T'), ((35, 26), (39, 27), 'P')],   # Route 42 gate -> open path
        signs={(2, 10): 'BURNED_TOWER', (38, 10): 'TIN_TOWER', (15, 21): 'CITY', (21, 21): 'DANCE_THEATER',
               (8, 28): 'GYM'},
        connections=[('MAP_ROUTE42', 18, 'right'), ('MAP_ROUTE37', 10, 'down')]),
    'NewBarkTown': dict(TOWN, src='New_Bark_Town_GSC.png', url=BASE + '5/54/New_Bark_Town_GSC.png',
        secondary='gTileset_PalletTown', border=BORDER_FOREST, music='MUS_RG_PALLET', xfill='P',
        buildings=[('pal_lab', 4, 0), ('pal_house', 12, 1), ('pal_house', 2, 9), ('pal_house', 10, 9)],
        overrides=[],
        signs={(8, 8): 'CITY', (11, 5): 'PLAYERS_HOUSE', (3, 3): 'ELMS_LAB', (9, 13): 'ELMS_HOUSE'},
        connections=[('MAP_ROUTE29', 0, 'left'), ('MAP_ROUTE27', 0, 'right')]),
    'Route27': dict(ROUTE, src='Kanto_Route_27_GSC.png', url=BASE + 'e/e7/Kanto_Route_27_GSC.png',
        secondary='gTileset_ViridianCity', border=BORDER_FOREST, music='MUS_RG_ROUTE24', xfill='P',
        buildings=[('vir_house', 31, 4)],   # Sandstorm house; brick piers -> xfill sand path
        overrides=[],
        signs={(25, 7): 'TOHJO_FALLS'},
        connections=[('MAP_NEW_BARK_TOWN', 0, 'left'), ('MAP_ROUTE26', -90, 'right')]),
    'Route26': dict(ROUTE, src='Kanto_Route_26_GSC.png', url=BASE + 'e/ee/Kanto_Route_26_GSC.png',
        secondary='gTileset_ViridianCity', border=BORDER_ROCK, music='MUS_RG_ROUTE24', xfill='P',
        buildings=[('vir_house', 14, 54), ('vir_house', 4, 68)],   # heal house, day-of-week siblings
        # top: Victory Road Gate -> mountain pass straight into FRLG Route 22 (gate role taken by
        # the FRLG Pokemon League Front Gate there)
        overrides=[((6, 0), (6, 5), 'M'), ((9, 0), (9, 5), 'M'), ((7, 0), (8, 5), 'P')],
        signs={(8, 6): 'R26'},
        connections=[('MAP_ROUTE27', 90, 'left'), ('MAP_ROUTE22', -1, 'up')]),
    'Route28': dict(ROUTE, src='Kanto_Route_28_GSC.png', url=BASE + '8/8d/Kanto_Route_28_GSC.png',
        secondary='gTileset_ViridianCity', border=BORDER_ROCK, music='MUS_RG_ROUTE3', xfill='G',
        buildings=[('vir_house', 6, 0)],   # Steel Wing house
        # east: Victory Road Gate -> mountain; walk rows carved east into FRLG Route 22
        overrides=[((32, 2), (35, 5), 'M'), ((36, 6), (39, 8), 'P')],
        signs={(31, 5): 'R28'},
        connections=[('MAP_SILVER_CAVE_OUTSIDE', -18, 'left'), ('MAP_ROUTE22', -10, 'right')]),
    'SilverCaveOutside': dict(ROUTE, src='Mt._Silver_Exterior_GSC.png', url=BASE + 'e/e5/Mt._Silver_Exterior_GSC.png',
        secondary='gTileset_ViridianCity', border=BORDER_ROCK, music='MUS_RG_VICTORY_ROAD', xfill='G',
        buildings=[('vir_pc', 21, 16)],
        overrides=[],
        signs={(17, 13): 'MT_SILVER'},
        connections=[('MAP_ROUTE28', 18, 'right')]),
    # ---------------------------------------------------------------- phase 5
    'Route36': dict(ROUTE, src='Johto_Route_36_C.png', url=BASE + '1/18/Johto_Route_36_C.png',
        secondary='gTileset_ViridianCity', border=BORDER_FOREST, xfill='G',
        # National Park gate -> house stand-in (door faces south, path carved to the main road);
        # Ruins of Alph north gate -> house stand-in (its boulder pair becomes trees)
        buildings=[('vir_house', 14, 6), ('vir_house', 46, 13)],
        overrides=[((15, 10), (19, 10), 'P'), ((50, 14), (51, 15), 'T')],
        signs={(29, 1): 'R37', (21, 7): 'NATIONAL_PARK', (55, 7): 'R36', (45, 11): 'RUINS_OF_ALPH'},
        connections=[('MAP_ROUTE37', 20, 'up'), ('MAP_VIOLET_CITY', 0, 'right')]),
    'Route37': dict(ROUTE, src='Johto_Route_37_GSC.png', url=BASE + 'a/a4/Johto_Route_37_GSC.png',
        secondary='gTileset_ViridianCity', border=BORDER_FOREST, xfill='G',
        buildings=[],
        overrides=[],
        signs={(5, 3): 'R37'},
        connections=[('MAP_ECRUTEAK_CITY', -10, 'up'), ('MAP_ROUTE36', -20, 'down')]),
}

SIGN_TEXT = {
    ('BlackthornCity', 'CITY'): 'BLACKTHORN CITY\\nA Quiet Mountain Retreat',
    ('BlackthornCity', 'GYM'): 'BLACKTHORN CITY POKéMON GYM\\nLEADER: CLAIR\\pThe Blessed User of\\nDragon POKéMON',
    ('BlackthornCity', 'DRAGONS_DEN'): "DRAGON'S DEN AHEAD",
    ('BlackthornCity', 'MOVE_DELETER'): "MOVE DELETER'S HOUSE",
    ('BlackthornCity', 'TRAINER_TIPS'): 'TRAINER TIPS',
    ('MahoganyTown', 'CITY'): 'MAHOGANY TOWN\\nWelcome to the Home of the Ninja',
    ('MahoganyTown', 'SHOP'): 'MAHOGANY SOUVENIR SHOP',
    ('MahoganyTown', 'GYM'): "MAHOGANY TOWN POKéMON GYM\\nLEADER: PRYCE\\pThe Teacher of\\nWinter's Harshness",
    ('VioletCity', 'CITY'): 'VIOLET CITY\\nThe City of Nostalgic Scents',
    ('VioletCity', 'GYM'): 'VIOLET CITY POKéMON GYM\\nLEADER: FALKNER\\pThe Elegant Master of\\nFlying POKéMON',
    ('VioletCity', 'SPROUT_TOWER'): 'SPROUT TOWER\\nExperience the Way of POKéMON',
    ('VioletCity', 'SCHOOL'): "EARL'S POKéMON ACADEMY",
    ('VioletCity', 'TRAINER_TIPS'): 'TRAINER TIPS',
    ('VioletCity', 'HOUSE'): "VIOLET CITY",
    ('Route29', 'R29_W'): 'ROUTE 29\\nCHERRYGROVE CITY - NEW BARK TOWN',
    ('Route29', 'R29_E'): 'ROUTE 29\\nCHERRYGROVE CITY - NEW BARK TOWN',
    ('Route30', 'R30'): 'ROUTE 30\\nVIOLET CITY - CHERRYGROVE CITY',
    ('Route30', 'MR_POKEMON'): "MR. POKéMON'S HOUSE\\nSTRAIGHT AHEAD!",
    ('Route30', 'TRAINER_TIPS'): 'TRAINER TIPS',
    ('Route30', 'BERRY_HOUSE'): 'BERRY MASTER\\nBerries for everyone!',
    ('Route31', 'R31'): 'ROUTE 31\\nVIOLET CITY - CHERRYGROVE CITY',
    ('Route31', 'DARK_CAVE'): 'DARK CAVE',
    ('Route42', 'R42'): 'ROUTE 42\\nECRUTEAK CITY - MAHOGANY TOWN',
    ('Route42', 'MT_MORTAR'): 'MT. MORTAR\\nWaterfall Cave Inside',
    ('Route43', 'R43'): 'ROUTE 43',
    ('Route43', 'LAKE_OF_RAGE'): 'LAKE OF RAGE\\nNORTH TO LAKE OF RAGE',
    ('Route43', 'TRAINER_TIPS'): 'TRAINER TIPS',
    ('Route44', 'R44'): 'ROUTE 44\\nMAHOGANY TOWN - BLACKTHORN CITY',
    ('Route44', 'ICE_PATH'): 'ICE PATH AHEAD',
    ('Route36', 'R37'): 'ROUTE 37',
    ('Route36', 'NATIONAL_PARK'): 'ROUTE 36\\nNATIONAL PARK GATE',
    ('Route36', 'R36'): 'ROUTE 36\\nVIOLET CITY',
    ('Route36', 'RUINS_OF_ALPH'): 'RUINS OF ALPH\\nNORTH ENTRANCE',
    ('Route37', 'R37'): 'ROUTE 37\\nECRUTEAK CITY AHEAD',
    ('EcruteakCity', 'CITY'): 'ECRUTEAK CITY\\nA Historical City\\pWhere the Past\\nMeets the Present',
    ('EcruteakCity', 'TIN_TOWER'): 'TIN TOWER\\pA legendary POKéMON is said to\\nroost here.',
    ('EcruteakCity', 'GYM'): 'ECRUTEAK CITY POKéMON GYM\\nLEADER: MORTY\\pThe Mystic Seer of\\nthe Future',
    ('EcruteakCity', 'DANCE_THEATER'): 'ECRUTEAK DANCE THEATER',
    ('EcruteakCity', 'BURNED_TOWER'): 'BURNED TOWER\\pIt was destroyed by a mysterious fire.\\pPlease stay away, as it is unsafe.',
    ('NewBarkTown', 'CITY'): 'NEW BARK TOWN\\pThe Town Where the\\nWinds of a New\\nBeginning Blow',
    ('NewBarkTown', 'PLAYERS_HOUSE'): "{PLAYER}'s HOUSE",
    ('NewBarkTown', 'ELMS_LAB'): 'ELM POKéMON LAB',
    ('NewBarkTown', 'ELMS_HOUSE'): "ELM'S HOUSE",
    ('Route26', 'R26'): 'ROUTE 26\\pPOKéMON LEAGUE\\nRECEPTION GATE',
    ('Route27', 'TOHJO_FALLS'): 'TOHJO FALLS\\pTHE LINK BETWEEN\\nKANTO AND JOHTO',
    ('Route28', 'R28'): 'ROUTE 28',
    ('SilverCaveOutside', 'MT_SILVER'): 'MT. SILVER',
}

# ------------------------------------------------------------------ helpers
def snake_upper(name):
    import re
    return re.sub(r'(?<=[a-z])(?=[A-Z])', '_', name).upper()   # Route29 -> ROUTE29

def load_blocks(name, w, h):
    d = open(os.path.join(REPO, 'data/layouts', name, 'map.bin'), 'rb').read()
    v = struct.unpack('<%dH' % (w * h), d)
    return [list(v[r * w:(r + 1) * w]) for r in range(h)]

_ATTRS = {}
def common_attrs(secondary):
    if secondary not in _ATTRS:
        c = collections.defaultdict(collections.Counter)
        for l, b in frlg_layouts():
            ok = l.get('secondary_tileset') == secondary
            for row in b:
                for v in row:
                    m = v & 0x3FF
                    if m < 0x280 or ok:
                        c[m][v & 0xFC00] += 1
        _ATTRS[secondary] = {m: cnt.most_common(1)[0][0] for m, cnt in c.items()}
    return _ATTRS[secondary]

_LEARNED = {}
def learned(kind):
    if kind not in _LEARNED:
        if kind == 'mountain':
            fam, grassy = mountain_family()
            grassy -= {0x076, 0x077, 0x080, 0x081, 0x082, 0x0B4, 0x0B5, 0x0B6}
            _LEARNED[kind] = Learned(fam, grassy)
        else:
            _LEARNED[kind] = Learned(SAND_PATH)
    return _LEARNED[kind]

def grid_for(src):
    d = json.load(open(os.path.join(SRC_DIR, 'cells.json')))
    return d['grids'][src]

# ------------------------------------------------------------------ conversion
def convert(name):
    cfg = MAPS[name]
    grid = grid_for(cfg['src'])
    H, W = len(grid), len(grid[0])
    unknown = sorted({c for r in grid for c in r if c not in CLASS})
    if unknown:
        raise SystemExit('%s: unclassified cell ids %s' % (name, unknown))
    sem = [[CLASS[c] for c in row] for row in grid]
    for (x0, y0), (x1, y1), cls in cfg['overrides']:
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                sem[y][x] = cls
    attrs = common_attrs(cfg['secondary'])
    out = [[None] * W for _ in range(H)]
    notes = collections.defaultdict(list)

    # ---- buildings
    doors = []
    tsets = {}
    for tname, bx, by in cfg['buildings']:
        lay, lw, lh, tx, ty, tw, th = TEMPLATES[tname]
        src_l = json.load(open(os.path.join(REPO, 'data/layouts/layouts.json')))['layouts']
        sec = next(l['secondary_tileset'] for l in src_l if l['blockdata_filepath'].endswith('/' + lay + '/map.bin'))
        tb = load_blocks(lay, lw, lh)
        if sec not in tsets:
            tsets[sec] = Tilesets(tileset_dir('gTileset_General_Frlg', True), tileset_dir(sec))
        for dy in range(th):
            for dx in range(tw):
                v = tb[ty + dy][tx + dx]
                if (v & 0x3FF) >= 0x280 and sec != cfg['secondary']:
                    raise SystemExit('%s: template %s uses secondary metatiles of %s' % (name, tname, sec))
                if not (0 <= bx + dx < W and 0 <= by + dy < H):
                    raise SystemExit('%s: %s at %d,%d out of bounds' % (name, tname, bx, by))
                if out[by + dy][bx + dx] is not None:
                    raise SystemExit('%s: building overlap at %d,%d' % (name, bx + dx, by + dy))
                out[by + dy][bx + dx] = v
                sem[by + dy][bx + dx] = 'X'
                if tsets[sec].attr(v & 0x3FF) & 0x1FF in DOOR_BEHAVIORS:
                    doors.append((tname, bx + dx, by + dy))
    bmask = [[out[y][x] is not None for x in range(W)] for y in range(H)]
    for y in range(H):
        for x in range(W):
            if sem[y][x] == 'X' and not bmask[y][x]:
                sem[y][x] = cfg['xfill']
                notes['xfill'].append((x, y))

    # ---- boulders: water rocks if they touch water, else a small rock mound (M)
    for y in range(H):
        for x in range(W):
            if sem[y][x] == 'B0' and x + 1 < W and y + 1 < H and \
                    [sem[y][x + 1], sem[y + 1][x], sem[y + 1][x + 1]] == ['B1', 'B2', 'B3']:
                ring = [(x + i, y + j) for i in range(-1, 3) for j in range(-1, 3)
                        if not (0 <= i <= 1 and 0 <= j <= 1)]
                wet = any(0 <= a < W and 0 <= b < H and sem[b][a] in ('W', 'R') for a, b in ring)
                for j in (0, 1):
                    for i in (0, 1):
                        sem[y + j][x + i] = ('w%d' % (j * 2 + i)) if wet else 'M'
    for y in range(H):
        for x in range(W):
            if sem[y][x] in ('B0', 'B1', 'B2', 'B3'):     # broken boulder (cut by map edge)
                sem[y][x] = 'M'
                notes['broken_boulder'].append((x, y))

    def S(x, y, default=None):
        if 0 <= x < W and 0 <= y < H:
            return sem[y][x]
        if default is not None:
            return default
        return sem[min(max(y, 0), H - 1)][min(max(x, 0), W - 1)]   # clamp: edges continue

    def put(x, y, m, a=None):
        out[y][x] = m | (attrs.get(m, 0) if a is None else a)

    WET = ('W', 'R', 'w0', 'w1', 'w2', 'w3')
    def sea_for(x, y):
        land = lambda xx, yy: S(xx, yy) not in WET
        u, l, r = land(x, y - 1), land(x - 1, y), land(x + 1, y)
        if u and l: k = 'TL'
        elif u and r: k = 'TR'
        elif u: k = 'T'
        elif l: k = 'L'
        elif r: k = 'R'
        elif land(x - 1, y - 1): k = 'iUL'
        elif land(x + 1, y - 1): k = 'iUR'
        else: k = 'C'
        return SEA[k]

    mtn_mask = lambda xx, yy: S(xx, yy) in ('M', 'C')
    sand_mask = lambda xx, yy: S(xx, yy) in ('P', 'S')
    isT = lambda xx, yy: S(xx, yy) == 'T'

    def lone_tree(x, y):
        for ox in (-1, 0):
            for oy in (-1, 0):
                if all(isT(x + ox + i, y + oy + j) for i in (0, 1) for j in (0, 1)):
                    return False
        return True

    for y in range(H):
        for x in range(W):
            if bmask[y][x]:
                continue
            c = sem[y][x]
            if c == 'T':
                if lone_tree(x, y):
                    put(x, y, BUSH); notes['bush'].append((x, y)); continue
                top = (y % 2 == 0)
                le = x % 2 == 0 and not isT(x - 1, y)
                re_ = x % 2 == 1 and not isT(x + 1, y)
                if top:
                    m = FOREST_TOP_L if le else FOREST_TOP_R if re_ else FOREST_TOP[x % 2]
                elif not isT(x, y + 1):
                    m = FOREST_TRUNK_L if le else FOREST_TRUNK_R if re_ else FOREST_TRUNK[x % 2]
                else:
                    m = FOREST_BOT_L if le else FOREST_BOT_R if re_ else FOREST_BOT[x % 2]
                put(x, y, m)
            elif c == 'U':
                put(x, y, BUSH)
            elif c in ('G', 'F'):
                if c == 'F':
                    m = FLOWER
                elif S(x, y - 1, 'G') == 'W':
                    m = SHORE_BELOW_WATER
                else:
                    m = GRASS[(x * 7 + y * 13 + (x * y) % 5) % 4]
                put(x, y, m)
            elif c == 'H':
                put(x, y, TALL_GRASS)
            elif c == 'S':
                put(x, y, SIGN)
            elif c == 'P':
                if cfg['path'] == 'sand':
                    put(x, y, learned('sand').pick(sand_mask, x, y))
                    continue
                isP = lambda xx, yy: S(xx, yy) in ('P', 'S')
                u, d, l, r = isP(x, y - 1), isP(x, y + 1), isP(x - 1, y), isP(x + 1, y)
                key = ('T' if not u else 'B' if not d else '') + ('L' if not l else 'R' if not r else '')
                if key == '':
                    if not isP(x + 1, y - 1): key = 'iUR'
                    elif not isP(x - 1, y - 1): key = 'iUL'
                    elif not isP(x + 1, y + 1): key = 'iDR'
                    elif not isP(x - 1, y + 1): key = 'iDL'
                    else: key = 'C'
                put(x, y, GREY_PATH[key])
            elif c == 'W':
                put(x, y, sea_for(x, y))
            elif c == 'R':
                bx, by = x - x % 2, y - y % 2
                if all(S(bx + i, by + j, '') == 'R' for i in (0, 1) for j in (0, 1)):
                    put(x, y, WATER_ROCK[y % 2][x % 2])
                else:
                    sem[y][x] = 'W'; put(x, y, sea_for(x, y))
            elif c in ('w0', 'w1', 'w2', 'w3'):
                i = int(c[1]); put(x, y, WATER_ROCK[i // 2][i % 2])
            elif c in ('M', 'C'):
                m = learned('mountain').pick(mtn_mask, x, y)
                if m in (0x073, 0x07D) and all(mtn_mask(x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
                    m = 0x071
                if c == 'C':
                    put(x, y, CAVE, ELEV3); notes['cave'].append((x, y))
                else:
                    put(x, y, m)
            elif c == 'L':
                isL = lambda xx, yy: S(xx, yy, 'L') == 'L'
                l, r = isL(x - 1, y), isL(x + 1, y)
                put(x, y, LEDGE if (l and r) or (not l and not r) else LEDGE_END_L if not l else LEDGE_END_R)
            elif c == 'VR':
                put(x, y, LEDGE_EAST)
            elif c == 'VL':
                put(x, y, LEDGE_WEST)
            else:
                raise SystemExit('%s: unhandled class %r at %d,%d' % (name, c, x, y))

    scells = {(x, y) for y in range(H) for x in range(W) if sem[y][x] == 'S'}
    if scells != set(cfg['signs']):
        raise SystemExit('%s: sign cells %s != configured %s' % (name, sorted(scells), sorted(cfg['signs'])))

    # ---- write layout
    od = os.path.join(REPO, 'data/layouts', name)
    os.makedirs(od, exist_ok=True)
    with open(os.path.join(od, 'map.bin'), 'wb') as f:
        for row in out:
            f.write(struct.pack('<%dH' % W, *row))
    with open(os.path.join(od, 'border.bin'), 'wb') as f:
        f.write(struct.pack('<4H', *[m | attrs.get(m, 0) for m in cfg['border']]))
    os.makedirs(os.path.join(HERE, 'out'), exist_ok=True)
    with open(os.path.join(HERE, 'out', name + '_semantic.txt'), 'w') as f:
        f.write('# %s %dx%d  source %s\n' % (name, W, H, cfg['url']))
        f.write('# T forest U bush P path G lawn F flower H tall grass W water R/w* rocks in water\n'
                '# M mountain C cave L ledge VL/VR side ledge S sign X building\n')
        for row in sem:
            f.write(' '.join('%-2s' % c for c in row) + '\n')
        f.write('\n# raw global cell ids (tools/johto cells.json)\n')
        for row in grid:
            f.write(' '.join('%3d' % c for c in row) + '\n')
    write_map_json(name, cfg, W, H)
    return dict(name=name, w=W, h=H, doors=doors, notes=dict(notes), out=out, sem=sem)


def write_map_json(name, cfg, W, H):
    up = snake_upper(name)
    md = os.path.join(REPO, 'data/maps', name)
    os.makedirs(md, exist_ok=True)
    signs = sorted(cfg['signs'].items(), key=lambda kv: (kv[0][1], kv[0][0]))
    seen = {}
    bg, scripts, texts = [], [], []
    for (x, y), key in signs:
        label = ''.join(p.capitalize() for p in key.split('_'))
        if label in seen:
            seen[label] += 1; label += str(seen[label])
        else:
            seen[label] = 1
        sc = '%s_EventScript_%sSign' % (name, label)
        tx = '%s_Text_%sSign' % (name, label)
        bg.append({'type': 'sign', 'x': x, 'y': y, 'elevation': 0,
                   'player_facing_dir': 'BG_EVENT_PLAYER_FACING_ANY', 'script': sc})
        scripts.append('%s::\n\tmsgbox %s, MSGBOX_SIGN\n\tend\n' % (sc, tx))
        lines = SIGN_TEXT[(name, key)].replace('\\p', '\\p\n').replace('\\n', '\\n\n').split('\n')
        body = '\n'.join('\t.string "%s%s"' % (ln, '$' if i == len(lines) - 1 else '') for i, ln in enumerate(lines))
        texts.append('%s::\n%s\n' % (tx, body))
    j = {
        'id': 'MAP_' + up, 'name': name, 'layout': 'LAYOUT_' + up,
        'music': cfg['music'], 'region': 'REGION_KANTO',
        'region_map_section': 'MAPSEC_VIRIDIAN_CITY', 'requires_flash': False,
        'weather': 'WEATHER_SUNNY', 'map_type': cfg['map_type'], 'allow_cycling': True,
        'allow_escaping': False, 'allow_running': True, 'show_map_name': False,
        'floor_number': 0, 'battle_scene': 'MAP_BATTLE_SCENE_NORMAL',
        'connections': [{'map': m, 'offset': o, 'direction': d} for m, o, d in cfg['connections']] or None,
        'object_events': [], 'warp_events': [], 'coord_events': [], 'bg_events': bg,
    }
    # keep hand/tool-authored events (warps from interiors.py, cave warps, objects) across re-conversion
    mp = os.path.join(md, 'map.json')
    if os.path.exists(mp):
        prev = json.load(open(mp))
        for k in ('warp_events', 'object_events', 'coord_events'):
            if prev.get(k):
                j[k] = prev[k]
    with open(mp, 'w') as f:
        f.write(json.dumps(j, indent=2, ensure_ascii=False) + '\n')
    with open(os.path.join(md, 'scripts.inc'), 'w') as f:
        f.write('%s_MapScripts::\n\t.byte 0\n\n' % name)
        f.write('\n'.join(scripts) + '\n' + '\n'.join(texts))


if __name__ == '__main__':
    names = sys.argv[1:] or list(MAPS)
    res = {}
    for n in names:
        r = convert(n)
        res[n] = {k: r[k] for k in ('w', 'h', 'doors', 'notes')}
        print(n, '%dx%d' % (r['w'], r['h']), 'doors', [(d[1], d[2]) for d in r['doors']],
              {k: len(v) for k, v in r['notes'].items()})
    print('learned tiler stats', {k: dict(v.stats) for k, v in _LEARNED.items()})
    rp = os.path.join(HERE, 'out', 'report.json')
    old = json.load(open(rp)) if os.path.exists(rp) else {}
    old.update(res)
    json.dump(old, open(rp, 'w'), indent=1, default=list)
