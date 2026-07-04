# v1 `ad_associations` - FULL field catalog (generated; do not hand-edit)

Complete leaf-level request-body schema per ad product, extracted
from the vendored Amazon OpenAPI specs. `*` after a field name =
required within its object. Enums >15 values: V1-GA-ENUMS.md.

Regenerate: `python3 docs/ads-api-v1/tools/gen_field_catalog.py`


## ALL - QUERY

- `adAssociationIdFilter`: {include*: array<string>}
- `adGroupIdFilter`: {include*: array<string>}
- `adIdFilter`: {include*: array<string>}
- `maxResults`: integer
- `nextToken`: string

## ALL - CREATE

- `adAssociations[]`: array of objects REQUIRED
- `adAssociations[].adGroupId` **REQUIRED**: string
- `adAssociations[].adId` **REQUIRED**: string
- `adAssociations[].endDateTime`: string
- `adAssociations[].startDateTime`: string
- `adAssociations[].state` **REQUIRED**: enum: ENABLED | PAUSED
- `adAssociations[].weight`: integer

## ALL - UPDATE

- `adAssociations[]`: array of objects REQUIRED
- `adAssociations[].adAssociationId` **REQUIRED**: string
- `adAssociations[].endDateTime`: string
- `adAssociations[].startDateTime`: string
- `adAssociations[].state`: enum: ENABLED | PAUSED
- `adAssociations[].weight`: integer

## ALL - DELETE

- `adAssociationIds` **REQUIRED**: array<string>

## AMAZON_DSP - QUERY

- `adAssociationIdFilter`: {include*: array<string>}
- `adGroupIdFilter`: {include*: array<string>}
- `adIdFilter`: {include*: array<string>}
- `maxResults`: integer
- `nextToken`: string

## AMAZON_DSP - CREATE

- `adAssociations[]`: array of objects REQUIRED
- `adAssociations[].adGroupId` **REQUIRED**: string
- `adAssociations[].adId` **REQUIRED**: string
- `adAssociations[].endDateTime`: string
- `adAssociations[].startDateTime`: string
- `adAssociations[].state` **REQUIRED**: enum: ENABLED | PAUSED
- `adAssociations[].weight`: integer

## AMAZON_DSP - UPDATE

- `adAssociations[]`: array of objects REQUIRED
- `adAssociations[].adAssociationId` **REQUIRED**: string
- `adAssociations[].endDateTime`: string
- `adAssociations[].startDateTime`: string
- `adAssociations[].state`: enum: ENABLED | PAUSED
- `adAssociations[].weight`: integer

## AMAZON_DSP - DELETE

- `adAssociationIds` **REQUIRED**: array<string>
