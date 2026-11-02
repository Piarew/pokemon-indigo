#!/usr/bin/env python3
"""Phase 5: build the hand-designed Diglett's Cave Johto tunnel and its Blackthorn entrance room.
 - DiglettsCave_JohtoTunnel: layout from tools/johto/diglett_tunnel_design.txt; rock edges are picked by
   nearest-5x5-neighbourhood match against the FRLG DiglettsCave_B1F layout (same tilesets).
 - DiglettsCave_BlackthornEntrance: a copy of the unedited FRLG north-entrance room (own layout).
 - FLAGGED FRLG EDIT: DiglettsCave_NorthEntrance_Frlg (Route 2 side) gets a 2nd ladder at (7,2) + warp #2.
 - BlackthornCity (4,23) cave mouth door warp -> BlackthornEntrance exit.
Idempotent; writes map.bin/border.bin/map.json/scripts.inc and the registrations."""
import json, os, struct, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
from register_maps import register

def rd(name, W, H):
    d = open(os.path.join(REPO, 'data/layouts', name, 'map.bin'), 'rb').read()
    assert len(d) == W * H * 2, name
    return [[struct.unpack_from('<H', d, (y * W + x) * 2)[0] for x in range(W)] for y in range(H)]

def wr(name, g):
    od = os.path.join(REPO, 'data/layouts', name); os.makedirs(od, exist_ok=True)
    with open(os.path.join(od, 'map.bin'), 'wb') as f:
        for r in g:
            for v in r: f.write(struct.pack('<H', v))

def mt(v): return v & 0x3FF
def coll(v): return (v >> 10) & 3

# ---------------- tunnel layout
B1F = rd('DiglettsCave_B1F_Frlg', 85, 80)
# learn from the vanilla B1F: undo east_blocks.py's cave-in so its rubble doesn't leak into the tunnel decoration
import east_blocks
for (x, y), (orig, _) in east_blocks.BARRIERS['DiglettsCave_B1F_Frlg']['cells'].items():
    B1F[y][x] = orig
BW, BH = 85, 80
WEIGHT = [[1, 1, 1, 1, 1], [1, 4, 4, 4, 1], [1, 4, 0, 4, 1], [1, 4, 4, 4, 1], [1, 1, 1, 1, 1]]

def mask(isfloor, x, y):
    return tuple(isfloor(x + dx, y + dy) for dy in range(-2, 3) for dx in range(-2, 3))

def b1f_floor(x, y):
    return 0 <= x < BW and 0 <= y < BH and coll(B1F[y][x]) == 0

SAMPLES = {}
for y in range(BH):
    for x in range(BW):
        v = B1F[y][x]
        if coll(v) == 0: continue
        k = mask(b1f_floor, x, y)
        SAMPLES.setdefault(k, {}).setdefault(v, 0)
        SAMPLES[k][v] += 1
FLAT_W = [w for r in WEIGHT for w in r]

def pick(k):
    if k in SAMPLES:
        return max(SAMPLES[k].items(), key=lambda kv: kv[1])[0], 'exact'
    best = min(SAMPLES, key=lambda s: sum(w for a, b, w in zip(s, k, FLAT_W) if a != b))
    return max(SAMPLES[best].items(), key=lambda kv: kv[1])[0], 'nearest'

FLOOR = 0x281 | 0x3000
LADDER_B1F = 0x297 | 0x3000
BOULDER = [[0x2D5 | 0x3000, 0x2D6 | 0x3000], [0x2DD | 0x3000, 0x2DE | 0x3000]]
ROCK = 0x291 | 0x0400

def build_tunnel():
    rows = [l for l in open(os.path.join(HERE, 'diglett_tunnel_design.txt')).read().split('\n')
            if l and not l.startswith('#  ') and not l.startswith('# ')]
    H, W = len(rows), len(rows[0])
    assert all(len(r) == W for r in rows) and (W + 15) * (H + 14) <= 10240
    isf = lambda x, y: 0 <= x < W and 0 <= y < H and rows[y][x] != '#'
    g = [[0] * W for _ in range(H)]
    stats = {'exact': 0, 'nearest': 0}
    lad = {}
    for y in range(H):
        for x in range(W):
            c = rows[y][x]
            if c == '#':
                if all(not isf(x + dx, y + dy) for dx in range(-2, 3) for dy in range(-2, 3)):
                    g[y][x] = ROCK
                else:
                    g[y][x], how = pick(mask(isf, x, y)); stats[how] += 1
            else:
                g[y][x] = FLOOR
            if c in 'KJ':
                g[y][x] = LADDER_B1F; lad[c] = (x, y)
    for y in range(H):
        for x in range(W):
            if rows[y][x] == 'o':
                for j in (0, 1):
                    for i in (0, 1):
                        assert rows[y + j][x + i] in '.o'
                        g[y + j][x + i] = BOULDER[j][i]
    return W, H, g, lad, stats

def dump_json(path, obj):
    with open(path, 'w') as f: f.write(json.dumps(obj, indent=2) + '\n')

def map_json(name, mid, layout, warps, objects=(), scripts_label=None, music='MUS_RG_VIRIDIAN_FOREST'):
    return {"id": mid, "name": name, "layout": layout, "music": music, "region": "REGION_KANTO",
            "region_map_section": "MAPSEC_DIGLETTS_CAVE", "requires_flash": False, "weather": "WEATHER_NONE",
            "map_type": "MAP_TYPE_UNDERGROUND", "allow_cycling": True, "allow_escaping": True,
            "allow_running": True, "show_map_name": True, "floor_number": 0,
            "battle_scene": "MAP_BATTLE_SCENE_NORMAL", "connections": None,
            "object_events": list(objects),
            "warp_events": [{"x": x, "y": y, "elevation": 3, "dest_map": m, "dest_warp_id": str(i)}
                            for (x, y, m, i) in warps],
            "coord_events": [], "bg_events": []}

def main():
    W, H, g, lad, stats = build_tunnel()
    wr('DiglettsCave_JohtoTunnel', g)
    with open(os.path.join(REPO, 'data/layouts/DiglettsCave_JohtoTunnel/border.bin'), 'wb') as f:
        f.write(struct.pack('<4H', *([ROCK] * 4)))
    print('tunnel %dx%d ladders %s edge picks %s' % (W, H, lad, stats))

    # Blackthorn entrance room: own copy of the untouched FRLG north-entrance room (copied once, before the edit)
    bd = os.path.join(REPO, 'data/layouts/DiglettsCave_BlackthornEntrance')
    if not os.path.exists(os.path.join(bd, 'map.bin')):
        os.makedirs(bd, exist_ok=True)
        ne0 = rd('DiglettsCave_NorthEntrance_Frlg', 10, 8)
        assert ne0[2][7] != ne0[4][6], 'north entrance already edited; restore it before the first copy'
        wr('DiglettsCave_BlackthornEntrance', ne0)
        import shutil
        shutil.copy(os.path.join(REPO, 'data/layouts/DiglettsCave_NorthEntrance_Frlg/border.bin'), bd)

    # FLAGGED FRLG EDIT: 2nd ladder in the Route 2 entrance room
    ne = rd('DiglettsCave_NorthEntrance_Frlg', 10, 8)
    ne[2][7] = ne[4][6]          # copy the existing ladder cell (0x2AF, elevation 3, passable)
    wr('DiglettsCave_NorthEntrance_Frlg', ne)
    p = os.path.join(REPO, 'data/maps/DiglettsCave_NorthEntrance_Frlg/map.json'); m = json.load(open(p))
    m['warp_events'] = [w for w in m['warp_events'] if not (w['x'] == 7 and w['y'] == 2)]
    m['warp_events'].append({"x": 7, "y": 2, "elevation": 3, "dest_map": "MAP_DIGLETTS_CAVE_JOHTO_TUNNEL", "dest_warp_id": "0"})
    dump_json(p, m)

    # tunnel map
    d = os.path.join(REPO, 'data/maps/DiglettsCave_JohtoTunnel'); os.makedirs(d, exist_ok=True)
    (kx, ky), (jx, jy) = lad['K'], lad['J']
    dump_json(os.path.join(d, 'map.json'), map_json(
        'DiglettsCave_JohtoTunnel', 'MAP_DIGLETTS_CAVE_JOHTO_TUNNEL', 'LAYOUT_DIGLETTS_CAVE_JOHTO_TUNNEL',
        [(kx, ky, 'MAP_DIGLETTS_CAVE_NORTH_ENTRANCE', 2), (jx, jy, 'MAP_DIGLETTS_CAVE_BLACKTHORN_ENTRANCE', 0)]))
    open(os.path.join(d, 'scripts.inc'), 'w').write(
        'DiglettsCave_JohtoTunnel_MapScripts::\n'
        '\tmap_script MAP_SCRIPT_ON_TRANSITION, DiglettsCave_JohtoTunnel_OnTransition\n\t.byte 0\n\n'
        'DiglettsCave_JohtoTunnel_OnTransition::\n\tsetworldmapflag FLAG_WORLD_MAP_DIGLETTS_CAVE_B1F\n\tend\n')

    # Blackthorn entrance room
    d = os.path.join(REPO, 'data/maps/DiglettsCave_BlackthornEntrance'); os.makedirs(d, exist_ok=True)
    bt = json.load(open(os.path.join(REPO, 'data/maps/BlackthornCity/map.json')))
    bidx = next(i for i, w in enumerate(bt['warp_events']) if (w['x'], w['y']) == (4, 23)) \
        if any((w['x'], w['y']) == (4, 23) for w in bt['warp_events']) else len(bt['warp_events'])
    dump_json(os.path.join(d, 'map.json'), map_json(
        'DiglettsCave_BlackthornEntrance', 'MAP_DIGLETTS_CAVE_BLACKTHORN_ENTRANCE', 'LAYOUT_DIGLETTS_CAVE_BLACKTHORN_ENTRANCE',
        [(6, 4, 'MAP_DIGLETTS_CAVE_JOHTO_TUNNEL', 1), (4, 6, 'MAP_BLACKTHORN_CITY', bidx)],
        objects=[{"type": "object", "graphics_id": "OBJ_EVENT_GFX_HIKER_FRLG", "x": 3, "y": 4, "elevation": 3,
                  "movement_type": "MOVEMENT_TYPE_LOOK_AROUND", "movement_range_x": 1, "movement_range_y": 1,
                  "trainer_type": "TRAINER_TYPE_NONE", "trainer_sight_or_berry_tree_id": "0",
                  "script": "DiglettsCave_BlackthornEntrance_EventScript_Hiker", "flag": "0"}]))
    open(os.path.join(d, 'scripts.inc'), 'w').write(
        'DiglettsCave_BlackthornEntrance_MapScripts::\n\t.byte 0\n\n'
        'DiglettsCave_BlackthornEntrance_EventScript_Hiker::\n'
        '\tmsgbox DiglettsCave_BlackthornEntrance_Text_Hiker, MSGBOX_NPC\n\tend\n\n'
        'DiglettsCave_BlackthornEntrance_Text_Hiker::\n'
        '\t.string "The DIGLETT dug this tunnel all the\\n"\n'
        '\t.string "way from KANTO!\\p"\n'
        '\t.string "Follow it and you\'ll come out by\\n"\n'
        '\t.string "PEWTER CITY on ROUTE 2.$"\n')

    # Blackthorn door warp
    if not any((w['x'], w['y']) == (4, 23) for w in bt['warp_events']):
        bt['warp_events'].append({"x": 4, "y": 23, "elevation": 0,
                                  "dest_map": "MAP_DIGLETTS_CAVE_BLACKTHORN_ENTRANCE", "dest_warp_id": "1"})
        dump_json(os.path.join(REPO, 'data/maps/BlackthornCity/map.json'), bt)

    # registrations
    register('gMapGroup_IndoorJohto', 'DiglettsCave_JohtoTunnel', W, H, 'gTileset_DiglettsCave')
    lp = os.path.join(REPO, 'data/layouts/layouts.json'); lj = json.load(open(lp))
    src = next(l for l in lj['layouts'] if l['id'] == 'LAYOUT_DIGLETTS_CAVE_NORTH_ENTRANCE')
    if not any(l['id'] == 'LAYOUT_DIGLETTS_CAVE_BLACKTHORN_ENTRANCE' for l in lj['layouts']):
        n = dict(src); n['id'] = 'LAYOUT_DIGLETTS_CAVE_BLACKTHORN_ENTRANCE'; n['name'] = 'DiglettsCave_BlackthornEntrance_Layout'
        n['border_filepath'] = 'data/layouts/DiglettsCave_BlackthornEntrance/border.bin'
        n['blockdata_filepath'] = 'data/layouts/DiglettsCave_BlackthornEntrance/map.bin'
        lj['layouts'].append(n)
        open(lp, 'w').write(json.dumps(lj, indent=2, ensure_ascii=False) + '\n')
    register('gMapGroup_IndoorJohto', 'DiglettsCave_BlackthornEntrance', 0, 0, None)

if __name__ == '__main__':
    main()
