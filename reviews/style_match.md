# Style match log — Kanha front view

Each `style_match_vNN.png` = reference | rebuild | 50 % overlay.

## v01
- ✅ Proportions, face layout, eyes, jewellery positions align in the overlay.
- ❌ Hair: blobby, lost the wispy locks; bangs are lumps.
- ❌ Shoulders read as puffed sleeve caps (arm capsule tops visible).
- ❌ Sash too small, flap a plain leaf shape, dhoti legs bulge.
- ❌ Hands: chubby mittens, claw-like — reference hands are slim with tapered fingers and thin dark lines.
- ❌ Feet blobby; brows too thin; blush too pink.
- Fix plan: lower contour smoothing on hair, strand texture, arms behind torso shoulder, authored sash + pleated flap, new hand library.

## v02
- ✅ Hair silhouette now wispy; hand library rebuilt (16 poses); sash and flap closer.
- ❌ Hair texture radiates from one point (helmet look); reference has wavy, soft strands.
- ❌ Torso shoulders boxy; neck strip visible; upper arms tube-like.
- ❌ Dhoti legs balloon outward at the hem; shins long; feet look like slippers.
- ❌ Outlines heavier/darker than the reference.
- ❌ Hands face forward with spread fingers; reference shows relaxed hands in profile (thumb forward).

## v03
- ✅ Hands now hang in profile like the reference (thumb forward), wavy hair strands.
- ❌ Pale rings around the eyes (overflow mask colour ≠ shaded face colour).
- ❌ Visible seams at elbows (joint caps) and between hips and dhoti legs.
- ❌ Face outline boxy (the guide's jaw is hidden by hair); neck strip visible; elf ears; ball nose.

## v04  (`style_match_v04.png`, `style_match_v04_head.png`)
Structural fixes:
- **Pupils are clipped to the eye-white shape** (`clip_to`) instead of a skin ring → no rings.
- **Outline-as-backing** for limb chains and the dhoti (`__line` parts behind all fills of a chain) →
  seamless elbows/knees/hips at any angle.
- Round chubby face authored over the guide; neck hidden behind the torso; small round ears; soft
  nose; fuller lips; bell earrings; darker iris; hair sheen patches.

Result: overlay alignment is close on head, eyes, jewellery, torso, sash, legs and feet.
Remaining gaps (accepted for now, revisit in polish):
- Hair is cleaner / less painterly than the reference (fewer loose strands, smoother top).
- Dhoti legs slightly fuller at the hem; front flap simpler than the reference's layered pleats.
- Reference line work is softer in places (it is a painted illustration); ours is crisp vector.
