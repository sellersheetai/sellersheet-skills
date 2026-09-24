# Cost comparison — only when the user asked for help choosing

The user decides. This page tells you how to lay the numbers out so the decision is
easy, and the ONE rule under which you may apply a choice yourself.

## The two totals (the same arithmetic as the STA-Options tab)

A placement ships with ONE carrier type, so every placement gets two comparable totals:

| Total | Formula | Inputs |
|---|---|---|
| Total (Partnered) | placement fee + Σ over shipments of the chosen partnered quote | `placementFee` from `orchestrate_fba_packing`; `partnered[].cost` from `generate_shipment_transport_options` (cheapest per shipment unless the user names a carrier) |
| Total (Own) | placement fee + Σ over shipments of (rate/kg × Weight (KG)) — or (rate/m³ × Volume (CBM)) when only a m³ rate is given | the user's own-carrier rates; `totals.weightKg` / `totals.volumeCbm` per shipment |

Weight is KG, volume CBM (LB ÷ 2.20462; IN³ × 0.0000163871; CM³ × 0.000001).

## The table you show

One row per placement, both totals, the cheapest cell of each column marked:

```
| Placement | Shipments | Warehouses | Placement fee | Partnered transport | Total (Partnered) | Own est. | Total (Own) |
|-----------|-----------|------------|---------------|---------------------|-------------------|----------|-------------|
| pl…a1     | 1         | XYZ1       | 64 USD        | 43.21 USD (UPS)     | 107.21 USD ✓      | 60.00    | 124.00      |
| pl…b2     | 5         | ABC1, …    | 0 USD         | 5 quotes: 210.40    | 210.40            | 250.00   | 250.00      |
```

Then, in one sentence each:
- which row is cheapest per column and by how much;
- the trade the user is making (fewer shipments vs lower fee; nearer warehouse vs price);
- the user's **preferred warehouse id(s)**, if any, as a tiebreak — never as a filter of Amazon's offer;
- own carrier needs a delivery window whose `availabilityType` is AVAILABLE and whose start is on or after the ship date.

Rates are quoted only when the user gave them. Never invent a rate, never quote a credit
price, never present an own-carrier "cost" Amazon did not return (own-carrier options have no quote).

## Getting the numbers the rule needs

"Cheapest total" needs a transport quote per placement, and quotes exist only after
`generate_shipment_transport_options` for THAT placement (an Amazon write, ~20–60 s each).
Under a rule: run it for every placement when there are ≤ 3, otherwise for the 3 lowest
placement fees, then compare. Under "help me choose" without autopilot: show the placement
table first (fees only), let the user shortlist, quote the shortlist. Mode A: pass
`sta_spreadsheet_id` ONLY on the call for the placement finally picked (it fills that block's
dropdowns); quote the other candidates without it, so STA-Options shows one picked block.

**No own-carrier rate given** (own carrier, "cheapest total"): Total (Own) falls back to the
placement fee alone — the columns then compare placement fees, which is still the cheapest
choice (the sidebar's own rule). Say so in the reply; do not stop.

## When you may apply a choice

Only if ALL of these are true, and then say which rule picked it:
1. the intake line "help me choose" is ✓ AND the user said, in their own words, to complete it
   end to end (autopilot ✓);
2. the user named the rule. "Pick the cheapest (for me)" NAMES the rule "cheapest total";
   "fewest shipments", "prefer warehouse X, else cheapest" and "single shipment to one of
   {FC codes}" (the 刷仓 rule, `WAREHOUSE_FISHING.md`) are the others. Restate the
   rule you understood in the reply so the user can correct it;
3. the rule yields ONE placement and ONE option per shipment without a tie.

A tie, or an Amazon option the rule cannot price (a partnered quote missing) → stop and show
the table. A missing own-carrier rate is NOT a stop (see the fallback above).
Everything else in this workflow (packing option, placement, transport option, delivery window)
remains a listed choice the user makes.
