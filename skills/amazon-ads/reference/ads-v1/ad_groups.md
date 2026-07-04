# v1 `ad_groups` - FULL field catalog (generated; do not hand-edit)

Complete leaf-level request-body schema per ad product, extracted
from the vendored Amazon OpenAPI specs. `*` after a field name =
required within its object. Enums >15 values: V1-GA-ENUMS.md.

Regenerate: `python3 docs/ads-api-v1/tools/gen_field_catalog.py`


## ALL - QUERY

- `adGroupIdFilter`: {include*: array<string>}
- `adProductFilter` **REQUIRED**: {include*: array<enum: AMAZON_DSP | SPONSORED_BRANDS | SPONSORED_DISPLAY | SPONSORED_PRODUCTS | SPONSORED_TELEVISION>}
- `campaignIdFilter`: {include*: array<string>}
- `marketplaceScopeFilter`: {include*: array<enum: GLOBAL | SINGLE_MARKETPLACE>}
- `maxResults`: integer
- `nameFilter`: {include*: array<string>, queryTermMatchType*: enum: BROAD_MATCH | EXACT_MATCH}
- `nextToken`: string
- `stateFilter`: {include*: array<enum: ARCHIVED | ENABLED | PAUSED>}

## ALL - CREATE

- `adGroups[]`: array of objects REQUIRED
- `adGroups[].adProduct` **REQUIRED**: enum: AMAZON_DSP | SPONSORED_BRANDS | SPONSORED_DISPLAY | SPONSORED_PRODUCTS | SPONSORED_TELEVISION
- `adGroups[].adSettings`: {productAttributeSetRefinementConfigurationId: string}
- `adGroups[].advertisedProductCategoryIds`: array<string>
- `adGroups[].bid`: {baseBid: number, defaultBid: number, marketplaceSettings: array<{currencyCode*: enum (61 values - see V1-GA-ENUMS.md), defaultBid: number, marketplace*: enum (23 values - see V1-GA-ENUMS.md)}>, maxAverageBid: number}
- `adGroups[].budgets`: array<{budgetType*: enum: MONETARY, budgetValue*: oneOf: monetaryBudgetValue{monetaryBudgetValue: {marketplaceSettings: array<{marketplace*: enum (23 values - see V1-GA-ENUMS.md), monetaryBudget*: object}>, monetaryBudget: {value*: number}}}, recurrenceTimePeriod*: enum: DAILY | LIFETIME | MONTHLY}>
- `adGroups[].campaignId` **REQUIRED**: string
- `adGroups[].creativeRotationType`: enum: RANDOM | WEIGHTED
- `adGroups[].creativeType`: enum: IMAGE | VIDEO
- `adGroups[].endDateTime`: string
- `adGroups[].fees`: array<{addToBudgetSpentAmount*: boolean, feeType*: enum: AMAZON_AUDIENCE | AMAZON_DSP | MANAGED_SERVICE_FEE | OMNICHANNEL_METRICS | THIRD_PARTY_APPLIED | THIRD_PARTY_AUDIENCE | THIRD_PARTY_TARGETING, feeValue*: number, thirdPartyProvider*: enum: COM_SCORE | CPM_1 | CPM_2 | CPM_3 | DOUBLE_CLICK_CAMPAIGN_MANAGER | DOUBLE_VERIFY | INTEGRAL_AD_SCIENCE}>
- `adGroups[].frequencies`: array<{eventMaxCount*: integer, frequencyTargetingSetting*: enum: HOUSEHOLD | USER, timeCount*: integer, timeUnit*: enum: DAYS | HOURS | MINUTES}>
- `adGroups[].inventoryType`: enum: AAP_MOBILE_APP | AMAZON_MOBILE_DISPLAY | AUDIO | AUDIO_AMAZON_DEAL | DISPLAY | LIVE_EVENTS | ONLINE_VIDEO | PODCAST | STANDARD_DISPLAY | STREAMING_TV | STREAMING_TV_AMAZON_DEAL | VIDEO
- `adGroups[].marketplaceConfigurations`: array<{marketplace*: enum (23 values - see V1-GA-ENUMS.md), overrides*: {name: string, state: enum: ARCHIVED | ENABLED | PAUSED, tags: array<{key*: string, value*: string}>}}>
- `adGroups[].marketplaceScope`: enum: GLOBAL | SINGLE_MARKETPLACE
- `adGroups[].marketplaces`: array<enum (23 values - see V1-GA-ENUMS.md)>
- `adGroups[].name` **REQUIRED**: string
- `adGroups[].optimization`: {bidStrategy: enum: MANUAL | NEW_TO_BRAND | PRIORITIZE_KPI_TARGET | RULE_BASED | SALES_DOWN_ONLY | SALES_UP_AND_DOWN | SPEND_BUDGET_IN_FULL | USE_CAMPAIGN_STRATEGY, budgetSettings: {budgetAllocation: enum: AUTO | MANUAL, dailyMinSpendValue: number}, goalSettings: {kpi: enum (32 values - see V1-GA-ENUMS.md)}}
- `adGroups[].pacing`: {deliveryProfile*: enum: ASAP | EVEN | PACE_AHEAD}
- `adGroups[].purchaseOrderNumber`: string
- `adGroups[].startDateTime`: string
- `adGroups[].state` **REQUIRED**: enum: ENABLED | PAUSED
- `adGroups[].tags`: array<{key*: string, value*: string}>
- `adGroups[].targetingSettings`: {amazonViewability*: {includeUnmeasurableImpressions*: boolean, viewabilityTier*: enum: ALL_TIERS | GREATER_THAN_40_PERCENT | GREATER_THAN_50_PERCENT | GREATER_THAN_60_PERCENT | GREATER_THAN_70_PERCENT | LESS_THAN_40_PERCENT}, automatedTargetingTactic: enum: AWARENESS | CUSTOMER_ACQUISITION | MAXIMIZE_PERFORMANCE | PROSPECTING | REMARKETING | RETENTION | SEARCH, defaultAudienceTargetingMatchType: enum: EXACT | SIMILAR, enableLanguageTargeting: boolean, tacticsConvertersExclusionType: enum: NO_EXCLUSION | RECENT_CONVERTERS, targetedPGDealId: string, timeZoneType*: enum: ADVERTISER_REGION | VIEWER, userLocationSignal*: enum: CURRENT | MULTIPLE_SIGNALS, videoCompletionTier: enum: ALL_TIERS | GREATER_THAN_10_PERCENT | GREATER_THAN_20_PERCENT | GREATER_THAN_30_PERCENT | GREATER_THAN_40_PERCENT | GREATER_THAN_50_PERCENT | GREATER_THAN_60_PERCENT | GREATER_THAN_70_PERCENT | GREATER_THAN_80_PERCENT | GREATER_THAN_90_PERCENT}

## ALL - UPDATE

- `adGroups[]`: array of objects REQUIRED
- `adGroups[].adGroupId` **REQUIRED**: string
- `adGroups[].adProduct`: enum: AMAZON_DSP | SPONSORED_BRANDS | SPONSORED_DISPLAY | SPONSORED_PRODUCTS | SPONSORED_TELEVISION
- `adGroups[].adSettings`: {productAttributeSetRefinementConfigurationId: string}
- `adGroups[].advertisedProductCategoryIds`: array<string>
- `adGroups[].bid`: {baseBid: number, defaultBid: number, marketplaceSettings: array<{currencyCode*: enum (61 values - see V1-GA-ENUMS.md), defaultBid: number, marketplace*: enum (23 values - see V1-GA-ENUMS.md)}>, maxAverageBid: number}
- `adGroups[].budgets`: array<{budgetType*: enum: MONETARY, budgetValue*: oneOf: monetaryBudgetValue{monetaryBudgetValue: {marketplaceSettings: array<{marketplace*: enum (23 values - see V1-GA-ENUMS.md), monetaryBudget*: object}>, monetaryBudget: {value*: number}}}, recurrenceTimePeriod*: enum: DAILY | LIFETIME | MONTHLY}>
- `adGroups[].creativeRotationType`: enum: RANDOM | WEIGHTED
- `adGroups[].endDateTime`: string
- `adGroups[].fees`: array<{addToBudgetSpentAmount*: boolean, feeType*: enum: AMAZON_AUDIENCE | AMAZON_DSP | MANAGED_SERVICE_FEE | OMNICHANNEL_METRICS | THIRD_PARTY_APPLIED | THIRD_PARTY_AUDIENCE | THIRD_PARTY_TARGETING, feeValue*: number, thirdPartyProvider*: enum: COM_SCORE | CPM_1 | CPM_2 | CPM_3 | DOUBLE_CLICK_CAMPAIGN_MANAGER | DOUBLE_VERIFY | INTEGRAL_AD_SCIENCE}>
- `adGroups[].frequencies`: array<{eventMaxCount*: integer, frequencyTargetingSetting*: enum: HOUSEHOLD | USER, timeCount*: integer, timeUnit*: enum: DAYS | HOURS | MINUTES}>
- `adGroups[].marketplaceConfigurations`: array<{marketplace*: enum (23 values - see V1-GA-ENUMS.md), overrides*: {name: string, state: enum: ARCHIVED | ENABLED | PAUSED, tags: array<{key*: string, value*: string}>}}>
- `adGroups[].marketplaceScope`: enum: GLOBAL | SINGLE_MARKETPLACE
- `adGroups[].marketplaces`: array<enum (23 values - see V1-GA-ENUMS.md)>
- `adGroups[].name`: string
- `adGroups[].optimization`: {bidStrategy: enum: MANUAL | NEW_TO_BRAND | PRIORITIZE_KPI_TARGET | RULE_BASED | SALES_DOWN_ONLY | SALES_UP_AND_DOWN | SPEND_BUDGET_IN_FULL | USE_CAMPAIGN_STRATEGY, budgetSettings: {budgetAllocation: enum: AUTO | MANUAL, dailyMinSpendValue: number}, goalSettings: {kpi: enum (32 values - see V1-GA-ENUMS.md)}}
- `adGroups[].pacing`: {deliveryProfile: enum: ASAP | EVEN | PACE_AHEAD}
- `adGroups[].purchaseOrderNumber`: string
- `adGroups[].startDateTime`: string
- `adGroups[].state`: enum: ENABLED | PAUSED
- `adGroups[].tags`: array<{key*: string, value*: string}>
- `adGroups[].targetingSettings`: {amazonViewability: {includeUnmeasurableImpressions: boolean, viewabilityTier: enum: ALL_TIERS | GREATER_THAN_40_PERCENT | GREATER_THAN_50_PERCENT | GREATER_THAN_60_PERCENT | GREATER_THAN_70_PERCENT | LESS_THAN_40_PERCENT}, defaultAudienceTargetingMatchType: enum: EXACT | SIMILAR, enableLanguageTargeting: boolean, tacticsConvertersExclusionType: enum: NO_EXCLUSION | RECENT_CONVERTERS, targetedPGDealId: string, timeZoneType: enum: ADVERTISER_REGION | VIEWER, userLocationSignal: enum: CURRENT | MULTIPLE_SIGNALS, videoCompletionTier: enum: ALL_TIERS | GREATER_THAN_10_PERCENT | GREATER_THAN_20_PERCENT | GREATER_THAN_30_PERCENT | GREATER_THAN_40_PERCENT | GREATER_THAN_50_PERCENT | GREATER_THAN_60_PERCENT | GREATER_THAN_70_PERCENT | GREATER_THAN_80_PERCENT | GREATER_THAN_90_PERCENT}

## ALL - DELETE

- `adGroupIds` **REQUIRED**: array<string>

## SPONSORED_PRODUCTS - QUERY

- `adGroupIdFilter`: {include*: array<string>}
- `adProductFilter` **REQUIRED**: {include*: array<enum: SPONSORED_PRODUCTS>}
- `campaignIdFilter`: {include*: array<string>}
- `maxResults`: integer
- `nameFilter`: {include*: array<string>, queryTermMatchType*: enum: BROAD_MATCH | EXACT_MATCH}
- `nextToken`: string
- `stateFilter`: {include*: array<enum: ARCHIVED | ENABLED | PAUSED>}

## SPONSORED_PRODUCTS - CREATE

- `adGroups[]`: array of objects REQUIRED
- `adGroups[].adProduct` **REQUIRED**: enum: SPONSORED_PRODUCTS
- `adGroups[].adSettings`: {productAttributeSetRefinementConfigurationId: string}
- `adGroups[].bid` **REQUIRED**: {defaultBid*: number}
- `adGroups[].campaignId` **REQUIRED**: string
- `adGroups[].name` **REQUIRED**: string
- `adGroups[].state` **REQUIRED**: enum: ENABLED | PAUSED
- `adGroups[].tags`: array<{key*: string, value*: string}>

## SPONSORED_PRODUCTS - UPDATE

- `adGroups[]`: array of objects REQUIRED
- `adGroups[].adGroupId` **REQUIRED**: string
- `adGroups[].adSettings`: {productAttributeSetRefinementConfigurationId: string}
- `adGroups[].bid`: {defaultBid: number}
- `adGroups[].name`: string
- `adGroups[].state`: enum: ENABLED | PAUSED
- `adGroups[].tags`: array<{key*: string, value*: string}>

## SPONSORED_PRODUCTS - DELETE

- `adGroupIds` **REQUIRED**: array<string>

## SPONSORED_BRANDS - QUERY

- `adGroupIdFilter`: {include*: array<string>}
- `adProductFilter` **REQUIRED**: {include*: array<enum: SPONSORED_BRANDS>}
- `campaignIdFilter`: {include*: array<string>}
- `maxResults`: integer
- `nameFilter`: {include*: array<string>, queryTermMatchType*: enum: BROAD_MATCH | EXACT_MATCH}
- `nextToken`: string
- `stateFilter`: {include*: array<enum: ARCHIVED | ENABLED | PAUSED>}

## SPONSORED_BRANDS - CREATE

- `adGroups[]`: array of objects REQUIRED
- `adGroups[].adProduct` **REQUIRED**: enum: SPONSORED_BRANDS
- `adGroups[].campaignId` **REQUIRED**: string
- `adGroups[].name` **REQUIRED**: string
- `adGroups[].state` **REQUIRED**: enum: ENABLED | PAUSED
- `adGroups[].tags`: array<{key*: string, value*: string}>

## SPONSORED_BRANDS - UPDATE

- `adGroups[]`: array of objects REQUIRED
- `adGroups[].adGroupId` **REQUIRED**: string
- `adGroups[].name`: string
- `adGroups[].state`: enum: ENABLED | PAUSED
- `adGroups[].tags`: array<{key*: string, value*: string}>

## SPONSORED_BRANDS - DELETE

- `adGroupIds` **REQUIRED**: array<string>

## SPONSORED_DISPLAY - QUERY

- `adGroupIdFilter`: {include*: array<string>}
- `adProductFilter` **REQUIRED**: {include*: array<enum: SPONSORED_DISPLAY>}
- `campaignIdFilter`: {include*: array<string>}
- `maxResults`: integer
- `nameFilter`: {include*: array<string>, queryTermMatchType*: enum: BROAD_MATCH | EXACT_MATCH}
- `nextToken`: string
- `stateFilter`: {include*: array<enum: ARCHIVED | ENABLED | PAUSED>}

## SPONSORED_DISPLAY - CREATE

- `adGroups[]`: array of objects REQUIRED
- `adGroups[].adProduct` **REQUIRED**: enum: SPONSORED_DISPLAY
- `adGroups[].bid`: {defaultBid: number}
- `adGroups[].campaignId` **REQUIRED**: string
- `adGroups[].creativeType`: enum: IMAGE | VIDEO
- `adGroups[].marketplaceScope` **REQUIRED**: enum: SINGLE_MARKETPLACE
- `adGroups[].marketplaces` **REQUIRED**: array<enum (21 values - see V1-GA-ENUMS.md)>
- `adGroups[].name` **REQUIRED**: string
- `adGroups[].optimization`: {goalSettings: {kpi: enum: ADD_TO_CART | APPLICATIONS | CHECKOUTS | CLICKS | CONTACTS | LEADS | OTHER | PAGE_VIEWS | PURCHASES | REACH | SEARCH | SIGN_UP | SUBSCRIBE}}
- `adGroups[].state` **REQUIRED**: enum: ENABLED | PAUSED

## SPONSORED_DISPLAY - UPDATE

- `adGroups[]`: array of objects REQUIRED
- `adGroups[].adGroupId` **REQUIRED**: string
- `adGroups[].bid`: {defaultBid: number}
- `adGroups[].name`: string
- `adGroups[].optimization`: {goalSettings: {kpi: enum: ADD_TO_CART | APPLICATIONS | CHECKOUTS | CLICKS | CONTACTS | LEADS | OTHER | PAGE_VIEWS | PURCHASES | REACH | SEARCH | SIGN_UP | SUBSCRIBE}}
- `adGroups[].state`: enum: ENABLED | PAUSED

## SPONSORED_DISPLAY - DELETE

- `adGroupIds` **REQUIRED**: array<string>

## SPONSORED_TELEVISION - QUERY

- `adGroupIdFilter`: {include*: array<string>}
- `adProductFilter` **REQUIRED**: {include*: array<enum: SPONSORED_TELEVISION>}
- `campaignIdFilter`: {include*: array<string>}
- `maxResults`: integer
- `nameFilter`: {include*: array<string>, queryTermMatchType*: enum: BROAD_MATCH | EXACT_MATCH}
- `nextToken`: string
- `stateFilter`: {include*: array<enum: ARCHIVED | ENABLED | PAUSED>}

## SPONSORED_TELEVISION - CREATE

- `adGroups[]`: array of objects REQUIRED
- `adGroups[].adProduct` **REQUIRED**: enum: SPONSORED_TELEVISION
- `adGroups[].bid`: {baseBid: number, defaultBid: number}
- `adGroups[].campaignId` **REQUIRED**: string
- `adGroups[].marketplaces`: array<enum: AU | BR | CA | DE | ES | FR | GB | IN | IT | JP | MX | SG | US>
- `adGroups[].name` **REQUIRED**: string
- `adGroups[].state` **REQUIRED**: enum: ENABLED | PAUSED

## SPONSORED_TELEVISION - UPDATE

- `adGroups[]`: array of objects REQUIRED
- `adGroups[].adGroupId` **REQUIRED**: string
- `adGroups[].adProduct`: enum: SPONSORED_TELEVISION
- `adGroups[].bid`: {baseBid: number, defaultBid: number}
- `adGroups[].marketplaces`: array<enum: AU | BR | CA | DE | ES | FR | GB | IN | IT | JP | MX | SG | US>
- `adGroups[].name`: string
- `adGroups[].state`: enum: ENABLED | PAUSED

## AMAZON_DSP - QUERY

- `adGroupIdFilter`: {include*: array<string>}
- `adProductFilter` **REQUIRED**: {include*: array<enum: AMAZON_DSP>}
- `campaignIdFilter`: {include*: array<string>}
- `maxResults`: integer
- `nextToken`: string
- `stateFilter`: {include*: array<enum: ARCHIVED | ENABLED | PAUSED>}

## AMAZON_DSP - CREATE

- `adGroups[]`: array of objects REQUIRED
- `adGroups[].adProduct` **REQUIRED**: enum: AMAZON_DSP
- `adGroups[].advertisedProductCategoryIds` **REQUIRED**: array<string>
- `adGroups[].bid` **REQUIRED**: {baseBid*: number, maxAverageBid: number}
- `adGroups[].budgets`: array<{budgetType*: enum: MONETARY, budgetValue*: oneOf: monetaryBudgetValue{monetaryBudgetValue: {monetaryBudget: {value*: number}}}, recurrenceTimePeriod*: enum: DAILY | LIFETIME | MONTHLY}>
- `adGroups[].campaignId` **REQUIRED**: string
- `adGroups[].creativeRotationType` **REQUIRED**: enum: RANDOM | WEIGHTED
- `adGroups[].endDateTime` **REQUIRED**: string
- `adGroups[].fees`: array<{addToBudgetSpentAmount*: boolean, feeType*: enum: AMAZON_AUDIENCE | AMAZON_DSP | MANAGED_SERVICE_FEE | OMNICHANNEL_METRICS | THIRD_PARTY_APPLIED | THIRD_PARTY_AUDIENCE | THIRD_PARTY_TARGETING, feeValue*: number, thirdPartyProvider*: enum: COM_SCORE | CPM_1 | CPM_2 | CPM_3 | DOUBLE_CLICK_CAMPAIGN_MANAGER | DOUBLE_VERIFY | INTEGRAL_AD_SCIENCE}>
- `adGroups[].frequencies`: array<{eventMaxCount*: integer, frequencyTargetingSetting*: enum: HOUSEHOLD | USER, timeCount*: integer, timeUnit*: enum: DAYS | HOURS | MINUTES}>
- `adGroups[].inventoryType` **REQUIRED**: enum: AAP_MOBILE_APP | AMAZON_MOBILE_DISPLAY | AUDIO | AUDIO_AMAZON_DEAL | DISPLAY | LIVE_EVENTS | ONLINE_VIDEO | PODCAST | STANDARD_DISPLAY | STREAMING_TV | STREAMING_TV_AMAZON_DEAL | VIDEO
- `adGroups[].name` **REQUIRED**: string
- `adGroups[].optimization` **REQUIRED**: {bidStrategy*: enum: PRIORITIZE_KPI_TARGET | SPEND_BUDGET_IN_FULL | USE_CAMPAIGN_STRATEGY, budgetSettings: {budgetAllocation: enum: AUTO | MANUAL, dailyMinSpendValue: number}}
- `adGroups[].pacing` **REQUIRED**: {deliveryProfile*: enum: ASAP | EVEN | PACE_AHEAD}
- `adGroups[].purchaseOrderNumber`: string
- `adGroups[].startDateTime` **REQUIRED**: string
- `adGroups[].state` **REQUIRED**: enum: ENABLED | PAUSED
- `adGroups[].tags`: array<{key*: string, value*: string}>
- `adGroups[].targetingSettings` **REQUIRED**: {amazonViewability*: {includeUnmeasurableImpressions*: boolean, viewabilityTier*: enum: ALL_TIERS | GREATER_THAN_40_PERCENT | GREATER_THAN_50_PERCENT | GREATER_THAN_60_PERCENT | GREATER_THAN_70_PERCENT | LESS_THAN_40_PERCENT}, automatedTargetingTactic: enum: AWARENESS | CUSTOMER_ACQUISITION | MAXIMIZE_PERFORMANCE | PROSPECTING | REMARKETING | RETENTION | SEARCH, defaultAudienceTargetingMatchType: enum: EXACT | SIMILAR, enableLanguageTargeting: boolean, tacticsConvertersExclusionType: enum: NO_EXCLUSION | RECENT_CONVERTERS, targetedPGDealId: string, timeZoneType*: enum: ADVERTISER_REGION | VIEWER, userLocationSignal*: enum: CURRENT | MULTIPLE_SIGNALS, videoCompletionTier: enum: ALL_TIERS | GREATER_THAN_10_PERCENT | GREATER_THAN_20_PERCENT | GREATER_THAN_30_PERCENT | GREATER_THAN_40_PERCENT | GREATER_THAN_50_PERCENT | GREATER_THAN_60_PERCENT | GREATER_THAN_70_PERCENT | GREATER_THAN_80_PERCENT | GREATER_THAN_90_PERCENT}

## AMAZON_DSP - UPDATE

- `adGroups[]`: array of objects REQUIRED
- `adGroups[].adGroupId` **REQUIRED**: string
- `adGroups[].advertisedProductCategoryIds`: array<string>
- `adGroups[].bid`: {baseBid: number, maxAverageBid: number}
- `adGroups[].budgets`: array<{budgetType*: enum: MONETARY, budgetValue*: oneOf: monetaryBudgetValue{monetaryBudgetValue: {monetaryBudget: {value*: number}}}, recurrenceTimePeriod*: enum: DAILY | LIFETIME | MONTHLY}>
- `adGroups[].creativeRotationType`: enum: RANDOM | WEIGHTED
- `adGroups[].endDateTime`: string
- `adGroups[].fees`: array<{addToBudgetSpentAmount*: boolean, feeType*: enum: AMAZON_AUDIENCE | AMAZON_DSP | MANAGED_SERVICE_FEE | OMNICHANNEL_METRICS | THIRD_PARTY_APPLIED | THIRD_PARTY_AUDIENCE | THIRD_PARTY_TARGETING, feeValue*: number, thirdPartyProvider*: enum: COM_SCORE | CPM_1 | CPM_2 | CPM_3 | DOUBLE_CLICK_CAMPAIGN_MANAGER | DOUBLE_VERIFY | INTEGRAL_AD_SCIENCE}>
- `adGroups[].frequencies`: array<{eventMaxCount*: integer, frequencyTargetingSetting*: enum: HOUSEHOLD | USER, timeCount*: integer, timeUnit*: enum: DAYS | HOURS | MINUTES}>
- `adGroups[].name`: string
- `adGroups[].optimization`: {bidStrategy: enum: PRIORITIZE_KPI_TARGET | SPEND_BUDGET_IN_FULL | USE_CAMPAIGN_STRATEGY, budgetSettings: {budgetAllocation: enum: AUTO | MANUAL, dailyMinSpendValue: number}}
- `adGroups[].pacing`: {deliveryProfile: enum: ASAP | EVEN | PACE_AHEAD}
- `adGroups[].purchaseOrderNumber`: string
- `adGroups[].startDateTime`: string
- `adGroups[].state`: enum: ENABLED | PAUSED
- `adGroups[].tags`: array<{key*: string, value*: string}>
- `adGroups[].targetingSettings`: {amazonViewability: {includeUnmeasurableImpressions: boolean, viewabilityTier: enum: ALL_TIERS | GREATER_THAN_40_PERCENT | GREATER_THAN_50_PERCENT | GREATER_THAN_60_PERCENT | GREATER_THAN_70_PERCENT | LESS_THAN_40_PERCENT}, defaultAudienceTargetingMatchType: enum: EXACT | SIMILAR, enableLanguageTargeting: boolean, tacticsConvertersExclusionType: enum: NO_EXCLUSION | RECENT_CONVERTERS, targetedPGDealId: string, timeZoneType: enum: ADVERTISER_REGION | VIEWER, userLocationSignal: enum: CURRENT | MULTIPLE_SIGNALS, videoCompletionTier: enum: ALL_TIERS | GREATER_THAN_10_PERCENT | GREATER_THAN_20_PERCENT | GREATER_THAN_30_PERCENT | GREATER_THAN_40_PERCENT | GREATER_THAN_50_PERCENT | GREATER_THAN_60_PERCENT | GREATER_THAN_70_PERCENT | GREATER_THAN_80_PERCENT | GREATER_THAN_90_PERCENT}
