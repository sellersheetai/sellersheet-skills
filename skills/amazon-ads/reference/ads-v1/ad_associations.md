# v1 `ad_associations` - FULL field catalog (generated from Amazon's official OpenAPI specification; do not hand-edit)

Complete leaf-level request-body schema per ad product. `*` after a
field name = required within its object. Enums >15 values: ENUMS.md.

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