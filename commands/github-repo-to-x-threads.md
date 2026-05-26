---
description: Analyze repos, papers, URLs, files, ideas, or existing packs and create responsible X posting packs with strategy routing, evidence review, images, and optional publish.
argument-hint: '<repo-url|owner/repo|local-path|paper-url|web-url|file|idea> [...] [--source-file sources.txt] [--run-id id] [--refresh]'
allowed-tools: Bash(python:*), Bash(git:*), Bash(gh:*), Bash(rg:*), Bash(jq:*), Read, Write, Edit, Grep, Glob
---

# GitHub Repo to X Threads

Use the `github-repo-to-x-threads` skill from this plugin/project. If the skill body is not already loaded, read:

`$CLAUDE_PLUGIN_ROOT/skills/github-repo-to-x-threads/SKILL.md`

If `$CLAUDE_PLUGIN_ROOT` is not available, read:

`skills/github-repo-to-x-threads/SKILL.md`

## Task

Analyze the sources provided in `$ARGUMENTS`, choose a posting strategy, create a governed local run workspace, cross-check public claims, and produce a final X posting pack.

Thread length is adaptive. Do not force exactly 8 posts; use the number of posts the repo evidence and user angle justify.

Actual generated images are part of the default posting pack. Use native image generation when available, then register the files in `images_manifest.json`. Only leave prompt-only images when the user explicitly chose text-only/prompts-only/manual images or image generation is unavailable.

First route the input when it is not clearly a single GitHub/local repo, or when the user asks for strategy/self-evolution:

```bash
python -B "$CLAUDE_PLUGIN_ROOT/skills/github-repo-to-x-threads/scripts/x_strategy_router.py" $ARGUMENTS
```

For arbitrary-input durable work, run:

```bash
python -B "$CLAUDE_PLUGIN_ROOT/skills/github-repo-to-x-threads/scripts/run_any_to_x_pack.py" $ARGUMENTS
```

For multi-repo or deep GitHub repo work, run:

```bash
python -B "$CLAUDE_PLUGIN_ROOT/skills/github-repo-to-x-threads/scripts/run_repo_to_x_pack.py" $ARGUMENTS
```

If using the repository skill path instead:

```bash
python -B "skills/github-repo-to-x-threads/scripts/run_repo_to_x_pack.py" $ARGUMENTS
```

Then read the generated `SUMMARY.md`, each `repo_context.json`, `claims_ledger.json`, `cross_check_review.md`, `posting_pack.md`, and `images_manifest.json`.

If a `strategy_decision.json` exists, read it before drafting. After review or publish, record outcomes with `record_post_outcome.py` when the user provides metrics or qualitative feedback.

If the draft feels rigid, generic, or not worth publishing, run an angle-first tournament before trying to publish:

```bash
python -B "$CLAUDE_PLUGIN_ROOT/skills/github-repo-to-x-threads/scripts/x_draft_tournament.py" <repo-run-dir> \
  --prompt "User taste feedback" \
  --write-proposed-pack
```

Treat `posting_pack.proposed.md` as a candidate. Re-run claim, image, and eval gates before live publishing.

Before live publishing, prefer running:

```bash
python -B "$CLAUDE_PLUGIN_ROOT/skills/github-repo-to-x-threads/scripts/x_eval_post.py" <repo-run-dir>
```

After live publishing, prefer:

```bash
python -B "$CLAUDE_PLUGIN_ROOT/skills/github-repo-to-x-threads/scripts/x_collect_metrics.py" <repo-run-dir>
python -B "$CLAUDE_PLUGIN_ROOT/skills/github-repo-to-x-threads/scripts/x_calibrate_strategy.py" <repo-run-dir>
```

Do not present a pack as ready until `cross_check_review.md` is `pass`. Keep generated outputs in the local ignored workspace and do not commit `.env`, cloned repos, generated images, or repo-specific run artifacts.

Before presenting "Ready To Post", run:

```bash
python -B "$CLAUDE_PLUGIN_ROOT/skills/github-repo-to-x-threads/scripts/check_image_assets.py" <repo-run-dir>
```

If using the repository skill path instead:

```bash
python -B "skills/github-repo-to-x-threads/scripts/check_image_assets.py" <repo-run-dir>
```
