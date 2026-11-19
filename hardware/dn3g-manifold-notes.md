# DEPCON DN-3G ("DOWN3") manifold — integration notes for Camper

Source: DN-3G height-gauge version manual V1.5 (2024-01-08), Shenzhen DEPCON.
Hardware: ECU + 4-corner solenoid valve group + air pump + wired remote.
BLE: name `DOWN3`, Gen3 app, 0–30 m, NO auth (Gen2 needed password/login).
Camper MAC: XX:XX:XX:XX:XX:XX. ESP config: v3.3.0+.

## Facts that matter for our ESP/HA setup
- **Height-gauge version, sensors NOT installed yet.** The valve's own
  5-gear system (factory 10/30/50/70/100 % of height scale) is
  height-based → meaningless/unreliable until height rulers are
  installed AND min/max calibration is done (procedure: factory reset →
  low-lying → calibrate MIN → raise full+level → calibrate MAX).
  Expect possible E-15/17/19/21 (height sensor failure) fault codes
  until then. Our ESP PSI-preset system is independent — it pulses
  corner valves against corner pressure sensors, so it works today.
- **Valve "Auto Adjustment"** = valve-side auto-maintain to current
  gear (±2 %). CONFLICTS with ESP "Preset Auto Maintain". Rule:
  only ONE may be on. Recommended: valve Auto Adjustment OFF,
  ESP Auto Maintain ON.
- **"Low Down With Ignition Off"** dumps ALL bags to 0 on ignition
  off. MUST be OFF on a trailer (ignition = our manifold relay).
- **"Flame out control"**: when OFF, valve de-energizes with ignition.
  We power the manifold via the ESP relay (Air Manifold,
  ALWAYS_ON), so set to keep valve controllable — but never leave
  manifold energized long on battery without charge.
- **Air pump control**: pump auto-starts below min / stops at max.
  Factory 100–169 psi (absolute limits 100–200). Note: dashboard
  "tank overpressure" banner is set at >150 psi — if pump stop is
  169, RAISE the dashboard threshold to ~180 or lower pump stop.
- **Air pressure/height limit** (valve-side corner limits): align with
  ESP values (ESP: min 20 / max 75 / emergency cap 80 psi).
- **Air leakage alarm**: recommended ON (5 beeps on leak).
- **Gear ±2 % tolerance** is normal per manual.
- Voice control exists on the remote ("little down down" wake word).

## Fault codes (wired remote display)
E-01 tank leak · E-02 pump/tank sensor · E-03/04 FL sensor leak/fail ·
E-06/07 FR · E-09/10 RL · E-12/13 RR · E-15/17/19/21 height sensor
FL/FR/RL/RR fail · E-23/24 ignition V low/high · E-25/26 battery V low/high.

## Leak testing
Soapy water 1:4; allowable <7 sccm per joint; pressure drops ~2 psi
per 5 °C cooling (not a leak).

## Open items
- Validate FFF1 frame layout on Gen3 (byte order: gear, tank, FL, RL,
  RR, FR) — assumed same as Gen2, unverified.
- Height sensors: install later per manual section IV (mount mid-travel,
  pendulum perpendicular, equal swing angles, steering interference
  test on fronts). Then valve gears + height calibration become usable
  and we decide ESP height integration (ESP v4.x).

---

## DOWN3 (Gen3) BLE protocol — DECODED (v3.9.0)

Source: nRF GATT dump + DOWN 2.3 app (`cn.com.depcon.carble`) + ESP capture.

**GATT:** service `FFF0`, `FFF2` = write (cmd), `FFF1` = notify (status, CCCD 2902). No auth.

**Commands (write to FFF2)** — identical to Gen2:
- Status poll `02 00 05 07`; Read settings `02 5D 5D BC`
- Corner ±: FL `02 0A 0A 16`/`02 0B 0B 18`, FR `02 08 08 12`/`02 09 09 14`,
  RL `02 10 10 22`/`02 11 11 24`, RR `02 0E 0E 1E`/`02 0F 0F 20`
- Axle: FrontUp `02 06 06 0E` FrontDn `02 07 07 10` RearUp `02 0C 0C 1A` RearDn `02 0D 0D 1C`
- Quick gear N: `02 18 0N cksum`; Low-on `02 13 13 28`

**Notify stream (FFF1):** many small frames, each `[type][len][payload..len][checksum]`,
checksum = sum(type..last payload) & 0xFF. The rich live frame is **type 0x01, len 0x0A**:

| payload byte | field |
|---|---|
| p0 | current gear (0 = none) |
| p1 | air tank PSI |
| p2 | FL height % (100 = no sensor) |
| p3 | RL height % |
| p4 | RR height % |
| p5 | FR height % |
| p6 | FL corner PSI |
| p7 | RL corner PSI |
| p8 | RR corner PSI |
| p9 | FR corner PSI |

Small single-byte frames (0x02,0x05,0x06,0x08,0x09,0x0E) = per-channel status flags
(meaning TBD, not needed for PSI). Frame 0x10 (15 zeros) = gear/settings block, TBD.

Corner order everywhere = **FL, RL, RR, FR** (matches app iArr[3..6]).
