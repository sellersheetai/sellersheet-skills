---
name: listing-health
description_zh: "listing 被抑制、listing 健康检查、商品不可售、搜索不到商品、listing 报错、问题修复优先级、变体异常。"
description_en: "Use when a seller asks which Amazon listings are suppressed, not buyable or hidden from search; why a listing…"
author: SellerSheet AI
version: 0.18.1
metadata: {apis: [data, listings], pattern: Gate}
description: >-
  Use when a seller asks which Amazon listings are suppressed, not buyable or hidden from search; why a
  listing stopped selling; what a listing issue means and which to fix first; or which variation families
  have a broken child — "audit my listings", "why is this ASIN suppressed", "fix my listing errors". Counts
  the store from the warehouse without calling Amazon, confirms live, agrees each fix with the seller,
  applies it and re-reads. Do NOT use for writing new copy or images (image-gen) or for sales, inventory
  or ads reporting (report-data, amazon-ads).
  中文触发词：listing 被抑制、listing 健康检查、商品不可售、搜索不到商品、listing 报错、问题修复优先级、变体异常。
---

# Listing health

Find what is wrong with a store's Amazon listings, fix what costs sales first, and confirm Amazon took
the fix. Preflight first: [`sellersheet-shared`](../sellersheet-shared/SKILL.md).

## 1. Count from the warehouse (no Amazon call)

Start from the listings report, so SKUs the seller no longer lists don't count:

```
query_report_data(
    store='myStore-AE',
    tables=['rpt_get_merchant_listings_all_data'],
    joins=[{'table': 'listing_images',
            'on': {'store_id': 'store_id', 'country_code': 'country_code', 'seller_sku': 'seller_sku'}}],
    columns=['listing_images.issue_enforcements'],
    aggregations=[{'column': 'rpt_get_merchant_listings_all_data.seller_sku', 'op': 'count', 'alias': 'skus'}],
    group_by=['listing_images.issue_enforcements'],
    filters=[{'column': 'listing_images.issue_severity', 'op': 'eq', 'value': 'ERROR'}],
    order_by=[{'column': 'skus', 'dir': 'desc'}],
    report_date='latest',
)
```

Then list the SKUs of one group, adding a `contains` filter on `listing_images.issue_enforcements` and the
columns `seller_sku`, `listing_images.issues` and `listing_images.issues_checked_at`. `issues` is large, so
ask for it only on the SKUs you are working on. `issue_severity` NULL means Amazon has not been asked yet:
say so, never report it as healthy.

## 2. Work in this order

A listing can carry several enforcements; take the first that applies.

| `issue_enforcements` | What it means | What to do |
|---|---|---|
| `LISTING_SUPPRESSED` | The listing can't be bought | First. Fix what `issues` names |
| `CATALOG_ITEM_REMOVED` | Amazon removed the catalog item, so no offer on it can sell | Read the issue. If it names nothing the seller can change, tell them to open a case in Seller Central; don't keep patching |
| `SEARCH_SUPPRESSED` | Can be bought by link, hidden from search | Second |
| `ATTRIBUTE_SUPPRESSED` | Amazon rejected one value; the listing usually still sells | Report it and fix it at the seller's next edit; don't bulk-patch |
| empty, with `issue_severity` `ERROR` | A submitted value was refused | Fix at the next publish |
| `issue_severity` `WARNING` | Advice | Mention the count; act only if asked |

An issue with empty `attributeNames` usually has no value to change, such as "You need approval to list in
this brand". Tell the seller what Amazon asks for instead of patching.

Common codes (Amazon writes the text in the marketplace's language, and codes can change, so trust the text):

| Code | Usually means | Fix |
|---|---|---|
| 18320 | Main image missing or wrong | Upload a compliant MAIN image |
| 100588 | MAIN image background is not pure white | Replace the image |
| 100581 | An image has text, a logo, a graphic or a watermark | Amazon often says no action is required; a clean image if the seller wants it shown |
| 100476 | Title too long to use Item Highlights (over 75 characters) | Shorten the title |
| 99300 | A field has promotional claims or external links | Rewrite the field the issue names |
| 20000 | Amazon cannot fetch an image URL | Resubmit from a URL Amazon can reach |
| 8541 | A listing value contradicts the catalog (the text names which, often brand) | Correct the value, or list under the right ASIN |

## 3. Confirm live before acting

The warehouse can be up to 30 days old for a change Amazon made itself. Read up to 20 SKUs in one call, and
work from this answer:

```
listings_searchListingsItems(store, identifiers=[...], identifiers_type='SKU',
                             included_data=['summaries', 'issues', 'relationships'], page_size=20)
```

## 4. Agree each fix (gate)

Show the seller, per SKU: the issue, the change you propose, and what happens if it is left alone. If they
work in a sheet, write this there. Change nothing until they approve it.

## 5. Apply, then re-read

1. `listings_getListingsItem(store, sku)` for the current values and `productType`. A patch sends each
   attribute's value array in exactly that shape.
2. `listings_patchListingsItem(store, sku, product_type, patches, mode='VALIDATION_PREVIEW')`. When it answers
   `VALID`, repeat without `mode`.
3. `listings_getListingsItem` again about 30 seconds later confirms the submission. An image or a suppression
   can take longer to clear, so re-read later before trying again.

## Variation families

- A family is one `parent_sku`. The row whose `variation_role` is `parent` is not sold itself, so an empty
  price or FNSKU there is normal.
- Families with a child in error: query `listing_images`, group by `listing_images.parent_sku`, and filter
  `variation_role` = `child` and `issue_severity` = `ERROR`.
- `standalone` describes the SKU, not the ASIN. A standalone SKU can sit on an ASIN that belongs to a family,
  which is a second offer outside the family. `catalogItems_getCatalogItem(store, asin, includedData=['relationships'])`
  shows the ASIN's parent.

## When did it change?

`listing_images` holds the current state. `sp_listing_events` holds each status, issue and brand-content event
Amazon sent, so it can date a suppression:

```
query_report_data(
    store='myStore-AE',
    tables=['sp_listing_events'],
    columns=['sp_listing_events.event_time', 'sp_listing_events.type', 'sp_listing_events.status',
             'sp_listing_events.severities', 'sp_listing_events.enforcements'],
    filters=[{'column': 'sp_listing_events.sku', 'op': 'eq', 'value': 'MYSKU-001'}],
    order_by=[{'column': 'sp_listing_events.event_time', 'dir': 'desc'}],
)
```

`enforcements` containing `LISTING_SUPPRESSED` dates the suppression, and `severities` = `NONE` dates the all-clear.
To see whether it came before a sales drop, read `rpt_dk_sales_traffic_by_asin` for the ASIN in a second query and
compare the dates; don't join them.

A store's history starts the day it began receiving these notifications, which for most stores is recent, so no
row does not prove nothing changed. [`report-data`](../report-data/SKILL.md) has the columns.

## Knowing sooner

A listing is re-read within a day of the seller's own edit. For an alert when Amazon changes a listing's
status or issues, the seller sets up a webhook in the SellerSheet web app, under Settings → Webhooks.
