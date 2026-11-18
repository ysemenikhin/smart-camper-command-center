# Rendering the documentation screenshots

The images in `docs/images/` are produced from this repository's code, not
photographed off the trailer. Anyone can regenerate them:

1. **Install HA in a venv.**
   ```sh
   uv venv venv && uv pip install -p venv/bin/python homeassistant home-assistant-frontend \
       hassil home-assistant-intents ha-ffmpeg
   ```
2. **Build the config folder.**
   ```sh
   mkdir -p config/themes config/www/community
   cp configuration.yaml config/
   cp ../../homeassistant/themes/garmin_dark.yaml config/themes/
   cp ../../homeassistant/dashboards/smart-camper-dashboard.yaml config/ui-lovelace.yaml
   ```
3. **Add the custom cards.** Put `button-card.js`, `card-mod.js` and
   `apexcharts-card.js` from their GitHub releases into `config/www/community/`.
4. **Add the placeholder images.**
   - Cameras: five JPEGs in `config/www/cams/`, added as **Local File** camera
     entities named `left_cam_sub_stream`, `right_cam_sub_stream`,
     `rear_cam_sub_stream`, `front_cam_sub_stream` and `internal_tablet_cam`.
   - Wi-Fi QR: put a demo QR at `config/www/wifi-qr.png`. The dashboard's Wi-Fi
     tile points at `/local/wifi-qr.png`; on the real system that is your own
     network's QR.
5. **Start HA and onboard a user.**
   ```sh
   venv/bin/hass -c config
   ```
   Onboard a user `demo` / `demo-render-only`, and save a long-lived token to
   `token.txt`.
6. **Seed the demo states.** `python3 seed.py token.txt day`. The profiles are:
   - `day`: normal running.
   - `unlocked`: suspension settings unlocked mid-countdown.
   - `alert`: one alert active on the strip.
7. **Shoot.**
   ```sh
   python3 shoot.py out home,energy,...,connectivity "" --full
   ```
   This captures 1340 × 800 at 2× device scale, so the PNGs are 2680 px wide.

The 24 h charts on the Energy tab need history. Write a day of synthetic states
into the recorder database before taking that shot.
