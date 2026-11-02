Route7_Frlg_MapScripts::
	.byte 0

Route7_EventScript_UndergroundPathSign::
	msgbox Route7_Text_UndergroundPathSign, MSGBOX_SIGN
	end

Route7_Text_UndergroundPathSign::
	.string "UNDERGROUND PATH\n"
	.string "CELADON CITY - LAVENDER TOWN$"

@ ---- East block (indigo custom; see tools/johto/east_blocks.py) ----
Route7_Frlg_EventScript_TreeWallSign::
	msgbox Route7_Frlg_Text_TreeWall, MSGBOX_SIGN
	end

Route7_Frlg_Text_TreeWall:
	.string "Trees have grown over the\n"
	.string "road to SAFFRON CITY.\p"
	.string "There is no way through.$"
