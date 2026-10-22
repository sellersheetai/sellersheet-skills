# Reference modes — style vs blend vs exact swap

When the operator gives you a reference image, FIRST decide what they want from it.
The two ends of the spectrum take **different pipelines** (this mirrors Studio's
"Reference use" toggle, and the split is deliberate — do not unify them):

| Operator intent | Mode | Pipeline |
|---|---|---|
| "Recreate this LOOK around my product" | **A — Style** | reverse_prompt → adapt (you) → edit with product photos only |
| "Style mode keeps missing the look" | **B — Blend** | Mode A prompt + the ref appended LAST as an input |
| "Keep THIS exact scene, just put my product in it" | **C — Exact swap** | ONE edit call, ref FIRST as the base scene, short swap prompt |

Ask in plain text if the intent is ambiguous — "borrow the style, or keep the exact
scene and swap the product?" is a one-line question that saves a wasted credit.

## Mode A — Style (recreate the concept; the reference is NOT an input)

Two calls, then the edit:
1. `reverse_prompt(reference)` → structured `json_prompt` (free).
2. **Adapt it yourself** into ONE concise edit prompt (the art-director step), then
3. `edit_image(prompt=adapted, image_sources=[operator's real product photos])` —
   **do not include the reference image.** Its style rides only as text.

Adapt rules (each one earned by a real regression):
- **Recognize the reference's TYPE and keep what that type needs** — infographic →
  feature callouts + room for text; lifestyle → a believable in-use moment; size
  chart → a scale reference; main → clean background.
- **Adapt the concept to OUR product, don't translate literally.** Change clashing
  colors/props/backgrounds to flatter ours (a red apple in a red scene becomes our
  yellow banana in a yellow-flattering scene).
- **Preserve the reference's compositional logic**: camera angle, POINT OF VIEW,
  framing, lighting, mood. A first-person hand-held reference must stay
  first-person — generic slot briefs ("in-use scene") must never override the
  reference's framing.
- **Describe the product only briefly** — the sample photo is the product truth.
  Do not stuff specs, bullets, or keyword-rich titles into the edit prompt; they
  drown the composition.
- **Copyright-safe by construction**: the output is a NEW image sharing only the
  reference's idea and composition — reproduce NONE of its identifiable objects,
  props, text, or branding. This is the whole point of Mode A: recreate a
  competitor's winning logic without copyright exposure.
- **The operator's typed instruction wins** when present; when absent, the
  reference drives — don't inject a default brief that fights it.

## Mode B — Blend (style + visual anchor)

Same adapted prompt as Mode A, **plus** the reference appended **LAST** in
`image_sources`, labeled in the prompt:

    Image 1..N = the REAL product (keep exact: shape, colors, materials, text).
    LAST image = STYLE REFERENCE ONLY — borrow its lighting, scene, mood and
    composition; take NO product, color, object, or text from it.

Use Mode B when Mode A output keeps drifting from the look (a weak one-line style
description barely moves an edit — the real towel-restyle case). Trade-off: the
visual match is closer, but the model can copy recognizable elements — **never use
Mode B on a competitor's protected creative you must not visually reproduce.**

## Mode C — Exact swap (keep the scene, replace the product)

ONE call. **No reverse_prompt, no adapt** — turning the reference into a text
paragraph makes the model re-invent the scene and the layout drifts far from the
reference (observed repeatedly; this is why swap is a separate mode).

    edit_image(
      image_sources=[reference FIRST, product photo(s) after],
      prompt="Image 1 is the base scene — keep its layout, background, lighting,
              camera angle and every other element EXACTLY. Replace ONLY the
              product in it with the product shown in Image 2 (exact shape,
              colors, materials, printed text). Change nothing else.")

Caveat: gpt-image-2 has no mask-based inpainting — the whole frame re-renders, so
the swap is close-but-not-pixel-perfect. That is the best the current model does.

## Every mode

- An Amazon MAIN (s0) still overrides the reference: pure white, product-only,
  no text/props, square — state it in the prompt regardless of mode.
- Append your product-fidelity preserve-list once, at the end, in your own words
  (see `prompting.md` "change only X" block) — LLM-written adapt prose alone won't
  hold fidelity.
- Recolor is NOT a reference mode — it's the 2-input color-reference edit in
  `prompting.md` / SKILL Phase 4.
