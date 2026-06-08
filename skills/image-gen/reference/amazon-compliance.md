# Amazon image compliance + QA gate

Read before approving any image. Amazon SUPPRESSES non-compliant main images (the
listing loses its photo) and rejects non-compliant A+. Treat this as a hard gate,
not advice. Your own judgment is advisory on **category exceptions** — let the
operator override (see slot-canon "main image policy varies by category").

## MAIN image (s0) — hard rules
- **Pure white background, RGB 255/255/255** (the true-white, not off-white). Amazon
  literally samples the corners. Generate on pure white; verify the corners read #FFF.
- **Product fills ~85% of the frame.** Not tiny, not cropped.
- **Product only.** NO text, logos, watermarks, badges, borders, color blocks,
  insets/collages, props, backgrounds, hands, or graphics of any kind on the main.
- **Real, accurate product.** No illustration/render that misrepresents it. No
  bonus items shown that aren't included.
- **≥1600px on the longest side** (zoom). 2000px+ ideal. Request `2048x2048` (the default) and
  gpt-image-2 returns true 2048.
- **Square (1:1), JPEG/PNG/TIFF, sRGB.**
- Category exceptions exist (apparel on-model, some accept a composite main) —
  confirm with the operator; don't assume pure-white is always required.

## Gallery / secondary (s1–s8) — looser, but still
- No Amazon-prohibited claims baked into the image (see Claims below).
- Mobile-first: text must be **legible as a ~200px thumbnail** — big, high-contrast,
  ≤ a few words per line. Most buyers never tap to zoom.
- Keep a consistent brand system across the set (see brand kit in SKILL Phase 1).
- ≥1600px so the gallery zoom works.

## Claims & certifications (applies to images AND A+ text) — vet before render
Do NOT put on an image / in A+ text:
- Pricing, % off, deals, "sale", free shipping, time-sensitive ("new", "limited").
- "Best seller", "#1", "Amazon's Choice", "top rated", ranking/award claims without
  Amazon-acceptable proof.
- Guarantees/warranties (restricted in many categories), medical/health/disease
  claims, "cure/treat/prevent".
- Contact info, website URLs, QR codes, external links, social handles.
- Competitor names/comparisons by brand.
- **Certifications must be REAL and owned** (OEKO-TEX, GOTS, CE, FDA, FSC, etc.). If
  a reference image shows a cert mark, only keep it if the operator confirms they
  hold it — ASK. Never invent or carry over a cert from a competitor's photo.

## QA checklist — run per image before status=APPROVED
- [ ] **Resolution** ≥1600px longest edge (request `2048x2048` — the default).
- [ ] **Main: white purity** — corners sample #FFFFFF; product-only; no text/props.
- [ ] **Color accuracy** — matches the operator's REAL product (not the reference's).
- [ ] **Text correctness** — every rendered word is spelled right and legible at
      thumbnail size; no garbled/duplicated letters (gpt-image-2 garbles dense text).
- [ ] **Claims/cert** — nothing prohibited; certs are real (above).
- [ ] **Brand consistency** — palette/fonts/icon style match the rest of the set.
- [ ] **Fidelity** — product geometry/proportions true (gate main+detail on this).

## Localization (multi-marketplace)
The operator sells across UK/DE/FR/IT/ES/NL/PL/SE/etc. **Image text + A+ copy must be
localized per marketplace.** Reuse the same base photo; only the text/copy layer
changes. For A+ this is easy — the copy lives in Amazon's text fields per locale
(see aplus-modules.md), so the IMAGES are language-neutral. For PDP gallery
infographics (text baked in), produce one localized variant per marketplace.

## The compliance gate
`status` may only reach **APPROVED** after the QA checklist passes. Record the result
in the slot's `scores` cell, e.g.
`{"fidelity":98,"compliance":"pass","legible_thumb":true,"claims":"ok","verdict":"pass"}`.
On any main-image violation → status `FAILED: <reason>` and regenerate; never ship a
main that risks suppression.
