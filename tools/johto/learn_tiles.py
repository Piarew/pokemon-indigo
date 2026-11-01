#!/usr/bin/env python3
"""Learn auto-tiling rules for a metatile *family* from the existing FRLG layouts.

For every cell of every FRLG layout (gTileset_General_Frlg primary) whose metatile is in
the family, record its neighbourhood signature (which of the 8 neighbours are also in the
family, plus how far the family extends N/S/W/E, capped) and the metatile actually used.
`pick()` then returns the most common metatile for a signature, falling back to coarser
signatures and finally to the nearest seen 8-neighbour pattern.
"""
import collections, json, os, struct, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'cherrygrove'))
from fr_render import REPO

N8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
W8 = [1, 2, 1, 2, 2, 1, 2, 1]   # orthogonal neighbours matter more


# our own Johto conversions must never feed back into the corpus
JOHTO = ('CherrygroveCity', 'BlackthornCity', 'MahoganyTown', 'VioletCity',
         'Route29', 'Route30', 'Route31', 'Route42', 'Route43', 'Route44',
         'EcruteakCity', 'NewBarkTown', 'Route26', 'Route27', 'Route28', 'SilverCaveOutside')


# FRLG layouts edited by frlg_edits.py: learn from the untouched upstream copy so the edits never
# feed back into the tilers (keeps converter output stable).
PRISTINE = {'data/layouts/Route22_Frlg/map.bin': '72bd0bff9c'}


def frlg_layouts():
    for l in json.load(open(os.path.join(REPO, 'data/layouts/layouts.json')))['layouts']:
        if l.get('primary_tileset') == 'gTileset_General_Frlg' and not l['name'].startswith(('RS_',) + JOHTO) and 'BattleTower' not in l['name']:
            if l['blockdata_filepath'] in PRISTINE:
                import subprocess
                d = subprocess.check_output(['git', 'show', '%s:%s' % (PRISTINE[l['blockdata_filepath']],
                                                                       l['blockdata_filepath'])], cwd=REPO)
            else:
                d = open(os.path.join(REPO, l['blockdata_filepath']), 'rb').read()
            w, h = l['width'], l['height']
            v = struct.unpack('<%dH' % (w * h), d[:w * h * 2])
            yield l, [[v[y * w + x] for x in range(w)] for y in range(h)]


def run(mask, x, y, dx, dy, cap):
    n = 0
    while n < cap:
        x += dx; y += dy
        if not mask(x, y):
            break
        n += 1
    return n


def signature(mask, x, y, caps=(3, 3, 2, 2)):
    n8 = tuple(bool(mask(x + dx, y + dy)) for dx, dy in N8)
    d = (run(mask, x, y, 0, -1, caps[0]), run(mask, x, y, 0, 1, caps[1]),
         run(mask, x, y, -1, 0, caps[2]), run(mask, x, y, 1, 0, caps[3]))
    return n8, d


class Learned:
    def __init__(self, family, allowed=None, edge_in=True):
        """family: set of metatile ids; allowed: ids that may be emitted (default family)"""
        self.family = set(family)
        self.allowed = set(allowed if allowed is not None else family)
        self.full = collections.defaultdict(collections.Counter)
        self.mid = collections.defaultdict(collections.Counter)
        self.n8 = collections.defaultdict(collections.Counter)
        for l, b in frlg_layouts():
            h, w = len(b), len(b[0])
            def mask(x, y):
                if 0 <= x < w and 0 <= y < h:
                    return (b[y][x] & 0x3FF) in self.family
                return edge_in   # off-map counts as "more of the same"
            for y in range(h):
                for x in range(w):
                    m = b[y][x] & 0x3FF
                    if m not in self.allowed:
                        continue
                    n8, d = signature(mask, x, y)
                    self.full[(n8, d)][m] += 1
                    self.mid[(n8, d[1])][m] += 1
                    self.n8[n8][m] += 1
        self.stats = collections.Counter()

    def pick(self, mask, x, y):
        n8, d = signature(mask, x, y)
        for table, key, lvl in ((self.full, (n8, d), 'full'), (self.mid, (n8, d[1]), 'mid'),
                                (self.n8, n8, 'n8')):
            if key in table:
                self.stats[lvl] += 1
                return table[key].most_common(1)[0][0]
        # nearest seen 8-neighbour pattern
        best = min(self.n8, key=lambda k: (sum(w for a, b_, w in zip(k, n8, W8) if a != b_),
                                           -sum(self.n8[k].values())))
        self.stats['nearest'] += 1
        return self.n8[best].most_common(1)[0][0]
