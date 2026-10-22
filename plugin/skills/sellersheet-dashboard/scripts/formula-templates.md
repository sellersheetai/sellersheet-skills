# Formula templates

Copy-paste formulas tested in production builds (empirically verified across single- and multi-store builds). Substitute placeholders in `<angle brackets>`.

## Row-2 freshness pill (TEXTJOIN from `_status`)

For each visible tab, replace any hardcoded "Refreshed YYYY-MM-DD" with:

```javascript
=TEXTJOIN(" · ", TRUE,
  "<tab purpose>",
  "<raw1> " & IFERROR(INDEX(_status!I:I, MATCH("_raw_<raw1>", _status!A:A, 0)), "?"),
  "<raw2> " & IFERROR(INDEX(_status!I:I, MATCH("_raw_<raw2>", _status!A:A, 0)), "?"),
  "oldest " & TEXT(MINIFS(_status!F:F, _status!A:A, "_raw_<raw1>"), "yyyy-mm-dd hh:mm") & " UTC",
  "budget " & INDEX(_status!E:E, MATCH("_raw_<raw1>", _status!A:A, 0)) & "h")
```

For multi-store rows in `_status`, use array-match:
```javascript
"<raw1> AE " & IFERROR(INDEX(_status!I:I, MATCH(1, (_status!A:A="_raw_<raw1>")*(_status!B:B="<store>"), 0)), "?"),
```

## `_status` status formula (per row)

```javascript
=IF(J{n}<>"","RED-error",
  IF((NOW()-F{n})*24>E{n}*2,"RED-stale",
    IF((NOW()-F{n})*24>E{n},"AMBER-aging","GREEN-fresh")))
```

Where `{n}` is the row number. Apply to column I starting row 2.

## `_status.row_count` formula (per row)

```javascript
=COUNTIF('_raw_<tab>'!A:A, B{n})
```

For `_raw_catalog` which is store-agnostic (store="ALL"):
```javascript
=COUNTA('_raw_catalog'!A2:A)
```

## `_status.agent_actions_count` formula (per row)

```javascript
=IFERROR(COUNTIFS(_agent_notes!E:E, A{n}, _agent_notes!C:C, B{n}, _agent_notes!L:L, ""), 0)
```

(Counts active — not superseded — agent notes scoped to this raw tab × store.)

## README live freshness spill — per-column ARRAYFORMULA

DO NOT use `SQL()` here — `_status` column I has `NOW()` which makes SQL fail. Use per-column `ARRAYFORMULA`:

```
README!A15:I15 (header row, manually written):
  ["Raw Tab", "Store", "Source rpt_*", "Cadence", "Budget h", "Last Pulled UTC", "Status", "Rows", "Last Error"]

README!A16: =ARRAYFORMULA(_status!A2:A13)
README!B16: =ARRAYFORMULA(_status!B2:B13)
README!C16: =ARRAYFORMULA(_status!C2:C13)
README!D16: =ARRAYFORMULA(_status!D2:D13)
README!E16: =ARRAYFORMULA(_status!E2:E13)
README!F16: =ARRAYFORMULA(IF(_status!F2:F13="","",TEXT(_status!F2:F13,"yyyy-mm-dd hh:mm")))
README!G16: =ARRAYFORMULA(_status!I2:I13)
README!H16: =ARRAYFORMULA(_status!H2:H13)
README!I16: =ARRAYFORMULA(_status!J2:J13)
```

Adjust `_status!*2:*13` row range to match your actual `_status` row count.

## Canonical Image-at-A formula (with `_raw_catalog` JOIN)

```javascript
=MAP(SQL("SELECT cat.[image_url] 
          FROM ? AS data LEFT JOIN ? AS cat 
            ON data.[store]=cat.[store] AND data.[sku]=cat.[sku] 
          <WHERE clause matching the data SQL> 
          ORDER BY <same as data SQL>
          <LIMIT 200 if data SQL has LIMIT 200>",
         '_raw_<self>'!A1:<lastcol>, '_raw_catalog'!A1:E),
     LAMBDA(url, IF(url="image_url", "Image",
                    IF(url="", "", IMAGE(url)))))
```

Example for Inventory and Restock:
```javascript
=MAP(SQL("SELECT cat.[image_url] 
          FROM ? AS data LEFT JOIN ? AS cat 
            ON data.[store]=cat.[store] AND data.[sku]=cat.[sku] 
          WHERE data.[afn_warehouse_quantity] > 0 
          ORDER BY data.[afn_warehouse_quantity] DESC, data.[sku] ASC 
          LIMIT 200", 
         '_raw_inventory'!A1:R, '_raw_catalog'!A1:F),
     LAMBDA(url, IF(url="image_url", "Image", IF(url="", "", IMAGE(url)))))
```

## SQL data spill with overflow guard

```javascript
=SQL("SELECT [store] AS [Store], [sku] AS [SKU], [asin] AS [ASIN], [product] AS [Product], 
        [your_price] AS [Price (AED)], [afn_fulfillable_quantity] AS [Fulfillable], 
        [afn_reserved_quantity] AS [Reserved], [inbound_total] AS [Inbound], 
        [afn_warehouse_quantity] AS [Warehouse Qty], [afn_unsellable_quantity] AS [Unsellable] 
      FROM ? 
      WHERE [afn_warehouse_quantity] > 0 
      ORDER BY [afn_warehouse_quantity] DESC, [sku] ASC 
      LIMIT 200", 
     '_raw_inventory'!A1:R)
```

## Overflow footer (anchor 1 row below max spill extent)

When the spill is anchored at row 14 with LIMIT 200, the data ends at row 214. Overflow footer at row 215:

```javascript
="Showing first 200 of " 
  & COUNTIFS('_raw_inventory'!A:A, "<store>", '_raw_inventory'!M:M, ">0") 
  & " active SKUs (LIMIT 200 guard). See _raw_inventory tab for the full catalog list."
```

(Column M = `afn_warehouse_quantity` in canonical inventory schema. Adjust to your column.)

Format with soft yellow `[1, 0.949, 0.8]` bg + italic.

## AGENT INSIGHTS FILTER (per visible tab)

Anchor row depends on max spill extent — row 150 for bounded tabs, row 400 for catalog-scaling tabs.

```javascript
=IFERROR(FILTER({_agent_notes!B2:B100, _agent_notes!D2:D100, _agent_notes!G2:G100, 
                 _agent_notes!H2:H100, _agent_notes!I2:I100, _agent_notes!J2:J100},
                _agent_notes!E2:E100="<tab name>",
                _agent_notes!L2:L100=""),
         "No active insights for this tab.")
```

Format the date column (col A relative to the spill) with `DATE_TIME` number format.

## TODOAY'S TOP 3 FIRES on HOME (rows 4-8)

```
HOME!A4 (red banner):
  TODAY'S TOP 3 FIRES — ranked by urgency × recoverable revenue
  bg [0.815, 0.220, 0.220], white bold 12pt

HOME!A5:F5 (navy header):
  Rank | Store | Insight | Action | Confidence | Supporting cells

HOME!A6 (FILTER formula, spills 3 rows):
  =IFERROR(FILTER({_agent_notes!F2:F100, _agent_notes!D2:D100, _agent_notes!H2:H100, 
                   _agent_notes!I2:I100, _agent_notes!K2:K100, _agent_notes!J2:J100},
                  REGEXMATCH(_agent_notes!F2:F100, "^fire-"),
                  _agent_notes!L2:L100=""), 
            "no fires — enjoy the morning")

HOME!A6:F8 background: agent cream [0.996, 0.973, 0.890]
```

## Threshold-triggered self-pruning agent cell

```javascript
=IF(<source!cell> <comparator> <threshold>, "<callout text>", "")
```

Example — AE Invoice Defect remediation block, self-prunes when defect rate <5%:
```javascript
=IF(AccountHealth!B11 > 0.05, "AE Invoice Defect 97.92% — activate VCS, set up auto-invoicing for B2B orders", "")
```

## FX VLOOKUP in `_raw_cogs`

```javascript
// Landed cost (AED) from total RMB
=M2 / VLOOKUP("AED", cfg_fx, 2, FALSE)

// Profit (AED) = price - fees - landed
=F2 - I2 - N2

// Margin %
=IFERROR(O2/F2, "")

// Suggested price (target ~37% gross margin)
=Q2 * 1.6
```

`cfg_fx` is the named range pointing at `_config!A2:B5` (currency, rate per RMB columns).

## Concentration risk on HOME

```javascript
="Top SKU 30d = " 
  & TEXT(MAX(SUMIFS('_raw_inventory'!N:N, '_raw_inventory'!A:A, "<store>")) 
       / SUM(SUMIFS('_raw_inventory'!N:N, '_raw_inventory'!A:A, "<store>")), "0%") 
  & " of <store> revenue"
```

(Replace column N with the sales_t30 column in your `_raw_inventory` schema.)

## Dead capital on HOME (per store)

```javascript
=SUMPRODUCT(
  ('_raw_inventory'!A:A="<store>") * 
  ('_raw_inventory'!<units_t30_col>=0) * 
  ('_raw_inventory'!<available_col>) * 
  ('_raw_inventory'!<your_price_col>) * 0.4)
```

(0.4 multiplier is the fall-back when COGS isn't populated — yields a conservative dead-capital estimate.)

## `=HYPERLINK` to drill tabs from HOME

```javascript
=HYPERLINK("#gid=" & <sheet_id>, "→ Open <Tab Name>")
```

Pull real `<sheet_id>` from `list_sheet_tabs` — never hardcode plain text arrows.

## See also

- `scripts/seed-status-rows.md` — `_status` rows pre-filled with budgets
- `scripts/post-build-checklist.md` — verification routine
- `reference/freshness-system.md`, `reference/image-catalog.md`, `reference/cogs-schema.md` — schema specs the formulas above depend on
