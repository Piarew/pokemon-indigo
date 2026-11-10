#ifndef GUARD_MOVE_DISTILLER_H
#define GUARD_MOVE_DISTILLER_H

#include "global.h"
#include "constants/move_distiller.h"
#include "constants/moves.h"

#define DISTILLED_MOVE_BYTES 128

bool32 IsMoveDistillable(enum Move move);
bool32 IsMoveDistilled(enum Move move);
bool32 IsDistillerTutorActive(void);
u32 CountDistilledMoves(void);

void DistillerInspectSelectedMon(void);
void DistillerDonateSelectedMon(void);
void DistillerHasArchivedMoves(void);
void DistillerChooseArchivedMove(void);
void DistillerSetTutorActive(void);
void DistillerClearTutorActive(void);

#endif // GUARD_MOVE_DISTILLER_H
