"""Render the hand library as a sheet (both sides). python -m tools.hand_sheet out.png"""
import sys
from tools.art.hands import HANDS, hand_layers
from tools.art.svgpart import part_svg, rasterise
layers = []
cols = 8
for i, h in enumerate(HANDS):
    for side, flip in (('L', 1), ('R', -1)):
        r, c = divmod(i, cols)
        x = 80 + c * 160 + (0 if side == 'L' else 0)
        y = 60 + (r * 2 + (0 if side == 'L' else 1)) * 190
        layers += hand_layers(h, x, y, 1.0, flip)
svg = part_svg(layers, 1300, 820)
rasterise(svg, sys.argv[1], scale=1.0, w=1300, h=820, crop=False)
