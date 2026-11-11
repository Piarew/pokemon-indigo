CinnabarIsland_Frlg_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, CinnabarIsland_OnTransition
	.byte 0

CinnabarIsland_OnTransition::
	setworldmapflag FLAG_WORLD_MAP_CINNABAR_ISLAND
	end

CinnabarIsland_EventScript_IslandSign::
	msgbox CinnabarIsland_Text_IslandSign, MSGBOX_SIGN
	end

CinnabarIsland_EventScript_GymSign::
	msgbox CinnabarIsland_Text_GymSign, MSGBOX_SIGN
	end

CinnabarIsland_Text_IslandSign::
	.string "Cinnabar Island\n"
	.string "The Fiery Town of Burning Desire$"

CinnabarIsland_Text_GymSign::
	.string "There's a notice here…\p"
	.string "Cinnabar Gym has relocated to\n"
	.string "Seafoam Islands.\p"
	.string "- Blaine$"
