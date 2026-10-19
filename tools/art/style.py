"""Shared style helpers for all view builders (line weights, shading presets, part registry)."""
import json, os
from .geom import smooth_closed, ellipse_pts
from .svgpart import write_part
from .palette import KANHA

LINE = 3.8      # outer line width (U)
LINE_IN = 3.0   # inner detail lines


def shade(color, dx=8, dy=10, k=0.94, blur=7, **kw):
    return dict(color=color, dx=dx, dy=dy, k=k, blur=blur, **kw)


def limb_shade(P, flip=1):
    return dict(color=P['skin_sh'], dx=-10 * flip, dy=0, kx=0.86, ky=1.0, blur=8)


def skin_layer(P, d, **kw):
    L = dict(d=d, fill=P['skin'], stroke=P['skin_line'], sw=LINE, outer=True,
             shade=shade(P['skin_sh'], 9, 7, 0.93, 8))
    L.update(kw)
    return L


def gold_band(P, d, w=20):
    return [dict(d=d, stroke=P['gold_line'], sw=w + 5, cap='butt'), dict(d=d, stroke=P['gold'], sw=w, cap='butt'),
            dict(d=d, stroke=P['gold_hi'], sw=w * 0.22, opacity=0.7, cap='butt')]


def mirror_pts(pts, cx=360.0):
    return [(2 * cx - x, y) for x, y in pts][::-1]


def hair_style(P):
    return dict(fill=P['hair'], stroke=P['hair_line'], sw=LINE * 0.8,
                shade=shade(P['hair_sh'], 10, 12, 0.92, 10))


def hair_sheen(P, blobs):
    return [dict(d=smooth_closed(ellipse_pts(x, y, rx, ry, 24, rot=r)), fill=P['hair_hi'], opacity=o, blur=b)
            for x, y, rx, ry, r, o, b in blobs]


def gold(P, sw=2.4):
    return dict(fill=P['gold'], stroke=P['gold_line'], sw=sw, shade=shade(P['gold_sh'], 4, 5, 0.85, 4),
                light=dict(color=P['gold_hi'], dx=-4, dy=-6, k=0.4, blur=3))


class PartSet:
    """Collects parts for one view and writes them (PNG + SVG + meta.json)."""

    def __init__(self, out, svg_out):
        self.out, self.svg_out = out, svg_out
        self.parts = {}
        self.skeleton = {}

    def add(self, name, layers, pivot, z, backing=False, line_z=None, bone=None, **extra):
        if bone:
            extra['bone'] = bone
        self.parts[name] = (layers, pivot, z, extra, backing, line_z)

    def write(self, only=None):
        metas = []
        for name, (layers, pivot, z, extra, backing, line_z) in self.parts.items():
            if only and name not in only:
                continue
            metas.extend(write_part(name, layers, self.out, pivot, z, extra, svg_dir=self.svg_out,
                                    backing=backing, line_z=line_z))
        with open(os.path.join(self.out, 'meta.json'), 'w') as f:
            json.dump(metas, f, indent=1)
        with open(os.path.join(self.out, 'skeleton.json'), 'w') as f:
            json.dump(self.skeleton, f, indent=1)
        return metas


def bone_for(name):
    """Default bone assignment for a part by name (same names in every view)."""
    n = name
    for pre, bone in (('hair_lock_', None), ('earring_', None)):
        if n.startswith(pre):
            return n.replace('hair_lock_', 'lock_')
    table = [('feather', 'feather'), ('upperarm_', 'upperarm_'), ('forearm_', 'forearm_'), ('hand_', 'hand_'),
             ('dhoti_', 'thigh_'), ('shin_', 'shin_'), ('foot_', 'foot_'), ('flap', 'flap')]
    for pre, b in table:
        if n.startswith(pre):
            if b.endswith('_'):
                side = n.split('_')[1]
                return b + side
            return b
    if n in ('torso', 'necklace', 'neck'):
        return 'chest'
    if n in ('hips', 'buckle'):
        return 'hips'
    return 'head'


def set_palette(pal):
    """Point every art module at a palette (used for recoloured friends)."""
    from . import face, hands, hairtex
    import sys
    for mod in (face, hands, hairtex):
        mod.P = pal
    for k, m in list(sys.modules.items()):
        if k.startswith('tools.art.boy_') or k.startswith('tools.art.char_'):
            m.P = pal
