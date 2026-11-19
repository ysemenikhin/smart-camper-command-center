# 01 — Architecture

## The shape of the system

Home Assistant is the brain. Two ESP32 boards are the hands. Nothing
safety-critical depends on a cloud service, and the trailer stays controllable
when there is no internet, no phone signal and no external network at all.

```mermaid
graph TB
    subgraph Trailer["EXPEDITION TRAILER"]
        subgraph Brain["Raspberry Pi 4 — Home Assistant OS"]
            HA["Home Assistant<br/>packages · automations · dashboard"]
            MQTT["Mosquitto"]
            G2R["go2rtc<br/>camera restreaming"]
        end

        subgraph Boards["ESP32 boards — ESPHome"]
            SUS["Air Suspension<br/>ESP32-S3-N16R8<br/>IMU · BLE · 2 relays"]
            REL["Relay Board<br/>KinCony KC868-A16S<br/>16 relays · 2 ADC · RF433 · RTC"]
        end

        subgraph Pneu["Pneumatics"]
            MAN["DN-3G manifold<br/>+ ECU (BLE)"]
            BAGS["4 air bags<br/>FL · FR · RL · RR"]
            TANK["Air tank<br/>110 psi cut-in / 150 cut-out"]
        end

        subgraph Power["Energy"]
            BMS["2× LiFePO₄ banks<br/>BLE BMS"]
            MPPT["2× Renogy MPPT<br/>440 W + 880 W"]
            SHUNT["920 Ah shunt"]
        end

        subgraph Net["Connectivity"]
            RTR["GL.iNet X3000<br/>cellular · repeater"]
            STAR["Starlink"]
        end

        CAMS["4 exterior cameras<br/>+ 1 interior"]
        TABLET["10in wall tablet<br/>Lenovo TB311FU"]
    end

    HA <-->|"native API<br/>encrypted"| SUS
    HA <-->|"native API<br/>encrypted"| REL
    SUS <-->|BLE| MAN
    MAN --> BAGS
    TANK --> MAN
    HA <-->|BLE| BMS
    HA <--> MPPT
    HA <--> SHUNT
    HA <--> RTR
    HA <--> STAR
    CAMS --> G2R --> HA
    HA --> TABLET
    SUS -->|"relay: manifold ignition"| MAN
    SUS -->|"relay: articulation valves"| BAGS

    style HA fill:#1c242c,stroke:#e8a33d,color:#e8edf2
    style SUS fill:#1c242c,stroke:#3aa6dd,color:#e8edf2
    style REL fill:#1c242c,stroke:#3aa6dd,color:#e8edf2
```

## Where each decision is made

This matters more than the wiring. Putting a decision in the wrong place is how
you get a system that misbehaves when the network hiccups.

| Decision | Lives in | Why there |
|---|---|---|
| Should this relay be on? | **Relay board firmware** | A physical button must work with HA switched off entirely |
| Has the stabiliser circuit been on too long? | **Relay board firmware** | A 10-minute cut-off that depends on the network is not a safety timer |
| Is this corner at its target pressure? | **Suspension firmware** | Closed-loop control at 10 Hz cannot survive network latency |
| Which way is "level"? | **Suspension firmware** | IMU fusion needs to run beside the sensor |
| Which drive mode are we in? | **Suspension firmware** | Targets must survive an HA restart |
| Is the battery low? | **Home Assistant** | Needs data from three sources the boards cannot see |
| Should the gauges be on right now? | **Home Assistant** (schedule) | Convenience, not safety |
| What does the driver see? | **Home Assistant** (dashboard) | Presentation only — never control logic |

**The rule:** anything that must still work with the Pi unplugged goes in
firmware. Everything else goes in Home Assistant.

## Control flow — a levelling run

```mermaid
sequenceDiagram
    participant U as User (tablet)
    participant HA as Home Assistant
    participant ESP as Suspension ESP32-S3
    participant IMU as IMU (BMI160)
    participant M as DN-3G manifold

    U->>HA: Tap "Auto Level"
    HA->>U: Confirmation dialog
    U->>HA: Confirm
    HA->>ESP: switch.turn_on auto_level
    ESP->>M: Close articulation valves
    ESP->>M: Dump all four corners to floor
    loop Until roll within threshold
        ESP->>IMU: Read roll
        ESP->>M: Let the HIGH side down
    end
    loop Until pitch within threshold
        ESP->>IMU: Read pitch
        ESP->>M: Raise or lower the REAR
    end
    ESP->>HA: preset_status = "Levelled"
    HA->>U: Tile turns green, spoken announcement
    Note over ESP: If a correction is impossible<br/>(nose needs lowering past the floor)<br/>it announces and stops rather than fighting
```

## Failure behaviour

The system is built to degrade, not collapse.

| What fails | What happens |
|---|---|
| Home Assistant down | Both boards keep running. Physical buttons still switch every relay. Suspension holds its last mode. |
| Network down | Boards raise their own AP. Suspension board's RGB LED goes red. |
| Manifold BLE drops | Suspension reports disconnected; dashboard raises an alert; a power-cycle watchdog is planned via the ignition relay |
| One BMS bank drops | All battery figures switch to the shunt as a coherent set — never a mix of two sources |
| Tank gauges relay off | Tank sensors go **unavailable**, not 0% — a missing reading must never render as a real one |
| A height sensor fails | Suspension latches to PSI-target mode and says so with a banner |
| Cellular drops to 3G | Signal strength reads "No Data" — the router publishes no metric on 3G |

That last column is the design philosophy in miniature: **missing data is shown
as missing.** Several bugs in this project's history were caused by a
`| float(0)` turning an absent reading into a confident zero.

## Next

- [02 — Hardware & BOM](../hardware/bom.md)
- [04 — Air suspension](04-air-suspension.md) for the levelling algorithm in detail
