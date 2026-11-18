# 11 — Safety

Read this before building any of it.

This system controls compressed air, mains-voltage AC, a diesel burner, and jacks
that lift several tonnes. Software mistakes here have physical consequences.

## What can actually hurt you

| System | Hazard |
|---|---|
| **Air suspension** | A trailer can drop on a limb. Air at 150 psi in a burst line whips. A corner raising unexpectedly can tip a trailer on a slope. |
| **Stabiliser jacks** | Crush injury. A jack driven into the ground can lift a wheel or bend a leg. Exposed jack buttons get leaned on. |
| **Electric steps** | Deploying while moving destroys them and endangers anyone alongside. |
| **Inverter** | 230 V AC in a damp aluminium box. |
| **Diesel heater** | Combustion, hot exhaust, fuel. |
| **Compressor** | Stored energy remains after power is removed. |

## Design rules this project follows

### 1. Safety timers live in firmware

The stabiliser circuit's 10-minute cut-off runs on the ESP32, not in a Home
Assistant automation.

A timer that depends on the Raspberry Pi being awake, the network being up and
the automation not being disabled **is not a safety timer**. Firmware runs
whether or not anything else does.

### 2. Dangerous circuits fail OFF

Relay 15 (stabilisers) is `ALWAYS_OFF` on boot, with an explicit boot lockout.

The physical switch is a **locking** type, so it holds its position through a
power cut. A naive "follow the switch on boot" design would energise the jacks
the moment power returned, with nobody watching. So the firmware ignores the
switch position at boot and requires a fresh press.

### 3. Missing data is shown as missing

Tank sensors go **unavailable** when the gauges relay is off — never 0%.

An empty tank and an unpowered sender must not look the same. Several bugs here
came from `| float(0)` turning an absent reading into a confident zero: an
unavailable cell signal became "Poor", a dead BMS became "0 W / Idle".

**A wrong number is worse than a missing one**, because a missing one prompts you
to look.

### 4. Degraded operation is visible

When the battery drops to shunt fallback, the alert strip says so. The system
keeps working, and tells you it is not working the way it should.

### 5. Consequential actions confirm

Auto Level, mode changes, unlocking settings, re-baselining the fuel gauge — all
ask first. The settings that govern how the suspension behaves on the road sit
behind a lock that re-engages after five minutes on its own.

### 6. Road-legal systems are not on this network

Brake lights, indicators and running lights are **wired conventionally** and are
not on any relay this software can touch.

This is deliberate. A road-legal lighting circuit should not depend on a
Raspberry Pi, an ESP32, or a YAML file someone edited at a campsite at 11 pm.

## Known gaps on this build

Stated plainly, because a safety document that only lists what is handled is
misleading.

| Gap | Risk | Status |
|---|---|---|
| **No movement interlock on the stabilisers** | The jacks can be energised while the trailer is capable of moving | The real exposure here is the uncovered front-jack buttons and people catching them with an elbow while getting into the storage box — not driving away with legs down. An **ignition feed** on a spare input (DI13/DI16 are free) is the intended fix, preferred over GPS speed because it is a direct electrical fact rather than an inference. |
| **No steps-retracted interlock** | Steps can be left deployed when driving off | Currently procedural. The steps were split onto their own relay partly to make an interlock possible later. |
| **Manifold BLE can go stale** | Suspension control silently unavailable | Detected and alerted. A power-cycle watchdog using the manifold's ignition relay is designed but not yet built. |
| **Tank heating relay unwired** | None currently | Relay 16 is allocated but nothing is connected. |

## If you build from this

1. **Verify every pin against your own board revision.** The A2 analogue pin here
   was initially assumed to be GPIO39; that is A4, a 4–20 mA current input, and
   would have been wrong for a voltage sender.
2. **Verify IMU signs physically** before enabling any automatic levelling. A
   sign error is a runaway, not a small offset.
3. **Test every cut-off by triggering it**, not by reading the code.
4. **Fuse every relay circuit appropriately.** The relay board switches; it does
   not protect.
5. **Keep a mechanical way out.** Every relay here has a physical switch beside
   it, and the trailer works with Home Assistant switched off entirely. Retain
   that property.

## Not a certified system

Nothing here is safety-certified, redundant, or fail-operational. It is a
well-engineered hobby system on one trailer. Treat it as a starting point for
your own engineering judgement, not as a validated design.
