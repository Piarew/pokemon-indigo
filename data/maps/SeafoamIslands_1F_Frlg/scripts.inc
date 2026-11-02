SeafoamIslands_1F_Frlg_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, SeafoamIslands_1F_OnTransition
	.byte 0

SeafoamIslands_1F_OnTransition::
	setworldmapflag FLAG_WORLD_MAP_SEAFOAM_ISLANDS_1F
	end

@ ---- Seafoam ice wall (indigo custom; see tools/johto/seafoam_block.py) ----
SeafoamIslands_1F_EventScript_IceWallSign::
	msgbox SeafoamIslands_1F_Text_IceWall, MSGBOX_SIGN
	end

SeafoamIslands_1F_Text_IceWall:
	.string "A thick wall of ice seals the\n"
	.string "eastern passage. It won't budge.$"
