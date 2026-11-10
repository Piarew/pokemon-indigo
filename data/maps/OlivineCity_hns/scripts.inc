OlivineCity_hns_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, OlivineCity_hns_OnTransition
	.byte 0

OlivineCity_hns_OnTransition::
	setworldmapflag FLAG_WORLD_MAP_OLIVINE_CITY
	end
