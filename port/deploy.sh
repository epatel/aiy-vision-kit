#!/bin/bash
# From the Mac: copies port/ and the binaries archive to a Pi and runs install.sh.
#
#   port/deploy.sh pi@vision-kit.local [install.sh options]
#
# Needs SSH key login and passwordless sudo (the Raspberry Pi OS default for the
# first user). The archive defaults to vendor/aiy-binaries.tgz; override with
# AIY_BINARIES=/path/to/file.
set -euo pipefail

HOST="${1:?usage: $0 user@host [install.sh options]}"
shift
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BINARIES="${AIY_BINARIES:-$ROOT/vendor/aiy-binaries.tgz}"
[[ -f "$BINARIES" ]] || { echo "missing $BINARIES (create it with port/fetch-binaries.sh)" >&2; exit 1; }

rsync -a --delete \
  --exclude __pycache__ --exclude '*.egg-info' --exclude '*.o' --exclude '*.ko' \
  --exclude '*.mod*' --exclude '.*.cmd' --exclude Module.symvers --exclude modules.order \
  "$ROOT/port/" "$HOST:vision-kit-port/"
rsync -a "$BINARIES" "$HOST:vision-kit-port/aiy-binaries.tgz"
ssh -t "$HOST" "cd vision-kit-port && sudo ./install.sh --binaries aiy-binaries.tgz $*"
