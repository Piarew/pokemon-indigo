EventScript_UseTimeChanger::
	lockall
	message TimeChanger_Text_WhichTime
	waitmessage
	dynmultipush TimeChanger_Text_Morning, 0
	dynmultipush TimeChanger_Text_Day, 1
	dynmultipush TimeChanger_Text_Evening, 2
	dynmultipush TimeChanger_Text_Night, 3
	dynmultistack 0, 0, FALSE, 4, FALSE, 0, DYN_MULTICHOICE_CB_NONE
	goto_if_eq VAR_RESULT, MULTI_B_PRESSED, EventScript_UseTimeChangerEnd
	fadescreenswapbuffers FADE_TO_BLACK
	callnative Script_SetTimeOfDayFromResult, requests_effects=1
	fadescreenswapbuffers FADE_FROM_BLACK
EventScript_UseTimeChangerEnd::
	releaseall
	end

TimeChanger_Text_WhichTime:
	.string "Change the time of day to…$"

TimeChanger_Text_Morning:
	.string "Morning$"

TimeChanger_Text_Day:
	.string "Day$"

TimeChanger_Text_Evening:
	.string "Evening$"

TimeChanger_Text_Night:
	.string "Night$"
