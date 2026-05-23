# Run Workspace Contract

Generated artifacts are governed under one local workspace:

```text
repo-to-x-workspace/
  runs/
    <run-id>/
      run_manifest.json
      SUMMARY.md
      repos/
        <repo-id>/
          repo_context.json
          file_manifest.txt
          claims_ledger.json
          cross_check_review.md
          posting_pack.md
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
