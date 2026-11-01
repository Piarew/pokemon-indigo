#!/usr/bin/env python3
"""Convert the Pokemon Gold/Silver Cherrygrove City map image into a FRLG-tileset layout.

Source image: https://archives.bulbagarden.net/media/upload/0/09/Cherrygrove_City_GSC.png
(640x288 px = 20x9 GSC 32px blocks = 40x18 cells of 16x16 px).

Approach
  * Scale: 1 GSC 16x16 px cell (2x2 GB tiles, one quarter of a 32x32 GSC block)
    -> 1 FRLG 16x16 metatile.  So the 20x9-block GSC map becomes a 40x18 layout,
    the same pixel scale as the original.
  * Every distinct 16x16 cell in the image (40 of them) was labelled by hand with a
    semantic class (CELL_CLASS below). No pixel matching against FRLG art.
  * Each class is drawn with existing metatiles from gTileset_General_Frlg (primary)
    and gTileset_ViridianCity (secondary), with auto-tiling for path/water/forest edges.
  * Buildings are stamped from templates copied verbatim (incl. collision/elevation)
    out of data/layouts/ViridianCity_Frlg/map.bin.
  * Collision/elevation for every other metatile = the most common value that metatile
    has across all existing FRLG layouts in the repo.

Usage:  python3 tools/cherrygrove/convert_cherrygrove.py [path/to/Cherrygrove_City_GSC.png]
Writes data/layouts/CherrygroveCity/{map.bin,border.bin} and
tools/cherrygrove/cherrygrove_semantic.txt.
"""
import collections, json, os, struct, sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
SRC = sys.argv[1] if len(sys.argv) > 1 else '/workspace/cherrygrove_gsc.png'
W, H = 40, 18

# ---------------------------------------------------------------- semantic classes
# Unique 16x16 cells, numbered in raster order of first appearance in the image
# (see tools/cherrygrove/gsc_cells.png).
CELL_CLASS = {
    0: 'T', 8: 'T', 15: 'T',               # forest tree top / bottom half, lone tree on grass
    1: 'P',                                 # pale dotted ground = town path
    16: 'G',                                # bright green = lawn
    31: 'F', 35: 'F',                       # lawn with red flower
    5: 'W', 6: 'W', 7: 'W', 22: 'W', 38: 'W', 39: 'W',  # sea (5/7/22/38/39 = rock-edged shore)
    27: 'R',                                # sea with submerged rocks -> rocks in water
    37: 'R',                                # rock plateau (islet) -> rocks in water
    23: 'B0', 24: 'B1', 25: 'B2', 26: 'B3', # 2x2 boulder (TL, TR, BL, BR)
    36: 'S',                                # metal sign
    # Mart (2,3,4 / 9,10,11 / 12,13,14 / 17,18,19,20), PC (.. 21), houses (28,29,30 / 32,18,33,34)
    2: 'X', 3: 'X', 4: 'X', 9: 'X', 10: 'X', 11: 'X', 12: 'X', 13: 'X', 14: 'X',
    17: 'X', 18: 'X', 19: 'X', 20: 'X', 21: 'X', 28: 'X', 29: 'X', 30: 'X',
    32: 'X', 33: 'X', 34: 'X',
}

# ---------------------------------------------------------------- FRLG metatiles
FOREST_TOP = (0x01C, 0x01D)          # even row, (even x, odd x)
FOREST_BOT = (0x014, 0x015)
FOREST_TOP_L, FOREST_TOP_R = 0x01E, 0x01F
FOREST_BOT_L, FOREST_BOT_R = 0x016, 0x017
FOREST_TRUNK = (0x024, 0x025)        # bottom row of a forest, trunks over grass
FOREST_TRUNK_L, FOREST_TRUNK_R = 0x026, 0x027
GRASS = (0x008, 0x009, 0x010, 0x011)
FLOWER = 0x004
SIGN = 0x002
# grey paved path (primary) 9-slice + concave corners
PATH = {'C': 0x16E, 'T': 0x166, 'B': 0x176, 'L': 0x16D, 'R': 0x16F,
        'TL': 0x165, 'TR': 0x167, 'BL': 0x175, 'BR': 0x177,
        'iUR': 0x196, 'iUL': 0x195, 'iDR': 0x19E, 'iDL': 0x19D}
# sea with rocky rim (primary)
SEA = {'C': 0x12B, 'T': 0x123, 'L': 0x12A, 'R': 0x12C, 'TL': 0x120, 'TR': 0x121,
       'iUL': 0x131, 'iUR': 0x130}
SHORE_BELOW_WATER = 0x133            # land tile drawn under a water body
WATER_ROCK = ((0x110, 0x111), (0x118, 0x119))

# Building templates: (x0, y0, w, h) rectangles in ViridianCity_Frlg/map.bin
VIRIDIAN = ('ViridianCity_Frlg', 48, 40)
TEMPLATES = {
    'house': (24, 8, 5, 4),   # green-roof house, door at (1,3)
    'mart':  (34, 16, 4, 4),  # door at (2,3)
    'pc':    (24, 23, 5, 4),  # Poke Center minus its top roof-lip row (2B0-2B4); door at (2,3)
}
# placements (template, x, y) in the new map + doors/signs (see notes)
BUILDINGS = [
    ('mart', 22, 0),   # GSC mart cols 22-25 rows 0-3, door (23,3) -> FRLG door (24,3)
    ('pc',   27, 0),   # GSC PC cols 28-31, door (29,3) -> FRLG cols 27-31, door (29,3)
    ('house', 16, 4),  # GSC 16-19 x 6-7, door (17,7) -> 16-20 x 4-7, door (17,7)
    ('house', 24, 6),  # GSC 24-27 x 8-9, door (25,9) -> 24-28 x 6-9, door (25,9)
    ('house', 30, 8),  # GSC 30-33 x 10-11, door (31,11) -> 30-34 x 8-11, door (31,11)
]
# semantic overrides applied after classification (x, y, class) -- documented in notes
OVERRIDES = [
    ((26, 0), (26, 3), 'G'),   # half tree left between Mart and widened PC -> lawn
    ((35, 8), (35, 11), 'G'),  # half tree left right of widened house 3 -> lawn
    ((35, 2), (35, 2), 'T'),   # complete the 2x2 FRLG tree for the lone GSC trees at (34..35, 2..3)
    ((30, 8), (30, 8), 'P'),   # city sign moved off house-3 roof...
    ((31, 7), (31, 7), 'S'),   # ...to (31,7)
]


def load_blocks(name, w, h):
    d = open(os.path.join(REPO, 'data/layouts', name, 'map.bin'), 'rb').read()
    v = struct.unpack('<%dH' % (w * h), d)
    return [list(v[r * w:(r + 1) * w]) for r in range(h)]


def common_attrs():
    """most common (collision|elevation) upper bits per metatile id across FRLG layouts"""
    layouts = json.load(open(os.path.join(REPO, 'data/layouts/layouts.json')))['layouts']
    c = collections.defaultdict(collections.Counter)
    for l in layouts:
        if l.get('primary_tileset') != 'gTileset_General_Frlg':
            continue
        sec_ok = l.get('secondary_tileset') == 'gTileset_ViridianCity'
        b = load_blocks(os.path.basename(os.path.dirname(l['blockdata_filepath'])), l['width'], l['height'])
        for row in b:
            for v in row:
                m = v & 0x3FF
                if m < 0x280 or sec_ok:
                    c[m][v & 0xFC00] += 1
    return {m: cnt.most_common(1)[0][0] for m, cnt in c.items()}


def classify():
    im = Image.open(SRC).convert('RGB')
    assert im.size == (640, 288), im.size
    uniq, grid = {}, []
    for y in range(H):
        row = []
        for x in range(W):
            k = im.crop((x * 16, y * 16, x * 16 + 16, y * 16 + 16)).tobytes()
            uniq.setdefault(k, len(uniq))
            row.append(uniq[k])
        grid.append(row)
    sem = [[CELL_CLASS[c] for c in row] for row in grid]
    return grid, sem


def main():
    grid, sem = classify()
    for (x0, y0), (x1, y1), cls in OVERRIDES:
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                sem[y][x] = cls
    attrs = common_attrs()
    vir = load_blocks(*VIRIDIAN)
    out = [[None] * W for _ in range(H)]

    # stamp buildings
    bmask = [[False] * W for _ in range(H)]
    for name, bx, by in BUILDINGS:
        tx, ty, tw, th = TEMPLATES[name]
        for dy in range(th):
            for dx in range(tw):
                out[by + dy][bx + dx] = vir[ty + dy][tx + dx]
                bmask[by + dy][bx + dx] = True
                sem[by + dy][bx + dx] = 'X'

    def S(x, y, default):
        if 0 <= x < W and 0 <= y < H:
            return sem[y][x]
        return default

    def put(x, y, m):
        out[y][x] = m | attrs.get(m, 0)

    def SEA_CENTER_FOR(x, y):
        land = lambda xx, yy: S(xx, yy, 'W') not in ('W', 'R', 'B0', 'B1', 'B2', 'B3')
        u, l, r = land(x, y - 1), land(x - 1, y), land(x + 1, y)
        if u and l: k = 'TL'
        elif u and r: k = 'TR'
        elif u: k = 'T'
        elif l: k = 'L'
        elif r: k = 'R'
        elif land(x - 1, y - 1): k = 'iUL'
        elif land(x + 1, y - 1): k = 'iUR'
        else: k = 'C'   # FRLG sea has no rim tile for land only below / diagonally below
        return SEA[k]

    for y in range(H):
        for x in range(W):
            if bmask[y][x]:
                continue
            c = sem[y][x]
            if c == 'T':
                isT = lambda xx, yy: S(xx, yy, 'T') == 'T'
                top = (y % 2 == 0)
                left_edge = x % 2 == 0 and not isT(x - 1, y)
                right_edge = x % 2 == 1 and not isT(x + 1, y)
                if top:
                    m = FOREST_TOP_L if left_edge else FOREST_TOP_R if right_edge else FOREST_TOP[x % 2]
                elif not isT(x, y + 1):
                    m = FOREST_TRUNK_L if left_edge else FOREST_TRUNK_R if right_edge else FOREST_TRUNK[x % 2]
                else:
                    m = FOREST_BOT_L if left_edge else FOREST_BOT_R if right_edge else FOREST_BOT[x % 2]
                put(x, y, m)
            elif c in ('G', 'F'):
                water_above = S(x, y - 1, c) in ('W',)
                if c == 'F':
                    m = FLOWER
                elif water_above:
                    m = SHORE_BELOW_WATER
                else:
                    m = GRASS[(x * 7 + y * 13 + (x * y) % 5) % 4]
                put(x, y, m)
            elif c == 'S':
                put(x, y, SIGN)
            elif c == 'P':
                isP = lambda xx, yy: S(xx, yy, 'P') in ('P', 'S')
                u, d, l, r = isP(x, y - 1), isP(x, y + 1), isP(x - 1, y), isP(x + 1, y)
                key = ('T' if not u else 'B' if not d else '') + ('L' if not l else 'R' if not r else '')
                if key == '':
                    if not isP(x + 1, y - 1): key = 'iUR'
                    elif not isP(x - 1, y - 1): key = 'iUL'
                    elif not isP(x + 1, y + 1): key = 'iDR'
                    elif not isP(x - 1, y + 1): key = 'iDL'
                    else: key = 'C'
                put(x, y, PATH[key])
            elif c == 'W':
                put(x, y, SEA_CENTER_FOR(x, y))
            elif c == 'R':
                # Only a full, 2-aligned 2x2 group of rock cells becomes a FRLG water rock;
                # FRLG has no 1x1 rock-in-water metatile, so stray rock cells become sea.
                bx, by = x - x % 2, y - y % 2
                if all(S(bx + i, by + j, '') == 'R' for i in (0, 1) for j in (0, 1)):
                    put(x, y, WATER_ROCK[y % 2][x % 2])
                else:
                    sem[y][x] = 'W'
                    put(x, y, SEA_CENTER_FOR(x, y))
            elif c.startswith('B'):
                i = int(c[1])
                put(x, y, WATER_ROCK[i // 2][i % 2])
            else:
                raise SystemExit('unhandled class %r at %d,%d' % (c, x, y))

    od = os.path.join(REPO, 'data/layouts/CherrygroveCity')
    os.makedirs(od, exist_ok=True)
    with open(os.path.join(od, 'map.bin'), 'wb') as f:
        for row in out:
            f.write(struct.pack('<%dH' % W, *row))
    # border: same 2x2 forest block Viridian City uses
    with open(os.path.join(REPO, 'data/layouts/ViridianCity_Frlg/border.bin'), 'rb') as f:
        border = f.read()
    with open(os.path.join(od, 'border.bin'), 'wb') as f:
        f.write(border)
    with open(os.path.join(HERE, 'cherrygrove_semantic.txt'), 'w') as f:
        f.write('# semantic grid after overrides/buildings (40x18). T=tree P=path G=lawn F=flower\n'
                '# W=sea R=rocks-in-water B0..B3=boulder quarters S=sign X=building\n')
        for row in sem:
            f.write(' '.join('%-2s' % c for c in row) + '\n')
        f.write('\n# raw unique-cell ids from the source image\n')
        for row in grid:
            f.write(' '.join('%2d' % c for c in row) + '\n')
    print('wrote', od)


if __name__ == '__main__':
    main()
