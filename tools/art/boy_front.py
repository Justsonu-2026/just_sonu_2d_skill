"""Kanha — FRONT view part builder.

Guide: build/guide/front_classes.npy (reference crop x 562..742, y 555..1005 at 4x).
All coordinates in U (see geom.py). Output: build/parts/boy/front/*.png + meta.json,
SVG masters in characters/boy/parts/front/.
"""
import json, os
import numpy as np
from .geom import *
from .svgpart import write_part
from .common import load_classes, yy_xx
from .palette import KANHA as P
from . import face as F
from .hairtex import strands
from .hands import hand_layers, HANDS, HANDS_SIDE

VIEW = 'front'
OUT = 'build/parts/boy/front'
SVG_OUT = 'characters/boy/parts/front'

LINE = 3.8      # outer line width (U)
LINE_IN = 3.0   # inner detail lines


def shade(color, dx=8, dy=10, k=0.94, blur=7, **kw):
    return dict(color=color, dx=dx, dy=dy, k=k, blur=blur, **kw)


def skin_layer(d, **kw):
    L = dict(d=d, fill=P['skin'], stroke=P['skin_line'], sw=LINE, outer=True,
             shade=shade(P['skin_sh'], 9, 7, 0.93, 8))
    L.update(kw)
    return L


def gold_band(d, w=20):
    return [dict(d=d, stroke=P['gold_line'], sw=w + 5, cap='butt'), dict(d=d, stroke=P['gold'], sw=w, cap='butt'),
            dict(d=d, stroke=P['gold_hi'], sw=w * 0.22, opacity=0.7, cap='butt')]


def mirror_pts(pts, cx=360.0):
    return [(2 * cx - x, y) for x, y in pts][::-1]


HAIR_STYLE = dict(fill=P['hair'], stroke=P['hair_line'], sw=LINE * 0.8,
                  shade=shade(P['hair_sh'], 10, 12, 0.92, 10))


def hair_sheen(blobs):
    """Soft painted highlight patches (blurred ellipses) like the reference's hair."""
    return [dict(d=smooth_closed(ellipse_pts(x, y, rx, ry, 24, rot=r)), fill=P['hair_hi'], opacity=o, blur=b)
            for x, y, rx, ry, r, o, b in blobs]


def build(write=True, palette=None, out=None, svg_out=None, only=None):
    from .style import PartSet, bone_for, set_palette
    from .palette import KANHA
    set_palette(palette or KANHA)
    C = load_classes(VIEW)
    Y, X = yy_xx()
    PS = PartSet(out or OUT, svg_out or SVG_OUT)

    def add(name, layers, pivot, z, backing=False, line_z=None, **extra):
        PS.add(name, layers, pivot, z, backing, line_z, bone=bone_for(name), **extra)

    HAIR_STYLE = dict(fill=P['hair'], stroke=P['hair_line'], sw=LINE * 0.8, shade=shade(P['hair_sh'], 10, 12, 0.92, 10))

    # ------------------------------------------------------------------ HEAD
    head_reg = Y < 885
    face_core = (C['skin_all'] | C['gold']) & head_reg & (X > 192) & (X < 532) & (Y > 470)
    face_core = largest_components(fill_holes(morph(face_core, 'close', 8)))
    face_core = morph(face_core, 'open', 6)
    dome = poly_mask(ellipse_pts(362, 655, 166, 205, 48))
    face_pts = [(362, 452), (282, 466), (220, 520), (194, 600), (190, 680), (198, 756), (222, 818), (268, 860),
                (318, 876), (362, 880), (406, 876), (456, 860), (502, 818), (526, 756), (534, 680), (530, 600),
                (504, 520), (442, 466)]
    face_d = smooth_closed(face_pts)
    face_ext = poly_mask(union_pts([face_pts]))
    head_pivot = (360, 850)

    face_layers = [dict(d=face_d, fill=P['skin'], stroke=P['skin_line'], sw=LINE,
                        shade=[shade(P['skin_sh'], 0, 12, 0.92, 12, opacity=0.9)],
                        light=dict(color=P['skin_hi'], dx=-30, dy=-40, k=0.55, blur=30, opacity=0.5))]
    face_layers += F.blush(250, 770, 36, 20, opacity=0.3)
    face_layers += F.blush(474, 770, 36, 20, opacity=0.3)
    face_layers += F.tilak(364, 556, 1.1, 1.0)
    add('head', face_layers, head_pivot, 20)

    for side, cx in (('R', 188), ('L', 536)):
        sg = -1 if side == 'R' else 1
        ear = ellipse_pts(cx, 712, 24, 36, 24, rot=0.12 * sg)
        ear_d = smooth_closed(ear)
        inner = [(cx - 4 * sg, 692), (cx + 6 * sg, 712), (cx - 2 * sg, 734)]
        add(f'ear_{side}', [skin_layer(ear_d, outer=False, shade=shade(P['skin_sh'], 6 * sg, 4, 0.8, 6)),
                            dict(d=smooth_open(inner), stroke=P['skin_line'], sw=LINE_IN, opacity=0.8)],
            (cx - 16 * sg, 715), 18)

    # hair back = whole hair silhouette (minus feather), filled behind the face
    hair_m = C['hair'] & head_reg & (Y > 235)
    hair_m = largest_components(morph(hair_m, 'open', 2))
    hair_all = fill_holes(morph(hair_m | face_ext, 'close', 6)) & ~(C['green'] & (Y < 300))
    hair_all = largest_components(hair_all)
    hair_back_d = mask_to_d(hair_all, step=4, sigma=1.1)
    sheen = hair_sheen([(280, 360, 110, 55, -0.5, 0.45, 26), (460, 350, 90, 45, 0.5, 0.35, 24),
                        (140, 560, 40, 90, 0.2, 0.3, 20), (590, 560, 40, 90, -0.2, 0.3, 20),
                        (370, 300, 60, 30, 0.0, 0.3, 18)])
    hb = [dict(d=hair_back_d, extra=sheen, **HAIR_STYLE)]
    tex_mask = morph(hair_all, 'erode', 6)
    kw = dict(step=6, gravity=0.025, wave=0.09, wave_len=22, w=4.5, opacity=0.5, hi_every=3)
    hb += strands(tex_mask, (368, 330), n=40, a0=-178, a1=-2, r0=40, lmax=520, seed=3, **kw)
    hb += strands(tex_mask, (368, 330), n=16, a0=150, a1=205, r0=120, lmax=400, seed=5, **kw)
    hb += strands(tex_mask, (368, 330), n=16, a0=-25, a1=30, r0=120, lmax=400, seed=6, **kw)
    add('hair_back', hb, head_pivot, 5)

    # hair front locks (bangs) over the forehead; split into 3 locks for overlap
    bang_zone = morph(dome, 'dilate', 18) & (Y < 612)
    bangs = (hair_m | (dome & ~face_core)) & bang_zone
    bangs = morph(fill_holes(bangs), 'open', 2)
    cuts = [(X < 300), (X >= 300) & (X < 430), (X >= 430)]
    lock_piv = [(250, 470), (365, 440), (470, 470)]
    for i, cm in enumerate(cuts):
        m = bangs & morph(cm, 'dilate', 8 if i == 1 else 0)
        m = largest_components(m)
        if m.sum() < 300:
            continue
        d = mask_to_d(m, step=4, sigma=1.1)
        tex = strands(morph(m, 'erode', 4), (368, 330), n=12, a0=-170, a1=-10, r0=60, step=6,
                      lmax=300, gravity=0.04, seed=10 + i, wave=0.09, wave_len=22, w=5, opacity=0.45)
        add(f'hair_lock_{i}', [dict(d=d, **HAIR_STYLE)] + tex, lock_piv[i], 32 + (1 if i == 1 else 0))

    # peacock feather (pivot at its quill, behind the top of the head)
    feather_m = (C['green'] | C['gold'] | C['dhoti'] | C['sash'] | (C['hair'] & (Y < 260))) & (Y < 300) & (X > 340)
    feather_m = largest_components(fill_holes(morph(feather_m, 'close', 5)))
    fd = mask_to_d(feather_m, step=4, sigma=1.2)
    feather_layers = [
        dict(d=fd, fill=P['feather_g'], stroke=P['feather_line'], sw=LINE_IN,
             shade=shade(P['feather_g3'], 8, 8, 0.9, 8),
             light=dict(color=P['feather_g2'], dx=-12, dy=-14, k=0.7, blur=10, opacity=0.9)),
    ]
    for a in np.linspace(-0.9, 0.9, 11):   # barbs
        feather_layers.append(dict(d=smooth_open([(398, 268), (430 + 40 * a, 200), (455 + 110 * a, 110)]),
                                   stroke=P['feather_g3'], sw=2.2, opacity=0.55, clip=fd))
    feather_layers += [
        dict(d=smooth_closed(ellipse_pts(462, 192, 52, 68, 30, rot=0.45)), fill=P['feather_y'],
             stroke=P['gold_line'], sw=2),
        dict(d=smooth_closed(ellipse_pts(458, 197, 38, 50, 28, rot=0.45)), fill=P['feather_teal']),
        dict(d=smooth_closed(ellipse_pts(455, 200, 27, 34, 24, rot=0.45)), fill=P['feather_blue']),
        dict(d=smooth_closed(ellipse_pts(452, 203, 16, 20, 20, rot=0.45)), fill=P['feather_dark']),
        dict(d=smooth_closed(ellipse_pts(448, 196, 5, 7, 10, rot=0.45)), fill='#8fc8ff', opacity=0.8),
    ]
    add('feather', feather_layers, (395, 275), 4)

    # ------------------------------------------------------------- FACE FEATURES
    eyes = {'R': (270, 676, -1), 'L': (452, 676, +1)}   # screen-left eye is the character's right
    for side, (cx, cy, flip) in eyes.items():
        add(f'eye_{side}_white', F.eye_white(cx, cy, 1.0, 1.0, flip), (cx, cy), 21, eye_white_of=f'eye_{side}')
        for st in F.EYE_STATES:
            add(f'eye_{side}_{st}', F.eye_over(cx, cy, 1.0, 1.0, flip, st), (cx, cy), 23,
                swap=f'eye_{side}', state=st)
        add(f'pupil_{side}', F.pupil(cx + 3 * flip, cy + 4, 1.0, 1.0), (cx + 3 * flip, cy + 4), 22,
            clip_to=f'eye_{side}_white')
        bx = cx - 10 * flip
        add(f'brow_{side}', F.brow(bx, 578, 1.05, 1.0, flip), (bx, 578), 25)
    add('nose', F.nose(361, 731, 1.45, 'front'), (361, 731), 24)
    for mname in F.MOUTHS:
        add(f'mouth_{mname}', F.mouth(mname, 366, 790, 1.25, 1.0), (366, 790), 26, swap='mouth', state=mname)

    for side, (ex, ey) in (('R', (186, 742)), ('L', (538, 742))):
        bead = smooth_closed(ellipse_pts(ex, ey + 12, 8, 9, 14))
        bell = [(ex, ey + 20), (ex + 9, ey + 30), (ex + 15, ey + 50), (ex + 12, ey + 64), (ex, ey + 70),
                (ex - 12, ey + 64), (ex - 15, ey + 50), (ex - 9, ey + 30)]
        gold = dict(fill=P['gold'], stroke=P['gold_line'], sw=2.2, shade=shade(P['gold_sh'], 4, 5, 0.85, 4),
                    light=dict(color=P['gold_hi'], dx=-4, dy=-6, k=0.4, blur=3))
        add(f'earring_{side}', [dict(d=bead, **gold), dict(d=smooth_closed(bell), **gold),
                                dict(d=smooth_closed(ellipse_pts(ex, ey + 72, 4, 4, 10)), **gold)], (ex, ey), 27)

    # --------------------------------------------------------------------- BODY
    neck = [(318, 800), (404, 800), (414, 895), (360, 908), (306, 895)]
    nd = smooth_closed(neck)
    add('neck', [dict(d=nd, fill=P['skin']),
                 dict(d=smooth_closed([(300, 820), (420, 820), (420, 880), (360, 896), (300, 880)]),
                      fill=P['skin_sh2'], opacity=0.6, blur=8, clip=nd)], (360, 900), 7.9)

    torso_L = [(312, 872), (262, 888), (222, 912), (196, 945), (182, 985), (194, 1008), (224, 1024),
               (232, 1080), (226, 1160), (222, 1290)]
    torso = torso_L + [(360, 1310)] + mirror_pts(torso_L)
    td = smooth_closed(torso)
    torso_layers = [skin_layer(td, outer=False, shade=[shade(P['skin_sh'], 0, -10, 0.9, 12)])]
    for sgn in (-1, 1):
        torso_layers.append(dict(d=smooth_closed(ellipse_pts(360 + sgn * 70, 1080, 80, 26, 20)), fill=P['skin_sh'],
                                 opacity=0.5, blur=10, clip=td))
        torso_layers.append(dict(d=smooth_open([(360 + sgn * 30, 1062), (360 + sgn * 80, 1070), (360 + sgn * 128, 1052)]),
                                 stroke=P['skin_line'], sw=LINE_IN, opacity=0.4))
        # armpit crease
        torso_layers.append(dict(d=smooth_open([(360 + sgn * 182, 990), (360 + sgn * 150, 1015), (360 + sgn * 136, 1040)]),
                                 stroke=P['skin_line'], sw=LINE_IN, opacity=0.7))
    torso_layers.append(dict(d=smooth_closed(ellipse_pts(360, 1135, 9, 6, 12)), fill=P['skin_line'], opacity=0.6))
    torso_layers.append(dict(d=smooth_closed(ellipse_pts(360, 884, 92, 26, 20)), fill=P['skin_sh2'], opacity=0.7,
                             blur=9, clip=td))
    add('torso', torso_layers, (360, 1250), 8)

    neck_layers = []
    short = [(268, 880), (300, 925), (360, 950), (420, 925), (452, 880)]
    long_ = [(292, 890), (310, 960), (340, 1030), (360, 1058), (380, 1030), (410, 960), (428, 890)]
    for c in (short, long_):
        neck_layers.append(dict(d=smooth_open(c), stroke=P['gold_line'], sw=12))
        neck_layers.append(dict(d=smooth_open(c), stroke=P['gold'], sw=8))
        neck_layers.append(dict(d=smooth_open(c), stroke=P['gold_hi'], sw=2.5, opacity=0.7))
    neck_layers.append(dict(d=smooth_closed(ellipse_pts(360, 968, 24, 26, 20)), fill=P['gold'],
                            stroke=P['gold_line'], sw=2.5, shade=shade(P['gold_sh'], 4, 4, 0.8, 4)))
    neck_layers.append(dict(d=smooth_closed(ellipse_pts(360, 968, 12, 13, 16)), fill=P['sash'],
                            stroke=P['sash_line'], sw=1.5))
    neck_layers.append(dict(d=smooth_closed(ellipse_pts(360, 1074, 13, 20, 16)), fill=P['gem'],
                            stroke=P['gold_line'], sw=3, light=dict(color=P['gem_hi'], dx=-3, dy=-6, k=0.4, blur=3)))
    add('necklace', neck_layers, (360, 885), 12)

    # arms: upper arm behind the torso's shoulder; forearm + elbow cap in front
    arm_spec = {'R': dict(sh=(205, 982), el=(166, 1150), wr=(152, 1250), flip=-1),
                'L': dict(sh=(515, 982), el=(554, 1150), wr=(568, 1250), flip=1)}
    for side, a in arm_spec.items():
        upd = smooth_closed(capsule_pts(a['sh'], a['el'], 43, 39))
        bx = a['sh'][0]
        band = smooth_open([(bx - 70, 1022), (bx, 1040), (bx + 70, 1024)])
        limb_sh = dict(color=P['skin_sh'], dx=-10 * a['flip'], dy=0, kx=0.86, ky=1.0, blur=8)
        add(f'upperarm_{side}', [skin_layer(upd, shade=limb_sh, extra=gold_band(band, 20))], a['sh'], 14,
            backing=True, line_z=13.8)
        fo = smooth_closed(capsule_pts(a['el'], a['wr'], 38, 30))
        wband = smooth_open([(a['wr'][0] - 50, a['wr'][1] - 14), (a['wr'][0], a['wr'][1] - 8),
                             (a['wr'][0] + 50, a['wr'][1] - 14)])
        add(f'forearm_{side}', [skin_layer(fo, shade=limb_sh, extra=gold_band(wband, 12))], a['el'], 14.1,
            backing=True, line_z=13.8)
        for hname in HANDS + HANDS_SIDE:
            add(f'hand_{side}_{hname}', hand_layers(hname, a['wr'][0], a['wr'][1] - 4, 1.12, a['flip'], 0.0),
                a['wr'], 14.2, swap=f'hand_{side}', state=hname, backing=True, line_z=13.8)

    # hips: dhoti top + sash band (authored over the traced guide)
    hips_pts = [(206, 1150), (300, 1170), (360, 1180), (420, 1168), (514, 1142), (530, 1250), (534, 1350),
                (360, 1370), (190, 1355), (192, 1250)]
    hips_d = smooth_closed(hips_pts)
    sash_pts = [(204, 1142), (262, 1150), (330, 1168), (360, 1176), (398, 1166), (468, 1148), (518, 1136),
                (526, 1205), (522, 1268), (480, 1262), (430, 1246), (360, 1240), (292, 1252), (236, 1276),
                (198, 1292), (196, 1215)]
    sash_d = smooth_closed(sash_pts)
    hips_layers = [
        dict(d=hips_d, fill=P['dhoti'], stroke=P['dhoti_line'], sw=LINE, outer=True,
             shade=shade(P['dhoti_sh'], 0, -14, 0.9, 10)),
        dict(d=sash_d, fill=P['sash'], stroke=P['sash_line'], sw=LINE_IN, shade=shade(P['sash_sh'], 0, -12, 0.9, 8),
             light=dict(color=P['sash_hi'], dx=0, dy=-26, k=0.8, blur=10, opacity=0.35)),
    ]
    for c in ([(222, 1200), (280, 1218), (326, 1236)], [(500, 1196), (442, 1214), (396, 1232)],
              [(214, 1166), (270, 1180), (318, 1196)], [(508, 1160), (452, 1176), (404, 1190)],
              [(206, 1240), (250, 1252)], [(516, 1232), (476, 1240)]):
        hips_layers.append(dict(d=smooth_open(c), stroke=P['sash_sh'], sw=7, opacity=0.9, blur=1.5))
        hips_layers.append(dict(d=smooth_open(c), stroke=P['sash_line'], sw=2, opacity=0.6))
    add('hips', hips_layers, (360, 1200), 9, backing=True, line_z=8.4)

    # dhoti legs (left/right): authored over the traced guide; under the hips, over the shins
    leg_R = [(214, 1300), (360, 1300), (366, 1420), (358, 1530), (346, 1582), (300, 1594), (252, 1588),
             (214, 1566), (198, 1500), (192, 1400), (198, 1330)]
    for side in ('R', 'L'):
        pts = leg_R if side == 'R' else mirror_pts(leg_R, 362)
        d = smooth_closed(pts)
        x0 = 200 if side == 'R' else 364
        hem = smooth_open([(x0 - 20, 1556), (x0 + 70, 1584), (x0 + 175, 1570)])
        folds = [smooth_open([(x0 + 40, 1360), (x0 + 55, 1440), (x0 + 50, 1530)]),
                 smooth_open([(x0 + 100, 1370), (x0 + 110, 1460), (x0 + 115, 1540)]),
                 smooth_open([(x0 + 140, 1400), (x0 + 145, 1480)])]
        add(f'dhoti_{side}', [dict(d=d, fill=P['dhoti'], stroke=P['dhoti_line'], sw=LINE, outer=True,
                                   shade=shade(P['dhoti_sh'], 14 if side == 'L' else -14, 8, 0.9, 12),
                                   extra=[dict(d=hem, stroke=P['dhoti_sh'], sw=22),
                                          dict(d=hem, stroke=P['dhoti_line'], sw=2.5, opacity=0.5)]
                                   + [dict(d=f, stroke=P['dhoti_sh'], sw=7, opacity=0.8, blur=2.5) for f in folds])],
            (288, 1310) if side == 'R' else (436, 1310), 8.6, backing=True, line_z=8.4)

    # front flap: pleated orange cloth from the buckle
    flap = [(312, 1212), (408, 1212), (428, 1290), (420, 1380), (404, 1440), (392, 1420), (380, 1478),
            (366, 1508), (350, 1470), (336, 1430), (322, 1452), (306, 1380), (294, 1290)]
    fl = smooth_closed(flap, 0.8)
    add('flap', [dict(d=fl, fill=P['sash'], stroke=P['sash_line'], sw=LINE_IN + 0.5,
                      shade=shade(P['sash_sh'], 12, 0, 0.88, 8),
                      light=dict(color=P['sash_hi'], dx=-14, dy=0, k=0.5, blur=8, opacity=0.5),
                      extra=[dict(d=smooth_open([(338, 1235), (334, 1350), (338, 1440)]), stroke=P['sash_sh'], sw=7, blur=1.5),
                             dict(d=smooth_open([(362, 1240), (364, 1360), (366, 1500)]), stroke=P['sash_sh'], sw=6, blur=1.5),
                             dict(d=smooth_open([(386, 1235), (392, 1350), (390, 1440)]), stroke=P['sash_sh'], sw=7, blur=1.5)])],
        (360, 1220), 11)
    add('buckle', [dict(d=smooth_closed(ellipse_pts(360, 1190, 36, 33, 24)), fill=P['gold'], stroke=P['gold_line'],
                        sw=3, shade=shade(P['gold_sh'], 5, 5, 0.85, 5), light=dict(color=P['gold_hi'], dx=-6, dy=-8, k=0.45, blur=4)),
                   dict(d=smooth_closed(ellipse_pts(360, 1190, 20, 18, 20)), fill='none', stroke=P['gold_sh'], sw=3)],
        (360, 1190), 11.5)

    # shins (with anklet) and feet (authored; toes unioned into the silhouette)
    for side, sx in (('R', 292), ('L', 440)):
        sgn = 1 if side == 'R' else -1
        sd = smooth_closed(capsule_pts((sx, 1560), (sx + 2 * sgn, 1700), 39, 36))
        ank = smooth_open([(sx - 48, 1668), (sx, 1680), (sx + 48, 1668)])
        add(f'shin_{side}', [skin_layer(sd, shade=dict(color=P['skin_sh'], dx=-10 * sgn, dy=0, kx=0.86, ky=1.0, blur=8),
                                        extra=gold_band(ank, 14))], (sx, 1580), 6.6, backing=True, line_z=6.0)
        fx = lambda x: sx + (x - 292) * sgn
        body = ellipse_pts(fx(266), 1728, 70, 38, 28)
        ankle = ellipse_pts(fx(294), 1696, 36, 26, 20)
        toes = [(fx(318), 1752, 17, 15), (fx(290), 1758, 13, 12), (fx(265), 1758, 12, 11),
                (fx(242), 1754, 11, 10), (fx(222), 1746, 10, 9)]
        polys = [body, ankle] + [ellipse_pts(x, y, rx, ry, 16) for x, y, rx, ry in toes]
        fdd = union_d(polys)
        lines = []
        for (x0, y0, rx0, _), (x1, y1, rx1, _) in zip(toes[:-1], toes[1:]):
            mx = (x0 + x1) / 2
            lines.append(dict(d=smooth_open([(mx, max(y0, y1) - 2), (mx + sgn * 1, max(y0, y1) + 10)]),
                              stroke=P['skin_line'], sw=2.2, opacity=0.8))
        add(f'foot_{side}', [skin_layer(fdd, shade=shade(P['skin_sh'], 0, -10, 0.92, 8))] + lines,
            (sx, 1700), 6.4, backing=True, line_z=6.0)

    PS.skeleton = dict(
        root=(360, 1765), hips=(360, 1230), chest=(360, 1150), neck=(360, 880), head=(360, 850), head_top=(360, 450),
        feather=(395, 275), lock_0=(250, 470), lock_1=(365, 440), lock_2=(470, 470),
        earring_R=(186, 742), earring_L=(538, 742),
        upperarm_R=(205, 982), forearm_R=(166, 1150), hand_R=(152, 1250), hand_R_tip=(150, 1380),
        upperarm_L=(515, 982), forearm_L=(554, 1150), hand_L=(568, 1250), hand_L_tip=(570, 1380),
        thigh_R=(288, 1310), shin_R=(292, 1560), foot_R=(294, 1690), foot_R_tip=(240, 1760),
        thigh_L=(436, 1310), shin_L=(440, 1560), foot_L=(438, 1690), foot_L_tip=(492, 1760),
        flap=(360, 1220))
    return PS.write(only) if write else PS


if __name__ == '__main__':
    build()
