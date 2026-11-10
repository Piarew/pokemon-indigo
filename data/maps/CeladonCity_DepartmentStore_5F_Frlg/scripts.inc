CeladonCity_DepartmentStore_5F_Frlg_MapScripts::
	.byte 0

CeladonCity_DepartmentStore_5F_EventScript_Gentleman::
	msgbox CeladonCity_DepartmentStore_5F_Text_ExplainStatEnhancers, MSGBOX_NPC
	end

CeladonCity_DepartmentStore_5F_EventScript_Sailor::
	msgbox CeladonCity_DepartmentStore_5F_Text_HereForStatEnhancers, MSGBOX_NPC
	end

CeladonCity_DepartmentStore_5F_EventScript_FloorSign::
	msgbox CeladonCity_DepartmentStore_5F_Text_Drugstore, MSGBOX_SIGN
	end

CeladonCity_DepartmentStore_5F_EventScript_ClerkXItems::
	lock
	faceplayer
	message gText_HowMayIServeYou
	waitmessage
	pokemart CeladonCity_DepartmentStore_5F_XItems
	msgbox gText_PleaseComeAgain
	release
	end

	.align 2
CeladonCity_DepartmentStore_5F_XItems::
	.2byte ITEM_X_ATTACK
	.2byte ITEM_X_DEFEND
	.2byte ITEM_X_SPEED
	.2byte ITEM_X_SPECIAL
	.2byte ITEM_X_ACCURACY
	.2byte ITEM_GUARD_SPEC
	.2byte ITEM_DIRE_HIT
	.2byte ITEM_NONE
	release
	end

CeladonCity_DepartmentStore_5F_EventScript_ClerkVitamins::
	lock
	faceplayer
	message gText_HowMayIServeYou
	waitmessage
	pokemart CeladonCity_DepartmentStore_5F_Vitamins
	msgbox gText_PleaseComeAgain
	release
	end

	.align 2
CeladonCity_DepartmentStore_5F_Vitamins::
	.2byte ITEM_HP_UP
	.2byte ITEM_PROTEIN
	.2byte ITEM_IRON
	.2byte ITEM_CALCIUM
	.2byte ITEM_ZINC
	.2byte ITEM_CARBOS
	.2byte ITEM_BOTTLE_CAP
	.2byte ITEM_GOLD_BOTTLE_CAP
	.2byte ITEM_ABILITY_CAPSULE
	.2byte ITEM_ABILITY_PATCH
	.2byte ITEM_FRESH_START_MOCHI
	.2byte ITEM_LINKING_CORD
	.2byte ITEM_METAL_COAT
	.2byte ITEM_KINGS_ROCK
	.2byte ITEM_DRAGON_SCALE
	.2byte ITEM_UPGRADE
	.2byte ITEM_DUBIOUS_DISC
	.2byte ITEM_PROTECTOR
	.2byte ITEM_ELECTIRIZER
	.2byte ITEM_MAGMARIZER
	.2byte ITEM_REAPER_CLOTH
	.2byte ITEM_PRISM_SCALE
	.2byte ITEM_SACHET
	.2byte ITEM_WHIPPED_DREAM
	.2byte ITEM_DEEP_SEA_TOOTH
	.2byte ITEM_DEEP_SEA_SCALE
	.2byte ITEM_NONE
	release
	end

CeladonCity_DepartmentStore_5F_Text_ExplainStatEnhancers::
	.string "POKéMON stat enhancers can be\n"
	.string "bought only here.\p"
	.string "HP UP increases the base HP of a\n"
	.string "POKéMON.\p"
	.string "CALCIUM raises the base SP. ATK\n"
	.string "stat of one POKéMON.\p"
	.string "ZINC boosts the base SP. DEF stat\n"
	.string "of one POKéMON.\p"
	.string "CARBOS enhances the base SPEED\n"
	.string "stat.$"

CeladonCity_DepartmentStore_5F_Text_HereForStatEnhancers::
	.string "I'm here for POKéMON stat\n"
	.string "enhancers.\p"
	.string "PROTEIN increases the base ATTACK\n"
	.string "power.\p"
	.string "IRON increases the base DEFENSE\n"
	.string "stat.$"

CeladonCity_DepartmentStore_5F_Text_Drugstore::
	.string "5F: DRUGSTORE$"

