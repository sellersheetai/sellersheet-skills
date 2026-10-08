---
name: fba-inbound
description_zh: "创建FBA货件、入库计划、发货到亚马逊、补货、STA表、分仓方案、运输方案、箱标、装箱单、上传物流单号、货件状态、取消计划、刷美西仓（刷仓换低运费）——无论是否使用 SellerSheet FBA 表格。"
description_en: "Use when a user wants stock sent to Amazon FBA — \"create FBA shipment\", \"inbound plan\", \"send to Amazon\",…"
author: SellerSheet AI
version: 0.16.2
metadata: {apis: [fba], pattern: Gate}
description: >-
  Use when a user wants stock sent to Amazon FBA — "create FBA shipment", "inbound plan",
  "send to Amazon", "restock FBA", "STA sheet", "placement options", "transport options",
  "FBA box labels", "packing list", "upload tracking", "shipment status", "cancel plan",
  "get a US-West warehouse" — whether or not they use the SellerSheet FBA spreadsheet,
  including "just do the whole thing" and "pick the cheapest for me" requests. Do NOT use
  for Amazon Advertising campaigns or budgets (use amazon-ads) or for warehouse-synced
  inventory/order reporting (use report-data).
  中文触发词：创建FBA货件、入库计划、发货到亚马逊、补货、STA表、分仓方案、运输方案、箱标、装箱单、上传物流单号、货件状态、取消计划、刷美西仓（刷仓换低运费）——无论是否使用 SellerSheet FBA 表格。
---

# FBA Inbound

One intake gate, one chain, one handover file — with or without the SellerSheet FBA
spreadsheet, with the compound tools or the granular Amazon operations. Preflight first:
[`sellersheet-shared`](../sellersheet-shared/SKILL.md) (`get_user_context` succeeds,
`data.canUseMcp` is true, store refs are `<store>-<CC>`).

## 0. Rules

- **Never choose for the user.** Packing option, placement, transport option, delivery
  window: the server lists, the user picks, you record — unless a rule the user named under
  autopilot (§3) picks, and then you say which rule did.
- **Intake before Amazon.** Nothing is created while a REQUIRED intake line is ✗.
- **Confirming charges and locks** (§4a): the placement fee, and the carrier at its quoted
  price. Amazon has no preview and no undo.
- **Cancel is a commit.** Interactive: say what `fbaInbound_cancelInboundPlan` voids (the
  plan and every shipment in it), end with a literal question, call it only on the word
  `CONFIRM`. Autopilot: only when the user's own instruction covered this exact cancel (the
  fishing loop, §4d). Void windows: partnered small parcel 24 h after transport confirmation,
  partnered LTL 1 h; after that, money committed to the carrier may not come back — say so.
- **Carrier mixing:** partnered and own-carrier shipments in one plan only on DIFFERENT
  shipping modes with every shipment partnered-eligible; otherwise Amazon refuses
  (`FBA_INB_0354`).
- **Ids come from tool results only.** Indian (IN) stores are read-only; a read-only key stops
  at listing and says so.
- Mode B never touches the SellerSheet FBA spreadsheet or a plan workbook; Mode A never builds
  a parallel sheet. Never mix modes in one plan.

## 1. Two choices, stated in the first reply

| | Mode A — SellerSheet | Mode B — standalone |
|---|---|---|
| When | `get_user_context().data.workspace_config.userSettingBySpreadsheet.fbaSpreadsheetId` is set and the user named no other destination | no FBA spreadsheet id, or the user said "no sheet" / named another output |
| Inputs | `Shipment Setting` (address by `warehouseCode` = `<store>-<CC>-<code>`), `Product Info` (per MSKU: qtyPerBox, boxDimensions "LxWxH", boxWeight, label/prep), the plan's `Manage Shipments` row | the user, their own sheet (`read_sheet`) or file |
| Outputs | the plan workbook `fbaInbound_create_sta_sheet` builds; with `sta_spreadsheet_id` the server renders STA-Options, Inbound PL and the label links; you write the stepper cells, row 12, Manage Shipments and `_state` — `references/SHEET_LAYOUT.md` | the form chosen at intake line 16: chat tables (default), HTML, a tab in their sheet (`write_sheet`), a local `.xlsx`; labels as a file or a Drive link |

Say it: "Mode A — I'll use your SellerSheet FBA spreadsheet" / "Mode B — no SellerSheet
spreadsheet; outputs go to …". If genuinely unclear, that is the ONE question before intake.

**Tools.** The compound tools (left column of §4) run Amazon's generate → poll → list →
confirm loop on the server and are the default. Granular operations (right column) only when
the compound cannot take the step: a plan moved past its entry point in the sidebar or Seller
Central, Split First / pack-later, content updates after confirmation, India, or one operation
the user named. A granular write returns an `operationId` — poll it bounded (§4b).

## 2. Intake — `references/INTAKE.md`

Print the 16-line checklist with ✓ / ✗ / ? in the first reply, after the mode. REQUIRED:
store, ship-from address (every field, phone included), MSKUs + units, box spec per MSKU
(Box First), ship date, delivery-window start (own carrier), pallet details (LTL / FTL).
Optional: Shipping Solution (AMAZON_PARTNERED_CARRIER | USE_YOUR_OWN_CARRIER) and Shipping
Mode (a GROUP: SPD | LTL / FTL, ocean under LTL / FTL) — blank lists every option; preferred
carrier, preferred warehouse ids, own-carrier rates, label sizes. Ask every ✗ REQUIRED line in
ONE message, with lines 14 (autopilot) and 15 (help me choose) unless already answered, then
stop. Mode A: a missing Shipment Setting or Product Info row is an intake ✗ — ask, never
invent; `fbaInbound_create_sta_sheet` refuses an unknown or incomplete warehouse code before it
creates anything and names the codes that exist.

## 3. Autopilot and "help me choose"

- **Autopilot** = the user said, in their own words, to complete it end to end. With every
  required line ✓, run the chain without pausing between tools; pause only at the two choices
  (placement; transport + window) and the confirm gate (§4a).
- **Help me choose** = the user asked you to compare or pick. Build the two-total table in
  `references/COST_COMPARISON.md`. Apply it yourself only under autopilot AND a rule the user
  named ("pick the cheapest" = cheapest total; fewest shipments; prefer warehouse X, else
  cheapest) AND no tie — then say so: "Rule 'cheapest total' picked pl…a1 (107.21 USD vs
  210.40)". A tie, or a quote the rule cannot price → show the table and wait.
- "Just get it done" with a missing address is neither: it is an intake ✗.

## 4. The chain

| Stage | Compound tool (default) | Granular Amazon operations (poll each write, §4b) | Mode A writes (`SHEET_LAYOUT.md`) |
|---|---|---|---|
| Plan workbook (A only) | `fbaInbound_create_sta_sheet(store, plan_name, skus, warehouse_code, ship_date, shipping_solution?, shipping_mode?, …)` → `staSpreadsheetId`, `planFolderId`, `manageShipmentsFormulas` | — | Manage Shipments `planFolder` + `planName` formulas; Box No. ✎ per item row (Split First: Total Qty ✎); `_state` STA_CREATED |
| Plan + packing + placement options | `fbaInbound_orchestrate_packing(store, plan_name, source_address, items, boxes, msku_prep_details, sta_spreadsheet_id?)` ~40–60 s → `planId`, `placementOptions[{placementOptionId, placementFee, shipmentCount, shipments[{shipmentId, warehouseId, destination, totals}]}]`; `requiresHumanSelection` → show `packingOptions`, re-call with `selected_packing_option_id` + `plan_id` (the plan continues) | `fbaInbound_setPrepDetails` → `fbaInbound_createInboundPlan` → `fbaInbound_generatePackingOptions` → `fbaInbound_listPackingOptions` → `fbaInbound_confirmPackingOption` → `fbaInbound_setPackingInformation` → `fbaInbound_generatePlacementOptions` → `fbaInbound_listPlacementOptions` | chips `1a.` `1b.` `1c.` DONE + ids, `2.` READY; Manage Shipments `planId`; `_state` PACKING_GENERATED; STA-Options rendered by the server |
| **User picks a placement** | table: placement, shipments, warehouses (code + city, ST), fee; aiRank 1 = lowest fee, say so | same | chip `2.` row 6 = `<placementOptionId> (<fee> USD · <warehouseIds>)`; `_state` PLACEMENT_SELECTED |
| Transport + delivery windows | `fbaInbound_generate_shipment_options(store, plan_id, placement_option_id, ship_date, pallet_info?, limit=3, shipping_solution?, shipping_mode?, sta_spreadsheet_id?)` ~20–60 s → `placementFee`; per shipment `partnered[]` (the 3 cheapest per mode), `ownCarrier[]`, `deliveryWindows[]` | `fbaInbound_generateTransportationOptions` → `fbaInbound_listTransportationOptions`; own carrier: `fbaInbound_generateDeliveryWindowOptions` → `fbaInbound_listDeliveryWindowOptions` | STA-Options block dropdowns (server); `_state` OPTIONS_LISTED |
| **User picks per shipment** | ONE `transportationOptionId` and, own carrier, ONE `deliveryWindowOptionId` | same | chips `3.` / `3b.` row 6 ids; `_state.selections` |
| Confirm (§4a) | `fbaInbound_confirm_plan_options(store, plan_id, placement_option_id, [{shipmentId, transportOptionId, deliveryWindowOptionId?}], sta_spreadsheet_id?)` → `confirmedShipments[{shipmentId, fbaId, referenceId, warehouseId, status}]` | `fbaInbound_confirmPlacementOption` → own carrier: `fbaInbound_confirmDeliveryWindowOptions` → `fbaInbound_confirmTransportationOptions` (window BEFORE transport) | row 12 by label (Status, FBA ID, Reference ID, Warehouse ID); chip `4.` DONE; Manage Shipments one row per shipment; `_state` CONFIRMED |
| Labels | `fbaInbound_get_labels(store, inbound_plan_id, shipment_id, page_type, label_type, number_of_packages, page_size, label_size, sta_spreadsheet_id?)` — `inbound_plan_id`, not `plan_id` | same tool | A: `<FBA id>.pdf` saved in the plan folder and linked by the server; B: decode `labelData` where the user said; `_state` LABELS_DOWNLOADED |
| Packing list | `fbaInbound_create_packing_list(store, plan_id, sta_spreadsheet_id?, confirmed_shipments)` → `amazonBoxes[]` | `fbaInbound_listShipmentBoxes` | A: `Inbound PL` tab (server); B: the 11 columns in the user's form; `_state` PACKING_LIST_WRITTEN |
| Tracking (own carrier) | `fbaInbound_updateShipmentTrackingDetails(store, plan_id, shipment_id, spd_tracking_items=[{boxId, trackingId}…])` — one call per shipment, every box; LTL / FTL: `ltl_tracking_detail={billOfLadingNumber, freightBillNumber:[…]}` | same tool | Manage Shipments `carrier`, `tracking`, `trackingUploaded`; `_state` TRACKING_UPLOADED |
| Status | `fbaInbound_sync_shipment_status(store, plan_id, shipment_id)` per shipment | `fbaInbound_getShipment` | Manage Shipments `status`, row 12; terminal (CLOSED / CANCELLED / ABANDONED / DELETED) → `_state` COMPLETE |

Reading the options:

- **Partnered** `partnered[]` is a view: the 3 cheapest options per shipping mode per
  shipment, cheapest first; `data.counts` is Amazon's total. Raise `limit` (0 = all) or read
  `fbaInbound_listTransportationOptions(placement_option_id, shipment_id)` when the carrier the
  user wants is missing. Pass `shipping_solution` and `shipping_mode` (SPD | LTL / FTL) from the
  plan workbook's row 9 or the intake; partnered-only also skips the delivery windows; a shipment
  with no match keeps its full list and the notification names it.
- **Own carrier** `ownCarrier[]` has no price (Amazon does not quote it); every own-carrier choice
  needs a delivery window confirmed BEFORE transport. `Other` is Amazon's catch-all carrier.
- **Delivery windows:** Amazon marks windows that start before the ship date — even ones already
  begun — AVAILABLE. Offer only windows whose `startDate` is on or after the user's
  delivery-window start (and the ship date), AVAILABLE or DISCOUNTED, earliest first. They expire
  at `deliveryWindowsValidUntil` (usually 3 days), so a far-origin shipment picks a window it can
  meet, not the first one.
- **Mode B presentation:** the same columns as the SellerSheet tabs (`references/SHEET_LAYOUT.md`:
  STA-Options for placements and options, Inbound PL for the packing list), one row per box × SKU;
  labels decoded to `<FBA id>.pdf` locally or `start_drive_upload` to a folder the user named.

### 4a. The confirm gate

Before `fbaInbound_confirm_plan_options` (or the granular confirms) restate, in money: the
placement and its fee, each shipment's chosen option with its quote (own carrier: "no Amazon
quote; window <start>–<end>"), and that confirming charges the fee and locks the carrier at
that price with no undo. Interactive: wait for an explicit go-ahead to THAT summary — an
earlier "ok" does not count. Autopilot: only when the user asked for the whole thing AND a
named rule (or the user) picked every option; otherwise stop and show the summary. Placement
first; own carrier confirms its window before transportation.

### 4b. Bounded polling — granular operations only

The compound tools wait on the server. A granular write returns an `operationId` at once:
poll `fbaInbound_getInboundOperationStatus` after 10–15 s, then roughly double the wait, at
most 3 checks. `FAILED` → report `operationProblems` and stop; still `IN_PROGRESS` → hand the
operation id to the user instead of looping.

### 4c. After confirmation, per carrier

| Carrier | The user does next | Void window |
|---|---|---|
| Partnered small parcel (SPD) | print box labels; schedule the pickup with the carrier (Amazon does not); tracking comes from the carrier | 24 h |
| Partnered LTL / FTL | pallet labels + bill of lading from Amazon; freight-ready within 2 weeks; pallet details were required at the transport step | 1 h |
| Own carrier | ship, then upload tracking: one number per box (SPD) or one freight bill / BOL per shipment (LTL / FTL); API-created shipments only | any time, no charge |

Repeat at the right moment: placement is permanent once confirmed; box contents changed after
placement mean regenerating placement options; a changed source address invalidates the
transportation options; one freight bill per shipment; several expiration dates for one SKU
need separate plans.

### 4d. Fishing for a warehouse (刷仓 / 刷美西仓) — `references/WAREHOUSE_FISHING.md`

The user wants one nearby FC and says so. A plan's placement set is fixed for its 3-day
validity; only a NEW plan, another ship-from address or another box split is a new draw. The
reference page is the loop — create, check, keep the hit, cancel the losers (part of the
instruction the user gave).

## 5. Handover file — `references/HANDOVER_TEMPLATE.md`

`fba-inbound-<planName>.md`, created at intake and rewritten after EVERY phase: ids, who
chose what, what is done, what the user must answer, the exact next tool call. Mode A: the
same text in a `_handover` tab of the plan workbook (`add_sheet_tab` once, then
`write_sheet('_handover!A1', [[text]])`), plus the local file when you have a filesystem.
Mode B: next to the user's outputs. `_state` and the workbook are not a substitute.

## 6. Before you say "done"

- [ ] mode and tool path stated in the first reply; intake ✓ on every required line, asked in
      one message; autopilot and help-me-choose recorded
- [ ] every choice made by the user or by a named rule; the confirm gate shown in money
- [ ] confirm result carries FBA ids; row 12 / Manage Shipments (A) written
- [ ] labels and packing list where the mode says; tracking uploaded or left for later with
      the box ids listed; status synced and written
- [ ] handover file rewritten with "Next command" filled in
- [ ] CANCELLED exit instead: plan cancelled on Amazon; row 5 chips, row 12 Status, Manage
      Shipments status and handover stage = CANCELLED; row 6 ids and the label links stay as
      the audit trail

## Common mistakes

| Mistake | Fix |
|---|---|
| A plan workbook "as my own record" for a user with no FBA spreadsheet | Mode B: the handover file is your record |
| Refusing "pick the cheapest for me" outright | Build the comparison; apply the rule only under autopilot + a named rule + no tie, and say which rule chose |
| Confirming on a "yes" given before the fee and quotes were on screen | Restate them in money, then ask (§4a) |
| Offering the first AVAILABLE window | Filter by the delivery-window start / ship date first |
| Pasting every transportation option into the reply | The 3 cheapest per mode; the full list only when a wanted carrier is missing |
| Hand-writing STA-Options / Inbound PL rows | Pass `sta_spreadsheet_id`; the server renders the sidebar's tabs |
| Stopping after every tool in autopilot, or polling a compound tool | Pause only at the two choices and the confirm gate; only a granular write needs §4b |
