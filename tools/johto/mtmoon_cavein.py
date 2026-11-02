#!/usr/bin/env python3
"""Mt. Moon cave-in (FireRed edit, flagged): block the Cerulean-side exit of MtMoon_B1F_Frlg.

The Route 4 (Cerulean side) exit of Mt. Moon is the ladder at B1F (45,4) in the small chamber x37-46 y2-5, which is
reached only from the B2F hole warp at B1F (39,4).  A rockfall of cave boulder metatiles (the 0x282/0x283 rubble the
chamber edges already use, collision 1) fills column x43 y2-5 and x42 y2/3/5, leaving a one-tile alcove at (42,4) in
which a static overworld encounter stands; the player faces it from (41,4).  Everything else in Mt. Moon (1F, B2F,
the rest of B1F, the Pewter-side entrance) is untouched.  The ladder pocket x44-46 is still reachable from Route 4
via its ladder, but it dead-ends at the rockfall.

Species/level are single constants (SPECIES / LEVEL below -> one .equ in the script + the object sprite).  The encounter
is one-time: FLAG (an unused FRLG flag) is set whatever the battle outcome and hides the object.
Idempotent: always rebuilt from the upstream (BASE_COMMIT) B1F files.
"""
import json, os, struct, subprocess

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
BASE_COMMIT = '72bd0bff9c'
MAP = 'MtMoon_B1F_Frlg'
BIN = 'data/layouts/MtMoon_B1F_Frlg/map.bin'
W = 49

SPECIES = 'MEWTWO'                 # placeholder: swap here (e.g. 'ARTICUNO'); drives SPECIES_x and OBJ_EVENT_GFX_x
LEVEL = 70
FLAG = 'FLAG_UNUSED_0x4A7'         # unused FRLG flag (flags_frlg.h "Unused hidden item flags"); one-time encounter
ALCOVE = (42, 4)
ROCK_A, ROCK_B = (37, 2), (36, 2)  # source cells for rubble metatiles 0x283 / 0x282
ROCKS = [(43, 2, 'A'), (43, 3, 'B'), (43, 4, 'A'), (43, 5, 'B'), (42, 2, 'A'), (42, 3, 'A'), (42, 5, 'A')]

def git_show(path):
    return subprocess.check_output(['git', 'show', '%s:%s' % (BASE_COMMIT, path)], cwd=REPO)

SCRIPT = """
@ ---- Mt. Moon cave-in (indigo custom; see tools/johto/mtmoon_cavein.py) ----
.equ MTMOON_CAVEIN_SPECIES, SPECIES_@SP
.equ MTMOON_CAVEIN_LEVEL, @LV

MtMoon_B1F_OnResume::
	call_if_set FLAG_SYS_CTRL_OBJ_DELETE, MtMoon_B1F_EventScript_TryRemoveCaveInMon
	end

MtMoon_B1F_EventScript_TryRemoveCaveInMon::
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_ne VAR_RESULT, B_OUTCOME_CAUGHT, Common_EventScript_NopReturn
	removeobject VAR_LAST_TALKED
	return

MtMoon_B1F_EventScript_CaveInMon::
	lock
	faceplayer
	setwildbattle MTMOON_CAVEIN_SPECIES, MTMOON_CAVEIN_LEVEL
	waitse
	playmoncry MTMOON_CAVEIN_SPECIES, CRY_MODE_ENCOUNTER
	message MtMoon_B1F_Text_CaveInMon
	waitmessage
	waitmoncry
	delay 10
	playbgm MUS_RG_ENCOUNTER_GYM_LEADER, 0
	waitbuttonpress
	setflag FLAG_SYS_CTRL_OBJ_DELETE
	special BattleSetup_StartLegendaryBattle
	clearflag FLAG_SYS_CTRL_OBJ_DELETE
	setflag @FLAG
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_WON, EventScript_RemoveStaticMon
	goto_if_eq VAR_RESULT, B_OUTCOME_RAN, MtMoon_B1F_EventScript_RanFromCaveInMon
	goto_if_eq VAR_RESULT, B_OUTCOME_PLAYER_TELEPORTED, MtMoon_B1F_EventScript_RanFromCaveInMon
	release
	end

MtMoon_B1F_EventScript_RanFromCaveInMon::
	setvar VAR_0x8004, MTMOON_CAVEIN_SPECIES
	goto EventScript_MonFlewAway
	end

MtMoon_B1F_EventScript_CaveInSign::
	msgbox MtMoon_B1F_Text_CaveIn, MSGBOX_SIGN
	end

MtMoon_B1F_Text_CaveInMon:
	.string "Something stirs among the fallen\\n"
	.string "rocks…$"

MtMoon_B1F_Text_CaveIn:
	.string "The tunnel to ROUTE 4 has caved in.\\n"
	.string "There's no getting through here…$"
"""

def main():
    raw = bytearray(git_show(BIN))
    v = list(struct.unpack('<%dH' % (len(raw) // 2), raw))
    src = {'A': v[ROCK_A[1] * W + ROCK_A[0]], 'B': v[ROCK_B[1] * W + ROCK_B[0]]}
    assert all((s >> 10) & 3 for s in src.values()) and (src['A'] & 0x3FF, src['B'] & 0x3FF) == (0x283, 0x282)
    for x, y, k in ROCKS:
        assert (v[y * W + x] >> 10) & 3 == 0, (x, y)          # only carving into open floor
        v[y * W + x] = src[k]
    out = struct.pack('<%dH' % len(v), *v)
    assert len(out) == len(raw)
    open(os.path.join(REPO, BIN), 'wb').write(out)

    j = json.loads(git_show('data/maps/%s/map.json' % MAP))
    j['object_events'] = [{'type': 'object', 'graphics_id': 'OBJ_EVENT_GFX_' + SPECIES, 'x': ALCOVE[0], 'y': ALCOVE[1],
                           'elevation': 3, 'movement_type': 'MOVEMENT_TYPE_FACE_LEFT', 'movement_range_x': 0,
                           'movement_range_y': 0, 'trainer_type': 'TRAINER_TYPE_NONE',
                           'trainer_sight_or_berry_tree_id': '0', 'script': 'MtMoon_B1F_EventScript_CaveInMon',
                           'flag': FLAG}]
    j['bg_events'] = list(j.get('bg_events') or []) + [
        {'type': 'sign', 'x': 42, 'y': 3, 'elevation': 0, 'player_facing_dir': 'BG_EVENT_PLAYER_FACING_ANY',
         'script': 'MtMoon_B1F_EventScript_CaveInSign'}]
    open(os.path.join(REPO, 'data/maps', MAP, 'map.json'), 'w').write(json.dumps(j, indent=2) + '\n')

    sc = git_show('data/maps/%s/scripts.inc' % MAP).decode()
    assert sc.strip() == 'MtMoon_B1F_Frlg_MapScripts::\n\t.byte 0'
    sc = ('MtMoon_B1F_Frlg_MapScripts::\n\tmap_script MAP_SCRIPT_ON_RESUME, MtMoon_B1F_OnResume\n\t.byte 0\n' +
          SCRIPT.replace('@SP', SPECIES).replace('@LV', str(LEVEL)).replace('@FLAG', FLAG))
    open(os.path.join(REPO, 'data/maps', MAP, 'scripts.inc'), 'w').write(sc)
    print('mtmoon_cavein: B1F rockfall %d cells, %s Lv%d at %s (flag %s)' % (len(ROCKS), SPECIES, LEVEL, ALCOVE, FLAG))

if __name__ == '__main__':
    main()
