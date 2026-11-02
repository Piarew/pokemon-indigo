#!/usr/bin/env python3
"""Tile-level reachability over the whole world (read-only helper, used by west_blocks.py and gap_audit.py).

BFS over (map, x, y) across ALL maps in data/maps:
  * a cell is enterable when its map.bin collision bits are 0, or it holds a warp_event;
  * stepping on a warp_event moves to the destination warp's cell (MAP_DYNAMIC warps are skipped: they only return
    the player to where they came from);
  * walking off an edge follows the map connection covering that cell (up/down/left/right) if the target cell is
    enterable.
Deliberately an OVER-approximation of what the player can do: elevation, ledge direction, surf/waterfall/cut/strength
requirements, object events (NPCs, cut trees, boulders, smash rocks), coord-event gates and arrow-warp facing are all
ignored.  So a map this BFS cannot reach is unreachable in-game by walking/surfing; only scripted warps and Fly could
add edges, and west_blocks.py checks those separately.
Usage: tilereach.py [MapDir ...]   (prints which of the given maps are reachable from Pallet Town)"""
import json, os, struct, glob, collections, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
PALLET = ('MAP_PALLET_TOWN', 6, 8)          # in front of the player's house door

def load_world():
    lay = {l['id']: l for l in json.load(open(os.path.join(REPO, 'data/layouts/layouts.json')))['layouts'] if 'id' in l}
    world, dirs = {}, {}
    for p in glob.glob(os.path.join(REPO, 'data/maps/*/map.json')):
        m = json.load(open(p))
        l = lay.get(m.get('layout'))
        if not l:
            continue
        w, h = l['width'], l['height']
        try:
            raw = open(os.path.join(REPO, l['blockdata_filepath']), 'rb').read()
        except OSError:
            continue
        if len(raw) != 2 * w * h:
            continue
        world[m['id']] = {'m': m, 'w': w, 'h': h, 'bin': l['blockdata_filepath'], 'raw': raw}
        dirs[m['id']] = os.path.basename(os.path.dirname(p))
    return world, dirs

def reach(world, starts, overrides=None, extra_edges=()):
    """starts: [(map_id, x, y)].  overrides: {blockdata_filepath: bytes} replacing map.bin contents.
    extra_edges: [((map,x,y),(map,x,y))] additional one-way moves (e.g. scripted warps).  Returns {map_id: set(cells)}."""
    overrides = overrides or {}
    grids = {}
    for mid, e in world.items():
        raw = overrides.get(e['bin'], e['raw'])
        v = struct.unpack('<%dH' % (e['w'] * e['h']), raw)
        warps = {}
        for wp in e['m'].get('warp_events') or []:
            warps[(wp['x'], wp['y'])] = (wp['dest_map'], int(wp['dest_warp_id']) if str(wp['dest_warp_id']).lstrip('-').isdigit() else -1)
        grids[mid] = (e['w'], e['h'], v, warps, e['m'].get('connections') or [])
    extra = collections.defaultdict(list)
    for a, b in extra_edges:
        extra[a].append(b)

    def ok(mid, x, y):
        w, h, v, warps, _ = grids[mid]
        return 0 <= x < w and 0 <= y < h and ((v[y * w + x] >> 10) & 3 == 0 or (x, y) in warps)

    seen = collections.defaultdict(set)
    q = collections.deque()
    for s in starts:
        seen[s[0]].add((s[1], s[2])); q.append(s)
    while q:
        mid, x, y = q.popleft()
        w, h, v, warps, conns = grids[mid]
        nxt = list(extra.get((mid, x, y), ()))
        if (x, y) in warps:
            dm, di = warps[(x, y)]
            if dm in grids and di >= 0:
                dw = grids[dm][3]
                ev = world[dm]['m'].get('warp_events') or []
                if di < len(ev):
                    nxt.append((dm, ev[di]['x'], ev[di]['y']))
        for dx, dy, side in ((1, 0, 'right'), (-1, 0, 'left'), (0, 1, 'down'), (0, -1, 'up')):
            a, b = x + dx, y + dy
            if 0 <= a < w and 0 <= b < h:
                if ok(mid, a, b):
                    nxt.append((mid, a, b))
                continue
            for c in conns:
                if c['direction'] != side or c['map'] not in grids:
                    continue
                tw, th = grids[c['map']][0], grids[c['map']][1]
                off = int(c['offset'])
                if side in ('left', 'right'):
                    ta, tb = (tw - 1 if side == 'left' else 0), y - off
                else:
                    ta, tb = x - off, (th - 1 if side == 'up' else 0)
                if ok(c['map'], ta, tb):
                    nxt.append((c['map'], ta, tb))
        for n in nxt:
            if (n[1], n[2]) not in seen[n[0]]:
                seen[n[0]].add((n[1], n[2])); q.append(n)
    return dict(seen)

if __name__ == '__main__':
    world, dirs = load_world()
    r = reach(world, [PALLET])
    ids = {d: i for i, d in dirs.items()}
    for n in sys.argv[1:]:
        print(n, 'REACHABLE' if ids.get(n) in r else 'unreachable')
    print('%d/%d maps reachable from Pallet Town' % (len(r), len(world)))
