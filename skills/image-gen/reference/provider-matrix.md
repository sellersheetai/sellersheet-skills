# Provider matrix — openai (gpt-image-2) vs nanobanana (Gemini)

Default **openai**. Both are image MCP tools (`generate_image`, `edit_image`) selected via
`provider=`.

| Need | Provider | Why |
|------|----------|-----|
| Legible TEXT (infographics, scale labels, badges) | **openai** | gpt-image-2 renders text far better |
| Max product fidelity / fine texture | **openai** | preserves detail (e.g. center grip band) |
| Transparent background | **neither (downstream step)** | gpt-image-2 outputs opaque only; nanobanana alpha is unreliable. Generate opaque, then remove the background downstream (e.g. an external bg-removal pass) for a true transparent asset. |
| Speed / when openai is timing out | **nanobanana** | different backend, fast, search-grounded |
| Quick color-only nudges | either | `edit_image` chains well on nanobanana |

## Reliability ladder (gpt-image-2 times out intermittently — plan for it)
1. Fire `edit_image` (openai) → get job_id.
2. Poll `check_image_job` every ~30–40s (Bash `for i in $(seq 1 2); do sleep 20; done`; bare sleep
   is blocked). Timeout signature = status "processing" with frozen `updated_at`, then error
   "Request timed out". 2-input compose times out most.
3. On timeout: **retry once on openai.**
4. Still failing: **fall back to nanobanana** (single input; for recolor pass the master as the only
   input + put the target color/hex in the prompt). Mark the result "texture-degraded" in status,
   and offer to re-run on openai once its backend recovers.

## Sizes / async
- openai sizes: 2048/1536/1024 squares + 1024×1536 / 1536×1024 / auto. Default PDP 2048×2048.
- nanobanana returns ~1024–1254 — fine for review/secondary, flag lower-res for main.
- All generate/edit jobs (including the agent-driven auto-refine `edit_image` loop) are async → job_id → poll. Single 60–120s; compose 2–5 min.
