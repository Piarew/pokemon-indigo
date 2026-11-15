IndigoCity_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, IndigoCity_OnTransition
	.byte 0

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
