JubilifeCity_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, JubilifeCity_OnTransition
	.byte 0

JubilifeCity_OnTransition::
	setworldmapflag FLAG_WORLD_MAP_JUBILIFE_CITY
	end
