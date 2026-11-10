const u8 gEasyChatWord_Meet[] = _("Meet");
const u8 gEasyChatWord_Play[] = _("Play");
const u8 gEasyChatWord_Hurried[] = _("Hurried");
const u8 gEasyChatWord_Goes[] = _("Goes");
const u8 gEasyChatWord_Giddy[] = _("Giddy");
const u8 gEasyChatWord_Happy[] = _("Happy");
const u8 gEasyChatWord_Happiness[] = _("Happiness");
const u8 gEasyChatWord_Excite[] = _("Excite");
const u8 gEasyChatWord_Important[] = _("Important");
const u8 gEasyChatWord_Funny[] = _("Funny");
const u8 gEasyChatWord_Got[] = _("Got");
const u8 gEasyChatWord_GoHome[] = _("Go Home");
const u8 gEasyChatWord_Disappointed[] = _("Disappointed");
const u8 gEasyChatWord_Disappoints[] = _("Disappoints");
const u8 gEasyChatWord_Sad[] = _("Sad");
const u8 gEasyChatWord_Try[] = _("Try");
const u8 gEasyChatWord_Tries[] = _("Tries");
const u8 gEasyChatWord_Hears[] = _("Hears");
const u8 gEasyChatWord_Think[] = _("Think");
const u8 gEasyChatWord_Hear[] = _("Hear");
const u8 gEasyChatWord_Wants[] = _("Wants");
const u8 gEasyChatWord_Misheard[] = _("Misheard");
const u8 gEasyChatWord_Dislike[] = _("Dislike");
const u8 gEasyChatWord_Angry[] = _("Angry");
const u8 gEasyChatWord_Anger[] = _("Anger");
const u8 gEasyChatWord_Scary[] = _("Scary");
const u8 gEasyChatWord_Lonesome[] = _("Lonesome");
const u8 gEasyChatWord_Disappoint[] = _("Disappoint");
const u8 gEasyChatWord_Joy[] = _("Joy");
const u8 gEasyChatWord_Gets[] = _("Gets");
const u8 gEasyChatWord_Never[] = _("Never");
const u8 gEasyChatWord_Darn[] = _("Darn");
const u8 gEasyChatWord_Downcast[] = _("Downcast");
const u8 gEasyChatWord_Incredible[] = _("Incredible");
const u8 gEasyChatWord_Likes[] = _("Likes");
const u8 gEasyChatWord_Dislikes[] = _("Dislikes");
const u8 gEasyChatWord_Boring[] = _("Boring");
const u8 gEasyChatWord_Care[] = _("Care");
const u8 gEasyChatWord_Cares[] = _("Cares");
const u8 gEasyChatWord_AllRight[] = _("All Right");
const u8 gEasyChatWord_Adore[] = _("Adore");
const u8 gEasyChatWord_Disaster[] = _("Disaster");
const u8 gEasyChatWord_Enjoy[] = _("Enjoy");
const u8 gEasyChatWord_Enjoys[] = _("Enjoys");
const u8 gEasyChatWord_Eat[] = _("Eat");
const u8 gEasyChatWord_Lacking[] = _("Lacking");
const u8 gEasyChatWord_Bad[] = _("Bad");
const u8 gEasyChatWord_Hard[] = _("Hard");
const u8 gEasyChatWord_Terrible[] = _("Terrible");
const u8 gEasyChatWord_Should[] = _("Should");
const u8 gEasyChatWord_Nice[] = _("Nice");
const u8 gEasyChatWord_Drink[] = _("Drink");
const u8 gEasyChatWord_Surprise[] = _("Surprise");
const u8 gEasyChatWord_Fear[] = _("Fear");
const u8 gEasyChatWord_Want[] = _("Want");
const u8 gEasyChatWord_Wait[] = _("Wait");
const u8 gEasyChatWord_Satisfied[] = _("Satisfied");
const u8 gEasyChatWord_See[] = _("See");
const u8 gEasyChatWord_Rare[] = _("Rare");
const u8 gEasyChatWord_Negative[] = _("Negative");
const u8 gEasyChatWord_Done[] = _("Done");
const u8 gEasyChatWord_Danger[] = _("Danger");
const u8 gEasyChatWord_Defeated[] = _("Defeated");
const u8 gEasyChatWord_Beat[] = _("Beat");
const u8 gEasyChatWord_Great[] = _("Great");
const u8 gEasyChatWord_Romantic[] = _("Romantic");
const u8 gEasyChatWord_Question[] = _("Question");
const u8 gEasyChatWord_Understand[] = _("Understand");
const u8 gEasyChatWord_Understands[] = _("Understands");

const struct EasyChatWordInfo gEasyChatGroup_Feelings[] = {
    [EC_INDEX(EC_WORD_MEET)] =
    {
        .text = COMPOUND_STRING("Meet"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_ADORE),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_PLAY)] =
    {
        .text = COMPOUND_STRING("Play"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_ALL_RIGHT),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_HURRIED)] =
    {
        .text = COMPOUND_STRING("Hurried"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_ANGER),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_GOES)] =
    {
        .text = COMPOUND_STRING("Goes"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_ANGRY),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_GIDDY)] =
    {
        .text = COMPOUND_STRING("Giddy"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_BAD),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_HAPPY)] =
    {
        .text = COMPOUND_STRING("Happy"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_BEAT),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_HAPPINESS)] =
    {
        .text = COMPOUND_STRING("Happiness"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_BORING),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_EXCITE)] =
    {
        .text = COMPOUND_STRING("Excite"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_CARE),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_IMPORTANT)] =
    {
        .text = COMPOUND_STRING("Important"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_CARES),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_FUNNY)] =
    {
        .text = COMPOUND_STRING("Funny"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_DANGER),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_GOT)] =
    {
        .text = COMPOUND_STRING("Got"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_DARN),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_GO_HOME)] =
    {
        .text = COMPOUND_STRING("Go Home"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_DEFEATED),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_DISAPPOINTED)] =
    {
        .text = COMPOUND_STRING("Disappointed"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_DISAPPOINT),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_DISAPPOINTS)] =
    {
        .text = COMPOUND_STRING("Disappoints"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_DISAPPOINTED),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_SAD)] =
    {
        .text = COMPOUND_STRING("Sad"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_DISAPPOINTS),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_TRY)] =
    {
        .text = COMPOUND_STRING("Try"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_DISASTER),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_TRIES)] =
    {
        .text = COMPOUND_STRING("Tries"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_DISLIKE),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_HEARS)] =
    {
        .text = COMPOUND_STRING("Hears"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_DISLIKES),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_THINK)] =
    {
        .text = COMPOUND_STRING("Think"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_DONE),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_HEAR)] =
    {
        .text = COMPOUND_STRING("Hear"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_DOWNCAST),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_WANTS)] =
    {
        .text = COMPOUND_STRING("Wants"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_DRINK),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_MISHEARD)] =
    {
        .text = COMPOUND_STRING("Misheard"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_EAT),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_DISLIKE)] =
    {
        .text = COMPOUND_STRING("Dislike"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_ENJOY),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_ANGRY)] =
    {
        .text = COMPOUND_STRING("Angry"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_ENJOYS),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_ANGER)] =
    {
        .text = COMPOUND_STRING("Anger"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_EXCITE),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_SCARY)] =
    {
        .text = COMPOUND_STRING("Scary"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_FEAR),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_LONESOME)] =
    {
        .text = COMPOUND_STRING("Lonesome"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_FUNNY),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_DISAPPOINT)] =
    {
        .text = COMPOUND_STRING("Disappoint"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_GETS),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_JOY)] =
    {
        .text = COMPOUND_STRING("Joy"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_GIDDY),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_GETS)] =
    {
        .text = COMPOUND_STRING("Gets"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_GO_HOME),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_NEVER)] =
    {
        .text = COMPOUND_STRING("Never"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_GOES),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_DARN)] =
    {
        .text = COMPOUND_STRING("Darn"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_GOT),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_DOWNCAST)] =
    {
        .text = COMPOUND_STRING("Downcast"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_GREAT),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_INCREDIBLE)] =
    {
        .text = COMPOUND_STRING("Incredible"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_HAPPINESS),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_LIKES)] =
    {
        .text = COMPOUND_STRING("Likes"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_HAPPY),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_DISLIKES)] =
    {
        .text = COMPOUND_STRING("Dislikes"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_HARD),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_BORING)] =
    {
        .text = COMPOUND_STRING("Boring"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_HEAR),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_CARE)] =
    {
        .text = COMPOUND_STRING("Care"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_HEARS),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_CARES)] =
    {
        .text = COMPOUND_STRING("Cares"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_HURRIED),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_ALL_RIGHT)] =
    {
        .text = COMPOUND_STRING("All Right"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_IMPORTANT),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_ADORE)] =
    {
        .text = COMPOUND_STRING("Adore"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_INCREDIBLE),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_DISASTER)] =
    {
        .text = COMPOUND_STRING("Disaster"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_JOY),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_ENJOY)] =
    {
        .text = COMPOUND_STRING("Enjoy"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_LACKING),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_ENJOYS)] =
    {
        .text = COMPOUND_STRING("Enjoys"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_LIKES),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_EAT)] =
    {
        .text = COMPOUND_STRING("Eat"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_LONESOME),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_LACKING)] =
    {
        .text = COMPOUND_STRING("Lacking"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_MEET),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_BAD)] =
    {
        .text = COMPOUND_STRING("Bad"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_MISHEARD),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_HARD)] =
    {
        .text = COMPOUND_STRING("Hard"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_NEGATIVE),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_TERRIBLE)] =
    {
        .text = COMPOUND_STRING("Terrible"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_NEVER),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_SHOULD)] =
    {
        .text = COMPOUND_STRING("Should"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_NICE),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_NICE)] =
    {
        .text = COMPOUND_STRING("Nice"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_PLAY),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_DRINK)] =
    {
        .text = COMPOUND_STRING("Drink"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_QUESTION),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_SURPRISE)] =
    {
        .text = COMPOUND_STRING("Surprise"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_RARE),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_FEAR)] =
    {
        .text = COMPOUND_STRING("Fear"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_ROMANTIC),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_WANT)] =
    {
        .text = COMPOUND_STRING("Want"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_SAD),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_WAIT)] =
    {
        .text = COMPOUND_STRING("Wait"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_SATISFIED),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_SATISFIED)] =
    {
        .text = COMPOUND_STRING("Satisfied"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_SCARY),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_SEE)] =
    {
        .text = COMPOUND_STRING("See"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_SEE),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_RARE)] =
    {
        .text = COMPOUND_STRING("Rare"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_SHOULD),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_NEGATIVE)] =
    {
        .text = COMPOUND_STRING("Negative"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_SURPRISE),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_DONE)] =
    {
        .text = COMPOUND_STRING("Done"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_TERRIBLE),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_DANGER)] =
    {
        .text = COMPOUND_STRING("Danger"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_THINK),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_DEFEATED)] =
    {
        .text = COMPOUND_STRING("Defeated"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_TRIES),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_BEAT)] =
    {
        .text = COMPOUND_STRING("Beat"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_TRY),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_GREAT)] =
    {
        .text = COMPOUND_STRING("Great"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_UNDERSTAND),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_ROMANTIC)] =
    {
        .text = COMPOUND_STRING("Romantic"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_UNDERSTANDS),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_QUESTION)] =
    {
        .text = COMPOUND_STRING("Question"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_WAIT),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_UNDERSTAND)] =
    {
        .text = COMPOUND_STRING("Understand"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_WANT),
        .enabled = TRUE,
    },
    [EC_INDEX(EC_WORD_UNDERSTANDS)] =
    {
        .text = COMPOUND_STRING("Understands"),
        .alphabeticalOrder = EC_INDEX(EC_WORD_WANTS),
        .enabled = TRUE,
    },
};
