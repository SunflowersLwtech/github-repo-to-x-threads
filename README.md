# github-repo-to-x-threads

Agent Skills plugin for turning GitHub repositories and other technical inputs into responsible X/Twitter posting packs.

The canonical skill is agent-neutral:

```text
skills/github-repo-to-x-threads/
  SKILL.md
  scripts/
  references/
```

Adapter metadata is thin and separate:

```text
.codex-plugin/plugin.json      # Codex plugin manifest
.claude-plugin/plugin.json     # Claude Code plugin manifest
commands/                      # Claude plugin slash command fallback
```

Do not install this project by copying the whole repository into `.claude/skills`. The reusable skill lives under `skills/`; installers and plugin manifests adapt that folder for each agent surface.

## Coding Agent One-Line Config

Coding agents should treat `AGENTS.md` plus `skills/github-repo-to-x-threads/SKILL.md` as the source of truth, keep generated runs/images/env files out of git, and use `scripts/install_skill_bundle.sh /Users/sunfl/Documents/media/X` only to sync local install surfaces.

## What It Does

Given one or more GitHub repos, owner/repo strings, local paths, arXiv/alphaXiv papers, web URLs, PDFs/notes, existing posting packs, or raw ideas, the skill guides an agent to:

1. classify the input and choose a posting strategy,
2. clone/read repos or collect source-specific evidence for papers, pages, files, and ideas,
3. cross-check evidence against live metadata when available,
4. separate verified facts, reasonable inference, and user vision,
5. draft a paste-ready X thread/article with attribution and caveats,
6. create a final-mile posting pack with image placement and alt text,
7. generate and govern GPT Image 2-style assets through a local image registry by default,
8. optionally publish the approved pack through the official X API from the CLI,
9. record outcomes into local strategy memory so later posts can improve,
10. synthesize eval/publish/experiment signals into an auditable skill-evolution report and patch plan.

## Install For Local Use

The helper installs the canonical skill plus local adapters without committing generated outputs:

```bash
scripts/install_skill_bundle.sh /Users/sunfl/Documents/media/X
```

It writes:

```text
/Users/sunfl/Documents/media/X/
  skills/github-repo-to-x-threads/      # canonical plugin skill
  .codex-plugin/plugin.json             # Codex plugin manifest
  .claude-plugin/plugin.json            # Claude plugin manifest
  commands/github-repo-to-x-threads.md  # Claude plugin command
  .claude/skills/github-repo-to-x-threads/  # Claude project adapter
```

It also installs one user-level Codex skill copy to:

```text
~/.agents/skills/github-repo-to-x-threads/
```

Do not also keep this skill under `~/.codex/skills/` or the bundle's `.agents/skills/`; Codex will show duplicate entries if the same skill is present in multiple scanned locations.

## Manual Install

Codex official user skill location:

```bash
mkdir -p ~/.agents/skills
cp -R skills/github-repo-to-x-threads ~/.agents/skills/
```

Claude Code personal skill location:

```bash
mkdir -p ~/.claude/skills
cp -R skills/github-repo-to-x-threads ~/.claude/skills/
```

For plugin distribution, use the repository root as the plugin folder. Codex reads `.codex-plugin/plugin.json`; Claude Code reads `.claude-plugin/plugin.json` and the root `skills/` directory.

## Governed Multi-Repo Runs

Use the run-pack script when you want one governed workspace for one or more repos:

```bash
python -B skills/github-repo-to-x-threads/scripts/run_repo_to_x_pack.py \
  https://github.com/owner/repo owner2/repo2 --refresh
```

Or use a source list:

```bash
python -B skills/github-repo-to-x-threads/scripts/run_repo_to_x_pack.py \
  --source-file repos.txt --refresh
```

Outputs are written under:

```text
repo-to-x-workspace/runs/<run-id>/
```

Each repo gets:

- `repo_context.json`
- `file_manifest.txt`
- `claims_ledger.json`
- `cross_check_review.md`
- `posting_pack.md`
- `images_manifest.json`
- `images/`
- `repo/` when the source is remote

`repo-to-x-workspace/` is ignored by git. It is the local, accessible place for cloned repos, generated images, drafts, review notes, and final posting packs.

## Any Input Strategy Runs

For non-repo or strategy-first inputs, start with the router:

```bash
python -B skills/github-repo-to-x-threads/scripts/x_strategy_router.py \
  "https://www.alphaxiv.org/abs/2605.22817" \
  --prompt "帮我决定策略并发成中文 X thread"
```

For a governed workspace:

```bash
python -B skills/github-repo-to-x-threads/scripts/run_any_to_x_pack.py \
  "https://www.alphaxiv.org/abs/2605.22817" \
  --prompt "帮我决定策略并发成中文 X thread" \
  --run-id vpo-paper-share
```

This creates:

```text
repo-to-x-workspace/runs/<run-id>/
  strategy_decision.json
  run_manifest.json
  SUMMARY.md
  repos/<source-id>/
    repo_context.json
    source_context.json
    claims_ledger.json
    cross_check_review.md
    posting_pack.md
    images_manifest.json
    images/
```

Use `run_repo_to_x_pack.py` for deep GitHub repo collection. Use `run_any_to_x_pack.py` when the source can be a paper, web URL, PDF, existing pack, or raw idea.

## Self-Evolving Strategy Memory

After review or live publish, record the result:

```bash
python -B skills/github-repo-to-x-threads/scripts/record_post_outcome.py \
  repo-to-x-workspace/runs/<run-id>/repos/<source-id> \
  --manual-quality 0.8 \
  --lesson "The strongest posts used a direct caveat in the hook."
```

When real X metrics are available:

```bash
python -B skills/github-repo-to-x-threads/scripts/record_post_outcome.py \
  repo-to-x-workspace/runs/<run-id>/repos/<source-id> \
  --impressions 10000 \
  --likes 120 \
  --reposts 18 \
  --replies 9 \
  --bookmarks 35 \
  --lesson "Architecture images worked better than generic hero images."
```

This writes ignored local memory:

```text
repo-to-x-workspace/strategy-memory/outcomes.jsonl
repo-to-x-workspace/strategy-memory/strategy_profile.json
```

Future `x_strategy_router.py` runs read this profile and surface learned notes. The memory biases strategy selection; it does not replace evidence checks or authorize unsupported public claims.

For a broader self-evolution pass across evals, live publish logs, recorded
outcomes, and Trending experiments:

```bash
python -B skills/github-repo-to-x-threads/scripts/x_skill_evolution.py \
  --runs-root repo-to-x-workspace/runs \
  --memory-root repo-to-x-workspace/strategy-memory \
  --run-id review_latest
```

This writes:

```text
repo-to-x-workspace/skill-evolution/<run-id>/
  signal_ledger.json
  skill_evolution_summary.json
  skill_evolution_report.md
  skill_patch_plan.md
```

Add `--apply-profile` only when you want the proposed rules stored in ignored
local `strategy_profile.json` as routing guidance. The script never edits
`SKILL.md` or public claims automatically; turn `skill_patch_plan.md` into a
reviewed code/doc change with a regression eval.

## X Eval Agent

Use Grok plus deterministic checks to score a posting pack before publishing:

```bash
python -B skills/github-repo-to-x-threads/scripts/x_eval_post.py \
  repo-to-x-workspace/runs/<run-id>/repos/<source-id>
```

It writes:

```text
post_eval.json
x_eval_report.md
```

If `GROK_API_KEY` is present in the local ignored `.env`, Grok provides semantic scores and suggestions. Without Grok, the script falls back to deterministic rubric checks.

The evaluator is intentionally strict on editorial quality. It now scores:

- `angle_freshness`
- `specificity_density`
- `voice_authenticity`

A safe summary can still be marked `revise` if it feels rigid or generic.

When a draft feels weak, run a Grok draft tournament:

```bash
python -B skills/github-repo-to-x-threads/scripts/x_draft_tournament.py \
  repo-to-x-workspace/runs/<run-id>/repos/<source-id> \
  --prompt "User says the current skill is too rigid and quality is not good" \
  --write-proposed-pack
```

It writes:

```text
draft_tournament.json
draft_tournament.md
posting_pack.proposed.md
```

Use the proposed pack as a candidate, then re-run claim/image/eval gates before publishing.

After publishing, collect X metrics and calibrate strategy memory:

```bash
python -B skills/github-repo-to-x-threads/scripts/x_collect_metrics.py \
  repo-to-x-workspace/runs/<run-id>/repos/<source-id>

python -B skills/github-repo-to-x-threads/scripts/x_calibrate_strategy.py \
  repo-to-x-workspace/runs/<run-id>/repos/<source-id> \
  --lesson "Architecture images beat generic hero images for this audience."
```

## Trending Experiments

For broad testing, pull current GitHub Trending and run multi-round text-only evals before spending time on deep clones or images:

```bash
python -B skills/github-repo-to-x-threads/scripts/x_trending_experiment.py \
  --limit 10 \
  --rounds 3 \
  --since daily \
  --metadata-only \
  --run-id trending_daily_metadata
```

This writes `trending_experiment_results.json` and `trending_experiment_report.md` under the run directory. The script only accepts a tournament rewrite when it scores better than the current draft.

Use deep clone mode only after a repo survives the fast screen:

```bash
python -B skills/github-repo-to-x-threads/scripts/x_trending_experiment.py \
  --limit 3 \
  --rounds 3 \
  --since daily \
  --refresh
```

The evaluator is not a real X ranking oracle. It combines local posting-pack gates, approximate recommendation-system heuristics, Grok semantic review, and the user's own historical outcomes.

## Image Governance

Final posting packs should generate actual images by default. Use text-only, no-images, prompts-only, or manual-image mode only when the user explicitly asks for it or the image tool is unavailable.

Generated image files must be copied into the repo run directory and registered:

```bash
python -B skills/github-repo-to-x-threads/scripts/register_image_asset.py \
  repo-to-x-workspace/runs/<run-id>/repos/<repo-id> /path/to/generated.png \
  --id image-1 \
  --post 1/N \
  --purpose "hook visual" \
  --prompt "..." \
  --alt-text "..." \
  --disclosure "Generated conceptual visual, not an official project screenshot."
```

The registry writes `images_manifest.json` with:

- stable image id,
- post placement,
- source type,
- model,
- governed local path,
- `sha256`,
- MIME type,
- prompt,
- alt text,
- disclosure,
- review status.

If the generation tool cannot expose a file path, register a prompt-only entry with `--prompt-only` and do not claim an actual governed image file exists.

When an agent is asked for actual images, it should use its native image generation capability first, such as Codex `imagegen` / built-in image generation. Script-drawn cards, SVG placeholders, browser screenshots, or canvas diagrams are not substitutes for GPT Image-style assets unless the user explicitly asked for deterministic code-native graphics.

Before a pack is presented as ready, run:

```bash
python -B skills/github-repo-to-x-threads/scripts/check_image_assets.py \
  repo-to-x-workspace/runs/<run-id>/repos/<repo-id>
```

Only pass `--allow-prompt-only` when the user opted out of actual images or the image generation tool could not provide a governable local file.

## Adaptive Threads

The skill does not force exactly 8 posts. It uses the repo evidence and the user's angle to choose the length: short repos can be 4-6 posts, richer repo+vision posts can be 8-12, and longer threads are acceptable when needed for attribution, evidence, caveats, or practical use.

## Official X API CLI Publishing

Full automation is supported only through official X API user credentials. The first post is created by the CLI as a normal root post; each later thread item is created as a reply to the previous post by default.

Existing app-only keys such as `X_BEARER_TOKEN` are not enough to publish. For the bundled publisher, configure OAuth2 user credentials with these scopes:

```text
tweet.read users.read tweet.write media.write offline.access
```

One-time setup:

1. Create or open your app in the X Developer Portal.
2. Enable OAuth2 user authentication for the app.
3. Add this callback URL exactly, or set your own and use it consistently:

```text
http://127.0.0.1:8765/callback
```

4. Put the app's OAuth2 Client ID in your local ignored `.env`:

```bash
cp skills/github-repo-to-x-threads/.env.example .env
# edit .env and set X_CLIENT_ID, optionally X_CLIENT_SECRET
python -B skills/github-repo-to-x-threads/scripts/x_oauth2_pkce_setup.py --env-file .env
```

Dry-run the generated posting pack:

```bash
python -B skills/github-repo-to-x-threads/scripts/x_publish_thread.py \
  repo-to-x-workspace/runs/<run-id>/repos/<repo-id>
```

Publish after review:

```bash
python -B skills/github-repo-to-x-threads/scripts/x_publish_thread.py \
  repo-to-x-workspace/runs/<run-id>/repos/<repo-id> \
  --live
```

The publisher uploads registered images, attempts to set alt text, marks generated-image posts with `made_with_ai`, posts the first thread item, then replies with the rest. It writes `x_publish_log.json` in the ignored run directory and never logs tokens.

Do not use cookie replay, website automation, hidden GraphQL calls, `auth_session` services, or proxy-based third-party posting as this project's default path.

When using an external bundle such as `/Users/sunfl/Documents/media/X`, you may keep local user-governed artifacts at the bundle root:

- `/Users/sunfl/Documents/media/X/.env`
- `/Users/sunfl/Documents/media/X/repo-to-x-workspace/`

The installer preserves these bundle-root paths. Do not commit `.env`, and do not place real env files or generated run workspaces under `skills/`.

## Local Env

Create a local `.env` when you want live GitHub metadata or official X API publishing:

```bash
cp skills/github-repo-to-x-threads/.env.example .env
```

Set one of:

- `GH_TOKEN`
- `GITHUB_TOKEN`
- `GITHUB_PERSONAL_ACCESS_TOKEN`

For official X API publishing, set `X_CLIENT_ID` first and then run `x_oauth2_pkce_setup.py` to populate `X_OAUTH2_ACCESS_TOKEN` and `X_OAUTH2_REFRESH_TOKEN`.

For Grok-based pre-publish evaluation, set:

- `GROK_API_KEY`
- `GROK_MODEL` (defaults to `grok-4.3`)

`.env` files are ignored by git. Do not commit real tokens.

## Git Hygiene

Tracked:

- `skills/github-repo-to-x-threads/`
- `.codex-plugin/plugin.json`
- `.claude-plugin/plugin.json`
- `commands/`
- root installer scripts
- `README.md`
- `AGENTS.md`
- `evals/`

Ignored:

- `.env`
- `.claude/` generated local adapters
- `.agents/` duplicate local adapters
- `repo-to-x-workspace/`
- cloned third-party repos
- generated images
- repo-specific claims ledgers and posting packs
- `.DS_Store`, `._*`, `__pycache__`

Before publishing changes:

```bash
git status --short --ignored
git diff --check
rg -n --hidden --glob '!.env' --glob '!.git/**' '(g[h]p_|g[h]o_|github_[p]at_|BEGIN [A-Z ]{0,30}PRIVATE KEY)' . || true
```
