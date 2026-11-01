#!/usr/bin/env python3
"""Phase 6: collision-driven GSC cave -> FRLG converter (Silver Cave, Tohjo Falls, Dark Cave, Mt. Mortar,
Dragon's Den, Union Cave, ...).  Source = pokecrystal block data (tools/johto/pkc.py), so every 16px cell has
an exact GSC collision value; no image classification needed.  1:1 tile scale, coordinates = pokecrystal.

Per cell: FLOOR/UP_WALL/side walls/ledges(HOP_*) -> F floor, WALL/HEADBUTT_TREE -> W, WATER/WATERFALL/
WHIRLPOOL/BUOY -> A water, warp cells -> M south mat (WARP_CARPET_DOWN), O door in the wall (CAVE/DOOR),
U ladder up / D ladder down (LADDER/STAIRCASE, by the LEVEL of the two maps).  Simple field-move policy:
ledges become plain floor, waterfalls plain water, pits are dropped.
Floor/water not reachable from a warp (walking + surfing) -> W (GSC void fill); W not in any 2x2 W block ->
R lone rock.  W/F/A are then tiled by a 5x5 nearest-weighted class-mask match learned from FRLG reference
cave layouts with the same secondary tileset (floor forced to elevation 3, water elevation 1, wall coll 1).
Outside cave mouths are found (or appended) by coordinate on the Johto outdoor map, so this runs after
interiors.py.  usage: python3 tools/johto/gsc_cave.py [GROUP ...]   (default: all groups)"""
import json, os, re, struct, sys
from collections import Counter, deque
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', 'cherrygrove'))
import pkc
from register_maps import register
from tsdir import tileset_dir

def snake_upper(n): return re.sub(r'(?<=[a-z])(?=[A-Z])', '_', n).upper()
MID = lambda n: 'MAP_' + snake_upper(n)
NAMES = re.findall(r'^\s*(MB_\w+)', open(os.path.join(REPO, 'include/constants/metatile_behaviors.h')).read(), re.M)
CONST2NAME = {c: n for n, c in re.findall(r'map_attributes (\w+), (\w+),', pkc._attr)}

# group -> config.  maps: pokecrystal map names (= our map dirs).  level: relative floor height (ladder up/down).
# outside: our outdoor map dirs whose cave mouths get wired.  enc: (land slots 12, water slots 5 or None) per map.
L_SILVER = [('GOLBAT', 45), ('GRAVELER', 44), ('ONIX', 45), ('GOLBAT', 46), ('MACHOKE', 44), ('URSARING', 46),
            ('GRAVELER', 46), ('DONPHAN', 45), ('MACHOKE', 47), ('URSARING', 48), ('GOLBAT', 48), ('MISDREAVUS', 47)]
W_SILVER = [('GOLDUCK', 40), ('GOLDUCK', 42), ('SEAKING', 41), ('GOLDUCK', 44), ('SEAKING', 43)]
L_TOHJO = [('ZUBAT', 21), ('RATICATE', 22), ('ZUBAT', 23), ('GOLBAT', 22), ('SLOWPOKE', 22), ('RATICATE', 24),
           ('GOLBAT', 24), ('SLOWPOKE', 24), ('ZUBAT', 22), ('GOLBAT', 25), ('RATICATE', 23), ('SLOWPOKE', 23)]
W_TOHJO = [('GOLDEEN', 20), ('SLOWPOKE', 22), ('GOLDEEN', 22), ('SEAKING', 24), ('SLOWBRO', 26)]
L_DARKV = [('GEODUDE', 3), ('ZUBAT', 3), ('GEODUDE', 2), ('ZUBAT', 2), ('TEDDIURSA', 3), ('DUNSPARCE', 2),
           ('GEODUDE', 4), ('ZUBAT', 4), ('DUNSPARCE', 4), ('TEDDIURSA', 4), ('DUNSPARCE', 3), ('GEODUDE', 3)]
L_DARKB = [('GOLBAT', 23), ('GRAVELER', 23), ('WOBBUFFET', 21), ('URSARING', 25), ('GEODUDE', 21), ('ZUBAT', 21),
           ('GOLBAT', 25), ('GRAVELER', 25), ('WOBBUFFET', 23), ('URSARING', 23), ('DUNSPARCE', 23), ('GOLBAT', 27)]
W_DARK = [('MAGIKARP', 15), ('GOLDEEN', 15), ('MAGIKARP', 20), ('GOLDEEN', 20), ('GYARADOS', 20)]
L_MORTAR = [('ZUBAT', 14), ('GEODUDE', 14), ('RATTATA', 14), ('MACHOP', 14), ('GOLBAT', 16), ('MARILL', 15),
            ('ZUBAT', 16), ('GEODUDE', 16), ('RATICATE', 16), ('MACHOP', 16), ('GRAVELER', 17), ('GOLBAT', 18)]
W_MORTAR = [('GOLDEEN', 15), ('MARILL', 15), ('GOLDEEN', 18), ('MARILL', 20), ('SEAKING', 20)]
GROUPS = {
    'silver': dict(maps=['SilverCaveRoom1', 'SilverCaveRoom2', 'SilverCaveRoom3', 'SilverCaveItemRooms'],
                   secondary='gTileset_CeruleanCave',
                   refs=['CeruleanCave_1F_Frlg', 'CeruleanCave_2F_Frlg', 'CeruleanCave_B1F_Frlg'],
                   music='MUS_RG_ROCKET_HIDEOUT', mapsec='MAPSEC_CERULEAN_CAVE', flash=False,
                   level={}, outside=['SilverCaveOutside'], comps={'SilverCaveItemRooms': [{0}, {1}]},
                   enc={n: (L_SILVER, W_SILVER) for n in ['SilverCaveRoom1', 'SilverCaveRoom2', 'SilverCaveRoom3', 'SilverCaveItemRooms']}),
    'tohjo': dict(maps=['TohjoFalls'], secondary='gTileset_CeruleanCave',
                  refs=['CeruleanCave_1F_Frlg', 'CeruleanCave_2F_Frlg', 'CeruleanCave_B1F_Frlg'],
                  music='MUS_RG_MT_MOON', mapsec='MAPSEC_SEAFOAM_ISLANDS', flash=False,
                  level={}, outside=['Route27'], enc={'TohjoFalls': (L_TOHJO, W_TOHJO)}),
    'dark': dict(maps=['DarkCaveVioletEntrance', 'DarkCaveBlackthornEntrance'], secondary='gTileset_CeruleanCave',
                 refs=['CeruleanCave_1F_Frlg', 'CeruleanCave_2F_Frlg', 'CeruleanCave_B1F_Frlg'],
                 music='MUS_RG_MT_MOON', mapsec='MAPSEC_SEAFOAM_ISLANDS', flash=True,
                 level={}, outside=['Route31', 'Route45', 'Route46'],
                 enc={'DarkCaveVioletEntrance': (L_DARKV, W_DARK), 'DarkCaveBlackthornEntrance': (L_DARKB, W_DARK)}),
    'mortar': dict(maps=['MountMortar1FOutside', 'MountMortar1FInside', 'MountMortar2FInside', 'MountMortarB1F'],
                   secondary='gTileset_CeruleanCave',
                   refs=['CeruleanCave_1F_Frlg', 'CeruleanCave_2F_Frlg', 'CeruleanCave_B1F_Frlg'],
                   music='MUS_RG_MT_MOON', mapsec='MAPSEC_SEAFOAM_ISLANDS', flash=False,
                   level={'MountMortar1FOutside': 1, 'MountMortar1FInside': 1, 'MountMortar2FInside': 2, 'MountMortarB1F': 0,
                          'up': {('MountMortar1FInside', 5, 39), ('MountMortar1FInside', 33, 41)}},
                   outside=['Route42'],
                   enc={n: (L_MORTAR, W_MORTAR) for n in ['MountMortar1FOutside', 'MountMortar1FInside', 'MountMortar2FInside', 'MountMortarB1F']}),
}
WATER_B = {'MB_OCEAN_WATER', 'MB_POND_WATER', 'MB_DEEP_WATER', 'MB_SEMI_DEEP_WATER', 'MB_WATERFALL', 'MB_FAST_WATER',
           'MB_SOUTHWARD_CURRENT', 'MB_NORTHWARD_CURRENT', 'MB_EASTWARD_CURRENT', 'MB_WESTWARD_CURRENT', 'MB_INTERIOR_DEEP_WATER'}
SKIP_B = {'MB_LADDER', 'MB_ROCK_STAIRS', 'MB_SOUTH_ARROW_WARP', 'MB_NORTH_ARROW_WARP', 'MB_EAST_ARROW_WARP',
          'MB_WEST_ARROW_WARP', 'MB_NON_ANIMATED_DOOR', 'MB_MT_PYRE_HOLE', 'MB_SIGNPOST', 'MB_FALL_WARP', 'MB_CAVE_DOOR'}
FLOOR_C = {'FLOOR', 'UP_WALL', 'RIGHT_WALL', 'LEFT_WALL', 'DOWN_WALL', 'TALL_GRASS', 'LONG_GRASS', 'ICE',
           'HOP_DOWN', 'HOP_LEFT', 'HOP_RIGHT', 'HOP_DOWN_LEFT', 'HOP_DOWN_RIGHT', 'PIT', 'COUNTER'}
WATER_C = {'WATER', 'WATERFALL', 'WHIRLPOOL', 'BUOY'}
WARP_C = {'WARP_CARPET_DOWN', 'WARP_CARPET_UP', 'WARP_CARPET_LEFT', 'WARP_CARPET_RIGHT', 'CAVE', 'DOOR', 'LADDER', 'STAIRCASE'}
FLOOR, MAT, LADDER_DOWN, LADDER_UP, DOOR = 0x281, 0x287, 0x285, 0x296, 0x294
E3, E1, C1 = 0x3000, 0x1000, 0x0400
WEIGHT = [1, 1, 1, 1, 1, 1, 4, 4, 4, 1, 1, 4, 0, 4, 1, 1, 4, 4, 4, 1, 1, 1, 1, 1, 1]

LAYOUTS = {l['blockdata_filepath'].split('/')[-2]: l for l in json.load(open(os.path.join(REPO, 'data/layouts/layouts.json')))['layouts'] if 'id' in l}

def grid_of(name):
    l = LAYOUTS[name]; W, H = l['width'], l['height']
    d = open(os.path.join(REPO, l['blockdata_filepath']), 'rb').read()
    return W, H, [[struct.unpack_from('<H', d, (y * W + x) * 2)[0] for x in range(W)] for y in range(H)]

def behaviours(secondary, primary='gTileset_General_Frlg'):
    pa = open(os.path.join(tileset_dir(primary, True), 'metatile_attributes.bin'), 'rb').read()
    sa = open(os.path.join(tileset_dir(secondary), 'metatile_attributes.bin'), 'rb').read()
    def b(mt):
        buf, i = (pa, mt) if mt < 0x280 else (sa, mt - 0x280)
        return NAMES[struct.unpack_from('<I', buf, i * 4)[0] & 0x1FF] if i * 4 < len(buf) else '?'
    return b

def mask(cls, x, y):
    return tuple(cls(x + dx, y + dy) for dy in range(-2, 3) for dx in range(-2, 3))

class Learner:
    def __init__(self, secondary, refs):
        self.beh = behaviours(secondary)
        self.samples = {'w': {}, 'f': {}, 'a': {}}
        rocks, tops = Counter(), {LADDER_UP: Counter(), DOOR: Counter()}
        for ref in refs:
            RW, RH, RG = grid_of(ref)
            def raw(x, y):
                if not (0 <= x < RW and 0 <= y < RH): return 'w'
                v = RG[y][x]; b = self.beh(v & 0x3FF)
                if b in WATER_B: return 'a'
                return 'f' if (v >> 10) & 3 == 0 else 'w'
            isw = lambda x, y: raw(x, y) == 'w'
            lone = lambda x, y: isw(x, y) and not any(all(isw(x + i + a, y + j + b) for a in (0, 1) for b in (0, 1))
                                                     for i in (-1, 0) for j in (-1, 0))
            cls = lambda x, y: 'f' if lone(x, y) else raw(x, y)
            for y in range(RH):
                for x in range(RW):
                    v = RG[y][x]; mt = v & 0x3FF
                    if mt in tops and y > 0: tops[mt][RG[y - 1][x]] += 1
                    if lone(x, y):
                        rocks[mt] += 1; continue
                    if self.beh(mt) in SKIP_B: continue
                    c = cls(x, y)
                    self.samples[c].setdefault(mask(cls, x, y), Counter())[mt] += 1
        # never learn the ladder/door top pieces (they read as stray ladders inside plain walls)
        topset = {v & 0x3FF for c in tops.values() for v in c}
        for cc in self.samples.values():
            for k in list(cc):
                for mt in topset: cc[k].pop(mt, None)
                if not cc[k]: del cc[k]
        self.rock = rocks.most_common(1)[0][0]
        self.tops = {k: (c.most_common(1)[0][0] if c else None) for k, c in tops.items()}
        self.fill = max(((m, c) for k, cc in self.samples['w'].items() if set(k) == {'w'} for m, c in cc.items()),
                        key=lambda mc: mc[1])[0]

    def pick(self, c, k):
        s = self.samples[c]
        if k not in s:
            k = min(s, key=lambda t: sum(w for a, b, w in zip(t, k, WEIGHT) if a != b))
        return s[k].most_common(1)[0][0]

def edge_wall(coll, x, y, dx, dy):
    """GSC directional walls: UP_WALL has a wall on its north edge (no crossing it either way), etc."""
    a, b = coll[y][x], coll[y + dy][x + dx]
    return ((dy == -1 and (a == 'UP_WALL' or b == 'DOWN_WALL')) or (dy == 1 and (b == 'UP_WALL' or a == 'DOWN_WALL')) or
            (dx == 1 and (a == 'RIGHT_WALL' or b == 'LEFT_WALL')) or (dx == -1 and (a == 'LEFT_WALL' or b == 'RIGHT_WALL')))

def warp_kind(m, x, y, dest_name, level):
    c = m.coll[y][x]
    if c in ('LADDER', 'STAIRCASE'):
        lv, dl = level.get(m.name, 0), level.get(dest_name, 0)
        if dl == lv: dl = lv + (1 if (m.name, x, y) in level.get('up', ()) else -1)
        return 'U' if dl > lv else 'D'
    if c in ('CAVE', 'DOOR'): return 'O'
    return 'M'

def build(cfg, name, L):
    m = pkc.load(name)
    W, H = m.w, m.h
    assert (W + 15) * (H + 14) <= 10240, name
    sem = [['F' if m.coll[y][x] in FLOOR_C else 'A' if m.coll[y][x] in WATER_C else 'W' for x in range(W)] for y in range(H)]
    for y in range(H):
        for x in range(W):
            if m.coll[y][x] in WARP_C: sem[y][x] = 'F'      # carpets/ladders without a warp: plain floor
            if m.coll[y][x] not in FLOOR_C | WATER_C | WARP_C | {'WALL', 'HEADBUTT_TREE', 'CUT_TREE'}:
                print('  note: %s (%d,%d) collision %s -> wall' % (name, x, y, m.coll[y][x]))
    # GSC ledges: the HOP cell is the one you stand on; you jump over the next cell (the ledge graphic, wall
    # collision).  Ledges become floor, so the jumped-over cell becomes floor too (when the landing cell is open).
    HOPS = {'HOP_DOWN': [(0, 1)], 'HOP_LEFT': [(-1, 0)], 'HOP_RIGHT': [(1, 0)],
            'HOP_DOWN_LEFT': [(0, 1), (-1, 0)], 'HOP_DOWN_RIGHT': [(0, 1), (1, 0)]}
    for y in range(H):
        for x in range(W):
            for dx, dy in HOPS.get(m.coll[y][x], []):
                ax, ay, bx, by = x + dx, y + dy, x + 2 * dx, y + 2 * dy
                if 0 <= bx < W and 0 <= by < H and sem[ay][ax] == 'W' and m.coll[ay][ax] == 'WALL' \
                        and m.coll[by][bx] in FLOOR_C | WARP_C:
                    sem[ay][ax] = 'F'
    warps = []
    for i, (x, y, dc, di) in enumerate(m.warps):
        dn = CONST2NAME[dc]
        if m.coll[y][x] == 'PIT': continue
        k = warp_kind(m, x, y, dn, cfg['level'])
        sem[y][x] = k
        warps.append((i, x, y, dn, di, k))
    for i, x, y, dn, di, k in warps:
        if k == 'M' and y + 1 < H and sem[y + 1][x] in 'FA': sem[y + 1][x] = 'W'   # mat = south exit
        if k == 'O' and y > 0: sem[y - 1][x] = 'W'
    # reachability: walk + surf from every warp (mats are left northwards, wall doors southwards)
    seen = {(x, y) for _, x, y, *_ in warps}; q = deque(seen)
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if sem[y][x] == 'O' and dy != 1: continue
            if sem[y][x] == 'M' and dy == 1: continue
            if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in seen and sem[ny][nx] in 'FA' \
                    and not edge_wall(m.coll, x, y, dx, dy):
                seen.add((nx, ny)); q.append((nx, ny))
    for y in range(H):
        for x in range(W):
            if sem[y][x] in 'FA' and (x, y) not in seen: sem[y][x] = 'W'
    isW = lambda x, y: not (0 <= x < W and 0 <= y < H) or sem[y][x] == 'W'
    for y in range(H):
        for x in range(W):
            if sem[y][x] == 'W' and not any(isW(x + a, y + b) for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                sem[y][x] = 'R'     # isolated GSC boulder -> FRLG rock (thin wall lines stay walls)
    def cls(x, y):
        if not (0 <= x < W and 0 <= y < H): return 'w'
        s = sem[y][x]
        return 'w' if s in 'WO' else 'a' if s == 'A' else 'f'
    g = [[0] * W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            s = sem[y][x]
            if s == 'W':
                g[y][x] = (L.fill if all(cls(x + a, y + b) == 'w' for a in range(-2, 3) for b in range(-2, 3))
                           else L.pick('w', mask(cls, x, y))) | C1
            elif s == 'A': g[y][x] = L.pick('a', mask(cls, x, y)) | E1
            elif s == 'F':     # plain floor unless water is near (shore rims are learned)
                k = mask(cls, x, y)
                g[y][x] = (L.pick('f', k) if 'a' in k else FLOOR) | E3
            elif s == 'R': g[y][x] = L.rock | C1
            elif s == 'M': g[y][x] = MAT | E3
            elif s == 'D': g[y][x] = LADDER_DOWN | E3
            elif s == 'U':
                g[y][x] = LADDER_UP | E3
                if y > 0 and sem[y - 1][x] == 'W' and L.tops[LADDER_UP]: g[y - 1][x] = L.tops[LADDER_UP]
            elif s == 'O':
                g[y][x] = DOOR | E3
    for y in range(H):      # door tops after the wall pass
        for x in range(W):
            if sem[y][x] == 'O' and y > 0 and L.tops[DOOR]: g[y - 1][x] = L.tops[DOOR]
    return m, sem, g, warps

def check(name, sem, warps, coll, comps=None):
    W, H = len(sem[0]), len(sem)
    pos = [(x, y) for _, x, y, *_ in warps]
    def reach(s):
        seen = {s}; q = deque([s])
        while q:
            x, y = q.popleft()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if sem[y][x] == 'O' and (dx, dy) != (0, 1): continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in seen and sem[ny][nx] in 'FAUDMO' \
                        and not edge_wall(coll, x, y, dx, dy):
                    if sem[ny][nx] == 'O' and (dx, dy) != (0, -1): continue
                    seen.add((nx, ny))
                    if sem[ny][nx] in 'FA': q.append((nx, ny))
        return {i for i, p in enumerate(pos) if p in seen}
    comps = comps or [set(range(len(pos)))]
    for comp in comps:
        for i in comp:
            got = reach(pos[i]) | {i}
            assert comp <= got, (name, i, got, comp)
    return comps

def write(name, W, H, g, sem, L, cfg, warps, idx):
    od = os.path.join(REPO, 'data/layouts', name); os.makedirs(od, exist_ok=True)
    with open(os.path.join(od, 'map.bin'), 'wb') as f:
        for r in g:
            for v in r: f.write(struct.pack('<H', v))
    with open(os.path.join(od, 'border.bin'), 'wb') as f: f.write(struct.pack('<4H', *([L.fill | C1] * 4)))
    os.makedirs('/workspace/p6/sem', exist_ok=True)
    open('/workspace/p6/sem/%s_semantic.txt' % name, 'w').write(
        '# %s %dx%d  F floor W wall R rock A water M mat O wall door U/D ladder\n' % (name, W, H) +
        '\n'.join(''.join(r) for r in sem) + '\n')
    d = os.path.join(REPO, 'data/maps', name); os.makedirs(d, exist_ok=True)
    we = []
    for j, (i, x, y, dn, di, k) in enumerate(warps):
        we.append({"x": x, "y": y, "elevation": 3, "dest_map": MID(dn), "dest_warp_id": str(idx[(name, j)])})
    mj = {"id": MID(name), "name": name, "layout": 'LAYOUT_' + snake_upper(name), "music": cfg['music'],
          "region": "REGION_KANTO", "region_map_section": cfg['mapsec'], "requires_flash": cfg['flash'],
          "weather": "WEATHER_NONE", "map_type": "MAP_TYPE_UNDERGROUND", "allow_cycling": True,
          "allow_escaping": True, "allow_running": True, "show_map_name": False, "floor_number": 0,
          "battle_scene": "MAP_BATTLE_SCENE_NORMAL", "connections": None, "object_events": [],
          "warp_events": we, "coord_events": [], "bg_events": []}
    open(os.path.join(d, 'map.json'), 'w').write(json.dumps(mj, indent=2) + '\n')
    open(os.path.join(d, 'scripts.inc'), 'w').write('%s_MapScripts::\n\t.byte 0\n' % name)
    register('gMapGroup_IndoorJohto', name, W, H, cfg['secondary'], cfg.get('primary', 'gTileset_General_Frlg'))

def wire_outside(outside, ox, oy, dest, wi):
    p = os.path.join(REPO, 'data/maps', outside, 'map.json'); mj = json.load(open(p))
    k = next((i for i, w in enumerate(mj['warp_events']) if (w['x'], w['y']) == (ox, oy)), None)
    if k is None:
        mj['warp_events'].append({"x": ox, "y": oy, "elevation": 0, "dest_map": MID(dest), "dest_warp_id": str(wi)})
        k = len(mj['warp_events']) - 1
    else:
        mj['warp_events'][k].update(dest_map=MID(dest), dest_warp_id=str(wi))
    open(p, 'w').write(json.dumps(mj, indent=2) + '\n')
    return k

def encounters(cfg):
    p = os.path.join(REPO, 'src/data/wild_encounters.json'); wj = json.load(open(p))
    for grp in wj['wild_encounter_groups']:
        enc = grp.get('encounters', [])
        if not any(e.get('base_label', '').startswith('sFourIslandIcefallCave1F_') for e in enc): continue
        for name, (land, water) in cfg['enc'].items():
            for ver in ('FireRed', 'LeafGreen'):
                lab = 's' + name.replace('_', '') + '_' + ver
                e = {"map": MID(name), "base_label": lab}
                if land:
                    e["land_mons"] = {"encounter_rate": 7, "mons": [
                        {"min_level": l, "max_level": l, "species": 'SPECIES_' + s} for s, l in land]}
                if water and any(r.count('A') for r in open('/workspace/p6/sem/%s_semantic.txt' % name).read().split('\n')[1:]):
                    e["water_mons"] = {"encounter_rate": 2, "mons": [
                        {"min_level": l - 5, "max_level": l, "species": 'SPECIES_' + s} for s, l in water]}
                old = next((i for i, x in enumerate(enc) if x.get('base_label') == lab), None)
                if old is None: enc.append(e)
                else: enc[old] = e
        break
    open(p, 'w').write(json.dumps(wj, indent=2, ensure_ascii=False) + '\n')

def run(gname):
    cfg = GROUPS[gname]
    L = Learner(cfg['secondary'], cfg['refs'])
    built = {}
    for name in cfg['maps']:
        m, sem, g, warps = build(cfg, name, L)
        check(name, sem, warps, m.coll, cfg.get('comps', {}).get(name))
        built[name] = (m, sem, g, warps)
        print('%-28s %dx%d warps %s reach OK' % (name, m.w, m.h, [(x, y, k, dn) for _, x, y, dn, _, k in warps]))
    # index maps: (map, our warp j) -> dest warp index
    pos = {n: [(i, x, y) for i, x, y, *_ in b[3]] for n, b in built.items()}
    idx = {}
    for name, (m, sem, g, warps) in built.items():
        for j, (i, x, y, dn, di, k) in enumerate(warps):
            if dn in built:
                idx[(name, j)] = next(jj for jj, (ii, *_ ) in enumerate(pos[dn]) if ii == di)
            else:
                assert dn in cfg['outside'], (name, dn)
                ox, oy = pkc.load(dn).warps[di][:2]
                idx[(name, j)] = wire_outside(dn, ox, oy, name, j)
    for name, (m, sem, g, warps) in built.items():
        write(name, m.w, m.h, g, sem, L, cfg, warps, idx)
    encounters(cfg)
    return built

if __name__ == '__main__':
    for gname in (sys.argv[1:] or list(GROUPS)):
        run(gname)
