#!/bin/bash
# Installs the AIY Vision Kit v1 stack on Raspberry Pi OS Lite (32-bit) Bookworm or Trixie.
#
#   sudo ./install.sh --binaries /path/to/aiy-binaries.tgz [options]
#
# Run from the port/ directory. Safe to re-run. The binaries archive holds the
# Myriad firmware and the models, taken from an official AIY image (Google's apt
# repo that used to ship them is gone).
#
# Options:
#   --binaries FILE    archive with lib/firmware/myriad_fw.mvcmd and opt/aiy/models/ (required)
#   --user NAME        user for the Joy Detector service and LED/GPIO access (default: $SUDO_USER or pi)
#   --no-joy-service   don't enable the Joy Detector at boot
#   --streaming        start the Joy Detector with --enable_streaming
#   --hold-kernel      apt-mark hold the kernel so upgrades can't break the drivers
set -euo pipefail

AIY_VERSION=2.0.0
FIRMWARE_SHA256=438a1fc9b1b2e86465c7049d345ae9373bcddbc82c47a4d395952c00a8f3d1d3

SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BINARIES=""
TARGET_USER="${SUDO_USER:-pi}"
JOY_SERVICE=1
STREAMING=0
HOLD_KERNEL=0

log() { printf '\n==> %s\n' "$*"; }
die() { printf 'error: %s\n' "$*" >&2; exit 1; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --binaries) BINARIES="$2"; shift 2 ;;
    --user) TARGET_USER="$2"; shift 2 ;;
    --no-joy-service) JOY_SERVICE=0; shift ;;
    --streaming) STREAMING=1; shift ;;
    --hold-kernel) HOLD_KERNEL=1; shift ;;
    -h|--help) sed -n '2,19p' "$0"; exit 0 ;;
    *) die "unknown option: $1" ;;
  esac
done

[[ $EUID -eq 0 ]] || die "run with sudo"
[[ -n "$BINARIES" && -f "$BINARIES" ]] || die "--binaries FILE is required (see port/README or CLAUDE.md)"
id "$TARGET_USER" >/dev/null 2>&1 || die "user $TARGET_USER does not exist"
[[ -f "$SRC_DIR/drivers/dkms.conf" && -d "$SRC_DIR/python/src/aiy" ]] || die "run from the port/ directory"

# Read os-release in a subshell: it defines VERSION and friends.
OS_CODENAME="$(. /etc/os-release && echo "${VERSION_CODENAME:-}")"
case "$OS_CODENAME" in
  bookworm|trixie) ;;
  *) die "unsupported OS: $(. /etc/os-release && echo "${PRETTY_NAME:-unknown}") (need Raspberry Pi OS Bookworm or Trixie)" ;;
esac
if ! tr -d '\0' < /proc/device-tree/hat/product 2>/dev/null | grep -q VisionBonnet; then
  echo "warning: no Vision Bonnet found in /proc/device-tree/hat; continuing anyway"
fi
KERNEL="$(uname -r)"
CONFIG_TXT=/boot/firmware/config.txt
REBOOT_NEEDED=0

log "Installing packages"
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y --no-install-recommends \
  dkms build-essential "linux-headers-$KERNEL" gpiod \
  python3-venv python3-setuptools python3-protobuf python3-pil python3-numpy \
  python3-picamera2 python3-gpiozero python3-lgpio python3-rpi-lgpio \
  fonts-freefont-ttf avahi-utils

log "Installing Myriad firmware and models from $BINARIES"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT
tar -xzf "$BINARIES" -C "$STAGE" lib/firmware/myriad_fw.mvcmd opt/aiy/models
echo "$FIRMWARE_SHA256  $STAGE/lib/firmware/myriad_fw.mvcmd" | sha256sum -c --quiet \
  || die "myriad_fw.mvcmd checksum mismatch"
install -m 644 "$STAGE/lib/firmware/myriad_fw.mvcmd" /lib/firmware/myriad_fw.mvcmd
install -d /opt/aiy/models
install -m 644 "$STAGE"/opt/aiy/models/* /opt/aiy/models/
echo "$(ls /opt/aiy/models | wc -l) model files in /opt/aiy/models"

log "Building kernel modules with DKMS (slow on a Pi Zero: ~10 minutes)"
# Drop modules installed by hand during development; they would shadow DKMS's.
rm -rf /lib/modules/*/updates/aiy
for old in $(dkms status aiy-vision-kit 2>/dev/null | sed -n 's#^aiy-vision-kit/\([^,:]*\).*#\1#p' | sort -u); do
  dkms remove -m aiy-vision-kit -v "$old" --all || true
done
DKMS_SRC="/usr/src/aiy-vision-kit-$AIY_VERSION"
rm -rf "$DKMS_SRC"
mkdir -p "$DKMS_SRC"
(cd "$SRC_DIR/drivers" && tar --exclude=debian --exclude='*.o' --exclude='*.ko' --exclude='*.mod*' \
   --exclude='.*.cmd' --exclude=Module.symvers --exclude=modules.order -cf - .) | tar -xf - -C "$DKMS_SRC"
sed -i "s/#MODULE_VERSION#/$AIY_VERSION/" "$DKMS_SRC/dkms.conf"
dkms add -m aiy-vision-kit -v "$AIY_VERSION"
dkms build -m aiy-vision-kit -v "$AIY_VERSION" -k "$KERNEL"
dkms install -m aiy-vision-kit -v "$AIY_VERSION" -k "$KERNEL" --force

log "Installing udev rules and module autoload"
install -m 644 "$SRC_DIR"/udev/60-aiy-*.rules /etc/udev/rules.d/
echo pwm-soft > /etc/modules-load.d/pwm-soft.conf
udevadm control --reload
usermod -aG gpio,i2c,spi,video "$TARGET_USER"

log "Configuring $CONFIG_TXT"
if ! grep -q '^dtoverlay=spi0-1cs,cs0_pin=7' "$CONFIG_TXT"; then
  cp -n "$CONFIG_TXT" "$CONFIG_TXT.orig-aiy" || true
  printf '\n# >>> aiy-vision-kit\n[all]\n# Keep GPIO6/8 free for the Myriad driver\ndtoverlay=spi0-1cs,cs0_pin=7\n# <<< aiy-vision-kit\n' >> "$CONFIG_TXT"
  REBOOT_NEEDED=1
fi

log "Installing the Python library into /opt/aiy/venv"
install -d /opt/aiy/python
(cd "$SRC_DIR/python" && tar --exclude=__pycache__ --exclude='*.egg-info' -cf - .) | tar -xf - -C /opt/aiy/python
[[ -d /opt/aiy/venv ]] || python3 -m venv --system-site-packages /opt/aiy/venv
# Offline: every dependency comes from apt through --system-site-packages.
/opt/aiy/venv/bin/pip install --quiet --no-index --no-build-isolation -e /opt/aiy/python
/opt/aiy/venv/bin/python -c 'import aiy.camera, aiy.vision.inference, aiy.leds, aiy.board' \
  || die "Python library import check failed"

log "Installing the Joy Detector service"
JOY_ARGS="--blink_on_error"
[[ $STREAMING -eq 1 ]] && JOY_ARGS="$JOY_ARGS --enable_streaming --mdns_name AIY-Board"
sed -e "s/@USER@/$TARGET_USER/" -e "s/@JOY_ARGS@/$JOY_ARGS/" \
  "$SRC_DIR/systemd/joy_detection_demo.service" > /etc/systemd/system/joy_detection_demo.service
systemctl daemon-reload
if [[ $JOY_SERVICE -eq 1 ]]; then
  systemctl enable joy_detection_demo.service
else
  systemctl disable joy_detection_demo.service 2>/dev/null || true
fi

if [[ $HOLD_KERNEL -eq 1 ]]; then
  log "Holding kernel packages"
  apt-mark hold $(dpkg-query -W -f='${Package}\n' 'linux-image-*rpi*' 'linux-headers-*rpi*' 2>/dev/null)
fi

log "Done"
cat <<EOF
  Modules:   $(dkms status aiy-vision-kit | head -1)
  Python:    /opt/aiy/venv/bin/python  (examples in /opt/aiy/python/src/examples/vision)
  Service:   joy_detection_demo $( [[ $JOY_SERVICE -eq 1 ]] && echo enabled || echo disabled )
EOF
if [[ $REBOOT_NEEDED -eq 1 ]]; then
  echo "  Reboot required (config.txt changed): sudo reboot"
else
  echo "  Reboot recommended so the modules and udev permissions apply cleanly."
fi
