"""Kanha v2 (flat style) — FRONT view, built entirely from primitives (no tracing).

Canvas 720 x 1800 U, ground y=1765, centre x=360. ~2.9 heads tall toddler.
Style rules: flat fill + ONE hard cel shadow (light from top-left), one bold outline
colour (P['line']), highlights only on eyes / hair / gold.
"""
import math
from tools.art.geom import (smooth_closed, smooth_open, ellipse_pts, capsule_pts, union_pts, union_d,
                            taper_pts, catmull_rom_d)
from tools.art.style import PartSet, bone_for
from tools.art.hands import hand_layers, HANDS, HANDS_SIDE
from . import face as F
from .palette import KANHA

P = KANHA
LW = 6.0
OUT = 'build/parts/kanha/front'
SVG_OUT = 'characters/boy/parts/front'


def cel(color, dx=10, dy=12, k=0.97):
    """Hard-edged cel shadow: the part's own shape offset toward the light, clipped."""
    return dict(color=color, dx=-dx, dy=-dy, k=k, blur=0.6)


def fillp(d, fill, sh=None, lw=LW, outer=True, **kw):
    L = dict(d=d, fill=fill, stroke=P['line'], sw=lw, outer=outer)
    if sh:
        L['shade'] = cel(sh, **kw.pop('cel', {}))
    L.update(kw)
    return L


def skin(d, **kw):
    return fillp(d, P['skin'], P['skin_sh'], **kw)


def band(d, w=18):
    return [dict(d=d, stroke=P['line'], sw=w + 2 * 4, cap='butt'), dict(d=d, stroke=P['gold'], sw=w, cap='butt'),
            dict(d=d, stroke=P['gold_hi'], sw=w * 0.25, cap='butt', opacity=0.9)]


def chain(pts, w=8):
    d = smooth_open(pts)
    return [dict(d=d, stroke=P['line'], sw=w + 7), dict(d=d, stroke=P['gold'], sw=w)]


def mirror(pts, cx=360.0):
    return [(2 * cx - x, y) for x, y in pts][::-1]


def build(write=True, out=None, svg_out=None, only=None, palette=None):
    global P
    P = palette or KANHA
    F.P = P
    PS = PartSet(out or OUT, svg_out or SVG_OUT)

    def add(name, layers, pivot, z, backing=False, line_z=None, **extra):
        PS.add(name, layers, pivot, z, backing, line_z, bone=bone_for(name), **extra)

    hand_skin = dict(fill=P['skin'], sh=P['skin_sh'], line=P['line'], blur=0.6, sh_op=1.0, lw=5.0)
    HEAD = (360, 840)

    # ------------------------------------------------------------------ HEAD
    face_pts = [(360 + 196 * math.cos(a), 640 + 186 * math.sin(a) * (1.06 if math.sin(a) > 0 else 1.0))
                for a in [2 * math.pi * i / 40 for i in range(40)]]
    face_d = smooth_closed(face_pts)
    fl = [dict(d=face_d, fill=P['skin'], stroke=P['line'], sw=LW, shade=cel(P['skin_sh'], 14, 10, 0.98))]
    fl += F.blush(250, 738) + F.blush(470, 738) + F.tilak(360, 525, 1.0)
    add('head', fl, HEAD, 20)

    for side, cx in (('R', 168), ('L', 552)):
        sg = -1 if side == 'R' else 1
        add(f'ear_{side}', [skin(smooth_closed(ellipse_pts(cx, 668, 34, 44, 24))),
                            dict(d=smooth_open([(cx - 6 * sg, 648), (cx + 8 * sg, 668), (cx - 2 * sg, 690)]),
                                 stroke=P['line'], sw=4)], (cx - 20 * sg, 668), 18)

    # hair (back mass): union of ellipses + curl tips, hard highlight streak
    tips = []
    for x, y, a in ((128, 700, 2.4), (150, 760, 2.0), (196, 790, 1.75), (592, 700, 0.75), (570, 760, 1.15),
                    (524, 790, 1.4)):
        dx, dy = math.cos(a), math.sin(a)
        tips.append(taper_pts([(x - dx * 70, y - dy * 70), (x, y), (x + dx * 40 - dy * 12, y + dy * 40 + dx * 12)],
                              60, 0, 60))
    hair_back = [ellipse_pts(360, 560, 250, 236, 48), ellipse_pts(160, 640, 76, 120, 32),
                 ellipse_pts(560, 640, 76, 120, 32)] + tips
    hb_d = catmull_rom_d(union_pts(hair_back, step=4, sigma=1.0))
    hi = taper_pts([(200, 520), (230, 420), (330, 360)], 4, 0, 26)
    add('hair_back', [dict(d=hb_d, fill=P['hair'], stroke=P['line'], sw=LW, shade=cel(P['hair_sh'], 16, 16, 0.97),
                           extra=[dict(d=catmull_rom_d(hi), fill=P['hair_hi'])])], HEAD, 5)

    # bun + bead band, feather
    bun = smooth_closed(ellipse_pts(360, 322, 70, 62, 32))
    beads = []
    for i in range(9):
        t = i / 8.0
        x = 296 + 128 * t
        y = 372 + 16 * math.sin(math.pi * t)
        beads.append(dict(d=smooth_closed(ellipse_pts(x, y, 11, 11, 12)), fill=P['gold'], stroke=P['line'], sw=3.5))
    add('bun', [dict(d=bun, fill=P['hair'], stroke=P['line'], sw=LW, shade=cel(P['hair_sh'], 10, 10, 0.95),
                     extra=[dict(d=catmull_rom_d(taper_pts([(318, 320), (340, 284), (380, 272)], 3, 0, 14)),
                                 fill=P['hair_hi'])])] + beads, (360, 360), 4.6)
    fc, frot = (424, 196), 0.42
    fe = lambda rx, ry, n=36: smooth_closed(ellipse_pts(fc[0], fc[1], rx, ry, n, rot=frot))
    vane = [(fc[0] + 62 * math.cos(a) * math.cos(frot) - 112 * math.sin(a) * math.sin(frot) * (1.0 if math.sin(a) < 0 else 0.92),
             fc[1] + 62 * math.cos(a) * math.sin(frot) + 112 * math.sin(a) * math.cos(frot))
            for a in [2 * math.pi * i / 40 for i in range(40)]]
    feather = [dict(d=smooth_open([(380, 330), (396, 290), (410, 250)]), stroke=P['line'], sw=9),
               dict(d=smooth_closed(vane), fill=P['feather_g'], stroke=P['line'], sw=LW * 0.85,
                    shade=cel(P['feather_g2'], -10, -10, 0.95)),
               dict(d=fe(40, 54), fill=P['feather_y'], stroke=P['line'], sw=3),
               dict(d=fe(29, 40), fill=P['feather_teal']),
               dict(d=fe(20, 28), fill=P['feather_blue']),
               dict(d=fe(11, 16), fill=P['feather_dark'])]
    add('feather', feather, (388, 318), 4.4)

    # fringe: three lock groups of tapered pointed locks
    def lock(root, mid, tip, w):
        return taper_pts([root, mid, tip], w, 0, w)
    groups = {
        0: [lock((240, 410), (206, 480), (184, 566), 96), lock((292, 404), (276, 470), (262, 540), 84)],
        1: [ellipse_pts(362, 418, 196, 64, 36), lock((344, 404), (334, 462), (320, 520), 72),
            lock((396, 404), (410, 458), (424, 512), 70)],
        2: [lock((432, 404), (450, 470), (462, 540), 84), lock((480, 410), (514, 480), (536, 566), 96)],
    }
    piv = {0: (250, 420), 1: (360, 400), 2: (470, 420)}
    for i, polys in groups.items():
        d = catmull_rom_d(union_pts(polys, step=3, sigma=0.9))
        ex = []
        if i == 1:
            ex.append(dict(d=catmull_rom_d(taper_pts([(250, 420), (330, 384), (430, 392)], 3, 0, 18)), fill=P['hair_hi']))
        add(f'hair_lock_{i}', [dict(d=d, fill=P['hair'], stroke=P['line'], sw=LW, shade=cel(P['hair_sh'], 8, 8, 0.97),
                                    extra=ex)], piv[i], 32 + (0.5 if i == 1 else 0))

    # face features
    eyes = {'R': (282, 652, -1), 'L': (438, 652, 1)}
    for side, (cx, cy, flip) in eyes.items():
        add(f'eye_{side}_white', F.eye_white(cx, cy, 1.0, 1.0, flip), (cx, cy), 21, eye_white_of=f'eye_{side}')
        for st in F.EYE_STATES:
            add(f'eye_{side}_{st}', F.eye_over(cx, cy, 1.0, 1.0, flip, st), (cx, cy), 23, swap=f'eye_{side}', state=st)
        add(f'pupil_{side}', F.pupil(cx, cy + 6, 1.0), (cx, cy + 6), 22, clip_to=f'eye_{side}_white')
        add(f'brow_{side}', F.brow(cx, 568, 1.0, 1.0, flip), (cx, 568), 25)
    add('nose', F.nose(360, 712), (360, 712), 24)
    for m in F.MOUTHS:
        add(f'mouth_{m}', F.mouth(m, 360, 764, 1.0), (360, 764), 26, swap='mouth', state=m)
    for side, (ex, ey) in (('R', (166, 704)), ('L', (554, 704))):
        add(f'earring_{side}', [
            dict(d=smooth_closed(ellipse_pts(ex, ey + 10, 9, 9, 14)), fill=P['gold'], stroke=P['line'], sw=3.5),
            dict(d=smooth_closed([(ex, ey + 22), (ex + 14, ey + 44), (ex + 10, ey + 62), (ex, ey + 68), (ex - 10, ey + 62),
                                  (ex - 14, ey + 44)]), fill=P['gold'], stroke=P['line'], sw=3.5,
                 shade=cel(P['gold_sh'], 5, 5, 0.9))], (ex, ey), 27)

    # --------------------------------------------------------------------- BODY
    add('neck', [dict(d=smooth_closed([(316, 760), (404, 760), (410, 880), (310, 880)]), fill=P['skin'])], (360, 870), 7.9)
    torso_R = [(312, 818), (266, 830), (232, 852), (214, 890), (218, 940), (230, 990), (234, 1060), (238, 1140), (250, 1220)]
    torso = torso_R + mirror(torso_R)
    td = smooth_closed(torso)
    tl = [dict(d=td, fill=P['skin'], stroke=P['line'], sw=LW, shade=cel(P['skin_sh'], 16, 6, 0.97),
               extra=[dict(d=smooth_closed(ellipse_pts(360, 820, 110, 30, 24)), fill=P['skin_sh'])]),
          dict(d=smooth_open([(286, 976), (316, 992), (346, 986)]), stroke=P['line'], sw=4),
          dict(d=smooth_open([(374, 986), (404, 992), (434, 976)]), stroke=P['line'], sw=4),
          dict(d=smooth_closed(ellipse_pts(360, 1076, 7, 9, 12)), fill=P['line'])]
    add('torso', tl, (360, 1150), 8)

    nk = chain([(278, 836), (300, 880), (360, 902), (420, 880), (442, 836)])
    nk += chain([(296, 846), (316, 930), (360, 972), (404, 930), (424, 846)], 7)
    nk += [dict(d=smooth_closed(ellipse_pts(360, 912, 19, 19, 20)), fill=P['gold'], stroke=P['line'], sw=4,
                shade=cel(P['gold_sh'], 5, 5, 0.9)),
           dict(d=smooth_closed(ellipse_pts(360, 912, 8, 8, 14)), fill=P['gem']),
           dict(d=smooth_closed([(360, 968), (374, 988), (360, 1010), (346, 988)]), fill=P['gem'], stroke=P['line'], sw=4)]
    add('necklace', nk, (360, 830), 12)

    # arms (limb chains drawn with outline backing -> seamless joints)
    arms = {'R': dict(sh=(244, 926), el=(206, 1030), wr=(172, 1118), flip=-1),
            'L': dict(sh=(476, 926), el=(514, 1030), wr=(548, 1118), flip=1)}
    for side, a in arms.items():
        lsh = dict(cel=dict(dx=10 * a['flip'], dy=0, k=0.97))
        up = smooth_closed(capsule_pts(a['sh'], a['el'], 42, 39))
        add(f'upperarm_{side}', [skin(up, **lsh, extra=band(smooth_open([(a['sh'][0] - 60, 950), (a['sh'][0], 958),
                                                                         (a['sh'][0] + 60, 950)])))],
            a['sh'], 14, backing=True, line_z=13.8)
        fo = smooth_closed(capsule_pts(a['el'], a['wr'], 38, 33))
        add(f'forearm_{side}', [skin(fo, **lsh, extra=band(smooth_open([(a['wr'][0] - 50, a['wr'][1] - 18),
                                                                        (a['wr'][0], a['wr'][1] - 12),
                                                                        (a['wr'][0] + 50, a['wr'][1] - 18)]), 12))],
            a['el'], 14.1, backing=True, line_z=13.8)
        for h in HANDS + HANDS_SIDE:
            add(f'hand_{side}_{h}', hand_layers(h, a['wr'][0], a['wr'][1] - 4, 1.0, a['flip'], 0.0, skin=hand_skin),
                a['wr'], 14.2, swap=f'hand_{side}', state=h, backing=True, line_z=13.8)

    # hips: dhoti top + sash band
    hips = [(220, 1110), (360, 1130), (500, 1110), (510, 1220), (512, 1300), (360, 1320), (208, 1300), (210, 1220)]
    sash = [(216, 1104), (290, 1118), (360, 1126), (430, 1118), (504, 1104), (508, 1150), (506, 1192), (430, 1204),
            (360, 1212), (290, 1204), (214, 1192), (212, 1150)]
    hl = [fillp(smooth_closed(hips), P['dhoti'], P['dhoti_sh'], cel=dict(dx=0, dy=14, k=0.97)),
          dict(d=smooth_closed(sash), fill=P['sash'], stroke=P['line'], sw=LW * 0.8, shade=cel(P['sash_sh'], 0, 12, 0.97)),
          dict(d=smooth_open([(232, 1150), (290, 1162), (330, 1170)]), stroke=P['sash_sh'], sw=6),
          dict(d=smooth_open([(390, 1170), (430, 1162), (488, 1150)]), stroke=P['sash_sh'], sw=6)]
    add('hips', hl, (360, 1160), 9, backing=True, line_z=8.4)

    leg_R = [(222, 1250), (362, 1250), (366, 1380), (352, 1466), (330, 1494), (292, 1500), (252, 1494), (230, 1466),
             (216, 1380)]
    for side in ('R', 'L'):
        pts = leg_R if side == 'R' else mirror(leg_R)
        x0 = 222 if side == 'R' else 366
        hem = smooth_open([(x0 - 10, 1468), (x0 + 66, 1486), (x0 + 142, 1468)])
        fold = smooth_open([(x0 + 70 + (14 if side == 'R' else -14), 1310), (x0 + 72, 1380), (x0 + 70, 1440)])
        add(f'dhoti_{side}', [fillp(smooth_closed(pts), P['dhoti'], P['dhoti_sh'],
                                    cel=dict(dx=(-14 if side == 'R' else 14), dy=8, k=0.97),
                                    extra=[dict(d=hem, stroke=P['dhoti_hem'], sw=16),
                                           dict(d=fold, stroke=P['dhoti_sh'], sw=6)])],
            (290, 1260) if side == 'R' else (430, 1260), 8.6, backing=True, line_z=8.4)

    flap = [(328, 1186), (392, 1186), (404, 1250), (398, 1320), (382, 1370), (360, 1396), (338, 1370), (322, 1320),
            (316, 1250)]
    add('flap', [dict(d=smooth_closed(flap, 0.7), fill=P['sash'], stroke=P['line'], sw=LW * 0.8,
                      shade=cel(P['sash_sh'], 10, 0, 0.95),
                      extra=[dict(d=smooth_open([(346, 1210), (342, 1300), (352, 1370)]), stroke=P['sash_sh'], sw=5),
                             dict(d=smooth_open([(374, 1210), (378, 1300), (368, 1370)]), stroke=P['sash_sh'], sw=5)])],
        (360, 1196), 11)
    add('buckle', [dict(d=smooth_closed(ellipse_pts(360, 1162, 30, 28, 24)), fill=P['gold'], stroke=P['line'], sw=4.5,
                        shade=cel(P['gold_sh'], 6, 6, 0.95)),
                   dict(d=smooth_closed(ellipse_pts(360, 1162, 12, 11, 16)), fill=P['gem'])], (360, 1162), 11.5)

    for side, sx in (('R', 292), ('L', 428)):
        sg = 1 if side == 'R' else -1
        sd = smooth_closed(capsule_pts((sx, 1460), (sx, 1640), 40, 38))
        add(f'shin_{side}', [skin(sd, cel=dict(dx=-10 * sg, dy=0, k=0.97),
                                  extra=band(smooth_open([(sx - 50, 1606), (sx, 1614), (sx + 50, 1606)]), 13))],
            (sx, 1470), 6.6, backing=True, line_z=6.0)
        fx = lambda x: sx + (x - 292) * sg
        fpts = [(fx(260), 1668), (fx(318), 1664), (fx(340), 1690), (fx(342), 1730), (fx(326), 1756), (fx(280), 1764),
                (fx(226), 1760), (fx(198), 1744), (fx(204), 1716), (fx(230), 1690)]
        fd = smooth_closed(fpts)
        toes = [dict(d=smooth_open([(fx(x), 1744), (fx(x + 2), 1760)]), stroke=P['line'], sw=4) for x in (236, 262, 290)]
        add(f'foot_{side}', [skin(fd, cel=dict(dx=0, dy=12, k=0.97))] + toes, (sx, 1650), 6.4, backing=True, line_z=6.0)

    PS.skeleton = dict(
        root=(360, 1765), hips=(360, 1180), chest=(360, 1100), neck=(360, 840), head=HEAD, head_top=(360, 330),
        feather=(388, 318), lock_0=piv[0], lock_1=piv[1], lock_2=piv[2], earring_R=(166, 704), earring_L=(554, 704),
        upperarm_R=arms['R']['sh'], forearm_R=arms['R']['el'], hand_R=arms['R']['wr'], hand_R_tip=(160, 1236),
        upperarm_L=arms['L']['sh'], forearm_L=arms['L']['el'], hand_L=arms['L']['wr'], hand_L_tip=(560, 1236),
        thigh_R=(290, 1260), shin_R=(292, 1470), foot_R=(292, 1650), foot_R_tip=(250, 1750),
        thigh_L=(430, 1260), shin_L=(428, 1470), foot_L=(428, 1650), foot_L_tip=(470, 1750),
        flap=(360, 1196))
    return PS.write(only) if write else PS


if __name__ == '__main__':
    build()
