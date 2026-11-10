TwinleafTown_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, TwinleafTown_OnTransition
	.byte 0

TwinleafTown_OnTransition::
	setworldmapflag FLAG_WORLD_MAP_TWINLEAF_TOWN
	end
