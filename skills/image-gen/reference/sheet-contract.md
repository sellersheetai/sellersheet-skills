# 'Images Generation' sheet contract

The operator's structured record/control surface — the **`Images Generation` tab inside the
operator's catalog spreadsheet** (their main workbook for the store). Locate the catalog
spreadsheet via `get_user_context` (or `search_drive_files`), then open its `Images Generation`
tab — don't hardcode a spreadsheet ID across stores. If the tab doesn't exist yet, ask the
operator to run the sidebar's Images Generation setup (the tab is builder-owned) before recording.

**This tab is SHARED with the GAS sidebar** — its buttons (Fetch by SKU/ASIN, Reverse Prompt,
Optimize Prompt, Generate, Score) and a background poller read and write the same cells. Follow
the conventions below exactly or you will fight the sidebar's conditional formats and poller.

## Shape (layout v3, 2026-07-19)

- **4 header rows**: row 1 = machine keys (`s0_ref`,`s0_v1`,…), **hidden**; row 2 = brand band
  (A2 carries the bilingual tab guide); row 3 = group bands (`Product`, `Summary`,
  `Slot 0 · MAIN` … `Slot 8 · PT08`, `Basic A+ 1..5`, `Premium A+ 1..5`); row 4 = display
  headers with **cell-notes that document the whole workflow — read row-4 notes before
  operating a new workbook.**
- **Data starts row 5.** 4 frozen rows / 4 frozen cols. 203 columns total.
- **13 lead cols A–M**: store (A, must be `<store>-<CC>`), sku (B — becomes a hyperlink to the
  row's Drive folder), asin, ref_asin, sample_image_1-3 (E–G), product_context (H),
  ref_image_1-3 (I–K, the shared style library), overall_status (L), notes (M).
- Then nineteen 10-col blocks: **s0–s8, a1–a5, p1–p5** starting at col N (see slot-canon.md
  for the letter map). Block fields, in order:
  `ref, role, dim, prompt, reversed_prompt, scores, v1, v2, v3, status`.

## Rules

- **ONE ROW PER SKU.** A variation family = N rows. The main image goes in that row's `s0_v1`.
- **Slots = image ROLES of that SKU** (s0 main, s1.. secondary), NOT sibling colors.
- **Image cells**: formula `=IMAGE("<thumbnail_url>")` + cell note `Full-res: <cdn_url>` —
  exactly what the sidebar writes. CDN https URLs render directly; reading back, check the
  formula first, then the note, then the raw value.
- **V1–V3 are display cells, not the version ledger.** Fill the first empty of V1/V2/V3; when
  all three are full, overwrite V3 and append the replaced cell's URL to its note under
  `Replaced:`. The REAL version numbers are allocated server-side in the Image Library
  (unbounded v1..vn per store/parent/child/slot/lang) — `list_generated_images` shows them
  all; sidebar Fetch by SKU merges library images into empty V cells and lists overflow in
  the V1 note as `Also available: v<n> -> <cdn_url>`.
- **scores** cell = your compact fidelity read (e.g. `{"product_fidelity":98,...,"verdict":"pass"}`).
  The sidebar's Score button writes here too — append, don't clobber a fresh entry.
- **status** cell — use the SIDEBAR's vocabulary (conditional formats key on it):
  `DONE` (optionally `DONE · <provider>`) · `QUEUED job:<id>` (an in-flight billed job —
  NEVER submit another for that slot) · `BLOCKED: <reason>` · `ERROR: <reason>`.
  Express your own workflow states inside that grammar: a planned-but-ungenerated slot is
  `BLOCKED: awaiting direction sign-off`; an approved one is `DONE · approved v2`.
- **overall_status** (col L) is a roll-up the sidebar recomputes — write it as joined
  `LABEL VERB` fragments or leave it to the sidebar; don't invent a separate state machine.
- **reversed_prompt** cell holds the raw `reverse_prompt` output for that slot's ref;
  **prompt** holds the adapted generation prompt. Preserve prior content in the cell note
  (dated) when replacing either — that's the sidebar's convention.
- After writing, **read the row back and scan for `#VALUE!/#REF!/#SPILL!/#N/A`** before
  reporting done.

## Version history

- 2026-06-04: renumbered s1–s9 → **s0–s8 (s0 = main)**.
- 2026-07-19 (layout v3): brand band row inserted (headers moved to row 4, data to row 5) and
  `ref_asin` lead col added (12 → 13 lead cols; blocks moved M → N). The sidebar builder
  migrates older workbooks in place — if a workbook looks off-by-one against this contract,
  ask the operator to re-run the sidebar setup rather than guessing columns. **Always verify
  against hidden row 1's machine keys before writing.**
