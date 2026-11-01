#!/usr/bin/env python3
"""Generate FRLG-copied interiors for the Johto doors and wire the warps.

Each interior reuses an existing FRLG LAYOUT (no new map.bin).  Exit warps are
copied from the source FRLG map and pointed at the Johto door; the Johto door
warp points at the interior's first exit warp.  Re-runnable: rewrites the
interior dirs, the Johto maps' warp_events for configured doors, the
IndoorJohto map group, the event_scripts.s includes and the heal locations.

usage: python3 tools/johto/interiors.py
"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
MAPS = os.path.join(REPO, 'data', 'maps')
GROUP = 'gMapGroup_IndoorJohto'

def snake_upper(n):
    s = re.sub(r'(?<=[a-z])(?=[A-Z0-9])', '_', n)
    s = re.sub(r'(?<=[0-9])(?=[A-Z][a-z])', '_', s)
    return s.upper()

# kind -> list of (suffix, FRLG source map dir); first entry is the entrance map
KINDS = {
    'pc':       [('PokemonCenter_1F', 'ViridianCity_PokemonCenter_1F_Frlg'),
                 ('PokemonCenter_2F', 'ViridianCity_PokemonCenter_2F_Frlg')],
    'mart':     [('Mart', 'ViridianCity_Mart_Frlg')],
    'vhouse':   [(None, 'ViridianCity_House_Frlg')],
    'lhouse1':  [(None, 'LavenderTown_House1_Frlg')],
    'lhouse2':  [(None, 'LavenderTown_House2_Frlg')],
    'phouse1':  [(None, 'PewterCity_House1_Frlg')],
    'phouse2':  [(None, 'PewterCity_House2_Frlg')],
    'fhouse1':  [(None, 'FuchsiaCity_House1_Frlg')],
    'fhouse3':  [(None, 'FuchsiaCity_House3_Frlg')],
    'volunteer':[(None, 'LavenderTown_VolunteerPokemonHouse_Frlg')],
    'rival':    [(None, 'PalletTown_RivalsHouse_Frlg')],
    'dojo':     [(None, 'SaffronCity_Dojo_Frlg')],
    'lab':      [(None, 'PalletTown_ProfessorOaksLab_Frlg')],
    'players':  [('_1F', 'PalletTown_PlayersHouse_1F_Frlg'), ('_2F', 'PalletTown_PlayersHouse_2F_Frlg')],
    'gym_pewter':   [('Gym', 'PewterCity_Gym_Frlg')],
    'gym_viridian': [('Gym', 'ViridianCity_Gym_Frlg')],
    'gym_fuchsia':  [('Gym', 'FuchsiaCity_Gym_Frlg')],
    'gym_cinnabar': [('Gym', 'CinnabarIsland_Gym_Frlg')],
}

# outside map -> [(door x, y, kind, name suffix or None for kind default)]
DOORS = {
    'CherrygroveCity': [(24, 3, 'mart', None), (29, 3, 'pc', None), (17, 7, 'vhouse', 'House1'),
                        (25, 9, 'vhouse', 'GuideGentsHouse'), (31, 11, 'vhouse', 'House2')],
    'VioletCity': [(10, 17, 'mart', None), (18, 17, 'gym_pewter', None), (32, 25, 'pc', None),
                   (3, 15, 'lhouse1', 'House1'), (30, 17, 'volunteer', 'EarlsAcademy'),
                   (21, 29, 'lhouse2', 'House2'), (3, 29, 'lhouse1', 'House3')],
    'BlackthornCity': [(18, 11, 'gym_cinnabar', None), (15, 29, 'mart', None), (21, 29, 'pc', None),
                       (13, 21, 'phouse1', 'House1'), (29, 23, 'phouse2', 'House2'),
                       (9, 31, 'phouse1', 'MoveDeletersHouse')],
    'MahoganyTown': [(7, 13, 'gym_viridian', None), (15, 13, 'pc', None), (12, 7, 'mart', None),
                     (16, 7, 'vhouse', 'SouvenirShop')],
    'EcruteakCity': [(6, 27, 'gym_fuchsia', None), (23, 27, 'pc', None), (30, 21, 'mart', None),
                     (16, 3, 'fhouse1', 'WiseTriosHouse'), (12, 11, 'fhouse1', 'House1'),
                     (5, 17, 'fhouse3', 'House2'), (13, 17, 'fhouse1', 'House3'),
                     (29, 27, 'fhouse3', 'House4'), (5, 21, 'fhouse1', 'LugiaSpeechHouse'),
                     (13, 27, 'fhouse3', 'ItemfinderHouse'), (23, 21, 'dojo', 'DanceTheater')],
    'NewBarkTown': [(7, 4, 'lab', 'ElmsLab'), (13, 5, 'players', 'PlayersHouse'),
                    (3, 13, 'rival', 'House1'), (11, 13, 'rival', 'ElmsHouse')],
    'Route26': [(15, 57, 'vhouse', 'HealHouse'), (5, 71, 'vhouse', 'DayOfWeekSiblingsHouse')],
    'Route27': [(32, 7, 'vhouse', 'SandstormHouse')],
    'Route28': [(7, 3, 'vhouse', 'SteelWingHouse')],
    'Route29': [(27, 3, 'vhouse', 'Route46Gate')],
    'Route30': [(16, 5, 'vhouse', 'MrPokemonsHouse'), (7, 39, 'vhouse', 'BerryHouse')],
    'Route43': [(16, 35, 'vhouse', 'TollGate')],
    'SilverCaveOutside': [(23, 19, 'pc', None)],
}

HEAL = {  # outside map -> heal location id
    'CherrygroveCity': 'HEAL_LOCATION_CHERRYGROVE_CITY', 'VioletCity': 'HEAL_LOCATION_VIOLET_CITY',
    'BlackthornCity': 'HEAL_LOCATION_BLACKTHORN_CITY', 'MahoganyTown': 'HEAL_LOCATION_MAHOGANY_TOWN',
    'EcruteakCity': 'HEAL_LOCATION_ECRUTEAK_CITY', 'SilverCaveOutside': 'HEAL_LOCATION_SILVER_CAVE_OUTSIDE',
}

MART_ITEMS = {
    'early': ['ITEM_POKE_BALL', 'ITEM_POTION', 'ITEM_ANTIDOTE', 'ITEM_PARALYZE_HEAL', 'ITEM_AWAKENING',
              'ITEM_BURN_HEAL', 'ITEM_ESCAPE_ROPE', 'ITEM_REPEL'],
    'late': ['ITEM_GREAT_BALL', 'ITEM_ULTRA_BALL', 'ITEM_SUPER_POTION', 'ITEM_HYPER_POTION', 'ITEM_REVIVE',
             'ITEM_FULL_HEAL', 'ITEM_ICE_HEAL', 'ITEM_ESCAPE_ROPE', 'ITEM_SUPER_REPEL', 'ITEM_MAX_REPEL'],
}
LATE = {'MahoganyTown', 'BlackthornCity', 'EcruteakCity'}
KEEP_DEST = {'MAP_UNION_ROOM_FRLG', 'MAP_TRADE_CENTER_FRLG', 'MAP_DYNAMIC'}


def load(d):
    return json.load(open(os.path.join(MAPS, d, 'map.json')))


def dump(d, j):
    os.makedirs(os.path.join(MAPS, d), exist_ok=True)
    with open(os.path.join(MAPS, d, 'map.json'), 'w') as f:
        f.write(json.dumps(j, indent=2, ensure_ascii=False) + '\n')


def interior_names(outside, kind, suffix):
    parts = KINDS[kind]
    out = []
    for i, (ksuf, src) in enumerate(parts):
        if suffix is None:
            name = '%s_%s' % (outside, ksuf)
        elif ksuf and ksuf.startswith('_'):
            name = '%s_%s%s' % (outside, suffix, ksuf)
        else:
            name = '%s_%s' % (outside, suffix)
        out.append((name, src))
    return out


def main():
    created = []          # interior dir names
    heal_entries = []
    for outside, doors in DOORS.items():
        oj = load(outside)
        oid = oj['id']
        door_xy = {(x, y) for x, y, _, _ in doors}
        warps = [w for w in oj.get('warp_events', []) if (w['x'], w['y']) not in door_xy]
        for x, y, kind, suffix in doors:
            names = interior_names(outside, kind, suffix)
            srcids = {}
            for name, src in names:
                srcids[load(src)['id']] = 'MAP_' + snake_upper(name)
            door_idx = len(warps)
            entry_exit = None
            for bi, (name, src) in enumerate(names):
                sj = load(src)
                up = snake_upper(name)
                new_warps = []
                for w in sj['warp_events']:
                    w = dict(w)
                    if w['dest_map'] in srcids:
                        w['dest_map'] = srcids[w['dest_map']]
                    elif w['dest_map'] in KEEP_DEST:
                        pass
                    else:
                        w['dest_map'] = oid
                        w['dest_warp_id'] = str(door_idx)
                        if bi == 0 and entry_exit is None:
                            entry_exit = len(new_warps)
                    new_warps.append(w)
                objs, scripts = [], []
                ms = ['%s_MapScripts::' % name]
                if kind == 'pc' and bi == 0:
                    nurse = dict(load(src)['object_events'][0])
                    nurse['local_id'] = 'LOCALID_%s_NURSE' % snake_upper(outside)
                    nurse['script'] = '%s_EventScript_Nurse' % name
                    objs.append(nurse)
                    ms += ['\tmap_script MAP_SCRIPT_ON_TRANSITION, %s_OnTransition' % name,
                           '\tmap_script MAP_SCRIPT_ON_RESUME, CableClub_OnResume', '\t.byte 0', '',
                           '%s_OnTransition::' % name, '\tsetrespawn %s' % HEAL[outside], '\tend', '',
                           '%s_EventScript_Nurse::' % name, '\tlock', '\tfaceplayer',
                           '\tcall EventScript_PkmnCenterNurse_Frlg', '\trelease', '\tend', '']
                    heal_entries.append({'id': HEAL[outside], 'map': oid, 'x': x, 'y': y + 1,
                                         'respawn_map': 'MAP_' + up, 'respawn_npc': nurse['local_id']})
                elif kind == 'pc':
                    objs = [dict(o) for o in sj['object_events']]
                    for o in objs:
                        o.pop('local_id', None)
                    txt = open(os.path.join(MAPS, src, 'scripts.inc')).read()
                    txt = txt.replace(src[:-len('_Frlg')] + '_Frlg_MapScripts', name + '_MapScripts')
                    txt = txt.replace(src[:-len('_Frlg')], name)
                    ms = [txt]
                elif kind == 'mart':
                    clerk = dict(load(src)['object_events'][0])
                    clerk.pop('local_id', None)
                    clerk['script'] = '%s_EventScript_Clerk' % name
                    objs.append(clerk)
                    items = MART_ITEMS['late' if outside in LATE else 'early']
                    ms += ['\t.byte 0', '', '%s_EventScript_Clerk::' % name, '\tlock', '\tfaceplayer',
                           '\tmessage gText_HowMayIServeYou', '\twaitmessage', '\tpokemart %s_Items' % name,
                           '\tmsgbox gText_PleaseComeAgain', '\trelease', '\tend', '', '\t.align 2',
                           '%s_Items::' % name] + ['\t.2byte %s' % it for it in items] + ['\tpokemartlistend', '']
                else:
                    ms += ['\t.byte 0', '']
                music = sj['music']
                if kind not in ('pc', 'mart', 'lab') and not kind.startswith('gym'):
                    music = oj['music']
                j = {
                    'id': 'MAP_' + up, 'name': name, 'layout': sj['layout'], 'music': music,
                    'region': 'REGION_KANTO', 'region_map_section': oj['region_map_section'],
                    'requires_flash': False, 'weather': sj['weather'], 'map_type': sj['map_type'],
                    'allow_cycling': sj['allow_cycling'], 'allow_escaping': sj['allow_escaping'],
                    'allow_running': sj['allow_running'], 'show_map_name': False,
                    'floor_number': sj.get('floor_number', 0), 'battle_scene': sj['battle_scene'],
                    'connections': None, 'object_events': objs, 'warp_events': new_warps,
                    'coord_events': [], 'bg_events': [],
                }
                dump(name, j)
                with open(os.path.join(MAPS, name, 'scripts.inc'), 'w') as f:
                    f.write('\n'.join(ms) + '\n')
                created.append(name)
            assert entry_exit is not None, (outside, x, y)
            warps.append({'x': x, 'y': y, 'elevation': 0, 'dest_map': 'MAP_' + snake_upper(names[0][0]),
                          'dest_warp_id': str(entry_exit)})
        oj['warp_events'] = warps
        dump(outside, oj)

    # map group
    mg_path = os.path.join(MAPS, 'map_groups.json')
    mg = json.load(open(mg_path))
    if GROUP not in mg['group_order']:
        mg['group_order'].append(GROUP)
    mg[GROUP] = created
    with open(mg_path, 'w') as f:
        f.write(json.dumps(mg, indent=2) + '\n')

    # event_scripts.s includes, after the SilverCaveOutside include
    es_path = os.path.join(REPO, 'data', 'event_scripts.s')
    es = open(es_path).read()
    es = re.sub(r'\t\.include "data/maps/[^"]+/scripts\.inc"  @ johto-interior\n', '', es)
    anchor = '\t.include "data/maps/SilverCaveOutside/scripts.inc"\n'
    assert anchor in es
    inc = ''.join('\t.include "data/maps/%s/scripts.inc"  @ johto-interior\n' % n for n in created)
    es = es.replace(anchor, anchor + inc, 1)
    open(es_path, 'w').write(es)

    # heal locations
    hl_path = os.path.join(REPO, 'src', 'data', 'heal_locations.json')
    hl = json.load(open(hl_path))
    ids = {h['id'] for h in heal_entries}
    key = [k for k in hl if isinstance(hl[k], list)][0]
    hl[key] = [h for h in hl[key] if h['id'] not in ids] + heal_entries
    with open(hl_path, 'w') as f:
        f.write(json.dumps(hl, indent=2) + '\n')
    print('%d interior maps, %d heal locations' % (len(created), len(heal_entries)))


if __name__ == '__main__':
    main()
