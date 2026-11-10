EventScript_IndigoFieldAgent::
	lock
	faceplayer
	goto_if_set FLAG_INDIGO_MET_AGENT, EventScript_IndigoFieldAgent_TryGive
	msgbox IndigoFieldAgent_Text_Intro, MSGBOX_DEFAULT
	setflag FLAG_INDIGO_MET_AGENT
EventScript_IndigoFieldAgent_TryGive::
	specialvar VAR_RESULT, TryGiveIndigoFieldMoves
	goto_if_eq VAR_RESULT, 0, EventScript_IndigoFieldAgent_NothingNew
	msgbox IndigoFieldAgent_Text_Granted, MSGBOX_DEFAULT
	playfanfare MUS_RG_OBTAIN_KEY_ITEM
	waitfanfare
	goto EventScript_IndigoFieldAgent_TryGive

EventScript_IndigoFieldAgent_NothingNew::
	specialvar VAR_RESULT, CountIndigoFieldMoves
	goto_if_eq VAR_RESULT, NUM_INDIGO_FIELD_MOVES, EventScript_IndigoFieldAgent_AllDone
	msgbox IndigoFieldAgent_Text_ComeBack, MSGBOX_DEFAULT
	release
	end

EventScript_IndigoFieldAgent_AllDone::
	msgbox IndigoFieldAgent_Text_AllDone, MSGBOX_DEFAULT
	release
	end

IndigoFieldAgent_Text_Intro:
	.string "I'm an agent of the Indigo League.\p"
	.string "As you earn type recognition from\n"
	.string "gyms, I'll authorize field techniques\l"
	.string "for your team.$"

IndigoFieldAgent_Text_Granted:
	.string "The League authorizes you to use\n"
	.string "{STR_VAR_1} in the field.$"

IndigoFieldAgent_Text_ComeBack:
	.string "Earn more Indigo recognition, and\n"
	.string "I'll have a new technique for you.$"

IndigoFieldAgent_Text_AllDone:
	.string "That's every field technique I can\n"
	.string "authorize. Use them well.$"

EventScript_IndigoHqGate::
	specialvar VAR_RESULT, CountIndigoGyms
	goto_if_eq VAR_RESULT, NUM_INDIGO_GYMS, EventScript_IndigoHqGatePass
	msgbox IndigoHq_Text_NeedAllEighteen, MSGBOX_DEFAULT
	closemessage
	applymovement LOCALID_PLAYER, Common_Movement_WalkDown
	waitmovement 0
	releaseall
	end

EventScript_IndigoHqGatePass::
	releaseall
	end

EventScript_IndigoHqNotReady::
	msgbox IndigoHq_Text_NeedAllEighteen, MSGBOX_DEFAULT
	release
	end

IndigoHq_Text_NeedAllEighteen:
	.string "Team Indigo HQ opens to Trainers who\n"
	.string "have earned all 18 type recognitions.$"
