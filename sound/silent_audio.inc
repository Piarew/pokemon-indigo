@ Silent audio data, used instead of the real voicegroups/samples/songs when
@ AUDIO_DISABLED is TRUE in include/config/general.h. See docs/prune-audio.md.
@
@ Every entry of gSongTable (song_table.inc is unchanged, so every MUS_*/SE_*
@ ID keeps its slot and music player) points at mus_dummy below: a 0-track
@ song header, identical in shape to vanilla mus_dummy (which the game already
@ plays to silence the BGM player). Starting it leaves the music player with
@ no active tracks, so IsBGMStopped()/IsSEPlaying()/etc. report "not playing"
@ right away and nothing waiting on them can stall.

	.align 2
@ 128 silent square voices; never actually read (no track ever plays a note),
@ but kept valid because m4a stores it as the player's tone pointer and the
@ Pokémon cry song template references it.
voicegroup_dummy::
	.rept 128
	voice_square_1 60, 0, 0, 2, 0, 0, 15, 0
	.endr

@ Cry tables are empty (P_CRIES_ENABLED is FALSE); labels kept for src/sound.c.
	.align 2
gCryTable::
gCryTable_Reverse::

	.align 2
mus_dummy::
	.byte 0     @ NumTrks
	.byte 0     @ NumBlks
	.byte 0     @ Priority
	.byte 0     @ Reverb (no SOUND_MODE_REVERB_SET bit: sound mode untouched)
	.4byte voicegroup_dummy

@ Point every song table entry at the silent song, keeping its music player.
	.purgem song
	.macro song label:req, music_player:req, unknown:req
	.4byte mus_dummy
	.2byte \music_player
	.2byte \unknown
	.endm
