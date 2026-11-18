# 02 — Hardware & bill of materials

Everything physically in the trailer. Where a choice was non-obvious, the reason
is given — those reasons are usually the useful part.

## Controllers

| Item | Detail | Notes |
|---|---|---|
| Raspberry Pi 4 | Home Assistant OS | Runs everything. On the trailer's 12 V through a regulated supply. |
| ESP32-S3-N16R8 | Air suspension controller | On a screw-terminal breakout. **Replaced a classic ESP32** — the S3's second core and larger PSRAM handle BLE to the manifold plus IMU fusion without stalling. |
| KinCony KC868-A16S | Relay board | ESP32-based, 16 relays, 16 opto inputs, 4 analogue inputs, RS485, RF433, DS3231 RTC, Ethernet. |
| Lenovo TB311FU | 10" wall tablet | The primary interface. The dashboard is laid out for its **1340 × 800** usable area. |

### Why the KC868-A16S

Sixteen relays and sixteen physical inputs on one DIN-mountable board with
Ethernet, for less than the cost of wiring that many separate modules. The
opto-isolated inputs matter: every relay has a real switch beside it, so the
trailer works with Home Assistant switched off.

Its quirks are documented in [05 — Relay board](05-relay-board.md). The important
one: relays and inputs are on **four PCF8574 I²C expanders**, not native GPIO.

## Pneumatics

| Item | Detail |
|---|---|
| DN-3G air management manifold | With its own ECU, controlled over BLE. Four independent corner solenoids plus IN/EXH. |
| 4 × air bags | One per corner, FL / FR / RL / RR |
| Air tank | Compressor cut-in **110 psi**, cut-out **~150 psi**, safety valve **175 psi** |
| 2 × electric ball valves | Off-road articulation. Left valve ties front-left + rear-left; right valve ties front-right + rear-right. |
| BMI160 IMU | 6-axis, on I²C at 0x69. Provides roll and pitch. |

**No cross-link valve exists in the manifold** — the articulation valves are
external and were added specifically to allow axle articulation off-road. With
them open each *side* becomes one volume, so pitch equalises within a side and
roll control remains; levelling always runs with them **closed**.

## Energy

| Item | Detail |
|---|---|
| 2 × LiFePO₄ banks | 12 V, read over BLE via the BMS integration. Jiabaida BMS. |
| Renogy 920 Ah shunt | Used as a **fallback** for all battery figures when either bank drops |
| Renogy MPPT 1 | 440 W array, ~27.6 V string |
| Renogy MPPT 2 | 880 W array, ~63.9 V string |
| Inverter | 220 V AC, switched by relay 11 with an LED feedback relay ganged to it |

## Water

| Item | Detail |
|---|---|
| Clear water tank A | 114 × 70 × 23 cm = **183.5 L** |
| Clear water tank B | 81 × 55 × 23 cm = **102.5 L** |
| Grey water tank | 81 × 55 × 23 cm = **102.5 L** |
| 2 × level senders | Analogue, read on the relay board's AI1 / AI2 (0–5 V conditioned inputs) |
| Water pump | Relay 9 |

Published capacities are **280 L clear / 100 L grey** — the owner's working
figures, slightly below the geometric maxima because the tanks are never filled
to the absolute brim.

## Connectivity

| Item | Detail |
|---|---|
| GL.iNet X3000 (Spitz AX) | 5G router. Cellular WAN plus Wi-Fi repeater mode. |
| Starlink | Secondary WAN, repeated by the router |

## Cameras

| Item | Detail |
|---|---|
| 4 × exterior IP cameras | Left, right, rear, front. Each exposes a **main** and a **sub** stream. |
| 1 × interior camera | MJPEG, on the tablet |

The dual-stream arrangement is the trick that makes a 4-up live grid work on a
tablet: the grid runs the low-resolution sub-streams so all four decode at once,
and tapping a tile opens that camera's full-resolution main stream.

## Heating

| Item | Detail |
|---|---|
| Vevor diesel heater | Integrated via a custom HA integration. Reports cumulative litres consumed but has **no tank level sensor** — hence the virtual fuel tank in the package. |

## Loads on the relay board

See [05 — Relay board](05-relay-board.md) for the full map. Summary: interior and
exterior lighting, awning lights, inverter, fan, water pump, electric steps,
water gauges, stabiliser circuit, tank heating.

**All sixteen relays are allocated. None are spare.** Any new load needs one
freed or additional hardware.

## What this does NOT include

- No mains shore-power management
- No fridge control (runs on its own thermostat)
- No tyre pressure monitoring
- No brake or road-legal lighting control — deliberately. Road lighting is
  wired conventionally and is not on any relay this software can reach.

That last one is a safety boundary, not an omission. See [11 — Safety](11-safety.md).
