"""Stamp library for building FRLG town maps on gTileset_General_Frlg + gTileset_SaffronCity.

All building stamps are copied verbatim (metatile | collision | elevation) from
data/layouts/SaffronCity_Frlg/map.bin so they stay pixel-identical to Saffron.
Walkable tiles are forced to elevation 3 (Saffron's ground elevation).

Coordinates: Canvas uses (x, y) = column, row; stamp(...) places the stamp's top-left.
"""
import os, struct

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SAFFRON = os.path.join(REPO, 'data/layouts/SaffronCity_Frlg/map.bin')
SW, SH = 66, 55
_s = struct.unpack('<%dH' % (SW * SH), open(SAFFRON, 'rb').read())

def saffron(x, y):
    return _s[y * SW + x]

ELEV = 3
PAVE = 0x2E9          # plain city paving (walkable)
GRASS = 0x001         # plain grass (walkable)
FLOWER = 0x004        # red flowers (walkable)
SIGN = 0x002          # wooden signpost (solid)
BUSH = 0x005          # small round bush (solid)

# name: (sx0, sy0, sx1, sy1, [door offsets relative to top-left], note)
STAMPS = {
    'house_door':      (21, 10, 24, 14, [(1, 4)], '4x5 two-storey green-roof house, door bottom'),
    'house_plain':     (17, 10, 20, 14, [],       '4x5 two-storey house, no door (decor)'),
    'house_short':     (22, 18, 25, 21, [],       '4x4 one-storey house, no door (decor)'),
    'house_wide_door': (41, 34, 45, 38, [(2, 4)], '5x5 wide house (Mr. Psychic), door bottom centre'),
    'mart':            (38, 18, 41, 21, [(2, 3)], '4x4 Poke Mart'),
    'pokecenter':      (22, 34, 26, 38, [(2, 4)], '5x5 Pokemon Center'),
    'apartment':       (19, 25, 23, 30, [],       '5x6 yellow apartment block, no door (decor)'),
    'tower':           (29, 16, 37, 30, [(4, 14)],'9x15 Silph-style tower'),
    'dojo':            (37, 8, 42, 12,  [(3, 4)], '6x5 dojo; door is walk-through (non-animated)'),
    'gym':             (43, 8, 49, 12,  [(3, 4)], '7x5 gym building'),
    'sign_tall':       (42, 13, 42, 14, [],       '1x2 Saffron city sign (top walkable overlay, bottom solid)'),
}

def stamp_size(name):
    sx0, sy0, sx1, sy1 = STAMPS[name][:4]
    return sx1 - sx0 + 1, sy1 - sy0 + 1

def raw(mt, col, elev):
    return (mt & 0x3FF) | ((col & 3) << 10) | ((elev & 0xF) << 12)


class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.b = [[raw(PAVE, 0, ELEV)] * w for _ in range(h)]
        self.doors = {}      # name -> list of (x, y)
        self.log = []

    def set(self, x, y, mt, col=0, elev=None):
        if elev is None:
            elev = 0 if col else ELEV
        self.b[y][x] = raw(mt, col, elev)

    def mt(self, x, y):
        return self.b[y][x] & 0x3FF

    def solid(self, x, y):
        return (self.b[y][x] >> 10) & 3 != 0

    def fill(self, x0, y0, x1, y1, mt, col=0):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.set(x, y, mt, col)

    def copy_saffron(self, sx0, sy0, sx1, sy1, dx, dy, walk_elev=ELEV):
        """Copy a Saffron rectangle so that its top-left lands at (dx, dy)."""
        for y in range(sy0, sy1 + 1):
            for x in range(sx0, sx1 + 1):
                v = saffron(x, y)
                if not (v >> 10) & 3:
                    v = (v & 0x0FFF) | (walk_elev << 12)
                self.b[dy + y - sy0][dx + x - sx0] = v

    def stamp(self, name, x, y, label=None):
        sx0, sy0, sx1, sy1, doors, note = STAMPS[name]
        w, h = stamp_size(name)
        assert 0 <= x and x + w <= self.w and 0 <= y and y + h <= self.h, (name, x, y)
        self.copy_saffron(sx0, sy0, sx1, sy1, x, y)
        pos = [(x + dx, y + dy) for dx, dy in doors]
        self.doors.setdefault(label or name, []).extend(pos)
        self.log.append('%-24s %-16s at (%2d,%2d) size %dx%d doors %s' % (label or name, name, x, y, w, h, pos))
        return pos

    # --- trees -----------------------------------------------------------
    @staticmethod
    def tree_mt(x, y):
        """Saffron tree grid: even x = left half, odd x = right half; even y = top, odd y = bottom."""
        return [[0x014, 0x015], [0x01C, 0x01D]][y & 1][x & 1]

    def trees(self, x0, y0, x1, y1):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.set(x, y, self.tree_mt(x, y), 1)

    def tree_clump(self, x, y, w=2, h=2):
        """Free-standing tree(s) on grass, FRLG town style (Celadon 46-47,4-6): crown top 0x00E/0x00F
        (drawn over grass), crown bottom 0x01E/0x01F, trunk row 0x024/0x025. x, y even; w=2 per tree.
        Occupies rows y..y+2. h is kept for API compatibility (single tree height only)."""
        assert x % 2 == 0 and y % 2 == 0 and w % 2 == 0
        for xx in range(x, x + w):
            r = xx % 2
            self.set(xx, y, (0x00E, 0x00F)[r], 1)
            self.set(xx, y + 1, (0x01E, 0x01F)[r], 1)
            self.set(xx, y + 2, (0x024, 0x025)[r], 1)

    # --- fences ----------------------------------------------------------
    def fence_h(self, x0, x1, y):
        """Free-standing horizontal fence (Saffron 31D 30D.. 31E)."""
        for x in range(x0, x1 + 1):
            self.set(x, y, 0x31D if x == x0 else 0x31E if x == x1 else 0x30D, 1)

    def fence_v(self, x, y0, y1, side='left'):
        """Vertical fence run (Saffron perimeter posts 0x320 left-style / 0x322 right-style)."""
        for y in range(y0, y1 + 1):
            self.set(x, y, 0x320 if side == 'left' else 0x322, 1)

    def plaza(self, x0, y0, x1, y1):
        """Saffron's darker paved 'lot' patch (2E3/2E4/2E5 top, 2EB/2EC/2ED sides+fill, 2F3/2F4/2F5 bottom).
        Only repaints tiles that are currently plain walkable paving, so call it BEFORE or AFTER stamping
        buildings - buildings are never overwritten. Use it under/around groups of buildings like Saffron."""
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if self.mt(x, y) != PAVE or self.solid(x, y):
                    continue
                top, bot, left, right = y == y0, y == y1, x == x0, x == x1
                if top:
                    m = 0x2E3 if left else 0x2E5 if right else 0x2E4
                elif bot:
                    m = 0x2F3 if left else 0x2F5 if right else 0x2F4
                else:
                    m = 0x2EB if left else 0x2ED if right else 0x2EC
                self.set(x, y, m)

    def grass_patch(self, x0, y0, x1, y1):
        """Plain grass rectangle (walkable). Trees/flowers/bushes may only go on grass, never on paving."""
        self.fill(x0, y0, x1, y1, GRASS)

    def save(self, layout_dir):
        os.makedirs(layout_dir, exist_ok=True)
        with open(os.path.join(layout_dir, 'map.bin'), 'wb') as f:
            for row in self.b:
                f.write(struct.pack('<%dH' % self.w, *row))
        with open(os.path.join(REPO, 'data/layouts/SaffronCity_Frlg/border.bin'), 'rb') as src:
            open(os.path.join(layout_dir, 'border.bin'), 'wb').write(src.read())


def frame(c, west=6, east=59, top_fence=9, bottom_fence=45, gate_dx=0, cave_x=34):
    """Build the outer frame used by Indigo City:
    - Victory Road mountain face across rows 0..5 with the cave entrance (0xA9) at (cave_x, 5).
    - Approach area rows 6..top_fence-1: grass with a sandy path from the cave down to the fence gap.
    - Saffron-style perimeter fence (west fence column at even x, east at odd x, top/bottom at odd y)
      with tree belts outside using Saffron's fence-adjacent tree variants.
    - Saffron's south gatehouse (Saffron x31..38, y43..52) centred on the main avenue.
    Returns dict with gate warp tiles, cave tile and the checkpoint gap tiles."""
    W, H = c.w, c.h
    assert west % 2 == 0 and east % 2 == 1 and top_fence % 2 == 1 and bottom_fence % 2 == 1
    # everything outside starts as trees
    c.trees(0, 0, W - 1, H - 1)
    # interior paving
    c.fill(west + 1, top_fence + 1, east - 1, bottom_fence - 1, PAVE)
    # side fences + adjacent tree variants
    for y in range(top_fence + 1, bottom_fence):
        c.set(west, y, 0x320, 1); c.set(east, y, 0x322, 1)
    for y in range(top_fence, bottom_fence + 2):
        c.set(west - 1, y, 0x017 if y % 2 == 0 else 0x01F, 1)
        c.set(east + 1, y, 0x016 if y % 2 == 0 else 0x01E, 1)
    # bottom fence (Saffron rows 43-45)
    c.set(west, bottom_fence, 0x328, 1); c.set(east, bottom_fence, 0x32A, 1)
    for x in range(west + 1, east):
        c.set(x, bottom_fence, 0x329, 1)
        c.set(x, bottom_fence + 1, 0x30F if x % 2 else 0x30E, 1)   # fence foot shading (unreachable -> solid)
        c.set(x, bottom_fence + 2, 0x01F if x % 2 else 0x01E, 1)
    c.set(west, bottom_fence + 1, 0x316, 1); c.set(east, bottom_fence + 1, 0x317, 1)
    c.set(west, bottom_fence + 2, 0x01E, 1); c.set(east, bottom_fence + 2, 0x01F, 1)
    # south gatehouse: Saffron x31..38, y43..52 ; Saffron fence row is 43 -> align to bottom_fence
    gdx, gdy = 31 + gate_dx, bottom_fence
    c.copy_saffron(31, 43, 38, 52, gdx, gdy)
    gate = [(gdx + 3, gdy + 3), (gdx + 4, gdy + 3)]          # MB_SOUTH_ARROW_WARP tiles (Saffron 34,46 / 35,46)
    # top fence: Saffron row 8 (0x024/0x025 trunks) + row 9 (0x318 corner, 0x319 rail, 0x31C rail end)
    gap = [cave_x, cave_x + 1]
    for x in range(west, east + 1):
        if x == west:
            c.set(x, top_fence, 0x318, 1)
        elif x in gap:
            c.set(x, top_fence, 0x2E1, 0)                        # Saffron's gap paving (row 9 x33-36)
        else:
            c.set(x, top_fence, 0x319, 1)
    c.set(gap[0] - 1, top_fence, 0x31C, 1)           # rail end left of the gap (Saffron 32,9)
    c.set(gap[1] + 1, top_fence, 0x31B, 1)           # rail end right of the gap
    # approach area between mountain and fence
    c.fill(west, 6, east, top_fence - 1, GRASS)       # trees keep whole 2-wide trunks: x<=west-1 (odd) and x>=east+1 (even)
    # sandy path cave -> gap (Saffron north gate approach tiles)
    for y in range(6, top_fence):
        c.set(gap[0], y, 0x0DB if y < top_fence - 1 else 0x0E3); c.set(gap[1], y, 0x0DD if y < top_fence - 1 else 0x0E5)
    c.set(gap[0], 6, 0x0D3); c.set(gap[1], 6, 0x0D5)
    # mountain rows 0..5 : rock fill, bottom edge (0x07C), face (0x079) with cave 0xA9
    for x in range(W):
        for y in range(0, 4):
            c.set(x, y, 0x071, 1)
        c.set(x, 4, 0x07C, 1)
        c.set(x, 5, 0x079, 1)
    c.set(cave_x, 5, 0x0A9, 0)      # cave entrance (MB_NON_ANIMATED_DOOR, walkable like Route 4/23)
    # gap tiles also get grass shoulders cleared of trunks
    return {'gate_warps': gate, 'cave': (cave_x, 5), 'checkpoint_gap': [(g, top_fence) for g in gap]}
