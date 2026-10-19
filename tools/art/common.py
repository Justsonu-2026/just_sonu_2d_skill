"""Shared helpers for view builders: loading guide classes, composing parts for previews."""
import json, os
import numpy as np
from PIL import Image
from .geom import fill_holes, morph, largest_components

CLASS_NAMES = ['bg', 'ground', 'skin', 'skin_sh', 'hair', 'dhoti', 'sash', 'gold', 'green']


def load_classes(view):
    lab = np.load(f'build/guide/{view}_classes.npy')
    C = {n: lab == i for i, n in enumerate(CLASS_NAMES)}
    C['skin_all'] = C['skin'] | C['skin_sh']
    C['fig'] = fill_holes(~(C['bg'] | C['ground']))
    return C


def yy_xx(shape=(1800, 720)):
    return np.mgrid[0:shape[0], 0:shape[1]]


def compose(metas, partdir, scale=1.5, w=720, h=1800, bg=(255, 255, 255, 255), only=None):
    """Composite part PNGs (sorted by z) onto a canvas the size of the view crop."""
    canvas = Image.new('RGBA', (int(w * scale), int(h * scale)), bg)
    byname = {m['name']: m for m in metas}

    def placed(m):
        layer = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
        im = Image.open(os.path.join(partdir, m['name'] + '.png')).convert('RGBA')
        layer.paste(im, (int(round(m['bbox'][0] * scale)), int(round(m['bbox'][1] * scale))))
        return layer

    for m in sorted(metas, key=lambda m: m['z']):
        if only and m['name'] not in only:
            continue
        if m.get('hidden'):
            continue
        layer = placed(m)
        if m.get('clip_to') and m['clip_to'] in byname:   # e.g. pupils clipped to the eye white
            mask = placed(byname[m['clip_to']]).getchannel('A')
            a = np.minimum(np.array(layer.getchannel('A')), np.array(mask))
            layer.putalpha(Image.fromarray(a))
        canvas.alpha_composite(layer)
    return canvas
