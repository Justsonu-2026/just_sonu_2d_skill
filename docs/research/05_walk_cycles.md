# 05 — Walk cycles

Links:
- Richard Williams, *The Animator's Survival Kit* (walk chapter).
- Overview of walk key poses: https://en.wikipedia.org/wiki/Walk_cycle

## Human (toddler) walk — 12 f per step, 24 f per cycle

Key poses per step (frame numbers for the first step of a 24 f cycle):

| Frame | Pose | Body height | Notes |
|---|---|---|---|
| 0 | **Contact** | mid | Front heel touches, legs at widest, arms opposite and widest |
| 3 | **Down** | lowest | Weight lands on front leg, knee bends, arms swing through |
| 6 | **Passing** | mid | Back leg passes the standing leg, foot lifted |
| 9 | **Up** | highest | Standing leg pushes, body highest |
| 12 | Contact (other foot) | mid | Mirror of frame 0 |

- A toddler: short stride, wider stance, slight side-to-side sway, bigger bob (about 4% of
  height), arms a little away from the body.
- **No foot sliding:** the planted foot's world X must stay fixed from contact to toe-off.
  We drive the root forward by exactly `stride / step_frames` per frame and place feet
  in world space with IK, so the contact foot is pinned.
- Overlap: head lags the body bob by 1–2 f; hair, feather and sash ends lag 2–4 f.
- Stop: last step is shorter, body overshoots forward then settles back over 6–10 f.

## Quadruped puppy trot — 8 f per step, 16 f cycle

- Trot = diagonal pairs move together (front-left with back-right).
- Body bobs twice per cycle; head counter-bobs slightly.
- Ears: floppy, lag 2–3 f behind head motion; tail: 3 segments, each lagging 2 f
  (wave travels down the tail). While happy the tail wags at ~4 f per side.
- Short legs → small stride, fast cadence (6–8 f per step).
