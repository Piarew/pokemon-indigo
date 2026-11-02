#!/usr/bin/env python3
"""Register new spike maps with the build: layouts.json entry (frlg layout_version), map group membership
and the event_scripts.s include.  Idempotent.
usage: python3 tools/johto/register_maps.py GROUP MapDir:W:H:SECONDARY_TILESET [...]
  e.g. register_maps.py gMapGroup_TownsAndRoutes_Frlg Route36:60:18:gTileset_ViridianCity
  (layout id/name derive from the map dir; a map whose map.json reuses an existing layout may pass W=0)"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
from interiors import snake_upper

def register(group, name, w, h, secondary, primary='gTileset_General_Frlg'):
    lp = os.path.join(REPO, 'data/layouts/layouts.json')
    lj = json.load(open(lp))
    lid = 'LAYOUT_' + snake_upper(name)
    if w and not any(l.get('id') == lid for l in lj['layouts']):
        bp = 'data/layouts/%s/map.bin' % name
        assert os.path.getsize(os.path.join(REPO, bp)) == w * h * 2, (name, 'bin size')
        assert (w + 15) * (h + 14) <= 10240, (name, 'too big')
        lj['layouts'].append({'id': lid, 'name': name + '_Layout', 'width': w, 'height': h,
                              'border_width': 2, 'border_height': 2, 'primary_tileset': primary,
                              'secondary_tileset': secondary,
                              'border_filepath': 'data/layouts/%s/border.bin' % name,
                              'blockdata_filepath': bp, 'layout_version': 'frlg'})
        with open(lp, 'w') as f:
            f.write(json.dumps(lj, indent=2, ensure_ascii=False) + '\n')
    gp = os.path.join(REPO, 'data/maps/map_groups.json')
    gj = json.load(open(gp))
    if name not in gj[group]:
        gj[group].append(name)
        with open(gp, 'w') as f:
            f.write(json.dumps(gj, indent=2) + '\n')
    ep = os.path.join(REPO, 'data/event_scripts.s')
    es = open(ep).read()
    inc = '\t.include "data/maps/%s/scripts.inc"\n' % name
    if inc not in es:
        anchor = '\t.include "data/maps/SilverCaveOutside/scripts.inc"\n'
        # keep outdoor/cave maps together after the last plain (non-interior) Johto include
        idx = es.index(anchor) + len(anchor)
        while es.startswith('\t.include', idx) and '@ johto-interior' not in es[idx:es.index('\n', idx)]:
            idx = es.index('\n', idx) + 1
        es = es[:idx] + inc + es[idx:]
        open(ep, 'w').write(es)

if __name__ == '__main__':
    group = sys.argv[1]
    for spec in sys.argv[2:]:
        n, w, h, sec = spec.split(':')
        register(group, n, int(w), int(h), sec)
        print('registered', n)
