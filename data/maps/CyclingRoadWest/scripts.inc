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

CyclingRoadWest_EventScript_WestSign::
	msgbox CyclingRoadWest_Text_WestSign, MSGBOX_SIGN
	end

CyclingRoadWest_EventScript_EastSign::
	msgbox CyclingRoadWest_Text_EastSign, MSGBOX_SIGN
	end

CyclingRoadWest_Text_WestSign:
	.string "CYCLING ROAD WEST\n"
	.string "VIRIDIAN CITY - CELADON CITY\p"
	.string "Uphill to CELADON. Keep pedaling!$"

CyclingRoadWest_Text_EastSign:
	.string "CYCLING ROAD WEST\n"
	.string "Downhill to VIRIDIAN CITY.$"
