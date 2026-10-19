# 02 — The 12 Principles applied to a Blender cut-out rig

Source: Frank Thomas & Ollie Johnston, *The Illusion of Life: Disney Animation* (1981);
summary at https://en.wikipedia.org/wiki/Twelve_basic_principles_of_animation

In a cut-out rig the parts are rigid drawings, so every principle has to be faked with
**transforms, part swaps and timing**. That is the whole craft.

| # | Principle | How to do it on a cut-out rig in Blender | Where it shows in our story |
|---|---|---|---|
| 1 | Squash & stretch | Non-uniform scale on a control bone at the part's base (`scale_y` down / `scale_x` up, keep area ≈ constant: `sx = 1/sqrt(sy)`). Never scale the head drawing more than ~8% or it goes off-model. | Puppy body squashes 20% on the bump into Kanha's leg; Kanha's root compresses ~6% on the kneel landing. |
| 2 | Anticipation | Key a small opposite move 3–6 f before the main action. | Kanha dips 4 f before turning his head; puppy crouches (tail down, body low) before the bump; small lean-back before the kneel. |
| 3 | Staging | One idea per shot, silhouette test (render a black alpha matte), keep the acting part of the body clear of other shapes. | Shot 3 is a single head-turn; Shot 4 is only the puppy looking up. |
| 4 | Straight-ahead vs pose-to-pose | Pose-to-pose: key poses (`CONSTANT`), then breakdowns, then switch to `BEZIER` and polish. Straight-ahead only for secondary drag (hair/tail) which we generate procedurally. | Every shot is blocked stepped first (`reviews/*_blocking`). |
| 5 | Follow-through & overlap | Child bones lag the parent by 2–4 f (offset keys or a damped-spring pass over the parent's rotation). | Hair locks, peacock feather, sash ends, puppy ears/tail, puppy tag. |
| 6 | Slow in / slow out | `BEZIER` + `AUTO_CLAMPED` handles; for holds, use ease-out/ease-in pairs. Only mechanical things linear. | All moves; camera push-in uses slow ease. |
| 7 | Arcs | Move hands/head with IK targets keyed on arcs (add a mid key offset perpendicular to the path); verify with motion paths / onion trails on the contact sheet. | Head turn dips on an arc; puppy's lift path to the chest is an arc. |
| 8 | Secondary action | Small layered actions that support the main one, never compete. | Friends nod/react while Kanha talks; puppy tail wags while trotting. |
| 9 | Timing | Frame counts per action (see `05_walk_cycles.md` and the timing cheat sheet). | Blink 5 f, head turn 8 f, bump 3 f squash + 6 f recoil. |
| 10 | Exaggeration | Push key poses beyond reality: bigger eye scale on the "notice", bigger head tilt. | Eyes scale to 115% on the notice; "aww" pose with shoulders up. |
| 11 | Solid drawing | View switching with real 3/4/side/back drawings; never rotate a front drawing to fake a side. Keep overlaps hidden. | Turn-around views are full drawings. |
| 12 | Appeal | Big readable eyes, simple silhouettes, chubby toddler proportions from the reference. | The reference design already has it — protect it by staying on-model. |
