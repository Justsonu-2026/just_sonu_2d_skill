"""Pose/axis test for a CloudRig character: key a few test poses and playblast them.
python tools/anim3d/pose_test.py <blend> <outdir>"""
import sys, os, time
sys.path.insert(0, os.getcwd())
import bpy
from tools.anim3d.rigkit import Rig, FWD, UP, LFT
from tools.anim3d import playblast as pbk

blend, outdir = sys.argv[-2], sys.argv[-1]
bpy.ops.wm.open_mainfile(filepath=blend)
sc = bpy.context.scene
ob = [o for o in bpy.data.objects if o.type == 'ARMATURE' and o.name.startswith('RIG')][0]
R = Rig(ob)
for side, word in (('L', 'left'), ('R', 'right')):
    R.pb[f'PRP-UpperArm.{side}'][f'ik_{word}_arm'] = 0.0

Y = (0, 1, 0)
def arms_down(f, extra_L=(), extra_R=()):
    R.key('FK-UpperArm.L', f, rot=[(Y, 72)] + list(extra_L))
    R.key('FK-UpperArm.R', f, rot=[(Y, -72)] + list(extra_R))

# f1 neutral arms down
arms_down(1)
for b in ('FK-Forearm.L', 'FK-Forearm.R', 'Jaw', 'FK-Head', 'FK-Neck'):
    R.key(b, 1, rot=[])
R.key('MSTR-Spine_Torso', 1, loc=(0, 0, 0), rot=[])
for b in ('ACT-Eyelid_Upper.L', 'ACT-Eyelid_Upper.R', 'ACT-MouthCorner.L', 'ACT-MouthCorner.R', 'MSTR-Eyebrow.L'):
    R.pb[b].location = (0, 0, 0); R.pb[b].keyframe_insert('location', frame=1)
# f2 elbows bend forward 60, L arm swings forward 30
arms_down(2, extra_L=[((1, 0, 0), -30)])
R.key('FK-Forearm.L', 2, rot=[((0, 0, 1), -60)])
R.key('FK-Forearm.R', 2, rot=[((0, 0, 1), 60)])
# f3 eyelids: local x +0.04 on L, local y on R ; mouth corners up ; jaw open
arms_down(3)
R.pb['ACT-Eyelid_Upper.L'].location = (0.04, 0, 0); R.pb['ACT-Eyelid_Upper.L'].keyframe_insert('location', frame=3)
R.pb['ACT-Eyelid_Upper.R'].location = (-0.04, 0, 0); R.pb['ACT-Eyelid_Upper.R'].keyframe_insert('location', frame=3)
R.pb['ACT-MouthCorner.L'].location = (0.03, 0, 0); R.pb['ACT-MouthCorner.L'].keyframe_insert('location', frame=3)
R.pb['ACT-MouthCorner.R'].location = (-0.03, 0, 0); R.pb['ACT-MouthCorner.R'].keyframe_insert('location', frame=3)
R.key('Jaw', 3, rot=[(LFT, 18)])
# f4 head turn left 30 + tilt, torso down
arms_down(4)
R.key('FK-Head', 4, rot=[(UP, 30), (FWD, 10)])
R.key('MSTR-Spine_Torso', 4, loc=(0, 0, -0.06), rot=[(LFT, 10)])

sc.frame_start, sc.frame_end = 1, 4
cd = bpy.data.cameras.new('TestCam'); cam = bpy.data.objects.new('TestCam', cd); sc.collection.objects.link(cam)
cam.location = (1.6, -3.0, 0.85); cam.rotation_euler = (1.5708, 0, 0.49); cd.lens = 50; sc.camera = cam
pbk.workbench(sc)
t = time.time()
paths = pbk.render_frames(sc, [1, 2, 3, 4], outdir, 'pose')
print('TIME per frame', (time.time() - t) / 4)
pbk.contact_sheet(paths, os.path.join(outdir, 'pose_sheet.png'), cols=2, width=1600)
# face close-up of f1 vs f3
cam.location = (0.35, -0.75, 1.12); cam.rotation_euler = (1.5708, 0, 0.44); cd.lens = 60
p = pbk.render_frames(sc, [1, 3], outdir, 'face')
pbk.contact_sheet(p, os.path.join(outdir, 'face_sheet.png'), cols=2, width=1600)
