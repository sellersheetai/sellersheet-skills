<!-- Generated from Amazon's A+ Content API model (2020-11-01) and its module pages. Do not hand-edit: regenerate. -->

# Brand Story modules (5)

Shapes from the model; `Required` is within its object. Components: README.md.

## `BRAND_STORY_IMAGE_WITH_LOGO`

Module key: `brandStoryImageWithLogo`. The required background card for all Brand Story Content. Provides a full-width background image with a Brand logo overlay, headline, and body text. All other Brand Story modules appear within this carousel.

| Field | Type | Required | Bounds |
|---|---|---|---|
| `title` | TextComponent |  |  |
| `description` | ParagraphComponent |  |  |
| `desktopImage` | ImageComponent | yes |  |
| `mobileImage` | ImageComponent | yes |  |

Amazon's limits for this module:

| Field | Required | Constraint |
|---|---|---|
| `title` | Optional | value: max 30 chars |
| `description` | Optional | textList: max 3 rows; total ≤ 135 chars |
| `desktopImage` | Required | min 1464w × 625h px |
| `mobileImage` | Required | min 463w × 625h px |

```json
{
  "contentModuleType": "BRAND_STORY_IMAGE_WITH_LOGO",
  "brandStoryImageWithLogo": {
    "title": {
      "value": "…"
    },
    "description": {
      "textList": [
        {
          "value": "…"
        }
      ]
    },
    "desktopImage": {
      "uploadDestinationId": "<image URL or id>",
      "altText": "…"
    },
    "mobileImage": {
      "uploadDestinationId": "<image URL or id>",
      "altText": "…"
    }
  }
}
```

## `BRAND_STORY_FOUR_ASIN`

Module key: `brandStoryFourAsin`. A Brand Story card displaying up to four product ASINs with images, enabling cross-selling to other products in your catalog.

| Field | Type | Required | Bounds |
|---|---|---|---|
| `title` | TextComponent | yes |  |
| `brandStoreId` | TextComponent |  |  |
| `asinImages` | array of object | yes | exactly 4 items |
| `asinImages[].asinImage` | object | yes |  |
| `asinImages[].asinImage.productAsin` | TextComponent | yes |  |
| `asinImages[].asinImage.productImage` | ImageComponent | yes |  |

Amazon's limits for this module:

| Field | Required | Constraint |
|---|---|---|
| `title` | Required | value: max 30 chars |
| `brandStoreId` | Optional | value: max 100 chars |
| `asinImages` (exactly 4 items) | Required |  |
| `productImage` | Required | min 166w × 182h px |
| `productAsin` | Required | value: exactly 10 chars |

```json
{
  "contentModuleType": "BRAND_STORY_FOUR_ASIN",
  "brandStoryFourAsin": {
    "title": {
      "value": "…"
    },
    "brandStoreId": {
      "value": "…"
    },
    "asinImages": [
      {
        "asinImage": {
          "productAsin": {
            "value": "…"
          },
          "productImage": {
            "uploadDestinationId": "<image URL or id>",
            "altText": "…"
          }
        }
      }
    ]
  }
}
```

## `BRAND_STORY_MEDIA_ASSET`

Module key: `brandStoryMediaAsset`. A Brand Story card featuring a single image as the primary visual element.

| Field | Type | Required | Bounds |
|---|---|---|---|
| `title` | TextComponent |  |  |
| `description` | ParagraphComponent |  |  |
| `image` | ImageComponent | yes |  |

Amazon's limits for this module:

| Field | Required | Constraint |
|---|---|---|
| `title` | Optional | value: max 30 chars |
| `description` | Optional | textList: max 3 rows; total ≤ 135 chars |
| `image` | Required | min 362w × 453h px |

```json
{
  "contentModuleType": "BRAND_STORY_MEDIA_ASSET",
  "brandStoryMediaAsset": {
    "title": {
      "value": "…"
    },
    "description": {
      "textList": [
        {
          "value": "…"
        }
      ]
    },
    "image": {
      "uploadDestinationId": "<image URL or id>",
      "altText": "…"
    }
  }
}
```

## `BRAND_STORY_ABOUT`

Module key: `brandStoryAbout`. A Brand Story card with text-focused content for telling your Brand's story, mission, or values.

| Field | Type | Required | Bounds |
|---|---|---|---|
| `logoImage` | ImageComponent | yes |  |
| `title` | TextComponent |  |  |
| `slogan` | ParagraphComponent |  |  |

Amazon's limits for this module:

| Field | Required | Constraint |
|---|---|---|
| `logoImage` | Required | min 315w × 145h px |
| `title` | Optional | value: max 30 chars |
| `slogan` | Optional | textList: max 10 rows; total ≤ 450 chars |

```json
{
  "contentModuleType": "BRAND_STORY_ABOUT",
  "brandStoryAbout": {
    "logoImage": {
      "uploadDestinationId": "<image URL or id>",
      "altText": "…"
    },
    "title": {
      "value": "…"
    },
    "slogan": {
      "textList": [
        {
          "value": "…"
        }
      ]
    }
  }
}
```

## `BRAND_STORY_QUESTIONS`

Module key: `brandStoryQuestions`. A Brand Story card with question-and-answer pairs about your Brand.

| Field | Type | Required | Bounds |
|---|---|---|---|
| `questionAnswerPairs` | array of object | yes | exactly 3 items |
| `questionAnswerPairs[].questionAnswerPair` | object | yes |  |
| `questionAnswerPairs[].questionAnswerPair.question` | TextComponent | yes |  |
| `questionAnswerPairs[].questionAnswerPair.answer` | ParagraphComponent | yes |  |

Amazon's limits for this module:

| Field | Required | Constraint |
|---|---|---|
| `questionAnswerPairs` (exactly 3 items) | Required |  |
| `question` | Optional | value: max 70 chars |
| `answer` | Optional | textList: max 3 rows; total ≤ 200 chars |

```json
{
  "contentModuleType": "BRAND_STORY_QUESTIONS",
  "brandStoryQuestions": {
    "questionAnswerPairs": [
      {
        "questionAnswerPair": {
          "question": {
            "value": "…"
          },
          "answer": {
            "textList": [
              {
                "value": "…"
              }
            ]
          }
        }
      }
    ]
  }
}
```
