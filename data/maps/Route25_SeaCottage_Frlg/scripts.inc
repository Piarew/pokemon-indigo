.equ BILL_IN_TELEPORTER,     FLAG_TEMP_2
.equ RETURN_AFTER_SS_TICKET, FLAG_TEMP_3

Route25_SeaCottage_Frlg_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Route25_SeaCottage_OnTransition
	map_script MAP_SCRIPT_ON_FRAME_TABLE, Route25_SeaCottage_OnFrame
	.byte 0

Route25_SeaCottage_OnTransition::
	call_if_unset FLAG_HELPED_BILL_IN_SEA_COTTAGE, Route25_SeaCottage_EventScript_HideClefairyBill
	call_if_set FLAG_GOT_SS_TICKET, Route25_SeaCottage_EventScript_SetReturnedAfterSSTicket
	end

Route25_SeaCottage_OnFrame::
	map_script_2 VAR_TRAIN, 1, Route25_SeaCottage_EventScript_ExitTrain
	.2byte 0

Route25_SeaCottage_EventScript_HideClefairyBill::
	clearflag FLAG_HIDE_BILL_CLEFAIRY
	setobjectxyperm LOCALID_BILL_HUMAN, 11, 22
	return

Route25_SeaCottage_EventScript_SetReturnedAfterSSTicket::
	setflag RETURN_AFTER_SS_TICKET
	return

Route25_SeaCottage_EventScript_Bill::
	lock
	faceplayer
	goto_if_set RETURN_AFTER_SS_TICKET, Route25_SeaCottage_EventScript_BillGoLookAtPC
	goto_if_set FLAG_GOT_SS_TICKET, Route25_SeaCottage_EventScript_BillGoToSSAnne
	goto_if_set FLAG_HELPED_BILL_IN_SEA_COTTAGE, Route25_SeaCottage_EventScript_BillGiveSSTicket
	checkplayergender
	goto_if_eq VAR_RESULT, MALE, Route25_SeaCottage_EventScript_BillAskForHelpMale
	goto_if_eq VAR_RESULT, FEMALE, Route25_SeaCottage_EventScript_BillAskForHelpFemale
	end

Route25_SeaCottage_EventScript_BillAskForHelpMale::
	msgbox Route25_SeaCottage_Text_ImBillHelpMeOutPal, MSGBOX_YESNO
	goto Route25_SeaCottage_EventScript_BillAskForHelp
	end

Route25_SeaCottage_EventScript_BillAskForHelpFemale::
	msgbox Route25_SeaCottage_Text_ImBillHelpMeOutLady, MSGBOX_YESNO
	goto Route25_SeaCottage_EventScript_BillAskForHelp
	end

Route25_SeaCottage_EventScript_BillAskForHelp::
	call_if_eq VAR_RESULT, NO, Route25_SeaCottage_EventScript_DeclineHelpBill
	msgbox Route25_SeaCottage_Text_RunCellSeparationOnPC
	closemessage
	delay 10
	applymovement LOCALID_BILL_CLEFAIRY, Route25_SeaCottage_Movement_BillEnterSeparator
	waitmovement 0
	playse SE_WARP_IN
	waitse
	removeobject LOCALID_BILL_CLEFAIRY
	setflag BILL_IN_TELEPORTER
	release
	end

@ Just returns after message, execution continues as if player had said yes
Route25_SeaCottage_EventScript_DeclineHelpBill::
	checkplayergender
	call_if_eq VAR_RESULT, MALE, Route25_SeaCottage_EventScript_DeclineHelpBillMale
	call_if_eq VAR_RESULT, FEMALE, Route25_SeaCottage_EventScript_DeclineHelpBillFemale
	return

Route25_SeaCottage_EventScript_DeclineHelpBillMale::
	msgbox Route25_SeaCottage_Text_NoPleaseChief
	return

Route25_SeaCottage_EventScript_DeclineHelpBillFemale::
	msgbox Route25_SeaCottage_Text_NoPleaseBeautiful
	return

Route25_SeaCottage_EventScript_BillGoToSSAnne::
	msgbox Route25_SeaCottage_Text_SSAnnePartyYouGoInstead
	release
	end

Route25_SeaCottage_EventScript_BillGiveSSTicket::
	famechecker FAMECHECKER_BILL, FCPICKSTATE_COLORED, UpdatePickStateFromSpecialVar8005
	checkplayergender
	call_if_eq VAR_RESULT, MALE, Route25_SeaCottage_EventScript_BillThanksMale
	call_if_eq VAR_RESULT, FEMALE, Route25_SeaCottage_EventScript_BillThanksFemale
	checkitemspace ITEM_SS_TICKET
	goto_if_eq VAR_RESULT, FALSE, Route25_SeaCottage_EventScript_NoRoomForSSTicket
	giveitem_msg Route25_SeaCottage_Text_ReceivedSSTicketFromBill, ITEM_SS_TICKET, 1, MUS_RG_OBTAIN_KEY_ITEM
	setflag FLAG_GOT_SS_TICKET_DUP
	setflag FLAG_HIDE_NUGGET_BRIDGE_ROCKET
	setflag FLAG_GOT_SS_TICKET
	setflag FLAG_SYS_PC_LANETTE
	goto Route25_SeaCottage_EventScript_BillGoToSSAnne
	end

Route25_SeaCottage_EventScript_BillThanksMale::
	msgbox Route25_SeaCottage_Text_ThanksBudTakeThis
	return

Route25_SeaCottage_EventScript_BillThanksFemale::
	msgbox Route25_SeaCottage_Text_ThanksLadyTakeThis
	return

Route25_SeaCottage_EventScript_NoRoomForSSTicket::
	msgbox Route25_SeaCottage_Text_YouveGotTooMuchStuff
	release
	end

Route25_SeaCottage_EventScript_BillGoLookAtPC::
	msgbox Route25_SeaCottage_Text_CheckOutRareMonsOnPC
	release
	end

Route25_SeaCottage_Movement_BillEnterSeparator::
	walk_in_place_faster_up
	delay_16
	walk_in_place_faster_up
	step_end

Route25_SeaCottage_EventScript_Computer::
	lockall
	goto_if_set RETURN_AFTER_SS_TICKET, Route25_SeaCottage_EventScript_OpenBillsMonList
	goto_if_set BILL_IN_TELEPORTER, Route25_SeaCottage_EventScript_RunCellSeparator
	msgbox Route25_SeaCottage_Text_TeleporterIsDisplayed
	releaseall
	end

Route25_SeaCottage_EventScript_RunCellSeparator::
	fadeoutbgm 0
	msgbox Route25_SeaCottage_Text_InitiatedTeleportersCellSeparator
	closemessage
	clearflag BILL_IN_TELEPORTER
	setflag FLAG_HELPED_BILL_IN_SEA_COTTAGE
	delay 35
	playse SE_PIN
	waitse
	call Route25_SeaCottage_EventScript_PlayTeleporterBeepSE
	call Route25_SeaCottage_EventScript_PlayTeleporterBeepSE
	call Route25_SeaCottage_EventScript_PlayTeleporterBeepSE
	call Route25_SeaCottage_EventScript_PlayTeleporterBeepSE
	playse SE_WARP_IN
	waitse
	call Route25_SeaCottage_EventScript_PlayTeleporterBeepSE
	call Route25_SeaCottage_EventScript_PlayTeleporterBeepSE
	fadeinbgm 0
	addobject LOCALID_BILL_HUMAN
	clearflag FLAG_HIDE_BILL_HUMAN_SEA_COTTAGE
	delay 50
	playfanfare MUS_LEVEL_UP
	applymovement LOCALID_BILL_HUMAN, Route25_SeaCottage_Movement_BillExitSeparator
	waitmovement 0
	waitfanfare
	releaseall
	end

Route25_SeaCottage_EventScript_PlayTeleporterBeepSE::
	playse SE_BALL
	waitse
	delay 20
	return

Route25_SeaCottage_EventScript_OpenBillsMonList::
	msgbox Route25_SeaCottage_Text_BillsFavoriteMonList
	goto Route25_SeaCottage_EventScript_BillsMonList
	end

Route25_SeaCottage_EventScript_BillsMonList::
	message Route25_SeaCottage_Text_SeeWhichMon
	waitmessage
	multichoice 0, 0, MULTI_EEVEELUTIONS, FALSE
	switch VAR_RESULT
	case 0, Route25_SeaCottage_EventScript_ViewEevee
	case 1, Route25_SeaCottage_EventScript_ViewFlareon
	case 2, Route25_SeaCottage_EventScript_ViewJolteon
	case 3, Route25_SeaCottage_EventScript_ViewVaporeon
	case 4, Route25_SeaCottage_EventScript_ExitBillsMonList
	case 127, Route25_SeaCottage_EventScript_ExitBillsMonList
	end

Route25_SeaCottage_EventScript_ViewEevee::
	showmonpic SPECIES_EEVEE, 10, 3
	waitbuttonpress
	hidemonpic
	setvar VAR_0x8004, SPECIES_EEVEE
	special SetSeenMon
	goto Route25_SeaCottage_EventScript_BillsMonList
	end

Route25_SeaCottage_EventScript_ViewFlareon::
	showmonpic SPECIES_FLAREON, 10, 3
	waitbuttonpress
	hidemonpic
	setvar VAR_0x8004, SPECIES_FLAREON
	special SetSeenMon
	goto Route25_SeaCottage_EventScript_BillsMonList
	end

Route25_SeaCottage_EventScript_ViewJolteon::
	showmonpic SPECIES_JOLTEON, 10, 3
	waitbuttonpress
	hidemonpic
	setvar VAR_0x8004, SPECIES_JOLTEON
	special SetSeenMon
	goto Route25_SeaCottage_EventScript_BillsMonList
	end

Route25_SeaCottage_EventScript_ViewVaporeon::
	showmonpic SPECIES_VAPOREON, 10, 3
	waitbuttonpress
	hidemonpic
	setvar VAR_0x8004, SPECIES_VAPOREON
	special SetSeenMon
	goto Route25_SeaCottage_EventScript_BillsMonList
	end

Route25_SeaCottage_EventScript_ExitBillsMonList::
	releaseall
	end

Route25_SeaCottage_Movement_BillExitSeparator::
	walk_in_place_faster_down
	step_end

Route25_SeaCottage_EventScript_Attendant::
	lock
	faceplayer
	goto_if_unset FLAG_HELPED_BILL_IN_SEA_COTTAGE, Route25_SeaCottage_EventScript_AttendantTrainNotRunning
	msgbox Route25_SeaCottage_Text_OfficerRightThisWay
	closemessage
	applymovement LOCALID_ROUTE25_STATION_ATTENDANT, Route25_SeaCottage_Movement_AttendantMoveUp
	waitmovement 0
	applymovement OBJ_EVENT_ID_PLAYER, Route25_SeaCottage_Movement_WalkToTrain
	waitmovement 0
	special SpawnCameraObject
	applymovement OBJ_EVENT_ID_PLAYER, Common_Movement_WalkUp
	waitmovement 0
	playse SE_EXIT
	waitse
	fadescreen FADE_TO_BLACK
	applymovement OBJ_EVENT_ID_CAMERA, Route25_SeaCottage_Movement_CameraPanUp
	waitmovement 0
	applymovement OBJ_EVENT_ID_CAMERA, Route25_SeaCottage_Movement_CameraPanLeft
	waitmovement 0
	delay 60
	applymovement LOCALID_ROUTE25_STATION_TRAIN, Route25_SeaCottage_Movement_SlideRight
	applymovement OBJ_EVENT_ID_CAMERA, Route25_SeaCottage_Movement_SlideRight
	playbgm MUS_RG_SS_ANNE, FALSE
	fadescreen FADE_FROM_BLACK
	playse SE_TRUCK_MOVE
	delay 220
	playse SE_TRUCK_STOP
	applymovement LOCALID_ROUTE25_STATION_TRAIN, Route25_SeaCottage_Movement_SlideRight
	applymovement OBJ_EVENT_ID_CAMERA, Route25_SeaCottage_Movement_SlideRight
	fadescreen FADE_TO_BLACK
	waitse
	special RemoveCameraObject
	setvar VAR_TRAIN, 1
	delay 60
	warp MAP_SAFFRON_CITY_TRAIN_STATION_HNS, 1
	waitstate
	delay 60
	end

Route25_SeaCottage_EventScript_AttendantTrainNotRunning::
	msgbox Route25_SeaCottage_Text_OfficerTrainNotRunning
	closemessage
	release
	end

Route25_SeaCottage_EventScript_ExitTrain::
	lock
	applymovement LOCALID_ROUTE25_STATION_ATTENDANT, Route25_SeaCottage_Movement_AttendantMoveUp
	applymovement OBJ_EVENT_ID_PLAYER, Route25_SeaCottage_Movement_ExitTrain
	waitmovement 0
	setvar VAR_TRAIN, 0
	applymovement LOCALID_ROUTE25_STATION_ATTENDANT, Route25_SeaCottage_Movement_AttendantMoveDown
	waitmovement 0
	release
	end

Route25_SeaCottage_Movement_ExitTrain::
	walk_down
	walk_left
	walk_left
	walk_left
	walk_down
	walk_down
	walk_down
	step_end

Route25_SeaCottage_Movement_AttendantMoveUp::
	face_up
	walk_up
	walk_left
	face_right
	step_end

Route25_SeaCottage_Movement_AttendantMoveDown::
	walk_right
	walk_down
	step_end

Route25_SeaCottage_Movement_WalkToTrain::
	walk_up
	walk_up
	walk_up
	walk_right
	walk_right
	walk_right
	walk_up
	walk_up
	step_end

Route25_SeaCottage_Movement_CameraPanUp::
	slide_up
	slide_up
	slide_up
	slide_up
	slide_up
	slide_up
	slide_up
	slide_up
	slide_up
	slide_up
	slide_up
	step_end

Route25_SeaCottage_Movement_CameraPanLeft::
	slide_left
	slide_left
	slide_left
	slide_left
	slide_left
	slide_left
	slide_left
	slide_left
	slide_left
	slide_left
	slide_left
	step_end

Route25_SeaCottage_Movement_SlideRight::
	slide_right
	slide_right
	slide_right
	slide_right
	slide_right
	slide_right
	slide_right
	slide_right
	slide_right
	slide_right
	slide_right
	slide_right
	slide_right
	slide_right
	slide_right
	slide_right
	slide_right
	slide_right
	slide_right
	slide_right
	slide_right
	slide_right
	slide_right
	slide_right
	slide_right
	slide_right
	slide_right
	slide_right
	slide_right
	slide_right
	slide_right
	slide_right
	step_end

Route25_SeaCottage_Text_ImBillHelpMeOutPal::
	.string "Hiya! I'm a Pokémon…\n"
	.string "…No I'm not!\p"
	.string "Call me Bill!\n"
	.string "I'm a true-blue Pokémaniac!\p"
	.string "Hey!\n"
	.string "What's with that skeptical look?\p"
	.string "I'm not joshing you, pal.\p"
	.string "I screwed up an experiment and got\n"
	.string "combined with a Pokémon!\p"
	.string "So, how about it?\n"
	.string "Help me out here!$"

Route25_SeaCottage_Text_ImBillHelpMeOutLady::
	.string "Hiya! I'm a Pokémon…\n"
	.string "…No I'm not!\p"
	.string "Call me Bill!\n"
	.string "I'm a true-blue Pokémaniac!\p"
	.string "Hey!\n"
	.string "What's with that skeptical look?\p"
	.string "I'm not joshing you, lady.\p"
	.string "I screwed up an experiment and got\n"
	.string "combined with a Pokémon!\p"
	.string "So, how about it?\n"
	.string "Help me out here!$"

Route25_SeaCottage_Text_RunCellSeparationOnPC::
	.string "Wait till I hop onto the separator\n"
	.string "pad.\p"
	.string "When I do, go to the station PC and\n"
	.string "run the Cell Separation System.$"

Route25_SeaCottage_Text_NoPleaseChief::
	.string "No!?\n"
	.string "Now don't be so cold!\p"
	.string "Come on, you gotta help a guy in\n"
	.string "deep, deep trouble!\p"
	.string "What do you say, chief?\n"
	.string "Please?\p"
	.string "Okay?\n"
	.string "All right!$"

Route25_SeaCottage_Text_NoPleaseBeautiful::
	.string "No!?\n"
	.string "Now don't be so cold!\p"
	.string "Come on, you gotta help a guy in\n"
	.string "deep, deep trouble!\p"
	.string "What do you say, beautiful?\n"
	.string "Please?\p"
	.string "Okay?\n"
	.string "All right!$"

Route25_SeaCottage_Text_ThanksBudTakeThis::
	.string "Bill: Yeehah!\n"
	.string "Thanks, bud! I owe you one!\p"
	.string "So, did you come to see my\n"
	.string "Pokémon collection?\p"
	.string "You didn't?\n"
	.string "That's a bummer.\p"
	.string "I've got to thank you…\n"
	.string "Oh, here, maybe this'll do.$"

Route25_SeaCottage_Text_ThanksLadyTakeThis::
	.string "Bill: Yeehah!\n"
	.string "Thanks, lady! I owe you one!\p"
	.string "So, did you come to see my\n"
	.string "Pokémon collection?\p"
	.string "You didn't?\n"
	.string "That's a bummer.\p"
	.string "I've got to thank you…\n"
	.string "Oh, here, maybe this'll do.$"

Route25_SeaCottage_Text_ReceivedSSTicketFromBill::
	.string "{PLAYER} received an S.S. Ticket\n"
	.string "from Bill.$"

Route25_SeaCottage_Text_YouveGotTooMuchStuff::
	.string "You've got too much stuff!$"

Route25_SeaCottage_Text_SSAnnePartyYouGoInstead::
	.string "That cruise ship S.S. Anne is in\n"
	.string "Vermilion City.\p"
	.string "I hear there are lots of Trainers\n"
	.string "on board, too.\p"
	.string "They invited me to their party, but\n"
	.string "I can't stand fancy do's.\p"
	.string "Why don't you go instead of me?\n"
	.string "Go on and have a good time.$"

Route25_SeaCottage_Text_CheckOutRareMonsOnPC::
	.string "Bill: Feel like checking out some\n"
	.string "of my rare Pokémon on my PC?\p"
	.string "Go on, check out my PC.$"

Route25_SeaCottage_Text_TeleporterIsDisplayed::
	.string "The Cell Separator is displayed on\n"
	.string "the PC monitor.$"

Route25_SeaCottage_Text_InitiatedTeleportersCellSeparator::
	.string "{PLAYER} initiated the Cell\n"
	.string "Separator.$"

Route25_SeaCottage_Text_BillsFavoriteMonList::
	.string "Bill's favorite Pokémon list!$"

Route25_SeaCottage_Text_SeeWhichMon::
	.string "Which Pokémon do you want to see?$"

Route25_SeaCottage_Text_OfficerTrainNotRunning::
	.string "The Magnet Train isn't running.\p"
	.string "Bill's in the middle of an experiment,\n"
	.string "and… well, you should talk to that\p"
	.string "Clefairy.$"

Route25_SeaCottage_Text_OfficerRightThisWay::
	.string "This Magnet Train runs between the\n"
	.string "Cerulean Cape and Saffron City.\p"
	.string "Right this way, please.$"
