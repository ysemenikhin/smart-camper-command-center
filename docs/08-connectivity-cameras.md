# 08 — Connectivity & cameras

## WAN

A GL.iNet X3000 handles cellular and can repeat an external Wi-Fi network
(campsite, or Starlink). Home Assistant reports which one is actually carrying
traffic.

| WAN mode | Shown as |
|---|---|
| Cellular | `Cellular · CARRIER` (the live network name) |
| Repeating Starlink | `Repeater · Starlink` |
| Repeating other Wi-Fi | `Repeater · <SSID>` |
| Neither | `Offline` |

"Internet" is a separate thing from "WAN up": it is a **ping to 1.1.1.1**. A
router can hold a perfectly healthy cellular link to a network that is not
passing traffic, and only an end-to-end test catches that.

## Cellular signal — and why it sometimes cannot be shown

Signal strength is computed from the two measures that actually mean something
on LTE/5G:

- **RSRP** −110…−75 dBm → 0…100% (reference signal power)
- **SINR** −5…+20 dB → 0…100% (signal quality)
- Weighted **70/30 toward RSRP** — you need power first, then a clean signal

RSSI is deliberately **not** used as the primary measure: it lumps in noise and
interference and reads optimistic. An earlier version scaled RSSI as
`(RSSI+100)/40`, which maps −60 dBm to 100% and pinned the gauge at 105% on a
measured −58 dBm.

> **An earlier version also showed Wi-Fi strength on a tile labelled "Cell
> Signal"** whenever the repeater was connected. A −89 dBm Wi-Fi uplink made the
> whole tab read "Poor" while cellular was fine. The repeater link now has its
> own separate sensor. If a tile is labelled cellular, it shows cellular.

### The 3G gap

When the modem falls back to **WCDMA**, this router publishes **no signal metric
at all** — RSRP, RSRQ, SINR *and* RSSI all go `unknown` simultaneously, while the
link itself stays up and passes traffic.

There is no number to display, so the rating reads **"No Data"** and the dial
shows the band instead of a dBm figure. It does not read "Poor", because a
missing measurement is not a weak signal. Verified against 24 hours of history:
the metrics vanish at the exact moment the band changes from NR5G-NSA to WCDMA.

Locking the modem to LTE/5G would lose the 3G fallback where only 3G exists, so
the network mode stays on **AUTO**. A router-side watchdog (`camper-cellwatch`)
pulls the modem back to LTE when it gets stuck on 3G. See
[13 — Router scripts](13-router-scripts.md).

## Throughput

Download and upload read the router's **raw bytes-per-second** entities and
format them in the card, auto-scaling between kbps and Mbps.

> This is not the obvious design, and there is a reason. Reading a pre-rounded
> Mbps sensor collapsed 1207 B/s and 1305 B/s both to "10 kbps" — two different
> rates displaying identically. At idle the link sits around 12 kbps, which a
> fixed Mbps scale renders as a useless "0.0". Format at the display, not at the
> source.

## Cameras

Four exterior cameras plus one interior. Each exterior camera is added **twice**:

| Entity | Stream | Used for |
|---|---|---|
| `camera.<name>_sub_stream` | Low-res sub-stream | The live 4-up grid |
| `camera.<name>` | Full-res main stream | Opened on tap |

**This is the whole trick.** Four full-resolution H.264 streams will not decode
simultaneously on a tablet — the grid stutters or drops feeds. Four sub-streams
will. Tapping a tile opens the main stream for the one camera you actually want
to look at.

The RTSP sub-stream is usually the main URL with a stream parameter, e.g.
`...&stream=1...` — check your camera's documentation.

`go2rtc` (built into recent HA) does the restreaming; `stream:` comes via
`default_config`.

### Layout

The Cameras tab is a 2-column grid: Left / Right, then Rear / Front, with the
interior camera below. Each exterior cell carries the light for that view
directly beneath it — press the button while looking at what it lights.

Rear has no light of its own, so that cell carries an **All Lights** toggle
instead, which also keeps all four cells the same height.

Sizing is a genuine trade-off. At 16:9 in a 2-column grid on a 1340 px-wide
tablet, each feed is ~370 px tall and the second row's buttons fall off the
screen. At 20:9 they are ~296 px and everything fits — but the cameras are
natively 16:9, so a wider box letterboxes rather than crops. Pick your
compromise: full frame with scrolling, or no scrolling with dead space.

## GPS

The router's built-in GNSS feeds Home Assistant through a webhook
(`router-scripts/usr/bin/camper-gps.sh` → `packages/camper_gps.yaml`). It provides:

- `device_tracker.camper_gps`;
- speed, heading, altitude and satellite sensors;
- a home location that follows the trailer once it moves more than 2 km, so the
  weather forecast is for where it is parked.

See [13 — Router scripts](13-router-scripts.md).
