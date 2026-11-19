# Contributing

Thanks for wanting to help. This repository is the configuration of one real
expedition trailer, published so others can rebuild or adapt it. Fixes,
clearer docs, notes from your own build and adaptations for other hardware are
all welcome.

Before anything else, read [docs/11-safety.md](docs/11-safety.md). This code
switches 12 V loads and moves a loaded trailer on air bags.

## Ways to contribute

- **Report a bug:** open an issue with the *Bug report* template.
- **Ask a question about your build:** use the *Question* template.
- **Suggest a feature:** use the *Feature request* template.
- **Send a fix or a doc improvement:** open a pull request (see below).
- **Security problem or leaked secret:** do **not** open a public issue; see
  [SECURITY.md](SECURITY.md).

## Ground rules

1. **No secrets, ever.** Wi-Fi credentials, API and OTA keys, MAC addresses,
   sensor addresses, IP addresses, domains, camera URLs and GPS positions stay
   in your own `esphome/secrets.yaml` (gitignored) or your Home Assistant
   config. Use `!secret` and the placeholders in
   [`esphome/secrets.yaml.example`](esphome/secrets.yaml.example). CI fails
   the pull request if it finds a real-looking MAC, private IP or key.
2. **Safety logic stays in firmware.** Timers, boot states and interlocks that
   must work with Home Assistant down belong in the ESPHome config, not in an
   automation.
3. **Label every number.** Calibration values in the docs say whether they were
   *measured*, *derived* or *assumed*. Keep doing that.
4. **One change per version.** See below.

## Versioning

Every configuration file carries its own version in its header, and each
version has one changelog line saying what changed and why. Full rules:
[docs/14-versioning.md](docs/14-versioning.md).

When you change a component file:

- Bump its version in the header and add the changelog line **in the same
  edit**. For the ESPHome boards, also bump `config_version` and `config_date`
  in `substitutions:`.
- Add a row to [CHANGELOG.md](CHANGELOG.md).
- Base the change on the last version that is confirmed working on hardware.

Docs-only changes need no version bump.

## Pull requests

1. Branch from the latest `main`. Name it after the component and version,
   e.g. `relay-board/v2.3.10`, or `docs/<topic>` for documentation.
2. Use [Conventional Commits](https://www.conventionalcommits.org/) for commit
   messages, e.g. `fix(relay-board): ...`, `docs: ...`.
3. Run the checks below locally.
4. Open the pull request and fill in the template. CI must pass.
5. Say how you tested it. For anything that moves air or switches loads,
   "tested on hardware" with what you saw beats "compiles".

The maintainer reviews and merges. Releases are tagged after the merge (see
[docs/14-versioning.md](docs/14-versioning.md#tags-and-releases)).

## Checks to run before pushing

```sh
pip install yamllint esphome

# YAML syntax
yamllint -c .yamllint.yml esphome packages dashboard themes .github

# ESPHome configs, with throwaway secrets
cd esphome
cp secrets.yaml.example secrets.yaml      # then put a real base64 key and a
                                           # non-zero MAC in it for the check
esphome config relay-board.yaml
esphome config air-suspension-s3.yaml
```

`secrets.yaml` is gitignored; never force-add it.

## Screenshots

Screenshots in [`images/`](images/) are from the running trailer with private
details blurred. If you add one, blur Wi-Fi QR codes, IP addresses, network
names and camera images, and strip the file's metadata. Demo renders can be
produced with [`tools/render-screenshots`](tools/render-screenshots/README.md).

## Code of conduct

This project follows the [Code of Conduct](CODE_OF_CONDUCT.md). By taking part
you agree to it.
