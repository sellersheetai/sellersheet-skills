# Local build → one-shot import (heavy net-new builds)

The Codex-spreadsheets-style pipeline: author the whole workbook **locally** as `.xlsx`
(openpyxl), then land it in Drive as a **native Google Sheet with a single upload** —
instead of dozens of MCP write/format round-trips that fight burst limits.

## When to use (and when not)

Use for **net-new workbooks or heavy multi-tab builds** — roughly anything that would
take more than ~15 MCP write/format calls (multiple tabs, formula bands, conditional
formats, charts).

Requirements: a local shell + Python + `openpyxl` (`pip install openpyxl`). **Hosted
agents without a filesystem (claude.ai web, ChatGPT connectors) can't run this — use the
standard MCP Build workflow instead.** Also skip it for small edits and single-tab
additions to a live workbook: the MCP path is simpler and preserves in-place conventions.

## Pipeline

1. **Get the data** — `query_report_data` etc. as usual.
2. **Build the `.xlsx` locally** with openpyxl: every tab (hidden `_raw_*` included),
   formulas, number formats, conditional formats, charts, notes, frozen panes, dropdowns.
   Render-verify locally if you can before uploading.
3. **Upload + convert in one call** — `start_drive_upload` with
   `convertTo="application/vnd.google-apps.spreadsheet"` (source `mimeType` = the xlsx
   MIME `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`). It returns
   a resumable session; **the PUT's `Content-Type` must equal the declared source
   mimeType or Google 400s.** (`copy_drive_file` also accepts `convertTo` for
   copy-and-convert.)
4. **Net-new workbook** → done: the upload IS the deliverable.
   **Into an existing workbook** → `copy_sheet_tab` each tab cross-workbook **in
   dependency order (`_raw_*` first** so name-bound references land), then delete the
   scratch workbook.
5. **Verify server-side** — the Final review gate in SKILL.md applies unchanged.

## Verified fidelity (xlsx → native Sheet, and copy_sheet_tab)

These survive conversion intact: `=SQL()` **verbatim as a formula** (no `_xludf.`
prefix; evaluates once the sidebar opens — same pending contract as MCP-written),
`=SPARKLINE()` / `=IMAGE()`, standard formulas (evaluate immediately), CellIs +
ColorScale conditional formats (imported AND applied), `@` text format (leading-zero
UPCs, date-shaped SKUs), cell notes (incl. CJK), frozen rows, exact fill colors,
openpyxl `LineChart` (arrives as a native Sheets chart with ranges + anchor mapped),
hidden `sheet_state`, data-validation dropdowns.

## Gotchas (each one cost a debugging round — don't relearn them)

1. **Fonts/widths**: cells without an explicit font import as Calibri 11. Set
   Arial 10 explicitly on EVERY styled cell and explicit widths on EVERY used column.
2. **DataBarRule is silently DROPPED** in conversion — use `ColorScaleRule` for bars.
3. **`SQL()` takes ranges as ARGS**: `=SQL("… FROM ?", '_raw_x'!A1:F107)` —
   `FROM [tabname]` throws a browser-side TypeError when the sidebar evaluates it.
4. Upload PUT `Content-Type` must match the session's declared source mimeType (see
   step 3) — mismatches 400.
5. Copy tabs in dependency order; a formula tab copied before its `_raw_*` source
   arrives with broken references that stay broken.
