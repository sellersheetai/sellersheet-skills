---
name: fbn-inbound
description_zh: "noon 入仓、FBN 发货、创建 ASN、加商品到 ASN、封箱、预约送仓时段、重新预约、取消 ASN、noon 货件状态。"
description_en: "Use when a user wants stock sent into noon's fulfilment centres (FBN, Fulfilled by noon) — \"create a noon…"
author: SellerSheet AI
version: 0.16.6
metadata: {apis: [noon], pattern: Gate}
description: >-
  Use when a user wants stock sent into noon's fulfilment centres (FBN, Fulfilled by noon) —
  "create a noon ASN", "FBN inbound shipment", "send stock to noon", "which SKUs can go to FBN",
  "add items to the ASN", "seal the ASN", "book a noon delivery slot", "reschedule the noon slot",
  "cancel the ASN", "where is my noon shipment". Runs noon's inbound flow with the SellerSheet MCP
  tools only — no spreadsheet is read or written during the steps. Do NOT use for Amazon FBA
  shipments (use fba-inbound) or for noon report data such as orders, finance or FBN inventory
  aging (use noon-report-data).
  中文触发词：noon 入仓、FBN 发货、创建 ASN、加商品到 ASN、封箱、预约送仓时段、重新预约、取消 ASN、noon 货件状态。
---

# FBN Inbound (noon)

Send stock into a noon fulfilment centre as an ASN (advance shipping notice): pick the SKUs,
create the ASN, add the lines, seal it, book a delivery slot. Everything runs through the
`noon_inbound_*` MCP tools and is reported in chat. Preflight first:
[`sellersheet-shared`](../sellersheet-shared/SKILL.md) — `get_user_context` succeeds and
`data.canUseMcp` is true.

**The store ref.** noon tools take a ref from
`get_user_context().data.noonAccountInfo.accounts[].store_refs` — `<account>-<CC>`, e.g.
`myNoon-AE`. The `-CC` is the destination country of the ASN. No connected noon account → the
user connects one on the SellerSheet dashboard first.

**The ASN page on noon.** Every ASN has a page in noon's seller portal:
`https://fbn-inbound.noon.partners/en-<cc>/asn/<asn_nr>?project=<project_code>` — `<cc>` is the
store ref's country in lower case (`ae`, `sa`, `eg`), `<project_code>` is the `project_code` of
the same account in `get_user_context().data.noonAccountInfo.accounts[]`. Give the ASN number
as this link after Create and again after Schedule, so the user can open the shipment on noon.

## 0. Rules

- **No spreadsheet during the steps.** Do not read or write a sheet while running the flow; the
  record is the chat. Only when the user asks for it, write ONE summary at the end (the ASN,
  its lines, the booked slot) with the sheet tools — see the sellersheet-sheets skill.
- **noon holds the state.** Before any write on an existing ASN, read it with
  `noon_inbound_GetShipment`; never assume a status from earlier in the conversation.
- **Never choose for the user.** The warehouse, date and time slot are the user's pick — unless
  the user named a rule for autopilot (§4), and then say which rule picked.
- **Writes need approval.** `noon_inbound_CreateShipment`, `noon_inbound_UpdateShipmentItems`,
  `noon_inbound_DeleteShipmentItems`, `noon_inbound_UpdateShipmentStatus` and
  `noon_inbound_ScheduleShipment` change the ASN on noon. Interactive: show what will change,
  wait for a yes. Autopilot: only what the user's own words asked for.
- **Ids come from tool results only** — the ASN number from the create or list result, the
  warehouse code / date / slot from `noon_inbound_GetSlotAvailability`.
- **Global sellers only.** If any inbound tool answers 403 `PERMISSION_DENIED` "This API is only
  available to global sellers", stop: noon offers the inbound API only to accounts enrolled in
  its global (cross-border) seller programme. Say so, suggest the user asks noon partner support
  to enable it, and do not retry. The account's other noon tools are unaffected.

## 1. The five stages

Report progress as one line after every stage, the same five steps the SellerSheet sheet shows:
`1. Prepare ✓ · 2. Create ✓ A0… · 3. Items ✓ 3 SKU · 120 units · 4. Seal ▸ · 5. Schedule`.

| Stage | Tool | Done when |
|---|---|---|
| 1. Prepare | `noon_inbound_ListEligibleItems` (page with `next_token` until `''`) | every SKU the user wants is listed |
| 2. Create | `noon_inbound_CreateShipment` (`store`, `exref_nr`) | `data.shipment.asn_nr`, status `ASN_STATUS_CREATED` |
| 3. Items | `noon_inbound_UpdateShipmentItems` (`asn_nr`, `items`) | `expected_qty` and `total_sku_count` equal what the user asked for |
| 4. Seal | `noon_inbound_UpdateShipmentStatus` (`action` SEAL) | status `ASN_STATUS_SEALED` |
| 5. Schedule | `noon_inbound_GetSlotAvailability`, then `noon_inbound_ScheduleShipment` | status `ASN_STATUS_SCHEDULED` with the booked warehouse, date and slot |

**1. Prepare.** Only active catalog items with a mapped barcode, a title and an uploaded image
are eligible. A SKU the user wants that is not in the list cannot go on an ASN — say which, and
that it must be fixed in noon's catalog first. Keep each item's `storage_type`.

**2. Create.** `exref_nr` is the user's own reference (a PO number) and is required. noon is
idempotent on it: a reused Ext Ref returns THAT ASN — possibly already sealed, scheduled or
cancelled. Read the returned status: continue from the stage it implies, or, for a cancelled
or expired ASN, ask for a new Ext Ref. The country comes from the store ref; leave
`country_code` and `shipment_type` out.

**3. Items.** Each line is `{partner_sku, qty, storage_type}`, at most 1000 per call; an existing
SKU's qty is overwritten (upsert). `storage_type` must be `STORAGE_TYPE_STANDARD`,
`STORAGE_TYPE_OVERSIZE` or `STORAGE_TYPE_BULKY` — noon rejects `STORAGE_TYPE_UNSPECIFIED`. When
the eligible list shows UNSPECIFIED, ask the user which type (STANDARD for ordinary-size goods)
before sending. Remove a line with `noon_inbound_DeleteShipmentItems`. Verify with
`noon_inbound_ListShipmentItems` and show the lines before sealing.

**4. Seal.** Sealing locks the item list for good. Seal only after the user confirmed the
lines from step 3.

**5. Schedule.** `noon_inbound_GetSlotAvailability` returns warehouses, each with days and
time slots. Summarise it (warehouses, first and last date, slots per day) rather than dumping
every row, let the user pick one warehouse + date + slot, then call
`noon_inbound_ScheduleShipment` with `dst_warehouse_code`, `schedule_date` (`YYYY-MM-DD`) and
`schedule_slot` (`{start, end}` as `HH:MM`) exactly as listed. The dates and times are the
warehouse's local (marketplace) time with no zone: quote them as given, never convert them to
the user's time zone, and say they are the marketplace's time. When recording them in a sheet,
write them as text so the sheet does not turn them into date values.

**Anytime.** `noon_inbound_GetShipment` (status, booked slot, `qty_received` / `qty_putaway`
once receiving starts), `noon_inbound_ListShipments` (find a draft or audit history; filter by
status), RESCHEDULE and CANCEL through `noon_inbound_UpdateShipmentStatus`.

## 2. Gates — check before every write

The same gates the SellerSheet sheet runs. A refused step sends nothing to noon; tell the user
why and what to do instead. A status you have not read yet is not a reason to refuse — read it.

| Step | Runs only when | Otherwise |
|---|---|---|
| Create | the conversation holds no open ASN for this shipment | continue that ASN, or ask whether a second one is really wanted |
| Items / delete lines | status CREATED | sealed or later: the lines are locked — cancel and create a new ASN to change them |
| Seal | status CREATED, lines pushed and confirmed by the user | push or fix the lines first |
| Slot availability | status SEALED (re-running refreshes the list) | CREATED: seal first · SCHEDULED: reschedule first |
| Schedule | status SEALED and exactly one slot chosen | ask the user to pick one slot |
| Reschedule | status SCHEDULED | only a scheduled ASN can be rescheduled |
| Cancel | status CREATED, SEALED or SCHEDULED | RECEIVING or INBOUNDED: noon is already receiving it — it can no longer be cancelled |

**Cancel is final.** A cancelled ASN cannot be reopened, and its Ext Ref keeps returning it. In
an interactive session, say so and cancel only on the user's explicit yes.

**Reschedule** moves a SCHEDULED ASN back to SEALED and releases the booking; then run step 5
again.

## 3. After scheduling

The status moves on noon's side: `ASN_STATUS_SCHEDULED` → `ASN_STATUS_RECEIVING` (the warehouse
is checking the goods in) → `ASN_STATUS_INBOUNDED` (stock is available). `ASN_STATUS_EXPIRED`
means the booked slot passed unused — create a new ASN. Report `qty_received` and
`qty_putaway` against `expected_qty` when the user asks where the shipment is.

## 4. Autopilot ("just do the whole thing")

Run the stages in order and stop at the first gate that refuses. The SKUs and quantities the
request names are the user's confirmation of the lines (step 3, the Seal gate) once
`noon_inbound_ListShipmentItems` shows exactly those; any difference stops for the user. Pick a
slot only by a rule the user stated ("earliest date", "Dubai only", "warehouse RUH07",
"mornings") and say which rule picked it. Without a rule, stop at step 5 with the summary and
ask. Finish with the progress line and the ASN page link.

## 5. Errors

| Answer | Meaning | Do |
|---|---|---|
| 400 `FAILED_PRECONDITION`, `INVALID_ASN_STATUS` | the ASN is not in the status this step needs | `noon_inbound_GetShipment`, report the status, take the step the gate table names |
| 400 `INVALID_ARGUMENT` naming a SKU | the SKU is not FBN-eligible, the qty is not a positive whole number, or the storage type is missing | fix that line and resend |
| 400 slot not available | the slot was taken or the date passed | `noon_inbound_GetSlotAvailability` again and re-pick |
| 403 "only available to global sellers" | the account is not enabled for the inbound API | stop (§0) |
| 429 | rate limited | wait for `retry_after`, then retry once |

Relay each tool's `notification.message`; pass `human_action` on when it is present.

## 6. Example

User: "Send 48 black and 48 white bottles and 24 green ones to noon UAE, PO-2026-014."

1. `noon_inbound_ListEligibleItems` → `MYSKU-BLK`, `MYSKU-WHT`, `MYSKU-GRN` listed,
   `STORAGE_TYPE_STANDARD`. Line: `1. Prepare ✓ 3 SKUs`.
2. Approve → `noon_inbound_CreateShipment(store='myNoon-AE', exref_nr='PO-2026-014')` →
   `A0XXXXXXXPN`, CREATED.
3. Approve → `noon_inbound_UpdateShipmentItems` with the three lines → `expected_qty` 120,
   `total_sku_count` 3; show the lines; the user confirms.
4. Approve → `noon_inbound_UpdateShipmentStatus(action='SEAL')` → SEALED.
5. `noon_inbound_GetSlotAvailability` → "2 warehouses (Abu Dhabi, Dubai), 5 days from Sunday,
   4 slots a day — which one?" → the user picks Dubai, Monday 12:00–14:00 →
   `noon_inbound_ScheduleShipment` → SCHEDULED.
   Line: `1. Prepare ✓ · 2. Create ✓ A0XXXXXXXPN · 3. Items ✓ 3 SKU · 120 units · 4. Seal ✓ · 5. Schedule ✓ Dubai Mon 12:00–14:00`,
   then the ASN page: `https://fbn-inbound.noon.partners/en-ae/asn/A0XXXXXXXPN?project=<project_code>`.
