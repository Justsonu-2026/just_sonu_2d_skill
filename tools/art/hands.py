"""Hand library in the reference style: slim tapered fingers, thin dark line, flat fill with
a soft shadow. The palm + extended fingers form ONE silhouette (no line across finger bases);
finger separation lines are each finger's outline clipped to outside the palm. Curled fingers
and a front thumb are drawn over the palm with their own outline.

Local space (s=1 = front-view size in the reference, hand ~130 U long):
wrist at (0,0), the hand points down (+y), thumb on local -x.
`flip` mirrors x, `angle` rotates the whole hand (radians, clockwise on screen).
"""
import math
import numpy as np
import cv2
from .geom import smooth_closed, smooth_open, ellipse_pts, resample_closed, smooth_circular
from .palette import KANHA as P

HANDS = ['relaxed', 'open', 'wave', 'fist', 'point', 'thumbs_up', 'peace', 'grab', 'cupped',
         'half_curl', 'palm_up', 'ok', 'pinch', 'clap', 'press', 'hip']
# profile (knife-edge) drawings: palm seen from the side, used for hanging arms / side view
HANDS_SIDE = ['side_relaxed', 'side_fist', 'side_open', 'side_cupped']
SIDE_SX = 0.75

PALM = [(-19, -6), (19, -6), (27, 22), (31, 48), (27, 64), (8, 70), (-12, 69), (-27, 62), (-31, 44), (-27, 20)]
KNUCKLES = [(-21, 63), (-7, 68), (8, 67), (22, 60)]      # index, middle, ring, pinky
LENS = [[24, 17, 13], [27, 19, 14], [25, 17, 13], [19, 14, 11]]
R0, R1 = 8.6, 6.2      # finger radius base / tip
THUMB_BASE = (-25, 22)
TR0, TR1 = 10.5, 7.5


def _chain(base, ang, lens, curls):
    pts = [np.array(base, float)]
    a = ang
    for L, c in zip(lens, curls):
        a += c
        pts.append(pts[-1] + L * np.array([-math.sin(a), math.cos(a)]))  # +a turns toward the thumb (-x)
    return pts


def _capsule(p0, p1, r0, r1, n=12):
    d = p1 - p0
    ang = math.atan2(d[1], d[0])
    pts = []
    for i in range(n + 1):
        a = ang - math.pi / 2 + math.pi * i / n
        pts.append(p1 + r1 * np.array([math.cos(a), math.sin(a)]))
    for i in range(n + 1):
        a = ang + math.pi / 2 + math.pi * i / n
        pts.append(p0 + r0 * np.array([math.cos(a), math.sin(a)]))
    return np.array(pts)


def _chain_polys(pts, r0, r1):
    n = len(pts) - 1
    rs = [r0 + (r1 - r0) * i / n for i in range(n + 1)]
    return [_capsule(pts[i], pts[i + 1], rs[i], rs[i + 1]) for i in range(n)]


def _union_outline(polys, sc=5.0):
    allp = np.vstack(polys)
    mn = allp.min(0) - 4; mx = allp.max(0) + 4
    w, h = int((mx[0] - mn[0]) * sc) + 1, int((mx[1] - mn[1]) * sc) + 1
    m = np.zeros((h, w), np.uint8)
    for p in polys:
        cv2.fillPoly(m, [np.round((np.asarray(p) - mn) * sc).astype(np.int32)], 1)
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    c = max(cs, key=cv2.contourArea)[:, 0, :].astype(float) / sc + mn
    return smooth_circular(resample_closed(c, 2.5), 1.0)


def _pose(name):
    """Return dict(fingers=[(ang, curls, layer)]*4, thumb=(ang, curls, layer), palm_lines=bool)."""
    st = [0, 0, 0]
    out = dict(palm_lines=False)
    if name.startswith('side_'):
        base = name[5:]
        if base == 'relaxed':
            c = [0.45, 0.6, 0.45]
            out['fingers'] = [(0.25, c, 'u'), (0.12, c, 'u'), (0.0, c, 'u'), (-0.12, c, 'u')]
            out['thumb'] = (0.25, [-0.05, 0.2], 'o')
            return out
        out.update(_pose(base))
        return out
    if name == 'relaxed':
        out['fingers'] = [(0.0, [0.25, 0.45, 0.35], 'u'), (-0.04, [0.25, 0.45, 0.35], 'u'),
                          (-0.08, [0.25, 0.45, 0.35], 'u'), (-0.14, [0.25, 0.45, 0.35], 'u')]
        out['thumb'] = (0.35, [-0.1, 0.15], 'o')
    elif name in ('open', 'press', 'clap'):
        out['fingers'] = [(0.12, st, 'u'), (0.03, st, 'u'), (-0.06, st, 'u'), (-0.16, st, 'u')]
        out['thumb'] = (0.9, [0.05, 0.1], 'u')
        out['palm_lines'] = name != 'press'
    elif name == 'palm_up':
        out['fingers'] = [(0.1, [0.1, 0.15, 0.1], 'u'), (0.02, [0.1, 0.15, 0.1], 'u'),
                          (-0.06, [0.1, 0.15, 0.1], 'u'), (-0.14, [0.1, 0.15, 0.1], 'u')]
        out['thumb'] = (1.0, [0.0, 0.1], 'u')
        out['palm_lines'] = True
    elif name == 'wave':
        out['fingers'] = [(0.32, st, 'u'), (0.1, st, 'u'), (-0.12, st, 'u'), (-0.36, st, 'u')]
        out['thumb'] = (1.2, [0.0, 0.05], 'u')
        out['palm_lines'] = True
    elif name in ('fist', 'hip', 'grab', 'point', 'peace', 'thumbs_up'):
        fold = ('f', [0.0], 'o')
        out['fingers'] = [fold] * 4
        out['thumb'] = (-1.35, [0.0, -0.1], 'o')
        if name == 'grab':
            g = (0.0, [0.55, 0.75, 0.6], 'u')
            out['fingers'] = [g] * 4
            out['thumb'] = (0.5, [-0.3, -0.3], 'o')
        if name == 'point':
            out['fingers'] = [(0.0, st, 'u')] + [fold] * 3
        if name == 'peace':
            out['fingers'] = [(0.16, st, 'u'), (-0.08, st, 'u')] + [fold] * 2
        if name == 'thumbs_up':
            out['thumb'] = (3.05, [0.0, 0.0], 'u')
    elif name == 'cupped':
        c = [0.4, 0.5, 0.35]
        out['fingers'] = [(0.1, c, 'u'), (0.0, c, 'u'), (-0.08, c, 'u'), (-0.16, c, 'u')]
        out['thumb'] = (1.6, [0.3, 0.2], 'u')
    elif name == 'half_curl':
        c = [0.7, 0.8, 0.5]
        out['fingers'] = [(0.05, c, 'u'), (0.0, c, 'u'), (-0.05, c, 'u'), (-0.1, c, 'u')]
        out['thumb'] = (0.6, [0.15, 0.35], 'o')
    elif name in ('ok', 'pinch'):
        rest = [0.05, 0.05, 0.05] if name == 'ok' else [0.6, 0.7, 0.4]
        out['fingers'] = [(0.25, [0.7, 0.9, 0.6], 'o'), (-0.02, rest, 'u'), (-0.12, rest, 'u'), (-0.24, rest, 'u')]
        out['thumb'] = (-0.2, [-0.3, -0.2], 'o')
    else:
        raise KeyError(name)
    return out


def hand_layers(name, wx, wy, s=1.0, flip=1, angle=0.0, skin=None, sx=None):
    """Layers for one hand drawing; the wrist sits at (wx, wy)."""
    sk = skin or dict(fill=P['skin'], sh=P['skin_sh'], line=P['hand_line'])
    if sx is None:
        sx = SIDE_SX if name.startswith('side_') else 1.0
    S = _pose(name)
    c, si = math.cos(angle), math.sin(angle)

    def T(pts):
        out = []
        for x, y in pts:
            x, y = x * flip * s * sx, y * s
            out.append((wx + x * c - y * si, wy + x * si + y * c))
        return out

    palm = np.array(PALM, float)
    under, over = [], []
    for (kx, ky), lens, (ang, curls, lay) in zip(KNUCKLES, LENS, S['fingers']):
        if ang == 'f':   # folded finger: a short knuckle segment seen end-on
            pts = _chain((kx, ky - 12), 0.0, [16], [0.0])
            polys = _chain_polys(pts, R0 + 0.8, R0)
        else:
            pts = _chain((kx, ky - 6), ang, lens, curls)
            polys = _chain_polys(pts, R0, R1)
        (under if lay == 'u' else over).append(polys)
    tang, tc, tlay = S['thumb']
    tpts = _chain(THUMB_BASE, tang, [22, 18], tc)
    tpolys = _chain_polys(tpts, TR0, TR1)
    (under if tlay == 'u' else over).append(tpolys)

    sil = _union_outline([palm] + [p for f in under for p in f])
    sil_d = smooth_closed(T(sil))
    palm_d = smooth_closed(T(palm))
    lw = sk.get('lw', 2.6) * s
    hb = sk.get('blur', 5)
    L = [dict(d=sil_d, fill=sk['fill'],
              shade=dict(color=sk['sh'], dx=4 * s * flip, dy=5 * s, k=0.9, blur=hb * s, opacity=sk.get('sh_op', 0.8)))]
    # separation lines of extended fingers: their outlines, clipped to outside the palm
    big = f'M{wx-400},{wy-400} L{wx+400},{wy-400} L{wx+400},{wy+400} L{wx-400},{wy+400} Z '
    for f in under:
        fd = smooth_closed(T(_union_outline(f)))
        L.append(dict(d=fd, stroke=sk['line'], sw=lw * 0.8, clip=big + palm_d, clip_rule='evenodd', opacity=0.9))
    L.append(dict(d=sil_d, stroke=sk['line'], sw=lw, outer=True))
    if S['palm_lines']:
        L.append(dict(d=smooth_open(T([(-20, 40), (-2, 46), (18, 40)])), stroke=sk['line'], sw=lw * 0.6, opacity=0.6))
        L.append(dict(d=smooth_open(T([(-14, 24), (-6, 36), (-4, 50)])), stroke=sk['line'], sw=lw * 0.6, opacity=0.6))
    for f in over:
        fd = smooth_closed(T(_union_outline(f)))
        L.append(dict(d=fd, fill=sk['fill'], stroke=sk['line'], sw=lw * 0.9,
                      shade=dict(color=sk['sh'], dx=2 * s, dy=3 * s, k=0.85, blur=min(hb, 3) * s, opacity=sk.get('sh_op', 0.8))))
    return L
