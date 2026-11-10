BlackthornCity_hns_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, BlackthornCity_hns_OnTransition
	.byte 0

BlackthornCity_hns_OnTransition::
	setworldmapflag FLAG_WORLD_MAP_BLACKTHORN_CITY
	end
