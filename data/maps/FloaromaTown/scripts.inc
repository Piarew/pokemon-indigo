FloaromaTown_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, FloaromaTown_OnTransition
	.byte 0

FloaromaTown_OnTransition::
	setworldmapflag FLAG_WORLD_MAP_FLOAROMA_TOWN
	end
