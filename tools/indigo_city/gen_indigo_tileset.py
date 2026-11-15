#!/usr/bin/env python3
"""Generate data/tilesets/secondary/indigo_city from saffron_city_frlg.

gTileset_IndigoCity reuses Saffron's tile art; only palettes and metatiles differ:
  * pal 11 (house roofs)   green  -> blue
  * pal 12 (house walls)   yellow -> pale blue
  * pal 8  (tower roof / doors) purple -> blue
  * pal 7  (unused in Saffron) = primary pal 5 with the tan gym roof ramp -> indigo.
    The gym roof metatiles (primary 0x141.. and Saffron 0x300..) are duplicated at
    the end of the secondary set with their pal-5 tiles repointed to pal 7.
    GYM_REMAP maps original metatile id -> Indigo copy; gen_indigo_city.py applies it.
Saffron's own tileset is not modified.  Run from the repo root.
"""
import colorsys, os, shutil, struct

SRC = 'data/tilesets/secondary/saffron_city_frlg'
DST = 'data/tilesets/secondary/indigo_city'
PRI = 'data/tilesets/primary/general_frlg'
NUM_PRI = 0x280
GYM_PAL_SRC, GYM_PAL = 5, 7
GYM_METATILES = [0x300, 0x301, 0x302, 0x303,
                 0x141, 0x142, 0x143, 0x149, 0x14A, 0x14B,
                 0x152, 0x153, 0x154]


def read_pal(path):
    lines = open(path).read().split('\n')
    return [tuple(map(int, l.split())) for l in lines[3:19]]


def write_pal(path, pal):
    with open(path, 'w', newline='\r\n') as f:
        f.write('JASC-PAL\n0100\n16\n' + ''.join('%d %d %d\n' % c for c in pal))


def hls(c, hue, sat=lambda s: s, light=lambda l: l):
    h, l, s = colorsys.rgb_to_hls(*[v / 255 for v in c])
    r, g, b = colorsys.hls_to_rgb(hue / 360, max(0, min(1, light(l))), max(0, min(1, sat(s))))
    return tuple(int(round(v * 255)) for v in (r, g, b))


def recolor(pal, idxs, fn):
    return [fn(c) if i in idxs else c for i, c in enumerate(pal)]


def palettes():
    pals = [read_pal('%s/palettes/%02d.pal' % (SRC, i)) for i in range(16)]
    pals[11] = recolor(pals[11], (10, 11, 12, 13, 14),
                       lambda c: hls(c, 214, lambda s: s * 1.9 + 0.1, lambda l: min(0.9, l * 1.05)))
    pals[12] = recolor(pals[12], (6, 7, 9, 10, 11),
                       lambda c: hls(c, 205, lambda s: s * 0.45, lambda l: min(0.95, l * 1.1)))
    pals[8] = recolor(pals[8], (7, 8, 9, 13, 14),
                      lambda c: hls(c, 214, lambda s: s * 1.2))
    gym = read_pal('%s/palettes/%02d.pal' % (PRI, GYM_PAL_SRC))
    # tan roof ramp 6..12 -> deep blue-violet (indigo), lightness compressed downward
    pals[GYM_PAL] = recolor(gym, (6, 7, 8, 9, 10, 11, 12),
                            lambda c: hls(c, 252, lambda s: 0.55, lambda l: 0.12 + l * 0.6))
    return pals


def metatile(blob, i):
    return list(struct.unpack_from('<8H', blob, i * 16))


def build():
    os.makedirs(DST + '/palettes', exist_ok=True)
    for i, p in enumerate(palettes()):
        write_pal('%s/palettes/%02d.pal' % (DST, i), p)
    smt = open(SRC + '/metatiles.bin', 'rb').read()
    sat = open(SRC + '/metatile_attributes.bin', 'rb').read()
    pmt = open(PRI + '/metatiles.bin', 'rb').read()
    pat = open(PRI + '/metatile_attributes.bin', 'rb').read()
    out_mt, out_at = bytearray(smt), bytearray(sat)
    remap = {}
    for mid in GYM_METATILES:
        if mid < NUM_PRI:
            tiles, attr = metatile(pmt, mid), pat[mid * 4:mid * 4 + 4]
        else:
            tiles, attr = metatile(smt, mid - NUM_PRI), sat[(mid - NUM_PRI) * 4:(mid - NUM_PRI) * 4 + 4]
        tiles = [(t & 0x0FFF) | (GYM_PAL << 12) if (t >> 12) == GYM_PAL_SRC else t for t in tiles]
        remap[mid] = NUM_PRI + len(out_mt) // 16
        out_mt += struct.pack('<8H', *tiles)
        out_at += attr
    assert len(out_mt) // 16 <= 0x400 - NUM_PRI
    open(DST + '/metatiles.bin', 'wb').write(out_mt)
    open(DST + '/metatile_attributes.bin', 'wb').write(out_at)
    return remap


GYM_REMAP = None


def gym_remap():
    """Deterministic remap without writing files (Saffron count + order)."""
    n = os.path.getsize(SRC + '/metatiles.bin') // 16
    return {mid: NUM_PRI + n + k for k, mid in enumerate(GYM_METATILES)}


if __name__ == '__main__':
    r = build()
    assert r == gym_remap()
    print('wrote', DST, 'gym remap:', ', '.join('%03X->%03X' % kv for kv in r.items()))
