# testing-on-device

How to reach the test Pi, which SD card is in it, the test scripts in `port/tests/`, and the shell traps that cost time in earlier sessions.

## The cards (one Pi, swap SD cards)

| Card | Host | Kernel / Python | State |
|---|---|---|---|
| Google's official image (reference) | `pi@raspberrypi.local`, or `192.168.11.2` over the USB data port | 5.10.17 / 3.7.3 | **Don't `apt upgrade`.** Baseline in `vendor/baseline/` |
| Bookworm Lite 32-bit | `pi@vision-kit.local` | 6.12.109 / 3.11.2 | Set up by `deploy.sh` after `uninstall.sh` (it was the development card) |
| Trixie Lite 32-bit | `pi@vision-kit.local` | 6.18.50 / 3.13.5 | Fresh card set up only by `deploy.sh`. Sudoers file added by hand. Its service runs with `--enable_streaming` (unit edited by hand) |

Two cards share the hostname: check `uname -r` before trusting results. If `raspberrypi.local` doesn't answer, that card isn't in the Pi.
SSH key auth works with `-o BatchMode=yes`. `dkms` is in `/usr/sbin`, which isn't on `pi`'s PATH over ssh.

## Test scripts (copy `port/tests/` to the Pi, run with `/opt/aiy/venv/bin/python`)

| Script | Checks | Needs |
|---|---|---|
| `hardware_check.py [--button S]` | LEDs, buzzer, PIN_A GPIO/PWM, LED_1 (and the button) | service stopped |
| `button_wait.py --presses N` | a person pressing the button (run it in the background, read its log) | service stopped |
| `camera_shim_smoke.py` | capture, H.264 circular buffer, resolution change | service stopped |
| `camera_face_snapshot.py` | live face boxes line up with a capture | service stopped, a face in view |
| `camera_inference_probe.py` | bonnet inference while *another* process streams (e.g. `rpicam-vid --mode 1640:1232:10:P`) | camera free |
| `joy_photo_annotate.py --input IMG` | the Joy Detector's photo + annotation path | service stopped |
| `streaming_client.py --host localhost` | the protobuf stream on 4665 | service running **with** streaming |
| `examples/vision/face_detection.py --input ~/view2.jpg` | Myriad + model, no camera. Expected: `face_score=0.87744140625`, box `(2613, 679, 436, 436)`, identical to Buster | bonnet free |

`vendor/baseline/view2.jpg` is the reference still (a face on a TV). Copy it to the Pi's home folder; `/tmp` is cleared at reboot.

## Traps

- **`pgrep -f`/`pkill -f` match their own ssh command line.** `ssh host 'pkill -f joy_detection_demo.py; …'` kills the remote shell itself, because its command line
  contains the pattern. Put kill-and-restart logic in a script file on the Pi (`bash /tmp/restart.sh`), and never repeat the pattern elsewhere in the same ssh command.
- **sudo drops `PYTHONPATH`.** Run tests as `pi` with the venv's Python; don't `sudo` them.
- **Background runs on the Pi:** `setsid nohup CMD > /tmp/x.log 2>&1 < /dev/null &`, otherwise ssh waits or the process dies with the session.
- **Long jobs** (DKMS builds, deploys) take over the 2-minute tool timeout: run them in the background with output to a log, and check the real exit code instead of piping through `tail`.
- **mDNS adds latency** to `.local` names (around 0.3 s per connect from the Mac). Use the IP for timing measurements (`hostname -I` on the Pi).
- **Hangs:** run Python tests with `timeout -s ABRT 120 python -X faulthandler …`. On timeout, every thread's stack is printed.
- `vendor/baseline/system.txt` contains NUL bytes; use `grep -a`. The rtk wrapper hides grep's "Binary file matches"; `rtk proxy grep` shows it.
- Quiet libcamera with `LIBCAMERA_LOG_LEVELS=*:WARN`. Auto-exposure needs a few seconds in a dark room: a still taken 1.5 s after the camera starts came out black (`raspistill -t 1500` on Buster), and 5 s was fine.
