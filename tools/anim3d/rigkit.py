"""Helpers for animating CloudRig characters (Blender Studio rigs) from Python.

Conventions (armature space, before the `root` bone's transform):
  FWD = (0,-1,0)  the character faces -Y
  UP  = (0, 0,1)
  LFT = (1, 0,0)  the character's left (.L side) is +X

Rotations are given as a list of (axis, degrees) about *rest-pose armature axes* and are
converted to each bone's local basis by conjugating with the bone's rest matrix. For FK
children the axis is carried along by the parent's pose, which is what an animator expects
("bend the elbow about the arm's own hinge").
Locations are offsets in armature space, converted to the bone's local basis.
"""
import math
import bpy
from mathutils import Vector, Quaternion, Matrix, Euler

FWD = Vector((0, -1, 0))
UP = Vector((0, 0, 1))
LFT = Vector((1, 0, 0))


def ax(v):
    return Vector(v).normalized()


class Rig:
    def __init__(self, ob):
        self.ob = ob
        self.pb = ob.pose.bones
        self._rest = {b.name: b.matrix_local.to_3x3() for b in ob.data.bones}

    # ------------------------------------------------------------- conversion
    def q_local(self, bone, rots):
        """Quaternion basis for `bone` from [(axis, deg), ...] about rest armature axes (applied in order)."""
        Rw = Quaternion()
        for axis, deg in rots:
            Rw = Quaternion(ax(axis), math.radians(deg)) @ Rw
        M = self._rest[bone].to_quaternion()
        return M.inverted() @ Rw @ M

    def loc_local(self, bone, vec):
        return self._rest[bone].inverted() @ Vector(vec)

    # ------------------------------------------------------------- set + key
    def set(self, bone, rot=None, loc=None, scale=None):
        pb = self.pb[bone]
        if rot is not None:
            q = self.q_local(bone, rot) if isinstance(rot, list) else rot
            if pb.rotation_mode == 'QUATERNION':
                pb.rotation_quaternion = q
            elif pb.rotation_mode == 'AXIS_ANGLE':
                a, ang = q.to_axis_angle(); pb.rotation_axis_angle = (ang, *a)
            else:
                pb.rotation_euler = q.to_euler(pb.rotation_mode, pb.rotation_euler)
        if loc is not None:
            pb.location = self.loc_local(bone, loc)
        if scale is not None:
            pb.scale = scale if not isinstance(scale, (int, float)) else (scale,) * 3

    def key(self, bone, frame, rot=None, loc=None, scale=None, interp=None):
        self.set(bone, rot, loc, scale)
        pb = self.pb[bone]
        paths = []
        if rot is not None:
            paths.append({'QUATERNION': 'rotation_quaternion', 'AXIS_ANGLE': 'rotation_axis_angle'}.get(pb.rotation_mode, 'rotation_euler'))
        if loc is not None:
            paths.append('location')
        if scale is not None:
            paths.append('scale')
        for p in paths:
            pb.keyframe_insert(p, frame=frame, group=bone)
        if interp:
            self.set_interp(bone, frame, interp)

    def key_prop(self, bone, prop, value, frame, interp=None):
        pb = self.pb[bone]
        pb[prop] = value
        pb.keyframe_insert(f'["{prop}"]', frame=frame, group=bone)
        if interp:
            self.set_interp(bone, frame, interp, prop=prop)

    def set_interp(self, bone, frame, interp, prop=None):
        act = self.ob.animation_data.action
        for fc in fcurves(act):
            if f'pose.bones["{bone}"]' in fc.data_path and (prop is None or prop in fc.data_path):
                for kp in fc.keyframe_points:
                    if abs(kp.co.x - frame) < 0.01:
                        kp.interpolation = interp


def fcurves(action):
    """All F-Curves of an action (Blender 4.4+ layered actions or legacy)."""
    try:
        return list(action.fcurves)
    except Exception:
        out = []
        for layer in action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    out.extend(bag.fcurves)
        return out


def all_fcurves(ob):
    if not ob.animation_data or not ob.animation_data.action:
        return []
    return fcurves(ob.animation_data.action)


def ease(t):
    """Smoothstep slow-in/slow-out on 0..1."""
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def lerp(a, b, t):
    return a + (b - a) * t
