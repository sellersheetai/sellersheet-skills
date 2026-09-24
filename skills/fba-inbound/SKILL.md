---
name: fba-inbound
description_zh: "创建FBA货件、入库计划、发货到亚马逊、补货、STA表、分仓方案、运输方案、箱标、装箱单、上传物流单号、货件状态、取消计划、刷美西仓（刷仓换低运费）——无论是否使用 SellerSheet FBA 表格。"
description_en: "Use when a user wants stock sent to Amazon FBA — \"create FBA shipment\", \"inbound plan\", \"send to Amazon\",…"
author: SellerSheet AI
version: 0.12.0
description: >-
  Use when a user wants stock sent to Amazon FBA — "create FBA shipment", "inbound plan",
  "send to Amazon", "restock FBA", "STA sheet", "placement options", "transport options",
  "FBA box labels", "packing list", "upload tracking", "shipment status", "cancel plan",
  "get a US-West warehouse" — whether or not they use the SellerSheet FBA spreadsheet,
  including "just do the whole thing" and "pick the cheapest for me" requests.
  中文触发词：创建FBA货件、入库计划、发货到亚马逊、补货、STA表、分仓方案、运输方案、箱标、装箱单、上传物流单号、货件状态、取消计划、刷美西仓（刷仓换低运费）——无论是否使用 SellerSheet FBA 表格。
---

# FBA Inbound

Two modes, one intake gate, one chain of tools, one handover file. Read this page, then
the ONE mode reference that applies. Run the standard preflight in
[`sellersheet-shared`](../sellersheet-shared/SKILL.md) first (`get_user_context` succeeds,
`data.canUseMcp` is true; store refs follow its `<store>-<CC>` rule).

## 0. Rules that never change

- **Never choose for the user.** Placement option, transportation option, delivery window,
  packing option: the server lists, the user picks, you record. The only exception is a
  rule the user named under autopilot (§3) — and then you say which rule chose.
- **Intake before Amazon.** Nothing is created (`create_sta_sheet`, `orchestrate_fba_packing`)
  while a REQUIRED intake line is ✗. "Just do it" is not an answer to a missing address.
- **Confirm is irreversible** on Amazon's side. Cancel (`cancel_inbound_plan`) only when the
  user says "cancel".
- **Ids come from tool results only** — box ids, FBA ids, reference ids, option ids are never
  typed from memory or invented.
- Indian (IN) stores are read-only. Amazon writes need SP write access on the key; a
  read-only key stops at listing and says so.
- Mode B never touches the SellerSheet FBA spreadsheet or a plan workbook. Mode A never
  builds a parallel sheet.

## 1. Pick the mode in the first message

| | Mode A — SellerSheet | Mode B — standalone |
|---|---|---|
| Condition | `get_user_context().data.workspace_config.userSettingBySpreadsheet.fbaSpreadsheetId` is set AND the user has not asked for another destination | no FBA spreadsheet id, OR the user said "no sheet" / keeps stock elsewhere / named another output (HTML, their own sheet, Excel) |
| Where things live | the plan workbook `create_sta_sheet` builds (the sidebar's own); STA-Options, Inbound PL and the label links are rendered by the server when you pass `sta_spreadsheet_id`; Manage Shipments row; `_state` | wherever the user said: chat tables, an HTML page, their Google Sheet (`write_sheet`), a local `.xlsx`; labels as a file or Drive link |
| Reference | `references/MODE_A_SELLERSHEET.md` | `references/MODE_B_STANDALONE.md` |

State the mode in your first reply ("Mode A — I'll use your SellerSheet FBA spreadsheet" /
"Mode B — no SellerSheet spreadsheet; outputs go to …"). If it is genuinely unclear, that is
the ONE question you ask before the intake list. Never mix modes in one plan.

## 2. Intake gate — `references/INTAKE.md`

Print the 16-line checklist with ✓ / ✗ / ? per line, in the first reply, after the mode.
Ask for every ✗ REQUIRED line in ONE message, then stop. Lines 14 (autopilot) and 15
(help me choose) are always asked once, in that same message, unless the user's words
already answered them.

Required lines: store, ship-from address, MSKUs + units, box spec (Box First), carrier
type, transportation mode, ship date, delivery-window start (own carrier), pallet details
(LTL/FTL). Optional: preferred carrier, preferred warehouse id(s), own-carrier rates.

## 3. Autopilot and "help me choose"

- **Autopilot = the user said, in their own words, to complete it end to end** ("do the
  whole thing", "run it through to labels"). With every required line ✓, run the chain
  without pausing between tools; pause ONLY at the two choices (placement; transport +
  window).
- **Help me choose = the user asked you to compare or to pick** ("which is cheapest?",
  "pick the cheapest for me"). Build the comparison in `references/COST_COMPARISON.md`.
  If autopilot is also on AND the user named the rule ("pick the cheapest" = "cheapest
  total"; "fewest shipments"; "prefer warehouse X, else cheapest") AND the rule yields one
  answer with no tie, apply it and say so: "Rule 'cheapest total' picked pl…a1 (107.21 USD
  vs 210.40)". Restate the rule in your reply so the user can correct it. Otherwise show
  the table and wait.
- "Just get it done" with a missing address is neither: it is an intake ✗.

## 4. The chain (both modes)

```
get_user_context → [inventory check, optional]
→ create_sta_sheet (A only)
→ orchestrate_fba_packing  → placement options            ← user picks (or rule)
→ generate_shipment_transport_options → per shipment: partnered / own / windows  ← user picks
→ confirm_fba_placement → FBA ids
→ get_labels (+ label_size) → PDF   →   create_fba_packing_list → rows / Inbound PL
→ update_shipment_tracking_details (own carrier, per shipment, all boxes in one call)
→ sync_fba_shipment_status
```

Mode A passes `sta_spreadsheet_id` to orchestrate, transport, confirm, labels and packing
list — the server renders STA-Options / Inbound PL / the label links in the sidebar's own
layout; you still write the stepper cells, row 12, Manage Shipments and `_state`. Mode B
never passes it and presents every result in the user's form.

Own carrier: pick the earliest `deliveryWindows[]` entry with `availabilityType` AVAILABLE
whose `startDate` is on or after the user's Delivery Window Start Date (a window that has
already begun qualifies only if that date falls inside it). Partnered: windows are bundled
into the transport option. Note `get_labels` takes `inbound_plan_id` where every other tool
takes `plan_id`.

## 4b. Use case — fishing for a warehouse (刷仓 / 刷美西仓) — `references/WAREHOUSE_FISHING.md`

The user wants a specific destination (usually a US-West FC to cut own-carrier freight) and
says so: "刷美西仓", "get me a West Coast warehouse", "I want LAX/ONT/SBD". Amazon's placement
set is fixed per plan for its 3-day validity (re-running placement options on the SAME plan
returns the SAME set), so the only way to get a different offer is a NEW plan, a different
ship-from address, or a different box/quantity split. The reference page is the loop:
create several plans at once when inbound capacity allows, keep the one whose single
shipment lands in a wanted FC, cancel the rest; when capacity is short, create → check →
cancel → create again. The user's wanted FC list is the named rule; cancelling the losing
plans is part of the instruction they gave.

## 5. Handover file — `references/HANDOVER_TEMPLATE.md`

`fba-inbound-<planName>.md`, created at intake and rewritten after EVERY phase — ids,
choices and who made them, what is done, what the user must answer, the exact next tool
call. Mode A: the same text lives in a `_handover` tab of the plan workbook (`add_sheet_tab`
once, then `write_sheet('_handover!A1', [[text]])`) — `start_drive_upload` only opens a
session that needs an HTTP PUT, which an MCP-only agent cannot do; write the local file too
when you have a filesystem. Mode B: saved next to the user's outputs. `_state` and the
workbook are NOT a substitute: the handover text is what a human or the next agent reads
without the chat.

## 6. Checklist before you say "done"

- [ ] mode stated in the first reply
- [ ] intake ✓ on every required line, asked in one message
- [ ] autopilot and help-me-choose asked or inferred from the user's words, and recorded
- [ ] every choice made by the user, or by a named rule the user gave
- [ ] confirm result carries FBA ids; row 12 / Manage Shipments (A) written
- [ ] labels: A = plan folder + 3 links (server); B = where the user said
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
| Treating `_state` or the workbook as the handover | Write `fba-inbound-<planName>.md` every phase |
| Asking optional lines (label sizes, expiration) as if required | Ask required ✗ lines; optional lines get defaults you state |
| Hand-writing STA-Options / STA-PL rows | Pass `sta_spreadsheet_id`; the server renders the sidebar's tabs |
| Stopping after every tool in autopilot | Pause only at the two choices |
