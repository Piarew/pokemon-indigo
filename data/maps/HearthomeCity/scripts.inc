HearthomeCity_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, HearthomeCity_OnTransition
	.byte 0

HearthomeCity_OnTransition::
	setworldmapflag FLAG_WORLD_MAP_HEARTHOME_CITY
	end
