---
name: aplus-content
description_zh: "A+内容、创建A+、高级A+、品牌故事、更新A+、哪些ASIN有A+、关联ASIN、提交A+审核、下架A+、A+被拒、A+校验报错。"
description_en: "Use when managing Amazon A+ Content for a store — audit what is live, create Basic or Premium A+ or a Brand…"
author: SellerSheet AI
version: 0.22.1
metadata: {apis: [aplus], pattern: Gate}
description: >-
  Use when managing Amazon A+ Content for a store — audit what is live, create Basic or Premium
  A+ or a Brand Story, update live content, link or remove ASINs, submit for approval, take
  content down, or fix an A+ error. Triggers: "A+ content", "create A+", "Premium A+", "Brand
  Story", "update my A+", "which ASINs have A+", "link ASINs to A+", "submit A+", "suspend A+",
  "A+ rejected", "A+ validation error". Do NOT use to generate or edit the images themselves
  (use image-gen, which also has every module's image sizes) or for listing titles, bullets and
  attributes. 中文触发词：A+内容、创建A+、高级A+、品牌故事、更新A+、哪些ASIN有A+、关联ASIN、提交A+审核、下架A+、A+被拒、A+校验报错。
---

# A+ Content

The whole life of an A+ document through the SellerSheet `aplusContent_*` tools: find what is
live, write the document, check it, publish it, change it, take it down. Preflight first:
[`sellersheet-shared`](../sellersheet-shared/SKILL.md) (`get_user_context` succeeds,
`data.canUseMcp` is true, store refs are `<store>-<CC>`). A+ needs a brand-registered seller
(or a vendor account); Premium and Brand Story need an eligible brand on top.

Images come from [`image-gen`](../image-gen/SKILL.md): it knows each module's image sizes and
makes them. This skill writes the document those images go into.

## 0. Rules

- **Read before you write.** Before creating content for an ASIN, check what is live on it
  (`aplusContent_searchContentPublishRecords`). Only one document per ASIN per family (A+,
  Brand Story) is live at a time: approving a new one takes the ASIN over from the old one.
- **Every write tool carries `Gate: approve`.** Show the document or the ASIN change and wait
  for the user's approve, unless their own words already asked for this exact change.
- **ASIN links are a full replacement.** `aplusContent_postContentDocumentAsinRelations` sets
  the complete set; an ASIN left out loses this content. Read the current set first and send it
  whole.
- **One family per document.** All `STANDARD_*`, all `PREMIUM_*` (at most 7 modules) or all
  `BRAND_STORY_*` (exactly one `BRAND_STORY_IMAGE_WITH_LOGO`). Never mixed. Validate and create
  refuse a mix and an eighth Premium module, but accept a Brand Story without its
  `BRAND_STORY_IMAGE_WITH_LOGO`: check that card yourself.
- **Ids come from tool results only:** a `contentReferenceKey` from a search or a create, ASINs
  from the user or the catalog.
- **A 200 can still carry problems.** Read `data.errors` and `data.warnings` on every answer.

## 1. Which kind

| | Basic A+ | Premium A+ | Brand Story |
|---|---|---|---|
| Shows | under Product Description (vendors: From the Manufacturer) | the same slot, wider modules | "From the Brand", a carousel apart from A+ |
| `contentType` | `EBC` (seller), `EMC` (vendor) | `EBC` / `EMC` | `BrandStory` |
| Modules | 15 `STANDARD_*` | 19 `PREMIUM_*`, at most 7 per document | 5 `BRAND_STORY_*` |
| Who | brand-registered seller, vendor | an eligible brand (Amazon checks at create or submit) | an eligible brand |
| Badge on the document | `STANDARD` | `PREMIUM` | none |

A Premium module that needs a video (`PREMIUM_VIDEO_TEXT`, `PREMIUM_HERO_VIDEO`,
`PREMIUM_VIDEO_IMAGE_CAROUSEL`) takes media ids from Amazon's media registration, which these
tools do not offer yet: build Premium documents without them, and tell the user video modules
are set up in Seller Central.

Which module for which job, the page order and the copy rules: `reference/modules-guide.md`.
Every module's JSON: `reference/schema/` (README first).

## 2. The tools

| Tool | What it does | Writes |
|---|---|---|
| `aplusContent_searchContentPublishRecords(store, asin)` | what is live on one ASIN (content family and key) | |
| `aplusContent_searchContentDocuments(store)` | every document's metadata: name, status, badges | |
| `aplusContent_list_documents_detailed(store)` | up to 50 documents with their content and ASINs, for a sheet | |
| `aplusContent_getContentDocument(store, contentReferenceKey)` | one document, ready to edit and send back | |
| `aplusContent_listContentDocumentAsinRelations(store, contentReferenceKey)` | the ASINs a document is linked to | |
| `aplusContent_validateContentDocumentAsinRelations(store, asinSet, contentDocument)` | a dry run of a document against ASINs | |
| `aplusContent_create_and_publish(store, contentDocument, asinSet, submitForApproval)` | upload images, create, link ASINs, submit (each step reported) | yes |
| `aplusContent_updateContentDocument(store, contentReferenceKey, contentDocument)` | replace a document's content, key and ASINs kept | yes |
| `aplusContent_postContentDocumentAsinRelations(store, contentReferenceKey, asinSet)` | set the complete ASIN list | yes |
| `aplusContent_postContentDocumentApprovalSubmission(store, contentReferenceKey)` | submit for Amazon's review | yes |
| `aplusContent_postContentDocumentSuspendSubmission(store, contentReferenceKey)` | take live content off every linked ASIN | yes |

Images: each image slot takes its own image, at least the minimum size Amazon gives for that slot
in `reference/schema/` (a desktop and a mobile slot are two images of different shapes). Put an
image URL (or an existing A+ image id) in each image's `uploadDestinationId`.
Create, validate and update upload the URL; with `imageCropSpecification` left out they set the
crop to the full image, so make the image at the module's ratio (`image-gen` has every slot's
size) or give a crop of that ratio. A crop of another ratio comes back as an Amazon warning,
`MEDIA_FAILED_VALIDATION` ("dimensions … are not compatible with the image bounds").
Amazon takes PNG or JPEG of at most 3 MiB (3,145,728 bytes) per image. A larger one (an
AI-generated PNG often is) is re-encoded before upload: an opaque image becomes JPEG at full size, a
transparent PNG is scaled down, and its upload record carries a `note` saying so. Tell the user,
and check a scaled image still meets its slot's minimum size.

## 3. Workflows

**Audit a store.** `aplusContent_searchContentDocuments` → for the documents that matter,
`aplusContent_getContentDocument` and `aplusContent_listContentDocumentAsinRelations`
(`includedDataSet` `METADATA` adds per-ASIN badges: `CONTENT_PUBLISHED`,
`CONTENT_NOT_PUBLISHED`, `BRAND_NOT_ELIGIBLE`, `CATALOG_NOT_FOUND`). For one ASIN,
`aplusContent_searchContentPublishRecords` says what shoppers see. A publish record names the
family (`EBC`), never the tier: the tier is the document's badge.

**Create.**
1. Check what is live on the ASINs (§0). Agree the kind (§1) and the module list
   (`reference/modules-guide.md`) with the user.
2. Get the images made at their sizes (`image-gen`), or take the user's.
3. Write the document from `reference/schema/` and Amazon's limits there (character counts,
   image minimums, item counts).
4. Dry run: `aplusContent_validateContentDocumentAsinRelations`; fix every entry in
   `data.errors`. A clean dry run does not prove eligibility or ownership of the ASINs.
5. Show the document; on approve, `aplusContent_create_and_publish` with `submitForApproval`
   false. Read `data.steps`: a failed step stops the rest, and `data.contentReferenceKey` is set
   once create succeeded.
6. Read the links with `aplusContent_listContentDocumentAsinRelations` (`includedDataSet`
   `METADATA`): an ASIN badged `BRAND_NOT_ELIGIBLE`, or a warning such as "an existing retail
   contribution on this ASIN", will refuse the submit. Link the set again without it, or stop
   and tell the user (Amazon's own content owns that ASIN). Then
   `aplusContent_postContentDocumentApprovalSubmission`.
7. Status: `SUBMITTED`, then `APPROVED` or `REJECTED` (some accounts are approved at once).
   Review typically takes 1–7 business days.

**Change live content.** `aplusContent_getContentDocument` → edit → show the change →
`aplusContent_updateContentDocument` → `aplusContent_postContentDocumentApprovalSubmission`.
Updating an approved document, or posting its ASIN set, sets it back to `DRAFT`; Amazon keeps
the approved version live until the new one is approved, so always submit again. The locale
cannot change: a new locale is a new document.

**Add or remove ASINs.** Read the set (`aplusContent_listContentDocumentAsinRelations`, every
page) → change it → optionally dry-run → `aplusContent_postContentDocumentAsinRelations` with
the whole set → submit again. Amazon accepts any ASIN here and refuses an ASIN outside the brand
only at submit: check the per-ASIN badges.

**Take content down.** `aplusContent_postContentDocumentSuspendSubmission` removes it from every
linked ASIN; the document and its links stay, and it reads `DRAFT`. Bring it back by submitting
again.

## 4. When it fails

Amazon's answers and what to do about each: `reference/troubleshooting.md`. The common ones:
a field over its limit (the field path is in the error's `details`), a mixed or oversized
Premium list, a locale with an underscore, an ASIN outside the brand at submit, and Brand Story
refused for an account that lacks it.

## 5. The SellerSheet sheet

In the SellerSheet Google Sheet, the Create A+ tab builds Standard modules from its rows (one
module per row, config in row 4) and takes any document as JSON in its Content Document cell;
the List A+ tab lists every document. Load A+ fills Create A+ from a document key. Premium and
Brand Story documents load there as JSON; their modules have no row layout.
