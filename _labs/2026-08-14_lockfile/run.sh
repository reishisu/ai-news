#!/bin/bash
# 依存の固定 — 実証スクリプト一式
# 使い方: bash run.sh   (このファイルがあるディレクトリで実行)
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="$HERE/work"
rm -rf "$WORK"; mkdir -p "$WORK"

# npm 12 を手元に用意する(環境の npm は 10 系)
if [ ! -x "$HERE/tools/node_modules/npm/bin/npm-cli.js" ]; then
  mkdir -p "$HERE/tools"
  (cd "$HERE/tools" && npm install npm@12.0.2 --prefix . --no-audit --no-fund >/dev/null 2>&1)
fi
NPM12="node $HERE/tools/node_modules/npm/bin/npm-cli.js"

PKG='{
  "name": "lockdemo",
  "version": "1.0.0",
  "private": true,
  "dependencies": { "chalk": "^4.0.0" }
}'

hr() { echo; echo "########## $1"; }

# ---------- 1. lock 無し: 同じ package.json から別の木が生える ----------
hr "1 lock 無し / install する時期で変わる"
mkdir -p "$WORK/e1"; cd "$WORK/e1"
echo "$PKG" > package.json; cp "$HERE/tree.sh" .
npm install --before=2020-05-01 --no-audit --no-fund >/dev/null 2>&1
echo "== A: 2020-05-01 時点 =="; bash tree.sh
rm -rf node_modules package-lock.json
npm install --no-audit --no-fund >/dev/null 2>&1
echo "== B: 今日 =="; bash tree.sh

# ---------- 2. lock 有り: 何年経っても同じ ----------
hr "2 lock 有り / 2020 の lock を今日 ci"
mkdir -p "$WORK/e2"; cd "$WORK/e2"
echo "$PKG" > package.json; cp "$HERE/tree.sh" .
npm install --before=2020-05-01 --no-audit --no-fund >/dev/null 2>&1
rm -rf node_modules
npm ci --no-audit --no-fund >/dev/null 2>&1
bash tree.sh

# ---------- 3. lock が無いと npm ci は動かない ----------
hr "3 lock 無しで npm ci (npm10 と npm12 の文面差)"
mkdir -p "$WORK/e3"; cd "$WORK/e3"; echo "$PKG" > package.json
echo "-- npm 10 --"; npm ci 2>&1 | head -5 | fold -s -w 38
echo "-- npm 12 --"; $NPM12 ci 2>&1 | head -5 | fold -s -w 38

# ---------- 4. package.json だけ動かす ----------
hr "4 範囲を ^4 -> ^5 に変更して npm ci"
cp -r "$WORK/e2" "$WORK/e4"; cd "$WORK/e4"
node -e 'const f=require("fs");const p=JSON.parse(f.readFileSync("package.json"));
p.dependencies.chalk="^5.0.0";f.writeFileSync("package.json",JSON.stringify(p,null,2))'
npm ci --no-audit --no-fund 2>&1 | grep -E 'code EUSAGE|in sync|Invalid:' \
  | fold -s -w 38
echo "落ちた後も node_modules は残る:"
node -p "require('./node_modules/chalk/package.json').version"

# ---------- 5. 依存を足しただけ ----------
hr "5 依存を1つ足して npm ci"
cp -r "$WORK/e2" "$WORK/e5"; cd "$WORK/e5"
node -e 'const f=require("fs");const p=JSON.parse(f.readFileSync("package.json"));
p.dependencies.ms="^2.1.3";f.writeFileSync("package.json",JSON.stringify(p,null,2))'
npm ci --no-audit --no-fund 2>&1 | grep -E 'Missing:' | fold -s -w 38

# ---------- 6. npm install も lock を読む ----------
hr "6 範囲を満たす限り npm install も lock に従う"
cp -r "$WORK/e2" "$WORK/e6"; cd "$WORK/e6"
rm -rf node_modules; cp package-lock.json /tmp/lock-before.json
npm install --no-audit --no-fund >/dev/null 2>&1
bash tree.sh
diff -q /tmp/lock-before.json package-lock.json >/dev/null \
  && echo "package-lock.json は変化なし" || echo "package-lock.json が変化した"

# ---------- 7. 取得元は固定されない / 中身は固定される ----------
hr "7 registry を差し替える"
if curl -s --noproxy '*' --max-time 2 -o /dev/null http://127.0.0.1:8871/; then
  echo "ポート 8871 が既に使われています。止めてから実行してください"; exit 1
fi
cp -r "$WORK/e2" "$WORK/e7"; cd "$WORK/e7"; rm -rf node_modules
cp "$HERE/mirror-server.js" .
node -e 'const l=require("./package-lock.json");const {execSync}=require("child_process");
const fs=require("fs"),path=require("path");
for (const v of Object.values(l.packages)) { if(!v.resolved) continue;
  const dest="mirror"+new URL(v.resolved).pathname;
  fs.mkdirSync(path.dirname(dest),{recursive:true});
  execSync(`curl -sSL -o ${dest} ${v.resolved}`); }'
node mirror-server.js >/dev/null 2>&1 &
MIRROR_PID=$!
sleep 1
curl -s --noproxy '*' --max-time 3 -o /dev/null \
  http://127.0.0.1:8871/chalk/-/chalk-4.0.0.tgz \
  || { echo "ミラーが起動していません"; exit 1; }
echo "registry=http://127.0.0.1:8871/" > .npmrc
rm -f access.log
NO_PROXY='*' no_proxy='*' npm ci --no-audit --no-fund --cache "$(mktemp -d)" 2>&1 | fold -s -w 38
echo "-- lock に書いてある取得元 --"
node -e 'console.log(require("./package-lock.json").packages["node_modules/chalk"].resolved)' | fold -w 38
echo "-- 実際に取りに来た先 --"; sort -u access.log | fold -w 38

hr "8 中身をすり替えると落ちる"
mkdir -p /tmp/evil/package/source
echo '{ "name":"chalk","version":"4.0.0","main":"source/index.js" }' > /tmp/evil/package/package.json
echo "module.exports=require('child_process').execSync;" > /tmp/evil/package/source/index.js
tar czf mirror/chalk/-/chalk-4.0.0.tgz -C /tmp/evil package
rm -rf node_modules
NO_PROXY='*' no_proxy='*' npm ci --no-audit --no-fund --cache "$(mktemp -d)" 2>&1 \
  | grep -E 'code EINTEGRITY|but got' | fold -s -w 38
kill $MIRROR_PID 2>/dev/null

# ---------- 9. lock は「スクリプトを走らせるか」を固定しない ----------
hr "9 postinstall: npm10 は走る / npm12 は止まる"
mkdir -p "$WORK/e9/hello-dep"; cd "$WORK/e9"
cat > hello-dep/package.json <<'EOF'
{
  "name": "hello-dep",
  "version": "1.0.0",
  "scripts": {
    "postinstall": "node -e \"require('fs').writeFileSync(process.env.INIT_CWD+'/ran.txt','ran')\""
  }
}
EOF
(cd hello-dep && npm pack --pack-destination .. >/dev/null 2>&1)
cat > package.json <<'EOF'
{
  "name": "scriptdemo",
  "version": "1.0.0",
  "private": true,
  "dependencies": { "hello-dep": "file:./hello-dep-1.0.0.tgz" }
}
EOF
rm -rf hello-dep
npm install --no-audit --no-fund >/dev/null 2>&1
echo "-- lock のエントリ --"
node -e 'const l=require("./package-lock.json");
const e=l.packages["node_modules/hello-dep"];
console.log("hasInstallScript:", e.hasInstallScript)'
echo "-- npm 10 で ci --"; rm -rf node_modules ran.txt
npm ci --no-audit --no-fund >/dev/null 2>&1
[ -f ran.txt ] && echo "ran.txt: できた" || echo "ran.txt: できない"
echo "-- npm 12 で ci (同じ lock) --"; rm -rf node_modules ran.txt
$NPM12 ci --no-audit --no-fund 2>&1 | grep 'install-scripts' | head -2 | fold -s -w 38
[ -f ran.txt ] && echo "ran.txt: できた" || echo "ran.txt: できない"

# ---------- 10. tarball URL 依存 ----------
hr "10 tarball URL 依存 npm10 と npm12"
mkdir -p "$WORK/e10"; cd "$WORK/e10"
cat > package.json <<'EOF'
{
  "name": "remotedemo",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "chalk": "https://registry.npmjs.org/chalk/-/chalk-4.0.0.tgz"
  }
}
EOF
echo "-- npm 10 --"; npm install --no-audit --no-fund 2>&1 | fold -s -w 38
rm -rf node_modules package-lock.json
echo "-- npm 12 --"; $NPM12 install --no-audit --no-fund 2>&1 | grep '^npm error' | head -3 | fold -s -w 38

# ---------- 11. lock はフラグを覚えていない ----------
hr "11 --legacy-peer-deps で作った lock"
mkdir -p "$WORK/e11/src/libx" "$WORK/e11/src/plugin"; cd "$WORK/e11"
echo '{ "name": "libx", "version": "2.0.0" }' > src/libx/package.json
echo '{ "name": "plugin", "version": "1.0.0", "peerDependencies": { "libx": "^1.0.0" } }' > src/plugin/package.json
(cd src/libx && npm pack --pack-destination ../.. >/dev/null 2>&1)
(cd src/plugin && npm pack --pack-destination ../.. >/dev/null 2>&1)
cat > package.json <<'EOF'
{
  "name": "peerdemo",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "libx": "file:./libx-2.0.0.tgz",
    "plugin": "file:./plugin-1.0.0.tgz"
  }
}
EOF
echo "-- 素の install --"; npm install --no-audit --no-fund 2>&1 | grep '^npm error code' | fold -s -w 38
echo "-- --legacy-peer-deps 付き --"; npm install --legacy-peer-deps --no-audit --no-fund 2>&1 | fold -s -w 38
echo "-- その lock でフラグ無し ci --"; rm -rf node_modules
npm ci --no-audit --no-fund 2>&1 | grep '^npm error' | head -2 | fold -s -w 38
echo "-- 同じフラグを付けた ci --"; rm -rf node_modules
npm ci --legacy-peer-deps --no-audit --no-fund 2>&1 | grep -v '^npm warn' | fold -s -w 38


# ---------- 12. npm12 の許可は package.json に、しかもバージョン付きで残る ----------
hr "12 npm12 install-scripts approve"
mkdir -p "$WORK/e12"; cd "$WORK/e12"
echo '{"name":"esb","version":"1.0.0","private":true,
"dependencies":{"esbuild":"0.21.5"}}' > package.json
$NPM12 install --no-audit --no-fund 2>&1 | grep 'install-scripts   ' | fold -s -w 38
echo "-- approve --"
$NPM12 install-scripts approve esbuild 2>&1 | fold -s -w 38
echo "-- 許可は package.json に書かれる --"
node -e 'console.log(JSON.stringify(require("./package.json").allowScripts))' | fold -w 38
echo "-- lock 側に allowScripts はあるか --"
node -e 'const l=require("./package-lock.json");
console.log("lock:", "allowScripts" in l.packages[""])'
echo "-- 0.23.0 に上げると再びブロックされる --"
node -e 'const f=require("fs");const p=JSON.parse(f.readFileSync("package.json"));
p.dependencies.esbuild="0.23.0";f.writeFileSync("package.json",JSON.stringify(p,null,2))'
rm -rf node_modules package-lock.json
$NPM12 install --no-audit --no-fund 2>&1 | grep 'install-scripts   ' | fold -s -w 38


# ---------- 13. npm-shrinkwrap.json は npm12 で無視される ----------
hr "13 npm-shrinkwrap.json のみを置く"
cp -r "$WORK/e2" "$WORK/e13"; cd "$WORK/e13"
rm -rf node_modules; mv package-lock.json npm-shrinkwrap.json
echo "-- npm 10 で ci --"
npm ci --no-audit --no-fund 2>&1 | fold -s -w 38
node -p "'chalk ' + require('./node_modules/chalk/package.json').version"
echo "-- npm 12 で ci --"; rm -rf node_modules
$NPM12 ci --no-audit --no-fund 2>&1 | grep -E 'code EUSAGE|can only install' \
  | fold -s -w 38
echo "-- npm 12 で install --"; rm -rf node_modules
$NPM12 install --no-audit --no-fund 2>&1 | fold -s -w 38
bash tree.sh
echo "-- 置かれたファイル --"; ls *.json

hr "versions"
echo "node $(node -v)"
echo "npm  $(npm -v)"
echo "npm12 $($NPM12 -v)"
