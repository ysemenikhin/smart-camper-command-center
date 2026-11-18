"""Seed a demo Home Assistant with realistic Smart Camper states (render only)."""
import json, sys, urllib.request, datetime as dt

B = "http://localhost:8123"
TOK = open(sys.argv[1]).read().strip()
PROFILE = sys.argv[2] if len(sys.argv) > 2 else "day"

def post(eid, state, **attr):
    req = urllib.request.Request(f"{B}/api/states/{eid}", method="POST",
        data=json.dumps({"state": str(state), "attributes": attr}).encode(),
        headers={"Authorization": f"Bearer {TOK}", "Content-Type": "application/json"})
    urllib.request.urlopen(req).read()

def call(domain, service, data):
    req = urllib.request.Request(f"{B}/api/services/{domain}/{service}", method="POST",
        data=json.dumps(data).encode(),
        headers={"Authorization": f"Bearer {TOK}", "Content-Type": "application/json"})
    urllib.request.urlopen(req).read()

def s(eid, v, unit=None, name=None, dc=None, sc="measurement", **kw):
    a = dict(kw)
    if unit: a["unit_of_measurement"] = unit
    if name: a["friendly_name"] = name
    if dc: a["device_class"] = dc
    if unit and sc: a["state_class"] = sc
    post(eid, v, **a)

now = dt.datetime(2026, 11, 7, 12, 40, tzinfo=dt.timezone.utc)
unlocked = PROFILE == "unlocked"
alert = PROFILE == "alert"

# ---------------- Weather ----------------
fc = [{"datetime": (now + dt.timedelta(hours=h)).isoformat(), "condition": c, "temperature": t}
      for h, c, t in [(1, "sunny", 14), (2, "sunny", 15), (3, "partlycloudy", 15),
                      (4, "partlycloudy", 13), (5, "cloudy", 11), (6, "clear-night", 8)]]
post("weather.forecast_home", "sunny", friendly_name="Forecast Home", temperature=14,
     temperature_unit="°C", humidity=52, wind_speed=9, wind_speed_unit="km/h")
post("sensor.camper_weather", "sunny", friendly_name="Camper Weather", temp=14, mode="hourly", forecast=fc)
post("input_boolean.camper_weather_hourly", "on", friendly_name="Weather Hourly")

# ---------------- Energy ----------------
for i, (soc, v, a, w, e, t) in enumerate([(78, 13.31, 9.8, 130, 4720, 17.4),
                                          (77, 13.30, 9.4, 125, 4660, 17.1)], 1):
    s(f"sensor.battery_{i}_battery", soc, "%", f"Battery {i} Battery", "battery")
    s(f"sensor.battery_{i}_voltage", v, "V", f"Battery {i} Voltage", "voltage")
    s(f"sensor.battery_{i}_current", a, "A", f"Battery {i} Current", "current")
    s(f"sensor.battery_{i}_power", w, "W", f"Battery {i} Power", "power")
    s(f"sensor.battery_{i}_stored_energy", e, "Wh", f"Battery {i} Stored Energy", "energy_storage")
    s(f"sensor.battery_{i}_temperature", t, "°C", f"Battery {i} Temperature", "temperature")
    post(f"binary_sensor.battery_{i}_problem", "off", friendly_name=f"Battery {i} Problem", device_class="problem")
s("sensor.camper_battery_soc", 77.5, "%", "Camper Battery SOC", "battery")
s("sensor.camper_battery_voltage", 13.31, "V", "Camper Battery Voltage", "voltage")
s("sensor.camper_battery_power", 255, "W", "Camper Battery Power", "power")
s("sensor.camper_stored_energy", 9380, "Wh", "Camper Stored Energy", "energy_storage")
post("sensor.camper_charge_state", "Charging", friendly_name="Camper Charge State")
post("sensor.camper_charge_display", "Charging 19.2A 255W", friendly_name="Camper Charge Display", icon="mdi:battery-charging")
s("sensor.camper_load_current", 6.4, "A", "Camper Load Current", "current")
s("sensor.camper_load_power", 85, "W", "Camper Load Power", "power")
post("sensor.camper_runtime_display", "4h to full", friendly_name="Camper Runtime Display")
s("sensor.mppt_1_440w_current_solar_watts", 118, "W", "MPPT 1 440W Current Solar Watts", "power")
s("sensor.mppt_2_880w_current_solar_watts", 236, "W", "MPPT 2 880W Current Solar Watts", "power")
s("sensor.mppt_1_440w_aux_battery_charging_ampers", 8.6, "A", "MPPT 1 Charging", "current")
s("sensor.mppt_2_880w_aux_battery_charging_ampers", 17.0, "A", "MPPT 2 Charging", "current")
s("sensor.camper_solar_power", 354, "W", "Camper Solar Power", "power")
s("sensor.camper_solar_today", 1.84, "kWh", "Camper Solar Today", "energy", "total_increasing")
s("sensor.energy_production_today_remaining", 0.9, "kWh", "Energy Production Today Remaining", "energy")
s("sensor.energy_production_tomorrow", 3.1, "kWh", "Energy Production Tomorrow", "energy")

# ---------------- Water ----------------
s("sensor.clear_water_tank", 62, "%", "Clear Water Tank")
s("sensor.gray_water_tank", 23, "%", "Gray Water Tank")
s("sensor.clear_water_litres", 174, "L", "Clear Water Litres")
s("sensor.gray_water_litres", 22, "L", "Gray Water Litres")
for eid, v, n in [("clean_water_tank_temp", 11.8, "Clean Water Tank Temp"), ("grey_water_tank_temp", 10.9, "Grey Water Tank Temp"),
                  ("water_pipe_1_temp", 9.6, "Water Pipe 1 Temp"), ("water_pipe_2_temp", 8.7, "Water Pipe 2 Temp")]:
    s(f"sensor.relay_board_{eid}", v, "°C", n, "temperature")

# ---------------- Relay board ----------------
relays = {"main_light": ("on", "Main Light"), "outdoor_left": ("off", "Outdoor Left"), "bedroom_light": ("off", "Bedroom Light"),
          "front_outdoor": ("on", "Front Outdoor"), "main_bedroom_red": ("on", "Main Bedroom Red"),
          "outdoor_right": ("off", "Outdoor Right"), "fan": ("off", "Fan"), "awning_red_left": ("on", "Awning Red Left"),
          "water_pump": ("on", "Water Pump"), "awning_red_right": ("on", "Awning Red Right"), "inverter": ("off", "Inverter"),
          "steps": ("on", "Steps"), "water_gauges": ("on", "Water Gauges"), "stabilisers": ("off", "Stabilisers"),
          "tank_pipe_heater": ("off", "Tank & Pipe Heater")}
for k, (st, n) in relays.items():
    post(f"switch.relay_board_{k}", st, friendly_name=n)
for k, st in [("all_on", "off"), ("exterior_on", "off"), ("night_mode", "off"), ("stealth", "off")]:
    post(f"binary_sensor.camper_scene_{k}", st, friendly_name=f"Camper Scene {k}")
for sc in ["all_lights_on", "all_lights_toggle", "front_flash", "heater_set_mode", "police_lights",
           "police_toggle", "set_fuel_level", "set_gear"]:
    post(f"script.camper_{sc}", "off", friendly_name=sc.replace("_", " ").title())

# ---------------- Climate / diesel heater ----------------
post("climate.diesel_heater", "heat", friendly_name="Diesel Heater", hvac_modes=["off", "heat", "fan_only"],
     current_temperature=19.5, temperature=21, min_temp=8, max_temp=36, target_temp_step=1, supported_features=385)
post("switch.diesel_heater_power", "on", friendly_name="Diesel Heater Power")
post("switch.diesel_heater_auto_start_stop", "off", friendly_name="Auto Start/Stop")
post("switch.diesel_heater_timer", "off", friendly_name="Timer")
post("select.diesel_heater_running_mode", "Temperature", friendly_name="Running Mode", options=["Temperature", "Level"])
post("number.diesel_heater_level", 4, friendly_name="Level", min=1, max=10, step=1)
post("input_number.camper_pending_gear", 0, friendly_name="Pending Gear", min=0, max=10, step=1)
post("sensor.diesel_heater_running_step", "Running", friendly_name="Heater State")
post("binary_sensor.diesel_heater_active", "on", friendly_name="Burner", device_class="running")
post("binary_sensor.diesel_heater_connected", "on", friendly_name="Heater Connected", device_class="connectivity")
post("binary_sensor.diesel_heater_problem", "off", friendly_name="Heater Problem", device_class="problem")
post("sensor.diesel_heater_error", "No error", friendly_name="Heater Error")
s("sensor.diesel_heater_interior_temperature", 19.5, "°C", "Interior Temperature", "temperature")
s("sensor.diesel_heater_case_temperature", 112, "°C", "Heat Exchanger", "temperature")
s("sensor.diesel_heater_supply_voltage", 13.2, "V", "Heater Supply", "voltage")
s("sensor.diesel_heater_altitude", 1180, "m", "Elevation", "distance")
s("sensor.diesel_heater_daily_runtime", 3.4, "h", "Runtime Today", "duration")
s("sensor.diesel_heater_total_runtime", 412, "h", "Total Runtime", "duration", "total_increasing")
s("sensor.diesel_heater_estimated_daily_fuel_consumed", 0.71, "L", "Used Today")
s("sensor.diesel_heater_estimated_hourly_fuel_consumption", 0.21, "L/h", "Burn Rate")
s("sensor.diesel_heater_estimated_fuel_since_refuel", 2.4, "L", "Fuel Since Refuel")
s("sensor.camper_fuel_remaining", 7.6, "L", "Camper Fuel Remaining")
s("sensor.camper_fuel_remaining_percent", 76, "%", "Camper Fuel Remaining Percent")
s("sensor.camper_heat_hours_left", 36.2, "h", "Camper Heat Hours Left")
post("sensor.camper_heat_time_left", "1d 12h", friendly_name="Camper Heat Time Left")
post("input_select.camper_fuel_tank_capacity", "10 L", friendly_name="Fuel Tank Capacity",
     options=["5 L", "8 L", "10 L", "12 L", "15 L", "20 L", "25 L", "30 L"])
post("input_select.camper_fuel_level", "10.0 L", friendly_name="Litres In Tank Now",
     options=[f"{x/2:.1f} L" for x in range(0, 21)])

# ---------------- Suspension ----------------
P = "camper_air_suspension"
for c, psi, h, n in [("front_left", 41, 48, "Front Left"), ("front_right", 40, 47, "Front Right"),
                     ("rear_left", 43, 46, "Rear Left"), ("rear_right", 42, 47, "Rear Right")]:
    s(f"sensor.{P}_{c}", psi, "psi", n)
for c, h in [("fl", 48), ("fr", 47), ("rl", 46), ("rr", 47)]:
    s(f"sensor.{P}_height_{c}", h, "%", f"Height {c.upper()}")
s(f"sensor.{P}_air_tank", 132, "psi", "Air Tank")
s(f"sensor.{P}_roll", 0.2, "°", "Roll")
s(f"sensor.{P}_pitch", -0.1, "°", "Pitch")
post(f"sensor.{P}_preset_status", "Reached Highway Normal Load", friendly_name="Preset Status")
post(f"sensor.{P}_front_jack_advice", "Not needed", friendly_name="Front Jack Advice")
post(f"select.{P}_gear", "Highway Normal Load", friendly_name="Gear",
     options=["Highway Normal Load", "Highway Heavy Load", "Off-Road", "Parked", "Easy Maneuver"])
for sw, st in [("air_manifold", "on"), ("load_sharing_off_road_articulation", "off"), ("manifold_ble_link", "on"),
               ("preset_auto_maintain", "on"), ("preset_mode_psi", "off")]:
    post(f"switch.{P}_{sw}", st, friendly_name=sw.replace("_", " ").title())
for b, st in [("articulation_settling", "off"), ("compressor_running", "off"), ("manifold_connected", "on")]:
    post(f"binary_sensor.{P}_{b}", st, friendly_name=b.replace("_", " ").title())
post("binary_sensor.compressor_running", "off", friendly_name="Compressor Running")
for b in ["all_lower", "all_raise", "auto_level", "front_axle_lower", "front_axle_raise", "front_left_lower",
          "front_left_raise", "front_right_lower", "front_right_raise", "full_dump_0_psi", "left_side_lower",
          "left_side_raise", "rear_axle_lower", "rear_axle_raise", "rear_left_lower", "rear_left_raise",
          "rear_right_lower", "rear_right_raise", "right_side_lower", "right_side_raise", "stop_preset"]:
    post(f"button.{P}_{b}", "unknown", friendly_name=b.replace("_", " ").title())
presets = {"parked": (20, 20, 25, 25), "highway_normal": (45, 45, 40, 40), "highway_heavy": (50, 50, 45, 45),
           "off_road": (75, 75, 55, 55), "easy_maneuver": (30, 30, 55, 20)}
for k, (fh, rh, fp, rp) in presets.items():
    for ax, hv, pv in [("front", fh, fp), ("rear", rh, rp)]:
        post(f"number.{P}_{k}_{ax}_height", hv, friendly_name=f"{k} {ax} height", min=0, max=100, step=1, unit_of_measurement="%", mode="box")
        post(f"number.{P}_{k}_{ax}_psi", pv, friendly_name=f"{k} {ax} psi", min=0, max=90, step=1, unit_of_measurement="psi", mode="box")
for k, v, mn, mx, u in [("emergency_cap_psi", 95, 30, 100, "psi"), ("level_threshold", 0.3, 0, 0.5, "°"),
                        ("max_corner_psi", 75, 30, 90, "psi"), ("min_corner_psi", 20, 0, 40, "psi"),
                        ("preset_height_deadband", 2, 0, 8, "%"), ("preset_psi_deadband", 3, 0, 10, "psi")]:
    post(f"number.{P}_{k}", v, friendly_name=k.replace("_", " ").title(), min=mn, max=mx, step=1 if mx > 1 else 0.05,
         unit_of_measurement=u, mode="slider")
for k, v, u in [("suspension_roll", 0.3, "°"), ("road_cross_slope", -0.1, "°"), ("max_roll_authority", 4.2, "°"),
                ("chassis_twist", 0.1, "°"), ("suspension_pitch", 0.4, "°"), ("road_pitch_slope", -0.5, "°"),
                ("max_pitch_authority", 8.3, "°")]:
    s(f"sensor.air_suspension_{k}", v, u, k.replace("_", " ").title())
post("sensor.camper_suspension_stance", "Ride Height", friendly_name="Camper Suspension Stance")
post("sensor.camper_suspension_balance", "Balanced", friendly_name="Camper Suspension Balance")
post("input_number.camper_balance_threshold", 3, friendly_name="Balance Threshold", min=0, max=10, step=0.5)
post("input_boolean.camper_settings_unlock", "on" if unlocked else "off", friendly_name="Suspension Settings Unlocked")
post("sensor.camper_settings_unlock_countdown", "2:47" if unlocked else "LOCKED", friendly_name="Camper Settings Unlock Countdown")

# ---------------- Connectivity ----------------
post("binary_sensor.camper_internet", "on", friendly_name="Camper Internet", device_class="connectivity")
post("sensor.camper_wan_mode", "Cellular · CARRIER · 5G", friendly_name="Camper WAN Mode")
post("sensor.camper_wan_type", "cellular", friendly_name="Camper WAN Type")
post("sensor.camper_wan_ip", "203.0.113.24", friendly_name="Camper WAN IP")
s("sensor.camper_cell_signal", 71, "%", "Camper Cell Signal")
post("sensor.camper_cell_rating", "Good", friendly_name="Camper Cell Rating")
s("sensor.camper_wan_down", 4.812, "Mbps", "Camper WAN Down"); s("sensor.camper_wan_down_mbps", 4.812, "Mbps")
s("sensor.camper_wan_up", 0.734, "Mbps", "Camper WAN Up")
post("sensor.gl_inet_x3000_cellular_band", "NR5G-NSA n78", friendly_name="Cell Band")
post("sensor.gl_inet_x3000_cellular_network", "CARRIER", friendly_name="Provider")
s("sensor.gl_inet_x3000_cellular_rsrp", -89, "dBm", "RSRP", "signal_strength")
s("sensor.gl_inet_x3000_wan_download_rate", 601500, "B/s", "Download", "data_rate")
s("sensor.gl_inet_x3000_wan_upload_rate", 91750, "B/s", "Upload", "data_rate")
post("binary_sensor.gl_inet_x3000_repeater_connected", "off", friendly_name="Repeater Connected")
post("select.gl_inet_x3000_wifi_network", "-- select network --", friendly_name="Wi-Fi Network", options=["-- select network --"])
post("switch.gl_inet_x3000_repeater_auto_switch_networks", "on", friendly_name="Auto-Switch")
post("switch.gl_inet_x3000_system_led", "off", friendly_name="Router LED")
post("button.gl_inet_x3000_disconnect_repeater", "unknown", friendly_name="Disconnect Repeater")
post("button.gl_inet_x3000_scan_wifi_networks", "unknown", friendly_name="Scan Wi-Fi")
s("sensor.speedtest_download", 86.4, "Mbit/s", "Download", "data_rate")
s("sensor.speedtest_upload", 21.7, "Mbit/s", "Upload", "data_rate")
s("sensor.speedtest_ping", 41, "ms", "Ping", "duration")
post("binary_sensor.starlink_connectivity", "off", friendly_name="Starlink", device_class="connectivity")
post("binary_sensor.starlink_obstructed", "off", friendly_name="Sky View", device_class="problem")

# ---------------- Alerts ----------------
lines = ["🟠 **GREY TANK NEARLY FULL** — 91%  ·  *Water tab*"] if alert else []
post("sensor.camper_alert_summary", len(lines), friendly_name="Camper Alert Summary", lines=lines)
post("binary_sensor.camper_any_alert", "on" if lines else "off", friendly_name="Camper Any Alert", device_class="problem")

call("frontend", "set_theme", {"name": "garmin_dark", "mode": "dark"})
call("frontend", "set_theme", {"name": "garmin_dark"})
print("seeded", PROFILE)
