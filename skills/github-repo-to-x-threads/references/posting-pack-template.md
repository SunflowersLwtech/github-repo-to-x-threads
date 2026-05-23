# Posting Pack

This file is generated per repo and should stay in the local ignored workspace unless the user explicitly chooses to publish it elsewhere.

## Evidence Summary

- Repo:
- Local source checked:
- Live metadata checked:
- Caveats:

## Posting Strategy

Write the strategy here.

## Publish Mode

- Default: `manual-safe`
- Optional after explicit approval and official X API OAuth2 setup: `official-api-publish`

## Ready To Post

```text
(1/N)

```

## Posting Map

- Thread count is adaptive. Use `N` only after the final draft is reviewed; do not force exactly 8 posts.
- Post 1: attach image 1 by default unless the user explicitly opted out of images
  - Alt text:
  - Disclosure:
  - Registry id: `image-1`
  - Registry status: `planned`

## Length Audit

- 1/N: `OK`

Allowed states:

- `OK`: publishable as-is.
- `Tight`: do not add more text.
- `Split`: split before posting.

## Images

| Image | Post | Purpose | Path | Alt Text | Disclosure |
| --- | --- | --- | --- | --- | --- |
| image-1 | 1/N | hook visual |  |  | Generated conceptual visual, not an official project screenshot. |

Image governance:

- Actual generated images are required by default for ready-to-post packs unless the user explicitly requested text-only, no images, prompts-only, or manual images.
- Register generated image files with `scripts/register_image_asset.py`.
- Keep image files under `images/`, not in chat-only output or random temp folders.
- Do not mark this pack ready while a referenced image is missing from `images_manifest.json`.
- Do not mark this pack ready while images are only `planned` or `prompt_only`, unless prompt-only was an explicit user choice or the image tool is unavailable.
- Actual image files need `sha256`, `mime_type`, alt text, disclosure, and review status.
- Run `scripts/check_image_assets.py <repo-run-dir>` before presenting this as ready.

## Pre-Flight

- Repo owner credited.
- Personal vision labeled as personal.
- No unsupported "best/first/only" claim.
- Images are conceptual or attributed.
- Every attached image is registered in `images_manifest.json`.
- Actual image gate passed, unless prompt-only/manual images were explicitly chosen.
- Link works.
- Cross-check review status is `pass`.
- For `official-api-publish`: user explicitly approved `--live`.
- For `official-api-publish`: `.env` has OAuth2 user token credentials, not only `X_BEARER_TOKEN`.

## Do Not Say

-
