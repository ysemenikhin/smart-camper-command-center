# 10 — Calibration

The method, with the real numbers from this trailer as worked examples. Copy the
method; measure your own values.

## Principle: label every number

Three kinds of number end up in a config, and confusing them is how systems lie
to you:

| Label | Meaning |
|---|---|
| **Measured** | Read off the hardware. Repeatable. |
| **Derived** | Computed from measured values plus stated geometry. |
| **Assumed** | A placeholder. Not verified. |

Assumed values are fine — as long as they are *named* as assumed everywhere they
appear, so nobody later mistakes them for measurements.

---

## Water tank senders

### Step 1 — know your instrument before you trust it

Before calibrating, check whether the reference you are comparing against is
continuous or quantised.

This trailer's panel gauge displays only **12, 23, 37, 50, 62, 73, 86, 99** —
eight steps of 12.5%, and it never reaches 100 even with water pouring out of the
filler. So:

- It cannot validate anything finer than ±6%
- A true 19% displays as "12", because 19 falls between step 1 and step 2

That last point resolved an apparent 7-point disagreement that looked like a
calibration error for days. It was not an error. It was quantisation.

### Step 2 — calibrate in board-read millivolts

Not multimeter millivolts at the sender. The board's analogue front end applies
an unknown divider; calibrating on what the board reports removes that unknown
rather than modelling it. It also means **no external divider should be fitted**.

### Step 3 — let the reading settle

The filter chain includes a 60-second moving average, so every value is a
one-minute trailing average.

**Stop filling. Wait two minutes. Then read.** A reading taken while water is
still going in is biased low, and that bias is invisible.

### Step 4 — take points across the range

Real data from the clear tank:

| Gauge % | Board mV |
|---|---|
| 12 | 388.9 |
| 23 | 497 |
| 37 | 665 |
| 50 | 799 |
| 62 | 921 |
| 73 | 1037 |
| 86 | 1187 |
| 99 (overflowing) | 1318 |

### Step 5 — fit, and check the residuals

Least-squares on those points:

```
mV = 258.3 + 10.734 × gauge%
```

| Gauge % | Measured | Predicted | Error |
|---|---|---|---|
| 23 | 497 | 505 | −8 |
| 37 | 665 | 656 | +9 |
| 50 | 799 | 795 | +4 |
| 62 | 921 | 924 | −3 |
| 73 | 1037 | 1042 | −5 |
| 86 | 1187 | 1181 | +6 |
| 99 | 1318 | 1321 | −3 |

±9 mV across an 820 mV span — about **1%**. The sender is linear.

**The strongest evidence** is that the 12% point was left out of the fit, and the
resulting line predicts it at 387 mV against a measured 388.9. A line landing
2 mV from a point it never saw is not a coincidence.

### Step 6 — decide what 0% and 100% mean

Extrapolating the fit gives gauge-0% at **258 mV** and gauge-100% at **1332 mV**.
But the tank overflows at **1318 mV**, and the sender reads **~142 mV** dry.

So the panel gauge's scale sits *inside* the tank's real range — its zero is
about 2 cm above dry, its 100 is above what the tank can reach.

Two valid answers, and you must choose consciously:

| Choice | Set empty/full to | Result |
|---|---|---|
| Match the panel gauge | 258 / 1332 | Agrees with the gauge everywhere within 1 point. 0% is not dry; % cannot be converted to litres. |
| True contents | 142 / 1318 | 100% = overflowing, 0% = dry, % × capacity = litres. Reads ~6 points above the panel gauge mid-tank, permanently. |

This build uses **both**: the gauge-matched pair drives the percentage, a second
pair in Home Assistant drives the litres. See [06 — Water tanks](06-water-tanks.md).

### Step 7 — the check nobody does

Everything above proves the sender agrees with **the gauge**. It does not prove
either agrees with **litres** — both could share the same bend.

Pour a *measured* volume into an empty tank and check it against the prediction.
At 12.44 L/cm and ~51 mV/cm, the clear tank should move about **4.1 mV per
litre**, so 20 L ≈ 222 mV.

This is still outstanding on this trailer. It is listed as unverified rather than
quietly assumed.

### Adjusting the right end

If the top of the scale is wrong, change **full** — not empty.

Near a full tank, moving *empty* barely shifts the number: at 1318 mV, changing
empty from 258 to 220 moves the reading from 98.70% to 98.74%. But it shifts the
whole lower half, taking the worst mid-tank error from ±0.9 to +3.0 points.

**Empty anchors the bottom, full anchors the top.** Use the one nearest the error.

---

## Suspension corner heights

Height sensors report a percentage; humans think in centimetres.

**Method:** set a corner to several known percentages across its range, and tape-
measure the actual height at each. Fit a line per corner.

Results here (R² ≥ 0.998 on all four):

| Corner | cm = |
|---|---|
| FL | 0.1382 × % + 14.32 |
| FR | 0.1369 × % + 14.36 |
| RL | 0.1536 × % + 14.41 |
| RR | 0.1465 × % + 14.23 |

RL's slope is 12% steeper than FR's. **Do not assume the four corners share a
line** — mounting geometry differs, and a shared constant would put one corner
out by over a centimetre at full travel.

---

## IMU orientation

The one calibration you must do by hand, once, and then hard-code.

1. Park on ground you have verified level independently — a spirit level on the
   chassis, not the floor.
2. Run the zero calibration.
3. **Verify the signs physically.** Lift one side and watch which way roll moves.

On this trailer: **left-low = negative roll, nose-down = negative pitch.**

Getting this wrong does not produce a small error — it produces a runaway. The
controller raises the wrong side until it hits a limit.

> Do not build a runtime polarity auto-detector. It was tried here, and it
> failed twice: once by writing a learned-wrong value to flash that survived
> reboots, and once by having a "getting worse" threshold (0.25°/burst) coarser
> than the drift it was meant to detect (~0.2°/burst). Determine the sign once,
> by hand, and hard-code it.

Calibration offsets persist across reboots. **Recalibrate after a flash.**

---

## Diesel fuel

The Vevor heater reports cumulative litres consumed but has no tank sensor. So
the tank is virtual: enter how many litres you put in, press **Set Level**, and
the system snapshots the heater's running total. Remaining is then

```
entered_litres − (total_now − snapshot)
```

which handles partial fills correctly. Setting the level asks for confirmation,
because doing it at the wrong moment re-baselines the gauge against reality.
