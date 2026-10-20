# CLAUDE.md

Port of the Google AIY Vision Kit v1 software stack to current Raspberry Pi OS (Bookworm first,
then Trixie). See `README.md` for the plan and `TODO.html` for the checklist.

## Hardware
- Raspberry Pi Zero W: ARMv6, 512 MB RAM. Needs the **32-bit (armhf) Lite** image. No 64-bit, no desktop.
- Vision Bonnet: Movidius MA2450 over SPI0, plus an MCU on I2C `0x51` (GPIO/PWM/ADC), and a KTD2026 RGB LED driver at `0x30`.
- Pi Camera v2 (imx219). Its CSI cable runs *through* the bonnet, which reads frames as they pass.
  Inference only works while the Pi is streaming from the camera at 1640×1232 (picamera `sensor_mode=4`).
- The bonnet's device-tree overlay is stored in its HAT EEPROM, so no `dtoverlay=` line is needed for it.

## Facts established (2026-10-20)
- Google apt repo `packages.cloud.google.com/apt aiyprojects-stable` → 404. The `aiy-vision-firmware`
  (`/lib/firmware/myriad_fw.mvcmd`) and `aiy-models` packages exist only inside the GitHub release images
  (`aiyprojects-2021-04-02.img.xz`) or the user's existing SD card.
- The upstream AIY repo has been unchanged since 2021-04-15 and is vendored at `docs/aiyprojects-raspbian/`.
- The full list of kernel and Python breaks, checked against the `rpi-6.12.y` headers, is in **`port/DEPENDENCIES.md`** (IDs K1–K9, P1–P5).
  The biggest: `pwm-aiy-io` needs `.apply` and `devm_pwmchip_alloc`, `protocol_pb2.py` is old-style generated code with no `.proto` source,
  and the `Annotator` relies on picamera MMAL internals.
- Keep Google's `leds-ktd202x`. The mainline driver uses the same compatible string but isn't enabled in `bcmrpi_defconfig`, and `aiy/leds.py` depends on Google's sysfs layout.
- `HACKING.md` requires `dtoverlay=spi0-1cs,cs0_pin=7` (GPIO6 must not be used as SPI CS).
  The `start_x=1` and `gpu_mem=128` lines are legacy-camera settings; don't carry them over to Bookworm.
- `setup.py` pulls in the Assistant and Cloud Speech libraries. Trim to the vision dependencies only.

## Baseline captured (2026-10-20)
- The reference card runs the official 2021-04-02 image: kernel 5.10.17+, Python 3.7.3, picamera 1.13, protobuf 3.14.0, gpiozero 1.5.1.
  The board is a Pi Zero W Rev 1.1 (`9000c1`). Don't `apt upgrade` this card.
- Reach it with `ssh pi@raspberrypi.local` (key auth works non-interactively) over USB gadget networking (`192.168.11.2`).
- `vendor/` is gitignored. Recreate `vendor/aiy-binaries.tgz` with `port/fetch-binaries.sh`, which downloads the official image from GitHub releases,
  verifies its SHA-256, and copies the files out with debugfs (local, or in Docker). `vendor/baseline/` (logs and photos) can't be recreated, but nothing needs it.
- `vendor/aiy-binaries.tgz` holds `lib/firmware/myriad_fw.mvcmd`, 9 models in `opt/aiy/models/*.binaryproto`,
  and the DKMS sources as installed. `vendor/baseline/` holds `system.txt`, `kernel-boot.log` and `hw-sw.txt`.
- `face_detection_camera.py --num_frames 150` runs cleanly at about 10–15 fps. That's the benchmark for the picamera2 port.
  Stop `joy_detection_demo` first because it holds the camera, and start it again afterwards.
- A normal boot logs `aiy-vision spi0.0: Failed to bind reset GPIO: -517` several times. That's EPROBE_DEFER while it waits
  for `gpio-aiy-io`, which is fine. It then logs "Resetting myriad", "Writing myriad firmware", "Myriad ready". Expect the same order on Bookworm.

## Trixie test card (current, 2026-10-20)
- `pi@vision-kit.local` is now a **Trixie** card: kernel `6.18.50+rpt-rpi-v6`, Python 3.13.5. It was set up only by `port/deploy.sh`, and passwordless sudo
  was added by hand in `/etc/sudoers.d/010_pi-nopasswd`. The Bookworm card below uses the same hostname, so check `uname -r` to see which is inserted.
- Python-only changes: rsync `port/python/` to the Pi and `sudo rsync` it into `/opt/aiy/python/` (editable install). That skips the 10-minute DKMS rebuild of a full `deploy.sh`.
- Driver code must build on both 6.12 and 6.18. Use `LINUX_VERSION_CODE` checks (see `gpio-aiy-io.c` and `pwm-soft.c`).

## Bookworm test card (2026-10-20)
- `ssh pi@vision-kit.local` (key auth). Bookworm Lite 32-bit, kernel `6.12.109+rpt-rpi-v6`, Python 3.11.2, protobuf 4.21.12.
  Only one card fits the Pi at a time, so if `raspberrypi.local` doesn't answer, the reference card isn't inserted.
- Phase 2 gate passed. Details are in `port/DEPENDENCIES.md` → Status.
- Work loop: edit `port/drivers/` on the Mac, rsync to `~/aiy-port/drivers/` **excluding build output**
  (`--exclude '*.ko' --exclude '*.o' --exclude '*.mod*' --exclude '.*.cmd' --exclude Module.symvers --exclude modules.order`;
  `--delete` without those excludes wipes the built modules), run `make -C <dir>` on the Pi, install to `/lib/modules/$(uname -r)/updates/aiy/`, then `depmod -a`.
- On the Pi: firmware is in `/lib/firmware/myriad_fw.mvcmd`, models in `/opt/aiy/models/`, the Python library is run from `~/aiy-port/src` via `PYTHONPATH`
  (no venv yet), and the test image is `~/aiy-port/view2.jpg`. `config.txt` has `dtoverlay=spi0-1cs,cs0_pin=7`; the original is backed up as `config.txt.orig`.
- `vendor/baseline/system.txt` contains NUL bytes, so use `grep -a`. The rtk wrapper hides grep's "Binary file matches" message; use `rtk proxy grep` to see it.
- Python work copy: edit `port/python/src/` and rsync it to `~/aiy-port/src/` (excluding `__pycache__`). Device tests are in `port/tests/` → `~/aiy-port/tests/`.
  Set `LIBCAMERA_LOG_LEVELS=*:WARN` to quiet libcamera. Only one process can open the camera at a time.
- **Since Phase 6 the card is set up by `port/install.sh`** (`port/deploy.sh pi@vision-kit.local`). The installed system is in `/opt/aiy` (venv `/opt/aiy/venv/bin/python`,
  library `/opt/aiy/python`) plus DKMS `aiy-vision-kit`. `~/aiy-port` on the Pi is a leftover development copy and isn't used by the service.
  Run tests with `/opt/aiy/venv/bin/python`, and stop `joy_detection_demo` first because it holds the camera and LEDs. `dkms` is in `/usr/sbin`, which isn't on `pi`'s PATH over ssh.
- Phase 5 setup on the Pi (now done by `install.sh`): `/etc/modules-load.d/pwm-soft.conf`, `/etc/udev/rules.d/60-aiy-*.rules`
  (from `port/udev/`), and apt packages `build-essential dkms device-tree-compiler gpiod python3-protobuf python3-pil python3-numpy python3-picamera2 fonts-freefont-ttf`.
- Hardware test: `PYTHONPATH=~/aiy-port/src python3 ~/aiy-port/tests/hardware_check.py [--button SECONDS]`, run as `pi`, not root (sudo drops PYTHONPATH).
- The camera shim is `aiy/camera.py`. Examples import `from aiy.camera import PiCamera` (or `from aiy import camera as picamera`).
- The Mac's clang diagnostics on `port/drivers/*.c` are noise because it has no kernel headers. The Pi's gcc is what counts.

## Conventions
- `docs/` holds read-only snapshots. Don't edit them; re-fetch instead. Each vendored tree has a `COMMIT` file, and each fetched page has a `source:` header.
- Put new work in `port/` (drivers, Python shim, `install.sh`) and extracted binaries in `vendor/`, which stays out of git.
- Target paths on the Pi: `/boot/firmware/config.txt`, venv at `~/aiy-venv` created with `--system-site-packages` (so it can see apt's `python3-picamera2`).
- DKMS builds on a Pi Zero are slow (tens of minutes). Prefer building in a container or Pi 3/4 running the same kernel headers when iterating.
- Diagrams: mermaid, not ASCII.

## Verification checkpoints
1. `dmesg | grep -i "Myriad ready"` and `/dev/vision_spicomm` exists.
2. `ImageInference` on a still JPEG returns faces.
3. `CameraInference` with picamera2 at 1640×1232 returns results.
4. Button press, RGB LED, buzzer and privacy LED all work.
