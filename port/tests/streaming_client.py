#!/usr/bin/env python3
"""Checks the Vision Kit streaming server's protobuf TCP port (what the AIY app uses).

Connects, sends stream_control(enabled=True), and reads ClientBound messages for
--seconds. Expects a Start first, then Video (H.264) and optional Overlay (SVG).
Writes the video to --h264 so it can be checked with ffprobe/ffmpeg.

    streaming_client.py --host localhost --seconds 10 --h264 /tmp/tcp.h264
"""
import argparse
import collections
import socket
import struct
import time

from aiy.vision.streaming.proto import messages_pb2 as pb2


def recv_exact(sock, n):
    buf = bytearray()
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise EOFError('server closed the connection')
        buf.extend(chunk)
    return bytes(buf)


def send(sock, message):
    data = message.SerializeToString()
    sock.sendall(struct.pack('!I', len(data)) + data)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--port', type=int, default=4665)
    parser.add_argument('--seconds', type=float, default=10)
    parser.add_argument('--h264', default='/tmp/tcp.h264')
    args = parser.parse_args()

    sock = socket.create_connection((args.host, args.port))
    start = time.monotonic()
    send(sock, pb2.ServerBound(stream_control=pb2.StreamControl(enabled=True)))

    counts = collections.Counter()
    order = []
    first_video_at = None
    last_overlay = ''
    with open(args.h264, 'wb') as out:
        while time.monotonic() - start < args.seconds:
            size = struct.unpack('!I', recv_exact(sock, 4))[0]
            message = pb2.ClientBound()
            message.ParseFromString(recv_exact(sock, size))
            which = message.WhichOneof('message')
            counts[which] += 1
            if len(order) < 3:
                order.append(which)
            if which == 'start':
                print('start: %dx%d' % (message.start.width, message.start.height))
            elif which == 'video':
                if first_video_at is None:
                    first_video_at = time.monotonic() - start
                out.write(message.video.data)
            elif which == 'overlay':
                last_overlay = message.overlay.svg

    send(sock, pb2.ServerBound(stream_control=pb2.StreamControl(enabled=False)))
    sock.close()

    print('messages:', dict(counts))
    print('first messages:', order)
    print('first video after %.2f s' % (first_video_at or -1))
    if last_overlay:
        print('last overlay (%d chars): %s...' % (len(last_overlay), last_overlay[:160]))
    ok = order[:1] == ['start'] and counts['video'] > 0
    print('TCP STREAM OK' if ok else 'TCP STREAM FAIL')


if __name__ == '__main__':
    main()
