# Action sheets — operator input surfaces

The `_raw_*` + `SQL()` pattern in `growable-tables.md` is for **read-mode/list views** — operator scans data, doesn't fill in cells. This file is the complement: **action sheets** where the operator types into the sheet to drive a workflow (filters, acknowledgements, manual overrides).

Anchored in the live SellerSheet vendor workbook redesign (May 2026). The three vendor sheets — `Vendor Orders`, `Vendor PO Items`, `Vendor PO Status` — are the canonical reference. If anything in this doc conflicts with what those sheets do, those sheets win.

## The decision: 2-row header vs 4-row header

A sheet is one of two shapes. Pick before writing anything else.

| Shape | When | Header rows | Data starts |
|---|---|---|---|
| **2-row** (action) | Primary workflow surface — operator's main edit target | Row 1 keys, Row 2 display | Row 3 |
| **4-row** (filter + browse) | List/status surface with operator-tunable filters on top | Row 1 keys, Row 2 filter labels, Row 3 filter inputs, Row 4 display | Row 5 |

**2-row** is for sheets like `Vendor PO Items` — operator fills Ack Code / Reject Reason in the data rows themselves. The display header row gets the emerald treatment because this surface is "where the work happens."

**4-row** is for sheets like `Vendor Orders` / `Vendor PO Status` — operator scans rows, optionally narrows the list via row-3 filter inputs (store, date range, status, etc.). Display header row gets navy because this surface is "where you browse."

`setFrozenRows(2)` or `setFrozenRows(4)` accordingly. Get this right or scrolling breaks.

## Row anatomy — the four bands

These names appear throughout the GAS code and this skill. Memorize them.

### Row 1 — key headers (code contract, recessed)

The CODE reads/writes by these names via `getColumnMapping(headers)` lookup. Humans should barely see this row. Style:

- Font: **Arial 7pt**, gray `[0.659, 0.682, 0.722]` (`#A8AEB8`)
- Background: white
- Weight: normal (not bold)
- Row height: 14 px
- Values: lowerCamelCase identifiers — `store`, `purchaseOrderNumber`, `sellingParty`, `ackCode1`, `imageUrl`, `lastSyncedAt`

The recessed styling tells the human "this is for the machine — don't worry about it." The header-name lookup means columns can be reordered later without breaking code.

```javascript
// helper used in setupVendorSheet
function styleKeyHeaderRow(sheet, lastCol) {
  sheet.getRange(1, 1, 1, lastCol)
    .setFontFamily('Arial').setFontSize(7).setFontColor('#A8AEB8')
    .setBackground('#FFFFFF').setFontWeight('normal').setVerticalAlignment('middle');
  sheet.setRowHeight(1, 14);
}
```

### Row 2 — emerald label row (action) OR filter-label band (4-row)

In a **2-row sheet**, row 2 is the display header — emerald background with white bold Arial 10pt text. This is "the row humans look at." Example: `Vendor PO Items` row 2 = `Image | Image URL | Store | Vendor Code | PO State | PO Number | Seq # | ASIN | Vendor SKU | Ordered Qty | Back Order OK | Ack Code ✏️ | ...`

In a **4-row sheet**, row 2 is the **filter-label band** — same emerald styling but only spans **columns A–L** (12 cells). Cols M+ get white-background padding so the emerald band stops cleanly mid-row. The narrowing band signals "filters are here; the data viewport extends wider."

```javascript
function styleEmeraldRow(sheet, row, lastCol) {
  sheet.getRange(row, 1, 1, lastCol)
    .setFontFamily('Arial').setFontSize(10).setFontColor('#FFFFFF')
    .setBackground('#10B981').setFontWeight('bold')
    .setVerticalAlignment('middle').setHorizontalAlignment('center');
  sheet.setRowHeight(row, 28);
}

// On a 4-row sheet, emerald only spans A-L:
styleEmeraldRow(ordersSheet, 2, 12);
// Right-pad cols M+ with white so the band stops cleanly:
ordersSheet.getRange(2, 13, 1, lastCol - 12).setBackground('#FFFFFF');
```

### Row 3 — filter input band (4-row only)

Light gray-blue background `[0.929, 0.945, 0.961]` (`#EDF1F5`), italic, Arial 10pt. Cells in A3:L3 are where the operator types filter values. Cols M+ stay white (continuation of the row-2 band-stop).

Filter inputs ARE the data validation surface — apply dropdowns here for Amazon enum values (see "Dropdowns" section below).

```javascript
function styleFilterInputRow(sheet, row, lastCol) {
  sheet.getRange(row, 1, 1, lastCol)
    .setFontFamily('Arial').setFontSize(10).setFontColor('#000000')
    .setBackground('#EDF1F5').setFontStyle('italic').setFontWeight('normal')
    .setVerticalAlignment('middle');
  sheet.setRowHeight(row, 24);
}
```

Default values: `'DESC'` in the Sort Order column; everything else blank. Operator can type a value or pick from the dropdown. Blank = no filter applied.

### Row 4 — navy display headers (4-row only)

Full-width navy `[0.157, 0.2, 0.318]` (`#28334F`) band, Arial 10pt bold white text. Same style as row 2 of a 2-row sheet but in navy because this surface is read-mode, not action-mode.

```javascript
function styleNavyHeaderRow(sheet, row, lastCol) {
  sheet.getRange(row, 1, 1, lastCol)
    .setFontFamily('Arial').setFontSize(10).setFontColor('#FFFFFF')
    .setBackground('#28334F').setFontWeight('bold')
    .setVerticalAlignment('middle').setHorizontalAlignment('center');
  sheet.setRowHeight(row, 26);
}
```

## Emerald vs navy — the action-vs-read rule

This is the single most useful design rule in the whole pattern:

- **Emerald `#10B981`** marks the row the operator EDITS/ACTS on. Display headers of an action sheet (2-row layout), filter-label rows on a browse sheet (4-row).
- **Navy `#28334F`** marks the row the operator READS. Display headers of a list/browse sheet (4-row layout).

Same workbook can have both. The vendor workbook:
- `Vendor PO Items` (action) — row 2 emerald
- `Vendor Orders` (browse) — row 2 emerald (filter labels), row 4 navy (display)
- `Vendor PO Status` (browse) — row 2 emerald (filter labels), row 4 navy (display)

If you find yourself wanting "two emerald rows" on a 4-row sheet (one for filter labels, one for display), stop — you're conflating action and read. The display row must be navy if the operator is browsing, not editing.

## The IMAGE arrayformula slot

If the sheet has product thumbnails, column A holds an IMAGE arrayformula. Code NEVER writes to column A; writes always start at column B.

| Layout | A formula cell | Data range |
|---|---|---|
| 2-row sheet | `A2` | `B3:B` |
| 4-row sheet | `A4` | `B5:B` |

```javascript
// 2-row sheet (Vendor PO Items)
itemsSheet.getRange('A2').setFormula(
  '={"Image"; arrayformula(if(isblank(B3:B),"",IMAGE(B3:B)))}'
);

// 4-row sheet (Vendor PO Status)
statusSheet.getRange('A4').setFormula(
  '={"Image"; arrayformula(if(isblank(B5:B),"",IMAGE(B5:B)))}'
);
```

The literal string `"Image"` is the first element of the array, so the formula cell displays "Image" (the column label) while spilling thumbnails below. Both A2 and A4 inherit the same brand styling as their respective display-header rows — the cell stays emerald or navy with bold white text, and the IMAGE spill below renders against the white data background.

When you write data rows, pass `startCol=2` to `_upsertRows` (or whatever your write helper is) so col A is never touched.

## Dropdowns — Amazon enum cells get warning-mode validation

Any filter/input cell that maps to an Amazon SP-API enum gets a dropdown. Use **warning mode** (`strict: false`, `setAllowInvalid(true)`) so operators can paste arbitrary text without errors — the dropdown is a hint, not a gate.

```javascript
// GAS helper
function setDropdown(sheet, range, values) {
  const rule = SpreadsheetApp.newDataValidation()
    .requireValueInList(values, true)
    .setAllowInvalid(true)  // warning mode — paste-tolerant
    .build();
  sheet.getRange(range).setDataValidation(rule);
}

// MCP equivalent
add_sheet_dropdown(spreadsheet_id, "Vendor Orders!F3",
  ["New", "Acknowledged", "Closed"], strict=false)
```

### Where dropdowns go

| Sheet | Cell | Values |
|---|---|---|
| **Filter rows** (4-row sheets, row 3) | A3:L3 cells matching an enum filter | Amazon enum values |
| **Action columns** (2-row sheets, data rows 3+) | Open range e.g. `L3:L500` | Amazon enum values |
| **Sort order** | Any sheet, last filter col | `["ASC", "DESC"]` (default `'DESC'`) |
| **Boolean filters** | Filter cell | `["true", "false"]` (lowercase — Amazon API casing) |

For data-row dropdowns (action sheets), use a bounded range like `'L3:L500'` rather than `'L3:L'` — Sheets accepts open ranges but Apps Script perf degrades on huge ranges.

### Common Amazon SP-API enum dropdowns

Reusable list — match the API spec exactly (case-sensitive).

| Domain | Cell context | Values |
|---|---|---|
| Vendor PO state (filter) | `Vendor Orders!F3` | `New / Acknowledged / Closed` |
| Vendor PO state (data) | `Vendor PO Items!E:E` | `New / Acknowledged / Closed` |
| PO Item state | `Vendor Orders!I3` | `Cancelled` |
| Is PO Changed | `Vendor Orders!H3` | `true / false` |
| PO status (filter) | `Vendor PO Status!G3` | `OPEN / CLOSED` |
| Confirmation status | `Vendor PO Status!H3`, `Vendor PO Status!O:O` | `ACCEPTED / PARTIALLY_ACCEPTED / REJECTED / UNCONFIRMED` |
| Receive status | `Vendor PO Status!I3`, `Vendor PO Status!R:R` | `NOT_RECEIVED / PARTIALLY_RECEIVED / RECEIVED` |
| Ack Code (input) | `Vendor PO Items!L:L`, `Vendor PO Items!P:P` | `Accepted / Backordered / Rejected` |
| Rejection Reason | `Vendor PO Items!O:O`, `Vendor PO Items!S:S` | `TemporarilyUnavailable / InvalidProductIdentifier / ObsoleteProduct` |
| Sort order | Any filter row | `ASC / DESC` |

### Why warning mode

The user might:
- Paste a multi-row dataset that happens to have the right values — strict mode would reject the paste.
- Type a new value Amazon recently added before this catalog is updated.
- Want to test filtering with a typo to see what happens.

Strict-mode (`setAllowInvalid(false)`) makes all three of those a pain. Use it only when the cell drives a feed submission where invalid values would burn API quota.

## Status chips — color rules per Amazon enum

Apply via `add_sheet_conditional_format` or `setStatusChipRules` (GAS). Use **open ranges** like `C5:C` so new rows inherit. One rule per value.

| Domain | Range | Rule |
|---|---|---|
| PO state | `Vendor Orders!C5:C`, `Vendor PO Items!E3:E` | Acknowledged=GREEN, New=AMBER, Closed=RED |
| PO status | `Vendor PO Status!F5:F` | OPEN=AMBER (action pending), CLOSED=GREEN |
| Confirmation status | `Vendor PO Status!O5:O` | ACCEPTED=GREEN, PARTIALLY_ACCEPTED=AMBER, UNCONFIRMED=AMBER, REJECTED=RED |
| Receive status | `Vendor PO Status!R5:R` | RECEIVED=GREEN, PARTIALLY_RECEIVED=AMBER, NOT_RECEIVED=RED |

**Semantic rule for color choice**: RED = action needed or terminally rejected; AMBER = in-progress / waiting / partial; GREEN = done / acknowledged / received. "Closed" is GREEN on PO Status (you're done with it) but RED on PO State (you can't act on it anymore). Same word, different color, because the operator's relationship to it differs.

### Two chip palettes — when to use which

The brand palette in `brand-standards.md` gives bold chips for low-density use:

| Bold (brand) | Hex | Use when |
|---|---|---|
| GREEN | `#8ECA94` | Single chip in a row — title bar, KPI badge |
| AMBER | `#FFD86B` | Same |
| RED | `#ED736E` | Same |

But on a long status column where every row has a chip, the bold palette is visually loud. Use the soft Excel-pastel palette instead:

| Soft (pastel) | Hex | Use when |
|---|---|---|
| GREEN | `#C6EFCE` / fg `#1F7333` | Status column on a 100+ row sheet |
| AMBER | `#FFF2CC` / fg `#996600` | Same |
| RED | `#FFC7CE` / fg `#9C0006` | Same |

The vendor sheets use soft pastels on 4 status columns × 16+ rows because at that density, bold chips would be exhausting to scan. Apply the bold palette for KPI tiles, freshness pills, and one-off badges.

(Soft pastels overlap with `#FFF2CC` in the brand spec — there it's labeled "footer callout / overflow notice." Two roles for one color is a known overlap; in practice they don't appear on the same tab.)

## Editable-cell marker (pencil emoji)

Columns the operator EDITS in data rows get a `✏️` pencil emoji in the display header. Visually signals "type here" so the operator doesn't waste time hunting for the right cell.

Example display headers from `Vendor PO Items`:
- `Ack Code ✏️` — operator fills in
- `Ack Qty ✏️` — operator may override the pre-filled value
- `Ship Date ✏️` — operator fills if Backordered
- `Reject Reason ✏️` — operator fills if Rejected
- `Ack Code 2 ✏️` / etc. — optional second acknowledgement set

Non-editable columns get no marker. Apply sparingly — if every column has a pencil, the signal is lost.

This is the only place emojis appear in vendor sheet headers. Don't decorate with stars, checkmarks, or other emoji.

## Column-reorder discipline

Action sheets evolve — columns get added, reordered, removed. The pattern that survives reorders:

### Rule 1 — Always read via `getColumnMapping(headers)`

GAS helper. Reads row 1 (key headers), returns a `{name: 1-based-col}` map. Use the map to find columns instead of hardcoding indices.

```javascript
const headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
const col = getColumnMapping(headers);
const poCol = col.purchaseOrderNumber;       // resolves to current position
const stateCol = col.purchaseOrderState;
```

### Rule 2 — Keep fallback indices in sync with the documented layout

When code falls back to a hardcoded index (because the header lookup failed), that fallback must match the CURRENT canonical layout — not an earlier one. A stale fallback silently writes to the wrong column.

```javascript
// Correct — fallback matches new layout (PO Number at col D on Vendor Orders)
const poIdx = (col.purchaseOrderNumber || 4) - 1;

// Wrong — fallback still points to old col B from before the reorder
const poIdx = (col.purchaseOrderNumber || 2) - 1;
```

When you reorder columns, grep for every `col.X || N` pattern and verify `N` against the new layout. Document the layout in a SHEET LAYOUT block at the top of the source file so the next person doesn't have to reverse-engineer it.

### Rule 3 — Reorder existing data, don't just rewrite headers

If a sheet already has data when you reorder columns, rewriting only row 1 leaves all rows below in the OLD column order — silent data corruption. Either:

1. Read all data, remap each row to the new positions, write back. Then clear orphaned cells in removed columns.
2. Clear the data entirely and re-sync from the upstream source (Amazon, DB) after deploying the new code.

Option 2 is cleaner when re-sync is cheap. Use option 1 when re-sync is expensive (API quota, slow upstream).

## Removing columns — three-step cleanup

Removing columns from an action sheet has more residue than adding:

1. **Clear the now-orphaned column range** — old values stay in cols R/S/T after you shrink to col Q. `clear_sheet_range(spreadsheet_id, 'Sheet!R1:T1000')`.
2. **Delete orphaned conditional format rules** — chip rules on `Q5:Q` and `R5:R` continue to exist and apply to whatever new content occupies those columns. They won't match the new data so they silently no-op, but cosmetically they're cruft. Use `sheet_batch_update` with `deleteConditionalFormatRule` requests to remove them.
3. **Delete orphaned dropdown rules** — `add_sheet_dropdown` rules persist after column removal. Same as above — silently no-op on numeric data but cruft. Use `set_sheet_data_validation` with an empty rule, or `sheet_batch_update` with `setDataValidation` clearing the range.

Steps 2 and 3 are cosmetic if the orphaned rules can never match the new content. Skip them on a deadline; clean them when polishing.

## Idempotent re-setup

The setup function must be safe to run multiple times — operator may click the Setup button after every Amazon API change. Pattern:

```javascript
function ensureTab(name) {
  let sheet = ss.getSheetByName(name);
  if (!sheet) sheet = ss.insertSheet(name);
  return sheet;
}

function setStatusChipRules(sheet, a1Range, mapping) {
  const range = sheet.getRange(a1Range);
  const rangeA1 = range.getA1Notation();
  // Drop existing rules targeting this same range — keeps reruns idempotent
  const filtered = sheet.getConditionalFormatRules().filter(function(r) {
    return !r.getRanges().some(function(rg) { return rg.getA1Notation() === rangeA1; });
  });
  // ... add fresh rules
  sheet.setConditionalFormatRules(filtered.concat(newRules));
}
```

Idempotency rules:
- Use `ensureTab` not `insertSheet` so re-runs don't error.
- For conditional formats: filter out existing rules on the SAME RANGE before adding new ones. Don't just blindly append — you'll end up with N copies of every chip rule.
- For dropdowns: re-applying overwrites cleanly. No filter step needed.
- For number formats: idempotent; re-apply freely.
- For frozen rows / col widths: idempotent.
- For values: `write_sheet` overwrites cleanly. Don't trust `getLastRow()` if you have arrayformulas in col A — they make `getLastRow()` return spurious values. Use a helper that scans a specific data column instead:
  ```javascript
  function _lastRowOfColumn(sheet, colNum) {
    const lastRow = sheet.getLastRow();
    if (lastRow < 1) return 0;
    const values = sheet.getRange(1, colNum, lastRow).getValues();
    for (let i = values.length - 1; i >= 0; i--) {
      if (values[i][0] !== '' && values[i][0] != null) return i + 1;
    }
    return 0;
  }
  ```

## Quick reference — the 9 rules

When building an action sheet, this is the checklist:

1. **Decide shape**: 2-row (action surface) or 4-row (filter + browse). Frozen rows match.
2. **Row 1 = code contract**: lowerCamelCase keys, Arial 7pt gray, recessed.
3. **Emerald = where operator acts; Navy = where operator reads.** Never both on same row.
4. **Filter rows narrow to A-L**: emerald band stops at col 12, cols M+ white-padded.
5. **Image col A = arrayformula at A2 (2-row) or A4 (4-row)**. Writes always start col B.
6. **Amazon enum cells get dropdowns** in warning mode (`strict: false`).
7. **Status chips use soft pastels** (`#C6EFCE / #FFF2CC / #FFC7CE`) on long columns, bold brand on KPIs.
8. **Editable data columns get `✏️`** in display header. Sparingly.
9. **Reads use `getColumnMapping(headers)`**, fallbacks match current layout, reorder remaps existing data.

## See also

- `reference/brand-standards.md` — palette + font + number formats
- `reference/conditional-formatting.md` — chip + gradient mechanics
- `reference/growable-tables.md` — read-mode/list pattern (the complement to this file)
- `reference/image-pattern.md` — column-A arrayformula deep-dive
- `reference/mcp-gotchas.md` — `getLastRow()` + arrayformula gotcha
