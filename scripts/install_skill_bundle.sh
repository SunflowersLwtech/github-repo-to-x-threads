#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <bundle-root>" >&2
  echo "Example: $0 /Volumes/T7/AI_Dev/X" >&2
  exit 2
fi

bundle_root="${1%/}"
skill_name="github-repo-to-x-threads"
source_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
target_dir="$bundle_root/skills/$skill_name"

mkdir -p "$bundle_root/skills"

COPYFILE_DISABLE=1 rsync -a --delete \
  --exclude='.env' \
  --exclude='.git' \
  --exclude='*.skill' \
  --exclude='evals' \
  --exclude='repo-to-x-workspace' \
  --exclude='repo-to-x-output' \
  --exclude='repo-to-x-runs' \
  --exclude='.DS_Store' \
  --exclude='._*' \
  "$source_root/" "$target_dir/"

if [[ -f "$source_root/$skill_name.skill" ]]; then
  cp "$source_root/$skill_name.skill" "$bundle_root/$skill_name.skill"
fi

find "$bundle_root" -maxdepth 5 -name '.DS_Store' -delete
find "$bundle_root" -maxdepth 5 -name '._*' -delete

if command -v xattr >/dev/null 2>&1; then
  xattr -cr "$target_dir" 2>/dev/null || true
  find "$bundle_root" -maxdepth 5 -name '._*' -delete
fi

echo "Installed skill folder: $target_dir"
if [[ -f "$bundle_root/$skill_name.skill" ]]; then
  echo "Installed package: $bundle_root/$skill_name.skill"
fi
