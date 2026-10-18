#!/usr/bin/env bash
set -euo pipefail

# Run at the repository root; installs project skills for supported agents.
cd "$(git rev-parse --show-toplevel)"

for name in writing-discipline natural-japanese yomiyasu; do
  rm -rf -- ".agents/skills/$name" ".claude/skills/$name" ".opencode/skills/$name"
done

# --copy avoids Git symlink checkout issues on Windows.
npx --yes skills@latest add rebuildup/writing-skills \
  --skill writing-discipline --skill natural-japanese \
  --agent codex --agent claude-code --agent opencode \
  --copy --yes

npx --yes skills@latest add nanaism/yomiyasu \
  --skill yomiyasu \
  --agent codex --agent claude-code --agent opencode \
  --copy --yes

for name in writing-discipline natural-japanese yomiyasu; do
  test -f ".agents/skills/$name/SKILL.md" || { echo "Missing Codex skill: $name" >&2; exit 1; }
  test -f ".claude/skills/$name/SKILL.md" || { echo "Missing Claude skill: $name" >&2; exit 1; }
  # OpenCode and Codex both use the shared .agents/skills/ project path.
done
test -f skills-lock.json || { echo 'skills-lock.json was not generated' >&2; exit 1; }

npx --yes skills@latest list -a codex -a claude-code -a opencode
