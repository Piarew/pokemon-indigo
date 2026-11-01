CyclingRoadWest_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, CyclingRoadWest_OnTransition
	map_script MAP_SCRIPT_ON_WARP_INTO_MAP_TABLE, CyclingRoadWest_OnWarp
	.byte 0

@ same as Route 16: still on the Cycling Road -> keep the forced-bike flag
CyclingRoadWest_OnTransition::
	call_if_eq VAR_MAP_SCENE_ROUTE16, 1, CyclingRoadWest_OnTransitionCyclingRoad
	end

CyclingRoadWest_OnTransitionCyclingRoad::
	setflag FLAG_SYS_ON_CYCLING_ROAD
	return

CyclingRoadWest_OnWarp::
	map_script_2 VAR_MAP_SCENE_ROUTE16, 1, CyclingRoadWest_OnWarpCyclingRoad
	.2byte 0

CyclingRoadWest_OnWarpCyclingRoad::
	special ForcePlayerOntoBike
	end

@ Viridian end, eastbound (VAR_MAP_SCENE_ROUTE16 == 0): stand-in for a Cycling Road gatehouse
CyclingRoadWest_EventScript_EnterCyclingRoad::
	lockall
	specialvar VAR_RESULT, GetPlayerAvatarBike
	goto_if_eq VAR_RESULT, 0, CyclingRoadWest_EventScript_NoPedestrians
	setvar VAR_MAP_SCENE_ROUTE16, 1
	setflag FLAG_SYS_ON_CYCLING_ROAD
	releaseall
	end

CyclingRoadWest_EventScript_NoPedestrians::
	msgbox CyclingRoadWest_Text_NoPedestrians
	closemessage
	applymovement LOCALID_PLAYER, CyclingRoadWest_Movement_WalkLeft
	waitmovement 0
	releaseall
	end

CyclingRoadWest_Movement_WalkLeft:
	walk_left
	step_end

CyclingRoadWest_EventScript_WestSign::
	msgbox CyclingRoadWest_Text_WestSign, MSGBOX_SIGN
	end

CyclingRoadWest_EventScript_EastSign::
	msgbox CyclingRoadWest_Text_EastSign, MSGBOX_SIGN
	end

CyclingRoadWest_Text_NoPedestrians:
	.string "No pedestrians are allowed on\n"
	.string "CYCLING ROAD!\p"
	.string "Please come back on a BIKE.$"

CyclingRoadWest_Text_WestSign:
	.string "CYCLING ROAD WEST\n"
	.string "VIRIDIAN CITY - CELADON CITY\p"
	.string "BIKES ONLY! Uphill to CELADON.$"

CyclingRoadWest_Text_EastSign:
	.string "CYCLING ROAD WEST\n"
	.string "Downhill to VIRIDIAN CITY.$"
