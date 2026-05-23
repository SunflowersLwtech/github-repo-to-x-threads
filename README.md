# github-repo-to-x-threads

Codex/Claude-style skill for turning a GitHub repository into responsible X threads.

It is designed for the workflow where the user drops a GitHub repo into a session and expects the agent to:

1. clone or read the repo locally,
2. cross-check repo files against live GitHub metadata,
3. separate verified facts from inference and the user's personal vision,
4. draft a paste-ready X thread,
5. prepare or generate conceptual GPT Image 2 / image-generation-style visuals with clear disclosure.

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
