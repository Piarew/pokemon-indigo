#include "global.h"
#include "battle.h"
#include "challenge.h"
#include "event_data.h"
#include "overworld.h"
#include "pokedex.h"
#include "pokemon.h"
#include "pokemon_storage_system.h"
#include "string_util.h"
#include "move.h"
#include "constants/abilities.h"
#include "constants/battle.h"
#include "constants/moves.h"

EWRAM_DATA static bool8 sNuzlockeBlockCatch = FALSE;

bool32 IsNuzlockeActive(void)
{
    return FlagGet(FLAG_SYS_NUZLOCKE);
}

bool32 IsWildRandomizerActive(void)
{
    return FlagGet(FLAG_SYS_RANDOMIZER_WILD);
}

bool32 IsTrainerRandomizerActive(void)
{
    return FlagGet(FLAG_SYS_RANDOMIZER_TRAINER);
}

bool32 IsAbilityRandomizerActive(void)
{
    return FlagGet(FLAG_SYS_RANDOMIZER_ABILITY);
}

bool32 IsMovesetRandomizerActive(void)
{
    return FlagGet(FLAG_SYS_RANDOMIZER_MOVESET);
}

bool32 IsMovesetSignatureRandomizerActive(void)
{
    return IsMovesetRandomizerActive() && FlagGet(FLAG_SYS_RANDOMIZER_MOVESET_SIGNATURE);
}

bool32 NuzlockeIsCatchBlocked(void)
{
    return IsNuzlockeActive() && sNuzlockeBlockCatch;
}

bool32 NuzlockeBlocksHealing(struct Pokemon *mon)
{
    if (!IsNuzlockeActive())
        return FALSE;
    if (GetMonData(mon, MON_DATA_SPECIES) == SPECIES_NONE || GetMonData(mon, MON_DATA_IS_EGG))
        return FALSE;
    return GetMonData(mon, MON_DATA_HP) == 0;
}

static bool32 NuzlockeIsMapsecUsed(u32 mapsec)
{
    if (mapsec >= NUZLOCKE_MAPSEC_FLAG_BYTES * 8)
        return TRUE;
    return (gSaveBlock3Ptr->nuzlockeMapsecFlags[mapsec / 8] >> (mapsec % 8)) & 1;
}

static void NuzlockeSetMapsecUsed(u32 mapsec)
{
    if (mapsec >= NUZLOCKE_MAPSEC_FLAG_BYTES * 8)
        return;
    gSaveBlock3Ptr->nuzlockeMapsecFlags[mapsec / 8] |= (1 << (mapsec % 8));
}

static bool32 SkipNuzlockeBattleRules(void)
{
    return (gBattleTypeFlags & (BATTLE_TYPE_LINK
                              | BATTLE_TYPE_RECORDED
                              | BATTLE_TYPE_FRONTIER
                              | BATTLE_TYPE_EREADER_TRAINER
                              | BATTLE_TYPE_RECORDED_LINK));
}

void NuzlockeOnWildBattleStart(void)
{
    struct Pokemon *wildMon;
    enum Species species;
    u32 mapsec;

    sNuzlockeBlockCatch = FALSE;
    if (!IsNuzlockeActive() || SkipNuzlockeBattleRules())
        return;
    if (gBattleTypeFlags & BATTLE_TYPE_TRAINER)
        return;

    wildMon = &gParties[B_TRAINER_OPPONENT_A][0];
    species = GetMonData(wildMon, MON_DATA_SPECIES);
    if (species == SPECIES_NONE)
        return;

    // Shiny clause: always catchable, does not consume the area.
    if (IsMonShiny(wildMon))
        return;

    // Dupes clause: already-owned species do not consume the area.
    if (GetSetPokedexFlag(SpeciesToNationalPokedexNum(species), FLAG_GET_CAUGHT))
        return;

    mapsec = GetCurrentRegionMapSectionId();
    if (NuzlockeIsMapsecUsed(mapsec))
        sNuzlockeBlockCatch = TRUE;
    else
        NuzlockeSetMapsecUsed(mapsec);
}

static bool32 PartyHasLivingMon(void)
{
    u32 i;

    for (i = 0; i < PARTY_SIZE; i++)
    {
        struct Pokemon *mon = &gParties[B_TRAINER_PLAYER][i];
        if (GetMonData(mon, MON_DATA_SPECIES) == SPECIES_NONE)
            break;
        if (!GetMonData(mon, MON_DATA_IS_EGG) && GetMonData(mon, MON_DATA_HP) > 0)
            return TRUE;
    }
    return FALSE;
}

void NuzlockeHandleFaintedParty(void)
{
    u32 i;

    if (!IsNuzlockeActive() || SkipNuzlockeBattleRules())
        return;

    // Full wipe: leave fainted mons in the party so whiteout can heal them.
    if (!PartyHasLivingMon())
        return;

    for (i = 0; i < PARTY_SIZE; i++)
    {
        struct Pokemon *mon = &gParties[B_TRAINER_PLAYER][i];
        if (GetMonData(mon, MON_DATA_SPECIES) == SPECIES_NONE)
            continue;
        if (GetMonData(mon, MON_DATA_IS_EGG))
            continue;
        if (GetMonData(mon, MON_DATA_HP) != 0)
            continue;

        if (CopyMonToPC(mon) != MON_GIVEN_TO_PC)
        {
            // PC is full: release.
        }
        ZeroMonData(mon);
    }
    CompactPartySlots();
    CalculatePlayerPartyCount();
}

static bool32 IsRandomizerSpecies(enum Species species, bool32 allowLegendaries)
{
    if (species == SPECIES_NONE || species >= NUM_SPECIES || species == SPECIES_EGG)
        return FALSE;
    if (gSpeciesInfo[species].natDexNum == NATIONAL_DEX_NONE)
        return FALSE;
    if (GET_BASE_SPECIES_ID(species) != species)
        return FALSE;
    if (gSpeciesInfo[species].isMegaEvolution
     || gSpeciesInfo[species].isPrimalReversion
     || gSpeciesInfo[species].isUltraBurst
     || gSpeciesInfo[species].isGigantamax
     || gSpeciesInfo[species].isTeraForm)
        return FALSE;
    if (!allowLegendaries
     && (gSpeciesInfo[species].isRestrictedLegendary
      || gSpeciesInfo[species].isSubLegendary
      || gSpeciesInfo[species].isMythical
      || gSpeciesInfo[species].isUltraBeast
      || gSpeciesInfo[species].isParadox))
        return FALSE;
    return TRUE;
}

static u32 HashTrainerSpecies(u32 species)
{
    u32 seed = (gSaveBlock2Ptr->playerTrainerId[3] << 24)
             | (gSaveBlock2Ptr->playerTrainerId[2] << 16)
             | (gSaveBlock2Ptr->playerTrainerId[1] << 8)
             |  gSaveBlock2Ptr->playerTrainerId[0];
    u32 hash = seed ^ (species * 0x45D9F3Bu);

    hash ^= hash >> 16;
    hash *= 0x45D9F3Bu;
    hash ^= hash >> 16;
    return hash;
}

enum Species RemapSpeciesForRandomizer(enum Species species, bool32 allowLegendaries)
{
    u32 count = 0;
    u32 pick;
    u32 i;
    enum Species base = GET_BASE_SPECIES_ID(species);

    if (!IsRandomizerSpecies(base, TRUE))
        return species;

    for (i = 1; i < NUM_SPECIES; i++)
    {
        if (IsRandomizerSpecies(i, allowLegendaries))
            count++;
    }
    if (count == 0)
        return species;

    pick = HashTrainerSpecies(base) % count;
    for (i = 1; i < NUM_SPECIES; i++)
    {
        if (!IsRandomizerSpecies(i, allowLegendaries))
            continue;
        if (pick == 0)
            return i;
        pick--;
    }
    return species;
}

static bool32 IsRandomizerAbility(enum Ability ability)
{
    if (ability == ABILITY_NONE || ability >= ABILITIES_COUNT)
        return FALSE;
    if (StringCompare(gAbilitiesInfo[ability].name, gAbilitiesInfo[ABILITY_NONE].name) == 0)
        return FALSE;
    return TRUE;
}

enum Ability RemapAbilityForRandomizer(enum Species species, u32 personality, u32 slot)
{
    u32 count = 0;
    u32 pick;
    u32 i;
    u32 hash;

    for (i = 1; i < ABILITIES_COUNT; i++)
    {
        if (IsRandomizerAbility(i))
            count++;
    }
    if (count == 0)
        return GetAbilityBySpecies(species, 0);

    hash = HashTrainerSpecies(species) ^ personality ^ (slot * 0x9E3779B9u);
    hash ^= hash >> 16;
    hash *= 0x45D9F3Bu;
    hash ^= hash >> 16;
    pick = hash % count;

    for (i = 1; i < ABILITIES_COUNT; i++)
    {
        if (!IsRandomizerAbility(i))
            continue;
        if (pick == 0)
            return i;
        pick--;
    }
    return GetAbilityBySpecies(species, 0);
}

static enum Ability NextRandomizerAbility(enum Ability start, enum Ability avoid1, enum Ability avoid2)
{
    u32 i;
    u32 range = ABILITIES_COUNT - 1;
    u32 index = (start == 0) ? 0 : (start - 1);

    for (i = 1; i <= range; i++)
    {
        enum Ability ability = ((index + i) % range) + 1;
        if (!IsRandomizerAbility(ability))
            continue;
        if (ability == avoid1 || ability == avoid2)
            continue;
        return ability;
    }
    return start;
}

void ChooseRandomizerAbilitySlots(enum Species species, u32 personality, enum Ability *slot0, enum Ability *slot1, enum Ability *hidden, bool32 keepHidden)
{
    enum Ability ability0 = RemapAbilityForRandomizer(species, personality, 0);
    enum Ability ability1 = RemapAbilityForRandomizer(species, personality, 1);
    enum Ability abilityH = keepHidden ? *hidden : RemapAbilityForRandomizer(SPECIES_NONE, personality, 2);

    if (ability1 == ability0)
        ability1 = NextRandomizerAbility(ability1, ability0, abilityH);
    if (!keepHidden && (abilityH == ability0 || abilityH == ability1))
        abilityH = NextRandomizerAbility(abilityH, ability0, ability1);
    if (ability1 == abilityH)
        ability1 = NextRandomizerAbility(ability1, ability0, abilityH);
    if (ability0 == abilityH || ability0 == ability1)
        ability0 = NextRandomizerAbility(ability0, ability1, abilityH);

    *slot0 = ability0;
    *slot1 = ability1;
    *hidden = abilityH;
}

#define MAX_REMAPPED_LEVEL_UP_MOVES 64
#define MOVE_OWNER_SHARED 0xFFFF

EWRAM_DATA static u16 sFamilyPrevo[NUM_SPECIES];
EWRAM_DATA static u16 sMoveOwnerFamily[MOVES_COUNT];
EWRAM_DATA static bool8 sSignatureIndexReady;
EWRAM_DATA static enum Species sRemappedLearnsetSpecies;
EWRAM_DATA static bool8 sRemappedLearnsetKeepSignature;
EWRAM_DATA static struct LevelUpMove sRemappedLearnset[MAX_REMAPPED_LEVEL_UP_MOVES];

static bool32 IsRandomizerMove(enum Move move)
{
    if (move == MOVE_NONE || move >= MOVES_COUNT)
        return FALSE;
    if (move == MOVE_STRUGGLE || move == MOVE_SKETCH)
        return FALSE;
    if (GetMoveEffect(move) == EFFECT_PLACEHOLDER)
        return FALSE;
    if (StringCompare(GetMoveName(move), GetMoveName(MOVE_NONE)) == 0)
        return FALSE;
    return TRUE;
}

static enum Species GetRandomizerFamilyRoot(enum Species species)
{
    enum Species root = GET_BASE_SPECIES_ID(species);
    u32 i;

    for (i = 0; i < 8; i++)
    {
        enum Species prevo = sFamilyPrevo[root];
        if (prevo == SPECIES_NONE)
            break;
        root = GET_BASE_SPECIES_ID(prevo);
    }
    return root;
}

static void EnsureSignatureIndex(void)
{
    u32 i, j;

    if (sSignatureIndexReady)
        return;

    memset(sFamilyPrevo, 0, sizeof(sFamilyPrevo));
    memset(sMoveOwnerFamily, 0, sizeof(sMoveOwnerFamily));

    for (i = 1; i < NUM_SPECIES; i++)
    {
        const struct Evolution *evolutions;

        if (!IsSpeciesEnabled(i))
            continue;
        evolutions = GetSpeciesEvolutions(i);
        if (evolutions == NULL)
            continue;
        for (j = 0; evolutions[j].method != EVOLUTIONS_END; j++)
        {
            enum Species target = SanitizeSpeciesId(evolutions[j].targetSpecies);
            if (target != SPECIES_NONE && sFamilyPrevo[target] == SPECIES_NONE)
                sFamilyPrevo[target] = i;
        }
    }

    for (i = 1; i < NUM_SPECIES; i++)
    {
        const struct LevelUpMove *learnset;
        enum Species family;

        if (!IsSpeciesEnabled(i))
            continue;
        family = GetRandomizerFamilyRoot(i);
        learnset = GetSpeciesLevelUpLearnsetRaw(i);
        for (j = 0; learnset[j].move != LEVEL_UP_MOVE_END; j++)
        {
            enum Move move = learnset[j].move;
            if (move == MOVE_NONE || move >= MOVES_COUNT)
                continue;
            if (sMoveOwnerFamily[move] == SPECIES_NONE)
                sMoveOwnerFamily[move] = family;
            else if (sMoveOwnerFamily[move] != family)
                sMoveOwnerFamily[move] = MOVE_OWNER_SHARED;
        }
    }

    sSignatureIndexReady = TRUE;
}

static enum Move FindSignatureMove(enum Species species)
{
    const struct LevelUpMove *learnset = GetSpeciesLevelUpLearnsetRaw(species);
    enum Species family;
    u32 i;

    EnsureSignatureIndex();
    family = GetRandomizerFamilyRoot(species);
    for (i = 0; learnset[i].move != LEVEL_UP_MOVE_END; i++)
    {
        enum Move move = learnset[i].move;
        if (move == MOVE_NONE || move >= MOVES_COUNT)
            continue;
        if (sMoveOwnerFamily[move] == family)
            return move;
    }
    return MOVE_NONE;
}

static bool32 MoveInList(enum Move move, const enum Move *list, u32 count)
{
    u32 i;

    for (i = 0; i < count; i++)
    {
        if (list[i] == move)
            return TRUE;
    }
    return FALSE;
}

static enum Move RemapMoveForRandomizer(enum Species species, u32 slot, const enum Move *avoid, u32 avoidCount)
{
    u32 count = 0;
    u32 pick;
    u32 i;
    u32 hash;
    enum Move chosen = MOVE_NONE;

    for (i = 1; i < MOVES_COUNT; i++)
    {
        if (IsRandomizerMove(i))
            count++;
    }
    if (count == 0)
        return MOVE_NONE;

    hash = HashTrainerSpecies(species) ^ (slot * 0x9E3779B9u);
    hash ^= hash >> 16;
    hash *= 0x45D9F3Bu;
    hash ^= hash >> 16;
    pick = hash % count;

    for (i = 1; i < MOVES_COUNT; i++)
    {
        if (!IsRandomizerMove(i))
            continue;
        if (pick == 0)
        {
            chosen = i;
            break;
        }
        pick--;
    }

    if (chosen == MOVE_NONE || !MoveInList(chosen, avoid, avoidCount))
        return chosen;

    for (i = 1; i <= MOVES_COUNT; i++)
    {
        enum Move move = ((chosen - 1 + i) % (MOVES_COUNT - 1)) + 1;
        if (!IsRandomizerMove(move))
            continue;
        if (!MoveInList(move, avoid, avoidCount))
            return move;
    }
    return chosen;
}

const struct LevelUpMove *RemapLevelUpLearnsetForRandomizer(enum Species species, const struct LevelUpMove *learnset)
{
    bool32 keepSignature = IsMovesetSignatureRandomizerActive();
    enum Move signature = MOVE_NONE;
    enum Move used[MAX_REMAPPED_LEVEL_UP_MOVES];
    u32 usedCount = 0;
    u32 i;

    species = SanitizeSpeciesId(species);
    if (sRemappedLearnsetSpecies == species
     && sRemappedLearnsetKeepSignature == keepSignature
     && sRemappedLearnset[0].move != MOVE_NONE)
        return sRemappedLearnset;

    if (keepSignature)
        signature = FindSignatureMove(species);

    for (i = 0; learnset[i].move != LEVEL_UP_MOVE_END && i < MAX_REMAPPED_LEVEL_UP_MOVES - 1; i++)
    {
        enum Move move;

        sRemappedLearnset[i].level = learnset[i].level;
        if (i == 0 && signature != MOVE_NONE)
            move = signature;
        else
            move = RemapMoveForRandomizer(species, i, used, usedCount);
        if (move == MOVE_NONE)
            move = learnset[i].move;
        sRemappedLearnset[i].move = move;
        used[usedCount++] = move;
    }

    sRemappedLearnset[i].move = LEVEL_UP_MOVE_END;
    sRemappedLearnset[i].level = 0;
    sRemappedLearnsetSpecies = species;
    sRemappedLearnsetKeepSignature = keepSignature;
    return sRemappedLearnset;
}
