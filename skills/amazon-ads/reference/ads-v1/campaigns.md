# v1 `campaigns` - FULL field catalog (generated; do not hand-edit)

Complete leaf-level request-body schema per ad product, extracted
from the vendored Amazon OpenAPI specs. `*` after a field name =
required within its object. Enums >15 values: V1-GA-ENUMS.md.

Regenerate: `python3 docs/ads-api-v1/tools/gen_field_catalog.py`


## ALL - QUERY

- `adProductFilter` **REQUIRED**: {include*: array<enum: AMAZON_DSP | SPONSORED_BRANDS | SPONSORED_DISPLAY | SPONSORED_PRODUCTS | SPONSORED_TELEVISION>}
- `campaignIdFilter`: {include*: array<string>}
- `goalFilter`: {include*: array<enum: AWARENESS | CONSIDERATION | CONVERSIONS>}
- `marketplaceScopeFilter`: {include*: array<enum: GLOBAL | SINGLE_MARKETPLACE>}
- `maxResults`: integer
- `nameFilter`: {include*: array<string>, queryTermMatchType*: enum: BROAD_MATCH | EXACT_MATCH}
- `nextToken`: string
- `portfolioIdFilter`: {include*: array<string>}
- `stateFilter`: {include*: array<enum: ARCHIVED | ENABLED | PAUSED>}

## ALL - CREATE

- `campaigns[]`: array of objects REQUIRED
- `campaigns[].adProduct` **REQUIRED**: enum: AMAZON_DSP | SPONSORED_BRANDS | SPONSORED_DISPLAY | SPONSORED_PRODUCTS | SPONSORED_TELEVISION
- `campaigns[].adomains`: array<string>
- `campaigns[].autoCreationSettings`: {autoCreateTargets: boolean, autoManageCampaign: boolean}
- `campaigns[].brandId`: string
- `campaigns[].budgets`: array<{budgetType*: enum: MONETARY, budgetValue*: oneOf: monetaryBudgetValue{monetaryBudgetValue: {marketplaceSettings: array<{marketplace*: enum (23 values - see V1-GA-ENUMS.md), monetaryBudget*: object}>, monetaryBudget: {value*: number}}}, recurrenceTimePeriod*: enum: DAILY | LIFETIME | MONTHLY}>
- `campaigns[].costType`: enum: CPC | CPM | FIXED_PRICE | VCPM
- `campaigns[].countries`: array<enum (75 values - see V1-GA-ENUMS.md)>
- `campaigns[].endDateTime`: string
- `campaigns[].fees`: array<{feeType*: enum: AGENCY, feeValue*: number, feeValueType*: enum: PERCENTAGE_OF_BUDGET}>
- `campaigns[].flights`: array<{budget*: {budgetType*: enum: MONETARY, budgetValue*: oneOf: monetaryBudgetValue{monetaryBudgetValue: {marketplaceSettings: array<object>, monetaryBudget: {value*: number}}}}, endDateTime*: string, flightId: string, name: string, startDateTime*: string}>
- `campaigns[].frequencies`: array<{eventMaxCount*: integer, frequencyTargetingSetting*: enum: HOUSEHOLD | USER, timeCount*: integer, timeUnit*: enum: DAYS | HOURS | MINUTES}>
- `campaigns[].marketplaceConfigurations`: array<{marketplace*: enum (23 values - see V1-GA-ENUMS.md), overrides*: {endDateTime: string, name: string, optimizations: {bidSettings: {bidAdjustments: {audienceBidAdjustments: array<object>, creativeBidAdjustments: array<object>, placementBidAdjustments: array<object>, shopperSegmentBidAdjustments: array<object>}, bidStrategy: enum: MANUAL | NEW_TO_BRAND | PRIORITIZE_KPI_TARGET | RULE_BASED | SALES_DOWN_ONLY | SALES_UP_AND_DOWN | SPEND_BUDGET_IN_FULL | USE_CAMPAIGN_STRATEGY}, budgetSettings: {budgetAllocation: enum: AUTO | MANUAL, flightBudgetRolloverStrategy: enum: CUMULATIVE_BUDGET_ROLLOVER | NO_ROLLOVER | PRIOR_BUDGET_ROLLOVER, offAmazonBudgetControlStrategy: enum: MAXIMIZE_REACH | MINIMIZE_SPEND}, goalSettings: {kpi*: enum (32 values - see V1-GA-ENUMS.md), kpiValue: number}, primaryInventoryTypes: array<enum: AUDIO | DISPLAY | VIDEO_OLV | VIDEO_STV>}, startDateTime: string, state: enum: ARCHIVED | ENABLED | PAUSED, tags: array<{key*: string, value*: string}>}}>
- `campaigns[].marketplaceScope`: enum: GLOBAL | SINGLE_MARKETPLACE
- `campaigns[].marketplaces`: array<enum (23 values - see V1-GA-ENUMS.md)>
- `campaigns[].name` **REQUIRED**: string
- `campaigns[].optimizations`: {bidSettings: {bidAdjustments: {audienceBidAdjustments: array<{audienceId*: string, percentage*: integer}>, creativeBidAdjustments: array<{creativeType: enum: SPOTLIGHT, percentage*: integer}>, placementBidAdjustments: array<{percentage*: integer, placement*: enum: HOME_PAGE | PRODUCT_PAGE | REST_OF_SEARCH | SITE_AMAZON_BUSINESS | TOP_OF_SEARCH}>, shopperSegmentBidAdjustments: array<object>}, bidStrategy: enum: MANUAL | NEW_TO_BRAND | PRIORITIZE_KPI_TARGET | RULE_BASED | SALES_DOWN_ONLY | SALES_UP_AND_DOWN | SPEND_BUDGET_IN_FULL | USE_CAMPAIGN_STRATEGY}, budgetSettings: {budgetAllocation: enum: AUTO | MANUAL, flightBudgetRolloverStrategy: enum: CUMULATIVE_BUDGET_ROLLOVER | NO_ROLLOVER | PRIOR_BUDGET_ROLLOVER, offAmazonBudgetControlStrategy: enum: MAXIMIZE_REACH | MINIMIZE_SPEND}, goalSettings: {kpi*: enum (32 values - see V1-GA-ENUMS.md), kpiValue: number}, primaryInventoryTypes: array<enum: AUDIO | DISPLAY | VIDEO_OLV | VIDEO_STV>}
- `campaigns[].portfolioId`: string
- `campaigns[].purchaseOrderNumber`: string
- `campaigns[].salesChannel`: enum: AMAZON | OFF_AMAZON
- `campaigns[].siteRestrictions`: array<enum: AMAZON_BUSINESS | AMAZON_HAUL>
- `campaigns[].skanAppId`: string
- `campaigns[].startDateTime`: string
- `campaigns[].state` **REQUIRED**: enum: ENABLED | PAUSED
- `campaigns[].tags`: array<{key*: string, value*: string}>
- `campaigns[].targetedPGDealId`: string

## ALL - UPDATE

- `campaigns[]`: array of objects REQUIRED
- `campaigns[].adProduct`: enum: AMAZON_DSP | SPONSORED_BRANDS | SPONSORED_DISPLAY | SPONSORED_PRODUCTS | SPONSORED_TELEVISION
- `campaigns[].adomains`: array<string>
- `campaigns[].budgets`: array<{budgetType*: enum: MONETARY, budgetValue*: oneOf: monetaryBudgetValue{monetaryBudgetValue: {marketplaceSettings: array<{marketplace*: enum (23 values - see V1-GA-ENUMS.md), monetaryBudget*: object}>, monetaryBudget: {value*: number}}}, recurrenceTimePeriod*: enum: DAILY | LIFETIME | MONTHLY}>
- `campaigns[].campaignId` **REQUIRED**: string
- `campaigns[].costType`: enum: CPC | CPM | FIXED_PRICE | VCPM
- `campaigns[].countries`: array<enum (75 values - see V1-GA-ENUMS.md)>
- `campaigns[].endDateTime`: string
- `campaigns[].fees`: array<{feeType*: enum: AGENCY, feeValue*: number, feeValueType*: enum: PERCENTAGE_OF_BUDGET}>
- `campaigns[].flights`: array<{budget*: {budgetType*: enum: MONETARY, budgetValue*: oneOf: monetaryBudgetValue{monetaryBudgetValue: {marketplaceSettings: array<object>, monetaryBudget: {value*: number}}}}, endDateTime*: string, flightId: string, name: string, startDateTime*: string}>
- `campaigns[].frequencies`: array<{eventMaxCount*: integer, frequencyTargetingSetting*: enum: HOUSEHOLD | USER, timeCount*: integer, timeUnit*: enum: DAYS | HOURS | MINUTES}>
- `campaigns[].marketplaceConfigurations`: array<{marketplace*: enum (23 values - see V1-GA-ENUMS.md), overrides*: {endDateTime: string, name: string, optimizations: {bidSettings: {bidAdjustments: {audienceBidAdjustments: array<object>, creativeBidAdjustments: array<object>, placementBidAdjustments: array<object>, shopperSegmentBidAdjustments: array<object>}, bidStrategy: enum: MANUAL | NEW_TO_BRAND | PRIORITIZE_KPI_TARGET | RULE_BASED | SALES_DOWN_ONLY | SALES_UP_AND_DOWN | SPEND_BUDGET_IN_FULL | USE_CAMPAIGN_STRATEGY}, budgetSettings: {budgetAllocation: enum: AUTO | MANUAL, flightBudgetRolloverStrategy: enum: CUMULATIVE_BUDGET_ROLLOVER | NO_ROLLOVER | PRIOR_BUDGET_ROLLOVER, offAmazonBudgetControlStrategy: enum: MAXIMIZE_REACH | MINIMIZE_SPEND}, goalSettings: {kpi*: enum (32 values - see V1-GA-ENUMS.md), kpiValue: number}, primaryInventoryTypes: array<enum: AUDIO | DISPLAY | VIDEO_OLV | VIDEO_STV>}, startDateTime: string, state: enum: ARCHIVED | ENABLED | PAUSED, tags: array<{key*: string, value*: string}>}}>
- `campaigns[].marketplaces`: array<enum (23 values - see V1-GA-ENUMS.md)>
- `campaigns[].name`: string
- `campaigns[].optimizations`: {bidSettings: {bidAdjustments: {audienceBidAdjustments: array<{audienceId*: string, percentage*: integer}>, creativeBidAdjustments: array<{creativeType: enum: SPOTLIGHT, percentage*: integer}>, placementBidAdjustments: array<{percentage*: integer, placement*: enum: HOME_PAGE | PRODUCT_PAGE | REST_OF_SEARCH | SITE_AMAZON_BUSINESS | TOP_OF_SEARCH}>, shopperSegmentBidAdjustments: array<object>}, bidStrategy: enum: MANUAL | NEW_TO_BRAND | PRIORITIZE_KPI_TARGET | RULE_BASED | SALES_DOWN_ONLY | SALES_UP_AND_DOWN | SPEND_BUDGET_IN_FULL | USE_CAMPAIGN_STRATEGY}, budgetSettings: {budgetAllocation: enum: AUTO | MANUAL, flightBudgetRolloverStrategy: enum: CUMULATIVE_BUDGET_ROLLOVER | NO_ROLLOVER | PRIOR_BUDGET_ROLLOVER, offAmazonBudgetControlStrategy: enum: MAXIMIZE_REACH | MINIMIZE_SPEND}, goalSettings: {kpi: enum (32 values - see V1-GA-ENUMS.md), kpiValue: number}, primaryInventoryTypes: array<enum: AUDIO | DISPLAY | VIDEO_OLV | VIDEO_STV>}
- `campaigns[].portfolioId`: string
- `campaigns[].purchaseOrderNumber`: string
- `campaigns[].siteRestrictions`: array<enum: AMAZON_BUSINESS | AMAZON_HAUL>
- `campaigns[].skanAppId`: string
- `campaigns[].startDateTime`: string
- `campaigns[].state`: enum: ENABLED | PAUSED
- `campaigns[].tags`: array<{key*: string, value*: string}>
- `campaigns[].targetedPGDealId`: string

## ALL - DELETE

- `campaignIds` **REQUIRED**: array<string>

## SPONSORED_PRODUCTS - QUERY

- `adProductFilter` **REQUIRED**: {include*: array<enum: SPONSORED_PRODUCTS>}
- `campaignIdFilter`: {include*: array<string>}
- `maxResults`: integer
- `nameFilter`: {include*: array<string>, queryTermMatchType*: enum: BROAD_MATCH | EXACT_MATCH}
- `nextToken`: string
- `portfolioIdFilter`: {include*: array<string>}
- `stateFilter`: {include*: array<enum: ARCHIVED | ENABLED | PAUSED>}

## SPONSORED_PRODUCTS - CREATE

- `campaigns[]`: array of objects REQUIRED
- `campaigns[].adProduct` **REQUIRED**: enum: SPONSORED_PRODUCTS
- `campaigns[].autoCreationSettings` **REQUIRED**: {autoCreateTargets*: boolean, autoManageCampaign: boolean}
- `campaigns[].budgets` **REQUIRED**: array<{budgetType*: enum: MONETARY, budgetValue*: oneOf: monetaryBudgetValue{monetaryBudgetValue: {monetaryBudget*: {value*: number}}}, recurrenceTimePeriod*: enum: DAILY}>
- `campaigns[].countries`: array<enum (23 values - see V1-GA-ENUMS.md)>
- `campaigns[].endDateTime`: string
- `campaigns[].marketplaceScope` **REQUIRED**: enum: SINGLE_MARKETPLACE
- `campaigns[].marketplaces`: array<enum (23 values - see V1-GA-ENUMS.md)>
- `campaigns[].name` **REQUIRED**: string
- `campaigns[].optimizations`: {bidSettings: {bidAdjustments: {audienceBidAdjustments: array<{audienceId*: string, percentage*: integer}>, creativeBidAdjustments: array<{creativeType: enum: SPOTLIGHT, percentage*: integer}>, placementBidAdjustments: array<{percentage*: integer, placement*: enum: PRODUCT_PAGE | REST_OF_SEARCH | SITE_AMAZON_BUSINESS | TOP_OF_SEARCH}>}, bidStrategy: enum: MANUAL | RULE_BASED | SALES_DOWN_ONLY | SALES_UP_AND_DOWN}, budgetSettings: {offAmazonBudgetControlStrategy: enum: MAXIMIZE_REACH | MINIMIZE_SPEND}}
- `campaigns[].portfolioId`: string
- `campaigns[].siteRestrictions`: array<enum: AMAZON_BUSINESS | AMAZON_HAUL>
- `campaigns[].startDateTime` **REQUIRED**: string
- `campaigns[].state` **REQUIRED**: enum: ENABLED | PAUSED
- `campaigns[].tags`: array<{key*: string, value*: string}>

## SPONSORED_PRODUCTS - UPDATE

- `campaigns[]`: array of objects REQUIRED
- `campaigns[].budgets`: array<{budgetType*: enum: MONETARY, budgetValue*: oneOf: monetaryBudgetValue{monetaryBudgetValue: {monetaryBudget*: {value*: number}}}, recurrenceTimePeriod*: enum: DAILY}>
- `campaigns[].campaignId` **REQUIRED**: string
- `campaigns[].endDateTime`: string
- `campaigns[].name`: string
- `campaigns[].optimizations`: {bidSettings: {bidAdjustments: {audienceBidAdjustments: array<{audienceId*: string, percentage*: integer}>, creativeBidAdjustments: array<{creativeType: enum: SPOTLIGHT, percentage*: integer}>, placementBidAdjustments: array<{percentage*: integer, placement*: enum: PRODUCT_PAGE | REST_OF_SEARCH | SITE_AMAZON_BUSINESS | TOP_OF_SEARCH}>}, bidStrategy: enum: MANUAL | RULE_BASED | SALES_DOWN_ONLY | SALES_UP_AND_DOWN}, budgetSettings: {offAmazonBudgetControlStrategy: enum: MAXIMIZE_REACH | MINIMIZE_SPEND}}
- `campaigns[].portfolioId`: string
- `campaigns[].siteRestrictions`: array<enum: AMAZON_BUSINESS | AMAZON_HAUL>
- `campaigns[].startDateTime`: string
- `campaigns[].state`: enum: ENABLED | PAUSED
- `campaigns[].tags`: array<{key*: string, value*: string}>

## SPONSORED_PRODUCTS - DELETE

- `campaignIds` **REQUIRED**: array<string>

## SPONSORED_BRANDS - QUERY

- `adProductFilter` **REQUIRED**: {include*: array<enum: SPONSORED_BRANDS>}
- `campaignIdFilter`: {include*: array<string>}
- `goalFilter`: {include*: array<enum: AWARENESS | CONSIDERATION | CONVERSIONS>}
- `maxResults`: integer
- `nameFilter`: {include*: array<string>, queryTermMatchType*: enum: BROAD_MATCH | EXACT_MATCH}
- `nextToken`: string
- `portfolioIdFilter`: {include*: array<string>}
- `stateFilter`: {include*: array<enum: ARCHIVED | ENABLED | PAUSED>}

## SPONSORED_BRANDS - CREATE

- `campaigns[]`: array of objects REQUIRED
- `campaigns[].adProduct` **REQUIRED**: enum: SPONSORED_BRANDS
- `campaigns[].autoCreationSettings`: {autoCreateTargets: boolean}
- `campaigns[].brandId`: string
- `campaigns[].budgets` **REQUIRED**: array<{budgetType*: enum: MONETARY, budgetValue*: oneOf: monetaryBudgetValue{monetaryBudgetValue: {monetaryBudget*: {value*: number}}}, recurrenceTimePeriod*: enum: DAILY | LIFETIME}>
- `campaigns[].costType` **REQUIRED**: enum: CPC | CPM | FIXED_PRICE | VCPM
- `campaigns[].countries`: array<enum (23 values - see V1-GA-ENUMS.md)>
- `campaigns[].endDateTime`: string
- `campaigns[].marketplaceScope` **REQUIRED**: enum: SINGLE_MARKETPLACE
- `campaigns[].marketplaces`: array<enum (23 values - see V1-GA-ENUMS.md)>
- `campaigns[].name` **REQUIRED**: string
- `campaigns[].optimizations`: {bidSettings: {bidAdjustments: {audienceBidAdjustments: array<{audienceId*: string, percentage*: integer}>, placementBidAdjustments: array<{percentage*: integer, placement*: enum: HOME_PAGE | PRODUCT_PAGE | REST_OF_SEARCH | TOP_OF_SEARCH}>, shopperSegmentBidAdjustments: array<object>}, bidStrategy: enum: MANUAL | SALES_UP_AND_DOWN}, goalSettings: {kpi*: enum: CLICKS | TOP_OF_SEARCH_IMPRESSION_SHARE}}
- `campaigns[].portfolioId`: string
- `campaigns[].salesChannel`: enum: AMAZON | OFF_AMAZON
- `campaigns[].siteRestrictions`: array<enum: AMAZON_BUSINESS>
- `campaigns[].startDateTime` **REQUIRED**: string
- `campaigns[].state` **REQUIRED**: enum: ENABLED | PAUSED
- `campaigns[].tags`: array<{key*: string, value*: string}>
- `campaigns[].targetedPGDealId`: string

## SPONSORED_BRANDS - UPDATE

- `campaigns[]`: array of objects REQUIRED
- `campaigns[].budgets`: array<{budgetType*: enum: MONETARY, budgetValue*: oneOf: monetaryBudgetValue{monetaryBudgetValue: {monetaryBudget*: {value*: number}}}, recurrenceTimePeriod*: enum: DAILY | LIFETIME}>
- `campaigns[].campaignId` **REQUIRED**: string
- `campaigns[].endDateTime`: string
- `campaigns[].name`: string
- `campaigns[].optimizations`: {bidSettings: {bidAdjustments: {audienceBidAdjustments: array<{audienceId*: string, percentage*: integer}>, placementBidAdjustments: array<{percentage*: integer, placement*: enum: HOME_PAGE | PRODUCT_PAGE | REST_OF_SEARCH | TOP_OF_SEARCH}>, shopperSegmentBidAdjustments: array<object>}, bidStrategy: enum: MANUAL | SALES_UP_AND_DOWN}}
- `campaigns[].portfolioId`: string
- `campaigns[].startDateTime`: string
- `campaigns[].state`: enum: ENABLED | PAUSED
- `campaigns[].tags`: array<{key*: string, value*: string}>
- `campaigns[].targetedPGDealId`: string

## SPONSORED_BRANDS - DELETE

- `campaignIds` **REQUIRED**: array<string>

## SPONSORED_DISPLAY - QUERY

- `adProductFilter` **REQUIRED**: {include*: array<enum: SPONSORED_DISPLAY>}
- `campaignIdFilter`: {include*: array<string>}
- `maxResults`: integer
- `nameFilter`: {include*: array<string>, queryTermMatchType*: enum: BROAD_MATCH | EXACT_MATCH}
- `nextToken`: string
- `portfolioIdFilter`: {include*: array<string>}
- `stateFilter`: {include*: array<enum: ARCHIVED | ENABLED | PAUSED>}

## SPONSORED_DISPLAY - CREATE

- `campaigns[]`: array of objects REQUIRED
- `campaigns[].adProduct` **REQUIRED**: enum: SPONSORED_DISPLAY
- `campaigns[].budgets` **REQUIRED**: array<{budgetType*: enum: MONETARY, budgetValue*: oneOf: monetaryBudgetValue{monetaryBudgetValue: {monetaryBudget*: {value*: number}}}}>
- `campaigns[].costType` **REQUIRED**: enum: CPC | VCPM
- `campaigns[].countries`: array<enum (21 values - see V1-GA-ENUMS.md)>
- `campaigns[].endDateTime`: string
- `campaigns[].marketplaceScope` **REQUIRED**: enum: SINGLE_MARKETPLACE
- `campaigns[].marketplaces`: array<enum (21 values - see V1-GA-ENUMS.md)>
- `campaigns[].name` **REQUIRED**: string
- `campaigns[].portfolioId`: string
- `campaigns[].startDateTime` **REQUIRED**: string
- `campaigns[].state` **REQUIRED**: enum: ENABLED | PAUSED
- `campaigns[].tags`: array<{key*: string, value*: string}>

## SPONSORED_DISPLAY - UPDATE

- `campaigns[]`: array of objects REQUIRED
- `campaigns[].budgets`: array<{budgetType*: enum: MONETARY, budgetValue*: oneOf: monetaryBudgetValue{monetaryBudgetValue: {monetaryBudget*: {value*: number}}}}>
- `campaigns[].campaignId` **REQUIRED**: string
- `campaigns[].costType`: enum: CPC | VCPM
- `campaigns[].endDateTime`: string
- `campaigns[].name`: string
- `campaigns[].portfolioId`: string
- `campaigns[].startDateTime`: string
- `campaigns[].state`: enum: ENABLED | PAUSED
- `campaigns[].tags`: array<{key*: string, value*: string}>

## SPONSORED_DISPLAY - DELETE

- `campaignIds` **REQUIRED**: array<string>

## SPONSORED_TELEVISION - QUERY

- `adProductFilter` **REQUIRED**: {include*: array<enum: SPONSORED_TELEVISION>}
- `maxResults`: integer
- `nextToken`: string
- `stateFilter`: {include*: array<enum: ARCHIVED | ENABLED | PAUSED>}

## SPONSORED_TELEVISION - CREATE

- `campaigns[]`: array of objects REQUIRED
- `campaigns[].adProduct` **REQUIRED**: enum: SPONSORED_TELEVISION
- `campaigns[].budgets` **REQUIRED**: array<{budgetType*: enum: MONETARY, budgetValue*: oneOf: monetaryBudgetValue{monetaryBudgetValue: {monetaryBudget: {value*: number}}}, recurrenceTimePeriod*: enum: DAILY}>
- `campaigns[].countries`: array<enum: AU | BR | CA | DE | ES | FR | GB | IN | IT | JP | MX | SG | US>
- `campaigns[].endDateTime`: string
- `campaigns[].marketplaces`: array<enum: AU | BR | CA | DE | ES | FR | GB | IN | IT | JP | MX | SG | US>
- `campaigns[].name` **REQUIRED**: string
- `campaigns[].startDateTime` **REQUIRED**: string
- `campaigns[].state` **REQUIRED**: enum: ENABLED | PAUSED

## SPONSORED_TELEVISION - UPDATE

- `campaigns[]`: array of objects REQUIRED
- `campaigns[].adProduct`: enum: SPONSORED_TELEVISION
- `campaigns[].budgets`: array<{budgetType*: enum: MONETARY, budgetValue*: oneOf: monetaryBudgetValue{monetaryBudgetValue: {monetaryBudget: {value*: number}}}, recurrenceTimePeriod*: enum: DAILY}>
- `campaigns[].campaignId` **REQUIRED**: string
- `campaigns[].countries`: array<enum: AU | BR | CA | DE | ES | FR | GB | IN | IT | JP | MX | SG | US>
- `campaigns[].endDateTime`: string
- `campaigns[].marketplaces`: array<enum: AU | BR | CA | DE | ES | FR | GB | IN | IT | JP | MX | SG | US>
- `campaigns[].name`: string
- `campaigns[].startDateTime`: string
- `campaigns[].state`: enum: ENABLED | PAUSED

## AMAZON_DSP - QUERY

- `adProductFilter` **REQUIRED**: {include*: array<enum: AMAZON_DSP>}
- `campaignIdFilter`: {include*: array<string>}
- `maxResults`: integer
- `nextToken`: string
- `stateFilter`: {include*: array<enum: ARCHIVED | ENABLED | PAUSED>}

## AMAZON_DSP - CREATE

- `campaigns[]`: array of objects REQUIRED
- `campaigns[].adProduct` **REQUIRED**: enum: AMAZON_DSP
- `campaigns[].adomains`: array<string>
- `campaigns[].autoCreationSettings`: {autoManageCampaign: boolean}
- `campaigns[].budgets`: array<{budgetType*: enum: MONETARY, budgetValue*: oneOf: monetaryBudgetValue{monetaryBudgetValue: {monetaryBudget: {value*: number}}}, recurrenceTimePeriod*: enum: DAILY | LIFETIME | MONTHLY}>
- `campaigns[].countries`: array<enum (74 values - see V1-GA-ENUMS.md)>
- `campaigns[].fees`: array<{feeType*: enum: AGENCY, feeValue*: number, feeValueType*: enum: PERCENTAGE_OF_BUDGET}>
- `campaigns[].flights` **REQUIRED**: array<{budget*: {budgetType*: enum: MONETARY, budgetValue*: oneOf: monetaryBudgetValue{monetaryBudgetValue: {monetaryBudget: {value*: number}}}}, endDateTime*: string, flightId: string, name: string, startDateTime*: string}>
- `campaigns[].frequencies`: array<{eventMaxCount*: integer, frequencyTargetingSetting*: enum: HOUSEHOLD | USER, timeCount*: integer, timeUnit*: enum: DAYS | HOURS | MINUTES}>
- `campaigns[].marketplaces`: array<enum (17 values - see V1-GA-ENUMS.md)>
- `campaigns[].name` **REQUIRED**: string
- `campaigns[].optimizations` **REQUIRED**: {bidSettings*: {bidStrategy*: enum: PRIORITIZE_KPI_TARGET | SPEND_BUDGET_IN_FULL | USE_CAMPAIGN_STRATEGY}, budgetSettings: {budgetAllocation: enum: AUTO | MANUAL, flightBudgetRolloverStrategy: enum: CUMULATIVE_BUDGET_ROLLOVER | NO_ROLLOVER | PRIOR_BUDGET_ROLLOVER}, goalSettings: {kpi*: enum (19 values - see V1-GA-ENUMS.md), kpiValue: number}, primaryInventoryTypes: array<enum: AUDIO | DISPLAY | VIDEO_OLV | VIDEO_STV>}
- `campaigns[].purchaseOrderNumber`: string
- `campaigns[].skanAppId`: string
- `campaigns[].state` **REQUIRED**: enum: ENABLED | PAUSED
- `campaigns[].tags`: array<{key*: string, value*: string}>

## AMAZON_DSP - UPDATE

- `campaigns[]`: array of objects REQUIRED
- `campaigns[].adomains`: array<string>
- `campaigns[].budgets`: array<{budgetType*: enum: MONETARY, budgetValue*: oneOf: monetaryBudgetValue{monetaryBudgetValue: {monetaryBudget: {value*: number}}}, recurrenceTimePeriod*: enum: DAILY | LIFETIME | MONTHLY}>
- `campaigns[].campaignId` **REQUIRED**: string
- `campaigns[].fees`: array<{feeType*: enum: AGENCY, feeValue*: number, feeValueType*: enum: PERCENTAGE_OF_BUDGET}>
- `campaigns[].flights`: array<{budget*: {budgetType*: enum: MONETARY, budgetValue*: oneOf: monetaryBudgetValue{monetaryBudgetValue: {monetaryBudget: {value*: number}}}}, endDateTime*: string, flightId: string, name: string, startDateTime*: string}>
- `campaigns[].frequencies`: array<{eventMaxCount*: integer, frequencyTargetingSetting*: enum: HOUSEHOLD | USER, timeCount*: integer, timeUnit*: enum: DAYS | HOURS | MINUTES}>
- `campaigns[].name`: string
- `campaigns[].optimizations`: {bidSettings: {bidStrategy: enum: PRIORITIZE_KPI_TARGET | SPEND_BUDGET_IN_FULL | USE_CAMPAIGN_STRATEGY}, budgetSettings: {budgetAllocation: enum: AUTO | MANUAL, flightBudgetRolloverStrategy: enum: CUMULATIVE_BUDGET_ROLLOVER | NO_ROLLOVER | PRIOR_BUDGET_ROLLOVER}, goalSettings: {kpi: enum (19 values - see V1-GA-ENUMS.md), kpiValue: number}, primaryInventoryTypes: array<enum: AUDIO | DISPLAY | VIDEO_OLV | VIDEO_STV>}
- `campaigns[].purchaseOrderNumber`: string
- `campaigns[].skanAppId`: string
- `campaigns[].state`: enum: ENABLED | PAUSED
- `campaigns[].tags`: array<{key*: string, value*: string}>
