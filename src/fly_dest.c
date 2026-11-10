#include "global.h"
#include "bg.h"
#include "event_data.h"
#include "field_effect.h"
#include "fly_dest.h"
#include "gpu_regs.h"
#include "international_string_util.h"
#include "list_menu.h"
#include "main.h"
#include "menu.h"
#include "overworld.h"
#include "palette.h"
#include "party_menu.h"
#include "region_map.h"
#include "regions.h"
#include "scanline_effect.h"
#include "sound.h"
#include "sprite.h"
#include "string_util.h"
#include "strings.h"
#include "task.h"
#include "text.h"
#include "text_window.h"
#include "window.h"
#include "constants/flags.h"
#include "constants/heal_locations.h"
#include "constants/region_map_sections.h"
#include "constants/rgb.h"
#include "constants/songs.h"

#define FLY_DEST_MAX_SHOWED 6
#define FLY_DEST_NAME_LENGTH (MAP_NAME_LENGTH + 1)
#define FLY_DEST_LIST_CAPACITY 24
#define FLY_FRAME_BASE_TILE 0x1A2
#define TAG_FLY_SCROLL_ARROW 2000

enum {
    WIN_FLY_HEADER,
    WIN_FLY_LIST,
    WIN_FLY_FOOTER,
};

enum FlyDestTab {
    FLY_TAB_KANTO,
    FLY_TAB_JOHTO,
    FLY_TAB_SINNOH,
    FLY_TAB_COUNT,
};

struct FlyDest {
    u8 region;
    u16 healLocation;
    u16 mapSec;
    u16 flag;
};

static void MainCB2_FlyDest(void);
static void VBlankCB_FlyDest(void);
static void Task_FlyDestFadeIn(u8 taskId);
static void Task_FlyDestHandleInput(u8 taskId);
static void Task_FlyDestFadeOut(u8 taskId);
static void InitFlyDestWindows(void);
static void DrawFlyDestHeaderForTask(u8 taskId);
static void DrawFlyDestFooter(void);
static void BuildFlyDestList(u8 taskId);
static void DestroyFlyDestList(u8 taskId);
static void SwitchFlyDestTab(u8 taskId, s32 direction);
static enum FlyDestTab GetDefaultFlyDestTab(void);

static EWRAM_DATA bool8 sOpenedFromPartyMenu = FALSE;
static EWRAM_DATA u16 sFlyDestScrollOffset = 0;
static EWRAM_DATA u16 sFlyDestSelectedRow = 0;
static EWRAM_DATA struct ListMenuItem sFlyDestItems[FLY_DEST_LIST_CAPACITY] = {0};
static EWRAM_DATA u8 sFlyDestNames[FLY_DEST_LIST_CAPACITY][FLY_DEST_NAME_LENGTH] = {0};

static const u16 sFlyDestBgPal[] = {RGB(17, 18, 31)};

static const u8 sText_Kanto[] = _("Kanto");
static const u8 sText_Johto[] = _("Johto");
static const u8 sText_Sinnoh[] = _("Sinnoh");
static const u8 sText_NoDestinations[] = _("No destinations");
static const u8 sText_FlyDestFooter[] = _("A: Fly  B: Cancel  {L_BUTTON}{R_BUTTON}: Region");
static const u8 sText_LButton[] = _("{L_BUTTON}");
static const u8 sText_RButton[] = _("{R_BUTTON}");

static const u8 *const sFlyTabNames[FLY_TAB_COUNT] = {
    [FLY_TAB_KANTO] = sText_Kanto,
    [FLY_TAB_JOHTO] = sText_Johto,
    [FLY_TAB_SINNOH] = sText_Sinnoh,
};

static const struct BgTemplate sFlyDestBgTemplates[] = {
    {
        .bg = 1,
        .charBaseIndex = 1,
        .mapBaseIndex = 30,
        .screenSize = 0,
        .paletteMode = 0,
        .priority = 0,
        .baseTile = 0,
    },
    {
        .bg = 0,
        .charBaseIndex = 1,
        .mapBaseIndex = 31,
        .screenSize = 0,
        .paletteMode = 0,
        .priority = 1,
        .baseTile = 0,
    },
};

static const struct WindowTemplate sFlyDestWinTemplates[] = {
    [WIN_FLY_HEADER] = {
        .bg = 1,
        .tilemapLeft = 2,
        .tilemapTop = 1,
        .width = 26,
        .height = 2,
        .paletteNum = 15,
        .baseBlock = 1,
    },
    [WIN_FLY_LIST] = {
        .bg = 0,
        .tilemapLeft = 2,
        .tilemapTop = 4,
        .width = 26,
        .height = 12,
        .paletteNum = 15,
        .baseBlock = 53,
    },
    [WIN_FLY_FOOTER] = {
        .bg = 1,
        .tilemapLeft = 2,
        .tilemapTop = 17,
        .width = 26,
        .height = 2,
        .paletteNum = 15,
        .baseBlock = 365,
    },
    DUMMY_WIN_TEMPLATE,
};

static const struct FlyDest sFlyDests[] = {
    // Kanto mainland
    {REGION_KANTO, HEAL_LOCATION_PALLET_TOWN, MAPSEC_PALLET_TOWN, FLAG_WORLD_MAP_PALLET_TOWN},
    {REGION_KANTO, HEAL_LOCATION_VIRIDIAN_CITY, MAPSEC_VIRIDIAN_CITY, FLAG_WORLD_MAP_VIRIDIAN_CITY},
    {REGION_KANTO, HEAL_LOCATION_PEWTER_CITY, MAPSEC_PEWTER_CITY, FLAG_WORLD_MAP_PEWTER_CITY},
    {REGION_KANTO, HEAL_LOCATION_CERULEAN_CITY, MAPSEC_CERULEAN_CITY, FLAG_WORLD_MAP_CERULEAN_CITY},
    {REGION_KANTO, HEAL_LOCATION_LAVENDER_TOWN, MAPSEC_LAVENDER_TOWN, FLAG_WORLD_MAP_LAVENDER_TOWN},
    {REGION_KANTO, HEAL_LOCATION_VERMILION_CITY, MAPSEC_VERMILION_CITY, FLAG_WORLD_MAP_VERMILION_CITY},
    {REGION_KANTO, HEAL_LOCATION_CELADON_CITY, MAPSEC_CELADON_CITY, FLAG_WORLD_MAP_CELADON_CITY},
    {REGION_KANTO, HEAL_LOCATION_FUCHSIA_CITY, MAPSEC_FUCHSIA_CITY, FLAG_WORLD_MAP_FUCHSIA_CITY},
    {REGION_KANTO, HEAL_LOCATION_CINNABAR_ISLAND, MAPSEC_CINNABAR_ISLAND, FLAG_WORLD_MAP_CINNABAR_ISLAND},
    {REGION_KANTO, HEAL_LOCATION_INDIGO_PLATEAU, MAPSEC_INDIGO_PLATEAU, FLAG_WORLD_MAP_INDIGO_PLATEAU_EXTERIOR},
    {REGION_KANTO, HEAL_LOCATION_SAFFRON_CITY, MAPSEC_SAFFRON_CITY, FLAG_WORLD_MAP_SAFFRON_CITY},
    {REGION_KANTO, HEAL_LOCATION_ROUTE4, MAPSEC_ROUTE_4_POKECENTER, FLAG_WORLD_MAP_ROUTE4_POKEMON_CENTER_1F},
    {REGION_KANTO, HEAL_LOCATION_ROUTE10, MAPSEC_ROUTE_10_POKECENTER, FLAG_WORLD_MAP_ROUTE10_POKEMON_CENTER_1F},
    // Sevii (shown on the Kanto tab)
    {REGION_KANTO, HEAL_LOCATION_ONE_ISLAND, MAPSEC_ONE_ISLAND, FLAG_WORLD_MAP_ONE_ISLAND},
    {REGION_KANTO, HEAL_LOCATION_TWO_ISLAND, MAPSEC_TWO_ISLAND, FLAG_WORLD_MAP_TWO_ISLAND},
    {REGION_KANTO, HEAL_LOCATION_THREE_ISLAND, MAPSEC_THREE_ISLAND, FLAG_WORLD_MAP_THREE_ISLAND},
    {REGION_KANTO, HEAL_LOCATION_FOUR_ISLAND, MAPSEC_FOUR_ISLAND, FLAG_WORLD_MAP_FOUR_ISLAND},
    {REGION_KANTO, HEAL_LOCATION_FIVE_ISLAND, MAPSEC_FIVE_ISLAND, FLAG_WORLD_MAP_FIVE_ISLAND},
    {REGION_KANTO, HEAL_LOCATION_SIX_ISLAND, MAPSEC_SIX_ISLAND, FLAG_WORLD_MAP_SIX_ISLAND},
    {REGION_KANTO, HEAL_LOCATION_SEVEN_ISLAND, MAPSEC_SEVEN_ISLAND, FLAG_WORLD_MAP_SEVEN_ISLAND},
    // Johto
    {REGION_JOHTO, HEAL_LOCATION_NEW_BARK_TOWN, MAPSEC_NEW_BARK_TOWN, FLAG_WORLD_MAP_NEW_BARK_TOWN},
    {REGION_JOHTO, HEAL_LOCATION_CHERRYGROVE_CITY, MAPSEC_CHERRYGROVE_CITY, FLAG_WORLD_MAP_CHERRYGROVE_CITY},
    {REGION_JOHTO, HEAL_LOCATION_VIOLET_CITY, MAPSEC_VIOLET_CITY, FLAG_WORLD_MAP_VIOLET_CITY},
    {REGION_JOHTO, HEAL_LOCATION_AZALEA_TOWN, MAPSEC_AZALEA_TOWN, FLAG_WORLD_MAP_AZALEA_TOWN},
    {REGION_JOHTO, HEAL_LOCATION_GOLDENROD_CITY, MAPSEC_GOLDENROD_CITY, FLAG_WORLD_MAP_GOLDENROD_CITY},
    {REGION_JOHTO, HEAL_LOCATION_ECRUTEAK_CITY, MAPSEC_ECRUTEAK_CITY, FLAG_WORLD_MAP_ECRUTEAK_CITY},
    {REGION_JOHTO, HEAL_LOCATION_OLIVINE_CITY, MAPSEC_OLIVINE_CITY, FLAG_WORLD_MAP_OLIVINE_CITY},
    {REGION_JOHTO, HEAL_LOCATION_CIANWOOD_CITY, MAPSEC_CIANWOOD_CITY, FLAG_WORLD_MAP_CIANWOOD_CITY},
    {REGION_JOHTO, HEAL_LOCATION_MAHOGANY_TOWN, MAPSEC_MAHOGANY_TOWN, FLAG_WORLD_MAP_MAHOGANY_TOWN},
    {REGION_JOHTO, HEAL_LOCATION_BLACKTHORN_CITY, MAPSEC_BLACKTHORN_CITY, FLAG_WORLD_MAP_BLACKTHORN_CITY},
    // Sinnoh
    {REGION_SINNOH, HEAL_LOCATION_TWINLEAF_TOWN, MAPSEC_TWINLEAF_TOWN, FLAG_WORLD_MAP_TWINLEAF_TOWN},
    {REGION_SINNOH, HEAL_LOCATION_SANDGEM_TOWN, MAPSEC_SANDGEM_TOWN, FLAG_WORLD_MAP_SANDGEM_TOWN},
    {REGION_SINNOH, HEAL_LOCATION_JUBILIFE_CITY, MAPSEC_JUBILIFE_CITY, FLAG_WORLD_MAP_JUBILIFE_CITY},
    {REGION_SINNOH, HEAL_LOCATION_OREBURGH_CITY, MAPSEC_OREBURGH_CITY, FLAG_WORLD_MAP_OREBURGH_CITY},
    {REGION_SINNOH, HEAL_LOCATION_FLOAROMA_TOWN, MAPSEC_FLOAROMA_TOWN, FLAG_WORLD_MAP_FLOAROMA_TOWN},
    {REGION_SINNOH, HEAL_LOCATION_ETERNA_CITY, MAPSEC_ETERNA_CITY, FLAG_WORLD_MAP_ETERNA_CITY},
    {REGION_SINNOH, HEAL_LOCATION_HEARTHOME_CITY, MAPSEC_HEARTHOME_CITY, FLAG_WORLD_MAP_HEARTHOME_CITY},
    {REGION_SINNOH, HEAL_LOCATION_SOLACEON_TOWN, MAPSEC_SOLACEON_TOWN, FLAG_WORLD_MAP_SOLACEON_TOWN},
    {REGION_SINNOH, HEAL_LOCATION_CELESTIC_TOWN, MAPSEC_CELESTIC_TOWN, FLAG_WORLD_MAP_CELESTIC_TOWN},
    {REGION_SINNOH, HEAL_LOCATION_VEILSTONE_CITY, MAPSEC_VEILSTONE_CITY, FLAG_WORLD_MAP_VEILSTONE_CITY},
    {REGION_SINNOH, HEAL_LOCATION_PASTORIA_CITY, MAPSEC_PASTORIA_CITY, FLAG_WORLD_MAP_PASTORIA_CITY},
    {REGION_SINNOH, HEAL_LOCATION_CANALAVE_CITY, MAPSEC_CANALAVE_CITY, FLAG_WORLD_MAP_CANALAVE_CITY},
    {REGION_SINNOH, HEAL_LOCATION_SNOWPOINT_CITY, MAPSEC_SNOWPOINT_CITY, FLAG_WORLD_MAP_SNOWPOINT_CITY},
    {REGION_SINNOH, HEAL_LOCATION_SUNYSHORE_CITY, MAPSEC_SUNYSHORE_CITY, FLAG_WORLD_MAP_SUNYSHORE_CITY},
    {REGION_SINNOH, HEAL_LOCATION_FIGHT_AREA, MAPSEC_FIGHT_AREA, FLAG_WORLD_MAP_FIGHT_AREA},
    {REGION_SINNOH, HEAL_LOCATION_SURVIVAL_AREA, MAPSEC_SURVIVAL_AREA, FLAG_WORLD_MAP_SURVIVAL_AREA},
    {REGION_SINNOH, HEAL_LOCATION_RESORT_AREA, MAPSEC_RESORT_AREA, FLAG_WORLD_MAP_RESORT_AREA},
};

#define tState          data[0]
#define tListTaskId     data[1]
#define tArrowTaskId    data[2]
#define tTab            data[3]
#define tItemCount      data[4]
#define tChoseDest      data[5]
#define tHealLocation   data[6]
#define tMaxShowed      data[7]

void FlyDest_SetOpenedFromPartyMenu(bool32 fromParty)
{
    sOpenedFromPartyMenu = fromParty;
}

void CB2_OpenFlyDestList(void)
{
    switch (gMain.state)
    {
    default:
    case 0:
        SetVBlankCallback(NULL);
        gMain.state++;
        break;
    case 1:
        DmaClearLarge16(3, (void *)VRAM, VRAM_SIZE, 0x1000);
        DmaClear32(3, OAM, OAM_SIZE);
        DmaClear16(3, PLTT, PLTT_SIZE);
        SetGpuReg(REG_OFFSET_DISPCNT, 0);
        SetGpuReg(REG_OFFSET_BG0CNT, 0);
        SetGpuReg(REG_OFFSET_BG0HOFS, 0);
        SetGpuReg(REG_OFFSET_BG0VOFS, 0);
        SetGpuReg(REG_OFFSET_BG1CNT, 0);
        SetGpuReg(REG_OFFSET_BG1HOFS, 0);
        SetGpuReg(REG_OFFSET_BG1VOFS, 0);
        SetGpuReg(REG_OFFSET_BG2CNT, 0);
        SetGpuReg(REG_OFFSET_BG2HOFS, 0);
        SetGpuReg(REG_OFFSET_BG2VOFS, 0);
        SetGpuReg(REG_OFFSET_BG3CNT, 0);
        SetGpuReg(REG_OFFSET_BG3HOFS, 0);
        SetGpuReg(REG_OFFSET_BG3VOFS, 0);
        SetGpuReg(REG_OFFSET_WIN0H, 0);
        SetGpuReg(REG_OFFSET_WIN0V, 0);
        SetGpuReg(REG_OFFSET_WIN1H, 0);
        SetGpuReg(REG_OFFSET_WIN1V, 0);
        SetGpuReg(REG_OFFSET_WININ, 0);
        SetGpuReg(REG_OFFSET_WINOUT, 0);
        SetGpuReg(REG_OFFSET_BLDCNT, 0);
        SetGpuReg(REG_OFFSET_BLDALPHA, 0);
        SetGpuReg(REG_OFFSET_BLDY, 0);
        ResetBgsAndClearDma3BusyFlags(0);
        InitBgsFromTemplates(0, sFlyDestBgTemplates, ARRAY_COUNT(sFlyDestBgTemplates));
        ChangeBgX(0, 0, BG_COORD_SET);
        ChangeBgY(0, 0, BG_COORD_SET);
        ChangeBgX(1, 0, BG_COORD_SET);
        ChangeBgY(1, 0, BG_COORD_SET);
        ChangeBgX(2, 0, BG_COORD_SET);
        ChangeBgY(2, 0, BG_COORD_SET);
        ChangeBgX(3, 0, BG_COORD_SET);
        ChangeBgY(3, 0, BG_COORD_SET);
        InitWindows(sFlyDestWinTemplates);
        DeactivateAllTextPrinters();
        SetGpuReg(REG_OFFSET_DISPCNT, DISPCNT_OBJ_ON | DISPCNT_OBJ_1D_MAP);
        ShowBg(0);
        ShowBg(1);
        gMain.state++;
        break;
    case 2:
        ResetPaletteFade();
        ScanlineEffect_Stop();
        ResetTasks();
        ResetSpriteData();
        FreeAllSpritePalettes();
        gMain.state++;
        break;
    case 3:
        LoadUserWindowBorderGfx(0, FLY_FRAME_BASE_TILE, BG_PLTT_ID(STD_WINDOW_PALETTE_NUM));
        LoadPalette(gStandardMenuPalette, BG_PLTT_ID(15), PLTT_SIZE_4BPP);
        LoadPalette(sFlyDestBgPal, BG_PLTT_ID(0), sizeof(sFlyDestBgPal));
        Menu_LoadStdPal();
        ClearScheduledBgCopiesToVram();
        gMain.state++;
        break;
    case 4:
        InitFlyDestWindows();
        gMain.state++;
        break;
    case 5:
    {
        u8 taskId = CreateTask(Task_FlyDestFadeIn, 0);

        gTasks[taskId].tListTaskId = TASK_NONE;
        gTasks[taskId].tArrowTaskId = TASK_NONE;
        gTasks[taskId].tTab = GetDefaultFlyDestTab();
        gTasks[taskId].tChoseDest = FALSE;
        gTasks[taskId].tHealLocation = HEAL_LOCATION_NONE;
        DrawFlyDestHeaderForTask(taskId);
        DrawFlyDestFooter();
        BuildFlyDestList(taskId);
        BlendPalettes(PALETTES_ALL, 16, RGB_BLACK);
        BeginNormalPaletteFade(PALETTES_ALL, 0, 16, 0, RGB_BLACK);
        SetVBlankCallback(VBlankCB_FlyDest);
        SetMainCallback2(MainCB2_FlyDest);
        break;
    }
    }
}

static void MainCB2_FlyDest(void)
{
    RunTasks();
    AnimateSprites();
    BuildOamBuffer();
    DoScheduledBgTilemapCopiesToVram();
    UpdatePaletteFade();
}

static void VBlankCB_FlyDest(void)
{
    LoadOam();
    ProcessSpriteCopyRequests();
    TransferPlttBuffer();
}

static enum FlyDestTab GetDefaultFlyDestTab(void)
{
    switch (GetCurrentRegion())
    {
    case REGION_JOHTO:
        return FLY_TAB_JOHTO;
    case REGION_SINNOH:
        return FLY_TAB_SINNOH;
    default:
        return FLY_TAB_KANTO;
    }
}

static u8 FlyTabToRegion(enum FlyDestTab tab)
{
    switch (tab)
    {
    case FLY_TAB_JOHTO:
        return REGION_JOHTO;
    case FLY_TAB_SINNOH:
        return REGION_SINNOH;
    default:
        return REGION_KANTO;
    }
}

static void CopyFlyDestMapName(u8 *dest, mapsec_u16_t mapSec)
{
    const u8 *src;
    u32 i;

    dest[0] = EOS;
    if (mapSec >= MAPSEC_NONE)
        return;

    src = gRegionMapEntries[mapSec].name;
    if (src == NULL)
        return;

    for (i = 0; i < FLY_DEST_NAME_LENGTH - 1; i++)
    {
        dest[i] = src[i];
        if (src[i] == EOS)
            return;
    }
    dest[FLY_DEST_NAME_LENGTH - 1] = EOS;
}

static void InitFlyDestWindows(void)
{
    FillWindowPixelBuffer(WIN_FLY_HEADER, PIXEL_FILL(1));
    FillWindowPixelBuffer(WIN_FLY_LIST, PIXEL_FILL(1));
    FillWindowPixelBuffer(WIN_FLY_FOOTER, PIXEL_FILL(1));
    PutWindowTilemap(WIN_FLY_HEADER);
    PutWindowTilemap(WIN_FLY_LIST);
    PutWindowTilemap(WIN_FLY_FOOTER);
    DrawStdFrameWithCustomTileAndPalette(WIN_FLY_HEADER, FALSE, FLY_FRAME_BASE_TILE, STD_WINDOW_PALETTE_NUM);
    DrawStdFrameWithCustomTileAndPalette(WIN_FLY_LIST, FALSE, FLY_FRAME_BASE_TILE, STD_WINDOW_PALETTE_NUM);
    DrawStdFrameWithCustomTileAndPalette(WIN_FLY_FOOTER, FALSE, FLY_FRAME_BASE_TILE, STD_WINDOW_PALETTE_NUM);
    ScheduleBgCopyTilemapToVram(0);
    ScheduleBgCopyTilemapToVram(1);
}

static void DrawFlyDestHeaderForTask(u8 taskId)
{
    const u8 *name = sFlyTabNames[gTasks[taskId].tTab];

    FillWindowPixelBuffer(WIN_FLY_HEADER, PIXEL_FILL(1));
    AddTextPrinterParameterized(WIN_FLY_HEADER, FONT_NORMAL, sText_LButton, 4, 1, TEXT_SKIP_DRAW, NULL);
    AddTextPrinterParameterized(WIN_FLY_HEADER, FONT_NORMAL, name, GetStringCenterAlignXOffset(FONT_NORMAL, name, 208), 1, TEXT_SKIP_DRAW, NULL);
    AddTextPrinterParameterized(WIN_FLY_HEADER, FONT_NORMAL, sText_RButton, 192, 1, TEXT_SKIP_DRAW, NULL);
    CopyWindowToVram(WIN_FLY_HEADER, COPYWIN_FULL);
}

static void DrawFlyDestFooter(void)
{
    FillWindowPixelBuffer(WIN_FLY_FOOTER, PIXEL_FILL(1));
    AddTextPrinterParameterized(WIN_FLY_FOOTER, FONT_NARROW, sText_FlyDestFooter, 4, 1, TEXT_SKIP_DRAW, NULL);
    CopyWindowToVram(WIN_FLY_FOOTER, COPYWIN_FULL);
}

static void DestroyFlyDestList(u8 taskId)
{
    if (gTasks[taskId].tListTaskId != TASK_NONE)
    {
        DestroyListMenuTask(gTasks[taskId].tListTaskId, &sFlyDestScrollOffset, &sFlyDestSelectedRow);
        gTasks[taskId].tListTaskId = TASK_NONE;
    }
    if (gTasks[taskId].tArrowTaskId != TASK_NONE)
    {
        RemoveScrollIndicatorArrowPair(gTasks[taskId].tArrowTaskId);
        gTasks[taskId].tArrowTaskId = TASK_NONE;
    }
}

static void BuildFlyDestList(u8 taskId)
{
    struct ListMenuTemplate template;
    u8 region = FlyTabToRegion(gTasks[taskId].tTab);
    u32 i, count = 0;
    u8 showed;

    DestroyFlyDestList(taskId);
    FillWindowPixelBuffer(WIN_FLY_LIST, PIXEL_FILL(1));

    for (i = 0; i < ARRAY_COUNT(sFlyDests); i++)
    {
        if (sFlyDests[i].region == region && FlagGet(sFlyDests[i].flag))
        {
            if (count >= FLY_DEST_LIST_CAPACITY)
                break;
            CopyFlyDestMapName(sFlyDestNames[count], sFlyDests[i].mapSec);
            sFlyDestItems[count].name = sFlyDestNames[count];
            sFlyDestItems[count].id = i;
            count++;
        }
    }

    if (count == 0)
    {
        sFlyDestItems[0].name = sText_NoDestinations;
        sFlyDestItems[0].id = LIST_CANCEL;
        count = 1;
    }

    gTasks[taskId].tItemCount = count;
    sFlyDestScrollOffset = 0;
    sFlyDestSelectedRow = 0;

    showed = (count < FLY_DEST_MAX_SHOWED) ? count : FLY_DEST_MAX_SHOWED;
    gTasks[taskId].tMaxShowed = showed;

    memset(&template, 0, sizeof(template));
    template.items = sFlyDestItems;
    template.moveCursorFunc = ListMenuDefaultCursorMoveFunc;
    template.itemPrintFunc = NULL;
    template.totalItems = count;
    template.maxShowed = showed;
    template.windowId = WIN_FLY_LIST;
    template.header_X = 0;
    template.item_X = 8;
    template.cursor_X = 0;
    template.upText_Y = 1;
    template.cursorPal = 2;
    template.fillValue = 1;
    template.cursorShadowPal = 3;
    template.lettersSpacing = 0;
    template.itemVerticalPadding = 0;
    template.scrollMultiple = LIST_MULTIPLE_SCROLL_DPAD;
    template.fontId = FONT_NORMAL;
    template.cursorKind = CURSOR_BLACK_ARROW;

    gTasks[taskId].tListTaskId = ListMenuInit(&template, 0, 0);
    if (count > showed)
    {
        gTasks[taskId].tArrowTaskId = AddScrollIndicatorArrowPairParameterized(
            SCROLL_ARROW_UP,
            220,
            40,
            136,
            count - showed,
            TAG_FLY_SCROLL_ARROW,
            TAG_FLY_SCROLL_ARROW,
            &sFlyDestScrollOffset);
    }
    CopyWindowToVram(WIN_FLY_LIST, COPYWIN_FULL);
    ScheduleBgCopyTilemapToVram(0);
}

static void SwitchFlyDestTab(u8 taskId, s32 direction)
{
    s32 tab = gTasks[taskId].tTab + direction;

    if (tab < 0)
        tab = FLY_TAB_COUNT - 1;
    else if (tab >= FLY_TAB_COUNT)
        tab = 0;

    gTasks[taskId].tTab = tab;
    PlaySE(SE_SELECT);
    DrawFlyDestHeaderForTask(taskId);
    BuildFlyDestList(taskId);
}

static void Task_FlyDestFadeIn(u8 taskId)
{
    if (!gPaletteFade.active)
        gTasks[taskId].func = Task_FlyDestHandleInput;
}

static void Task_FlyDestHandleInput(u8 taskId)
{
    s32 input;
    u8 listTaskId = gTasks[taskId].tListTaskId;

    if (JOY_NEW(L_BUTTON))
    {
        SwitchFlyDestTab(taskId, -1);
        return;
    }
    if (JOY_NEW(R_BUTTON))
    {
        SwitchFlyDestTab(taskId, 1);
        return;
    }

    if (listTaskId == TASK_NONE)
        return;

    input = ListMenu_ProcessInput(listTaskId);
    ListMenuGetScrollAndRow(listTaskId, &sFlyDestScrollOffset, &sFlyDestSelectedRow);
    switch (input)
    {
    case LIST_NOTHING_CHOSEN:
        break;
    case LIST_CANCEL:
        PlaySE(SE_SELECT);
        gTasks[taskId].tChoseDest = FALSE;
        BeginNormalPaletteFade(PALETTES_ALL, 0, 0, 16, RGB_BLACK);
        gTasks[taskId].func = Task_FlyDestFadeOut;
        break;
    default:
        if (input < 0 || input >= (s32)ARRAY_COUNT(sFlyDests))
            break;
        PlaySE(SE_SELECT);
        gTasks[taskId].tChoseDest = TRUE;
        gTasks[taskId].tHealLocation = sFlyDests[input].healLocation;
        BeginNormalPaletteFade(PALETTES_ALL, 0, 0, 16, RGB_BLACK);
        gTasks[taskId].func = Task_FlyDestFadeOut;
        break;
    }
}

static void Task_FlyDestFadeOut(u8 taskId)
{
    bool32 choseDest;
    u16 healLocation;

    if (gPaletteFade.active)
        return;

    choseDest = gTasks[taskId].tChoseDest;
    healLocation = gTasks[taskId].tHealLocation;
    DestroyFlyDestList(taskId);
    SetVBlankCallback(NULL);
    FreeAllWindowBuffers();
    DestroyTask(taskId);

    if (choseDest)
    {
        SetWarpDestinationToHealLocation(healLocation);
        ReturnToFieldFromFlyMapSelect();
    }
    else if (sOpenedFromPartyMenu)
    {
        SetMainCallback2(CB2_ReturnToPartyMenuFromFlyMap);
    }
    else
    {
        if (gMain.savedCallback == NULL)
            gMain.savedCallback = CB2_ReturnToFieldWithOpenMenu;
        SetMainCallback2(gMain.savedCallback);
    }
}

#undef tState
#undef tListTaskId
#undef tArrowTaskId
#undef tTab
#undef tItemCount
#undef tChoseDest
#undef tHealLocation
#undef tMaxShowed
