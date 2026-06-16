# Action sheets — operator input surfaces

> **Quick grammar lives in `SKILL.md` → "Header grammar (v2)".** That section is enough to
> build the common case (the five bands, the three shapes — action / filter+browse /
> control-block — hidden machine row, ✎ glyph, copy-from-master). This file is the deep
> dive: per-band helper code, the narrowing-band rule, IMAGE arrayformula slot, dropdown
> warning mode, status-chip map, idempotent re-setup.

> **⚠ Header System v2 override (2026-06-11)** — the operator adopted "Direction D"
> (see `brand-standards.md` → Header System v2). Where this file conflicts, v2 wins:
> 1. ALL display-header / filter-label rows are **navy `#28334F`** — no emerald display
>    rows anymore (emerald = banner only).
> 2. Input semantics live in the **header font color**: gold `#FFD86B` = required input,
>    white = optional input, slate `#8CA0B3` = button-filled.
> 3. Title banners are **never merged** (merges break freeze panes) — format the band,
>    write the title in the first cell only.
> 4. **Never set row heights** (including image rows and title rows — Sheets defaults only).
> 5. The editable marker is the monochrome glyph **`✎`** (inherits font color), never the
>    emoji `✏️`, and only on pure display rows — never on machine-parsed rows
>    (row-1 keys, Publish Queue row 5).

The `_raw_*` + `SQL()` pattern in `growable-tables.md` is for **read-mode/list views** — operator scans data, doesn't fill in cells. This file is the complement: **action sheets** where the operator types into the sheet to drive a workflow (filters, acknowledgements, manual overrides).

Anchored in the live SellerSheet vendor workbook redesign (May 2026). The three vendor sheets — `Vendor Orders`, `Vendor PO Items`, `Vendor PO Status` — are the canonical reference. If anything in this doc conflicts with what those sheets do, those sheets win.

## The decision: 3-row header vs 5-row header

Every action surface gets a row-1 title banner (merged emerald). Below the banner, a sheet is one of two shapes. Pick before writing anything else.

| Shape | When | Header rows | Data starts |
|---|---|---|---|
| **3-row** (action) | Primary workflow surface — operator's main edit target | Row 1 title, Row 2 keys, Row 3 display | Row 4 |
| **5-row** (filter + browse) | List/status surface with operator-tunable filters on top | Row 1 title, Row 2 keys, Row 3 filter labels, Row 4 filter inputs, Row 5 display | Row 6 |

**3-row** is for sheets like `Vendor PO Items` and `Vendor Log` — operator fills Ack Code / Reject Reason in the data rows themselves (Items) or appends audit entries (Log). On Items the display header row gets the emerald treatment because this surface is "where the work happens"; on Log it gets navy because it's an audit trail.

**5-row** is for sheets like `Vendor Orders` / `Vendor PO Status` — operator scans rows, optionally narrows the list via row-4 filter inputs (store, date range, status, etc.). Display header row gets navy because this surface is "where you browse."

`setFrozenRows(3)` or `setFrozenRows(5)` accordingly. Get this right or scrolling breaks.

## Row anatomy — the five bands

These names appear throughout the GAS code and this skill. Memorize them.

### Row 1 — key headers (code contract, HIDDEN)

The CODE reads/writes by these names via `getColumnMapping(headers)` lookup. **The row is hidden via `sheet.hideRows(1)`** — humans never see it. Style:

- Font: **Arial 7pt**, gray `[0.659, 0.682, 0.722]` (`#A8AEB8`)
- Background: white
- Weight: normal (not bold)
- Row height: 14 px (irrelevant once hidden; kept so unhiding for inspection is sane)
- Values: lowerCamelCase identifiers — `store`, `purchaseOrderNumber`, `sellingParty`, `ackCode1`, `imageUrl`, `lastSyncedAt`

The hidden row tells the human "you don't need to think about this." The header-name lookup means columns can be reordered later without breaking code. `sheet.getRange(1, 1, ...)` still returns the values — visibility doesn't affect reads.

```javascript
// helper used in setupVendorSheet
function styleKeyHeaderRow(sheet, row, lastCol) {
  sheet.getRange(row, 1, 1, lastCol)
    .setFontFamily('Arial').setFontSize(7).setFontColor('#A8AEB8')
    .setBackground('#FFFFFF').setFontWeight('normal').setVerticalAlignment('middle');
  sheet.setRowHeight(row, 14);
}

// Hide after writing — code-contract row never displayed
sheet.hideRows(1);
```

### Row 2 — title banner (emerald, merged, brand presence)

The first row the operator sees. Merged across the full column width. Brand-and-context text — `"SellerSheet • <SheetName>"` — in white Arial 14pt bold on emerald `#10B981`. Row height ~34 px. This is the row that makes every visible tab read as one branded workbook, per the brand-standards rule "Title bars on every visible tab wear emerald."

```javascript
function styleTitleRow(sheet, row, lastCol, titleText) {
  sheet.getRange(row, 1, 1, lastCol).breakApart();  // clear any prior merge
  sheet.getRange(row, 1).setValue(titleText);
  sheet.getRange(row, 1, 1, lastCol).merge()
    .setFontFamily('Arial').setFontSize(14).setFontColor('#FFFFFF')
    .setBackground('#10B981').setFontWeight('bold')
    .setVerticalAlignment('middle').setHorizontalAlignment('left');
  sheet.setRowHeight(row, 34);
}
```

Title text format: `'SellerSheet • <SheetName>'` (use the bullet `•` U+2022 between brand and sheet name). Keep it short — this row should not need to wrap. Left-aligned, not centered — the title is a brand label, not a heading; centering merged banners makes the text float in dead space when the sheet is wide. Both rows 1 and 2 count toward `setFrozenRows` (the hidden row still occupies a logical slot in the frozen pane).

```javascript
// helper used in setupVendorSheet
function styleKeyHeaderRow(sheet, row, lastCol) {
  sheet.getRange(row, 1, 1, lastCol)
    .setFontFamily('Arial').setFontSize(7).setFontColor('#A8AEB8')
    .setBackground('#FFFFFF').setFontWeight('normal').setVerticalAlignment('middle');
  sheet.setRowHeight(row, 14);
}
```

### Row 3 — emerald display row (3-row sheet) OR filter-label band (5-row sheet)

In a **3-row sheet**, row 3 is the display header — emerald background with white bold Arial 10pt text. This is "the row humans look at." Example: `Vendor PO Items` row 3 = `Image | Image URL | Store | Vendor Code | PO State | PO Number | Seq # | ASIN | Vendor SKU | Ordered Qty | Back Order OK | Ack Code ✏️ | ...`

In a **5-row sheet**, row 3 is the **filter-label band** — same emerald styling but only spans **columns A–L** (12 cells). Cols M+ get white-background padding so the emerald band stops cleanly mid-row. The narrowing band signals "filters are here; the data viewport extends wider."

```javascript
function styleEmeraldRow(sheet, row, lastCol) {
  sheet.getRange(row, 1, 1, lastCol)
    .setFontFamily('Arial').setFontSize(10).setFontColor('#FFFFFF')
    .setBackground('#10B981').setFontWeight('bold')
    .setVerticalAlignment('middle').setHorizontalAlignment('left');
  sheet.setRowHeight(row, 28);
}

// On a 5-row sheet, emerald only spans A-L on the filter-label row:
styleEmeraldRow(ordersSheet, 3, 12);
// Right-pad cols M+ with white so the band stops cleanly:
ordersSheet.getRange(3, 13, 1, lastCol - 12).setBackground('#FFFFFF');
```

### Row 4 — filter input band (5-row only)

Light gray-blue background `[0.929, 0.945, 0.961]` (`#EDF1F5`), italic, Arial 10pt. Cells in A4:L4 are where the operator types filter values. Cols M+ stay white (continuation of the row-3 band-stop).

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

### Row 5 — navy display headers (5-row only)

Full-width navy `[0.157, 0.2, 0.318]` (`#28334F`) band, Arial 10pt bold white text. Same style as row 3 of a 3-row sheet but in navy because this surface is read-mode, not action-mode.

This is also the row where Sheets' **basic filter** dropdown arrows appear (see next section). On a 5-row sheet they sit on row 5; on a 3-row sheet they sit on row 3 (the emerald display row).

```javascript
function styleNavyHeaderRow(sheet, row, lastCol) {
  sheet.getRange(row, 1, 1, lastCol)
    .setFontFamily('Arial').setFontSize(10).setFontColor('#FFFFFF')
    .setBackground('#28334F').setFontWeight('bold')
    .setVerticalAlignment('middle').setHorizontalAlignment('left');
  sheet.setRowHeight(row, 26);
}
```

All header rows (title, emerald label, navy display) are **left-aligned**. Matches data-cell default behavior (text left, numbers right), keeps header text anchored to col A so the operator's eye lands in the same place per row. Center-aligning header rows on wide sheets makes labels float in dead space; merged emerald banners look especially awkward centered on a 20-col sheet.

## Basic filter on the display-header row

Apply Sheets' built-in basic filter on the **display-header row** of any list/action sheet so operators get click-to-filter dropdown arrows on every column without typing into the dedicated filter-input row. The filter dropdowns are native, support multi-select, search, and sort.

```javascript
function setBasicFilter(sheet, displayHeaderRow, lastCol) {
  const existing = sheet.getFilter();
  if (existing) existing.remove();   // idempotent re-setup
  const lastRow = sheet.getMaxRows();
  if (lastRow < displayHeaderRow) return;
  sheet.getRange(displayHeaderRow, 1, lastRow - displayHeaderRow + 1, lastCol)
    .createFilter();
}

// 5-row sheet (Vendor Orders, Vendor PO Status) — anchor on row 5
setBasicFilter(ordersSheet, 5, 17);

// 3-row sheet (Vendor PO Items) — anchor on row 3
setBasicFilter(itemsSheet, 3, 24);
```

### When to apply, when to skip

Most action/browse sheets benefit. A few don't.

| Apply when | Skip when |
|---|---|
| Operator scans 50+ rows and needs ad-hoc narrowing | Sheet has fewer than ~10 rows |
| Multiple status columns exist (Confirm Status, Receive Status, etc.) | Append-only audit log where rows are reviewed chronologically |
| Same dataset gets queried with different filter combinations | Sheet is a single fixed-shape report (KPI tile) |

Examples from the vendor workbook:
- `Vendor Orders` — YES (filter by PO State, Selling Party, etc.)
- `Vendor PO Items` — YES (filter by Ack Code, by PO Number while acknowledging)
- `Vendor PO Status` — YES (filter by Confirm/Receive Status across line items)
- `Vendor Log` — NO (append-only audit; operator scans chronologically, rarely filters)

### Coexistence with the dedicated filter-input row (row 4)

5-row sheets have a dedicated filter-input row at row 4 that drives the next *API call's* filter (it's read by GAS, sent as a query param to Amazon). The row-5 basic filter is purely client-side — it narrows what's already in the sheet without re-fetching.

Operator mental model:
- **Row 4 filter inputs** → "narrow what I'm pulling FROM Amazon next time I click sync"
- **Row 5 basic filter dropdowns** → "narrow what I'm looking at RIGHT NOW in the sheet"

Both can be set at once. Row 4 narrows the pull, then row 5 narrows the view further within what was pulled.

## Emerald vs navy — the action-vs-read rule

This is the single most useful design rule in the whole pattern:

- **Emerald `#10B981`** marks the row the operator EDITS/ACTS on. Display headers of an action sheet (3-row layout), filter-label rows on a browse sheet (5-row). Also the title banner on row 2 of every sheet.
- **Navy `#28334F`** marks the row the operator READS. Display headers of a list/browse sheet (5-row layout).

Same workbook can have both. The vendor workbook:
- `Vendor PO Items` (action) — row 2 emerald title, row 3 emerald display
- `Vendor Log` (audit, read-mode) — row 2 emerald title, row 3 navy display
- `Vendor Orders` (browse) — row 2 emerald title, row 3 emerald (filter labels), row 5 navy (display)
- `Vendor PO Status` (browse) — same shape as Vendor Orders

If you find yourself wanting "two emerald rows below the title" on a 5-row sheet (one for filter labels, one for display), stop — you're conflating action and read. The display row must be navy if the operator is browsing, not editing. (The title banner doesn't count — it's a brand surface, not a workflow row.)

## The IMAGE arrayformula slot

If the sheet has product thumbnails, column A holds an IMAGE arrayformula. Code NEVER writes to column A; writes always start at column B.

| Layout | A formula cell | Data range |
|---|---|---|
| 3-row sheet | `A3` | `B4:B` |
| 5-row sheet | `A5` | `B6:B` |

```javascript
// 3-row sheet (Vendor PO Items)
itemsSheet.getRange('A3').setFormula(
  '={"Image"; arrayformula(if(isblank(B4:B),"",IMAGE(B4:B)))}'
);

// 5-row sheet (Vendor PO Status)
statusSheet.getRange('A5').setFormula(
  '={"Image"; arrayformula(if(isblank(B6:B),"",IMAGE(B6:B)))}'
);
```

The literal string `"Image"` is the first element of the array, so the formula cell displays "Image" (the column label) while spilling thumbnails below. Both A3 and A5 inherit the same brand styling as their respective display-header rows — the cell stays emerald or navy with bold white text, and the IMAGE spill below renders against the white data background.

When you write data rows, pass `startCol=2` to `_upsertRows` (or whatever your write helper is) so col A is never touched.

**Do not set a custom row height on image data rows.** Let Sheets keep its default (~21 px). The IMAGE thumbnail is a preview to confirm "is this the right ASIN", not a detail viewer — operators don't zoom in on a 70px-tall preview, they click out to the catalog or the Amazon page if they need details. Taller rows just push other line items off-screen and slow scrolling. If you need a bigger preview, expose it on a per-row hover or a side panel, not by globally inflating every row.

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
add_sheet_dropdown(spreadsheet_id, "Vendor Orders!F4",
  ["New", "Acknowledged", "Closed"], strict=false)
```

### Where dropdowns go

| Sheet | Cell | Values |
|---|---|---|
| **Filter rows** (5-row sheets, row 4) | A4:L4 cells matching an enum filter | Amazon enum values |
| **Action columns** (3-row sheets, data rows 4+) | Open range e.g. `L4:L500` | Amazon enum values |
| **Sort order** | Any sheet, last filter col | `["ASC", "DESC"]` (default `'DESC'`) |
| **Boolean filters** | Filter cell | `["true", "false"]` (lowercase — Amazon API casing) |

For data-row dropdowns (action sheets), use a bounded range like `'L4:L500'` rather than `'L4:L'` — Sheets accepts open ranges but Apps Script perf degrades on huge ranges.

### Common Amazon SP-API enum dropdowns

Reusable list — match the API spec exactly (case-sensitive). Anchor cells are the live vendor workbook coordinates (post-title-row).

| Domain | Cell context | Values |
|---|---|---|
| Vendor PO state (filter) | `Vendor Orders!F4` | `New / Acknowledged / Closed` |
| Vendor PO state (data) | `Vendor PO Items!E:E` | `New / Acknowledged / Closed` |
| PO Item state | `Vendor Orders!I4` | `Cancelled` |
| Is PO Changed | `Vendor Orders!H4` | `true / false` |
| PO status (filter) | `Vendor PO Status!G4` | `OPEN / CLOSED` |
| Confirmation status | `Vendor PO Status!H4`, `Vendor PO Status!O:O` | `ACCEPTED / PARTIALLY_ACCEPTED / REJECTED / UNCONFIRMED` |
| Receive status | `Vendor PO Status!I4`, `Vendor PO Status!R:R` | `NOT_RECEIVED / PARTIALLY_RECEIVED / RECEIVED` |
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

Apply via `add_sheet_conditional_format` or `setStatusChipRules` (GAS). Use **open ranges** like `C6:C` so new rows inherit. One rule per value.

| Domain | Range | Rule |
|---|---|---|
| PO state | `Vendor Orders!C6:C`, `Vendor PO Items!E4:E` | Acknowledged=GREEN, New=AMBER, Closed=RED |
| PO status | `Vendor PO Status!F6:F` | OPEN=AMBER (action pending), CLOSED=GREEN |
| Confirmation status | `Vendor PO Status!O6:O` | ACCEPTED=GREEN, PARTIALLY_ACCEPTED=AMBER, UNCONFIRMED=AMBER, REJECTED=RED |
| Receive status | `Vendor PO Status!R6:R` | RECEIVED=GREEN, PARTIALLY_RECEIVED=AMBER, NOT_RECEIVED=RED |

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
- For values: `write_sheet` overwrites cleanly. Don't trust `getLastRow()` if you have arrayformulas in col A — they make `getLastRow()` return spurious values. Use a helper that scans a specific data column from a known data-start row instead:
  ```javascript
  // dataStartRow is required — encodes the sheet's header anatomy (4 for 3-row, 6 for 5-row)
  function _lastRowOfColumn(sheet, colNum, dataStartRow) {
    const maxRow = sheet.getMaxRows();
    if (maxRow < dataStartRow) return dataStartRow - 1;
    const values = sheet.getRange(dataStartRow, colNum, maxRow - dataStartRow + 1).getValues();
    for (let i = values.length - 1; i >= 0; i--) {
      if (values[i][0] !== '' && values[i][0] != null) return i + dataStartRow;
    }
    return dataStartRow - 1;
  }
  ```

## Quick reference — the 11 rules

When building an action sheet, this is the checklist:

1. **Row 1 = HIDDEN code-contract row**: lowerCamelCase keys, Arial 7pt gray. Hidden via `sheet.hideRows(1)`. Code reads these via `getColumnMapping(headers)`.
2. **Row 2 = emerald title banner** merged across full width: `"SellerSheet • <SheetName>"`, Arial 14pt bold white on `#10B981`. First row the operator sees on every visible tab.
3. **Decide shape**: 3-row (action surface) or 5-row (filter + browse). Frozen rows match — including the hidden row 1.
4. **Emerald = where operator acts; Navy = where operator reads.** Never both on same workflow row. Title row is brand-only and doesn't count toward this rule.
5. **Filter rows narrow to A-L**: emerald band stops at col 12, cols M+ white-padded.
6. **Image col A = arrayformula at A3 (3-row) or A5 (5-row)**. Writes always start col B.
7. **Amazon enum cells get dropdowns** in warning mode (`strict: false`). Filter inputs live at row 4 on 5-row sheets.
8. **Apply Sheets' basic filter on the display-header row** so operators get click-to-filter dropdown arrows on every column. Skip on append-only audit logs.
9. **Status chips use soft pastels** (`#C6EFCE / #FFF2CC / #FFC7CE`) on long columns, bold brand on KPIs. Apply to open ranges anchored at data start (e.g. `C6:C` on 5-row, `E4:E` on 3-row).
10. **Editable data columns get `✏️`** in display header. Sparingly.
11. **Reads use `getColumnMapping(headers)`**, fallbacks match current layout, reorder remaps existing data. Pass an explicit `dataStartRow` (4 for 3-row, 6 for 5-row) to any helper that scans data.

## See also

- `reference/brand-standards.md` — palette + font + number formats
- `reference/conditional-formatting.md` — chip + gradient mechanics
- `reference/growable-tables.md` — read-mode/list pattern (the complement to this file)
- `reference/image-pattern.md` — column-A arrayformula deep-dive
- `reference/mcp-gotchas.md` — `getLastRow()` + arrayformula gotcha
