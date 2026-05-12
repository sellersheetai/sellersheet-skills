# Server-side error semantics

The SellerSheet MCP reads via Google's API, which can't evaluate browser-side custom functions like `SQL()` and `IMAGE()`. This means **the same cell can show different states server-side vs browser-side**, and you need to distinguish what each error actually means.

## Error class table

| Error | What it means | Pending state OR real bug? | What to do |
|---|---|---|---|
| **`#NAME?`** | `SQL()` or `IMAGE()` is undefined here. Add-on hasn't loaded (server-side, or first browser open before add-on enabled). | **Pending state — expected.** Will render once add-on activates. | Wait for browser open; click Extensions → SellerSheet → Open if needed. |
| **`#REF!`** | Real spill collision or invalid cell ref. Read `effective_value.error.message` to confirm — usually `"Array result was not expanded because it would overwrite data in <cell>"`. | **Real bug — must fix.** | Move the colliding content, shrink the spill (add `LIMIT N`), or both. |
| **`#ERROR!`** | Formula syntax broken, OR `SQL()` reading a range that touches `NOW()` / `RAND()` / `RANDARRAY()` / `RANDBETWEEN()`. Read `effective_value.error.message` for the specific reason. | **Real bug — must fix.** | Often `"function not allowed to reference a cell with NOW()"` — replace `SQL(<range with NOW())>` with per-column `ARRAYFORMULA`. |
| **`#VALUE!`** | Type mismatch — e.g., FX VLOOKUP failing because the lookup key is in the wrong cell, or a formula expecting a number got a string. | **Real bug — must fix.** | Almost always a schema drift between formula and source. |
| **`#DIV/0!`** | Division by zero — usually a margin calc against an empty selling-price cell, or a ratio with empty units. | **Tolerable.** | Wrap with `IFERROR(..., "")` or `IF(denom=0, "—", numerator/denom)` so the tab renders gracefully when inputs are empty. |
| **`#N/A`** | VLOOKUP/MATCH didn't find the key. | **Probably real bug.** | Check that the lookup key matches the source data exactly (case, whitespace, dashes). Wrap in `IFERROR(..., "")` if absence is legitimate. |
| **`#NAME?`** on a non-`SQL()` / non-`IMAGE()` formula | Typo in function name or referenced range doesn't exist. | **Real bug — must fix.** | Check the formula text; verify named ranges. |

## Diagnosing `#REF!` on a SQL spill cell

When the spill anchor (e.g., `Inventory!B14`) shows `#REF!`:

1. **`get_sheet_cell(spreadsheet_id, range_=<that cell>)`** → read `effective_value.error.message`.
2. If the message is `"Array result was not expanded because it would overwrite data in <cell>"` — that's a **spill collision**. Look up what's at `<cell>`. Almost always:
   - A section anchored too close to the spill (e.g., AGENT INSIGHTS at row 60 when the spill needs row 200+).
   - Leftover content from a previous layout.
   - A merged cell range overlapping the spill row.
3. **Fix**:
   - Clear the colliding content, OR
   - Add `LIMIT N` to the SQL (see `reference/sql-function.md`), OR
   - Move the offending section further down the tab.

## Diagnosing `#ERROR!` on a SQL cell

When a cell with `=SQL(...)` shows `#ERROR!`:

1. **`get_sheet_cell`** → read `effective_value.error.message`.
2. **`"This function is not allowed to reference a cell with NOW(), RAND(), RANDARRAY(), or RANDBETWEEN()"`** — your SQL range includes a cell with a volatile function. Common cause: reading `_status` (which has `NOW()` in the status formula). Replace `SQL()` with per-column `ARRAYFORMULA`.
3. **`"SyntaxError: ... got 'STORE'"`** or similar — alasql parser hit a reserved word. Bracket-quote every column name and alias. See `reference/sql-function.md`.
4. **Other parser errors** — usually a typo or missing comma in the SELECT list.

## Diagnosing `#NAME?` on a non-SQL/non-IMAGE cell

If you see `#NAME?` on a cell whose formula is `=ARRAYFORMULA(...)`, `=FILTER(...)`, `=TEXTJOIN(...)`, etc., **that's a real bug**:

- Typo in function name (`=ARRAYFROMULA` instead of `=ARRAYFORMULA`).
- Referenced range that doesn't exist (`=SUM(InvenTory!A:A)` when the tab is `Inventory`).
- Named range that hasn't been defined yet.

Don't dismiss it as "pending state."

## The Golden Rule

> **Never accept `#REF!`, `#ERROR!`, or `#VALUE!` as "the add-on will fix it on open."** Those are real bugs. Only `#NAME?` on cells whose formula begins with `=SQL(` or `=IMAGE(` is the documented pending state.

Common builder mistake: claiming `#REF!` is pending because "alasql isn't loaded yet." It isn't. `#REF!` is always a real bug. The fix may be simple (move a section down 250 rows) but the diagnosis is non-negotiable.

## How to verify a fresh sheet

Scan every visible tab for the four error classes:

```
read_sheet on tab → look at the JSON for any "#REF!", "#ERROR!", "#VALUE!", "#N/A"
```

If found, `get_sheet_cell` on that specific cell to read `effective_value.error.message`. Triage by the table above. **`#NAME?` on `=SQL(` cells is the only acceptable pending state for a server-side read.**

See `scripts/verify-after-write.md` for the full read-back routine.

## `#NAME?` triage cheatsheet

| Cell formula starts with | `#NAME?` means | Action |
|---|---|---|
| `=SQL(...)` | alasql not loaded server-side | Pending — expected. Open in browser. |
| `=IMAGE(...)` | image fetch pending external-resource consent | Pending — expected. Allow Access in browser. |
| `=ARRAYFORMULA(...)` | typo in function name OR referenced range doesn't exist | Real bug — fix the formula |
| `=FILTER(...)` | typo or undefined named range | Real bug — fix |
| `=VLOOKUP(...)` | typo in function or undefined named range | Real bug — fix |
| anything else | function name or named range is wrong | Real bug — fix |

## See also

- `reference/sql-function.md` — bracket-quote rule (prevents `#ERROR!` on alasql parse errors)
- `reference/mcp-gotchas.md` — NULL vs empty-string (prevents `#VALUE!` on WHERE filters)
- `scripts/verify-after-write.md` — the full read-back routine
