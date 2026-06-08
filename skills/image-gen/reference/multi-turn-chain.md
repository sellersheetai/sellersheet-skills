# Multi-turn refine — the stateless chain

How to iterate on ONE image across many turns (refine, restyle step-by-step,
add elements one at a time) using only `generate_image` + `edit_image`. There is
no server-side conversation / `previous_response_id` chaining for images — the agent
threads state itself: **each turn's output Drive URL becomes the next turn's input.**

## The loop

The only thing you carry between turns is `current` — one Drive URL string.

1. **Anchor (turn 0).** Either `generate_image(...)` (inline → `data.images[0].drive_url`)
   or `edit_image(image_sources=[real_photo_url], prompt=adapted json_prompt)` →
   poll → `drive_url`. Set `current = drive_url`. Pass `output_folder_id` (or rely
   on the workspace `imagesFolderId`) so every turn lands in Drive and returns a URL.
2. **Refine (turns 1..N).** For each single change:
   - `edit_image(prompt=<one change + preserve-list>, image_sources=[current], provider="openai", output_folder_id=…)` → `job_id`
   - `check_image_job(job_id)` every ~30s until `status="done"`
   - read `drive_url` (the new image) + `revised_prompt` (drift signal). If `drive_url`
     is null on the first `done` poll, poll once more (Drive upload is async).
   - deliver + gate with the operator; on approval set `current = new drive_url`.
3. Repeat. Each `edit_image` turn costs 1 credit.

## Prompting each turn (see `prompting.md`)

- **One change per turn**, then restate the preserve-list every time (drift compounds):
  `Change only the background to a marble countertop. Keep the product geometry,
  branding, label text (verbatim), camera angle, lighting, and all other colors
  identical. Do not add or remove any object or text.`
- **Index multiple inputs** when a turn uses a reference (e.g. recolor):
  `Image 1 = master product (keep exact). Image 2 = color reference only.`
- Read `revised_prompt` from `check_image_job` to catch where the model drifted, and
  tighten the next turn.

## Worked example — hero mug, iterated
```
generate_image("white ceramic mug, studio product shot, soft light", openai)         → A
edit_image([A], "change only background → marble countertop; keep mug identical")    → poll → B
edit_image([B], "change only lighting → warm golden hour; keep everything else")      → poll → C
edit_image([C], 'add ONLY the text "12 OZ" bottom-right, small; change nothing else') → poll → D
```
Each arrow is one approved turn. `current` walks A→B→C→D. `D` is the final.

## Gotchas
- Chain input = the **full-res** `drive_url` (`uc?export=download&id=…`), NOT the
  `thumbnail_url`. The thumbnail is only for sheet `IMAGE()` previews.
- A fan-out (family recolor) is the same chain branched from one approved master —
  one `edit_image` per color from the master's `drive_url`, batch-poll with
  `check_image_jobs`. See Phase 4 + `gotchas.md`.
- Reliability ladder when openai stalls: retry once on openai, then fall
  back to `provider="nanobanana"` (single input). See `provider-matrix.md`.
