#ifndef GUARD_CHALLENGE_H
#define GUARD_CHALLENGE_H

#include "global.h"

#define FLAG_SYS_NUZLOCKE           FLAG_UNUSED_0x4AD
#define FLAG_SYS_RANDOMIZER_WILD    FLAG_UNUSED_0x4AE
#define FLAG_SYS_RANDOMIZER_TRAINER FLAG_UNUSED_0x4AF

#define NUZLOCKE_MAPSEC_FLAG_BYTES 32

bool32 IsNuzlockeActive(void);
bool32 IsWildRandomizerActive(void);
bool32 IsTrainerRandomizerActive(void);
bool32 NuzlockeIsCatchBlocked(void);
bool32 NuzlockeBlocksHealing(struct Pokemon *mon);
void NuzlockeOnWildBattleStart(void);
void NuzlockeHandleFaintedParty(void);
enum Species RemapSpeciesForRandomizer(enum Species species, bool32 allowLegendaries);

#endif // GUARD_CHALLENGE_H
