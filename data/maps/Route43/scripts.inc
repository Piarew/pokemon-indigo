Route43_MapScripts::
	.byte 0

Route43_EventScript_LakeOfRageSign::
	msgbox Route43_Text_LakeOfRageSign, MSGBOX_SIGN
	end

Route43_EventScript_R43Sign::
	msgbox Route43_Text_R43Sign, MSGBOX_SIGN
	end

Route43_EventScript_TrainerTipsSign::
	msgbox Route43_Text_TrainerTipsSign, MSGBOX_SIGN
	end

Route43_Text_LakeOfRageSign::
	.string "LAKE OF RAGE\n"
	.string "NORTH TO LAKE OF RAGE$"

Route43_Text_R43Sign::
	.string "ROUTE 43$"

Route43_Text_TrainerTipsSign::
	.string "TRAINER TIPS$"
