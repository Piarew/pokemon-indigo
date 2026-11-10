SolaceonTown_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, SolaceonTown_OnTransition
	.byte 0

SolaceonTown_OnTransition::
	setworldmapflag FLAG_WORLD_MAP_SOLACEON_TOWN
	end
