<!-- Generated from Amazon's A+ Content API model (2020-11-01) and its module pages. Do not hand-edit: regenerate. -->

# Premium A+ modules (19)

Shapes from the model; `Required` is within its object. Components: README.md.

## `PREMIUM_IMAGE_TEXT`

Module key: `premiumImageText`. A single image paired with text, positioned side by side. The image can appear on the left or right of the text block.

| Field | Type | Required | Bounds |
|---|---|---|---|
| `positionType` | LEFT \| RIGHT | yes |  |
| `subheadline` | TextComponent |  |  |
| `headline` | TextComponent | yes |  |
| `bodyText` | ParagraphComponent |  |  |
| `image` | ImageComponent | yes |  |

Amazon's limits for this module:

| Field | Required | Constraint |
|---|---|---|
| `positionType` | Required | `LEFT` \| `RIGHT` |
| `headline` | Required | value: 1–80 chars; not blank |
| `image` | Required | min 800w × 600h px |
| `subheadline` | Optional | value: max 40 chars |
| `bodyText` | Optional | textList: 1–5 items; total < 501 chars |

```json
{
  "contentModuleType": "PREMIUM_IMAGE_TEXT",
  "premiumImageText": {
    "positionType": "LEFT | RIGHT",
    "subheadline": {
      "value": "…"
    },
    "headline": {
      "value": "…"
    },
    "bodyText": {
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

## `PREMIUM_TEXT`

Module key: `premiumText`. A text-only module with headline and body text, allowing greater character limits than other modules for explaining more details or instructions on your product.

| Field | Type | Required | Bounds |
|---|---|---|---|
| `description` | ParagraphComponent | yes |  |
| `headline` | TextComponent |  |  |

Amazon's limits for this module:

| Field | Required | Constraint |
|---|---|---|
| `description` | Required | textList: 1–11 items; total ≤ 5000 chars |
| `headline` | Optional | value: max 80 chars |

```json
{
  "contentModuleType": "PREMIUM_TEXT",
  "premiumText": {
    "description": {
      "textList": [
        {
          "value": "…"
        }
      ]
    },
    "headline": {
      "value": "…"
    }
  }
}
```

## `PREMIUM_FULL_BACKGROUND_TEXT`

Module key: `premiumFullBackgroundText`. A full-width background image with a text overlay box containing subheadline, headline, and body text. The text box can be positioned to the left or right, and styled light or dark.

| Field | Type | Required | Bounds |
|---|---|---|---|
| `positionType` | LEFT \| RIGHT | yes |  |
| `colorType` | DARK \| LIGHT | yes |  |
| `subheadline` | TextComponent |  |  |
| `headline` | TextComponent |  |  |
| `description` | ParagraphComponent |  |  |
| `desktopImage` | ImageComponent | yes |  |
| `mobileImage` | ImageComponent | yes |  |

Amazon's limits for this module:

| Field | Required | Constraint |
|---|---|---|
| `positionType` | Required | `LEFT` \| `RIGHT` |
| `colorType` | Required | `DARK` \| `LIGHT` |
| `desktopImage` | Required | min 1464w × 600h px |
| `mobileImage` | Required | min 600w × 450h px |
| `subheadline` | Optional | value: max 40 chars |
| `headline` | Optional | value: max 60 chars |
| `description` | Optional | textList: 1–2 items; total ≤ 300 chars |

```json
{
  "contentModuleType": "PREMIUM_FULL_BACKGROUND_TEXT",
  "premiumFullBackgroundText": {
    "positionType": "LEFT | RIGHT",
    "colorType": "DARK | LIGHT",
    "subheadline": {
      "value": "…"
    },
    "headline": {
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

## `PREMIUM_FULL_BACKGROUND_IMAGE`

Module key: `premiumFullBackgroundImage`. A full-width background image that spans the entire module width, with optional headline and body text below.

| Field | Type | Required | Bounds |
|---|---|---|---|
| `headline` | TextComponent |  |  |
| `footer` | ParagraphComponent |  |  |
| `desktopImage` | ImageComponent | yes |  |
| `mobileImage` | ImageComponent | yes |  |

Amazon's limits for this module:

| Field | Required | Constraint |
|---|---|---|
| `desktopImage` | Required | min 1464w × 600h px |
| `mobileImage` | Required | min 600w × 450h px |
| `headline` | Optional | value: max 80 chars |
| `footer` | Optional | textList: 1–4 items; total < 301 chars |

```json
{
  "contentModuleType": "PREMIUM_FULL_BACKGROUND_IMAGE",
  "premiumFullBackgroundImage": {
    "headline": {
      "value": "…"
    },
    "footer": {
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

## `PREMIUM_FOUR_COLUMN_IMAGES`

Module key: `premiumFourColumnImages`. Four images displayed in a row with a single headline above. Each image has its own subheadline and body text.

| Field | Type | Required | Bounds |
|---|---|---|---|
| `headline` | TextComponent |  |  |
| `columns` | array of object | yes | 3–4 items |
| `columns[].imageColumn` | object | yes |  |
| `columns[].imageColumn.position` | integer | yes | 1– |
| `columns[].imageColumn.image` | ImageComponent | yes |  |
| `columns[].imageColumn.headline` | TextComponent |  |  |
| `columns[].imageColumn.description` | ParagraphComponent |  |  |

Amazon's limits for this module:

| Field | Required | Constraint |
|---|---|---|
| `headline` | Optional | value: max 80 chars |
| `columns` (3–4 items) | Required |  |
| `position` | Required | 1–4; unique per columns array |
| `image` | Required | min 300w × 225h px |
| `headline` | Optional | value: max 30 chars |
| `description` | Optional | textList: 1–5 items; total ≤ 150 chars |

```json
{
  "contentModuleType": "PREMIUM_FOUR_COLUMN_IMAGES",
  "premiumFourColumnImages": {
    "headline": {
      "value": "…"
    },
    "columns": [
      {
        "imageColumn": {
          "position": 1,
          "image": {
            "uploadDestinationId": "<image URL or id>",
            "altText": "…"
          },
          "headline": {
            "value": "…"
          },
          "description": {
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

## `PREMIUM_DUAL_IMAGE_TEXT`

Module key: `premiumDualImageText`. Two images displayed side by side with a single headline above. Each image has its own subheadline and body text.

| Field | Type | Required | Bounds |
|---|---|---|---|
| `headline` | TextComponent |  |  |
| `columns` | array of object | yes | exactly 2 items |
| `columns[].imageColumn` | object | yes |  |
| `columns[].imageColumn.position` | integer | yes | 1– |
| `columns[].imageColumn.image` | ImageComponent | yes |  |
| `columns[].imageColumn.headline` | TextComponent |  |  |
| `columns[].imageColumn.description` | ParagraphComponent |  |  |

Amazon's limits for this module:

| Field | Required | Constraint |
|---|---|---|
| `headline` | Optional | value: max 50 chars |
| `columns` exactly 2 items | Required |  |
| `position` | Required | 1 or 2; unique per columns array |
| `image` | Required | min 650w × 350h px |
| `headline` | Optional | value: max 50 chars |
| `description` | Optional | textList: 1–5 items; total ≤ 300 chars |

```json
{
  "contentModuleType": "PREMIUM_DUAL_IMAGE_TEXT",
  "premiumDualImageText": {
    "headline": {
      "value": "…"
    },
    "columns": [
      {
        "imageColumn": {
          "position": 1,
          "image": {
            "uploadDestinationId": "<image URL or id>",
            "altText": "…"
          },
          "headline": {
            "value": "…"
          },
          "description": {
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

## `PREMIUM_IMAGE_CAROUSEL`

Module key: `premiumImageCarousel`. A carousel of full-width image panels, each with its own headline and body text. Users swipe or click through panels.

| Field | Type | Required | Bounds |
|---|---|---|---|
| `headline` | TextComponent |  |  |
| `footer` | ParagraphComponent |  |  |
| `carouselCards` | array of object | yes | 2–6 items |
| `carouselCards[].imagePanel` | object | yes |  |
| `carouselCards[].imagePanel.position` | integer | yes | 1–6 |
| `carouselCards[].imagePanel.title` | TextComponent |  |  |
| `carouselCards[].imagePanel.buttonText` | TextComponent |  |  |
| `carouselCards[].imagePanel.asin` | TextComponent |  |  |
| `carouselCards[].imagePanel.description` | ParagraphComponent |  |  |
| `carouselCards[].imagePanel.desktopImage` | ImageComponent | yes |  |
| `carouselCards[].imagePanel.mobileImage` | ImageComponent | yes |  |

Amazon's limits for this module:

| Field | Required | Constraint |
|---|---|---|
| `headline` | Optional | value: max 80 chars |
| `footer` | Optional | textList: 1–4 items; total ≤ 300 chars |
| `carouselCards` (2–6 items) | Required |  |
| `position` | Required | 1–6; unique per carousel |
| `title` | Optional | value: max 50 chars |
| `buttonText` | Optional | value: max 12 chars |
| `asin` | Optional | value: exactly 10 chars |
| `description` | Optional | textList: 1–4 items; total ≤ 200 chars |
| `desktopImage` | Required | min 1464w × 600h px |
| `mobileImage` | Required | min 600w × 450h px |

```json
{
  "contentModuleType": "PREMIUM_IMAGE_CAROUSEL",
  "premiumImageCarousel": {
    "headline": {
      "value": "…"
    },
    "footer": {
      "textList": [
        {
          "value": "…"
        }
      ]
    },
    "carouselCards": [
      {
        "imagePanel": {
          "position": 1,
          "title": {
            "value": "…"
          },
          "buttonText": {
            "value": "…"
          },
          "asin": {
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
    ]
  }
}
```

## `PREMIUM_NAVIGATION_CAROUSEL`

Module key: `premiumNavigationCarousel`. A carousel of full-width image panels with clickable navigation tabs. Each panel has its own navigation text, subheadline, headline, and body text.

| Field | Type | Required | Bounds |
|---|---|---|---|
| `carouselCards` | array of object | yes | 2–5 items |
| `carouselCards[].navigationPanel` | object | yes |  |
| `carouselCards[].navigationPanel.position` | integer | yes | 1–5 |
| `carouselCards[].navigationPanel.title` | TextComponent |  |  |
| `carouselCards[].navigationPanel.navText` | TextComponent | yes |  |
| `carouselCards[].navigationPanel.subtitle` | TextComponent |  |  |
| `carouselCards[].navigationPanel.description` | ParagraphComponent |  |  |
| `carouselCards[].navigationPanel.desktopImage` | ImageComponent | yes |  |
| `carouselCards[].navigationPanel.mobileImage` | ImageComponent | yes |  |

Amazon's limits for this module:

| Field | Required | Constraint |
|---|---|---|
| `carouselCards` 2–5 items | Required |  |
| `position` | Required | 1–5; unique per carousel |
| `navText` | Required | value: 1–25 chars; not blank |
| `desktopImage` | Required | min 1464w × 600h px |
| `mobileImage` | Required | min 600w × 450h px |
| `title` | Optional | value: max 50 chars |
| `subtitle` | Optional | value: max 25 chars |
| `description` | Optional | textList: 1–4 items; total ≤ 100 chars |

```json
{
  "contentModuleType": "PREMIUM_NAVIGATION_CAROUSEL",
  "premiumNavigationCarousel": {
    "carouselCards": [
      {
        "navigationPanel": {
          "position": 1,
          "title": {
            "value": "…"
          },
          "navText": {
            "value": "…"
          },
          "subtitle": {
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
    ]
  }
}
```

## `PREMIUM_REGIMEN_CAROUSEL`

Module key: `premiumRegimenCarousel`. A carousel with a module headline, full-width image panels, and navigation tabs. Each panel has its own inset headline, inset body text, and navigation text.

| Field | Type | Required | Bounds |
|---|---|---|---|
| `headline` | TextComponent |  |  |
| `carouselCards` | array of object | yes | 2–5 items |
| `carouselCards[].regimenPanel` | object | yes |  |
| `carouselCards[].regimenPanel.position` | integer | yes | 1–5 |
| `carouselCards[].regimenPanel.title` | TextComponent |  |  |
| `carouselCards[].regimenPanel.navText` | TextComponent | yes |  |
| `carouselCards[].regimenPanel.description` | ParagraphComponent |  |  |
| `carouselCards[].regimenPanel.desktopImage` | ImageComponent | yes |  |
| `carouselCards[].regimenPanel.mobileImage` | ImageComponent | yes |  |

Amazon's limits for this module:

| Field | Required | Constraint |
|---|---|---|
| `headline` | Optional | value: max 100 chars |
| `carouselCards` 2–5 items | Required |  |
| `position` | Required | 1–5; unique per carousel |
| `navText` | Required | value: 1–20 chars; not blank |
| `desktopImage` | Required | min 1464w × 600h px |
| `mobileImage` | Required | min 600w × 450h px |
| `title` | Optional | value: max 20 chars |
| `description` | Optional | textList: 1–4 items; total ≤ 100 chars |

```json
{
  "contentModuleType": "PREMIUM_REGIMEN_CAROUSEL",
  "premiumRegimenCarousel": {
    "headline": {
      "value": "…"
    },
    "carouselCards": [
      {
        "regimenPanel": {
          "position": 1,
          "title": {
            "value": "…"
          },
          "navText": {
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
    ]
  }
}
```

## `PREMIUM_THREE_COLUMN_COMPARISON`

Module key: `premiumThreeColumnComparison`. A comparison table displaying products side by side with features, tooltips, and detail rows.

| Field | Type | Required | Bounds |
|---|---|---|---|
| `headline` | TextComponent | yes |  |
| `comparisonProducts` | array of object | yes | exactly 3 items |
| `comparisonProducts[].position` | integer |  | 1–3 |
| `comparisonProducts[].productTitle` | TextComponent |  |  |
| `comparisonProducts[].productAsin` | TextComponent |  |  |
| `comparisonProducts[].image` | ImageComponent |  |  |
| `comparisonRows` | array of object | yes | 2–5 items |
| `comparisonRows[].position` | integer |  | 1–5 |
| `comparisonRows[].metricValues` | array of object |  | exactly 3 items |
| `comparisonRows[].metricValues[].metricName` | TextComponent |  |  |
| `comparisonRows[].metricValues[].metricValue` | ParagraphComponent |  |  |

Amazon's limits for this module:

| Field | Required | Constraint |
|---|---|---|
| `headline` | Required | value: 1–80 chars; not blank |
| `comparisonProducts` (exactly 3 items) | Required |  |
| `position` | Required | 1–3; unique per `array` |
| `productTitle` | Required | value: 1–30 chars |
| `productAsin` | Required | value: exactly 10 chars |
| `image` | Required | min 300w × 225h px |
| `comparisonRows` 2–5 items | Required |  |
| `position` | Required | unique per `array` |
| `metricValues` exactly 3 items | Required |  |
| `metricName` | Required | value: 1–30 chars |
| `metricValue` | Required | textList: 1 item; max 80 chars |

```json
{
  "contentModuleType": "PREMIUM_THREE_COLUMN_COMPARISON",
  "premiumThreeColumnComparison": {
    "headline": {
      "value": "…"
    },
    "comparisonProducts": [
      {
        "position": 1,
        "productTitle": {
          "value": "…"
        },
        "productAsin": {
          "value": "…"
        },
        "image": {
          "uploadDestinationId": "<image URL or id>",
          "altText": "…"
        }
      }
    ],
    "comparisonRows": [
      {
        "position": 1,
        "metricValues": [
          {
            "metricName": {
              "value": "…"
            },
            "metricValue": {
              "textList": [
                {
                  "value": "…"
                }
              ]
            }
          }
        ]
      }
    ]
  }
}
```

## `PREMIUM_COMPARISON_CAROUSEL`

Module key: `premiumComparisonCarousel`. A comparison table with product images, headline per product, and feature rows with text.

| Field | Type | Required | Bounds |
|---|---|---|---|
| `headline` | TextComponent | yes |  |
| `comparisonProducts` | array of object | yes | 3–5 items |
| `comparisonProducts[].comparisonProduct` | object | yes |  |
| `comparisonProducts[].comparisonProduct.position` | integer |  | 1– |
| `comparisonProducts[].comparisonProduct.productTitle` | TextComponent |  |  |
| `comparisonProducts[].comparisonProduct.productAsin` | TextComponent |  |  |
| `comparisonProducts[].comparisonProduct.desktopImage` | ImageComponent |  |  |
| `comparisonProducts[].comparisonProduct.mobileImage` | ImageComponent |  |  |
| `comparisonMetrics` | array of object | yes | 3–7 items |
| `comparisonMetrics[].comparisonRow` | object | yes |  |
| `comparisonMetrics[].comparisonRow.position` | integer |  | 1– |
| `comparisonMetrics[].comparisonRow.metricName` | TextComponent |  |  |
| `comparisonMetrics[].comparisonRow.comparisonType` | TextComponent |  |  |
| `comparisonMetrics[].comparisonRow.additionalInfo` | TextComponent |  |  |
| `comparisonMetrics[].comparisonRow.comparisonFields` | array of object |  |  |
| `comparisonMetrics[].comparisonRow.comparisonFields[].comparisonField` | PlainTextItem | yes |  |

Amazon's limits for this module:

| Field | Required | Constraint |
|---|---|---|
| `headline` | Required | value: 1–25 chars; not blank |
| `comparisonProducts` (3–5 items) | Required |  |
| `position` | Required | 1–5; unique per `array` |
| `productTitle` | Required | value: 1–25 chars |
| `productAsin` | Required | value: exactly 10 chars |
| `desktopImage` | Required | min 488w × 700h px |
| `mobileImage` | Required | min 600w × 450h px |
| `comparisonMetrics` (3–7 items) | Required |  |
| `position` | Required | 1–7; unique per array |
| `metricName` | Optional | value: max 20 chars |
| `comparisonType` | Required | `checkbox` \| `input-field` |
| `comparisonFields` (3–5 items) | Required |  |
| `position` | Required | matches product position |
| `value` | Required | max 20 chars; "true"/"false" for checkbox |

```json
{
  "contentModuleType": "PREMIUM_COMPARISON_CAROUSEL",
  "premiumComparisonCarousel": {
    "headline": {
      "value": "…"
    },
    "comparisonProducts": [
      {
        "comparisonProduct": {
          "position": 1,
          "productTitle": {
            "value": "…"
          },
          "productAsin": {
            "value": "…"
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
    ],
    "comparisonMetrics": [
      {
        "comparisonRow": {
          "position": 1,
          "metricName": {
            "value": "…"
          },
          "comparisonType": {
            "value": "…"
          },
          "additionalInfo": {
            "value": "…"
          },
          "comparisonFields": [
            {
              "comparisonField": {
                "position": 1,
                "value": "…"
              }
            }
          ]
        }
      }
    ]
  }
}
```

## `PREMIUM_COMPARISON_SCROLLER`

Module key: `premiumComparisonScroller`. A scrollable comparison view with full-height product images, chart headline, and feature rows with text per product.

| Field | Type | Required | Bounds |
|---|---|---|---|
| `headline` | TextComponent | yes |  |
| `showATC` | boolean |  |  |
| `showPrices` | boolean |  |  |
| `showReviews` | boolean |  |  |
| `comparisonProducts` | array of object | yes | 3–7 items |
| `comparisonProducts[].comparisonProduct` | object | yes |  |
| `comparisonProducts[].comparisonProduct.position` | integer |  | 1– |
| `comparisonProducts[].comparisonProduct.productTitle` | TextComponent |  |  |
| `comparisonProducts[].comparisonProduct.productAsin` | TextComponent |  |  |
| `comparisonProducts[].comparisonProduct.desktopImage` | ImageComponent |  |  |
| `comparisonProducts[].comparisonProduct.mobileImage` | ImageComponent |  |  |
| `comparisonRows` | array of object | yes | 5–12 items |
| `comparisonRows[].comparisonRow` | object | yes |  |
| `comparisonRows[].comparisonRow.position` | integer |  | 1– |
| `comparisonRows[].comparisonRow.metricName` | TextComponent |  |  |
| `comparisonRows[].comparisonRow.comparisonType` | TextComponent |  |  |
| `comparisonRows[].comparisonRow.additionalInfo` | TextComponent |  |  |
| `comparisonRows[].comparisonRow.comparisonFields` | array of object |  |  |
| `comparisonRows[].comparisonRow.comparisonFields[].comparisonField` | PlainTextItem | yes |  |

Amazon's limits for this module:

| Field | Required | Constraint |
|---|---|---|
| `headline` | Required | value: 1–80 chars; not blank |
| `showATC` | Optional | `true` \| `false` |
| `showPrices` | Optional | `true` \| `false` |
| `showReviews` | Optional | `true` \| `false` |
| `comparisonProducts` 4–7 items | Required |  |
| `position` | Required | 1–7; unique per array |
| `productTitle` | Required | value: 1–25 chars |
| `productAsin` | Required | value: exactly 10 chars |
| `desktopImage` | Required | min 200w × 225h px |
| `comparisonRows` 5–12 items | Required |  |
| `position` | Required | 1–12; unique per array |
| `metricName` | Optional | value: max 30 chars |
| `comparisonType` | Required | `checkbox` \| `input-field` |
| `additionalInfo` | Optional | value: max 150 chars |
| `comparisonFields` 4–7 items | Required |  |
| `position` | Required | matches product position |
| `value` | Optional | max 30 chars; `true`/`false` for checkbox |

```json
{
  "contentModuleType": "PREMIUM_COMPARISON_SCROLLER",
  "premiumComparisonScroller": {
    "headline": {
      "value": "…"
    },
    "showATC": "true",
    "showPrices": "true",
    "showReviews": "true",
    "comparisonProducts": [
      {
        "comparisonProduct": {
          "position": 1,
          "productTitle": {
            "value": "…"
          },
          "productAsin": {
            "value": "…"
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
    ],
    "comparisonRows": [
      {
        "comparisonRow": {
          "position": 1,
          "metricName": {
            "value": "…"
          },
          "comparisonType": {
            "value": "…"
          },
          "additionalInfo": {
            "value": "…"
          },
          "comparisonFields": [
            {
              "comparisonField": {
                "position": 1,
                "value": "…"
              }
            }
          ]
        }
      }
    ]
  }
}
```

## `PREMIUM_HOTSPOT_IMAGE`

Module key: `premiumHotspotImage`. A full-width image with clickable hotspot markers that reveal headline and descriptive text for each point of interest.

| Field | Type | Required | Bounds |
|---|---|---|---|
| `desktopImage` | ImageComponent | yes |  |
| `hotSpots` | array of object | yes | 2–6 items |
| `hotSpots[].imageHotSpot` | object | yes |  |
| `hotSpots[].imageHotSpot.mobileImage` | ImageComponent | yes |  |
| `hotSpots[].imageHotSpot.title` | TextComponent | yes |  |
| `hotSpots[].imageHotSpot.description` | TextComponent |  |  |
| `hotSpots[].imageHotSpot.xCoordinate` | TextComponent | yes |  |
| `hotSpots[].imageHotSpot.yCoordinate` | TextComponent | yes |  |

Amazon's limits for this module:

| Field | Required | Constraint |
|---|---|---|
| `desktopImage` | Required | min 1464w × 600h px |
| `hotSpots` (2–6 items) | Required |  |
| `title` | Required | value: 1–50 chars |
| `xCoordinate` | Required | string pixel value (for example, "25") |
| `yCoordinate` | Required | string pixel value (for example, "150") |
| `mobileImage` | Required | min 600w × 450h px |
| `description` | Optional | value: max 200 chars |

```json
{
  "contentModuleType": "PREMIUM_HOTSPOT_IMAGE",
  "premiumHotspotImage": {
    "desktopImage": {
      "uploadDestinationId": "<image URL or id>",
      "altText": "…"
    },
    "hotSpots": [
      {
        "imageHotSpot": {
          "mobileImage": {
            "uploadDestinationId": "<image URL or id>",
            "altText": "…"
          },
          "title": {
            "value": "…"
          },
          "description": {
            "value": "…"
          },
          "xCoordinate": {
            "value": "…"
          },
          "yCoordinate": {
            "value": "…"
          }
        }
      }
    ]
  }
}
```

## `PREMIUM_HOTSPOT_IMAGE_TEXT`

Module key: `premiumHotspotImageText`. A full-width image with clickable hotspot markers, plus a module headline and body text above the image.

| Field | Type | Required | Bounds |
|---|---|---|---|
| `headline` | TextComponent | yes |  |
| `mainDescription` | ParagraphComponent |  |  |
| `desktopImage` | ImageComponent | yes |  |
| `hotSpots` | array of object | yes | 2–6 items |
| `hotSpots[].imageTextHotSpot` | object | yes |  |
| `hotSpots[].imageTextHotSpot.mobileImage` | ImageComponent | yes |  |
| `hotSpots[].imageTextHotSpot.title` | TextComponent | yes |  |
| `hotSpots[].imageTextHotSpot.xCoordinate` | TextComponent | yes |  |
| `hotSpots[].imageTextHotSpot.yCoordinate` | TextComponent | yes |  |

Amazon's limits for this module:

| Field | Required | Constraint |
|---|---|---|
| `headline` | Required | value: 1–80 chars; not blank |
| `mainDescription` | Optional | textList: 1–2 items; total ≤ 300 chars |
| `desktopImage` | Required | min 1464w × 600h px |
| `hotSpots` (2–6 items) | Required |  |
| `title` | Required | value: 1–50 chars |
| `xCoordinate` | Required | string pixel value (for example, "25") |
| `yCoordinate` | Required | string pixel value (for example, "150") |
| `mobileImage` | Required | min 600w × 450h px |

```json
{
  "contentModuleType": "PREMIUM_HOTSPOT_IMAGE_TEXT",
  "premiumHotspotImageText": {
    "headline": {
      "value": "…"
    },
    "mainDescription": {
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
    "hotSpots": [
      {
        "imageTextHotSpot": {
          "mobileImage": {
            "uploadDestinationId": "<image URL or id>",
            "altText": "…"
          },
          "title": {
            "value": "…"
          },
          "xCoordinate": {
            "value": "…"
          },
          "yCoordinate": {
            "value": "…"
          }
        }
      }
    ]
  }
}
```

## `PREMIUM_FAQ`

Module key: `premiumFaq`. A list of question-and-answer pairs with a configurable background color scheme of light or dark.

| Field | Type | Required | Bounds |
|---|---|---|---|
| `colorType` | DARK \| LIGHT |  |  |
| `faqs` | array of object | yes | 2–5 items |
| `faqs[].faq` | object | yes |  |
| `faqs[].faq.question` | ParagraphComponent | yes |  |
| `faqs[].faq.answer` | ParagraphComponent | yes |  |

Amazon's limits for this module:

| Field | Required | Constraint |
|---|---|---|
| `colorType` | Required | `DARK` \| `LIGHT` |
| `faqs` 2–5 items | Required |  |
| `question` | Required | textList: 1 item; max 120 chars |
| `answer` | Required | textList: 1–5 items; total ≤ 250 chars |

```json
{
  "contentModuleType": "PREMIUM_FAQ",
  "premiumFaq": {
    "colorType": "DARK | LIGHT",
    "faqs": [
      {
        "faq": {
          "question": {
            "textList": [
              {
                "value": "…"
              }
            ]
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

## `PREMIUM_TECH_SPECS`

Module key: `premiumTechSpecs`. A structured list of specification-definition pairs with a headline, for presenting key technical details of your product.

| Field | Type | Required | Bounds |
|---|---|---|---|
| `headline` | TextComponent | yes |  |
| `columnCount` | integer |  | 1–2 |
| `techSpecs` | array of object | yes | 4–16 items |
| `techSpecs[].techSpec` | object | yes |  |
| `techSpecs[].techSpec.specKey` | TextComponent | yes |  |
| `techSpecs[].techSpec.specValue` | TextComponent | yes |  |

Amazon's limits for this module:

| Field | Required | Constraint |
|---|---|---|
| `headline` | Optional | value: max 80 chars |
| `columnCount` | Required | 1 or 2 |
| `techSpecs` (4–16 items) | Required |  |
| `specKey` | Required | value: 1–30 chars |
| `specValue` | Required | value: 1–500 chars |

```json
{
  "contentModuleType": "PREMIUM_TECH_SPECS",
  "premiumTechSpecs": {
    "headline": {
      "value": "…"
    },
    "columnCount": 1,
    "techSpecs": [
      {
        "techSpec": {
          "specKey": {
            "value": "…"
          },
          "specValue": {
            "value": "…"
          }
        }
      }
    ]
  }
}
```

## `PREMIUM_VIDEO_TEXT`

Module key: `premiumVideoText`. A video paired with text containing subheadline, headline, and body text. The video can appear on the left or right of the text block.

| Field | Type | Required | Bounds |
|---|---|---|---|
| `positionType` | LEFT \| RIGHT | yes |  |
| `title` | TextComponent |  |  |
| `headline` | TextComponent | yes |  |
| `description` | ParagraphComponent |  |  |
| `video` | VideoComponent | yes |  |

Amazon's limits for this module:

| Field | Required | Constraint |
|---|---|---|
| `positionType` | Required | `LEFT` \| `RIGHT` |
| `headline` | Required | value: 1–80 chars; not blank |
| `video` | Required | preview image min 800w × 600h px |
| `title` | Optional | value: max 40 chars |
| `description` | Optional | textList: 1–5 items; total ≤ 500 chars |

```json
{
  "contentModuleType": "PREMIUM_VIDEO_TEXT",
  "premiumVideoText": {
    "positionType": "LEFT | RIGHT",
    "title": {
      "value": "…"
    },
    "headline": {
      "value": "…"
    },
    "description": {
      "textList": [
        {
          "value": "…"
        }
      ]
    },
    "video": {
      "videoMediaId": "<media id>",
      "imageMediaId": "<media id>"
    }
  }
}
```

## `PREMIUM_HERO_VIDEO`

Module key: `premiumHeroVideo`. A full-width video with optional headline and body text below.

| Field | Type | Required | Bounds |
|---|---|---|---|
| `headline` | TextComponent |  |  |
| `heroVideo` | VideoComponent | yes |  |
| `footer` | ParagraphComponent |  |  |

Amazon's limits for this module:

| Field | Required | Constraint |
|---|---|---|
| `heroVideo` | Required | preview min 1464w × 600h px; video min 960w × 540h px |
| `headline` | Optional | value: max 80 chars |
| `footer` | Optional | textList: 1–4 items; total ≤ 300 chars |

```json
{
  "contentModuleType": "PREMIUM_HERO_VIDEO",
  "premiumHeroVideo": {
    "headline": {
      "value": "…"
    },
    "heroVideo": {
      "videoMediaId": "<media id>",
      "imageMediaId": "<media id>"
    },
    "footer": {
      "textList": [
        {
          "value": "…"
        }
      ]
    }
  }
}
```

## `PREMIUM_VIDEO_IMAGE_CAROUSEL`

Module key: `premiumVideoImageCarousel`. A carousel of panels, each containing a video or image with its own panel headline, subheadline, and body text. A module headline appears above the carousel.

| Field | Type | Required | Bounds |
|---|---|---|---|
| `headline` | TextComponent |  |  |
| `carouselCards` | array of object | yes | 2–6 items |
| `carouselCards[].videoCarouselPanel` | object | yes |  |
| `carouselCards[].videoCarouselPanel.position` | integer | yes | 1–6 |
| `carouselCards[].videoCarouselPanel.title` | TextComponent |  |  |
| `carouselCards[].videoCarouselPanel.positionType` | LEFT \| RIGHT |  |  |
| `carouselCards[].videoCarouselPanel.subheadline` | TextComponent |  |  |
| `carouselCards[].videoCarouselPanel.description` | ParagraphComponent |  |  |
| `carouselCards[].videoCarouselPanel.desktopImage` | ImageComponent |  |  |
| `carouselCards[].videoCarouselPanel.mobileImage` | ImageComponent |  |  |
| `carouselCards[].videoCarouselPanel.video` | VideoComponent |  |  |

Amazon's limits for this module:

| Field | Required | Constraint |
|---|---|---|
| `headline` | Optional | value: max 80 chars |
| `carouselCards` 2–6 items | Required |  |
| `position` | Required | 1–6; unique per carousel |
| `positionType` | Required | `LEFT` \| `RIGHT` |
| `subheadline` | Required | value: max 80 chars |
| `title` | Optional | value: max 50 chars |
| `description` | Optional | textList: 1–4 items; total ≤ 500 chars |
| `video` | Image or Video | preview image min 800w × 600h px |
| `desktopImage` | Image or Video | min 800w × 600h px |
| `mobileImage` | Image or Video | min 600w × 450h px |

```json
{
  "contentModuleType": "PREMIUM_VIDEO_IMAGE_CAROUSEL",
  "premiumVideoImageCarousel": {
    "headline": {
      "value": "…"
    },
    "carouselCards": [
      {
        "videoCarouselPanel": {
          "position": 1,
          "title": {
            "value": "…"
          },
          "positionType": "LEFT | RIGHT",
          "subheadline": {
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
          },
          "video": {
            "videoMediaId": "<media id>",
            "imageMediaId": "<media id>"
          }
        }
      }
    ]
  }
}
```
