# 03 — Integrations, add-ons and custom cards

Everything Home Assistant needs. Taken from the live system's config-entry and
device registries, so this is what is genuinely installed, not what ought to be.

## Core integrations

| Integration | Provides | Source |
|---|---|---|
| **ESPHome** | Both boards — "Camper Air Suspension" and "Relay Board" | Built in |
| **MQTT** (Mosquitto) | Message broker | Add-on |
| **go2rtc** | Camera restreaming | Built in |
| **Generic Camera** | 8 entries — 4 cameras × main + sub stream | Built in |
| **MJPEG IP Camera** | Interior tablet camera | Built in |
| **Bluetooth** | Host adapter, for BLE BMS and iBeacon | Built in |
| **Mobile App** | Tablet and phone — notifications and TTS | Built in |
| **Met.no** | Weather forecast | Built in |
| **Forecast.Solar** | 2 entries, one per array | Built in |
| **Starlink** | Dish status, obstruction, heading | Built in |
| **SpeedTest.net** | WAN throughput | Built in |
| **Ping** | `1.1.1.1` — the actual internet-up test | Built in |
| **Google Translate TTS** | Speech | Built in |
| **Wyoming** (Piper) | Local text-to-speech | Add-on |
| **Backup** | Scheduled backups | Built in |
| **Raspberry Pi** / **RPi Power** | Host health, undervoltage warning | Built in |
| **Template** (trigger + webhook) | Router GPS → `device_tracker.camper_gps` and sensors (`packages/camper_gps.yaml`) | Built in |
| **Browser Mod** | Tablet media player for spoken announcements (`packages/camper_voice.yaml`) | HACS |

The RPi Power one earns its place: undervoltage on a 12 V system with a
long DC run is a real failure mode, and it shows up as random Pi reboots that
look like software faults.

## HACS integrations

| Integration | Provides | Repo |
|---|---|---|
| **BLE Battery Management System** | Both LiFePO₄ banks over BLE | `patman15/ha-bms-ble` |
| **GL.iNet Router** | Cellular signal, WAN mode, repeater, throughput | `vithurshanselvarajah/ha-glinet` |
| **Renogy** | MPPTs and the 920 Ah shunt | `firstof9/ha-renogy` |
| **Diesel Heater** | Vevor heater control and consumption | `Spettacolo83/...` |

> **Pin the BMS integration version.** Version 2.13.0 works. 2.14.0 broke the
> connection outright ("BMS is stale / communication timed out") — a regression
> from an `aiobmsble` rewrite. This is the single most fragile dependency here,
> because it is the primary battery source. Test BMS updates before trusting them.

## HACS frontend (custom cards)

| Card | Used for |
|---|---|
| **button-card** | Almost every tile. The dashboard is built on it. |
| **card-mod** | Grid titles, the settings-lock overlay, the unlock blink |
| **layout-card** | Grid layout control |
| **apexcharts-card** | Battery and solar history graphs |
| **Mushroom** | A few standard rows |
| **Stack In Card** | Nested card grouping |
| **Battery State Card** | Battery entity rows |
| **Card-Mod Studio** | Development aid, not required at runtime |

`button-card` and `card-mod` are **required** — the dashboard will not render
without them.

## Add-ons

| Add-on | Purpose |
|---|---|
| ESPHome Device Builder | Compile and OTA both boards from inside HA |
| File editor | Edit packages without SSH |
| Terminal & SSH | Shell access |
| Mosquitto broker | MQTT |
| Cloudflared | Remote access without opening a port |
| Firefox | A browser on the HA host, for router admin pages |

## Custom cards: two traps worth knowing

Both cost real debugging time on this project.

**1. `custom:button-card` does not template the `service:` field.**
`[[[ ]]]` templates are evaluated in `service_data` but **not** in `service`.
A tile written as `service: [[[ return 'script.' + variables.script ]]]` sends
that string verbatim as a service name and silently does nothing. The working
pattern is a literal service with a templated entity:

```yaml
tap_action:
  action: call-service
  service: script.turn_on          # literal
  service_data:
    entity_id: "[[[ return 'script.' + variables.script; ]]]"   # templated
```

**2. `size:` is a percentage of card width, not height.**
`panel_button` inherits `size: 34%`. In a wide, short card — a 658 px-wide camera
cell 44 px tall — that asks for a ~220 px glyph, which cannot draw, so the icon
silently vanishes. Worse, the icon lives inside `#img-cell`, which is
`overflow: hidden` and can compute to 0 px wide. Fixing it needs `img_cell` sized
explicitly:

```yaml
styles:
  img_cell: [{width: 22px}, {min-width: 22px}, {overflow: visible}]
  icon:     [{width: 20px}, {height: 20px}, {"--mdc-icon-size": 20px}]
```

## Entity naming

Everything this project creates is prefixed:

- `sensor.camper_*` — template sensors from the package
- `switch.relay_board_*` — relay board outputs
- `*.camper_air_suspension_*` — suspension board

> **`unique_id` is not `entity_id`.** The entity id derives from `name:`. Two
> separate bugs here came from templates referencing a `unique_id`
> (`sensor.camper_cell_signal_pct`) which silently resolved to nothing and then
> to `0` — rendering as a confident "Poor" signal rating. Always verify entity
> ids in Developer Tools.
