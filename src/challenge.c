#include "global.h"
#include "battle.h"
#include "challenge.h"
#include "event_data.h"
#include "overworld.h"
#include "pokedex.h"
#include "pokemon.h"
#include "pokemon_storage_system.h"
#include "constants/battle.h"

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
