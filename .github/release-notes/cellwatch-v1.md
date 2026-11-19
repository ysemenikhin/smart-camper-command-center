## 3G watchdog (router) — v1

**File:** `router-scripts/usr/bin/camper-cellwatch.sh + router-scripts/etc/init.d/camper-cellwatch`

With network mode AUTO the modem dropped to 3G (WCDMA) while parked and stayed there. The watchdog pulls it back to LTE when it is stuck on 3G, and keeps the 3G fallback where only 3G exists.

Runs on the GL.iNet router with BusyBox sh and gl_modem; nothing extra to install.

**Install:** Copy both files to the router and enable the service, as described in docs/13-router-scripts.md.

This tag marks the version at the public release (2026-11-18). Earlier versions were developed in a private repository; their changelog is in the file header and in [CHANGELOG.md](https://github.com/ysemenikhin/smart-camper-command-center/blob/main/CHANGELOG.md).
