Route36_MapScripts::
	.byte 0

Route36_EventScript_R37Sign::
	msgbox Route36_Text_R37Sign, MSGBOX_SIGN
	end

Route36_EventScript_NationalParkSign::
	msgbox Route36_Text_NationalParkSign, MSGBOX_SIGN
	end

Route36_EventScript_R36Sign::
	msgbox Route36_Text_R36Sign, MSGBOX_SIGN
	end

Route36_EventScript_RuinsOfAlphSign::
	msgbox Route36_Text_RuinsOfAlphSign, MSGBOX_SIGN
	end

Route36_Text_R37Sign::
	.string "ROUTE 37$"

Route36_Text_NationalParkSign::
	.string "ROUTE 36\n"
	.string "NATIONAL PARK GATE$"

Route36_Text_R36Sign::
	.string "ROUTE 36\n"
	.string "VIOLET CITY$"

Route36_Text_RuinsOfAlphSign::
	.string "RUINS OF ALPH\n"
	.string "NORTH ENTRANCE$"

@ ---- West block (indigo custom; see tools/johto/west_blocks.py) ----
Route36_EventScript_TreeWallSign::
	msgbox Route36_Text_TreeWall, MSGBOX_SIGN
	end

Route36_Text_TreeWall:
	.string "The trees have grown together\n"
	.string "into a thick wall.\p"
	.string "There is no way west from here.$"
