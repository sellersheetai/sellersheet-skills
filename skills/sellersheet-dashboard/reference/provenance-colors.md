# Provenance colors + cell notes

The 5-color fill system encodes **who wrote this cell**. Two axes:
1. **Background fill** — provenance (always applied)
2. **Cell note** — structured JSON-prefix (mandatory on every non-default-white cell)

Lets a reader answer "where does this number come from, when was it last touched, who touched it last" without leaving the cell.

## 5-color provenance fill (RGB float values for SellerSheet MCP)

| Provenance | RGB | Hex | When to use |
|---|---|---|---|
| **Raw warehouse** | `[1.000, 1.000, 1.000]` | `#FFFFFF` | Default — `_raw_*` data rows (no fill needed; visible only by absence of tinting) |
| **Formula-derived** | `[0.953, 0.961, 0.973]` | `#F3F5F8` | Any cell with `=`… formula on a visible tab. So light it reads as "computed", doesn't compete with status chips. |
| **Agent-written** | `[0.996, 0.973, 0.890]` | `#FEF8E3` | Cells written by an AI agent (judgment, narrative, recommendation). Distinct from yellow user-input. |
| **User input** | `[1.000, 0.949, 0.800]` | `#FFF2CC` | Yellow — `_raw_cogs` operator-edit cells (selling price, FBA fee, product cost, weight). |
| **Config readback** | `[0.953, 0.973, 0.961]` | `#F3F8F6` | Cells that resolve via `cfg_fx` / `cfg_ship_rmb_kg` / `cfg_referral_pct` named ranges. Same emerald family as brand band, but 8% saturation — subliminally "config". |

All five tints are ΔE > 4 from each other and from the SellerSheet emerald brand band `[0.063, 0.725, 0.506]`. No accidental collisions.

## Cell notes — mandatory, structured

Every non-default-white cell carries a note. Format is regex-checkable on one line:

```
<prefix> | <timestamp_or_formula> | source=<a1_refs> | <freeform context or quoted insight>
```

Prefixes (must match the fill color):

```
agent    | 2026-05-12T06:00Z | source=_raw_ppc_attribution,_raw_cogs | confidence=0.7 | "Queen 153x203 bleeding -AUD 2.67/unit × 3 sold T30"
formula  | =SUMPRODUCT(...) | depends=_raw_cogs!U2:U150 | regenerated=on_open
config   | cfg_fx[AED]=1.96 | as_of=2026-05-12 | manual_edit
user     | edited 2026-05-08 by phone.w10
raw      | pull_run=abc123 | 2026-05-11T08:15Z   (only on A1 of each raw tab — see below)
```

A weekly sweeper agent can run `get_sheet_notes` across the workbook and regex-match `^(agent|formula|config|user|raw)\s\|`. Any cell whose visual tint doesn't match its note prefix surfaces drift — the sweep is a built-in lint.

## Don't carpet-note raw data

Putting a `raw | pull_run=...` note on every cell of a 1000-row `_raw_inventory` writes 1000 notes per refresh, slow to write and useless to read. **One note on `_raw_xxx!A1`** (the header origin cell) carries the run JSON; `_status` is authoritative for the rest of the rows.

Same for `_raw_catalog`, `_raw_listings`, etc. — one note per raw tab, never per cell.

## Visual rules cheat sheet (full palette)

Provenance fills are the **content** signal. The rest of the palette is the **structural** signal — section bands, headers, chips.

| Element | Color | Notes |
|---|---|---|
| Title bar row 1 | Emerald `[0.063, 0.725, 0.506]`, white bold 18pt | Every visible tab |
| Freshness pill row 2 | bg `[0.929, 0.945, 0.961]`, font `[0.4,0.4,0.4]`, 9pt italic | One line of metadata; live formula from `_status` |
| Section band | Emerald `[0.063, 0.725, 0.506]`, white bold 11pt | Merged across full width |
| Sub-header / column header | Navy `[0.157, 0.2, 0.318]`, white bold | The row that holds column names |
| **SQL-spilled table header row** | **Navy `[0.157, 0.2, 0.318]`, white bold** | Apply to the cell range where the spill's header lands (e.g. `Inventory and Restock!A14:K14`) |
| TOP 3 FIRES banner | Red `[0.815, 0.220, 0.220]`, white bold 12pt | HOME!A4 only |
| AGENT INSIGHTS section band | Emerald `[0.063, 0.725, 0.506]`, white bold | One per visible tab, anchored row 150 or 400 |
| KPI value cell | Bold 14pt | Big number tiles on HOME |
| REORDER chip | Red `[0.929, 0.451, 0.431]`, white | Conditional formatting on the Decision column |
| SOON chip | Amber-orange `[1, 0.65, 0.42]`, white | |
| HOLD chip | Green `[0.557, 0.792, 0.58]`, white | |
| REVIEW chip | Brown-gray `[0.65, 0.6, 0.55]`, white | |
| DEAD / DORMANT chip | Dark gray `[0.45, 0.45, 0.45]`, white | |
| WoC / margin gradient | Red `[0.929,0.451,0.431]` → Amber `[1,0.847,0.42]` → Green `[0.557,0.792,0.58]` | Open-range conditional gradient |
| Status badge GREEN-fresh | `[0.776, 0.91, 0.835]` | On `_status.status` column |
| Status badge AMBER-aging | `[1, 0.898, 0.6]` | On `_status.status` column |
| Status badge RED-stale / RED-error | `[0.957, 0.78, 0.765]` | On `_status.status` column |
| Footer callout / overflow notice | Soft yellow `[1.0, 0.949, 0.8]`, gray italic text | Always ABOVE the table |

Row heights: KPI rows ≈ 25 px (default), data rows with thumbnails = **38 px** (set out to row 300+ ahead of growth). Image column width = **50 px**.

## Conditional formatting on `_status.status` column

Three rules on `_status!I2:I100`:

```
Rule 1: Background = [0.776, 0.91, 0.835] when value starts with "GREEN"
Rule 2: Background = [1, 0.898, 0.6]      when value starts with "AMBER"
Rule 3: Background = [0.957, 0.78, 0.765] when value starts with "RED"
```

If `TEXT_STARTS_WITH` condition type errors on your MCP, fall back to `CUSTOM_FORMULA`: `=LEFT($I2,5)="GREEN"` etc. — same result.

## See also

- `reference/freshness-system.md` — what fills the `_status` cells the colors decorate
- `reference/agent-insights.md` — where agent-cream fills cluster (the inline FILTER sections)
- `reference/cogs-schema.md` — yellow-user vs cool-gray-formula columns on the COGS tab
- `scripts/post-build-checklist.md` — how to sweep for color/note mismatches
