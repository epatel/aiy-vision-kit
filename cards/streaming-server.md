# streaming-server

The live video server in `aiy/vision/streaming/server.py` (`StreamingServer`), started by the Joy Detector with `--enable_streaming`: its ports, protocol, and what was fixed for picamera2.

## Ports

| Port | Client | Protocol |
|---|---|---|
| 4664 | browser: `http://<pi>:4664/` | HTTP for the page and assets (`streaming/assets/`), then WebSocket. H.264 decoded in the page by Broadway.js, plus the SVG overlay |
| 4665 | AIY Android app (found through mDNS `_aiy_vision_video._tcp`, published with `avahi-publish-service`) | 4-byte big-endian length + protobuf (`streaming/proto/messages.proto`) |
| 4666 | anything: `ffplay tcp://<pi>:4666`, `nc <pi> 4666 > x.h264` | raw H.264 Annex B |

Protobuf flow: the client sends `ServerBound{stream_control{enabled=true}}` → the server sends `ClientBound{start{width,height}}`, then `video{data}` (whole NAL units, starting at
an SPS) and `overlay{svg}` messages. `enabled=false` → `stop`. The first enabled client makes the server `start_recording()`; when the last one leaves it stops.

## How it uses the camera

- `camera.start_recording(server, format='h264', profile='baseline', inline_headers=True, bitrate=…, intra_period=0)`. The server's `write(data)` is called per frame.
  It requires `data` to start with `00 00 00 01` and looks at the first NAL type only.
- With the picamera2 shim, a keyframe arrives as SPS+PPS+IDR in one `write()`. That is still a valid stream, and Broadway decodes it.
- Each client has a `DroppingQueue(15)`. When it is full, the frame is dropped and the client waits for the next SPS ("Running behind, dropping messages").
  That happens now and then over the Pi Zero's Wi-Fi and resyncs cleanly.
- A client that needs an SPS makes the server call `camera.request_key_frame()` on every frame. The shim forces one keyframe per 0.25 s at most, which matters:
  without it, a second viewer waited 1.31 s on average for the periodic IDR; with it, 0.15 s.

## Bugs fixed in the server

- `_process_web_request()` did `'Upgrade' in request.headers['Connection']`. A request without a `Connection` header (curl sends none, browsers do) crashed with
  `TypeError`. Headers are now read with `.get(…, '')` and compared case-insensitively.
- After an error in `WsProtoClient._receive_message()` only the rx thread ended. The tx thread waited forever, so the socket stayed open (the request hung) and
  the client was never removed (the count climbed with each bad request). The error path now puts `None` on the tx queue, which ends the tx thread and stops the client.
- Unsupported requests (e.g. POST) now close at once instead of hanging.

## Turning it on

- At install: `port/deploy.sh pi@HOST --streaming` (adds `--enable_streaming --mdns_name AIY-Board` to the service).
- Quickly, on a running card: change the unit's `ExecStart` to end with `--blink_on_error --enable_streaming --mdns_name AIY-Board`, then `daemon-reload` and restart.
  A later plain `deploy.sh` (without `--streaming`) rewrites the unit and turns it off again.

## Checking

- Raw: `nc <pi> 4666 > x.h264` for a few seconds, then `ffprobe -count_frames x.h264` and `ffmpeg -v error -i x.h264 -f null -`. Expected: Baseline 820×616 (the Joy Detector's
  resolution) at about 21 fps, an IDR every ~30 frames, no decode errors (ignore the last, truncated frame).
- Protobuf: `port/tests/streaming_client.py --host localhost --seconds 10 --h264 /tmp/tcp.h264` (run on the Pi with `/opt/aiy/venv/bin/python`). Expects `start`
  first, then video and overlay messages.
- Web: `curl http://<pi>:4664/` gives 200 and 468 bytes; `curl …/broadway/Decoder.js` gives 297 KB. A browser should log "Started: 820x616" and
  "First frame decoded" in the console. Start/Stop on the page shows up in the server log as `stream_control True/False` and recording start/stop.
- Join latency: connect a second client while one streams and time the first `recv()`. Use the IP, not `.local`, or mDNS lookup time skews it.
- The server logs to the Joy Detector's journal: `journalctl -u joy_detection_demo -o cat | grep streaming.server`.
