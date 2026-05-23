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
skill_src="$source_root/skills/$skill_name"

canonical_skill_dir="$bundle_root/skills/$skill_name"
claude_project_skill_dir="$bundle_root/.claude/skills/$skill_name"
codex_project_skill_dir="$bundle_root/.agents/skills/$skill_name"
claude_project_command_dir="$bundle_root/.claude/commands"
plugin_command_dir="$bundle_root/commands"

codex_user_skill_dir="${AGENTS_HOME:-$HOME/.agents}/skills/$skill_name"
codex_legacy_skill_dir="${CODEX_HOME:-$HOME/.codex}/skills/$skill_name"

if [[ ! -f "$skill_src/SKILL.md" ]]; then
  echo "Missing canonical skill: $skill_src/SKILL.md" >&2
  exit 1
fi

copy_skill() {
  local dest="$1"
  mkdir -p "$dest"
  COPYFILE_DISABLE=1 rsync -a --delete --delete-excluded \
    --exclude='.env' \
    --exclude='repo-to-x-workspace' \
    --exclude='repo-to-x-output' \
    --exclude='repo-to-x-runs' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.DS_Store' \
    --exclude='._*' \
    "$skill_src/" "$dest/"
}

mkdir -p \
  "$bundle_root/.codex-plugin" \
  "$bundle_root/.claude-plugin" \
  "$plugin_command_dir" \
  "$claude_project_command_dir"

copy_skill "$canonical_skill_dir"
copy_skill "$claude_project_skill_dir"
copy_skill "$codex_project_skill_dir"
copy_skill "$codex_user_skill_dir"
copy_skill "$codex_legacy_skill_dir"

cp "$source_root/.codex-plugin/plugin.json" "$bundle_root/.codex-plugin/plugin.json"
cp "$source_root/.claude-plugin/plugin.json" "$bundle_root/.claude-plugin/plugin.json"
cp "$source_root/commands/$skill_name.md" "$plugin_command_dir/$skill_name.md"
cp "$source_root/commands/$skill_name.md" "$claude_project_command_dir/$skill_name.md"
cp "$source_root/README.md" "$bundle_root/README.md"
[[ -f "$source_root/AGENTS.md" ]] && cp "$source_root/AGENTS.md" "$bundle_root/AGENTS.md"

rm -f "$bundle_root/$skill_name.skill"
rm -rf "$bundle_root/.claude/skills/$skill_name/.claude" "$bundle_root/.claude/skills/$skill_name/.claude-plugin"
rm -rf "$bundle_root/.agents/skills/$skill_name/.claude" "$bundle_root/.agents/skills/$skill_name/.claude-plugin"

find "$bundle_root" -maxdepth 8 -name '.DS_Store' -delete
find "$bundle_root" -maxdepth 8 -name '._*' -delete
find "$bundle_root" -maxdepth 10 -name '__pycache__' -type d -prune -exec rm -rf {} +
find "$codex_user_skill_dir" -maxdepth 8 -name '__pycache__' -type d -prune -exec rm -rf {} +
find "$codex_legacy_skill_dir" -maxdepth 8 -name '__pycache__' -type d -prune -exec rm -rf {} +

if command -v xattr >/dev/null 2>&1; then
  xattr -cr "$bundle_root" "$codex_user_skill_dir" "$codex_legacy_skill_dir" 2>/dev/null || true
  find "$bundle_root" -maxdepth 8 -name '._*' -delete
  find "$codex_user_skill_dir" -maxdepth 8 -name '._*' -delete
  find "$codex_legacy_skill_dir" -maxdepth 8 -name '._*' -delete
fi

echo "Installed canonical plugin skill: $canonical_skill_dir"
echo "Installed Codex plugin manifest: $bundle_root/.codex-plugin/plugin.json"
echo "Installed Claude plugin manifest: $bundle_root/.claude-plugin/plugin.json"
echo "Installed plugin command: $plugin_command_dir/$skill_name.md"
echo "Installed Claude project adapter: $claude_project_skill_dir"
echo "Installed Codex repo adapter: $codex_project_skill_dir"
echo "Installed Codex user skill: $codex_user_skill_dir"
echo "Installed Codex legacy user skill: $codex_legacy_skill_dir"
