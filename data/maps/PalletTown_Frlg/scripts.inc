.equ SIGN_LADY_READY, VAR_TEMP_2

PalletTown_Frlg_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, PalletTown_OnTransition
	map_script MAP_SCRIPT_ON_FRAME_TABLE, PalletTown_OnFrame
	.byte 0

PalletTown_OnTransition::
	setworldmapflag FLAG_WORLD_MAP_PALLET_TOWN
	call_if_set FLAG_PALLET_LADY_NOT_BLOCKING_SIGN, PalletTown_EventScript_TryReadySignLady
	call_if_eq VAR_MAP_SCENE_PALLET_TOWN_SIGN_LADY, 0, PalletTown_EventScript_SetSignLadyPos
	call_if_eq VAR_MAP_SCENE_PALLET_TOWN_SIGN_LADY, 1, PalletTown_EventScript_SetSignLadyDone
	end

PalletTown_EventScript_TryReadySignLady::
	goto_if_unset FLAG_OPENED_START_MENU, Common_EventScript_NopReturn
	goto_if_ge VAR_MAP_SCENE_PALLET_TOWN_SIGN_LADY, 1, Common_EventScript_NopReturn
	setvar VAR_MAP_SCENE_PALLET_TOWN_SIGN_LADY, 1
	return

PalletTown_EventScript_SetSignLadyDone::
	setvar VAR_MAP_SCENE_PALLET_TOWN_SIGN_LADY, 2
	return

PalletTown_EventScript_SetSignLadyPos::
	goto_if_set FLAG_PALLET_LADY_NOT_BLOCKING_SIGN, PalletTown_EventScript_MoveSignLadyToRouteEntrance
	setobjectxyperm LOCALID_PALLET_SIGN_LADY, 5, 15
	setobjectmovementtype LOCALID_PALLET_SIGN_LADY, MOVEMENT_TYPE_FACE_UP
	return

PalletTown_EventScript_MoveSignLadyToRouteEntrance::
	setobjectxyperm LOCALID_PALLET_SIGN_LADY, 12, 2
	setobjectmovementtype LOCALID_PALLET_SIGN_LADY, MOVEMENT_TYPE_FACE_DOWN
	setvar SIGN_LADY_READY, TRUE
	return

PalletTown_OnFrame::
	map_script_2 VAR_MAP_SCENE_PALLET_TOWN_OAK, 2, PalletTown_EventScript_OakRatingScene
	.2byte 0

@ Oak approaches player after exiting their house post Elite Four to check if they should receieve the National Dex
PalletTown_EventScript_OakRatingScene::
	lockall
	textcolor NPC_TEXT_COLOR_MALE
	setobjectxyperm LOCALID_PALLET_PROF_OAK, 14, 14
	setobjectmovementtype LOCALID_PALLET_PROF_OAK, MOVEMENT_TYPE_FACE_LEFT
	addobject LOCALID_PALLET_PROF_OAK
	applymovement LOCALID_PALLET_PROF_OAK, PalletTown_Movement_OakWalkToPlayersDoor
	waitmovement 0
	goto_if_unset FLAG_WORLD_MAP_ONE_ISLAND, PalletTown_EventScript_NotBeenToOneIslandYet
	msgbox PalletTown_Text_OakLetMeSeePokedex
	setvar VAR_0x8004, 0
	specialvar VAR_RESULT, GetFrlgPokedexCount
	copyvar VAR_0x8008, VAR_0x8005
	copyvar VAR_0x8009, VAR_0x8006
	buffernumberstring STR_VAR_1, VAR_0x8008
	buffernumberstring STR_VAR_2, VAR_0x8009
	goto_if_lt VAR_0x8009, 60, PalletTown_EventScript_NotEnoughMonsForNationalDex
	msgbox PalletTown_Text_CaughtXImpressiveFollowMe
	closemessage
	playbgm MUS_FOLLOW_ME, 0
	applymovement LOCALID_PLAYER, PalletTown_Movement_PlayerWalkToLabFromHouse
	applymovement LOCALID_PALLET_PROF_OAK, PalletTown_Movement_OakWalkToLabFromHouse
	waitmovement 0
	opendoor 16, 13
	waitdooranim
	applymovement LOCALID_PALLET_PROF_OAK, PalletTown_Movement_OakEnterLab
	applymovement LOCALID_PLAYER, PalletTown_Movement_PlayerEnterLab
	waitmovement 0
	closedoor 16, 13
	waitdooranim
	setvar VAR_MAP_SCENE_PALLET_TOWN_PROFESSOR_OAKS_LAB, 7
	setvar VAR_MAP_SCENE_PALLET_TOWN_OAK, 3
	setflag FLAG_HIDE_OAK_IN_PALLET_TOWN
	warp MAP_PALLET_TOWN_PROFESSOR_OAKS_LAB, 13, 20
	waitstate
	releaseall
	end

PalletTown_EventScript_EndOakRatingScene::
	closemessage
	applymovement LOCALID_PALLET_PROF_OAK, PalletTown_Movement_OakExit
	waitmovement 0
	removeobject LOCALID_PALLET_PROF_OAK
	setvar VAR_MAP_SCENE_PALLET_TOWN_OAK, 3
	releaseall
	end

PalletTown_EventScript_NotEnoughMonsForNationalDex::
	msgbox PalletTown_Text_CaughtXPuttingInHonestEffort
	goto PalletTown_EventScript_EndOakRatingScene
	end

PalletTown_EventScript_NotBeenToOneIslandYet::
	msgbox PalletTown_Text_OakYouEnjoyingTraveling
	goto PalletTown_EventScript_EndOakRatingScene
	end

PalletTown_Movement_OakWalkToPlayersDoor::
	walk_left
	walk_left
	walk_left
	walk_up
	walk_up
	walk_up
	walk_up
	walk_up
	walk_left
	walk_left
	walk_left
	walk_left
	walk_left
	walk_in_place_faster_up
	step_end

PalletTown_Movement_OakExit::
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_right
	walk_right
	walk_right
	step_end

PalletTown_Movement_OakWalkToLabFromHouse::
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	walk_in_place_faster_up
	step_end

PalletTown_Movement_PlayerWalkToLabFromHouse::
	walk_down
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_right
	walk_right
	walk_right
	walk_right
	step_end

PalletTown_EventScript_OakTriggerLeft::
	lockall
	setvar VAR_TEMP_1, 0
	goto PalletTown_EventScript_OakTrigger
	end

PalletTown_EventScript_OakTriggerRight::
	lockall
	setvar VAR_TEMP_1, 1
	goto PalletTown_EventScript_OakTrigger
	end

PalletTown_EventScript_OakTrigger::
	famechecker FAMECHECKER_OAK, FCPICKSTATE_COLORED, UpdatePickStateFromSpecialVar8005
	textcolor NPC_TEXT_COLOR_MALE
	delay 30
	playbgm MUS_RG_OAK, 0
	message PalletTown_Text_OakDontGoOut
	waitmessage
	delay 85
	closemessage
	applymovement LOCALID_PLAYER, Common_Movement_WalkInPlaceFasterDown
	waitmovement 0
	playse SE_PIN
	applymovement LOCALID_PLAYER, Common_Movement_ExclamationMark
	waitmovement 0
	delay 30
	addobject LOCALID_PALLET_PROF_OAK
	call_if_eq VAR_TEMP_1, 0, PalletTown_EventScript_OakEnterLeft
	call_if_eq VAR_TEMP_1, 1, PalletTown_EventScript_OakEnterRight
	delay 30
	msgbox PalletTown_Text_OakGrassUnsafeNeedMon
	closemessage
	delay 30
	call_if_eq VAR_TEMP_1, 0, PalletTown_EventScript_OakLeadPlayerToLabLeft
	call_if_eq VAR_TEMP_1, 1, PalletTown_EventScript_OakLeadPlayerToLabRight
	opendoor 16, 13
	waitdooranim
	applymovement LOCALID_PALLET_PROF_OAK, PalletTown_Movement_OakEnterLab
	applymovement LOCALID_PLAYER, PalletTown_Movement_PlayerEnterLab
	waitmovement 0
	closedoor 16, 13
	waitdooranim
	setvar VAR_MAP_SCENE_PALLET_TOWN_PROFESSOR_OAKS_LAB, 1
	clearflag FLAG_HIDE_OAK_IN_HIS_LAB
	setvar VAR_MAP_SCENE_PALLET_TOWN_OAK, 1
	setflag FLAG_HIDE_OAK_IN_PALLET_TOWN
	setflag FLAG_DONT_TRANSITION_MUSIC
	warp MAP_PALLET_TOWN_PROFESSOR_OAKS_LAB, 13, 20
	waitstate
	releaseall
	end

PalletTown_EventScript_OakEnterLeft::
	applymovement LOCALID_PALLET_PROF_OAK, PalletTown_Movement_OakEnterLeft
	waitmovement 0
	return

PalletTown_EventScript_OakEnterRight::
	applymovement LOCALID_PALLET_PROF_OAK, PalletTown_Movement_OakEnterRight
	waitmovement 0
	return

PalletTown_EventScript_OakLeadPlayerToLabLeft::
	applymovement LOCALID_PALLET_PROF_OAK, PalletTown_Movement_OakWalkToLabLeft
	applymovement LOCALID_PLAYER, PalletTown_Movement_PlayerWalkToLabLeft
	waitmovement 0
	return

PalletTown_EventScript_OakLeadPlayerToLabRight::
	applymovement LOCALID_PALLET_PROF_OAK, PalletTown_Movement_OakWalkToLabRight
	applymovement LOCALID_PLAYER, PalletTown_Movement_PlayerWalkToLabRight
	waitmovement 0
	return

PalletTown_Movement_OakEnterLeft::
	walk_up
	walk_up
	walk_right
	walk_up
	walk_up
	walk_right
	walk_up
	walk_up
	step_end

PalletTown_Movement_OakEnterRight::
	walk_right
	walk_up
	walk_up
	walk_right
	walk_up
	walk_up
	walk_right
	walk_up
	walk_up
	step_end

	.macro walk_to_lab
	walk_left
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_right
	walk_right
	walk_right
	walk_right
	.endm

PalletTown_Movement_OakWalkToLabLeft::
	walk_down
	walk_to_lab
	walk_right
	walk_in_place_faster_up
	step_end

PalletTown_Movement_OakWalkToLabRight::
	walk_down
	walk_left
	walk_to_lab
	walk_right
	walk_in_place_faster_up
	step_end

PalletTown_Movement_OakEnterLab::
	walk_up
	set_invisible
	step_end

PalletTown_Movement_PlayerWalkToLabLeft::
	walk_down
	walk_down
	walk_to_lab
	step_end

PalletTown_Movement_PlayerWalkToLabRight::
	walk_down
	walk_down
	walk_left
	walk_to_lab
	step_end

PalletTown_Movement_PlayerEnterLab::
	walk_right
	walk_up
	set_invisible
	step_end

PalletTown_EventScript_SignLady::
	lock
	goto_if_eq VAR_MAP_SCENE_PALLET_TOWN_SIGN_LADY, 2, PalletTown_EventScript_SignLadyDone
	goto_if_eq VAR_MAP_SCENE_PALLET_TOWN_SIGN_LADY, 1, PalletTown_EventScript_SignLadyJustShowedSign
	goto_if_eq SIGN_LADY_READY, TRUE, PalletTown_EventScript_SignLadyStartShowSign
	goto_if_set FLAG_TEMP_2, PalletTown_EventScript_SignLadyGoReadSign
	msgbox PalletTown_Text_HmmIsThatRight
	applymovement LOCALID_PALLET_SIGN_LADY, Common_Movement_FacePlayer
	waitmovement 0
	playse SE_PIN
	applymovement LOCALID_PALLET_SIGN_LADY, Common_Movement_ExclamationMark
	waitmovement 0
	applymovement LOCALID_PALLET_SIGN_LADY, Common_Movement_Delay48
	waitmovement 0
	msgbox PalletTown_Text_OhLookLook
	closemessage
	call_if_eq VAR_FACING, DIR_EAST, PalletTown_EventScript_SignLadyMoveOutOfWayRight
	call_if_ne VAR_FACING, DIR_EAST, PalletTown_EventScript_SignLadyMoveOutOfWayLeft
	copyobjectxytoperm LOCALID_PALLET_SIGN_LADY
	setflag FLAG_TEMP_2
	release
	end

PalletTown_EventScript_SignLadyMoveOutOfWayRight::
	applymovement LOCALID_PALLET_SIGN_LADY, PalletTown_Movement_SignLadyMoveOutOfWayRight
	waitmovement 0
	return

PalletTown_EventScript_SignLadyMoveOutOfWayLeft::
	applymovement LOCALID_PALLET_SIGN_LADY, PalletTown_Movement_SignLadyMoveOutOfWayLeft
	waitmovement 0
	return

PalletTown_EventScript_SignLadyDone::
	applymovement LOCALID_PALLET_SIGN_LADY, Common_Movement_FacePlayer
	waitmovement 0
	msgbox PalletTown_Text_RaisingMonsToo
	release
	end

PalletTown_EventScript_SignLadyGoReadSign::
	applymovement LOCALID_PALLET_SIGN_LADY, Common_Movement_FacePlayer
	waitmovement 0
	msgbox PalletTown_Text_ReadItReadIt
	release
	end

PalletTown_EventScript_SignLadyJustShowedSign::
	applymovement LOCALID_PALLET_SIGN_LADY, Common_Movement_FacePlayer
	waitmovement 0
	msgbox PalletTown_Text_SignsAreUsefulArentThey
	release
	end

PalletTown_Movement_SignLadyMoveOutOfWayRight::
	walk_right
	walk_in_place_faster_left
	step_end

PalletTown_Movement_SignLadyMoveOutOfWayLeft::
	walk_left
	walk_in_place_faster_right
	step_end

PalletTown_EventScript_FatMan::
	msgbox PalletTown_Text_CanStoreItemsAndMonsInPC, MSGBOX_NPC
	end

PalletTown_EventScript_OaksLabSign::
	lockall
	famechecker FAMECHECKER_OAK, 0
	msgbox PalletTown_Text_OakPokemonResearchLab
	releaseall
	end

PalletTown_EventScript_PlayersHouseSign::
	msgbox PalletTown_Text_PlayersHouse, MSGBOX_SIGN
	end

PalletTown_EventScript_RivalsHouseSign::
	msgbox PalletTown_Text_RivalsHouse, MSGBOX_SIGN
	end

PalletTown_EventScript_TownSign::
	msgbox PalletTown_Text_TownSign, MSGBOX_SIGN
	end

PalletTown_EventScript_TrainerTips::
	lockall
	msgbox PalletTown_Text_PressStartToOpenMenu
	setvar VAR_MAP_SCENE_PALLET_TOWN_SIGN_LADY, 1
	releaseall
	end

PalletTown_EventScript_SignLadyTrigger::
	lockall
	applymovement LOCALID_PALLET_SIGN_LADY, Common_Movement_WalkInPlaceFasterRight
	applymovement LOCALID_PLAYER, Common_Movement_WalkInPlaceFasterLeft
	waitmovement 0
	call PalletTown_EventScript_SignLadyShowSign
	releaseall
	end

PalletTown_EventScript_SignLadyShowSign::
	textcolor NPC_TEXT_COLOR_FEMALE
	msgbox PalletTown_Text_LookCopiedTrainerTipsSign
	closemessage
	delay 20
	textcolor NPC_TEXT_COLOR_NEUTRAL
	setflag FLAG_OPENED_START_MENU
	setvar VAR_MAP_SCENE_PALLET_TOWN_SIGN_LADY, 1
	setvar SIGN_LADY_READY, FALSE
	special SetWalkingIntoSignVars
	special DisableMsgBoxWalkaway
	signmsg
	msgbox PalletTown_Text_PressStartToOpenMenuCopy
	normalmsg
	return

PalletTown_EventScript_SignLadyStartShowSign::
	applymovement LOCALID_PALLET_SIGN_LADY, Common_Movement_FacePlayer
	waitmovement 0
	call PalletTown_EventScript_SignLadyShowSign
	release
	end

PalletTown_Text_OakDontGoOut::
	.string "ASH: Hey! Don't go out there!$"

PalletTown_Text_OakGrassUnsafeNeedMon::
	.string "ASH: Wild Pokémon live in the\n"
	.string "grass.\p"
	.string "They fight two at a time on this\n"
	.string "route. I learned that the hard way.\p"
	.string "I'm ASH. Prof. Ash, if the plaque\n"
	.string "makes you formal.\p"
	.string "OAK taught me in this town.\n"
	.string "He's gone. The work isn't.\p"
	.string "You need partners before you need\n"
	.string "a road.\p"
	.string "Come to the lab. I've got three\n"
	.string "waiting.\p"
	.string "They don't like being a single.$"

PalletTown_Text_RaisingMonsToo::
	.string "I'm raising Pokémon, too.\p"
	.string "When they get strong, they can\n"
	.string "protect me.$"

PalletTown_Text_CanStoreItemsAndMonsInPC::
	.string "You can store items and Pokémon\n"
	.string "in a PC.\p"
	.string "The Champion who lived in your\n"
	.string "house used a PC like a closet.\p"
	.string "We still tell that story because\n"
	.string "we don't have a new one.\p"
	.string "ASH says you'll write it.\n"
	.string "ASH says that about everyone.$"

PalletTown_Text_OakPokemonResearchLab::
	.string "Ash Pokémon Research Lab\p"
	.string "A small plaque under the paint:\n"
	.string "In memory of Prof. Samuel Oak.$"

PalletTown_Text_PlayersHouse::
	.string "{PLAYER}'s house$"

PalletTown_Text_RivalsHouse::
	.string "{RIVAL}'s house$"

PalletTown_Text_TownSign::
	.string "Pallet Town\n"
	.string "Shades of your journey await!\p"
	.string "Prof. Ash's Pokémon Research Lab$"

PalletTown_Text_OakLetMeSeePokedex::
	.string "Oak: Ah, {PLAYER}!\n"
	.string "You're back, are you?\p"
	.string "How much have you filled in your\n"
	.string "Pokédex?\p"
	.string "May I see it?\p"
	.string "Let's see…$"

PalletTown_Text_CaughtXPuttingInHonestEffort::
	.string "You've caught {STR_VAR_2}…\p"
	.string "Hm, it looks as if you're putting\n"
	.string "in an honest effort.\p"
	.string "When you manage to fill it some\n"
	.string "more, come show me, please.$"

PalletTown_Text_CaughtXImpressiveFollowMe::
	.string "You've caught… {STR_VAR_2}!?\n"
	.string "Now, this is impressive!\p"
	.string "There's something I wanted to ask\n"
	.string "of you, {PLAYER}.\p"
	.string "Come.\n"
	.string "Follow me.$"

PalletTown_Text_OakYouEnjoyingTraveling::
	.string "Oak: Ah, {PLAYER}!\n"
	.string "You seem to be enjoying traveling.\p"
	.string "Knowing you, {PLAYER}, I can easily\n"
	.string "imagine you going even farther.\p"
	.string "Good for you, good for you.\n"
	.string "Hohoho.$"

@ For the NPC in Pallet Town that talks about the Trainer Tips sign
PalletTown_Text_HmmIsThatRight::
	.string "Hmm…\n"
	.string "Is that right…$"

PalletTown_Text_OhLookLook::
	.string "Oh!\n"
	.string "Look, look!$"

PalletTown_Text_ReadItReadIt::
	.string "Read it, read it!$"

@ Used by sign
PalletTown_Text_PressStartToOpenMenu::
	.string "Trainer Tips\p"
	.string "Press Start to open the Menu!$"

PalletTown_Text_SignsAreUsefulArentThey::
	.string "Signs are useful, aren't they?\p"
	.string "That one used to say OAK.\n"
	.string "They painted ASH over it and left\p"
	.string "a plaque so the tourists would\n"
	.string "stop asking if the old man was\p"
	.string "napping.$"

PalletTown_Text_LookCopiedTrainerTipsSign::
	.string "Look, look!\p"
	.string "I copied what it said on one of\n"
	.string "those Trainer Tips signs!$"

@ Used by NPC
PalletTown_Text_PressStartToOpenMenuCopy::
	.string "Trainer Tips!\p"
	.string "Press Start to open the Menu!$"

@ Sprite-preview NPCs. Real Indigo gym teams (6v6 doubles).
@ Beating one here sets that gym trainer's defeated flag.

	.macro pallet_indigo_preview trainer:req, intro:req, defeat:req, after:req
	trainerbattle_double \trainer, \intro, \defeat, PalletTown_Text_IndigoNeedTwo
	msgbox \after, MSGBOX_AUTOCLOSE
	end
	.endm

PalletTown_EventScript_IndigoViridian::
	pallet_indigo_preview TRAINER_LEADER_INDIGO_VIRIDIAN, PalletTown_Text_WrenIntro, PalletTown_Text_WrenDefeat, PalletTown_Text_WrenAfter
PalletTown_EventScript_IndigoPewter::
	pallet_indigo_preview TRAINER_LEADER_INDIGO_PEWTER, PalletTown_Text_MasonIntro, PalletTown_Text_MasonDefeat, PalletTown_Text_MasonAfter
PalletTown_EventScript_IndigoCerulean::
	pallet_indigo_preview TRAINER_LEADER_INDIGO_CERULEAN, PalletTown_Text_MaeveIntro, PalletTown_Text_MaeveDefeat, PalletTown_Text_MaeveAfter
PalletTown_EventScript_IndigoCeladon::
	pallet_indigo_preview TRAINER_LEADER_INDIGO_CELADON, PalletTown_Text_PepperIntro, PalletTown_Text_PepperDefeat, PalletTown_Text_PepperAfter
PalletTown_EventScript_IndigoSaffron::
	pallet_indigo_preview TRAINER_LEADER_INDIGO_SAFFRON, PalletTown_Text_IoriIntro, PalletTown_Text_IoriDefeat, PalletTown_Text_IoriAfter
PalletTown_EventScript_IndigoFuchsia::
	pallet_indigo_preview TRAINER_LEADER_INDIGO_FUCHSIA, PalletTown_Text_HoltIntro, PalletTown_Text_HoltDefeat, PalletTown_Text_HoltAfter
PalletTown_EventScript_IndigoCherrygrove::
	pallet_indigo_preview TRAINER_LEADER_INDIGO_CHERRYGROVE, PalletTown_Text_ArloIntro, PalletTown_Text_ArloDefeat, PalletTown_Text_ArloAfter
PalletTown_EventScript_IndigoViolet::
	pallet_indigo_preview TRAINER_LEADER_INDIGO_VIOLET, PalletTown_Text_LenoreIntro, PalletTown_Text_LenoreDefeat, PalletTown_Text_LenoreAfter
PalletTown_EventScript_IndigoGoldenrod::
	pallet_indigo_preview TRAINER_LEADER_INDIGO_GOLDENROD, PalletTown_Text_ValeIntro, PalletTown_Text_ValeDefeat, PalletTown_Text_ValeAfter
PalletTown_EventScript_IndigoOlivine::
	pallet_indigo_preview TRAINER_LEADER_INDIGO_OLIVINE, PalletTown_Text_BramIntro, PalletTown_Text_BramDefeat, PalletTown_Text_BramAfter
PalletTown_EventScript_IndigoCianwood::
	pallet_indigo_preview TRAINER_LEADER_INDIGO_CIANWOOD, PalletTown_Text_YarrowIntro, PalletTown_Text_YarrowDefeat, PalletTown_Text_YarrowAfter
PalletTown_EventScript_IndigoBlackthorn::
	pallet_indigo_preview TRAINER_LEADER_INDIGO_BLACKTHORN, PalletTown_Text_SigridIntro, PalletTown_Text_SigridDefeat, PalletTown_Text_SigridAfter
PalletTown_EventScript_IndigoJubilife::
	pallet_indigo_preview TRAINER_LEADER_INDIGO_JUBILIFE, PalletTown_Text_PiperIntro, PalletTown_Text_PiperDefeat, PalletTown_Text_PiperAfter
PalletTown_EventScript_IndigoOreburgh::
	pallet_indigo_preview TRAINER_LEADER_INDIGO_OREBURGH, PalletTown_Text_GritIntro, PalletTown_Text_GritDefeat, PalletTown_Text_GritAfter
PalletTown_EventScript_IndigoEterna::
	pallet_indigo_preview TRAINER_LEADER_INDIGO_ETERNA, PalletTown_Text_EdithIntro, PalletTown_Text_EdithDefeat, PalletTown_Text_EdithAfter
PalletTown_EventScript_IndigoSnowpoint::
	pallet_indigo_preview TRAINER_LEADER_INDIGO_SNOWPOINT, PalletTown_Text_MagnusIntro, PalletTown_Text_MagnusDefeat, PalletTown_Text_MagnusAfter
PalletTown_EventScript_IndigoSunyshore::
	pallet_indigo_preview TRAINER_LEADER_INDIGO_SUNYSHORE, PalletTown_Text_WadeIntro, PalletTown_Text_WadeDefeat, PalletTown_Text_WadeAfter
PalletTown_EventScript_IndigoPastoria::
	pallet_indigo_preview TRAINER_LEADER_INDIGO_PASTORIA, PalletTown_Text_GilesIntro, PalletTown_Text_GilesDefeat, PalletTown_Text_GilesAfter

PalletTown_Text_IndigoNeedTwo::
	.string "Bring two POKéMON.\n"
	.string "This is a Double Battle.$"

PalletTown_Text_WrenIntro::
	.string "I'm WREN. I keep the woods standing,\n"
	.string "with or without Indigo's blessing.\p"
	.string "Grass POKéMON grow on their own terms.\n"
	.string "Let's see if you respect that.$"

PalletTown_Text_WrenDefeat::
	.string "You cut a path.\n"
	.string "I'll plant around it.$"

PalletTown_Text_WrenAfter::
	.string "Viridian's gym is a greenhouse.\n"
	.string "Come when you're ready to get dirty.$"

PalletTown_Text_MasonIntro::
	.string "Name's MASON. I smith steel the old\n"
	.string "Pewter way.\p"
	.string "Indigo pays for the forge.\n"
	.string "I pay them back in tempered POKéMON.$"

PalletTown_Text_MasonDefeat::
	.string "Solid work.\n"
	.string "You didn't warp in the heat.$"

PalletTown_Text_MasonAfter::
	.string "Steel bends. It doesn't break.\n"
	.string "Remember that in my gym.$"

PalletTown_Text_MaeveIntro::
	.string "MAEVE, darling. Cerulean's stage is mine.\p"
	.string "Fairy POKéMON love an audience.\n"
	.string "Give them a show.$"

PalletTown_Text_MaeveDefeat::
	.string "Oh, you stole my spotlight.$"

PalletTown_Text_MaeveAfter::
	.string "Keep practicing.\n"
	.string "The next act is in Cerulean.$"

PalletTown_Text_PepperIntro::
	.string "PEPPER, Celadon kitchen.\n"
	.string "Fire isn't garnish.\p"
	.string "It's the whole dish.\p"
	.string "Sit down. Dinner's a Double Battle.$"

PalletTown_Text_PepperDefeat::
	.string "Overcooked.\n"
	.string "I'll plate it better next time.$"

PalletTown_Text_PepperAfter::
	.string "Celadon's gym smells like spice.\n"
	.string "Don't be late.$"

PalletTown_Text_IoriIntro::
	.string "IORI. Saffron dojo.\n"
	.string "A belt is earned, not issued.\p"
	.string "Fighting POKéMON don't fake a strike.\n"
	.string "Neither do I.$"

PalletTown_Text_IoriDefeat::
	.string "Your form held.\n"
	.string "Bow.$"

PalletTown_Text_IoriAfter::
	.string "The dojo doors stay open.\n"
	.string "Come train for real.$"

PalletTown_Text_HoltIntro::
	.string "HOLT. I walk Fuchsia's preserve.\p"
	.string "Dragon POKéMON keep to the deep paths.\n"
	.string "Stay on mine.$"

PalletTown_Text_HoltDefeat::
	.string "You found the trail.\n"
	.string "Most don't.$"

PalletTown_Text_HoltAfter::
	.string "The Safari's quieter than it looks.\n"
	.string "My gym isn't.$"

PalletTown_Text_ArloIntro::
	.string "ARLO. I catalog ordinary POKéMON\n"
	.string "like they're treasures.\p"
	.string "Normal types get overlooked.\n"
	.string "That's a mistake.$"

PalletTown_Text_ArloDefeat::
	.string "Noted.\n"
	.string "You're going in the field journal.$"

PalletTown_Text_ArloAfter::
	.string "Cherrygrove's gym is a collection.\n"
	.string "Handle with care.$"

PalletTown_Text_LenoreIntro::
	.string "…LENORE. I tend Violet's empty houses.\p"
	.string "Ghost POKéMON stayed when the city\n"
	.string "didn't. Indigo can wait.$"

PalletTown_Text_LenoreDefeat::
	.string "You walked out.\n"
	.string "That's rarer than you think.$"

PalletTown_Text_LenoreAfter::
	.string "Violet is abandoned.\n"
	.string "The gym still has lights on.$"

PalletTown_Text_ValeIntro::
	.string "VALE. Goldenrod deals in what people\n"
	.string "won't say out loud.\p"
	.string "Dark POKéMON know a good contract.\n"
	.string "Do you?$"

PalletTown_Text_ValeDefeat::
	.string "Fine.\n"
	.string "You drove a harder bargain.$"

PalletTown_Text_ValeAfter::
	.string "The department store's honest.\n"
	.string "My gym isn't. Come anyway.$"

PalletTown_Text_BramIntro::
	.string "BRAM. I keep Olivine's light turning.\p"
	.string "Flying POKéMON read the wind.\n"
	.string "So do ships. So do I.$"

PalletTown_Text_BramDefeat::
	.string "Gust caught me.\n"
	.string "I'll trim the lamp.$"

PalletTown_Text_BramAfter::
	.string "Climb the tower when you want\n"
	.string "a proper match.$"

PalletTown_Text_YarrowIntro::
	.string "YARROW. I mix what Cianwood's clinic\n"
	.string "won't touch.\p"
	.string "Poison isn't cruelty.\n"
	.string "It's a measured dose.$"

PalletTown_Text_YarrowDefeat::
	.string "You had the antidote ready.\n"
	.string "Good.$"

PalletTown_Text_YarrowAfter::
	.string "Come to the pharmacy gym.\n"
	.string "Wipe your feet.$"

PalletTown_Text_SigridIntro::
	.string "SIGRID. Ice is a teacher.\n"
	.string "Blackthorn is the classroom.\p"
	.string "If you can't keep your footing,\n"
	.string "turn back.$"

PalletTown_Text_SigridDefeat::
	.string "Avalanche on me.\n"
	.string "I'll climb it.$"

PalletTown_Text_SigridAfter::
	.string "The mountain gym doesn't lower\n"
	.string "itself. You climb.$"

PalletTown_Text_PiperIntro::
	.string "PIPER, live from Jubilife!\p"
	.string "Electric POKéMON don't whisper.\n"
	.string "Neither does the news.$"

PalletTown_Text_PiperDefeat::
	.string "And that's a wrap.\n"
	.string "You took the segment.$"

PalletTown_Text_PiperAfter::
	.string "Tune in at the TV gym.\n"
	.string "Bring two POKéMON. We're doubles.$"

PalletTown_Text_GritIntro::
	.string "GRIT. I map what sits under Oreburgh.\p"
	.string "Ground POKéMON don't lie about\n"
	.string "bedrock. I don't either.$"

PalletTown_Text_GritDefeat::
	.string "You found the fault line.\n"
	.string "I'll mark it.$"

PalletTown_Text_GritAfter::
	.string "The mine gym goes down.\n"
	.string "Watch your head.$"

PalletTown_Text_EdithIntro::
	.string "EDITH. I keep Eterna's records,\n"
	.string "not Indigo's speeches.\p"
	.string "Psychic POKéMON remember.\n"
	.string "So should you.$"

PalletTown_Text_EdithDefeat::
	.string "Written down.\n"
	.string "You won.$"

PalletTown_Text_EdithAfter::
	.string "The library gym is quiet.\n"
	.string "Your battle won't be.$"

PalletTown_Text_MagnusIntro::
	.string "MAGNUS. Snowpoint expeditions\n"
	.string "don't turn around.\p"
	.string "Rock POKéMON wait out the storm.\n"
	.string "Pack for it.$"

PalletTown_Text_MagnusDefeat::
	.string "Base camp.\n"
	.string "We'll summit later.$"

PalletTown_Text_MagnusAfter::
	.string "The gym is a ridge, not a lobby.\n"
	.string "Dress warm.$"

PalletTown_Text_WadeIntro::
	.string "WADE. I keep Sunyshore's water moving.\p"
	.string "Water POKéMON follow pressure.\n"
	.string "So do pipes. So do I.$"

PalletTown_Text_WadeDefeat::
	.string "Leak on my side.\n"
	.string "I'll patch it.$"

PalletTown_Text_WadeAfter::
	.string "The coastal gym is live.\n"
	.string "Bring two POKéMON.$"

PalletTown_Text_GilesIntro::
	.string "GILES. I study bugs others swat.\p"
	.string "Bug POKéMON built the marsh.\n"
	.string "Indigo just put a sign on it.$"

PalletTown_Text_GilesDefeat::
	.string "Specimen noted.\n"
	.string "You're quicker than you look.$"

PalletTown_Text_GilesAfter::
	.string "Pastoria's gym is a net and a notebook.\n"
	.string "Come get caught.$"


