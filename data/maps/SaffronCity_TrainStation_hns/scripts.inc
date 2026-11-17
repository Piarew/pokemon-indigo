SaffronCity_TrainStation_hns_MapScripts::
	map_script MAP_SCRIPT_ON_FRAME_TABLE, SaffronStation_OnFrame
	.byte 0

SaffronStation_OnFrame::
	map_script_2 VAR_TRAIN, 1, SaffronStation_EventScript_ExitTrain
	.2byte 0

SaffronStation_EventScript_Nerd::
	goto_if_set FLAG_HELPED_BILL_IN_SEA_COTTAGE, SaffronStation_EventScript_NerdRunning
	msgbox SaffronMagnetTrainStation_Text_GymGuide, MSGBOX_NPC
	end

SaffronStation_EventScript_NerdRunning::
	msgbox SaffronMagnetTrainStation_Text_GymGuideRunning, MSGBOX_NPC
	end

SaffronStation_EventScript_Lass::
	msgbox SaffronMagnetTrainStation_Text_Lass, MSGBOX_NPC
	end

SaffronStation_EventScript_Teacher::
	msgbox SaffronMagnetTrainStation_Text_Teacher, MSGBOX_NPC
	end

SaffronStation_EventScript_Attendant::
	lock
	faceplayer
	goto_if_unset FLAG_HELPED_BILL_IN_SEA_COTTAGE, SaffronStation_EventScript_AttendantTrainNotRunning
	msgbox SaffronMagnetTrainStation_Text_OfficerAskDestination
	dynmultipush SaffronMagnetTrainStation_Text_DestCape, 0
	dynmultipush SaffronMagnetTrainStation_Text_DestOreburgh, 1
	dynmultipush SaffronMagnetTrainStation_Text_DestCancel, 2
	dynmultistack 0, 0, FALSE, 3, FALSE, 0, DYN_MULTICHOICE_CB_NONE
	switch VAR_RESULT
	case 0, SaffronStation_EventScript_BoardToCape
	case 1, SaffronStation_EventScript_BoardToOreburgh
	case 2, SaffronStation_EventScript_AttendantDeclined
	case MULTI_B_PRESSED, SaffronStation_EventScript_AttendantDeclined
	end

SaffronStation_EventScript_BoardToCape::
	msgbox SaffronMagnetTrainStation_Text_OfficerRightThisWay
	closemessage
	call SaffronStation_EventScript_BoardTrain
	warp MAP_ROUTE25_SEA_COTTAGE, 19, 16
	waitstate
	delay 60
	end

SaffronStation_EventScript_BoardToOreburgh::
	msgbox SaffronMagnetTrainStation_Text_OfficerRightThisWay
	closemessage
	call SaffronStation_EventScript_BoardTrain
	warp MAP_OREBURGH_CITY_FLAT3_F1, 19, 16
	waitstate
	delay 60
	end

SaffronStation_EventScript_BoardTrain::
	applymovement LOCALID_SAFFRON_STATION_ATTENDANT, SaffronStation_Movement_AttendantMoveUp
	waitmovement 0
	applymovement OBJ_EVENT_ID_PLAYER, SaffronStation_Movement_WalkToTrain
	waitmovement 0
	special SpawnCameraObject
	applymovement OBJ_EVENT_ID_PLAYER, Common_Movement_WalkUp
	waitmovement 0
	playse SE_EXIT
	waitse
	fadescreen FADE_TO_BLACK
	applymovement OBJ_EVENT_ID_CAMERA, SaffronStation_Movement_CameraPanUp
	waitmovement 0
	applymovement OBJ_EVENT_ID_CAMERA, SaffronStation_Movement_CameraPanRight
	waitmovement 0
	delay 60
	applymovement LOCALID_SAFFRON_STATION_TRAIN, SaffronStation_Movement_SlideLeft
	applymovement OBJ_EVENT_ID_CAMERA, SaffronStation_Movement_SlideLeft
	playbgm MUS_RG_SS_ANNE, FALSE
	fadescreen FADE_FROM_BLACK
	playse SE_TRUCK_MOVE
	delay 220
	playse SE_TRUCK_STOP
	applymovement LOCALID_SAFFRON_STATION_TRAIN, SaffronStation_Movement_SlideLeft
	applymovement OBJ_EVENT_ID_CAMERA, SaffronStation_Movement_SlideLeft
	fadescreen FADE_TO_BLACK
	waitse
	special RemoveCameraObject
	setvar VAR_TRAIN, 1
	delay 60
	return

SaffronStation_EventScript_AttendantTrainNotRunning::
	msgbox SaffronMagnetTrainStation_Text_OfficerTrainNotOperating
	closemessage
	release
	end

SaffronStation_EventScript_AttendantDeclined::
	msgbox SaffronMagnetTrainStation_Text_OfficerHopeToSeeYouAgain
	closemessage
	release
	end

SaffronStation_EventScript_ExitTrain::
	lock
	applymovement LOCALID_SAFFRON_STATION_ATTENDANT, SaffronStation_Movement_AttendantMoveUp
	applymovement OBJ_EVENT_ID_PLAYER, SaffronStation_Movement_ExitTrain
	waitmovement 0
	setvar VAR_TRAIN, 0
	applymovement LOCALID_SAFFRON_STATION_ATTENDANT, SaffronStation_Movement_AttendantMoveDown
	waitmovement 0
	release
	end

SaffronStation_Movement_ExitTrain::
	walk_down
	walk_left
	walk_left
	walk_left
	walk_down
	walk_down
	walk_down
	step_end

SaffronStation_Movement_AttendantMoveUp::
	face_up
	walk_up
	walk_left
	face_right
	step_end

SaffronStation_Movement_AttendantMoveDown::
	walk_right
	walk_down
	step_end

SaffronStation_Movement_WalkToTrain::
	walk_up
	walk_up
	walk_up
	walk_right
	walk_right
	walk_right
	walk_up
	walk_up
	step_end

SaffronStation_Movement_CameraPanUp::
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

SaffronStation_Movement_CameraPanRight::
	slide_right
	slide_right
	slide_right
	slide_right
	slide_right
	slide_right
	step_end

SaffronStation_Movement_SlideLeft::
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

SaffronMagnetTrainStation_Text_OfficerAskDestination::
	.string "The Magnet Train is running.\n"
	.string "Where would you like to go?$"

SaffronMagnetTrainStation_Text_DestCape::
	.string "Cerulean Cape$"

SaffronMagnetTrainStation_Text_DestOreburgh::
	.string "Oreburgh City$"

SaffronMagnetTrainStation_Text_DestCancel::
	.string "Cancel$"

SaffronMagnetTrainStation_Text_OfficerComingAboard::
	.string "We'll soon depart for the Cerulean\n"
	.string "Cape.\p"
	.string "Are you coming aboard?$"

SaffronMagnetTrainStation_Text_OfficerRightThisWay::
	.string "Right this way, please.$"

SaffronMagnetTrainStation_Text_OfficerHopeToSeeYouAgain::
	.string "We hope to see you again!$"

SaffronMagnetTrainStation_Text_OfficerTrainNotOperating::
	.string "I'm sorry, but the Magnet Train\n"
	.string "isn't operating now.$"

SaffronMagnetTrainStation_Text_GymGuide::
	.string "The Magnet Train is a super-modern\n"
	.string "rail liner that uses electricity\p"
	.string "and magnets to attain incredible\n"
	.string "speed.\p"
	.string "However, if there isn't any\n"
	.string "electricity…$"

SaffronMagnetTrainStation_Text_GymGuideRunning::
	.string "Whew…\p"
	.string "How many times have I gone back\n"
	.string "and forth between Saffron and the\l"
	.string "Cerulean Cape?$"

SaffronMagnetTrainStation_Text_Teacher::
	.string "Before the Magnet Train Station\n"
	.string "was built, there was a house there.\p"
	.string "A little girl named Copycat used\n"
	.string "to live there.$"

SaffronMagnetTrainStation_Text_Lass::
	.string "Hi. This train goes to the Cerulean\n"
	.string "Cape, where Bill lives, and through\l"
	.string "the mountain to Oreburgh.$"
