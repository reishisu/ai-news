#!/usr/bin/env bash
# 経路A: Claude Code のプラグインとして入れる。
# CLAUDE_CONFIG_DIR を渡すと、本番の ~/.claude を汚さずに試せる。
set -eu
export CLAUDE_CONFIG_DIR="${1:-$HOME/.claude}"
mkdir -p "$CLAUDE_CONFIG_DIR"

echo "--- 1. 公式マーケットプレイスを登録 ---"
# 対話で1度も起動していない環境では自動登録されない。
# 登録済みなら「already」と出るだけで害はない。
claude plugin marketplace add anthropics/claude-plugins-official

echo "--- 2. プラグインを入れる ---"
claude plugin install mattpocock-skills

echo "--- 3. 入ったか確認 ---"
claude plugin list
claude plugin details mattpocock-skills
