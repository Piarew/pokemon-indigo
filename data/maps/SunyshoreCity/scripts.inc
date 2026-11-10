SunyshoreCity_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, SunyshoreCity_OnTransition
	.byte 0

SunyshoreCity_OnTransition::
	setworldmapflag FLAG_WORLD_MAP_SUNYSHORE_CITY
	end
