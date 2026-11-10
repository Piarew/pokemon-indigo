IndigoPlateau_hns_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, IndigoPlateau_hns_OnTransition
	.byte 0

IndigoPlateau_hns_OnTransition::
	setworldmapflag FLAG_WORLD_MAP_INDIGO_PLATEAU_EXTERIOR
	end
