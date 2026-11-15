#!/usr/bin/env python3
"""Compose Indigo City from the Saffron stamp library and write its map json."""
import json
import os
from collections import deque

from stamps import BUSH, FLOWER, GRASS, PAVE, SIGN, Canvas, frame, stamp_size

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
os.chdir(REPO)

HOUSE = 'MAP_SAFFRON_CITY_HOUSE'
DEST = {
    'League Registration Hall': 'MAP_SAFFRON_CITY_GYM',
    'Battle Club': 'MAP_SAFFRON_CITY_GYM',
    'Pokemon Center': 'MAP_SAFFRON_CITY_POKEMON_CENTER_1F',
    'Poke Mart': 'MAP_SAFFRON_CITY_MART',
    'Indigo Department Store': 'MAP_SILPH_CO_1F',
}

WEST_FENCE, EAST_FENCE, TOP_FENCE, BOT_FENCE = 6, 59, 9, 45


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
    place('house_wide_door', 47, 11, 'Trade & Link Center')
    place('house_plain', 53, 11)

    # Band B (y18..32). Avenue x33..36 stays clear (sign at 33,10 is the exception).
    place('pokecenter', 9, 18, 'Pokemon Center')
    place('mart', 15, 19, 'Poke Mart')
    place('tower', 22, 18, 'Indigo Department Store')
    place('apartment', 39, 18)
    place('apartment', 44, 18)
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

    precheck(c, (34, 47))

    c.save('data/layouts/IndigoCity')

    warps = []
    for x, y in info['gate_warps']:
        warps.append(warp(x, y, 'MAP_RECEPTION_GATE_HNS', '1', 3))
    warps.append(warp(info['cave'][0], info['cave'][1], 'MAP_VICTORY_ROAD_KANTO_B2F_HNS', '0', 3))
    for label, doors in placed:
        dest = DEST.get(label, HOUSE)
        for x, y in doors:
            warps.append(warp(x, y, dest, '1', 0))

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
        'object_events': [],
        'warp_events': warps,
        'coord_events': coord_events,
        'bg_events': [],
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
    """Closed pen east of Day Care. Interior grass is solid so the pen is not an unreachable walkable pocket."""
    c.fence_h(14, 21, 36)
    c.fence_h(14, 21, 42)
    c.fence_v(14, 37, 41, 'left')
    c.fence_v(21, 37, 41, 'right')
    for y in range(37, 42):
        for x in range(15, 21):
            c.set(x, y, GRASS, 1)


def warp(x, y, dest, dest_id, elev):
    return {'x': x, 'y': y, 'elevation': elev, 'dest_map': dest, 'dest_warp_id': dest_id}


def precheck(c, start):
    sx, sy = start
    seen = {(sx, sy)}
    q = deque([(sx, sy)])
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < c.w and 0 <= ny < c.h and (nx, ny) not in seen and not c.solid(nx, ny):
                e1 = (c.b[y][x] >> 12) & 0xF
                e2 = (c.b[ny][nx] >> 12) & 0xF
                if e1 == e2 or e1 in (0, 15) or e2 in (0, 15):
                    seen.add((nx, ny))
                    q.append((nx, ny))
    unreach = [(x, y) for y in range(c.h) for x in range(c.w) if not c.solid(x, y) and (x, y) not in seen]
    print('precheck start=%s reachable=%d walkable_unreachable=%d' % (start, len(seen), len(unreach)))
    if unreach:
        print('unreachable sample:', unreach[:40])
        raise SystemExit(1)


if __name__ == '__main__':
    main()
