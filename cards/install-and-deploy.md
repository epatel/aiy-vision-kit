# install-and-deploy

The scripts in `port/` that turn a freshly flashed card into a working Vision Kit, what each step installs, and the quick paths for updating a card that's already set up.

## The scripts

The Makefile wraps them: `make fetch`, `make deploy [HOST=… ARGS=…]`, `make reboot`, `make uninstall`, `make status`.


| Script | Runs on | Does |
|---|---|---|
| `fetch-binaries.sh` | the Mac/Linux box | Downloads `aiyprojects-2021-04-02.img.xz` (1.2 GB, cached in `vendor/cache/`, resumable), checks the published SHA-256, carves out the root partition with Python, copies `/lib/firmware/myriad_fw.mvcmd` and `/opt/aiy/models/` out with `debugfs` (local, or in a `debian:bookworm-slim` container), checks the firmware SHA-256 and that there are 15 model files, writes `vendor/aiy-binaries.tgz`. Needs about 6 GB free while running. |
| `deploy.sh pi@HOST [opts]` | the Mac | rsyncs `port/` to `~/vision-kit-port/` (without build output) and the archive, then `ssh -t … sudo ./install.sh --binaries aiy-binaries.tgz [opts]` |
| `install.sh` | the Pi, as root | Everything below. Safe to re-run. Options `--no-joy-service`, `--streaming`, `--hold-kernel`, `--user NAME` |
| `uninstall.sh` | the Pi, as root | Removes what install added (apt packages stay). Removes the `config.txt` block between the markers |

## install.sh, in order

1. Checks: root, archive given, run from `port/`, OS codename `bookworm` or `trixie` (read in a **subshell**: sourcing `/etc/os-release` defines `VERSION`, which once
   overwrote the script's own version), bonnet in `/proc/device-tree/hat` (a warning only).
2. apt: `dkms build-essential linux-headers-$(uname -r) gpiod python3-venv python3-setuptools python3-protobuf python3-pil python3-numpy python3-picamera2 python3-gpiozero python3-lgpio python3-rpi-lgpio fonts-freefont-ttf avahi-utils`.
   On a fresh Trixie Lite card this is the slowest step (picamera2 pulls in libcamera and ffmpeg libraries). `python3-setuptools` is needed because 3.12+ venvs don't include it;
   `fonts-freefont-ttf` because the Joy Detector hard-codes FreeSans and Lite lacks it.
3. Firmware + models from the archive (SHA-256 checked) → `/lib/firmware/`, `/opt/aiy/models/`.
4. DKMS: removes hand-installed `/lib/modules/*/updates/aiy` and old `aiy-vision-kit` versions, copies `drivers/` to `/usr/src/aiy-vision-kit-2.0.0`, then add/build/install
   for the running kernel. **About 10 minutes on a Pi Zero, on every run**, even when nothing changed.
5. udev rules, `/etc/modules-load.d/pwm-soft.conf`, `usermod -aG gpio,i2c,spi,video`.
6. `config.txt`: appends a block marked `# >>> aiy-vision-kit` … `# <<< aiy-vision-kit` with `dtoverlay=spi0-1cs,cs0_pin=7` (only if missing). A reboot is needed after the first install.
7. Python: copies `python/` to `/opt/aiy/python`, creates `/opt/aiy/venv --system-site-packages`, then `pip install --no-index --no-build-isolation -e /opt/aiy/python`
   (offline; every dependency comes from apt). Then an import check.
8. Writes `joy_detection_demo.service` (user, `WorkingDirectory=~`, args) and enables it unless `--no-joy-service`.

## Card prerequisites

- Raspberry Pi OS **Lite 32-bit**, Bookworm or Trixie. Set hostname, user, Wi-Fi and SSH key in Imager.
- **Passwordless sudo** for `deploy.sh` (it runs `sudo` over a non-interactive ssh). Bookworm Imager images give the first user that; **Trixie doesn't**. Run once:
  `ssh -t pi@HOST 'echo "pi ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/010_pi-nopasswd && sudo chmod 0440 /etc/sudoers.d/010_pi-nopasswd'`.
- `vendor/aiy-binaries.tgz` on the Mac (`port/fetch-binaries.sh`).

## Quick updates (skip the 10-minute rebuild)

- **Python only:** `rsync -a --exclude __pycache__ port/python/ pi@HOST:vision-kit-port/python/`, then on the Pi `sudo rsync -a --exclude '*.egg-info' ~/vision-kit-port/python/ /opt/aiy/python/`
  and `sudo systemctl restart joy_detection_demo`. The editable install picks it up. For a single file: `scp` to `/tmp`, then `sudo install -m 644`.
- **Service args:** edit `/etc/systemd/system/joy_detection_demo.service`, `daemon-reload`, restart. The next `deploy.sh` rewrites it from `port/systemd/joy_detection_demo.service`.
- **Drivers:** build by hand on the Pi from a copy of `port/drivers/` (see `make -C <dir>`), or run `deploy.sh` and wait.

## Gotchas

- `deploy.sh` needs `ssh -t`; from a non-tty shell you get "Pseudo-terminal will not be allocated", which is harmless.
- When a deploy's output is piped through `tail`, a failure can look like exit code 0. Write to a log and keep `$?`.
- DKMS builds only for the running kernel at install time. On later kernel upgrades DKMS's own hook builds for each new kernel whose headers are installed.
- After `uninstall.sh` and a reboot, `lsmod | grep aiy` is empty and `/opt/aiy` is gone. An empty `[all]` line can remain from hand-edited configs; it's harmless.
