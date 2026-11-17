OreburghCity_Flat3_F1_MapScripts::
	map_script MAP_SCRIPT_ON_FRAME_TABLE, OreburghStation_OnFrame
	.byte 0

OreburghStation_OnFrame::
	map_script_2 VAR_TRAIN, 1, OreburghStation_EventScript_ExitTrain
	.2byte 0

OreburghStation_EventScript_Hiker::
	msgbox OreburghStation_Text_Hiker, MSGBOX_NPC
	end

OreburghStation_EventScript_Worker::
	msgbox OreburghStation_Text_Worker, MSGBOX_NPC
	end

OreburghStation_EventScript_Attendant::
	lock
	faceplayer
	goto_if_unset FLAG_HELPED_BILL_IN_SEA_COTTAGE, OreburghStation_EventScript_AttendantTrainNotRunning
	msgbox OreburghStation_Text_OfficerComingAboard, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, OreburghStation_EventScript_AttendantDeclined
	msgbox OreburghStation_Text_OfficerRightThisWay
	closemessage
	applymovement LOCALID_OREBURGH_STATION_ATTENDANT, OreburghStation_Movement_AttendantMoveUp
	waitmovement 0
	applymovement OBJ_EVENT_ID_PLAYER, OreburghStation_Movement_WalkToTrain
	waitmovement 0
	special SpawnCameraObject
	applymovement OBJ_EVENT_ID_PLAYER, Common_Movement_WalkUp
	waitmovement 0
	playse SE_EXIT
	waitse
	fadescreen FADE_TO_BLACK
	applymovement OBJ_EVENT_ID_CAMERA, OreburghStation_Movement_CameraPanUp
	waitmovement 0
	applymovement OBJ_EVENT_ID_CAMERA, OreburghStation_Movement_CameraPanLeft
	waitmovement 0
	delay 60
	applymovement LOCALID_OREBURGH_STATION_TRAIN, OreburghStation_Movement_SlideRight
	applymovement OBJ_EVENT_ID_CAMERA, OreburghStation_Movement_SlideRight
	playbgm MUS_RG_SS_ANNE, FALSE
	fadescreen FADE_FROM_BLACK
	playse SE_TRUCK_MOVE
	delay 220
	playse SE_TRUCK_STOP
	applymovement LOCALID_OREBURGH_STATION_TRAIN, OreburghStation_Movement_SlideRight
	applymovement OBJ_EVENT_ID_CAMERA, OreburghStation_Movement_SlideRight
	fadescreen FADE_TO_BLACK
	waitse
	special RemoveCameraObject
	setvar VAR_TRAIN, 1
	delay 60
	warp MAP_SAFFRON_CITY_TRAIN_STATION_HNS, 1
	waitstate
	delay 60
	end

OreburghStation_EventScript_AttendantTrainNotRunning::
	msgbox OreburghStation_Text_OfficerTrainNotOperating
	closemessage
	release
	end

OreburghStation_EventScript_AttendantDeclined::
	msgbox OreburghStation_Text_OfficerHopeToSeeYouAgain
	closemessage
	release
	end

OreburghStation_EventScript_ExitTrain::
	lock
	applymovement LOCALID_OREBURGH_STATION_ATTENDANT, OreburghStation_Movement_AttendantMoveUp
	applymovement OBJ_EVENT_ID_PLAYER, OreburghStation_Movement_ExitTrain
	waitmovement 0
	setvar VAR_TRAIN, 0
	applymovement LOCALID_OREBURGH_STATION_ATTENDANT, OreburghStation_Movement_AttendantMoveDown
	waitmovement 0
	release
	end

OreburghStation_Movement_ExitTrain::
	walk_down
	walk_left
	walk_left
	walk_left
	walk_down
	walk_down
	walk_down
	step_end

OreburghStation_Movement_AttendantMoveUp::
	face_up
	walk_up
	walk_left
	face_right
	step_end

OreburghStation_Movement_AttendantMoveDown::
	walk_right
	walk_down
	step_end

OreburghStation_Movement_WalkToTrain::
	walk_up
	walk_up
	walk_up
	walk_right
	walk_right
	walk_right
	walk_up
	walk_up
	step_end

OreburghStation_Movement_CameraPanUp::
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

OreburghStation_Movement_CameraPanLeft::
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

OreburghStation_Movement_SlideRight::
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

OreburghStation_Text_Hiker::
	.string "They blasted this subway straight\n"
	.string "through the mountain.\p"
	.string "Takes you all the way to Kanto,\n"
	.string "if the line's running.$"

OreburghStation_Text_Worker::
	.string "I helped dig the tunnel.\p"
	.string "Never thought I'd see a train\n"
	.string "under Oreburgh.$"

OreburghStation_Text_OfficerComingAboard::
	.string "This subway runs through the mountain\n"
	.string "to Saffron City.\p"
	.string "Are you coming aboard?$"

OreburghStation_Text_OfficerRightThisWay::
	.string "Right this way, please.$"

OreburghStation_Text_OfficerHopeToSeeYouAgain::
	.string "We hope to see you again!$"

OreburghStation_Text_OfficerTrainNotOperating::
	.string "I'm sorry, but the subway isn't\n"
	.string "running to Kanto yet.\p"
	.string "Bill's still working out the line\n"
	.string "on the Cerulean Cape.$"
