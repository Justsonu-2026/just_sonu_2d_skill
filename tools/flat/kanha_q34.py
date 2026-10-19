"""Kanha v2 (flat) — 3/4 FRONT view facing screen-left. Built from primitives.
Near side = character's LEFT (screen-right, suffix L); far side = RIGHT (screen-left, suffix R).
The facing-right 3/4 is this set mirrored in Blender."""
import math
from tools.art.geom import smooth_closed, smooth_open, ellipse_pts, capsule_pts, union_pts, catmull_rom_d
from tools.art.style import PartSet, bone_for
from tools.art.hands import hand_layers, HANDS, HANDS_SIDE
from tools.art.palette import far_side
from . import face as F
from .kit import Kit, LW, mirror
from .palette import KANHA

OUT = 'build/parts/kanha/q34'
SVG_OUT = 'characters/boy/parts/q34'


def build(write=True, out=None, svg_out=None, only=None, palette=None):
    P = palette or KANHA
    F.P = P
    K, KF = Kit(P), Kit(far_side(P, 0.12))
    PF = KF.P
    PS = PartSet(out or OUT, svg_out or SVG_OUT)

    def add(name, layers, pivot, z, backing=False, line_z=None, **extra):
        PS.add(name, layers, pivot, z, backing, line_z, bone=bone_for(name), **extra)

    HEAD = (350, 840)
    # ------------------------------------------------------------------ HEAD
    face_pts = []
    for i in range(40):
        a = 2 * math.pi * i / 40
        c, s = math.cos(a), math.sin(a)
        rx = 186 if c > 0 else 176
        face_pts.append((346 + rx * c - (14 * max(0, s) * max(0, -c)), 640 + 186 * s * (1.06 if s > 0 else 1.0)))
    face_d = smooth_closed(face_pts)
    fl = [dict(d=face_d, fill=P['skin'], stroke=P['line'], sw=LW, shade=K.cel(P['skin_sh'], 22, 10, 0.98))]
    fl += F.blush(198, 738, 20, 15) + F.blush(430, 740) + F.tilak(302, 525, 1.0, 0.84)
    add('head', fl, HEAD, 20)
    add('ear_L', [K.skin(smooth_closed(ellipse_pts(536, 668, 32, 44, 24))),
                  dict(d=smooth_open([(530, 648), (544, 668), (534, 690)]), stroke=P['line'], sw=4)], (516, 668), 18)

    hb = [ellipse_pts(372, 560, 252, 236, 48), ellipse_pts(574, 650, 84, 130, 32), ellipse_pts(160, 610, 56, 96, 32),
          K.tip(604, 720, 0.7), K.tip(584, 776, 1.1), K.tip(540, 800, 1.4), K.tip(134, 680, 2.4), K.tip(164, 730, 2.05)]
    add('hair_back', [K.hair(hb, extra=[K.streak([(220, 500), (250, 410), (350, 356)], 26)])], HEAD, 5)
    add('bun', [dict(d=smooth_closed(ellipse_pts(380, 322, 66, 62, 32)), fill=P['hair'], stroke=P['line'], sw=LW,
                     shade=K.cel(P['hair_sh'], 10, 10, 0.95), extra=[K.streak([(336, 320), (356, 284), (392, 272)], 14)])]
        + K.beads(320, 440, 372, sag=18), (380, 360), 4.6)
    add('feather', K.feather((440, 196), 0.42, [(400, 330), (416, 290), (428, 250)], sx=0.9), (408, 318), 4.4)

    groups = {
        0: [K.lock((200, 420), (172, 486), (158, 560), 86), K.lock((248, 404), (232, 470), (218, 540), 80)],
        1: [ellipse_pts(346, 418, 196, 64, 36), K.lock((300, 404), (288, 462), (272, 520), 72),
            K.lock((352, 404), (362, 458), (370, 512), 70)],
        2: [K.lock((400, 404), (424, 470), (444, 540), 90), K.lock((456, 410), (500, 480), (530, 566), 104)],
    }
    piv = {0: (220, 420), 1: (340, 400), 2: (460, 420)}
    for i, polys in groups.items():
        ex = [K.streak([(220, 420), (300, 384), (400, 392)], 18)] if i == 1 else []
        add(f'hair_lock_{i}', [K.hair(polys, cel=(8, 8), extra=ex)], piv[i], 32 + (0.5 if i == 1 else 0))

    eyes = {'R': (222, 654, -1, 0.7), 'L': (382, 654, 1, 1.0)}
    for side, (cx, cy, flip, sx) in eyes.items():
        add(f'eye_{side}_white', F.eye_white(cx, cy, 1.0, sx, flip), (cx, cy), 21, eye_white_of=f'eye_{side}')
        for st in F.EYE_STATES:
            add(f'eye_{side}_{st}', F.eye_over(cx, cy, 1.0, sx, flip, st), (cx, cy), 23, swap=f'eye_{side}', state=st)
        px = cx - 8 * sx
        add(f'pupil_{side}', F.pupil(px, cy + 6, 1.0, sx), (px, cy + 6), 22, clip_to=f'eye_{side}_white')
        add(f'brow_{side}', F.brow(cx - 4 * sx, 570, 1.0, sx, flip), (cx, 570), 25)
    add('nose', F.nose(282, 716, 1.0, 1.0, 1, view='q34'), (282, 716), 24)
    for m in F.MOUTHS:
        add(f'mouth_{m}', F.mouth(m, 300, 766, 1.0, 0.84), (300, 766), 26, swap='mouth', state=m)
    add('earring_L', K.earring(538, 704), (538, 704), 27)
    add('earring_R', K.earring(162, 708), (162, 708), 17)

    # --------------------------------------------------------------------- BODY
    add('neck', [dict(d=smooth_closed([(300, 760), (392, 760), (398, 880), (296, 880)]), fill=P['skin'])], (346, 870), 7.9)
    torso = [(300, 818), (262, 830), (234, 852), (220, 890), (222, 940), (228, 990), (230, 1060), (234, 1140), (246, 1220),
             (470, 1220), (482, 1140), (486, 1060), (490, 990), (496, 930), (488, 880), (462, 846), (424, 826)]
    td = smooth_closed(torso)
    add('torso', [dict(d=td, fill=P['skin'], stroke=P['line'], sw=LW, shade=K.cel(P['skin_sh'], 18, 6, 0.97),
                       extra=[dict(d=smooth_closed(ellipse_pts(346, 820, 110, 30, 24)), fill=P['skin_sh'])]),
                  dict(d=smooth_open([(258, 976), (282, 990), (306, 984)]), stroke=P['line'], sw=4),
                  dict(d=smooth_open([(338, 986), (372, 994), (406, 978)]), stroke=P['line'], sw=4),
                  dict(d=smooth_closed(ellipse_pts(318, 1076, 6, 9, 12)), fill=P['line'])], (350, 1150), 8)
    nk = K.chain([(250, 836), (268, 880), (316, 902), (380, 880), (410, 836)])
    nk += K.chain([(264, 846), (280, 930), (318, 972), (366, 930), (392, 846)], 7)
    nk += [dict(d=smooth_closed(ellipse_pts(318, 912, 16, 19, 20)), fill=P['gold'], stroke=P['line'], sw=4,
                shade=K.cel(P['gold_sh'], 5, 5, 0.9)),
           dict(d=smooth_closed(ellipse_pts(318, 912, 7, 8, 14)), fill=P['gem']),
           dict(d=smooth_closed([(318, 968), (330, 988), (318, 1010), (306, 988)]), fill=P['gem'], stroke=P['line'], sw=4)]
    add('necklace', nk, (330, 830), 12)

    arms = {'R': dict(sh=(240, 926), el=(206, 1030), wr=(178, 1118), flip=-1, z=7.5, lz=7.3, K=KF, sc=0.94),
            'L': dict(sh=(470, 926), el=(500, 1030), wr=(526, 1118), flip=1, z=14, lz=13.8, K=K, sc=1.0)}
    for side, a in arms.items():
        k = a['K']
        lsh = dict(cel=dict(dx=10 * a['flip'], dy=0, k=0.97))
        up = smooth_closed(capsule_pts(a['sh'], a['el'], 42 * a['sc'], 39 * a['sc']))
        add(f'upperarm_{side}', [k.skin(up, **lsh, extra=k.band(smooth_open([(a['sh'][0] - 60, 952), (a['sh'][0], 960),
                                                                             (a['sh'][0] + 60, 952)])))],
            a['sh'], a['z'], backing=True, line_z=a['lz'])
        fo = smooth_closed(capsule_pts(a['el'], a['wr'], 38 * a['sc'], 33 * a['sc']))
        add(f'forearm_{side}', [k.skin(fo, **lsh, extra=k.band(smooth_open([(a['wr'][0] - 50, a['wr'][1] - 18),
                                                                            (a['wr'][0], a['wr'][1] - 12),
                                                                            (a['wr'][0] + 50, a['wr'][1] - 18)]), 12))],
            a['el'], a['z'] + 0.1, backing=True, line_z=a['lz'])
        for h in HANDS + HANDS_SIDE:
            add(f'hand_{side}_{h}', hand_layers(h, a['wr'][0], a['wr'][1] - 4, a['sc'], a['flip'], 0.0, skin=k.hand_skin()),
                a['wr'], a['z'] + 0.2, swap=f'hand_{side}', state=h, backing=True, line_z=a['lz'])

    hips = [(226, 1110), (320, 1130), (490, 1108), (500, 1220), (502, 1300), (360, 1320), (214, 1300), (216, 1220)]
    sash = [(222, 1104), (270, 1118), (320, 1126), (400, 1118), (494, 1102), (498, 1150), (496, 1192), (400, 1204),
            (320, 1212), (270, 1204), (220, 1192), (218, 1150)]
    add('hips', [K.fillp(smooth_closed(hips), P['dhoti'], P['dhoti_sh'], cel=dict(dx=0, dy=14, k=0.97)),
                 dict(d=smooth_closed(sash), fill=P['sash'], stroke=P['line'], sw=LW * 0.8, shade=K.cel(P['sash_sh'], 0, 12, 0.97)),
                 dict(d=smooth_open([(352, 1170), (420, 1160), (480, 1148)]), stroke=P['sash_sh'], sw=6)],
        (350, 1160), 9, backing=True, line_z=8.4)
    legs = {'R': ([(224, 1250), (330, 1250), (334, 1380), (322, 1466), (304, 1490), (270, 1496), (244, 1488), (230, 1466),
                   (220, 1380)], KF, 8.5),
            'L': ([(320, 1250), (500, 1250), (504, 1380), (490, 1466), (466, 1494), (420, 1500), (378, 1494), (350, 1466),
                   (326, 1380)], K, 8.6)}
    for side, (pts, k, z) in legs.items():
        xs = [p[0] for p in pts]
        x0, x1 = min(xs) + 8, max(xs) - 8
        hem = smooth_open([(x0 - 10, 1468), ((x0 + x1) / 2, 1486), (x1 + 10, 1468)])
        fold = smooth_open([((x0 + x1) / 2 + 6, 1310), ((x0 + x1) / 2 + 8, 1380), ((x0 + x1) / 2 + 6, 1440)])
        add(f'dhoti_{side}', [k.fillp(smooth_closed(pts), k.P['dhoti'], k.P['dhoti_sh'], cel=dict(dx=14, dy=8, k=0.97),
                                      extra=[dict(d=hem, stroke=k.P['dhoti_hem'], sw=16), dict(d=fold, stroke=k.P['dhoti_sh'], sw=6)])],
            ((x0 + x1) / 2, 1260), z, backing=True, line_z=8.4 if side == 'L' else 8.3)
    flap = [(288, 1186), (352, 1186), (362, 1250), (356, 1320), (340, 1370), (318, 1396), (298, 1370), (284, 1320), (278, 1250)]
    add('flap', [dict(d=smooth_closed(flap, 0.7), fill=P['sash'], stroke=P['line'], sw=LW * 0.8, shade=K.cel(P['sash_sh'], 10, 0, 0.95),
                      extra=[dict(d=smooth_open([(306, 1210), (302, 1300), (312, 1370)]), stroke=P['sash_sh'], sw=5),
                             dict(d=smooth_open([(334, 1210), (338, 1300), (328, 1370)]), stroke=P['sash_sh'], sw=5)])],
        (320, 1196), 11)
    add('buckle', K.buckle(320, 1162, 26, 28), (320, 1162), 11.5)

    for side, sx, k, z in (('R', 272, KF, 6.0), ('L', 424, K, 6.6)):
        sd = smooth_closed(capsule_pts((sx, 1460), (sx, 1640), 38 if side == 'R' else 40, 36 if side == 'R' else 38))
        add(f'shin_{side}', [k.skin(sd, cel=dict(dx=10, dy=0, k=0.97),
                                    extra=k.band(smooth_open([(sx - 50, 1606), (sx, 1614), (sx + 50, 1606)]), 13))],
            (sx, 1470), z + 0.2, backing=True, line_z=z - 0.4)
        fpts = [(sx + 28, 1668), (sx - 30, 1664), (sx - 66, 1690), (sx - 88, 1726), (sx - 80, 1754), (sx - 40, 1764),
                (sx + 10, 1764), (sx + 38, 1752), (sx + 46, 1720), (sx + 44, 1690)]
        add(f'foot_{side}', k.foot(fpts, [sx - 70, sx - 48, sx - 26]), (sx, 1650), z, backing=True, line_z=z - 0.4)

    PS.skeleton = dict(
        root=(350, 1765), hips=(350, 1180), chest=(350, 1100), neck=(350, 840), head=HEAD, head_top=(370, 330),
        feather=(408, 318), lock_0=piv[0], lock_1=piv[1], lock_2=piv[2], earring_L=(538, 704), earring_R=(162, 708),
        upperarm_R=arms['R']['sh'], forearm_R=arms['R']['el'], hand_R=arms['R']['wr'], hand_R_tip=(166, 1236),
        upperarm_L=arms['L']['sh'], forearm_L=arms['L']['el'], hand_L=arms['L']['wr'], hand_L_tip=(538, 1236),
        thigh_R=(272, 1260), shin_R=(272, 1470), foot_R=(272, 1650), foot_R_tip=(200, 1750),
        thigh_L=(420, 1260), shin_L=(424, 1470), foot_L=(424, 1650), foot_L_tip=(350, 1750),
        flap=(320, 1196))
    return PS.write(only) if write else PS


if __name__ == '__main__':
    build()
