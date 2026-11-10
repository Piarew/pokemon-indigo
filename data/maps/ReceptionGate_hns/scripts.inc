ReceptionGate_hns_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, ReceptionGate_OnTransition
	.byte 0

ReceptionGate_OnTransition::
	specialvar VAR_RESULT, CountIndigoGyms
	goto_if_eq VAR_RESULT, NUM_INDIGO_GYMS, ReceptionGate_EventScript_UnlockVictoryRoad
	setvar VAR_TEMP_1, 0
	end

ReceptionGate_EventScript_UnlockVictoryRoad::
	setvar VAR_TEMP_1, 1
	end

ReceptionGate_EventScript_VictoryRoadGate::
	lockall
	goto_if_ne VAR_FACING, DIR_NORTH, ReceptionGate_EventScript_VictoryRoadGateRelease
	goto EventScript_IndigoHqGate

ReceptionGate_EventScript_VictoryRoadGateRelease::
	releaseall
	end

ReceptionGate_EventScript_SinnohGuide::
	lock
	faceplayer
	msgbox ReceptionGate_Text_OfferSinnoh, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, ReceptionGate_EventScript_SinnohGuideDeclined
	closemessage
	fadescreen FADE_TO_BLACK
	setrespawn HEAL_LOCATION_TWINLEAF_TOWN
	warp MAP_TWINLEAF_TOWN, 16, 19
	waitstate
	end

ReceptionGate_EventScript_SinnohGuideDeclined::
	msgbox ReceptionGate_Text_SinnohGuideDeclined, MSGBOX_DEFAULT
	release
	end

ReceptionGate_Text_OfferSinnoh::
	.string "This gate links Johto and Kanto.\p"
	.string "I can send you on to Sinnoh from\n"
	.string "here, if you like.\p"
	.string "Travel to Twinleaf Town?$"

ReceptionGate_Text_SinnohGuideDeclined::
	.string "Very well. I'll be here when you're\n"
	.string "ready.$"
