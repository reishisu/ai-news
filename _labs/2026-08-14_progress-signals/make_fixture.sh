#!/usr/bin/env bash
# make_fixture.sh — 検証用リポジトリを作る(日時は全部固定)
# 統合済み枝 8本: 着手 s / 最終コミット e / 統合 m (単位=時間)
#   サイクルタイム = m-s, レビュー待ち = m-e
# 未統合の枝 3本: hot(静止1h) / warm(静止40h) / cold(静止120h)
set -eu
DIR="${1:?usage: make_fixture.sh <dir>}"
rm -rf "$DIR"; mkdir -p "$DIR"; cd "$DIR"
git init -q -b main .
git config user.email dev@example.com
git config user.name  dev

BASE=$(date -u -d '2026-08-01T00:00:00Z' +%s)

c() {  # c <時間オフセット> <名前> <メッセージ>
  local t=$((BASE + $1*3600))
  local d; d=$(date -u -d "@$t" +'%Y-%m-%dT%H:%M:%S+0000')
  GIT_AUTHOR_DATE="$d" GIT_COMMITTER_DATE="$d" \
  GIT_AUTHOR_NAME="$2" GIT_COMMITTER_NAME="$2" \
    git commit -q --allow-empty -m "$3"
}
m() {  # m <時間オフセット> <枝>
  local t=$((BASE + $1*3600))
  local d; d=$(date -u -d "@$t" +'%Y-%m-%dT%H:%M:%S+0000')
  GIT_AUTHOR_DATE="$d" GIT_COMMITTER_DATE="$d" \
  GIT_AUTHOR_NAME=lead GIT_COMMITTER_NAME=lead \
    git merge -q --no-ff "$2" -m "Merge $2"
}

c 0 lead "init"

# "s e m 担当"  → cycle=m-s / review=m-e
SPECS="1,2,3,aoi 4,7,8,aoi 9,13,15,ken 16,22,25,ken
       26,34,38,mio 39,53,59,mio 60,80,90,aoi 91,121,139,ken"
i=0
for spec in $SPECS; do
  i=$((i+1))
  IFS=, read -r s e mm who <<EOF
$spec
EOF
  git checkout -q -b "feat-$i" main
  c "$s" "$who" "feat-$i start"
  c "$e" "$who" "feat-$i done"
  git checkout -q main
  m "$mm" "feat-$i"
  git branch -q -d "feat-$i"
done

# 幹はその後も動く
c 150 lead "trunk work a"
c 180 lead "trunk work b"
c 210 lead "trunk work c"

# 未統合の枝(now=2026-08-10T00:00Z = 216h 時点で判定する)
git checkout -q -b hot   main;   c 214 aoi "hot wip";  c 215 aoi "hot wip2"
git checkout -q -b warm  main;   c 170 mio "warm wip"; c 176 mio "warm wip2"
git checkout -q -b cold  main~3; c 90  ken "cold wip"; c 96 ken "cold wip2"
git checkout -q main
echo "fixture ready: $DIR"
