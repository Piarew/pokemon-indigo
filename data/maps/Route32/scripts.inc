Route32_MapScripts::
	.byte 0

Route32_EventScript_SignSign::
	msgbox Route32_Text_SignSign, MSGBOX_SIGN
	end

Route32_EventScript_Sign2Sign::
	msgbox Route32_Text_Sign2Sign, MSGBOX_SIGN
	end

Route32_EventScript_Sign3Sign::
	msgbox Route32_Text_Sign3Sign, MSGBOX_SIGN
	end

Route32_Text_SignSign::
	.string "ROUTE 32\n"
	.string "VIOLET CITY - AZALEA TOWN$"

Route32_Text_Sign2Sign::
	.string "ROUTE 32\n"
	.string "VIOLET CITY - AZALEA TOWN$"

Route32_Text_Sign3Sign::
	.string "ROUTE 32\n"
	.string "VIOLET CITY - AZALEA TOWN$"

@ ---- West block (indigo custom; see tools/johto/west_blocks.py) ----
Route32_EventScript_RockfallSign::
	msgbox Route32_Text_Rockfall, MSGBOX_SIGN
	end

Route32_Text_Rockfall:
	.string "Fallen rocks have buried the\n"
	.string "path to UNION CAVE.\p"
	.string "There is no way through.$"
