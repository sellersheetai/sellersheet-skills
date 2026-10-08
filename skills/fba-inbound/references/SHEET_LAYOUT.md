# FBA Inbound Sheet Layout Reference (stepper console)

Every sheet below is the SAME one the SellerSheet sidebar writes. Locate columns
by the row-1 machine key (Manage Shipments, Shipment Setting, item tables), by
the row-8 / row-11 label (plan workbook inputs and status) or by the display
header (STA-Options). Never by a fixed letter.

---

## Manage Shipments (FBA spreadsheet, 29 keys)

Row 1 machine keys (hidden), row 2 banner, row 3 display headers, row 4+ data —
one row per plan until confirmation, then one row per shipment.

| Key | Display | Notes |
|---|---|---|
| store | Store ✎ | `<store>-<CC>` |
| warehouseCode | Warehouse Code ✎ | matches a Shipment Setting row |
| planName | Plan Name ✎ | after Phase 3: `=HYPERLINK(<workbook url>, <plan name>)` |
| status | Status | WORKING / SHIPPED / … / CANCELLED |
| notes | Notes ✎ | free text |
| skus | MSKUs ✎ | one per line |
| shippingSolution | Shipping Solution ✎ | dropdown, optional: AMAZON_PARTNERED_CARRIER / USE_YOUR_OWN_CARRIER — copied to the plan workbook's row 9; narrows the Transportation Option dropdown |
| shippingMode | Shipping Mode ✎ | dropdown, optional, a GROUP: SPD / LTL / FTL (ocean counts as LTL / FTL) — copied to row 9; narrows the Transportation Option dropdown; a shipment with no match shows every option and the notification says so |
| preferedCarrier | Prefered Carrier | free text |
| fulfillmentSplit | Fulfillment Split | "Box First, Split Later" / "Split First (Only for truckload)" |
| casePacked | Case Packed | YES / NO |
| shipDate | Ship Date ✎ | YYYY-MM-DD |
| deliveryWindowStartDate | Delivery Window Start Date | YYYY-MM-DD |
| planFolder | Plan Folder | `=HYPERLINK(<Drive folder url>, <CC>FBA<timestamp>)` |
| planId | Plan ID | wf… |
| shipmentId | Shipment ID | sh… (one row per shipment after confirmation) |
| fbaLabel | FBA Label | link to the saved label PDF |
| fbaId | FBA ID | FBA… |
| amazonReferenceId | Reference ID | assigned by Amazon after WORKING |
| warehouseId | Warehouse ID | destination FC |
| box | Box | box count |
| quantity | Quantity | units |
| carrier | Carrier ✎ | own carrier name |
| tracking | Tracking ✎ | tracking number(s) |
| trackingUploaded | Tracking Uploaded | TRUE after Phase 9 |
| createdAt | Created At | |
| appointmentId / appointmentStatus / appointmentSlotTime | Appointment … | self-ship appointments (IN) |

The sidebar finds a plan's rows by the workbook id in the Plan Name link or the
folder id in the Plan Folder link — never by the plan name text.

## Shipment Setting (FBA spreadsheet)

Keys: `warehouseCode, companyName, name, phoneNumber, email, addressLine1,
addressLine2, city, stateOrProvinceCode, countryCode, postalCode,
unitOfDimention, unitOfWeight`. `warehouseCode` is the composite key
`<store>-<CC>-<code>` (e.g. `MYSTORE-US-CN`); the plan workbook's
`Send From Address ✎` holds that key and the address is the rest of the row.

## Product Info (FBA spreadsheet)

Keys: `store, image, seller-sku, fulfillment-channel-sku, asin, condition-type,
title, qtyPerBox, boxDimensions, boxWeight, labelOwner, prepOwner,
prepCategory, prepTypes, image_url`. Every MSKU on a plan needs a row here for
the same store; with Case Packed = YES the plan workbook's item rows pull
Qty/Box, Box Dimensions ("LxWxH"), Box Weight and the prep block from it.

---

## Plan workbook — STA-BoxFirst / STA-SplitFirst (the stepper console)

The MCP path and the sidebar share ONE plan workbook (`fbaInbound_create_sta_sheet`, identical
to the sidebar's "Create STA SS"). Address cells by their row-1 machine key, row-8 label or
row-13 display header — except the stepper, which the sidebar anchors on `A3 = PROGRESS`.

| Rows | Content |
|---|---|
| 1 | hidden machine keys of the item table: Box First `boxNo, msku, image, fnsku, title, asin, qtyPerBox, boxDimensions, boxWeight, boxes, quantity, expiration, labelOwner, prepOwner, prepCategory, prepTypes`; Split First `msku, image, fnsku, title, asin, totalQty, expiration, labelOwner, prepOwner, prepCategory, prepTypes` |
| 3 | `A3 = PROGRESS` (anchor), `B3` next-step formula, `D3` the Product Info "Allow access" chip (the human clicks it once; the server cannot) |
| 4 | stepper chips — Box First: `1a. Plan · 1b. Packing · 1c. Pack Info · 2. Placement · 3. Transport · 3b. Delivery Win · 4. Confirm`; Split First: `1. Plan · 2. Placement · 3. Pack Info · 4. Transport · 5. Delivery Win · 6. Confirm` |
| 5 | per-chip status: `DONE` / `READY` / `CANCELLED` / blank |
| 6 | per-chip id: plan id under `1a.`, packing option under `1b.`, packing group under `1c.`, the placement pick under `2.`, transport id under `3.`, window id under `3b.`, FBA id under `4.` |
| 8 / 9 | inputs, label → value: `Store ✎, Plan Name ✎, Ship Date ✎, Send From Address ✎ (<store>-<CC>-<warehouseCode>), Delivery Window Start Date, Case Packed, Pallet Packed, Weight Unit, Dimension Unit, Preferred Carrier, Shipping Solution, Shipping Mode, FNSKU Label Size, FBA Box Label Size` (a workbook built before 2026-10-08 carries `Preferred Trans. Mode` instead of the two Shipping cells — every reader goes by label) |
| 11 / 12 | status, label → value: `Status, FBA ID, Fulfillment Split, Reference ID, Warehouse ID, Total QTY, Total Boxes, Total Weight, Total Volume` |
| 13 | display headers of the item table |
| 14+ | items — Box First: `Box No. ✎` (`1` or `2~4`) and `MSKU ✎`; Image/FNSKU/Description/ASIN and (Case Packed = YES) Qty/Box, Box Dimensions, Box Weight, Label/Prep Owner, Prep Category, Prep Type spill from Product Info. Split First: `MSKU ✎` and `Total Qty ✎` |

Building the Amazon inputs from rows 14+ (by the row-1 keys): `items` = plan totals per MSKU;
`boxes` = one spec per distinct box shape and contents, `quantity` = boxes of that spec; boxNo
`1` → one box, `2~4` → boxes 2, 3, 4, several rows with the same boxNo → one mixed box;
`msku_prep_details` from the prep columns; `source_address` = the Shipment Setting row (keys
`name, addressLine1, addressLine2, city, stateOrProvinceCode, countryCode, postalCode,
phoneNumber, companyName`). Mode B builds the same three from the user's table.

### `_state` (one cell)

`_state!A1` is one JSON string: `stage, planId, packingOptionId, packingGroupId,
selectedPlacementOptionId, selections, confirmedShipments, labels, packingList, tracking`.
`fbaInbound_create_sta_sheet` creates the tab (stage STA_CREATED); rewrite it with
`write_sheet(staSpreadsheetId, '_state!A1', [[json_string]])`. Stages: `STA_CREATED →
PACKING_GENERATED → PLACEMENT_SELECTED → OPTIONS_LISTED → CONFIRMED → LABELS_DOWNLOADED →
PACKING_LIST_WRITTEN → TRACKING_UPLOADED → COMPLETE` (`CANCELLED` from anywhere). Before
acting, read `_state`, then confirm with Amazon (`fbaInbound_get_plan_status` before
confirmation, `fbaInbound_sync_shipment_status` after). If the stepper (rows 5/6) says the
sidebar went further than `_state`, trust the sheet and Amazon, update `_state`, tell the user.

### Picking up a plan the sidebar started

Read row 6 under `1a.` (plan id) and `2.` (placement pick — the id before the first space),
row 12 (FBA ID = confirmed), STA-Options by header names (`Shipment ID`, `Transportation
Option`, `Delivery Window Option`, `FBA ID`, `Reference ID`, `Warehouse ID`, `Status`; ids are
the text before the first space). Confirm the state with Amazon before continuing; write the
handover file before doing anything else.

Cell contract for the MCP path:

| What | Where | Value |
|---|---|---|
| plan id | row 6 under chip `1a.` (Split First `1.`) | `wf…`; row 5 `DONE` |
| packing option / group | row 6 under `1b.` / `1c.` | `po…` / `pg…`; row 5 `DONE` |
| placement pick | row 6 under `2.` | `<placementOptionId> (<fee> USD · <warehouseIds>)`; row 5 `READY` until confirmed |
| transport / window picks | row 6 under `3.` / `3b.` | the chosen ids |
| confirmation | row 12 by label | `Status`=CONFIRMED, `FBA ID`, `Reference ID`, `Warehouse ID`; chip `4.` (`6.`) `DONE` |
| cancel | row 5 all chips, row 12 `Status` | `CANCELLED` |

## STA-Options (rendered by the SERVER in mode A; read by header name)

`fbaInbound_orchestrate_packing(sta_spreadsheet_id=…)` renders it, `fbaInbound_generate_shipment_options`
fills the picked block's dropdowns, `fbaInbound_confirm_plan_options` writes the choices, `fbaInbound_get_labels`
turns the FBA ID cell into the PDF link. Same layout as the sidebar's "2. Gen Placement Opts.":

Summary table rows 1..N+1: `Placement Option: | Number of Shipments | Placement Fee |
Total Transportation Fee | Freight Est. | Total (Partnered) | Total (Own)` — D/E read the block
header, F = C+D, G = C+E; the cheapest cell per column turns green when N > 1.

One block per placement option after a blank row (first block at row N+3; each block =
header + column header + one row per shipment + blank):
- block header row: `Placement Option:` | id | `Placement Fee` | fee | `Total Transportation Fee` |
  Σ Transportation Fee | `Total Est. (kg)` | Σ Est. (kg) | `Total Est. (m³)` | Σ Est. (m³) |
  `Total (Partnered)` | fee + Σ transport | `Total (Own)` | fee + (Σ kg est. or Σ m³ est.)
- column header row (19): `Shipment ID | Declared Value | Freight Class | Pallet Info |
  Transportation Option | Delivery Window Option | Transportation Fee | FBA ID |
  Reference ID | Warehouse ID | Status | Total QTY | Total Boxes | Weight (KG) |
  Volume (CBM) | Rate/kg ✎ | Est. (kg) | Rate/m³ ✎ | Est. (m³)`
- one data row per shipment. Dropdown texts: transportation
  `to… (<solution> - <mode> - <carrier code / name> - <cost> <currency>)` (own carrier has an
  empty cost), delivery window `<id> (<Mon DD> - <Mon DD>)` in the spreadsheet's timezone.
  `Transportation Fee` = the cost parsed from the chosen transport text; `Est.` = rate × kg / m³.
  Weight is KG (LB ÷ 2.20462), volume CBM (IN³ × 0.0000163871, CM³ × 0.000001).
- The `Warehouse ID` cell keeps the bare FC code (every reader keys on it) and carries a
  NOTE `City, ST ZIP · Region (中文)` — city/state/zip from Amazon's shipment destination, the
  region only when the FC is in the known table (East / Central / West as Seller Central
  groups them); an unknown FC shows no region rather than a guess.
- The sidebar's Confirm reads the ids as the text before the first space; the AI never
  writes these cells by hand — it passes `sta_spreadsheet_id` and the server does.

## Inbound PL (the FINAL packing list, written by the server in mode A)

`fbaInbound_create_packing_list(sta_spreadsheet_id=…)` writes it and removes a stale `STA-PL`.
Row 1 headers (navy band, frozen): `Image | Box ID | Template | FNSKU | MSKU | ASIN | Quantity |
Weight | Weight Unit | Dimensions | Unit of Measurement`; one row per box × SKU, sorted by Box
ID, Template, MSKU; A1 holds the Image array formula over Product Info. No shipment column —
tracking lives in Manage Shipments. Mode B presents the same 11 columns in the user's form.

## Label links (mode A, written by the server)

`fbaInbound_get_labels(sta_spreadsheet_id=…)` saves `<FBA id>.pdf` into the plan folder (the workbook's
parent) and writes `=HYPERLINK(pdf, "<FBA id>")` into the STA-Options FBA ID cell and the
Manage Shipments `fbaId` cell, and `=HYPERLINK(pdf, "<FBA id>.pdf")` into `fbaLabel`. A linked
FBA ID is the sidebar's "label already fetched" gate.
