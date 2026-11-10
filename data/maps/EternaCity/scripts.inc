EternaCity_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, EternaCity_OnTransition
	.byte 0

EternaCity_OnTransition::
	setworldmapflag FLAG_WORLD_MAP_ETERNA_CITY
	end
