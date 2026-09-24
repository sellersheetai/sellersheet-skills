# Mode A — the SellerSheet FBA spreadsheet and the sidebar's plan workbook

The MCP path and the sidebar share ONE plan workbook (created by `create_sta_sheet`,
identical to the sidebar's "Create STA SS"). The server renders the sidebar's tabs when
you pass `sta_spreadsheet_id`; you write only the **handover cells** the sidebar reads.
At every phase the human may press the sidebar button for the next step, and you may pick
up a plan the sidebar started by reading the same cells.

Address cells by their **row-1 machine key**, **row-8 label** or **row-13 display
header**, never by a fixed letter — except the stepper, which the sidebar anchors on
`A3 = PROGRESS`. Full column maps: `SHEET_LAYOUT.md`.

## The plan workbook (stepper console)

| Rows | Content |
|---|---|
| 1 | hidden machine keys of the item table: Box First `boxNo, msku, image, fnsku, title, asin, qtyPerBox, boxDimensions, boxWeight, boxes, quantity, expiration, labelOwner, prepOwner, prepCategory, prepTypes`; Split First `msku, image, fnsku, title, asin, totalQty, expiration, labelOwner, prepOwner, prepCategory, prepTypes` |
| 3 | `A3 = PROGRESS` (anchor), `B3` next-step formula, `D3` the Product Info "Allow access" chip |
| 4 | stepper chips — Box First: `1a. Plan · 1b. Packing · 1c. Pack Info · 2. Placement · 3. Transport · 3b. Delivery Win · 4. Confirm`; Split First: `1. Plan · 2. Placement · 3. Pack Info · 4. Transport · 5. Delivery Win · 6. Confirm` |
| 5 | per-chip status: `DONE` / `READY` / `CANCELLED` / blank |
| 6 | per-chip id: plan id under `1a.`, packing option under `1b.`, packing group under `1c.`, the **placement pick** under `2.` as `<placementOptionId> (<fee> USD · <warehouseIds>)`, transport id under `3.`, window id under `3b.`, FBA id under `4.` |
| 8 / 9 | inputs, label → value: `Store ✎, Plan Name ✎, Ship Date ✎, Send From Address ✎ (short key <store>-<CC>-<warehouseCode>), Delivery Window Start Date, Case Packed, Pallet Packed, Weight Unit, Dimension Unit, Preferred Carrier, Preferred Trans. Mode, FNSKU Label Size, FBA Box Label Size` |
| 11 / 12 | status, label → value: `Status, FBA ID, Fulfillment Split, Reference ID, Warehouse ID, Total QTY, Total Boxes, Total Weight, Total Volume` |
| 13 | display headers of the item table |
| 14+ | items — Box First: `Box No. ✎` (`1` or `2~4`) and `MSKU ✎`; Image/FNSKU/Description/ASIN and (Case Packed = YES) Qty/Box, Box Dimensions, Box Weight, Label/Prep Owner, Prep Category, Prep Type spill from Product Info. Split First: `MSKU ✎` and `Total Qty ✎` |

Tabs the SERVER renders: `STA-Options` (orchestrate / transport / confirm / labels),
`Inbound PL` (packing list). You never hand-write them.

## Plan state

`_state!A1` JSON: `stage, planId, packingOptionId, packingGroupId,
selectedPlacementOptionId, selections, confirmedShipments, labels, packingList, tracking`.
`create_sta_sheet` creates the `_state` tab and writes the first JSON (stage STA_CREATED);
you rewrite it with `write_sheet(staSpreadsheetId, '_state!A1', [[json_string]])` — one
cell, the whole document as a string. `_state` never holds INTAKE (that stage exists only
in the handover text, before the workbook exists).
Stages: `STA_CREATED → PACKING_GENERATED → PLACEMENT_SELECTED → OPTIONS_LISTED →
CONFIRMED → LABELS_DOWNLOADED → PACKING_LIST_WRITTEN → TRACKING_UPLOADED → COMPLETE`
(`CANCELLED` from anywhere). Before acting, read `_state`, then confirm with Amazon
(`get_fba_plan_status` before confirmation, `sync_fba_shipment_status` after). If the
stepper (rows 5/6) says the sidebar went further than `_state`, trust the sheet and
Amazon, update `_state`, tell the user. The handover file (`HANDOVER_TEMPLATE.md`) is
rewritten at the same moments and uploaded to the plan folder.

## Phases

### Intake (SKILL.md §2) — sources in this mode
`get_user_context().data.workspace_config.userSettingBySpreadsheet.fbaSpreadsheetId` is
the FBA spreadsheet. Read `Shipment Setting!A1:M` (address by `warehouseCode`
`<store>-<CC>-<code>`) and `Product Info!A1:Z` (MSKU rows: qtyPerBox, boxDimensions
"LxWxH", boxWeight, labelOwner, prepOwner, prepCategory, prepTypes). A missing warehouse
code or MSKU row is an intake ✗ — ask, do not invent.

### Manage Shipments row
The plan row in the FBA spreadsheet's `Manage Shipments` (keys `store, warehouseCode,
planName, skus (one per line), shippingSolution, shippingMode, preferedCarrier,
fulfillmentSplit, casePacked, shipDate, deliveryWindowStartDate`). If the user has not
written it, append it with `write_sheet` by those keys (row 1 = keys, data from row 4).

### Plan workbook
```
create_sta_sheet(store, plan_name, skus, warehouse_code, ship_date,
                 delivery_window_start_date, case_packed, fulfillment_split,
                 shipping_solution, shipping_mode, preferred_carrier,
                 fnsku_label_size, fba_box_label_size)
→ data.staSpreadsheetId, spreadsheetUrl, tabName, planFolderId, planFolderName,
  manageShipmentsFormulas {planFolder, planName}, addressKeyKnown
```
Write the two formulas into the plan row's `planFolder` and `planName` columns (by key).
Tell the user to click the STA tab's D3 cell once ("Allow access") — the server cannot.
Box First: write `Box No. ✎` per item row from row 14 (`1`, `2~4`); Split First: `Total
Qty ✎`. `_state.stage = STA_CREATED`. Handover file created.

### Plan + packing + placement options
Read rows 14+ by the row-1 keys; build `items` (plan totals), `boxes` (one spec per
distinct box shape and contents; `quantity` = boxes of that spec) and `msku_prep_details`.
boxNo rules: `1` → one box; `2~4` → boxes 2, 3, 4; several rows with the same boxNo → one
mixed box.
```
orchestrate_fba_packing(store, plan_name, source_address, items, boxes,
                        msku_prep_details, sta_spreadsheet_id) → ~40–60 s
→ planId, packingOptionId, packingGroupId,
  placementOptions[{placementOptionId, placementFee, shipmentCount, shipmentIds,
                    shipments[{shipmentId, warehouseId, status, totals}], aiRank}],
  staOptions {tab, rows, blocks}
```
`source_address` = the Shipment Setting row (keys `name, addressLine1, addressLine2, city,
stateOrProvinceCode, countryCode, postalCode, phoneNumber, companyName`). If
`requiresHumanSelection` is true, show `packingOptions`, let the user pick, re-call with
`selected_packing_option_id`. Write the stepper: `1a.` DONE + planId, `1b.` DONE +
packingOptionId, `1c.` DONE + packingGroupId, `2.` READY; Manage Shipments `planId`.
`_state.stage = PACKING_GENERATED`. STA-Options is now in the workbook (server).

### The user picks a placement, then the options for it
Show the placement options as a table (fee, shipment count, warehouses; aiRank 1 = lowest
fee; say so, do not decide — unless SKILL.md §3 applies). Write the pick into the `2.`
chip's row-6 cell: `<placementOptionId> (<fee> USD · <warehouseIds joined by ", ">)`.
`_state.stage = PLACEMENT_SELECTED`.
```
generate_shipment_transport_options(store, plan_id, placement_option_id, ship_date,
                                    pallet_info?, sta_spreadsheet_id) → ~20–60 s
→ shipments[{shipmentId, warehouseId, status, totals,
             partnered[{transportationOptionId, shippingMode, carrierName, cost, currency}],
             ownCarrier[{transportationOptionId, shippingMode, carrierName}],
             deliveryWindows[{deliveryWindowOptionId, startDate, endDate, validUntil, availabilityType}]}],
  staOptions {updated}
```
Present per shipment: partnered by cost, own carrier by mode and carrier, windows earliest
first. The user chooses ONE transportationOptionId per shipment and, for own carrier, ONE
window (the dropdowns in STA-Options carry the same lists). Record the choices in
`_state.selections`; write the ids under the `3.` / `3b.` chips. `_state.stage = OPTIONS_LISTED`.

### Confirm
```
confirm_fba_placement(store, plan_id, placement_option_id,
    [{shipmentId, transportOptionId, deliveryWindowOptionId?}, …], sta_spreadsheet_id)
→ confirmedShipments[{shipmentId, shipmentConfirmationId, fbaId, referenceId, warehouseId, status}],
  staOptions {updated}
```
`fbaId == shipmentConfirmationId`; `referenceId` is empty while WORKING. Write row 12 by
label (`Status` = CONFIRMED, `FBA ID`, `Reference ID`, `Warehouse ID`); chip `4.` (`6.`)
DONE + FBA id; Manage Shipments `shipmentId, fbaId, amazonReferenceId, warehouseId,
status, box, quantity` (one row per shipment: copy the plan row for the second onward).
`_state.stage = CONFIRMED`. After confirmation labels are available at once, box ids are
`<FBA id>U000001…`, tracking can be uploaded while WORKING, `cancel_inbound_plan` still works.

### Labels + packing list
```
get_labels(store, inbound_plan_id, shipment_id, page_type='PackageLabel_Thermal_NonPCP',
           label_type='BARCODE_2D', number_of_packages=<boxes>, page_size=<boxes>,
           label_size=<row 9 "FBA Box Label Size">, sta_spreadsheet_id)
→ driveUrl, fileName, links {staOptions, manageShipments}, pageCount, labelData
create_fba_packing_list(store, plan_id, sta_spreadsheet_id, confirmed_shipments)
→ inboundPl {tab, rows}, amazonBoxes[…]
```
The server saved `<FBA id>.pdf` into the plan folder and linked the three cells; the
`Inbound PL` tab is written. Write nothing for those. If a PageType is refused, fall back
to `PackageLabel_Plain_Paper`. `_state.stage = LABELS_DOWNLOADED` → `PACKING_LIST_WRITTEN`.

### Tracking (own carrier)
The user gives one tracking number per box (or you read Manage Shipments `tracking`).
ONE call per shipment: `update_shipment_tracking_details(store, plan_id, shipment_id,
spd_tracking_items=[{boxId: amazonBoxId, trackingId}, …])` (LTL:
`ltl_tracking_detail={billOfLadingNumber, freightBillNumber:[…]}`). Manage Shipments
`carrier`, `tracking` (one per line), `trackingUploaded = TRUE`. `_state.stage = TRACKING_UPLOADED`.

### Status
`sync_fba_shipment_status(store, plan_id, shipment_id)` per shipment; write `status` to
Manage Shipments and row 12; terminal (CLOSED / SHIPPED / RECEIVED / CANCELLED) →
`_state.stage = COMPLETE`.

### Cancel
Only when the user says so: `cancel_inbound_plan(store, plan_id)`; stepper row 5 →
CANCELLED on every chip, row 12 `Status` → CANCELLED, Manage Shipments `status` →
CANCELLED, `_state.stage` and the handover stage CANCELLED. Row 6 ids, the STA-Options
rows and the label links are left as they are (audit trail); a confirmed plan can still be
cancelled.

## Picking up a plan the sidebar started
Read row 6 under `1a.` (plan id) and `2.` (placement pick — the id before the first
space), row 12 (FBA ID = confirmed), STA-Options by header names (`Shipment ID`,
`Transportation Option`, `Delivery Window Option`, `FBA ID`, `Reference ID`,
`Warehouse ID`, `Status`; the ids are the text before the first space). Confirm the state
with Amazon before continuing; write the handover file before doing anything else.
