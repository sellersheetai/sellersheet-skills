# Intake — collected and confirmed BEFORE anything is created on Amazon

Print this checklist back to the user with ✓ (have it), ✗ (missing) or ? (unsure) per line.
Any ✗ on a REQUIRED line stops the workflow until the user answers. Never fill a ✗ with a
guess; never call `create_sta_sheet` or `orchestrate_fba_packing` with a ✗ outstanding.

| # | Field | Required | Mode A source (SellerSheet FBA spreadsheet) | Mode B source | Valid values |
|---|---|---|---|---|---|
| 1 | Store (`<store>-<CC>`) | always | `get_user_context().data.stores[].store_refs` | same | one ref, verbatim |
| 2 | Ship-from address | always | `Shipment Setting` row by `warehouseCode` (`<store>-<CC>-<code>`) → name, addressLine1/2, city, stateOrProvinceCode, countryCode, postalCode, phoneNumber, companyName, email | ask, or read the user's own sheet / file | every field non-empty; phone required by Amazon |
| 3 | Products: MSKU + total units | always | `Product Info` row per MSKU (same store): seller-sku, asin, fnsku | ask, or the user's sheet / xlsx | MSKU must exist on the store (`get_listing` / `search_listings_items` if unsure) |
| 4 | Box spec per MSKU: units/box, L×W×H, weight, units | Box First (default) | `Product Info` qtyPerBox, boxDimensions "LxWxH", boxWeight + the row-9 Weight/Dimension Unit | ask | units KG/LB, CM/IN; a box ≤ 25 in / 63.5 cm on every side and ≤ 50 lb / 22.7 kg unless the user says the product is oversize |
| 5 | Prep / label owner | default if not given | `Product Info` labelOwner, prepOwner, prepCategory, prepTypes | state the default SELLER / SELLER / NONE in the reply; never a blocking ✗ | AMAZON or SELLER |
| 6 | Carrier type | always | Manage Shipments `shippingSolution` | ask | AMAZON_PARTNERED_CARRIER or USE_YOUR_OWN_CARRIER |
| 7 | Transportation mode | always | `shippingMode` | ask | GROUND_SMALL_PARCEL, FREIGHT_LTL, FREIGHT_FTL_PALLET, FREIGHT_FTL_NONPALLET, OCEAN_LCL, OCEAN_FCL, AIR_SMALL_PARCEL, AIR_SMALL_PARCEL_EXPRESS |
| 8 | Preferred carrier | optional | `preferedCarrier` | ask once | free text; used to sort, never to filter |
| 9 | Ship date | always | `shipDate` | ask | `YYYY-MM-DD`, today or later |
| 10 | Delivery window start | own carrier | `deliveryWindowStartDate` | ask | `YYYY-MM-DD` ≥ ship date |
| 11 | Preferred warehouse id(s) | optional | ask | ask | Amazon FC codes (e.g. `ABC1`); only ever a ranking hint |
| 12 | Pallet details | LTL / FTL only | STA-Options row: Declared Value (USD number), Freight Class (`NONE`, `FC_50` … `FC_500`), Pallet Info lines `LxWxHxWeightxQty STACKABLE|NON_STACKABLE` | ask | all three or none per shipment |
| 13 | Own-carrier rates | when "help me choose" + own carrier | ask | ask | rate per kg and/or per m³, currency |
| 14 | Autopilot | always ask once | — | — | yes only if the user said, in their own words, to complete it end to end |
| 15 | Help me choose | always ask once | — | — | yes + the rule (cheapest total / fewest shipments / prefer warehouse X) — see COST_COMPARISON.md |
| 16 | Output form (mode B) | mode B | — | ask | chat tables, HTML page, the user's Google Sheet id + tab, local `.xlsx` path |

## How to ask (one message, only the ✗ lines)

EN: "Before I create anything on Amazon I need: <✗ lines>. Everything else I have: <✓ lines>."
中文: "在亚马逊上创建计划之前，我还需要：<✗ 行>。已具备：<✓ 行>。"

Ask everything missing in ONE message, then wait. Do not ask again for a line that is ✓.

## Autopilot rule (line 14)

- Autopilot **yes** and every REQUIRED line ✓ → run create → orchestrate → (choice) → transport →
  (choice) → confirm → labels → packing list without pausing between tools, pausing ONLY at the
  two choices — unless line 15 is also **yes with a rule** that yields one answer (then say which
  rule chose, and continue).
- Autopilot **no** (default) → stop after every phase, show the result, ask to continue.
- "Just do it" without the prerequisites is NOT autopilot: collect the ✗ lines first.

## What is never asked

- Box ids, FBA ids, reference ids, option ids — they come from tool results only.
- A credit price — never quoted.
- Permission to cancel — cancel only when the user says "cancel".
