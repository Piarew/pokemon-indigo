#!/usr/bin/env python3
"""Warp audit for the Johto spike (read-only).
For each map: lists warp_events, checks that each warp's destination exists and points back
(dest map has a warp whose dest is this map), and lists warp-capable cells (doors, cave mouths,
ladders, arrow/stair warps, holes) that have no warp_event yet = the TODO list for interiors/caves.
Usage: python3 tools/johto/warp_audit.py [--dump] [MapDir ...]   (default: all Johto maps)
  --dump also prints a metatile/collision grid of each map (for authoring caves by hand)."""
import json, os, re, struct, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', 'cherrygrove'))
from tsdir import tileset_dir

JOHTO = ['CherrygroveCity', 'BlackthornCity', 'MahoganyTown', 'VioletCity', 'EcruteakCity', 'NewBarkTown',
         'Route26', 'Route27', 'Route28', 'Route29', 'Route30', 'Route31', 'Route42', 'Route43', 'Route44',
         'SilverCaveOutside']
NAMES = re.findall(r'^\s*(MB_\w+)', open(os.path.join(REPO, 'include/constants/metatile_behaviors.h')).read(), re.M)
WARPY = {'MB_NON_ANIMATED_DOOR', 'MB_ANIMATED_DOOR', 'MB_LADDER', 'MB_SOUTH_ARROW_WARP', 'MB_NORTH_ARROW_WARP',
         'MB_EAST_ARROW_WARP', 'MB_WEST_ARROW_WARP', 'MB_UP_RIGHT_STAIR_WARP', 'MB_UP_LEFT_STAIR_WARP',
         'MB_DOWN_RIGHT_STAIR_WARP', 'MB_DOWN_LEFT_STAIR_WARP', 'MB_MT_PYRE_HOLE', 'MB_FALL_WARP'}
layouts = {l['id']: l for l in json.load(open(os.path.join(REPO, 'data/layouts/layouts.json')))['layouts'] if 'id' in l}
all_maps = {}
for p in glob.glob(os.path.join(REPO, 'data/maps/*/map.json')):
    m = json.load(open(p)); all_maps[m['id']] = m

def attrs(ts, primary):
    return open(os.path.join(tileset_dir(ts, primary), 'metatile_attributes.bin'), 'rb').read()

def behaviour(pa, sa, npri, mt):
    b, i = (pa, mt) if mt < npri else (sa, mt - npri)
    return NAMES[struct.unpack_from('<I', b, i * 4)[0] & 0x1FF] if i * 4 < len(b) else '?'

def audit(name, dump=False):
    m = json.load(open(os.path.join(REPO, 'data/maps', name, 'map.json')))
    l = layouts[m['layout']]
    w, h = l['width'], l['height']
    v = struct.unpack('<%dH' % (w * h), open(os.path.join(REPO, l['blockdata_filepath']), 'rb').read())
    pa, sa = attrs(l['primary_tileset'], True), attrs(l['secondary_tileset'], False)
    npri = len(pa) // 4
    warps = m.get('warp_events') or []
    have = {(wp['x'], wp['y']) for wp in warps}
    print('== %s (%s, %dx%d, %d warps)' % (name, m['id'], w, h, len(warps)))
    for i, wp in enumerate(warps):
        dest = all_maps.get(wp['dest_map'])
        if wp['dest_map'] == 'MAP_DYNAMIC':
            st = 'dynamic'
        elif not dest:
            st = '!! dest map missing'
        else:
            back = [j for j, b in enumerate(dest.get('warp_events') or []) if b['dest_map'] == m['id']]
            st = 'ok (back warps %s)' % back if back else '!! no warp back'
        print('  warp %d (%d,%d) -> %s #%s  %s' % (i, wp['x'], wp['y'], wp['dest_map'], wp['dest_warp_id'], st))
    todo = []
    for y in range(h):
        for x in range(w):
            b = behaviour(pa, sa, npri, v[y * w + x] & 0x3FF)
            if b in WARPY and (x, y) not in have:
                todo.append('(%d,%d) %s' % (x, y, b.replace('MB_', '')))
    if todo:
        print('  warp-capable cells without warp: ' + ', '.join(todo))
    if dump:
        for y in range(h):
            print('  %3d ' % y + ' '.join('%03x%s' % (c & 0x3FF, '#' if (c >> 10) & 3 else '.') for c in v[y * w:(y + 1) * w]))

if __name__ == '__main__':
    args = sys.argv[1:]
    dump = '--dump' in args
    names = [a for a in args if a != '--dump'] or JOHTO
    for n in names:
        audit(n, dump)
