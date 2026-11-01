CyclingRoadWestGate_1F_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, CyclingRoadWestGate_1F_OnTransition
	.byte 0

CyclingRoadWestGate_1F_OnTransition::
	clearflag FLAG_SYS_ON_CYCLING_ROAD
	call_if_set FLAG_GOT_BICYCLE, CyclingRoadWestGate_1F_EventScript_DisableNeedBikeTrigger
	end

CyclingRoadWestGate_1F_EventScript_DisableNeedBikeTrigger::
	setvar VAR_TEMP_1, 1
	return

CyclingRoadWestGate_1F_EventScript_Guard::
	msgbox CyclingRoadWestGate_1F_Text_CyclingRoadIsDownhillCourse, MSGBOX_NPC
	end

CyclingRoadWestGate_1F_EventScript_NeedBikeTriggerTop::
	lockall
	setvar VAR_0x8008, 0
	goto CyclingRoadWestGate_1F_EventScript_NeedBikeTrigger
	end

CyclingRoadWestGate_1F_EventScript_NeedBikeTriggerMidTop::
	lockall
	setvar VAR_0x8008, 1
	goto CyclingRoadWestGate_1F_EventScript_NeedBikeTrigger
	end

CyclingRoadWestGate_1F_EventScript_NeedBikeTriggerMid::
	lockall
	setvar VAR_0x8008, 2
	goto CyclingRoadWestGate_1F_EventScript_NeedBikeTrigger
	end

CyclingRoadWestGate_1F_EventScript_NeedBikeTriggerMidBottom::
	lockall
	setvar VAR_0x8008, 3
	goto CyclingRoadWestGate_1F_EventScript_NeedBikeTrigger
	end

CyclingRoadWestGate_1F_EventScript_NeedBikeTriggerBottom::
	lockall
	setvar VAR_0x8008, 4
	goto CyclingRoadWestGate_1F_EventScript_NeedBikeTrigger
	end

CyclingRoadWestGate_1F_EventScript_NeedBikeTrigger::
	textcolor NPC_TEXT_COLOR_MALE
	msgbox CyclingRoadWestGate_1F_Text_ExcuseMeWaitUp
	closemessage
	applymovement LOCALID_PLAYER, Common_Movement_WalkInPlaceFasterUp
	waitmovement 0
	delay 20
	call_if_eq VAR_0x8008, 1, CyclingRoadWestGate_1F_EventScript_PlayerWalkToCounterMidTop
	call_if_eq VAR_0x8008, 2, CyclingRoadWestGate_1F_EventScript_PlayerWalkToCounterMid
	call_if_eq VAR_0x8008, 3, CyclingRoadWestGate_1F_EventScript_PlayerWalkToCounterMidBottom
	call_if_eq VAR_0x8008, 4, CyclingRoadWestGate_1F_EventScript_PlayerWalkToCounterBottom
	msgbox CyclingRoadWestGate_1F_Text_NoPedestriansOnCyclingRoad
	closemessage
	applymovement LOCALID_PLAYER, CyclingRoadWestGate_1F_Movement_WalkLeft
	waitmovement 0
	releaseall
	end

CyclingRoadWestGate_1F_EventScript_PlayerWalkToCounterMidTop::
	applymovement LOCALID_PLAYER, CyclingRoadWestGate_1F_Movement_WalkUp
	waitmovement 0
	return

CyclingRoadWestGate_1F_EventScript_PlayerWalkToCounterMid::
	applymovement LOCALID_PLAYER, CyclingRoadWestGate_1F_Movement_WalkUp2
	waitmovement 0
	return

CyclingRoadWestGate_1F_EventScript_PlayerWalkToCounterMidBottom::
	applymovement LOCALID_PLAYER, CyclingRoadWestGate_1F_Movement_WalkUp3
	waitmovement 0
	return

CyclingRoadWestGate_1F_EventScript_PlayerWalkToCounterBottom::
	applymovement LOCALID_PLAYER, CyclingRoadWestGate_1F_Movement_WalkUp4
	waitmovement 0
	return

CyclingRoadWestGate_1F_Movement_WalkUp::
	walk_up
	step_end

CyclingRoadWestGate_1F_Movement_WalkUp2::
	walk_up
	walk_up
	step_end

CyclingRoadWestGate_1F_Movement_WalkUp3::
	walk_up
	walk_up
	walk_up
	step_end

CyclingRoadWestGate_1F_Movement_WalkUp4::
	walk_up
	walk_up
	walk_up
	walk_up
	step_end

CyclingRoadWestGate_1F_Movement_WalkLeft::
	walk_left
	step_end

CyclingRoadWestGate_1F_EventScript_OldMan::
	msgbox CyclingRoadWestGate_1F_Text_HowdYouGetInGoodEffort, MSGBOX_NPC
	end

CyclingRoadWestGate_1F_Text_NoPedestriansOnCyclingRoad::
	.string "No pedestrians are allowed on\n"
	.string "CYCLING ROAD!$"

CyclingRoadWestGate_1F_Text_CyclingRoadIsDownhillCourse::
	.string "CYCLING ROAD WEST climbs all the\n"
	.string "way to CELADON. Good luck!$"

CyclingRoadWestGate_1F_Text_ExcuseMeWaitUp::
	.string "Excuse me!\n"
	.string "Wait up, please!$"

CyclingRoadWestGate_1F_Text_HowdYouGetInGoodEffort::
	.string "How'd you get in?\n"
	.string "Good effort!$"

