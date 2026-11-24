<!-- Generated from Amazon's A+ Content API model (2020-11-01) and its module pages. Do not hand-edit: regenerate. -->

# A+ module images — the size of every image slot

Every image an A+ module takes, with Amazon's minimum size. Make each image at its slot's size or
larger at the same ratio; Amazon scales it to the module. Each slot is its own image: a
full-width Premium or Brand Story module takes a desktop image AND a separate mobile image. Which
module to use, and the document itself, belong to the `aplus-content` skill.

## Standard (Basic) A+

| Module type | What the module is for | Image slot | Minimum size | Ratio |
|---|---|---|---|---|
| `STANDARD_COMPANY_LOGO` | The standard company logo image | Image | 600×180 | 3.33:1 |
| `STANDARD_COMPARISON_TABLE` | The standard product comparison table | Image in blocks 1-6 | 150×300 | 0.50:1 |
| `STANDARD_FOUR_IMAGE_TEXT` | Four standard images with text, presented across a single row | Image in blocks 1-4 | 220×200 | 1.10:1 |
| `STANDARD_FOUR_IMAGE_TEXT_QUADRANT` | Four standard images with text, presented on a grid of four quadrants | Image | 135×135 | 1.00:1 |
| `STANDARD_HEADER_IMAGE_TEXT` | Standard headline text, an image, and body text | Image | 970×600 | 1.62:1 |
| `STANDARD_IMAGE_SIDEBAR` | Two images, two paragraphs, and two bulleted lists | Main image | 300×400 | 0.75:1 |
| `STANDARD_IMAGE_SIDEBAR` |  | Sidebar image | 300×175 | 1.71:1 |
| `STANDARD_IMAGE_TEXT_OVERLAY` | A standard background image with a floating text box | Image | 970×300 | 3.23:1 |
| `STANDARD_MULTIPLE_IMAGE_TEXT` | Standard images with text, presented one at a time | Highlight Image (Note: Thumbnail generated automatically from highlight image) | 300×300 | 1.00:1 |
| `STANDARD_PRODUCT_DESCRIPTION` | Standard product description text | — (no image Amazon sizes) | — | — |
| `STANDARD_SINGLE_IMAGE_HIGHLIGHTS` | A standard image with several paragraphs and a bulleted list | Main image | 300×300 | 1.00:1 |
| `STANDARD_SINGLE_IMAGE_SPECS_DETAIL` | A standard image with paragraphs and a bulleted list, and extra space for technical details | Main image | 300×300 | 1.00:1 |
| `STANDARD_SINGLE_SIDE_IMAGE` | A standard headline and body text with an image on the side | Main Image | 300×300 | 1.00:1 |
| `STANDARD_TECH_SPECS` | The standard table of technical feature names and definitions | — (no image Amazon sizes) | — | — |
| `STANDARD_TEXT` | A standard headline and body text | — (no image Amazon sizes) | — | — |
| `STANDARD_THREE_IMAGE_TEXT` | Three standard images with text, presented across a single row | Image | 300×300 | 1.00:1 |

## Premium A+

| Module type | What the module is for | Image slot | Minimum size | Ratio |
|---|---|---|---|---|
| `PREMIUM_IMAGE_TEXT` | A single image paired with text, positioned side by side | `image` | 800×600 | 1.33:1 |
| `PREMIUM_TEXT` | A text-only module with headline and body text, allowing greater character limits than other modules for explaining more details or instructions on your product | — (no image Amazon sizes) | — | — |
| `PREMIUM_FULL_BACKGROUND_TEXT` | A full-width background image with a text overlay box containing subheadline, headline, and body text | `desktopImage` | 1464×600 | 2.44:1 |
| `PREMIUM_FULL_BACKGROUND_TEXT` |  | `mobileImage` | 600×450 | 1.33:1 |
| `PREMIUM_FULL_BACKGROUND_IMAGE` | A full-width background image that spans the entire module width, with optional headline and body text below | `desktopImage` | 1464×600 | 2.44:1 |
| `PREMIUM_FULL_BACKGROUND_IMAGE` |  | `mobileImage` | 600×450 | 1.33:1 |
| `PREMIUM_FOUR_COLUMN_IMAGES` | Four images displayed in a row with a single headline above | `image` | 300×225 | 1.33:1 |
| `PREMIUM_DUAL_IMAGE_TEXT` | Two images displayed side by side with a single headline above | `image` | 650×350 | 1.86:1 |
| `PREMIUM_IMAGE_CAROUSEL` | A carousel of full-width image panels, each with its own headline and body text | `desktopImage` | 1464×600 | 2.44:1 |
| `PREMIUM_IMAGE_CAROUSEL` |  | `mobileImage` | 600×450 | 1.33:1 |
| `PREMIUM_NAVIGATION_CAROUSEL` | A carousel of full-width image panels with clickable navigation tabs | `desktopImage` | 1464×600 | 2.44:1 |
| `PREMIUM_NAVIGATION_CAROUSEL` |  | `mobileImage` | 600×450 | 1.33:1 |
| `PREMIUM_REGIMEN_CAROUSEL` | A carousel with a module headline, full-width image panels, and navigation tabs | `desktopImage` | 1464×600 | 2.44:1 |
| `PREMIUM_REGIMEN_CAROUSEL` |  | `mobileImage` | 600×450 | 1.33:1 |
| `PREMIUM_THREE_COLUMN_COMPARISON` | A comparison table displaying products side by side with features, tooltips, and detail rows | `image` | 300×225 | 1.33:1 |
| `PREMIUM_COMPARISON_CAROUSEL` | A comparison table with product images, headline per product, and feature rows with text | `desktopImage` | 488×700 | 0.70:1 |
| `PREMIUM_COMPARISON_CAROUSEL` |  | `mobileImage` | 600×450 | 1.33:1 |
| `PREMIUM_COMPARISON_SCROLLER` | A scrollable comparison view with full-height product images, chart headline, and feature rows with text per product | `desktopImage` | 200×225 | 0.89:1 |
| `PREMIUM_HOTSPOT_IMAGE` | A full-width image with clickable hotspot markers that reveal headline and descriptive text for each point of interest | `desktopImage` | 1464×600 | 2.44:1 |
| `PREMIUM_HOTSPOT_IMAGE` |  | `mobileImage` | 600×450 | 1.33:1 |
| `PREMIUM_HOTSPOT_IMAGE_TEXT` | A full-width image with clickable hotspot markers, plus a module headline and body text above the image | `desktopImage` | 1464×600 | 2.44:1 |
| `PREMIUM_HOTSPOT_IMAGE_TEXT` |  | `mobileImage` | 600×450 | 1.33:1 |
| `PREMIUM_FAQ` | A list of question-and-answer pairs with a configurable background color scheme of light or dark | — (no image Amazon sizes) | — | — |
| `PREMIUM_TECH_SPECS` | A structured list of specification-definition pairs with a headline, for presenting key technical details of your product | — (no image Amazon sizes) | — | — |
| `PREMIUM_VIDEO_TEXT` | A video paired with text containing subheadline, headline, and body text | `video` (a video: make its thumbnail image at this size) | 800×600 | 1.33:1 |
| `PREMIUM_HERO_VIDEO` | A full-width video with optional headline and body text below | `heroVideo` (a video: make its thumbnail image at this size) | 1464×600 | 2.44:1 |
| `PREMIUM_VIDEO_IMAGE_CAROUSEL` | A carousel of panels, each containing a video or image with its own panel headline, subheadline, and body text | `video` (a video: make its thumbnail image at this size) | 800×600 | 1.33:1 |
| `PREMIUM_VIDEO_IMAGE_CAROUSEL` |  | `desktopImage` | 800×600 | 1.33:1 |
| `PREMIUM_VIDEO_IMAGE_CAROUSEL` |  | `mobileImage` | 600×450 | 1.33:1 |

## Brand Story

| Module type | What the module is for | Image slot | Minimum size | Ratio |
|---|---|---|---|---|
| `BRAND_STORY_IMAGE_WITH_LOGO` | The required background card for all Brand Story Content | `desktopImage` | 1464×625 | 2.34:1 |
| `BRAND_STORY_IMAGE_WITH_LOGO` |  | `mobileImage` | 463×625 | 0.74:1 |
| `BRAND_STORY_FOUR_ASIN` | A Brand Story card displaying up to four product ASINs with images, enabling cross-selling to other products in your catalog | `productImage` | 166×182 | 0.91:1 |
| `BRAND_STORY_MEDIA_ASSET` | A Brand Story card featuring a single image as the primary visual element | `image` | 362×453 | 0.80:1 |
| `BRAND_STORY_ABOUT` | A Brand Story card with text-focused content for telling your Brand's story, mission, or values | `logoImage` | 315×145 | 2.17:1 |
| `BRAND_STORY_QUESTIONS` | A Brand Story card with question-and-answer pairs about your Brand | — (no image Amazon sizes) | — | — |
