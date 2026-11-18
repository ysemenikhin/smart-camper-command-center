# Smart Camper Command Center

[![ci](https://github.com/ysemenikhin/smart-camper-command-center/actions/workflows/ci.yml/badge.svg)](https://github.com/ysemenikhin/smart-camper-command-center/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Home Assistant + ESPHome control system for an off-road expedition trailer:

- **Four-corner air suspension** with IMU auto-levelling, five drive modes and
  off-road articulation.
- **16 relay circuits** with physical buttons, an RF433 remote and an RTC
  schedule.
- **Tank metering** in litres, and **freeze monitoring** with four DS18B20
  sensors.
- **Dual LiFePO₄ banks** with shunt fallback, and **1320 W solar** on two MPPTs.
- **Diesel heater** with a virtual fuel tank.
- **Cameras**, plus **cellular / Wi-Fi / Starlink** status, a router **GPS
  tracker** and a 3G watchdog.

It all runs on a dark dashboard built for a 10" wall tablet.

This is the configuration running on a real trailer, published with credentials
and identifying details removed. Every calibration number in the docs says
whether it was **measured**, **derived** or **assumed**.

![Home tab](images/tab-home.png)

## Dashboard tabs

| | | |
|---|---|---|
| [![Home](images/tab-home.png)](docs/09-dashboard.md#1-home--the-one-glance-status-board) **Home**: at-a-glance status | [![Energy](images/tab-energy.png)](docs/09-dashboard.md#2-energy--battery-and-solar-in-detail) **Energy**: banks, MPPTs, 24 h charts | [![Lighting](images/tab-lighting.png)](docs/09-dashboard.md#3-lighting--every-relay-grouped-by-where-it-is) **Lighting**: relays, scenes, effects |
| [![Water](images/tab-water.png)](docs/09-dashboard.md#4-water--tanks-pump-and-freeze-protection) **Water**: tanks, litres, pipe temperatures | [![Climate](images/tab-climate.png)](docs/09-dashboard.md#5-climate--diesel-heater-and-its-virtual-fuel-tank) **Climate**: heater, virtual fuel tank | [![Suspension](images/tab-suspension.png)](docs/09-dashboard.md#6-suspension--air-ride-levelling-and-settings) **Suspension**: corners, roll/pitch, modes |
| [![Cameras](images/tab-cameras.png)](docs/09-dashboard.md#7-cameras--four-sides-and-the-interior) **Cameras**: four sides and the interior | [![Connectivity](images/tab-connectivity.png)](docs/09-dashboard.md#8-connectivity--which-link-is-carrying-traffic) **Connectivity**: WAN, signal, Starlink | [![Suspension settings](images/tab-suspension-settings.png)](docs/09-dashboard.md#6-suspension--air-ride-levelling-and-settings) **Suspension settings**: behind a lock |

Screenshots are from the running trailer. The Wi-Fi QR code, the WAN IP, the
Wi-Fi network name and the camera images are blurred.

## System overview

```mermaid
graph TB
    subgraph Pi["Raspberry Pi 4 — Home Assistant OS"]
        HA["Home Assistant<br/>packages · dashboard · automations"]
    end
    subgraph ESP["ESPHome boards"]
        SUS["Air suspension<br/>ESP32-S3 · BMI160 IMU · BLE"]
        REL["Relay board<br/>KinCony KC868-A16S · 16 relays<br/>tank ADCs · DS18B20 · RF433 · RTC"]
    end
    MAN["DN-3G air manifold<br/>4 corner bags"]
    BMS["2× LiFePO₄ BMS (BLE)"]
    MPPT["2× MPPT + 920 Ah shunt"]
    RTR["GL.iNet X3000<br/>cellular · repeater · GPS"]
    HTR["Diesel heater (BLE)"]
    CAM["4 exterior + 1 interior camera"]
    TAB["10 in wall tablet"]

    HA <-->|native API| SUS
    HA <-->|native API| REL
    SUS <-->|BLE| MAN
    HA <-->|BLE| BMS
    HA <--> MPPT
    HA <--> HTR
    RTR -->|webhook: GPS| HA
    RTR <-->|integration| HA
    CAM --> HA
    HA --> TAB
```

**The rule:** anything that must still work with the Pi unplugged lives in
firmware: relay buttons, the stabiliser 10-minute cut-off, suspension
closed-loop control, the gauges schedule. Everything else lives in Home
Assistant.

## Documentation

| Doc | Contents |
|---|---|
| [01 — Architecture](docs/01-architecture.md) | How the parts fit, where each decision is made, failure behaviour |
| [02 — Hardware & BOM](hardware/bom.md) | Every component and why it was chosen |
| [Wiring](hardware/wiring.md) | Front 12 V system cable by cable: fuses, relays, buttons, gauges (PDF + sheets) |
| [03 — Integrations](docs/03-integrations.md) | HA integrations, HACS integrations and cards, add-ons, as running |
| [04 — Air suspension](docs/04-air-suspension.md) | Levelling algorithm, modes, PSI fallback, the sign-error story |
| [05 — Relay board](docs/05-relay-board.md) | Full relay map, timers, interlocks, board quirks |
| [06 — Water tanks](docs/06-water-tanks.md) | Senders, ADC filtering, two calibration scales |
| [07 — Energy](docs/07-energy.md) | BMS, MPPTs, shunt fallback |
| [08 — Connectivity & cameras](docs/08-connectivity-cameras.md) | WAN modes, signal maths, dual-stream cameras |
| [09 — Dashboard](docs/09-dashboard.md) | **Every tab: what it does and why** |
| [10 — Calibration](docs/10-calibration.md) | Tanks, corner heights, IMU, with real data |
| [11 — Safety](docs/11-safety.md) | **Read before building** |
| [12 — Installation](docs/12-installation.md) | From a clone to a working system |
| [13 — Router scripts](docs/13-router-scripts.md) | GPS sender and 3G watchdog on the router |
| [14 — Versioning](docs/14-versioning.md) | Component versions, tags, branching, CI |
| [15 — Troubleshooting](docs/15-troubleshooting.md) | Problems that actually happened, and their fixes |
| [DN-3G manifold notes](hardware/dn3g-manifold-notes.md) | BLE protocol and valve-side settings |

## Repository layout

```
esphome/
  air-suspension-s3.yaml        ESP32-S3: IMU, BLE to the manifold, levelling
  relay-board.yaml              KC868-A16S: 16 relays, tanks, DS18B20, RF433, RTC
  secrets.yaml.example          copy to secrets.yaml and fill in
packages/
  camper.yaml                   templates, alerts, scripts, automations, helpers
  camper_light_effects.yaml     Police / Front Flash effects
  camper_gps.yaml               router GPS webhook → device tracker + sensors
  camper_voice.yaml             spoken suspension announcements
dashboard/
  smart-camper-dashboard.yaml   the dashboard (raw YAML)
themes/
  garmin_dark.yaml              theme the dashboard is designed against
router-scripts/                 GL.iNet scripts: GPS sender, 3G watchdog
docs/                           documentation
hardware/                       BOM, wiring diagram (PDF + sheets), manifold notes
images/                         dashboard screenshots
tools/render-screenshots/       renders demo screenshots from the code
```

## Versions

Each component is versioned independently. See [CHANGELOG.md](CHANGELOG.md) and
[docs/14-versioning.md](docs/14-versioning.md).

| Component | Current |
|---|---|
| Dashboard | v207 |
| HA package | v58 |
| Relay board firmware | v2.3.9 |
| Air suspension firmware | v5.0.8-S3 |
| Light effects / GPS / 3G watchdog / voice | v2 / v1 / v1 / v4 |
| Theme | v4.0 |

Tested on Home Assistant 2026.10.2 and ESPHome 2026.10.2.

## Quick start

The relay map, tank sizes and corner constants describe one trailer, so this
cannot be used unchanged. Read [11 — Safety](docs/11-safety.md) and
[12 — Installation](docs/12-installation.md). In short:

1. `cp esphome/secrets.yaml.example esphome/secrets.yaml` and fill it in.
2. Flash `relay-board.yaml` first, then `air-suspension-s3.yaml`.
3. Copy `packages/*` into `config/packages/` and `themes/garmin_dark.yaml` into
   `config/themes/`.
4. Install `button-card`, `card-mod` and `apexcharts-card` from HACS.
5. Paste `dashboard/smart-camper-dashboard.yaml` into a new dashboard's raw
   editor.
6. **Calibrate before trusting any reading:** [10 — Calibration](docs/10-calibration.md).

Something not working? [15 — Troubleshooting](docs/15-troubleshooting.md).

## Contributing

Fixes, doc improvements and notes from your own build are welcome. See
[CONTRIBUTING.md](CONTRIBUTING.md) and the [Code of Conduct](CODE_OF_CONDUCT.md).
Found a leaked secret or unsafe behaviour? See [SECURITY.md](SECURITY.md).

## Licence

MIT. See [LICENSE](LICENSE), including the safety notice.
