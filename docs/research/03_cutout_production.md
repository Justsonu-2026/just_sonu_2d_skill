# 03 — How studios rig and animate cut-out characters

Links:
- Toon Boom Harmony — How to rig a cut-out character: https://docs.toonboom.com/help/harmony-21/premium/getting-started/character-building.html
- Toon Boom Harmony — About cut-out animation: https://docs.toonboom.com/help/harmony-24/premium/cut-out-animation/about-cut-out-animation.html
- Toon Boom — Mouth charts / lip-sync: https://learn.toonboom.com/modules/lip-sync-animation1/topic/mouth-charts1
- Moho Vitruvian bones (switching whole bone sets / views): https://anim.works/?p=23652
- Rhubarb Lip Sync (automatic mouth keys from audio): https://github.com/DanielSWolf/rhubarb-lip-sync

## Common practice (Harmony, Moho, Animate, After Effects + Duik)

1. **Layer splitting.** Every part that moves on its own is its own layer: head, hair back,
   hair front locks, ears, brows, eyes (white, iris, lid), nose, mouth, neck, torso, hips,
   upper arm, forearm, hand, thigh, shin, foot, clothing flaps.
2. **Joint overlaps with rounded ends.** The end of each limb segment is a circle centred on
   the pivot. The parent overlaps the child (or a fill-only "joint cap" sits on top), so the
   join stays clean at any angle. Lines that would cross the joint are removed.
3. **Pivot placement.** Pivot = centre of that rounded end. Wrong pivots are the #1 cause of
   "sliding" joints.
4. **Hierarchy / pegs.** Master peg → hips → torso → neck → head; torso → arms; hips → legs.
   Harmony uses pegs, Moho bones, Duik bones/IK in AE. In Blender: one armature, each part
   object bone-parented.
5. **Drawing substitution / switch layers.** Hands, mouths, eyes and whole views are
   *swapped*, not deformed. Harmony: drawing substitution (keyed stepped). Moho: switch
   layers + smart bones. Blender: integer custom properties driving visibility.
6. **Hand library.** 15–30 drawn hands per side; animator swaps them on the pose.
7. **Mouth charts / visemes.** Usually 8–10 shapes (A/I, E, O, U, MBP, FV, L, WQ, rest +
   expressions), drawn per head angle. Mouth changes 1–2 frames before the sound.
8. **Eye sets.** Eye whites, separate pupils (move/scale), lids as swaps for blinks
   (open → half → closed → half → open, 4–6 f).
9. **Head turnarounds & view switching.** Each head angle is a full drawing set. The head
   switches 1–3 frames before the body ("head leads"). A blur/smear or a one-frame
   in-between drawing hides the pop.
10. **Smears.** One- or two-frame stretched drawings on fast moves; in cut-out this is
    usually a scale-stretch along the motion direction or motion blur.
11. **Holds and moving holds.** A real freeze longer than ~12 f looks dead. A moving hold
    keeps breathing (1–2% chest scale), blinks, small head drift, overlapping hair settle.
12. **Animate on 1s or 2s.** TV cut-out usually animates on 1s for transforms, 2s for
    swaps. We render at 24 fps on 1s.

## What we take from it
- Parts as separate Blender objects with origins at the pivot.
- Joint caps (fill-only circles) above the two segments at each elbow/knee.
- `CONSTANT` interpolation for every swap property.
- Head-leads-body view switching with a 2-frame offset.
