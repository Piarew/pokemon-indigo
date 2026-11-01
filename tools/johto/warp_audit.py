#!/usr/bin/env python3
"""Warp audit for the Johto spike (read-only).
For each map: lists warp_events, checks that each warp's destination exists and points back
(dest map has a warp whose dest is this map), and lists warp-capable cells (doors, cave mouths,
ladders, arrow/stair warps, holes) that have no warp_event yet = the TODO list for interiors/caves.
Usage: python3 tools/johto/warp_audit.py [--dump] [--quiet] [MapDir ...]
  default: all Johto outdoor maps + every map in the IndoorJohto group + Johto caves.
  --dump also prints a metatile/collision grid of each map (for authoring caves by hand).
Strict: exit status 1 if any warp is broken (missing dest map, dest_warp_id out of range, dest warp
not pointing back) or any warp-capable cell lacks a warp and is not in the TODO allowlist below."""
import json, os, re, struct, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', 'cherrygrove'))
from tsdir import tileset_dir

JOHTO = ['CherrygroveCity', 'BlackthornCity', 'MahoganyTown', 'VioletCity', 'EcruteakCity', 'NewBarkTown',
         'Route26', 'Route27', 'Route28', 'Route29', 'Route30', 'Route31', 'Route42', 'Route43', 'Route44', 'Route36', 'Route37',
         'SilverCaveOutside']
NAMES = re.findall(r'^\s*(MB_\w+)', open(os.path.join(REPO, 'include/constants/metatile_behaviors.h')).read(), re.M)
WARPY = {'MB_NON_ANIMATED_DOOR', 'MB_ANIMATED_DOOR', 'MB_LADDER', 'MB_SOUTH_ARROW_WARP', 'MB_NORTH_ARROW_WARP',
         'MB_EAST_ARROW_WARP', 'MB_WEST_ARROW_WARP', 'MB_UP_RIGHT_STAIR_WARP', 'MB_UP_LEFT_STAIR_WARP',
         'MB_DOWN_RIGHT_STAIR_WARP', 'MB_DOWN_LEFT_STAIR_WARP', 'MB_MT_PYRE_HOLE', 'MB_FALL_WARP'}
# Known, deliberately unwarped cells (towers/caves not built yet). (map dir, x, y): reason
TODO_ALLOW = {
    ('BlackthornCity', 20, 1): "Dragon's Den (TODO)",
    ('VioletCity', 23, 6): 'Sprout Tower (TODO)',
    ('EcruteakCity', 5, 6): 'Burned Tower (TODO)',
    ('EcruteakCity', 18, 11): 'Tin Tower entrance (TODO)',
    ('EcruteakCity', 36, 7): 'Bell/Tin Tower stand-in (TODO)',
    ('Route27', 26, 5): 'Tohjo Falls (TODO)',
    ('Route27', 36, 5): 'Tohjo Falls (TODO)',
    ('Route31', 34, 5): 'Dark Cave (TODO)',
    ('Route42', 10, 5): 'Mt. Mortar (TODO)',
    ('Route42', 28, 9): 'Mt. Mortar (TODO)',
    ('Route42', 46, 7): 'Mt. Mortar (TODO)',
    ('SilverCaveOutside', 18, 11): 'Silver Cave (TODO)',
}
EXTRA = ['DiglettsCave_JohtoTunnel', 'DiglettsCave_BlackthornEntrance',
         'IcePath_1F', 'IcePath_B1F', 'IcePath_B2F_MahoganySide', 'IcePath_B2F_BlackthornSide', 'IcePath_B3F']
layouts = {l['id']: l for l in json.load(open(os.path.join(REPO, 'data/layouts/layouts.json')))['layouts'] if 'id' in l}
all_maps = {}
for p in glob.glob(os.path.join(REPO, 'data/maps/*/map.json')):
    m = json.load(open(p)); all_maps[m['id']] = m

def attrs(ts, primary):
    return open(os.path.join(tileset_dir(ts, primary), 'metatile_attributes.bin'), 'rb').read()

def behaviour(pa, sa, npri, mt):
    b, i = (pa, mt) if mt < npri else (sa, mt - npri)
    return NAMES[struct.unpack_from('<I', b, i * 4)[0] & 0x1FF] if i * 4 < len(b) else '?'

def audit(name, dump=False, quiet=False):
    m = json.load(open(os.path.join(REPO, 'data/maps', name, 'map.json')))
    l = layouts[m['layout']]
    w, h = l['width'], l['height']
    v = struct.unpack('<%dH' % (w * h), open(os.path.join(REPO, l['blockdata_filepath']), 'rb').read())
    pa, sa = attrs(l['primary_tileset'], True), attrs(l['secondary_tileset'], False)
    npri = len(pa) // 4
    warps = m.get('warp_events') or []
    have = {(wp['x'], wp['y']) for wp in warps}
    print('== %s (%s, %dx%d, %d warps)' % (name, m['id'], w, h, len(warps)))
    errs = []
    for i, wp in enumerate(warps):
        dest = all_maps.get(wp['dest_map'])
        if wp['dest_map'] == 'MAP_DYNAMIC':
            st = 'dynamic'
        elif not dest:
            st = '!! dest map missing'
        else:
            dw = dest.get('warp_events') or []
            try:
                di = int(wp['dest_warp_id'])
            except ValueError:
                di = -1
            if not 0 <= di < len(dw):
                st = '!! dest_warp_id out of range'
            elif dw[di]['dest_map'] not in (m['id'], 'MAP_DYNAMIC'):
                st = '!! dest warp #%d points to %s, not back here' % (di, dw[di]['dest_map'])
            elif dw[di]['dest_map'] == m['id'] and not (0 <= int(dw[di]['dest_warp_id']) < len(warps)):
                st = '!! return warp id out of range'
            else:
                st = 'ok'
        if st.startswith('!!'):
            errs.append('warp %d (%d,%d): %s' % (i, wp['x'], wp['y'], st))
        if not quiet or st.startswith('!!'):
            print('  warp %d (%d,%d) -> %s #%s  %s' % (i, wp['x'], wp['y'], wp['dest_map'], wp['dest_warp_id'], st))
    todo = []
    for y in range(h):
        for x in range(w):
            b = behaviour(pa, sa, npri, v[y * w + x] & 0x3FF)
            if b in WARPY and (x, y) not in have:
                if (name, x, y) in TODO_ALLOW:
                    todo.append('(%d,%d) %s [%s]' % (x, y, b.replace('MB_', ''), TODO_ALLOW[(name, x, y)]))
                else:
                    errs.append('(%d,%d) %s has no warp' % (x, y, b.replace('MB_', '')))
    if todo and not quiet:
        print('  allowlisted TODO cells: ' + ', '.join(todo))
    for e in errs:
        print('  ERROR ' + e)
    if dump:
        for y in range(h):
            print('  %3d ' % y + ' '.join('%03x%s' % (c & 0x3FF, '#' if (c >> 10) & 3 else '.') for c in v[y * w:(y + 1) * w]))
    return errs, todo

if __name__ == '__main__':
    args = sys.argv[1:]
    dump = '--dump' in args
    quiet = '--quiet' in args
    names = [a for a in args if not a.startswith('--')]
    if not names:
        groups = json.load(open(os.path.join(REPO, 'data/maps/map_groups.json')))
        names = JOHTO + [n for n in EXTRA if os.path.exists(os.path.join(REPO, 'data/maps', n))] + \
            groups.get('gMapGroup_IndoorJohto', [])
    nerr = ntodo = 0
    for n in names:
        e, t = audit(n, dump, quiet)
        nerr += len(e); ntodo += len(t)
    print('warp audit: %d maps, %d errors, %d allowlisted TODO cells -> %s' % (
        len(names), nerr, ntodo, 'PASS' if nerr == 0 else 'FAIL'))
    sys.exit(1 if nerr else 0)
