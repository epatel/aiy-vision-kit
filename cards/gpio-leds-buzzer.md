# gpio-leds-buzzer

The arcade button, RGB/privacy LEDs, buzzer and expansion pins (PIN_A..D, LED_1/2), as seen from Python (`aiy/pins.py`, `aiy/leds.py`, `aiy/_buzzer.py`, `aiy/board.py`), and the traps found porting them.

## What drives what

| Thing | Hardware | Kernel interface | Python |
|---|---|---|---|
| Arcade button | BCM GPIO 23 | SoC gpiochip | `aiy.board.Board().button` (gpiozero, lgpio backend) |
| Button LED (Board.led) | BCM GPIO 25 | SoC gpiochip | `Board().led` |
| RGB LED + privacy LED | KTD2026 @ I2C 0x30 | `leds-ktd202x` → `/sys/class/leds/ktd202x:led1..4/device/…` (Google's sysfs) | `aiy.leds.Leds` |
| Buzzer | BCM GPIO 22 | `pwm-soft` → `/sys/class/pwm-soft/{export,pwmN}` | `aiy.toneplayer.TonePlayer(gpio=22)` |
| PIN_A..D, LED_1/2 | MCU lines via `gpio-aiy-io` / `pwm-aiy-io` | sysfs GPIO + `/sys/class/pwm/pwmchipN` | `aiy.pins.PIN_A` etc. with gpiozero `LED`, `PWMOutputDevice`, … |

## Traps (all fixed in `port/python`)

- **gpiozero 2.x.** Devices reserve pins through `pin_factory.board_info`, which only knows the Pi header. AIY's `HybridFactory` now keeps its own
  reservation table for `AIYPinSpec` pins and passes everything else to the default lgpio factory. `HatPin` provides `info.name` (the spec itself),
  because devices release reservations by `pin.info.name`. `RPi.GPIO` imports come from `python3-rpi-lgpio`.
- **The closed-pin cache.** `HatFactory` cached pins in a class-level dict and handed a *closed* pin to the next device on the same pin, which then did nothing.
  `pin()` now makes a fresh `HatPin` when the cached one is closed.
- **Export directory name.** On 6.12 an exported line appears as `/sys/class/gpio/AIY_USER0` (named after the line); on 6.18 always as `gpio<N>`.
  `SysFsPin.export()` uses whichever appears, and both of its waits time out after 5 s (they used to loop forever, which looked like a hang).
- **GPIO base 512.** The SoC gpiochip base moved to 512 in 6.6. `pwm-soft` takes global numbers, so `_buzzer.py` adds the base of the `pinctrl-bcm2835` chip (BCM22 → 534).
  The AIY chip's base is dynamic too (566 here); `pins.py` reads it from sysfs.
- **pwmchip number.** `pins.py` finds the `pwm-aiy-io` pwmchip by device name instead of assuming `pwmchip0`.
- **Reading back an output.** For the MCU, `/sys/class/gpio/…/value` of an *output* returns the input register, so it always reads 0. To check that a pin
  really toggled, read the MCU output-level register 0x21 (bit = line offset) through `sudo cat /sys/kernel/debug/regmap/1-0051/registers`.
- **Permissions.** Without Google's udev rules (`port/udev/60-aiy-*.rules`), user `pi` gets EACCES on the LED and pwm-soft sysfs files.
  The rules give group `gpio` access; `install.sh` installs them and adds the user to `gpio,i2c,spi,video`. The pwm-soft rule fires when the class is registered,
  so after installing it by hand you need `modprobe -r pwm-soft && modprobe pwm-soft`.
- **lgpio working directory.** lgpio creates `.lgd-nfy*` files in the current directory. A systemd service starts in `/`, so units must set `WorkingDirectory=~`.
- **Mainline ktd202x.** The upstream kernel has its own `leds-ktd202x` with the same `kinetic,ktd2026` compatible string but a different sysfs layout.
  `bcmrpi_defconfig` doesn't build it. If a future kernel does, blacklist it, because `aiy/leds.py` needs Google's driver.

## Checking

- `/opt/aiy/venv/bin/python port/tests/hardware_check.py` (copied to the Pi) checks: RGB red/green/blue and privacy LED (KTD brightness readback), LEDs off,
  the buzzer (a pwm-soft export appears in dmesg), PIN_A output (MCU register 0x21), LED_1, and PIN_A PWM at 25 % / 1 kHz (sysfs period/duty).
  `--button SECONDS` also waits for a press. Run it as `pi`; sudo drops `PYTHONPATH`, and the venv makes it unnecessary.
- `port/tests/button_wait.py` blinks the LED and logs N presses. Run it in the background while someone presses the button.
- The ADC reads supply rails: `cat /sys/bus/iio/devices/iio:device0/in_voltage4_v3p3_input` gives about 3300 (mV).
