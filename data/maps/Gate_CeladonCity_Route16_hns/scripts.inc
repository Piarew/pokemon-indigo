Gate_CeladonCity_Route16_hns_MapScripts::
	.byte 0

@ No bicycle check. Walk through and keep FLAG_SYS_CYCLING_ROAD in sync.
Gate_CeladonCity_Route16_TriggerScript::
	lockall
	goto_if_set FLAG_SYS_CYCLING_ROAD, Gate_CeladonCity_Route16_ExitCyclingRoad
	goto Gate_CeladonCity_Route16_EnterCyclingRoad

Gate_CeladonCity_Route16_EnterCyclingRoad::
	applymovement OBJ_EVENT_ID_PLAYER, Common_Movement_WalkLeft
	waitmovement 0
	setflag FLAG_SYS_CYCLING_ROAD
	releaseall
	end

Gate_CeladonCity_Route16_ExitCyclingRoad::
	applymovement OBJ_EVENT_ID_PLAYER, Common_Movement_WalkRight
	waitmovement 0
	clearflag FLAG_SYS_CYCLING_ROAD
	releaseall
	end

Gate_CeladonCity_Route16_EventScript_Officer::
	end
