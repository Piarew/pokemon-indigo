@ Indigo City Battle Club rematches (src/indigo_rematch.c).
@ Each Kanto leader script starts with:
@	specialvar VAR_RESULT, IndigoRematch_GetVisitState
@	goto_if_ne VAR_RESULT, INDIGO_REMATCH_NONE, <Gym>_EventScript_<Leader>Rematch
@ and the rematch block is:
@	lock / faceplayer
@	goto_if_eq VAR_RESULT, INDIGO_REMATCH_DONE_TODAY, EventScript_IndigoRematchDoneToday
@	msgbox Text_IndigoRematchIntro
@	trainerbattle_no_intro TRAINER_LEADER_X, Text_IndigoRematchDefeat
@	goto EventScript_IndigoRematchWon
@ trainerbattle_no_intro ignores the trainer's defeated flag; party levels are
@ scaled to the level cap in CreateNPCTrainerParty. No badge, TM, or story flags.

EventScript_IndigoRematchWon::
	special IndigoRematch_SetDoneToday
	msgbox Text_IndigoRematchPostBattle
	release
	end

EventScript_IndigoRematchDoneToday::
	msgbox Text_IndigoRematchDoneToday
	release
	end

Text_IndigoRematchIntro::
	.string "So the Battle Club sent you!\p"
	.string "My team has grown alongside yours.\n"
	.string "Let's see how strong you've become!$"

Text_IndigoRematchDefeat::
	.string "Impressive…\n"
	.string "You're even stronger than before.$"

Text_IndigoRematchPostBattle::
	.string "That was a great battle.\p"
	.string "The Battle Club picks a new\n"
	.string "challenger every day. Come again!$"

Text_IndigoRematchDoneToday::
	.string "We already battled today.\p"
	.string "Check the Battle Club tomorrow\n"
	.string "for your next challenge!$"
