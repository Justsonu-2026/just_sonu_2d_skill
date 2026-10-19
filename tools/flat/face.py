"""Flat-style face kit: eyes (6 states), pupils, brows, nose, 16 mouths, tilak, blush.

All shapes are built from primitives in a local space and placed with (cx, cy, s, sx, flip):
  s = scale, sx = horizontal foreshortening for 3/4 / side views, flip = mirror (+1 / -1).
"""
import math
from tools.art.geom import smooth_closed, smooth_open, ellipse_pts, poly_d
from .palette import KANHA

P = KANHA
LW = 5.0          # face line width
EYE_STATES = ['open', 'half', 'closed', 'happy', 'squint', 'wide']
MOUTHS = ['rest', 'AI', 'E', 'O', 'U', 'MBP', 'FV', 'L', 'WQ',
          'smile', 'laugh', 'oh', 'frown', 'grit', 'nervous', 'smirk']

ERX, ERY = 40.0, 50.0   # eye white radii


def T(pts, cx, cy, s=1.0, sx=1.0, flip=1, rot=0.0):
    c, si = math.cos(rot), math.sin(rot)
    out = []
    for x, y in pts:
        x *= flip
        x, y = x * c - y * si, x * si + y * c
        out.append((cx + x * s * sx, cy + y * s))
    return out


def eye_white_pts(cx, cy, s=1.0, sx=1.0, flip=1):
    # slightly egg-shaped: flatter on the inner-bottom side
    pts = [(math.cos(a) * ERX * (1.0 + 0.06 * math.sin(a)), math.sin(a) * ERY * (0.96 if math.sin(a) > 0 else 1.0))
           for a in [2 * math.pi * i / 32 for i in range(32)]]
    return T(pts, cx, cy, s, sx, flip)


def eye_white_d(cx, cy, s=1.0, sx=1.0, flip=1):
    return smooth_closed(eye_white_pts(cx, cy, s, sx, flip))


def eye_white(cx, cy, s=1.0, sx=1.0, flip=1):
    d = eye_white_d(cx, cy, s, sx, flip)
    return [dict(d=d, fill=P['eye_white'], stroke=P['line'], sw=LW * s)]


def pupil(cx, cy, s=1.0, sx=1.0):
    r = 31 * s
    iris = smooth_closed(ellipse_pts(cx, cy, r * sx, r, 28))
    lower = smooth_closed(ellipse_pts(cx, cy + 9 * s, r * 0.78 * sx, r * 0.62, 24))
    pup = smooth_closed(ellipse_pts(cx, cy, 17 * s * sx, 18 * s, 20))
    return [dict(d=iris, fill=P['iris'], extra=[dict(d=lower, fill=P['iris_hi'])]),
            dict(d=pup, fill=P['pupil']),
            dict(d=smooth_closed(ellipse_pts(cx + 11 * s * sx, cy - 12 * s, 10 * s * sx, 10 * s, 16)), fill='#ffffff'),
            dict(d=smooth_closed(ellipse_pts(cx - 10 * s * sx, cy + 12 * s, 4.5 * s * sx, 4.5 * s, 12)), fill='#ffffff')]


def _arc(a0, a1, rx=ERX, ry=ERY, n=12, k=1.0):
    return [(math.cos(a) * rx * k, math.sin(a) * ry * k) for a in [a0 + (a1 - a0) * i / (n - 1) for i in range(n)]]


def eye_over(cx, cy, s=1.0, sx=1.0, flip=1, state='open', skin=None):
    skin = skin or P['skin']
    white = eye_white_d(cx, cy, s, sx, flip)
    L = []
    lash = lambda pts, w=9: dict(d=smooth_open(T(pts, cx, cy, s, sx, flip)), stroke=P['line'], sw=w * s)
    top = _arc(math.radians(195), math.radians(345))
    flick = [(ERX * 0.92, -ERY * 0.32), (ERX * 1.25, -ERY * 0.62)]
    if state in ('open', 'wide'):
        L.append(lash(top))
        L.append(lash(flick, 7))
    elif state in ('half', 'squint'):
        lid_y = -4 if state == 'half' else 6
        edge = [(-ERX - 4, lid_y + 6), (-ERX * 0.5, lid_y - 2), (0, lid_y - 4), (ERX * 0.5, lid_y - 2), (ERX + 4, lid_y + 4)]
        lid = edge + [(ERX + 10, -ERY - 12), (-ERX - 10, -ERY - 12)]
        L.append(dict(d=smooth_closed(T(lid, cx, cy, s, sx, flip), 0.5), fill=skin, clip=white))
        if state == 'squint':
            bot_edge = [(-ERX - 4, 22), (0, 28), (ERX + 4, 20)]
            bot = bot_edge + [(ERX + 10, ERY + 12), (-ERX - 10, ERY + 12)]
            L.append(dict(d=smooth_closed(T(bot, cx, cy, s, sx, flip), 0.5), fill=skin, clip=white))
            L.append(lash(bot_edge, 5))
        L.append(lash(edge))
        L.append(lash([(ERX + 2, lid_y + 2), (ERX * 1.25, lid_y - 14)], 7))
    elif state == 'closed':
        L.append(lash([(-ERX, 6), (-ERX * 0.5, 20), (0, 24), (ERX * 0.5, 20), (ERX, 6)]))
        L.append(lash([(ERX * 0.95, 8), (ERX * 1.25, 0)], 7))
    elif state == 'happy':
        L.append(lash([(-ERX, 16), (-ERX * 0.5, -6), (0, -12), (ERX * 0.5, -6), (ERX, 16)], 10))
    return L


def brow(cx, cy, s=1.0, sx=1.0, flip=1, raise_=0.0, angle=0.0):
    """Short thick rounded brow. angle>0 lifts the inner end (worried), <0 angry."""
    base = [(-30, 4), (-12, -6), (10, -8), (30, -2)]
    pts = []
    for x, y in base:
        t = (x + 30) / 60.0
        pts.append((x, y - raise_ - angle * (1 - t) * 14))
    return [dict(d=smooth_open(T(pts, cx, cy, s, sx, flip)), stroke=P['brow'], sw=11 * s)]


def nose(cx, cy, s=1.0, sx=1.0, flip=1, view='front'):
    if view == 'front':
        return [dict(d=smooth_open(T([(-12, -2), (-6, 8), (6, 8), (12, -2)], cx, cy, s, sx)), stroke=P['line'], sw=4.5 * s)]
    # 3/4: little hook pointing toward the facing side
    return [dict(d=smooth_open(T([(4, -18), (-8, 2), (-4, 10), (8, 8)], cx, cy, s, sx, flip)), stroke=P['line'], sw=4.5 * s)]


def tilak(cx, cy, s=1.0, sx=1.0):
    u = [(-13, -30), (-12, 6), (-6, 22), (0, 25), (6, 22), (12, 6), (13, -30),
         (6, -30), (5, 6), (3, 14), (0, 15), (-3, 14), (-5, 6), (-6, -30)]
    return [dict(d=smooth_closed(T(u, cx, cy, s, sx), 0.4), fill=P['tilak'], stroke=P['line'], sw=2.5 * s),
            dict(d=smooth_closed(ellipse_pts(cx, cy + 8 * s, 2.8 * s * sx, 6 * s, 10)), fill=P['tilak_red'])]


def blush(cx, cy, rx=30, ry=16, s=1.0, sx=1.0):
    return [dict(d=smooth_closed(ellipse_pts(cx, cy, rx * s * sx, ry * s, 20)), fill=P['blush'], opacity=0.55)]


# ------------------------------------------------------------------- mouths
def _open(cx, cy, s, sx, outline, teeth_top=0.0, teeth_bot=0.0, tongue=0.0, tongue_up=False):
    O = T(outline, cx, cy, s, sx)
    d = smooth_closed(O)
    ys = [p[1] for p in outline]
    top, bot = min(ys), max(ys)
    h = bot - top
    ex = []
    if teeth_top:
        ex.append(dict(d=poly_d(T([(-70, top - 20), (70, top - 20), (70, top + h * teeth_top), (-70, top + h * teeth_top)],
                                  cx, cy, s, sx)), fill=P['teeth']))
    if teeth_bot:
        ex.append(dict(d=poly_d(T([(-70, bot + 20), (70, bot + 20), (70, bot - h * teeth_bot), (-70, bot - h * teeth_bot)],
                                  cx, cy, s, sx)), fill=P['teeth']))
    if tongue:
        if tongue_up:
            tg = ellipse_pts(0, top + h * 0.45, 16, h * 0.4, 18)
        else:
            tg = ellipse_pts(0, bot + h * 0.1, 22, h * tongue, 18)
        ex.append(dict(d=smooth_closed(T(tg, cx, cy, s, sx)), fill=P['tongue']))
    return [dict(d=d, fill=P['mouth_in'], extra=ex), dict(d=d, stroke=P['line'], sw=LW * s)]


def _line(pts, cx, cy, s, sx, w=LW):
    return dict(d=smooth_open(T(pts, cx, cy, s, sx)), stroke=P['line'], sw=w * s)


def mouth(name, cx, cy, s=1.0, sx=1.0):
    if name == 'rest':
        return [_line([(-22, -4), (-10, 4), (0, 6), (10, 4), (22, -4)], cx, cy, s, sx)]
    if name == 'smile':
        return _open(cx, cy, s, sx, [(-30, -6), (0, -2), (30, -6), (20, 12), (0, 22), (-20, 12)], teeth_top=0.3, tongue=0.3)
    if name == 'laugh':
        return _open(cx, cy, s, sx, [(-32, -8), (0, -4), (32, -8), (24, 18), (0, 36), (-24, 18)], teeth_top=0.22, tongue=0.35)
    if name == 'AI':
        return _open(cx, cy, s, sx, [(-24, -4), (0, -6), (24, -4), (18, 14), (0, 28), (-18, 14)], teeth_top=0.2, tongue=0.3)
    if name == 'E':
        return _open(cx, cy, s, sx, [(-28, -2), (0, -6), (28, -2), (16, 9), (0, 12), (-16, 9)], teeth_top=0.4, teeth_bot=0.25)
    if name == 'O':
        return _open(cx, cy, s, sx, ellipse_pts(0, 6, 14, 18, 16), tongue=0.25)
    if name == 'oh':
        return _open(cx, cy, s, sx, ellipse_pts(0, 8, 18, 24, 16), tongue=0.25)
    if name in ('U', 'WQ'):
        r = 9 if name == 'U' else 7
        return _open(cx, cy, s, sx, ellipse_pts(0, 4, r, r + 2, 14))
    if name == 'MBP':
        return [_line([(-18, 0), (0, 2), (18, 0)], cx, cy, s, sx, LW * 1.1),
                _line([(-8, 8), (0, 10), (8, 8)], cx, cy, s, sx, 3)]
    if name == 'FV':
        L = _open(cx, cy, s, sx, [(-22, -4), (0, -6), (22, -4), (16, 6), (0, 9), (-16, 6)], teeth_top=0.7)
        return L + [_line([(-16, 10), (0, 14), (16, 10)], cx, cy, s, sx, 3.5)]
    if name == 'L':
        return _open(cx, cy, s, sx, [(-22, -4), (0, -6), (22, -4), (16, 12), (0, 22), (-16, 12)], teeth_top=0.22,
                     tongue=0.4, tongue_up=True)
    if name == 'frown':
        return [_line([(-22, 8), (-10, 0), (0, -2), (10, 0), (22, 8)], cx, cy, s, sx)]
    if name == 'grit':
        L = _open(cx, cy, s, sx, [(-28, -6), (0, -8), (28, -6), (26, 10), (0, 12), (-26, 10)], teeth_top=0.5, teeth_bot=0.5)
        L.insert(1, dict(d=smooth_open(T([(-28, 2), (0, 2), (28, 2)], cx, cy, s, sx)), stroke=P['line'], sw=2.5 * s))
        return L
    if name == 'nervous':
        return [_line([(-24, 2), (-14, -4), (-4, 3), (6, -4), (16, 3), (26, -2)], cx, cy, s, sx)]
    if name == 'smirk':
        return [_line([(-20, 2), (-4, 4), (10, 0), (24, -10)], cx, cy, s, sx)]
    raise KeyError(name)
