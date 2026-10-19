# 04 — Blender for 2D cut-out work

Links:
- Blender manual (current): https://docs.blender.org/manual/en/latest/
- Grease Pencil (v3 since 4.3): https://docs.blender.org/manual/en/latest/grease_pencil/index.html
- Blender 4.3 overview of GPv3: https://www.cgchannel.com/2024/11/5-key-features-in-blender-4-3/
- GPv3 Python API change (modifiers moved to `object.modifiers`): https://projects.blender.org/blender/blender-developer-docs/pulls/72
- SVG import: https://docs.blender.org/manual/en/latest/addons/import_export/scalable_vector_graphics.html
- Drivers: https://docs.blender.org/manual/en/latest/animation/drivers/index.html
- IK constraint: https://docs.blender.org/manual/en/latest/animation/constraints/tracking/ik_solver.html
- `bpy` on PyPI (Blender as a Python module): https://pypi.org/project/bpy/

## Options for the art inside Blender

| Option | Pros | Cons |
|---|---|---|
| **Grease Pencil v3** | Native 2D, stroke thickness, layers, frames (great for swaps) | SVG import → GP loses gradients; stroke look differs from the reference painting; GP API changed heavily in 4.3 |
| **SVG → Curve → Mesh** | True vector, crisp at any zoom | Blender's SVG importer ignores gradients, blur and stroke styles; outlines need extra geometry |
| **SVG master → high-res PNG → textured plane (chosen)** | Keeps the full SVG look (gradients, soft shadow, strokes) exactly; one quad per part, fast; origin = pivot | Raster, so we render textures at ≥ 2× the largest on-screen size to stay crisp |

The owner's reference is a *painted* vector style (soft gradient shading, blush, thin
coloured line). Only the textured-plane route keeps that look, so we author SVG as the
master art and rasterise it with CairoSVG at 2–4× display size.

## Rigging in Blender for cut-out

- **Armature in the XZ plane**, camera orthographic looking down −Y. Bones rotate about the
  Y axis only (lock other rotations) so the rig stays flat.
- Parts are **bone-parented** (`parent_type = 'BONE'`) with origins at their pivots.
- **Draw order** = Y offset (closer to camera = in front). Per-view draw order is applied by
  setting each part's local Y from a table when `view` changes.
- **IK**: `IK` constraint on forearm/shin with `chain_count = 2` and a pole target; an
  `ik_fk` custom property drives the constraint `influence`.
- **Swap system**: integer custom properties on the `CTRL` bone (`mouth`, `eye_L`,
  `eye_R`, `brow_L`, `brow_R`, `hand_L`, `hand_R`, `view`). Each swap part's
  `hide_render`/`hide_viewport` is driven by `prop == index`. Keys on these properties use
  `CONSTANT` interpolation.
- **Bendy bones** are possible for soft limbs but our parts are rigid drawings, so we skip
  them (they would distort the painted art).

## Rendering crisp "vector-like" output

- Orthographic camera, `film_transparent` off, view transform **Standard** (not AgX/Filmic,
  which shift flat colours), look `None`.
- Materials: image texture → **Emission** (strength 1) mixed with **Transparent** by alpha
  → output. That gives exactly the texture colours.
- Engine: EEVEE (or Workbench/Cycles fallback). Texture interpolation `Linear` or `Cubic`,
  mipmaps on. Pixel filter ~1.0 px.
- Headless: `python script.py` with the `bpy` module, or `blender -b -P script.py`.
  In this container Blender's download site is blocked, so we use `pip install bpy`
  (Blender 5.2 LTS) and install Mesa EGL for offscreen GPU emulation.
