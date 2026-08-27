#!/usr/bin/env bash
# 実験4: 同じ名前のスキルが「プロジェクト側」と「プラグイン側」の両方にあるとき、
#        素の /名前 はどちらを呼ぶのか。
# 引数1: 作業ディレクトリ  引数2: CLAUDE_CONFIG_DIR（プラグイン導入済みのもの）
set -eu
DIR="${1:?作業ディレクトリを渡してください}"
rm -rf "$DIR"; mkdir -p "$DIR/.claude/skills/grill-me"; cd "$DIR"; git init -q

# プラグイン側にも grill-me がある状態で、同名をプロジェクトに置く。
# 本文は一言返すだけにして、どちらが動いたか一目で分かるようにする。
cat > .claude/skills/grill-me/SKILL.md <<'EOF'
---
description: プロジェクト側の同名スキル。衝突の実験用。
---

一言だけ返す: LOCAL-WINS
EOF
