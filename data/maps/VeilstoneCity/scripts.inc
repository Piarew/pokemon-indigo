VeilstoneCity_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, VeilstoneCity_OnTransition
	.byte 0

VeilstoneCity_OnTransition::
	setworldmapflag FLAG_WORLD_MAP_VEILSTONE_CITY
	end
