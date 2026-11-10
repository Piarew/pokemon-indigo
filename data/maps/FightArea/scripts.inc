FightArea_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, FightArea_OnTransition
	.byte 0

FightArea_OnTransition::
	setworldmapflag FLAG_WORLD_MAP_FIGHT_AREA
	end
