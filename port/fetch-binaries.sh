#!/bin/bash
# Rebuilds vendor/aiy-binaries.tgz (Myriad firmware + models) from Google's
# official AIY system image on GitHub. These files were only ever shipped as
# .debs from Google's apt repo, which is gone, so the image is the one public,
# checksummed source left.
#
#   port/fetch-binaries.sh [--keep-image] [--out FILE]
#
# Downloads aiyprojects-2021-04-02.img.xz (1.2 GB) into vendor/cache/ (resumable,
# kept for re-runs), verifies its SHA-256, and copies the files out of the ext4
# root partition with debugfs, so nothing is mounted and no root is needed.
# debugfs comes from e2fsprogs: on Linux it is usually installed; on macOS use
# `brew install e2fsprogs`, or have Docker running and it is used automatically.
#
# Needs about 6 GB of free space while running (the image is decompressed).
set -euo pipefail

RELEASE_URL=https://github.com/google/aiyprojects-raspbian/releases/download/v20210402
IMAGE=aiyprojects-2021-04-02.img
# Same value as install.sh checks.
FIRMWARE_SHA256=438a1fc9b1b2e86465c7049d345ae9373bcddbc82c47a4d395952c00a8f3d1d3
EXPECTED_MODEL_FILES=15

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CACHE="$ROOT/vendor/cache"
OUT="$ROOT/vendor/aiy-binaries.tgz"
KEEP_IMAGE=0

log() { printf '\n==> %s\n' "$*"; }
die() { printf 'error: %s\n' "$*" >&2; exit 1; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --keep-image) KEEP_IMAGE=1; shift ;;
    --out) OUT="$2"; shift 2 ;;
    -h|--help) sed -n '2,16p' "$0"; exit 0 ;;
    *) die "unknown option: $1" ;;
  esac
done

for tool in curl xz python3 tar; do
  command -v "$tool" >/dev/null || die "missing $tool"
done
if command -v shasum >/dev/null; then sha256() { shasum -a 256 "$@"; }; else sha256() { sha256sum "$@"; }; fi

# Prefer a local debugfs; fall back to one in a Debian container.
DEBUGFS=""
for candidate in debugfs /sbin/debugfs /usr/sbin/debugfs \
                 /opt/homebrew/opt/e2fsprogs/sbin/debugfs /usr/local/opt/e2fsprogs/sbin/debugfs; do
  if command -v "$candidate" >/dev/null 2>&1; then DEBUGFS="$(command -v "$candidate")"; break; fi
done
if [[ -z "$DEBUGFS" ]]; then
  docker info >/dev/null 2>&1 || die "need debugfs (brew install e2fsprogs / apt install e2fsprogs) or a running Docker"
  DEBUGFS=docker
fi

mkdir -p "$CACHE"
WORK="$(mktemp -d "$CACHE/work.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT

log "Downloading $IMAGE.xz (resumes if interrupted)"
curl -fsSL --retry 3 -o "$CACHE/$IMAGE.xz.sha256" "$RELEASE_URL/$IMAGE.xz.sha256"
expected="$(awk '{print $1; exit}' "$CACHE/$IMAGE.xz.sha256")"
checksum() { sha256 "$CACHE/$IMAGE.xz" | awk '{print $1}'; }
if [[ -f "$CACHE/$IMAGE.xz" && "$(checksum)" == "$expected" ]]; then
  echo "already downloaded"
else
  curl -fL --retry 3 -C - -o "$CACHE/$IMAGE.xz" "$RELEASE_URL/$IMAGE.xz"
  [[ "$(checksum)" == "$expected" ]] || die "$IMAGE.xz checksum mismatch (delete $CACHE/$IMAGE.xz and retry)"
fi
echo "SHA-256 OK: $expected"

log "Decompressing"
xz -dc -T0 "$CACHE/$IMAGE.xz" > "$WORK/$IMAGE"

# The root filesystem is the second MBR partition.
OFFSET="$(python3 -I - "$WORK/$IMAGE" <<'EOF'
import struct, sys
with open(sys.argv[1], 'rb') as f:
    mbr = f.read(512)
if mbr[510:512] != b'\x55\xaa':
    sys.exit('no MBR partition table')
entry = mbr[446 + 16:446 + 32]
if entry[4] != 0x83:
    sys.exit('partition 2 is type %#x, expected Linux (0x83)' % entry[4])
print(struct.unpack('<I', entry[8:12])[0] * 512)
EOF
)"

log "Extracting the root partition (offset $OFFSET)"
# Carve the partition out so debugfs can read it as a plain ext4 image
# (portable: macOS dd has no byte-offset skip).
python3 -I - "$WORK/$IMAGE" "$WORK/rootfs.ext4" "$OFFSET" <<'EOF'
import shutil, sys
src, dst, offset = sys.argv[1], sys.argv[2], int(sys.argv[3])
with open(src, 'rb') as fin, open(dst, 'wb') as fout:
    fin.seek(offset)
    shutil.copyfileobj(fin, fout, 4 << 20)
EOF
[[ $KEEP_IMAGE -eq 1 ]] || rm -f "$WORK/$IMAGE"

mkdir -p "$WORK/out/lib/firmware" "$WORK/out/opt/aiy"
COMMANDS='dump -p /lib/firmware/myriad_fw.mvcmd OUT/lib/firmware/myriad_fw.mvcmd
rdump /opt/aiy/models OUT/opt/aiy'
if [[ "$DEBUGFS" == docker ]]; then
  echo "using debugfs in debian:bookworm-slim"
  printf '%s\n' "${COMMANDS//OUT//work/out}" > "$WORK/cmds"
  docker run --rm -v "$WORK:/work" debian:bookworm-slim debugfs -f /work/cmds /work/rootfs.ext4
else
  echo "using $DEBUGFS"
  printf '%s\n' "${COMMANDS//OUT/$WORK/out}" > "$WORK/cmds"
  "$DEBUGFS" -f "$WORK/cmds" "$WORK/rootfs.ext4"
fi

log "Verifying"
echo "$FIRMWARE_SHA256  $WORK/out/lib/firmware/myriad_fw.mvcmd" > "$WORK/fw.sha256"
sha256 -c "$WORK/fw.sha256" >/dev/null || die "myriad_fw.mvcmd checksum mismatch"
count="$(ls "$WORK/out/opt/aiy/models" | wc -l | tr -d ' ')"
[[ "$count" -eq "$EXPECTED_MODEL_FILES" ]] || die "expected $EXPECTED_MODEL_FILES model files, got $count"
echo "firmware OK, $count model files"

mkdir -p "$(dirname "$OUT")"
tar -czf "$OUT" -C "$WORK/out" lib/firmware/myriad_fw.mvcmd opt/aiy/models
if [[ $KEEP_IMAGE -eq 1 ]]; then
  mv "$WORK/rootfs.ext4" "$CACHE/"
  [[ -f "$WORK/$IMAGE" ]] && mv "$WORK/$IMAGE" "$CACHE/"
fi
log "Wrote $OUT"
echo "The download stays in $CACHE/$IMAGE.xz for re-runs; delete it to free 1.2 GB."
