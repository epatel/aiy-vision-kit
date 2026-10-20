# CLAUDE.md

## About this project

A port of Google's AIY Vision Kit v1 software (Pi Zero W + Vision Bonnet with a Movidius MA2450 + Pi Camera v2) from its last official Raspbian Buster image to
Raspberry Pi OS Lite 32-bit **Bookworm (kernel 6.12) and Trixie (kernel 6.18)**. The work is in `port/`: patched kernel drivers (DKMS), the `aiy` Python library
with a picamera-compatible shim on Picamera2, and scripts that set up a freshly flashed card. People-facing docs: `README.md`, `port/README.md` (install, Known gaps),
`port/DEPENDENCIES.md` (every change and why, with test results).

## Commands

`make` (from the repo root, on the Mac) lists every target as a numbered menu. `HOST=pi@…` and `ARGS=…` override the defaults (`pi@vision-kit.local`, none).
- `make fetch`: get the Myriad firmware and models (not in git) into `vendor/aiy-binaries.tgz`
- `make deploy [ARGS="--streaming --no-joy-service --hold-kernel"]`, then `make reboot`: install or update a card (about 10 min; the drivers rebuild every time)
- `make status`: DKMS, "Myriad ready" (from the journal, not `dmesg`, which pwm-soft floods), `/dev/vision_spicomm`, Joy Detector state and args
- `make test_hw` / `make test_face` / `make test_camera` / `make test_stream`: device tests. They copy `port/tests/` over, and the first three stop the Joy Detector
  (it holds the camera and bonnet) and start it again afterwards. `test_face` needs `VIEW2=<jpeg with a face>` if `vendor/baseline/view2.jpg` is missing
- `make patches`: regenerate `port/*.patch`. `make check_docs`: check this file, the cards and the setup record. `make uninstall`: remove it all from the card
- Script options: `port/install.sh --help`, `port/fetch-binaries.sh --help`

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
- [standing-defaults](cards/standing-defaults.md) — before installing any Python dependency, or adding anything that stores data

When you commit a change that adds non-obvious logic, settles an architectural choice,
or makes a card above wrong, update or add the card in that commit and keep this index
in sync. Proposed diffs and answers need no card edits. Cards stay self-contained: no
card links to another.

## Conventions

- Edits under `docs/aiyprojects-raspbian/` and `docs/reference/` are blocked (`.claude/settings.json`): they are upstream snapshots, so re-fetch instead. `docs/README.md` is ours and editable.
- `port/*.patch` regenerate automatically after edits to `port/drivers/` or `port/python/src/` (hook `.claude/hooks/regen-patches.sh`); after shell-based edits, run `make patches`.
- Work goes in `port/`; binaries and logs go in gitignored `vendor/`. Driver code must build on 6.12 **and** 6.18.
- Never `apt upgrade` the reference card running Google's original image.
- Diagrams: mermaid, not ASCII.
