<!-- Generated from Amazon's A+ Content API model (2020-11-01) and its module pages. Do not hand-edit: regenerate. -->

# A+ content document — module reference

Read this before writing a `contentDocument` for the A+ tools (create, update, validate). One
file per module family: `standard.md`, `premium.md`, `brand-story.md`. Each module lists its JSON
key, every field with its type, whether it is required within its object, and its bounds; then
Amazon's own limits for that module (character counts, minimum image sizes); then a skeleton to
fill in (an array shows one item: repeat it within the bounds).

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
