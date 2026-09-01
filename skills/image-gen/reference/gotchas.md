# Gotchas (these WILL bite you — all observed in real runs)

## Required params & delivery (R2/CDN — Drive is NOT in this path)

- **`store` + `sku` + `slot` are REQUIRED on generate/edit** — the call is rejected
  (400) without them. They are what gives the image a canonical R2 home and
  therefore a `cdn_url` at all. The store ref must name the marketplace:
  **`<store>-<CC>`** (e.g. `myStore-US`) — a bare store name is rejected; pass a
  `store_refs` entry from `get_user_context` verbatim.
- **Check the Image Library before regenerating.** `list_generated_images(store,
  sku/parent_sku, slot)` finds every image already saved — free, and returns the
  exact image; a regeneration costs a credit and returns a different one.
- **Open the returned `cdn_url` / `thumbnail_url` directly.** If your harness needs
  the bytes locally to display the image, fetch with curl:
  `curl -sL "<cdn_url>" -o /tmp/x.png`.
- **`cdn_url` can lag `status='done'` by a few seconds** (the R2 upload is async).
  Null on the first done poll → poll once more, don't conclude failure. Job status
  is dropped ~15 min after submit — capture the URL before then (the image itself
  stays in the Library forever).
- **Deliver every image twice:** show it to the operator AND record it in the sheet.
  One image → one cell.
- **Don't fan out 20 image jobs at once.** A large concurrent burst overloads
  gpt-image-2 → mass "killed mid-processing" errors. Batch ~4–6 at a time (e.g.
  per color). Keep status updates flowing every turn.
- **If `AskUserQuestion` isn't available or returns empty in your harness, ask the
  operator in plain text.**

## Providers & billing (full rules: provider-matrix.md)

- **Never resubmit a `processing` job** — no client timeout exists; a resubmit is a
  new, separately-billed job. Re-run only on `status='error'` (errors and partial
  delivery are auto-refunded).
- **nanobanana smooths/loses fine texture** and outputs lower-res (~1024/1254). Use
  it for speed or an error re-run; for legible TEXT and max fidelity use openai.
  Mark nanobanana outputs "texture-degraded" in status.
- Insufficient credits → HTTP 402; the operator tops up **Image Credits** at
  sellersheetai.com/billing (the text-AI pool is separate — "Copy Credits").

## Resolution / size

- **Explicitly request `2048x2048` for product images** — the generate default is
  `1024x1024`, NOT 2048. gpt-image-2 honors the `size` param: request `2048x2048`
  → true 2048×2048 (≥1600 for Amazon zoom). Supported: `2048x2048` / `1536x1536` /
  `1024x1024` squares + `1024x1536` / `1536x1024`. Constraints: edges
  multiple-of-16, ≤3840px, ratio ≤3:1, area 655k–8.29M px — the server snaps any
  odd request to the nearest valid size.
- Image generation costs real money — set `quality` deliberately, especially on
  recolor fan-outs.

## Color / recolor

- **Recoloring a BLACK master LIGHTENS the result** — pure black → purple/blue comes
  out pale. Specify the exact target as "deeper, more saturated #HEX", and if your
  own visual check finds color is off (color accuracy < ~90) run a targeted
  **deepen pass** (edit "deepen/saturate to #HEX"). Best color fidelity: feed the
  child's REAL color photo as a 2nd input = COLOR REFERENCE ONLY ("do not copy its
  layout").
- When recoloring text/scene slots, instruct "recolor ONLY the pad; keep all text,
  numbers, icons, layout, background, people identical and legible" — edits can
  otherwise garble rendered text.

## References / product truth

- **A listing's own reference photo can be wrong/unrepresentative.** Example: a
  child's main photo showed a different mold (smooth + circular hole) than the real
  product (C-opening + textured) → you judged the shape wrong at ~65% fidelity. The
  image was actually correct. **When a reference contradicts the product, ASK the
  operator about the physical item — don't trust your own verdict or the photo.**
- **Your fidelity judgment is advisory, not gospel.** Scene/infographic slots
  naturally read low on product fidelity because you're comparing them against a
  product-only photo — gate those on human review, not the fidelity number. Gate
  main/detail slots on fidelity.
- Picking the wrong reference MODE wastes credits — "borrow the style" vs "keep the
  exact scene, swap the product" are different pipelines. See
  `reference-modes.md` BEFORE any reference-driven edit.

## Sheets

- **Write image cells the way the sidebar does**: formula `=IMAGE("<thumbnail_url>")`
  + a cell note `Full-res: <cdn_url>`. CDN https URLs render directly in `=IMAGE()`.
  To read a URL back out of a cell: the `=IMAGE()` formula first, then a URL in the
  note, then the raw value.
- **Use the sidebar's status vocabulary** (`DONE` / `QUEUED job:<id>` / `BLOCKED:` /
  `ERROR:`) — the tab's conditional formatting and the sidebar poller key on it.
  See `sheet-contract.md`.
- After any write, READ BACK the row and scan for `#VALUE! / #REF! / #SPILL! / #N/A`
  before claiming done. (Each image cell is an independent `=IMAGE()`, safe to write
  directly — unlike spilling-array-formula sheets where you must avoid the header
  cell.)

## Fan-out (Phase 4) subagent contract

For N colors × M slots, dispatch one background subagent PER COLOR. Give each: the
master slots' **cdn_urls**, the color name + hex + real color-ref URL, the exact
sheet row + V1/status cell letters, and the full per-slot loop (edit_image → poll →
on `error` re-run once → write cell per the conventions above → after all M, build
a contact-sheet preview with script/preview_builder.py and show it to the operator).
Have it RETURN the cdn_urls, any re-run/provider-switch slots, and garbled-text
warnings. Different colors = different rows → no write conflicts.
