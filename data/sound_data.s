	.section .rodata

	.include "asm/macros.inc"
	.include "constants/constants.inc"

	.include "asm/macros/m4a.inc"
	.include "asm/macros/music_voice.inc"
	.include "include/config/general.h"
	.include "include/config/pokemon.h"
#if AUDIO_DISABLED == TRUE
	@ All audio stripped (see docs/prune-audio.md): no voicegroups, keysplits,
	@ wave/PCM samples, cries or songs; every song ID plays a silent song.
	.include "sound/silent_audio.inc"
	.include "sound/music_player_table.inc"
	.include "sound/song_table.inc"
#else
	.include "sound/voice_groups.inc"
	.include "sound/keysplit_tables.inc"
	.include "sound/programmable_wave_data.inc"
	.include "sound/music_player_table.inc"
	.include "sound/song_table.inc"
	.include "sound/direct_sound_data.inc"
#endif

	.align 2
