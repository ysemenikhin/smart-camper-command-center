## Voice announcements package — v4

**File:** `packages/camper_voice.yaml`

Fully local when possible: uses Piper if it is installed, otherwise Home Assistant Cloud TTS.

Without Browser Mod, announcements go to the tablet as a Companion-app TTS notification. With Browser Mod they are spoken immediately through its media player.

**Install:** Copy into `<config>/packages/`. Change the voice in `script.camper_say`.

This tag marks the version at the public release (2026-11-18). Earlier versions were developed in a private repository; their changelog is in the file header and in [CHANGELOG.md](https://github.com/ysemenikhin/smart-camper-command-center/blob/main/CHANGELOG.md).
