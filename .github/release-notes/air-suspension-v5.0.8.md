## Air suspension firmware (ESP32-S3) — v5.0.8-S3

**File:** `esphome/air-suspension-s3.yaml`

Long-term statistics: `state_class: measurement` on the 4 height sensors and the 9 roll/pitch sensors, so Home Assistant keeps their history past the 10-day recorder purge. No control logic changed.

Flash the relay board first, then this board. Calibrate the corner heights and the IMU before trusting levelling.

**Install:** Fill in `api_encryption_key`, Wi-Fi and `manifold_mac` in `secrets.yaml`.

This tag marks the version at the public release (2026-11-18). Earlier versions were developed in a private repository; their changelog is in the file header and in [CHANGELOG.md](https://github.com/ysemenikhin/smart-camper-command-center/blob/main/CHANGELOG.md).
