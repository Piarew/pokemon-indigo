#!/usr/bin/env python3
"""East blocks: Kanto's east half (Cerulean, Saffron, Lavender, Vermilion and everything behind them) is closed off.

The road blocks sit at the eastern edges of Celadon City and Fuchsia City, on the ROUTE map just outside each town,
built from the routes' own FireRed metatiles (collision 1) with sign bg_events on both faces of the barrier (the
style used by all Indigo road blocks, see west_blocks.py).  No town map, connection or warp is edited.

  ROUTE7    (Celadon City east exit -> Saffron City, Underground Path west entrance, Route 7 gate)
            tree wall x2-3 y1-5: the 4-row path corridor x0-3 y2-5 is planted with the route's own tree metatiles
            (0x01E/0x01F and 0x016/0x017 forest-edge tree halves; (2,1)/(3,1) 0x024/0x025 -> 0x014/0x015 so the canopy
            joins the tree line above).  Celadon side keeps the 2-cell stub x0-1 y2-5.
  ROUTE15   (Fuchsia City east exit -> Route 15 gate, Route 14/13/12, Lavender Town)
            rockslide x2-3 y10-12: the 3-row sand road between the tree line and the fence is filled with boulder
            metatile 0x0AF (rock on sand).  Fuchsia side keeps the stub x0-1 y10-12.
  DIGLETT'S CAVE B1F  (FireRed edit; Route 2 north entrance -> south entrance -> Route 11 / Vermilion City)
            cave-in at x80 y71-72, the 2-high neck just before the south-entrance ladder (82,71): DiglettsCave rubble
            metatile 0x283 (the cave's own rock piles).  The north entrance, the whole tunnel and the Johto tunnel to
            Blackthorn stay open; the ladder becomes a dead-end pocket (x81-82) for anyone arriving from Route 11.
  SEAGALLOP (FireRed edit, data/scripts/seagallop.inc; Sevii Islands -> Vermilion City harbor)
            EventScript_SailToDest - the single entry to DoSeagallopFerryScene - reroutes a Vermilion destination
            to Cinnabar Island with a "harbor closed" message, so the Sevii ferries cannot land the player in the east
            and nobody is stranded in the Sevii Islands.

Already closed before this script: Mt. Moon (mtmoon_cavein.py B1F rockfall) - re-checked here as load-bearing.

Idempotent: every barrier cell carries its expected original word; a cell holding the original is replaced, a cell
already holding the barrier is left alone, anything else aborts.  The sign scripts / seagallop guard are rewritten
behind a marker.

Test (tilereach.py over-approximating BFS, ignoring elevation/ledges/HM obstacles/objects): from Pallet Town,
Celadon City, Fuchsia City and Cinnabar Island, no SEVERED map (and no PARTIAL far-side cell) is reachable and every
KEEP map is; without the barriers the east IS reachable, and removing any single barrier (incl. the Mt. Moon cave-in)
reopens it.  Every check runs twice: plain tilereach (what gap_audit.py sees) and with every FRLG ledge cell
(MB_JUMP_*, stored with collision 1) opened both ways, since plain tilereach treats ledges as walls.  Also: no script outside the severed area warps into it, and the ferry guard is in place.
Usage: east_blocks.py [--preview DIR]"""
import os, re, struct, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
import tilereach
import west_blocks as wb
sys.path.insert(0, os.path.join(HERE, '..', 'cherrygrove'))
from tsdir import tileset_dir

SOLID = 0x400
BARRIERS = {
    'Route7_Frlg': {
        'what': 'tree wall', 'cells': {
            (2, 1): (0x0424, 0x014), (3, 1): (0x0425, 0x015),
            (2, 2): (0x3008, 0x01E), (3, 2): (0x3009, 0x01F),
            (2, 3): (0x3010, 0x016), (3, 3): (0x3011, 0x017),
            (2, 4): (0x3008, 0x01E), (3, 4): (0x3009, 0x01F),
            (2, 5): (0x300E, 0x016), (3, 5): (0x300F, 0x017)},
        'signs': [(2, y) for y in (2, 3, 4, 5)] + [(3, y) for y in (2, 3, 4, 5)],
        'label': 'TreeWall',
        'text': ['Trees have grown over the', 'road to SAFFRON CITY.', 'There is no way through.']},
    'Route15_Frlg': {
        'what': 'rockslide', 'cells': {(x, y): (o, 0x0AF) for x in (2, 3)
                                       for y, o in ((10, 0x30D4), (11, 0x30DC), (12, 0x30E4))},
        'signs': [(2, y) for y in (10, 11, 12)] + [(3, y) for y in (10, 11, 12)],
        'label': 'Rockslide',
        'text': ['A rockslide has buried the', 'road east to LAVENDER TOWN.', 'It can\'t be crossed.']},
    'DiglettsCave_B1F_Frlg': {
        'what': 'cave-in', 'cells': {(80, 71): (0x3281, 0x283), (80, 72): (0x3281, 0x283)},
        'signs': [(80, 71), (80, 72)],
        'label': 'CaveIn',
        'text': ['A cave-in has sealed the', 'tunnel to VERMILION CITY.', 'There is no way through.']},
}
SEVERED = sorted('''
CeruleanCave_1F_Frlg CeruleanCave_2F_Frlg CeruleanCave_B1F_Frlg CeruleanCity_BikeShop_Frlg CeruleanCity_Frlg
CeruleanCity_Gym_Frlg CeruleanCity_House1_Frlg CeruleanCity_House2_Frlg CeruleanCity_House3_Frlg
CeruleanCity_House4_Frlg CeruleanCity_House5_Frlg CeruleanCity_Mart_Frlg CeruleanCity_PokemonCenter_1F_Frlg
CeruleanCity_PokemonCenter_2F_Frlg DiglettsCave_SouthEntrance_Frlg LavenderTown_Frlg LavenderTown_House1_Frlg
LavenderTown_House2_Frlg LavenderTown_Mart_Frlg LavenderTown_PokemonCenter_1F_Frlg LavenderTown_PokemonCenter_2F_Frlg
LavenderTown_VolunteerPokemonHouse_Frlg PokemonTower_1F_Frlg PokemonTower_2F_Frlg PokemonTower_3F_Frlg
PokemonTower_4F_Frlg PokemonTower_5F_Frlg PokemonTower_6F_Frlg PokemonTower_7F_Frlg PowerPlant_Frlg RockTunnel_1F_Frlg
RockTunnel_B1F_Frlg Route10_Frlg Route10_PokemonCenter_1F_Frlg Route10_PokemonCenter_2F_Frlg
Route11_EastEntrance_1F_Frlg Route11_EastEntrance_2F_Frlg Route11_Frlg Route12_FishingHouse_Frlg Route12_Frlg
Route12_NorthEntrance_1F_Frlg Route12_NorthEntrance_2F_Frlg Route13_Frlg Route14_Frlg Route15_WestEntrance_1F_Frlg
Route15_WestEntrance_2F_Frlg Route24_Frlg Route25_Frlg Route25_SeaCottage_Frlg Route5_Frlg Route5_SouthEntrance_Frlg
Route6_Frlg Route6_NorthEntrance_Frlg Route7_EastEntrance_Frlg Route8_Frlg Route8_WestEntrance_Frlg Route9_Frlg
SSAnne_1F_Corridor_Frlg SSAnne_1F_Room1_Frlg SSAnne_1F_Room2_Frlg SSAnne_1F_Room3_Frlg SSAnne_1F_Room4_Frlg
SSAnne_1F_Room5_Frlg SSAnne_1F_Room6_Frlg SSAnne_1F_Room7_Frlg SSAnne_2F_Corridor_Frlg SSAnne_2F_Room1_Frlg
SSAnne_2F_Room2_Frlg SSAnne_2F_Room3_Frlg SSAnne_2F_Room4_Frlg SSAnne_2F_Room5_Frlg SSAnne_2F_Room6_Frlg
SSAnne_3F_Corridor_Frlg SSAnne_B1F_Corridor_Frlg SSAnne_B1F_Room1_Frlg SSAnne_B1F_Room2_Frlg SSAnne_B1F_Room3_Frlg
SSAnne_B1F_Room4_Frlg SSAnne_B1F_Room5_Frlg SSAnne_CaptainsOffice_Frlg SSAnne_Deck_Frlg SSAnne_Exterior_Frlg
SSAnne_Kitchen_Frlg SaffronCity_CopycatsHouse_1F_Frlg SaffronCity_CopycatsHouse_2F_Frlg SaffronCity_Dojo_Frlg
SaffronCity_Frlg SaffronCity_Gym_Frlg SaffronCity_House_Frlg SaffronCity_Mart_Frlg SaffronCity_MrPsychicsHouse_Frlg
SaffronCity_PokemonCenter_1F_Frlg SaffronCity_PokemonCenter_2F_Frlg SaffronCity_PokemonTrainerFanClub_Frlg
SilphCo_10F_Frlg SilphCo_11F_Frlg SilphCo_1F_Frlg SilphCo_2F_Frlg SilphCo_3F_Frlg SilphCo_4F_Frlg SilphCo_5F_Frlg
SilphCo_6F_Frlg SilphCo_7F_Frlg SilphCo_8F_Frlg SilphCo_9F_Frlg SilphCo_Elevator_Frlg UndergroundPath_EastEntrance_Frlg
UndergroundPath_EastWestTunnel_Frlg UndergroundPath_NorthEntrance_Frlg UndergroundPath_NorthSouthTunnel_Frlg
UndergroundPath_SouthEntrance_Frlg UndergroundPath_WestEntrance_Frlg VermilionCity_Frlg VermilionCity_Gym_Frlg
VermilionCity_House1_Frlg VermilionCity_House2_Frlg VermilionCity_House3_Frlg VermilionCity_Mart_Frlg
VermilionCity_PokemonCenter_1F_Frlg VermilionCity_PokemonCenter_2F_Frlg VermilionCity_PokemonFanClub_Frlg'''.split())
# Partly severed: the town-side stub stays reachable, the far side must not be.
PARTIAL = {'Route7_Frlg': [(4, 4), (4, 7), (7, 14), (15, 10), (20, 10)],
           'Route15_Frlg': [(4, 11), (9, 11), (16, 11), (40, 11)],
           'DiglettsCave_B1F_Frlg': [(81, 71), (81, 72), (82, 71)],
           'Route4_Frlg': [(60, 10)]}                     # Route 4 east of Mt. Moon (closed by mtmoon_cavein.py)
KEEP = sorted('''
PalletTown_Frlg Route1_Frlg ViridianCity_Frlg Route22_Frlg Route2_Frlg ViridianForest_Frlg PewterCity_Frlg Route3_Frlg
Route4_Frlg MtMoon_1F_Frlg MtMoon_B1F_Frlg DiglettsCave_NorthEntrance_Frlg DiglettsCave_B1F_Frlg
DiglettsCave_JohtoTunnel DiglettsCave_BlackthornEntrance BlackthornCity CeladonCity_Frlg CeladonCity_Gym_Frlg
CeladonCity_DepartmentStore_1F_Frlg CeladonCity_GameCorner_Frlg RocketHideout_B1F_Frlg Route7_Frlg Route16_Frlg
Route16_NorthEntrance_1F_Frlg Route16_House_Frlg CyclingRoadWest Route17_Frlg Route18_Frlg FuchsiaCity_Frlg
FuchsiaCity_PokemonCenter_1F_Frlg SafariZone_Center_Frlg Route15_Frlg Route19_Frlg Route20_Frlg SeafoamIslands_1F_Frlg
SeafoamIslands_B1F_Frlg SeafoamIslands_B2F_Frlg SeafoamIslands_B3F_Frlg SeafoamIslands_B4F_Frlg CinnabarIsland_Frlg
PokemonMansion_1F_Frlg Route21_North_Frlg Route21_South_Frlg VioletCity SeaRouteVioletEast'''.split())
STARTS = {'Pallet Town': tilereach.PALLET, 'Celadon City': ('MAP_CELADON_CITY', 28, 22),
          'Fuchsia City': ('MAP_FUCHSIA_CITY', 24, 8), 'Cinnabar Island': ('MAP_CINNABAR_ISLAND', 12, 1)}
MARK = '@ ---- East block (indigo custom; see tools/johto/east_blocks.py) ----'
MTMOON = ('data/layouts/MtMoon_B1F_Frlg/map.bin', 'ce5a58a6c4^')    # pre-cave-in revision of the Mt. Moon rockfall

SEAGALLOP = os.path.join(REPO, 'data/scripts/seagallop.inc')
GUARD = '\tcall_if_eq VAR_0x8006, SEAGALLOP_VERMILION_CITY, EventScript_IndigoVermilionHarborClosed  @ east block\n'
GUARD_BLOCK = MARK + '''
@ Vermilion City is behind the east blocks: any ferry bound for it puts in at Cinnabar Island instead.
EventScript_IndigoVermilionHarborClosed::
	msgbox Text_IndigoVermilionHarborClosed
	setvar VAR_0x8006, SEAGALLOP_CINNABAR_ISLAND
	return

Text_IndigoVermilionHarborClosed:
	.string "VERMILION harbor has been closed\\n"
	.string "since the rockslides.\\p"
	.string "This ship will put in at\\n"
	.string "CINNABAR ISLAND instead.$"
'''

def build():
    out = {}
    for name, b in BARRIERS.items():
        l, v = wb.blocks(name); w = l['width']
        pristine, edited = list(v), list(v)
        for (x, y), (orig, mt) in b['cells'].items():
            cur, new = v[y * w + x], SOLID | mt
            if cur not in (orig, new):
                sys.exit('east_blocks: %s (%d,%d) is 0x%04X, expected original 0x%04X or barrier 0x%04X - layout changed'
                         % (name, x, y, cur, orig, new))
            pristine[y * w + x] = orig; edited[y * w + x] = new
        pk = lambda a: struct.pack('<%dH' % len(a), *a)
        out[name] = (l['blockdata_filepath'], pk(pristine), pk(edited))
    return out

def write_events(name, b):
    """Same as west_blocks.write_events, behind this script's marker."""
    import json
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

def patch_seagallop(sc):
    """-> seagallop.inc with the Vermilion->Cinnabar guard (idempotent)."""
    sc = sc.replace(GUARD, '')
    if MARK in sc:
        sc = sc[:sc.index(MARK)].rstrip('\n') + '\n'
    label = 'EventScript_SailToDest::\n'
    assert sc.count(label) == 1, 'seagallop.inc: EventScript_SailToDest not found once'
    sc = sc.replace(label, label + GUARD)
    return sc.rstrip('\n') + '\n\n' + GUARD_BLOCK

def check_ferry(sc):
    """The guard must sit at the top of the one script that reaches the ferry scene."""
    import glob
    n = sum(len(re.findall(r'^\s*special\s+DoSeagallopFerryScene\b', open(f, errors='replace').read(), re.M))
            for f in glob.glob(os.path.join(REPO, 'data/**/*.inc'), recursive=True))
    assert n == 1, 'DoSeagallopFerryScene is called from %d scripts (expected only EventScript_SetSail)' % n
    head = sc[sc.index('EventScript_SailToDest::'):]
    assert head.split('\n')[1] + '\n' == GUARD, 'seagallop guard is not the first line of EventScript_SailToDest'
    assert re.search(r'EventScript_SetSail::(?:(?!::).)*special DoSeagallopFerryScene', sc, re.S)
    callers = re.findall(r'goto EventScript_SetSail', sc)
    assert len(callers) == 2, 'EventScript_SetSail reached from outside EventScript_SailToDest'

MB_NAMES = re.findall(r'^\s*(MB_\w+)', open(os.path.join(REPO, 'include/constants/metatile_behaviors.h')).read(), re.M)
JUMP = {i for i, n in enumerate(MB_NAMES) if n.startswith('MB_JUMP_')}

def _attrs(ts, primary):
    d = tileset_dir(ts, primary)
    a = open(os.path.join(d, 'metatile_attributes.bin'), 'rb').read()
    n = len(open(os.path.join(d, 'metatiles.bin'), 'rb').read()) // 16
    sz = len(a) // n                                    # FRLG: u32 (behavior & 0x1FF), Emerald: u16 (& 0xFF)
    return [struct.unpack_from('<I' if sz == 4 else '<H', a, i * sz)[0] & (0x1FF if sz == 4 else 0xFF) for i in range(n)]

def open_ledges(base):
    """FRLG ledge metatiles carry collision 1, so plain tilereach treats one-way ledges as walls (an UNDER-
    approximation there).  -> overrides with every MB_JUMP_* cell made passable in both directions (on top of
    `base`), restoring the over-approximation for ledges."""
    import json
    out, cache = {}, {}
    for l in json.load(open(os.path.join(REPO, 'data/layouts/layouts.json')))['layouts']:
        if 'id' not in l:
            continue
        p, k = l['blockdata_filepath'], (l['primary_tileset'], l['secondary_tileset'])
        if k not in cache:
            try:
                cache[k] = (_attrs(k[0], True), _attrs(k[1], False))
            except (OSError, ZeroDivisionError, KeyError):
                cache[k] = None
        raw = base.get(p) or open(os.path.join(REPO, p), 'rb').read()
        if cache[k] is None:
            if p in base:
                out[p] = raw
            continue
        pa, sa = cache[k]; npri = 0x280 if len(pa) > 512 else 0x200
        v = list(struct.unpack('<%dH' % (len(raw) // 2), raw)); ch = 0
        for i, x in enumerate(v):
            mt = x & 0x3FF
            b = pa[mt] if mt < npri else (sa[mt - npri] if mt - npri < len(sa) else None)
            if b in JUMP and x & 0xC00:
                v[i] = x & ~0xC00; ch += 1
        if ch or p in base:
            out[p] = struct.pack('<%dH' % len(v), *v)
    return out

def test(world, dirs, built):
    """Plain tilereach (as gap_audit.py) and ledges-open mode; both must hold."""
    out = None
    for ledges in (False, True):
        r = _test(world, dirs, built, ledges)
        out = out or r
        if ledges:
            out = (out[0], out[1], {k: '%s/%s' % (out[2][k], v) for k, v in r[2].items()})
    return out

def _test(world, dirs, built, ledges):
    L = open_ledges if ledges else (lambda o: o)
    mode = ' (ledges open)' if ledges else ''
    ids = {d: i for i, d in dirs.items()}
    sev = {ids[n] for n in SEVERED}
    edited = {p: e for p, _, e in built.values()}
    pristine = {p: o for p, o, _ in built.values()}
    E = L(edited)
    res = {}
    for label, s in STARTS.items():
        r = tilereach.reach(world, [s], E)
        leak = sorted(dirs[i] for i in sev if i in r)
        assert not leak, 'east block leaks from %s%s: %s' % (label, mode, leak)
        lost = [n for n in KEEP if ids[n] not in r]
        assert not lost, 'east block cut off %s from %s%s' % (lost, label, mode)
        for n, cells in PARTIAL.items():
            bad = [c for c in cells if c in r[ids[n]]]
            assert not bad, 'east block leaks on %s from %s%s: %s' % (n, label, mode, bad)
        res[label] = r
    assert len({frozenset(r) for r in res.values()}) == 1, 'starts reach different map sets'
    r0 = tilereach.reach(world, [STARTS['Pallet Town']], L(pristine))
    assert sev <= set(r0), 'test sanity: unblocked world should reach %s' % sorted(dirs[i] for i in sev - set(r0))
    alone = {}
    for name, (p, o, e) in built.items():
        ov = dict(edited); ov[p] = o
        r1 = tilereach.reach(world, [STARTS['Pallet Town']], L(ov))
        alone[name] = len([i for i in sev if i in r1])
        assert alone[name], 'barrier %s is redundant: removing it alone reopens nothing' % name
    try:                                             # the pre-existing Mt. Moon cave-in is part of the seal too
        raw = subprocess.run(['git', 'show', '%s:%s' % (MTMOON[1], MTMOON[0])], cwd=REPO, capture_output=True,
                             check=True).stdout
        ov = dict(edited); ov[MTMOON[0]] = raw
        r1 = tilereach.reach(world, [STARTS['Pallet Town']], L(ov))
        alone['MtMoon cave-in'] = len([i for i in sev if i in r1])
        # plain tilereach cannot see the Route 4 ledge drop to Cerulean, so the cave-in only matters with ledges open
        assert alone['MtMoon cave-in'] or not ledges, 'Mt. Moon cave-in no longer matters?'
    except subprocess.CalledProcessError:
        alone['MtMoon cave-in'] = '?'
    warps = wb.script_warps(world, dirs, sev) if not ledges else []
    assert not warps, 'scripted warps into the severed east: %s' % warps
    return res, r0, alone

def preview(outdir, built):
    sys.path.insert(0, os.path.join(HERE, '..', 'cherrygrove'))
    from fr_render import Tilesets, render_blocks
    from tsdir import tileset_dir
    from PIL import Image, ImageDraw
    os.makedirs(outdir, exist_ok=True)
    for name, b in BARRIERS.items():
        m, l = wb.layout(name); w, h = l['width'], l['height']
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
        c.save(os.path.join(outdir, 'east_block_%s.png' % name.lower()))

def main():
    built = build()
    world, dirs = tilereach.load_world()
    res, r0, alone = test(world, dirs, built)
    sg = patch_seagallop(open(SEAGALLOP).read())
    check_ferry(sg)
    for name, (p, _, e) in built.items():
        open(os.path.join(REPO, p), 'wb').write(e)
        write_events(name, BARRIERS[name])
    open(SEAGALLOP, 'w').write(sg)
    if '--preview' in sys.argv:
        preview(sys.argv[sys.argv.index('--preview') + 1], built)
    print('east_blocks: Route7 tree wall x2-3 y1-5, Route15 rockslide x2-3 y10-12, Diglett\'s Cave B1F cave-in x80 '
          'y71-72, Seagallop Vermilion->Cinnabar; reach test from %s: 0/%d severed maps reachable, %d/%d keep maps '
          'reachable, %d maps total (unblocked: %d; severed maps reopened by removing one barrier, plain/ledges-open: %s) -> PASS'
          % ('/'.join(STARTS), len(SEVERED), len(KEEP), len(KEEP), len(res['Pallet Town']), len(r0),
             ', '.join('%s %s' % kv for kv in alone.items())))

if __name__ == '__main__':
    main()
