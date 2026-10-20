#!/usr/bin/env python3
"""Exercises the Joy Detector's photo + annotation path without a button press.

Runs face detection on a still image with the bonnet, then hands the faces and a
fake camera (whose capture() returns that image) to the demo's own Photographer.
Expects an original and an _annotated file in --folder.

    joy_photo_annotate.py --input view2.jpg --folder /tmp/joy-photos
"""
import argparse
import glob
import importlib.util
import os
import shutil

from PIL import Image

from aiy.vision.inference import ImageInference
from aiy.vision.models import face_detection

DEMO = '/opt/aiy/python/src/examples/vision/joy/joy_detection_demo.py'


class StillCamera:
    """Stands in for PiCamera: capture() writes the given image."""

    def __init__(self, path):
        self._path = path

    def capture(self, stream, format='jpeg', use_video_port=False):
        with open(self._path, 'rb') as f:
            shutil.copyfileobj(f, stream)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--folder', default='/tmp/joy-photos')
    args = parser.parse_args()

    spec = importlib.util.spec_from_file_location('joy_demo', DEMO)
    demo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(demo)

    image = Image.open(args.input)
    with ImageInference(face_detection.model()) as inference:
        faces = face_detection.get_faces(inference.run(image))
    print('faces:', len(faces))

    shutil.rmtree(args.folder, ignore_errors=True)  # also checks the folder gets created
    with demo.Photographer('jpeg', args.folder) as photographer:
        photographer.update_faces((faces, image.size))
        photographer.shoot(StillCamera(args.input))
    files = sorted(glob.glob(os.path.join(args.folder, '*')))
    for f in files:
        print(os.path.basename(f), Image.open(f).size)
    annotated = [f for f in files if f.endswith('_annotated.jpeg')]
    ok = len(files) == 2 and len(annotated) == 1 if faces else len(files) == 1
    print('PHOTO OK' if ok else 'PHOTO FAIL')


if __name__ == '__main__':
    main()
