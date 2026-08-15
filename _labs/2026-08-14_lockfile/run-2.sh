#!/usr/bin/env bash
# 追試(記事の3章・4章の一般化を検証しなおすためのもの)
#   14. lock の resolved が registry.npmjs.org 以外のとき、
#       設定した registry ではなく lock の URL へ取りに行く
#   15. peer 衝突のエラー文面は、フィクスチャの名前で変わる
# 使い方: bash run-2.sh
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="$HERE/work2"
rm -rf "$WORK"; mkdir -p "$WORK"

export NO_PROXY=127.0.0.1,localhost
export no_proxy=127.0.0.1,localhost
export npm_config_audit=false
export npm_config_fund=false
export npm_config_progress=false
export npm_config_update_notifier=false

W=38
short() { fold -s -w $W; }
hr() { echo; echo "########## $1"; }

# 私設レジストリ2台。A=lock を作った側 / B=あとで設定する側
rm -f "$HERE/reg/A.log" "$HERE/reg/B.log"
PORT=8871 LOG=A.log node "$HERE/reg/registry.js" &
A=$!
PORT=8872 LOG=B.log node "$HERE/reg/registry.js" &
B=$!
sleep 1
trap 'kill $A $B 2>/dev/null' EXIT

# ---------- 14 ----------
hr "14 resolved が別ホストのときの npm ci"
mkdir -p "$WORK/e14"; cd "$WORK/e14"
printf '{"name":"app","version":"1.0.0","dependencies":{"demo-lib":"1.0.0"}}\n' > package.json
export npm_config_cache="$WORK/cache14"
npm_config_registry=http://127.0.0.1:8871/ npm install >/dev/null 2>&1
echo "-- lock の resolved --"
node -e 'console.log(require("./package-lock.json").packages["node_modules/demo-lib"].resolved)' | short
rm -rf node_modules "$WORK/cache14"
: > "$HERE/reg/A.log"; : > "$HERE/reg/B.log"
echo "-- registry を 8872 にして npm ci --"
npm_config_registry=http://127.0.0.1:8872/ npm ci 2>&1 | tail -2 | short
echo "8871(lockのURL) への取得: $(grep -c 'demo-lib.*tgz' "$HERE/reg/A.log")"
echo "8872(設定した先) への取得: $(grep -c 'demo-lib.*tgz' "$HERE/reg/B.log")"

# ---------- 15 ----------
hr "15 peer 衝突: フラグ無し ci のエラー文面"
# 15a: 私設レジストリの demo-peer(peerDeps: demo-lib@^1.0.0)
mkdir -p "$WORK/e15a"; cd "$WORK/e15a"
printf '{"name":"app","version":"1.0.0","dependencies":{"demo-peer":"^1.0.0","demo-lib":"^2.0.0"}}\n' > package.json
export npm_config_cache="$WORK/cache15a"
export npm_config_registry=http://127.0.0.1:8871/
npm install --legacy-peer-deps >/dev/null 2>&1
rm -rf node_modules
echo "-- 15a 私設レジストリ(demo-peer) --"
npm ci 2>&1 | grep -v '^npm error$' | grep -m6 'code \|Fix the\|this command\|Conflicting\|peer ' | short
unset npm_config_registry

# 15b: 公開レジストリに存在しない名前
mkdir -p "$WORK/e15b"; cd "$WORK/e15b"
export npm_config_cache="$WORK/cache15b"
mkdir -p zzq-notreal-peer
cat > zzq-notreal-peer/package.json <<'EOF'
{"name":"zzq-notreal-peer","version":"1.0.0",
 "peerDependencies":{"zzq-notreal-base":"^1.0.0"}}
EOF
printf '{"name":"app","version":"1.0.0","dependencies":{"zzq-notreal-peer":"file:zzq-notreal-peer","zzq-notreal-base":"^2.0.0"}}\n' > package.json
npm install --legacy-peer-deps >/dev/null 2>&1
rm -rf node_modules
echo "-- 15b 公開レジストリに無い名前 --"
npm ci 2>&1 | grep -m3 'code \|404 ' | short

echo
echo "########## versions"
echo "npm  $(npm -v)"
echo "node $(node -v)"
