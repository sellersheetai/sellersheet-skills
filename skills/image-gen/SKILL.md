---
name: image-gen
description: Use when creating or optimizing Amazon product listing images or A+ Content for a store SKU or a whole variation family — learns mature competitors' image style, generates/recolors product-faithful images with gpt-image-2 via the connected image MCP tools, enforces Amazon main-image compliance, builds A+ modules, scores them, builds review previews, and records into the operator's 'Images Generation' Google Sheet. Triggers: "make/optimize listing images", "main/hero image", "A+ content", "A+模块/品牌故事", "competitor image style", "出主图/副图/套图", "recolor variants", "image-gen on the row", "学竞品风格生成产品图". Default provider openai; gated phases (operator approves before spend). NOT for non-Amazon image edits — for that call the MCP image tools directly.
version: 0.8.1
---

# image-gen — Amazon listing image suite

Learn competitor image style → generate product-faithful images → score → preview → record to
the 'Images Generation' sheet. The hard-won rules live in `reference/`.
**Read the relevant reference file before the matching phase.**

- `reference/slot-canon.md` — slot model (s0=main … s8), roles, the PHOTOGRAPHIC-vs-GRAPHIC slot split, copy-brief
- `reference/amazon-compliance.md` — main-image hard rules, claims/cert vetting, the QA gate (run before APPROVED), localization
- `reference/aplus-modules.md` — A+ module dimensions + page arc; copy can be baked into the image or live in Amazon's text fields
- `reference/gotchas.md` — the failure modes that WILL bite you (delivery, providers, size & resolution, recolor)
- `reference/sheet-contract.md` — how to read/write the 'Images Generation' sheet without breaking it
- `reference/provider-matrix.md` — openai vs nanobanana: when to use which, retry/fallback ladder
- `reference/prompting.md` — edit/multi-image/text prompting templates (index inputs, preserve-lists, literal-text rules, photorealism cues). Apply on top of the reverse_prompt json_prompt for every edit.
- `reference/multi-turn-chain.md` — iterate ONE image across turns with generate_image + edit_image: thread the prior turn's drive_url back as the next edit_image input. Read before any step-by-step refine/restyle.
- `script/preview_builder.py` — build contact-sheet / comparison / direction previews to show the operator

## Golden rules (do not violate)
1. **Plan first, gate before spend.** Default to GATED phases: get operator sign-off on (a) the
   learned style/direction and (b) the first/master set, BEFORE generating the full family.
   Image generation costs real money — never fan out 20 images on an unconfirmed template.
2. **Product fidelity is sacred.** The generated product must match the operator's REAL photos.
   If a feature isn't on the physical product (e.g. straps), never render it — and if a real
   reference photo contradicts the product, ASK the operator, don't guess (see gotchas).
3. **Every image is delivered twice:** (a) shown/sent to the operator, (b) recorded in the
   'Images Generation' sheet. Save a local copy (curl the Drive URL) if your harness needs the
   bytes to display it. See `reference/gotchas.md`.
4. **Mirror the operator's language; lead with the action/decision; quantify (scores).**

## Phase 0 — Intake (ALWAYS gate here; ask the operator in plain text)
Branch on optimize-existing vs new product:
- **Optimize existing** → ask for **store + SKU**. Then ask: **do you already have an imitation /
  reference image?**
  - YES → use it as the style ref; **do NOT search Amazon for competitors.**
  - NO → go to competitor discovery.
- **New product** → ask for **sample product images + planned SKU name + store.**

Pull the variation family early (`search_listings_items(variation_parent_sku=…)`, union across
marketplaces) so you know every child SKU and which children lack a real color photo. Confirm
image-gen is alive first: `get_user_context` (canUseMcp, imagesFolderId).

## Phase 1 — Learn the style (GATE: show direction before generating)
Competitor discovery (only if no operator-supplied ref): **prefer a US store** — find **≥3 mature
US competitors** in-category via `search_catalog_items(keywords + salesRanks + images)`; take their
high-res mains. Then:
- Extract style from each competitor image: read the image (your own vision) + `reverse_prompt` to derive a structured JSON prompt.
- **Compare our current images vs competitors, per slot**, and write concrete gap notes + a
  per-slot optimization suggestion.
- For each suggestion, build a **direction board** locally so the operator sees the intended look:
  `python script/preview_builder.py direction --own OUR.jpg --refs REF1.jpg [REF2 …] --label "s1 infographic" --out dir_s1.jpg`, then show it to the operator.
- **Lock a brand kit** (reused across every slot + A+ for consistency): palette (hex), fonts,
  logo lockup (prefer the operator's real logo asset — feed it as an input image; generate a
  wordmark only if none exists), icon style, tone. Ask the operator if they have one; otherwise
  propose from the direction and confirm.
- **Gate:** operator confirms the direction + brand kit before any generation.

## Phase 2 — Master (GATE: master sign-off)
Generate the **s0 main** for the first/master SKU with `edit_image` (operator's real photos as the
product source + adapted style prompt). Judge product fidelity yourself (≥ 95 target) by visually
comparing the result to the operator's real product photos in-context. To refine it (fix lighting,
swap background, nudge composition) **iterate the stateless chain** — feed the master's `drive_url`
back as `edit_image`'s `image_sources` with a one-change + preserve-list prompt; see
`reference/multi-turn-chain.md`. Deliver + record. **Gate:** operator approves the master before
building the rest.

## Phase 3 — Secondary slots for the master SKU (GATE: full-set sign-off)
Plan the secondary slots per `reference/slot-canon.md` — **count is flexible per product**, not
fixed. Typical: s1 infographic, s2 in-use/lifestyle, s3 scale/fit, s4 material/detail (+ more).
- **Photographic vs graphic slots** (slot-canon): photo slots (s2/s4) are clean product shots;
  graphic slots (s1/s3/s5) carry text/icons/measurements/brand. **Generate BOTH directly with
  gpt-image-2** — for graphic slots use `provider="openai"`, `quality="high"`, exact quoted copy,
  and QA every word. No separate compositing step.
- **Write the copy brief first** for any text-bearing slot (≤5–7-word benefit headline + support
  line, operator-approved) — see slot-canon "Copy brief".
- Generate each at **2048×2048** (default) from real photos, deliver, record. Build a
  **contact-sheet preview** of s0–sN.
- **Run the QA gate** on each (`reference/amazon-compliance.md`): resolution ≥1600 (request
  `2048x2048` — the default), main white-purity + no text/props, claims/cert vetted, text legible
  at thumbnail size, brand-consistent. **Gate:** operator confirms the whole set before recolor.

## Phase 4 — Family recolor (fan-out)
Recolor the confirmed master set to every other child color. One **row per child SKU**; image goes
in that slot's V1. Use each child's REAL color photo as the 2nd input (color reference only) +
explicit hex; keep all text/scene/layout identical. Recoloring a black master tends to lighten —
state "deeper/saturated #hex" and add a deepen pass if color_accuracy < 90 (see gotchas). For large
fan-outs, dispatch one subagent per color (see `reference/gotchas.md` for the contract). Per color,
show a contact-sheet preview.

## Phase 5 — Deliver & record
Per image: open the returned `drive_url` / `thumbnail_url` / `webViewLink` (curl the Drive URL if
your harness needs a local copy to display), show it to the operator, then write the sheet cell.
After each color/set, show a preview. Read back the row and scan for `#VALUE!/#REF!/#SPILL!` before
reporting done. Close with a status summary.
- **Compliance gate before `APPROVED`:** run the `reference/amazon-compliance.md` QA checklist and
  record the multi-axis result in the slot's `scores` cell
  (`{"fidelity":98,"compliance":"pass","legible_thumb":true,"claims":"ok","verdict":"pass"}`).
  A main-image violation → `FAILED:<reason>` + regenerate; never ship a main that risks suppression.

## Phase 6 — A+ Content (when the operator wants A+ / Premium A+)
Read `reference/aplus-modules.md` first. Generate each module image at its dimensions (default to
the module's exact size) with gpt-image-2. Two options for copy: **bake headlines/labels directly
into the image** (gpt-image-2 renders them — QA every word), OR keep the image clean and put the
copy in Amazon's module **text fields** (easier localization — reuse one image, swap the text per
marketplace). Build the page along the arc (header → benefits → comparison → trust → brand story).
If the operator has a real logo asset, feed it as an input image so it places accurately. Record
into the sheet's a1–a5 / p1–p5 columns; same compliance gate (claims/cert/legibility) applies.
