# joy-detector

The kit's default app, `examples/vision/joy/joy_detection_demo.py`, run at boot by `joy_detection_demo.service`: face detection drives the button LED colour, the button takes photos, and it can stream video.

## Trigger and flow

- **Start:** systemd at boot (`Requires=dev-vision_spicomm.device`, so it waits for the Myriad driver), as the install user, from `WorkingDirectory=~`.
  It runs `ExecStart=/opt/aiy/venv/bin/python /opt/aiy/python/src/examples/vision/joy/joy_detection_demo.py --blink_on_error`, plus `--enable_streaming --mdns_name AIY-Board` with `--streaming`.
- Steps:
  - opens `Leds`, `Board`, a `TonePlayer` on BCM22, the `Photographer` (writes to `~/Pictures`), the `Animator` and `PiCamera(sensor_mode=4, resolution=(820, 616))`;
  - loads the FaceDetection model (a short tune plays), then runs `CameraInference` in a loop;
  - computes a moving average of the joy score, which drives the RGB LED, and logs "High/Low joy detected" with hysteresis;
  - a button press beeps and takes a photo: `capture(…, use_video_port=True)` gives the original JPEG, plus an `_annotated` copy with face boxes and a
    "Joy: 0.81" label **only if faces were seen in the latest inference result**;
  - with streaming on, it sends SVG overlays ("Faces: N Avg. joy: X") to stream clients.
- Logs go to `journalctl -u joy_detection_demo -o cat`. Photo lines: "Button pressed." → "Taking photo…" → "Saving original …" / "Saving annotated …".

## Invariants

- **It holds the camera, the LEDs and the bonnet.** Stop the service before running any other camera or LED script (`sudo systemctl stop joy_detection_demo`)
  and start it again afterwards.
- `~/Pictures` must exist and be writable. `Photographer.__init__` now creates it, because Raspberry Pi OS Lite has no `~/Pictures` (Google's desktop image did).
- The font is `/usr/share/fonts/truetype/freefont/FreeSans.ttf` (`fonts-freefont-ttf`). Label height uses `FreeTypeFont.getbbox()[3]`;
  `getsize()` was removed in Pillow 10, which Trixie ships (Pillow 11).

## Failure modes

- **A photo error kills the photo thread silently.** `Service._run` doesn't catch exceptions. Before the `~/Pictures` fix, the first press raised `FileNotFoundError`
  and every later press was ignored. The log still showed "Saving … done", because the `stopwatch` helper logs "done" in a `finally`.
  If presses beep but no files appear, look for a traceback after the first "Button pressed."
- **No `_annotated` file** means no face was detected at that moment (common with backlit faces), not a bug.
- **Every stop or restart logs an `InterruptedError` traceback.** SIGTERM interrupts the Myriad ioctl. It's harmless.
- **lgpio needs a writable working directory.** Without `WorkingDirectory=~` the service fails at start with `FileNotFoundError: '.lgd-nfy-3'`.

## Checking

- Live: watch the journal for "Model loaded." and "… joy detected." lines while a face is in view.
- Photo path without pressing the button: `port/tests/joy_photo_annotate.py --input view2.jpg --folder /tmp/joy-photos`. It runs real bonnet face detection on a still and
  feeds a fake camera to the demo's own `Photographer`, then expects an original plus `_annotated`. Stop the service first (it holds the bonnet).
- Button presses: `port/tests/button_wait.py` in the background, or just press and `ls ~/Pictures`.
