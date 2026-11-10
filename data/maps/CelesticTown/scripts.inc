CelesticTown_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, CelesticTown_OnTransition
	.byte 0

CelesticTown_OnTransition::
	setworldmapflag FLAG_WORLD_MAP_CELESTIC_TOWN
	end
