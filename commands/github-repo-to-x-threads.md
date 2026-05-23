---
description: Analyze GitHub repos and create responsible X thread posting packs with evidence review and image assets.
argument-hint: '<repo-url|owner/repo|local-path> [...] [--source-file repos.txt] [--run-id id] [--refresh]'
allowed-tools: Bash(python:*), Bash(git:*), Bash(gh:*), Bash(rg:*), Bash(jq:*), Read, Write, Edit, Grep, Glob
---

# GitHub Repo to X Threads

Use the `github-repo-to-x-threads` skill from this plugin/project. If the skill body is not already loaded, read:

`$CLAUDE_PLUGIN_ROOT/skills/github-repo-to-x-threads/SKILL.md`

If `$CLAUDE_PLUGIN_ROOT` is not available, read:

`skills/github-repo-to-x-threads/SKILL.md`

## Task

Analyze the repo sources provided in `$ARGUMENTS`, create a governed local run workspace, cross-check public claims, and produce a final X posting pack.

For multi-repo or durable work, run:

```bash
python -B "$CLAUDE_PLUGIN_ROOT/skills/github-repo-to-x-threads/scripts/run_repo_to_x_pack.py" $ARGUMENTS
```

If using the repository skill path instead:

```bash
python -B "skills/github-repo-to-x-threads/scripts/run_repo_to_x_pack.py" $ARGUMENTS
```

Then read the generated `SUMMARY.md`, each `repo_context.json`, `claims_ledger.json`, `cross_check_review.md`, `posting_pack.md`, and `images_manifest.json`.

Do not present a pack as ready until `cross_check_review.md` is `pass`. Keep generated outputs in the local ignored workspace and do not commit `.env`, cloned repos, generated images, or repo-specific run artifacts.
