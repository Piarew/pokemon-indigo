Route31_MapScripts::
	.byte 0

Route31_EventScript_R31Sign::
	msgbox Route31_Text_R31Sign, MSGBOX_SIGN
	end

Route31_EventScript_DarkCaveSign::
	msgbox Route31_Text_DarkCaveSign, MSGBOX_SIGN
	end

Route31_Text_R31Sign::
	.string "ROUTE 31\n"
	.string "VIOLET CITY - CHERRYGROVE CITY$"

Route31_Text_DarkCaveSign::
	.string "DARK CAVE$"
