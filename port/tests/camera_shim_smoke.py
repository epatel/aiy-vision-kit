#!/usr/bin/env python3
"""Exercises the aiy.camera picamera shim: capture, recording, circular buffer, reconfigure."""
import io
import os
import tempfile
import time

from PIL import Image

from aiy.camera import PiCamera, PiCameraCircularIO, Color


def check(name, ok, detail=''):
    print('%-28s %s %s' % (name, 'OK  ' if ok else 'FAIL', detail), flush=True)
    return ok


def main():
    out = tempfile.mkdtemp(prefix='aiy-shim-')
    results = []
    with PiCamera(sensor_mode=4, resolution=(820, 616), framerate=30) as camera:
        camera.start_preview()
        time.sleep(2)  # Let AE settle.

        stream = io.BytesIO()
        t = time.monotonic()
        camera.capture(stream, format='jpeg', use_video_port=True)
        image = Image.open(io.BytesIO(stream.getvalue()))
        results.append(check('capture jpeg (BytesIO)', image.size == (820, 616),
                             '%s %.2fs' % (image.size, time.monotonic() - t)))

        path = os.path.join(out, 'still.png')
        camera.annotate_text = 'hello'
        camera.annotate_background = Color('black')
        camera.capture(path)
        camera.annotate_text = ''
        results.append(check('capture png (path)', Image.open(path).size == (820, 616)))

        circ = PiCameraCircularIO(camera, seconds=3)
        camera.start_recording(circ, format='h264', profile='baseline', inline_headers=True)
        camera.wait_recording(4)
        clip = os.path.join(out, 'clip.h264')
        circ.copy_to(clip)
        camera.stop_recording()
        size = os.path.getsize(clip)
        with open(clip, 'rb') as f:
            head = f.read(4)
        results.append(check('circular h264 copy_to', size > 10000 and head == b'\x00\x00\x00\x01',
                             '%d bytes' % size))

        camera.resolution = (1640, 1232)
        stream = io.BytesIO()
        camera.capture(stream, format='jpeg')
        image = Image.open(io.BytesIO(stream.getvalue()))
        results.append(check('resolution change', image.size == (1640, 1232), str(image.size)))

        camera.stop_preview()
    print('ALL OK' if all(results) else 'SOME FAILED', '- files in', out)


if __name__ == '__main__':
    main()
