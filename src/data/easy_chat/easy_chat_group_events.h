const u8 gEasyChatWord_Appeal[] = _("Appeal");
const u8 gEasyChatWord_Events[] = _("Events");
const u8 gEasyChatWord_StayAtHome[] = _("Stay-at-Home");
const u8 gEasyChatWord_Berry[] = _("Berry");
const u8 gEasyChatWord_Contest[] = _("Contest");
const u8 gEasyChatWord_Mc[] = _("Mc");
const u8 gEasyChatWord_Judge[] = _("Judge");
const u8 gEasyChatWord_Super[] = _("Super");
const u8 gEasyChatWord_Stage[] = _("Stage");
const u8 gEasyChatWord_HallOfFame[] = _("Hall of Fame");
const u8 gEasyChatWord_Evolution[] = _("Evolution");
const u8 gEasyChatWord_Hyper[] = _("Hyper");
const u8 gEasyChatWord_BattleTower[] = _("Battle Tower");
const u8 gEasyChatWord_Leaders[] = _("Leaders");
const u8 gEasyChatWord_BattleRoom[] = _("Battle Room");
const u8 gEasyChatWord_Hidden[] = _("Hidden");
const u8 gEasyChatWord_SecretBase[] = _("Secret Base");
const u8 gEasyChatWord_Blend[] = _("Blend");
const u8 gEasyChatWord_POKEBLOCK[] = _("{POKEBLOCK}");
const u8 gEasyChatWord_Master[] = _("Master");
const u8 gEasyChatWord_Rank[] = _("Rank");
const u8 gEasyChatWord_Ribbon[] = _("Ribbon");
const u8 gEasyChatWord_Crush[] = _("Crush");
const u8 gEasyChatWord_Direct[] = _("Direct");
const u8 gEasyChatWord_Tower[] = _("Tower");
const u8 gEasyChatWord_Union[] = _("Union");
const u8 gEasyChatWord_Room[] = _("Room");
const u8 gEasyChatWord_Wireless[] = _("Wireless");
const u8 gEasyChatWord_Frontier[] = _("Frontier");

const struct EasyChatWordInfo gEasyChatGroup_Events[] = {
    [EC_INDEX(EC_WORD_APPEAL)] =
    {
        .text = COMPOUND_STRING("Appeal"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_APPEAL),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_EVENTS)] =
    {
        .text = COMPOUND_STRING("Events"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_BATTLE_ROOM),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_STAY_AT_HOME)] =
    {
        .text = COMPOUND_STRING("Stay-at-Home"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_BATTLE_TOWER),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_BERRY)] =
    {
        .text = COMPOUND_STRING("Berry"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_BERRY),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_CONTEST)] =
    {
        .text = COMPOUND_STRING("Contest"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_BLEND),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_MC)] =
    {
        .text = COMPOUND_STRING("Mc"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_CONTEST),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_JUDGE)] =
    {
        .text = COMPOUND_STRING("Judge"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_CRUSH),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_SUPER)] =
    {
        .text = COMPOUND_STRING("Super"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_DIRECT),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_STAGE)] =
    {
        .text = COMPOUND_STRING("Stage"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_EVENTS),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_HALL_OF_FAME)] =
    {
        .text = COMPOUND_STRING("Hall of Fame"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_EVOLUTION),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_EVOLUTION)] =
    {
        .text = COMPOUND_STRING("Evolution"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_FRONTIER),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_HYPER)] =
    {
        .text = COMPOUND_STRING("Hyper"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_HALL_OF_FAME),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_BATTLE_TOWER)] =
    {
        .text = COMPOUND_STRING("Battle Tower"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_HIDDEN),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_LEADERS)] =
    {
        .text = COMPOUND_STRING("Leaders"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_HYPER),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_BATTLE_ROOM)] =
    {
        .text = COMPOUND_STRING("Battle Room"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_JUDGE),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_HIDDEN)] =
    {
        .text = COMPOUND_STRING("Hidden"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_LEADERS),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_SECRET_BASE)] =
    {
        .text = COMPOUND_STRING("Secret Base"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_MASTER),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_BLEND)] =
    {
        .text = COMPOUND_STRING("Blend"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_MC),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_POKEBLOCK)] =
    {
        .text = COMPOUND_STRING("{POKEBLOCK}"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_POKEBLOCK),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_MASTER)] =
    {
        .text = COMPOUND_STRING("Master"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_RANK),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_RANK)] =
    {
        .text = COMPOUND_STRING("Rank"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_RIBBON),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_RIBBON)] =
    {
        .text = COMPOUND_STRING("Ribbon"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_ROOM),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_CRUSH)] =
    {
        .text = COMPOUND_STRING("Crush"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_SECRET_BASE),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_DIRECT)] =
    {
        .text = COMPOUND_STRING("Direct"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_STAGE),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_TOWER)] =
    {
        .text = COMPOUND_STRING("Tower"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_STAY_AT_HOME),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_UNION)] =
    {
        .text = COMPOUND_STRING("Union"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_SUPER),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_ROOM)] =
    {
        .text = COMPOUND_STRING("Room"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_TOWER),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_WIRELESS)] =
    {
        .text = COMPOUND_STRING("Wireless"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_UNION),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_FRONTIER)] =
    {
        .text = COMPOUND_STRING("Frontier"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_WIRELESS),
        .enabled = TRUE,
    },
};
