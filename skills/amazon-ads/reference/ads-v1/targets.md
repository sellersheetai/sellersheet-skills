# v1 `targets` - FULL field catalog (generated from Amazon's official OpenAPI specification; do not hand-edit)

Complete leaf-level request-body schema per ad product. `*` after a
field name = required within its object. Enums >15 values: ENUMS.md.

## ALL - QUERY

- `adGroupIdFilter`: {include*: array<string>}
- `adProductFilter` **REQUIRED**: {include*: array<enum: AMAZON_DSP | SPONSORED_BRANDS | SPONSORED_DISPLAY | SPONSORED_PRODUCTS | SPONSORED_TELEVISION>}
- `campaignIdFilter`: {include*: array<string>}
- `inventorySourceIdFilter`: {include*: array<{defaultValue: string}>}
- `inventorySourceTypeFilter`: {include*: array<enum: AMAZON | APD | DEAL | INVENTORY_GROUP | THIRD_PARTY_EXCHANGE>}
- `keywordFilter`: {include*: array<string>, queryTermMatchType*: enum: BROAD_MATCH | EXACT_MATCH}
- `marketplaceScopeFilter`: {include*: array<enum: GLOBAL | SINGLE_MARKETPLACE>}
- `matchTypeFilter`: {include*: array<enum (18 values - see ENUMS.md)>}
- `maxResults`: integer
- `nativeLanguageLocaleFilter`: {include*: array<enum (166 values - see ENUMS.md)>}
- `negativeFilter`: {include*: array<boolean>}
- `nextToken`: string
- `productIdFilter`: {include*: array<string>, queryTermMatchType*: enum: BROAD_MATCH | EXACT_MATCH}
- `stateFilter`: {include*: array<enum: ARCHIVED | ENABLED | PAUSED>}
- `targetIdFilter`: {include*: array<string>}
- `targetTypeFilter`: {include*: array<enum (27 values - see ENUMS.md)>}

## ALL - CREATE

- `targets[]`: array of objects REQUIRED
- `targets[].adGroupId`: string
- `targets[].adProduct` **REQUIRED**: enum: AMAZON_DSP | SPONSORED_BRANDS | SPONSORED_DISPLAY | SPONSORED_PRODUCTS | SPONSORED_TELEVISION
- `targets[].bid`: {bid: number, marketplaceSettings: array<{bid: number, currencyCode*: enum (61 values - see ENUMS.md), marketplace*: enum (23 values - see ENUMS.md)}>}
- `targets[].campaignId`: string
- `targets[].marketplaceConfigurations`: array<{marketplace*: enum (23 values - see ENUMS.md), overrides*: {state: enum: ARCHIVED | ENABLED | PAUSED, tags: array<{key*: string, value*: string}>, targetDetails: oneOf: keywordTarget{keywordTarget: {keyword*: string, matchType*: enum: BROAD | EXACT | PHRASE, nativeLanguageKeyword: string, nativeLanguageLocale: enum (166 values - see ENUMS.md)}} | themeTarget{themeTarget: {matchType*: enum: INTERESTED_AUDIENCE | KEYWORDS_CLOSE_MATCH | KEYWORDS_LOOSE_MATCH | KEYWORDS_RELATED_TO_GIFTS | KEYWORDS_RELATED_TO_PEER_BRANDS_PRODUCT_CATEGORY | KEYWORDS_RELATED_TO_PRIME_DAY | KEYWORDS_RELATED_TO_YOUR_BRAND | KEYWORDS_RELATED_TO_YOUR_LANDING_PAGES | KEYWORDS_RELATED_TO_YOUR_PRODUCT_CATEGORY | PRODUCTS_SIMILAR_TO_ADVERTISED_PRODUCTS | PRODUCT_COMPLEMENTS | PRODUCT_SUBSTITUTES}}}}>
- `targets[].marketplaceScope`: enum: GLOBAL | SINGLE_MARKETPLACE
- `targets[].marketplaces`: array<enum (23 values - see ENUMS.md)>
- `targets[].negative` **REQUIRED**: boolean
- `targets[].state` **REQUIRED**: enum: ENABLED | PAUSED
- `targets[].tags`: array<{key*: string, value*: string}>
- `targets[].targetDetails` **REQUIRED**: oneOf: keywordTarget{keywordTarget: {keyword*: string, matchType*: enum: BROAD | EXACT | PHRASE, nativeLanguageKeyword: string, nativeLanguageLocale: enum (166 values - see ENUMS.md)}} | productTarget{productTarget: {matchType*: enum: PRODUCT_COMPLEMENTS | PRODUCT_EXACT | PRODUCT_REMARKETING | PRODUCT_SIMILAR, product*: {marketplaceSettings: array<{marketplace*: enum (23 values - see ENUMS.md), productId*: string}>, productId: string}, productIdType*: enum: ASIN | SKU}} | productCategoryTarget{productCategoryTarget: {matchType: enum: MULTISIGNAL_BROAD, productCategoryRefinement*: {marketplaceSettings: array<{marketplace*: enum (23 values - see ENUMS.md), productCategoryRefinement*: {productAgeRangeId: string, productAgeRangeIdResolved: string, productBrandId: string, productBrandIdResolved: string, productCategoryId: string, productCategoryIdResolved: string, productGenreId: string, productPriceGreaterThan: number, productPriceLessThan: number, productPrimeShippingEligible: boolean, productRatingGreaterThan: number, productRatingLessThan: number}}>, productCategoryRefinement: {productAgeRangeId: string, productAgeRangeIdResolved: string, productBrandId: string, productBrandIdResolved: string, productCategoryId: string, productCategoryIdResolved: string, productGenreId: string, productPriceGreaterThan: number, productPriceLessThan: number, productPrimeShippingEligible: boolean, productRatingGreaterThan: number, productRatingLessThan: number}}, productGenreRefinement: {productGenreId*: string}}} | productAudienceTarget{productAudienceTarget: {asin*: {defaultValue: string}, event*: enum: PURCHASE | VIEW, lookback*: enum: DAYS_14 | DAYS_180 | DAYS_30 | DAYS_365 | DAYS_60 | DAYS_7 | DAYS_90, matchType*: enum: PRODUCT_EXACT | PRODUCT_SIMILAR}} | audienceTarget{audienceTarget: {acrossGroupOperator: enum: ALL | ANY, audienceId*: {defaultValue: string}, groupId: string, inGroupOperator: enum: ALL | ANY}} | locationTarget{locationTarget: {locationId*: string, locationIdResolved: string}} | domainTarget{domainTarget: {domainTargetDetails*: oneOf: domainListTarget{domainListTarget: {domainListId*: string}} | domainNameTarget{domainNameTarget: {domainName*: string}} | domainFileTarget{domainFileTarget: {domainFileKey*: string, domainFileName*: string}} | advertiserDomainList{advertiserDomainList: {inheritFromAdvertiser*: boolean}}, domainTargetType*: enum: ADVERTISER_DOMAIN_LIST | DOMAIN_FILE | DOMAIN_LIST | DOMAIN_NAME}} | appTarget{appTarget: {appId*: string, appType*: enum: MOBILE | STREAMING_TV}} | deviceTarget{deviceTarget: {deviceOrientation: enum: LANDSCAPE | PORTRAIT, deviceType*: enum: CONNECTED_DEVICE | CONNECTED_TV | DESKTOP | MOBILE, mobileDevice: enum: ANDROID | IPAD | IPHONE | KINDLE_FIRE | KINDLE_FIRE_HD, mobileEnvironment: enum: APP | WEB, mobileOs: enum: ANDROID | IOS}} | dayPartTarget{dayPartTarget: {dayOfWeek*: enum: FRIDAY | MONDAY | SATURDAY | SUNDAY | THURSDAY | TUESDAY | WEDNESDAY, timeOfDay*: {endTime*: string, startTime*: string}}} | contentCategoryTarget{contentCategoryTarget: {contentCategoryId*: string}} | contentGenreTarget{contentGenreTarget: {contentGenre*: enum (73 values - see ENUMS.md)}} | contentRatingTarget{contentRatingTarget: {contentRatingType*: enum: DSP_CONTENT_RATING | TWITCH_CONTENT_RATING, contentRatingTypeDetails*: oneOf: dspContentRating{dspContentRating: {dspContentRating*: enum: RATING_NOT_AVAILABLE | SUITABLE_FOR_ADULTS | SUITABLE_FOR_ALL_AUDIENCES | SUITABLE_FOR_MATURE_AUDIENCES | SUITABLE_FOR_MOST_AUDIENCES_WITH_PARENTAL_GUIDANCE | SUITABLE_FOR_TEEN_AND_OLDER_AUDIENCES}} | twitchContentRating{twitchContentRating: {twitchContentRating*: enum: TWITCH_MODERATE | TWITCH_RESTRICTIVE}}}} | brandSafetyTierTarget{brandSafetyTierTarget: {brandSafetyTier*: enum: EXPANDED | RESTRICTIVE | STANDARD}} | brandSafetyCategoryTarget{brandSafetyCategoryTarget: {brandSafetyCategory*: enum: ACCIDENTS_DISASTERS_AND_TRAGEDIES | ALCOHOL_AND_RELATED_PRODUCTS | BLOOD_GORE_VIOLENCE | CRIME | DRUG_REFERENCES_OR_USE | GAMBLING | HIGHLY_DEBATED_SOCIAL_ISSUES | POLITICS | PROFANITY | RELIGIOUS_CONTENT | SEXUAL_REFERENCES_AND_SUGGESTIVE | SHOCK_AND_HORROR | TOBACCO_AND_RELATED_PRODUCTS | UNRATED_MEDIA_CONTENT | WEAPONS}} | inventorySourceTarget{inventorySourceTarget: {inventorySourceId*: {defaultValue: string}, inventorySourceType*: enum: AMAZON | APD | DEAL | INVENTORY_GROUP | THIRD_PARTY_EXCHANGE}} | adInitiationTarget{adInitiationTarget: {videoInitiationType*: enum: AUTOPLAY | UNKNOWN | USER_INITIATED}} | adPlayerSizeTarget{adPlayerSizeTarget: {adPlayerSize*: enum: LARGE | MEDIUM | SMALL | UNKNOWN}} | videoAdFormatTarget{videoAdFormatTarget: {videoAdFormat*: enum: FULL_EPISODE_PLAYER | INSTREAM | OUTSTREAM}} | thirdPartyTarget{thirdPartyTarget: {thirdPartyTargetDetails*: oneOf: doubleVerifyFraudInvalidTraffic{doubleVerifyFraudInvalidTraffic: {blockAppAndSites: boolean, excludeAppsAndSites: enum: ALLOW_ALL | FRAUD_TRAFFIC_LEVEL_GTE_02 | FRAUD_TRAFFIC_LEVEL_GTE_04 | FRAUD_TRAFFIC_LEVEL_GTE_06 | FRAUD_TRAFFIC_LEVEL_GTE_08 | FRAUD_TRAFFIC_LEVEL_GTE_10 | FRAUD_TRAFFIC_LEVEL_GTE_100 | FRAUD_TRAFFIC_LEVEL_GTE_25 | FRAUD_TRAFFIC_LEVEL_GTE_50, excludeImpressions: boolean}} | doubleVerifyStandardDisplayBrandSafety{doubleVerifyStandardDisplayBrandSafety: {contentCategories: array<enum: AD_SERVER | CELEBRITY_GOSSIP | CULTS_SURVIVALISM | EXTREME_GRAPHIC | GAMBLING | INCENTIVIZED_MALWARE_CLUTTER | INFLAMMATORY_POLITICS_NEWS | NEGATIVE_NEWS_FINANCIAL | NEGATIVE_NEWS_PHARMACEUTICAL | NON_STANDARD_CONTENT_NON_ENGLISH | NON_STANDARD_CONTENT_PARKING_PAGE | OCCULT | PIRACY_COPYRIGHT_INFRINGEMENT | UNMODERATED_UGC_FORUMS_IMAGES_VIDEO>, contentCategoriesWithRisk: array<{key*: string, value*: enum: ALLOW_ALL | HIGH | HIGH_MEDIUM | HIGH_MEDIUM_LOW}>, unknownContent: boolean}} | doubleVerifyBrandSafety{doubleVerifyBrandSafety: {appAgeRating: array<enum: ADULTS_ONLY_18_PLUS | EVERYONE_4_PLUS | MATURE_17_PLUS | TEENS_12_PLUS | TWEENS_9_PLUS | UNKNOWN>, appStarRating: enum: ALLOW_ALL | APP_STAR_RATING_LT_1_POINT_5_STARS | APP_STAR_RATING_LT_2_POINT_5_STARS | APP_STAR_RATING_LT_2_STARS | APP_STAR_RATING_LT_3_POINT_5_STARS | APP_STAR_RATING_LT_3_STARS | APP_STAR_RATING_LT_4_POINT_5_STARS | APP_STAR_RATING_LT_4_STARS, contentCategories: array<enum: AD_SERVER | CELEBRITY_GOSSIP | CULTS_SURVIVALISM | EXTREME_GRAPHIC | GAMBLING | INCENTIVIZED_MALWARE_CLUTTER | INFLAMMATORY_POLITICS_NEWS | NEGATIVE_NEWS_FINANCIAL | NEGATIVE_NEWS_PHARMACEUTICAL | NON_STANDARD_CONTENT_NON_ENGLISH | NON_STANDARD_CONTENT_PARKING_PAGE | OCCULT | PIRACY_COPYRIGHT_INFRINGEMENT | UNMODERATED_UGC_FORUMS_IMAGES_VIDEO>, contentCategoriesWithRisk: array<{key*: string, value*: enum: ALLOW_ALL | HIGH | HIGH_MEDIUM | HIGH_MEDIUM_LOW}>, excludeAppsWithInsufficientRating: boolean, unknownContent: boolean}} | doubleVerifyViewability{doubleVerifyViewability: {averageCompletionAndFullyViewableRateTargeting: enum: ALLOW_ALL | AVG_COMPLETION_FULLY_VIEWABLE_GTE_10 | AVG_COMPLETION_FULLY_VIEWABLE_GTE_20 | AVG_COMPLETION_FULLY_VIEWABLE_GTE_25 | AVG_COMPLETION_FULLY_VIEWABLE_GTE_30 | AVG_COMPLETION_FULLY_VIEWABLE_GTE_35 | AVG_COMPLETION_FULLY_VIEWABLE_GTE_40, brandExposureViewabilityTargeting: enum: ALLOW_ALL | BRAND_EXPOSURE_VIEWABILITY_GTE_10_SEC_AVG_DURATION | BRAND_EXPOSURE_VIEWABILITY_GTE_15_SEC_AVG_DURATION | BRAND_EXPOSURE_VIEWABILITY_GTE_5_SEC_AVG_DURATION, includeUnmeasurableImpressions: boolean, mrcViewabilityTargeting: enum: ALLOW_ALL | MRC_VIEWABILITY_GTE_30 | MRC_VIEWABILITY_GTE_40 | MRC_VIEWABILITY_GTE_50 | MRC_VIEWABILITY_GTE_55 | MRC_VIEWABILITY_GTE_60 | MRC_VIEWABILITY_GTE_65 | MRC_VIEWABILITY_GTE_70 | MRC_VIEWABILITY_GTE_75 | MRC_VIEWABILITY_GTE_80}} | doubleVerifyAuthenticBrandSafety{doubleVerifyAuthenticBrandSafety: {doubleVerifySegmentId: string}} | doubleVerifyCustomContextualSegmentId{doubleVerifyCustomContextualSegmentId: {doubleVerifySegmentId: string}} | doubleVerifyAuthenticAttention{doubleVerifyAuthenticAttention: {universalAttention*: boolean}} | integralAdScienceFraudInvalidTraffic{integralAdScienceFraudInvalidTraffic: {targetSetting: enum: ALLOW_ALL | FRAUD_INVALID_TRAFFIC_EXCLUDE_HIGH_MODERATE_RISK | FRAUD_INVALID_TRAFFIC_EXCLUDE_HIGH_RISK}} | integralAdScienceBrandSafety{integralAdScienceBrandSafety: {excludeContent: boolean, iasBrandSafetyAdult: enum: ALLOW_ALL | BRAND_SAFETY_EXCLUDE_HIGH_AND_MODERATE_RISK | BRAND_SAFETY_EXCLUDE_HIGH_RISK, iasBrandSafetyAlcohol: enum: ALLOW_ALL | BRAND_SAFETY_EXCLUDE_HIGH_AND_MODERATE_RISK | BRAND_SAFETY_EXCLUDE_HIGH_RISK, iasBrandSafetyGambling: enum: ALLOW_ALL | BRAND_SAFETY_EXCLUDE_HIGH_AND_MODERATE_RISK | BRAND_SAFETY_EXCLUDE_HIGH_RISK, iasBrandSafetyHateSpeech: enum: ALLOW_ALL | BRAND_SAFETY_EXCLUDE_HIGH_AND_MODERATE_RISK | BRAND_SAFETY_EXCLUDE_HIGH_RISK, iasBrandSafetyIllegalDownloads: enum: ALLOW_ALL | BRAND_SAFETY_EXCLUDE_HIGH_AND_MODERATE_RISK | BRAND_SAFETY_EXCLUDE_HIGH_RISK, iasBrandSafetyIllegalDrugs: enum: ALLOW_ALL | BRAND_SAFETY_EXCLUDE_HIGH_AND_MODERATE_RISK | BRAND_SAFETY_EXCLUDE_HIGH_RISK, iasBrandSafetyOffensiveLanguage: enum: ALLOW_ALL | BRAND_SAFETY_EXCLUDE_HIGH_AND_MODERATE_RISK | BRAND_SAFETY_EXCLUDE_HIGH_RISK, iasBrandSafetyViolence: enum: ALLOW_ALL | BRAND_SAFETY_EXCLUDE_HIGH_AND_MODERATE_RISK | BRAND_SAFETY_EXCLUDE_HIGH_RISK}} | integralAdScienceViewability{integralAdScienceViewability: {standard*: enum: GROUPM | MRC | NONE | PUBLICIS, viewabilityTargeting: enum: ALLOW_ALL | VIEWABILITY_TIER_GT_40 | VIEWABILITY_TIER_GT_50 | VIEWABILITY_TIER_GT_60 | VIEWABILITY_TIER_GT_70 | VIEWABILITY_TIER_LT_40}} | integralAdScienceContextualTargeting{integralAdScienceContextualTargeting: {topicalSegments: array<string>, verticalSegments: array<string>}} | integralAdScienceContextualAvoidance{integralAdScienceContextualAvoidance: {avoidanceSegments: array<string>}} | pixalateFraudInvalidTraffic{pixalateFraudInvalidTraffic: {excludeAppsAndDomains: boolean, excludeIpAddressAndUserAgents: boolean, excludeOttAndMobileDevices: boolean, excludeRemovedAppsFromAppStores: boolean}} | integralAdScienceQualitySync{integralAdScienceQualitySync: {segmentId: string}} | newsGuardBrandGuardTrustedNewsTargeting{newsGuardBrandGuardTrustedNewsTargeting: {targetingList: array<enum: BASIC_INCLUDE | BUSINESS_INCLUDE | COMMUNITY_INCLUDE | HEALTH_INCLUDE | HIGH_INCLUDE | LIFESTYLE_INCLUDE | LOCAL_INCLUDE | MAX_INCLUDE | POLITICS_INCLUDE | TECH_INCLUDE>}} | newsGuardBrandGuardMisinformationSafety{newsGuardBrandGuardMisinformationSafety: {avoidanceList: array<enum: AI_GENERATED_MFA | BASIC_EXCLUDE | CLIMATE_MISINFORMATION | COVID_MISINFORMATION | ELECTION_MISINFORMATION | HEALTH_MISINFORMATION | HIGH_EXCLUDE | ISRAEL_HAMAS_MISINFORMATION | MAX_EXCLUDE | MISINFORMATION_SITES | OPINIONATED_NEWS | QANON_MISINFORMATION | UKRAINE_MISINFORMATION | VACCINE_MISINFORMATION>}}, thirdPartyTargetType*: enum (16 values - see ENUMS.md)}} | themeTarget{themeTarget: {matchType*: enum: INTERESTED_AUDIENCE | KEYWORDS_CLOSE_MATCH | KEYWORDS_LOOSE_MATCH | KEYWORDS_RELATED_TO_GIFTS | KEYWORDS_RELATED_TO_PEER_BRANDS_PRODUCT_CATEGORY | KEYWORDS_RELATED_TO_PRIME_DAY | KEYWORDS_RELATED_TO_YOUR_BRAND | KEYWORDS_RELATED_TO_YOUR_LANDING_PAGES | KEYWORDS_RELATED_TO_YOUR_PRODUCT_CATEGORY | PRODUCTS_SIMILAR_TO_ADVERTISED_PRODUCTS | PRODUCT_COMPLEMENTS | PRODUCT_SUBSTITUTES}} | contentInstreamPositionTarget{contentInstreamPositionTarget: {instreamPosition*: enum: MID_ROLL | POST_ROLL | PRE_ROLL | UNKNOWN}} | contentOutstreamPositionTarget{contentOutstreamPositionTarget: {outstreamPosition*: enum: ACCOMPANYING_CONTENT | INTERSTITIAL | STANDALONE | UNKNOWN}} | videoContentDurationTarget{videoContentDurationTarget: {duration*: enum: EXTENDED | LONG | MEDIUM | SHORT | UNKNOWN}} | foldPositionTarget{foldPositionTarget: {foldPosition*: enum: ABOVE_THE_FOLD | BELOW_THE_FOLD | UNKNOWN}} | nativeContentPositionTarget{nativeContentPositionTarget: {nativePosition*: enum: IN_ARTICLE | IN_FEED | PERIPHERAL | RECOMMENDATION | UNKNOWN}} | placementTypeTarget{placementTypeTarget: {placementType*: enum: REWARDED}}
- `targets[].targetType` **REQUIRED**: enum (27 values - see ENUMS.md)

## ALL - UPDATE

- `targets[]`: array of objects REQUIRED
- `targets[].bid`: {bid: number, marketplaceSettings: array<{bid: number, currencyCode*: enum (61 values - see ENUMS.md), marketplace*: enum (23 values - see ENUMS.md)}>}
- `targets[].campaignId`: string
- `targets[].marketplaceConfigurations`: array<{marketplace*: enum (23 values - see ENUMS.md), overrides*: {state: enum: ARCHIVED | ENABLED | PAUSED, tags: array<{key*: string, value*: string}>, targetDetails: oneOf: keywordTarget{keywordTarget: {keyword*: string, matchType*: enum: BROAD | EXACT | PHRASE, nativeLanguageKeyword: string, nativeLanguageLocale: enum (166 values - see ENUMS.md)}} | themeTarget{themeTarget: {matchType*: enum: INTERESTED_AUDIENCE | KEYWORDS_CLOSE_MATCH | KEYWORDS_LOOSE_MATCH | KEYWORDS_RELATED_TO_GIFTS | KEYWORDS_RELATED_TO_PEER_BRANDS_PRODUCT_CATEGORY | KEYWORDS_RELATED_TO_PRIME_DAY | KEYWORDS_RELATED_TO_YOUR_BRAND | KEYWORDS_RELATED_TO_YOUR_LANDING_PAGES | KEYWORDS_RELATED_TO_YOUR_PRODUCT_CATEGORY | PRODUCTS_SIMILAR_TO_ADVERTISED_PRODUCTS | PRODUCT_COMPLEMENTS | PRODUCT_SUBSTITUTES}}}}>
- `targets[].marketplaceScope`: enum: GLOBAL | SINGLE_MARKETPLACE
- `targets[].marketplaces`: array<enum (23 values - see ENUMS.md)>
- `targets[].state`: enum: ENABLED | PAUSED
- `targets[].tags`: array<{key*: string, value*: string}>
- `targets[].targetId` **REQUIRED**: string

## ALL - DELETE

- `targetIds` **REQUIRED**: array<string>

## SPONSORED_PRODUCTS - QUERY

- `adGroupIdFilter`: {include*: array<string>}
- `adProductFilter` **REQUIRED**: {include*: array<enum: SPONSORED_PRODUCTS>}
- `campaignIdFilter`: {include*: array<string>}
- `keywordFilter`: {include*: array<string>, queryTermMatchType*: enum: BROAD_MATCH | EXACT_MATCH}
- `matchTypeFilter`: {include*: array<enum: BROAD | EXACT | KEYWORDS_CLOSE_MATCH | KEYWORDS_LOOSE_MATCH | KEYWORDS_RELATED_TO_GIFTS | KEYWORDS_RELATED_TO_PEER_BRANDS_PRODUCT_CATEGORY | KEYWORDS_RELATED_TO_PRIME_DAY | KEYWORDS_RELATED_TO_YOUR_BRAND | KEYWORDS_RELATED_TO_YOUR_PRODUCT_CATEGORY | PHRASE | PRODUCT_COMPLEMENTS | PRODUCT_EXACT | PRODUCT_SIMILAR | PRODUCT_SUBSTITUTES>}
- `maxResults`: integer
- `negativeFilter`: {include*: array<boolean>}
- `nextToken`: string
- `productIdFilter`: {include*: array<string>, queryTermMatchType*: enum: BROAD_MATCH | EXACT_MATCH}
- `stateFilter`: {include*: array<enum: ARCHIVED | ENABLED | PAUSED>}
- `targetIdFilter`: {include*: array<string>}
- `targetTypeFilter`: {include*: array<enum: KEYWORD | LOCATION | PRODUCT | PRODUCT_CATEGORY | THEME>}

## SPONSORED_PRODUCTS - CREATE

- `targets[]`: array of objects REQUIRED
- `targets[].adGroupId`: string
- `targets[].adProduct` **REQUIRED**: enum: SPONSORED_PRODUCTS
- `targets[].bid`: {bid: number}
- `targets[].campaignId`: string
- `targets[].negative` **REQUIRED**: boolean
- `targets[].state` **REQUIRED**: enum: ENABLED | PAUSED
- `targets[].tags`: array<{key*: string, value*: string}>
- `targets[].targetDetails` **REQUIRED**: oneOf: keywordTarget{keywordTarget: {keyword*: string, matchType*: enum: BROAD | EXACT | PHRASE, nativeLanguageKeyword: string, nativeLanguageLocale: enum: zh_CN}} | productTarget{productTarget: {matchType*: enum: PRODUCT_EXACT | PRODUCT_SIMILAR, product*: {productId*: string}, productIdType*: enum: ASIN | SKU}} | productCategoryTarget{productCategoryTarget: {productCategoryRefinement*: {productCategoryRefinement*: {productAgeRangeId: string, productBrandId: string, productCategoryId: string, productGenreId: string, productPriceGreaterThan: number, productPriceLessThan: number, productPrimeShippingEligible: boolean, productRatingGreaterThan: number, productRatingLessThan: number}}}} | locationTarget{locationTarget: {locationId*: string}} | themeTarget{themeTarget: {matchType*: enum: KEYWORDS_CLOSE_MATCH | KEYWORDS_LOOSE_MATCH | KEYWORDS_RELATED_TO_GIFTS | KEYWORDS_RELATED_TO_PEER_BRANDS_PRODUCT_CATEGORY | KEYWORDS_RELATED_TO_PRIME_DAY | KEYWORDS_RELATED_TO_YOUR_BRAND | KEYWORDS_RELATED_TO_YOUR_PRODUCT_CATEGORY | PRODUCT_COMPLEMENTS | PRODUCT_SUBSTITUTES}}
- `targets[].targetType` **REQUIRED**: enum: KEYWORD | LOCATION | PRODUCT | PRODUCT_CATEGORY | THEME

## SPONSORED_PRODUCTS - UPDATE

- `targets[]`: array of objects REQUIRED
- `targets[].bid`: {bid: number}
- `targets[].state`: enum: ENABLED | PAUSED
- `targets[].tags`: array<{key*: string, value*: string}>
- `targets[].targetId` **REQUIRED**: string

## SPONSORED_PRODUCTS - DELETE

- `targetIds` **REQUIRED**: array<string>

## SPONSORED_BRANDS - QUERY

- `adGroupIdFilter`: {include*: array<string>}
- `adProductFilter` **REQUIRED**: {include*: array<enum: SPONSORED_BRANDS>}
- `campaignIdFilter`: {include*: array<string>}
- `keywordFilter`: {include*: array<string>, queryTermMatchType*: enum: BROAD_MATCH | EXACT_MATCH}
- `matchTypeFilter`: {include*: array<enum: BROAD | EXACT | KEYWORDS_RELATED_TO_YOUR_BRAND | KEYWORDS_RELATED_TO_YOUR_LANDING_PAGES | PHRASE | PRODUCT_EXACT>}
- `maxResults`: integer
- `nativeLanguageLocaleFilter`: {include*: array<enum: zh_CN>}
- `negativeFilter`: {include*: array<boolean>}
- `nextToken`: string
- `stateFilter`: {include*: array<enum: ARCHIVED | ENABLED | PAUSED>}
- `targetIdFilter`: {include*: array<string>}
- `targetTypeFilter`: {include*: array<enum: KEYWORD | PRODUCT | PRODUCT_CATEGORY | THEME>}

## SPONSORED_BRANDS - CREATE

- `targets[]`: array of objects REQUIRED
- `targets[].adGroupId` **REQUIRED**: string
- `targets[].adProduct` **REQUIRED**: enum: SPONSORED_BRANDS
- `targets[].bid`: {bid*: number}
- `targets[].campaignId`: string
- `targets[].negative` **REQUIRED**: boolean
- `targets[].state` **REQUIRED**: enum: ENABLED | PAUSED
- `targets[].targetDetails` **REQUIRED**: oneOf: keywordTarget{keywordTarget: {keyword*: string, matchType*: enum: BROAD | EXACT | PHRASE, nativeLanguageKeyword: string, nativeLanguageLocale: enum: zh_CN}} | productTarget{productTarget: {matchType*: enum: PRODUCT_EXACT, product*: {productId: string}, productIdType*: enum: ASIN}} | productCategoryTarget{productCategoryTarget: {productCategoryRefinement*: {productCategoryRefinement: {productBrandId: string, productCategoryId: string, productPriceGreaterThan: number, productPriceLessThan: number, productRatingGreaterThan: number, productRatingLessThan: number}}}} | themeTarget{themeTarget: {matchType*: enum: KEYWORDS_RELATED_TO_YOUR_BRAND | KEYWORDS_RELATED_TO_YOUR_LANDING_PAGES}}
- `targets[].targetType` **REQUIRED**: enum: KEYWORD | PRODUCT | PRODUCT_CATEGORY | THEME

## SPONSORED_BRANDS - UPDATE

- `targets[]`: array of objects REQUIRED
- `targets[].bid`: {bid: number}
- `targets[].state`: enum: ENABLED | PAUSED
- `targets[].targetId` **REQUIRED**: string

## SPONSORED_BRANDS - DELETE

- `targetIds` **REQUIRED**: array<string>

## SPONSORED_DISPLAY - QUERY

- `adGroupIdFilter`: {include*: array<string>}
- `adProductFilter` **REQUIRED**: {include*: array<enum: SPONSORED_DISPLAY>}
- `campaignIdFilter`: {include*: array<string>}
- `maxResults`: integer
- `nextToken`: string
- `stateFilter`: {include*: array<enum: ARCHIVED | ENABLED | PAUSED>}
- `targetIdFilter`: {include*: array<string>}

## SPONSORED_DISPLAY - CREATE

- `targets[]`: array of objects REQUIRED
- `targets[].adGroupId`: string
- `targets[].adProduct` **REQUIRED**: enum: SPONSORED_DISPLAY
- `targets[].bid`: {bid: number}
- `targets[].campaignId`: string
- `targets[].negative` **REQUIRED**: boolean
- `targets[].state` **REQUIRED**: enum: ENABLED | PAUSED
- `targets[].targetDetails` **REQUIRED**: oneOf: keywordTarget{keywordTarget: {keyword*: string, matchType*: enum: BROAD | EXACT | PHRASE, nativeLanguageKeyword: string, nativeLanguageLocale: enum: en_US}} | productTarget{productTarget: {matchType*: enum: PRODUCT_EXACT | PRODUCT_SIMILAR, product*: {productId: string}, productIdType*: enum: ASIN | SKU}} | productCategoryTarget{productCategoryTarget: {productCategoryRefinement*: {productCategoryRefinement: {productAgeRangeId: string, productAgeRangeIdResolved: string, productBrandId: string, productBrandIdResolved: string, productCategoryId: string, productCategoryIdResolved: string, productPriceGreaterThan: number, productPriceLessThan: number, productPrimeShippingEligible: boolean, productRatingGreaterThan: number, productRatingLessThan: number}}}} | productAudienceTarget{productAudienceTarget: {asin*: {defaultValue: string}, event*: enum: PURCHASE | VIEW, lookback*: enum: DAYS_14 | DAYS_180 | DAYS_30 | DAYS_365 | DAYS_60 | DAYS_7 | DAYS_90, matchType*: enum: PRODUCT_EXACT | PRODUCT_SIMILAR}} | audienceTarget{audienceTarget: {audienceId*: {defaultValue: string}}} | locationTarget{locationTarget: {locationId*: string, locationIdResolved: string}} | contentCategoryTarget{contentCategoryTarget: {contentCategoryId*: string}} | themeTarget{themeTarget: {matchType*: enum: INTERESTED_AUDIENCE}}
- `targets[].targetType` **REQUIRED**: enum: AUDIENCE | CONTENT_CATEGORY | KEYWORD | LOCATION | PRODUCT | PRODUCT_AUDIENCE | PRODUCT_CATEGORY | THEME

## SPONSORED_DISPLAY - UPDATE

- `targets[]`: array of objects REQUIRED
- `targets[].bid`: {bid: number}
- `targets[].state`: enum: ENABLED | PAUSED
- `targets[].targetId` **REQUIRED**: string

## SPONSORED_DISPLAY - DELETE

- `targetIds` **REQUIRED**: array<string>

## SPONSORED_TELEVISION - QUERY

- `adGroupIdFilter`: {include*: array<string>}
- `adProductFilter` **REQUIRED**: {include*: array<enum: SPONSORED_TELEVISION>}
- `campaignIdFilter`: {include*: array<string>}
- `maxResults`: integer
- `nextToken`: string
- `stateFilter`: {include*: array<enum: ARCHIVED | ENABLED | PAUSED>}
- `targetIdFilter`: {include*: array<string>}

## SPONSORED_TELEVISION - CREATE

- `targets[]`: array of objects REQUIRED
- `targets[].adGroupId` **REQUIRED**: string
- `targets[].adProduct` **REQUIRED**: enum: SPONSORED_TELEVISION
- `targets[].negative` **REQUIRED**: boolean
- `targets[].state` **REQUIRED**: enum: ENABLED | PAUSED
- `targets[].targetDetails` **REQUIRED**: oneOf: audienceTarget{audienceTarget: {audienceId*: {defaultValue: string}, groupId: string}} | locationTarget{locationTarget: {locationId*: string}}
- `targets[].targetType` **REQUIRED**: enum: AUDIENCE | LOCATION

## SPONSORED_TELEVISION - UPDATE

- `targets[]`: array of objects REQUIRED
- `targets[].state`: enum: ENABLED | PAUSED
- `targets[].targetId` **REQUIRED**: string

## SPONSORED_TELEVISION - DELETE

- `targetIds` **REQUIRED**: array<string>

## AMAZON_DSP - QUERY

- `adGroupIdFilter`: {include*: array<string>}
- `adProductFilter` **REQUIRED**: {include*: array<enum: AMAZON_DSP>}
- `inventorySourceIdFilter`: {include*: array<{defaultValue: string}>}
- `inventorySourceTypeFilter`: {include*: array<enum: AMAZON | APD | DEAL | INVENTORY_GROUP | THIRD_PARTY_EXCHANGE>}
- `maxResults`: integer
- `nextToken`: string
- `stateFilter`: {include*: array<enum: ARCHIVED | ENABLED | PAUSED>}
- `targetTypeFilter`: {include*: array<enum (26 values - see ENUMS.md)>}

## AMAZON_DSP - CREATE

- `targets[]`: array of objects REQUIRED
- `targets[].adGroupId` **REQUIRED**: string
- `targets[].adProduct` **REQUIRED**: enum: AMAZON_DSP
- `targets[].negative` **REQUIRED**: boolean
- `targets[].state` **REQUIRED**: enum: ENABLED | PAUSED
- `targets[].targetDetails` **REQUIRED**: oneOf: keywordTarget{keywordTarget: {keyword*: string, matchType*: enum: BROAD}} | productTarget{productTarget: {matchType*: enum: PRODUCT_COMPLEMENTS | PRODUCT_EXACT | PRODUCT_REMARKETING | PRODUCT_SIMILAR, product*: object, productIdType*: enum: ASIN}} | productCategoryTarget{productCategoryTarget: {matchType: enum: MULTISIGNAL_BROAD, productCategoryRefinement*: {productCategoryRefinement: {productCategoryId: string}}}} | audienceTarget{audienceTarget: {acrossGroupOperator: enum: ALL | ANY, audienceId*: {defaultValue: string}, groupId: string, inGroupOperator: enum: ALL | ANY}} | locationTarget{locationTarget: {locationId*: string}} | domainTarget{domainTarget: {domainTargetDetails*: oneOf: domainListTarget{domainListTarget: {domainListId*: string}} | domainNameTarget{domainNameTarget: {domainName*: string}} | domainFileTarget{domainFileTarget: {domainFileKey*: string, domainFileName*: string}} | advertiserDomainList{advertiserDomainList: {inheritFromAdvertiser*: boolean}}, domainTargetType*: enum: ADVERTISER_DOMAIN_LIST | DOMAIN_FILE | DOMAIN_LIST | DOMAIN_NAME}} | appTarget{appTarget: {appId*: string, appType*: enum: MOBILE | STREAMING_TV}} | deviceTarget{deviceTarget: {deviceOrientation: enum: LANDSCAPE | PORTRAIT, deviceType*: enum: CONNECTED_DEVICE | CONNECTED_TV | DESKTOP | MOBILE, mobileDevice: enum: ANDROID | IPAD | IPHONE | KINDLE_FIRE | KINDLE_FIRE_HD, mobileEnvironment: enum: APP | WEB, mobileOs: enum: ANDROID | IOS}} | dayPartTarget{dayPartTarget: {dayOfWeek*: enum: FRIDAY | MONDAY | SATURDAY | SUNDAY | THURSDAY | TUESDAY | WEDNESDAY, timeOfDay*: {endTime*: string, startTime*: string}}} | contentCategoryTarget{contentCategoryTarget: {contentCategoryId*: string}} | contentGenreTarget{contentGenreTarget: {contentGenre*: enum (73 values - see ENUMS.md)}} | contentRatingTarget{contentRatingTarget: {contentRatingType*: enum: DSP_CONTENT_RATING | TWITCH_CONTENT_RATING, contentRatingTypeDetails*: oneOf: dspContentRating{dspContentRating: {dspContentRating*: enum: RATING_NOT_AVAILABLE | SUITABLE_FOR_ADULTS | SUITABLE_FOR_ALL_AUDIENCES | SUITABLE_FOR_MATURE_AUDIENCES | SUITABLE_FOR_MOST_AUDIENCES_WITH_PARENTAL_GUIDANCE | SUITABLE_FOR_TEEN_AND_OLDER_AUDIENCES}} | twitchContentRating{twitchContentRating: {twitchContentRating*: enum: TWITCH_MODERATE | TWITCH_RESTRICTIVE}}}} | brandSafetyTierTarget{brandSafetyTierTarget: {brandSafetyTier*: enum: EXPANDED | RESTRICTIVE | STANDARD}} | brandSafetyCategoryTarget{brandSafetyCategoryTarget: {brandSafetyCategory*: enum: ACCIDENTS_DISASTERS_AND_TRAGEDIES | ALCOHOL_AND_RELATED_PRODUCTS | BLOOD_GORE_VIOLENCE | CRIME | DRUG_REFERENCES_OR_USE | GAMBLING | HIGHLY_DEBATED_SOCIAL_ISSUES | POLITICS | PROFANITY | RELIGIOUS_CONTENT | SEXUAL_REFERENCES_AND_SUGGESTIVE | SHOCK_AND_HORROR | TOBACCO_AND_RELATED_PRODUCTS | UNRATED_MEDIA_CONTENT | WEAPONS}} | inventorySourceTarget{inventorySourceTarget: {inventorySourceId*: {defaultValue: string}, inventorySourceType*: enum: AMAZON | APD | DEAL | INVENTORY_GROUP | THIRD_PARTY_EXCHANGE}} | adInitiationTarget{adInitiationTarget: {videoInitiationType*: enum: AUTOPLAY | UNKNOWN | USER_INITIATED}} | adPlayerSizeTarget{adPlayerSizeTarget: {adPlayerSize*: enum: LARGE | MEDIUM | SMALL | UNKNOWN}} | videoAdFormatTarget{videoAdFormatTarget: {videoAdFormat*: enum: FULL_EPISODE_PLAYER | INSTREAM | OUTSTREAM}} | thirdPartyTarget{thirdPartyTarget: {thirdPartyTargetDetails*: oneOf: doubleVerifyFraudInvalidTraffic{doubleVerifyFraudInvalidTraffic: {blockAppAndSites: boolean, excludeAppsAndSites: enum: ALLOW_ALL | FRAUD_TRAFFIC_LEVEL_GTE_02 | FRAUD_TRAFFIC_LEVEL_GTE_04 | FRAUD_TRAFFIC_LEVEL_GTE_06 | FRAUD_TRAFFIC_LEVEL_GTE_08 | FRAUD_TRAFFIC_LEVEL_GTE_10 | FRAUD_TRAFFIC_LEVEL_GTE_100 | FRAUD_TRAFFIC_LEVEL_GTE_25 | FRAUD_TRAFFIC_LEVEL_GTE_50, excludeImpressions: boolean}} | doubleVerifyStandardDisplayBrandSafety{doubleVerifyStandardDisplayBrandSafety: {contentCategories: array<enum: AD_SERVER | CELEBRITY_GOSSIP | CULTS_SURVIVALISM | EXTREME_GRAPHIC | GAMBLING | INCENTIVIZED_MALWARE_CLUTTER | INFLAMMATORY_POLITICS_NEWS | NEGATIVE_NEWS_FINANCIAL | NEGATIVE_NEWS_PHARMACEUTICAL | NON_STANDARD_CONTENT_NON_ENGLISH | NON_STANDARD_CONTENT_PARKING_PAGE | OCCULT | PIRACY_COPYRIGHT_INFRINGEMENT | UNMODERATED_UGC_FORUMS_IMAGES_VIDEO>, contentCategoriesWithRisk: array<{key*: string, value*: enum: ALLOW_ALL | HIGH | HIGH_MEDIUM | HIGH_MEDIUM_LOW}>, unknownContent: boolean}} | doubleVerifyBrandSafety{doubleVerifyBrandSafety: {appAgeRating: array<enum: ADULTS_ONLY_18_PLUS | EVERYONE_4_PLUS | MATURE_17_PLUS | TEENS_12_PLUS | TWEENS_9_PLUS | UNKNOWN>, appStarRating: enum: ALLOW_ALL | APP_STAR_RATING_LT_1_POINT_5_STARS | APP_STAR_RATING_LT_2_POINT_5_STARS | APP_STAR_RATING_LT_2_STARS | APP_STAR_RATING_LT_3_POINT_5_STARS | APP_STAR_RATING_LT_3_STARS | APP_STAR_RATING_LT_4_POINT_5_STARS | APP_STAR_RATING_LT_4_STARS, contentCategories: array<enum: AD_SERVER | CELEBRITY_GOSSIP | CULTS_SURVIVALISM | EXTREME_GRAPHIC | GAMBLING | INCENTIVIZED_MALWARE_CLUTTER | INFLAMMATORY_POLITICS_NEWS | NEGATIVE_NEWS_FINANCIAL | NEGATIVE_NEWS_PHARMACEUTICAL | NON_STANDARD_CONTENT_NON_ENGLISH | NON_STANDARD_CONTENT_PARKING_PAGE | OCCULT | PIRACY_COPYRIGHT_INFRINGEMENT | UNMODERATED_UGC_FORUMS_IMAGES_VIDEO>, contentCategoriesWithRisk: array<{key*: string, value*: enum: ALLOW_ALL | HIGH | HIGH_MEDIUM | HIGH_MEDIUM_LOW}>, excludeAppsWithInsufficientRating: boolean, unknownContent: boolean}} | doubleVerifyViewability{doubleVerifyViewability: {averageCompletionAndFullyViewableRateTargeting: enum: ALLOW_ALL | AVG_COMPLETION_FULLY_VIEWABLE_GTE_10 | AVG_COMPLETION_FULLY_VIEWABLE_GTE_20 | AVG_COMPLETION_FULLY_VIEWABLE_GTE_25 | AVG_COMPLETION_FULLY_VIEWABLE_GTE_30 | AVG_COMPLETION_FULLY_VIEWABLE_GTE_35 | AVG_COMPLETION_FULLY_VIEWABLE_GTE_40, brandExposureViewabilityTargeting: enum: ALLOW_ALL | BRAND_EXPOSURE_VIEWABILITY_GTE_10_SEC_AVG_DURATION | BRAND_EXPOSURE_VIEWABILITY_GTE_15_SEC_AVG_DURATION | BRAND_EXPOSURE_VIEWABILITY_GTE_5_SEC_AVG_DURATION, includeUnmeasurableImpressions: boolean, mrcViewabilityTargeting: enum: ALLOW_ALL | MRC_VIEWABILITY_GTE_30 | MRC_VIEWABILITY_GTE_40 | MRC_VIEWABILITY_GTE_50 | MRC_VIEWABILITY_GTE_55 | MRC_VIEWABILITY_GTE_60 | MRC_VIEWABILITY_GTE_65 | MRC_VIEWABILITY_GTE_70 | MRC_VIEWABILITY_GTE_75 | MRC_VIEWABILITY_GTE_80}} | doubleVerifyAuthenticBrandSafety{doubleVerifyAuthenticBrandSafety: {doubleVerifySegmentId: string}} | doubleVerifyCustomContextualSegmentId{doubleVerifyCustomContextualSegmentId: {doubleVerifySegmentId: string}} | doubleVerifyAuthenticAttention{doubleVerifyAuthenticAttention: {universalAttention*: boolean}} | integralAdScienceFraudInvalidTraffic{integralAdScienceFraudInvalidTraffic: {targetSetting: enum: ALLOW_ALL | FRAUD_INVALID_TRAFFIC_EXCLUDE_HIGH_MODERATE_RISK | FRAUD_INVALID_TRAFFIC_EXCLUDE_HIGH_RISK}} | integralAdScienceBrandSafety{integralAdScienceBrandSafety: {excludeContent: boolean, iasBrandSafetyAdult: enum: ALLOW_ALL | BRAND_SAFETY_EXCLUDE_HIGH_AND_MODERATE_RISK | BRAND_SAFETY_EXCLUDE_HIGH_RISK, iasBrandSafetyAlcohol: enum: ALLOW_ALL | BRAND_SAFETY_EXCLUDE_HIGH_AND_MODERATE_RISK | BRAND_SAFETY_EXCLUDE_HIGH_RISK, iasBrandSafetyGambling: enum: ALLOW_ALL | BRAND_SAFETY_EXCLUDE_HIGH_AND_MODERATE_RISK | BRAND_SAFETY_EXCLUDE_HIGH_RISK, iasBrandSafetyHateSpeech: enum: ALLOW_ALL | BRAND_SAFETY_EXCLUDE_HIGH_AND_MODERATE_RISK | BRAND_SAFETY_EXCLUDE_HIGH_RISK, iasBrandSafetyIllegalDownloads: enum: ALLOW_ALL | BRAND_SAFETY_EXCLUDE_HIGH_AND_MODERATE_RISK | BRAND_SAFETY_EXCLUDE_HIGH_RISK, iasBrandSafetyIllegalDrugs: enum: ALLOW_ALL | BRAND_SAFETY_EXCLUDE_HIGH_AND_MODERATE_RISK | BRAND_SAFETY_EXCLUDE_HIGH_RISK, iasBrandSafetyOffensiveLanguage: enum: ALLOW_ALL | BRAND_SAFETY_EXCLUDE_HIGH_AND_MODERATE_RISK | BRAND_SAFETY_EXCLUDE_HIGH_RISK, iasBrandSafetyViolence: enum: ALLOW_ALL | BRAND_SAFETY_EXCLUDE_HIGH_AND_MODERATE_RISK | BRAND_SAFETY_EXCLUDE_HIGH_RISK}} | integralAdScienceViewability{integralAdScienceViewability: {standard*: enum: GROUPM | MRC | NONE | PUBLICIS, viewabilityTargeting: enum: ALLOW_ALL | VIEWABILITY_TIER_GT_40 | VIEWABILITY_TIER_GT_50 | VIEWABILITY_TIER_GT_60 | VIEWABILITY_TIER_GT_70 | VIEWABILITY_TIER_LT_40}} | integralAdScienceContextualTargeting{integralAdScienceContextualTargeting: {topicalSegments: array<string>, verticalSegments: array<string>}} | integralAdScienceContextualAvoidance{integralAdScienceContextualAvoidance: {avoidanceSegments: array<string>}} | pixalateFraudInvalidTraffic{pixalateFraudInvalidTraffic: {excludeAppsAndDomains: boolean, excludeIpAddressAndUserAgents: boolean, excludeOttAndMobileDevices: boolean, excludeRemovedAppsFromAppStores: boolean}} | integralAdScienceQualitySync{integralAdScienceQualitySync: {segmentId: string}} | newsGuardBrandGuardTrustedNewsTargeting{newsGuardBrandGuardTrustedNewsTargeting: {targetingList: array<enum: BASIC_INCLUDE | BUSINESS_INCLUDE | COMMUNITY_INCLUDE | HEALTH_INCLUDE | HIGH_INCLUDE | LIFESTYLE_INCLUDE | LOCAL_INCLUDE | MAX_INCLUDE | POLITICS_INCLUDE | TECH_INCLUDE>}} | newsGuardBrandGuardMisinformationSafety{newsGuardBrandGuardMisinformationSafety: {avoidanceList: array<enum: AI_GENERATED_MFA | BASIC_EXCLUDE | CLIMATE_MISINFORMATION | COVID_MISINFORMATION | ELECTION_MISINFORMATION | HEALTH_MISINFORMATION | HIGH_EXCLUDE | ISRAEL_HAMAS_MISINFORMATION | MAX_EXCLUDE | MISINFORMATION_SITES | OPINIONATED_NEWS | QANON_MISINFORMATION | UKRAINE_MISINFORMATION | VACCINE_MISINFORMATION>}}, thirdPartyTargetType*: enum (16 values - see ENUMS.md)}} | themeTarget{themeTarget: {matchType*: enum: PRODUCTS_SIMILAR_TO_ADVERTISED_PRODUCTS}} | contentInstreamPositionTarget{contentInstreamPositionTarget: {instreamPosition*: enum: MID_ROLL | POST_ROLL | PRE_ROLL | UNKNOWN}} | contentOutstreamPositionTarget{contentOutstreamPositionTarget: {outstreamPosition*: enum: ACCOMPANYING_CONTENT | INTERSTITIAL | STANDALONE | UNKNOWN}} | videoContentDurationTarget{videoContentDurationTarget: {duration*: enum: EXTENDED | LONG | MEDIUM | SHORT | UNKNOWN}} | foldPositionTarget{foldPositionTarget: {foldPosition*: enum: ABOVE_THE_FOLD | BELOW_THE_FOLD | UNKNOWN}} | nativeContentPositionTarget{nativeContentPositionTarget: {nativePosition*: enum: IN_ARTICLE | IN_FEED | PERIPHERAL | RECOMMENDATION | UNKNOWN}} | placementTypeTarget{placementTypeTarget: {placementType*: enum: REWARDED}}
- `targets[].targetType` **REQUIRED**: enum (26 values - see ENUMS.md)

## AMAZON_DSP - DELETE

- `targetIds` **REQUIRED**: array<string>