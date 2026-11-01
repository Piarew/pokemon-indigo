NewBarkTown_MapScripts::
	.byte 0

NewBarkTown_EventScript_ElmsLabSign::
	msgbox NewBarkTown_Text_ElmsLabSign, MSGBOX_SIGN
	end

NewBarkTown_EventScript_PlayersHouseSign::
	msgbox NewBarkTown_Text_PlayersHouseSign, MSGBOX_SIGN
	end

NewBarkTown_EventScript_CitySign::
	msgbox NewBarkTown_Text_CitySign, MSGBOX_SIGN
	end

NewBarkTown_EventScript_ElmsHouseSign::
	msgbox NewBarkTown_Text_ElmsHouseSign, MSGBOX_SIGN
	end

NewBarkTown_Text_ElmsLabSign::
	.string "ELM POKéMON LAB$"

NewBarkTown_Text_PlayersHouseSign::
	.string "{PLAYER}'s HOUSE$"

NewBarkTown_Text_CitySign::
	.string "NEW BARK TOWN\p"
	.string "The Town Where the\n"
	.string "Winds of a New\n"
	.string "Beginning Blow$"

NewBarkTown_Text_ElmsHouseSign::
	.string "ELM'S HOUSE$"
