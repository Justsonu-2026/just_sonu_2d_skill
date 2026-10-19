"""Probe face control axes: render the eyes/mouth with each ACT/MSTR control moved along
each local axis. python tools/anim3d/face_probe.py <blend> <outdir> <bone> <amount>"""
import sys, os, time
sys.path.insert(0, os.getcwd())
import bpy
from tools.anim3d import playblast as pbk

blend, outdir, bone, amt = sys.argv[-4], sys.argv[-3], sys.argv[-2], float(sys.argv[-1])
bpy.ops.wm.open_mainfile(filepath=blend)
sc = bpy.context.scene
for ob in bpy.data.objects:
    if ob.type == 'MESH':
        for m in ob.modifiers:
            if m.type == 'SUBSURF':
                m.render_levels = min(m.levels, 1)
            if m.type == 'PARTICLE_SYSTEM':
                m.show_render = False
ob = [o for o in bpy.data.objects if o.type == 'ARMATURE' and o.name.startswith('RIG')][0]
pb = ob.pose.bones[bone]
head = ob.data.bones['FK-Head'].head_local
cd = bpy.data.cameras.new('C'); cam = bpy.data.objects.new('C', cd); sc.collection.objects.link(cam)
cam.location = (0.0, -0.9, head.z + 0.13); cam.rotation_euler = (1.5708, 0, 0); cd.lens = 70; sc.camera = cam
pbk.workbench(sc, res=(640, 360))
variants = [('rest', (0, 0, 0))] + [(f'{a}{s}', tuple((amt if s == '+' else -amt) if i == k else 0 for i in range(3)))
                                    for k, a in enumerate('xyz') for s in '+-']
paths = []
for name, v in variants:
    pb.location = v
    t = time.time()
    sc.frame_set(1)
    p = os.path.join(outdir, f'{bone}_{name}.png'); sc.render.filepath = p
    bpy.ops.render.render(write_still=True)
    print('TIME', name, round(time.time() - t, 1), flush=True)
    paths.append(p)
pbk.contact_sheet(paths, os.path.join(outdir, f'probe_{bone}.png'), cols=4, width=1600)
