#include "global.h"
#include "indigo_rematch.h"
#include "battle_setup.h"
#include "caps.h"
#include "data.h"
#include "event_data.h"
#include "random.h"
#include "rtc.h"
#include "string_util.h"
#include "constants/characters.h"
#include "constants/maps.h"
#include "constants/opponents.h"
#include "constants/pokemon.h"

#if IS_FRLG

// VAR_INDIGO_REMATCH_GYM: low byte = today's gym (1-based index into sRematchGyms,
// 0 = none); REMATCH_VISIT_BIT = player entered the current gym through Indigo City;
// REMATCH_DONE_BIT = today's leader already beaten in a Battle Club rematch.
// VAR_INDIGO_REMATCH_DAY: gLocalTime.days the pick was made on.
#define REMATCH_GYM_MASK   0x00FF
#define REMATCH_VISIT_BIT  0x8000
#define REMATCH_DONE_BIT   0x4000  // today's rematch already won; cleared by the daily reroll
#define REMATCH_FLAG_BIT   0x2000  // the rematch trainer's own trainer flag was already set before the battle
#define REMATCH_ENTRY_WARP 1  // middle of the three entrance warps in every Kanto gym

// trainerId: the team the leader uses in Battle Club rematches. Kanto leaders
// use their Pokémon Indigo team (TRAINER_LEADER_INDIGO_<city>). Vermilion and
// Cinnabar have no Indigo team, so Lt. Surge and Blaine keep their FRLG teams.
struct RematchGym
{
    u16 map;
    u16 defeatedFlag;
    u16 trainerId;
    const u8 *leader;
};

static const u8 sText_Brock[] = _("Brock");
static const u8 sText_Misty[] = _("Misty");
static const u8 sText_LtSurge[] = _("Lt. Surge");
static const u8 sText_Erika[] = _("Erika");
static const u8 sText_Koga[] = _("Koga");
static const u8 sText_Sabrina[] = _("Sabrina");
static const u8 sText_Blaine[] = _("Blaine");
static const u8 sText_Giovanni[] = _("Giovanni");

static const struct RematchGym sRematchGyms[] =
{
    { MAP_PEWTER_CITY_GYM,     FLAG_DEFEATED_BROCK,           TRAINER_LEADER_INDIGO_PEWTER,   sText_Brock },
    { MAP_CERULEAN_CITY_GYM,   FLAG_DEFEATED_MISTY,           TRAINER_LEADER_INDIGO_CERULEAN, sText_Misty },
    { MAP_VERMILION_CITY_GYM,  FLAG_DEFEATED_LT_SURGE,        TRAINER_LEADER_LT_SURGE,        sText_LtSurge },
    { MAP_CELADON_CITY_GYM,    FLAG_DEFEATED_ERIKA,           TRAINER_LEADER_INDIGO_CELADON,  sText_Erika },
    { MAP_FUCHSIA_CITY_GYM,    FLAG_DEFEATED_KOGA,            TRAINER_LEADER_INDIGO_FUCHSIA,  sText_Koga },
    { MAP_SAFFRON_CITY_GYM,    FLAG_DEFEATED_SABRINA,         TRAINER_LEADER_INDIGO_SAFFRON,  sText_Sabrina },
    { MAP_CINNABAR_ISLAND_GYM, FLAG_DEFEATED_BLAINE,          TRAINER_LEADER_BLAINE,          sText_Blaine },
    { MAP_VIRIDIAN_CITY_GYM,   FLAG_DEFEATED_LEADER_GIOVANNI, TRAINER_LEADER_INDIGO_VIRIDIAN, sText_Giovanni },
};

static u32 GetPickedGym(void)
{
    return VarGet(VAR_INDIGO_REMATCH_GYM) & REMATCH_GYM_MASK;
}

static void SetPickedGym(u32 gym)
{
    // A new pick also re-opens the once-per-day rematch.
    VarSet(VAR_INDIGO_REMATCH_GYM, (VarGet(VAR_INDIGO_REMATCH_GYM) & REMATCH_VISIT_BIT) | gym);
}

static bool32 IsVisiting(void)
{
    return (VarGet(VAR_INDIGO_REMATCH_GYM) & REMATCH_VISIT_BIT) != 0;
}

static void SetVisiting(bool32 visiting)
{
    u16 value = VarGet(VAR_INDIGO_REMATCH_GYM) & ~REMATCH_VISIT_BIT;
    VarSet(VAR_INDIGO_REMATCH_GYM, visiting ? (value | REMATCH_VISIT_BIT) : value);
}

static bool32 IsGymDefeated(u32 gym)
{
    return gym >= 1 && gym <= ARRAY_COUNT(sRematchGyms) && FlagGet(sRematchGyms[gym - 1].defeatedFlag);
}

static bool32 IsRematchGymMap(u16 map)
{
    u32 i;
    for (i = 0; i < ARRAY_COUNT(sRematchGyms); i++)
    {
        if (sRematchGyms[i].map == map)
            return TRUE;
    }
    return FALSE;
}

// Returns today's gym (1-based), rerolling when the day changed or the
// stored pick is no longer valid. 0 = no Kanto leader defeated yet.
u16 IndigoRematch_UpdateDaily(void)
{
    u8 candidates[ARRAY_COUNT(sRematchGyms)];
    u32 i, count = 0, current = GetPickedGym();
    u16 today;

    RtcCalcLocalTime();
    today = (u16)gLocalTime.days;
    if (current != 0 && VarGet(VAR_INDIGO_REMATCH_DAY) == today && IsGymDefeated(current))
        return current;

    for (i = 1; i <= ARRAY_COUNT(sRematchGyms); i++)
    {
        if (IsGymDefeated(i))
            candidates[count++] = i;
    }
    // Avoid repeating yesterday's leader when there is a choice.
    if (count > 1 && IsGymDefeated(current))
    {
        for (i = 0; i < count; i++)
        {
            if (candidates[i] == current)
            {
                candidates[i] = candidates[--count];
                break;
            }
        }
    }

    current = count ? candidates[Random() % count] : 0;
    SetPickedGym(current);
    VarSet(VAR_INDIGO_REMATCH_DAY, today);
    return current;
}

void IndigoRematch_BufferLeaderName(void)
{
    u32 gym = IndigoRematch_UpdateDaily();
    if (gym != 0)
        StringCopy(gStringVar1, sRematchGyms[gym - 1].leader);
    else
        gStringVar1[0] = EOS;
}

// Called by SetupWarp for every regular (non-dynamic) warp.
void IndigoRematch_AdjustWarp(s8 warpEventId, u8 *mapGroup, u8 *mapNum, u8 *warpId)
{
    u16 src = (gSaveBlock1Ptr->location.mapGroup << 8) | gSaveBlock1Ptr->location.mapNum;
    u16 dest = (*mapGroup << 8) | *mapNum;

    if (src == MAP_INDIGO_CITY && warpEventId == INDIGO_CITY_REMATCH_DOOR_WARP)
    {
        u32 gym = IndigoRematch_UpdateDaily();
        if (gym != 0)
        {
            *mapGroup = MAP_GROUP(sRematchGyms[gym - 1].map);
            *mapNum = MAP_NUM(sRematchGyms[gym - 1].map);
            *warpId = REMATCH_ENTRY_WARP;
            SetVisiting(TRUE);
        }
    }
    else if (src != dest && IsRematchGymMap(src))
    {
        // Leaving a Kanto gym (warps inside the Saffron gym have src == dest).
        if (IsVisiting())
        {
            *mapGroup = MAP_GROUP(MAP_INDIGO_CITY);
            *mapNum = MAP_NUM(MAP_INDIGO_CITY);
            *warpId = INDIGO_CITY_REMATCH_DOOR_WARP;
        }
        SetVisiting(FALSE);
    }
    else if (src != dest && IsRematchGymMap(dest))
    {
        // Normal entry from the gym's home city.
        SetVisiting(FALSE);
    }
}

// Special for the Kanto leader scripts: INDIGO_REMATCH_NONE / _READY / _DONE_TODAY.
// Not rerolled here, so the day turning over mid-visit doesn't re-open a rematch
// until the player comes back through the Battle Club.
u16 IndigoRematch_GetVisitState(void)
{
    u16 value = VarGet(VAR_INDIGO_REMATCH_GYM);
    if (!(value & REMATCH_VISIT_BIT))
        return INDIGO_REMATCH_NONE;
    return (value & REMATCH_DONE_BIT) ? INDIGO_REMATCH_DONE_TODAY : INDIGO_REMATCH_READY;
}

static const struct RematchGym *GetCurrentMapRematchGym(void)
{
    u16 map = (gSaveBlock1Ptr->location.mapGroup << 8) | gSaveBlock1Ptr->location.mapNum;
    u32 i;
    for (i = 0; i < ARRAY_COUNT(sRematchGyms); i++)
    {
        if (sRematchGyms[i].map == map)
            return &sRematchGyms[i];
    }
    return NULL;
}

// Run right before the rematch battle: remember whether the rematch team's
// trainer flag was already set, so winning a rematch doesn't mark e.g.
// TRAINER_LEADER_INDIGO_PEWTER as beaten for any future gym script.
void IndigoRematch_BeforeBattle(void)
{
    const struct RematchGym *gym = GetCurrentMapRematchGym();
    u16 value = VarGet(VAR_INDIGO_REMATCH_GYM) & ~REMATCH_FLAG_BIT;
    if (gym != NULL && HasTrainerBeenFought(gym->trainerId))
        value |= REMATCH_FLAG_BIT;
    VarSet(VAR_INDIGO_REMATCH_GYM, value);
}

// Run after a won rematch: mark today's rematch as done and restore the
// rematch team's trainer flag to its pre-battle state.
void IndigoRematch_SetDoneToday(void)
{
    const struct RematchGym *gym = GetCurrentMapRematchGym();
    u16 value = VarGet(VAR_INDIGO_REMATCH_GYM);
    if (gym != NULL && !(value & REMATCH_FLAG_BIT))
        ClearTrainerFlag(gym->trainerId);
    VarSet(VAR_INDIGO_REMATCH_GYM, (value & ~REMATCH_FLAG_BIT) | REMATCH_DONE_BIT);
}

// Battle Club rematches use the leader's original party, shifted so the
// highest-level mon sits at the current level cap and the rest keep their
// offsets below it (clamped to 1..MAX_LEVEL). Returns the trainer to build
// the party from: the original one unless this is a Battle Club rematch.
const struct Trainer *IndigoRematch_ScaleTrainer(u16 trainerNum, const struct Trainer *trainer, struct Trainer *tempTrainer, struct TrainerMon *tempParty)
{
    u32 i, maxLvl = 0;
    s32 shift, lvl;

    if (!IsVisiting() || trainer->partySize == 0 || trainer->partySize > PARTY_SIZE
     || trainer->poolSize != 0 || trainer->overrideTrainer != 0)
        return trainer;
    for (i = 0; i < ARRAY_COUNT(sRematchGyms); i++)
    {
        if (sRematchGyms[i].trainerId == trainerNum)
            break;
    }
    if (i == ARRAY_COUNT(sRematchGyms))
        return trainer;

    for (i = 0; i < trainer->partySize; i++)
    {
        if (trainer->party[i].lvl > maxLvl)
            maxLvl = trainer->party[i].lvl;
    }
    shift = (s32)GetCurrentLevelCap() - (s32)maxLvl;

    *tempTrainer = *trainer;
    for (i = 0; i < trainer->partySize; i++)
    {
        tempParty[i] = trainer->party[i];
        lvl = tempParty[i].lvl + shift;
        tempParty[i].lvl = (lvl < 1) ? 1 : (lvl > MAX_LEVEL) ? MAX_LEVEL : lvl;
    }
    tempTrainer->party = tempParty;
    return tempTrainer;
}

#else // !IS_FRLG

u16 IndigoRematch_UpdateDaily(void)
{
    return 0;
}

void IndigoRematch_BufferLeaderName(void)
{
    gStringVar1[0] = EOS;
}

void IndigoRematch_AdjustWarp(s8 warpEventId, u8 *mapGroup, u8 *mapNum, u8 *warpId)
{
}

u16 IndigoRematch_GetVisitState(void)
{
    return 0;
}

void IndigoRematch_BeforeBattle(void)
{
}

void IndigoRematch_SetDoneToday(void)
{
}

const struct Trainer *IndigoRematch_ScaleTrainer(u16 trainerNum, const struct Trainer *trainer, struct Trainer *tempTrainer, struct TrainerMon *tempParty)
{
    return trainer;
}

#endif // IS_FRLG
