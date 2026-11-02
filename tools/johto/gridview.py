"""Render an FRLG layout with a coordinate grid (dev helper)."""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'cherrygrove'))
from fr_render import Tilesets, read_blocks, render_blocks, REPO
from tsdir import tileset_dir
from PIL import ImageDraw

def layout(name):
    for l in json.load(open(os.path.join(REPO, 'data/layouts/layouts.json')))['layouts']:
        if l.get('name') == name or l.get('id') == name:
            return l

def render(name, out, x0=0, y0=0, x1=None, y1=None, scale=2):
    l = layout(name)
    ts = Tilesets(tileset_dir(l['primary_tileset'], True), tileset_dir(l['secondary_tileset']))
    b = read_blocks(os.path.join(REPO, l['blockdata_filepath']), l['width'], l['height'])
    x1 = x1 or l['width']; y1 = y1 or l['height']
    b = [r[x0:x1] for r in b[y0:y1]]
    im = render_blocks(ts, b, scale)
    d = ImageDraw.Draw(im); s = 16 * scale
    for x in range(x1 - x0):
        d.line([(x * s, 0), (x * s, im.size[1])], fill=(0, 0, 0))
        d.text((x * s + 2, 1), str(x + x0), fill=(255, 0, 0))
    for y in range(y1 - y0):
        d.line([(0, y * s), (im.size[0], y * s)], fill=(0, 0, 0))
        d.text((1, y * s + 10), str(y + y0), fill=(0, 0, 255))
    im.save(out)

if __name__ == '__main__':
    a = sys.argv[1:]
    render(a[0], a[1], *map(int, a[2:]))
