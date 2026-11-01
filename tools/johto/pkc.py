#!/usr/bin/env python3
"""Read pokecrystal (pret/pokecrystal, cloned at $PKC, default /workspace/pokecrystal) map data:
block map (.blk), tileset metatiles + per-quadrant collision, warps / bg events / connections.
Every GSC block is 2x2 16px cells, so one collision value per cell (1:1 with FRLG metatiles).

  m = load('SilverCaveRoom1')
  m.w, m.h (cells), m.coll[y][x] ('FLOOR', 'WALL', 'WATER', 'LADDER', ...), m.quad[y][x] (4 GSC tile ids),
  m.warps [(x, y, DEST_CONST, dest_index_0based)], m.signs [(x, y, kind)], m.tileset, m.conns [(dir, CONST, off)]
"""
import os, re
PKC = os.environ.get('PKC', '/workspace/pokecrystal')
_coll_names = {}
for mm in re.finditer(r'DEF COLL_(\w+)\s+EQU \$([0-9a-f]+)', open(os.path.join(PKC, 'constants/collision_constants.asm')).read()):
    _coll_names.setdefault(int(mm.group(2), 16), mm.group(1))

def _tileset_coll(ts):
    out = []
    for line in open(os.path.join(PKC, 'data/tilesets/%s_collision.asm' % ts)):
        mm = re.match(r'\s*tilecoll\s+([^;]+)', line)
        if not mm: continue
        vals = []
        for t in mm.group(1).split(','):
            t = t.strip()
            vals.append(_coll_names.get(int(t, 16), t) if re.fullmatch(r'[0-9a-fA-F]{2}', t) else t)
        out.append(vals)
    return out

def _const_name(name):      # SilverCaveRoom1 -> SILVER_CAVE_ROOM_1 (pokecrystal style)
    s = re.sub(r'(?<=[a-z])(?=[A-Z0-9])|(?<=[0-9])(?=[A-Z])', '_', name).upper()
    return s

_dims = {mm.group(1): (int(mm.group(2)), int(mm.group(3))) for mm in re.finditer(
    r'map_const\s+(\w+),\s*(\d+),\s*(\d+)', open(os.path.join(PKC, 'constants/map_constants.asm')).read())}
_maps = {mm.group(1): mm.group(2) for mm in re.finditer(r'^\s*map (\w+), TILESET_(\w+)', open(os.path.join(PKC, 'data/maps/maps.asm')).read(), re.M)}
_attr = open(os.path.join(PKC, 'data/maps/attributes.asm')).read()
_blk = {}
for mm in re.finditer(r'^(\w+)_Blocks:\s*\n((?:\w+_Blocks:\s*\n)*)\s*INCBIN "([^"]+)"', open(os.path.join(PKC, 'data/maps/blocks.asm')).read(), re.M):
    for lab in [mm.group(1)] + re.findall(r'(\w+)_Blocks:', mm.group(2)):
        _blk[lab] = mm.group(3)

class Map: pass

def load(name):
    m = Map(); m.name = name
    am = re.search(r'map_attributes %s, (\w+), \$[0-9a-f]+\n((?:\s*connection.*\n)*)' % name, _attr)
    m.const = am.group(1)
    m.conns = [(c[0], c[2], int(c[3])) for c in re.findall(r'connection (\w+), (\w+), (\w+), (-?\d+)', am.group(2))]
    bw, bh = _dims[m.const]
    m.w, m.h = bw * 2, bh * 2
    m.tileset = _maps[name].lower()
    blk = open(os.path.join(PKC, _blk[name]), 'rb').read()
    assert len(blk) == bw * bh, (name, len(blk), bw, bh)
    meta = open(os.path.join(PKC, 'data/tilesets/%s_metatiles.bin' % m.tileset), 'rb').read()
    coll = _tileset_coll(m.tileset)
    m.blocks = [list(blk[y * bw:(y + 1) * bw]) for y in range(bh)]
    m.coll = [[None] * m.w for _ in range(m.h)]
    m.quad = [[None] * m.w for _ in range(m.h)]
    for by in range(bh):
        for bx in range(bw):
            b = blk[by * bw + bx]
            for q in range(4):
                cx, cy = bx * 2 + q % 2, by * 2 + q // 2
                m.coll[cy][cx] = coll[b][q] if b < len(coll) else 'WALL'
                t = meta[b * 16:(b + 1) * 16]
                ox, oy = (q % 2) * 2, (q // 2) * 2
                m.quad[cy][cx] = (t[oy * 4 + ox], t[oy * 4 + ox + 1], t[(oy + 1) * 4 + ox], t[(oy + 1) * 4 + ox + 1])
    src = open(os.path.join(PKC, 'maps/%s.asm' % name)).read()
    m.warps = [(int(a), int(b), c, int(d) - 1) for a, b, c, d in re.findall(r'warp_event\s+(\d+),\s*(\d+),\s*(\w+),\s*(\d+)', src)]
    m.signs = [(int(a), int(b), c) for a, b, c in re.findall(r'bg_event\s+(\d+),\s*(\d+),\s*(\w+)', src)]
    m.objects = re.findall(r'object_event\s+(\d+),\s*(\d+),\s*(\w+),.*?OBJECTTYPE_(\w+),\s*\w+,\s*(\w+)', src)
    return m

def show(m):
    ch = {'FLOOR': '.', 'WALL': '#', 'WATER': '~', 'LADDER': 'H', 'STAIRCASE': 'S', 'PIT': 'O', 'CAVE': 'C',
          'WARP_CARPET_DOWN': 'v', 'WARP_CARPET_UP': '^', 'WARP_CARPET_LEFT': '<', 'WARP_CARPET_RIGHT': '>',
          'DOOR': 'D', 'TALL_GRASS': '"', 'WATERFALL': 'Y', 'ICE': 'I', 'HOP_DOWN': 'L', 'HOP_LEFT': '[', 'HOP_RIGHT': ']',
          'HOP_DOWN_LEFT': 'L', 'HOP_DOWN_RIGHT': 'L', 'UP_WALL': '_', 'HEADBUTT_TREE': 'T', 'CUT_TREE': 'u',
          'WHIRLPOOL': '@', 'BUOY': 'b', 'COUNTER': '=', 'LONG_GRASS': '"', 'RIGHT_WALL': '|', 'LEFT_WALL': '|'}
    wp = {(x, y): str(i % 10) for i, (x, y, _, _) in enumerate(m.warps)}
    return '\n'.join(''.join(wp.get((x, y), ch.get(m.coll[y][x], '?')) for x in range(m.w)) for y in range(m.h))

if __name__ == '__main__':
    import sys
    for n in sys.argv[1:]:
        m = load(n)
        print(n, m.const, m.w, m.h, m.tileset, m.conns, m.warps)
        print(show(m))
