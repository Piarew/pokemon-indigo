#ifndef GUARD_CHALLENGE_H
#define GUARD_CHALLENGE_H

#include "global.h"
#include "constants/abilities.h"

#define FLAG_SYS_NUZLOCKE            FLAG_UNUSED_0x4AD
#define FLAG_SYS_RANDOMIZER_WILD     FLAG_UNUSED_0x4AE
#define FLAG_SYS_RANDOMIZER_TRAINER  FLAG_UNUSED_0x4AF
#define FLAG_SYS_RANDOMIZER_ABILITY  FLAG_UNUSED_0x4BD
#define FLAG_SYS_RANDOMIZER_MOVESET  FLAG_UNUSED_0x4BE
#define FLAG_SYS_RANDOMIZER_MOVESET_SIGNATURE FLAG_UNUSED_0x4BF

#define NUZLOCKE_MAPSEC_FLAG_BYTES 32

bool32 IsNuzlockeActive(void);
bool32 IsWildRandomizerActive(void);
bool32 IsTrainerRandomizerActive(void);
bool32 IsAbilityRandomizerActive(void);
bool32 IsMovesetRandomizerActive(void);
bool32 IsMovesetSignatureRandomizerActive(void);
bool32 NuzlockeIsCatchBlocked(void);
bool32 NuzlockeBlocksHealing(struct Pokemon *mon);
void NuzlockeOnWildBattleStart(void);
void NuzlockeHandleFaintedParty(void);
enum Species RemapSpeciesForRandomizer(enum Species species, bool32 allowLegendaries);
enum Ability RemapAbilityForRandomizer(enum Species species, u32 personality, u32 slot);
void ChooseRandomizerAbilitySlots(enum Species species, u32 personality, enum Ability *slot0, enum Ability *slot1, enum Ability *hidden, bool32 keepHidden);
const struct LevelUpMove *RemapLevelUpLearnsetForRandomizer(enum Species species, const struct LevelUpMove *learnset);

#endif // GUARD_CHALLENGE_H
