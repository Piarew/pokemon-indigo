#ifndef GUARD_INDIGO_REMATCH_H
#define GUARD_INDIGO_REMATCH_H

// Indigo City east gym ("Battle Club"): daily rotating rematch gym.
// Its door leads to one defeated Kanto leader's gym, rerolled once per day;
// leaving that gym returns to Indigo City instead of the gym's home city.

// Warp event in data/maps/IndigoCity/map.json for the Battle Club door.
// tools/indigo_city/gen_indigo_city.py asserts this index.
#define INDIGO_CITY_REMATCH_DOOR_WARP 7

u16 IndigoRematch_UpdateDaily(void);
void IndigoRematch_BufferLeaderName(void);
void IndigoRematch_AdjustWarp(s8 warpEventId, u8 *mapGroup, u8 *mapNum, u8 *warpId);

#endif // GUARD_INDIGO_REMATCH_H
