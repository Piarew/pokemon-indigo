"""Metatile families in gTileset_General_Frlg, derived from the art (pixel colours)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'cherrygrove'))
from fr_render import Tilesets
from tsdir import tileset_dir

ROCK = {(222, 197, 164), (189, 148, 139), (148, 106, 106), (123, 74, 74), (238, 213, 197), (90, 57, 65)}
GRASS = {(115, 205, 164), (139, 222, 189), (65, 180, 139), (164, 230, 197)}
SAND = {(238, 230, 139), (222, 197, 139), (213, 189, 106)}
JUMP = {0x38, 0x39, 0x3A, 0x3B}

_ts = None
def ts():
    global _ts
    if _ts is None:
        _ts = Tilesets(tileset_dir('gTileset_General_Frlg', True), tileset_dir('gTileset_PewterCity'))
    return _ts

def fractions(m):
    px = list(ts().metatile_image(m).getdata())
    n = len(px)
    return (sum(p in ROCK for p in px) / n, sum(p in GRASS for p in px) / n, sum(p in SAND for p in px) / n)

def mountain_family():
    """rock-art metatiles of the cliff/mountain block 0x068-0x0BB (+cave door), excluding ledges"""
    fam, grassy = set(), set()
    for m in range(0x068, 0x0BC):
        if (ts().attr(m) & 0x1FF) in JUMP:
            continue
        r, g, s = fractions(m)
        if r >= 0.2 or m == 0x0A9:
            fam.add(m)
            if s <= g or s < 0.05:
                grassy.add(m)
    return fam, grassy

if __name__ == '__main__':
    f, g = mountain_family()
    print('family', ' '.join('%03X' % m for m in sorted(f)))
    print('grass-variant', ' '.join('%03X' % m for m in sorted(g)))
