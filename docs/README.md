# docs/ — reference material

Snapshots taken on **2026-10-20**. Treat everything here as read-only reference; do not edit
vendored files. Re-fetch rather than patch.

## Vendored sources

| Path | What | Upstream |
|---|---|---|
| [`aiyprojects-raspbian/`](aiyprojects-raspbian/) | Google AIY repo: kernel drivers, overlays, Python `aiy` library, examples, schematics. Commit in `COMMIT`. Last upstream change 2021-04-15. | <https://github.com/google/aiyprojects-raspbian> |
| [`reference/picamera2/`](reference/picamera2/) | Picamera2 library source; the manual PDF has the examples (replacement for `picamera`). Commit in `COMMIT`. | <https://github.com/raspberrypi/picamera2> |
| [`reference/rpi-documentation/`](reference/rpi-documentation/) | Raspberry Pi official docs, AsciiDoc source only (os, config_txt, camera, linux_kernel, configuration, raspberry-pi, accessories/camera). Commit in `COMMIT`. | <https://github.com/raspberrypi/documentation> |

### Most useful files inside the AIY repo

| File | Why |
|---|---|
| [`HACKING.md`](aiyprojects-raspbian/HACKING.md) | How the stock stack is installed on plain Raspbian: package list, `config.txt` lines, `dmesg` check (`Myriad ready`). |
| [`CHANGES.md`](aiyprojects-raspbian/CHANGES.md) | Image release history. |
| [`drivers/vision/aiy-vision.c`](aiyprojects-raspbian/drivers/vision/aiy-vision.c) | Myriad SPI driver → `/dev/vision_spicomm`, loads `myriad_fw.mvcmd`. |
| [`drivers/aiy/aiy/`](aiyprojects-raspbian/drivers/aiy/aiy/) | Bonnet MCU drivers: `aiy-io-i2c` (mfd), `gpio-aiy-io`, `pwm-aiy-io`, `aiy-adc`. |
| [`drivers/leds/leds-ktd202x.c`](aiyprojects-raspbian/drivers/leds/leds-ktd202x.c) | RGB button LED driver. |
| [`drivers/pwm/pwm-soft.c`](aiyprojects-raspbian/drivers/pwm/pwm-soft.c) | Software PWM for the piezo buzzer. |
| [`drivers/overlays/vision/.../aiy-visionbonnet-overlay.dts`](aiyprojects-raspbian/drivers/overlays/vision/opt/aiy/overlay-vision/aiy-visionbonnet-overlay.dts) | Device tree (normally read from the bonnet EEPROM). |
| [`src/aiy/vision/_spicomm.py`](aiyprojects-raspbian/src/aiy/vision/_spicomm.py) | Python ↔ driver ioctl protocol. |
| [`src/aiy/vision/inference.py`](aiyprojects-raspbian/src/aiy/vision/inference.py) | `CameraInference`, `ImageInference`. |
| [`src/aiy/pins.py`](aiyprojects-raspbian/src/aiy/pins.py) | gpiozero pin factory over sysfs GPIO/PWM. |
| [`src/examples/vision/`](aiyprojects-raspbian/src/examples/vision/) | Demos; all use `picamera` with `sensor_mode=4` (1640×1232). |
| [`schematics/`](aiyprojects-raspbian/schematics/) | Bonnet schematics. |

## Fetched pages (`reference/`)

HTML converted to Markdown with pandoc; each file has a `source:` header.

**AIY**
- [aiy-vision-kit-v1.md](reference/aiy-vision-kit-v1.md) — the kit's assembly and usage guide
- [aiy-models.md](reference/aiy-models.md) — the models that ship for the kit
- [aiy-readthedocs-vision.md](reference/aiy-readthedocs-vision.md), [aiy-readthedocs-inference.md](reference/aiy-readthedocs-inference.md) — Python API

**Raspberry Pi OS**
- [rpi-news-bullseye-camera.md](reference/rpi-news-bullseye-camera.md) — why the legacy camera stack and `picamera` went away
- [rpi-news-bookworm.md](reference/rpi-news-bookworm.md), [rpi-news-trixie.md](reference/rpi-news-trixie.md) — release notes
- [picamera2-manual.pdf](reference/picamera2-manual.pdf) — Picamera2 manual (86 pages)
- [rpi-dt-overlays-README.txt](reference/rpi-dt-overlays-README.txt) — all overlays and their params (`spi0-1cs`, etc.), kernel branch rpi-6.12.y
- `rpi-documentation/documentation/asciidoc/computers/`:
  [os](reference/rpi-documentation/documentation/asciidoc/computers/os/),
  [config_txt](reference/rpi-documentation/documentation/asciidoc/computers/config_txt/),
  [camera](reference/rpi-documentation/documentation/asciidoc/computers/camera/),
  [linux_kernel](reference/rpi-documentation/documentation/asciidoc/computers/linux_kernel/)

**Linux kernel / userspace**
- [kernel-gpio-consumer.md](reference/kernel-gpio-consumer.md) — gpiod descriptor API (used by `aiy-vision.c`)
- [kernel-gpio-sysfs.md](reference/kernel-gpio-sysfs.md) — deprecated sysfs GPIO (used by `aiy/pins.py`)
- [kernel-gpio-chardev.md](reference/kernel-gpio-chardev.md) — the replacement character device ABI
- [kernel-spi-summary.md](reference/kernel-spi-summary.md), [kernel-firmware-api.md](reference/kernel-firmware-api.md), [kernel-pwm.md](reference/kernel-pwm.md), [kernel-leds-class.md](reference/kernel-leds-class.md)
- [dkms-manpage.md](reference/dkms-manpage.md)
- [libgpiod-README.md](reference/libgpiod-README.md), [libgpiod-python-README.md](reference/libgpiod-python-README.md)
- [gpiozero-pins.md](reference/gpiozero-pins.md) — pin factories (lgpio, native)
- [protobuf-python-news.md](reference/protobuf-python-news.md) — protobuf 4.x Python breaking change

## Not here (and why)

- **Myriad firmware and the models** (`aiy-vision-firmware`, `aiy-models` .debs). Google's apt repo
  `packages.cloud.google.com/apt … aiyprojects-stable` returns **404** (checked 2026-10-20). The only remaining
  copy is inside the system images on the
  [GitHub releases page](https://github.com/google/aiyprojects-raspbian/releases) (latest
  `aiyprojects-2021-04-02.img.xz`, 1.1 GB), or on your current SD card. They're binaries, so extract them to `../vendor/`, not here.
