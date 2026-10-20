#!/bin/bash
# Removes what install.sh added. Apt packages are left installed.
#
#   sudo ./uninstall.sh
set -euo pipefail

[[ $EUID -eq 0 ]] || { echo "run with sudo" >&2; exit 1; }
CONFIG_TXT=/boot/firmware/config.txt

systemctl disable --now joy_detection_demo.service 2>/dev/null || true
rm -f /etc/systemd/system/joy_detection_demo.service
systemctl daemon-reload

for old in $(dkms status aiy-vision-kit 2>/dev/null | sed -n 's#^aiy-vision-kit/\([^,:]*\).*#\1#p' | sort -u); do
  dkms remove -m aiy-vision-kit -v "$old" --all || true
done
rm -rf /usr/src/aiy-vision-kit-* /lib/modules/*/updates/aiy

rm -f /etc/udev/rules.d/60-aiy-*.rules /etc/modules-load.d/pwm-soft.conf
udevadm control --reload

rm -rf /opt/aiy /lib/firmware/myriad_fw.mvcmd

# Remove the block install.sh appended, plus the unmarked lines from early hand setups.
sed -i '/^# >>> aiy-vision-kit$/,/^# <<< aiy-vision-kit$/d' "$CONFIG_TXT"
sed -i -e '/^# AIY Vision Bonnet: keep GPIO6\/8 free for the Myriad driver$/d' \
       -e '/^dtoverlay=spi0-1cs,cs0_pin=7$/d' "$CONFIG_TXT"

depmod -a
echo "Uninstalled. Reboot to unload the modules: sudo reboot"
