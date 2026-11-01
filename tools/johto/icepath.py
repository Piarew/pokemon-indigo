#!/usr/bin/env python3
"""Phase 5: Ice Path (GSC/Crystal) -> FRLG, 5 floors, 1:1 tile scale, gTileset_SeafoamIslands (Icefall Cave look).
Source images: Bulbagarden Ice_Path_{1F,B1F,B2F,B3F}_C.png in /workspace/johto_src (B2F image holds both
B2F maps side by side).  Pipeline per floor:
  GSC 16x16 cell -> semantic: I ice, F floor, W rock/wall, U ladder up, D ladder down, M exit mat
  (holes in B1F become floor; strength boulders are replaced by fixed rocks where they land on B2F;
   the B3F Rock Smash rock is dropped -> simple field-move policy)
  F/I cells not reachable from a warp -> W (image border fill); W cells not in any 2x2 W block -> R (lone rock)
  W -> 5x5-neighbourhood nearest match learned from FRLG Icefall Cave 1F/B1F.
Also writes map.json/scripts.inc, registers the maps (gMapGroup_IndoorJohto), wires Route 44 (56,7) and
Blackthorn (36,9), adds FR/LG wild encounters, and checks every warp is reachable with ice-sliding physics."""
import copy, hashlib, json, os, struct, sys
from collections import deque
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
SRC = '/workspace/johto_src'
sys.path.insert(0, HERE)
from register_maps import register

ELEV3 = 0x3000
FLOOR, ICE = 0x281 | ELEV3, 0x34B | ELEV3
LADDER_UP, LADDER_DOWN, MAT = 0x296 | ELEV3, 0x285 | ELEV3, 0x287 | ELEV3
ROCK_FLOOR, ROCK_ICE = 0x372 | 0x400, 0x33F | 0x400
FILL = 0x291 | 0x400

# (map, image, x0 px, w, h)
FLOORS = [('IcePath_1F', 'Ice_Path_1F_C.png', 0, 40, 36),
          ('IcePath_B1F', 'Ice_Path_B1F_C.png', 0, 20, 36),
          ('IcePath_B2F_MahoganySide', 'Ice_Path_B2F_C.png', 0, 20, 18),
          ('IcePath_B2F_BlackthornSide', 'Ice_Path_B2F_C.png', 340, 10, 18),
          ('IcePath_B3F', 'Ice_Path_B3F_C.png', 0, 20, 18)]
MID = lambda n: 'MAP_' + __import__('re').sub(r'(?<=[a-z])(?=[A-Z])', '_', n).upper()
# warps (pokecrystal coords, holes dropped); target = (map, index)
WARPS = {
    'IcePath_1F': [((4, 19), 'MAP_ROUTE44', None), ((36, 27), 'MAP_BLACKTHORN_CITY', None),
                   ((37, 5), 'IcePath_B1F', 0), ((37, 13), 'IcePath_B1F', 2)],
    'IcePath_B1F': [((3, 15), 'IcePath_1F', 2), ((17, 3), 'IcePath_B2F_MahoganySide', 0),
                    ((5, 25), 'IcePath_1F', 3), ((11, 27), 'IcePath_B2F_BlackthornSide', 0)],
    'IcePath_B2F_MahoganySide': [((17, 1), 'IcePath_B1F', 1), ((9, 11), 'IcePath_B3F', 0)],
    'IcePath_B2F_BlackthornSide': [((3, 15), 'IcePath_B1F', 3), ((3, 3), 'IcePath_B3F', 1)],
    'IcePath_B3F': [((3, 5), 'IcePath_B2F_MahoganySide', 1), ((15, 5), 'IcePath_B2F_BlackthornSide', 1)],
}
# GSC strength boulders dropped through the B1F holes land here: fixed rocks (simple field moves)
EXTRA_ROCKS = {'IcePath_B2F_MahoganySide': [(11, 3), (4, 7), (3, 12), (12, 13)]}
# GSC design: 1F and B1F are each split into two halves joined only through the lower floors
COMPONENTS = {'IcePath_1F': [{0, 2}, {1, 3}], 'IcePath_B1F': [{0, 1}, {2, 3}]}
OUTSIDE = {'IcePath_1F': {0: ('Route44', (56, 7)), 1: ('BlackthornCity', (36, 9))}}
# GSC cell ids are content hashes; the classes below are decided from pixel content (see classify)
def classify(c):
    px = list(c.get_flattened_data()) if hasattr(c, 'get_flattened_data') else list(c.getdata())
    dark = sum(1 for p in px if sum(p) < 200)
    cnt = {}
    for p in px: cnt[p] = cnt.get(p, 0) + 1
    if cnt.get((176, 232, 248), 0) > 80 and cnt.get((80, 216, 248), 0) > 80: return 'I'
    if cnt.get((240, 240, 88), 0) > 30: return 'M'
    if dark >= 120: return 'H' if dark >= 135 else 'D'   # 79 hole (140) / 37 ladder-down hole (122)
    if dark == 76 and cnt.get((200, 248, 248), 0) >= 90: return 'U'  # 85 ladder up
    if dark == 54 and cnt.get((200, 248, 248), 0) >= 100: return 'F'  # 35 stairs
    if dark == 15: return 'W'   # thin wall-edge fringe (17/56/72)
    if dark < 15: return 'F'
    return 'W'

def load_sem(img, x0, w, h):
    im = Image.open(os.path.join(SRC, img)).convert('RGB')
    return [[classify(im.crop((x0 + x * 16, y * 16, x0 + x * 16 + 16, y * 16 + 16))) for x in range(w)] for y in range(h)]

def grid_of(name):
    L = {l['blockdata_filepath'].split('/')[-2]: l for l in json.load(open(os.path.join(REPO, 'data/layouts/layouts.json')))['layouts']}
    l = L[name]; W, H = l['width'], l['height']
    d = open(os.path.join(REPO, l['blockdata_filepath']), 'rb').read()
    return W, H, [[struct.unpack_from('<H', d, (y * W + x) * 2)[0] for x in range(W)] for y in range(H)]

def mask(isf, x, y):
    return tuple(isf(x + dx, y + dy) for dy in range(-2, 3) for dx in range(-2, 3))
# Icefall's yellow ledge/step strips read as stray stairs next to GSC walls -> never learned
YELLOW = {0x2C9, 0x342, 0x355, 0x356, 0x35F}
WEIGHT = [1, 1, 1, 1, 1, 1, 4, 4, 4, 1, 1, 4, 0, 4, 1, 1, 4, 4, 4, 1, 1, 1, 1, 1, 1]
SAMPLES = {}
for ref in ('FourIsland_IcefallCave_1F_Frlg', 'FourIsland_IcefallCave_B1F_Frlg'):
    RW, RH, RG = grid_of(ref)
    # 'floor' = passable or a lone rock/ice-rock (so rocks don't count as cave wall)
    rf = lambda x, y: 0 <= x < RW and 0 <= y < RH and ((RG[y][x] >> 10) & 3 == 0 or RG[y][x] & 0x3FF in (0x372, 0x33F, 0x347, 0x348, 0x349, 0x34F, 0x30B))
    for y in range(RH):
        for x in range(RW):
            v = RG[y][x]
            if rf(x, y) or v & 0x3FF in YELLOW: continue
            SAMPLES.setdefault(mask(rf, x, y), {}).setdefault(v, 0)
            SAMPLES[mask(rf, x, y)][v] += 1

def pick(k):
    if k not in SAMPLES:
        k = min(SAMPLES, key=lambda s: sum(w for a, b, w in zip(s, k, WEIGHT) if a != b))
    return max(SAMPLES[k].items(), key=lambda kv: kv[1])[0]

def build(name, img, x0, W, H):
    sem = load_sem(img, x0, W, H)
    for (x, y) in EXTRA_ROCKS.get(name, []):
        assert sem[y][x] == 'I', (name, x, y, sem[y][x]); sem[y][x] = 'W'
    for y in range(H):
        for x in range(W):
            if sem[y][x] == 'H': sem[y][x] = 'F'
            if sem[y][x] == 'M': sem[y][x] = 'W'      # exit mats sit on the warp cell instead (FRLG style)
    warps = WARPS[name]
    for (x, y), _, _ in warps:
        assert sem[y][x] in 'UDF', (name, x, y, sem[y][x])
    # reachability (plain 4-neighbour over walkable) from every warp -> the rest is image fill
    seen = set(); q = deque(p for p, _, _ in warps); seen |= set(q)
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in seen and sem[ny][nx] in 'FIUD':
                seen.add((nx, ny)); q.append((nx, ny))
    for y in range(H):
        for x in range(W):
            if sem[y][x] in 'FIUD' and (x, y) not in seen: sem[y][x] = 'W'
    isW = lambda x, y: not (0 <= x < W and 0 <= y < H) or sem[y][x] == 'W'
    for y in range(H):
        for x in range(W):
            if sem[y][x] == 'W' and not any(all(isW(x + i + a, y + j + b) for a in (0, 1) for b in (0, 1))
                                            for i in (-1, 0) for j in (-1, 0)):
                sem[y][x] = 'R'
    isf = lambda x, y: 0 <= x < W and 0 <= y < H and sem[y][x] != 'W'
    g = [[0] * W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            c = sem[y][x]
            if c == 'W':
                g[y][x] = FILL if all(not isf(x + a, y + b) for a in range(-2, 3) for b in range(-2, 3)) else pick(mask(isf, x, y))
            elif c == 'F': g[y][x] = FLOOR
            elif c == 'I': g[y][x] = ICE
            elif c == 'U': g[y][x] = LADDER_UP
            elif c == 'D': g[y][x] = LADDER_DOWN
            elif c == 'R':
                n = [sem[y + b][x + a] for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)) if 0 <= x + a < W and 0 <= y + b < H]
                g[y][x] = ROCK_ICE if n.count('I') > len(n) / 2 else ROCK_FLOOR
    for i, ((x, y), dest, _) in enumerate(warps):
        if not dest.startswith('IcePath'):
            g[y][x] = MAT; sem[y][x] = 'F'
    return sem, g

def solve(name, sem, W, H):
    """BFS with FRLG ice physics: on ice you keep sliding until the next cell is blocked or you leave ice."""
    warps = [p for p, _, _ in WARPS[name]]
    walk = lambda x, y: 0 <= x < W and 0 <= y < H and sem[y][x] in 'FIUD'
    def step(x, y, dx, dy):
        nx, ny = x + dx, y + dy
        if not walk(nx, ny): return None
        while sem[ny][nx] == 'I' and walk(nx + dx, ny + dy):
            nx, ny = nx + dx, ny + dy
        return nx, ny
    reach = {}
    for s in warps:
        seen = {s}; q = deque([s])
        while q:
            x, y = q.popleft()
            for d in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = step(x, y, *d)
                if n and n not in seen: seen.add(n); q.append(n)
        reach[s] = [w for w in warps if w in seen or any(abs(w[0] - a) + abs(w[1] - b) == 1 and sem[w[1]][w[0]] != 'I' for a, b in seen)]
    return reach

def write(name, W, H, g, sem):
    od = os.path.join(REPO, 'data/layouts', name); os.makedirs(od, exist_ok=True)
    with open(os.path.join(od, 'map.bin'), 'wb') as f:
        for r in g:
            for v in r: f.write(struct.pack('<H', v))
    with open(os.path.join(od, 'border.bin'), 'wb') as f: f.write(struct.pack('<4H', *([FILL] * 4)))
    os.makedirs('/workspace/p5/icepath_sem', exist_ok=True)
    open(os.path.join('/workspace/p5/icepath_sem', name + '_semantic.txt'), 'w').write(
        '# %s %dx%d  I ice F floor W wall R rock U/D ladders\n' % (name, W, H) + '\n'.join(''.join(r) for r in sem) + '\n')

def main():
    out = {}
    for name, img, x0, W, H in FLOORS:
        assert (W + 15) * (H + 14) <= 10240
        sem, g = build(name, img, x0, W, H)
        write(name, W, H, g, sem)
        out[name] = (W, H, sem)
        r = solve(name, sem, W, H)
        pos = [p for p, _, _ in WARPS[name]]
        comps = COMPONENTS.get(name, [set(range(len(pos)))])
        for comp in comps:
            for i in comp:
                got = {pos.index(w) for w in r[pos[i]]}
                assert got == comp, (name, i, got, comp)
        print('%-28s %dx%d ice-physics reach-check OK %s' % (name, W, H, comps))
    # outside warp indices
    idx = {}
    for name, ow in OUTSIDE.items():
        for wi, (omap, (ox, oy)) in ow.items():
            p = os.path.join(REPO, 'data/maps', omap, 'map.json'); m = json.load(open(p))
            k = next((i for i, w in enumerate(m['warp_events']) if (w['x'], w['y']) == (ox, oy)), None)
            if k is None:
                m['warp_events'].append({"x": ox, "y": oy, "elevation": 0, "dest_map": MID(name), "dest_warp_id": str(wi)})
                k = len(m['warp_events']) - 1
            else:
                m['warp_events'][k].update(dest_map=MID(name), dest_warp_id=str(wi))
            open(p, 'w').write(json.dumps(m, indent=2) + '\n')
            idx[(name, wi)] = k
    for name, img, x0, W, H in FLOORS:
        d = os.path.join(REPO, 'data/maps', name); os.makedirs(d, exist_ok=True)
        we = []
        for i, ((x, y), dest, di) in enumerate(WARPS[name]):
            if dest.startswith('IcePath'):
                we.append({"x": x, "y": y, "elevation": 3, "dest_map": MID(dest), "dest_warp_id": str(di)})
            else:
                we.append({"x": x, "y": y, "elevation": 3, "dest_map": dest, "dest_warp_id": str(idx[(name, i)])})
        mj = {"id": MID(name), "name": name, "layout": 'LAYOUT_' + MID(name)[4:], "music": "MUS_RG_SEVII_CAVE",
              "region": "REGION_KANTO", "region_map_section": "MAPSEC_SEAFOAM_ISLANDS", "requires_flash": False,
              "weather": "WEATHER_NONE", "map_type": "MAP_TYPE_UNDERGROUND", "allow_cycling": True,
              "allow_escaping": True, "allow_running": True, "show_map_name": False, "floor_number": 0,
              "battle_scene": "MAP_BATTLE_SCENE_NORMAL", "connections": None, "object_events": [],
              "warp_events": we, "coord_events": [], "bg_events": []}
        open(os.path.join(d, 'map.json'), 'w').write(json.dumps(mj, indent=2) + '\n')
        open(os.path.join(d, 'scripts.inc'), 'w').write('%s_MapScripts::\n\t.byte 0\n' % name)
        register('gMapGroup_IndoorJohto', name, W, H, 'gTileset_SeafoamIslands')
    # wild encounters (GSC Ice Path species; FR Delibird / LG Sneasel like Icefall Cave)
    p = os.path.join(REPO, 'src/data/wild_encounters.json'); wj = json.load(open(p))
    slots = [('SWINUB', 22), ('ZUBAT', 22), ('SWINUB', 23), ('GOLBAT', 24), ('ZUBAT', 23), ('SWINUB', 21),
             ('X', 23), ('JYNX', 22), ('GOLBAT', 25), ('SWINUB', 24), ('GOLBAT', 26), ('X', 24)]
    for grp in wj['wild_encounter_groups']:
        enc = grp.get('encounters', [])
        if not any(e.get('base_label', '').startswith('sFourIslandIcefallCave1F_') for e in enc): continue
        if any(e.get('map', '').startswith('MAP_ICE_PATH') for e in enc): break
        for name, *_ in FLOORS:
            for ver, x in (('FireRed', 'DELIBIRD'), ('LeafGreen', 'SNEASEL')):
                lab = 's' + name.replace('_', '') + '_' + ver
                enc.append({"map": MID(name), "base_label": lab, "land_mons": {"encounter_rate": 7, "mons": [
                    {"min_level": l, "max_level": l, "species": 'SPECIES_' + (x if s == 'X' else s)} for s, l in slots]}})
        open(p, 'w').write(json.dumps(wj, indent=2, ensure_ascii=False) + '\n')
        break

if __name__ == '__main__':
    main()
