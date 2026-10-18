# ai-knowledge

[AGENTS.md](AGENTS.md) と [執筆方針](docs/執筆方針.md) に従う。本文を作る前にwriting-discipline、自然さの確認にnatural-japanese、最終推敲にyomiyasuを使う。各スキルはプロジェクトに収録済み。

- `.claude/skills/`: Claude Code向けスキル入口。
- `.agents/skills/`: 3スキルの実体と実行スクリプト。
- `python3 scripts/editorial_check.py`: 機械で確認できる要件の検査。

スキルは文章の内容を検証しない。読者が答えを一目で得られるかを、人間視点で判定する。
