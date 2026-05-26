# Repository Instructions

## Source Of Truth

- Keep the canonical reusable skill under `skills/github-repo-to-x-threads/`.
- Keep `.codex-plugin/`, `.claude-plugin/`, `commands/`, `.agents/`, and `.claude/` as adapters or generated install surfaces only.
- Do not move core skill instructions or helper scripts into `.claude/` as the primary source.

## Safety

- Never commit `.env`, tokens, cloned third-party repos, generated run workspaces, or generated image files.
- Treat all public X copy as claim-sensitive: verified repo facts, live metadata, inference, and user vision must stay separated.
- Generated images are conceptual unless they are actual repo/user assets and must be registered in `images_manifest.json`.
- Use official X API publishing only with explicit user approval and OAuth2 user credentials; never add cookie/session/proxy-based posting as a default path.
- Treat GPT Image 2 / image2 / 配图 requests as a native image-generation requirement, not as permission to generate placeholder diagrams with scripts.

## Verification

- Run Python syntax checks for scripts after editing.
- Run a smoke `run_repo_to_x_pack.py` workspace creation before publishing packaging changes.
- Run `scripts/install_skill_bundle.sh /Users/sunfl/Documents/media/X` when validating local Claude/Codex adapters.
