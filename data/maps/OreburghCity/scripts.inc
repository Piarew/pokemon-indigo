OreburghCity_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, OreburghCity_OnTransition
	.byte 0

OreburghCity_OnTransition::
	setworldmapflag FLAG_WORLD_MAP_OREBURGH_CITY
	end
