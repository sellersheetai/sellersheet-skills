# 'Images Generation' sheet contract

The operator's structured record/control surface — the **`Images Generation` tab inside the
operator's catalog spreadsheet** (their main workbook for the store). Locate the catalog
spreadsheet via `get_user_context` (or `search_drive_files`), then open its `Images Generation`
tab — don't hardcode a spreadsheet ID across stores. If the tab doesn't exist yet, create it (or
ask the operator) before recording.

## Shape
- **3 header rows.** row1 = machine keys (`s0_ref`,`s0_v1`,…), row2 = section labels
  (`Slot 0`,`Slot 1`,…), row3 = human labels (`S0 Ref`,…) with **cell-notes that document the
  whole workflow — read row-3 notes before operating a new workbook.**
- **Data starts row 4.** Lead cols A–L: store, sku, asin, sample_image_1-3, product_context,
  ref_image_1-3, overall_status, notes. Then slot blocks s0–s8 (see slot-canon.md for columns),
  then A+ a1–a5 / p1–p5.

## Rules
- **ONE ROW PER SKU.** A variation family = N rows. The main image goes in that row's `s0_v1`.
- **Slots = image ROLES of that SKU** (s0 main, s1.. secondary), NOT sibling colors.
- Versions: first gen → `v1`; iterations → `v2`, `v3`. Keep superseded versions in v2/v3 with a
  note in the status cell rather than deleting.
- **Image cells are independent `=IMAGE("url")`** — safe to write directly. Drive → thumbnail proxy
  `=IMAGE("https://drive.google.com/thumbnail?sz=w400&id=<ID>")`; CDN https URLs render directly.
- **scores** cell = your own compact fidelity read, written by the agent (e.g. `{"product_fidelity":98,...,"verdict":"pass"}`).
- **status** cell lifecycle: PLANNED → BRIEF_READY → GENERATING → V1_READY → (EDIT_V1: …) →
  V2_READY → APPROVED:V{n}; plus SKIPPED:/FAILED:/RETRY.
- **overall_status** (col K) is the workbook gate: EMPTY→PLAN→PLANNING→BRIEFS_READY→GENERATE→
  GENERATING→REVIEW→COMPLETE.
- After writing, **read the row back and scan for `#VALUE!/#REF!/#SPILL!/#N/A`** before reporting done.

## Renumber note (done 2026-06-04)
This workbook was renumbered from s1–s9 to **s0–s8 (s0 = main)** by rewriting header rows 1–3 across
cols M:CX. If you meet a workbook still on s1–s9, either follow its numbering or renumber the same way.
