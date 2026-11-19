# Changelog

One entry per released version, newest first. The full reasoning for each version is in the changelog header of the file itself.

Versions up to the public release (dashboard v206, relay board v2.3.8 and older) were developed in a private repository. Their entries are kept below for reference, but their commits and tags are not part of this repository. From the public release on, each version is tagged here; see [docs/14-versioning.md](docs/14-versioning.md).

## Public release — 2026-11-18

| Date | Tag | Change |
|---|---|---|
| 2026-11-18 | `dashboard-v207` | Header title line said v145; it now shows the current version. Comment-only, the dashboard is identical to v206. |
| 2026-11-18 | `relay-board-v2.3.9` | DS18B20 address tags removed from the comments (addresses stay in `secrets.yaml`). Comments and Config Version only; firmware behaves as v2.3.8. |

Repository: files moved to the public layout (`esphome/`, `packages/`, `dashboard/`, `themes/`, `router-scripts/`, `docs/`, `hardware/`, `images/`); real dashboard screenshots with private details blurred; wiring diagram (front 12 V, v10); integrations doc corrected to the running system; troubleshooting doc; contributor files, issue and PR templates; CI validates ESPHome configs on every pull request.

## Before the public release

| Date | Tag | Change |
|---|---|---|
| 2026-10-28 | `package-v58` | 15 s SMOOTHING REMOVED from the Energy/Home tile and Load |
| 2026-10-28 | `dashboard-v206` | Energy tab bank cards: a Power row under Current on each bank - |
| 2026-10-28 | `cellwatch-v1` | 2026-10-28. WHY: with network mode AUTO the modem dropped to 3G |
| 2026-10-21 | `gps-v1` | 2026-10-21. Replaces the UI automation "GLnet router GPS update" |
| 2026-10-20 | `light-effects-v2` | 2026-10-20. POLICE is now WHITE / RED instead of LEFT / RIGHT: |
| 2026-10-20 | `dashboard-v205` | Lighting tab, Scenes: two new tiles, no other change |
| 2026-10-20 | `light-effects-v1` | 2026-10-20. Two outdoor light effects, HA-only (no relay-board |
| 2026-10-20 | `relay-board-v2.3.8` | STATUS ENTITIES (all diagnostic except the Restart button): |
| 2026-10-20 | `relay-board-v2.3.7` | RF433 SLOTS 4 -> 6. Added RF Slot 5/6 Code, Learn Slot 5/6 and |
| 2026-10-20 | `relay-board-v2.3.6` | RF433 PRESS HANDLING - rf_check_slots and the on_rc_switch gate |
| 2026-10-08 | `relay-board-v2.3.5` | DS18B20 OFFSETS RECALCULATED. v2.3.4 used ONE reading and |
| 2026-10-07 | `relay-board-v2.3.4` | DS18B20 OFFSETS - all four aligned to the LOWEST sensor (Grey), |
| 2026-10-07 | `dashboard-v204` | FIX for v203: setting padding to 0 also SHRANK the camera light |
| 2026-10-07 | `dashboard-v203` | Cameras light buttons: icon+text sat on the bottom edge. Same root |
| 2026-10-07 | `dashboard-v202` | Cameras tab light buttons: icon and text now the SAME SIZE as the |
| 2026-10-07 | `dashboard-v201` | Water Pump / Tank & Pipe Heat: ROOT CAUSE of v197-v200 |
| 2026-10-07 | `dashboard-v200` | FIX for v199: size: 38px on the card did NOT stop the icon |
| 2026-10-07 | `dashboard-v199` | Water tab row 3: Water Pump and Tank & Pipe Heat stretched to HALF |
| 2026-10-07 | `dashboard-v198` | Water tab row 3 (Water Pump, Tank & Pipe Heat) now uses the SAME |
| 2026-10-07 | `dashboard-v197` | Water tab rebuilt around the DS18B20s (relay-board v2.3.3): |
| 2026-10-07 | `relay-board-v2.3.3` | Renamed "Pipe 1 Temp" -> "Water Pipe 1 Temp" and |
| 2026-10-07 | `relay-board-v2.3.2` | DS18B20s get their final names (assigned in address order; the owner |
| 2026-10-07 | `relay-board-v2.3.1` | IDENTIFICATION BUILD for the 4 DS18B20s. Each publishes under a |
| 2026-09-29 | `dashboard-v196` | Two fixes, both traced on the live system: |
| 2026-09-29 | `package-v57` | ticks every SECOND, not every 5. At /5 the display jumped 4:10 -> |
| 2026-09-25 | `relay-board-v2.0.2` | Added the two fitted expansion modules: |
| 2026-09-18 | `air-suspension-v5.0.8` | LONG-TERM STATISTICS: state_class: measurement added to the |
| 2026-08-27 | `voice-v4` | FULLY LOCAL when possible. The TTS engine is auto-selected: if a |
| 2026-07-11 | `theme-v4.0` | Consolidated modern element fixes for white boxes, selection lists, and code editor |
