#!/usr/bin/env python3
"""Render map dirs side by side into one PNG (warps marked).  usage: render_list.py OUT.png Map [Map ...]"""
import json, os, sys
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from render_maps import render, map_json
out, names = sys.argv[1], sys.argv[2:]
ims = []
for n in names:
    im, l = render(n); d = ImageDraw.Draw(im)
    for i, w in enumerate(map_json(n)['warp_events'] or []):
        d.rectangle([w['x'] * 16, w['y'] * 16, w['x'] * 16 + 15, w['y'] * 16 + 15], outline=(255, 0, 255))
        d.text((w['x'] * 16 + 3, w['y'] * 16 + 2), str(i), fill=(255, 0, 255))
    ims.append((n, im))
W = sum(im.width for _, im in ims) + 16 * (len(ims) + 1); H = max(im.height for _, im in ims) + 40
c = Image.new('RGB', (W, H), 'white'); x = 16; d = ImageDraw.Draw(c)
for n, im in ims:
    c.paste(im, (x, 28)); d.text((x, 8), n, fill='black'); x += im.width + 16
c.save(out); print(out, c.size)
