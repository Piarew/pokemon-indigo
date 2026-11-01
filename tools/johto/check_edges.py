#!/usr/bin/env python3
"""Sanity-check map connections: reciprocal entries with mirrored offsets, and which edge cells are
passable (collision 0) on one side but blocked on the other."""
import json, os, struct, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
OPP = {'up': 'down', 'down': 'up', 'left': 'right', 'right': 'left'}
MAPS = sys.argv[1:] or ['CherrygroveCity', 'BlackthornCity', 'MahoganyTown', 'VioletCity',
                        'Route29', 'Route30', 'Route31', 'Route42', 'Route43', 'Route44']
layouts = {l['id']: l for l in json.load(open(os.path.join(REPO, 'data/layouts/layouts.json')))['layouts'] if 'id' in l}
mj = {n: json.load(open(os.path.join(REPO, 'data/maps', n, 'map.json'))) for n in MAPS}
by_id = {m['id']: n for n, m in mj.items()}

def grid(n):
    l = layouts[mj[n]['layout']]
    w, h = l['width'], l['height']
    d = open(os.path.join(REPO, l['blockdata_filepath']), 'rb').read()
    assert len(d) == w * h * 2, (n, len(d), w, h)
    v = struct.unpack('<%dH' % (w * h), d)
    return w, h, [[v[y * w + x] for x in range(w)] for y in range(h)]

ok = True
for n in MAPS:
    w, h, g = grid(n)
    for c in mj[n]['connections'] or []:
        m = by_id.get(c['map'])
        if not m:
            print('%-16s %-5s -> %s (not checked)' % (n, c['direction'], c['map'])); continue
        back = [b for b in mj[m]['connections'] or [] if b['map'] == mj[n]['id'] and b['direction'] == OPP[c['direction']]]
        if not back or back[0]['offset'] != -c['offset']:
            print('!! %s -> %s has no mirrored connection' % (n, m)); ok = False
        mw, mh, mg = grid(m)
        o, d = c['offset'], c['direction']
        pairs = []   # (coord along edge, my cell, their cell)
        if d in ('up', 'down'):
            for x in range(w):
                if 0 <= x - o < mw:
                    pairs.append((x, g[0 if d == 'up' else h - 1][x], mg[mh - 1 if d == 'up' else 0][x - o]))
        else:
            for y in range(h):
                if 0 <= y - o < mh:
                    pairs.append((y, g[y][0 if d == 'left' else w - 1], mg[y - o][mw - 1 if d == 'left' else 0]))
        walk = lambda v: (v >> 10) & 3 == 0
        mine = [p[0] for p in pairs if walk(p[1])]
        bad = [p[0] for p in pairs if walk(p[1]) != walk(p[2])]
        print('%-16s %-5s -> %-16s overlap %2d cells, passable here %s, mismatched %s'
              % (n, d, m, len(pairs), mine, bad or 'none'))
sys.exit(0 if ok else 1)
