NewBarkTown_hns_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, NewBarkTown_hns_OnTransition
	.byte 0

NewBarkTown_hns_OnTransition::
	setworldmapflag FLAG_WORLD_MAP_NEW_BARK_TOWN
	end
