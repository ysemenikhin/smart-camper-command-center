# 15 — Troubleshooting

Problems that actually happened on this build, grouped by where they show up.
Each one links to the doc that explains it in full.

## Home Assistant and templates

| Symptom | Likely cause | Fix |
|---|---|---|
| Entity is `unknown`, template looks right | You referenced a `unique_id`, not an `entity_id`. The entity id comes from `name:`. | Check the id in Developer Tools → States. See [03](03-integrations.md#entity-naming). |
| A rating shows a confident "Poor" or a gauge shows 0 % | A missing value went through `\| float(0)` and became a real-looking zero. | Use an `availability:` guard so the entity goes **unavailable** instead. See [11 — Safety](11-safety.md). |
| Sensor "no longer provided by the template integration" | A structural YAML error, often a stray `- binary_sensor:` in the middle of a list that silently redefines sensors. | Parse the file (yamllint, or the HA config check) before restarting. |
| Two numbers that should agree do not (load vs discharge) | They come from different entities with different update rates and sign conventions. | Suspect the sourcing before the hardware. See [07 — Energy](07-energy.md#a-trap-charge-and-discharge-disagreeing). |
| Database grows fast, backups slow | Sensors that publish raw floats write a new row on every update. | Round them (`round:` in ESPHome, or in the template). See [07](07-energy.md#database-churn) and [05](05-relay-board.md#analogue-inputs--filtering). |

## Dashboard

| Symptom | Likely cause | Fix |
|---|---|---|
| Tile renders but does nothing when tapped | `custom:button-card` does not template the `service:` field. | Use a literal service and a templated `entity_id`. See [03](03-integrations.md#custom-cards-two-traps-worth-knowing). |
| Icon missing on a short, wide tile | `size:` is a % of card **width**; `#img-cell` is `overflow: hidden` and can compute to 0 px. | Size `img_cell` and `icon` explicitly. See [03](03-integrations.md#custom-cards-two-traps-worth-knowing). |
| "Duplicate mapping key" when saving the dashboard | Two `icon:` or `styles:` keys in one card. | Merge them into one. |
| Dashboard does not render at all | `button-card` or `card-mod` is missing. | Install both from HACS. See [03](03-integrations.md#hacs-frontend-custom-cards). |
| Layout looks wrong on the tablet | It was tuned against a browser window, not the device. | Measure the tablet's real viewport. See [12](12-installation.md#10-adapt-the-dashboard-to-your-screen). |

## Water tanks

| Symptom | Likely cause | Fix |
|---|---|---|
| Tank levels go **unavailable** overnight | Expected: the gauges relay (RE14) is off from 00:00 to 07:00 by the board's schedule, and the senders are only powered with it. | Press B14 to switch the gauges on. See [05](05-relay-board.md#gauges-relay-and-the-unavailable-not-zero-rule). |
| Tank reads 0 % instead of unavailable | Missing `availability:` guard, or a `\| float(0)` swallowing the absence. | Add the guard. |
| Level is wrong at the top or bottom of the tank | Calibration taken in the wrong units, or before the reading settled. | Calibrate in board-read millivolts and wait for it to settle. See [10 — Calibration](10-calibration.md#water-tank-senders). |

## Energy

| Symptom | Likely cause | Fix |
|---|---|---|
| All BMS entities unavailable, "BMS is stale / communication timed out" | A BMS integration update broke the connection. Version 2.14.0 did exactly this. | Roll back to the last version that worked; test updates before trusting them. See [03](03-integrations.md#hacs-integrations). |
| Random Raspberry Pi reboots that look like software faults | Undervoltage on the long 12 V run to the Pi. | Watch the RPi Power warning; fix the supply, not the software. |

## Air suspension

| Symptom | Likely cause | Fix |
|---|---|---|
| Auto-level makes it worse, or runs to a limit | The IMU sign or axis is wrong for how the board is mounted. | Check IMU orientation before trusting any levelling. See [04](04-air-suspension.md#the-sign-error--worth-reading-before-you-trust-your-own-imu) and [10](10-calibration.md#imu-orientation). |
| Heights jump around while parked | Height sensors not calibrated, or compressor vibration. | See [04](04-air-suspension.md#compressor-vibration) and [10](10-calibration.md#suspension-corner-heights). |
| Settings cannot be changed | They are locked by design; the lock relocks after 5 minutes. | Tap the lock bar and confirm. See [09](09-dashboard.md#6-suspension--air-ride-levelling-and-settings). |

## Relay board and ESPHome

| Symptom | Likely cause | Fix |
|---|---|---|
| OTA fails with "the device did not offer encryption; refusing to send the image in plaintext" | The firmware running on the board does not offer OTA encryption yet. | Check the boot log for "Encryption: offered" first; until it appears, flash a non-encrypted build or flash over USB. Notes at the `ota:` block of [`esphome/relay-board.yaml`](../esphome/relay-board.yaml). |
| OTA refused after the API key was lost | Encrypted OTA is a one-way door: without the key there is no OTA way back. | Flash over USB serial with a new key in `secrets.yaml`. |
| Stabilisers relay is off after a reboot | By design: RE15 is always off at boot and DI15 is locked out for 10 s. | Switch it on again. See [05](05-relay-board.md#relay-15--stabilisers-with-a-real-timer). |

## Connectivity

| Symptom | Likely cause | Fix |
|---|---|---|
| Signal dial shows "No Data" with band WCDMA | On 3G this router publishes no signal metrics at all; the link still works. | Nothing is broken. The cellwatch script pulls the modem back to LTE. See [08](08-connectivity-cameras.md#the-3g-gap) and [13](13-router-scripts.md#3g-watchdog-cellwatch). |
| Spoken announcements arrive up to a minute late | Without Browser Mod they go through Android push to the Companion app. | Install Browser Mod for immediate local speech. See [03](03-integrations.md#spoken-announcements). |
