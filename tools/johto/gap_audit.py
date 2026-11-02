#!/usr/bin/env python3
"""Gap audit for the Johto spike (read-only).
Scans every map that is new on the spike branch (Johto/custom maps) plus the FireRed maps the spike edits,
and lists every exit that leads nowhere:
  * OPEN EDGE   - passable cells on a map edge that no connection covers (the player walks into the border)
  * ONE-SIDED   - a connection whose target map is missing or has no mirrored connection back
  * NO WARP     - door / cave mouth / ladder / arrow-warp / hole cells with no warp_event
  * BAD WARP    - warp to a missing map or an out-of-range warp id
Then builds the map graph (connections + warps over ALL maps), prints the connected components the scoped
maps fall into, and whether each scoped map is reachable from Pallet Town.
Usage: gap_audit.py [--report FILE.md] [--strict]   (--strict: exit 1 if any gap not in ALLOW)"""
import json, os, struct, sys, glob, subprocess, collections
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', 'cherrygrove'))
from warp_audit import attrs, behaviour, WARPY, ONE_WAY, layouts
BASE = '12de80e9c09a7e89daf9ea8ff8d25a82c61c3c4d'   # merge-base of spike with upstream master
START = 'MAP_PALLET_TOWN'
# Deliberate / accepted gaps: (map dir, kind, detail-prefix): reason
ALLOW = {}
# Open edges are accepted automatically (listed under "Accepted") when
#   * BORDER  - a GSC map whose pokecrystal original has no connection on that side (the converter keeps the source
#               art, e.g. a path running into the tree line); out-of-bounds cells are always solid in-engine
#               (GetBorderBlockAt ORs MAPGRID_COLLISION_MASK), so the player just stops - cosmetic only
#   * VANILLA - a FireRed map whose edge was already open the same way at the merge base
# A GSC map that is open on a side where pokecrystal HAS a connection is reported as MISSING LINK.
GSC = json.load(open(os.path.join(HERE, 'gsc_connections.json')))['maps']

maps = {}
dirs = {}
for p in glob.glob(os.path.join(REPO, 'data/maps/*/map.json')):
    m = json.load(open(p)); maps[m['id']] = m; dirs[m['id']] = os.path.basename(os.path.dirname(p))

def scope():
    out = subprocess.run(['git', 'diff', '--name-only', BASE, '--', 'data/maps', 'data/layouts'], cwd=REPO,
                         capture_output=True, text=True).stdout.split()
    names = set()
    for f in out:
        parts = f.split('/')
        if len(parts) >= 4 and parts[1] == 'maps':
            names.add(parts[2])
        elif len(parts) >= 4 and parts[1] == 'layouts':
            for mid, m in maps.items():
                if layouts.get(m['layout'], {}).get('blockdata_filepath', '').split('/')[-2:-1] == [parts[2]]:
                    names.add(dirs[mid])
    return sorted(n for n in names if os.path.exists(os.path.join(REPO, 'data/maps', n, 'map.json')))

def grid(m):
    l = layouts[m['layout']]; w, h = l['width'], l['height']
    v = struct.unpack('<%dH' % (w * h), open(os.path.join(REPO, l['blockdata_filepath']), 'rb').read())
    return l, w, h, v

OPP = {'up': 'down', 'down': 'up', 'left': 'right', 'right': 'left'}

def audit_map(name):
    m = json.load(open(os.path.join(REPO, 'data/maps', name, 'map.json')))
    l, w, h, v = grid(m)
    pa, sa = attrs(l['primary_tileset'], True), attrs(l['secondary_tileset'], False); npri = len(pa) // 4
    gaps, auto = [], []
    conns = m.get('connections') or []
    for c in conns:
        t = maps.get(c['map'])
        if not t:
            gaps.append(('ONE-SIDED', '%s -> %s: target map missing' % (c['direction'], c['map']))); continue
        back = [b for b in (t.get('connections') or []) if b['map'] == m['id'] and b['direction'] == OPP[c['direction']]
                and int(b['offset']) == -int(c['offset'])]
        if not back:
            gaps.append(('ONE-SIDED', '%s -> %s offset %s has no mirrored connection' % (c['direction'], c['map'], c['offset'])))
    if m.get('map_type') not in ('MAP_TYPE_INDOOR', 'MAP_TYPE_SECRET_BASE'):
        sides = {'up': [(x, 0) for x in range(w)], 'down': [(x, h - 1) for x in range(w)],
                 'left': [(0, y) for y in range(h)], 'right': [(w - 1, y) for y in range(h)]}
        for side, cells in sides.items():
            covered = set()
            for c in conns:
                t = maps.get(c['map'])
                if c['direction'] != side or not t:
                    continue
                tl = layouts[t['layout']]; off = int(c['offset'])
                n = tl['width'] if side in ('up', 'down') else tl['height']
                covered |= set(range(off, off + n))
            run = []
            for i in range(len(cells) + 1):
                x, y = cells[i] if i < len(cells) else (0, 0)
                if i < len(cells) and (v[y * w + x] >> 10) & 3 == 0 and i not in covered:
                    run.append(i); continue
                if run and accept_edge(name, side, run, m):
                    auto.append(('OPEN EDGE', '%s edge %d-%d' % (side, run[0], run[-1]), accept_edge(name, side, run, m)))
                    run = []
                if run:
                    b = behaviour(pa, sa, npri, v[cells[run[0]][1] * w + cells[run[0]][0]] & 0x3FF).replace('MB_', '')
                    gaps.append(('OPEN EDGE', '%s edge %s %d-%d (%d cells, e.g. %s)' % (
                        side, 'x' if side in ('up', 'down') else 'y', run[0], run[-1], len(run), b)))
                    run = []
    have = {(wp['x'], wp['y']) for wp in (m.get('warp_events') or [])}
    for y in range(h):
        for x in range(w):
            b = behaviour(pa, sa, npri, v[y * w + x] & 0x3FF)
            if b in WARPY and (x, y) not in have:
                gaps.append(('NO WARP', '(%d,%d) %s' % (x, y, b.replace('MB_', ''))))
    for i, wp in enumerate(m.get('warp_events') or []):
        if wp['dest_map'] == 'MAP_DYNAMIC':
            continue
        d = maps.get(wp['dest_map'])
        if not d:
            gaps.append(('BAD WARP', 'warp %d (%d,%d) -> missing %s' % (i, wp['x'], wp['y'], wp['dest_map'])))
        elif not 0 <= int(wp['dest_warp_id']) < len(d.get('warp_events') or []):
            gaps.append(('BAD WARP', 'warp %d (%d,%d) -> %s #%s out of range' % (i, wp['x'], wp['y'], wp['dest_map'], wp['dest_warp_id'])))
    return [(k, d) for k, d in gaps if not any(name == a[0] and k == a[1] and d.startswith(a[2]) for a in ALLOW)], \
           [(k, d, ALLOW[a]) for k, d in gaps for a in ALLOW if name == a[0] and k == a[1] and d.startswith(a[2])] + auto

def open_cells(name, side, m, v, w, h, maps_by_id):
    """Passable edge indices on `side` not covered by a connection (for the given map.json/blockdata)."""
    cells = {'up': [(x, 0) for x in range(w)], 'down': [(x, h - 1) for x in range(w)],
             'left': [(0, y) for y in range(h)], 'right': [(w - 1, y) for y in range(h)]}[side]
    covered = set()
    for c in m.get('connections') or []:
        t = maps_by_id.get(c['map'])
        if c['direction'] == side and t:
            tl = layouts[t['layout']]; off = int(c['offset'])
            covered |= set(range(off, off + (tl['width'] if side in ('up', 'down') else tl['height'])))
    return {i for i, (x, y) in enumerate(cells) if (v[y * w + x] >> 10) & 3 == 0 and i not in covered}

_base_cache = {}
def base_open(name, side):
    """Open edge cells of a FireRed map at the merge base (None if it did not exist)."""
    if name not in _base_cache:
        git = lambda p: subprocess.run(['git', 'show', '%s:%s' % (BASE, p)], cwd=REPO, capture_output=True)
        r = git('data/maps/%s/map.json' % name)
        if r.returncode:
            _base_cache[name] = None
        else:
            m = json.loads(r.stdout); l = layouts[m['layout']]; w, h = l['width'], l['height']
            b = git(l['blockdata_filepath']).stdout
            v = struct.unpack('<%dH' % (w * h), b) if len(b) == 2 * w * h else None
            _base_cache[name] = (m, v, w, h)
    e = _base_cache[name]
    return None if not e or not e[1] else open_cells(name, side, e[0], e[1], e[2], e[3], maps)

def accept_edge(name, side, run, m):
    gname = name.replace('_', '')
    g = GSC.get(gname)
    if g is not None:
        want = [o for d, o in g if d == side]
        if not want:
            return 'BORDER: pokecrystal %s has no %s connection; out-of-bounds is solid in-engine (cosmetic)' % (gname, side)
        have = {dirs.get(c['map'], '').replace('_Frlg', '').replace('_', '') for c in m.get('connections') or []
                if c['direction'] == side}
        if all(o in have for o in want):
            return 'BORDER: outside the span of the %s neighbour(s) %s, which are connected (cosmetic)' % (side, '/'.join(want))
        return None
    if name.endswith('_Frlg'):
        b = base_open(name, side)
        if b is not None and set(run) <= b:
            return 'VANILLA: already open at the merge base (unchanged FireRed edge)'
    return None

def graph():
    adj = collections.defaultdict(set)
    for mid, m in maps.items():
        for c in m.get('connections') or []:
            if c['map'] in maps:
                adj[mid].add(c['map']); adj[c['map']].add(mid)
        for wp in m.get('warp_events') or []:
            if wp['dest_map'] in maps:
                adj[mid].add(wp['dest_map']); adj[wp['dest_map']].add(mid)
    return adj

def components(adj, ids):
    seen, comps = set(), []
    for s in ids:
        if s in seen:
            continue
        comp, q = set([s]), [s]
        while q:
            a = q.pop()
            for b in adj[a]:
                if b not in comp:
                    comp.add(b); q.append(b)
        seen |= comp; comps.append(comp)
    return comps

def main():
    args = sys.argv[1:]
    rep = args[args.index('--report') + 1] if '--report' in args else None
    names = scope()
    lines, total, allowed = [], 0, []
    for n in names:
        g, al = audit_map(n)
        allowed += [(n,) + a for a in al]
        if g:
            lines.append('### %s' % n)
            lines += ['- **%s** %s' % gd for gd in g]
            total += len(g)
    adj = graph()
    ids = [maps_id for maps_id in maps if dirs[maps_id] in names]
    comps = components(adj, ids)
    main_c = next((c for c in comps if START in c), None) or components(adj, [START])[0]
    out = ['# Gap audit', '', 'Scope: %d maps (new on spike + FireRed maps edited by the spike).' % len(names),
           'Gaps: %d (allow-listed: %d)' % (total, len(allowed)), '']
    out += ['## Connectivity', '']
    for c in sorted(comps, key=len, reverse=True):
        sc = sorted(dirs[i] for i in c if dirs[i] in names)
        tag = 'MAIN (contains Pallet Town)' if START in c else 'DISCONNECTED'
        out.append('- %s: %d maps total, %d scoped: %s' % (tag, len(c), len(sc), ', '.join(sc) if len(sc) < 40 else
                                                         ', '.join(sc[:40]) + ', ...'))
    out += ['', '## Gaps', ''] + (lines or ['(none)'])
    if allowed:
        out += ['', '## Accepted (allow-listed / auto-classified)', ''] + ['- %s **%s** %s - %s' % a for a in allowed]
    # outdoor dead ends: scoped outdoor maps with a single outdoor neighbour (connections + outdoor warps)
    outdoor = lambda i: maps[i].get('map_type') not in ('MAP_TYPE_INDOOR', 'MAP_TYPE_UNDERGROUND')
    dead = []
    for i in ids:
        if not outdoor(i):
            continue
        nb = {c['map'] for c in maps[i].get('connections') or [] if c['map'] in maps}
        if len(nb) <= 1:
            dead.append('%s (%s)' % (dirs[i], ', '.join(dirs[n] for n in nb) or 'warps only'))
    out += ['', '## Outdoor dead ends (<=1 connected outdoor neighbour)', ''] + ['- ' + d for d in sorted(dead)]
    have = set(dirs.values())
    missing = sorted(n for n, c in GSC.items() if c and n not in have and n + '_Frlg' not in have)
    out += ['', '## GSC outdoor maps not built (pokecrystal maps with connections)', '',
            ', '.join(missing) or '(none)']
    txt = '\n'.join(out) + '\n'
    print(txt)
    if rep:
        open(rep, 'w').write(txt)
    if '--strict' in args and total:
        sys.exit(1)

if __name__ == '__main__':
    main()
