# Handover file — `fba-inbound-<planName>.md`

Written after EVERY phase (create it at intake, rewrite it in place). It is what a human or
the next agent reads to continue without the chat. Mode A: the text goes into a `_handover`
tab of the plan workbook (`add_sheet_tab` once, then `write_sheet('_handover!A1', [[text]])`),
beside `_state!A1`; also a local file when you have a filesystem. Mode B: saved next to the
user's outputs (local directory or the Doc/Sheet the user named).

Fill every field; write `—` for "not yet", never leave a field out.

```markdown
---
mode: A | B
store: MYSTORE-US
planName: <plan name>
stage: INTAKE | STA_CREATED | PACKING_GENERATED | PLACEMENT_SELECTED | OPTIONS_LISTED | CONFIRMED | LABELS_DOWNLOADED | PACKING_LIST_WRITTEN | TRACKING_UPLOADED | COMPLETE | CANCELLED
planId: wf… | —
packingOptionId: po… | —
packingGroupId: pg… | —
placementOptionId: pl… | —          # chosen by: user | rule "<rule>" (autopilot)
shipments:
  - shipmentId: sh…
    warehouseId: XYZ1
    transportOptionId: to… | —      # chosen by: user | rule
    deliveryWindowOptionId: … | —   # own carrier only
    fbaId: FBA… | —
    referenceId: — 
    status: UNCONFIRMED | WORKING | SHIPPED | … 
    boxes: 15
    trackingUploaded: false
workbook: https://docs.google.com/spreadsheets/d/<id> | —     # mode A
planFolder: https://drive.google.com/drive/folders/<id> | —   # mode A
outputs:                                                      # mode B
  placements: <path or link>
  transport: <path or link>
  packingList: <path or link>
labels: <drive url | path> | —
updatedAt: 2026-01-01T00:00:00Z
---

## Intake (✓ / ✗ / ?)
- ship-from address: ✓ <warehouse code or one-line address>
- products + quantities + box spec: ✓ <n SKUs, n boxes>
- carrier type / mode / preferred carrier: ✓ USE_YOUR_OWN_CARRIER / GROUND_SMALL_PARCEL / —
- ship date / delivery window start: ✓ 2026-01-08 / 2026-01-12
- preferred warehouse id(s): — 
- pallet (declared value / freight class / pallet lines): n/a
- autopilot: no | yes ("<user's words>")
- help me choose: no | yes, rule "<rule>"

## Done
- <timestamp> — <what, by which tool, with which ids>

## Waiting on the user
- <the one decision or input needed now, with the options already listed>

## Next command
`<the exact next tool call, arguments filled in>`

## Rulings
- <every choice, who made it (user / rule), and the alternative that was not taken>

## Log
- <timestamp> — <one line per tool call: tool, ids, result or error sentence>
```

Rules:
- Ids are copied from tool results, never typed from memory.
- "Waiting on the user" and "Next command" are never both empty unless `stage` is COMPLETE
  or CANCELLED.
- On any error, the sentence from `notification.message` goes into the Log verbatim.
