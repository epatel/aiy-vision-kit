# kernel-drivers

The seven out-of-tree Vision Bonnet modules in `port/drivers/`: how they are built, what had to change for kernels 6.12 (Bookworm) and 6.18 (Trixie), and how to iterate on them.

## Source and build

- One DKMS package, `aiy-vision-kit` (`port/drivers/dkms.conf`). Its `MAKE[0]` runs `make -C vision`, `leds`, `pwm` and `aiy` with `KVERSION`/`KVER=${kernelver}`.
  Google shipped four packages; one is simpler and they always move together.
- Subdirectories: `vision/aiy-vision.c` (Myriad, SPI), `aiy/aiy/{mfd,gpio,pwm,iio/adc}/` (MCU), `leds/leds-ktd202x.c`, `pwm/pwm-soft.c`.
- The Makefiles use `M=$(CURDIR)`. Upstream had `$(PWD)`, which points at the wrong directory under `make -C`.
- **The same source must build on both 6.12 and 6.18.** Put version-specific code behind `LINUX_VERSION_CODE >= KERNEL_VERSION(x, y, 0)` and keep the old path unchanged.
- A full build takes about 10 minutes on a Pi Zero (single core).

## API changes already handled

| Change | Kernel | Where |
|---|---|---|
| `class_create(name)` lost the `THIS_MODULE` argument | 6.4 | `aiy-vision.c` |
| `vma->vm_flags` is read-only → `vm_flags_set()` | 6.3 | `aiy-vision.c` mmap |
| `spi_busnum_to_master()` removed (the check was dropped) | 5.x/6.x | `aiy-vision.c` probe |
| `spi->cs_gpio` removed → `spi_set_csgpiod(spi, 0, NULL)` | 6.x | `aiy-vision.c` |
| class `dev_uevent` takes `const struct device *` | 6.2 | `aiy-vision.c` |
| `of_match_ptr` needs `<linux/of.h>`; `gpio_chip` needs `<linux/gpio/driver.h>` | 6.x | several |
| SPI, I2C and platform `remove()` return `void` | 6.1 / 6.1 / 6.11 | all drivers |
| I2C `probe(client)` has one argument (use `i2c_client_get_device_id()`) | 6.3 | `aiy-io-i2c.c`, `leds-ktd202x.c` |
| `iio_dev.driver_module` removed | 6.x | `aiy-adc.c` |
| PWM legacy `.config/.enable/.disable` removed and `pwm_chip` embeds a `struct device` → `.apply()` + `devm_pwmchip_alloc()` + `pwmchip_get_drvdata()` | 6.x | `pwm-aiy-io.c` (rewritten) |
| `struct class.owner` removed; class attribute callbacks take `const` | 6.4 | `pwm-soft.c` |
| `ARCH_NR_GPIOS` removed (fallback 1024); `__gpio_set_value` → `gpio_set_value` | 6.x | `pwm-soft.c` |
| `gpio_chip.set` returns `int` | **6.17** | `gpio-aiy-io.c` (version check) |
| `hrtimer_init()` → `hrtimer_setup()` | **6.13** | `pwm-soft.c` (version check) |

Fixed bugs that weren't API changes:
- `pwm-soft` used the user-written GPIO number as an unchecked table index. There is now a bounds check.
- `aiy-adc` declared each channel twice (RAW and PROCESSED specs with the same `extend_name`). Newer IIO creates `*_label` from it, which gave `-EBUSY`.
  Each channel is now one spec with both info bits.
- `aiy-vision` had a `spi_device_id` table that was never wired up (`.id_table`), which caused a warning at load.

Still in use, so watch them on new kernels: the legacy integer GPIO API in `pwm-soft` (`CONFIG_GPIOLIB_LEGACY=y` on 6.18) and sysfs GPIO for `aiy/pins.py`
(`CONFIG_GPIO_SYSFS=y`). The SoC gpiochip base is **512** since 6.6, so BCM22 is global GPIO 534.

## Iterating without a full deploy

1. Edit on the Mac. The Mac's clang errors about missing `linux/*.h` are noise; only the Pi's gcc counts.
2. Copy to the Pi **without build output**:
   `rsync -a --exclude debian --exclude '*.ko' --exclude '*.o' --exclude '*.mod*' --exclude '.*.cmd' --exclude Module.symvers --exclude modules.order port/drivers/ pi@HOST:build/drivers/`
   (with `--delete` but without the excludes, rsync wipes modules already built on the Pi).
3. On the Pi: `make -C build/drivers/<dir>`. Compile errors show up in seconds, so fixing one at a time is quick.
4. To try a module by hand: `sudo rmmod <mod>; sudo insmod <path>.ko` or install it into `updates/` + `depmod -a`. `install.sh` removes `/lib/modules/*/updates/aiy`
   (old hand-installed copies would shadow the DKMS ones).
5. To finish, run `port/deploy.sh pi@HOST`, which rebuilds through DKMS.

Checking on the Pi: `sudo dmesg | grep -E "Myriad ready|SoftPWM|Driver loaded"`, `/usr/sbin/dkms status` (`dkms` isn't on `pi`'s PATH over ssh), `ls -l /dev/vision_spicomm`.

## Device tree

The overlay comes from the bonnet's EEPROM and needs no `dtoverlay=` line. `install.sh` only adds `dtoverlay=spi0-1cs,cs0_pin=7`, from Google's `HACKING.md`:
it moves the SPI controller's CS0 to GPIO7, so GPIO6/8 stay free for the driver's own chip-select and IRQ lines. Don't add `start_x=1` or `gpu_mem=128`;
they are legacy-camera settings.
