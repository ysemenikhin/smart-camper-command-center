## Router GPS — v1

**File:** `packages/camper_gps.yaml + router-scripts/…/camper-gps*`

The router's modem GPS posts to a Home Assistant webhook every 10 s while moving; the package turns it into `device_tracker.camper_gps` and sensors, and moves the home location for the weather only when it is more than 2 km away.

If you had a UI automation on the `glnet_router_gps` webhook, delete it first, or both will handle every report.

**Install:** Install the router script and init file as described in docs/13-router-scripts.md.

This tag marks the version at the public release (2026-11-18). Earlier versions were developed in a private repository; their changelog is in the file header and in [CHANGELOG.md](https://github.com/ysemenikhin/smart-camper-command-center/blob/main/CHANGELOG.md).
