# Gotchas (these WILL bite you — all observed in real runs)

## Delivery
- **Open the returned `drive_url` / `thumbnail_url` / `webViewLink` directly.** If your harness needs
  the bytes locally to display the image, fetch with curl:
  `curl -sL "https://drive.google.com/uc?export=download&id=<ID>" -o /tmp/x.png`.
- **Deliver every image twice:** show it to the operator AND record it in the sheet. One image →
  one cell.
- **To put a local image into Drive, use `start_drive_upload`** (returns a resumable `uploadUrl`; PUT
  the local bytes to it); **for an https source (e.g. an Amazon CDN image) use `save_url_to_drive`.**
  If a job returns inline b64 instead of a drive_url (can happen during backend restarts), decode the
  b64 and salvage it via `start_drive_upload`, or just **re-run the generation** until it returns a
  drive_url.
- **Don't fan out 20 image jobs at once.** A large concurrent burst overloads gpt-image-2 → mass
  "killed mid-processing" errors and stray inline-b64 returns. Batch ~4–6 at a time (e.g. per color),
  or accept heavy retries. Keep status updates flowing every turn.
- **If `AskUserQuestion` isn't available or returns empty in your harness, ask the operator in plain text.**

## Providers (see provider-matrix.md for the full ladder)
- **gpt-image-2 (provider="openai") backend intermittently TIMES OUT**, especially 2-input compose
  (seen 4+ times in one session). Signature: `check_image_job` status stays "processing" with a
  frozen `updated_at`, then errors "Request timed out". **Auto-retry once on openai, then fall back
  to provider="nanobanana"** (different backend, fast, single-input).
- **nanobanana smooths/loses fine texture** (e.g. a center grip band) and outputs lower-res
  (~1024/1254). Use it as a fallback or for speed; for legible TEXT (infographics, scale labels)
  and max fidelity prefer openai. Mark nanobanana outputs as "texture-degraded" in status.
- Jobs are async: `edit_image` returns a job_id → poll `check_image_job` (~30–40s;
  single 60–120s, compose 2–5 min). To wait in Bash use `for i in $(seq 1 N); do sleep 20; done`
  — a bare `sleep` is blocked by the harness.

## Resolution / size
- **Default to `2048x2048` for product images.** gpt-image-2 honors the `size` param: request
  `2048x2048` → true 2048×2048 (≥1600 for Amazon zoom). Supported: `2048x2048` / `1536x1536` /
  `1024x1024` squares + `1024x1536` / `1536x1024`. Constraints: edges multiple-of-16, ≤3840px,
  ratio ≤3:1, area 655k–8.29M px — the server snaps any odd request to the nearest valid size.
- Image generation costs real money — set `quality` deliberately, especially on recolor fan-outs.

## Color / recolor
- **Recoloring a BLACK master LIGHTENS the result** — pure black → purple/blue comes out pale.
  Specify the exact target as "deeper, more saturated #HEX", and if your own visual check finds
  color is off (color accuracy < ~90) run a targeted **deepen pass** (edit "deepen/saturate to #HEX"). Best color fidelity: feed
  the child's REAL color photo as a 2nd input = COLOR REFERENCE ONLY ("do not copy its layout").
- When recoloring text/scene slots, instruct "recolor ONLY the pad; keep all text, numbers, icons,
  layout, background, people identical and legible" — edits can otherwise garble rendered text.

## References / product truth
- **A listing's own reference photo can be wrong/unrepresentative.** Example: a child's main photo
  showed a different mold (smooth + circular hole) than the real product (C-opening + textured) →
  you judged the shape wrong at ~65% fidelity. The image was actually correct. **When a reference
  contradicts the product, ASK the operator about the physical item — don't trust your own verdict
  or the photo.** (Same principle as listing attribute-vs-bullet conflicts.)
- **Your fidelity judgment is advisory, not gospel.** Scene/infographic slots naturally read low on
  product fidelity because you're comparing them against a product-only photo — gate those on human
  review, not the fidelity number. Gate main/detail slots on fidelity.

## Sheets
- Drive images do NOT render via `uc?export=download` inside `=IMAGE()`. Use the thumbnail proxy:
  `=IMAGE("https://drive.google.com/thumbnail?sz=w400&id=<ID>")`. Amazon/alibaba CDN https URLs
  render directly.
- After any write, READ BACK the row and scan for `#VALUE! / #REF! / #SPILL! / #N/A` before
  claiming done. (In the 'Images Generation' sheet each image cell is an independent `=IMAGE()`,
  safe to write directly — unlike spilling-array-formula sheets where you must avoid the header cell.)

## Fan-out (Phase 4) subagent contract
For N colors × M slots, dispatch one background subagent PER COLOR. Give each: the master slot
Drive URLs, the color name + hex + real color-ref URL, the exact sheet row + V1/status cell letters,
and the full per-slot loop (edit_image → poll with retry/fallback → curl → write cell → after all M,
build a contact-sheet preview with script/preview_builder.py and show it to the operator). Have it
RETURN the drive IDs, any fallback slots, and garbled-text warnings. Different colors = different
rows → no write conflicts.
