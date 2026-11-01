MtMoon_B1F_Frlg_MapScripts::
	map_script MAP_SCRIPT_ON_RESUME, MtMoon_B1F_OnResume
	.byte 0

@ ---- Mt. Moon cave-in (indigo custom; see tools/johto/mtmoon_cavein.py) ----
.equ MTMOON_CAVEIN_SPECIES, SPECIES_MEWTWO
.equ MTMOON_CAVEIN_LEVEL, 70

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
	setflag FLAG_UNUSED_0x4A7
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
	.string "Something stirs among the fallen\n"
	.string "rocks…$"

MtMoon_B1F_Text_CaveIn:
	.string "The tunnel to ROUTE 4 has caved in.\n"
	.string "There's no getting through here…$"
