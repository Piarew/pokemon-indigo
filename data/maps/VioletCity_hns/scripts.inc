VioletCity_hns_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, VioletCity_hns_OnTransition
	.byte 0

VioletCity_hns_OnTransition::
	setworldmapflag FLAG_WORLD_MAP_VIOLET_CITY
	end
