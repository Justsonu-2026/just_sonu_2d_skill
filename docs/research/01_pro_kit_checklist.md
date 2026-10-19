# 01 — What a professional character kit contains

**Benchmark page:** https://www.characterbazaar.com/children/red-hair-boy-animated-vector-cartoon-character-model-sheet-aka-leo

> Access note (2026-10-19): this session's network policy blocks `characterbazaar.com`
> (proxy answered `403` on CONNECT, and web search did not index the product page).
> The checklist below is therefore built from how Character Bazaar–style "animated vector
> cartoon character model sheet" products are normally packaged, and from the owner's own
> reference image, which is laid out exactly like one of those sheets
> (*Hand Gestures*, *Lip Sync*, *Turn Around*, two story poses). No art from the page was
> viewed or copied.

## Checklist (this is our definition of "a complete kit")

| # | Item | What it is | Our file(s) |
|---|------|-----------|-------------|
| 1 | Model sheet | Hero pose + name + palette, reference and rebuild side by side | `characters/boy/sheets/model_sheet.png` |
| 2 | Construction sheet | Head circle + jaw, body masses, head-height ruler | `characters/boy/sheets/construction.png` |
| 3 | Colour model | Every fill, shadow, highlight and line colour with hex | `characters/boy/sheets/colour_model.png`, `style_guide.md` |
| 4 | Turnaround | Front, 3/4 front L+R, side L+R, 3/4 back, back — same height, on a ground line | `characters/boy/sheets/turnaround.png` |
| 5 | Head kit per view | Head base, hair back, hair front locks, ears, brows, eyes, nose, mouth layers | `parts/boy_head_*` |
| 6 | Eye set | Open, half, closed, happy (^), squint, wide; separate pupils | `sheets/eyes.png` |
| 7 | Mouth / lip-sync chart | Viseme set (A/I, E, O, U, M/B/P, F/V, L, W/Q, rest) + expression mouths, front and 3/4 | `sheets/mouth_chart.png` |
| 8 | Hand library | 16+ hand poses per side | `sheets/hands.png` |
| 9 | Expression sheet | ~10 emotions, front + 3/4 | `sheets/expressions.png` |
| 10 | Action poses | A handful of story poses that prove the design survives acting | `sheets/poses.png` |
| 11 | Layered source | Every part on its own named layer, pivots set, overlaps hidden | `parts/*.svg` |
| 12 | Rigged file | Ready-to-animate rig for the target software | `boy_rig.blend` |
| 13 | Formats | Vector master (SVG/AI/EPS), PNG renders, rig file | SVG + PNG + .blend |

## What makes those kits feel "pro"

- **Consistency across views** — volumes do not drift between front and side.
- **Joints are pre-solved** — rounded overlaps, no seams when you bend.
- **Mouths match head angle** — a 3/4 head needs 3/4 mouths.
- **Hands are drawn, not scaled** — each gesture is its own drawing.
- **Lip-sync chart is organised by phoneme group**, labelled, consistent size.
- **Clean, closed shapes** with a consistent line weight; simple cel shadows.
