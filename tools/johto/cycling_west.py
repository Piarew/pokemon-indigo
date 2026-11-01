#!/usr/bin/env python3
"""Custom route (B): CYCLING ROAD WEST - a bike-only extension of the FireRed Cycling Road from Route 16
(Celadon's west side) westward to Viridian City.  Appended to run_all.sh; idempotent.

New map CyclingRoadWest (64x26, gTileset_General_Frlg + gTileset_CeladonCity, MUS_RG_CYCLING), built from the
semantic grid designs/CyclingRoadWest.txt:
  T trees  g grass  t tall grass  p dirt path  f fence  s sign
  c Route-17 cycling ground (pull-down)  l striped bike lane (pull-down, 3 wide)  y pull-down grass
  L / R  Route-17 lamp-pole fence (left / right side)
East segment (rows 5-8) joins Route 16's cycling-road pocket, a Route-17-style downhill section (pull-down tiles:
riders coast south going west, pedal uphill going east) drops to the west segment (rows 17-20), which joins Viridian.
Bike-only: the map mirrors Route 16's scripts (VAR_MAP_SCENE_ROUTE16 == 1 -> FLAG_SYS_ON_CYCLING_ROAD, forced bike);
at the Viridian end coord triggers stand in for a gatehouse: x=4 (eastbound, var 0) refuses pedestrians, else sets
var/flag; x=3 (westbound, var 1) runs the stock EventScript_SetExitingCyclingRoad.

FIRERED EDITS (flagged; rebuilt from the untouched upstream copy at BASE_COMMIT every run):
  * Route16_Frlg map.bin   : x0-1, y11-14 (sea strip + fence) -> grass, a 4-tile gap into the new map
    Route16_Frlg map.json  : + connection left  MAP_CYCLING_ROAD_WEST offset 6
  * ViridianCity_Frlg map.bin : x42-47, y22-23 (one tree row of the east forest) -> grass; y21 -> tree-bottom
    edge tiles, y24 -> tree-top edge tiles
    ViridianCity_Frlg map.json : + connection right MAP_CYCLING_ROAD_WEST offset 4
usage: python3 tools/johto/cycling_west.py"""
import json, os, struct, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
from register_maps import register

NAME, MID = 'CyclingRoadWest', 'MAP_CYCLING_ROAD_WEST'
BASE_COMMIT = '72bd0bff9c'
P, B = 0x3000, 0x0400            # passable (elevation 3) / blocked

def tile_grid(g):
    H, W = len(g), len(g[0])
    at = lambda x, y, d='T': g[y][x] if 0 <= x < W and 0 <= y < H else d
    out = [[0] * W for _ in range(H)]
    runs = {}
    for y in range(H):
        for x in range(W):
            c = g[y][x]
            if c == 'T':
                top, left = y % 2 == 0, x % 2 == 0
                if top:
                    v = 0x01E if left and (at(x - 1, y) != 'T' or at(x, y - 1) != 'T') else \
                        0x01F if not left and at(x, y - 1) != 'T' else (0x01C if left else 0x01D)
                elif at(x, y + 1) != 'T':
                    v = 0x026 if left and at(x - 1, y) != 'T' else (0x024 if left else 0x025)
                else:
                    v = 0x016 if left and at(x - 1, y) != 'T' else (0x014 if left else 0x015)
                out[y][x] = B | v
            elif c in 'gs':
                out[y][x] = (P | (0x008 + x % 2 if y % 2 else 0x010 + x % 2)) if c == 'g' else B | 0x355
            elif c == 't':
                out[y][x] = P | 0x00D
            elif c == 'f':
                out[y][x] = B | 0x0E7
            elif c == 'p':
                u, d, l, r = at(x, y - 1) != 'p', at(x, y + 1) != 'p', at(x - 1, y) != 'p', at(x + 1, y) != 'p'
                row = 0 if u else 2 if d else 1
                col = 0 if l else 2 if r else 1
                out[y][x] = P | (0x0D3 + 8 * row + col)
            elif c == 'c':
                out[y][x] = P | ((0x33E if y % 2 == 0 else 0x346) + x % 2)
            elif c == 'y':
                out[y][x] = P | 0x352
            elif c == 'l':
                row = 0 if at(x, y - 1) != 'l' else 2 if at(x, y + 1) != 'l' else 1
                col = 0 if at(x - 1, y) != 'l' else 2 if at(x + 1, y) != 'l' else 1
                out[y][x] = P | ((0x320, 0x328, 0x330)[row] + col)
            elif c in 'LR':
                y0 = y
                while at(x, y0 - 1) == c: y0 -= 1
                k = (y - y0) % 5
                if c == 'L':
                    out[y][x] = B | (0x323, 0x32B, 0x333, 0x0F5, 0x0F5)[k]
                else:
                    out[y][x] = B | (0x325, 0x32D, 0x335, 0x0F4, 0x0F4)[k]
            else:
                raise SystemExit('unknown design char %r at %d,%d' % (c, x, y))
    # lamp heads drawn on the cycling ground beside the poles (Route 17: 324/334 right of L, 32C left of R)
    for y in range(H):
        for x in range(W):
            if g[y][x] == 'L' and at(x + 1, y) == 'c':
                k = out[y][x] & 0x3FF
                if k == 0x323: out[y][x + 1] = P | 0x324
                if k == 0x333: out[y][x + 1] = P | 0x334
            if g[y][x] == 'R' and at(x - 1, y) == 'c' and out[y][x] & 0x3FF == 0x325:
                out[y][x - 1] = P | 0x32C
    return out

def write_bin(path, cells):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        for row in cells:
            f.write(struct.pack('<%dH' % len(row), *row))

def upstream(path, w, h):
    raw = subprocess.check_output(['git', 'show', '%s:%s' % (BASE_COMMIT, path)], cwd=REPO)
    assert len(raw) == w * h * 2, path
    return [[struct.unpack_from('<H', raw, (y * w + x) * 2)[0] for x in range(w)] for y in range(h)]

def add_connection(mapdir, conn):
    p = os.path.join(REPO, 'data/maps', mapdir, 'map.json')
    j = json.load(open(p))
    cs = [c for c in (j.get('connections') or []) if c['map'] != conn['map']]
    assert not any(c['direction'] == conn['direction'] for c in cs), (mapdir, 'edge already used')
    j['connections'] = cs + [conn]
    open(p, 'w').write(json.dumps(j, indent=2, ensure_ascii=False) + '\n')

def frlg_edits():
    grass = lambda x, y: P | (0x008 + x % 2 if y % 2 else 0x010 + x % 2)
    # Route 16: open the cycling-road pocket's west fence / sea strip (x0-1, y11-14)
    b16 = 'data/layouts/Route16_Frlg/map.bin'
    g = upstream(b16, 48, 20)
    for y in range(11, 15):
        for x in range(0, 2):
            g[y][x] = grass(x, y)
    write_bin(os.path.join(REPO, b16), g)
    add_connection('Route16_Frlg', {'map': MID, 'offset': 6, 'direction': 'left'})
    # Viridian: cut one tree row (y22-23) through the east forest (x42-47)
    bv = 'data/layouts/ViridianCity_Frlg/map.bin'
    g = upstream(bv, 48, 40)
    for x in range(42, 48):
        g[21][x] = B | (0x026 if x == 42 else 0x024 + x % 2)
        g[22][x] = grass(x, 22); g[23][x] = grass(x, 23)
        g[24][x] = B | (0x01E + x % 2)
    write_bin(os.path.join(REPO, bv), g)
    add_connection('ViridianCity_Frlg', {'map': MID, 'offset': 4, 'direction': 'right'})

SCRIPTS = '''CyclingRoadWest_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, CyclingRoadWest_OnTransition
	map_script MAP_SCRIPT_ON_WARP_INTO_MAP_TABLE, CyclingRoadWest_OnWarp
	.byte 0

@ same as Route 16: still on the Cycling Road -> keep the forced-bike flag
CyclingRoadWest_OnTransition::
	call_if_eq VAR_MAP_SCENE_ROUTE16, 1, CyclingRoadWest_OnTransitionCyclingRoad
	end

CyclingRoadWest_OnTransitionCyclingRoad::
	setflag FLAG_SYS_ON_CYCLING_ROAD
	return

CyclingRoadWest_OnWarp::
	map_script_2 VAR_MAP_SCENE_ROUTE16, 1, CyclingRoadWest_OnWarpCyclingRoad
	.2byte 0

CyclingRoadWest_OnWarpCyclingRoad::
	special ForcePlayerOntoBike
	end

@ Viridian end, eastbound (VAR_MAP_SCENE_ROUTE16 == 0): stand-in for a Cycling Road gatehouse
CyclingRoadWest_EventScript_EnterCyclingRoad::
	lockall
	specialvar VAR_RESULT, GetPlayerAvatarBike
	goto_if_eq VAR_RESULT, 0, CyclingRoadWest_EventScript_NoPedestrians
	setvar VAR_MAP_SCENE_ROUTE16, 1
	setflag FLAG_SYS_ON_CYCLING_ROAD
	releaseall
	end

CyclingRoadWest_EventScript_NoPedestrians::
	msgbox CyclingRoadWest_Text_NoPedestrians
	closemessage
	applymovement LOCALID_PLAYER, CyclingRoadWest_Movement_WalkLeft
	waitmovement 0
	releaseall
	end

CyclingRoadWest_Movement_WalkLeft:
	walk_left
	step_end

CyclingRoadWest_EventScript_WestSign::
	msgbox CyclingRoadWest_Text_WestSign, MSGBOX_SIGN
	end

CyclingRoadWest_EventScript_EastSign::
	msgbox CyclingRoadWest_Text_EastSign, MSGBOX_SIGN
	end

CyclingRoadWest_Text_NoPedestrians:
	.string "No pedestrians are allowed on\\n"
	.string "CYCLING ROAD!\\p"
	.string "Please come back on a BIKE.$"

CyclingRoadWest_Text_WestSign:
	.string "CYCLING ROAD WEST\\n"
	.string "VIRIDIAN CITY - CELADON CITY\\p"
	.string "BIKES ONLY! Uphill to CELADON.$"

CyclingRoadWest_Text_EastSign:
	.string "CYCLING ROAD WEST\\n"
	.string "Downhill to VIRIDIAN CITY.$"
'''

def map_json():
    trig = lambda x, y, val, script: {'type': 'trigger', 'x': x, 'y': y, 'elevation': 0,
                                      'var': 'VAR_MAP_SCENE_ROUTE16', 'var_value': val, 'script': script}
    coords = []
    for y in (18, 19):
        coords.append(trig(4, y, '0', 'CyclingRoadWest_EventScript_EnterCyclingRoad'))
        coords.append(trig(3, y, '1', 'EventScript_SetExitingCyclingRoad'))
    sign = lambda x, y, s: {'type': 'sign', 'x': x, 'y': y, 'elevation': 0,
                            'player_facing_dir': 'BG_EVENT_PLAYER_FACING_ANY', 'script': s}
    return {'id': MID, 'name': NAME, 'layout': 'LAYOUT_CYCLING_ROAD_WEST', 'music': 'MUS_RG_CYCLING',
            'region': 'REGION_KANTO', 'region_map_section': 'MAPSEC_ROUTE_16', 'requires_flash': False,
            'weather': 'WEATHER_SUNNY', 'map_type': 'MAP_TYPE_ROUTE', 'allow_cycling': True,
            'allow_escaping': False, 'allow_running': True, 'show_map_name': False, 'floor_number': 0,
            'battle_scene': 'MAP_BATTLE_SCENE_NORMAL',
            'connections': [{'map': 'MAP_VIRIDIAN_CITY', 'offset': -4, 'direction': 'left'},
                            {'map': 'MAP_ROUTE16', 'offset': -6, 'direction': 'right'}],
            'object_events': [], 'warp_events': [], 'coord_events': coords,
            'bg_events': [sign(7, 17, 'CyclingRoadWest_EventScript_WestSign'),
                          sign(47, 5, 'CyclingRoadWest_EventScript_EastSign')]}

# GSC Kanto Route 17 flavour (day), FRLG 12-slot layout; grass patches only
LAND = [('RATICATE', 26), ('FEAROW', 27), ('DODUO', 26), ('PONYTA', 27), ('RATTATA', 24),
        ('SPEAROW', 24), ('RATICATE', 28), ('FEAROW', 29), ('DODUO', 28), ('PONYTA', 29), ('DODRIO', 30), ('RAPIDASH', 30)]

def wild():
    p = os.path.join(REPO, 'src/data/wild_encounters.json'); wj = json.load(open(p))
    grp = next(g for g in wj['wild_encounter_groups']
               if any(e.get('base_label', '').startswith('sFourIslandIcefallCave1F_') for e in g.get('encounters', [])))
    enc = grp['encounters']
    enc[:] = [e for e in enc if e.get('map') != MID]
    for ver in ('FireRed', 'LeafGreen'):
        enc.append({'map': MID, 'base_label': 's%s_%s' % (NAME, ver), 'land_mons': {'encounter_rate': 15, 'mons': [
            {'min_level': l, 'max_level': l, 'species': 'SPECIES_' + s} for s, l in LAND]}})
    open(p, 'w').write(json.dumps(wj, indent=2, ensure_ascii=False) + '\n')

def main():
    g = [list(r) for r in open(os.path.join(HERE, 'designs', NAME + '.txt')).read().split()]
    H, W = len(g), len(g[0])
    assert all(len(r) == W for r in g) and (W + 15) * (H + 14) <= 10240
    write_bin(os.path.join(REPO, 'data/layouts', NAME, 'map.bin'), tile_grid(g))
    write_bin(os.path.join(REPO, 'data/layouts', NAME, 'border.bin'), [[B | 0x01C, B | 0x01D], [B | 0x014, B | 0x015]])
    md = os.path.join(REPO, 'data/maps', NAME); os.makedirs(md, exist_ok=True)
    open(os.path.join(md, 'map.json'), 'w').write(json.dumps(map_json(), indent=2) + '\n')
    open(os.path.join(md, 'scripts.inc'), 'w').write(SCRIPTS)
    register('gMapGroup_TownsAndRoutes_Frlg', NAME, W, H, 'gTileset_CeladonCity')
    frlg_edits()
    wild()
    print('cycling_west: %s %dx%d, Route16 <-> %s <-> ViridianCity' % (NAME, W, H, NAME))

if __name__ == '__main__':
    main()
