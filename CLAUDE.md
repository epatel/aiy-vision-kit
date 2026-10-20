# CLAUDE.md

## About this project

A port of Google's AIY Vision Kit v1 software (Pi Zero W + Vision Bonnet with a Movidius MA2450 + Pi Camera v2) from its last official Raspbian Buster image to
Raspberry Pi OS Lite 32-bit **Bookworm (kernel 6.12) and Trixie (kernel 6.18)**. The work is in `port/`: patched kernel drivers (DKMS), the `aiy` Python library
with a picamera-compatible shim on Picamera2, and scripts that set up a freshly flashed card. People-facing docs: `README.md`, `port/README.md` (install, Known gaps),
`port/DEPENDENCIES.md` (every change and why, with test results).

## Commands

Run on the Mac, from the repo root:
- Get the firmware and models (not in git): `port/fetch-binaries.sh` → `vendor/aiy-binaries.tgz`
- Install or update a card: `port/deploy.sh pi@vision-kit.local [--streaming] [--no-joy-service] [--hold-kernel]`, then `ssh pi@vision-kit.local sudo reboot`
  (about 10 min; the drivers rebuild every time)
- Remove from a card: `ssh pi@vision-kit.local 'cd vision-kit-port && sudo ./uninstall.sh'`
- Options and help: `port/install.sh --help`, `port/fetch-binaries.sh --help`

Run on the Pi as `pi`, after `rsync -a port/tests/ pi@vision-kit.local:vision-kit-port/tests/` and `sudo systemctl stop joy_detection_demo`:
- Hardware: `/opt/aiy/venv/bin/python vision-kit-port/tests/hardware_check.py`
- Myriad + model, no camera: `/opt/aiy/venv/bin/python /opt/aiy/python/src/examples/vision/face_detection.py --input ~/view2.jpg`
- Live camera: `/opt/aiy/venv/bin/python /opt/aiy/python/src/examples/vision/face_detection_camera.py --num_frames 60`
- Driver status: `sudo dmesg | grep "Myriad ready"`, `/usr/sbin/dkms status`

## Cards

### Architecture
- [architecture](cards/architecture.md) — onboarding, or work spanning camera, bonnet, drivers and Python; where things live on the Pi

### Domains
- [kernel-drivers](cards/kernel-drivers.md) — editing or building anything in port/drivers, kernel API errors, a new kernel version, DKMS or boot-log questions
- [camera-shim](cards/camera-shim.md) — touching aiy/camera.py, porting picamera code, capture/recording/preview behaviour, or slow inference
- [gpio-leds-buzzer](cards/gpio-leds-buzzer.md) — button, LEDs, buzzer, PIN_A..D, gpiozero errors, sysfs permission or GPIO numbering problems
- [streaming-server](cards/streaming-server.md) — live video on ports 4664/4665/4666, the web viewer or AIY app stream, streaming bugs
- [install-and-deploy](cards/install-and-deploy.md) — changing install.sh, deploy.sh, uninstall.sh or fetch-binaries.sh, setting up a new card, or updating one quickly

### Features
- [joy-detector](cards/joy-detector.md) — the boot-time Joy Detector service, button photos, or anything that must stop it first
- [testing-on-device](cards/testing-on-device.md) — before running anything on the Pi: which card is in it, test scripts, ssh and pgrep traps

### Decisions
- [binaries-from-release-image](cards/binaries-from-release-image.md) — why firmware and models aren't in git, or where to get them if the source breaks
- [picamera-shim-over-rewrite](cards/picamera-shim-over-rewrite.md) — considering rewriting examples for Picamera2 or extending the shim
- [dkms-over-kernel-hold](cards/dkms-over-kernel-hold.md) — kernel upgrades breaking the drivers, or whether to pin the kernel
- [docs-licensing](cards/docs-licensing.md) — adding third-party material to docs/ or anything else that gets published

When you commit a change that adds non-obvious logic, settles an architectural choice,
or makes a card above wrong, update or add the card in that commit and keep this index
in sync. Proposed diffs and answers need no card edits. Cards stay self-contained: no
card links to another.

## Conventions

- `docs/` holds read-only upstream snapshots. Re-fetch instead of editing. Work goes in `port/`; binaries and logs go in gitignored `vendor/`.
- Driver code must build on 6.12 **and** 6.18. Regenerate `port/drivers.patch` / `port/python.patch` (diff against `docs/aiyprojects-raspbian/`) when those trees change.
- Never `apt upgrade` the reference card running Google's original image.
- Diagrams: mermaid, not ASCII.
