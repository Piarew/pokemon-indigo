#!/usr/bin/env python3
"""Seafoam Islands ice wall (FireRed edit, flagged): the caves can no longer be used to leave east.

The only Route 20 exits of the Seafoam caves are on 1F: west (6,21) and east (32,21).  The east exit sits in a
3-wide corridor x31-33 y20-21 between the ice-boulder columns at x30 and x34.  Two rows of the same ice-boulder
metatiles the cave already uses (0x29F top / 0x2A7 bottom, collision 1, copied from (30,20)/(30,21)) are frozen
across that corridor at y19-20, leaving the east warp tile (32,21) and its landing cell intact: someone arriving from
the east stands in a one-tile alcove facing the ice and walks back out; nobody inside can reach the east exit.
The ladder at (28,19) (east chamber <-> B1F) is untouched.  Sign bg_events on both wall rows (read from either side)
explains it.  B1F-B4F need no edit: they have no Route 20 exits (verified by the reachability test below).

Idempotent: always rebuilt from the upstream (BASE) 1F files.  Test: BFS over 1F..B4F (collision + all warps, boulders
and currents ignored = over-approximation) from the west entrance must reach every floor but not the east exit;
the same BFS on the unedited files must reach it (proves the test can see the route)."""
import json, os, struct, subprocess, collections

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
BASE = '12de80e9c09a7e89daf9ea8ff8d25a82c61c3c4d'
MAP = 'SeafoamIslands_1F_Frlg'
FLOORS = ['1F', 'B1F', 'B2F', 'B3F', 'B4F']
TOP, BOT = (30, 20), (30, 21)                      # ice boulder top / bottom halves to copy
WALL = [(x, 19, 'T') for x in (31, 32, 33)] + [(x, 20, 'B') for x in (31, 32, 33)]
SIGNS = [(32, 19), (32, 20)]                       # read from inside (y18) and from the east alcove (y21)
WEST, EAST = (6, 21), (32, 21)

SCRIPT = """
@ ---- Seafoam ice wall (indigo custom; see tools/johto/seafoam_block.py) ----
SeafoamIslands_1F_EventScript_IceWallSign::
	msgbox SeafoamIslands_1F_Text_IceWall, MSGBOX_SIGN
	end

SeafoamIslands_1F_Text_IceWall:
	.string "A thick wall of ice seals the\\n"
	.string "eastern passage. It won't budge.$"
"""

def git_show(path):
    return subprocess.check_output(['git', 'show', '%s:%s' % (BASE, path)], cwd=REPO)

def layouts():
    return {l['id']: l for l in json.load(open(os.path.join(REPO, 'data/layouts/layouts.json')))['layouts'] if 'id' in l}

def load(floor, override=None):
    name = 'SeafoamIslands_%s_Frlg' % floor
    m = json.load(open(os.path.join(REPO, 'data/maps', name, 'map.json')))
    l = layouts()[m['layout']]
    raw = override if override is not None else open(os.path.join(REPO, l['blockdata_filepath']), 'rb').read()
    return m, l['width'], l['height'], struct.unpack('<%dH' % (l['width'] * l['height']), raw)

def reach(bin1f=None):
    fl = {f: load(f, bin1f if f == '1F' else None) for f in FLOORS}
    ids = {fl[f][0]['id']: f for f in FLOORS}
    start = ('1F', WEST)
    seen, q, east = {start}, collections.deque([start]), False
    while q:
        f, (x, y) = q.popleft()
        m, w, h, v = fl[f]
        for wp in m['warp_events']:
            if (wp['x'], wp['y']) == (x, y):
                if wp['dest_map'] in ids:
                    d = ids[wp['dest_map']]; t = fl[d][0]['warp_events'][int(wp['dest_warp_id'])]
                    n = (d, (t['x'], t['y']))
                    if n not in seen:
                        seen.add(n); q.append(n)
                elif (f, (x, y)) == ('1F', EAST):
                    east = True
        warps = {(wp['x'], wp['y']) for wp in m['warp_events']}
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            a, b = x + dx, y + dy
            if 0 <= a < w and 0 <= b < h and ((v[b * w + a] >> 10) & 3 == 0 or (a, b) in warps):
                n = (f, (a, b))
                if n not in seen:
                    seen.add(n); q.append(n)
    return east, sorted({f for f, _ in seen})

def main():
    l = layouts()['LAYOUT_SEAFOAM_ISLANDS_1F']; W = l['width']; BIN = l['blockdata_filepath']
    raw = git_show(BIN)
    v = list(struct.unpack('<%dH' % (len(raw) // 2), raw))
    src = {'T': v[TOP[1] * W + TOP[0]], 'B': v[BOT[1] * W + BOT[0]]}
    assert (src['T'] & 0x3FF, src['B'] & 0x3FF) == (0x29F, 0x2A7) and all((s >> 10) & 3 for s in src.values())
    for x, y, k in WALL:
        assert (v[y * W + x] >> 10) & 3 == 0, (x, y)              # only freezing open floor
        v[y * W + x] = src[k]
    out = struct.pack('<%dH' % len(v), *v)
    assert len(out) == len(raw)

    east0, _ = reach(raw)
    east1, floors = reach(out)
    assert east0, 'test sanity: unedited Seafoam should connect west -> east'
    assert not east1, 'ice wall leaks: east exit still reachable from the west entrance'
    assert floors == sorted(FLOORS), floors
    open(os.path.join(REPO, BIN), 'wb').write(out)

    j = json.loads(git_show('data/maps/%s/map.json' % MAP))
    j['bg_events'] = list(j.get('bg_events') or []) + [
        {'type': 'sign', 'x': x, 'y': y, 'elevation': 0, 'player_facing_dir': 'BG_EVENT_PLAYER_FACING_ANY',
         'script': 'SeafoamIslands_1F_EventScript_IceWallSign'} for x, y in SIGNS]
    open(os.path.join(REPO, 'data/maps', MAP, 'map.json'), 'w').write(json.dumps(j, indent=2) + '\n')
    sc = git_show('data/maps/%s/scripts.inc' % MAP).decode()
    assert 'IceWall' not in sc
    open(os.path.join(REPO, 'data/maps', MAP, 'scripts.inc'), 'w').write(sc.rstrip('\n') + '\n' + SCRIPT)
    print('seafoam_block: 1F ice wall %d cells at x31-33 y19-20; reach test: unedited west->east %s, edited %s; '
          'floors reached %s -> PASS' % (len(WALL), east0, east1, '/'.join(floors)))

if __name__ == '__main__':
    main()
