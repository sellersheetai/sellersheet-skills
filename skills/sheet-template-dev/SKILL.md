---
name: sheet-template-dev
description: Use when DEVELOPING or changing a SellerSheet GAS tab template (Vendor / noon / SP-SB-SD / STA-style operator sheets in the Apps Script add-on) — authoring the layout with the buildSheet(spec) engine, verifying it headlessly via clasp run + the test MCP service account, and promoting the finished tab into the master template workbook so production provisions by COPYING the tab instead of rebuilding it. NOT for building one-off report sheets through MCP at runtime (that is the sellersheet-sheets skill) and NOT for editing data in an existing sheet.
type: skill
version: 0.1.0
---

# Sheet Template Dev

Develop the **layout** of a SellerSheet operator tab once, in code, verify it headlessly,
then promote it into the **master template** so production just copies it.

There are two audiences for sheet layout, do not confuse them:
- **Runtime MCP build** of a one-off report → `sellersheet-sheets` skill (MCP tools).
- **Authoring a reusable tab template** in the GAS add-on → **this skill** (`buildSheet`).

## The one engine — `buildSheet(spec)`

`google_sheet_addon/src/sheet_engine.js` is the single layout engine. It implements the
**Header grammar (v2)** (full grammar: `sellersheet-sheets/SKILL.md` → "Header grammar").
A tab is a stack of typed header **bands** above a data zone; the engine computes row
numbers, paints each band, **hides the machine row**, writes EN·CN notes, and lays out the
data zone (image array-formula, select checkbox, dropdowns, conditional formats, basic
filter, frozen rows/cols, column widths).

```js
buildSheet({
  name: 'noon Shipments',
  keys: ['asn_nr','exref_nr','status', ...],          // row 1 (hidden) — drives the column map
  banner: 'SellerSheet • noon Shipments',
  controls: [                                          // → label row + value row
    { col:'A', label:'Store ✎',  cls:'req', note:{en,cn} },
    { col:'B', label:'Status ✎', cls:'opt', dropdown:[...], default:'All', note:{en,cn} },
    { col:'C', label:'Page Size ✎', cls:'opt', default:200, note:{en,cn} },
  ],
  display: { headers:[...], notes:{ key:{en,cn} } },   // navy/slate header + EN·CN notes
  conditional: [{ key:'status', when:'contains', value:'SCHEDULED', bg:'#d4edda' }, ...],
  imageCol: { from:'image_url' },                      // optional col-A IMAGE() array-formula
  select: false, filter: true, frozenCols: 1, colWidths:{ asn_nr:130 },
}, spreadsheetIdOrSs, sheetName)
// → { sheet, rowOf:{machine,banner,controlLabel,controlValue,display}, dataStart, width }
```

**Band → shape:** include `controls` → control-block / filter+browse (data row 6, freeze 5);
omit it → action shape (data row 4, freeze 3). `bands[]` paints row-2 section spans instead
of a plain banner (STA / noon Inbound ①②③).

**Conventions baked in** (don't re-specify): emerald banner never merged, no row heights,
machine row hidden, navy display / slate font, gold=req · white=opt · slate=auto label
colors, `✎` on editable labels, EN·CN notes via `{en,cn}`.

## Migrate an existing builder onto the engine

Keep the public `setupXSheet()` name (the sidebar + clasp-run call it) — replace the body
with `return buildSheet(SPEC, ...)`. The list/write functions that populate the tab are
unchanged; they read/write by the same row constants the engine reports in `rowOf`.

## Verify headlessly — the loop (no browser)

```bash
# from google_sheet_addon/
npm run push:test                                   # clasp push to the test GAS project
npm run run:test -- setupXSheet --params '["<devSheetId>"]'   # clasp run the builder
```
Then read it back with the **test MCP service account** (it can read/write/note the dev
workbook `1DFCqlJXianyPhHRLYqCVXpi7r5QVOmSHCHXOSuU27Zc`):
`read_sheet` (values + FORMULA render for array-formulas), `get_sheet_notes` (EN·CN notes),
`list_sheet_tabs`/`get_sheet_metadata` (frozen rows, hidden row 1). Diff against the
expected layout. This is the same loop that verified the noon Shipments work.

clasp run uses the `testrun` user (7-day Testing-mode OAuth TTL); push uses `test`. See
`google_sheet_addon/deploy/README.md`.

## Promote to the master template → provision by copy

Master template workbook: **`1BVm1knCy_9DZGtCsaD9dKjvRVBMnF2_Vj7kyRiENF40`** (also the
`MASTER_TEMPLATE_ID` constant in `src/common.js`). Once a tab's layout is verified:

1. **Promote** the finished tab into the master (build it there, or copy the verified tab in).
2. **Provision by copy** — production creates a user's tab by copying the pristine master
   tab (`copy_sheet_tab` / Sheets-API `spreadsheets.sheets.copyTo`) and renaming it.
   Formatting, notes, conditional formats, dropdowns, frozen panes and image formulas come
   for free in one call — no cell-by-cell rebuild, far fewer MCP/GAS calls.

`buildSheet` is therefore a **dev-time** tool (author/repair the master), not a runtime path.

## Checklist

- [ ] Spec authored against the Header grammar; shape chosen (action / control-block / filter).
- [ ] `npm run push:test` + `clasp run` the builder on the dev workbook.
- [ ] MCP read-back: row positions, control values/dropdowns/defaults, EN·CN notes, hidden
      row 1, frozen rows, conditional chips, image array-formula (FORMULA render).
- [ ] Migrated builders keep their public name; populate/list fns still pass.
- [ ] Promote to master `1BVm1knCy…`; production provisions by copy.
- [ ] Deploy GAS test → verify → prod.
