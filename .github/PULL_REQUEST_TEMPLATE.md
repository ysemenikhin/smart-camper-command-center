## What and why

<!-- What changes, and the problem it solves. -->

## Components and versions

<!-- e.g. relay-board v2.3.9 -> v2.3.10. Write "docs only" if no component file changed. -->

## How it was tested

<!-- On hardware? What did you see? For firmware: "esphome config" passes is the minimum. -->

## Checklist

- [ ] Version bumped in the file header, with a changelog line, in the same edit (component files only)
- [ ] For ESPHome: `config_version` and `config_date` bumped
- [ ] Row added to `CHANGELOG.md`
- [ ] Docs updated where the behaviour, wiring or setup changed
- [ ] No secrets, MAC/IP/sensor addresses, domains, camera URLs or locations added
- [ ] `yamllint` and `esphome config` pass locally
- [ ] Safety: anything that switches a load or moves the suspension still fails OFF and keeps its firmware timer
