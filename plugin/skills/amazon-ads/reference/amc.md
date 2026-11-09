# Amazon Marketing Cloud (AMC)

AMC is Amazon's clean room: the advertiser's own ad events (impressions, clicks, spend) and
shopping events (purchases, new-to-brand, add-to-cart), queried in SQL, answered only as
aggregates. Look in this order:

1. Spend, clicks, ACOS, orders, search-term waste, what a click ended up buying: the report
   warehouse (`rpt_sp_*`, see `report-data`). Not AMC.
2. The questions in "Already synced" below: read the table.
3. Anything else: run your own query.

## Turn it on (once per store and Ads country)

`ads_amc_turn_on`. **Ask the seller first**: it creates an AMC instance on their Amazon Ads
account, and Amazon cannot delete it. Calling it again is safe. Amazon offers AMC to
advertisers with campaigns live in the last 28 days. `get_user_context` shows each store's
`amc` per country.

**Refused with `amc_terms_not_accepted`.** Amazon can create the instance before its AMC terms
are accepted and then refuses every query, so this call checks them. The instance is saved and
nothing is lost. Only the seller can accept, once per region (NA, EU or FE), with the Amazon
login that connected Ads. Pass this on, with the address as text rather than a link:

> Paste https://advertising.amazon.com/marketing-cloud into the browser you normally use for
> this store and accept the AMC terms. If a colleague connected Ads, ask them to do this step.

A login new to AMC is first asked to create an AMC account with the same e-mail address. Once
the terms are accepted, the synced reports start at their next scheduled run; calling
`ads_amc_turn_on` again confirms it.

## Already synced

With AMC on, SellerSheet runs these queries and keeps the rows. `list_amc_templates` gives each
one's question, SQL, how to read its rows and its table; `get_table_schema` gives the columns;
`query_report_data` reads them.

| Question | Table | New rows |
|---|---|---|
| New-to-brand share of each campaign's purchases | `rpt_amc_ntb_by_campaign` | weekly |
| Clicks, spend and purchases by hour of day | `rpt_amc_hour_of_day` | weekly |
| Add-to-cart and orders by search term | `rpt_amc_atc_by_search_term` | weekly |
| Campaigns that reach the same shoppers | `rpt_amc_campaign_overlap` | every 4 weeks |
| Ads seen per shopper against buying | `rpt_amc_impressions_per_shopper` | every 4 weeks |
| First and last search term clicked before buying | `rpt_amc_first_vs_attributed_term` | every 4 weeks |
| Keywords that sell the brand's other products | `rpt_amc_keyword_halo` | every 4 weeks |
| Advertised products that bring shoppers to the brand | `rpt_amc_ntb_gateway_asins` | every 4 weeks |
| How long after the ad people buy | `rpt_amc_time_to_conversion` | every 4 weeks |

- A weekly table covers 7 days and runs Monday 00:00 in the marketplace's zone. A four-weekly
  one covers 28 days and runs 15 days after the period ends, once attribution has settled.
- `period_start` is the first marketplace-local day of the period, not a day of activity.
- Each period has one row with `hidden` true: everything AMC suppressed under its privacy floor,
  summed. Totals include it; per-group answers leave it out.
- Read the template's `how_to_read` before quoting a number.

Two more are not synced by default: the next product after a first purchase
(`AMC_CROSS_SELL_NEXT_PURCHASE`) and the campaigns clicked before a first purchase
(`AMC_PATH_TO_CONVERSION`). Take their SQL from `list_amc_templates` and run it yourself.

## Run your own query

A template's SQL is the quickest start for another window or grouping.

1. `ads_get_data_source` for each table you will use: its columns, and each column's privacy
   class and minimum shoppers per row.
2. A new query: `ads_create_workflow_execution` with `dry_run=true` first. AMC checks the SQL
   and the window in seconds without running it; poll it like any run — `SUCCEEDED` means
   valid, `REJECTED` carries the reason.
3. `ads_create_workflow_execution` with the SQL and the window — for a calendar match with the
   Ads reports use `time_window_type='EXPLICIT'` and the marketplace's own time zone
   (`time_window_time_zone`, e.g. `Asia/Dubai`). The window end is exclusive.
4. `ads_get_workflow_execution` every 15–30 s until `SUCCEEDED` (usually under two minutes).
   `REJECTED` means AMC refused the SQL; `data.status_reason` names the column or the syntax
   error — fix and resubmit.
5. `ads_get_workflow_execution_download_urls` for the rows, up to 20 MB
   (`data.row_count_complete` is false past it).

AMC runs at most 10 queries at a time per instance. `ads_list_workflow_executions` lists the
instance's runs, newest first (the last 7 days unless you give `workflow_id` or
`min_creation_time`; dry runs are not listed). `ads_update_workflow_execution` cancels a run
still `PENDING` or `RUNNING`.

- The final SELECT must aggregate.
- Never alias a column with a SQL keyword (`hour`, `date`): the query is `REJECTED`.
- For numbers that no longer change, use `amazon_attributed_events_by_conversion_time`: its
  window is complete once it ends. The `by_traffic_time` table, the view the Sponsored Products
  console uses, keeps adding purchases for up to 30 days after the window.
- The attributed-events tables' `detail_page_view` and `add_to_cart` columns are 0 for Sponsored
  Products. For cart events use `conversions` (`event_subtype = 'shoppingCart'`).

## The privacy floor

AMC hides any value a result row could use to single out shoppers:

- `VERY_HIGH` columns (`user_id`, `ip_address`) never appear in the final SELECT — use them in
  joins and `COUNT(DISTINCT …)` only. A query that outputs one is `REJECTED`.
- A row is kept, but its dimensions are blanked, when it covers fewer shoppers than the
  column's minimum (2 for campaign, ad group, search term; 100 for bid, cost and postcode
  columns). The rows still count in totals; `data.hidden_rows` says how many.
- For a small advertiser most per-search-term rows come back blank. Group by campaign, match
  type or a keyword theme first; break a group down only when it is large.

## Numbers that differ from the Ads reports

- `spend` is in microcents: divide by 100,000,000.
- `purchases` counts the advertised product only. `total_purchases` adds the brand's other
  products — that is what the Ads reports call purchases.
- AMC counts slightly fewer impressions than the Ads reports; clicks and spend match.

## A query no template covers: did the clickers of a term buy later?

```sql
WITH clk AS (SELECT user_id, customer_search_term, MIN(event_dt_utc) AS first_click
             FROM sponsored_ads_traffic WHERE clicks > 0 AND customer_search_term IS NOT NULL
             GROUP BY user_id, customer_search_term),
     buy AS (SELECT user_id, MIN(event_dt_utc) AS first_buy FROM conversions
             WHERE event_category = 'purchase' GROUP BY user_id),
     attr AS (SELECT customer_search_term, SUM(purchases) AS attributed_purchases
              FROM amazon_attributed_events_by_traffic_time GROUP BY customer_search_term)
SELECT c.customer_search_term, COUNT(DISTINCT c.user_id) AS clickers,
       COUNT(DISTINCT IF(b.first_buy > c.first_click, c.user_id, NULL)) AS clickers_who_bought_later,
       MAX(a.attributed_purchases) AS attributed_purchases
FROM clk c LEFT JOIN buy b ON b.user_id = c.user_id
LEFT JOIN attr a ON a.customer_search_term = c.customer_search_term
GROUP BY c.customer_search_term
```

Sum the rows with no `attributed_purchases` for the zero-order terms as a group: per term, most
come back blank for a small advertiser. A named zero-order term whose clickers never bought
later is safe to negate.

## Save and schedule a query

Ask the seller first. `ads_create_workflow` saves the SQL under an id of your choosing;
`ads_create_schedule` runs it Daily or Weekly. Each run appears in
`ads_list_workflow_executions`, and its result can be downloaded for about a day, so read each
run in time. `ads_list_workflows` and `ads_list_schedules` name SellerSheet's synced entries in
`data.synced_ids`; those are read-only.

## Build an audience from a query

Ask the seller first: an audience that works cannot be changed, only replaced.

1. Count the shoppers with `ads_create_workflow_execution`, over the same tables without
   `_for_audiences`. Amazon fails an audience under 2,000; aim for 2,500.
2. `ads_create_query_based_audience` with SQL over the `*_for_audiences` tables whose SELECT
   returns `user_id`. Poll `ads_get_query_based_audience_by_audience_execution_id`.
3. When it is `SUCCEEDED`, find its `audienceId` with `ads_list_targetable_entities`. Use it as
   a Sponsored Products or Brands bid adjustment (`ads_update_campaign`) or a Sponsored Display
   target.

`ads_create_lookalike_audience` models shoppers similar to a seed of 500 to 500,000.
`ads_update_query_based_audience_by_audience_execution_id` fixes a `FAILED` audience only.
