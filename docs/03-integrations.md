# 03 — Integrations, add-ons and custom cards

Everything Home Assistant needs. Taken from the live system's config entries,
HACS and add-on lists on 2026-11-18, so this is what is genuinely running, not
what ought to be. The live system runs **Home Assistant 2026.10.2** with the
**ESPHome Device Builder 2026.10.2** add-on.

## Core integrations

| Integration | Provides | Source |
|---|---|---|
| **ESPHome** | Both boards: "Air Suspension" and "Relay Board" | Built in |
| **MQTT** (Mosquitto) | Message broker | Add-on |
| **go2rtc** | Camera restreaming | Built in |
| **Generic Camera** | 8 entries: 4 cameras × main + sub stream | Built in |
| **MJPEG IP Camera** | Interior tablet camera | Built in |
| **Bluetooth** | Host adapter, for the BLE BMS, the diesel heater and iBeacon | Built in |
| **Mobile App** | Tablet and phone: notifications and spoken announcements | Built in |
| **Met.no** | Weather forecast | Built in |
| **Forecast.Solar** | 2 entries, one per array | Built in |
| **Starlink** | Dish status, obstruction, heading | Built in |
| **SpeedTest.net** | WAN throughput | Built in |
| **Ping** | `1.1.1.1`, the actual internet-up test | Built in |
| **Wyoming** (Piper) | Local text-to-speech | Add-on |
| **Backup** | Scheduled backups | Built in |
| **Raspberry Pi** / **RPi Power** | Host health, undervoltage warning | Built in |
| **Template** (trigger + webhook) | Router GPS → `device_tracker.camper_gps` and sensors (`packages/camper_gps.yaml`) | Built in |

The RPi Power one earns its place: undervoltage on a 12 V system with a
long DC run is a real failure mode, and it shows up as random Pi reboots that
look like software faults.

### Spoken announcements

`packages/camper_voice.yaml` speaks suspension events on the tablet.

**Browser Mod is not used on the live system.** Without it, each announcement
goes to the tablet as a Companion-app (Mobile App) TTS notification, and the
tablet's own text-to-speech reads it out. This can lag by up to about a minute,
because the notification travels through Android push.

Browser Mod is optional. If you install it, the package finds its media player
and speaks through it straight away, using **Piper** when it is installed
(local, no internet) or Home Assistant Cloud otherwise.

## HACS integrations

| Integration | Provides | Repo | Running |
|---|---|---|---|
| **BLE Battery Management System** | Both LiFePO₄ banks over BLE | [`patman15/BMS_BLE-HA`](https://github.com/patman15/BMS_BLE-HA) | 2.19.0 |
| **GL.iNet Router** | Cellular signal, WAN mode, repeater, throughput | [`vithurshanselvarajah/ha-glinet-router`](https://github.com/vithurshanselvarajah/ha-glinet-router) | 1.6.6 |
| **Renogy** | MPPTs and the 920 Ah shunt | [`firstof9/ha-renogy`](https://github.com/firstof9/ha-renogy) | 2.1.2 |
| **Diesel Heater** | Vevor heater control and consumption, over BLE | [`Spettacolo83/homeassistant-diesel-heater`](https://github.com/Spettacolo83/homeassistant-diesel-heater) | 2.1.4.1 |

> **Test every BMS integration update before trusting it.** Version 2.14.0 once
> broke the connection outright ("BMS is stale / communication timed out"), a
> regression from an `aiobmsble` rewrite. The live system runs 2.19.0. This is
> the most fragile dependency here, because it is the primary battery source.

## HACS frontend (custom cards)

The dashboard needs exactly three custom cards:

| Card | Used for | Running |
|---|---|---|
| [**button-card**](https://github.com/custom-cards/button-card) | Almost every tile (151 cards). The dashboard is built on it. | 7.0.1 |
| [**card-mod**](https://github.com/thomasloven/lovelace-card-mod) | Grid titles, the settings-lock overlay, the unlock blink | 4.2.1 |
| [**apexcharts-card**](https://github.com/RomRider/apexcharts-card) | Battery and solar 24 h history graphs | 2.2.3 |

`button-card` and `card-mod` are **required**: the dashboard will not render
without them.

The live system also has layout-card, Mushroom, Stack In Card, Battery State
Card and Card-Mod Studio installed. This dashboard does not use any of them.

## Add-ons

| Add-on | Purpose |
|---|---|
| ESPHome Device Builder | Compile and OTA both boards from inside HA |
| Piper | Local text-to-speech, used when Browser Mod is installed |
| Mosquitto broker | MQTT |
| File editor | Edit packages without SSH |
| Terminal & SSH | Shell access |
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
