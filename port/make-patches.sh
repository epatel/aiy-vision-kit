#!/bin/bash
# Regenerates port/drivers.patch and port/python.patch: the diffs of this port
# against Google's upstream snapshot in docs/aiyprojects-raspbian/.
#
#   port/make-patches.sh [drivers|python]    (default: both)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
UPSTREAM="$ROOT/docs/aiyprojects-raspbian"
cd "$ROOT"

# Stable output: no file timestamps, and one fixed form for the per-file diff
# lines, so the patches only change when the code does.
normalize() {
  sed -E -e 's/^((---|\+\+\+) [^[:space:]]+)[[:space:]].*$/\1/' \
         -e 's#^diff .* (docs/aiyprojects-raspbian/[^ ]+) (port/[^ ]+)$#diff -ru \1 \2#'
}

drivers() {
  # dkms.conf is new here, and debian/ + make.sh are upstream packaging the port doesn't use.
  diff -ru -x debian -x make.sh -x dkms.conf -x '*.o' -x '*.ko' -x '*.mod*' -x '.*.cmd' \
       -x Module.symvers -x modules.order \
       docs/aiyprojects-raspbian/drivers port/drivers | grep -v '^Only in' | normalize > port/drivers.patch || true
}

python() {
  diff -ruN -x __pycache__ -x '*.egg-info' docs/aiyprojects-raspbian/src port/python/src | normalize > port/python.patch || true
}

[[ -d "$UPSTREAM" ]] || { echo "missing $UPSTREAM" >&2; exit 1; }
case "${1:-all}" in
  drivers) drivers ;;
  python) python ;;
  all) drivers; python ;;
  *) echo "usage: $0 [drivers|python]" >&2; exit 2 ;;
esac
