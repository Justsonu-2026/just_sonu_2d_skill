"""Kanha — SIDE view (facing screen-left) part builder.

Guide: build/guide/side_classes.npy (reference crop x 923..1103).
Facing left, the near side is the character's LEFT (suffix L), the far side RIGHT (suffix R).
Far limbs use a slightly darker palette so they read behind. Each leg is split at the knee:
the thigh is the upper dhoti, the shin part carries the lower dhoti + skin shin + anklet,
so knees can bend for walking and kneeling.
"""
import numpy as np
from .geom import *
from .common import load_classes, yy_xx
from .palette import KANHA as P, far_side
from . import face as F
from .hairtex import strands
from .hands import hand_layers, HANDS, HANDS_SIDE
from .style import LINE, LINE_IN, shade, gold_band, hair_sheen, PartSet, bone_for, set_palette

VIEW = 'side'
OUT = 'build/parts/boy/side'
SVG_OUT = 'characters/boy/parts/side'


def build(write=True, palette=None, out=None, svg_out=None, only=None):
    from .palette import KANHA
    pal = palette or KANHA
    set_palette(pal)
    PF = far_side(pal)
    C = load_classes(VIEW)
    Y, X = yy_xx()
    PS = PartSet(out or OUT, svg_out or SVG_OUT)

    def add(name, layers, pivot, z, backing=False, line_z=None, **extra):
        PS.add(name, layers, pivot, z, backing, line_z, bone=bone_for(name), **extra)

    def skin_layer(d, pal_=None, **kw):
        q = pal_ or P
        L = dict(d=d, fill=q['skin'], stroke=q['skin_line'], sw=LINE, outer=True, shade=shade(q['skin_sh'], 9, 7, 0.93, 8))
        L.update(kw)
        return L

    HS = dict(fill=P['hair'], stroke=P['hair_line'], sw=LINE * 0.8, shade=shade(P['hair_sh'], 10, 12, 0.92, 10))
    head_pivot = (290, 846)

    # ------------------------------------------------------------------ HEAD
    face_pts = [(250, 455), (196, 470), (162, 510), (150, 560), (152, 605), (150, 640), (142, 680), (128, 704),
                (124, 716), (134, 728), (142, 740), (138, 754), (146, 766), (142, 780), (150, 798), (170, 818),
                (206, 836), (250, 848), (300, 848), (350, 830), (380, 760), (386, 680), (372, 560), (332, 480)]
    face_d = smooth_closed(face_pts, 0.9)
    face_m = poly_mask(union_pts([face_pts]))
    fl = [dict(d=face_d, fill=P['skin'], stroke=P['skin_line'], sw=LINE,
               shade=[shade(P['skin_sh'], 16, 10, 0.92, 12, opacity=0.9)],
               light=dict(color=P['skin_hi'], dx=-40, dy=-30, k=0.55, blur=30, opacity=0.5))]
    fl += F.blush(212, 770, 30, 18, opacity=0.3)
    fl += [dict(d=d['d'], fill=d['fill'], stroke=d.get('stroke'), sw=d.get('sw', 2)) for d in F.tilak(170, 548, 1.05, 0.4)]
    fl.append(dict(d=smooth_open([(150, 720), (144, 728), (152, 732)]), stroke=P['skin_line'], sw=2.6, opacity=0.8))
    fl.append(dict(d=smooth_open([(214, 820), (240, 836), (270, 842)]), stroke=P['skin_line'], sw=2.4, opacity=0.35))
    add('head', fl, head_pivot, 20)

    add('ear_L', [skin_layer(smooth_closed(ellipse_pts(346, 722, 24, 36, 24, rot=0.1)), outer=False,
                             shade=shade(P['skin_sh'], 6, 4, 0.8, 6)),
                  dict(d=smooth_open([(340, 700), (352, 720), (343, 744)]), stroke=P['skin_line'], sw=LINE_IN, opacity=0.8)],
        (340, 724), 21)

    bun_c, bun_r = (392, 300), 72
    hair_m = C['hair'] & (Y < 890) & (Y > 225)
    hair_m = largest_components(morph(hair_m, 'open', 2))
    bun_m = poly_mask(ellipse_pts(bun_c[0], bun_c[1], bun_r, bun_r - 6, 40))
    hair_all = fill_holes(morph(hair_m | (face_m & (Y < 700)), 'close', 6)) & ~(C['green'] & (Y < 290))
    hair_all = largest_components(hair_all) & ~(bun_m & (Y < 330))
    hb_d = mask_to_d(hair_all, step=4, sigma=1.1)
    sheen = hair_sheen(P, [(300, 400, 120, 50, -0.3, 0.45, 26), (480, 520, 60, 110, 0.2, 0.35, 24),
                           (430, 760, 60, 50, 0.2, 0.3, 20)])
    hb = [dict(d=hb_d, extra=sheen, **HS)]
    tex = morph(hair_all, 'erode', 6)
    kw = dict(step=6, gravity=0.03, wave=0.09, wave_len=22, w=4.5, opacity=0.5, hi_every=3)
    hb += strands(tex, (380, 360), n=46, a0=-200, a1=60, r0=30, lmax=560, seed=3, **kw)
    add('hair_back', hb, head_pivot, 19.5)

    bun_l = [dict(d=smooth_closed(ellipse_pts(bun_c[0], bun_c[1], bun_r, bun_r - 6, 32)), **HS)]
    bun_l += strands(poly_mask(ellipse_pts(bun_c[0], bun_c[1], bun_r - 8, bun_r - 14, 32)), bun_c, n=16,
                     a0=-180, a1=180, r0=8, step=5, lmax=70, gravity=0.0, seed=21, wave=0.05, w=4, opacity=0.5)
    beads = []
    for t in np.linspace(0, 1, 14):
        a = np.radians(150 - 120 * t)
        x = bun_c[0] + (bun_r + 2) * np.cos(a) * 1.0 + 0
        y = bun_c[1] + 26 + (bun_r - 30) * np.sin(a) * 0.55 + 30 * t
        beads.append(dict(d=smooth_closed(ellipse_pts(x, y, 9, 9, 12)), fill=P['gold'], stroke=P['gold_line'], sw=1.6,
                          light=dict(color=P['gold_hi'], dx=-2, dy=-3, k=0.4, blur=2)))
    add('bun', bun_l + beads, bun_c, 19.7)

    bang_m = (hair_m & (X < 260) & (Y > 420) & (Y < 600)) | poly_mask([(110, 460), (250, 430), (262, 470), (180, 520), (120, 520)])
    bang_m = largest_components(morph(fill_holes(bang_m), 'open', 2))
    add('hair_lock_0', [dict(d=mask_to_d(bang_m, step=4, sigma=1.1), **HS)] +
        strands(morph(bang_m, 'erode', 3), (260, 420), n=8, a0=120, a1=200, r0=10, step=5, lmax=200, gravity=0.04,
                seed=31, wave=0.08, w=4, opacity=0.45), (240, 450), 32)

    feather_m = (C['green'] | C['gold'] | C['dhoti'] | C['sash'] | (C['hair'] & (Y < 230))) & (Y < 255) & (X > 380)
    feather_m = largest_components(fill_holes(morph(feather_m, 'close', 5)))
    fd = mask_to_d(feather_m, step=4, sigma=1.2)
    ys, xs = np.where(feather_m)
    fcx, fcy = xs.mean(), ys.min() + (ys.max() - ys.min()) * 0.42
    feather_layers = [dict(d=fd, fill=P['feather_g'], stroke=P['feather_line'], sw=LINE_IN,
                           shade=shade(P['feather_g3'], 8, 8, 0.9, 8),
                           light=dict(color=P['feather_g2'], dx=-12, dy=-14, k=0.7, blur=10, opacity=0.9))]
    for rx, ry, col in ((30, 52, 'feather_y'), (22, 39, 'feather_teal'), (16, 28, 'feather_blue'), (9, 16, 'feather_dark')):
        feather_layers.append(dict(d=smooth_closed(ellipse_pts(fcx, fcy, rx, ry, 28, rot=0.1)), fill=P[col],
                                   stroke=P['gold_line'] if col == 'feather_y' else None, sw=2))
    add('feather', feather_layers, (440, 245), 19.4)

    # face features (profile)
    ex, ey = 204, 668
    add('eye_L_white', F.eye_white(ex, ey, 1.0, 0.5, 1), (ex, ey), 21.2, eye_white_of='eye_L')
    for st in F.EYE_STATES:
        add(f'eye_L_{st}', F.eye_over(ex, ey, 1.0, 0.5, 1, st), (ex, ey), 23, swap='eye_L', state=st)
    add('pupil_L', F.pupil(ex - 10, ey + 4, 1.0, 0.5), (ex - 10, ey + 4), 22, clip_to='eye_L_white')
    add('brow_L', F.brow(212, 592, 1.0, 0.55, 1), (212, 592), 25)
    for mname in F.MOUTHS:
        L = F.mouth(mname, 160, 768, 1.15, 0.5)
        L = [dict(l, clip=face_d) for l in L]
        add(f'mouth_{mname}', L, (160, 768), 26, swap='mouth', state=mname)
    bead = smooth_closed(ellipse_pts(350, 764, 8, 9, 14))
    ex2, ey2 = 350, 752
    bell = [(ex2, ey2 + 20), (ex2 + 9, ey2 + 30), (ex2 + 15, ey2 + 50), (ex2 + 12, ey2 + 64), (ex2, ey2 + 70),
            (ex2 - 12, ey2 + 64), (ex2 - 15, ey2 + 50), (ex2 - 9, ey2 + 30)]
    g = dict(fill=P['gold'], stroke=P['gold_line'], sw=2.2, shade=shade(P['gold_sh'], 4, 5, 0.85, 4),
             light=dict(color=P['gold_hi'], dx=-4, dy=-6, k=0.4, blur=3))
    add('earring_L', [dict(d=bead, **g), dict(d=smooth_closed(bell), **g)], (ex2, ey2), 27)

    # --------------------------------------------------------------------- BODY
    add('neck', [dict(d=smooth_closed([(232, 790), (330, 790), (338, 900), (240, 900)]), fill=P['skin'])], (290, 890), 7.9)
    torso = [(252, 866), (216, 888), (200, 940), (196, 1000), (190, 1060), (184, 1120), (194, 1170), (210, 1290),
             (320, 1310), (402, 1290), (406, 1180), (402, 1080), (398, 980), (388, 920), (352, 880), (300, 866)]
    td = smooth_closed(torso)
    tl = [dict(d=td, fill=P['skin'], stroke=P['skin_line'], sw=LINE, shade=[shade(P['skin_sh'], 12, -6, 0.9, 12)])]
    tl.append(dict(d=smooth_closed(ellipse_pts(290, 880, 80, 24, 20)), fill=P['skin_sh2'], opacity=0.7, blur=9, clip=td))
    tl.append(dict(d=smooth_open([(204, 1040), (232, 1062), (270, 1060)]), stroke=P['skin_line'], sw=LINE_IN, opacity=0.4))
    add('torso', tl, (300, 1250), 8)
    nl = []
    for c in ([(250, 878), (230, 920), (212, 950)], [(268, 884), (240, 960), (214, 1040), (202, 1066)]):
        nl += [dict(d=smooth_open(c), stroke=P['gold_line'], sw=12), dict(d=smooth_open(c), stroke=P['gold'], sw=8),
               dict(d=smooth_open(c), stroke=P['gold_hi'], sw=2.5, opacity=0.7)]
    nl.append(dict(d=smooth_closed(ellipse_pts(208, 956, 9, 20, 16)), fill=P['gold'], stroke=P['gold_line'], sw=2.4))
    nl.append(dict(d=smooth_closed(ellipse_pts(200, 1074, 7, 17, 14)), fill=P['gem'], stroke=P['gold_line'], sw=2.4))
    add('necklace', nl, (250, 885), 12)

    # arms: near (L) in front, far (R) behind torso with darker palette
    for side, dx, z, lz, q in (('L', 0, 14, 13.8, P), ('R', 14, 7.3, 7.1, PF)):
        sh, el, wr = (300 + dx, 952), (298 + dx, 1140), (290 + dx, 1268)
        upd = smooth_closed(capsule_pts(sh, el, 44, 39))
        band = smooth_open([(sh[0] - 70, 1016), (sh[0], 1028), (sh[0] + 70, 1016)])
        lsh = dict(color=q['skin_sh'], dx=12, dy=0, kx=0.86, ky=1.0, blur=8)
        add(f'upperarm_{side}', [skin_layer(upd, q, shade=lsh, extra=gold_band(q, band, 20))], sh, z, backing=True, line_z=lz)
        fo = smooth_closed(capsule_pts(el, wr, 37, 30))
        wb = smooth_open([(wr[0] - 50, wr[1] - 14), (wr[0], wr[1] - 8), (wr[0] + 50, wr[1] - 14)])
        add(f'forearm_{side}', [skin_layer(fo, q, shade=lsh, extra=gold_band(q, wb, 12))], el, z + 0.1, backing=True, line_z=lz)
        sk = dict(fill=q['skin'], sh=q['skin_sh'], line=q['hand_line'])
        for hname in HANDS + HANDS_SIDE:
            add(f'hand_{side}_{hname}', hand_layers(hname, wr[0], wr[1] - 4, 1.1, 1, 0.0, skin=sk),
                wr, z + 0.2, swap=f'hand_{side}', state=hname, backing=True, line_z=lz)

    # hips (sash + dhoti top) and the front drape seen from the side
    hips_pts = [(194, 1160), (260, 1160), (330, 1150), (404, 1150), (412, 1250), (410, 1335), (300, 1350),
                (196, 1335), (186, 1250)]
    sash_pts = [(190, 1150), (300, 1146), (404, 1142), (414, 1220), (408, 1330), (340, 1324), (260, 1304), (192, 1286)]
    hl = [dict(d=smooth_closed(hips_pts), fill=P['dhoti'], stroke=P['dhoti_line'], sw=LINE, outer=True,
               shade=shade(P['dhoti_sh'], 12, -12, 0.9, 10)),
          dict(d=smooth_closed(sash_pts), fill=P['sash'], stroke=P['sash_line'], sw=LINE_IN,
               shade=shade(P['sash_sh'], 12, -10, 0.9, 8),
               light=dict(color=P['sash_hi'], dx=-10, dy=-26, k=0.8, blur=10, opacity=0.35))]
    for c in ([(220, 1190), (300, 1200), (390, 1196)], [(214, 1240), (300, 1262), (396, 1270)]):
        hl += [dict(d=smooth_open(c), stroke=P['sash_sh'], sw=7, opacity=0.9, blur=1.5),
               dict(d=smooth_open(c), stroke=P['sash_line'], sw=2, opacity=0.6)]
    add('hips', hl, (300, 1230), 9, backing=True, line_z=8.4)
    flap = [(204, 1168), (232, 1196), (226, 1290), (206, 1400), (176, 1480), (150, 1500), (132, 1480), (130, 1400),
            (150, 1300), (176, 1210)]
    add('flap', [dict(d=smooth_closed(flap), fill=P['sash'], stroke=P['sash_line'], sw=LINE_IN + 0.5,
                      shade=shade(P['sash_sh'], 12, 0, 0.88, 8),
                      extra=[dict(d=smooth_open([(200, 1210), (180, 1330), (150, 1470)]), stroke=P['sash_sh'], sw=6, blur=1.5)])],
        (200, 1180), 11)
    add('buckle', [dict(d=smooth_closed(ellipse_pts(198, 1182, 12, 28, 20)), fill=P['gold'], stroke=P['gold_line'], sw=3,
                        shade=shade(P['gold_sh'], 3, 5, 0.8, 4))], (198, 1182), 11.5)

    # legs: thigh (upper dhoti) | shin part (lower dhoti + skin + anklet) | foot
    hip, knee, ank = (300, 1330), (312, 1470), (345, 1672)
    for side, dx, zb, q in (('L', 0, 9.2, P), ('R', 16, 6.2, PF)):
        hx, kx_, ax = (hip[0] + dx, hip[1]), (knee[0] + dx, knee[1]), (ank[0] + dx, ank[1])
        th = smooth_closed(capsule_pts(hx, kx_, 98, 96))
        add(f'dhoti_{side}', [dict(d=th, fill=q['dhoti'], stroke=q['dhoti_line'], sw=LINE, outer=True,
                                   shade=shade(q['dhoti_sh'], 14, 0, 0.9, 12),
                                   extra=[dict(d=smooth_open([(hx[0] - 50, 1360), (hx[0] - 40, 1440)]), stroke=q['dhoti_sh'],
                                               sw=7, opacity=0.8, blur=2.5),
                                          dict(d=smooth_open([(hx[0] + 40, 1370), (hx[0] + 50, 1450)]), stroke=q['dhoti_sh'],
                                               sw=7, opacity=0.8, blur=2.5)])],
            hx, zb + 0.2, backing=True, line_z=zb - 0.6)
        cloth = smooth_closed(capsule_pts(kx_, (kx_[0] + 14, 1540), 96, 66))
        shin = smooth_closed(capsule_pts((kx_[0] + 18, 1520), ax, 42, 36))
        hem = smooth_open([(kx_[0] - 70, 1548), (kx_[0] + 10, 1572), (kx_[0] + 90, 1556)])
        ankb = smooth_open([(ax[0] - 50, 1650), (ax[0], 1660), (ax[0] + 50, 1650)])
        add(f'shin_{side}', [skin_layer(shin, q, shade=dict(color=q['skin_sh'], dx=12, dy=0, kx=0.86, ky=1, blur=8),
                                        extra=gold_band(q, ankb, 14)),
                             dict(d=cloth, fill=q['dhoti'], stroke=q['dhoti_line'], sw=LINE, outer=True,
                                  shade=shade(q['dhoti_sh'], 14, 8, 0.9, 12),
                                  extra=[dict(d=hem, stroke=q['dhoti_sh'], sw=24),
                                         dict(d=hem, stroke=q['dhoti_line'], sw=2.5, opacity=0.5)])],
            kx_, zb + 0.1, backing=True, line_z=zb - 0.6)
        fp = [(320 + dx, 1666), (372 + dx, 1678), (394 + dx, 1718), (390 + dx, 1756), (360 + dx, 1768), (250 + dx, 1768),
              (152 + dx, 1766), (122 + dx, 1756), (120 + dx, 1738), (152 + dx, 1722), (222 + dx, 1706), (290 + dx, 1684)]
        toes = [dict(d=smooth_open([(150 + dx + i * 16, 1752), (154 + dx + i * 16, 1766)]), stroke=q['skin_line'], sw=2.2,
                     opacity=0.7) for i in range(4)]
        add(f'foot_{side}', [skin_layer(smooth_closed(fp), q, shade=shade(q['skin_sh'], 0, -10, 0.92, 8))] + toes,
            ax, zb, backing=True, line_z=zb - 0.6)

    PS.skeleton = dict(
        root=(300, 1765), hips=(300, 1240), chest=(300, 1150), neck=(290, 880), head=head_pivot, head_top=(290, 450),
        feather=(440, 245), lock_0=(240, 450), earring_L=(350, 752),
        upperarm_L=(300, 952), forearm_L=(298, 1140), hand_L=(290, 1268), hand_L_tip=(286, 1395),
        upperarm_R=(314, 952), forearm_R=(312, 1140), hand_R=(304, 1268), hand_R_tip=(300, 1395),
        thigh_L=hip, shin_L=knee, foot_L=ank, foot_L_tip=(130, 1750),
        thigh_R=(hip[0] + 16, hip[1]), shin_R=(knee[0] + 16, knee[1]), foot_R=(ank[0] + 16, ank[1]), foot_R_tip=(146, 1750),
        flap=(200, 1180))
    return PS.write(only) if write else PS


if __name__ == '__main__':
    build()
