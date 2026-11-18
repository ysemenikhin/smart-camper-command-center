# Security policy

## What counts as a security problem here

- **A leaked secret or identifier** in the repository or its history: Wi-Fi
  credentials, API or OTA keys, MAC or sensor addresses, IP addresses, domains,
  camera URLs, GPS positions.
- **Unsafe firmware behaviour:** a circuit that can come on by itself (for
  example after a reboot), a safety timer that can be bypassed, an interlock
  that can be defeated from Home Assistant, or suspension control that can
  drive the trailer outside its safe range.
- **Remote control without authorisation:** anything that lets someone on the
  network switch relays or move the suspension without Home Assistant or
  ESPHome authentication.

Ordinary bugs go in a normal issue.

## How to report

Use GitHub's private reporting: on the repository page open **Security →
Report a vulnerability**. Please do **not** open a public issue, and do not
paste the secret itself anywhere public.

Include:

- what you found and where (file and line, or commit),
- how it could be used or what could go wrong,
- how to reproduce it, if it is behavioural.

## What happens next

This is a personal project maintained in spare time. Reports are read and
acknowledged as soon as possible. A leaked secret is fixed first by rotating it
on the trailer, then by removing it from the repository. You will be told what
was done.

## Supported versions

Only the current version of each component on `main` is supported. Older
versions are kept for reference in [CHANGELOG.md](CHANGELOG.md) but are not
fixed.

## If you build from this repository

Your own system's security is yours: generate your own keys
(`openssl rand -base64 32`), keep `esphome/secrets.yaml` out of git, and do not
expose Home Assistant or the ESPHome boards to the internet without
authentication.
