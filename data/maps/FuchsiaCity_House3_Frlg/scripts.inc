FuchsiaCity_House3_Frlg_MapScripts::
	.byte 0

FuchsiaCity_House3_EventScript_MoveDeleter::
	lock
	faceplayer
	msgbox FuchsiaCity_House3_Text_WouldYouLikeToForgetMove, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, YES, FuchsiaCity_House3_EventScript_ChooseMonForMoveDeleter
	goto FuchsiaCity_House3_EventScript_CancelForgetMove
	end

FuchsiaCity_House3_EventScript_ChooseMonForMoveDeleter::
	msgbox FuchsiaCity_House3_Text_WhichMonShouldForgetMove
	special ChoosePartyMon
	goto_if_ge VAR_0x8004, PARTY_SIZE, FuchsiaCity_House3_EventScript_CancelForgetMove
	special IsSelectedMonEgg
	goto_if_eq VAR_RESULT, TRUE, FuchsiaCity_House3_EventScript_CantForgetMoveEgg
	special GetNumMovesSelectedMonHas
	goto_if_eq VAR_RESULT, 1, FuchsiaCity_House3_EventScript_CantForgetOnlyMove
	msgbox FuchsiaCity_House3_Text_WhichMoveShouldBeForgotten
	fadescreen FADE_TO_BLACK
	special MoveDeleterChooseMoveToForget
	fadescreen FADE_FROM_BLACK
	goto_if_eq VAR_0x8005, MAX_MON_MOVES, FuchsiaCity_House3_EventScript_ChooseMonForMoveDeleter
	special BufferMoveDeleterNicknameAndMove
	msgbox FuchsiaCity_House3_Text_MonsMoveShouldBeForgotten, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, YES, FuchsiaCity_House3_EventScript_ForgetMove
	goto FuchsiaCity_House3_EventScript_CancelForgetMove
	end

FuchsiaCity_House3_EventScript_ForgetMove::
	special MoveDeleterForgetMove
	playfanfare MUS_MOVE_DELETED
	waitfanfare
	msgbox FuchsiaCity_House3_Text_MonHasForgottenMoveCompletely
	release
	end

FuchsiaCity_House3_EventScript_CantForgetOnlyMove::
	special BufferMoveDeleterNicknameAndMove
	msgbox FuchsiaCity_House3_Text_MonOnlyKnowsOneMove
	release
	end

FuchsiaCity_House3_EventScript_CantForgetMoveEgg::
	msgbox FuchsiaCity_House3_Text_NoEggShouldKnowMoves
	release
	end

FuchsiaCity_House3_EventScript_CancelForgetMove::
	msgbox FuchsiaCity_House3_Text_ComeAgainToForgetOtherMoves
	release
	end

FuchsiaCity_House3_Text_WouldYouLikeToForgetMove::
	.string "Uh…\n"
	.string "Oh, yes, I'm the Move Deleter.\p"
	.string "I can make Pokémon forget their\n"
	.string "moves.\p"
	.string "Would you like me to do that?$"

FuchsiaCity_House3_Text_WhichMonShouldForgetMove::
	.string "Which Pokémon should forget a\n"
	.string "move?$"

FuchsiaCity_House3_Text_WhichMoveShouldBeForgotten::
	.string "Which move should be forgotten?$"

FuchsiaCity_House3_Text_MonOnlyKnowsOneMove::
	.string "{STR_VAR_1} seems to know only one\n"
	.string "move…$"

FuchsiaCity_House3_Text_MonsMoveShouldBeForgotten::
	.string "Hm! {STR_VAR_1}'s {STR_VAR_2}?\n"
	.string "That move should be forgotten?$"

FuchsiaCity_House3_Text_MonHasForgottenMoveCompletely::
	.string "It worked to perfection!\p"
	.string "{STR_VAR_1} has forgotten\n"
	.string "{STR_VAR_2} completely.$"

FuchsiaCity_House3_Text_ComeAgainToForgetOtherMoves::
	.string "Come again if there are other\n"
	.string "moves to be forgotten.$"

FuchsiaCity_House3_Text_NoEggShouldKnowMoves::
	.string "What?\n"
	.string "No Egg should know any moves.$"

FuchsiaCity_House3_EventScript_MoveDistiller::
	lock
	faceplayer
@ Debug: Distiller is in Oak's lab; skip the Champion gate so he can be tested immediately.
@	goto_if_unset FLAG_SYS_GAME_CLEAR, FuchsiaCity_House3_EventScript_DistillerNotReady
	msgbox FuchsiaCity_House3_Text_DistillerIntro
	dynmultipush FuchsiaCity_House3_Text_DistillerDonate, 0
	dynmultipush FuchsiaCity_House3_Text_DistillerTeach, 1
	dynmultipush FuchsiaCity_House3_Text_DistillerNeverMind, 2
	dynmultistack 0, 0, FALSE, 3, FALSE, 0, DYN_MULTICHOICE_CB_NONE
	switch VAR_RESULT
	case 0, FuchsiaCity_House3_EventScript_DistillerDonate
	case 1, FuchsiaCity_House3_EventScript_DistillerTeach
	goto FuchsiaCity_House3_EventScript_DistillerCancel
	end

FuchsiaCity_House3_EventScript_DistillerNotReady::
	msgbox FuchsiaCity_House3_Text_DistillerNotReady
	release
	end

FuchsiaCity_House3_EventScript_DistillerCancel::
	msgbox FuchsiaCity_House3_Text_DistillerComeAgain
	release
	end

FuchsiaCity_House3_EventScript_DistillerDonate::
	msgbox FuchsiaCity_House3_Text_DistillerWhichMon
	special ChoosePartyMon
	goto_if_ge VAR_0x8004, PARTY_SIZE, FuchsiaCity_House3_EventScript_DistillerCancel
	special DistillerInspectSelectedMon
	switch VAR_RESULT
	case DISTILLER_ERR_EGG, FuchsiaCity_House3_EventScript_DistillerEgg
	case DISTILLER_ERR_LAST_MON, FuchsiaCity_House3_EventScript_DistillerLastMon
	case DISTILLER_ERR_NOT_SINGLE_MOVE, FuchsiaCity_House3_EventScript_DistillerNotSingleMove
	case DISTILLER_ERR_FORBIDDEN_MOVE, FuchsiaCity_House3_EventScript_DistillerForbiddenMove
	msgbox FuchsiaCity_House3_Text_DistillerConfirmDonate, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, FuchsiaCity_House3_EventScript_DistillerCancel
	special DistillerDonateSelectedMon
	switch VAR_RESULT
	case DISTILLER_ERR_BAG_FULL, FuchsiaCity_House3_EventScript_DistillerBagFull
	case DISTILLER_OK_TM, FuchsiaCity_House3_EventScript_DistillerGaveTM
	case DISTILLER_OK_ALREADY_HAD_TM, FuchsiaCity_House3_EventScript_DistillerAlreadyHadTM
	case DISTILLER_OK_ARCHIVED, FuchsiaCity_House3_EventScript_DistillerArchived
	goto FuchsiaCity_House3_EventScript_DistillerCancel
	end

FuchsiaCity_House3_EventScript_DistillerEgg::
	msgbox FuchsiaCity_House3_Text_DistillerNoEgg
	release
	end

FuchsiaCity_House3_EventScript_DistillerLastMon::
	msgbox FuchsiaCity_House3_Text_DistillerLastMon
	release
	end

FuchsiaCity_House3_EventScript_DistillerNotSingleMove::
	msgbox FuchsiaCity_House3_Text_DistillerNotSingleMove
	release
	end

FuchsiaCity_House3_EventScript_DistillerForbiddenMove::
	msgbox FuchsiaCity_House3_Text_DistillerForbiddenMove
	release
	end

FuchsiaCity_House3_EventScript_DistillerBagFull::
	msgbox FuchsiaCity_House3_Text_DistillerBagFull
	release
	end

FuchsiaCity_House3_EventScript_DistillerGaveTM::
	msgbox FuchsiaCity_House3_Text_DistillerPressedDisc
	giveitem VAR_0x8000
	msgbox FuchsiaCity_House3_Text_DistillerCanTeachToo
	release
	end

FuchsiaCity_House3_EventScript_DistillerAlreadyHadTM::
	msgbox FuchsiaCity_House3_Text_DistillerAlreadyHadTM
	release
	end

FuchsiaCity_House3_EventScript_DistillerArchived::
	msgbox FuchsiaCity_House3_Text_DistillerArchived
	release
	end

FuchsiaCity_House3_EventScript_DistillerTeach::
	special DistillerHasArchivedMoves
	goto_if_eq VAR_RESULT, FALSE, FuchsiaCity_House3_EventScript_DistillerNoArchive
	msgbox FuchsiaCity_House3_Text_DistillerWhichMove
	special DistillerChooseArchivedMove
	goto_if_eq VAR_RESULT, FALSE, FuchsiaCity_House3_EventScript_DistillerCancel
	msgbox FuchsiaCity_House3_Text_DistillerWhichMonTeach
	special DistillerSetTutorActive
	special ChooseMonForMoveTutor
	special DistillerClearTutorActive
	goto_if_eq VAR_RESULT, FALSE, FuchsiaCity_House3_EventScript_DistillerTeachDeclined
	msgbox FuchsiaCity_House3_Text_DistillerTaught
	release
	end

FuchsiaCity_House3_EventScript_DistillerNoArchive::
	msgbox FuchsiaCity_House3_Text_DistillerNoArchive
	release
	end

FuchsiaCity_House3_EventScript_DistillerTeachDeclined::
	msgbox FuchsiaCity_House3_Text_DistillerTeachDeclined
	release
	end

FuchsiaCity_House3_Text_DistillerNotReady::
	.string "I'm assembling a press that can\n"
	.string "capture a Pokémon's only technique.\p"
	.string "Come see me after you've become\n"
	.string "Champion. I'll be ready then.$"

FuchsiaCity_House3_Text_DistillerIntro::
	.string "I'm Indigo's Move Distiller.\p"
	.string "Donate a Pokémon that knows exactly\n"
	.string "one move, and I'll press that\l"
	.string "technique into a disc.\p"
	.string "I keep the Pokémon. The Move Deleter\n"
	.string "here can strip extras first.$"

FuchsiaCity_House3_Text_DistillerDonate::
	.string "Donate a Pokémon$"

FuchsiaCity_House3_Text_DistillerTeach::
	.string "Teach a distilled move$"

FuchsiaCity_House3_Text_DistillerNeverMind::
	.string "Never mind$"

FuchsiaCity_House3_Text_DistillerComeAgain::
	.string "Come again if you have a specialist\n"
	.string "to donate.$"

FuchsiaCity_House3_Text_DistillerWhichMon::
	.string "Which Pokémon will you donate?$"

FuchsiaCity_House3_Text_DistillerConfirmDonate::
	.string "{STR_VAR_1} knows only {STR_VAR_2}.\p"
	.string "I'll keep {STR_VAR_1} forever.\n"
	.string "Is that acceptable?$"

FuchsiaCity_House3_Text_DistillerNoEgg::
	.string "I can't extract a technique from\n"
	.string "an Egg.$"

FuchsiaCity_House3_Text_DistillerLastMon::
	.string "That's your last battle-ready\n"
	.string "Pokémon. I won't take it.$"

FuchsiaCity_House3_Text_DistillerNotSingleMove::
	.string "{STR_VAR_1} still knows more than one\n"
	.string "move.\p"
	.string "Ask the Move Deleter to strip it\n"
	.string "down to a single technique first.$"

FuchsiaCity_House3_Text_DistillerForbiddenMove::
	.string "{STR_VAR_2} can't be pressed onto a\n"
	.string "disc. I won't take that Pokémon.$"

FuchsiaCity_House3_Text_DistillerBagFull::
	.string "Your TM Case is full.\n"
	.string "Make space, then come back.$"

FuchsiaCity_House3_Text_DistillerPressedDisc::
	.string "Marvelous! {STR_VAR_1} knew only\n"
	.string "{STR_VAR_2}. I'll press a disc.$"

FuchsiaCity_House3_Text_DistillerCanTeachToo::
	.string "I've also recorded that technique.\n"
	.string "I can teach it to any Pokémon.$"

FuchsiaCity_House3_Text_DistillerAlreadyHadTM::
	.string "You already have a disc for\n"
	.string "{STR_VAR_2}.\p"
	.string "I'll keep {STR_VAR_1} anyway, and I\n"
	.string "can teach that move to anyone.$"

FuchsiaCity_House3_Text_DistillerArchived::
	.string "There's no factory disc for\n"
	.string "{STR_VAR_2}.\p"
	.string "I've recorded it myself. Talk to me\n"
	.string "again, and I can teach it to any\l"
	.string "Pokémon.$"

FuchsiaCity_House3_Text_DistillerNoArchive::
	.string "I haven't recorded any techniques\n"
	.string "yet. Donate a specialist first.$"

FuchsiaCity_House3_Text_DistillerWhichMove::
	.string "Which recorded technique should I\n"
	.string "teach?$"

FuchsiaCity_House3_Text_DistillerWhichMonTeach::
	.string "Teach it to which Pokémon?$"

FuchsiaCity_House3_Text_DistillerTaught::
	.string "The technique took hold.\n"
	.string "Use it well.$"

FuchsiaCity_House3_Text_DistillerTeachDeclined::
	.string "Changed your mind?\n"
	.string "The record remains.$"

