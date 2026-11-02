Route30_MapScripts::
	.byte 0

Route30_EventScript_MrPokemonSign::
	msgbox Route30_Text_MrPokemonSign, MSGBOX_SIGN
	end

Route30_EventScript_R30Sign::
	msgbox Route30_Text_R30Sign, MSGBOX_SIGN
	end

Route30_EventScript_TrainerTipsSign::
	msgbox Route30_Text_TrainerTipsSign, MSGBOX_SIGN
	end

Route30_EventScript_BerryHouseSign::
	msgbox Route30_Text_BerryHouseSign, MSGBOX_SIGN
	end

Route30_Text_MrPokemonSign::
	.string "MR. POKéMON'S HOUSE\n"
	.string "STRAIGHT AHEAD!$"

Route30_Text_R30Sign::
	.string "ROUTE 30\n"
	.string "VIOLET CITY - CHERRYGROVE CITY$"

Route30_Text_TrainerTipsSign::
	.string "TRAINER TIPS$"

Route30_Text_BerryHouseSign::
	.string "BERRY MASTER\n"
	.string "Berries for everyone!$"
