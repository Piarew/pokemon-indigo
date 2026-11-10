#include "global.h"
#include "battle.h"
#include "event_data.h"
#include "item.h"
#include "list_menu.h"
#include "mail.h"
#include "malloc.h"
#include "menu.h"
#include "move.h"
#include "move_distiller.h"
#include "overworld.h"
#include "party_menu.h"
#include "pokemon.h"
#include "pokemon_storage_system.h"
#include "script.h"
#include "script_menu.h"
#include "sound.h"
#include "string_util.h"
#include "strings.h"
#include "task.h"
#include "text.h"
#include "window.h"
#include "constants/items.h"
#include "constants/moves.h"
#include "constants/party_menu.h"
#include "constants/songs.h"

#define DISTILLER_LIST_MAX_SHOWED 6

static EWRAM_DATA bool8 sDistillerTutorActive = FALSE;
static EWRAM_DATA struct ListMenuItem *sDistillerListItems = NULL;

static bool32 SetMoveDistilled(enum Move move);
static u32 GetMonMoveCountAndFirst(struct Pokemon *mon, enum Move *outMove);
static struct Pokemon *GetSelectedPartyMon(void);
static void Task_DistillerChooseMove(u8 taskId);
static void DistillerCloseMoveMenu(u8 taskId, bool32 choseMove, enum Move move);

bool32 IsMoveDistillable(enum Move move)
{
    if (move == MOVE_NONE || move >= MOVES_COUNT)
        return FALSE;
    if (move == MOVE_STRUGGLE || move == MOVE_SKETCH)
        return FALSE;
    if (GetMoveEffect(move) == EFFECT_PLACEHOLDER)
        return FALSE;
    return TRUE;
}

bool32 IsMoveDistilled(enum Move move)
{
    if (move == MOVE_NONE || move >= MOVES_COUNT)
        return FALSE;
    if ((move / 8) >= DISTILLED_MOVE_BYTES)
        return FALSE;
    return (gSaveBlock3Ptr->distilledMoves[move / 8] & (1 << (move % 8))) != 0;
}

bool32 IsDistillerTutorActive(void)
{
    return sDistillerTutorActive;
}

u32 CountDistilledMoves(void)
{
    u32 i, count = 0;

    for (i = 1; i < MOVES_COUNT; i++)
    {
        if (IsMoveDistilled(i))
            count++;
    }
    return count;
}

static bool32 SetMoveDistilled(enum Move move)
{
    if (!IsMoveDistillable(move))
        return FALSE;
    if ((move / 8) >= DISTILLED_MOVE_BYTES)
        return FALSE;
    gSaveBlock3Ptr->distilledMoves[move / 8] |= (1 << (move % 8));
    return TRUE;
}

static struct Pokemon *GetSelectedPartyMon(void)
{
    if (gSpecialVar_0x8004 >= PARTY_SIZE)
        return NULL;
    return &gParties[B_TRAINER_PLAYER][gSpecialVar_0x8004];
}

static u32 GetMonMoveCountAndFirst(struct Pokemon *mon, enum Move *outMove)
{
    u32 i, count = 0;
    enum Move first = MOVE_NONE;

    for (i = 0; i < MAX_MON_MOVES; i++)
    {
        enum Move move = GetMonData(mon, MON_DATA_MOVE1 + i);
        if (move != MOVE_NONE)
        {
            if (first == MOVE_NONE)
                first = move;
            count++;
        }
    }
    if (outMove != NULL)
        *outMove = first;
    return count;
}

static void BufferSelectedMonStrings(struct Pokemon *mon, enum Move move)
{
    GetMonNickname(mon, gStringVar1);
    if (move != MOVE_NONE)
        StringCopy(gStringVar2, GetMoveName(move));
    else
        gStringVar2[0] = EOS;
    gSpecialVar_0x8005 = move;
}

void DistillerInspectSelectedMon(void)
{
    struct Pokemon *mon = GetSelectedPartyMon();
    enum Move move = MOVE_NONE;
    u32 moveCount;

    gSpecialVar_Result = DISTILLER_ERR_NOT_SINGLE_MOVE;
    gSpecialVar_0x8005 = MOVE_NONE;
    if (mon == NULL || GetMonData(mon, MON_DATA_SPECIES) == SPECIES_NONE)
        return;

    BufferSelectedMonStrings(mon, MOVE_NONE);
    if (GetMonData(mon, MON_DATA_IS_EGG))
    {
        gSpecialVar_Result = DISTILLER_ERR_EGG;
        return;
    }

    moveCount = GetMonMoveCountAndFirst(mon, &move);
    BufferSelectedMonStrings(mon, move);

    if (CountPartyNonEggMons() <= 1)
    {
        gSpecialVar_Result = DISTILLER_ERR_LAST_MON;
        return;
    }
    if (moveCount != 1)
    {
        gSpecialVar_Result = DISTILLER_ERR_NOT_SINGLE_MOVE;
        return;
    }
    if (!IsMoveDistillable(move))
    {
        gSpecialVar_Result = DISTILLER_ERR_FORBIDDEN_MOVE;
        return;
    }

    gSpecialVar_Result = DISTILLER_OK;
}

void DistillerDonateSelectedMon(void)
{
    struct Pokemon *mon = GetSelectedPartyMon();
    enum Move move = MOVE_NONE;
    enum Item tmItem;
    u32 result;

    DistillerInspectSelectedMon();
    if (gSpecialVar_Result != DISTILLER_OK)
        return;

    mon = GetSelectedPartyMon();
    GetMonMoveCountAndFirst(mon, &move);
    tmItem = GetTMHMItemIdFromMoveId(move);

    if (tmItem != ITEM_NONE)
    {
        if (CheckBagHasItem(tmItem, 1))
        {
            result = DISTILLER_OK_ALREADY_HAD_TM;
        }
        else if (!CheckBagHasSpace(tmItem, 1))
        {
            gSpecialVar_Result = DISTILLER_ERR_BAG_FULL;
            return;
        }
        else
        {
            result = DISTILLER_OK_TM;
        }
    }
    else
    {
        result = DISTILLER_OK_ARCHIVED;
    }

    BufferSelectedMonStrings(mon, move);
    gSpecialVar_0x8000 = tmItem;
    SetMoveDistilled(move);
    if (MonHasMail(mon))
        TakeMailFromMon(mon);
    ZeroMonData(mon);
    CompactPartySlots();
    CalculatePlayerPartyCount();
    gSpecialVar_Result = result;
}

void DistillerHasArchivedMoves(void)
{
    gSpecialVar_Result = CountDistilledMoves() != 0;
}

void DistillerSetTutorActive(void)
{
    sDistillerTutorActive = TRUE;
}

void DistillerClearTutorActive(void)
{
    sDistillerTutorActive = FALSE;
}

void DistillerChooseArchivedMove(void)
{
    LockPlayerFieldControls();
    CreateTask(Task_DistillerChooseMove, 10);
}

static void Task_DistillerChooseMove(u8 taskId)
{
    u32 i, count, width, showed, height;
    u8 windowId;
    struct ListMenuTemplate template;

    if (gTasks[taskId].data[0] != 0)
    {
        s32 input = ListMenu_ProcessInput(gTasks[taskId].data[1]);
        switch (input)
        {
        case LIST_NOTHING_CHOSEN:
            break;
        case LIST_CANCEL:
            PlaySE(SE_SELECT);
            DistillerCloseMoveMenu(taskId, FALSE, MOVE_NONE);
            break;
        default:
            PlaySE(SE_SELECT);
            DistillerCloseMoveMenu(taskId, TRUE, input);
            break;
        }
        return;
    }

    count = CountDistilledMoves();
    if (count == 0)
    {
        gSpecialVar_Result = FALSE;
        gSpecialVar_0x8005 = MOVE_NONE;
        DestroyTask(taskId);
        ScriptContext_Enable();
        return;
    }

    sDistillerListItems = AllocZeroed((count + 1) * sizeof(struct ListMenuItem));
    if (sDistillerListItems == NULL)
    {
        gSpecialVar_Result = FALSE;
        gSpecialVar_0x8005 = MOVE_NONE;
        DestroyTask(taskId);
        ScriptContext_Enable();
        return;
    }

    count = 0;
    for (i = 1; i < MOVES_COUNT; i++)
    {
        if (IsMoveDistilled(i))
        {
            sDistillerListItems[count].name = GetMoveName(i);
            sDistillerListItems[count].id = i;
            count++;
        }
    }

    for (i = 1; i < count; i++)
    {
        struct ListMenuItem key = sDistillerListItems[i];
        s32 j = i - 1;
        while (j >= 0 && StringCompare(sDistillerListItems[j].name, key.name) > 0)
        {
            sDistillerListItems[j + 1] = sDistillerListItems[j];
            j--;
        }
        sDistillerListItems[j + 1] = key;
    }

    sDistillerListItems[count].name = gText_Cancel;
    sDistillerListItems[count].id = LIST_CANCEL;
    count++;

    width = 0;
    for (i = 0; i < count; i++)
        width = DisplayTextAndGetWidth(sDistillerListItems[i].name, width);
    width = ConvertPixelWidthToTileWidth(width);
    if (width < 8)
        width = 8;
    if (width > 16)
        width = 16;

    showed = (count < DISTILLER_LIST_MAX_SHOWED) ? count : DISTILLER_LIST_MAX_SHOWED;
    height = showed * 2;

    LoadMessageBoxAndBorderGfx();
    windowId = CreateWindowFromRect(1, 1, width, height);
    SetStandardWindowBorderStyle(windowId, FALSE);

    memset(&template, 0, sizeof(template));
    template.items = sDistillerListItems;
    template.moveCursorFunc = ListMenuDefaultCursorMoveFunc;
    template.itemPrintFunc = NULL;
    template.totalItems = count;
    template.maxShowed = showed;
    template.windowId = windowId;
    template.header_X = 0;
    template.item_X = 8;
    template.cursor_X = 0;
    template.upText_Y = 1;
    template.cursorPal = 2;
    template.fillValue = 1;
    template.cursorShadowPal = 3;
    template.lettersSpacing = 0;
    template.itemVerticalPadding = 0;
    template.scrollMultiple = LIST_NO_MULTIPLE_SCROLL;
    template.fontId = FONT_NARROW;
    template.cursorKind = CURSOR_BLACK_ARROW;

    gTasks[taskId].data[0] = 1;
    gTasks[taskId].data[1] = ListMenuInit(&template, 0, 0);
    gTasks[taskId].data[2] = windowId;
    ScheduleBgCopyTilemapToVram(0);
}

static void DistillerCloseMoveMenu(u8 taskId, bool32 choseMove, enum Move move)
{
    DestroyListMenuTask(gTasks[taskId].data[1], NULL, NULL);
    ClearToTransparentAndRemoveWindow(gTasks[taskId].data[2]);
    if (sDistillerListItems != NULL)
    {
        Free(sDistillerListItems);
        sDistillerListItems = NULL;
    }
    gSpecialVar_Result = choseMove;
    gSpecialVar_0x8005 = choseMove ? move : MOVE_NONE;
    DestroyTask(taskId);
    ScriptContext_Enable();
}
