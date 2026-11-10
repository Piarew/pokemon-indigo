SnowpointCity_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, SnowpointCity_OnTransition
	.byte 0

SnowpointCity_OnTransition::
	setworldmapflag FLAG_WORLD_MAP_SNOWPOINT_CITY
	end
