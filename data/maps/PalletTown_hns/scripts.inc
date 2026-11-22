PalletTown_hns_MapScripts::
	.byte 0

PalletCity_EventScript_CitySign::
	msgbox PalletCity_Text_CitySign, MSGBOX_SIGN
	end

PalletCity_Text_CitySign:
	.string "PALLET CITY\n"
	.string "Shades of your journey await!$"

PalletCity_EventScript_DeptStoreSign::
	msgbox PalletCity_Text_DeptStoreSign, MSGBOX_SIGN
	end

PalletCity_Text_DeptStoreSign:
	.string "PALLET DEPARTMENT STORE$"

PalletCity_EventScript_HarborSign::
	msgbox PalletCity_Text_HarborSign, MSGBOX_SIGN
	end

PalletCity_Text_HarborSign:
	.string "PALLET HARBOR$"
