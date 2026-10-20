# AIY Vision Kit v1 on Raspberry Pi OS Bookworm / Trixie: install

Turns a freshly flashed **Raspberry Pi OS Lite (32-bit) Bookworm or Trixie** card into a working Vision Kit:
Myriad drivers (DKMS), camera inference through picamera2, LEDs/button/buzzer, and the Joy Detector at boot.

## What you need

- Pi Zero W with the Vision Bonnet and Pi Camera v2, assembled as in Google's guide.
- **`aiy-binaries.tgz`**: the Myriad firmware and models, which can't be downloaded any more. Make it from an SD card running Google's
  official AIY image (`aiyprojects-2021-04-02.img.xz` from the
  [GitHub releases](https://github.com/google/aiyprojects-raspbian/releases)):

  ```bash
  ssh pi@raspberrypi.local 'dpkg -L aiy-vision-firmware aiy-models | while read f; do [ -f "$f" ] && echo "$f"; done | tar czf - -T -' > vendor/aiy-binaries.tgz
  ```

  `install.sh` checks the firmware's SHA-256.

## Install

1. In Raspberry Pi Imager, flash **Raspberry Pi OS Lite (32-bit)**, Bookworm or Trixie. In its settings, set a hostname, a user, Wi-Fi, and SSH with your public key.
   `deploy.sh` needs passwordless sudo. Bookworm gives the first user that by default; on Trixie run once:
   `ssh -t pi@vision-kit.local 'echo "pi ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/010_pi-nopasswd && sudo chmod 0440 /etc/sudoers.d/010_pi-nopasswd'`
2. From this repo on your computer:

   ```bash
   port/deploy.sh pi@vision-kit.local      # copies port/ + vendor/aiy-binaries.tgz, then runs install.sh
   ssh pi@vision-kit.local sudo reboot
   ```

   Or run it on the Pi yourself: `sudo ./install.sh --binaries aiy-binaries.tgz` from a copy of `port/`.

The DKMS build takes about 10 minutes on a Pi Zero. Options: `--no-joy-service`, `--streaming`, `--hold-kernel`, `--user NAME`.
`install.sh` is safe to re-run. `sudo ./uninstall.sh` removes everything it added except the apt packages.

## What gets installed

| Item | Where |
|---|---|
| Drivers `aiy-vision`, `aiy-io-i2c`, `gpio-aiy-io`, `pwm-aiy-io`, `aiy-adc`, `leds-ktd202x`, `pwm-soft` | DKMS package `aiy-vision-kit` (`/usr/src/aiy-vision-kit-2.0.0`). Rebuilt automatically for new kernels |
| Myriad firmware | `/lib/firmware/myriad_fw.mvcmd` |
| Models | `/opt/aiy/models/` |
| Python library + examples | `/opt/aiy/python` (editable install) in the venv `/opt/aiy/venv` (`--system-site-packages`; all dependencies come from apt) |
| udev rules (LED / pwm-soft access for the `gpio` group, `/dev/vision_spicomm` systemd tag) | `/etc/udev/rules.d/60-aiy-*.rules` |
| pwm-soft autoload | `/etc/modules-load.d/pwm-soft.conf` |
| SPI chip-select overlay | marked block in `/boot/firmware/config.txt` |
| Joy Detector | `joy_detection_demo.service` (enabled by default) |

## Using it

```bash
sudo systemctl stop joy_detection_demo        # it holds the camera
/opt/aiy/venv/bin/python /opt/aiy/python/src/examples/vision/face_detection_camera.py
```

In your own code, use `from aiy.camera import PiCamera` instead of `from picamera import PiCamera`.
See [`DEPENDENCIES.md`](DEPENDENCIES.md) for everything that changed from Google's stack and why.

## Kernel updates

DKMS rebuilds the modules when `apt upgrade` installs a new kernel. If a future kernel changes an API the drivers use, the build fails
and the bonnet stops working after the reboot. `--hold-kernel` avoids that by pinning the kernel. Check `dkms status` after upgrades.
