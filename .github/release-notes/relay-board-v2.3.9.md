## Relay board firmware (KinCony KC868-A16S) — v2.3.9

**File:** `esphome/relay-board.yaml`

DS18B20 address tags removed from the comments; the addresses stay in `secrets.yaml`. Comments and Config Version only, the firmware behaves exactly as v2.3.8.

v2.3.8 added the diagnostic status entities: Config Version, ESPHome Version, IP Address, Uptime, Status and a Restart button.

**Install:** Copy `esphome/secrets.yaml.example` to `secrets.yaml`, fill it in, and flash from the ESPHome Device Builder.

This tag marks the version at the public release (2026-11-18). Earlier versions were developed in a private repository; their changelog is in the file header and in [CHANGELOG.md](https://github.com/ysemenikhin/smart-camper-command-center/blob/main/CHANGELOG.md).
