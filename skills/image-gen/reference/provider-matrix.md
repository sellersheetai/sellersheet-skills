# Provider matrix — openai (gpt-image-2) vs nanobanana (Gemini)

Default **openai**. Both are image MCP tools (`generate_image`, `edit_image`) selected via
`provider=`.

| Need | Provider | Why |
|------|----------|-----|
| Legible TEXT (infographics, scale labels, badges) | **openai** | gpt-image-2 renders text far better |
| Max product fidelity / fine texture | **openai** | preserves detail (e.g. center grip band) |
| Transparent background | **neither (downstream step)** | gpt-image-2 outputs opaque only; nanobanana alpha is unreliable. Generate opaque, then remove the background downstream (e.g. an external bg-removal pass) for a true transparent asset. |
| Speed / a fast draft | **nanobanana** | different backend, fast, search-grounded, single-input only |
| Quick color-only nudges | either | `edit_image` chains well on nanobanana |

`provider="both"` runs BOTH backends and **holds 2 credits** — use it only when you
genuinely want to compare outputs.

## Reliability — the rules that keep you from double-billing

- **There is no server-side retry or fallback.** A provider either delivers or the
  job ends in `status='error'`; the server enforces a hard wall-clock deadline on
  the provider call. What YOU do is governed by the job status, nothing else.
- **NEVER resubmit a `processing` job.** There is no client timeout; long
  `processing` (edit up to ~2 min, compose ~5 min) is normal, not a failure. A
  resubmit is a NEW, separately-billed job and a duplicate image.
- **Re-run only on `status='error'`.** Errors (and partial delivery) are
  **auto-refunded**, so the re-run costs the same one credit. If openai errored,
  retrying once on openai is fine; for speed you may instead re-run on
  `nanobanana` (single input — for a recolor, pass the master alone and put the
  target color/hex in the prompt), mark the result "texture-degraded" in status,
  and offer an openai re-run later.
- **Job status is kept ~15 minutes after submit, then dropped.** Poll and read
  `cdn_url` inside that window; after it, only the R2 object (already in the
  Image Library) remains. `cdn_url` can lag `status='done'` by a few seconds —
  poll once more if it's null on the first done poll.
- Polling: `check_image_job` every ~20–30s (batch: `check_image_jobs`, ≤20 ids).
  To wait in Bash use `for i in $(seq 1 N); do sleep 20; done` — a bare `sleep`
  is blocked by the harness.

## Sizes / async

- openai sizes: 2048/1536/1024 squares + 1024×1536 / 1536×1024 / auto.
- **`generate_image` defaults to `1024x1024`** (matches Studio's preset) —
  **explicitly request `2048x2048` for PDP images**; `edit_image`'s tool default
  is already 2048.
- nanobanana returns ~1024–1254 — fine for review/secondary, flag lower-res for main.
- All edit jobs (including the refine chain) are async → job_id → poll. Single
  60–120s (openai) / ~10–30s (nanobanana); compose 2–5 min. `generate_image` is
  synchronous/inline.
