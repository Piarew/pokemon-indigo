#include "global.h"
#include "sprite.h"
#include "window.h"
#include "malloc.h"
#include "palette.h"
#include "decompress.h"
#include "trainer.h"
#include "trainer_pokemon_sprites.h"
#include "data.h"
#include "pokemon.h"
#include "constants/trainers.h"

#define PICS_COUNT 8

// Needs to be large enough to store either a decompressed Pokémon pic or trainer pic
#define PIC_SPRITE_SIZE max(MON_PIC_SIZE, TRAINER_PIC_SIZE)
#define MAX_PIC_FRAMES  max(MAX_MON_PIC_FRAMES, MAX_TRAINER_PIC_FRAMES)

#define TRAINER_FRONT_TILE_W (TRAINER_PIC_WIDTH / 8)
#define TRAINER_FRONT_SRC_TILE(x, y) ((y) * TRAINER_FRONT_TILE_W + (x))

// 80x80 cannot be one GBA sprite. Pack the 10-pitch gbagfx sheet into 6 OAM
// pieces: 64x64, two 16x32, two 32x16, and a 16x16 corner.
static const struct Subsprite sTrainerFrontPicSubsprites[] =
{
    {.x = -40, .y = -40, .shape = SPRITE_SHAPE(64x64), .size = SPRITE_SIZE(64x64), .tileOffset = 0,  .priority = 2},
    {.x =  24, .y = -40, .shape = SPRITE_SHAPE(16x32), .size = SPRITE_SIZE(16x32), .tileOffset = 64, .priority = 2},
    {.x =  24, .y =  -8, .shape = SPRITE_SHAPE(16x32), .size = SPRITE_SIZE(16x32), .tileOffset = 72, .priority = 2},
    {.x = -40, .y =  24, .shape = SPRITE_SHAPE(32x16), .size = SPRITE_SIZE(32x16), .tileOffset = 80, .priority = 2},
    {.x =  -8, .y =  24, .shape = SPRITE_SHAPE(32x16), .size = SPRITE_SIZE(32x16), .tileOffset = 88, .priority = 2},
    {.x =  24, .y =  24, .shape = SPRITE_SHAPE(16x16), .size = SPRITE_SIZE(16x16), .tileOffset = 96, .priority = 2},
};

static const struct SubspriteTable sTrainerFrontPicSubspriteTable[] =
{
    {ARRAY_COUNT(sTrainerFrontPicSubsprites), sTrainerFrontPicSubsprites}
};

static void CopyTrainerPicTile(const u8 *src, u32 srcTile, u8 *dest, u32 destTile)
{
    CpuCopy32(src + srcTile * TILE_SIZE_4BPP, dest + destTile * TILE_SIZE_4BPP, TILE_SIZE_4BPP);
}

static void CopyTrainerPicTileRect(const u8 *src, u8 *dest, u32 destStart, u32 srcX, u32 srcY, u32 width, u32 height, u32 destPitch)
{
    u32 y, x, destTile;

    destTile = destStart;
    for (y = 0; y < height; y++)
    {
        for (x = 0; x < width; x++)
            CopyTrainerPicTile(src, TRAINER_FRONT_SRC_TILE(srcX + x, srcY + y), dest, destTile++);
        destTile += destPitch - width;
    }
}

static void RepackTrainerFrontPic80(const u8 *src, u8 *dest)
{
    CopyTrainerPicTileRect(src, dest, 0,  0, 0, 8, 8, 8); // 64x64 at (0,0)
    CopyTrainerPicTileRect(src, dest, 64, 8, 0, 2, 4, 2); // 16x32 at (64,0)
    CopyTrainerPicTileRect(src, dest, 72, 8, 4, 2, 4, 2); // 16x32 at (64,32)
    CopyTrainerPicTileRect(src, dest, 80, 0, 8, 4, 2, 4); // 32x16 at (0,64)
    CopyTrainerPicTileRect(src, dest, 88, 4, 8, 4, 2, 4); // 32x16 at (32,64)
    CopyTrainerPicTileRect(src, dest, 96, 8, 8, 2, 2, 2); // 16x16 at (64,64)
}

u32 GetTrainerFrontPicSheetSize(enum TrainerPicID trainerPicId)
{
    u32 size = GetDecompressedDataSize(GetTrainerFrontPicData(trainerPicId));

    if (size >= TRAINER_PIC_SIZE)
        return TRAINER_PIC_SIZE;
    return TRAINER_PIC_LEGACY_SIZE;
}

u32 LoadTrainerFrontPicLinear(enum TrainerPicID trainerPicId, void *dest)
{
    const u32 *data = GetTrainerFrontPicData(trainerPicId);
    u32 size = GetTrainerFrontPicSheetSize(trainerPicId);

    DecompressDataWithHeaderWram(data, dest);
    return size;
}

u32 LoadTrainerFrontPicTiles(enum TrainerPicID trainerPicId, void *dest)
{
    u8 *temp;
    u32 size = GetTrainerFrontPicSheetSize(trainerPicId);

    if (size != TRAINER_PIC_SIZE)
    {
        DecompressDataWithHeaderWram(GetTrainerFrontPicData(trainerPicId), dest);
        return size;
    }

    temp = Alloc(TRAINER_PIC_SIZE);
    if (temp == NULL)
    {
        DecompressDataWithHeaderWram(GetTrainerFrontPicData(trainerPicId), dest);
        return TRAINER_PIC_LEGACY_SIZE;
    }

    DecompressDataWithHeaderWram(GetTrainerFrontPicData(trainerPicId), temp);
    RepackTrainerFrontPic80(temp, dest);
    Free(temp);
    return size;
}

void ApplyTrainerFrontPicSprite(struct Sprite *sprite, enum TrainerPicID trainerPicId)
{
    if (GetTrainerFrontPicSheetSize(trainerPicId) != TRAINER_PIC_SIZE)
    {
        sprite->subspriteTables = NULL;
        sprite->subspriteMode = SUBSPRITES_OFF;
        CalcCenterToCornerVec(sprite, SPRITE_SHAPE(64x64), SPRITE_SIZE(64x64), sprite->oam.affineMode);
        return;
    }

    SetSubspriteTables(sprite, sTrainerFrontPicSubspriteTable);
    sprite->subspriteMode = SUBSPRITES_IGNORE_PRIORITY;
    sprite->centerToCornerVecX = -(TRAINER_PIC_WIDTH / 2);
    sprite->centerToCornerVecY = -(TRAINER_PIC_HEIGHT / 2);
    sprite->oam.affineMode = ST_OAM_AFFINE_OFF;
}

struct PicData
{
    u8 *frames;
    struct SpriteFrameImage *images;
    u16 paletteTag;
    u8 spriteId;
    u8 active;
};

static EWRAM_DATA struct SpriteTemplate sCreatingSpriteTemplate = {};
static EWRAM_DATA struct PicData sSpritePics[PICS_COUNT] = {};

static const struct PicData sDummyPicData = {};

static const struct OamData sOamData_Normal =
{
    .shape = SPRITE_SHAPE(64x64),
    .size = SPRITE_SIZE(64x64)
};

static const struct OamData sOamData_Affine =
{
    .affineMode = ST_OAM_AFFINE_NORMAL,
    .shape = SPRITE_SHAPE(64x64),
    .size = SPRITE_SIZE(64x64)
};

static void DummyPicSpriteCallback(struct Sprite *sprite)
{

}

bool16 ResetAllPicSprites(void)
{
    int i;

    for (i = 0; i < PICS_COUNT; i ++)
        sSpritePics[i] = sDummyPicData;

    return FALSE;
}

static bool16 DecompressPic(u16 picId, u32 personality, bool8 isFrontPic, u8 *dest, bool8 isTrainer)
{
    if (!isTrainer)
    {
        enum Species species = picId;
        LoadSpecialPokePic(dest, species, personality, isFrontPic);
    }
    else
    {
        enum TrainerPicID trainerPicId = picId;
        if (isFrontPic)
            DecompressDataWithHeaderWram(GetTrainerFrontPicData(trainerPicId), dest);
        else
            CopyTrainerBackspriteFramesToDest(trainerPicId, dest);
    }
    return FALSE;
}

static void LoadPicPaletteByTagOrSlot(u16 species, bool8 isShiny, u32 personality, u8 paletteSlot, u16 paletteTag, bool8 isTrainer)
{
    if (!isTrainer)
    {
        if (paletteTag == TAG_NONE)
        {
            sCreatingSpriteTemplate.paletteTag = TAG_NONE;
            LoadPalette(GetMonSpritePalFromSpeciesAndPersonality(species, isShiny, personality), OBJ_PLTT_ID(paletteSlot), PLTT_SIZE_4BPP);
        }
        else
        {
            sCreatingSpriteTemplate.paletteTag = paletteTag;
            LoadSpritePaletteWithTag(GetMonSpritePalFromSpeciesAndPersonality(species, isShiny, personality), species);
        }
    }
    else
    {
        if (paletteTag == TAG_NONE)
        {
            sCreatingSpriteTemplate.paletteTag = TAG_NONE;
            LoadPalette(GetTrainerFrontPicPalette(species), OBJ_PLTT_ID(paletteSlot), PLTT_SIZE_4BPP);
        }
        else
        {
            sCreatingSpriteTemplate.paletteTag = paletteTag;
            LoadSpritePaletteWithTag(GetTrainerFrontPicPalette(species), GetTrainerPicTag(species, TRUE));
        }
    }
}

static void LoadPicPaletteBySlot(u16 species, bool8 isShiny, u32 personality, u8 paletteSlot, bool8 isTrainer)
{
    if (!isTrainer)
        LoadPalette(GetMonSpritePalFromSpeciesAndPersonality(species, isShiny, personality), PLTT_ID(paletteSlot), PLTT_SIZE_4BPP);
    else
        LoadPalette(GetTrainerFrontPicPalette(species), PLTT_ID(paletteSlot), PLTT_SIZE_4BPP);
}

static void AssignSpriteAnimsTable(bool8 isTrainer)
{
    if (!isTrainer)
        sCreatingSpriteTemplate.anims = gAnims_MonPic;
    else
        sCreatingSpriteTemplate.anims = gAnims_Trainer;
}

static u16 CreatePicSprite(u16 species, bool8 isShiny, u32 personality, bool8 isFrontPic, s16 x, s16 y, u8 paletteSlot, u16 paletteTag, bool8 isTrainer)
{
    u8 i;
    u8 *framePics;
    struct SpriteFrameImage *images;
    int j;
    u8 spriteId;
    u32 picSize;

    for (i = 0; i < PICS_COUNT; i ++)
    {
        if (!sSpritePics[i].active)
            break;
    }
    if (i == PICS_COUNT)
        return 0xFFFF;

    framePics = Alloc(PIC_SPRITE_SIZE * MAX_PIC_FRAMES);
    if (!framePics)
        return 0xFFFF;

    images = Alloc(sizeof(struct SpriteFrameImage) * MAX_PIC_FRAMES);
    if (!images)
    {
        Free(framePics);
        return 0xFFFF;
    }
    if (isTrainer && isFrontPic)
    {
        picSize = LoadTrainerFrontPicTiles(species, framePics);
    }
    else if (DecompressPic(species, personality, isFrontPic, framePics, isTrainer))
    {
        // debug trap?
        return 0xFFFF;
    }
    else
    {
        picSize = isTrainer ? TRAINER_BACK_PIC_SIZE : MON_PIC_SIZE;
    }
    for (j = 0; j < MAX_PIC_FRAMES; j ++)
    {
        images[j].data = framePics + PIC_SPRITE_SIZE * j;
        images[j].size = picSize;
    }
    sCreatingSpriteTemplate.tileTag = TAG_NONE;
    sCreatingSpriteTemplate.oam = &sOamData_Normal;
    AssignSpriteAnimsTable(isTrainer);
    sCreatingSpriteTemplate.images = images;
    sCreatingSpriteTemplate.affineAnims = gDummySpriteAffineAnimTable;
    sCreatingSpriteTemplate.callback = DummyPicSpriteCallback;
    LoadPicPaletteByTagOrSlot(species, isShiny, personality, paletteSlot, paletteTag, isTrainer);
    spriteId = CreateSprite(&sCreatingSpriteTemplate, x, y, 0);
    if (paletteTag == TAG_NONE)
        gSprites[spriteId].oam.paletteNum = paletteSlot;
    if (isTrainer && isFrontPic)
        ApplyTrainerFrontPicSprite(&gSprites[spriteId], species);
    sSpritePics[i].frames = framePics;
    sSpritePics[i].images = images;
    sSpritePics[i].paletteTag = paletteTag;
    sSpritePics[i].spriteId = spriteId;
    sSpritePics[i].active = TRUE;
    return spriteId;
}

u16 CreateMonPicSprite_Affine(enum Species species, bool8 isShiny, u32 personality, u8 flags, s16 x, s16 y, u8 paletteSlot, u16 paletteTag)
{
    u8 *framePics;
    struct SpriteFrameImage *images;
    int j;
    u8 i;
    u8 spriteId;
    u8 type;
    species = SanitizeSpeciesId(species);

    for (i = 0; i < PICS_COUNT; i++)
    {
        if (!sSpritePics[i].active)
            break;
    }
    if (i == PICS_COUNT)
        return 0xFFFF;

    framePics = Alloc(MON_PIC_SIZE * MAX_MON_PIC_FRAMES);
    if (!framePics)
        return 0xFFFF;

    if (flags & F_MON_PIC_NO_AFFINE)
    {
        flags &= ~F_MON_PIC_NO_AFFINE;
        type = MON_PIC_AFFINE_NONE;
    }
    else
    {
        type = flags;
    }
    images = Alloc(sizeof(struct SpriteFrameImage) * MAX_MON_PIC_FRAMES);
    if (!images)
    {
        Free(framePics);
        return 0xFFFF;
    }
    if (DecompressPic(species, personality, flags, framePics, FALSE))
    {
        // debug trap?
        return 0xFFFF;
    }
    for (j = 0; j < MAX_MON_PIC_FRAMES; j ++)
    {
        images[j].data = framePics + MON_PIC_SIZE * j;
        images[j].size = MON_PIC_SIZE;
    }
    sCreatingSpriteTemplate.tileTag = TAG_NONE;
    sCreatingSpriteTemplate.anims = gSpeciesInfo[species].frontAnimFrames;
    sCreatingSpriteTemplate.images = images;
    if (type == MON_PIC_AFFINE_FRONT)
    {
        sCreatingSpriteTemplate.affineAnims = gAffineAnims_BattleSpriteOpponentSide;
        sCreatingSpriteTemplate.oam = &sOamData_Affine;
    }
    else if (type == MON_PIC_AFFINE_BACK)
    {
        sCreatingSpriteTemplate.affineAnims = gAffineAnims_BattleSpritePlayerSide;
        sCreatingSpriteTemplate.oam = &sOamData_Affine;
    }
    else // MON_PIC_AFFINE_NONE
    {
        sCreatingSpriteTemplate.oam = &sOamData_Normal;
        sCreatingSpriteTemplate.affineAnims = gDummySpriteAffineAnimTable;
    }
    sCreatingSpriteTemplate.callback = DummyPicSpriteCallback;
    LoadPicPaletteByTagOrSlot(species, isShiny, personality, paletteSlot, paletteTag, FALSE);
    spriteId = CreateSprite(&sCreatingSpriteTemplate, x, y, 0);
    if (paletteTag == TAG_NONE)
        gSprites[spriteId].oam.paletteNum = paletteSlot;
    sSpritePics[i].frames = framePics;
    sSpritePics[i].images = images;
    sSpritePics[i].paletteTag = paletteTag;
    sSpritePics[i].spriteId = spriteId;
    sSpritePics[i].active = TRUE;
    return spriteId;
}

static u16 FreeAndDestroyPicSpriteInternal(u16 spriteId, bool8 clearPalette)
{
    u8 i;
    u8 *framePics;
    struct SpriteFrameImage *images;

    for (i = 0; i < PICS_COUNT; i ++)
    {
        if (sSpritePics[i].spriteId == spriteId)
            break;
    }
    if (i == PICS_COUNT)
        return 0xFFFF;

    framePics = sSpritePics[i].frames;
    images = sSpritePics[i].images;
    if (clearPalette && sSpritePics[i].paletteTag != TAG_NONE)
        FreeSpritePaletteByTag(GetSpritePaletteTagByPaletteNum(gSprites[spriteId].oam.paletteNum));
    DestroySprite(&gSprites[spriteId]);
    Free(framePics);
    Free(images);
    sSpritePics[i] = sDummyPicData;
    return 0;
}

static u16 LoadPicSpriteInWindow(u16 species, bool8 isShiny, u32 personality, bool8 isFrontPic, u8 paletteSlot, u8 windowId, bool8 isTrainer)
{
    if (DecompressPic(species, personality, isFrontPic, (u8 *)GetWindowAttribute(windowId, WINDOW_TILE_DATA), FALSE))
        return 0xFFFF;

    LoadPicPaletteBySlot(species, isShiny, personality, paletteSlot, isTrainer);
    return 0;
}

static u16 CreateTrainerCardSprite(u16 species, bool8 isShiny, u32 personality, bool8 isFrontPic, u16 destX, u16 destY, u8 paletteSlot, u8 windowId, bool8 isTrainer)
{
    u8 *framePics;
    u32 size;
    u16 width, height;

    framePics = Alloc(TRAINER_PIC_SIZE * MAX_TRAINER_PIC_FRAMES);
    if (!framePics)
        return 0xFFFF;

    if (isTrainer && isFrontPic)
        size = LoadTrainerFrontPicLinear(species, framePics);
    else if (DecompressPic(species, personality, isFrontPic, framePics, isTrainer))
    {
        Free(framePics);
        return 0xFFFF;
    }
    else
    {
        size = isTrainer ? TRAINER_BACK_PIC_SIZE : MON_PIC_SIZE;
    }

    if (size >= TRAINER_PIC_SIZE)
    {
        width = TRAINER_PIC_WIDTH;
        height = TRAINER_PIC_HEIGHT;
    }
    else
    {
        width = TRAINER_PIC_LEGACY_WIDTH;
        height = TRAINER_PIC_LEGACY_HEIGHT;
    }

    BlitBitmapRectToWindow(windowId, framePics, 0, 0, width, height, destX, destY, width, height);
    LoadPicPaletteBySlot(species, isShiny, personality, paletteSlot, isTrainer);
    Free(framePics);
    return 0;
}

u16 CreateMonPicSprite(enum Species species, bool8 isShiny, u32 personality, bool8 isFrontPic, s16 x, s16 y, u8 paletteSlot, u16 paletteTag)
{
    return CreatePicSprite(species, isShiny, personality, isFrontPic, x, y, paletteSlot, paletteTag, FALSE);
}

u16 FreeAndDestroyMonPicSprite(u16 spriteId)
{
    return FreeAndDestroyPicSpriteInternal(spriteId, TRUE);
}

u16 FreeAndDestroyMonPicSpriteNoPalette(u16 spriteId)
{
    return FreeAndDestroyPicSpriteInternal(spriteId, FALSE);
}

static u16 UNUSED LoadMonPicInWindow(enum Species species, bool8 isShiny, u32 personality, bool8 isFrontPic, u8 paletteSlot, u8 windowId)
{
    return LoadPicSpriteInWindow(species, isShiny, personality, isFrontPic, paletteSlot, windowId, FALSE);
}

// Unused, FRLG only
u16 CreateTrainerCardMonIconSprite(enum Species species, bool8 isShiny, u32 personality, bool8 isFrontPic, u16 destX, u16 destY, u8 paletteSlot, u8 windowId)
{
    return CreateTrainerCardSprite(species, isShiny, personality, isFrontPic, destX, destY, paletteSlot, windowId, FALSE);
}

u16 CreateTrainerPicSprite(u16 species, bool8 isFrontPic, s16 x, s16 y, u8 paletteSlot, u16 paletteTag)
{
    return CreatePicSprite(species, FALSE, 0, isFrontPic, x, y, paletteSlot, paletteTag, TRUE);
}

u16 FreeAndDestroyTrainerPicSprite(u16 spriteId)
{
    return FreeAndDestroyPicSpriteInternal(spriteId, TRUE);
}

static u16 UNUSED LoadTrainerPicInWindow(u16 species, bool8 isFrontPic, u8 paletteSlot, u8 windowId)
{
    return LoadPicSpriteInWindow(species, FALSE, 0, isFrontPic, paletteSlot, windowId, TRUE);
}

u16 CreateTrainerCardTrainerPicSprite(u16 species, bool8 isFrontPic, u16 destX, u16 destY, u8 paletteSlot, u8 windowId)
{
    return CreateTrainerCardSprite(species, FALSE, 0, isFrontPic, destX, destY, paletteSlot, windowId, TRUE);
}

u16 PlayerGenderToFrontTrainerPicId_Debug(enum Gender gender, bool8 getClass)
{
    if (getClass == TRUE)
    {
        if (gender != MALE)
            return gFacilityClassToPicIndex[FACILITY_CLASS_MAY];
        else
            return gFacilityClassToPicIndex[FACILITY_CLASS_BRENDAN];
    }
    return gender;
}

void CopyTrainerBackspriteFramesToDest(enum TrainerPicID trainerPicId, u8 *dest)
{
    const struct SpriteFrameImage *frame = GetTrainerBackPicImage(trainerPicId);
    // y_offset is repurposed to indicates how many frames does the trainer pic have.
    u32 size = (frame->size * GetTrainerBackPicCoords(trainerPicId)->y_offset);
    CpuSmartCopy16(frame->data, dest, size);
}
