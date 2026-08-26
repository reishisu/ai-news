#!/bin/bash
# 実験3: 良い description のまま disable-model-invocation を足すと自動起動は止まるか。
set -e
BASE="${1:-/home/user/skilllab3}"
rm -rf "$BASE"; mkdir -p "$BASE"
DESC='description: リリース前の確認手順を返す。ユーザーがリリース前に何を確認するか、デプロイしてよいか、公開前のチェックについて尋ねたときに使う。'

body() {
cat <<'MD'

リリース前に、次の3つをこの順で確認する。

1. `git status` が空であること
2. テストが全部通ること
3. バージョン番号を上げたこと

確認した内容を箇条書きで答える。
MD
}

mkdir -p "$BASE/A/.claude/skills/memo-1"
{ echo '---'; echo "$DESC"; echo '---'; body; } \
  > "$BASE/A/.claude/skills/memo-1/SKILL.md"

mkdir -p "$BASE/B/.claude/skills/memo-1"
{ echo '---'; echo "$DESC"
  echo 'disable-model-invocation: true'
  echo '---'; body; } > "$BASE/B/.claude/skills/memo-1/SKILL.md"

for d in A B; do (cd "$BASE/$d" && git init -q && git add -A && git -c user.email=a@b -c user.name=c commit -qm init); done
echo "作成: $BASE/A と $BASE/B"
