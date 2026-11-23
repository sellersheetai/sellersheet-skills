<!-- Generated from Amazon's A+ Content API model (2020-11-01) and its module pages. Do not hand-edit: regenerate. -->

# A+ content document — module reference

Read this before writing a `contentDocument` for the A+ tools (create, update, validate). One
file per module family: `standard.md`, `premium.md`, `brand-story.md`. Each module lists its JSON
key, every field with its type, whether it is required within its object, and its bounds, then a
skeleton to fill in (an array shows one item: repeat it within the bounds). Premium and Brand
Story modules also carry Amazon's own per-field limits (character counts, minimum image sizes);
for Standard image sizes see `../aplus-modules.md`.

## The document

```json
{
  "name": "…",
  "contentType": "EBC",
  "locale": "en-US",
  "contentModuleList": [{"contentModuleType": "STANDARD_HEADER_IMAGE_TEXT", "standardHeaderImageText": {}}]
}
```

- `name`: 1–100 characters, shown only in A+ Content Manager.
- `contentType`: `EBC` | `EMC` | `BrandStory`. `EBC` is a seller account's A+, standard or premium; `EMC` a
  vendor account's; `BrandStory` the "From the Brand" carousel.
- `locale`: a hyphenated language tag (`en-US`, `de-DE`, `ar-AE`), never an underscore. An update
  cannot change it.
- `contentModuleList`: 1–100 modules. Each module is `contentModuleType` plus ONE key, the
  module key named in the module's section, holding that module.

## Rules Amazon applies

- A document's modules are all `STANDARD_*`, all `PREMIUM_*` or all `BRAND_STORY_*`, never mixed.
- A Premium document holds at most 7 modules.
- A Brand Story document has exactly one `BRAND_STORY_IMAGE_WITH_LOGO`, the carousel's background.
- Only one document per ASIN per family (A+, Brand Story) is live at a time.
- Premium and Brand Story need an eligible brand: Amazon checks at create or submit, not at
  validate, so a clean validation does not prove eligibility.
- Video modules (`PREMIUM_VIDEO_TEXT`, `PREMIUM_HERO_VIDEO`, `PREMIUM_VIDEO_IMAGE_CAROUSEL`) take
  media ids that Amazon's media registration returns, which the SellerSheet tools do not create yet.

## Components

Used across every module; they appear by name in the shape tables.

| Component | JSON | Rules |
|---|---|---|
| `TextComponent` | `{"value": "…", "decoratorSet": [...]}` | `value` 1–10,000 chars unless the module's limits say less; `decoratorSet` optional |
| `ParagraphComponent` | `{"textList": [TextComponent, …]}` | 1–100 entries, one per line |
| `ImageComponent` | `{"uploadDestinationId": "…", "altText": "…", "imageCropSpecification": {…}}` | `altText` 1–100 chars. With the SellerSheet tools put an image URL in `uploadDestinationId` (it is uploaded for you) and leave the crop out (it is set to the full image) |
| `VideoComponent` | `{"videoMediaId": "…", "imageMediaId": "…", "imageCropSpecification": {…}}` | all three required |
| `PlainTextItem` | `{"position": 1, "value": "…"}` | positions unique within their list |
| `TextItem` | `{"position": 1, "text": TextComponent}` | positions unique within their list |

`decoratorSet[].type`: `LIST_ITEM` | `LIST_ORDERED` | `LIST_UNORDERED` | `STYLE_BOLD` | `STYLE_ITALIC` | `STYLE_LINEBREAK` | `STYLE_PARAGRAPH` | `STYLE_UNDERLINE`, each with `offset` and `length` (and `depth` for lists).
