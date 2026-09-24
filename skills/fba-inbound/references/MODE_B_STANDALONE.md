# Mode B — no SellerSheet FBA spreadsheet

The same Amazon chain, no plan workbook, no `sta_spreadsheet_id` anywhere. Every result is
delivered in the form the user chose at intake line 16, and the handover file is the
record. Do not create a SellerSheet workbook "as your own record" — the handover file is
your record.

## Intake sources in this mode

| Line | Where it comes from |
|---|---|
| Store | `get_user_context().data.stores[].store_refs` — one ref, verbatim |
| Ship-from address | the user, or a row they point you to in THEIR sheet (`read_sheet`) or file; all fields + phone |
| MSKUs, units, box spec, prep | the user's table — ask for it as `MSKU, units, units/box, LxWxH, weight, units`; read it from their Google Sheet with `read_sheet` or from a local `.xlsx`/`.csv` they gave you. Validate each MSKU exists on the store (`search_listings_items` / `get_listing`) |
| Carrier type, mode, dates, preferred warehouses, rates | the user |
| Output form | the user: chat tables (default), an HTML page, a tab in their Google Sheet (`write_sheet`, id + tab name), a local `.xlsx` (write it with openpyxl) |

Build `items`, `boxes` (one spec per distinct box shape and contents, `quantity` = boxes
of that spec) and `msku_prep_details` from that table exactly as mode A builds them from
the item rows. Mixed boxes: one `boxes` entry listing every SKU in the box.

## The chain

```
get_user_context
orchestrate_fba_packing(store, plan_name, source_address, items, boxes, msku_prep_details)
   → placementOptions[{placementOptionId, placementFee, shipmentCount, shipments[{shipmentId, warehouseId, totals}], aiRank}]
   (requiresHumanSelection → show packingOptions, re-call with selected_packing_option_id)
generate_shipment_transport_options(store, plan_id, placement_option_id, ship_date, pallet_info?)
   → per shipment partnered[] / ownCarrier[] / deliveryWindows[]
confirm_fba_placement(store, plan_id, placement_option_id, [{shipmentId, transportOptionId, deliveryWindowOptionId?}])
   → confirmedShipments[{shipmentId, fbaId, referenceId, warehouseId, status}]
get_labels(store, plan_id, shipment_id, page_type, label_type, number_of_packages, page_size, label_size)
   → labelData (base64 PDF), pageCount
create_fba_packing_list(store, plan_id, '', confirmed_shipments)
   → amazonBoxes[{amazonBoxId, shipmentId, boxName, msku, fnsku, asin, qty, labelOwner, boxDimensions, dimUnit, boxWeight, weightUnit, itemsInBox}]
update_shipment_tracking_details(store, plan_id, shipment_id, spd_tracking_items=[{boxId, trackingId}])
sync_fba_shipment_status(store, plan_id, shipment_id)
```

## Presenting each result (same columns as the SellerSheet tabs, so nothing is lost)

**Placement options** — one row per option:
`Placement | Shipments | Warehouses | Placement fee | aiRank` (aiRank 1 = lowest fee; say
so). With "help me choose": the two-total table in `COST_COMPARISON.md`.

**Transport options** — per shipment, two lists: partnered
`transportationOptionId | mode | carrier | cost currency` sorted by cost; own carrier
`transportationOptionId | mode | carrier` (no cost — Amazon does not quote it); windows
`deliveryWindowOptionId | start | end | availability` earliest first.

**Confirmation** — `shipmentId | FBA id | warehouse | status` and the note that reference
ids arrive later.

**Packing list** — the 11 Inbound PL columns: `Image | Box ID | Template | FNSKU | MSKU |
ASIN | Quantity | Weight | Weight Unit | Dimensions | Unit of Measurement`, one row per
box × SKU, sorted by Box ID then MSKU (no shipment column; `amazonBoxId` is the Box ID).
Leave Image blank unless the user's sheet has image URLs.

**Labels** — decode `labelData` to `<FBA id>.pdf`. Local file when the user works locally;
`start_drive_upload(parentId, name)` when they named a Drive folder; never silently into a
SellerSheet folder. Mention `pageCount` and the size applied.

**Output forms**
- Chat: markdown tables as above.
- HTML page: one page with the four tables above and the label link; plain HTML, no external
  scripts, the user's language.
- The user's Google Sheet: `write_sheet(spreadsheet_id, '<tab>!A1', rows)` with the same
  header rows; one tab per result (`FBA Placements`, `FBA Transport`, `FBA Packing List`).
- Local `.xlsx`: one workbook, one sheet per result, header row bold; write with openpyxl.

## Handover file

`fba-inbound-<planName>.md` (`HANDOVER_TEMPLATE.md`) next to the outputs — the local
directory the user is working in, or a Doc/Sheet they named. Rewritten after every phase;
"Next command" always filled in until COMPLETE / CANCELLED.

## What mode B never does

- `create_sta_sheet`, `sta_spreadsheet_id`, writes to a SellerSheet FBA spreadsheet.
- Guess a box spec, an address or a SKU from an Excel column name — ask.
- Pick an option without a user-named rule under autopilot (SKILL.md §3).
