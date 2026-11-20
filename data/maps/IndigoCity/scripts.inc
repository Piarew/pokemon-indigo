IndigoCity_MapScripts::
	map_script MAP_SCRIPT_ON_LOAD, IndigoCity_OnLoad
	map_script MAP_SCRIPT_ON_TRANSITION, IndigoCity_OnTransition
	.byte 0

@ Battle Club (east gym): daily rotating rematch gym, see src/indigo_rematch.c.
@ With no eligible gym cleared yet the door is bricked up (0x15B door -> 0x314 wall).
IndigoCity_OnLoad::
	specialvar VAR_RESULT, IndigoRematch_UpdateDaily
	call_if_eq VAR_RESULT, 0, IndigoCity_EventScript_LockBattleClub
	end

IndigoCity_EventScript_LockBattleClub::
	setmetatile 42, 15, 0x314, TRUE
	return

IndigoCity_OnTransition::
	specialvar VAR_RESULT, CountIndigoGyms
	goto_if_eq VAR_RESULT, NUM_INDIGO_GYMS, IndigoCity_EventScript_UnlockVictoryRoad
	setvar VAR_TEMP_1, 0
	end

IndigoCity_EventScript_UnlockVictoryRoad::
	setvar VAR_TEMP_1, 1
	end

IndigoCity_EventScript_VictoryRoadGate::
	lockall
	goto_if_ne VAR_FACING, DIR_NORTH, IndigoCity_EventScript_VictoryRoadGateRelease
	goto EventScript_IndigoHqGate

IndigoCity_EventScript_VictoryRoadGateRelease::
	releaseall
	end

IndigoCity_EventScript_BattleClubDoor::
	lockall
	specialvar VAR_RESULT, IndigoRematch_UpdateDaily
	goto_if_eq VAR_RESULT, 0, IndigoCity_EventScript_BattleClubLocked
	special IndigoRematch_BufferLeaderName
	msgbox IndigoCity_Text_BattleClubToday
	releaseall
	end

IndigoCity_EventScript_BattleClubLocked::
	msgbox IndigoCity_Text_BattleClubLocked
	releaseall
	end

IndigoCity_Text_BattleClubToday::
	.string "INDIGO BATTLE CLUB\p"
	.string "Today's challenger:\n"
	.string "the {STR_VAR_1} Gym Leader.\p"
	.string "The challenger changes daily.$"

IndigoCity_Text_BattleClubLocked::
	.string "The door is locked.\p"
	.string "INDIGO BATTLE CLUB\p"
	.string "Open to Trainers who have earned\n"
	.string "at least one type recognition.$"

IndigoCity_EventScript_Greeter::
	msgbox IndigoCity_Text_Greeter, MSGBOX_NPC
	end

IndigoCity_EventScript_BureauWoman::
	msgbox IndigoCity_Text_BureauWoman, MSGBOX_NPC
	end

IndigoCity_EventScript_ClubWatcher::
	msgbox IndigoCity_Text_ClubWatcher, MSGBOX_NPC
	end

IndigoCity_EventScript_Boy::
	msgbox IndigoCity_Text_Boy, MSGBOX_NPC
	end

IndigoCity_EventScript_FatMan::
	msgbox IndigoCity_Text_FatMan, MSGBOX_NPC
	end

IndigoCity_EventScript_HqWatcher::
	msgbox IndigoCity_Text_HqWatcher, MSGBOX_NPC
	end

IndigoCity_EventScript_CitySign::
	msgbox IndigoCity_Text_CitySign, MSGBOX_SIGN
	end

IndigoCity_EventScript_BureauSign::
	msgbox IndigoCity_Text_BureauSign, MSGBOX_SIGN
	end

IndigoCity_EventScript_HqSign::
	msgbox IndigoCity_Text_HqSign, MSGBOX_SIGN
	end

IndigoCity_Text_Greeter::
	.string "Welcome to Indigo City.\p"
	.string "The company lives here.\n"
	.string "The gyms live everywhere else.\p"
	.string "If you only have a map, walk.\p"
	.string "If you have two recognitions,\n"
	.string "the Bureau will take your name.$"

IndigoCity_Text_BureauWoman::
	.string "That's the Field Bureau.\n"
	.string "ODETTE keeps the desk.\p"
	.string "Two stamps, then she points you at\n"
	.string "Johto. Cherrygrove. A Normal gym.\p"
	.string "ARLO, if the paperwork is honest.$"

IndigoCity_Text_ClubWatcher::
	.string "The Battle Club opens after one\n"
	.string "recognition.\p"
	.string "VELVET watches from the steps\n"
	.string "when HQ wants a picture.\p"
	.string "Today the steps are empty.\n"
	.string "That is also a kind of message.$"

IndigoCity_Text_Boy::
	.string "A man in a navy coat walked by\n"
	.string "once. Everyone stood up.\p"
	.string "Mom said his name was BARRON.\n"
	.string "She said not to wave.$"

IndigoCity_Text_FatMan::
	.string "They built this city against the\n"
	.string "plateau.\p"
	.string "So visitors would stop calling\n"
	.string "it a League.\p"
	.string "It is still a League.\n"
	.string "It just has better paint.$"

IndigoCity_Text_HqWatcher::
	.string "The stairs stay shut until you\n"
	.string "have all eighteen types.\p"
	.string "TAKESHI's office is up there.\n"
	.string "Empty, most days.\p"
	.string "He walks the gyms instead of\n"
	.string "sitting in them.$"

IndigoCity_Text_CitySign::
	.string "Indigo City\n"
	.string "Type recognition. Public face of HQ.$"

IndigoCity_Text_BureauSign::
	.string "Indigo Field Bureau\n"
	.string "Trainers with two recognitions.$"

IndigoCity_Text_HqSign::
	.string "Indigo Plateau\n"
	.string "Eighteen types. Then the stairs.$"
