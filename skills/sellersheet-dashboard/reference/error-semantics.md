# Server-side error semantics

The dashboard relies on the SellerSheet GAS add-on for browser-side `SQL()` evaluation. Server-side reads (via `read_sheet`, `get_sheet_cell`, the Sheets API) cannot evaluate `SQL()` — alasql isn't defined in the API context. This means **the same cell can show different states server-side vs browser-side**, and you need to distinguish what each error actually means.

## Error class table

| Error | What it means | Pending state OR real bug? | What to do |
|---|---|---|---|
| **`#NAME?`** | `SQL()` is undefined here. Add-on hasn't loaded (server-side, or first browser open before add-on enabled). | **Pending state — expected.** Will render once add-on activates. | Wait for browser open; click Extensions → SellerSheet → Open if needed. |
| **`#REF!`** | Real spill collision or invalid cell ref. Read `effective_value.error.message` to confirm — usually `"Array result was not expanded because it would overwrite data in <cell>"`. | **Real bug — must fix.** | Move the colliding section, shrink the spill (add `LIMIT 200`), or both. See `reference/agent-insights.md` overflow-guard rule. |
| **`#ERROR!`** | Formula syntax broken, OR `SQL()` reading a range that touches `NOW()` / `RAND()` / `RANDARRAY()` / `RANDBETWEEN()`. Read `effective_value.error.message` for the specific reason. | **Real bug — must fix.** | Often "function not allowed to reference a cell with NOW()" — replace `SQL(_status!A1:L)` with per-column `ARRAYFORMULA`. See `reference/freshness-system.md`. |
| **`#VALUE!`** | Type mismatch — e.g., FX VLOOKUP failing because the lookup key is in the wrong cell, or a formula expecting a number got a string. | **Real bug — must fix.** | Almost always a schema drift between formula and source. Check column labels in `_raw_cogs` against the Profit and Cash SQL — see `reference/cogs-schema.md` "Common breakages". |
| **`#DIV/0!`** | Division by zero — usually a margin calc against an empty selling-price cell, or a ratio with empty units. | **Real bug — but tolerable.** | Wrap in `IFERROR(..., "")` or `IF(denom=0, "—", numerator/denom)` so the tab renders gracefully when COGS aren't yet entered. |
| **`#N/A`** | VLOOKUP/MATCH didn't find the key. | **Probably real bug.** | Check that the lookup key matches the source data exactly (case, whitespace, dashes). |

## Diagnosing `#REF!` on a SQL spill cell

When `Inventory and Restock!B14` (or wherever a SQL spill is anchored) shows `#REF!`:

1. **`get_sheet_cell(spreadsheet_id, range=<that cell>)`** → read `effective_value.error.message`.
2. If the message is `"Array result was not expanded because it would overwrite data in <cell>"` — that's a **spill collision**. Look up what's at `<cell>`. It's almost always:
   - AGENT INSIGHTS section anchored too close to the spill (row 60 / 150 when spill needs row 200+).
   - A leftover footer or stale content from a previous layout.
   - A merged cell range overlapping the spill row.
3. **Fix:** clear the colliding content OR add `LIMIT 200` to the SQL OR move the AGENT INSIGHTS anchor to row 400.

## Diagnosing `#ERROR!` on a SQL cell

When `README!A15` (or any cell with `=SQL(...)`) shows `#ERROR!`:

1. **`get_sheet_cell`** → read `effective_value.error.message`.
2. **`"This function is not allowed to reference a cell with NOW(), RAND(), RANDARRAY(), or RANDBETWEEN()"`** — your SQL range includes `_status!I` (which contains `NOW()` in the status formula). Replace with per-column `ARRAYFORMULA`. See `reference/freshness-system.md`.
3. **`"SyntaxError: ... got 'STORE'"`** or similar — alasql parser hit a reserved word (`store`, `status`, `date`, `index`, `order`, `decision`, `currency`...). Bracket-quote every column name and alias. See `reference/image-catalog.md`.
4. **Other:** look at the alasql docs.

## The Golden Rule

> **Never accept `#REF!` or `#ERROR!` as "the add-on will fix it on open."** Those are real bugs. Only `#NAME?` on cells whose formula begins with `=SQL(` or `=IMAGE(` is the documented pending state.

Common builder mistake: claiming `#REF!` is pending because "alasql isn't loaded yet." It isn't. `#REF!` is always a real bug. The fix may be simple (move AGENT INSIGHTS down 250 rows) but the diagnosis is non-negotiable: `effective_value.error.message` will say `"Array result was not expanded ..."` for a spill collision, never anything related to alasql.

## Sentinel: `#NAME?` on a formula that ISN'T `=SQL(` or `=IMAGE(`

If you see `#NAME?` on a cell whose formula is, say, `=ARRAYFORMULA(...)` or `=FILTER(...)` or `=TEXTJOIN(...)`, that's a **real bug** — usually a typo in a function name or a referenced range that doesn't exist. Don't dismiss it as "pending state."

## How to verify a fresh dashboard

Before declaring a build done, scan every visible tab for the four error classes:

```
read_sheet on tab → look at the JSON for any "#REF!", "#ERROR!", "#VALUE!", "#N/A"
```

If found, `get_sheet_cell` on that specific cell to read `effective_value.error.message`. Triage by the table above. **`#NAME?` on `=SQL(` cells is the only acceptable pending state for a server-side read.**

See `scripts/post-build-checklist.md` for the full verification routine.

## See also

- `reference/freshness-system.md` — the SQL/NOW() compatibility issue that produces `#ERROR!` on README
- `reference/agent-insights.md` — the AGENT INSIGHTS row-anchor rule that prevents `#REF!`
- `reference/cogs-schema.md` — the column-label drift that produces `#VALUE!` on Profit and Cash
- `scripts/post-build-checklist.md` — the full verification routine
