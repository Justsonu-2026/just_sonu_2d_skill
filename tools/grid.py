"""Overlay a labelled coordinate grid on an image (for reading coordinates by eye)."""
import sys
from PIL import Image, ImageDraw
im = Image.open(sys.argv[1]).convert('RGB'); out = sys.argv[2]
step = int(sys.argv[3]) if len(sys.argv) > 3 else 50
crop = list(map(int, sys.argv[4].split(','))) if len(sys.argv) > 4 else None
d = ImageDraw.Draw(im)
for x in range(0, im.width, step):
    d.line([(x, 0), (x, im.height)], fill=(255, 0, 0) if x % (2*step) == 0 else (255, 160, 160), width=1)
for y in range(0, im.height, step):
    d.line([(0, y), (im.width, y)], fill=(255, 0, 0) if y % (2*step) == 0 else (255, 160, 160), width=1)
for x in range(0, im.width, 2*step):
    for y in range(0, im.height, 2*step):
        d.text((x+2, y+1), f'{x},{y}', fill=(200, 0, 0))
if crop: im = im.crop(crop)
im.save(out)
