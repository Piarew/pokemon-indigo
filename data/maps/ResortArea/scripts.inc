ResortArea_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, ResortArea_OnTransition
	.byte 0

ResortArea_OnTransition::
	setworldmapflag FLAG_WORLD_MAP_RESORT_AREA
	end
