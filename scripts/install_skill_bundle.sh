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
project_skill_dir="$bundle_root/.claude/skills/$skill_name"
project_command_dir="$bundle_root/.claude/commands"
plugin_command_dir="$bundle_root/commands"

mkdir -p "$project_command_dir" "$plugin_command_dir" "$bundle_root/.claude-plugin"

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
  "$source_root/" "$project_skill_dir/"

rm -rf "$project_skill_dir/.claude" "$project_skill_dir/.claude-plugin" "$project_skill_dir/commands"
rm -rf "$bundle_root/skills"

cp "$source_root/.claude/commands/$skill_name.md" "$project_command_dir/$skill_name.md"
cp "$source_root/commands/$skill_name.md" "$plugin_command_dir/$skill_name.md"
cp "$source_root/.claude-plugin/plugin.json" "$bundle_root/.claude-plugin/plugin.json"
rm -f "$bundle_root/$skill_name.skill"

find "$bundle_root" -maxdepth 5 -name '.DS_Store' -delete
find "$bundle_root" -maxdepth 5 -name '._*' -delete

if command -v xattr >/dev/null 2>&1; then
  xattr -cr "$bundle_root/.claude" "$bundle_root/commands" "$bundle_root/.claude-plugin" 2>/dev/null || true
  find "$bundle_root" -maxdepth 5 -name '._*' -delete
fi

echo "Installed project skill: $project_skill_dir"
echo "Installed project command: $project_command_dir/$skill_name.md"
echo "Installed plugin command: $plugin_command_dir/$skill_name.md"
echo "Installed plugin manifest: $bundle_root/.claude-plugin/plugin.json"
