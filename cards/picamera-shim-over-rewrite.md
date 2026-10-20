# picamera-shim-over-rewrite

Decision: keep the AIY code on the picamera 1.13 API through a compatibility shim (`aiy/camera.py` on Picamera2), instead of rewriting each example and the annotator for Picamera2.

## The choice

`from picamera import PiCamera` becomes `from aiy.camera import PiCamera` (or `from aiy import camera as picamera`); nothing else in the examples changes.
The shim implements the parts of picamera the AIY code uses: the constructor with `sensor_mode`, `resolution`, `framerate`, preview, `capture`, recording,
`PiCameraCircularIO`, overlays, `annotate_*`, `request_key_frame`, `Color`.

## Alternatives considered

- **Rewrite every example for Picamera2:** 10 files plus `annotator.py` and the streaming server, each with its own Picamera2 configuration. That's more diff against
  upstream, and every user script written for the original kit would break.
- **A fake top-level `picamera` module:** zero import changes, but it shadows a real package name and hides from readers that the code no longer runs on MMAL.
- **Stay on the legacy camera stack (Bullseye):** removed in Bookworm, so it's a dead end.

## Why this won

- The core inference code (`aiy/vision/inference.py`, `_spicomm.py`) never used picamera. Only the "make the sensor stream" part needed replacing, and that maps
  onto one class.
- One place encodes the bonnet-specific knowledge: the sensor mode mapping, streaming from the constructor, keyframe rate-limiting.
- `port/python.patch` stays small: import lines in examples, plus real fixes.

## Costs accepted

- `annotate_text` only appears on captures, not on the preview or video.
- Overlays only show with a DRM preview (HDMI connected), and that is untested.
- Some picamera behaviours are approximations (sensor modes 5/6 map to the full-FoV binned mode; `intra_period=0` means one IDR per second).

## When to revisit

- New code that needs Picamera2 features the shim doesn't expose (multiple streams, `lores`, controls): use Picamera2 directly in that code rather than growing the shim.
- If the RGB888 main stream turns out to be what slows live inference (8–11 fps vs 10–15 on Buster), the shim is the single place to change it.
