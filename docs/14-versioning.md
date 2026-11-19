# 14 — Versioning and release process

Every configuration file is versioned on its own. The version is in the file
header, and each version has one changelog line saying what changed and why.

## Components and tags

| Component | File | Tag pattern | Current |
|---|---|---|---|
| Dashboard | `dashboard/smart-camper-dashboard.yaml` | `dashboard-vN` | v207 |
| HA package | `packages/camper.yaml` | `package-vN` | v58 |
| Relay board ESP | `esphome/relay-board.yaml` | `relay-board-vX.Y.Z` | v2.3.9 |
| Air suspension ESP | `esphome/air-suspension-s3.yaml` | `air-suspension-vX.Y.Z` | v5.0.8 |
| Light effects | `packages/camper_light_effects.yaml` | `light-effects-vN` | v2 |
| GPS | `packages/camper_gps.yaml` + `router-scripts/…/camper-gps*` | `gps-vN` | v1 |
| 3G watchdog | `router-scripts/…/camper-cellwatch*` | `cellwatch-vN` | v1 |
| Voice | `packages/camper_voice.yaml` | `voice-vN` | v4 |
| Theme | `themes/garmin_dark.yaml` | `theme-vX.Y` | v4.0 |

## History

The project was developed in a private repository up to dashboard v206 and
relay board v2.3.8. That repository's commits and tags are **not** part of this
one: the public history starts with an import of the configuration as it stood
on 9 Nov 2026, followed by the public-release changes.

Earlier versions are still described in each file's changelog header and in
[CHANGELOG.md](../CHANGELOG.md). From the public release on, every version is a
tag in this repository:

```sh
git tag -l 'dashboard-*'                                   # list releases
git show relay-board-v2.3.9:esphome/relay-board.yaml       # a file at a release
git diff relay-board-v2.3.9 relay-board-v2.3.10 -- esphome/relay-board.yaml
```

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

## Branching and pull requests

`main` is always the deployed state. Nothing is committed to `main` directly.

1. Branch from the latest `main`, named after the component and version, e.g.
   `relay-board/v2.3.10` (or `docs/<topic>` for documentation).
2. Edit, bump the header version and changelog, add a row to `CHANGELOG.md`.
3. Flash or install it and verify on the trailer.
4. Open a pull request. CI must pass.
5. The owner reviews and merges.

```sh
git switch main && git pull
git switch -c relay-board/v2.3.10
# edit, bump header + changelog, flash, verify on the trailer
git commit -am "fix(relay-board): v2.3.10 <changelog line>"
git push -u origin relay-board/v2.3.10
# then open the pull request on GitHub
```

## Tags and releases

Tags are not pushed by hand. They are listed in
[`.github/release-tags.txt`](../.github/release-tags.txt):

1. In the pull request (or a follow-up one), add the new tag on its own line,
   e.g. `relay-board-v2.3.10`, and its notes in
   `.github/release-notes/relay-board-v2.3.10.md`.
2. After the merge to `main`, the `release-tags` workflow creates every listed
   tag that does not exist yet, as an annotated tag on that commit, and a GitHub
   Release with those notes. Without a notes file, it uses the tag's row in
   `CHANGELOG.md`.

Existing tags are never moved. Never remove or rename a line in the file.

## CI

`.github/workflows/ci.yml` runs on every pull request and on every push to
`main`:

- **gitleaks** scans for secrets across the whole history.
- **yamllint** checks syntax, using a relaxed profile because HA and ESPHome use
  custom tags such as `!secret` and `!include`.
- A **placeholder check** fails the build if a real-looking MAC address, private
  IP or API key appears in a tracked file.
- **ESPHome config validation** runs `esphome config` on both boards, using
  throwaway secrets built from `secrets.yaml.example`.
