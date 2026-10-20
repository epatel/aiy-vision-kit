#!/usr/bin/env python3
"""Blinks the arcade button LED and logs presses until --timeout seconds pass.

Meant to run in the background while someone presses the button:
    nohup python3 button_wait.py --presses 3 > /tmp/button.log 2>&1 &
"""
import argparse
import time

from aiy.board import Board, Led
from aiy.toneplayer import TonePlayer


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--timeout', type=int, default=600)
    parser.add_argument('--presses', type=int, default=3)
    args = parser.parse_args()

    player = TonePlayer(gpio=22, bpm=480)
    start = time.monotonic()
    with Board() as board:
        board.led.state = Led.BLINK
        print('waiting for %d presses (timeout %d s)' % (args.presses, args.timeout), flush=True)
        count = 0
        while count < args.presses:
            remaining = args.timeout - (time.monotonic() - start)
            if remaining <= 0 or not board.button.wait_for_press(remaining):
                print('TIMEOUT after %d presses' % count, flush=True)
                break
            count += 1
            print('press %d at %.1f s' % (count, time.monotonic() - start), flush=True)
            board.led.state = Led.ON
            player.play('C6q')
            board.button.wait_for_release(5)
            board.led.state = Led.BLINK
        else:
            print('BUTTON OK: %d presses' % count, flush=True)
        board.led.state = Led.OFF


if __name__ == '__main__':
    main()
