PastoriaCity_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, PastoriaCity_OnTransition
	.byte 0

PastoriaCity_OnTransition::
	setworldmapflag FLAG_WORLD_MAP_PASTORIA_CITY
	end
