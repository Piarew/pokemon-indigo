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
Bike-only: the map mirrors Route 16's scripts (VAR_MAP_SCENE_ROUTE16 == 1 -> FLAG_SYS_ON_CYCLING_ROAD, forced bike).
At the Viridian end a real Cycling Road gatehouse plugs the corridor ('G' in the design = the lower block of FireRed
Route 16's gate exterior, x20-27 y8-14, copied tile-for-tile; doors x4/x11 y18).  Its interior CyclingRoadWestGate_1F
reuses LAYOUT_ROUTE16_NORTH_ENTRANCE_1F and a mirrored copy of the Route 16 gate script (guard; no BICYCLE ->
"No pedestrians" and stepped back WEST; reaching the east door sets VAR_MAP_SCENE_ROUTE16=1; reaching the west door
runs EventScript_SetExitingCyclingRoad, and the gate's OnTransition clears FLAG_SYS_ON_CYCLING_ROAD).  The upper
room of that layout (Route 16's pedestrian pass) is unused/unreachable.  CyclingRoadWestGate_2F reuses
LAYOUT_ENTRANCE_2F (binoculars + two cyclists).

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
from interiors import snake_upper

NAME, MID = 'CyclingRoadWest', 'MAP_CYCLING_ROAD_WEST'
BASE_COMMIT = '72bd0bff9c'
P, B = 0x3000, 0x0400            # passable (elevation 3) / blocked
GATE = (4, 13)                   # top-left of the 8x7 gatehouse; doors at (x+0, y+5) west and (x+7, y+5) east
G1, G2 = NAME + 'Gate_1F', NAME + 'Gate_2F'

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
            elif c == 'G':
                pass                                # gatehouse, overlaid below
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
    # gatehouse: lower block of Route 16's gate exterior (upstream x20-27 y8-14)
    gx, gy = GATE
    src = upstream('data/layouts/Route16_Frlg/map.bin', 48, 20)
    for dy in range(7):
        for dx in range(8):
            if g[gy + dy][gx + dx] == 'G':
                out[gy + dy][gx + dx] = src[8 + dy][20 + dx]
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

def gate_maps():
    """Gate interior (Route 16 gate layout + mirrored bike-check script) and its 2F."""
    raw = subprocess.check_output(['git', 'show', BASE_COMMIT + ':data/maps/Route16_NorthEntrance_1F_Frlg/scripts.inc'],
                                  cwd=REPO).decode()
    sc = raw.replace('Route16_NorthEntrance_1F_Frlg_MapScripts', G1 + '_MapScripts').replace('Route16_NorthEntrance_1F', G1)
    # the cycling road lies EAST of this gate (Route 16's lies west): turn pedestrians back westward
    sc = sc.replace(G1 + '_Movement_WalkRight', G1 + '_Movement_WalkLeft').replace(
        G1 + '_Movement_WalkLeft::\n\twalk_right', G1 + '_Movement_WalkLeft::\n\twalk_left')
    sc = sc.replace('"CYCLING ROAD is a downhill course\\n"\n\t.string "by the sea. It\'s a great ride.$"',
                    '"CYCLING ROAD WEST climbs all the\\n"\n\t.string "way to CELADON. Good luck!$"')
    assert 'walk_right' not in sc and 'climbs all' in sc
    os.makedirs(os.path.join(REPO, 'data/maps', G1), exist_ok=True)
    open(os.path.join(REPO, 'data/maps', G1, 'scripts.inc'), 'w').write(sc)
    j = json.loads(subprocess.check_output(['git', 'show', BASE_COMMIT + ':data/maps/Route16_NorthEntrance_1F_Frlg/map.json'],
                                           cwd=REPO))
    mid1, mid2 = 'MAP_' + snake_upper(G1), 'MAP_' + snake_upper(G2)
    j.update(id=mid1, name=G1, region_map_section='MAPSEC_ROUTE_16')
    j['object_events'] = [dict(o, script=o['script'].replace('Route16_NorthEntrance_1F', G1))
                          for o in j['object_events'] if 'Guard' in o['script']]      # upper room unused: no old man
    j['warp_events'] = [{'x': 1, 'y': 12, 'elevation': 3, 'dest_map': MID, 'dest_warp_id': '0'},
                        {'x': 11, 'y': 12, 'elevation': 3, 'dest_map': MID, 'dest_warp_id': '1'},
                        {'x': 9, 'y': 16, 'elevation': 3, 'dest_map': mid2, 'dest_warp_id': '0'},
                        # upper room (Route 16's pedestrian pass) is unreachable here; its arrow warps get
                        # one-way targets so they are never dangling
                        {'x': 1, 'y': 3, 'elevation': 3, 'dest_map': MID, 'dest_warp_id': '0'},
                        {'x': 11, 'y': 3, 'elevation': 3, 'dest_map': MID, 'dest_warp_id': '1'}]
    trig = lambda x, y, var, val, script: {'type': 'trigger', 'x': x, 'y': y, 'elevation': 3, 'var': var,
                                           'var_value': val, 'script': script}
    co = []
    for y, k in zip(range(10, 15), ('Top', 'MidTop', 'Mid', 'MidBottom', 'Bottom')):     # bike check at the counter
        co.append(trig(6, y, 'VAR_TEMP_1', '0', '%s_EventScript_NeedBikeTrigger%s' % (G1, k)))
    for x, y in ((2, 12), (1, 11), (1, 13)):        # west (Viridian) side: leaving the Cycling Road
        co.append(trig(x, y, 'VAR_MAP_SCENE_ROUTE16', '1', 'EventScript_SetExitingCyclingRoad'))
    for x, y in ((10, 12), (11, 11), (11, 13)):     # east (road) side: entering the Cycling Road
        co.append(trig(x, y, 'VAR_MAP_SCENE_ROUTE16', '0', 'EventScript_SetEnteringCyclingRoad'))
    j['coord_events'] = co
    open(os.path.join(REPO, 'data/maps', G1, 'map.json'), 'w').write(json.dumps(j, indent=2) + '\n')

    j2 = json.loads(subprocess.check_output(['git', 'show', BASE_COMMIT + ':data/maps/Route16_NorthEntrance_2F_Frlg/map.json'],
                                            cwd=REPO))
    j2.update(id=mid2, name=G2)
    j2['warp_events'] = [{'x': 10, 'y': 9, 'elevation': 3, 'dest_map': mid1, 'dest_warp_id': '2'}]
    j2['object_events'] = [dict(o, script=o['script'].replace('Route16_NorthEntrance_2F', G2))
                           for o in j2['object_events'] if 'Aide' not in o['script']]
    j2['bg_events'] = [dict(b, script=b['script'].replace('Route16_NorthEntrance_2F', G2)) for b in j2['bg_events']]
    os.makedirs(os.path.join(REPO, 'data/maps', G2), exist_ok=True)
    open(os.path.join(REPO, 'data/maps', G2, 'map.json'), 'w').write(json.dumps(j2, indent=2) + '\n')
    open(os.path.join(REPO, 'data/maps', G2, 'scripts.inc'), 'w').write(GATE2F.replace('@G', G2))
    register('gMapGroup_IndoorJohto', G1, 0, 0, None)
    register('gMapGroup_IndoorJohto', G2, 0, 0, None)

GATE2F = """@G_MapScripts::
	.byte 0

@G_EventScript_LittleBoy::
	msgbox @G_Text_LittleBoy, MSGBOX_NPC
	end

@G_EventScript_LittleGirl::
	msgbox @G_Text_LittleGirl, MSGBOX_NPC
	end

@G_EventScript_LeftBinoculars::
	msgbox @G_Text_LeftBinoculars, MSGBOX_SIGN
	end

@G_EventScript_RightBinoculars::
	msgbox @G_Text_RightBinoculars, MSGBOX_SIGN
	end

@G_Text_LittleBoy:
	.string "Riding up to CELADON is tough,\\n"
	.string "but coasting back down is great!$"

@G_Text_LittleGirl:
	.string "We ride here from VIRIDIAN every\\n"
	.string "weekend.$"

@G_Text_LeftBinoculars:
	.string "Let's see what the binoculars have\\n"
	.string "to show…\\p"
	.string "It's VIRIDIAN CITY's POKéMON GYM!$"

@G_Text_RightBinoculars:
	.string "Let's see what the binoculars have\\n"
	.string "to show…\\p"
	.string "A bike road winds up the hill\\n"
	.string "toward CELADON.$"
"""

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

CyclingRoadWest_EventScript_WestSign::
	msgbox CyclingRoadWest_Text_WestSign, MSGBOX_SIGN
	end

CyclingRoadWest_EventScript_EastSign::
	msgbox CyclingRoadWest_Text_EastSign, MSGBOX_SIGN
	end

CyclingRoadWest_Text_WestSign:
	.string "CYCLING ROAD WEST\\n"
	.string "VIRIDIAN CITY - CELADON CITY\\p"
	.string "Uphill to CELADON. Keep pedaling!$"

CyclingRoadWest_Text_EastSign:
	.string "CYCLING ROAD WEST\\n"
	.string "Downhill to VIRIDIAN CITY.$"
'''

def map_json():
    sign = lambda x, y, s: {'type': 'sign', 'x': x, 'y': y, 'elevation': 0,
                            'player_facing_dir': 'BG_EVENT_PLAYER_FACING_ANY', 'script': s}
    return {'id': MID, 'name': NAME, 'layout': 'LAYOUT_CYCLING_ROAD_WEST', 'music': 'MUS_RG_CYCLING',
            'region': 'REGION_KANTO', 'region_map_section': 'MAPSEC_ROUTE_16', 'requires_flash': False,
            'weather': 'WEATHER_SUNNY', 'map_type': 'MAP_TYPE_ROUTE', 'allow_cycling': True,
            'allow_escaping': False, 'allow_running': True, 'show_map_name': False, 'floor_number': 0,
            'battle_scene': 'MAP_BATTLE_SCENE_NORMAL',
            'connections': [{'map': 'MAP_VIRIDIAN_CITY', 'offset': -4, 'direction': 'left'},
                            {'map': 'MAP_ROUTE16', 'offset': -6, 'direction': 'right'}],
            'object_events': [], 'coord_events': [],
            'warp_events': [{'x': GATE[0], 'y': GATE[1] + 5, 'elevation': 3, 'dest_map': 'MAP_' + snake_upper(G1), 'dest_warp_id': '0'},
                            {'x': GATE[0] + 7, 'y': GATE[1] + 5, 'elevation': 3, 'dest_map': 'MAP_' + snake_upper(G1), 'dest_warp_id': '1'}],
            'bg_events': [sign(13, 17, 'CyclingRoadWest_EventScript_WestSign'),
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
    gate_maps()
    frlg_edits()
    wild()
    print('cycling_west: %s %dx%d, Route16 <-> %s <-> ViridianCity' % (NAME, W, H, NAME))

if __name__ == '__main__':
    main()
