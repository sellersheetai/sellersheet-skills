# A+ Content modules — what to produce

A+ (Enhanced Brand Content) is the below-the-fold story. Two tiers: **Basic A+**
(any Brand-Registered seller) and **Premium A+** (wider modules, video, hover
hotspots, carousel — eligibility-gated). Slots a1–a5 (Basic) / p1–p5 (Premium) in
the sheet.

## Two ways to handle A+ copy
Amazon A+ modules have **their own text fields** (headline + body) rendered as live
HTML, so you can either:
1. **Bake the copy into the image** — gpt-image-2 renders headlines/labels directly at
   the module size (`provider="openai"`, `quality="high"`, exact quoted copy, QA every
   word). Best when the text is part of the visual design.
2. **Keep the image clean and use Amazon's text fields** — generate a text-free image and
   put the copy in the module's fields. Best for easy localization (swap the text per
   marketplace, reuse one image).
Pick per module; option 2 is the simplest default when you just need a headline over a photo.

## Module image dimensions (the stable spec — design to these)
gpt-image-2 honors these via the `size` param; ratio must be ≤ 3:1 (the server snaps
to the nearest valid size; resize to exact on upload if needed — Amazon also resizes
to the module).

| Module | Image size (px) | Ratio | Notes |
|--------|-----------------|-------|-------|
| Brand logo | 600×180 | 3.33:1* | *over 3:1 → make ~600×200 then crop; prefer the operator's real logo (feed as input) — generate a wordmark only if none exists |
| Standard image header w/ text | 970×600 | 1.62:1 | hero/lifestyle photo, text in field |
| Image & dark/light text overlay | 970×300 | 3.23:1* | *>3:1 → generate ~970×336 (≤3:1) and crop |
| Single image (left/right) & text | 300×300 | 1:1 | small square photo |
| Three images & text | 300×300 ×3 | 1:1 | trio of clean photos |
| Four images & text | 220×200 ×4 | 1.1:1 | icon/feature photos (quadrant variant = 135×135) |
| Single image & sidebar | 300×400 main | 3:4 | + small sidebar images |
| Image & highlights | 300×300 | 1:1 | photo + bulleted highlights (text field) |
| **Comparison chart** | thumbnails 150×300 | 1:2 | up to 6 products; you supply clean product thumbnails, fill the table cells with text in the editor — NOT a baked table image |
| **Premium** full-width modules | 1464×600 / 1464×625 | ~2.34–2.44:1 | wider hero/lifestyle; Premium tier |
| **Brand Story** background | 1464×625 | 2.34:1 | shows on ALL the brand's ASINs; + ASIN "store" cards |

Produce each image at the size above (or the nearest ≤3:1 the server returns, then
resize). Bake the copy in or keep it text-free per the two options above. For the
comparison chart, supply clean product thumbnails and fill the matrix in the editor.

## Basic A+ — Amazon SP-API module spec (the authoritative requirement)
A standard (Basic) A+ document is **one or more `Standard*` modules in sequence** (the
canonical Amazon example uses 5; there is no hard published max — Amazon's editor caps
it, typically 5–7). These are the module-type names + image sizes the API
(`create_and_publish_aplus` / `post_content_document_approval_submission`) expects. The px below are the
**minimums** — generate at the ratio and ≥ the module px, then resize to exact on
upload (Amazon also resizes to the module).

| SP-API module type | Image size (px) | Ratio |
|--------------------|-----------------|-------|
| `StandardCompanyLogo` | 600×180 | 3.33:1 |
| `StandardHeaderImageText` | 970×600 | 1.62:1 |
| `StandardImageTextOverlay` | 970×300 | 3.23:1 |
| `StandardSingleSideImage` | 300×300 | 1:1 |
| `StandardSingleImageHighlights` | 300×300 | 1:1 |
| `StandardSingleImageSpecsDetail` | 300×300 | 1:1 |
| `StandardImageSidebar` (main / sidebar) | 300×400 / 300×175 | 0.75:1 / 1.71:1 |
| `StandardMultipleImageText` | 300×300 | 1:1 |
| `StandardThreeImageText` | 300×300 | 1:1 |
| `StandardFourImageText` | 220×200 | 1.1:1 |
| `StandardFourImageTextQuadrant` | 135×135 | 1:1 |
| `StandardComparisonTable` | 150×300 (per-product thumb) | 0.5:1 |
| `StandardText` | text only — no image | — |

**Text limits** (the editor shows the live per-module limit — design to it):
headlines ~70–200 chars, body up to ~6,000 chars, **image alt text ≤100 chars**,
captions ≤200 chars. Alt text is required and must describe the image (accessibility +
indexing) — write it for every module image.
Source: Amazon SP-API A+ Content module spec
(developer-docs.amazon.com/sp-api/docs/a-plus-content-examples).

## Recommended A+ page arc (the narrative)
1. **Header / brand promise** — header image (970×600 or Premium 1464×625) + the one-line value prop.
2. **Top benefits** — 3–4 image+text modules, benefit-led (not feature lists); one clean photo each.
3. **How it works / detail** — close-up/material modules.
4. **Comparison chart** — your range, or your product vs. a generic; objective rows only.
5. **Use cases / lifestyle** — in-context photos.
6. **Trust** — materials, real certifications (see amazon-compliance.md), brand story.
7. **Brand Story module** — brand narrative + cross-sell ASIN cards (appears across the catalog).

## A+ text rules (same restrictions as image claims)
No pricing/promotions/shipping, no contact info/URLs, no guarantees/medical claims,
no competitor brand names, no unproven superlatives, correct ™/® usage. Keep
headlines short + benefit-led; body scannable. Per-module character limits are shown
in the A+ editor — design to the limit (don't overrun, don't leave a header empty).

## Production checklist
- [ ] Generate each A+ image at the module ratio, ≥ the module px (copy baked in or text-free).
- [ ] Comparison chart: clean product thumbnails only; the matrix text goes in the editor.
- [ ] Copy written per module (benefit-led); baked in (QA every word) or in Amazon's text fields, localized per marketplace.
- [ ] Brand logo: prefer the operator's real logo asset (feed as input); generate a wordmark only if none exists.
- [ ] Run the amazon-compliance QA (claims, certs, legibility, brand consistency).
- [ ] Record in the sheet's a1–a5 / p1–p5 columns.
