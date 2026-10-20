# Licensed under the Apache License, Version 2.0.
"""picamera-compatible camera for the Vision Kit on libcamera (Picamera2).

The Vision Bonnet runs inference on the raw CSI-2 stream as it passes to the Pi, so
all it needs is the sensor streaming in the 1640x1232 binned mode (picamera
``sensor_mode=4``). This module keeps the subset of the picamera 1.13 API used by the
AIY examples so they only need their import changed::

    from aiy.camera import PiCamera

    with PiCamera(sensor_mode=4, resolution=(1640, 1232), framerate=30) as camera:
        camera.start_preview()
        ...

Differences from picamera:
  * The sensor starts streaming when the camera is opened (picamera did the same as
    far as the bonnet is concerned) and keeps streaming until ``close()``.
  * ``start_preview()`` only shows a DRM preview when an HDMI display is connected,
    or when ``AIY_CAMERA_PREVIEW=1``; ``AIY_CAMERA_PREVIEW=0`` disables it.
  * ``annotate_text`` is drawn on captured images only, not on the preview or video.
  * ``request_key_frame()`` is a no-op; H.264 always repeats headers and has an
    I-frame every ``intra_period`` frames (default: one per second).
  * Supported capture formats: jpeg, png, bmp, gif, rgb, bgr. Recording: h264, mjpeg.
"""

import collections
import glob
import io
import logging
import os
import threading
import time

import numpy as np
from PIL import ImageDraw

from picamera2 import Picamera2, Preview
from picamera2.encoders import H264Encoder, MJPEGEncoder
from picamera2.outputs import Output

logger = logging.getLogger(__name__)

# picamera sensor modes of Camera Module v2 (imx219) mapped to the libcamera sensor
# output size with the same field of view. Modes 5 and 6 were binned crops which
# libcamera doesn't offer, so they fall back to the full-FoV binned mode.
SENSOR_MODES = {
    0: (1640, 1232),  # picamera picked a mode automatically; use the bonnet's mode.
    1: (1920, 1080),
    2: (3280, 2464),
    3: (3280, 2464),
    4: (1640, 1232),
    5: (1640, 1232),
    6: (1640, 1232),
    7: (640, 480),
}

_CAPTURE_FORMATS = {'jpeg': 'JPEG', 'jpg': 'JPEG', 'png': 'PNG', 'bmp': 'BMP', 'gif': 'GIF'}

Resolution = collections.namedtuple('Resolution', ('width', 'height'))


class PiCameraError(Exception):
    """Raised for unsupported or invalid operations."""


class Color(str):
    """Stand-in for picamera.Color; any PIL color name or '#rrggbb' works."""


def _display_connected():
    for status in glob.glob('/sys/class/drm/card*-HDMI-A-*/status'):
        try:
            with open(status) as f:
                if f.read().strip() == 'connected':
                    return True
        except OSError:
            pass
    return False


def _preview_wanted():
    env = os.environ.get('AIY_CAMERA_PREVIEW')
    if env is not None:
        return env not in ('0', 'no', 'false', '')
    return _display_connected()


class _Overlay:
    """Returned by PiCamera.add_overlay(); mirrors picamera's renderer.update()."""

    def __init__(self, camera, size):
        self._camera = camera
        self._size = tuple(size)

    def update(self, source):
        width, height = self._size
        array = np.frombuffer(source, dtype=np.uint8).reshape((height, width, 4))
        self._camera._set_overlay(array)

    def close(self):
        self._camera._set_overlay(None)


class _ForwardOutput(Output):
    """Sends each encoded frame to a file-like object or a PiCameraCircularIO."""

    def __init__(self, target):
        super().__init__()
        self._target = target

    def outputframe(self, frame, keyframe=True, timestamp=None, packet=None, audio=False):
        if audio:
            return
        if isinstance(self._target, PiCameraCircularIO):
            self._target._add_frame(bytes(frame), keyframe, timestamp)
        else:
            self._target.write(frame)


class PiCameraCircularIO:
    """Keeps the last `seconds` of encoded video in memory, like picamera's class."""

    def __init__(self, camera, size=None, seconds=None, bitrate=17000000, splitter_port=1):
        if seconds is None and size is None:
            raise PiCameraError('Either size or seconds must be given')
        self._seconds = seconds
        self._size = size
        self._frames = collections.deque()  # (time, keyframe, data)
        self._bytes = 0
        self._lock = threading.Lock()

    def _add_frame(self, data, keyframe, timestamp):
        now = time.monotonic()
        with self._lock:
            self._frames.append((now, keyframe, data))
            self._bytes += len(data)
            while self._frames and (
                    (self._seconds is not None and now - self._frames[0][0] > self._seconds) or
                    (self._size is not None and self._bytes > self._size)):
                self._bytes -= len(self._frames.popleft()[2])

    def write(self, data):
        self._add_frame(bytes(data), True, None)
        return len(data)

    def copy_to(self, output, size=None, seconds=None, first_frame=None):
        """Writes buffered video to `output` (path or file), starting at a keyframe."""
        with self._lock:
            frames = list(self._frames)
        if seconds is not None and frames:
            cutoff = frames[-1][0] - seconds
            frames = [f for f in frames if f[0] >= cutoff]
        while frames and not frames[0][1]:
            frames.pop(0)
        own = isinstance(output, str)
        out = open(output, 'wb') if own else output
        try:
            written = 0
            for _, _, data in frames:
                if size is not None and written + len(data) > size:
                    break
                out.write(data)
                written += len(data)
        finally:
            if own:
                out.close()

    def clear(self):
        with self._lock:
            self._frames.clear()
            self._bytes = 0

    def flush(self):
        pass

    def close(self):
        self.clear()


class PiCamera:
    """Subset of picamera.PiCamera on top of Picamera2."""

    def __init__(self, camera_num=0, stereo_mode='none', stereo_decimate=False,
                 resolution=None, framerate=None, sensor_mode=0, **kwargs):
        if sensor_mode not in SENSOR_MODES:
            raise PiCameraError('Unsupported sensor_mode %r' % sensor_mode)
        self._sensor_mode = sensor_mode
        self._sensor_size = SENSOR_MODES[sensor_mode]
        self._resolution = Resolution(*(resolution or self._sensor_size))
        self._framerate = framerate or 30
        self._lock = threading.RLock()
        self._encoder = None
        self._encoder_file = None
        self._preview = False
        self._closed = False

        self.annotate_text = ''
        self.annotate_text_size = 32
        self.annotate_foreground = Color('white')
        self.annotate_background = None

        self._picam2 = Picamera2(camera_num)
        self._configure()
        self._picam2.start()

    # Configuration ----------------------------------------------------------------

    def _configure(self):
        config = self._picam2.create_video_configuration(
            main={'size': tuple(self._resolution), 'format': 'RGB888'},
            sensor={'output_size': self._sensor_size, 'bit_depth': 10},
            controls={'FrameRate': float(self._framerate)},
            buffer_count=4)
        self._picam2.configure(config)
        logger.debug('Camera configured: %s', self._picam2.camera_configuration()['sensor'])

    def _restart(self, change):
        with self._lock:
            if self._encoder:
                raise PiCameraError('Cannot change camera configuration while recording')
            self._picam2.stop()
            change()
            self._picam2.start()

    @property
    def resolution(self):
        return self._resolution

    @resolution.setter
    def resolution(self, value):
        def change():
            self._resolution = Resolution(*value)
            self._configure()
        self._restart(change)

    @property
    def framerate(self):
        return self._framerate

    @framerate.setter
    def framerate(self, value):
        self._framerate = value
        self._picam2.set_controls({'FrameRate': float(value)})

    @property
    def sensor_mode(self):
        return self._sensor_mode

    @property
    def closed(self):
        return self._closed

    @property
    def recording(self):
        return self._encoder is not None

    @property
    def previewing(self):
        return self._preview

    # Preview and overlays ---------------------------------------------------------

    def start_preview(self, **options):
        """Starts a DRM preview when a display is connected; otherwise a no-op."""
        with self._lock:
            if self._preview or not _preview_wanted():
                return
            if self._encoder:
                logger.warning('Preview cannot be started while recording; skipped')
                return

            def change():
                try:
                    self._picam2.start_preview(Preview.DRM)
                    self._preview = True
                except Exception as e:  # No usable display.
                    logger.warning('Preview unavailable: %s', e)
            self._restart(change)

    def stop_preview(self):
        with self._lock:
            if not self._preview or self._encoder:
                return

            def change():
                self._picam2.stop_preview()
                self._preview = False
            self._restart(change)

    def add_overlay(self, source, size=None, format=None, layer=0, alpha=255, **options):
        overlay = _Overlay(self, size or self._resolution)
        overlay.update(source)
        return overlay

    def remove_overlay(self, overlay):
        overlay.close()

    def _set_overlay(self, array):
        if self._preview:
            self._picam2.set_overlay(array)

    # Stills -----------------------------------------------------------------------

    def capture(self, output, format=None, use_video_port=False, resize=None,
                splitter_port=0, bayer=False, quality=85, **options):
        """Captures the current main-stream frame to a path or file-like object."""
        if format is None:
            if not isinstance(output, str):
                raise PiCameraError('format is required when output is not a filename')
            format = os.path.splitext(output)[1][1:]
        format = format.lower()

        image = self._picam2.capture_image('main')
        if resize:
            image = image.resize(tuple(resize))
        self._annotate(image)

        own = isinstance(output, str)
        out = open(output, 'wb') if own else output
        try:
            if format in _CAPTURE_FORMATS:
                save_options = {'quality': quality} if _CAPTURE_FORMATS[format] == 'JPEG' else {}
                image.save(out, _CAPTURE_FORMATS[format], **save_options)
            elif format == 'rgb':
                out.write(image.tobytes())
            elif format == 'bgr':
                out.write(image.tobytes('raw', 'BGR'))
            else:
                raise PiCameraError('Unsupported capture format %r' % format)
        finally:
            if own:
                out.close()

    def _annotate(self, image):
        if not self.annotate_text:
            return
        draw = ImageDraw.Draw(image)
        text = self.annotate_text
        if isinstance(text, bytes):
            text = text.decode('ascii', 'replace')
        box = draw.multiline_textbbox((0, 0), text)
        x = (image.width - (box[2] - box[0])) // 2
        if self.annotate_background:
            draw.rectangle((x - 4, 0, x + box[2] - box[0] + 4, box[3] + 4),
                           fill=str(self.annotate_background))
        draw.multiline_text((x, 2), text, fill=str(self.annotate_foreground or 'white'),
                            align='center')

    # Video ------------------------------------------------------------------------

    def start_recording(self, output, format=None, resize=None, splitter_port=1,
                        bitrate=17000000, quality=None, profile=None, inline_headers=True,
                        intra_period=None, **options):
        with self._lock:
            if self._encoder:
                raise PiCameraError('Already recording')
            if format is None:
                if not isinstance(output, str):
                    raise PiCameraError('format is required when output is not a filename')
                format = os.path.splitext(output)[1][1:]
            format = format.lower()
            if format == 'h264':
                encoder = H264Encoder(bitrate=bitrate, repeat=True,
                                      iperiod=intra_period or int(self._framerate),
                                      profile=profile)
            elif format == 'mjpeg':
                encoder = MJPEGEncoder(bitrate=bitrate)
            else:
                raise PiCameraError('Unsupported recording format %r' % format)

            if isinstance(output, str):
                self._encoder_file = open(output, 'wb')
                target = self._encoder_file
            else:
                target = output
            self._picam2.start_encoder(encoder, _ForwardOutput(target))
            self._encoder = encoder

    def wait_recording(self, timeout=0, splitter_port=1):
        if not self._encoder:
            raise PiCameraError('Not recording')
        time.sleep(timeout)

    def stop_recording(self, splitter_port=1):
        with self._lock:
            if not self._encoder:
                return
            self._picam2.stop_encoder(self._encoder)
            self._encoder = None
            if self._encoder_file:
                self._encoder_file.close()
                self._encoder_file = None

    def request_key_frame(self, splitter_port=1):
        pass

    # Lifecycle --------------------------------------------------------------------

    def close(self):
        with self._lock:
            if self._closed:
                return
            self.stop_recording()
            self._picam2.stop()
            if self._preview:
                self._picam2.stop_preview()
                self._preview = False
            self._picam2.close()
            self._closed = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.close()
