#ifndef GUARD_INDIGO_REMATCH_H
#define GUARD_INDIGO_REMATCH_H

struct Trainer;
struct TrainerMon;

// Indigo City east gym ("Battle Club"): daily rotating rematch gym.
// Its door leads to one cleared Indigo gym (FLAG_INDIGO_<TYPE>), rerolled once per in-game day;
// leaving that gym returns to Indigo City instead of the gym's home city.

// Warp event in data/maps/IndigoCity/map.json for the Battle Club door.
// tools/indigo_city/gen_indigo_city.py asserts this index.
#define INDIGO_CITY_REMATCH_DOOR_WARP 7

u16 IndigoRematch_UpdateDaily(void);
void IndigoRematch_BufferLeaderName(void);
void IndigoRematch_AdjustWarp(s8 warpEventId, u8 *mapGroup, u8 *mapNum, u8 *warpId);
u16 IndigoRematch_GetVisitState(void);
void IndigoRematch_BeforeBattle(void);
void IndigoRematch_SetDoneToday(void);
const struct Trainer *IndigoRematch_ScaleTrainer(u16 trainerNum, const struct Trainer *trainer, struct Trainer *tempTrainer, struct TrainerMon *tempParty);

#endif // GUARD_INDIGO_REMATCH_H
