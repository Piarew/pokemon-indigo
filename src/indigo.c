#include "global.h"
#include "indigo.h"
#include "bg.h"
#include "constants/indigo.h"
#include "constants/pokemon.h"
#include "constants/rgb.h"
#include "constants/songs.h"
#include "decompress.h"
#include "event_data.h"
#include "gpu_regs.h"
#include "graphics.h"
#include "main.h"
#include "malloc.h"
#include "menu.h"
#include "overworld.h"
#include "palette.h"
#include "pokemon_summary_screen.h"
#include "scanline_effect.h"
#include "sound.h"
#include "sprite.h"
#include "string_util.h"
#include "task.h"
#include "text.h"
#include "text_window.h"
#include "window.h"

const u8 gText_CantUseUntilIndigoAuth[] = _("This can't be used until the Indigo\nLeague authorizes it.{PAUSE_UNTIL_PRESS}");

#if IS_FRLG

static const u8 sIndigoRosterTypes[NUM_INDIGO_GYMS] =
{
    TYPE_NORMAL, TYPE_GHOST, TYPE_DARK, TYPE_FLYING, TYPE_POISON, TYPE_ICE,
    TYPE_GRASS, TYPE_STEEL, TYPE_FAIRY, TYPE_FIRE, TYPE_FIGHTING, TYPE_DRAGON,
    TYPE_ELECTRIC, TYPE_GROUND, TYPE_PSYCHIC, TYPE_ROCK, TYPE_WATER, TYPE_BUG,
};

static const u8 sKantoSixTypes[] =
{
    TYPE_GRASS, TYPE_STEEL, TYPE_FAIRY, TYPE_FIRE, TYPE_FIGHTING, TYPE_DRAGON,
};

struct IndigoFieldMoveGift
{
    enum FieldMove fieldMove;
    u16 flag;
    const u8 *name;
};

static const u8 sText_Cut[] = _("Cut");
static const u8 sText_Flash[] = _("Flash");
static const u8 sText_Strength[] = _("Strength");
static const u8 sText_Surf[] = _("Surf");
static const u8 sText_Fly[] = _("Fly");
static const u8 sText_RockSmash[] = _("Rock Smash");
static const u8 sText_Waterfall[] = _("Waterfall");
static const u8 sText_Defog[] = _("Defog");
static const u8 sText_RockClimb[] = _("Rock Climb");

static const struct IndigoFieldMoveGift sIndigoFieldMoveGifts[NUM_INDIGO_FIELD_MOVES] =
{
    { FIELD_MOVE_CUT,        FLAG_INDIGO_CUT,        sText_Cut },
    { FIELD_MOVE_FLASH,      FLAG_INDIGO_FLASH,      sText_Flash },
    { FIELD_MOVE_STRENGTH,   FLAG_INDIGO_STRENGTH,   sText_Strength },
    { FIELD_MOVE_SURF,       FLAG_INDIGO_SURF,       sText_Surf },
    { FIELD_MOVE_FLY,        FLAG_INDIGO_FLY,        sText_Fly },
    { FIELD_MOVE_ROCK_SMASH, FLAG_INDIGO_ROCK_SMASH, sText_RockSmash },
    { FIELD_MOVE_WATERFALL,  FLAG_INDIGO_WATERFALL,  sText_Waterfall },
    { FIELD_MOVE_DEFOG,      FLAG_INDIGO_DEFOG,      sText_Defog },
    { FIELD_MOVE_ROCK_CLIMB, FLAG_INDIGO_ROCK_CLIMB, sText_RockClimb },
};

static const u8 sText_Indigo[] = _("INDIGO");
static const u8 sText_Johto[] = _("Johto");
static const u8 sText_Kanto[] = _("Kanto");
static const u8 sText_Sinnoh[] = _("Sinnoh");
static const u8 sText_RosterHint[] = _("Press B to return");
static const u8 sText_Slash[] = _("/");

static const u8 sRosterTextColors[3] = { TEXT_COLOR_WHITE, TEXT_COLOR_DARK_GRAY, TEXT_COLOR_LIGHT_GRAY };

static const u8 sMoveTypeToOamPaletteNum[NUMBER_OF_MON_TYPES] =
{
    [TYPE_NORMAL] = 13,
    [TYPE_FIGHTING] = 13,
    [TYPE_FLYING] = 14,
    [TYPE_POISON] = 14,
    [TYPE_GROUND] = 13,
    [TYPE_ROCK] = 13,
    [TYPE_BUG] = 15,
    [TYPE_GHOST] = 14,
    [TYPE_STEEL] = 13,
    [TYPE_MYSTERY] = 15,
    [TYPE_FIRE] = 13,
    [TYPE_WATER] = 14,
    [TYPE_GRASS] = 15,
    [TYPE_ELECTRIC] = 13,
    [TYPE_PSYCHIC] = 14,
    [TYPE_ICE] = 14,
    [TYPE_DRAGON] = 15,
    [TYPE_DARK] = 13,
    [TYPE_FAIRY] = 14,
};

static const struct BgTemplate sIndigoBgTemplates[] =
{
    {
        .bg = 0,
        .charBaseIndex = 0,
        .mapBaseIndex = 31,
        .screenSize = 0,
        .paletteMode = 0,
        .priority = 0,
        .baseTile = 0,
    },
};

static const struct WindowTemplate sIndigoWindowTemplates[] =
{
    {
        .bg = 0,
        .tilemapLeft = 1,
        .tilemapTop = 1,
        .width = 28,
        .height = 18,
        .paletteNum = 15,
        .baseBlock = 1,
    },
    DUMMY_WIN_TEMPLATE,
};

EWRAM_DATA static u8 *sIndigoTilemap = NULL;

static void VBlankCB_IndigoRoster(void);
static void CB2_IndigoRoster(void);
static void Task_IndigoRosterFadeIn(u8 taskId);
static void Task_IndigoRosterWait(u8 taskId);
static void Task_IndigoRosterFadeOut(u8 taskId);
static void InitIndigoRosterGfx(void);
static void DrawIndigoRosterWindow(void);
static void CreateIndigoTypeIcons(void);
static void FreeIndigoRoster(void);

static bool32 HasKantoSix(void)
{
    u32 i;

    for (i = 0; i < ARRAY_COUNT(sKantoSixTypes); i++)
    {
        if (!HasIndigoType(sKantoSixTypes[i]))
            return FALSE;
    }
    return TRUE;
}

static bool32 IsFieldMoveGiftEligible(u32 index)
{
    switch (sIndigoFieldMoveGifts[index].fieldMove)
    {
    case FIELD_MOVE_CUT:
        return HasIndigoType(TYPE_GRASS);
    case FIELD_MOVE_FLASH:
        return HasIndigoType(TYPE_STEEL);
    case FIELD_MOVE_STRENGTH:
        return HasIndigoType(TYPE_FIGHTING);
    case FIELD_MOVE_SURF:
        return HasKantoSix();
    case FIELD_MOVE_FLY:
        return HasIndigoType(TYPE_NORMAL);
    case FIELD_MOVE_ROCK_SMASH:
        return HasIndigoType(TYPE_GROUND);
    case FIELD_MOVE_WATERFALL:
    case FIELD_MOVE_DEFOG:
    case FIELD_MOVE_ROCK_CLIMB:
        return HasIndigoType(TYPE_PSYCHIC);
    default:
        return FALSE;
    }
}

static u16 GetIndigoFlagForType(u32 type)
{
    if (type < TYPE_NORMAL || type > TYPE_FAIRY || type == TYPE_MYSTERY)
        return 0;
    if (type < TYPE_MYSTERY)
        return FLAG_INDIGO_NORMAL + (type - TYPE_NORMAL);
    return FLAG_INDIGO_NORMAL + (type - TYPE_NORMAL - 1);
}

u32 CountIndigoGyms(void)
{
    u32 i;
    u32 count = 0;

    for (i = 0; i < NUM_INDIGO_GYMS; i++)
    {
        if (FlagGet(FLAG_INDIGO_NORMAL + i))
            count++;
    }
    return count;
}

u32 CountIndigoFieldMoves(void)
{
    u32 i;
    u32 count = 0;

    for (i = 0; i < NUM_INDIGO_FIELD_MOVES; i++)
    {
        if (FlagGet(FLAG_INDIGO_CUT + i))
            count++;
    }
    return count;
}

bool32 HasIndigoType(u32 type)
{
    u16 flag = GetIndigoFlagForType(type);

    return flag != 0 && FlagGet(flag);
}

bool32 HasIndigoFieldMove(enum FieldMove fieldMove)
{
    u32 i;

    for (i = 0; i < NUM_INDIGO_FIELD_MOVES; i++)
    {
        if (sIndigoFieldMoveGifts[i].fieldMove == fieldMove)
            return FlagGet(sIndigoFieldMoveGifts[i].flag);
    }
    return FALSE;
}

void SyncIndigoCount(void)
{
    VarSet(VAR_INDIGO_COUNT, CountIndigoGyms());
}

void GiveIndigoRecognitionForType(u32 type)
{
    u16 flag = GetIndigoFlagForType(type);

    if (flag != 0)
        FlagSet(flag);
    SyncIndigoCount();
}

void GiveIndigoRecognition(void)
{
    GiveIndigoRecognitionForType(gSpecialVar_0x8004);
}

u16 TryGiveIndigoFieldMoves(void)
{
    u32 i;

    for (i = 0; i < NUM_INDIGO_FIELD_MOVES; i++)
    {
        if (IsFieldMoveGiftEligible(i) && !FlagGet(sIndigoFieldMoveGifts[i].flag))
        {
            FlagSet(sIndigoFieldMoveGifts[i].flag);
            StringCopy(gStringVar1, sIndigoFieldMoveGifts[i].name);
            return i + 1;
        }
    }
    return 0;
}

static void VBlankCB_IndigoRoster(void)
{
    LoadOam();
    ProcessSpriteCopyRequests();
    TransferPlttBuffer();
}

static void CB2_IndigoRoster(void)
{
    RunTasks();
    AnimateSprites();
    BuildOamBuffer();
    DoScheduledBgTilemapCopiesToVram();
    UpdatePaletteFade();
}

void CB2_ShowIndigoRoster(void)
{
    switch (gMain.state)
    {
    default:
    case 0:
        SetVBlankCallback(NULL);
        SetGpuReg(REG_OFFSET_DISPCNT, 0);
        DmaClearLarge16(3, (void *)VRAM, VRAM_SIZE, 0x1000);
        DmaClear32(3, OAM, OAM_SIZE);
        DmaClear16(3, PLTT, PLTT_SIZE);
        ScanlineEffect_Stop();
        ResetTasks();
        ResetSpriteData();
        ResetPaletteFade();
        FreeAllSpritePalettes();
        gMain.state++;
        break;
    case 1:
        InitIndigoRosterGfx();
        gMain.state++;
        break;
    case 2:
        DrawIndigoRosterWindow();
        CreateIndigoTypeIcons();
        BlendPalettes(PALETTES_ALL, 16, RGB_BLACK);
        BeginNormalPaletteFade(PALETTES_ALL, 0, 16, 0, RGB_BLACK);
        SetVBlankCallback(VBlankCB_IndigoRoster);
        SetMainCallback2(CB2_IndigoRoster);
        CreateTask(Task_IndigoRosterFadeIn, 0);
        break;
    }
}

static void InitIndigoRosterGfx(void)
{
    ClearScheduledBgCopiesToVram();
    ResetBgsAndClearDma3BusyFlags(0);
    InitBgsFromTemplates(0, sIndigoBgTemplates, ARRAY_COUNT(sIndigoBgTemplates));
    sIndigoTilemap = AllocZeroed(BG_SCREEN_SIZE);
    SetBgTilemapBuffer(0, sIndigoTilemap);
    ScheduleBgCopyTilemapToVram(0);
    SetGpuReg(REG_OFFSET_DISPCNT, DISPCNT_OBJ_ON | DISPCNT_OBJ_1D_MAP);
    ShowBg(0);
    InitWindows(sIndigoWindowTemplates);
    DeactivateAllTextPrinters();
    LoadMessageBoxAndBorderGfx();
    LoadPalette(gStandardMenuPalette, BG_PLTT_ID(15), PLTT_SIZE_4BPP);
}

static void DrawIndigoRosterWindow(void)
{
    u32 count = CountIndigoGyms();

    DrawStdWindowFrame(0, FALSE);
    FillWindowPixelBuffer(0, PIXEL_FILL(1));

    AddTextPrinterParameterized4(0, FONT_NORMAL, 8, 2, 0, 0, sRosterTextColors, TEXT_SKIP_DRAW, sText_Indigo);

    ConvertIntToDecimalStringN(gStringVar1, count, STR_CONV_MODE_LEFT_ALIGN, 2);
    StringAppend(gStringVar1, sText_Slash);
    ConvertIntToDecimalStringN(gStringVar2, NUM_INDIGO_GYMS, STR_CONV_MODE_LEFT_ALIGN, 2);
    StringAppend(gStringVar1, gStringVar2);
    AddTextPrinterParameterized4(0, FONT_NORMAL, 160, 2, 0, 0, sRosterTextColors, TEXT_SKIP_DRAW, gStringVar1);

    AddTextPrinterParameterized4(0, FONT_SMALL, 4, 32, 0, 0, sRosterTextColors, TEXT_SKIP_DRAW, sText_Johto);
    AddTextPrinterParameterized4(0, FONT_SMALL, 4, 64, 0, 0, sRosterTextColors, TEXT_SKIP_DRAW, sText_Kanto);
    AddTextPrinterParameterized4(0, FONT_SMALL, 4, 96, 0, 0, sRosterTextColors, TEXT_SKIP_DRAW, sText_Sinnoh);
    AddTextPrinterParameterized4(0, FONT_SMALL, 8, 128, 0, 0, sRosterTextColors, TEXT_SKIP_DRAW, sText_RosterHint);

    PutWindowTilemap(0);
    CopyWindowToVram(0, COPYWIN_FULL);
    ScheduleBgCopyTilemapToVram(0);
}

static void CreateIndigoTypeIcons(void)
{
    u32 i;
    u32 row;
    u32 col;
    u32 type;
    u8 spriteId;
    struct Sprite *sprite;
    s16 x;
    s16 y;

    LoadCompressedSpriteSheet(&gSpriteSheet_MoveTypes);
    LoadPalette(gMoveTypes_Pal, OBJ_PLTT_ID(13), 3 * PLTT_SIZE_4BPP);

    for (i = 0; i < NUM_INDIGO_GYMS; i++)
    {
        row = i / INDIGO_ROSTER_COLS;
        col = i % INDIGO_ROSTER_COLS;
        x = 56 + (s16)col * 32;
        y = 48 + (s16)row * 32;
        type = sIndigoRosterTypes[i];
        spriteId = CreateSprite(&gSpriteTemplate_MoveTypes, x + 16, y + 8, 2);
        sprite = &gSprites[spriteId];
        sprite->callback = SpriteCallbackDummy;
        StartSpriteAnim(sprite, type);
        sprite->oam.paletteNum = sMoveTypeToOamPaletteNum[type];
        sprite->invisible = !HasIndigoType(type);
    }
}

static void FreeIndigoRoster(void)
{
    FreeAllWindowBuffers();
    if (sIndigoTilemap != NULL)
    {
        Free(sIndigoTilemap);
        sIndigoTilemap = NULL;
    }
    ResetSpriteData();
    FreeAllSpritePalettes();
}

static void Task_IndigoRosterFadeIn(u8 taskId)
{
    if (!gPaletteFade.active)
        gTasks[taskId].func = Task_IndigoRosterWait;
}

static void Task_IndigoRosterWait(u8 taskId)
{
    if (JOY_NEW(A_BUTTON | B_BUTTON | START_BUTTON))
    {
        PlaySE(SE_SELECT);
        BeginNormalPaletteFade(PALETTES_ALL, 0, 0, 16, RGB_BLACK);
        gTasks[taskId].func = Task_IndigoRosterFadeOut;
    }
}

static void Task_IndigoRosterFadeOut(u8 taskId)
{
    if (!gPaletteFade.active)
    {
        FreeIndigoRoster();
        DestroyTask(taskId);
        SetMainCallback2(CB2_ReturnToFieldWithOpenMenu);
    }
}

#else // !IS_FRLG

u32 CountIndigoGyms(void)
{
    return 0;
}

u32 CountIndigoFieldMoves(void)
{
    return 0;
}

bool32 HasIndigoType(u32 type)
{
    return FALSE;
}

bool32 HasIndigoFieldMove(enum FieldMove fieldMove)
{
    return FALSE;
}

void SyncIndigoCount(void)
{
}

void GiveIndigoRecognitionForType(u32 type)
{
}

void GiveIndigoRecognition(void)
{
}

u16 TryGiveIndigoFieldMoves(void)
{
    return 0;
}

void CB2_ShowIndigoRoster(void)
{
    SetMainCallback2(CB2_ReturnToFieldWithOpenMenu);
}

#endif // IS_FRLG
