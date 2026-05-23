# github-repo-to-x-threads

Agent Skills plugin for turning GitHub repositories into responsible X/Twitter thread posting packs.

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

Coding agents should treat `AGENTS.md` plus `skills/github-repo-to-x-threads/SKILL.md` as the source of truth, keep generated runs/images/env files out of git, and use `scripts/install_skill_bundle.sh /Volumes/T7/AI_Dev/X` only to sync local install surfaces.

## What It Does

Given one or more GitHub repos, owner/repo strings, or local paths, the skill guides an agent to:

1. clone or read the repo locally,
2. cross-check repo files against live GitHub metadata,
3. separate verified facts, reasonable inference, and user vision,
4. draft a paste-ready X thread with attribution and caveats,
5. create a final-mile posting pack with image placement and alt text,
6. govern GPT Image 2-style assets through a local image registry.

## Install For Local Use

The helper installs the canonical skill plus local adapters without committing generated outputs:

```bash
scripts/install_skill_bundle.sh /Volumes/T7/AI_Dev/X
```

It writes:

```text
/Volumes/T7/AI_Dev/X/
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

## Image Governance

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

## Local Env

Create a local `.env` when you want live GitHub metadata through `gh`:

```bash
cp skills/github-repo-to-x-threads/.env.example .env
```

Set one of:

- `GH_TOKEN`
- `GITHUB_TOKEN`
- `GITHUB_PERSONAL_ACCESS_TOKEN`

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
