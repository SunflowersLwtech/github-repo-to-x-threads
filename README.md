# github-repo-to-x-threads

Codex/Claude-style skill for turning a GitHub repository into responsible X threads.

It is designed for the workflow where the user drops a GitHub repo into a session and expects the agent to:

1. clone or read the repo locally,
2. cross-check repo files against live GitHub metadata,
3. separate verified facts from inference and the user's personal vision,
4. draft a paste-ready X thread with a final-mile posting map,
5. prepare or generate conceptual GPT Image 2 / image-generation-style visuals with alt text and clear disclosure.

## Install

Copy this folder into your skills directory:

```bash
mkdir -p ~/.codex/skills/github-repo-to-x-threads
cp -R . ~/.codex/skills/github-repo-to-x-threads
```

## Helper

The bundled helper collects a first-pass repo context:

```bash
python scripts/collect_repo_context.py https://github.com/owner/repo --out /tmp/repo-to-x-context --refresh
```

Outputs:

- `/tmp/repo-to-x-context/repo_context.json`
- `/tmp/repo-to-x-context/file_manifest.txt`
- `/tmp/repo-to-x-context/repo/` for cloned remote repos

The helper is only a starting point. The skill still instructs the agent to read key files before making public claims.

## Governed Multi-Repo Runs

Use the run-pack script when you want one governed workspace for one or more repos:

```bash
python scripts/run_repo_to_x_pack.py https://github.com/owner/repo owner2/repo2 --refresh
```

Or use a source list:

```bash
python scripts/run_repo_to_x_pack.py --source-file repos.txt --refresh
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

## Output Bias

The skill is tuned for practical publishing. A good run should end with:

- a clean `Ready To Post` block,
- image placement for each selected post,
- alt text and disclosure text,
- a rough length audit,
- a short pre-flight checklist,
- generated images when image generation is available and requested.

## Local Env

Create `.env` from `.env.example` when you want live GitHub metadata through `gh`:

```bash
cp .env.example .env
```

Set one of:

- `GH_TOKEN`
- `GITHUB_TOKEN`
- `GITHUB_PERSONAL_ACCESS_TOKEN`

`.env` files are ignored by git. Do not commit real tokens.

## Git Hygiene

Tracked:

- `SKILL.md`
- `README.md`
- `scripts/`
- `references/`
- `evals/`
- `.env.example`

Ignored:

- `.env`
- `repo-to-x-workspace/`
- generated run outputs
- cloned third-party repos
- generated images
- repo-specific claims ledgers and posting packs

## Clean External-Disk Sync

For a loadable skill bundle on an external disk, install into a `skills/` folder:

```bash
scripts/install_skill_bundle.sh /Volumes/T7/AI_Dev/X
```

Expected layout:

```text
/Volumes/T7/AI_Dev/X/
  skills/
    github-repo-to-x-threads/
      SKILL.md
      scripts/
      references/
  github-repo-to-x-threads.skill
```

This matches the bundled skill layout used by OpenAI/Anthropic-style plugin folders: `<bundle-root>/skills/<skill-name>/SKILL.md`.

For a plain folder backup, use:

```bash
scripts/sync_clean_external.sh . /Volumes/T7/AI_Dev/X/backups/github-repo-to-x-threads
```

Both helpers set `COPYFILE_DISABLE=1`, exclude `.DS_Store` and `._*`, then clean any AppleDouble files produced during the sync.
