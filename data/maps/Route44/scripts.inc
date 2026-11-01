Route44_MapScripts::
	.byte 0

Route44_EventScript_IcePathSign::
	msgbox Route44_Text_IcePathSign, MSGBOX_SIGN
	end

Route44_EventScript_R44Sign::
	msgbox Route44_Text_R44Sign, MSGBOX_SIGN
	end

Route44_Text_IcePathSign::
	.string "ICE PATH AHEAD$"

Route44_Text_R44Sign::
	.string "ROUTE 44\n"
	.string "MAHOGANY TOWN - BLACKTHORN CITY$"
