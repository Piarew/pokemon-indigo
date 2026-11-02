import os, re
from fr_render import REPO
def tileset_dir(sym, primary=False):
    base = re.sub(r'(?<!^)(?=[A-Z])', '_', sym.replace('gTileset_', '').replace('_Frlg', '')).lower()
    base = base.replace('_frlg', '')
    kind = 'primary' if primary else 'secondary'
    alt = re.sub(r'(?<=[a-z])(?=\d)', '_', base)
    for cand in (base + '_frlg', base, alt + '_frlg', alt):
        p = os.path.join(REPO, 'data/tilesets', kind, cand)
        if os.path.isdir(p):
            return p
    raise FileNotFoundError(sym)
