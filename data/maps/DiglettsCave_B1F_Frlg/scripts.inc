DiglettsCave_B1F_Frlg_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, DiglettsCave_B1F_OnTransition
	.byte 0

DiglettsCave_B1F_OnTransition::
	setworldmapflag FLAG_WORLD_MAP_DIGLETTS_CAVE_B1F
	end

@ ---- East block (indigo custom; see tools/johto/east_blocks.py) ----
DiglettsCave_B1F_Frlg_EventScript_CaveInSign::
	msgbox DiglettsCave_B1F_Frlg_Text_CaveIn, MSGBOX_SIGN
	end

DiglettsCave_B1F_Frlg_Text_CaveIn:
	.string "A cave-in has sealed the\n"
	.string "tunnel to VERMILION CITY.\p"
	.string "There is no way through.$"
