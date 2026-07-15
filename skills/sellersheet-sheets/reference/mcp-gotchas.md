# MCP gotchas — quirks from live builds

These are SellerSheet MCP behaviors that bite during builds. Avoid by following the rules.

## `&` in tab names — don't use it

`read_sheet` returns HTTP 400 when the tab name contains `&` (Sheets API URL-encoding bug in the route). `list_sheet_tabs` HTML-encodes the `&` as `&amp;` in the response, but `rename_sheet_tab` accepts the encoded form, so the round-trip is inconsistent.

**Use `and` instead of `&`** — `"Profit and Cash"`, `"Inventory and Restock"`. Visual cost is negligible; debugging cost of the 400 is high.

## `write_sheet` parses leading `=` as formula

`write_sheet` uses `valueInputOption=USER_ENTERED`. Strings starting with `=` are parsed as live formulas. Verified empirically — batch-writing 84 `=SPARKLINE(...)` formulas in a single `write_sheet` call rendered all as live, not literal.

**Implication:** for column-wide formula writes (N rows of `=IFERROR(IMAGE(...))`, `=SPARKLINE(...)`, `=VLOOKUP(...)`), use a single `write_sheet` call with a 2D array of formula strings — far cheaper than N separate `write_sheet_formula` calls.

`write_sheet_formula` is appropriate when you want explicit per-cell intent or single-cell update. Both write formulas; equivalent in semantics, different in batching cost.

## Literal text starting with `=` MUST be apostrophe-escaped

The flip side of USER_ENTERED, and a recurring real-world bug: **any string cell that
begins with `=` (or `+`) is parsed as a live formula**, even when you obviously meant
prose. Prefix with an apostrophe — it doesn't render; it tells Sheets "literal text":

| You meant (documentation text) | What Sheets does unescaped | Write instead |
|---|---|---|
| `= ordered − refunded` (a Notes cell) | `#ERROR!` (parse failure) | `'= ordered − refunded` |
| `= date` (a source-mapping cell) | `#NAME?` (unknown range `date`) | `'= date` |
| `= amount − promo + tax` | `#ERROR!` | `'= amount − promo + tax` |
| `=SUM(A:A) — used on B12` | live `=SUM` + trailing garbage | `'=SUM(A:A) — used on B12` |

Where it bites (verified live, 2026-07-08 schema-review build — 6 cells across 2 tabs):
**Notes / derivation / source-mapping columns** in schema docs, data dictionaries, and
formula documentation — any table ABOUT formulas. The habit: after composing a
`write_sheet` values array, sweep it for cells whose string starts with `=` or `+` and
prefix those with `'`. One sweep costs seconds; the read-back-diagnose-repair loop costs
many calls.

**Repair trap:** when the read-back reveals these errors mid-table, do NOT patch
individual cells by their table row numbers — table row *N* sits at sheet row *N + header
offset*, and off-by-offset patches overwrite healthy neighbors (also verified live).
Rewrite the whole affected column range in one `write_sheet` with correctly escaped
values.

**Related quirk:** the apostrophe escape consumes only ONE leading char. A cell that
should *display* a leading quote (`'fee' or 'ad'`) needs a double apostrophe:
`"''fee' or 'ad'"`.

## USER_ENTERED coerces identifier strings into numbers and dates

The other face of USER_ENTERED: every value lands as if a human typed it into the cell,
so Sheets applies its full auto-parse — and Amazon identifiers are full of strings that
parse as something else:

| Identifier written as string | What Sheets stores | Damage |
|---|---|---|
| UPC `"0012345678905"` | number `12345678905` | leading zeros gone — barcode invalid |
| 16+ digit numeric (FNSKU-adjacent, GTIN-14 padded) | float | precision lost past 15 digits |
| SKU `"10-1"`, `"2024-01"`, `"MAY-25"` | a **date** | joins/VLOOKUPs silently miss |
| SKU `"5E10"` | scientific notation `50000000000` | same |
| `"TRUE"` / `"FALSE"` labels | boolean | string comparisons fail |

Order IDs (`123-4567890-1234567`) and ASINs starting with `B0…` happen to survive, which
is why this trap stays invisible until a UPC or date-shaped SKU shows up.

**Rules:**
- One-shot writes: apostrophe-prefix each identifier cell (`"'0012345678905"`) — same
  sweep as the leading-`=` escape above; do both in one pass.
- Growable `_raw_*` identifier columns (SKU, UPC/EAN, postal code): set the column's
  number format to text (`set_sheet_number_format` pattern `@`) **before** the first
  write — appended rows then stay text without per-cell apostrophes.
- After writing, spot-read one known-risky cell (a leading-zero UPC or hyphenated SKU)
  and confirm the value round-trips unchanged.

`SQL()` joins compare literal cell contents — a date-ified SKU in `_raw_catalog` fails to
join against the text SKU in the report tab with **no error cell anywhere**. If a JOIN
drops rows unpredictably, check identifier typing before suspecting the JOIN syntax.

## `format_sheet_range` over a merged cell can clear content

Applying `format_sheet_range` to a merged region sometimes clears the underlying text. Order of operations matters:

**Always `write_sheet` first, then `merge_sheet_cells`, then `format_sheet_range`.**

If reformatting an already-merged region with new text:
1. `unmerge_sheet_cells` first
2. `write_sheet` the new content
3. `merge_sheet_cells` again
4. `format_sheet_range` for visual styling

## Stale merged cells silently eat `SQL()` spills

A merged range that overlaps where a `SQL()` spill wants to land will silently truncate or fail the spill. Symptom: the header row of the SQL output shows only the first column (the rest of the row is "inside" a leftover merge from a previous layout), or no spill renders at all.

The formula reads correctly in FORMULA mode and shows `#NAME?` in server-side reads — the merge problem only manifests after the browser evaluates `SQL()`.

**When migrating a layout** (changing column count, repositioning section bands, re-running a tab), **unmerge the entire affected area before rewriting**. `unmerge_sheet_cells` on a generous range like `Tab!A1:Z30` is cheap insurance. Re-merge banner rows AFTER the new spill anchors are placed.

This is the real cause of many "JOIN didn't work" reports in early iterations — the JOIN syntax is fine; a leftover merge from a previous layout is eating the spilled header.

## Numeric `_raw_*` columns must be NULL (blank), never empty-string

`SQL()` evaluates `WHERE woc_t30 > 4` against the literal contents of a Sheets cell. If the cell holds `""` (empty string) instead of being blank, the comparison silently fails — the row is included or excluded unpredictably. Same for `ORDER BY`: text-zero `"0"` sorts after numeric `100`.

Rule: when writing a numeric value to a `_raw_*` cell:
- Real number → write the number directly (`3.14`, `0`, `100`).
- Missing / N/A → write **blank** (omit the value, or write `None` in Python which becomes blank in Sheets), NOT `""`.

When the MCP returns a value that's `None`/`null`, double-check your write path doesn't coerce to empty string. If unsure, write a `0` or skip the cell. Never `""` for a numeric column.

## "Truly blank" cells after a `null` write

`write_sheet` with `None`/`null` may leave `""` in the cell rather than a fully blank state. There's no clean API to guarantee 100% empty after a previous write.

For `_raw_*` numeric columns where blankness matters: `clear_sheet_range` first, then write only the populated rows.

## Chunked write recipe for large `query_report_data` payloads

`query_report_data` results that exceed the tool's max-return-token cap (~100KB+ JSON) trigger a tool error before you see the rows. Retrying the same call doesn't help — the rows aren't the problem, the response size is. Recovery:

1. **Re-run with smaller `limit` + explicit `offset`** to paginate (`limit=200, offset=0`, then `offset=200`, etc.), OR
2. **Drop long text columns** from the projection (`item_name`, descriptions) if not strictly needed.

Symptom: the query reports an error or empty payload, and the row count you wrote to the sheet is suspiciously small. Always check `total_count` in the MCP response against what you actually wrote.

Typical culprit: a catalog query with `item_name` included for thousands of SKUs. Project columns more narrowly.

## Deprecation marker for dropped columns

When you remove a column from a `_raw_*` schema in-place (without shifting other columns left to avoid breaking downstream formulas), rename the header from e.g. `image_url` → `_image_url_deprecated` and clear the data rows in that column.

Two benefits:
- Greppable marker so future cleanups know the column is dead.
- Doesn't shift column positions, so consumer formulas referencing later columns by letter still work.

Drop the column entirely only when you're sure no consumer formula references columns to its right by position.

## Conditional formatting tool variation

Some MCP versions error on `condition_type="TEXT_STARTS_WITH"` or `"TEXT_CONTAINS"`. Fall back to `CUSTOM_FORMULA` which is universally supported:

```javascript
// ❌ may error on some MCP builds
condition_type="TEXT_STARTS_WITH", value="GREEN"

// ✅ universal
condition_type="CUSTOM_FORMULA", value='=LEFT($I2,5)="GREEN"'
```

See `reference/conditional-formatting.md` for full examples.

## Rate limits — use `sheet_batch_update` for all multi-step formatting

SellerSheet MCP enforces a **burst limit on individual tool calls**: on the Business plan this is 3 requests per burst window. Sending 3 `format_sheet_range` calls in the same message will reliably hit it — the third call returns 429 and you lose the operation.

**The fix is always `sheet_batch_update`**, not spreading calls across messages.

`sheet_batch_update` sends all operations as a single HTTP request to the Sheets API — it bypasses the per-tool burst limit entirely. 43 `repeatCell` requests in one `sheet_batch_update` call = 1 MCP tool call, well inside any rate limit.

**Use `sheet_batch_update` whenever you have 3+ format operations** — not just "structural ops". This includes:

- Applying section band colors across a multi-section tab
- Applying `numberFormat` to multiple columns after SQL() anchors (see `reference/sql-function.md`)
- Resetting stale formatting from previous layouts
- Applying any combination of background, font, border, and numberFormat in one pass

```python
# ✅ One call — applies all 8 format ops atomically, no rate limit risk
sheet_batch_update(spreadsheet_id, [
    {"repeatCell": {...}},   # section band emerald
    {"repeatCell": {...}},   # SQL header navy
    {"repeatCell": {...}},   # number format: currency
    {"repeatCell": {...}},   # number format: percent
    {"repeatCell": {...}},   # number format: roas
    {"repeatCell": {...}},   # reset stale emerald from old layout
    {"repeatCell": {...}},   # overflow footer soft yellow
    {"repeatCell": {...}},   # metadata row gray
])

# ❌ 8 calls — guaranteed 429 on the 4th
format_sheet_range(...)   # hit 1
format_sheet_range(...)   # hit 2
format_sheet_range(...)   # hit 3
format_sheet_range(...)   # 429 — lost
```

**`format_sheet_range` is fine for single one-off ops** during exploration. Switch to `sheet_batch_update` the moment you're doing a build pass with multiple formatting steps.

**Batch into one tool call when possible**:
- Write a 500-row block in a single `write_sheet`, not 500 calls.
- Apply `format_sheet_range` over a whole header band, not per-column.
- Use `sheet_batch_update` for 3+ format/structural ops in one HTTP round-trip.

## See also

- `reference/sql-function.md` — bracket-quote rule + LIMIT defaults
- `reference/error-semantics.md` — how to diagnose what bit you
- `reference/formula-conventions.md` — NULL-vs-empty-string for numeric columns
