#include "global.h"
#include "indigo_rematch.h"
#include "event_data.h"
#include "random.h"
#include "rtc.h"
#include "string_util.h"
#include "constants/characters.h"
#include "constants/maps.h"

#if IS_FRLG

// VAR_INDIGO_REMATCH_GYM: low byte = today's gym (1-based index into sRematchGyms,
// 0 = none); REMATCH_VISIT_BIT = player entered the current gym through Indigo City.
// VAR_INDIGO_REMATCH_DAY: gLocalTime.days the pick was made on.
#define REMATCH_GYM_MASK   0x00FF
#define REMATCH_VISIT_BIT  0x8000
#define REMATCH_ENTRY_WARP 1  // middle of the three entrance warps in every Kanto gym

struct RematchGym
{
    u16 map;
    u16 defeatedFlag;
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
    { MAP_PEWTER_CITY_GYM,     FLAG_DEFEATED_BROCK,           sText_Brock },
    { MAP_CERULEAN_CITY_GYM,   FLAG_DEFEATED_MISTY,           sText_Misty },
    { MAP_VERMILION_CITY_GYM,  FLAG_DEFEATED_LT_SURGE,        sText_LtSurge },
    { MAP_CELADON_CITY_GYM,    FLAG_DEFEATED_ERIKA,           sText_Erika },
    { MAP_FUCHSIA_CITY_GYM,    FLAG_DEFEATED_KOGA,            sText_Koga },
    { MAP_SAFFRON_CITY_GYM,    FLAG_DEFEATED_SABRINA,         sText_Sabrina },
    { MAP_CINNABAR_ISLAND_GYM, FLAG_DEFEATED_BLAINE,          sText_Blaine },
    { MAP_VIRIDIAN_CITY_GYM,   FLAG_DEFEATED_LEADER_GIOVANNI, sText_Giovanni },
};

static u32 GetPickedGym(void)
{
    return VarGet(VAR_INDIGO_REMATCH_GYM) & REMATCH_GYM_MASK;
}

static void SetPickedGym(u32 gym)
{
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

#endif // IS_FRLG
