SurvivalArea_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, SurvivalArea_OnTransition
	.byte 0

SurvivalArea_OnTransition::
	setworldmapflag FLAG_WORLD_MAP_SURVIVAL_AREA
	end
