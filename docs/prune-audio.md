# Pruned audio (`prune` branch)

On the `prune` branch, all game audio is removed from the ROM. That covers music, fanfares and jingles, sound effects and Pokémon cries. The m4a sound engine stays, and every `MUS_*`, `SE_*` and cry constant is still defined. Scripts and C code that call `PlayBGM`, `PlaySE`, `PlayFanfare`, `PlayCry_*` and similar functions still compile and run. Those calls just produce no sound.

All the sound source files (`sound/songs/`, `sound/direct_sound_samples/`, `sound/cries/`, voicegroups and so on) are still in the repository. Only the linked output changes.

## Size impact (`make firered`)

| Build | `__rom_end` | Used | Free of 32 MiB |
|---|---|---|---|
| master (audio) | 0x09A1033C | 27,329,340 B (26,688.8 KiB) | 6,225,092 B (5.94 MiB) |
| prune (no audio) | 0x08F87CB8 | 16,284,856 B (15,903.2 KiB) | 17,269,576 B (16.47 MiB) |

The pruned build saves 11,044,484 B (about 10,785.6 KiB, or 10.53 MiB). The `.gba` file is now padded only to 16 MiB because the ROM fits in that size.

## How it works

1. **Config switches**
   - `include/config/general.h`: `AUDIO_DISABLED TRUE`. This is the master switch.
   - `include/config/pokemon.h`: `P_CRIES_ENABLED FALSE`. `GetCryIdBySpecies` returns `CRY_NONE`, no cry is ever started, and `gMPlay_PokemonCry` stays `NULL`.
2. **Makefile**: when `AUDIO_DISABLED` is `TRUE` in `general.h`, `MID_SRCS` is emptied. As a result, none of the `sound/songs/midi/*.mid` songs are converted or linked.
3. **`data/sound_data.s`**: when `AUDIO_DISABLED == TRUE`, the file no longer includes voice groups, keysplit tables, programmable wave data or `direct_sound_data.inc` (all PCM samples). It includes `sound/silent_audio.inc` instead, followed by the normal `music_player_table.inc` and `song_table.inc`.
4. **`sound/silent_audio.inc`** provides:
   - `voicegroup_dummy`: 128 square-wave voices, with no sample data.
   - Empty `gCryTable` / `gCryTable_Reverse` labels.
   - `mus_dummy`: a song header with 0 tracks.
   - A redefined `song` macro. Every `gSongTable` entry points at `mus_dummy` but keeps its original music player, so all 610 song IDs stay valid. A 0-track song leaves the player's track status bits clear, so the engine immediately reports "not playing".
5. **`src/sound.c`**
   - Fanfare durations are forced to 0, so `IsFanfareTaskInactive` / `WaitFanfare` return immediately.
   - `NULL` guards for `gMPlay_PokemonCry` in `StopCry`, `StopCryAndClearCrySongs`, `IsCryPlaying`, `IsCryPlayingOrClearCrySongs` and `Task_DuckBGMForPokemonCry`.
   - `IsCryFinished` returns `TRUE` right away when no cry player exists. It also cleans up any BGM-duck task and restores the BGM volume.
6. **`src/title_screen.c`** (Emerald title): the screen used to wait for the title BGM to end before restarting. It now uses a 2700-frame timer when audio is disabled. The FRLG title screen already uses a timer.

### Softlock review

Every script or C wait on audio checks for "not playing": `waitse`, `waitfanfare`, `waitmoncry`, `IsSEPlaying`, `IsBGMStopped`, `IsCryFinished`, `IsCryPlaying`, `IsNotWaitingForBGMStop` and `IsFanfareTaskInactive`. With silent songs and no cry player, each of these is satisfied on the first check.

## Restoring audio

Choose one of these:

- Set `AUDIO_DISABLED FALSE` in `include/config/general.h` and `P_CRIES_ENABLED TRUE` in `include/config/pokemon.h`, then run `make clean-assets` (or `make clean`) and `make firered`. This was verified to build at 27,329,404 B, which is master plus the 64 B of guards. The guards in `sound.c` stay in place and do no harm.
- Or revert the audio-pruning commits on `prune`. They are listed in `git log master..prune`.
