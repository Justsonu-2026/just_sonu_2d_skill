"""Import cut-out part PNGs (from tools/art builders) into Blender as textured planes.

Conventions
- 1 U (art unit) = 0.001 Blender units. Art (x, y) -> world (x, -, z):
      wx = (x - origin_x) * S,  wz = (origin_y - y) * S
- Draw order: world Y = -z_order * DEPTH (camera looks along +Y, so larger z_order is closer).
- Each plane's object origin sits at the part's pivot, so rotating the object (or its bone)
  rotates the drawing about the right joint.
- Material: image -> Emission (strength 1) mixed with Transparent by alpha, BLENDED render
  method. Optional `clip_to`: alpha is multiplied by another part's alpha, sampled through
  that part's object space (used to keep pupils inside the eye white).
"""
import json, os
import bpy
from mathutils import Matrix, Vector

S = 0.001
DEPTH = 0.002


def _mat_for(name, img_path, clip_obj=None, clip_img=None, clip_dims=None):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    try:
        mat.surface_render_method = 'BLENDED'
    except Exception:
        mat.blend_method = 'BLEND'
    mat.use_backface_culling = False
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    tex = nt.nodes.new('ShaderNodeTexImage')
    img = bpy.data.images.load(img_path, check_existing=True)
    img.alpha_mode = 'STRAIGHT'
    tex.image = img
    tex.interpolation = 'Linear'
    tex.extension = 'CLIP'
    emit = nt.nodes.new('ShaderNodeEmission')
    transp = nt.nodes.new('ShaderNodeBsdfTransparent')
    mix = nt.nodes.new('ShaderNodeMixShader')
    alpha_mul = nt.nodes.new('ShaderNodeMath'); alpha_mul.operation = 'MULTIPLY'
    vis = nt.nodes.new('ShaderNodeAttribute'); vis.attribute_type = 'OBJECT'; vis.attribute_name = 'vis'
    alpha_mul2 = nt.nodes.new('ShaderNodeMath'); alpha_mul2.operation = 'MULTIPLY'
    nt.links.new(tex.outputs['Color'], emit.inputs['Color'])
    nt.links.new(tex.outputs['Alpha'], alpha_mul.inputs[0])
    alpha_mul.inputs[1].default_value = 1.0
    if clip_obj is not None:
        # sample the clip part's texture in its own object space
        tc = nt.nodes.new('ShaderNodeTexCoord'); tc.object = clip_obj
        sep = nt.nodes.new('ShaderNodeSeparateXYZ')
        x0, z0, w, h = clip_dims
        mu = nt.nodes.new('ShaderNodeMath'); mu.operation = 'MULTIPLY_ADD'
        mu.inputs[1].default_value = 1.0 / w; mu.inputs[2].default_value = -x0 / w
        mv = nt.nodes.new('ShaderNodeMath'); mv.operation = 'MULTIPLY_ADD'
        mv.inputs[1].default_value = 1.0 / h; mv.inputs[2].default_value = -z0 / h
        comb = nt.nodes.new('ShaderNodeCombineXYZ')
        ctex = nt.nodes.new('ShaderNodeTexImage'); ctex.image = clip_img; ctex.extension = 'CLIP'
        nt.links.new(tc.outputs['Object'], sep.inputs[0])
        nt.links.new(sep.outputs['X'], mu.inputs[0])
        nt.links.new(sep.outputs['Z'], mv.inputs[0])
        nt.links.new(mu.outputs[0], comb.inputs['X'])
        nt.links.new(mv.outputs[0], comb.inputs['Y'])
        nt.links.new(comb.outputs[0], ctex.inputs['Vector'])
        nt.links.new(ctex.outputs['Alpha'], alpha_mul.inputs[1])
    nt.links.new(alpha_mul.outputs[0], alpha_mul2.inputs[0])
    nt.links.new(vis.outputs['Fac'], alpha_mul2.inputs[1])
    nt.links.new(alpha_mul2.outputs[0], mix.inputs['Fac'])
    nt.links.new(transp.outputs[0], mix.inputs[1])
    nt.links.new(emit.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs['Surface'])
    return mat


def make_plane(name, meta, partdir, origin, collection, z_offset=0.0, clip=None):
    """Create a plane for one part. origin = (ox, oy) art point that maps to world (0, 0)."""
    x0, y0, x1, y1 = meta['bbox']
    px, py = meta['pivot']
    # vertices relative to the pivot, in world units (X right, Z up)
    lx0, lx1 = (x0 - px) * S, (x1 - px) * S
    lz0, lz1 = (py - y1) * S, (py - y0) * S
    me = bpy.data.meshes.new(name)
    me.from_pydata([(lx0, 0, lz0), (lx1, 0, lz0), (lx1, 0, lz1), (lx0, 0, lz1)], [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new(name='UV')
    for i, (u, v) in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]):
        uv.data[i].uv = (u, v)
    ob = bpy.data.objects.new(name, me)
    collection.objects.link(ob)
    ob.location = ((px - origin[0]) * S, -(meta['z'] + z_offset) * DEPTH, (origin[1] - py) * S)
    ob['vis'] = 1.0
    ob['z_order'] = meta['z']
    ob['art_pivot'] = (px, py)
    ob['dims'] = (lx0, lz0, lx1 - lx0, lz1 - lz0)
    clip_obj = clip_img = clip_dims = None
    if clip is not None:
        clip_obj = clip
        clip_img = clip.active_material.node_tree.nodes['Image Texture'].image
        d = clip['dims']
        clip_dims = (d[0], d[1], d[2], d[3])
    mat = _mat_for('M_' + name, os.path.abspath(os.path.join(partdir, meta['name'] + '.png')),
                   clip_obj, clip_img, clip_dims)
    me.materials.append(mat)
    return ob


def import_view(partdir, collection_name, origin=(360.0, 1765.0), z_offset=0.0, prefix=''):
    metas = json.load(open(os.path.join(partdir, 'meta.json')))
    col = bpy.data.collections.new(collection_name)
    bpy.context.scene.collection.children.link(col)
    objs = {}
    # clip targets first
    order = sorted(metas, key=lambda m: 1 if m.get('clip_to') else 0)
    for m in order:
        clip = objs.get(m.get('clip_to')) if m.get('clip_to') else None
        ob = make_plane(prefix + m['name'], m, partdir, origin, col, z_offset, clip)
        for k in ('swap', 'state', 'line_of', 'clip_to', 'eye_white_of'):
            if k in m:
                ob[k] = m[k]
        objs[m['name']] = ob
    return objs, metas


def setup_render(scene, res=(1920, 1080), fps=24, engine='BLENDER_EEVEE', samples=8):
    scene.render.engine = engine
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.render.resolution_percentage = 100
    scene.render.fps = fps
    scene.view_settings.view_transform = 'Standard'
    scene.view_settings.look = 'None'
    scene.render.film_transparent = False
    scene.render.filter_size = 1.0
    try:
        scene.eevee.taa_render_samples = samples
    except Exception:
        pass
    if engine == 'CYCLES':
        scene.cycles.samples = samples
        scene.cycles.transparent_max_bounces = 128
        scene.cycles.max_bounces = 0
    w = scene.world or bpy.data.worlds.new('World')
    scene.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes.get('Background')
    if bg:
        bg.inputs['Color'].default_value = (1, 1, 1, 1)
        bg.inputs['Strength'].default_value = 1.0


def ortho_camera(scene, center=(0, 0.9), height=2.0, name='Camera'):
    cam_data = bpy.data.cameras.new(name)
    cam_data.type = 'ORTHO'
    cam_data.ortho_scale = height * scene.render.resolution_x / scene.render.resolution_y
    cam_data.clip_start = 0.01; cam_data.clip_end = 100
    cam = bpy.data.objects.new(name, cam_data)
    scene.collection.objects.link(cam)
    cam.location = (center[0], -20.0, center[1])
    cam.rotation_euler = (1.5707963, 0, 0)
    scene.camera = cam
    return cam
