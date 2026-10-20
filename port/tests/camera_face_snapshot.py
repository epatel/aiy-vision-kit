#!/usr/bin/env python3
"""Draws the bonnet's live face boxes on a frame captured at the same time.

Boxes come from the bonnet in sensor coordinates (1640x1232); the capture uses the
same resolution, so they should line up with the faces if orientation is right.
"""
import argparse
import io

from PIL import Image, ImageDraw

from aiy.camera import PiCamera
from aiy.vision.inference import CameraInference
from aiy.vision.models import face_detection


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='face_snapshot.jpg')
    parser.add_argument('--max_frames', type=int, default=200)
    args = parser.parse_args()

    with PiCamera(sensor_mode=4, resolution=(1640, 1232), framerate=30) as camera, \
         CameraInference(face_detection.model()) as inference:
        for result in inference.run(args.max_frames):
            faces = face_detection.get_faces(result)
            if not faces:
                continue
            stream = io.BytesIO()
            camera.capture(stream, format='jpeg')
            image = Image.open(io.BytesIO(stream.getvalue())).convert('RGB')
            draw = ImageDraw.Draw(image)
            for face in faces:
                x, y, w, h = face.bounding_box
                draw.rectangle((x, y, x + w, y + h), outline=(255, 0, 0), width=6)
                draw.text((x, y - 14), 'score=%.2f joy=%.2f' % (face.face_score, face.joy_score),
                          fill=(255, 255, 0))
                print('face score=%.2f box=%s' % (face.face_score, tuple(int(v) for v in face.bounding_box)))
            image.save(args.output)
            print('saved', args.output)
            return
    print('no faces in', args.max_frames, 'frames')


if __name__ == '__main__':
    main()
