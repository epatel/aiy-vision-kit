# camera-shim

`aiy/camera.py` (`port/python/src/aiy/camera.py`): a picamera-1.13-compatible `PiCamera` on top of Picamera2/libcamera, so the AIY examples only change their import.

## Why it exists

Raspberry Pi OS dropped the legacy MMAL camera stack and `picamera` in Bullseye. Every AIY camera example used `picamera.PiCamera(sensor_mode=4, …)`.
The bonnet doesn't care which library drives the sensor, only that the sensor streams in the right mode. So the shim keeps the old call pattern:

```python
from aiy.camera import PiCamera          # was: from picamera import PiCamera
from aiy import camera as picamera       # for code using picamera.PiCamera / PiCameraCircularIO
```

## Behaviour

- **The constructor configures and starts streaming at once.** It keeps streaming until `close()`. Some examples (`any_model_camera.py`, tests) only open
  `PiCamera(sensor_mode=4)` and never call `start_preview()`, and inference still has to run.
- Sensor mode → libcamera `sensor.output_size`: 0/4/5/6 → 1640×1232 (the bonnet's mode; libcamera has no 1640×922 or 1280×720 binned crops),
  1 → 1920×1080, 2/3 → 3280×2464, 7 → 640×480. The bit depth is 10. `resolution` only sets the main stream size, not the sensor mode.
- Main stream: `RGB888` at `resolution`, `buffer_count=4`, `FrameRate` from `framerate` (default 30). CMA (256 MB) is plenty.
- `resolution` and `framerate` can be set while running. A resolution change stops, reconfigures and restarts (not allowed while recording).
- `capture(output, format=…)`: grabs the main stream as a PIL image (about 0.1–0.9 s) and saves it as jpeg/png/bmp/gif, or raw rgb/bgr. `resize` works.
  `annotate_text` / `annotate_foreground` / `annotate_background` are drawn **on captures only**, not on the preview or video.
- `start_recording(output, format='h264'|'mjpeg', bitrate, profile, intra_period)`: hardware H.264 encoder (`H264Encoder(repeat=True, iperiod=intra_period or framerate)`).
  Each encoded frame goes through a small `Output` to any object with `write()`. picamera2's `FileOutput` would demand an `io.BufferedIOBase`.
  For keyframes the frames come as SPS+PPS+IDR in one buffer.
- `PiCameraCircularIO(camera, seconds=…)`: keeps the last N seconds of frames; `copy_to(path_or_file)` starts at a keyframe.
- **`request_key_frame()` calls `H264Encoder.force_key_frame()` at most once per 0.25 s** (`_KEY_FRAME_REQUEST_INTERVAL`). The streaming server calls it on *every*
  frame until it sees a keyframe, and each `force_key_frame()` queues another keyframe, so an unthrottled version would flood the stream with IDRs.
  Measured: a second viewer's time to first frame went from 1.31 s to 0.15 s.
- Preview: `start_preview()` starts a DRM preview only if `/sys/class/drm/card*-HDMI-A-*/status` says `connected`, or `AIY_CAMERA_PREVIEW=1`
  (`=0` forces it off). It restarts the camera to attach. Not tested with a display.
- Overlays: `add_overlay(bytes, size)` returns an object with `update(bytes)`, which goes to `Picamera2.set_overlay()` (RGBA). It only shows while previewing.
  `aiy/vision/annotator.py` uses this. The MMAL monkey patch it used to carry is gone.
- Also provided: `Color` (a `str` that PIL understands) and `Resolution` (a namedtuple with width/height; the streaming server unpacks it).

## Rules of thumb

- Only one process can open the camera. Stop `joy_detection_demo` before running any other camera script.
- Set `LIBCAMERA_LOG_LEVELS=*:WARN` to quiet libcamera's INFO lines.
- "Camera configuration has been adjusted!" from picamera2 is normal for sizes like 820×616 (stride alignment).
- Live inference runs at about 8–11 fps on Bookworm/Trixie (Buster: 10–15). The RGB888 main stream costs ISP/CPU time even when nothing captures;
  if speed matters, try YUV420 or a small main stream.
- Picamera2 version differences seen: 0.3.31 (Bookworm) and 0.3.38 (Trixie) both work with the same code.

## Tests

`port/tests/camera_shim_smoke.py` checks JPEG/PNG capture, the H.264 circular buffer, and a resolution change. `port/tests/camera_face_snapshot.py` draws the bonnet's live
face boxes on a capture taken at the same moment; they line up, so orientation and coordinates match Buster.
