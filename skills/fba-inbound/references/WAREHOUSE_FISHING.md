# Fishing for a warehouse — 刷仓 / 刷美西仓

**Goal.** The user ships with their own carrier and wants Amazon to route the whole plan to
one nearby FC (typically US-West: e.g. codes starting `LAX`, `ONT`, `SBD`, `LGB`, `SMF`,
`GYR`, `PHX`, `LAS`, `SNA` — the user names the list, you never assume it) so freight is
cheap. Amazon decides the destination per plan; the seller can only try again.

**目标。** 卖家用自己的承运商发货，希望整个计划只分到一个近处的仓（通常是美西仓，如
LAX/ONT/SBD/LGB/SMF/GYR/PHX/LAS/SNA 开头——由用户给出想要的仓代码列表，不要自己猜），
从而降低运费。分仓由亚马逊决定；卖家能做的只是再试。

## Facts that shape the loop（决定循环方式的事实）

1. **A plan's placement set is fixed for its validity window (3 days).** Re-running
   "generate placement options" on the SAME plan within that window returns the SAME options
   (same ids, same FCs, status OFFERED, `expiration` 3 days out). A re-run is not a new draw.
   同一计划三天内多次生成分仓方案，结果一样；重新生成不是重新抽签。
2. **A NEW plan is a new draw.** The same SKUs, boxes and address can be offered different
   FCs on a new plan. That is the lever; changing the ship-from address (fact 3) or the
   quantity / box split widens the draw.
   新建计划就是新的抽签——同样的 SKU、箱规、地址也会给出不同的仓；换发货地址或改数量/箱规，
   变化更大。
3. **A different ship-from address is also a new draw** (a second Shipment Setting row /
   another warehouse code). 换一个发货地址也会得到不同的分仓。
4. **Every ACTIVE plan reserves inbound capacity.** Amazon limits what a seller can have in
   flight (Seller Central inbound / storage capacity). When capacity allows, several plans
   can exist at once and be compared; when it does not, `orchestrate_fba_packing` fails or
   offers nothing useful, so the loop becomes create → check → cancel → create.
   每个未取消的计划都占用仓容：仓容够时可以一次建多个计划再比较；仓容不够时只能建一个、看结果、
   取消、再建。
5. **Placement fee vs freight.** A single-shipment placement usually carries a placement fee
   (e.g. 64 USD) while the multi-shipment option is free; the user trades that fee against
   own-carrier freight. Show both per candidate (`COST_COMPARISON.md`). Placement fees are
   charged at confirmation, so a plan cancelled before confirm has none.

## Intake additions for this use case

- wanted FC codes or prefixes — REQUIRED; the named rule is "single shipment to one of
  {codes}, cheapest total among those" (with no own-carrier rate given, cheapest placement fee);
- how many plans may exist at once — default 1 unless the user says capacity allows more;
- alternative ship-from addresses to try, in order — optional;
- how many draws before giving up — default 3.

## The loop（循环）

```
draws = []
for draw in 1..N (one at a time unless the user allowed several in flight):
    plan = orchestrate_fba_packing(plan_name = "<name>", source_address = <address for this draw>, …)
           # mode A: same workbook, pass sta_spreadsheet_id — the server re-renders STA-Options for this draw
    offered = plan.placementOptions[].shipments[].warehouseId
    hit = a placement with ONE shipment whose warehouseId matches the wanted list
    draws.append(draw, plan.planId, offered, hit)
    if hit: break
    if plans_in_flight == allowed: cancel_inbound_plan(plan.planId)     # part of the user's instruction
after the loop:
    cancel_inbound_plan on EVERY draw that is not the hit and is still active (parallel mode)
    the hit continues the normal chain (write the "2." pick, transport → confirm → …)
```

- Cancelling the losing draws is part of the fishing instruction the user gave; a draw the
  user did not ask you to fish with is never cancelled, and a CONFIRMED plan is never cancelled
  by the loop (cancel after confirm exists, but only on an explicit "cancel").
- Present every draw's placement table (SKILL.md §4 shape) so the user sees what Amazon offered
  even when it did not match; a partial match (2 shipments, one in the wanted FC) is shown, not
  silently taken.
- Mode A, one workbook: `create_sta_sheet` once with the user's plan name; every draw uses that
  name and that `sta_spreadsheet_id`, so STA-Options always shows the latest draw. Write the
  stepper (`1a.` id, `2.` pick) and Manage Shipments `planId` only for the hit; the losing draws
  live in the handover text ("draw 2: wf… offered ABE8/FTW1/SCK4 — no match — cancelled").
  Mode B: draws are rows in the handover text and the placement tables in the user's output.

## What to tell the user（告知用户）

- Which FCs each draw offered, the fee of the single-shipment option, and why a draw was
  cancelled. 每次抽签给了哪些仓、单货件方案的分仓费、为什么取消。
- That re-generating on the same plan will not change the answer for 3 days.
  同一计划三天内重新生成不会变。
- That a cancelled, unconfirmed plan carries no fee, and each draw is ~1 minute of tool time.
  未确认就取消的计划不收费；每次抽签约需 1 分钟。
