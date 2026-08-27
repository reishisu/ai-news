#!/usr/bin/env bash
# 経路B: skills CLI で、必要なスキルだけプロジェクトにコピーする。
# 第1引数にプロジェクトのパスを渡す。
set -eu
cd "${1:?プロジェクトのパスを渡してください}"

# grill-me は本文が「grilling を呼べ」の1行しかない。
# grilling を一緒に入れないと Unknown skill: grilling で止まる。
npx -y skills@latest add mattpocock/skills \
  --skill grill-me grilling \
  --agent claude-code -y

# grill-with-docs を使うなら domain-modeling も要る:
# npx -y skills@latest add mattpocock/skills \
#   --skill grill-with-docs grilling domain-modeling \
#   --agent claude-code -y

find .claude/skills -name SKILL.md | sort
