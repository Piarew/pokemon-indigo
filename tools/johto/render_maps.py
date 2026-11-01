#!/usr/bin/env python3
"""Render converted Johto layouts with the real FRLG metatiles, a side-by-side comparison with
the GSC source image, and an overview of the connected maps.
Usage: python3 tools/johto/render_maps.py OUTDIR [MapName ...]   (default: all maps)"""
import json, os, sys
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', 'cherrygrove'))
from fr_render import Tilesets, read_blocks, render_blocks, REPO
from tsdir import tileset_dir
from johto_convert import MAPS, SRC_DIR, snake_upper

LAYOUTS = {l['id']: l for l in json.load(open(os.path.join(REPO, 'data/layouts/layouts.json')))['layouts']}

def map_json(name):
    return json.load(open(os.path.join(REPO, 'data/maps', name, 'map.json')))

def render(name):
    l = LAYOUTS[map_json(name)['layout']]
    ts = Tilesets(tileset_dir(l['primary_tileset'], True), tileset_dir(l['secondary_tileset']))
    b = read_blocks(os.path.join(REPO, l['blockdata_filepath']), l['width'], l['height'])
    return render_blocks(ts, b, 1).convert('RGB'), l

def compare(name, outdir):
    img, l = render(name)
    stem = snake_upper(name).lower()
    img.save(os.path.join(outdir, stem + '_preview.png'))
    cfg = MAPS.get(name)
    g = Image.open(os.path.join(SRC_DIR, cfg['src'])).convert('RGB')
    pad, lab = 16, 24
    vertical = g.width > g.height * 1.5
    if vertical:
        c = Image.new('RGB', (max(g.width, img.width) + 2 * pad, g.height + img.height + 2 * lab + 3 * pad), 'white')
        c.paste(g, (pad, lab)); c.paste(img, (pad, g.height + 2 * lab + pad))
        pos2 = (pad, g.height + lab + pad + 6)
    else:
        c = Image.new('RGB', (g.width + img.width + pad * 3, max(g.height, img.height) + lab + pad), 'white')
        c.paste(g, (pad, lab)); c.paste(img, (g.width + pad * 2, lab))
        pos2 = (g.width + pad * 2, 6)
    d = ImageDraw.Draw(c)
    d.text((pad, 6), 'GSC/Crystal source: %s' % cfg['url'], fill='black')
    d.text(pos2, 'FRLG translation: %dx%d metatiles, General_Frlg + %s' % (
        l['width'], l['height'], l['secondary_tileset'].replace('gTileset_', '')), fill='black')
    c.save(os.path.join(outdir, stem + '_compare.png'))
    return img

def overview(names, outdir, scale=0.5):
    """place maps by their connections (BFS), one picture per connected component"""
    imgs = {n: render(n)[0] for n in names}
    ids = {map_json(n)['id']: n for n in names}
    placed_all, comps = set(), []
    for start in names:
        if start in placed_all:
            continue
        pos = {start: (0, 0)}; todo = [start]
        while todo:
            n = todo.pop()
            for c in map_json(n)['connections'] or []:
                m = ids.get(c['map'])
                if not m or m in pos:
                    continue
                x, y = pos[n]; w, h = imgs[n].width // 16, imgs[n].height // 16
                mw, mh = imgs[m].width // 16, imgs[m].height // 16
                o = c['offset']
                pos[m] = {'up': (x + o, y - mh), 'down': (x + o, y + h),
                          'left': (x - mw, y + o), 'right': (x + w, y + o)}[c['direction']]
                todo.append(m)
        placed_all |= set(pos); comps.append(pos)
    pics = []
    for pos in comps:
        x0 = min(p[0] for p in pos.values()); y0 = min(p[1] for p in pos.values())
        x1 = max(p[0] + imgs[n].width // 16 for n, p in pos.items())
        y1 = max(p[1] + imgs[n].height // 16 for n, p in pos.items())
        pic = Image.new('RGB', ((x1 - x0) * 16, (y1 - y0) * 16), (30, 30, 30))
        d = ImageDraw.Draw(pic)
        for n, (x, y) in pos.items():
            pic.paste(imgs[n], ((x - x0) * 16, (y - y0) * 16))
        for n, (x, y) in pos.items():
            d.rectangle([(x - x0) * 16, (y - y0) * 16, (x - x0) * 16 + imgs[n].width - 1,
                         (y - y0) * 16 + imgs[n].height - 1], outline=(255, 0, 255))
            d.text(((x - x0) * 16 + 4, (y - y0) * 16 + 4), n, fill=(255, 255, 0))
        pics.append(pic)
    W = sum(p.width for p in pics) + 32 * (len(pics) + 1); H = max(p.height for p in pics) + 64
    o = Image.new('RGB', (W, H), 'white'); x = 32
    for p in pics:
        o.paste(p, (x, 32)); x += p.width + 32
    ImageDraw.Draw(o).text((32, 10), 'FRLG Johto spike overview (maps placed by their map.json connections)', fill='black')
    o = o.resize((int(o.width * scale), int(o.height * scale)), Image.LANCZOS)
    o.save(os.path.join(outdir, 'johto_overview.png'))
    return o.size

if __name__ == '__main__':
    outdir = sys.argv[1]
    names = sys.argv[2:] or list(MAPS)
    for n in names:
        compare(n, outdir); print('rendered', n)
    if not sys.argv[2:]:
        print('overview', overview(['CherrygroveCity'] + list(MAPS), outdir))
