#!/bin/bash
# 2つのプロジェクトを作る。中身の違いは SKILL.md の description 1行だけ。
set -e
BASE="${1:-/home/user/skilllab}"
rm -rf "$BASE"; mkdir -p "$BASE"

body() {
cat <<'MD'

リリース前に、次の3つをこの順で確認する。

1. `git status` が空であること
2. テストが全部通ること
3. バージョン番号を上げたこと

確認した内容を箇条書きで答える。
MD
}

# A: よくある書き方(何をするかだけ)
mkdir -p "$BASE/A/.claude/skills/release-check"
{ echo '---'
  echo 'description: リリースのメモ'
  echo '---'
  body; } > "$BASE/A/.claude/skills/release-check/SKILL.md"

# B: いつ使うかを書いた版
mkdir -p "$BASE/B/.claude/skills/release-check"
{ echo '---'
  echo 'description: リリース前の確認手順を返す。ユーザーがリリース前に何を確認するか、デプロイしてよいか、公開前のチェックについて尋ねたときに使う。'
  echo '---'
  body; } > "$BASE/B/.claude/skills/release-check/SKILL.md"

for d in A B; do (cd "$BASE/$d" && git init -q && git add -A && git -c user.email=a@b -c user.name=c commit -qm init); done
echo "作成: $BASE/A と $BASE/B"
