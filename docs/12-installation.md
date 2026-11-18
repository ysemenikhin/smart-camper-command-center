# 12 — Installation

You cannot deploy this unchanged. The relay map, tank dimensions and corner
constants describe one trailer. This is the order that works.

## 0. Before anything

Read [11 — Safety](11-safety.md). Then decide which subsystems you actually
want — the relay board and the suspension board are independent and either works
without the other.

## 1. Prerequisites

- Home Assistant OS (this runs on a Raspberry Pi 4)
- ESPHome Device Builder add-on
- HACS, for the integrations and cards in [03 — Integrations](03-integrations.md)
- A 2.4 GHz network. **The ESP32 radios cannot see a 5 GHz-only SSID.**

## 2. Secrets

```bash
cd esphome
cp secrets.yaml.example secrets.yaml
openssl rand -base64 32          # paste into api_encryption_key
```

`secrets.yaml` is gitignored. Keep it that way.

## 3. Flash the relay board first

It is the simpler board, and it proves your toolchain before you fight BLE.

1. Edit `esphome/relay-board.yaml` — **rename every relay to your loads.** The
   ids stay `relay_01`…`relay_16` so they match wiring tags; the `name:` is what
   becomes the entity id.
2. Set the tank calibration numbers to something harmless (empty 0, full 3000)
   until you calibrate properly.
3. First flash over **USB**. OTA afterwards.
4. Confirm each relay clicks from Home Assistant *and* from its physical button.

> The GPIO5 strapping-pin warning at compile time is expected on this board and
> is harmless.

## 4. Flash the suspension board

Only if you have compatible hardware — a DN-3G manifold with BLE, four corners,
and an IMU.

1. First flash must be over **USB** (the UART port), then OTA.
2. Run the IMU zero calibration on verified-level ground.
3. **Verify the roll and pitch signs physically** — lift one side, watch the sign.
   See [10 — Calibration](10-calibration.md). Do not skip this.
4. Leave Auto Level switched off until the signs are confirmed.

## 5. Home Assistant package

```bash
cp homeassistant/packages/*.yaml  <config>/packages/
```

and in `configuration.yaml`:

```yaml
homeassistant:
  packages: !include_dir_named packages
```

Then **Developer Tools → YAML → Check configuration**, and restart.

Expect errors on first load for entities you do not have — the package references
specific BMS, MPPT, router and heater entity ids. Either install those
integrations or delete the sections you do not need.

## 6. Custom cards

Install via HACS. `button-card` and `card-mod` are **required** — without them
the dashboard renders as error cards.

## 7. Theme

```bash
cp homeassistant/themes/garmin_dark.yaml  <config>/themes/
```

Restart, then select it in your profile. The dashboard's colours assume it.

## 8. Dashboard

Create a new dashboard, switch to **raw configuration editor**, and paste
`homeassistant/dashboards/smart-camper-dashboard.yaml`.

> Home Assistant **strips comments** when you save from the raw editor. Keep the
> file in the repo as the documented master and edit there, not in the browser,
> or you will lose every explanatory comment the first time you touch a tile.

## 9. Calibrate

Nothing is trustworthy until you do. Follow [10 — Calibration](10-calibration.md)
in order: tank senders, then corner heights, then IMU.

## 10. Adapt the dashboard to your screen

The layout is tuned for 1340 × 800. **Measure your own device** — a browser
window is not a substitute, and tuning against the wrong viewport wasted real
time on this build. Tile heights and the grid-title `card_mod` block are the two
levers that matter.

## Version discipline

Every file here carries a version and a changelog in its header. It is worth
keeping:

- One change at a time, then confirm it works before the next
- Bump the version and add a changelog line in the same edit
- Always build the next change from the last **confirmed-working** version, not
  from the last one you wrote

On a system where a bad edit can drop a trailer on the ground, being able to say
exactly which version last worked is worth the bookkeeping.

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| Entity is `unknown`, template looks right | You referenced a `unique_id`, not an `entity_id`. Check Developer Tools. |
| Tile renders but does nothing | `service:` cannot be templated in button-card. Use a literal service, templated `entity_id`. |
| Icon missing on a short tile | `size:` is a % of card *width*; `#img-cell` is `overflow: hidden` and can compute to 0 px. See [03](03-integrations.md). |
| Sensor "no longer provided by the template integration" | A structural YAML error — often a stray `- binary_sensor:` mid-list silently redefining sensors. Parse the file. |
| Duplicate mapping key on dashboard save | Two `icon:` or `styles:` keys in one card. |
| BMS entities all unavailable | Check the integration version — 2.14.0 is broken, 2.13.0 works. |
| Tank reads 0% not unavailable | Missing `availability:` guard, or a `\| float(0)` swallowing the absence. |
