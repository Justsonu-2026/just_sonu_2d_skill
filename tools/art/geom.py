"""Geometry helpers for authoring clean vector parts.

Coordinates are in "U" units = 4 px of the 4x-upscaled reference crop = 1/4 reference px.
Every view crop is 720 x 1800 U with the character's centre at x=360 and the ground at
y=GROUND (feet bottom).

Main ideas
- A *guide mask* comes from the segmented reference (tools/segment_ref.py).
- `mask_to_paths` turns a binary mask into smooth closed cubic Bezier paths
  (contour -> uniform resample -> circular Gaussian smoothing -> Catmull-Rom -> Bezier).
- Hand-authored shapes use `smooth_closed(points)` (Catmull-Rom through key points) or
  primitives (`capsule`, `ellipse_pts`).
"""
import math
import numpy as np
import cv2

GROUND = 1765.0
CENTER_X = 360.0
W, H = 720, 1800


# ---------------------------------------------------------------- basic point utils
def resample_closed(pts, step):
    pts = np.asarray(pts, float)
    seg = np.diff(np.vstack([pts, pts[:1]]), axis=0)
    L = np.hypot(seg[:, 0], seg[:, 1])
    total = L.sum()
    n = max(int(total / step), 8)
    cum = np.concatenate([[0], np.cumsum(L)])
    t = np.linspace(0, total, n, endpoint=False)
    out = []
    j = 0
    for tt in t:
        while cum[j + 1] < tt:
            j += 1
        f = (tt - cum[j]) / max(L[j], 1e-9)
        out.append(pts[j] + f * seg[j])
    return np.array(out)


def smooth_circular(pts, sigma):
    if sigma <= 0:
        return pts
    n = len(pts)
    r = int(3 * sigma)
    k = np.exp(-0.5 * (np.arange(-r, r + 1) / sigma) ** 2)
    k /= k.sum()
    ext = np.vstack([pts[-r:], pts, pts[:r]]) if r > 0 else pts
    out = np.stack([np.convolve(ext[:, i], k, mode='valid') for i in range(2)], 1)
    return out[:n]


def catmull_rom_d(pts, closed=True, tension=1.0, fmt='%.1f'):
    """Cubic Bezier SVG path data through points (centripetal-ish uniform CR)."""
    pts = np.asarray(pts, float)
    n = len(pts)
    if n < 2:
        return ''
    f = lambda p: (fmt % p[0]) + ',' + (fmt % p[1])
    d = ['M' + f(pts[0])]
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if (closed or i > 0) else pts[i]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (closed or i + 2 < n) else pts[(i + 1) % n]
        c1 = p1 + (p2 - p0) * tension / 6.0
        c2 = p2 - (p3 - p1) * tension / 6.0
        d.append('C' + f(c1) + ' ' + f(c2) + ' ' + f(p2))
    if closed:
        d.append('Z')
    return ' '.join(d)


def smooth_closed(points, tension=1.0):
    return catmull_rom_d(points, True, tension)


def smooth_open(points, tension=1.0):
    return catmull_rom_d(points, False, tension)


def poly_d(points, closed=True):
    s = 'M' + ' L'.join('%.1f,%.1f' % (x, y) for x, y in points)
    return s + (' Z' if closed else '')


# ---------------------------------------------------------------- primitives
def ellipse_pts(cx, cy, rx, ry, n=24, rot=0.0, a0=0.0, a1=2 * math.pi):
    out = []
    cr, sr = math.cos(rot), math.sin(rot)
    for i in range(n):
        a = a0 + (a1 - a0) * i / n
        x, y = rx * math.cos(a), ry * math.sin(a)
        out.append((cx + x * cr - y * sr, cy + x * sr + y * cr))
    return out


def capsule_pts(p0, p1, r0, r1, n_cap=10):
    """Closed outline of a tapered capsule from p0 (radius r0) to p1 (radius r1)."""
    p0 = np.array(p0, float); p1 = np.array(p1, float)
    d = p1 - p0
    L = np.hypot(*d)
    ang = math.atan2(d[1], d[0])
    pts = []
    # cap at p1: from -90 to +90 relative to direction
    for i in range(n_cap + 1):
        a = ang - math.pi / 2 + math.pi * i / n_cap
        pts.append(p1 + r1 * np.array([math.cos(a), math.sin(a)]))
    for i in range(n_cap + 1):
        a = ang + math.pi / 2 + math.pi * i / n_cap
        pts.append(p0 + r0 * np.array([math.cos(a), math.sin(a)]))
    return resample_closed(np.array(pts), max(L, 1) / 12 + 2)


# ---------------------------------------------------------------- masks
def poly_mask(points, shape=(H, W)):
    m = np.zeros(shape, np.uint8)
    cv2.fillPoly(m, [np.round(np.asarray(points)).astype(np.int32)], 1)
    return m.astype(bool)


def fill_holes(mask):
    m = mask.astype(np.uint8)
    h, w = m.shape
    ff = m.copy()
    pad = np.zeros((h + 2, w + 2), np.uint8)
    cv2.floodFill(ff, pad, (0, 0), 1)
    return (m | (1 - ff)).astype(bool)


def morph(mask, op, r):
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))
    m = mask.astype(np.uint8)
    f = {'open': cv2.MORPH_OPEN, 'close': cv2.MORPH_CLOSE,
         'dilate': cv2.MORPH_DILATE, 'erode': cv2.MORPH_ERODE}[op]
    return cv2.morphologyEx(m, f, k).astype(bool)


def largest_components(mask, k=1, min_area=0):
    n, lab, stats, _ = cv2.connectedComponentsWithStats(mask.astype(np.uint8), 8)
    if n <= 1:
        return mask
    areas = stats[1:, cv2.CC_STAT_AREA]
    order = np.argsort(-areas)[:k] + 1
    out = np.zeros_like(mask, bool)
    for o in order:
        if stats[o, cv2.CC_STAT_AREA] >= min_area:
            out |= lab == o
    return out


def mask_to_paths(mask, step=6.0, sigma=2.5, min_area=200, holes=False):
    """Binary mask -> list of smooth closed path 'd' strings (outer contours)."""
    m = mask.astype(np.uint8) * 255
    mode = cv2.RETR_CCOMP if holes else cv2.RETR_EXTERNAL
    cs, _ = cv2.findContours(m, mode, cv2.CHAIN_APPROX_NONE)
    out = []
    for c in cs:
        if cv2.contourArea(c) < min_area:
            continue
        p = c[:, 0, :].astype(float)
        p = resample_closed(p, step)
        p = smooth_circular(p, sigma)
        out.append(catmull_rom_d(p))
    return out


def mask_to_d(mask, **kw):
    return ' '.join(mask_to_paths(mask, **kw))


def mask_contour_pts(mask, step=6.0, sigma=2.5):
    m = mask.astype(np.uint8) * 255
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    c = max(cs, key=cv2.contourArea)
    p = resample_closed(c[:, 0, :].astype(float), step)
    return smooth_circular(p, sigma)


def taper_pts(pts, w0, w1=None, wmid=None, n=24):
    """Closed outline of a stroke along `pts` whose width goes w0 -> wmid -> w1 (tapered)."""
    from scipy.interpolate import splprep, splev
    pts = np.asarray(pts, float)
    k = min(3, len(pts) - 1)
    tck, _ = splprep([pts[:, 0], pts[:, 1]], s=0, k=k)
    t = np.linspace(0, 1, n)
    x, y = splev(t, tck)
    dx, dy = splev(t, tck, der=1)
    L = np.hypot(dx, dy) + 1e-9
    nx, ny = -dy / L, dx / L
    w1 = 0.0 if w1 is None else w1
    wmid = max(w0, w1) if wmid is None else wmid
    wt = np.where(t < 0.5, w0 + (wmid - w0) * (t / 0.5), wmid + (w1 - wmid) * ((t - 0.5) / 0.5)) / 2
    left = np.stack([x + nx * wt, y + ny * wt], 1)
    right = np.stack([x - nx * wt, y - ny * wt], 1)[::-1]
    return np.vstack([left, right])


def taper_d(pts, w0, w1=None, wmid=None, n=24):
    return catmull_rom_d(taper_pts(pts, w0, w1, wmid, n))


def union_pts(polys, sc=4.0, step=3.0, sigma=1.2):
    """Union of several closed point polygons -> smoothed outline points."""
    allp = np.vstack([np.asarray(p, float) for p in polys])
    mn = allp.min(0) - 6; mx = allp.max(0) + 6
    w, h = int((mx[0] - mn[0]) * sc) + 1, int((mx[1] - mn[1]) * sc) + 1
    m = np.zeros((h, w), np.uint8)
    for p in polys:
        cv2.fillPoly(m, [np.round((np.asarray(p, float) - mn) * sc).astype(np.int32)], 1)
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    c = max(cs, key=cv2.contourArea)[:, 0, :].astype(float) / sc + mn
    return smooth_circular(resample_closed(c, step), sigma)


def union_d(polys, **kw):
    return catmull_rom_d(union_pts(polys, **kw))
