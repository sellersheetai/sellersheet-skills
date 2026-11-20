---
name: ads-v3-archive
description_zh: "2026-09-01 之前的亚马逊广告历史数据、旧版 v3 广告报表（rpt_sp_、rpt_sb_、rpt_sd_ 表）、跨 2026-09-01 的广告数据拆分与列名对照。"
description_en: "Temporary skill, removed on 2026-12-31, for Amazon Ads performance on days before 2026-09-01."
author: SellerSheet AI
description: >-
  Temporary skill, removed on 2026-12-31, for Amazon Ads performance on days before 2026-09-01. Covers the retired Ads Reporting v3 tables rpt_sp_*, rpt_sb_* and rpt_sd_* (campaigns, ad groups, keywords, targets, search terms, placement, advertised and purchased products), their columns, how each column maps to its Marketing Stream name, the attribution windows, and how to split a date range at 2026-09-01. Do NOT use for any day from 2026-09-01 (use report-data and amazon-ads, the Stream tables and views) or for the negative keyword and target lists (use report-data).
  中文触发词：2026-09-01 之前的亚马逊广告历史数据、旧版 v3 广告报表（rpt_sp_、rpt_sb_、rpt_sd_ 表）、跨 2026-09-01 的广告数据拆分与列名对照。
version: 0.20.2
metadata: {apis: [data], pattern: Reference}
---

# Ads v3 archive — removed on 2026-12-31

This skill and the 19 tables it describes are removed on 2026-12-31. After that date, Ads
performance history starts on 2026-09-01.

**The rule:** Ads performance from 2026-09-01: the Stream tables and views; before 2026-09-01:
see ads-v3-archive (until 2026-12-31). Never add the two; split a range at 2026-09-01.

## When to use it

- **Only for days before 2026-09-01.** From 2026-09-01 every day comes from the Stream tables
  and views (`report-data`, `amazon-ads`), even where a v3 table also holds a row for that day.
- Stream also holds some days before 2026-09-01. Ignore them: before 2026-09-01 the v3 tables
  are the source.
- Not for the negative keyword and target lists (`rpt_sp_negative_keywords`,
  `rpt_sp_campaign_negative_keywords`, `rpt_sp_negative_targets`,
  `rpt_sp_campaign_negative_targets`, `rpt_sb_negative_keywords`, `rpt_sd_negative_targets`):
  they are current lists, still synced, and `report-data` documents them.

Run the preflight in [`sellersheet-shared`](../sellersheet-shared/SKILL.md) first. The tables
need Amazon Advertising access for the store. Read them with `query_report_data`, the same way
as any synced table; the store ref filters the marketplace.

## The 19 tables

Every column, with its type and notes: `reference/<table>.json` in this skill's folder. Each
reference carries `deprecated: true`: the table is retired, not broken, and stays queryable until
2026-12-31. Every table is daily, keyed on `report_date`.

| v3 table | One row per | From 2026-09-01, read |
|---|---|---|
| `rpt_sp_campaigns`, `rpt_sb_campaigns`, `rpt_sd_campaigns` | campaign × day | `v_ads_campaign_daily` |
| `rpt_sp_ad_groups`, `rpt_sb_ad_groups`, `rpt_sd_ad_groups` | ad group × day | `rpt_ads_performance_daily`, summed by `ad_group_id` (names from `rpt_ads_ad_groups`) |
| `rpt_sp_keywords`, `rpt_sb_keywords` | keyword × day | `v_ads_target_daily` |
| `rpt_sp_targets`, `rpt_sb_targets`, `rpt_sd_targets` | product, audience or theme target × day | `v_ads_target_daily` |
| `rpt_sp_search_terms`, `rpt_sb_search_terms` | search term × keyword or target × day | `v_ads_search_term_daily` |
| `rpt_sp_campaign_placement` | campaign × placement × day | `v_ads_placement_daily` |
| `rpt_sp_advertised_products`, `rpt_sb_advertised_products`, `rpt_sd_advertised_products` | advertised product × day | `v_ads_product_daily` |
| `rpt_sp_purchased_products`, `rpt_sb_purchased_products` | advertised × purchased product × day | `rpt_ads_converted_product_daily` |

`sp` is Sponsored Products, `sb` Sponsored Brands, `sd` Sponsored Display: one table per ad
product. The Stream relations hold every ad product, so filter `ad_product` =
`'Sponsored Products'`, `'Sponsored Brands'` or `'Sponsored Display'` to match a v3 table.

### Gaps to know

- **`rpt_sp_keywords` and `rpt_sp_targets` are daily and complete from 2026-07-02.** Rows dated
  2026-07-01 and earlier are partial or trailing-window totals: never sum them. For those days use
  the campaign, ad group, search term or advertised product table. The two tables are disjoint
  (keywords in one, product and auto targets in the other): add them for every target.
- **`rpt_sp_campaign_placement` was not collected for every store.** Where a store has rows, they
  add up to its campaign totals. No rows for a store means not collected, not zero traffic.
- History starts in April 2026 at the earliest, later for a store that connected Ads later.
- A day with no v3 row had no delivery, or was not collected. Say so; never fill it from Stream.

## Windows

Stream carries one attribution window per campaign, `attribution_window_days`: **7 days for a
seller's Sponsored Products, 14 for a vendor's Sponsored Products, Sponsored Brands and
Sponsored Display.** v3 named its windows in the column:

| v3 | Windows | Same as Stream's |
|---|---|---|
| Sponsored Products | `_1d`, `_7d`, `_14d`, `_30d` columns | a seller: the `_7d` columns; a vendor: the `_14d` columns |
| `rpt_sp_campaign_placement` | `_14d` only | a vendor only. For a seller there is no 7-day column: across 2026-09-01 compare impressions, clicks and cost, and label each half's conversions with its window |
| Sponsored Brands, Sponsored Display | no suffix = 14 days, views included | the same columns |
| `rpt_sb_purchased_products` | `_14d` | the same columns |

Label every conversion number with its window. Never put a 14-day number next to a 7-day one as
if they were the same measure.

## Column map: v3 → Stream

Every table:

| v3 | Stream |
|---|---|
| `report_date`, `impressions`, `clicks` | the same |
| `cost` (Sponsored Products also `spend`, the same number) | `total_cost` |
| `campaign_id`, `ad_group_id`, `ad_id` | the same |
| `keyword_id`, `target_id` | `target_id` |
| `campaign_name`, `campaign_status`, `ad_group_name` | `campaign_name`, `campaign_state`, `ad_group_name`: the Stream views carry the current name and state, a v3 row the day's |
| `campaign_budget_amount` (SP), `campaign_budget` (SB, SD) | `campaign_budget` |
| `currency_code` (`currency` on placement) | `currency` |

Sponsored Products (the `_7d` names; a vendor's are the `_14d` ones):

| v3 | Stream |
|---|---|
| `purchases_7d`, `sales_7d` | `purchases`, `sales` |
| `units_sold_clicks_7d` | `units_sold_from_clicks` |
| `purchases_same_sku_7d`, `attributed_sales_same_sku_7d`, `units_sold_same_sku_7d` | `purchases_promoted`, `sales_promoted`, `units_sold_promoted` |
| `purchases_other_sku_7d`, `sales_other_sku_7d`, `units_sold_other_sku_7d` | `purchases_halo`, `sales_halo`, `units_sold_halo` |
| `keyword`, `targeting` | `keyword_text`, `expression` |
| `match_type`, `keyword_bid` | `match_type`, `bid` |
| `placement_classification` | `placement` (the same values) |
| `advertised_asin`, `advertised_sku`, `search_term` | the same |
| `purchased_asin` | `converted_asin` |

Sponsored Brands and Sponsored Display (14 days):

| v3 | Stream |
|---|---|
| `purchases`, `sales`, `units_sold` | the same |
| `purchases_clicks`, `sales_clicks`, `units_sold_clicks` | `purchases_from_clicks`, `sales_from_clicks`, `units_sold_from_clicks` |
| `purchases_promoted`, `sales_promoted` (SB) | the same |
| `purchases_promoted_clicks`, `sales_promoted_clicks` (SD) | `purchases_from_clicks_promoted`, `sales_from_clicks_promoted` |
| `new_to_brand_purchases`, `new_to_brand_sales`, `new_to_brand_units_sold`, `new_to_brand_detail_page_views` | the same; their `_clicks` columns are `_from_clicks` (SD's `new_to_brand_detail_page_view_clicks` / `_views` are `new_to_brand_detail_page_views_from_clicks` / `_from_views`) |
| `detail_page_views`, `add_to_cart` | the same; `_clicks` is `_from_clicks`, `_views` (SD) is `_from_views` |
| `branded_searches`, `branded_searches_views` (SD) | `branded_searches`, `branded_searches_from_views`, on `rpt_ads_performance_daily` |
| `viewable_impressions` (SB), `impressions_views` (SD) | `viewable_impressions` |
| `video_first_quartile_views`, `video_midpoint_views`, `video_third_quartile_views`, `video_complete_views`, `video_5_second_views`, `video_unmutes` | `first_quartile_video_ad`, `midpoint_video_ad`, `third_quartile_video_ad`, `complete_views_video_ad`, `five_second_views_video_ad`, `unmutes_video_ad` |
| `keyword` (SB keywords) | `keyword_text` |
| `targeting_text`, `targeting_expression` | `keyword_text` for a Sponsored Brands theme, `expression` for a product or audience target |
| `asin`, `sku` (SD advertised products) | `advertised_asin`, `advertised_sku` |

`rpt_sb_purchased_products` → `rpt_ads_converted_product_daily` with `ad_product` =
`'Sponsored Brands'`:

| v3 | Stream |
|---|---|
| `orders_14d`, `sales_14d`, `units_sold_14d` | `purchases`, `sales`, `units_sold` |
| `new_to_brand_purchases_14d`, `new_to_brand_sales_14d`, `new_to_brand_units_sold_14d` | `new_to_brand_purchases`, `new_to_brand_sales`, `new_to_brand_units_sold` |
| `purchased_asin` | `converted_asin` |
| `attribution_type` `'Promoted'` / `'Brand Halo'` | `product_relevance` `'Promoted'` / `'Brand halo'` |

**Match targets on `target_id`, not on their text.** The text changes form across the boundary:
a Sponsored Brands theme is `keywords-related-to-your-brand` in v3 and
`KEYWORDS_RELATED_TO_YOUR_BRAND` in Stream; a Sponsored Display clause is `asin="B0XXXXXXXX"` in
v3 and a JSON clause list in Stream.

**No Stream column:**

- Ratios and rates (`cost_per_click`, `click_through_rate`, `acos_*`, `roas_*`, `*_rate`,
  `*_percentage`, `e_cp_*`): compute them from the sums on either side.
- Sponsored Products' 1-day and 30-day columns, and the window Stream does not carry (a seller's
  `_14d`, a vendor's `_7d`).
- Impression share, Sponsored Display reach and frequency, the budget-rule columns, and
  descriptive columns such as `cost_type`, `bid_optimization`, `product_name`.

## Split a range at 2026-09-01

"Never add the two" means: never add both sources' numbers for the same day. They count the same
spend twice.

1. Days before 2026-09-01: the v3 table, `report_date` `lt` `2026-09-01`.
2. Days from 2026-09-01: the Stream relation from the table above, `report_date` `gte`
   `2026-09-01`, with the `ad_product` filter.
3. The two queries cover different days, so a range total adds them column by column, through
   the column map, on the same window. Compute ratios from those totals, never by averaging the
   two halves' ratios.
4. Where the windows cannot match (a seller's placement), show the halves side by side, each
   with its window.

## Query examples

Sponsored Products campaigns in August 2026 (a seller: the 7-day columns). A campaign renamed
in the window shows once per name; group by `campaign_id` alone and take its current name from
`rpt_ads_campaigns` when that matters:

```json
{"store": "myStore-US", "tables": ["rpt_sp_campaigns"],
 "columns": ["rpt_sp_campaigns.campaign_id", "rpt_sp_campaigns.campaign_name"],
 "aggregations": [{"column": "rpt_sp_campaigns.impressions", "op": "sum", "alias": "impressions"},
                  {"column": "rpt_sp_campaigns.clicks", "op": "sum", "alias": "clicks"},
                  {"column": "rpt_sp_campaigns.cost", "op": "sum", "alias": "spend"},
                  {"column": "rpt_sp_campaigns.purchases_7d", "op": "sum", "alias": "orders"},
                  {"column": "rpt_sp_campaigns.sales_7d", "op": "sum", "alias": "sales"}],
 "group_by": ["rpt_sp_campaigns.campaign_id", "rpt_sp_campaigns.campaign_name"],
 "filters": [{"column": "rpt_sp_campaigns.report_date", "op": "gte", "value": "2026-08-01"},
             {"column": "rpt_sp_campaigns.report_date", "op": "lt", "value": "2026-09-01"}],
 "order_by": [{"column": "spend", "dir": "desc"}]}
```

Sponsored Brands campaigns from 2026-08-15 to 2026-09-14: two queries, one per side of the
boundary, the same aliases, then add them per `campaign_id`:

```json
{"store": "myStore-US", "tables": ["rpt_sb_campaigns"],
 "columns": ["rpt_sb_campaigns.campaign_id"],
 "aggregations": [{"column": "rpt_sb_campaigns.clicks", "op": "sum", "alias": "clicks"},
                  {"column": "rpt_sb_campaigns.cost", "op": "sum", "alias": "spend"},
                  {"column": "rpt_sb_campaigns.purchases", "op": "sum", "alias": "orders"},
                  {"column": "rpt_sb_campaigns.sales", "op": "sum", "alias": "sales"}],
 "group_by": ["rpt_sb_campaigns.campaign_id"],
 "filters": [{"column": "rpt_sb_campaigns.report_date", "op": "gte", "value": "2026-08-15"},
             {"column": "rpt_sb_campaigns.report_date", "op": "lt", "value": "2026-09-01"}]}
```

```json
{"store": "myStore-US", "tables": ["v_ads_campaign_daily"],
 "columns": ["v_ads_campaign_daily.campaign_id"],
 "aggregations": [{"column": "v_ads_campaign_daily.clicks", "op": "sum", "alias": "clicks"},
                  {"column": "v_ads_campaign_daily.total_cost", "op": "sum", "alias": "spend"},
                  {"column": "v_ads_campaign_daily.purchases", "op": "sum", "alias": "orders"},
                  {"column": "v_ads_campaign_daily.sales", "op": "sum", "alias": "sales"}],
 "group_by": ["v_ads_campaign_daily.campaign_id"],
 "filters": [{"column": "v_ads_campaign_daily.ad_product", "op": "eq", "value": "Sponsored Brands"},
             {"column": "v_ads_campaign_daily.report_date", "op": "gte", "value": "2026-09-01"},
             {"column": "v_ads_campaign_daily.report_date", "op": "lt", "value": "2026-09-15"}]}
```

Sponsored Products search terms that sold in July and August 2026 (a seller: 7-day columns):

```json
{"store": "myStore-US", "tables": ["rpt_sp_search_terms"],
 "columns": ["rpt_sp_search_terms.search_term", "rpt_sp_search_terms.keyword",
             "rpt_sp_search_terms.match_type"],
 "aggregations": [{"column": "rpt_sp_search_terms.clicks", "op": "sum", "alias": "clicks"},
                  {"column": "rpt_sp_search_terms.cost", "op": "sum", "alias": "spend"},
                  {"column": "rpt_sp_search_terms.purchases_7d", "op": "sum", "alias": "orders"},
                  {"column": "rpt_sp_search_terms.sales_7d", "op": "sum", "alias": "sales"}],
 "group_by": ["rpt_sp_search_terms.search_term", "rpt_sp_search_terms.keyword",
              "rpt_sp_search_terms.match_type"],
 "filters": [{"column": "rpt_sp_search_terms.report_date", "op": "gte", "value": "2026-07-01"},
             {"column": "rpt_sp_search_terms.report_date", "op": "lt", "value": "2026-09-01"}],
 "having": [{"column": "orders", "op": "gte", "value": 1}],
 "order_by": [{"column": "sales", "dir": "desc"}], "limit": 50}
```

Stream names slightly fewer search terms than v3 did, so a term-level total can step down by a
fraction of a percent at 2026-09-01; campaign and target totals carry across.
