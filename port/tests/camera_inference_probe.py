#!/usr/bin/env python3
"""Run face detection on the bonnet's camera stream without touching the camera.

Something else (rpicam-vid, picamera2) must already be streaming from the sensor.
Prints a per-frame line and a summary.
"""
import argparse
import collections
import time

from aiy.vision.inference import CameraInference
from aiy.vision.models import face_detection


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--num_frames', '-n', type=int, default=100)
    args = parser.parse_args()

    counts = collections.Counter()
    start = time.monotonic()
    with CameraInference(face_detection.model()) as inference:
        for result in inference.run(args.num_frames):
            faces = face_detection.get_faces(result)
            counts[len(faces)] += 1
            print('#%05d (%5.2f fps): num_faces=%d %s' % (
                inference.count, inference.rate, len(faces),
                ' '.join('score=%.2f box=%s' % (f.face_score, tuple(int(v) for v in f.bounding_box))
                         for f in faces)), flush=True)
    elapsed = time.monotonic() - start
    print('SUMMARY frames=%d elapsed=%.1fs fps=%.2f faces=%s' % (
        sum(counts.values()), elapsed, sum(counts.values()) / elapsed, dict(counts)))


if __name__ == '__main__':
    main()
