#!/bin/bash
# PostToolUse hook (Edit|Write): after an edit under port/drivers/ or
# port/python/src/, regenerate the matching port/*.patch so the diffs against
# upstream never go stale. Fails open: anything missing means do nothing.
f=$(python3 -I -c 'import json, sys; print(json.load(sys.stdin).get("tool_input", {}).get("file_path", ""))' 2>/dev/null) || exit 0
root="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
case "$f" in
  "$root"/port/drivers/*|port/drivers/*) which=drivers ;;
  "$root"/port/python/src/*|port/python/src/*) which=python ;;
  *) exit 0 ;;
esac
[ -x "$root/port/make-patches.sh" ] || exit 0
"$root/port/make-patches.sh" "$which" >/dev/null 2>&1 || true
exit 0
