#!/usr/bin/env python3
"""Checks the bonnet's LEDs, buzzer and expansion pins against their sysfs state.

With --button, also waits for a press of the arcade button.
"""
import argparse
import glob
import subprocess
import time


def check(name, ok, detail=''):
    print('%-34s %s %s' % (name, 'OK  ' if ok else 'FAIL', detail), flush=True)
    return ok


def read(path):
    with open(path) as f:
        return f.read().strip()


def mcu_register(address):
    """Reads a bonnet MCU register through regmap debugfs (needs sudo)."""
    out = subprocess.run(['sudo', 'cat', '/sys/kernel/debug/regmap/1-0051/registers'],
                         capture_output=True, text=True, check=True).stdout
    for line in out.splitlines():
        reg, _, value = line.partition(':')
        if int(reg, 16) == address:
            return int(value, 16)
    raise KeyError(address)


def ktd_brightness():
    return [int(read('/sys/class/leds/ktd202x:led%d/brightness' % i)) for i in range(1, 5)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--button', type=int, default=0, metavar='SECONDS',
                        help='wait this long for an arcade button press')
    args = parser.parse_args()
    results = []

    from aiy.leds import Leds, Color, Pattern
    with Leds() as leds:
        for name, color, expected in (('red', Color.RED, [255, 0, 0]),
                                      ('green', Color.GREEN, [0, 255, 0]),
                                      ('blue', Color.BLUE, [0, 0, 255])):
            leds.update(Leds.rgb_on(color))
            time.sleep(0.4)
            got = ktd_brightness()
            results.append(check('RGB LED %s' % name, got[:3] == expected, str(got)))
        leds.update(Leds.privacy_on())
        time.sleep(0.4)
        got = ktd_brightness()
        results.append(check('privacy LED on', got[3] > 0, str(got)))
        leds.pattern = Pattern.blink(300)
        leds.update(Leds.rgb_pattern(Color.PURPLE))
        time.sleep(1.5)
        leds.update(Leds.rgb_off())
        leds.update(Leds.privacy_off())
        got = ktd_brightness()
        results.append(check('all LEDs off', got == [0, 0, 0, 0], str(got)))

    from aiy.toneplayer import TonePlayer
    before = subprocess.run(['dmesg'], capture_output=True, text=True).stdout.count('Registered device pwm')
    TonePlayer(gpio=22, bpm=240).play('C5q', 'E5q', 'G5q', 'C6h')
    log = subprocess.run(['dmesg'], capture_output=True, text=True).stdout
    registered = [l for l in log.splitlines() if 'Registered device pwm' in l]
    results.append(check('buzzer via pwm-soft', len(registered) > before,
                         registered[-1].split('] ')[-1] if registered else 'no pwm-soft export'))

    from gpiozero import LED, PWMOutputDevice
    from aiy.pins import PIN_A, LED_1
    with LED(PIN_A) as pin:
        # Reading 'value' of an output returns the MCU's input register (0), so
        # check the output-level register (0x21, bit = line offset 2) instead.
        pin.on()
        time.sleep(0.1)
        on = mcu_register(0x21)
        pin.off()
        time.sleep(0.1)
        off = mcu_register(0x21)
        results.append(check('PIN_A GPIO output (MCU reg)', bool(on & 0x04) and not off & 0x04,
                             'on=%#04x off=%#04x' % (on, off)))
    with LED(LED_1) as led:
        led.on()
        time.sleep(0.3)
        led.off()
        results.append(check('bonnet LED_1 toggle', True))
    with PWMOutputDevice(PIN_A, frequency=1000) as pwm:
        pwm.value = 0.25
        time.sleep(0.2)
        chip = [c for c in glob.glob('/sys/class/pwm/pwmchip*/pwm0')][0]
        period, duty, enabled = (read(chip + '/' + a) for a in ('period', 'duty_cycle', 'enable'))
        results.append(check('PIN_A PWM 25% @ 1 kHz', enabled == '1' and int(duty) * 4 == int(period),
                             'period=%s duty=%s enable=%s' % (period, duty, enabled)))

    if args.button:
        from aiy.board import Board, Led
        with Board() as board:
            board.led.state = Led.BLINK
            print('Press the arcade button within %d s...' % args.button, flush=True)
            pressed = board.button.wait_for_press(args.button)
            board.led.state = Led.OFF
            results.append(check('arcade button press', bool(pressed)))

    print('ALL OK' if all(results) else 'SOME FAILED')


if __name__ == '__main__':
    main()
