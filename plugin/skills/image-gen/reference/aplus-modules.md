# A+ module images — what to produce

A+ is the below-the-fold story of a detail page. This skill makes its images; the
`aplus-content` skill chooses the modules, writes the document and publishes it. Sheet slots
a1–a5 (Basic) / p1–p5 (Premium) are valid `slot` values on generate/edit, and they bill like any
other image.

## Sizes

Every image slot of every module type, with Amazon's minimum size, ratio and what the module is
for: `aplus-image-sizes.md`. Generate at the module's ratio and at least its minimum, then
resize to exact on upload (Amazon also scales to the module).

- gpt-image-2 takes the size through `size`, at a ratio of 3:1 or less (the server snaps to the
  nearest valid size). A slot over 3:1 (the 600×180 logo, the 970×300 overlay) is made at 3:1 or
  less and cropped: about 600×200 for the logo, 970×336 for the overlay.
- Full-width Premium and Brand Story modules take a desktop image AND a mobile image of another
  shape (1464×600 with 600×450; Brand Story 1464×625 with 463×625): make both from one scene.
- A video slot needs a thumbnail image at the slot's size; the video itself is not made here.

## Two ways to handle A+ copy

Amazon A+ modules have **their own text fields** (headline + body), so either:
1. **Bake the copy into the image**: gpt-image-2 renders headlines and labels at the module size
   (`provider="openai"`, `quality="high"`, exact quoted copy, QA every word). Best when the text
   is part of the design.
2. **Keep the image clean and use Amazon's text fields**: a text-free image, the copy in the
   module's fields. Best for localization (swap the text per marketplace, reuse one image).

Pick per module; option 2 is the simplest default when you just need a headline over a photo.

## Per image kind

- **Brand logo**: prefer the operator's real logo (feed it as an input image); generate a
  wordmark only if none exists.
- **Comparison thumbnails**: clean product shots on a plain ground, one per product, no table
  baked in. The comparison rows are text in the document.
- **Product cards (Brand Story four-ASIN)**: the product itself, the way it looks on its
  listing.
- **Full-width backgrounds**: keep the subject clear of the area where a text box or a hotspot
  marker sits.

## What the sheet slots hold

`a1–a5` and `p1–p5` hold one image each. A module that takes several images (a carousel, four
columns, a desktop and mobile pair) needs as many images as it has slots in
`aplus-image-sizes.md`; record what fits and keep the rest beside the document the
`aplus-content` skill builds.

## Production checklist

- [ ] Each image at the module ratio, at least the minimum, copy baked in or text-free.
- [ ] Desktop and mobile both made for every full-width Premium or Brand Story module.
- [ ] Baked copy: QA every word; localized per marketplace.
- [ ] Logo from the operator's real asset where one exists.
- [ ] The amazon-compliance QA (claims, certs, legibility, brand consistency).
- [ ] Recorded in the sheet's a1–a5 / p1–p5 columns.
