# Prompting templates — gpt-image-2 (from OpenAI's gpt-image prompting guide)

Apply these on top of the json_prompt from `reverse_prompt`. The json_prompt is
great for *generation*; edits and text/overlays need the extra structure below.

## Prompt anatomy — order it consistently
Write every prompt in this order so the model sets the right "mode" and polish:
**1) scene/background → 2) subject → 3) key details (materials, textures, colors) →
4) constraints (keep/exclude) → 5) intended use.** Naming the use ("Amazon main
image", "feature infographic", "lifestyle ad") tells the model how polished and what
layout to produce. For complex requests use short labeled segments or line breaks, not
one long paragraph — a skimmable template beats clever syntax. Any format (plain
paragraph, bullet list, JSON-like, tag-based) works as long as intent + constraints
are unambiguous.

## Specificity & quality cues
Be concrete about materials, shapes, textures, and the visual medium (photo / 3D
render / watercolor). Add targeted quality levers ONLY when needed — "film grain",
"textured brushstrokes", "macro detail", "studio softbox lighting". Don't pile on
adjectives; each lever should earn its place.

## Latency vs fidelity — pick `quality` deliberately
- `quality="low"` — fastest/cheapest; fine for drafts, direction boards, quick color
  nudges, high-volume fan-outs. Try it first when fidelity isn't critical.
- `quality="high"` — for small/dense text, infographics, scale labels, close-up
  product macros, identity-sensitive edits, and any final main/hero. Always high for
  graphic/typographic slots.
- `quality="medium"` — a middle ground; compare against high before shipping text.

## Composition — control the shot
Specify framing/viewpoint (close-up, wide, top-down), angle (eye-level, low-angle),
and lighting/mood (soft diffuse, golden hour, high-contrast). If layout matters, call
out placement: "logo top-right", "subject centered with negative space on the left".
For wide / cinematic / low-light / neon scenes add scale, atmosphere, and color so the
model doesn't trade mood for surface realism.

## People, pose & action
When a scene includes a person, describe scale, body framing, gaze, and object
interaction: "full body visible, feet included", "hands naturally gripping the
handle", "looking down at the product, not the camera". These fix proportion, action
geometry, and gaze.

## Multi-image edits — index every input
gpt-image-2 disambiguates inputs far better when you label them by index and say
how they interact. Always lead the edit prompt with an index legend:

    Image 1 = the master product photo (the item to keep exact).
    Image 2 = color reference ONLY (sample its hue; ignore its shape/text).
    Task: recolor the product in Image 1 to match Image 2's hue. Change nothing
    else — same geometry, same label text, same camera angle, same lighting.

## Style transfer — feed the reference as a 2nd input, do NOT just describe it
To make YOUR product look like a reference image's *style* (its background,
lighting, camera angle, framing, mood), pass BOTH as indexed inputs to edit_image:

    Image 1 = the product to keep (your exact item — colors, geometry, text).
    Image 2 = STYLE REFERENCE ONLY — copy its background, lighting, angle, framing
              and mood; take NO product, color, object, or text from it.
    Task: render the Image-1 product in Image 2's style.

A single-input edit + a *text description* of the style does NOT work: edit_image
anchors to the input image's own composition and barely moves it — you get the
original back, lightly cleaned. The reference must be an actual input image for its
look to transfer. (Real example: "restyle our striped towels to a premium
gray-background reference" → single-input-with-description returned the original
nearly unchanged; the *same* task as a 2-input edit transferred the gray background
+ three-quarter angle + muted premium lighting correctly.)

Even when borrowing a style, still override it in the prompt for an Amazon MAIN
image: pure white background, no text/logos/props, product-dominant, square.

## Edits — "change only X" + repeat the preserve-list EVERY turn
State the single change, then restate the invariants on every iteration (drift
compounds otherwise):

    Change only: <the one thing>.
    Keep everything else identical: product geometry, proportions, branding,
    label text (verbatim), camera angle, framing, lighting, background, colors
    of all other elements. Do not add or remove any object or text.

## Literal text & overlays
- Put exact copy in straight quotes or ALL CAPS: Render "30-DAY FRESHNESS" once.
- Spell tricky brand names letter-by-letter to fix character accuracy.
- Specify typography as constraints: font weight, size, color, placement.
- Use quality="high" for small text, dense infographics, multi-font layouts.

## Photorealism / fidelity
- Include the literal word "photorealistic".
- Use photography language: "shot at eye level, 50mm lens, soft diffuse light".
- Ask for real texture: pores, fabric wear, grain, micro-imperfections.

## Transparency
gpt-image-2 has no transparent background. Generate opaque, then run a downstream
background-removal step. Do NOT request background="transparent" for gpt-image-2.

## Iterate small, not monolithic
Start from a clean base prompt; refine with single-change follow-ups
("make the lighting warmer", "remove the extra reflection"). Re-specify any
critical detail that starts to drift. The job's `revised_prompt` (returned by
job_status) shows how the model rewrote your prompt — read it to spot drift.
