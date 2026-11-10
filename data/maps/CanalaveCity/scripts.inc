CanalaveCity_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, CanalaveCity_OnTransition
	.byte 0

CanalaveCity_OnTransition::
	setworldmapflag FLAG_WORLD_MAP_CANALAVE_CITY
	end
