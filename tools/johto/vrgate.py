#!/usr/bin/env python3
"""Victory Road Gate (Phase 6).  Run after gsc_cave.py (it patches Route26, which johto_convert.py regenerates).
- Stamps the FRLG League-gate south facade (Route22_Frlg rows 0-6, cols 4-12; same ViridianCity tileset) into the
  top of Route26 east of the mountain pass, with a path from the pass to its door.
- New map VictoryRoadGate reusing LAYOUT_ROUTE22_NORTH_ENTRANCE unchanged (no objects/scripts):
  south door <-> Route26 (14,5)/(15,5); north exit (7,1) -> Route23 warp #2 (in front of the FRLG League gate),
  ONE-WAY: Route23 / Route22_NorthEntrance are not modified (Indigo Plateau area is reserved for the owner's edits),
  so walking back from Route23 goes through the FRLG gate to Route22 and down the pass into Route26.
Idempotent."""
import json, os, struct, sys
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
from register_maps import register

def grid(path, w):
    d = open(os.path.join(REPO, path), 'rb').read(); v = list(struct.unpack('<%dH' % (len(d) // 2), d))
    return [v[i * w:(i + 1) * w] for i in range(len(v) // w)]

def save(path, g):
    with open(os.path.join(REPO, path), 'wb') as f:
        for r in g:
            for v in r: f.write(struct.pack('<H', v))

R22, R26 = 'data/layouts/Route22_Frlg/map.bin', 'data/layouts/Route26/map.bin'
g22, g26 = grid(R22, 48), grid(R26, 20)
X0 = 10                                           # facade cols 4..12 of Route22 -> Route26 cols 10..18
for y in range(7):
    for i in range(9): g26[y][X0 + i] = g22[y][4 + i]
PATH, PL, PR, MT = 0xdc | 0x3000, 0xdb | 0x3000, 0xdd | 0x3000, 0x71 | 0x400
for x in range(9, 18): g26[7][x] = PATH           # path from the pass east under the gate steps
g26[7][18] = PR; g26[7][19] = 0x70 | 0x400        # right path edge / mountain left edge
for x in range(10, 13): g26[8][x] = PATH          # old top edge of the widening below -> plain path
g26[8][13] = PR
g26[8][14] = 0x78 | 0x400                          # mountain top-left corner, then top edge
for x in range(15, 20): g26[8][x] = 0x79 | 0x400
save(R26, g26)

DOORS = [(14, 5), (15, 5)]
p = os.path.join(REPO, 'data/maps/Route26/map.json'); mj = json.load(open(p))
old = [i for i, w in enumerate(mj['warp_events']) if w['dest_map'] == 'MAP_VICTORY_ROAD_GATE']
base = old[0] if old else len(mj['warp_events'])   # replace in place: other warp indices stay stable on re-runs
assert not old or old == [base, base + 1], old
for k, (x, y) in enumerate(DOORS):
    w = {"x": x, "y": y, "elevation": 0, "dest_map": "MAP_VICTORY_ROAD_GATE", "dest_warp_id": "1"}
    if old: mj['warp_events'][base + k] = w
    else: mj['warp_events'].append(w)
open(p, 'w').write(json.dumps(mj, indent=2) + '\n')

t = json.load(open(os.path.join(REPO, 'data/maps/Route22_NorthEntrance_Frlg/map.json')))
t.update(id='MAP_VICTORY_ROAD_GATE', name='VictoryRoadGate', object_events=[], coord_events=[], bg_events=[],
         region_map_section='MAPSEC_ROUTE_22', music='MUS_RG_VIRIDIAN_FOREST')
t['warp_events'] = [{"x": 7, "y": 1, "elevation": 3, "dest_map": "MAP_ROUTE23", "dest_warp_id": "2"}] + \
    [{"x": x, "y": 10, "elevation": 3, "dest_map": "MAP_ROUTE26", "dest_warp_id": str(base)} for x in (6, 7, 8)]
d = os.path.join(REPO, 'data/maps/VictoryRoadGate'); os.makedirs(d, exist_ok=True)
open(os.path.join(d, 'map.json'), 'w').write(json.dumps(t, indent=2) + '\n')
open(os.path.join(d, 'scripts.inc'), 'w').write('VictoryRoadGate_MapScripts::\n\t.byte 0\n')
register('gMapGroup_IndoorJohto', 'VictoryRoadGate', 0, 0, None)
print('Route26 gate doors', DOORS, 'warp ids', base, base + 1)
