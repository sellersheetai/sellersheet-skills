<!-- Generated from Amazon's A+ Content API model (2020-11-01) and its module pages. Do not hand-edit: regenerate. -->

# Standard (Basic) A+ modules (15)

Shapes from the model; `Required` is within its object. Components: README.md.

## `STANDARD_COMPANY_LOGO`

Module key: `standardCompanyLogo`. The standard company logo image.

| Field | Type | Required | Bounds |
|---|---|---|---|
| `companyLogo` | ImageComponent | yes |  |

Amazon's limits for this module:

| Editor field | JSON path | Required | Limit |
|---|---|---|---|
| Image | `companyLogo` | Yes | Minimum image size: 600 x 180 pixels |
| Image alt text | `companyLogo` | Yes | `maxLength`: 100 |

```json
{
  "contentModuleType": "STANDARD_COMPANY_LOGO",
  "standardCompanyLogo": {
    "companyLogo": {
      "uploadDestinationId": "<image URL or id>",
      "altText": "…"
    }
  }
}
```

## `STANDARD_COMPARISON_TABLE`

Module key: `standardComparisonTable`. The standard product comparison table.

| Field | Type | Required | Bounds |
|---|---|---|---|
| `productColumns` | array of object |  | 0–6 items |
| `productColumns[].position` | integer | yes | 1–6 |
| `productColumns[].image` | ImageComponent |  |  |
| `productColumns[].title` | string |  | 1–80 chars |
| `productColumns[].asin` | string |  | ≥10 chars |
| `productColumns[].highlight` | boolean |  |  |
| `productColumns[].metrics` | array of PlainTextItem |  | 0–10 items |
| `metricRowLabels` | array of PlainTextItem |  | 0–10 items |

Amazon's limits for this module:

| Editor field | JSON path | Required | Limit |
|---|---|---|---|
| Metric name | `metricRowLabel` | No | `maxLength`: 100 |
| Title in blocks 1-6 | `productColumns.title` | No | `maxLength`: 80 |
| ASIN in blocks 1-6 | `productColumns.asin` | No | `maxLength`: 10 |
| Highlight column in blocks 1-6 | `productColumns.highlight` | Yes | `true` = Highlighted ; `false` = Not highlighted |
| Image in blocks 1-6 | `productColumns.image` | No | Minimum image size: 150 x 300 pixels |
| Image alt text in blocks 1-6 | `productColumns.image` | No | `maxLength`: 100 |
| Column Position in blocks 1-6 | `productColumns`[].position` | No | `Min` = 1 (first) ; `Max` = 6 (last) |
| Metric text in blocks 1-6 | `productColumns.metric` | No | `maxLength`: 250 |

```json
{
  "contentModuleType": "STANDARD_COMPARISON_TABLE",
  "standardComparisonTable": {
    "productColumns": [
      {
        "position": 1,
        "image": {
          "uploadDestinationId": "<image URL or id>",
          "altText": "…"
        },
        "title": "…",
        "asin": "…",
        "highlight": "true",
        "metrics": [
          {
            "position": 1,
            "value": "…"
          }
        ]
      }
    ],
    "metricRowLabels": [
      {
        "position": 1,
        "value": "…"
      }
    ]
  }
}
```

## `STANDARD_FOUR_IMAGE_TEXT`

Module key: `standardFourImageText`. Four standard images with text, presented across a single row.

| Field | Type | Required | Bounds |
|---|---|---|---|
| `headline` | TextComponent |  |  |
| `block1` | object |  |  |
| `block1.image` | ImageComponent |  |  |
| `block1.headline` | TextComponent |  |  |
| `block1.body` | ParagraphComponent |  |  |
| `block2` | object |  |  |
| `block2.image` | ImageComponent |  |  |
| `block2.headline` | TextComponent |  |  |
| `block2.body` | ParagraphComponent |  |  |
| `block3` | object |  |  |
| `block3.image` | ImageComponent |  |  |
| `block3.headline` | TextComponent |  |  |
| `block3.body` | ParagraphComponent |  |  |
| `block4` | object |  |  |
| `block4.image` | ImageComponent |  |  |
| `block4.headline` | TextComponent |  |  |
| `block4.body` | ParagraphComponent |  |  |

Amazon's limits for this module:

| Editor field | JSON path | Required | Limit |
|---|---|---|---|
| Main headline text | `headline` | No | `maxLength`: 200 |
| Headline text in blocks 1-4 | `block` {1-4}.headline` | No | `maxLength`: 160 |
| Body text in blocks 1-4 | `block` {1-4}.body` | No | `maxLength`: 1000 |
| Image in blocks 1-4 | `block` {1-4}.image` | Yes | Minimum image size: 220 x 200 |
| Image alt text in blocks 1-4 | `block` {1-4}.image` | No | `maxLength`: 100 |

```json
{
  "contentModuleType": "STANDARD_FOUR_IMAGE_TEXT",
  "standardFourImageText": {
    "headline": {
      "value": "…"
    },
    "block1": {
      "image": {
        "uploadDestinationId": "<image URL or id>",
        "altText": "…"
      },
      "headline": {
        "value": "…"
      },
      "body": {
        "textList": [
          {
            "value": "…"
          }
        ]
      }
    },
    "block2": {
      "image": {
        "uploadDestinationId": "<image URL or id>",
        "altText": "…"
      },
      "headline": {
        "value": "…"
      },
      "body": {
        "textList": [
          {
            "value": "…"
          }
        ]
      }
    },
    "block3": {
      "image": {
        "uploadDestinationId": "<image URL or id>",
        "altText": "…"
      },
      "headline": {
        "value": "…"
      },
      "body": {
        "textList": [
          {
            "value": "…"
          }
        ]
      }
    },
    "block4": {
      "image": {
        "uploadDestinationId": "<image URL or id>",
        "altText": "…"
      },
      "headline": {
        "value": "…"
      },
      "body": {
        "textList": [
          {
            "value": "…"
          }
        ]
      }
    }
  }
}
```

## `STANDARD_FOUR_IMAGE_TEXT_QUADRANT`

Module key: `standardFourImageTextQuadrant`. Four standard images with text, presented on a grid of four quadrants.

| Field | Type | Required | Bounds |
|---|---|---|---|
| `block1` | object | yes |  |
| `block1.image` | ImageComponent |  |  |
| `block1.headline` | TextComponent |  |  |
| `block1.body` | ParagraphComponent |  |  |
| `block2` | object | yes |  |
| `block2.image` | ImageComponent |  |  |
| `block2.headline` | TextComponent |  |  |
| `block2.body` | ParagraphComponent |  |  |
| `block3` | object | yes |  |
| `block3.image` | ImageComponent |  |  |
| `block3.headline` | TextComponent |  |  |
| `block3.body` | ParagraphComponent |  |  |
| `block4` | object | yes |  |
| `block4.image` | ImageComponent |  |  |
| `block4.headline` | TextComponent |  |  |
| `block4.body` | ParagraphComponent |  |  |

Amazon's limits for this module:

| Editor field | JSON path | Required | Limit |
|---|---|---|---|
| Image | `block` {1-4}.image` | Yes | Minimum image size: 135 x 135 pixels |
| Image alt text | `block` {1-4}.image` | Yes | `maxLength`: 100 |
| Headline | `block` {1-4}.headline` | Yes | `maxLength`: 160 |
| Body text | `block` {1-4}.body` | Yes | `maxLength`: 1000 |

```json
{
  "contentModuleType": "STANDARD_FOUR_IMAGE_TEXT_QUADRANT",
  "standardFourImageTextQuadrant": {
    "block1": {
      "image": {
        "uploadDestinationId": "<image URL or id>",
        "altText": "…"
      },
      "headline": {
        "value": "…"
      },
      "body": {
        "textList": [
          {
            "value": "…"
          }
        ]
      }
    },
    "block2": {
      "image": {
        "uploadDestinationId": "<image URL or id>",
        "altText": "…"
      },
      "headline": {
        "value": "…"
      },
      "body": {
        "textList": [
          {
            "value": "…"
          }
        ]
      }
    },
    "block3": {
      "image": {
        "uploadDestinationId": "<image URL or id>",
        "altText": "…"
      },
      "headline": {
        "value": "…"
      },
      "body": {
        "textList": [
          {
            "value": "…"
          }
        ]
      }
    },
    "block4": {
      "image": {
        "uploadDestinationId": "<image URL or id>",
        "altText": "…"
      },
      "headline": {
        "value": "…"
      },
      "body": {
        "textList": [
          {
            "value": "…"
          }
        ]
      }
    }
  }
}
```

## `STANDARD_HEADER_IMAGE_TEXT`

Module key: `standardHeaderImageText`. Standard headline text, an image, and body text.

| Field | Type | Required | Bounds |
|---|---|---|---|
| `headline` | TextComponent |  |  |
| `block` | object |  |  |
| `block.image` | ImageComponent |  |  |
| `block.headline` | TextComponent |  |  |
| `block.body` | ParagraphComponent |  |  |

Amazon's limits for this module:

| Editor field | JSON path | Required | Limit |
|---|---|---|---|
| Headline | `headline` | No | `maxLength`: 150 |
| Subheadline | `block.headline` | No | `maxLength`: 150 |
| Body text | `block.body` | No | `maxLength`: 6000 |
| Image | `block.image` | Yes | Minimum image size: 970 x 600 pixels |
| Image alt text | `block.image` | No | `maxLength`: 100 |

```json
{
  "contentModuleType": "STANDARD_HEADER_IMAGE_TEXT",
  "standardHeaderImageText": {
    "headline": {
      "value": "…"
    },
    "block": {
      "image": {
        "uploadDestinationId": "<image URL or id>",
        "altText": "…"
      },
      "headline": {
        "value": "…"
      },
      "body": {
        "textList": [
          {
            "value": "…"
          }
        ]
      }
    }
  }
}
```

## `STANDARD_IMAGE_SIDEBAR`

Module key: `standardImageSidebar`. Two images, two paragraphs, and two bulleted lists. One image is smaller and displayed in the sidebar.

| Field | Type | Required | Bounds |
|---|---|---|---|
| `headline` | TextComponent |  |  |
| `imageCaptionBlock` | object |  |  |
| `imageCaptionBlock.image` | ImageComponent |  |  |
| `imageCaptionBlock.caption` | TextComponent |  |  |
| `descriptionTextBlock` | object |  |  |
| `descriptionTextBlock.headline` | TextComponent |  |  |
| `descriptionTextBlock.body` | ParagraphComponent |  |  |
| `descriptionListBlock` | object |  |  |
| `descriptionListBlock.textList` | array of TextItem | yes | 0–8 items |
| `sidebarImageTextBlock` | object |  |  |
| `sidebarImageTextBlock.image` | ImageComponent |  |  |
| `sidebarImageTextBlock.headline` | TextComponent |  |  |
| `sidebarImageTextBlock.body` | ParagraphComponent |  |  |
| `sidebarListBlock` | object |  |  |
| `sidebarListBlock.textList` | array of TextItem | yes | 0–8 items |

Amazon's limits for this module:

| Editor field | JSON path | Required | Limit |
|---|---|---|---|
| Main headline text | `headline` | Yes | `maxLength`: 160 |
| Main sub-headline text | `descriptionTextBlock.headline` | Yes | `maxLength`: 200 |
| Main body text | `descriptionTextBlock.body` | Yes | `maxLength`: 500 |
| Main bullet point | `descriptionListBlock.textList` | No | `maxLength`: 200 |
| Main image | `imageCaptionBlock.image` | Yes | Minimum image size: 300 x 400 pixels |
| Main image alt text | `imageCaptionBlock.image` | Yes | `maxLength`: 100 |
| Main image caption text | `imageCaptionBlock.caption` | Yes | `maxLength`: 200 |
| Sidebar headline | `sidebarImageTextBlock.headline` | No | `maxLength`: 200 |
| Sidebar body text | `sidebarImageTextBlock.body` | No | `maxLength`: 500 |
| Sidebar bullet point | `sidebarListBlock.textList` | No | `maxLength`: 200 |
| Sidebar image | `sidebarImageTextBlock.image` | Yes | Minimum image size: 300 x 175 pixels |
| Sidebar image alt text | `sidebarImageTextBlock.image` | Yes | `maxLength`: 100 |

```json
{
  "contentModuleType": "STANDARD_IMAGE_SIDEBAR",
  "standardImageSidebar": {
    "headline": {
      "value": "…"
    },
    "imageCaptionBlock": {
      "image": {
        "uploadDestinationId": "<image URL or id>",
        "altText": "…"
      },
      "caption": {
        "value": "…"
      }
    },
    "descriptionTextBlock": {
      "headline": {
        "value": "…"
      },
      "body": {
        "textList": [
          {
            "value": "…"
          }
        ]
      }
    },
    "descriptionListBlock": {
      "textList": [
        {
          "position": 1,
          "text": {
            "value": "…"
          }
        }
      ]
    },
    "sidebarImageTextBlock": {
      "image": {
        "uploadDestinationId": "<image URL or id>",
        "altText": "…"
      },
      "headline": {
        "value": "…"
      },
      "body": {
        "textList": [
          {
            "value": "…"
          }
        ]
      }
    },
    "sidebarListBlock": {
      "textList": [
        {
          "position": 1,
          "text": {
            "value": "…"
          }
        }
      ]
    }
  }
}
```

## `STANDARD_IMAGE_TEXT_OVERLAY`

Module key: `standardImageTextOverlay`. A standard background image with a floating text box.

| Field | Type | Required | Bounds |
|---|---|---|---|
| `overlayColorType` | DARK \| LIGHT | yes |  |
| `block` | object |  |  |
| `block.image` | ImageComponent |  |  |
| `block.headline` | TextComponent |  |  |
| `block.body` | ParagraphComponent |  |  |

Amazon's limits for this module:

| Editor field | JSON path | Required | Limit |
|---|---|---|---|
| Overlay color type | `overlayColorType` | Yes | DARK - Dark, semi-opaque background (as in this example) ; LIGHT - White, semi-opaque background |
| Image | `block.image` | Yes | Minimum image size: 970 x 300 pixels |
| Image alt text | `block.image` | Yes | `maxLength`: 100 |
| Headline text | `block.headline` | No | `maxLength`: 70 |
| Body text | `block.body` | No | `maxLength`: 300 |

```json
{
  "contentModuleType": "STANDARD_IMAGE_TEXT_OVERLAY",
  "standardImageTextOverlay": {
    "overlayColorType": "DARK | LIGHT",
    "block": {
      "image": {
        "uploadDestinationId": "<image URL or id>",
        "altText": "…"
      },
      "headline": {
        "value": "…"
      },
      "body": {
        "textList": [
          {
            "value": "…"
          }
        ]
      }
    }
  }
}
```

## `STANDARD_MULTIPLE_IMAGE_TEXT`

Module key: `standardMultipleImageText`. Standard images with text, presented one at a time. The user clicks on thumbnails to view each block.

| Field | Type | Required | Bounds |
|---|---|---|---|
| `blocks` | array of object |  |  |
| `blocks[].block` | object |  |  |
| `blocks[].block.image` | ImageComponent |  |  |
| `blocks[].block.headline` | TextComponent |  |  |
| `blocks[].block.body` | ParagraphComponent |  |  |
| `blocks[].caption` | TextComponent |  |  |

Amazon's limits for this module:

| Editor field | JSON path | Required | Limit |
|---|---|---|---|
| Highlight Image (Note: Thumbnail generated automatically from highlight image) | `blocks.image` | Yes | Minimum image size: 300 x 300 pixels |
| Image alt text | `blocks.image` | No | `maxLength`: 100 |
| Headline Text | `blocks.headline` | No | `maxLength`: 160 |
| Description Text | `blocks.body` | No | `maxLength`: 1000 |
| Caption Text | `blocks.caption` | No | `maxLength`: 200 |

```json
{
  "contentModuleType": "STANDARD_MULTIPLE_IMAGE_TEXT",
  "standardMultipleImageText": {
    "blocks": [
      {
        "block": {
          "image": {
            "uploadDestinationId": "<image URL or id>",
            "altText": "…"
          },
          "headline": {
            "value": "…"
          },
          "body": {
            "textList": [
              {
                "value": "…"
              }
            ]
          }
        },
        "caption": {
          "value": "…"
        }
      }
    ]
  }
}
```

## `STANDARD_PRODUCT_DESCRIPTION`

Module key: `standardProductDescription`. Standard product description text.

| Field | Type | Required | Bounds |
|---|---|---|---|
| `body` | ParagraphComponent | yes |  |

Amazon's limits for this module:

| Editor field | JSON path | Required | Limit |
|---|---|---|---|
| Body text | `body` | No | `maxLength`: 6000 |

```json
{
  "contentModuleType": "STANDARD_PRODUCT_DESCRIPTION",
  "standardProductDescription": {
    "body": {
      "textList": [
        {
          "value": "…"
        }
      ]
    }
  }
}
```

## `STANDARD_SINGLE_IMAGE_HIGHLIGHTS`

Module key: `standardSingleImageHighlights`. A standard image with several paragraphs and a bulleted list.

| Field | Type | Required | Bounds |
|---|---|---|---|
| `image` | ImageComponent |  |  |
| `headline` | TextComponent |  |  |
| `textBlock1` | object |  |  |
| `textBlock1.headline` | TextComponent |  |  |
| `textBlock1.body` | ParagraphComponent |  |  |
| `textBlock2` | object |  |  |
| `textBlock2.headline` | TextComponent |  |  |
| `textBlock2.body` | ParagraphComponent |  |  |
| `textBlock3` | object |  |  |
| `textBlock3.headline` | TextComponent |  |  |
| `textBlock3.body` | ParagraphComponent |  |  |
| `bulletedListBlock` | object |  |  |
| `bulletedListBlock.headline` | TextComponent |  |  |
| `bulletedListBlock.block` | object |  |  |
| `bulletedListBlock.block.textList` | array of TextItem | yes | 0–8 items |

Amazon's limits for this module:

| Editor field | JSON path | Required | Limit |
|---|---|---|---|
| Main image | `image` | Yes | Minimum image size: 300 x 300 pixels |
| Image alt text | `image` | Yes | `maxLength`: 100 |
| Headline description | `headline` | No | `maxLength`: 160 |
| Subheadline 1 description | `textBlock1.headline` | No | `maxLength`: 200 |
| Body text 1 description | `textBlock1.body` | No | `maxLength`: 1000 |
| Subheadline 2 description | `textBlock2.headline` | Yes | `maxLength`: 200 |
| Body text 2 description | `textBlock2.body` | Yes | `maxLength`: 400 |
| Subheadline 3 description | `textBlock3.headline` | Yes | `maxLength`: 200 |
| Body text 3 description | `textBlock3.body` | Yes | `maxLength`: 400 |
| Headline tech specs | `bulletedListBlock.headline` | Yes | `maxLength`: 160 |
| Bullet Point tech specs | `bulletedListBlock.textList` | Yes | `maxLength`: 100 ; `Min position` = 1 (first); `Max position` = 8 (last) |

```json
{
  "contentModuleType": "STANDARD_SINGLE_IMAGE_HIGHLIGHTS",
  "standardSingleImageHighlights": {
    "image": {
      "uploadDestinationId": "<image URL or id>",
      "altText": "…"
    },
    "headline": {
      "value": "…"
    },
    "textBlock1": {
      "headline": {
        "value": "…"
      },
      "body": {
        "textList": [
          {
            "value": "…"
          }
        ]
      }
    },
    "textBlock2": {
      "headline": {
        "value": "…"
      },
      "body": {
        "textList": [
          {
            "value": "…"
          }
        ]
      }
    },
    "textBlock3": {
      "headline": {
        "value": "…"
      },
      "body": {
        "textList": [
          {
            "value": "…"
          }
        ]
      }
    },
    "bulletedListBlock": {
      "headline": {
        "value": "…"
      },
      "block": {
        "textList": [
          {
            "position": 1,
            "text": {
              "value": "…"
            }
          }
        ]
      }
    }
  }
}
```

## `STANDARD_SINGLE_IMAGE_SPECS_DETAIL`

Module key: `standardSingleImageSpecsDetail`. A standard image with paragraphs and a bulleted list, and extra space for technical details.

| Field | Type | Required | Bounds |
|---|---|---|---|
| `headline` | TextComponent |  |  |
| `image` | ImageComponent |  |  |
| `descriptionHeadline` | TextComponent |  |  |
| `descriptionBlock1` | object |  |  |
| `descriptionBlock1.headline` | TextComponent |  |  |
| `descriptionBlock1.body` | ParagraphComponent |  |  |
| `descriptionBlock2` | object |  |  |
| `descriptionBlock2.headline` | TextComponent |  |  |
| `descriptionBlock2.body` | ParagraphComponent |  |  |
| `specificationHeadline` | TextComponent |  |  |
| `specificationListBlock` | object |  |  |
| `specificationListBlock.headline` | TextComponent |  |  |
| `specificationListBlock.block` | object |  |  |
| `specificationListBlock.block.textList` | array of TextItem | yes | 0–8 items |
| `specificationTextBlock` | object |  |  |
| `specificationTextBlock.headline` | TextComponent |  |  |
| `specificationTextBlock.body` | ParagraphComponent |  |  |

Amazon's limits for this module:

| Editor field | JSON path | Required | Limit |
|---|---|---|---|
| Headline text | `headline` | No | `maxLength`: 200 |
| Headline description | `descriptionHeadline` | No | `maxLength`: 160 |
| Main image | `image` | Yes | Minimum image size: 300 x 300 pixels |
| Main image alt text | `image` | No | `maxLength`: 100 |
| Subheadline description | `descriptionBlock.headline` | No | `maxLength`: 200 |
| Body text description | `descriptionBlock.body` | Yes | `maxLength`: 400 |
| Headline tech specs | `specificationHeadline` | No | `maxLength`: 160 |
| Subheadline tech specs | `specificationListBlock.headline` | No | `maxLength`: 200 |
| Bullet point tech specs | `specificationListBlock.textList` | No | `maxLength`: 200 ; `Min position` = 1 (first); `Max position` = 8 (last) |
| Subheadline tech specs | `specificationTextBlock.headline` | No | `maxLength`: 200 |
| Body text tech specs | `specificationTextBlock.body` | Yes | `maxLength`: 1000 |

```json
{
  "contentModuleType": "STANDARD_SINGLE_IMAGE_SPECS_DETAIL",
  "standardSingleImageSpecsDetail": {
    "headline": {
      "value": "…"
    },
    "image": {
      "uploadDestinationId": "<image URL or id>",
      "altText": "…"
    },
    "descriptionHeadline": {
      "value": "…"
    },
    "descriptionBlock1": {
      "headline": {
        "value": "…"
      },
      "body": {
        "textList": [
          {
            "value": "…"
          }
        ]
      }
    },
    "descriptionBlock2": {
      "headline": {
        "value": "…"
      },
      "body": {
        "textList": [
          {
            "value": "…"
          }
        ]
      }
    },
    "specificationHeadline": {
      "value": "…"
    },
    "specificationListBlock": {
      "headline": {
        "value": "…"
      },
      "block": {
        "textList": [
          {
            "position": 1,
            "text": {
              "value": "…"
            }
          }
        ]
      }
    },
    "specificationTextBlock": {
      "headline": {
        "value": "…"
      },
      "body": {
        "textList": [
          {
            "value": "…"
          }
        ]
      }
    }
  }
}
```

## `STANDARD_SINGLE_SIDE_IMAGE`

Module key: `standardSingleSideImage`. A standard headline and body text with an image on the side.

| Field | Type | Required | Bounds |
|---|---|---|---|
| `imagePositionType` | LEFT \| RIGHT | yes |  |
| `block` | object |  |  |
| `block.image` | ImageComponent |  |  |
| `block.headline` | TextComponent |  |  |
| `block.body` | ParagraphComponent |  |  |

Amazon's limits for this module:

| Editor field | JSON path | Required | Limit |
|---|---|---|---|
| Image position | `imagePositionType` | Yes | `LEFT` (image is on left); `RIGHT` (image is on right) |
| Main headline text | `block.headline` | No | `maxLength`: 160 |
| Main body text | `block.body` | No | `maxLength`: 1000 |
| Main Image | `block.image` | Yes | Minimum image size: 300 x 300 pixels |
| Main image alt text | `block.image` | Yes | `maxLength`: 100 |

```json
{
  "contentModuleType": "STANDARD_SINGLE_SIDE_IMAGE",
  "standardSingleSideImage": {
    "imagePositionType": "LEFT | RIGHT",
    "block": {
      "image": {
        "uploadDestinationId": "<image URL or id>",
        "altText": "…"
      },
      "headline": {
        "value": "…"
      },
      "body": {
        "textList": [
          {
            "value": "…"
          }
        ]
      }
    }
  }
}
```

## `STANDARD_TECH_SPECS`

Module key: `standardTechSpecs`. The standard table of technical feature names and definitions.

| Field | Type | Required | Bounds |
|---|---|---|---|
| `headline` | TextComponent |  |  |
| `specificationList` | array of object | yes | 4–16 items |
| `specificationList[].label` | TextComponent |  |  |
| `specificationList[].description` | TextComponent |  |  |
| `tableCount` | integer |  | 1–2 |

Amazon's limits for this module:

| Editor field | JSON path | Required | Limit |
|---|---|---|---|
| Main headline | `headline` | Yes | `maxLength`: 80 |
| Spec Name (Min 4, Max 16) | `specificationList.label` | Yes | `maxLength`: 30 |
| Spec definition (Min 4, Max 16) | `specificationList.description` | Yes | `maxLength`: 500 |
| Table count (display specs in one table or two tables side by side) | `tableCount` | Yes | `1` = one table; `2` = two tables side by side |

```json
{
  "contentModuleType": "STANDARD_TECH_SPECS",
  "standardTechSpecs": {
    "headline": {
      "value": "…"
    },
    "specificationList": [
      {
        "label": {
          "value": "…"
        },
        "description": {
          "value": "…"
        }
      }
    ],
    "tableCount": 1
  }
}
```

## `STANDARD_TEXT`

Module key: `standardText`. A standard headline and body text.

| Field | Type | Required | Bounds |
|---|---|---|---|
| `headline` | TextComponent |  |  |
| `body` | ParagraphComponent | yes |  |

Amazon's limits for this module:

| Editor field | JSON path | Required | Limit |
|---|---|---|---|
| Headline text | `headline` | No | `maxLength`: 160 |
| Body text | `body` | No | `maxLength`: 5000 |

```json
{
  "contentModuleType": "STANDARD_TEXT",
  "standardText": {
    "headline": {
      "value": "…"
    },
    "body": {
      "textList": [
        {
          "value": "…"
        }
      ]
    }
  }
}
```

## `STANDARD_THREE_IMAGE_TEXT`

Module key: `standardThreeImageText`. Three standard images with text, presented across a single row.

| Field | Type | Required | Bounds |
|---|---|---|---|
| `headline` | TextComponent |  |  |
| `block1` | object |  |  |
| `block1.image` | ImageComponent |  |  |
| `block1.headline` | TextComponent |  |  |
| `block1.body` | ParagraphComponent |  |  |
| `block2` | object |  |  |
| `block2.image` | ImageComponent |  |  |
| `block2.headline` | TextComponent |  |  |
| `block2.body` | ParagraphComponent |  |  |
| `block3` | object |  |  |
| `block3.image` | ImageComponent |  |  |
| `block3.headline` | TextComponent |  |  |
| `block3.body` | ParagraphComponent |  |  |

Amazon's limits for this module:

| Editor field | JSON path | Required | Limit |
|---|---|---|---|
| Main headline Text | `headline` | Yes | `maxLength`: 200 |
| Headline | `block` {1-3}.headline` | Yes | `maxLength`: 160 |
| Image | `block` {1-3}.image` | Yes | Minimum image size: 300 x 300 pixels |
| Image alt text | `block` {1-3}.image` | Yes | `maxLength`: 100 |
| Body text | `block` {1-3}.body` | Yes | `maxLength`: 1000 |

```json
{
  "contentModuleType": "STANDARD_THREE_IMAGE_TEXT",
  "standardThreeImageText": {
    "headline": {
      "value": "…"
    },
    "block1": {
      "image": {
        "uploadDestinationId": "<image URL or id>",
        "altText": "…"
      },
      "headline": {
        "value": "…"
      },
      "body": {
        "textList": [
          {
            "value": "…"
          }
        ]
      }
    },
    "block2": {
      "image": {
        "uploadDestinationId": "<image URL or id>",
        "altText": "…"
      },
      "headline": {
        "value": "…"
      },
      "body": {
        "textList": [
          {
            "value": "…"
          }
        ]
      }
    },
    "block3": {
      "image": {
        "uploadDestinationId": "<image URL or id>",
        "altText": "…"
      },
      "headline": {
        "value": "…"
      },
      "body": {
        "textList": [
          {
            "value": "…"
          }
        ]
      }
    }
  }
}
```
