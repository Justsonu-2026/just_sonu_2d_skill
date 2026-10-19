# Plan

## Pipeline
1. **Guide layer** — `tools/segment_ref.py` classifies each reference view into material
   classes (skin, hair, dhoti, sash, gold, feather). Contours of those masks are the guide.
2. **Clean parts** — `tools/kanha_art/` builds every part as clean closed Bézier SVG paths:
   mask algebra (class ∩ cut-region ∪ hidden-area extension) → contour → resample →
   smooth → Catmull-Rom → cubic Bézier. Faces, eyes, mouths, hands, jewellery are authored
   parametrically in the same style. One cel-shadow tone per material, soft-edged like the
   reference, plus highlights.
3. **Rasterise** — `rsvg-convert` at 6× reference scale (crisp at 1080p close-ups).
4. **Blender** — each PNG becomes a plane object with origin at the part's pivot,
   bone-parented to an armature; swaps via custom properties + drivers; views via a `view`
   property; draw order via Y offsets.
5. **Animate** — Python keying helpers: blocking (constant) → breakdowns → bezier polish,
   procedural overlap for hair/feather/sash/ears/tail, blinks, lip-sync keys.
6. **Review loop** — render, contact sheets, look, write `reviews/*.md`, fix, repeat ≥ 3×.
7. **Edit** — ffmpeg: PNG sequence → H.264 MP4; GIF previews for the README.

## Order
M1 research → M2 front view rebuild + style match → M3 full kit → M4 rig → M5 Sample A →
M6 puppy + friends → M7 Sample B → M8 skill → M9 README + final push.
