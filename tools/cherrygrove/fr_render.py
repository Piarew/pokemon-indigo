#!/usr/bin/env python3
"""Render FRLG metatiles / map layouts from pokeemerald-expansion tileset data (PIL).

Usage as module: from fr_render import Tilesets, render_layout
"""
import os, struct
from PIL import Image, ImageDraw

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
NUM_TILES_PRIMARY = 640      # NUM_TILES_IN_PRIMARY_FRLG
NUM_METATILES_PRIMARY = 640  # NUM_METATILES_IN_PRIMARY_FRLG
NUM_PALS_PRIMARY = 7         # NUM_PALS_IN_PRIMARY_FRLG


def read_pal(path):
    lines = open(path).read().split('\n')
    n = int(lines[2])
    return [tuple(int(v) for v in lines[3 + i].split()) for i in range(n)]


class Tilesets:
    def __init__(self, primary_dir, secondary_dir):
        self.dirs = [os.path.join(REPO, primary_dir), os.path.join(REPO, secondary_dir)]
        pp = [read_pal(os.path.join(self.dirs[0], 'palettes', '%02d.pal' % i)) for i in range(16)]
        sp = [read_pal(os.path.join(self.dirs[1], 'palettes', '%02d.pal' % i)) for i in range(16)]
        self.pals = pp[:NUM_PALS_PRIMARY] + sp[NUM_PALS_PRIMARY:]
        self.tiles = self._load_tiles(self.dirs[0]) , self._load_tiles(self.dirs[1])
        self.metatiles = self._load_mt(self.dirs[0]), self._load_mt(self.dirs[1])
        self.attrs = self._load_attr(self.dirs[0]), self._load_attr(self.dirs[1])
        self._cache = {}

    @staticmethod
    def _load_tiles(d):
        im = Image.open(os.path.join(d, 'tiles.png'))
        w, h = im.size
        px = im.load()
        tiles = []
        for ty in range(h // 8):
            for tx in range(w // 8):
                # 4bpp: index & 0xF (some pngs are 8bpp-indexed with >16 entries)
                tiles.append([[px[tx * 8 + x, ty * 8 + y] & 0xF for x in range(8)] for y in range(8)])
        return tiles

    @staticmethod
    def _load_mt(d):
        data = open(os.path.join(d, 'metatiles.bin'), 'rb').read()
        v = struct.unpack('<%dH' % (len(data) // 2), data)
        return [v[i:i + 8] for i in range(0, len(v), 8)]

    @staticmethod
    def _load_attr(d):
        data = open(os.path.join(d, 'metatile_attributes.bin'), 'rb').read()
        return list(struct.unpack('<%dI' % (len(data) // 4), data))

    def num_metatiles(self):
        return len(self.metatiles[0]), len(self.metatiles[1])

    def attr(self, mid):
        if mid < NUM_METATILES_PRIMARY:
            return self.attrs[0][mid] if mid < len(self.attrs[0]) else None
        i = mid - NUM_METATILES_PRIMARY
        return self.attrs[1][i] if i < len(self.attrs[1]) else None

    def _tile(self, idx):
        if idx < NUM_TILES_PRIMARY:
            t = self.tiles[0]
        else:
            t = self.tiles[1]; idx -= NUM_TILES_PRIMARY
        return t[idx] if idx < len(t) else None

    def metatile_image(self, mid):
        if mid in self._cache:
            return self._cache[mid]
        if mid < NUM_METATILES_PRIMARY:
            mts = self.metatiles[0]; i = mid
        else:
            mts = self.metatiles[1]; i = mid - NUM_METATILES_PRIMARY
        img = Image.new('RGB', (16, 16), self.pals[0][0])
        if i < len(mts):
            px = img.load()
            for layer in range(2):
                for q in range(4):
                    e = mts[i][layer * 4 + q]
                    tidx = e & 0x3FF; hf = (e >> 10) & 1; vf = (e >> 11) & 1; pal = (e >> 12) & 0xF
                    tile = self._tile(tidx)
                    if tile is None:
                        continue
                    ox = (q & 1) * 8; oy = (q >> 1) * 8
                    for y in range(8):
                        for x in range(8):
                            c = tile[7 - y if vf else y][7 - x if hf else x]
                            if c == 0 and not (layer == 0 and q >= 0 and False):
                                continue
                            px[ox + x, oy + y] = self.pals[pal][c]
        else:
            ImageDraw.Draw(img).rectangle([0, 0, 15, 15], outline=(255, 0, 255))
        self._cache[mid] = img
        return img


def read_blocks(path, w, h):
    data = open(path, 'rb').read()
    v = struct.unpack('<%dH' % (len(data) // 2), data)
    assert len(v) == w * h, (len(v), w, h)
    return [list(v[r * w:(r + 1) * w]) for r in range(h)]


def render_blocks(ts, blocks, scale=1):
    h = len(blocks); w = len(blocks[0])
    img = Image.new('RGB', (w * 16, h * 16))
    for y in range(h):
        for x in range(w):
            img.paste(ts.metatile_image(blocks[y][x] & 0x3FF), (x * 16, y * 16))
    if scale != 1:
        img = img.resize((img.width * scale, img.height * scale), Image.NEAREST)
    return img


def contact_sheet(ts, ids, cols=16, scale=2):
    from PIL import ImageFont
    rows = (len(ids) + cols - 1) // cols
    cw = 16 * scale + 4; ch = 16 * scale + 12
    img = Image.new('RGB', (cols * cw, rows * ch), (40, 40, 40))
    d = ImageDraw.Draw(img)
    for n, mid in enumerate(ids):
        x = (n % cols) * cw; y = (n // cols) * ch
        img.paste(ts.metatile_image(mid).resize((16 * scale, 16 * scale), Image.NEAREST), (x + 2, y + 10))
        d.text((x + 2, y), '%X' % mid, fill=(255, 255, 0))
    return img
