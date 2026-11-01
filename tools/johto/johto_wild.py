#!/usr/bin/env python3
"""GSC wild encounters from pokecrystal (data/wild/{johto,kanto}_{grass,water}.asm, daytime lists) for every built
Johto map that has pokecrystal wild data (Phase 6).  Run after gsc_cave.py (it replaces that script's hand lists).
Slot mapping: FRLG land 12 slots (20,20,10,10,10,10,5,5,4,4,1,1) <- GSC 7 slots (30,30,20,10,5,4,1) as
[0,1,0,1,2,2,3,4,3,5,6,5]; FRLG water 5 slots (60,30,5,4,1) <- GSC 3 slots (60,30,10) as [0,1,2,2,2].
Rates: land = 2 x GSC day percent (clamped 4..25), water = GSC percent (min 2).
Land only if the GSC map has grass collision or is a cave/tower (whole floor rolls); water only if it has water."""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
import pkc
from interiors import snake_upper
PKC = os.environ.get('POKECRYSTAL', '/workspace/pokecrystal')
INDOOR_TILESETS = ('CAVE', 'DARK_CAVE', 'ICE_PATH', 'TOWER', 'RUINS_OF_ALPH', 'ALPH')
SPECIES_FIX = {'MR__MIME': 'MR_MIME', 'FARFETCH_D': 'FARFETCHD'}

def parse():
    grass, water = {}, {}
    for region in ('johto', 'kanto'):
        t = open(os.path.join(PKC, 'data/wild/%s_grass.asm' % region)).read()
        for mm in re.finditer(r'def_grass_wildmons (\w+)\n(.*?)end_grass_wildmons', t, re.S):
            body = mm.group(2)
            rates = [int(x) for x in re.findall(r'(\d+) percent', body)]
            mons = re.findall(r'db (\d+), (\w+)', body)
            grass[mm.group(1)] = (rates[1], [(s, int(l)) for l, s in mons[7:14]])     # day
        t = open(os.path.join(PKC, 'data/wild/%s_water.asm' % region)).read()
        for mm in re.finditer(r'def_water_wildmons (\w+)\n(.*?)end_water_wildmons', t, re.S):
            body = mm.group(2)
            rate = int(re.search(r'(\d+) percent', body).group(1))
            water[mm.group(1)] = (rate, [(s, int(l)) for l, s in re.findall(r'db (\d+), (\w+)', body)])
    return grass, water

# custom maps (no pokecrystal data): GSC-style 7 day slots / 3 water slots, GSC percent
CUSTOM = {
    'MortarTrail': ((10, [('SPEAROW', 14), ('MAREEP', 14), ('MANKEY', 15), ('MARILL', 15), ('FLAAFFY', 17),
                          ('SANDSHREW', 16), ('GIRAFARIG', 17)]),
                    (6, [('POLIWAG', 15), ('MARILL', 15), ('POLIWHIRL', 20)])),
}

def sp(s): return 'SPECIES_' + SPECIES_FIX.get(s, s)

def main():
    grass, water = parse()
    groups = json.load(open(os.path.join(REPO, 'data/maps/map_groups.json')))
    import johto_convert
    names = list(johto_convert.MAPS) + groups.get('gMapGroup_IndoorJohto', [])
    p = os.path.join(REPO, 'src/data/wild_encounters.json'); wj = json.load(open(p))
    grp = next(g for g in wj['wild_encounter_groups']
               if any(e.get('base_label', '').startswith('sFourIslandIcefallCave1F_') for e in g.get('encounters', [])))
    enc = grp['encounters']
    done = []
    for name in names:
        if name in CUSTOM:
            land, wat = CUSTOM[name]
        else:
            try: m = pkc.load(name)
            except Exception: continue
            flat = {c for row in m.coll for c in row}
            indoor = any(k in m.tileset.upper() for k in INDOOR_TILESETS)
            land = grass.get(m.const) if (indoor or flat & {'TALL_GRASS', 'LONG_GRASS'}) else None
            wat = water.get(m.const) if flat & {'WATER'} else None
        if not land and not wat: continue
        mid = 'MAP_' + snake_upper(name)
        enc[:] = [e for e in enc if e.get('map') != mid]
        for ver in ('FireRed', 'LeafGreen'):
            e = {'map': mid, 'base_label': 's' + name.replace('_', '') + '_' + ver}
            if land:
                rate, mons = land
                e['land_mons'] = {'encounter_rate': max(4, min(25, rate * 2)), 'mons': [
                    {'min_level': mons[i][1], 'max_level': mons[i][1], 'species': sp(mons[i][0])}
                    for i in (0, 1, 0, 1, 2, 2, 3, 4, 3, 5, 6, 5)]}
            if wat:
                rate, mons = wat
                e['water_mons'] = {'encounter_rate': max(2, rate), 'mons': [
                    {'min_level': max(2, mons[i][1] - 5), 'max_level': mons[i][1], 'species': sp(mons[i][0])}
                    for i in (0, 1, 2, 2, 2)]}
            enc.append(e)
        done.append('%s%s%s' % (name, ' L' if land else '', ' W' if wat else ''))
    open(p, 'w').write(json.dumps(wj, indent=2, ensure_ascii=False) + '\n')
    print('wild encounters:', len(done), 'maps:', ', '.join(done))

if __name__ == '__main__':
    main()
