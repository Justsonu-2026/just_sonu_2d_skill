"""Parametric face features in the reference's style (eyes, pupils, brows, nose, mouths,
tilak, blush). All functions return lists of svgpart layers in U coordinates.

`s`  = overall scale (1.0 = front-view size in the reference)
`sx` = horizontal foreshortening (1.0 front, ~0.75 far eye in 3/4)
`flip` = +1 for the eye on screen-right, -1 for screen-left (mirrors the lash flick).
"""
import math
import numpy as np
from .geom import smooth_closed, smooth_open, ellipse_pts, poly_d
from .palette import KANHA as P

EYE_STATES = ['open', 'half', 'closed', 'happy', 'squint', 'wide']


def _tf(pts, cx, cy, s, sx, flip=1, rot=0.0):
    out = []
    c, si = math.cos(rot), math.sin(rot)
    for x, y in pts:
        x = x * flip
        x, y = x * c - y * si, x * si + y * c
        out.append((cx + x * s * sx, cy + y * s))
    return out


# eye white outline (local, before transform). Upper lid arcs higher on the outer side.
_EYE_UP = [(-50, 6), (-44, -22), (-26, -42), (0, -48), (26, -42), (44, -24), (51, 2)]
_EYE_LO = [(47, 20), (30, 38), (0, 45), (-28, 40), (-46, 24)]


def eye_white_pts(cx, cy, s, sx, flip, wide=False):
    k = 1.08 if wide else 1.0
    pts = [(x * k, y * k) for x, y in _EYE_UP + _EYE_LO]
    return _tf(pts, cx, cy, s, sx, flip)


def eye_white(cx, cy, s=1.0, sx=1.0, flip=1):
    """Eye white (one shape for every open state). Pupils are clipped to it (clip_to)."""
    d = smooth_closed(eye_white_pts(cx, cy, s, sx, flip))
    return [dict(d=d, fill=P['eye_white'],
                 shade=dict(color=P['eye_white_sh'], dx=0, dy=14 * s, k=1.0, blur=6 * s))]


def eye_white_d(cx, cy, s=1.0, sx=1.0, flip=1):
    return smooth_closed(eye_white_pts(cx, cy, s, sx, flip))


def pupil(cx, cy, s=1.0, sx=1.0, r=36, wide=False):
    """Iris + pupil + highlights, centred at (cx, cy). Separate part so it can move/scale."""
    if wide:
        r *= 0.86
    rx, ry = r * s * sx, r * s
    iris = smooth_closed(ellipse_pts(cx, cy, rx, ry, 28))
    pup = smooth_closed(ellipse_pts(cx, cy + 2 * s, rx * 0.5, ry * 0.52, 20))
    h1 = smooth_closed(ellipse_pts(cx + 12 * s * sx, cy - 13 * s, 10 * s * sx, 10 * s, 14))
    h2 = smooth_closed(ellipse_pts(cx - 13 * s * sx, cy + 15 * s, 5 * s * sx, 5 * s, 10))
    return [
        dict(d=iris, fill=P['iris'], stroke=P['iris_dark'], sw=4 * s,
             shade=dict(color=P['iris_dark'], dx=0, dy=10 * s, k=0.85, blur=5 * s),
             light=dict(color=P['iris_light'], dx=0, dy=14 * s, k=0.55, blur=6 * s, opacity=0.9)),
        dict(d=pup, fill=P['pupil']),
        dict(d=h1, fill='#ffffff'),
        dict(d=h2, fill='#ffffff', opacity=0.9),
    ]


def _lash_line(cx, cy, s, sx, flip, pts_local, w=8.5):
    pts = _tf(pts_local, cx, cy, s, sx, flip)
    return dict(d=smooth_open(pts), fill=None, stroke=P['lash'], sw=w * s)


def _flick(cx, cy, s, sx, flip, base=(50, 2), tip=(62, -10)):
    p = _tf([base, ((base[0] + tip[0]) / 2 + 2, base[1] - 2), tip], cx, cy, s, sx, flip)
    return dict(d=smooth_open(p), fill=None, stroke=P['lash'], sw=5 * s)


def eye_over(cx, cy, s=1.0, sx=1.0, flip=1, state='open', skin=None):
    """Everything above the pupil for one eye state: lids (clipped to the eye white) + lashes."""
    skin = skin or P['skin']
    white = eye_white_d(cx, cy, s, sx, flip)
    L = []
    if state in ('open', 'wide'):
        L.append(_lash_line(cx, cy, s, sx, flip, _EYE_UP))
        L.append(_flick(cx, cy, s, sx, flip, (51, 2), (60, -8)))
        L.append(dict(d=smooth_open(_tf(_EYE_LO[1:-1], cx, cy, s, sx, flip)), stroke=P['skin_line'], sw=3 * s))
    elif state == 'half':
        lid_edge = [(-50, 6), (-30, -6), (0, -10), (30, -8), (51, 2)]
        lid = _tf([(-60, 10)] + lid_edge + [(60, 4), (60, -70), (-60, -70)], cx, cy, s, sx, flip)
        L.append(dict(d=smooth_closed(lid, 0.6), fill=skin, clip=white,
                      shade=dict(color=P['skin_sh'], dx=0, dy=-12 * s, k=1, blur=5 * s, opacity=0.7)))
        L.append(_lash_line(cx, cy, s, sx, flip, _EYE_UP, 4.5))
        L.append(_lash_line(cx, cy, s, sx, flip, lid_edge))
        L.append(_flick(cx, cy, s, sx, flip, (51, 2), (62, -6)))
        L.append(dict(d=smooth_open(_tf(_EYE_LO[1:-1], cx, cy, s, sx, flip)), stroke=P['skin_line'], sw=3 * s))
    elif state == 'squint':
        lid_edge = [(-50, 8), (-28, 2), (0, 0), (28, 0), (51, 4)]
        lid = _tf([(-60, 12)] + lid_edge + [(60, 6), (60, -70), (-60, -70)], cx, cy, s, sx, flip)
        L.append(dict(d=smooth_closed(lid, 0.6), fill=skin, clip=white))
        bot_edge = [(-50, 14), (-30, 22), (0, 26), (30, 22), (51, 12)]
        bot = _tf(bot_edge + [(60, 70), (-60, 70)], cx, cy, s, sx, flip)
        L.append(dict(d=smooth_closed(bot, 0.6), fill=skin, clip=white))
        L.append(_lash_line(cx, cy, s, sx, flip, lid_edge))
        L.append(dict(d=smooth_open(_tf(bot_edge[1:-1], cx, cy, s, sx, flip)), stroke=P['skin_line'], sw=3 * s))
    elif state == 'closed':
        L.append(_lash_line(cx, cy, s, sx, flip, [(-48, 8), (-26, 20), (0, 24), (26, 20), (50, 8)], 7.5))
        L.append(_flick(cx, cy, s, sx, flip, (50, 8), (60, 2)))
    elif state == 'happy':
        L.append(_lash_line(cx, cy, s, sx, flip, [(-44, 18), (-24, -4), (0, -12), (24, -4), (46, 16)], 8.5))
    return L


def brow(cx, cy, s=1.0, sx=1.0, flip=1, raise_=0.0, angle=0.0, kind='normal'):
    """Thick tapered brow arc. angle>0 lifts the inner end (worried); <0 angry."""
    shapes = {
        'normal': [(-38, 6), (-20, -6), (4, -10), (30, -4), (44, 6)],
        'up':     [(-38, 2), (-20, -12), (4, -16), (30, -10), (44, 0)],
    }
    base = shapes.get(kind, shapes['normal'])
    pts = []
    for x, y in base:
        # inner end is at -x (towards the nose) for flip=+1 (screen-right eye)
        t = (x + 38) / 82.0
        y = y - raise_ + angle * (1 - t) * 14 - angle * t * 4
        pts.append((x, y))
    top = _tf(pts, cx, cy, s, sx, flip)
    # tapered thickness: thick in the middle, thin at both ends
    th = [5, 10, 12, 10, 4]
    upper, lower = [], []
    for i, (x, y) in enumerate(top):
        upper.append((x, y - th[i] * s))
        lower.append((x, y + th[i] * s * 0.8))
    d = smooth_closed(upper + lower[::-1])
    return [dict(d=d, fill=P['brow'], stroke=P['brow'], sw=2 * s)]


def nose(cx, cy, s=1.0, view='front', flip=1):
    if view == 'front':
        tip = smooth_closed(ellipse_pts(cx, cy, 20 * s, 13 * s, 20))
        return [
            dict(d=smooth_closed(ellipse_pts(cx, cy + 4 * s, 24 * s, 15 * s, 20)), fill=P['skin_sh2'], opacity=0.75,
                 blur=4 * s),
            dict(d=tip, fill=P['skin'], opacity=0.9, blur=1.5 * s),
            dict(d=smooth_closed(ellipse_pts(cx - 4 * s, cy - 4 * s, 7 * s, 5 * s, 12)), fill=P['skin_hi'], opacity=0.8,
                 blur=2 * s),
            dict(d=smooth_open([(cx - 21 * s, cy - 1 * s), (cx - 16 * s, cy + 9 * s), (cx - 6 * s, cy + 10 * s)]),
                 stroke=P['skin_line'], sw=2.6 * s, opacity=0.8),
            dict(d=smooth_open([(cx + 21 * s, cy - 1 * s), (cx + 16 * s, cy + 9 * s), (cx + 6 * s, cy + 10 * s)]),
                 stroke=P['skin_line'], sw=2.6 * s, opacity=0.8),
        ]
    if view == 'q34':
        pts = _tf([(-6, -26), (10, -4), (16, 6), (8, 14), (-6, 12)], cx, cy, s, 1, flip)
        return [dict(d=smooth_open(pts), stroke=P['skin_line'], sw=3.2 * s),
                dict(d=smooth_closed(_tf([(0, 0), (12, 4), (14, 10), (2, 12), (-6, 8)], cx, cy, s, 1, flip)),
                     fill=P['skin_sh'], opacity=0.5, blur=2 * s)]
    return []


def tilak(cx, cy, s=1.0, sx=1.0):
    outer = _tf([(-17, -34), (-15, 10), (-8, 30), (0, 34), (8, 30), (15, 10), (17, -34),
                 (8, -34), (7, 8), (4, 20), (0, 22), (-4, 20), (-7, 8), (-8, -34)], cx, cy, s, sx)
    return [dict(d=smooth_closed(outer, 0.5), fill=P['tilak'], stroke=P['tilak_line'], sw=2 * s)]


def blush(cx, cy, rx, ry, s=1.0, opacity=0.45):
    return [dict(d=smooth_closed(ellipse_pts(cx, cy, rx * s, ry * s, 20)), fill=P['blush'],
                 opacity=opacity, blur=9 * s)]


# ----------------------------------------------------------------------------- mouths
MOUTHS = ['rest', 'AI', 'E', 'O', 'U', 'MBP', 'FV', 'L', 'WQ',
          'smile', 'laugh', 'oh', 'frown', 'grit', 'nervous', 'smirk']


def _m(pts, cx, cy, s, sx):
    return _tf(pts, cx, cy, s, sx)


def _open_mouth(cx, cy, s, sx, outline, teeth_top=0.0, teeth_bot=0.0, tongue=0.0, tongue_up=False,
                lip=True):
    """Generic open mouth from an outline (local pts). teeth_* = fraction of height."""
    O = _m(outline, cx, cy, s, sx)
    d = smooth_closed(O)
    ys = [p[1] for p in outline]
    top, bot = min(ys), max(ys)
    h = bot - top
    ex = []
    if teeth_top > 0:
        t = _m([(-60, top - 20), (60, top - 20), (60, top + h * teeth_top), (-60, top + h * teeth_top)], cx, cy, s, sx)
        ex.append(dict(d=poly_d(t), fill=P['teeth']))
    if teeth_bot > 0:
        t = _m([(-60, bot + 20), (60, bot + 20), (60, bot - h * teeth_bot), (-60, bot - h * teeth_bot)], cx, cy, s, sx)
        ex.append(dict(d=poly_d(t), fill=P['teeth']))
    if tongue > 0:
        if tongue_up:
            tg = _m(ellipse_pts(0, top + h * 0.45, 18, h * 0.4, 18), cx, cy, s, sx)
        else:
            tg = _m(ellipse_pts(0, bot + h * 0.15, 24, h * tongue, 18), cx, cy, s, sx)
        ex.append(dict(d=smooth_closed(tg), fill=P['tongue']))
    L = [dict(d=d, fill=P['mouth_in'], extra=ex)]
    L.append(dict(d=d, stroke=P['lips_line'], sw=3.2 * s))
    if lip:  # soft pink lower lip highlight under the opening
        lo = _m([(-14, bot + 4), (0, bot + 7), (14, bot + 4)], cx, cy, s, sx)
        L.append(dict(d=smooth_open(lo), stroke=P['lips'], sw=4 * s, opacity=0.8))
    return L


def mouth(name, cx, cy, s=1.0, sx=1.0):
    if name == 'rest':
        lower = _m([(-22, 2), (-10, 12), (0, 14), (10, 12), (23, 1), (10, 4), (0, 5), (-10, 4)], cx, cy, s, sx)
        upper = _m([(-26, -2), (-12, -6), (-4, -4), (0, -5), (4, -4), (12, -6), (26, -4), (12, 2), (0, 4), (-12, 2)],
                   cx, cy, s, sx)
        line = _m([(-30, -4), (-16, 3), (0, 5), (16, 2), (30, -6)], cx, cy, s, sx)
        return [dict(d=smooth_closed(lower), fill=P['lips'], opacity=0.95),
                dict(d=smooth_closed(upper), fill=P['lips'], opacity=0.7),
                dict(d=smooth_open(line), stroke=P['lips_line'], sw=3.4 * s),
                dict(d=smooth_open(_m([(-33, -8), (-29, -3)], cx, cy, s, sx)), stroke=P['lips_line'], sw=2.2 * s),
                dict(d=smooth_open(_m([(33, -10), (29, -5)], cx, cy, s, sx)), stroke=P['lips_line'], sw=2.2 * s)]
    if name == 'smile':
        o = [(-34, -6), (-16, -2), (0, -1), (16, -2), (34, -8), (24, 12), (0, 24), (-24, 13)]
        return _open_mouth(cx, cy, s, sx, o, teeth_top=0.3, tongue=0.3)
    if name == 'laugh':
        o = [(-36, -8), (-16, -4), (0, -3), (16, -4), (36, -10), (28, 18), (0, 38), (-28, 19)]
        return _open_mouth(cx, cy, s, sx, o, teeth_top=0.22, tongue=0.35)
    if name == 'AI':
        o = [(-28, -4), (-12, -6), (0, -5), (12, -6), (28, -4), (20, 16), (0, 30), (-20, 16)]
        return _open_mouth(cx, cy, s, sx, o, teeth_top=0.2, tongue=0.3)
    if name == 'E':
        o = [(-32, -2), (-14, -6), (0, -6), (14, -6), (32, -3), (18, 10), (0, 14), (-18, 10)]
        return _open_mouth(cx, cy, s, sx, o, teeth_top=0.38, teeth_bot=0.25)
    if name == 'O':
        return _open_mouth(cx, cy, s, sx, ellipse_pts(0, 6, 15, 19, 16), tongue=0.25)
    if name == 'oh':
        return _open_mouth(cx, cy, s, sx, ellipse_pts(0, 8, 19, 25, 16), tongue=0.25)
    if name == 'U':
        L = _open_mouth(cx, cy, s, sx, ellipse_pts(0, 4, 9, 11, 14), lip=False)
        ring = _m(ellipse_pts(0, 4, 16, 17, 16), cx, cy, s, sx)
        return [dict(d=smooth_closed(ring), fill=P['lips'], stroke=P['lips_line'], sw=2.5 * s)] + L
    if name == 'WQ':
        L = _open_mouth(cx, cy, s, sx, ellipse_pts(0, 4, 7, 8, 14), lip=False)
        ring = _m(ellipse_pts(0, 4, 13, 14, 16), cx, cy, s, sx)
        return [dict(d=smooth_closed(ring), fill=P['lips'], stroke=P['lips_line'], sw=2.5 * s)] + L
    if name == 'MBP':
        lips = _m([(-24, 0), (-10, -5), (0, -4), (10, -5), (24, 0), (10, 8), (0, 9), (-10, 8)], cx, cy, s, sx)
        return [dict(d=smooth_closed(lips), fill=P['lips'], stroke=P['lips_line'], sw=2.4 * s),
                dict(d=smooth_open(_m([(-22, 1), (0, 2), (22, 1)], cx, cy, s, sx)), stroke=P['lips_line'], sw=3 * s)]
    if name == 'FV':
        o = [(-24, -4), (0, -6), (24, -4), (18, 6), (0, 9), (-18, 6)]
        L = _open_mouth(cx, cy, s, sx, o, teeth_top=0.7, lip=False)
        lo = _m([(-22, 6), (0, 10), (22, 6), (14, 14), (0, 16), (-14, 14)], cx, cy, s, sx)
        return L + [dict(d=smooth_closed(lo), fill=P['lips'], stroke=P['lips_line'], sw=2.2 * s)]
    if name == 'L':
        o = [(-26, -4), (-10, -6), (0, -5), (10, -6), (26, -4), (18, 12), (0, 22), (-18, 12)]
        return _open_mouth(cx, cy, s, sx, o, teeth_top=0.22, tongue=0.4, tongue_up=True)
    if name == 'frown':
        line = _m([(-26, 8), (-12, 0), (0, -2), (12, 0), (26, 8)], cx, cy, s, sx)
        lower = _m([(-12, 4), (0, 8), (12, 4), (0, 2)], cx, cy, s, sx)
        return [dict(d=smooth_closed(lower), fill=P['lips'], opacity=0.8),
                dict(d=smooth_open(line), stroke=P['lips_line'], sw=3.4 * s)]
    if name == 'grit':
        o = [(-32, -6), (0, -8), (32, -6), (30, 10), (0, 12), (-30, 10)]
        L = _open_mouth(cx, cy, s, sx, o, teeth_top=0.5, teeth_bot=0.5, lip=False)
        L.append(dict(d=smooth_open(_m([(-30, 2), (0, 2), (30, 2)], cx, cy, s, sx)), stroke=P['lips_line'], sw=2 * s))
        for x in (-16, 0, 16):
            L.append(dict(d=poly_d(_m([(x, -6), (x, 10)], cx, cy, s, sx), False), stroke=P['eye_white_sh'], sw=1.6 * s))
        return L
    if name == 'nervous':
        line = _m([(-28, 2), (-18, -4), (-8, 3), (2, -4), (12, 3), (22, -3), (30, 2)], cx, cy, s, sx)
        return [dict(d=smooth_open(line), stroke=P['lips_line'], sw=3.4 * s)]
    if name == 'smirk':
        line = _m([(-24, 2), (-8, 4), (8, 2), (22, -6), (30, -12)], cx, cy, s, sx)
        lower = _m([(-6, 4), (6, 8), (16, 2), (6, 4)], cx, cy, s, sx)
        return [dict(d=smooth_closed(lower), fill=P['lips'], opacity=0.8),
                dict(d=smooth_open(line), stroke=P['lips_line'], sw=3.4 * s)]
    raise KeyError(name)
