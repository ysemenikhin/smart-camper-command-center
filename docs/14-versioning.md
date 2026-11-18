# 14 — Versioning and release process

Every configuration file is versioned on its own. The version is in the file
header, and each version has one changelog line saying what changed and why.
Git records the same history: **one commit per version, with that changelog
entry as the commit message, and an annotated tag per release.**

## Components and tags

| Component | File | Tag pattern | Range in this repo |
|---|---|---|---|
| Dashboard | `homeassistant/dashboards/smart-camper-dashboard.yaml` | `dashboard-vN` | v196 – v206 |
| HA package | `homeassistant/packages/camper.yaml` | `package-vN` | v57 – v58 |
| Relay board ESP | `esphome/relay-board.yaml` | `relay-board-vX.Y.Z` | v2.0.2, v2.3.1 – v2.3.8 |
| Air suspension ESP | `esphome/air-suspension-s3.yaml` | `air-suspension-vX.Y.Z` | v5.0.8 |
| Light effects | `homeassistant/packages/camper_light_effects.yaml` | `light-effects-vN` | v1 – v2 |
| GPS | `homeassistant/packages/camper_gps.yaml` + `router/…/camper-gps*` | `gps-vN` | v1 |
| 3G watchdog | `router/…/camper-cellwatch*` | `cellwatch-vN` | v1 |
| Voice | `homeassistant/packages/camper_voice.yaml` | `voice-vN` | v4 |
| Theme | `homeassistant/themes/garmin_dark.yaml` | `theme-vX.Y` | v4.0 |

Older versions are not kept as separate files. Retrieve any of them from git:

```sh
git tag -l 'dashboard-*'                                  # list releases
git show dashboard-v201:homeassistant/dashboards/smart-camper-dashboard.yaml
git diff relay-board-v2.3.5 relay-board-v2.3.6 -- esphome/relay-board.yaml
```

The commits carry the dates the versions were actually produced. Earlier
versions exist (dashboard from v1, package from v1, suspension firmware from
v1.0.0); they are summarised in each file's changelog header but are not in git.

## Rules

1. **One change per version.** Confirm it works on the trailer before the next.
2. **Bump the version and write the changelog line in the same edit.**
3. **Build each change on the last *confirmed-working* version,** not on the last
   one written.
4. **Firmware shows its version in HA** as a `Config Version` diagnostic sensor
   (`substitutions: config_version` / `config_date`), so the running build can
   be checked from the dashboard.
5. **Secrets never enter git.** They live in `esphome/secrets.yaml`, which is
   gitignored. `secrets.yaml.example` lists every key.

## Branching

`main` is always the deployed state. A change goes on a short-lived branch named
after the component and version, e.g. `relay-board/v2.3.9`, and merges with a
pull request once it is confirmed on the hardware. After the merge it is tagged.

```sh
git switch -c relay-board/v2.3.9
# edit, bump header + changelog, flash, verify on the trailer
git commit -am "relay-board v2.3.9: <changelog line>"
git switch main && git merge --no-ff relay-board/v2.3.9
git tag -a relay-board-v2.3.9 -m "relay-board v2.3.9: <changelog line>"
git push --follow-tags
```

## CI

`.github/workflows/ci.yml` runs on every push and pull request:

- **gitleaks** scans for secrets across the whole history.
- **yamllint** checks syntax, using a relaxed profile because HA and ESPHome use
  custom tags such as `!secret` and `!include`.
- A **placeholder check** fails the build if a real-looking MAC address, private
  IP or API key appears in a tracked file.
