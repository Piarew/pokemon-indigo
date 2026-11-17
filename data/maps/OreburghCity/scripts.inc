OreburghCity_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, OreburghCity_OnTransition
	.byte 0

OreburghCity_OnTransition::
	setworldmapflag FLAG_WORLD_MAP_OREBURGH_CITY
	end

OreburghCity_EventScript_StationSign::
	msgbox OreburghCity_Text_StationSign, MSGBOX_SIGN
	end

OreburghCity_Text_StationSign::
	.string "Oreburgh Station\n"
	.string "Subway to Saffron City$"
