# Choosing modules, ordering the page, writing the copy

The JSON of every module is in `schema/`; the image each one takes (size, desktop and mobile) is
in the `image-gen` skill's `reference/aplus-image-sizes.md`.

## Which module for which job

| Job on the page | Basic (`STANDARD_*`) | Premium (`PREMIUM_*`) |
|---|---|---|
| Open with the brand promise | `HEADER_IMAGE_TEXT`, `IMAGE_TEXT_OVERLAY` | `FULL_BACKGROUND_IMAGE`, `FULL_BACKGROUND_TEXT` |
| Brand mark | `COMPANY_LOGO` | (a full-width image with the logo in it) |
| One benefit with a photo | `SINGLE_SIDE_IMAGE`, `SINGLE_IMAGE_HIGHLIGHTS` | `IMAGE_TEXT`, `DUAL_IMAGE_TEXT` |
| Three or four benefits side by side | `THREE_IMAGE_TEXT`, `FOUR_IMAGE_TEXT`, `FOUR_IMAGE_TEXT_QUADRANT` | `FOUR_COLUMN_IMAGES` |
| Show several views or uses | `MULTIPLE_IMAGE_TEXT` | `IMAGE_CAROUSEL`, `NAVIGATION_CAROUSEL` |
| A routine or steps | — | `REGIMEN_CAROUSEL` |
| Point at parts of the product | — | `HOTSPOT_IMAGE`, `HOTSPOT_IMAGE_TEXT` |
| Detail beside a main image | `IMAGE_SIDEBAR` | — |
| Specifications | `SINGLE_IMAGE_SPECS_DETAIL`, `TECH_SPECS` | `TECH_SPECS` |
| Compare your range | `COMPARISON_TABLE` (up to 6 products) | `THREE_COLUMN_COMPARISON`, `COMPARISON_CAROUSEL`, `COMPARISON_SCROLLER` |
| Answer common questions | — | `FAQ` |
| Long text | `TEXT`, `PRODUCT_DESCRIPTION` | `TEXT` |
| Video | — | `VIDEO_TEXT`, `HERO_VIDEO`, `VIDEO_IMAGE_CAROUSEL` (not available through these tools yet) |

Brand Story is its own document (`contentType` `BrandStory`): one `BRAND_STORY_IMAGE_WITH_LOGO`
as the background, then cards: `BRAND_STORY_ABOUT` (logo and the brand's story),
`BRAND_STORY_MEDIA_ASSET` (one image), `BRAND_STORY_FOUR_ASIN` (four products to cross-sell, by
ASIN), `BRAND_STORY_QUESTIONS` (three questions about the brand). It shows on every ASIN it is
linked to, so it speaks for the brand, not one product.

## Page order

1. **Brand promise**: a header or full-width image and one line on why this product.
2. **Top benefits**: three or four benefit-led modules (outcomes, not a feature list), one
   clean photo each.
3. **How it works, detail**: close-ups, materials, parts.
4. **Comparison**: your own range, or yours against a generic one; objective rows only.
5. **In use**: the product in context.
6. **Trust**: materials and real certifications.

Basic has no hard module cap in the model (1–100); keep it to what a shopper scrolls, typically
five to seven. Premium stops at seven.

## Copy

- Each text field has Amazon's own limit in `schema/` (for example a Standard header's headline
  150 characters, its body 6,000; a Premium image-and-text headline 80). Write to the limit; do
  not leave a required headline empty.
- Alt text on every image, 100 characters at most, describing what the image shows.
- Never: prices, promotions, shipping terms, contact details or URLs, guarantees or warranties,
  medical or unproven claims, competitor names, superlatives you cannot prove. Use ™ and ®
  correctly.
- Benefit-led, short, scannable. One voice across the page and with the listing.
- Copy can be baked into an image or put in the module's text fields. Text fields localize
  (swap the text per marketplace, keep the image); baked text is checked word by word in the
  image.
- One document per locale: the locale is fixed once the document is created.
