#!/usr/bin/env python3
"""West blocks: the player can no longer leave the Indigo region westward through Violet City or Mahogany Town.

Three choke points, each closed on the ROUTE map just outside the town with existing General_Frlg metatiles
(collision 1), plus sign bg_events on both faces of the barrier (the Seafoam ice-wall style).  No town map, no
connection and no warp is edited: every connection stays mirrored and every warp pair stays intact, so there are no
one-sided links; the far side is simply unreachable on foot/surf.

  ROUTE36  (Violet City west exit -> Route 37/Ecruteak, Route 35/Goldenrod, National Park, Ruins of Alph gate)
           tree wall x56-57 y5-10: the 2-wide path corridor x56-57 y6-10 is planted with the route's own tree
           metatiles (0x01E/0x01F even rows, 0x016/0x017 odd rows = forest-edge tree halves; (56,5) 0x024 -> 0x014 so
           the canopy joins the tree line above).  Violet side keeps the 2-cell stub x58-59 y7-10.
  ROUTE42  (Mahogany Town west exit -> Mt. Mortar x3 entrances, Ecruteak City)
           rockslide x56-57 y4-7: the 4-row sand corridor below the cliff is filled with boulder metatile 0x0AF
           (rock on sand).  Mahogany side keeps the stub x58-59 y4-7.
  ROUTE32  (Violet City south exit -> Union Cave -> Route 33/Azalea, the only westward way off Route 32; its down
           connection to Route 33 is solid on both sides)
           rockfall x10-11 y77-78 in the 2-wide corridor between the Route 32 Pokemon Center and the Union Cave mouth
           (boulder 0x0AF).  The Pokemon Center, the whole north half of Route 32 and its sea edge (Violet southeast
           sea route) stay open; the Union Cave mouth (6,79) becomes a dead-end pocket for anyone arriving from inside.

Idempotent: every barrier cell carries its expected original word; a cell holding the original is replaced, a cell
already holding the barrier is left alone, anything else aborts (the generated layout changed - revisit the design).

Test (tilereach.py, an over-approximating BFS over every map, warp and connection, ignoring elevation/ledges/HM
obstacles/objects): from Pallet Town, Violet City and Mahogany Town, no SEVERED map is reachable and every KEEP map
is; with the barriers removed (all three, and each one alone) the west IS reachable, proving the test sees each
route and that each barrier is necessary.  Also: no script outside the severed area warps into it.
Usage: west_blocks.py [--preview DIR]"""
import json, os, re, struct, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
import tilereach

SOLID = 0x400                                    # collision 1, elevation 0 (as the surrounding tree/rock cells)
BARRIERS = {
    'Route36': {
        'what': 'tree wall', 'cells': {
            # (x, y): (original word, new metatile)
            (56, 5): (0x0424, 0x014),
            (56, 6): (0x3011, 0x01E),
            (56, 7): (0x3009, 0x016), (57, 7): (0x3010, 0x017),
            (56, 8): (0x30D4, 0x01E), (57, 8): (0x30D4, 0x01F),
            (56, 9): (0x30E4, 0x016), (57, 9): (0x30E4, 0x017),
            (56, 10): (0x3010, 0x01E), (57, 10): (0x3009, 0x01F)},
        'signs': [(57, y) for y in (7, 8, 9, 10)] + [(56, y) for y in (6, 7, 8, 9, 10)],
        'label': 'TreeWall',
        'text': ['The trees have grown together', 'into a thick wall.', 'There is no way west from here.']},
    'Route42': {
        'what': 'rockslide', 'cells': {(x, y): (o, 0x0AF) for x in (56, 57)
                                       for y, o in ((4, 0x30D4), (5, 0x30DC), (6, 0x30DC), (7, 0x30E4))},
        'signs': [(57, y) for y in (4, 5, 6, 7)] + [(56, y) for y in (4, 5, 6, 7)],
        'label': 'Rockslide',
        'text': ['A rockslide has buried the', 'road west to ECRUTEAK CITY.', 'It can\'t be crossed.']},
    'Route32': {
        'what': 'rockfall', 'cells': {(10, 77): (0x30DB, 0x0AF), (11, 77): (0x30DD, 0x0AF),
                                      (10, 78): (0x30DB, 0x0AF), (11, 78): (0x30DD, 0x0AF)},
        'signs': [(10, 77), (11, 77), (10, 78), (11, 78)],
        'label': 'Rockfall',
        'text': ['Fallen rocks have buried the', 'path to UNION CAVE.', 'There is no way through.']},
}
# Maps that must become unreachable (everything west of the three barriers).
SEVERED = sorted('''
AzaleaTown AzaleaTown_CharcoalKiln AzaleaTown_Gym AzaleaTown_KurtsHouse AzaleaTown_Mart AzaleaTown_PokemonCenter_1F
AzaleaTown_PokemonCenter_2F BurnedTower1F BurnedTowerB1F CianwoodCity CianwoodCity_Gym CianwoodCity_LugiaSpeechHouse
CianwoodCity_ManiasHouse CianwoodCity_Pharmacy CianwoodCity_PhotoStudio CianwoodCity_PokeSeersHouse
CianwoodCity_PokemonCenter_1F CianwoodCity_PokemonCenter_2F EcruteakCity EcruteakCity_DanceTheater EcruteakCity_Gym
EcruteakCity_House1 EcruteakCity_House2 EcruteakCity_House3 EcruteakCity_House4 EcruteakCity_ItemfinderHouse
EcruteakCity_LugiaSpeechHouse EcruteakCity_Mart EcruteakCity_PokemonCenter_1F EcruteakCity_PokemonCenter_2F
EcruteakCity_TinTowerEntrance EcruteakCity_WiseTriosHouse GoldenrodCity GoldenrodCity_BikeShop
GoldenrodCity_BillsFamilysHouse GoldenrodCity_DeptStore1F GoldenrodCity_FlowerShop GoldenrodCity_GameCorner
GoldenrodCity_Gym GoldenrodCity_HappinessRater GoldenrodCity_MagnetTrainStation GoldenrodCity_NameRater
GoldenrodCity_PPSpeechHouse GoldenrodCity_PokemonCenter_1F GoldenrodCity_PokemonCenter_2F GoldenrodCity_RadioTower1F
IlexForest MountMortar1FInside MountMortar1FOutside MountMortar2FInside MountMortarB1F OlivineCity OlivineCity_Cafe
OlivineCity_GoodRodHouse OlivineCity_Gym OlivineCity_Mart OlivineCity_PokemonCenter_1F OlivineCity_PokemonCenter_2F
OlivineCity_PunishmentSpeechHouse OlivineCity_TimsHouse Route33 Route34 Route34_DayCare Route35
Route35_NationalParkGate Route36_NationalParkGate Route36_RuinsOfAlphGate Route37 Route38 Route39 Route39_Barn
Route39_Farmhouse Route40 Route41 SlowpokeWellB1F SlowpokeWellB2F TinTower1F TinTowerRoof UnionCave1F UnionCaveB1F
UnionCaveB2F'''.split())
# Severed maps that were already tile-unreachable before the blocks (door only reachable from Route36's bottom edge
# x46-49, outside Route35's connection span) - excluded from the 'unblocked world reaches the west' sanity check.
ALREADY_UNREACHABLE = ['Route36_RuinsOfAlphGate']
# Partly severed (east stub / north half stays): reachable, but specific cells must not be.
PARTIAL = {'Route36': [(55, 8), (47, 16), (15, 9)], 'Route42': [(55, 5), (46, 7), (28, 9), (10, 5)],
           'Route32': [(10, 79), (6, 79)]}
# Must stay reachable from every start.
KEEP = sorted('''
PalletTown_Frlg VioletCity MahoganyTown BlackthornCity CherrygroveCity NewBarkTown MortarTrail MortarTrail_RestHouse
Route26 Route27 Route29 Route30 Route31 Route32 Route32_PokemonCenter_1F Route36 Route42 Route43 Route43_TollGate
Route44 Route45 Route46 LakeOfRage DarkCaveVioletEntrance DarkCaveBlackthornEntrance IcePath_1F SproutTower1F
SeaRouteVioletWest SeaRouteVioletCentral SeaRouteVioletEast CinnabarIsland_Frlg Route21_South_Frlg
VioletCity_PokemonCenter_1F MahoganyTown_PokemonCenter_1F DiglettsCave_BlackthornEntrance CyclingRoadWest'''.split())
STARTS = {'Pallet Town': tilereach.PALLET, 'Violet City': ('MAP_VIOLET_CITY', 32, 26),
          'Mahogany Town': ('MAP_MAHOGANY_TOWN', 15, 14)}
MARK = '@ ---- West block (indigo custom; see tools/johto/west_blocks.py) ----'

def layout(name):
    m = json.load(open(os.path.join(REPO, 'data/maps', name, 'map.json')))
    l = {l['id']: l for l in json.load(open(os.path.join(REPO, 'data/layouts/layouts.json')))['layouts'] if 'id' in l}[m['layout']]
    return m, l

def blocks(name):
    m, l = layout(name)
    raw = open(os.path.join(REPO, l['blockdata_filepath']), 'rb').read()
    return l, list(struct.unpack('<%dH' % (l['width'] * l['height']), raw))

def build():
    """-> {map: (blockdata path, pristine bytes, barrier bytes)} from the on-disk layout (idempotent)."""
    out = {}
    for name, b in BARRIERS.items():
        l, v = blocks(name); w = l['width']
        pristine, edited = list(v), list(v)
        for (x, y), (orig, mt) in b['cells'].items():
            cur, new = v[y * w + x], SOLID | mt
            if cur not in (orig, new):
                sys.exit('west_blocks: %s (%d,%d) is 0x%04X, expected original 0x%04X or barrier 0x%04X - layout changed'
                         % (name, x, y, cur, orig, new))
            pristine[y * w + x] = orig; edited[y * w + x] = new
        pk = lambda a: struct.pack('<%dH' % len(a), *a)
        out[name] = (l['blockdata_filepath'], pk(pristine), pk(edited))
    return out

def write_events(name, b):
    p = os.path.join(REPO, 'data/maps', name, 'map.json')
    j = json.load(open(p))
    script = '%s_EventScript_%sSign' % (name, b['label'])
    bg = [e for e in j.get('bg_events') or [] if e.get('script') != script]
    taken = {(e['x'], e['y']) for e in bg}
    assert not taken & set(b['signs']), (name, taken & set(b['signs']))
    bg += [{'type': 'sign', 'x': x, 'y': y, 'elevation': 0, 'player_facing_dir': 'BG_EVENT_PLAYER_FACING_ANY',
            'script': script} for x, y in b['signs']]
    j['bg_events'] = bg
    open(p, 'w').write(json.dumps(j, indent=2) + '\n')
    sp = os.path.join(REPO, 'data/maps', name, 'scripts.inc')
    sc = open(sp).read()
    if MARK in sc:
        sc = sc[:sc.index(MARK)]
    txt = '%s_Text_%s' % (name, b['label'])
    lines = b['text']
    body = '\t.string "%s\\n"\n' % lines[0]
    for i, s in enumerate(lines[1:], 1):
        body += '\t.string "%s%s"\n' % (s, '$' if i == len(lines) - 1 else '\\p' if i == 1 and len(lines) > 2 else '\\n')
    sc = sc.rstrip('\n') + '\n\n' + MARK + '\n%s::\n\tmsgbox %s, MSGBOX_SIGN\n\tend\n\n%s:\n%s' % (script, txt, txt, body)
    open(sp, 'w').write(sc)

def script_warps(world, dirs, severed_ids):
    """Scripted warps (warp*, setwarp, setdynamicwarp...) into a severed map from a script outside the severed area."""
    sev_dirs = {dirs[i] for i in severed_ids}
    hits = []
    files = glob.glob(os.path.join(REPO, 'data/maps/*/scripts.inc')) + glob.glob(os.path.join(REPO, 'data/scripts/**/*.inc'), recursive=True)
    pat = re.compile(r'^\s*(warp\w*|setwarp|setdynamicwarp|setescapewarp|setholewarp|setdivewarp)\s+(MAP_\w+)', re.M)
    for f in files:
        owner = os.path.basename(os.path.dirname(f)) if '/data/maps/' in f else None
        if owner in sev_dirs:
            continue
        for cmd, mp in pat.findall(open(f, errors='replace').read()):
            if mp in severed_ids:
                hits.append('%s: %s %s' % (os.path.relpath(f, REPO), cmd, mp))
    return hits

def test(world, dirs, built):
    ids = {d: i for i, d in dirs.items()}
    sev = {ids[n] for n in SEVERED}
    edited = {p: e for p, _, e in built.values()}
    pristine = {p: o for p, o, _ in built.values()}
    res = {}
    for label, s in STARTS.items():
        r = tilereach.reach(world, [s], edited)
        leak = sorted(dirs[i] for i in sev if i in r)
        assert not leak, 'west block leaks from %s: %s' % (label, leak)
        lost = [n for n in KEEP if ids[n] not in r]
        assert not lost, 'west block cut off %s from %s' % (lost, label)
        for n, cells in PARTIAL.items():
            bad = [c for c in cells if c in r[ids[n]]]
            assert not bad, 'west block leaks on %s from %s: %s' % (n, label, bad)
        res[label] = r
    a, b = res['Pallet Town'], res['Violet City']
    assert set(a) == set(b) == set(res['Mahogany Town']), 'starts reach different map sets'
    # sanity: the west is reachable without the barriers, and through each barrier alone
    r0 = tilereach.reach(world, [STARTS['Pallet Town']], pristine)
    pre = {ids[n] for n in ALREADY_UNREACHABLE}
    assert not pre & set(r0), 'ALREADY_UNREACHABLE is stale: %s' % sorted(dirs[i] for i in pre & set(r0))
    assert sev - pre <= set(r0), 'test sanity: unblocked world should reach %s' % sorted(dirs[i] for i in sev - pre - set(r0))
    alone = {}
    for name, (p, o, e) in built.items():
        ov = dict(edited); ov[p] = o
        r1 = tilereach.reach(world, [STARTS['Pallet Town']], ov)
        alone[name] = len([i for i in sev if i in r1])
        assert alone[name], 'barrier %s is redundant: removing it alone reopens nothing' % name
    warps = script_warps(world, dirs, sev)
    assert not warps, 'scripted warps into the severed west: %s' % warps
    return res, r0, alone

def preview(outdir, built):
    sys.path.insert(0, os.path.join(HERE, '..', 'cherrygrove'))
    from fr_render import Tilesets, render_blocks
    from tsdir import tileset_dir
    from PIL import Image, ImageDraw
    os.makedirs(outdir, exist_ok=True)
    for name, b in BARRIERS.items():
        m, l = layout(name); w, h = l['width'], l['height']
        ts = Tilesets(tileset_dir(l['primary_tileset'], True), tileset_dir(l['secondary_tileset']))
        xs = [x for x, _ in b['cells']]; ys = [y for _, y in b['cells']]
        x0, x1 = max(0, min(xs) - 9), min(w, max(xs) + 10); y0, y1 = max(0, min(ys) - 6), min(h, max(ys) + 7)
        _, o, e = built[name]
        imgs = []
        for raw in (o, e):
            v = struct.unpack('<%dH' % (w * h), raw)
            rows = [[v[y * w + x] & 0x3FF for x in range(x0, x1)] for y in range(y0, y1)]
            im = render_blocks(ts, rows, 3).convert('RGB'); d = ImageDraw.Draw(im); s = 48
            for (x, y) in b['cells']:
                d.rectangle([(x - x0) * s, (y - y0) * s, (x - x0 + 1) * s - 1, (y - y0 + 1) * s - 1], outline=(255, 0, 0))
            for (x, y) in b['signs']:
                d.text(((x - x0) * s + 3, (y - y0) * s + 2), 'S', fill=(255, 255, 0))
            imgs.append(im)
        W, H = imgs[0].size
        c = Image.new('RGB', (W * 2 + 30, H + 40), 'white'); d = ImageDraw.Draw(c)
        c.paste(imgs[0], (10, 30)); c.paste(imgs[1], (W + 20, 30))
        d.text((10, 8), '%s before (x%d-%d, y%d-%d)' % (name, x0, x1 - 1, y0, y1 - 1), fill='black')
        d.text((W + 20, 8), '%s after: %s (red = barrier cells, S = sign)' % (name, b['what']), fill='black')
        c.save(os.path.join(outdir, 'west_block_%s.png' % name.lower()))

def main():
    built = build()
    world, dirs = tilereach.load_world()
    res, r0, alone = test(world, dirs, built)          # tests run on in-memory layouts before anything is written
    for name, (p, _, e) in built.items():
        open(os.path.join(REPO, p), 'wb').write(e)
        write_events(name, BARRIERS[name])
    if '--preview' in sys.argv:
        preview(sys.argv[sys.argv.index('--preview') + 1], built)
    sev = len(SEVERED)
    print('west_blocks: Route36 tree wall x56-57 y5-10, Route42 rockslide x56-57 y4-7, Route32 rockfall x10-11 y77-78; '
          'reach test from %s: 0/%d severed maps reachable, %d/%d keep maps reachable, %d maps total '
          '(unblocked: %d; reopened by removing one barrier: %s) -> PASS'
          % ('/'.join(STARTS), sev, len(KEEP), len(KEEP), len(res['Pallet Town']), len(r0),
             ', '.join('%s %d' % kv for kv in alone.items())))

if __name__ == '__main__':
    main()
