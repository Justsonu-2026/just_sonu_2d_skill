"""Procedural hair texture: tapered strand strokes flowing from a crown point, clipped
to the hair silhouette. Gives the painted, strand-y look of the reference hair."""
import math
import numpy as np
from .geom import taper_d
from .palette import KANHA as P


def strands(mask, crown, n=40, a0=-170, a1=-10, r0=30, step=8, lmax=420, gravity=0.012,
            seed=1, color=None, w=6, opacity=0.65, hi_every=4, hi_color=None, side_curl=0.0,
            wave=0.0, wave_len=40.0):
    rng = np.random.default_rng(seed)
    H, W = mask.shape
    out = []
    for i in range(n):
        a = math.radians(a0 + (a1 - a0) * (i + rng.uniform(-0.3, 0.3)) / max(n - 1, 1))
        d = np.array([math.cos(a), math.sin(a)])
        p = np.array(crown, float) + d * (r0 + rng.uniform(0, 30))
        pts = [p.copy()]
        L = 0
        curl = rng.uniform(-0.01, 0.01) + side_curl * np.sign(d[0])
        phase = rng.uniform(0, 6.28)
        while L < lmax * rng.uniform(0.6, 1.0):
            # bend toward gravity (down) and curl
            c = curl + wave * math.sin(L / wave_len + phase)
            d = d + np.array([0, gravity]) + c * np.array([-d[1], d[0]])
            d /= np.linalg.norm(d)
            p = p + d * step
            x, y = int(round(p[0])), int(round(p[1]))
            if not (0 <= x < W and 0 <= y < H) or not mask[y, x]:
                break
            pts.append(p.copy())
            L += step
        if len(pts) < 5:
            continue
        hi = (i % hi_every == 0)
        col = (hi_color or P['hair_hi']) if hi else (color or P['hair_sh'])
        out.append(dict(d=taper_d(pts, w * 0.5, 0.0, w), fill=col, opacity=opacity * (0.7 if hi else 1.0),
                        blur=1.2 if hi else 0.6))
    return out
