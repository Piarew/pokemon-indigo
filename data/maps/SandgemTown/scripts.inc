SandgemTown_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, SandgemTown_OnTransition
	.byte 0

SandgemTown_OnTransition::
	setworldmapflag FLAG_WORLD_MAP_SANDGEM_TOWN
	end
