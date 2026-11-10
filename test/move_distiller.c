#include "global.h"
#include "battle.h"
#include "event_data.h"
#include "item.h"
#include "move_distiller.h"
#include "pokemon.h"
#include "test/test.h"

static void ResetDistillerTestParty(void)
{
    u32 i;

    for (i = 0; i < PARTY_SIZE; i++)
        ZeroMonData(&gParties[B_TRAINER_PLAYER][i]);
    memset(gSaveBlock3Ptr->distilledMoves, 0, DISTILLED_MOVE_BYTES);
    gSpecialVar_0x8004 = 0;
    gSpecialVar_0x8005 = MOVE_NONE;
    gSpecialVar_Result = 0;
}

static void MakeTestMon(u32 slot, enum Species species, enum Move move1, enum Move move2)
{
    CreateMon(&gParties[B_TRAINER_PLAYER][slot], species, 50, 0, OTID_STRUCT_PRESET(0));
    SetMonMoveSlot(&gParties[B_TRAINER_PLAYER][slot], move1, 0);
    SetMonMoveSlot(&gParties[B_TRAINER_PLAYER][slot], move2, 1);
    SetMonMoveSlot(&gParties[B_TRAINER_PLAYER][slot], MOVE_NONE, 2);
    SetMonMoveSlot(&gParties[B_TRAINER_PLAYER][slot], MOVE_NONE, 3);
}

static void MakeTwoMonParty(enum Move firstMonMove, enum Move firstMonMove2)
{
    ResetDistillerTestParty();
    MakeTestMon(0, SPECIES_WOBBUFFET, firstMonMove, firstMonMove2);
    MakeTestMon(1, SPECIES_WYNAUT, MOVE_COUNTER, MOVE_NONE);
    CalculatePlayerPartyCount();
}

TEST("Distiller rejects a Pokémon that knows more than one move")
{
    MakeTwoMonParty(MOVE_EARTHQUAKE, MOVE_SURF);
    DistillerInspectSelectedMon();
    EXPECT_EQ(gSpecialVar_Result, DISTILLER_ERR_NOT_SINGLE_MOVE);
    EXPECT_EQ(GetMonData(&gParties[B_TRAINER_PLAYER][0], MON_DATA_SPECIES), SPECIES_WOBBUFFET);
}

TEST("Distiller rejects donating the last non-egg Pokémon")
{
    ResetDistillerTestParty();
    MakeTestMon(0, SPECIES_WOBBUFFET, MOVE_EARTHQUAKE, MOVE_NONE);
    CalculatePlayerPartyCount();
    DistillerInspectSelectedMon();
    EXPECT_EQ(gSpecialVar_Result, DISTILLER_ERR_LAST_MON);
}

TEST("Distiller rejects Sketch and Struggle")
{
    MakeTwoMonParty(MOVE_SKETCH, MOVE_NONE);
    DistillerInspectSelectedMon();
    EXPECT_EQ(gSpecialVar_Result, DISTILLER_ERR_FORBIDDEN_MOVE);

    MakeTwoMonParty(MOVE_STRUGGLE, MOVE_NONE);
    DistillerInspectSelectedMon();
    EXPECT_EQ(gSpecialVar_Result, DISTILLER_ERR_FORBIDDEN_MOVE);
}

TEST("Distiller gives a TM for a single-move donation when one exists")
{
    SetBagItemsPointers();
    MakeTwoMonParty(MOVE_EARTHQUAKE, MOVE_NONE);
    ASSUME(GetTMHMItemIdFromMoveId(MOVE_EARTHQUAKE) == ITEM_TM_EARTHQUAKE);

    DistillerInspectSelectedMon();
    EXPECT_EQ(gSpecialVar_Result, DISTILLER_OK);
    DistillerDonateSelectedMon();
    EXPECT_EQ(gSpecialVar_Result, DISTILLER_OK_TM);
    EXPECT_EQ(gSpecialVar_0x8000, ITEM_TM_EARTHQUAKE);
    EXPECT(IsMoveDistilled(MOVE_EARTHQUAKE));
    EXPECT_EQ(GetMonData(&gParties[B_TRAINER_PLAYER][0], MON_DATA_SPECIES), SPECIES_WYNAUT);
    EXPECT_EQ(gPartiesCount[B_TRAINER_PLAYER], 1);
}

TEST("Distiller archives a single move that has no TM")
{
    SetBagItemsPointers();
    MakeTwoMonParty(MOVE_SPORE, MOVE_NONE);
    ASSUME(GetTMHMItemIdFromMoveId(MOVE_SPORE) == ITEM_NONE);

    DistillerDonateSelectedMon();
    EXPECT_EQ(gSpecialVar_Result, DISTILLER_OK_ARCHIVED);
    EXPECT(IsMoveDistilled(MOVE_SPORE));
    EXPECT_EQ(GetMonData(&gParties[B_TRAINER_PLAYER][0], MON_DATA_SPECIES), SPECIES_WYNAUT);
    DistillerHasArchivedMoves();
    EXPECT_EQ(gSpecialVar_Result, TRUE);
}

TEST("Distiller reports an existing TM instead of duplicating it")
{
    SetBagItemsPointers();
    MakeTwoMonParty(MOVE_EARTHQUAKE, MOVE_NONE);
    EXPECT(AddBagItem(ITEM_TM_EARTHQUAKE, 1));

    DistillerDonateSelectedMon();
    EXPECT_EQ(gSpecialVar_Result, DISTILLER_OK_ALREADY_HAD_TM);
    EXPECT(IsMoveDistilled(MOVE_EARTHQUAKE));
    EXPECT_EQ(GetMonData(&gParties[B_TRAINER_PLAYER][0], MON_DATA_SPECIES), SPECIES_WYNAUT);
}
