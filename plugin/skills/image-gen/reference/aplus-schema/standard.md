<!-- Generated from Amazon's A+ Content API model (2020-11-01) and its module pages. Do not hand-edit: regenerate. -->

# Standard (Basic) A+ modules (15)

Shapes from the model; `Required` is within its object. Components: README.md.

## `STANDARD_COMPANY_LOGO`

Module key: `standardCompanyLogo`. The standard company logo image.

| Field | Type | Required | Bounds |
|---|---|---|---|
| `companyLogo` | ImageComponent | yes |  |

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
