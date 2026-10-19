"""Shared flat-style building blocks (used by every view builder)."""
import math
from tools.art.geom import (smooth_closed, smooth_open, ellipse_pts, capsule_pts, union_pts, taper_pts, catmull_rom_d)
from . import palette

LW = 6.0


class Kit:
    def __init__(self, P):
        self.P = P

    def cel(self, color, dx=10, dy=12, k=0.97):
        return dict(color=color, dx=-dx, dy=-dy, k=k, blur=0.6)

    def fillp(self, d, fill, sh=None, lw=LW, outer=True, **kw):
        L = dict(d=d, fill=fill, stroke=self.P['line'], sw=lw, outer=outer)
        c = kw.pop('cel', {})
        if sh:
            L['shade'] = self.cel(sh, **c)
        L.update(kw)
        return L

    def skin(self, d, **kw):
        return self.fillp(d, self.P['skin'], self.P['skin_sh'], **kw)

    def band(self, d, w=18):
        P = self.P
        return [dict(d=d, stroke=P['line'], sw=w + 8, cap='butt'), dict(d=d, stroke=P['gold'], sw=w, cap='butt'),
                dict(d=d, stroke=P['gold_hi'], sw=w * 0.25, cap='butt', opacity=0.9)]

    def chain(self, pts, w=8):
        d = smooth_open(pts)
        return [dict(d=d, stroke=self.P['line'], sw=w + 7), dict(d=d, stroke=self.P['gold'], sw=w)]

    def hand_skin(self):
        P = self.P
        return dict(fill=P['skin'], sh=P['skin_sh'], line=P['line'], blur=0.6, sh_op=1.0, lw=5.0)

    def hair(self, polys, cel=(16, 16), extra=None):
        P = self.P
        d = catmull_rom_d(union_pts(polys, step=4, sigma=1.0))
        return dict(d=d, fill=P['hair'], stroke=P['line'], sw=LW, shade=self.cel(P['hair_sh'], *cel, 0.97),
                    extra=extra or [])

    def streak(self, pts, w=24):
        return dict(d=catmull_rom_d(taper_pts(pts, 3, 0, w)), fill=self.P['hair_hi'])

    def tip(self, x, y, a, L=70, w=60):
        dx, dy = math.cos(a), math.sin(a)
        return taper_pts([(x - dx * L, y - dy * L), (x, y), (x + dx * 40 - dy * 12, y + dy * 40 + dx * 12)], w, 0, w)

    def lock(self, root, mid, tip, w):
        return taper_pts([root, mid, tip], w, 0, w)

    def beads(self, x0, x1, y, sag=16, n=9, r=11):
        P = self.P
        out = []
        for i in range(n):
            t = i / (n - 1)
            out.append(dict(d=smooth_closed(ellipse_pts(x0 + (x1 - x0) * t, y + sag * math.sin(math.pi * t), r, r, 12)),
                            fill=P['gold'], stroke=P['line'], sw=3.5))
        return out

    def feather(self, fc, frot, quill, rx=62, ry=112, sx=1.0):
        P = self.P
        fe = lambda a, b, n=36: smooth_closed(ellipse_pts(fc[0], fc[1], a * sx, b, n, rot=frot))
        vane = []
        for i in range(40):
            a = 2 * math.pi * i / 40
            u, v = rx * sx * math.cos(a), ry * math.sin(a) * (1.0 if math.sin(a) < 0 else 0.92)
            vane.append((fc[0] + u * math.cos(frot) - v * math.sin(frot), fc[1] + u * math.sin(frot) + v * math.cos(frot)))
        return [dict(d=smooth_open(quill), stroke=P['line'], sw=9),
                dict(d=smooth_closed(vane), fill=P['feather_g'], stroke=P['line'], sw=LW * 0.85,
                     shade=self.cel(P['feather_g2'], -10, -10, 0.95)),
                dict(d=fe(40, 54), fill=P['feather_y'], stroke=P['line'], sw=3),
                dict(d=fe(29, 40), fill=P['feather_teal']), dict(d=fe(20, 28), fill=P['feather_blue']),
                dict(d=fe(11, 16), fill=P['feather_dark'])]

    def earring(self, ex, ey):
        P = self.P
        return [dict(d=smooth_closed(ellipse_pts(ex, ey + 10, 9, 9, 14)), fill=P['gold'], stroke=P['line'], sw=3.5),
                dict(d=smooth_closed([(ex, ey + 22), (ex + 14, ey + 44), (ex + 10, ey + 62), (ex, ey + 68),
                                      (ex - 10, ey + 62), (ex - 14, ey + 44)]), fill=P['gold'], stroke=P['line'],
                     sw=3.5, shade=self.cel(P['gold_sh'], 5, 5, 0.9))]

    def buckle(self, cx, cy, rx=30, ry=28):
        P = self.P
        return [dict(d=smooth_closed(ellipse_pts(cx, cy, rx, ry, 24)), fill=P['gold'], stroke=P['line'], sw=4.5,
                     shade=self.cel(P['gold_sh'], 6, 6, 0.95)),
                dict(d=smooth_closed(ellipse_pts(cx, cy, rx * 0.4, ry * 0.4, 16)), fill=P['gem'])]

    def foot(self, pts, toes_x, toe_y=1744, cel=(0, 12)):
        P = self.P
        L = [self.skin(smooth_closed(pts), cel=dict(dx=cel[0], dy=cel[1], k=0.97))]
        L += [dict(d=smooth_open([(x, toe_y), (x + 2, toe_y + 16)]), stroke=P['line'], sw=4) for x in toes_x]
        return L


def mirror(pts, cx=360.0):
    return [(2 * cx - x, y) for x, y in pts][::-1]
