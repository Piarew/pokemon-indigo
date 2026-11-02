#!/usr/bin/env python3
"""Cut every source image into 16x16 px cells and give each distinct cell a global id
(first appearance, files in the order below, row-major).  Writes $JOHTO_SRC/cells.json:
  files: image order, grids: {file: [[id,...],...]}, order: [file, cell x, cell y] of each id's first use.
Usage: python3 tools/johto/cells.py   (images downloaded into $JOHTO_SRC, default /workspace/johto_src;
source URLs are listed per map in johto_convert.MAPS)"""
import json, os
from PIL import Image
SRC_DIR = os.environ.get('JOHTO_SRC', '/workspace/johto_src')
FILES = ['Cherrygrove_City_GSC.png', 'Blackthorn_City_GSC.png', 'Johto_Route_29_GSC.png',
         'Johto_Route_30_GSC.png', 'Johto_Route_31_GSC.png', 'Johto_Route_32_GSC.png',
         'Johto_Route_42_GSC.png', 'Johto_Route_43_C.png', 'Johto_Route_44_GSC.png',
         'Johto_Route_45_GSC.png', 'Johto_Route_46_GSC.png', 'Mahogany_Town_GSC.png',
         'Violet_City_C.png', 'Ecruteak_City_C.png', 'New_Bark_Town_GSC.png',
         'Kanto_Route_26_GSC.png', 'Kanto_Route_27_GSC.png', 'Kanto_Route_28_GSC.png',
         'Mt._Silver_Exterior_GSC.png', 'Johto_Route_36_C.png', 'Johto_Route_37_GSC.png',
         # phase 6 (appended; ids above unchanged)
         'Lake_of_Rage_GSC.png', 'Johto_Route_33_GSC.png', 'Johto_Route_34_GSC.png', 'Johto_Route_35_GSC.png',
         'Johto_Route_38_GSC.png', 'Johto_Route_39_GSC.png', 'Azalea_Town_GSC.png', 'Ilex_Forest_GSC.png',
         'Goldenrod_City_C.png', 'Olivine_City_C.png', 'Cianwood_City_C.png']   # order fixes the ids used by johto_convert.CLASS -- do not reorder

def build(files):
    ids, order, grids = {}, [], {}
    for f in files:
        im = Image.open(os.path.join(SRC_DIR, f)).convert('RGB')
        g = []
        for py in range(0, im.height, 16):
            row = []
            for px in range(0, im.width, 16):
                key = im.crop((px, py, px + 16, py + 16)).tobytes()
                if key not in ids:
                    ids[key] = len(order); order.append([f, px // 16, py // 16])
                row.append(ids[key])
            g.append(row)
        grids[f] = g
    return {'files': files, 'grids': grids, 'order': order}

if __name__ == '__main__':
    out = os.path.join(SRC_DIR, 'cells.json')
    json.dump(build(FILES), open(out, 'w'))
    print('wrote', out)
