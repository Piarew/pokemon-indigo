PalletTown_PlayersHouse_1F_Frlg_MapScripts::
	map_script MAP_SCRIPT_ON_FRAME_TABLE, PalletTown_PlayersHouse_1F_OnFrame
	.byte 0

PalletTown_PlayersHouse_1F_OnFrame::
	map_script_2 VAR_MAP_SCENE_PALLET_TOWN_PLAYERS_HOUSE_2F, 1, PalletTown_PlayersHouse_1F_EventScript_MomRules
	.2byte 0

PalletTown_PlayersHouse_1F_EventScript_MomRules::
	lockall
	textcolor NPC_TEXT_COLOR_FEMALE
	applymovement LOCALID_PLAYERS_HOUSE_1F_MOM, PalletTown_PlayersHouse_1F_Movement_MomToPlayer
	waitmovement 0
	applymovement LOCALID_PLAYER, Common_Movement_WalkInPlaceFasterLeft
	waitmovement 0
	msgbox PalletTown_PlayersHouse_1F_Text_MomIntro
	msgbox PalletTown_PlayersHouse_1F_Text_MomAskNuzlocke, MSGBOX_YESNO
	call_if_eq VAR_RESULT, YES, PalletTown_PlayersHouse_1F_EventScript_EnableNuzlocke
	msgbox PalletTown_PlayersHouse_1F_Text_MomAskWildRandomizer
	dynmultipush PalletTown_PlayersHouse_1F_Text_ChoiceNormal, 0
	dynmultipush PalletTown_PlayersHouse_1F_Text_ChoiceRandomized, 1
	dynmultistack 0, 0, TRUE, 2, FALSE, 0, DYN_MULTICHOICE_CB_NONE
	call_if_eq VAR_RESULT, 1, PalletTown_PlayersHouse_1F_EventScript_EnableWildRandomizer
	msgbox PalletTown_PlayersHouse_1F_Text_MomAskTrainerRandomizer
	dynmultipush PalletTown_PlayersHouse_1F_Text_ChoiceNormal, 0
	dynmultipush PalletTown_PlayersHouse_1F_Text_ChoiceRandomized, 1
	dynmultistack 0, 0, TRUE, 2, FALSE, 0, DYN_MULTICHOICE_CB_NONE
	call_if_eq VAR_RESULT, 1, PalletTown_PlayersHouse_1F_EventScript_EnableTrainerRandomizer
	msgbox PalletTown_PlayersHouse_1F_Text_MomAskAbilityRandomizer
	dynmultipush PalletTown_PlayersHouse_1F_Text_ChoiceNormal, 0
	dynmultipush PalletTown_PlayersHouse_1F_Text_ChoiceRandomized, 1
	dynmultistack 0, 0, TRUE, 2, FALSE, 0, DYN_MULTICHOICE_CB_NONE
	call_if_eq VAR_RESULT, 1, PalletTown_PlayersHouse_1F_EventScript_EnableAbilityRandomizer
	msgbox PalletTown_PlayersHouse_1F_Text_MomAskMovesetRandomizer
	dynmultipush PalletTown_PlayersHouse_1F_Text_ChoiceNormal, 0
	dynmultipush PalletTown_PlayersHouse_1F_Text_ChoiceRandomized, 1
	dynmultipush PalletTown_PlayersHouse_1F_Text_ChoiceSignature, 2
	dynmultistack 0, 0, TRUE, 3, FALSE, 0, DYN_MULTICHOICE_CB_NONE
	call_if_eq VAR_RESULT, 1, PalletTown_PlayersHouse_1F_EventScript_EnableMovesetRandomizer
	call_if_eq VAR_RESULT, 2, PalletTown_PlayersHouse_1F_EventScript_EnableMovesetSignatureRandomizer
	msgbox PalletTown_PlayersHouse_1F_Text_MomGoSeeAsh
	closemessage
	applymovement LOCALID_PLAYERS_HOUSE_1F_MOM, PalletTown_PlayersHouse_1F_Movement_MomBackToTable
	waitmovement 0
	setvar VAR_MAP_SCENE_PALLET_TOWN_PLAYERS_HOUSE_2F, 2
	setvar VAR_MAP_SCENE_PALLET_TOWN_PROFESSOR_OAKS_LAB, 1
	setvar VAR_MAP_SCENE_VIRIDIAN_CITY_MART, 2
	setvar VAR_MAP_SCENE_VIRIDIAN_CITY_OLD_MAN, 2
	setvar VAR_MAP_SCENE_PEWTER_CITY, 2
	setflag FLAG_HIDE_PEWTER_CITY_GYM_GUIDE
	setflag FLAG_HIDE_BULBASAUR_BALL
	setflag FLAG_HIDE_SQUIRTLE_BALL
	releaseall
	end

PalletTown_PlayersHouse_1F_EventScript_EnableNuzlocke::
	setflag FLAG_UNUSED_0x4AD
	return

PalletTown_PlayersHouse_1F_EventScript_EnableWildRandomizer::
	setflag FLAG_UNUSED_0x4AE
	return

PalletTown_PlayersHouse_1F_EventScript_EnableTrainerRandomizer::
	setflag FLAG_UNUSED_0x4AF
	return

PalletTown_PlayersHouse_1F_EventScript_EnableAbilityRandomizer::
	setflag FLAG_UNUSED_0x4BD
	return

PalletTown_PlayersHouse_1F_EventScript_EnableMovesetRandomizer::
	setflag FLAG_UNUSED_0x4BE
	return

PalletTown_PlayersHouse_1F_EventScript_EnableMovesetSignatureRandomizer::
	setflag FLAG_UNUSED_0x4BE
	setflag FLAG_UNUSED_0x4BF
	return

PalletTown_PlayersHouse_1F_Movement_MomToPlayer::
	walk_right
	walk_up
	walk_up
	walk_in_place_faster_right
	step_end

PalletTown_PlayersHouse_1F_Movement_MomBackToTable::
	walk_down
	walk_down
	walk_left
	walk_in_place_faster_left
	step_end

PalletTown_PlayersHouse_1F_EventScript_Mom::
	lock
	faceplayer
	goto_if_set FLAG_BEAT_RIVAL_IN_OAKS_LAB, PalletTown_PlayersHouse_1F_EventScript_MomHeal
	msgbox PalletTown_PlayersHouse_1F_Text_MomAshNextDoor
	closemessage
	applymovement LOCALID_PLAYERS_HOUSE_1F_MOM, Common_Movement_FaceOriginalDirection
	waitmovement 0
	release
	end

PalletTown_PlayersHouse_1F_EventScript_MomHeal::
	msgbox PalletTown_PlayersHouse_1F_Text_YouShouldTakeQuickRest
	closemessage
	call Common_EventScript_OutOfCenterPartyHeal
	msgbox PalletTown_PlayersHouse_1F_Text_LookingGreatTakeCare
	release
	end

PalletTown_PlayersHouse_1F_EventScript_TV::
	lockall
	goto_if_eq VAR_FACING, DIR_NORTH, PalletTown_PlayersHouse_1F_EventScript_TVScreen
	msgbox PalletTown_PlayersHouse_1F_Text_OopsWrongSide
	releaseall
	end

PalletTown_PlayersHouse_1F_EventScript_TVScreen::
	msgbox PalletTown_PlayersHouse_1F_Text_IndigoOnTV
	releaseall
	end

PalletTown_PlayersHouse_1F_Text_MomIntro::
	.string "MOM: {PLAYER}!\p"
	.string "Today's the day you leave\n"
	.string "as a Pokémon Trainer.\p"
	.string "I'm proud of you.\p"
	.string "Kids from this town have\n"
	.string "taken that rite of passage.\p"
	.string "It's been that way for as\n"
	.string "long as I remember.\p"
	.string "You'll get your partners\n"
	.string "and walk the roads.\p"
	.string "You'll do it the way\n"
	.string "Trainers always have.\p"
	.string "Before you go, I have\n"
	.string "a few questions.\p"
	.string "How do you want this\n"
	.string "adventure to work?\p"
	.string "These are extra challenges.\n"
	.string "They stay on.\p"
	.string "If you want the usual rules,\n"
	.string "pick Normal, or say no.$"

PalletTown_PlayersHouse_1F_Text_MomAskNuzlocke::
	.string "MOM: Will you take on the\n"
	.string "additional Nuzlocke ruleset?\p"
	.string "Fainted Pokémon are boxed.\p"
	.string "You may catch only the first\n"
	.string "new species in each area.$"

PalletTown_PlayersHouse_1F_Text_MomAskWildRandomizer::
	.string "MOM: On your adventure, how\n"
	.string "do Pokémon populate locations?$"

PalletTown_PlayersHouse_1F_Text_MomAskTrainerRandomizer::
	.string "MOM: On your adventure, how\n"
	.string "do Trainers build their teams?$"

PalletTown_PlayersHouse_1F_Text_MomAskAbilityRandomizer::
	.string "MOM: On your adventure, how\n"
	.string "do Pokémon Abilities manifest?$"

PalletTown_PlayersHouse_1F_Text_MomAskMovesetRandomizer::
	.string "MOM: On your adventure, how\n"
	.string "do Pokémon learn moves?\p"
	.string "Normal keeps their usual moves.\p"
	.string "Randomized replaces every\n"
	.string "level-up move.\p"
	.string "Signature keeps a unique move\n"
	.string "first, then randomizes the rest.$"

PalletTown_PlayersHouse_1F_Text_ChoiceNormal::
	.string "Normal$"

PalletTown_PlayersHouse_1F_Text_ChoiceRandomized::
	.string "Randomized$"

PalletTown_PlayersHouse_1F_Text_ChoiceSignature::
	.string "Signature$"

PalletTown_PlayersHouse_1F_Text_MomGoSeeAsh::
	.string "MOM: That's everything.\n"
	.string "The lab is next door.\p"
	.string "{RIVAL} already went over.\n"
	.string "I'm proud of you.\p"
	.string "Go on.$"

PalletTown_PlayersHouse_1F_Text_MomAshNextDoor::
	.string "MOM: The lab is next door.\n"
	.string "I'm proud of you. Go on.$"

PalletTown_PlayersHouse_1F_Text_YouShouldTakeQuickRest::
	.string "MOM: {PLAYER}!\n"
	.string "You should take a quick rest.$"

PalletTown_PlayersHouse_1F_Text_LookingGreatTakeCare::
	.string "MOM: There. You and your Pokémon\n"
	.string "look ready for the road.\p"
	.string "I'm proud of you.\n"
	.string "Be careful out there.$"

PalletTown_PlayersHouse_1F_Text_IndigoOnTV::
	.string "An Indigo broadcast.\p"
	.string "A woman in gold is talking about\n"
	.string "type recognition like weather.\p"
	.string "The volume is down.\n"
	.string "Mom's rule.$"

PalletTown_PlayersHouse_1F_Text_OopsWrongSide::
	.string "Oops, wrong side…$"
