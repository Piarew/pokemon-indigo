#!/usr/bin/env python3
"""Minimal, reproducible edits to existing FRLG maps so the converted Johto maps can connect.

Route 22 (data/layouts/Route22_Frlg/map.bin) is rebuilt from the untouched upstream copy
(BASE_COMMIT) every run:
  * west edge  : Route 22's striped dirt road (rows 16-18) is extended through the cliff at x0-3
                 (road tiles copied from column 6, also replacing the road's left end at x4) -> Route 28
  * south edge : a 2-wide sand pass (x8-9) is carved through the mountain rows 19-23 -> Route 26
Mountain/sand cells around the carves are re-picked with the same learned tilers the converter
uses.  Connections are added to data/maps/Route22_Frlg/map.json (idempotent).
Usage: python3 tools/johto/frlg_edits.py"""
import json, os, struct, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from johto_convert import learned, common_attrs, SAND_PATH, REPO
from families import mountain_family

BASE_COMMIT = '72bd0bff9c'
BIN = 'data/layouts/Route22_Frlg/map.bin'
W, H = 48, 24
ROAD = {(x, y) for x in range(0, 5) for y in range(16, 19)}      # copied from (6, y)
CARVE = {(x, y) for x in range(8, 10) for y in range(19, 24)}     # learned sand tiler
NEW_CONNECTIONS = [{'map': 'MAP_ROUTE28', 'offset': 10, 'direction': 'left'},
                   {'map': 'MAP_ROUTE26', 'offset': 1, 'direction': 'down'}]

def main():
    raw = subprocess.check_output(['git', 'show', f'{BASE_COMMIT}:{BIN}'], cwd=REPO)
    assert len(raw) == W * H * 2
    b = [[struct.unpack_from('<H', raw, (y * W + x) * 2)[0] for x in range(W)] for y in range(H)]
    fam, _ = mountain_family()
    sem = [['M' if (b[y][x] & 0x3FF) in fam else 'P' if (b[y][x] & 0x3FF) in SAND_PATH else '.'
            for x in range(W)] for y in range(H)]
    for x, y in CARVE:
        sem[y][x] = 'P'
    for x, y in ROAD:
        sem[y][x] = 'R'; b[y][x] = b[y][6]
    for y in range(16, 19):
        for x in range(W):
            if sem[y][x] == '.' and (b[y][x] & 0x3FF) in (0x163, 0x16B, 0x173):
                sem[y][x] = 'R'
    def S(x, y):
        if 0 <= x < W and 0 <= y < H:
            return sem[y][x]
        x, y = min(max(x, 0), W - 1), min(max(y, 0), H - 1)   # off-map: continue the edge
        return sem[y][x]
    mtn = lambda x, y: S(x, y) == 'M'
    sand = lambda x, y: S(x, y) in ('P', 'R')
    attrs = common_attrs('gTileset_ViridianCity')
    near = {(x + dx, y + dy) for x, y in CARVE | ROAD for dx in range(-2, 3) for dy in range(-2, 3)}
    changed = sum(1 for x, y in ROAD)
    for x, y in sorted(near):
        if not (0 <= x < W and 0 <= y < H) or sem[y][x] in ('.', 'R'):
            continue
        m = (learned('mountain').pick(mtn, x, y) if sem[y][x] == 'M' else learned('sand').pick(sand, x, y))
        if m in (0x073, 0x07D) and all(mtn(x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
            m = 0x071
        v = m | attrs.get(m, 0)
        if v != b[y][x]:
            b[y][x] = v; changed += 1
    with open(os.path.join(REPO, BIN), 'wb') as f:
        f.write(b''.join(struct.pack('<H', b[y][x]) for y in range(H) for x in range(W)))
    p = os.path.join(REPO, 'data/maps/Route22_Frlg/map.json')
    j = json.load(open(p))
    for c in NEW_CONNECTIONS:
        if not any(e['map'] == c['map'] for e in j['connections']):
            j['connections'].append(c)
    with open(p, 'w') as f:
        f.write(json.dumps(j, indent=2, ensure_ascii=False) + '\n')
    print(f'Route22: {changed} cells changed, connections', [c['map'] for c in j['connections']])

if __name__ == '__main__':
    main()
