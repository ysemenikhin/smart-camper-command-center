## Home Assistant package — v58

**File:** `packages/camper.yaml`

15 s smoothing removed from the Energy/Home tile and Load. The BMS updates every 30 s, so the average only added delay; the tile now reads the battery current and power directly.

After upgrading, delete the two leftover entities Camper Battery Current Smoothed and Camper Battery Power Smoothed.

**Install:** Copy into `<config>/packages/` and restart Home Assistant.

This tag marks the version at the public release (2026-11-18). Earlier versions were developed in a private repository; their changelog is in the file header and in [CHANGELOG.md](https://github.com/ysemenikhin/smart-camper-command-center/blob/main/CHANGELOG.md).
