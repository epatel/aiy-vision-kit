# AIY Vision Kit v1 on Raspberry Pi OS Bookworm / Trixie: install

Turns a freshly flashed **Raspberry Pi OS Lite (32-bit) Bookworm or Trixie** card into a working Vision Kit:
Myriad drivers (DKMS), camera inference through picamera2, LEDs/button/buzzer, and the Joy Detector at boot.

## What you need

- Pi Zero W with the Vision Bonnet and Pi Camera v2, assembled as in Google's guide.
- **`vendor/aiy-binaries.tgz`**: the Myriad firmware and the models. They aren't in this repo, and Google's apt repo that shipped them is gone.
  The only public source left is Google's official system image on the
  [GitHub releases page](https://github.com/google/aiyprojects-raspbian/releases/tag/v20210402). This script downloads it and pulls the files out:

  ```bash
  port/fetch-binaries.sh        # 1.2 GB download (cached in vendor/cache/), needs debugfs or Docker
  ```

  It checks the image's published SHA-256 and the firmware's SHA-256, and needs no root and no mounting.
  You can also take the files from a card running the official image:
  `ssh pi@raspberrypi.local 'dpkg -L aiy-vision-firmware aiy-models | while read f; do [ -f "$f" ] && echo "$f"; done | tar czf - -T -' > vendor/aiy-binaries.tgz`.

## Prepare the SD card

The Pi Zero W runs headless here, with no screen or keyboard: everything happens over Wi-Fi and SSH, so set those up when you flash the card.

1. **Flash with [Raspberry Pi Imager](https://www.raspberrypi.com/software/)** (a current version: it writes the first-boot configuration the image reads).
   Choose the device *Raspberry Pi Zero*, then **Raspberry Pi OS Lite (32-bit)**. Trixie is the current release. Bookworm also works, and Imager lists it
   among the older releases. Don't pick a 64-bit or desktop image: the Pi Zero W's ARMv6 CPU can't run 64-bit, and the desktop is too heavy for 512 MB.
2. **Fill in Imager's customisation tabs:**
   - *Hostname:* for example `vision-kit` (the Makefile defaults to `pi@vision-kit.local`).
   - *Localisation:* your capital city and time zone. This also sets the Wi-Fi regulatory country, which Wi-Fi needs.
   - *User:* `pi` and a password.
   - *Wi-Fi:* SSID and password. **The Pi Zero W only has 2.4 GHz Wi-Fi**, so a 5 GHz-only network won't work.
   - *Remote Access:* turn on **Enable SSH** and choose **public key authentication**. Paste your public key (for example `~/.ssh/id_ed25519.pub`).
     This is a separate tab and easy to miss.
3. **Add an empty `ssh` file to the boot partition** before the first boot. After writing, Imager ejects the card, so put it back in. On a Mac its boot partition
   mounts as `bootfs`:

   ```bash
   touch /Volumes/bootfs/ssh
   diskutil eject /Volumes/bootfs
   ```

   This is the standard Raspberry Pi OS switch for SSH on **every** model, not a Pi Zero W quirk. With the file present, SSH is enabled at boot,
   and the file is then removed. Imager's own "Enable SSH" is applied later by the first-boot tooling (cloud-init on Trixie,
   which runs `systemctl enable --now ssh` in its last stage). On a single-core Pi Zero that last stage comes minutes into the first boot.
   One Trixie card here didn't answer SSH until the file was added. The file makes SSH come up early and doesn't depend on that tooling, and it's harmless alongside the Imager setting.
4. **First boot.** Insert the card and power the Pi from the **PWR IN** port. The first boot of a Pi Zero takes several minutes: it expands the file system,
   generates keys and runs the first-boot configuration. Then:

   ```bash
   ssh pi@vision-kit.local
   ```

   - *"REMOTE HOST IDENTIFICATION HAS CHANGED"*: each newly flashed card gets a new host key, so a second card with the same hostname triggers this.
     Run `ssh-keygen -R vision-kit.local`, then connect again.
   - *No answer:* wait a few more minutes, check that the Wi-Fi network is 2.4 GHz, or find the Pi's IP address in your router.
     Leaving a `wpa_supplicant.conf` in the boot partition no longer sets up Wi-Fi: Bookworm and later use NetworkManager, so use Imager's Wi-Fi tab.
5. **Passwordless sudo**, which `deploy.sh` needs because it runs `sudo` over a non-interactive ssh. Bookworm images from Imager give the first user this. **Trixie images don't**,
   so run this once; it asks for the password:

   ```bash
   ssh -t pi@vision-kit.local 'echo "pi ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/010_pi-nopasswd && sudo chmod 0440 /etc/sudoers.d/010_pi-nopasswd && sudo visudo -c'
   ```

   Check it with `ssh pi@vision-kit.local sudo -n true && echo ok`.

## Install

1. Prepare the card as above (reachable over SSH, passwordless sudo).
2. From this repo on your computer:

   ```bash
   port/deploy.sh pi@vision-kit.local      # or: make deploy   (copies port/ + vendor/aiy-binaries.tgz, then runs install.sh)
   ssh pi@vision-kit.local sudo reboot     # or: make reboot
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

The Joy Detector runs at boot. The LED shows how much people in view smile, and pressing the button saves a photo to `~/Pictures`
(plus an `_annotated` copy with face boxes when a face is in view).

With `install.sh --streaming` it also streams live video: open `http://<pi>:4664/` in a browser (H.264 decoded in the page,
with the joy overlay). Port 4665 is the protobuf stream the AIY app uses, and 4666 is raw H.264 (`ffplay tcp://<pi>:4666`).

```bash
sudo systemctl stop joy_detection_demo        # it holds the camera
/opt/aiy/venv/bin/python /opt/aiy/python/src/examples/vision/face_detection_camera.py
```

In your own code, use `from aiy.camera import PiCamera` instead of `from picamera import PiCamera`.
See [`DEPENDENCIES.md`](DEPENDENCIES.md) for everything that changed from Google's stack and why.

## Kernel updates

DKMS rebuilds the modules when `apt upgrade` installs a new kernel. If a future kernel changes an API the drivers use, the build fails
and the bonnet stops working after the reboot. `--hold-kernel` avoids that by pinning the kernel. Check `dkms status` after upgrades.

## Known gaps

Not verified yet, on either OS unless noted:

- **Camera preview and `Annotator` overlays on HDMI.** The DRM preview only starts when a display is connected; untested without one.
- **Bookworm after the Trixie fixes.** The `pins.py` and Joy Detector changes run on both OSes but were only tested on Trixie. The kernel-version
  checks in the drivers keep the 6.12 code path unchanged.
- **Live inference speed** is about 8–11 fps, against 10–15 fps on Google's Buster image. This may be the ISP producing RGB frames that nothing uses;
  not measured carefully.
- **Re-running `install.sh` always rebuilds the drivers** (about 10 minutes on a Pi Zero), even when nothing changed.
- **Voice Kit** code in `aiy/` (assistant, cloudspeech, voice) isn't ported or tested.
