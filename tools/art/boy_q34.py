"""Kanha — 3/4 FRONT view (facing screen-left) part builder.

Guide: build/guide/q34_classes.npy (reference crop x 745..925). The facing-right 3/4 view is
this set mirrored in Blender (scale.x = -1 on the view collection's root).
Near side = screen-right (character's left, suffix L); far side = screen-left (suffix R).
"""
import numpy as np
from .geom import *
from .common import load_classes, yy_xx
from .palette import KANHA as P
from . import face as F
from .hairtex import strands
from .hands import hand_layers, HANDS, HANDS_SIDE
from .style import LINE, LINE_IN, shade, gold_band, mirror_pts, hair_sheen, PartSet, bone_for, set_palette

VIEW = 'q34'
OUT = 'build/parts/boy/q34'
SVG_OUT = 'characters/boy/parts/q34'


def skin_layer(d, **kw):
    L = dict(d=d, fill=P['skin'], stroke=P['skin_line'], sw=LINE, outer=True, shade=shade(P['skin_sh'], 9, 7, 0.93, 8))
    L.update(kw)
    return L


def build(write=True, palette=None, out=None, svg_out=None, only=None):
    from .palette import KANHA
    set_palette(palette or KANHA)
    C = load_classes(VIEW)
    Y, X = yy_xx()
    PS = PartSet(out or OUT, svg_out or SVG_OUT)

    def add(name, layers, pivot, z, backing=False, line_z=None, **extra):
        PS.add(name, layers, pivot, z, backing, line_z, bone=bone_for(name), **extra)

    HS = dict(fill=P['hair'], stroke=P['hair_line'], sw=LINE * 0.8, shade=shade(P['hair_sh'], 10, 12, 0.92, 10))
    head_pivot = (330, 850)

    # ------------------------------------------------------------------ HEAD
    face_pts = [(330, 452), (262, 470), (214, 512), (184, 570), (168, 640), (164, 704), (170, 762), (190, 812),
                (230, 850), (282, 870), (330, 872), (384, 862), (434, 836), (470, 796), (490, 740), (496, 668),
                (488, 590), (462, 520), (410, 474)]
    face_d = smooth_closed(face_pts)
    face_m = poly_mask(union_pts([face_pts]))
    dome = poly_mask(ellipse_pts(330, 650, 162, 200, 48))
    fl = [dict(d=face_d, fill=P['skin'], stroke=P['skin_line'], sw=LINE,
               shade=[shade(P['skin_sh'], 10, 12, 0.92, 12, opacity=0.9)],
               light=dict(color=P['skin_hi'], dx=-40, dy=-40, k=0.55, blur=30, opacity=0.5))]
    fl += F.blush(212, 770, 24, 18, opacity=0.3)
    fl += F.blush(408, 772, 36, 20, opacity=0.3)
    fl += F.tilak(292, 548, 1.08, 0.86)
    add('head', fl, head_pivot, 20)

    ear_c = (500, 706)
    add('ear_L', [skin_layer(smooth_closed(ellipse_pts(*ear_c, 23, 36, 24, rot=0.15)), outer=False,
                             shade=shade(P['skin_sh'], 6, 4, 0.8, 6)),
                  dict(d=smooth_open([(496, 686), (507, 706), (499, 730)]), stroke=P['skin_line'], sw=LINE_IN, opacity=0.8)],
        (484, 710), 18)

    hair_m = C['hair'] & (Y < 880) & (Y > 225)
    hair_m = largest_components(morph(hair_m, 'open', 2))
    hair_all = fill_holes(morph(hair_m | (face_m & (Y < 700)), 'close', 6)) & ~(C['green'] & (Y < 290))
    hair_all = largest_components(hair_all)
    hb_d = mask_to_d(hair_all, step=4, sigma=1.1)
    sheen = hair_sheen(P, [(260, 360, 110, 55, -0.5, 0.45, 26), (450, 340, 90, 45, 0.5, 0.35, 24),
                           (130, 560, 40, 90, 0.2, 0.3, 20), (590, 560, 40, 90, -0.2, 0.3, 20)])
    hb = [dict(d=hb_d, extra=sheen, **HS)]
    tex = morph(hair_all, 'erode', 6)
    kw = dict(step=6, gravity=0.025, wave=0.09, wave_len=22, w=4.5, opacity=0.5, hi_every=3)
    crown = (380, 320)
    hb += strands(tex, crown, n=40, a0=-178, a1=-2, r0=40, lmax=520, seed=3, **kw)
    hb += strands(tex, crown, n=16, a0=150, a1=205, r0=120, lmax=400, seed=5, **kw)
    hb += strands(tex, crown, n=16, a0=-25, a1=30, r0=120, lmax=400, seed=6, **kw)
    add('hair_back', hb, head_pivot, 5)

    bang_zone = morph(dome, 'dilate', 18) & (Y < 610)
    bangs = morph(fill_holes((hair_m | (dome & ~face_m)) & bang_zone), 'open', 2)
    cuts = [(X < 270), (X >= 270) & (X < 400), (X >= 400)]
    lock_piv = [(220, 480), (330, 445), (440, 470)]
    for i, cm in enumerate(cuts):
        m = largest_components(bangs & morph(cm, 'dilate', 8 if i == 1 else 0))
        if m.sum() < 300:
            continue
        d = mask_to_d(m, step=4, sigma=1.1)
        t = strands(morph(m, 'erode', 4), crown, n=12, a0=-170, a1=-10, r0=60, step=6, lmax=300, gravity=0.04,
                    seed=10 + i, wave=0.09, wave_len=22, w=5, opacity=0.45)
        add(f'hair_lock_{i}', [dict(d=d, **HS)] + t, lock_piv[i], 32 + (1 if i == 1 else 0))

    feather_m = (C['green'] | C['gold'] | C['dhoti'] | C['sash'] | (C['hair'] & (Y < 250))) & (Y < 290) & (X > 380)
    feather_m = largest_components(fill_holes(morph(feather_m, 'close', 5)))
    fd = mask_to_d(feather_m, step=4, sigma=1.2)
    ys, xs = np.where(feather_m)
    fcx, fcy = xs.mean() + 8, ys.min() + (ys.max() - ys.min()) * 0.45
    feather_layers = [dict(d=fd, fill=P['feather_g'], stroke=P['feather_line'], sw=LINE_IN,
                           shade=shade(P['feather_g3'], 8, 8, 0.9, 8),
                           light=dict(color=P['feather_g2'], dx=-12, dy=-14, k=0.7, blur=10, opacity=0.9))]
    for a in np.linspace(-0.9, 0.9, 11):
        feather_layers.append(dict(d=smooth_open([(438, 275), (fcx + 30 * a, fcy + 10), (fcx + 90 * a, ys.min() + 20)]),
                                   stroke=P['feather_g3'], sw=2.2, opacity=0.55, clip=fd))
    for rx, ry, col in ((44, 58, 'feather_y'), (32, 43, 'feather_teal'), (23, 30, 'feather_blue'), (13, 17, 'feather_dark')):
        feather_layers.append(dict(d=smooth_closed(ellipse_pts(fcx, fcy, rx, ry, 28, rot=0.25)), fill=P[col],
                                   stroke=P['gold_line'] if col == 'feather_y' else None, sw=2))
    add('feather', feather_layers, (438, 275), 4)

    # ------------------------------------------------------------- FACE FEATURES
    eyes = {'R': (226, 680, -1, 0.74), 'L': (392, 680, 1, 1.0)}
    for side, (cx, cy, flip, sx) in eyes.items():
        add(f'eye_{side}_white', F.eye_white(cx, cy, 1.0, sx, flip), (cx, cy), 21, eye_white_of=f'eye_{side}')
        for st in F.EYE_STATES:
            add(f'eye_{side}_{st}', F.eye_over(cx, cy, 1.0, sx, flip, st), (cx, cy), 23, swap=f'eye_{side}', state=st)
        px = cx - 8 * sx
        add(f'pupil_{side}', F.pupil(px, cy + 4, 1.0, sx * 0.95), (px, cy + 4), 22, clip_to=f'eye_{side}_white')
        add(f'brow_{side}', F.brow(cx - 6 * flip * sx, 584, 1.05, sx, flip), (cx, 584), 25)
    nose_l = [dict(d=smooth_closed(ellipse_pts(268, 738, 20, 13, 18)), fill=P['skin_sh2'], opacity=0.7, blur=4),
              dict(d=smooth_open([(282, 700), (262, 728), (254, 742), (266, 750), (284, 746)]), stroke=P['skin_line'],
                   sw=3, opacity=0.9),
              dict(d=smooth_closed(ellipse_pts(268, 732, 8, 6, 12)), fill=P['skin_hi'], opacity=0.7, blur=2)]
    add('nose', nose_l, (270, 735), 24)
    for mname in F.MOUTHS:
        add(f'mouth_{mname}', F.mouth(mname, 284, 792, 1.2, 0.84), (284, 792), 26, swap='mouth', state=mname)

    # earrings: near (in front of the ear, sways) and far (behind the face)
    for side, (ex, ey), z in (('L', (506, 740), 27), ('R', (180, 752), 17)):
        bead = smooth_closed(ellipse_pts(ex, ey + 12, 8, 9, 14))
        bell = [(ex, ey + 20), (ex + 9, ey + 30), (ex + 15, ey + 50), (ex + 12, ey + 64), (ex, ey + 70),
                (ex - 12, ey + 64), (ex - 15, ey + 50), (ex - 9, ey + 30)]
        g = dict(fill=P['gold'], stroke=P['gold_line'], sw=2.2, shade=shade(P['gold_sh'], 4, 5, 0.85, 4),
                 light=dict(color=P['gold_hi'], dx=-4, dy=-6, k=0.4, blur=3))
        add(f'earring_{side}', [dict(d=bead, **g), dict(d=smooth_closed(bell), **g),
                                dict(d=smooth_closed(ellipse_pts(ex, ey + 72, 4, 4, 10)), **g)], (ex, ey), z)

    # --------------------------------------------------------------------- BODY
    neck = [(290, 790), (392, 790), (400, 895), (340, 905), (282, 895)]
    nd = smooth_closed(neck)
    add('neck', [dict(d=nd, fill=P['skin'])], (340, 900), 7.9)

    torso = [(300, 866), (250, 876), (218, 896), (202, 932), (196, 990), (202, 1060), (206, 1140), (208, 1290),
             (330, 1310), (488, 1290), (490, 1150), (498, 1060), (504, 990), (494, 930), (462, 896), (410, 874)]
    td = smooth_closed(torso)
    tl = [dict(d=td, fill=P['skin'], stroke=P['skin_line'], sw=LINE, shade=[shade(P['skin_sh'], 10, -10, 0.9, 12)])]
    tl.append(dict(d=smooth_closed(ellipse_pts(330, 884, 100, 26, 20)), fill=P['skin_sh2'], opacity=0.7, blur=9, clip=td))
    tl.append(dict(d=smooth_closed(ellipse_pts(250, 1080, 60, 22, 20)), fill=P['skin_sh'], opacity=0.5, blur=10, clip=td))
    tl.append(dict(d=smooth_closed(ellipse_pts(390, 1085, 90, 26, 20)), fill=P['skin_sh'], opacity=0.5, blur=10, clip=td))
    tl.append(dict(d=smooth_open([(220, 1060), (260, 1070), (300, 1058)]), stroke=P['skin_line'], sw=LINE_IN, opacity=0.4))
    tl.append(dict(d=smooth_open([(330, 1062), (400, 1072), (470, 1052)]), stroke=P['skin_line'], sw=LINE_IN, opacity=0.4))
    tl.append(dict(d=smooth_closed(ellipse_pts(282, 1135, 8, 6, 12)), fill=P['skin_line'], opacity=0.6))
    tl.append(dict(d=smooth_open([(470, 990), (440, 1020), (430, 1050)]), stroke=P['skin_line'], sw=LINE_IN, opacity=0.6))
    add('torso', tl, (340, 1250), 8)

    nl = []
    short = [(232, 882), (250, 920), (285, 948), (330, 935), (385, 900), (410, 878)]
    long_ = [(246, 892), (250, 960), (262, 1040), (272, 1068), (300, 1020), (350, 950), (400, 892)]
    for c in (short, long_):
        nl += [dict(d=smooth_open(c), stroke=P['gold_line'], sw=12), dict(d=smooth_open(c), stroke=P['gold'], sw=8),
               dict(d=smooth_open(c), stroke=P['gold_hi'], sw=2.5, opacity=0.7)]
    nl.append(dict(d=smooth_closed(ellipse_pts(286, 962, 21, 25, 20)), fill=P['gold'], stroke=P['gold_line'], sw=2.5,
                   shade=shade(P['gold_sh'], 4, 4, 0.8, 4)))
    nl.append(dict(d=smooth_closed(ellipse_pts(286, 962, 10, 13, 16)), fill=P['sash'], stroke=P['sash_line'], sw=1.5))
    nl.append(dict(d=smooth_closed(ellipse_pts(273, 1080, 12, 19, 16)), fill=P['gem'], stroke=P['gold_line'], sw=3,
                   light=dict(color=P['gem_hi'], dx=-3, dy=-6, k=0.4, blur=3)))
    add('necklace', nl, (330, 885), 12)

    # arms: far (R, screen-left) behind torso; near (L, screen-right) in front
    arm_spec = {'R': dict(sh=(214, 975), el=(170, 1140), wr=(164, 1250), flip=-1, z=7.4, lz=7.2),
                'L': dict(sh=(478, 975), el=(500, 1140), wr=(504, 1250), flip=1, z=14, lz=13.8)}
    for side, a in arm_spec.items():
        sc = 0.95 if side == 'R' else 1.0
        upd = smooth_closed(capsule_pts(a['sh'], a['el'], 42 * sc, 38 * sc))
        bx = a['sh'][0]
        band = smooth_open([(bx - 70, 1016), (bx, 1034), (bx + 70, 1018)])
        lsh = dict(color=P['skin_sh'], dx=-10 * a['flip'], dy=0, kx=0.86, ky=1.0, blur=8)
        add(f'upperarm_{side}', [skin_layer(upd, shade=lsh, extra=gold_band(P, band, 20))], a['sh'], a['z'],
            backing=True, line_z=a['lz'])
        fo = smooth_closed(capsule_pts(a['el'], a['wr'], 37 * sc, 30 * sc))
        wb = smooth_open([(a['wr'][0] - 50, a['wr'][1] - 14), (a['wr'][0], a['wr'][1] - 8), (a['wr'][0] + 50, a['wr'][1] - 14)])
        add(f'forearm_{side}', [skin_layer(fo, shade=lsh, extra=gold_band(P, wb, 12))], a['el'], a['z'] + 0.1,
            backing=True, line_z=a['lz'])
        for hname in HANDS + HANDS_SIDE:
            add(f'hand_{side}_{hname}', hand_layers(hname, a['wr'][0], a['wr'][1] - 4, 1.1 * sc, a['flip'], 0.0),
                a['wr'], a['z'] + 0.2, swap=f'hand_{side}', state=hname, backing=True, line_z=a['lz'])

    # hips + sash
    hips_pts = [(200, 1155), (265, 1185), (330, 1172), (420, 1152), (496, 1140), (505, 1250), (505, 1350),
                (350, 1372), (196, 1355), (194, 1250)]
    sash_pts = [(198, 1146), (232, 1160), (265, 1180), (300, 1176), (360, 1160), (430, 1144), (500, 1134),
                (508, 1200), (504, 1262), (450, 1255), (380, 1246), (300, 1244), (250, 1258), (200, 1290), (194, 1215)]
    hl = [dict(d=smooth_closed(hips_pts), fill=P['dhoti'], stroke=P['dhoti_line'], sw=LINE, outer=True,
               shade=shade(P['dhoti_sh'], 0, -14, 0.9, 10)),
          dict(d=smooth_closed(sash_pts), fill=P['sash'], stroke=P['sash_line'], sw=LINE_IN,
               shade=shade(P['sash_sh'], 0, -12, 0.9, 8),
               light=dict(color=P['sash_hi'], dx=0, dy=-26, k=0.8, blur=10, opacity=0.35))]
    for c in ([(215, 1196), (245, 1212), (262, 1232)], [(490, 1190), (400, 1206), (310, 1230)],
              [(470, 1156), (400, 1170), (320, 1190)], [(500, 1232), (440, 1238)]):
        hl += [dict(d=smooth_open(c), stroke=P['sash_sh'], sw=7, opacity=0.9, blur=1.5),
               dict(d=smooth_open(c), stroke=P['sash_line'], sw=2, opacity=0.6)]
    add('hips', hl, (340, 1200), 9, backing=True, line_z=8.4)

    legs = {'R': [(198, 1300), (300, 1300), (318, 1420), (312, 1530), (300, 1572), (258, 1584), (220, 1572),
                  (200, 1500), (194, 1400)],
            'L': [(290, 1300), (500, 1300), (506, 1400), (500, 1490), (484, 1548), (440, 1566), (380, 1562),
                  (340, 1545), (316, 1480), (300, 1400)]}
    for side, pts in legs.items():
        d = smooth_closed(pts)
        xs_ = [p[0] for p in pts]
        x0, x1 = min(xs_), max(xs_)
        yb = max(p[1] for p in pts)
        hem = smooth_open([(x0 - 10, yb - 30), ((x0 + x1) / 2, yb - 8), (x1 + 10, yb - 24)])
        folds = [smooth_open([(x0 + (x1 - x0) * f, 1360), (x0 + (x1 - x0) * f + 8, 1450), (x0 + (x1 - x0) * f + 4, yb - 40)])
                 for f in (0.3, 0.6, 0.85)]
        add(f'dhoti_{side}', [dict(d=d, fill=P['dhoti'], stroke=P['dhoti_line'], sw=LINE, outer=True,
                                   shade=shade(P['dhoti_sh'], 14 if side == 'L' else -14, 8, 0.9, 12),
                                   extra=[dict(d=hem, stroke=P['dhoti_sh'], sw=22),
                                          dict(d=hem, stroke=P['dhoti_line'], sw=2.5, opacity=0.5)]
                                   + [dict(d=f, stroke=P['dhoti_sh'], sw=7, opacity=0.8, blur=2.5) for f in folds])],
            (255, 1310) if side == 'R' else (400, 1310), 8.6 if side == 'L' else 8.5, backing=True, line_z=8.4)

    flap = [(226, 1212), (304, 1212), (318, 1300), (308, 1390), (296, 1440), (286, 1420), (276, 1478),
            (262, 1506), (250, 1470), (240, 1430), (230, 1450), (216, 1380), (210, 1300)]
    fl_d = smooth_closed(flap, 0.8)
    add('flap', [dict(d=fl_d, fill=P['sash'], stroke=P['sash_line'], sw=LINE_IN + 0.5,
                      shade=shade(P['sash_sh'], 12, 0, 0.88, 8),
                      light=dict(color=P['sash_hi'], dx=-14, dy=0, k=0.5, blur=8, opacity=0.5),
                      extra=[dict(d=smooth_open([(248, 1235), (242, 1350), (246, 1440)]), stroke=P['sash_sh'], sw=7, blur=1.5),
                             dict(d=smooth_open([(268, 1240), (268, 1360), (264, 1500)]), stroke=P['sash_sh'], sw=6, blur=1.5),
                             dict(d=smooth_open([(288, 1235), (294, 1350), (290, 1430)]), stroke=P['sash_sh'], sw=7, blur=1.5)])],
        (265, 1220), 11)
    add('buckle', [dict(d=smooth_closed(ellipse_pts(265, 1192, 30, 32, 24)), fill=P['gold'], stroke=P['gold_line'],
                        sw=3, shade=shade(P['gold_sh'], 5, 5, 0.85, 5), light=dict(color=P['gold_hi'], dx=-6, dy=-8, k=0.45, blur=4)),
                   dict(d=smooth_closed(ellipse_pts(265, 1192, 16, 18, 20)), fill='none', stroke=P['gold_sh'], sw=3)],
        (265, 1192), 11.5)

    # shins + feet (far R, near L). Feet point screen-left (3/4).
    for side, sx, top, z in (('R', 286, 1550, 6.0), ('L', 420, 1540, 6.6)):
        sd = smooth_closed(capsule_pts((sx, top), (sx, 1675), 36 if side == 'R' else 40, 34 if side == 'R' else 37))
        ank = smooth_open([(sx - 48, 1648), (sx, 1660), (sx + 48, 1648)])
        add(f'shin_{side}', [skin_layer(sd, shade=dict(color=P['skin_sh'], dx=10, dy=0, kx=0.86, ky=1.0, blur=8),
                                        extra=gold_band(P, ank, 14))], (sx, top + 20), z, backing=True, line_z=z - 0.5)
        if side == 'R':
            body = ellipse_pts(258, 1724, 72, 36, 28)
            ankle = ellipse_pts(286, 1690, 34, 26, 20)
            toes = [(196, 1742, 14, 13), (212, 1756, 12, 11), (232, 1762, 11, 10), (254, 1764, 10, 9), (276, 1762, 9, 8)]
        else:
            body = ellipse_pts(414, 1722, 52, 40, 28)
            ankle = ellipse_pts(420, 1688, 36, 26, 20)
            toes = [(378, 1748, 15, 14), (398, 1760, 12, 11), (420, 1764, 11, 10), (440, 1762, 10, 9), (458, 1754, 9, 8)]
        fdd = union_d([body, ankle] + [ellipse_pts(x, y, rx, ry, 16) for x, y, rx, ry in toes])
        lines = [dict(d=smooth_open([((a[0] + b[0]) / 2, max(a[1], b[1]) - 2), ((a[0] + b[0]) / 2, max(a[1], b[1]) + 9)]),
                      stroke=P['skin_line'], sw=2.2, opacity=0.8) for a, b in zip(toes[:-1], toes[1:])]
        add(f'foot_{side}', [skin_layer(fdd, shade=shade(P['skin_sh'], 0, -10, 0.92, 8))] + lines,
            (sx, 1690), z - 0.2, backing=True, line_z=z - 0.5)

    PS.skeleton = dict(
        root=(340, 1765), hips=(340, 1230), chest=(340, 1150), neck=(330, 880), head=(330, 850), head_top=(330, 450),
        feather=(438, 275), lock_0=lock_piv[0], lock_1=lock_piv[1], lock_2=lock_piv[2],
        earring_L=(506, 740), earring_R=(180, 752),
        upperarm_R=(214, 975), forearm_R=(170, 1140), hand_R=(164, 1250), hand_R_tip=(160, 1380),
        upperarm_L=(478, 975), forearm_L=(500, 1140), hand_L=(504, 1250), hand_L_tip=(506, 1380),
        thigh_R=(255, 1310), shin_R=(286, 1560), foot_R=(286, 1680), foot_R_tip=(200, 1755),
        thigh_L=(400, 1310), shin_L=(420, 1560), foot_L=(420, 1680), foot_L_tip=(380, 1755),
        flap=(265, 1220))
    return PS.write(only) if write else PS


if __name__ == '__main__':
    build()
