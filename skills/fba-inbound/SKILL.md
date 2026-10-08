---
name: fba-inbound
description_zh: "创建FBA货件、入库计划、发货到亚马逊、补货、STA表、分仓方案、运输方案、箱标、装箱单、上传物流单号、货件状态、取消计划、刷美西仓（刷仓换低运费）——无论是否使用 SellerSheet FBA 表格。"
description_en: "Use when a user wants stock sent to Amazon FBA — \"create FBA shipment\", \"inbound plan\", \"send to Amazon\",…"
author: SellerSheet AI
version: 0.16.0
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
spreadsheet, with the compound tools or the granular Amazon operations. This page is the
whole workflow; the reference pages hold layouts and tables only. Run the preflight in
[`sellersheet-shared`](../sellersheet-shared/SKILL.md) first (`get_user_context` succeeds,
`data.canUseMcp` is true; store refs follow its `<store>-<CC>` rule).

## 0. Rules that never change

- **Never choose for the user.** Packing option, placement, transportation option, delivery
  window: the server lists, the user picks, you record. The one exception is a rule the user
  named under autopilot (§3) — then say which rule chose.
- **Intake before Amazon.** Nothing is created (`fbaInbound_create_sta_sheet`,
  `fbaInbound_orchestrate_packing`, `fbaInbound_createInboundPlan`) while a REQUIRED intake
  line is ✗. "Just do it" is not an answer to a missing address.
- **Confirming charges and locks** (§4a). `fbaInbound_confirm_plan_options` (or
  `fbaInbound_confirmPlacementOption` + `fbaInbound_confirmTransportationOptions`) charges
  the placement fee and locks the carrier at the quoted price; Amazon has no preview and no
  undo. Restate the fee and the quote in money before it, and get the user's explicit go-ahead.
- **Cancel is a commit, not an approve.** Interactive: say exactly what
  `fbaInbound_cancelInboundPlan` will void — the plan and every shipment in it — and end the
  message with a literal question ("Cancel plan wf-abc and every shipment in it — are you
  sure?"); call it only when the reply is the literal word `CONFIRM`. Autopilot: only when the
  user's own instruction already covered this exact cancel (the fishing loop, §4d); "do the
  whole thing" never authorises a cancel. Void windows: partnered small parcel 24 h after
  transport confirmation, partnered LTL 1 h — after that cancelling still stops the plan but
  may not release money already committed to the carrier; say so.
- **Carrier mixing.** One plan may mix partnered and own-carrier shipments only when every
  shipment uses a DIFFERENT shipping mode and every shipment is eligible for the partnered
  program; otherwise Amazon refuses with `FBA_INB_0354`. A plan needing both gets separate
  shipments and modes, never one mixed shipment.
- **Ids come from tool results only** — plan, shipment, option, box and FBA ids are never
  typed from memory or invented.
- Indian (IN) stores are read-only. Amazon writes need SP write access on the key; a
  read-only key stops at listing and says so.
- Mode B never touches the SellerSheet FBA spreadsheet or a plan workbook. Mode A never
  builds a parallel sheet. Never mix modes in one plan.

## 1. Two choices, stated in the first reply

**Where things live.**

| | Mode A — SellerSheet | Mode B — standalone |
|---|---|---|
| When | `get_user_context().data.workspace_config.userSettingBySpreadsheet.fbaSpreadsheetId` is set AND the user has not asked for another destination | no FBA spreadsheet id, OR the user said "no sheet" / keeps stock elsewhere / named another output (chat, HTML, their own sheet, Excel) |
| Inputs | `Shipment Setting` (address by `warehouseCode` = `<store>-<CC>-<code>`), `Product Info` (MSKU rows: qtyPerBox, boxDimensions "LxWxH", boxWeight, label/prep columns), the plan's `Manage Shipments` row | the user, their own sheet (`read_sheet`) or file |
| Outputs | the plan workbook `fbaInbound_create_sta_sheet` builds (the sidebar's own); the server renders STA-Options, Inbound PL and the label links when you pass `sta_spreadsheet_id`; you write the stepper cells, row 12, Manage Shipments and `_state` — `references/SHEET_LAYOUT.md` | the form the user chose at intake line 16: chat tables (default), an HTML page, a tab in their sheet (`write_sheet`), a local `.xlsx`; labels as a file or a Drive link |

Say it: "Mode A — I'll use your SellerSheet FBA spreadsheet" / "Mode B — no SellerSheet
spreadsheet; outputs go to …". If it is genuinely unclear, that is the ONE question you ask
before the intake list.

**Which tools.** The compound tools (left column of §4) run Amazon's generate → poll → list
→ confirm loop on the server and return when Amazon is done; they are the default. Use the
granular Amazon operations (right column) only when the compound cannot take the step:
picking up a plan the sidebar or Seller Central moved past the compound's entry point, a
Split First / pack-later plan, content updates after confirmation, India, or a single
operation the user asked for by name. A granular write returns an `operationId` — poll it
bounded (§4b). Say which you are using when it is not the default.

## 2. Intake gate — `references/INTAKE.md`

Print the 16-line checklist with ✓ / ✗ / ? per line in the first reply, after the mode.
REQUIRED: store, ship-from address (every field, phone included), MSKUs + units, box spec
per MSKU (Box First), carrier type, shipping mode, ship date, delivery-window start (own
carrier), pallet details (LTL / FTL). Optional: preferred carrier, preferred warehouse ids,
own-carrier rates, label sizes. Ask for every ✗ REQUIRED line in ONE message, then stop.
Lines 14 (autopilot) and 15 (help me choose) are asked once, in that same message, unless the
user's words already answered them. Mode A: a missing Shipment Setting row or Product Info
row is an intake ✗ — ask, do not invent; `fbaInbound_create_sta_sheet` refuses an unknown or
incomplete warehouse code before it creates anything and names the codes that exist.

## 3. Autopilot and "help me choose"

- **Autopilot = the user said, in their own words, to complete it end to end** ("do the whole
  thing", "run it through to labels"). With every required line ✓, run the chain without
  pausing between tools; pause ONLY at the two choices (placement; transport + window) and
  at the confirm gate (§4a).
- **Help me choose = the user asked you to compare or to pick** ("which is cheapest?", "pick
  the cheapest for me"). Build the two-total table in `references/COST_COMPARISON.md`. If
  autopilot is also on AND the user named the rule ("pick the cheapest" = "cheapest total";
  "fewest shipments"; "prefer warehouse X, else cheapest") AND the rule yields one answer with
  no tie, apply it and say so: "Rule 'cheapest total' picked pl…a1 (107.21 USD vs 210.40)".
  A tie, or a quote the rule cannot price → show the table and wait.
- "Just get it done" with a missing address is neither: it is an intake ✗.

## 4. The chain

| Stage | Compound tool (default) | Granular Amazon operations (poll each write, §4b) | Mode A: what you write (`SHEET_LAYOUT.md`) |
|---|---|---|---|
| Plan workbook (A only) | `fbaInbound_create_sta_sheet(store, plan_name, skus, warehouse_code, ship_date, …)` → `staSpreadsheetId`, `planFolderId`, `manageShipmentsFormulas` | — | Manage Shipments row (`planFolder`, `planName` formulas); Box No. ✎ per item row (Split First: Total Qty ✎); `_state` = STA_CREATED |
| Plan + packing + placement options | `fbaInbound_orchestrate_packing(store, plan_name, source_address, items, boxes, msku_prep_details, sta_spreadsheet_id?)` ~40–60 s → `planId`, `placementOptions[{placementOptionId, placementFee, shipmentCount, shipments[{shipmentId, warehouseId, destination, totals}]}]`; `requiresHumanSelection` → show `packingOptions`, re-call with `selected_packing_option_id` + `plan_id` (the plan continues) | `fbaInbound_setPrepDetails` → `fbaInbound_createInboundPlan` → `fbaInbound_generatePackingOptions` → `fbaInbound_listPackingOptions` → `fbaInbound_confirmPackingOption` → `fbaInbound_setPackingInformation` → `fbaInbound_generatePlacementOptions` → `fbaInbound_listPlacementOptions` | chips `1a.` `1b.` `1c.` DONE + ids, `2.` READY; Manage Shipments `planId`; `_state` = PACKING_GENERATED; STA-Options rendered by the server |
| **User picks a placement** | show the table: placement, shipments, warehouses (code + city, state), fee; aiRank 1 = lowest fee, say so | same | chip `2.` row 6 = `<placementOptionId> (<fee> USD · <warehouseIds>)`; `_state` = PLACEMENT_SELECTED |
| Transport + delivery windows | `fbaInbound_generate_shipment_options(store, plan_id, placement_option_id, ship_date, pallet_info?, limit=3, shipping_solution?, sta_spreadsheet_id?)` ~20–60 s → `placementFee`; per shipment `partnered[]` (the 3 cheapest per shipping mode), `ownCarrier[]`, `deliveryWindows[]` | `fbaInbound_generateTransportationOptions` → `fbaInbound_listTransportationOptions`; own carrier: `fbaInbound_generateDeliveryWindowOptions` → `fbaInbound_listDeliveryWindowOptions` | STA-Options block dropdowns (server); `_state` = OPTIONS_LISTED |
| **User picks per shipment** | ONE `transportationOptionId` and, own carrier, ONE `deliveryWindowOptionId` | same | chips `3.` / `3b.` row 6 ids; `_state.selections` |
| Confirm (§4a) | `fbaInbound_confirm_plan_options(store, plan_id, placement_option_id, [{shipmentId, transportOptionId, deliveryWindowOptionId?}], sta_spreadsheet_id?)` → `confirmedShipments[{shipmentId, fbaId, referenceId, warehouseId, status}]` | `fbaInbound_confirmPlacementOption` → own carrier: `fbaInbound_confirmDeliveryWindowOptions` → `fbaInbound_confirmTransportationOptions` (a window BEFORE transport for own carrier) | row 12 by label (Status, FBA ID, Reference ID, Warehouse ID); chip `4.` DONE; Manage Shipments one row per shipment; `_state` = CONFIRMED |
| Labels | `fbaInbound_get_labels(store, inbound_plan_id, shipment_id, page_type, label_type, number_of_packages, page_size, label_size, sta_spreadsheet_id?)` — note `inbound_plan_id`, not `plan_id` | same tool | A: the server saves `<FBA id>.pdf` into the plan folder and links it (nothing to write); B: decode `labelData` where the user said; `_state` = LABELS_DOWNLOADED |
| Packing list | `fbaInbound_create_packing_list(store, plan_id, sta_spreadsheet_id?, confirmed_shipments)` → `amazonBoxes[]` | `fbaInbound_listShipmentBoxes` | A: `Inbound PL` tab (server); B: the 11 columns in the user's form; `_state` = PACKING_LIST_WRITTEN |
| Tracking (own carrier) | `fbaInbound_updateShipmentTrackingDetails(store, plan_id, shipment_id, spd_tracking_items=[{boxId, trackingId}…])` — one call per shipment, every box; LTL/FTL: `ltl_tracking_detail={billOfLadingNumber, freightBillNumber:[…]}` | same tool | Manage Shipments `carrier`, `tracking`, `trackingUploaded`; `_state` = TRACKING_UPLOADED |
| Status | `fbaInbound_sync_shipment_status(store, plan_id, shipment_id)` per shipment | `fbaInbound_getShipment` | Manage Shipments `status`, row 12; terminal (CLOSED / CANCELLED / ABANDONED / DELETED) → `_state` = COMPLETE |

Reading the options:

- **Partnered**: `partnered[]` is a view — the 3 cheapest options of each shipping mode per
  shipment, cheapest first, with `data.counts` carrying Amazon's totals. Raise `limit` (0 =
  all) or read `fbaInbound_listTransportationOptions(placement_option_id, shipment_id)` when
  the carrier the user wants is not among them. Pass `shipping_solution` as the intake's
  carrier type so the answer carries one list; partnered-only also skips the delivery windows.
- **Own carrier**: `ownCarrier[]` has no price — Amazon does not quote your own carrier; every
  own-carrier choice needs a delivery window confirmed BEFORE transport. `Other` is Amazon's
  catch-all for a carrier not on its list.
- **Delivery windows**: Amazon lists windows that start before the ship date — even ones
  already begun — as AVAILABLE. Offer only windows whose `startDate` is on or after the
  user's delivery-window start (and the ship date), `availabilityType` AVAILABLE or
  DISCOUNTED, earliest first; a window that has already begun qualifies only if that date
  falls inside it. Windows expire at `deliveryWindowsValidUntil` — usually 3 days — so a
  far-origin shipment picks a window it can meet, not the first one.
- **Mode B presentation**, same columns as the SellerSheet tabs so nothing is lost:
  placements `Placement | Shipments | Warehouses (code + city, ST) | Placement fee | aiRank`;
  transport per shipment `transportationOptionId | mode | carrier | cost currency` and own
  `transportationOptionId | mode | carrier`, windows `deliveryWindowOptionId | start | end |
  availability`; confirmation `shipmentId | FBA id | warehouse | status` (reference ids arrive
  later); packing list `Image | Box ID | Template | FNSKU | MSKU | ASIN | Quantity | Weight |
  Weight Unit | Dimensions | Unit of Measurement`, one row per box × SKU; labels decoded to
  `<FBA id>.pdf` (local, or `start_drive_upload` to a folder the user named — never silently
  into a SellerSheet folder).

### 4a. The confirm gate

Before `fbaInbound_confirm_plan_options` (or the granular confirms) restate, in money:
the placement option and its fee, every shipment's chosen option with its quote (own
carrier: "no Amazon quote; window <start>–<end>"), and that confirming charges the fee and
locks the carrier at that price with no undo (void windows in §0). Interactive: wait for an
explicit go-ahead to THAT summary — a plain "ok" to an earlier message is not it. Autopilot:
the user's own words asked for the whole thing AND a named rule (or the user) picked every
option; otherwise stop and show the summary. Confirm placement first; for own carrier the
delivery window must be confirmed before transportation.

### 4b. Bounded polling — granular operations only

The compound tools wait for Amazon on the server. A granular write
(`fbaInbound_createInboundPlan`, the `generate*` / `confirm*` / `set*` operations) returns an
`operationId` at once: poll `fbaInbound_getInboundOperationStatus` after 10–15 s, then roughly
double the wait, at most 3 checks. `FAILED` → report `operationProblems` and stop; still
`IN_PROGRESS` after 3 → hand the operation id back to the user instead of looping.

### 4c. After confirmation, per carrier

| Carrier | What the user does next | Void window |
|---|---|---|
| Partnered small parcel (SPD) | print box labels, schedule the pickup with the carrier (Amazon does not); tracking comes from the carrier | 24 h |
| Partnered LTL / FTL | pallet labels + bill of lading from Amazon; freight-ready within 2 weeks of creation; pallet details were required at the transport step | 1 h |
| Own carrier | ship, then upload tracking: one tracking number per box (SPD) or one freight bill / BOL number per shipment (LTL / FTL) — API-created shipments only | any time, no charge |

Constraints worth repeating at the right moment: placement is permanent once confirmed;
changing box contents after placement means regenerating placement options; changing the
source address invalidates the transportation options (regenerate); one freight bill per
shipment; multiple expiration dates for one SKU need separate plans.

### 4d. Fishing for a warehouse (刷仓 / 刷美西仓) — `references/WAREHOUSE_FISHING.md`

The user wants one nearby FC (usually US-West) and says so. A plan's placement set is fixed
for its 3-day validity, so only a NEW plan, another ship-from address or another box split
is a new draw. The reference page is the loop: create, check, keep the hit, cancel the
losers — cancelling them is part of the instruction the user gave.

## 5. Handover file — `references/HANDOVER_TEMPLATE.md`

`fba-inbound-<planName>.md`, created at intake and rewritten after EVERY phase — ids, who
chose what, what is done, what the user must answer, the exact next tool call. Mode A: the
same text in a `_handover` tab of the plan workbook (`add_sheet_tab` once, then
`write_sheet('_handover!A1', [[text]])`) plus the local file when you have a filesystem.
Mode B: next to the user's outputs. `_state` and the workbook are not a substitute: the
handover text is what a human or the next agent reads without the chat.

## 6. Checklist before you say "done"

- [ ] mode and tool path stated in the first reply
- [ ] intake ✓ on every required line, asked in one message
- [ ] autopilot and help-me-choose asked or inferred from the user's words, and recorded
- [ ] every choice made by the user, or by a named rule the user gave
- [ ] the confirm gate: fee and quotes restated in money, explicit go-ahead
- [ ] confirm result carries FBA ids; row 12 / Manage Shipments (A) written
- [ ] labels: A = plan folder + links (server); B = where the user said
- [ ] packing list: A = `Inbound PL` tab (server); B = the 11 columns in the user's form
- [ ] tracking uploaded, or explicitly left for later with the box ids listed
- [ ] status synced and written
- [ ] handover file rewritten with "Next command" filled in
- [ ] CANCELLED exit instead: plan cancelled on Amazon, row 5 chips + row 12 Status + Manage
      Shipments status + handover stage = CANCELLED; row 6 ids and the label links stay as the
      audit trail; "Next command" = none

## Common mistakes

| Mistake | Fix |
|---|---|
| Creating a plan workbook "as my own record" for a user with no FBA spreadsheet | Mode B: no workbook; the handover file is your record |
| Refusing "pick the cheapest for me" outright | Build the comparison; apply the rule only under autopilot + a named rule + no tie, and say which rule chose |
| Confirming on a "yes" given before the fee and quotes were on screen | Restate them in money, then ask (§4a) |
| Offering the first AVAILABLE window | Filter by the delivery-window start / ship date first; Amazon lists past windows as AVAILABLE |
| Pasting every transportation option into the reply | Show the 3 cheapest per mode; read the full list only when the user names a carrier that is missing |
| Treating `_state` or the workbook as the handover | Write `fba-inbound-<planName>.md` every phase |
| Asking optional lines (label sizes, expiration) as if required | Ask required ✗ lines; optional lines get defaults you state |
| Hand-writing STA-Options / Inbound PL rows | Pass `sta_spreadsheet_id`; the server renders the sidebar's tabs |
| Stopping after every tool in autopilot | Pause only at the two choices and the confirm gate |
| Polling a compound tool | It already waited; only a granular write needs §4b |
