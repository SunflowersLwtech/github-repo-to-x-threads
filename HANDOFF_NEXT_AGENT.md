# Handoff For Next Agent

Start here:

```text
You are continuing work in the migrated repo at /Users/sunfl/Documents/media/X.
Do not use /Volumes/T7/AI_Dev/X; that T7 copy was intentionally removed after migration.

Read AGENTS.md first, then skills/github-repo-to-x-threads/SKILL.md.
The canonical reusable skill remains skills/github-repo-to-x-threads/.
.codex-plugin/, .claude-plugin/, commands/, .claude/, and installed user skill copies are adapters only.

The local .env in /Users/sunfl/Documents/media/X contains Grok/X/GitHub credentials; never print secrets.
Use official X API publishing only after explicit user approval.
Generated run workspaces and generated images stay local and out of git.

Current focus:
- Improve github-repo-to-x-threads so it can evaluate and evolve X posts from any technical input.
- User disliked rigid, safe-summary threads; optimize for angle-first, high-taste, concrete technical posts.
- For GitHub Trending experiments, use metadata-only fast screening first:
  python -B skills/github-repo-to-x-threads/scripts/x_trending_experiment.py --limit 10 --rounds 3 --since daily --metadata-only
- Only deep clone/generate images for selected candidates after the text-only screen.

Important new scripts:
- skills/github-repo-to-x-threads/scripts/x_generate_posting_pack.py
- skills/github-repo-to-x-threads/scripts/x_trending_experiment.py
- skills/github-repo-to-x-threads/scripts/x_eval_post.py
- skills/github-repo-to-x-threads/scripts/x_draft_tournament.py
- skills/github-repo-to-x-threads/scripts/x_collect_metrics.py
- skills/github-repo-to-x-threads/scripts/x_calibrate_strategy.py

Recent experiment outputs:
- repo-to-x-workspace/runs/trending_daily_rounds_20260527_a/trending_experiment_report.md
  Deep clone experiment, 6 repos, heavy disk use; no candidate crossed ready threshold.
- repo-to-x-workspace/runs/trending_daily_metadata_20260527_b/trending_experiment_report.md
  Metadata-only experiment, 10 repos, 30 eval rounds; no ready candidate, but useful failure patterns.

Key findings to continue from:
- Default to text-only angle screening before images.
- Do not accept a Grok tournament rewrite unless its eval score improves.
- Common failures: no repeatable thesis, generic repo-note opener, too much README summary, too little concrete example, missing caveat, mixed-language voice drift.
- Early text-only eval should ignore image/media complaints; image gates happen only during publish prep.

Before handing results back, run:
- python -m py_compile skills/github-repo-to-x-threads/scripts/*.py
- scripts/install_skill_bundle.sh /Users/sunfl/Documents/media/X
```
