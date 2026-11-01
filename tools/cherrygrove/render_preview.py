#!/usr/bin/env python3
"""Render data/layouts/CherrygroveCity/map.bin with the real FRLG metatiles and a side-by-side
comparison with the GSC source image.
Usage: python3 tools/cherrygrove/render_preview.py [gsc.png] [preview.png] [compare.png]"""
import os, sys
from PIL import Image, ImageDraw
from fr_render import Tilesets, read_blocks, render_blocks, REPO

src = sys.argv[1] if len(sys.argv) > 1 else '/workspace/cherrygrove_gsc.png'
prev = sys.argv[2] if len(sys.argv) > 2 else '/workspace/cherrygrove_preview.png'
comp = sys.argv[3] if len(sys.argv) > 3 else '/workspace/cherrygrove_compare.png'
ts = Tilesets(os.path.join(REPO, 'data/tilesets/primary/general_frlg'),
              os.path.join(REPO, 'data/tilesets/secondary/viridian_city_frlg'))
blocks = read_blocks(os.path.join(REPO, 'data/layouts/CherrygroveCity/map.bin'), 40, 18)
img = render_blocks(ts, blocks, 1)
img.save(prev)
g = Image.open(src).convert('RGB')
pad, lab = 16, 24
c = Image.new('RGB', (g.width + img.width + pad * 3, max(g.height, img.height) + lab + pad), 'white')
c.paste(g, (pad, lab)); c.paste(img.convert('RGB'), (g.width + pad * 2, lab))
d = ImageDraw.Draw(c)
d.text((pad, 6), 'GSC Cherrygrove City (Bulbapedia archives, 640x288)', fill='black')
d.text((g.width + pad * 2, 6), 'FRLG translation: 40x18 metatiles, General_Frlg + ViridianCity', fill='black')
c.save(comp)
print(prev, img.size, comp, c.size)
