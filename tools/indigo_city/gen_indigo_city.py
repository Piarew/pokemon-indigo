#!/usr/bin/env python3
"""Compose Indigo City from the Saffron stamp library and write its map json."""
import json
import os
import re
from collections import deque

from gen_indigo_tileset import gym_remap
from stamps import BUSH, FLOWER, GRASS, PAVE, SIGN, Canvas, frame, stamp_size

TALL_GRASS = 0x00D      # MB_TALL_GRASS, land encounters (Viridian Forest / Route 6 use 0x0D)
BOULDER_GAP = (17, 36)
REMATCH_DOOR_MT = 0x15B  # gym door; scripts.inc swaps in wall 0x314 while the Battle Club is locked  # gap in the Day Care yard's north rail, blocked by a Strength boulder

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
os.chdir(REPO)

HOUSE = 'MAP_SAFFRON_CITY_HOUSE'
DEST = {
    'League Registration Hall': 'MAP_SAFFRON_CITY_GYM',
    # Placeholder: src/indigo_rematch.c redirects this door to today's rematch gym.
    'Battle Club': 'MAP_PEWTER_CITY_GYM',
    'Pokemon Center': 'MAP_SAFFRON_CITY_POKEMON_CENTER_1F',
    'Poke Mart': 'MAP_SAFFRON_CITY_MART',
    'Indigo Department Store': 'MAP_SILPH_CO_1F',
}

WEST_FENCE, EAST_FENCE, TOP_FENCE, BOT_FENCE = 6, 59, 9, 45


def indigo_gym_roofs(c, rects):
    """Point the gym stamps at gTileset_IndigoCity's indigo-roof metatile copies."""
    remap = gym_remap()
    for name, x0, y0, x1, y1 in rects:
        if name not in ('League Registration Hall', 'Battle Club'):
            continue
        n = 0
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                v = c.b[y][x]
                if (v & 0x3FF) in remap:
                    c.b[y][x] = (v & ~0x3FF) | remap[v & 0x3FF]
                    n += 1
        assert n, name


def main():
    c = Canvas(66, 56)
    info = frame(c)
    # South face of the copied gatehouse (Saffron y52) is a pair of enclosed
    # non-animated doors. They are not entrances; a solid wall tile keeps them
    # out of the walkable-unreachable and door-without-warp reports.
    c.set(34, 54, 0x189, 1)
    c.set(35, 54, 0x189, 1)

    placed = []
    rects = []

    def place(name, x, y, label=None):
        w, h = stamp_size(name)
        x1, y1 = x + w - 1, y + h - 1
        assert x >= WEST_FENCE + 2 and x1 <= EAST_FENCE - 2, (label or name, x, x1)
        assert y >= TOP_FENCE + 2 and y1 <= BOT_FENCE - 2, (label or name, y, y1)
        for oname, ox0, oy0, ox1, oy1 in rects:
            if x <= ox1 and ox0 <= x1 and y <= oy1 and oy0 <= y1:
                raise SystemExit('overlap %s (%d,%d)-(%d,%d) vs %s' % (label or name, x, y, x1, y1, oname))
        rects.append((label or name, x, y, x1, y1))
        doors = c.stamp(name, x, y, label)
        if doors:
            placed.append((label or name, doors))
        return doors

    # Band A (y11..15). Street y16..17 stays open paving.
    place('house_door', 8, 11, 'Move Tutor')
    place('house_door', 13, 11, 'Move Deleter')
    place('house_door', 18, 11, 'Name Rater')
    place('gym', 24, 11, 'League Registration Hall')
    place('gym', 39, 11, 'Battle Club')   # mirror of the League Hall across the avenue
    indigo_gym_roofs(c, rects)
    place('house_wide_door', 47, 11, 'Trade & Link Center')
    place('house_plain', 53, 11)

    # Band B (y18..32). Avenue x33..36 stays clear (sign at 33,10 is the exception).
    place('pokecenter', 9, 18, 'Pokemon Center')
    place('mart', 15, 19, 'Poke Mart')
    place('tower', 22, 18, 'Indigo Department Store')
    lay_pond(c)          # replaces the two apartment blocks (x39..48, y18..23)
    place('house_door', 51, 18, 'Hotel')
    place('house_short', 9, 26)
    place('house_wide_door', 15, 26, 'Pokemon Fan Club')
    lay_park(c)

    # Band C (y35..43). Street y33..34 stays open paving.
    place('house_door', 9, 37, 'Day Care')
    lay_daycare_yard(c)
    place('house_door', 24, 38, 'Resident House 1')
    place('house_short', 28, 39)
    place('house_door', 40, 38, 'Resident House 2')
    place('house_plain', 45, 38)
    place('house_door', 52, 38, 'Move Relearner')

    # Saffron-style darker paved lots around building groups (only repaint plain paving;
    # each lot starts one row below the roof-top row so roofs stay on plain paving).
    for lot in ((7, 12, 22, 16), (23, 12, 31, 16), (38, 12, 46, 16), (8, 19, 20, 23),
                (8, 27, 21, 31), (8, 38, 13, 42), (23, 39, 32, 43), (39, 39, 57, 43)):
        c.plaza(*lot)

    # Signs. None sit on the tile directly south of a door, and none sit on y16-17 or y33-34.
    signs = [(32, 43), (8, 22), (19, 22), (31, 15), (33, 10)]
    door_south = {(x, y + 1) for _, doors in placed for x, y in doors}
    for x, y in signs:
        assert (x, y) not in door_south, (x, y)
        assert not c.solid(x, y), (x, y, hex(c.mt(x, y)))
        c.set(x, y, SIGN, 1)

    for label, doors in placed:
        for x, y in doors:
            assert not c.solid(x, y + 1), (label, x, y + 1)

    for y in range(10, 45):
        for x in range(33, 37):
            if (x, y) == (33, 10):
                continue
            assert not c.solid(x, y), ('avenue', x, y, hex(c.mt(x, y)))

    precheck(c, (34, 47), blocked={BOULDER_GAP})
    precheck(c, (34, 47), label='with Strength')

    c.save('data/layouts/IndigoCity')

    warps = []
    for x, y in info['gate_warps']:
        warps.append(warp(x, y, 'MAP_RECEPTION_GATE_HNS', '1', 3))
    warps.append(warp(info['cave'][0], info['cave'][1], 'MAP_VICTORY_ROAD_KANTO_B2F_HNS', '0', 3))
    for label, doors in placed:
        dest = DEST.get(label, HOUSE)
        for x, y in doors:
            warps.append(warp(x, y, dest, '1', 0))

    # The C side (include/indigo_rematch.h) hardcodes the Battle Club door's warp index.
    hdr = open('include/indigo_rematch.h').read()
    door_warp = int(re.search(r'#define INDIGO_CITY_REMATCH_DOOR_WARP (\d+)', hdr).group(1))
    club = dict(placed)['Battle Club']
    assert len(club) == 1 and (warps[door_warp]['x'], warps[door_warp]['y']) == club[0], (door_warp, club)
    assert c.mt(*club[0]) == REMATCH_DOOR_MT, hex(c.mt(*club[0]))
    bg_events = [{
        'type': 'sign',
        'x': club[0][0],
        'y': club[0][1],
        'elevation': 0,
        'player_facing_dir': 'BG_EVENT_PLAYER_FACING_NORTH',
        'script': 'IndigoCity_EventScript_BattleClubDoor',
    }]

    coord_events = [
        {
            'type': 'trigger',
            'x': x,
            'y': 9,
            'elevation': 3,
            'var': 'VAR_TEMP_1',
            'var_value': '0',
            'script': 'IndigoCity_EventScript_VictoryRoadGate',
        }
        for x in (34, 35)
    ]
    map_obj = {
        'id': 'MAP_INDIGO_CITY',
        'name': 'IndigoCity',
        'layout': 'LAYOUT_INDIGO_CITY',
        'music': 'MUS_RG_CELADON',
        'region': 'REGION_KANTO',
        'region_map_section': 'MAPSEC_INDIGO_PLATEAU',
        'requires_flash': False,
        'weather': 'WEATHER_SUNNY',
        'map_type': 'MAP_TYPE_CITY',
        'allow_cycling': True,
        'allow_escaping': False,
        'allow_running': True,
        'show_map_name': True,
        'floor_number': 0,
        'battle_scene': 'MAP_BATTLE_SCENE_NORMAL',
        'connections': None,
        'object_events': [{
            'type': 'object',
            'graphics_id': 'OBJ_EVENT_GFX_PUSHABLE_BOULDER',
            'x': BOULDER_GAP[0],
            'y': BOULDER_GAP[1],
            'elevation': 3,
            'movement_type': 'MOVEMENT_TYPE_FACE_DOWN',
            'movement_range_x': 0,
            'movement_range_y': 0,
            'trainer_type': 'TRAINER_TYPE_NONE',
            'trainer_sight_or_berry_tree_id': '0',
            'script': 'EventScript_StrengthBoulder',
            'flag': '0',
        }],
        'warp_events': warps,
        'coord_events': coord_events,
        'bg_events': bg_events,
    }
    os.makedirs('data/maps/IndigoCity', exist_ok=True)
    with open('data/maps/IndigoCity/map.json', 'w') as f:
        json.dump(map_obj, f, indent=2)
        f.write('\n')

    print('--- log ---')
    for line in c.log:
        print(line)
    print('--- info ---')
    print(info)
    print('--- door legend ---')
    for i, w in enumerate(warps):
        print('warp%02d (%2d,%2d) elev %d -> %s #%s' % (i, w['x'], w['y'], w['elevation'], w['dest_map'], w['dest_warp_id']))


def lay_park(c):
    """Symmetric grass park x40..55, y26..31 inside a paved ring, split by a 2-wide paved walk
    (x47..48). Each half: bush hedge along the top, a centred tree clump, flower beds by the walk."""
    c.grass_patch(40, 26, 55, 31)
    c.fill(47, 26, 48, 31, PAVE)
    for x0 in (40, 49):                       # left half x40..46, right half x49..55 (mirror)
        mirror = (lambda x: x) if x0 == 40 else (lambda x: 95 - x)
        for x in range(40, 47):
            c.set(mirror(x), 26, BUSH, 1)
        c.tree_clump(42 if x0 == 40 else 52, 28)
        for x in (45, 46):
            for y in (27, 28, 30, 31):
                c.set(mirror(x), y, FLOWER)


def lay_daycare_yard(c):
    """Fenced tall-grass yard east of the Day Care (x14..21, y36..42). The north rail has a 1-tile
    gap at BOULDER_GAP that holds a Strength boulder object; push it south into the grass to enter."""
    gx, gy = BOULDER_GAP
    c.fence_h(14, gx - 1, 36)
    c.fence_h(gx + 1, 21, 36)
    c.set(gx, gy, GRASS)                   # walkable gap tile under the boulder
    c.fence_h(14, 21, 42)
    c.fence_v(14, 37, 41, 'left')
    c.fence_v(21, 37, 41, 'right')
    c.fill(15, 37, 20, 41, TALL_GRASS)     # walkable, wild-encounter tall grass


def lay_pond(c):
    """FRLG pond (General_Frlg 0x1A5-0x1AF water with rock rim, 0x133 lower lip) on a grass lot
    x40..49, y18..24. Water is MB_POND_WATER, collision 0, elevation 1 (surf / fishing), like
    Viridian City's pond; the rim/lip tiles are walkable grass at elevation 3."""
    c.grass_patch(40, 18, 49, 24)
    x0, x1, y0, y1 = 41, 48, 19, 22        # water rows y19..22, lip row y23
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if y == y0:
                m = 0x1A5 if x == x0 else 0x1A7 if x == x1 else 0x1A6
            else:
                m = 0x1AD if x == x0 else 0x1AF if x == x1 else 0x1AE
            c.set(x, y, m, 0, 1)
    for x in range(x0, x1 + 1):
        c.set(x, y1 + 1, 0x133)


def warp(x, y, dest, dest_id, elev):
    return {'x': x, 'y': y, 'elevation': elev, 'dest_map': dest, 'dest_warp_id': dest_id}


def precheck(c, start, blocked=(), label='no Strength'):
    sx, sy = start
    seen = {(sx, sy)}
    q = deque([(sx, sy)])
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < c.w and 0 <= ny < c.h and (nx, ny) not in seen and not c.solid(nx, ny) and (nx, ny) not in blocked:
                e1 = (c.b[y][x] >> 12) & 0xF
                e2 = (c.b[ny][nx] >> 12) & 0xF
                if e1 == e2 or e1 in (0, 15) or e2 in (0, 15):
                    seen.add((nx, ny))
                    q.append((nx, ny))
    water = lambda x, y: (c.b[y][x] >> 12) & 0xF == 1      # surf-only pond tiles
    unreach = [(x, y) for y in range(c.h) for x in range(c.w)
               if not c.solid(x, y) and not water(x, y) and (x, y) not in seen]
    yard = [(x, y) for x, y in unreach if 15 <= x <= 20 and 37 <= y <= 41 or (x, y) == BOULDER_GAP]
    print('precheck (%s) start=%s reachable=%d walkable_unreachable=%d (Day Care yard behind boulder: %d)'
          % (label, start, len(seen), len(unreach), len(yard)))
    unreach = [t for t in unreach if t not in yard]
    if unreach:
        print('unreachable sample:', unreach[:40])
        raise SystemExit(1)


if __name__ == '__main__':
    main()
