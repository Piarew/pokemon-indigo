#ifndef GUARD_INDIGO_H
#define GUARD_INDIGO_H

#include "constants/field_move.h"

extern const u8 gText_CantUseUntilIndigoAuth[];

u32 CountIndigoGyms(void);
u32 CountIndigoFieldMoves(void);
bool32 HasIndigoType(u32 type);
bool32 HasIndigoFieldMove(enum FieldMove fieldMove);
void SyncIndigoCount(void);
void GiveIndigoRecognition(void);
void GiveIndigoRecognitionForType(u32 type);
u16 TryGiveIndigoFieldMoves(void);
void CB2_ShowIndigoRoster(void);

#endif // GUARD_INDIGO_H
