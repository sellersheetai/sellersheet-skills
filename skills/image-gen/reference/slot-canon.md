# Slot canon

Slots are numbered **s0–s8** (9 PDP slots). **s0 = MAIN image.** Each slot is a different image
ROLE for the SAME SKU — NOT a place for sibling color variants. A variation family = one ROW per
child SKU; each child's main goes in its `s0_v1`.

After s0, the secondary count is **flexible — pick what the product needs, don't force a fixed set.**
A strong default for a physical-goods PDP:

| Slot | Role | Buyer question it answers |
|------|------|---------------------------|
| s0 | main (white or category-allowed composite hero) | "what is it" |
| s1 | feature infographic (icon callouts) | "why this one" |
| s2 | in-use / lifestyle | "what can I do with it" |
| s3 | scale / fit / dimensions | "will it fit / how big" |
| s4 | material / detail macro | "is it well made / how does it work" |
| s5–s8 | category-specific (comparison, what's-in-box, variants, warranty/brand, size chart…) | varies |

Notes:
- **s0 main image policy varies by category.** Some categories require pure-white product-only;
  others accept a composite with a human model as the main. Confirm with the operator; your own
  amazon-compliance judgment does NOT know category exceptions — treat it as advisory, let the
  operator override. See `reference/amazon-compliance.md` for the hard main-image rules + QA gate.
- **Dims default 2048×2048** for PDP (Amazon wants ≥1600 for zoom). gpt-image-2 honors the `size`
  param — request `2048x2048` and you get true 2048. A+ module sizes: see
  `reference/aplus-modules.md`.
- Don't depict features the physical product lacks (e.g. straps) even if a stock photo shows them.

## Photographic slots vs graphic/typographic slots
Both are generated **directly with gpt-image-2** — the split is about prompt approach, not method.

- **Photographic:** s0 main, s2 lifestyle/in-use, s4 material/detail macro, recolor family, most
  A+ images. Use reverse_prompt → edit_image on the operator's real photos. Keep the main clean:
  no text/props.
- **Graphic/typographic (text / icons / measurements / brand baked into the image):** s1 feature
  infographic, s3 scale/dimensions, s5 comparison/size-chart/what's-in-box. **Generate these
  directly with gpt-image-2** — `provider="openai"`, `quality="high"`, exact copy in straight
  quotes, explicit typography constraints (font weight/size/placement), and **QA every word
  letter-for-letter** (must stay legible at a ~200px thumbnail). Spell brand names letter-by-letter
  for character accuracy. If the operator has a real logo, feed it as an input image so it's placed
  accurately rather than reinvented. Don't fabricate certifications or competitor comparisons —
  those are compliance liabilities (see `reference/amazon-compliance.md`).

## Copy brief before generating a graphic slot
For s1/s3/s5 and any text-bearing image, write the COPY first (operator-approved):
a ≤5–7-word benefit headline + one support line per image, mined from reviews/competitors —
benefit-led (not feature), quantified, mobile-scannable. The copy drives conversion as much as
the picture. Localize per marketplace (reuse the photo, swap the text).

## The 'Images Generation' sheet column map (post-renumber, s0–s8)
12 lead cols then nine 10-col slot blocks. Block start columns:
s0=M, s1=W, s2=AG, s3=AQ, s4=BA, s5=BK, s6=BU, s7=CE, s8=CO. After s8 come A+ a1–a5 / p1–p5.
Within a block the 10 cells are: ref, role, dim, prompt, composition, scores, **v1, v2, v3**, status.
So a slot's V1 cell = block start + 6 columns (s0_v1=S, s1_v1=AC, s2_v1=AM, s3_v1=AW, s4_v1=BG,
s5_v1=BQ, s6_v1=CA, s7_v1=CK, s8_v1=CU); status = block start + 9 (s0=V, s1=AF, s2=AP, s3=AZ,
s4=BJ, s5=BT, s6=CD, s7=CN, s8=CX).
