# Run Workspace Contract

Generated artifacts are governed under one local workspace:

```text
repo-to-x-workspace/
  runs/
    <run-id>/
      run_manifest.json
      SUMMARY.md
      strategy_decision.json  # optional but preferred for arbitrary/adaptive inputs
      repos/
        <repo-id>/
          repo_context.json
          source_context.json  # optional alias for non-repo inputs
          file_manifest.txt
          claims_ledger.json
          cross_check_review.md
          posting_pack.md
          posting_queue.json     # optional parsed queue for official CLI publishing
          x_publish_log.json      # optional dry-run/live publish log, no tokens
          post_outcome.json       # optional local postmortem summary
          images_manifest.json
          images/
          repo/                  # cloned remote repo, when source is remote
```

`repo-to-x-workspace/` is intentionally ignored by git. It may contain cloned repos, draft posting copy, generated images, and local review notes.

## What Goes In Git

- Skill instructions.
- Scripts.
- Empty templates and references.
- `.env.example`.
- Packaging artifact if intentionally included.

## What Does Not Go In Git

- `.env` and real tokens.
- `repo-to-x-workspace/` run outputs.
- Cloned third-party repos.
- Generated images.
- Draft posting packs.
- Claims ledgers generated from specific repos.
- Cross-check review notes generated for a specific run.
- Posting queues and publish logs generated for a specific run.

## Image Asset Contract

Generated or sourced images used for X posting belong under each repo run directory:

```text
repos/<repo-id>/
  images_manifest.json
  images/
    image-1.png
```

Use `scripts/register_image_asset.py` to copy image files into `images/` and update `images_manifest.json`. A publishable image entry needs:

- stable `id`,
- `post` placement,
- `purpose`,
- `source_type`,
- `status`,
- `path` for real files or `prompt_only` status when no file path is available,
- `sha256` and `mime_type` for real files,
- `prompt`,
- `alt_text`,
- `disclosure`,
- `review_status`.

## Official X Publish Contract

`scripts/x_publish_thread.py` may create these files in the repo run directory:

- `posting_queue.json`: parsed post text and image id placement.
- `x_publish_log.json`: dry-run or live publish result, tweet ids, media ids, and status.

These files are local run artifacts and must not enter git. They must never include X tokens, refresh tokens, cookie values, sessions, or proxy credentials.

## Strategy Memory Contract

Adaptive/self-evolving runs may also use:

```text
repo-to-x-workspace/
  strategy-memory/
    outcomes.jsonl
    strategy_profile.json
```

`outcomes.jsonl` is append-only local memory written by `scripts/record_post_outcome.py`. `strategy_profile.json` stores aggregate quality signals and reusable lessons by strategy id. These files are local learning state, not source-of-truth instructions, and must not enter git.

The canonical skill may read this memory through `scripts/x_strategy_router.py` to bias future strategy decisions. It must not treat engagement data as factual evidence for public claims.
