# 05 — Relay board (KinCony KC868-A16S)

Sixteen relays, sixteen physical inputs, four analogue inputs, RF433, an RTC and
Ethernet, on one DIN-mountable ESP32 board.

## Relay map

**All sixteen are allocated. None are spare.**

| # | Load | Colour on dashboard | Notes |
|---|---|---|---|
| 1 | Main light | amber | |
| 2 | Outdoor left | amber | Flood spots |
| 3 | Bedroom light | amber | |
| 4 | Front outdoor | amber | LED bar |
| 5 | Main bedroom red | red | Night-vision-safe |
| 6 | Outdoor right | amber | Flood spots |
| 7 | Fan | blue | |
| 8 | Awning red left | red | |
| 9 | Water pump | blue | |
| 10 | Awning red right | red | |
| 11 | **Inverter** | amber | 220 V AC contactor |
| 12 | Inverter LED | — | Ganged to 11, both directions |
| 13 | **Electric steps** | amber | `ALWAYS_ON`, toggled by input DI12 |
| 14 | Water gauges | red | Powers the tank senders |
| 15 | **Stabilisers** | red | `ALWAYS_OFF` + 10-minute auto-off |
| 16 | Tank & pipe heating | red | Reserved, not yet wired |

Free inputs: **DI13 and DI16**.

## Three relays that need explanation

### Relay 11 + 12 — the inverter gang

Relay 11 is the inverter's dry contact; relay 12 drives the panel LED. They are
ganged **in both directions in firmware**, so the LED is correct whether the
inverter was switched from the physical button, from Home Assistant, or from the
board itself. Without this, the LED lies whenever the switch source changes.

Note the drawing this was built from had these two swapped — the as-built wiring
is authoritative.

### Relay 15 — stabilisers, with a real timer

The stabiliser jacks, front electric jack and (originally) the steps all ran off
one 90 A relay fed from a separate fuse box, switched by a **locking** (non-momentary)
button.

Two problems, both solved in firmware rather than in HA:

1. **A locking switch survives a reboot.** A naive "follow the switch" design
   would re-energise the jacks the moment power returned, with nobody watching.
   So relay 15 is `ALWAYS_OFF` on boot and there is an explicit boot lockout.

2. **A 10-minute auto-off**, because leaving the jack circuit live is how a
   stabiliser gets driven into the ground or a leg gets left down. The timer is a
   `script` with `mode: restart`, cancelled on turn-off:

```yaml
switch:
  - platform: gpio
    name: "Stabilisers"
    id: relay_15
    restore_mode: ALWAYS_OFF
    on_turn_on:
      - script.execute: stabiliser_timeout
    on_turn_off:
      - script.stop: stabiliser_timeout

script:
  - id: stabiliser_timeout
    mode: restart
    then:
      - delay: 10min
      - logger.log: "Stabilisers: 10 minute timeout - cutting power"
      - switch.turn_off: relay_15
```

**This timer is in firmware on purpose.** A safety cut-off that depends on the
Raspberry Pi being awake and the network being up is not a safety cut-off.

### Relay 13 — steps, split out

The steps were originally on the stabiliser circuit, which meant the 10-minute
timer would also kill the steps, and the steps could not be used independently.
They now have their own relay, `ALWAYS_ON` so they behave like a normal circuit,
toggled by input DI12.

## Board quirks

| Quirk | Consequence |
|---|---|
| Relays and inputs are on **4 × PCF8574 I²C expanders** (relays 0x24/0x25, inputs 0x22/0x23), not native GPIO | I²C on GPIO4/5. A bus fault takes out all sixteen at once. |
| **GPIO5 is a strapping pin** | ESPHome warns at compile time. Unavoidable on this board; harmless here. |
| DS3231 RTC at 0x68 + AT24C32 EEPROM at 0x57 | Gives wall-clock time with no network — used for the gauges schedule |
| ANALOG_A1 = **GPIO36**, A2 = **GPIO34** | These are the 0–5 V conditioned inputs. **A3 (GPIO35) and A4 (GPIO39) are 4–20 mA** current inputs and are wrong for voltage senders. |
| RF433 receiver on GPIO16 | **6 learnable slots** (v2.3.7). Press a fob, press *Learn Slot N* in HA; *RF Slot N Received* pulses 200 ms per press and drives HA automations. Unknown codes are ignored (v2.3.6). |
| 1-Wire on GPIO14 | **4 × DS18B20** connected (v2.3.0+): clean tank, grey tank, water pipe 1, water pipe 2. Powered from 3V-DC with a 4.7 k pull-up, 60 s updates rounded to 0.1 °C, per-sensor offsets from a 3-reading average (v2.3.5). Addresses live in `secrets.yaml`. |

> The A2 pin was initially guessed as GPIO39 and was wrong — that is A4, a
> current input. Check the vendor documentation for your board revision rather
> than inferring from pin order.

## Analogue inputs — filtering

The raw tank sender reading wandered 18 mV peak-to-peak on a completely still
tank, which rendered as a 1.3% wobble. The filter chain:

```yaml
samples: 32                    # average 32 reads inside each update
filters:
  - median: {window_size: 5, send_every: 1}
  - sliding_window_moving_average: {window_size: 12, send_every: 1}
  - round: 3
```

- `samples: 32` — noise falls with √N, so 32 reads cut it to ~0.23%. This was the
  single biggest improvement; it had been at 1, i.e. no averaging at all.
- `median: 5` — rejects one-off spikes
- `sliding_window_moving_average: 12` at a 5 s update = a **60-second mean**,
  leaving ~0.07% jitter

**The 60-second window has a consequence for calibration:** every reading is a
one-minute trailing average, so a value read while the tank is still filling is
biased low. Stop filling, wait two minutes, then read.

`round: 3` is not cosmetic. Without it the full float went to Home Assistant
(`0.29166665673255920`), so every 5 s update was a new database row — **12,312
rows per day from one sensor**. `accuracy_decimals` affects display only; HA
writes a row when the state *string* changes, so rounding a stable value stops
the churn without losing anything readable.

## Gauges relay and the "unavailable, not zero" rule

The tank senders are unpowered unless relay 14 is on. So the tank sensors publish
`NaN` whenever that relay is off, and the HA template sensors carry an
`availability:` guard that makes them **unavailable** rather than reporting 0%.

An empty tank and an unpowered sender must not look the same on a dashboard.

## Status entities (v2.3.8)

The board reports its own health to HA as diagnostic entities:

- **Config Version**: `2.3.8 (2026-10-20)`, from the `substitutions:` block.
- **ESPHome Version.**
- **IP Address.**
- **Uptime**, every 15 min, so it adds no recorder churn.
- **Status**: connected to HA.
- **Restart** button. A reboot always leaves RE15 Stabilisers **off**.
