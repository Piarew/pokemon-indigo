IndigoCity_MapScripts::
	map_script MAP_SCRIPT_ON_LOAD, IndigoCity_OnLoad
	map_script MAP_SCRIPT_ON_TRANSITION, IndigoCity_OnTransition
	.byte 0

@ Battle Club (east gym): daily rotating rematch gym, see src/indigo_rematch.c.
@ With no Kanto Leader defeated yet the door is bricked up (0x15B door -> 0x314 wall).
IndigoCity_OnLoad::
	specialvar VAR_RESULT, IndigoRematch_UpdateDaily
	call_if_eq VAR_RESULT, 0, IndigoCity_EventScript_LockBattleClub
	end

IndigoCity_EventScript_LockBattleClub::
	setmetatile 42, 15, 0x314, TRUE
	return

IndigoCity_OnTransition::
	specialvar VAR_RESULT, CountIndigoGyms
	goto_if_eq VAR_RESULT, NUM_INDIGO_GYMS, IndigoCity_EventScript_UnlockVictoryRoad
	setvar VAR_TEMP_1, 0
	end

IndigoCity_EventScript_UnlockVictoryRoad::
	setvar VAR_TEMP_1, 1
	end

IndigoCity_EventScript_VictoryRoadGate::
	lockall
	goto_if_ne VAR_FACING, DIR_NORTH, IndigoCity_EventScript_VictoryRoadGateRelease
	goto EventScript_IndigoHqGate

IndigoCity_EventScript_VictoryRoadGateRelease::
	releaseall
	end

IndigoCity_EventScript_BattleClubDoor::
	lockall
	specialvar VAR_RESULT, IndigoRematch_UpdateDaily
	goto_if_eq VAR_RESULT, 0, IndigoCity_EventScript_BattleClubLocked
	special IndigoRematch_BufferLeaderName
	msgbox IndigoCity_Text_BattleClubToday
	releaseall
	end

IndigoCity_EventScript_BattleClubLocked::
	msgbox IndigoCity_Text_BattleClubLocked
	releaseall
	end

IndigoCity_Text_BattleClubToday::
	.string "INDIGO BATTLE CLUB\n"
	.string "Today's Gym Leader: {STR_VAR_1}\p"
	.string "The challenger changes daily.$"

IndigoCity_Text_BattleClubLocked::
	.string "The door is locked.\p"
	.string "INDIGO BATTLE CLUB\n"
	.string "Open to Trainers who have beaten\l"
	.string "a Kanto Gym Leader.$"
