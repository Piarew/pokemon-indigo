MahoganyTown_MapScripts::
	.byte 0

MahoganyTown_EventScript_CitySign::
	msgbox MahoganyTown_Text_CitySign, MSGBOX_SIGN
	end

MahoganyTown_EventScript_ShopSign::
	msgbox MahoganyTown_Text_ShopSign, MSGBOX_SIGN
	end

MahoganyTown_EventScript_GymSign::
	msgbox MahoganyTown_Text_GymSign, MSGBOX_SIGN
	end

MahoganyTown_Text_CitySign::
	.string "MAHOGANY TOWN\n"
	.string "Welcome to the Home of the Ninja$"

MahoganyTown_Text_ShopSign::
	.string "MAHOGANY SOUVENIR SHOP$"

MahoganyTown_Text_GymSign::
	.string "MAHOGANY TOWN POKéMON GYM\n"
	.string "LEADER: PRYCE\p"
	.string "The Teacher of\n"
	.string "Winter's Harshness$"
