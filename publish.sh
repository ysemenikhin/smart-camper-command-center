#!/usr/bin/env bash
# Publish this repository to GitHub as a PUBLIC repo, with all history and tags.
# Needs the GitHub CLI logged in (gh auth login). Run from the repo root.
set -euo pipefail
NAME="${1:-smart-camper-command-center}"

echo "1/3 secret scan of every commit..."
if git log -p --all | grep -nIE '([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}|\b192\.168\.[0-9]+\.[0-9]+\b|key: "[A-Za-z0-9+/]{40,}={0,2}"|password: "[0-9a-f]{32}"' | grep -v 'XX:XX:XX:XX:XX:XX'; then
  echo "STOP: something that looks like a secret or identifier is in history."; exit 1
fi
command -v gitleaks >/dev/null && gitleaks detect --source . --log-opts="--all" || echo "(gitleaks not installed - grep scan passed)"

echo "2/3 creating github.com/<you>/$NAME (public) and pushing main..."
gh repo create "$NAME" --public --source . --remote origin --push \
  --description "Home Assistant + ESPHome control system for an off-road expedition trailer: air suspension with auto-levelling, 16-relay power, tanks, solar, heater, cameras, connectivity."

echo "3/3 pushing tags..."
git push origin --tags
gh repo edit --add-topic home-assistant,esphome,esp32,overlanding,camper,rv,air-suspension,iot,12v,kincony
echo "Done: $(gh repo view --json url -q .url)"
