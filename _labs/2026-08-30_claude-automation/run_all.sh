#!/usr/bin/env bash
# Claude Code を無人で走らせたときに何が起きるかを実測する。
# 使い方: bash run_all.sh 2>&1 | tee output.txt
# 端末幅は記事の規約(幅380px)に合わせて40桁に固定する。
export COLUMNS=40
W=/tmp/cc-auto-lab
rm -rf $W && mkdir -p $W
cd $W

j() { python3 -c "
import json,sys
d=json.load(open(sys.argv[1]))
for k in sys.argv[2:]:
    v=d.get(k)
    if k=='permission_denials':
        v=[x['tool_name'] for x in v]
    if k=='total_cost_usd' and v is not None:
        v=round(v,4)
    print('%-14s %s'%(k,str(v)[:24]))
" "$@"; }

echo "===== 段1 環境 ====="
claude --version
python3 -c "import platform;print('OS      ',platform.platform()[:34])"
date -u '+UTC     %Y-%m-%d %H:%M'

echo
echo "===== 段2 素の -p は動く ====="
mkdir -p s2 && cd s2
claude -p "1+1は？数字だけ" ; echo "exit=$?"
cd $W

echo
echo "===== 段3 権限が要る仕事 ====="
mkdir -p s3 && cd s3
claude -p "hello.txt を作り中身を hi に" > o.txt 2>/dev/null
echo "exit=$?"
echo "--- 応答 ---"
python3 -c "
print(open('o.txt',encoding='utf-8').read().strip()[:19])"
echo "--- 出来たファイル ---"
ls *.txt 2>/dev/null | grep -v '^o.txt$' || echo "(hello.txt は無い)"
cd $W

echo
echo "===== 段4 JSONで見ると success ====="
mkdir -p s4 && cd s4
claude -p "hello.txt を作り中身を hi に" \
  --output-format json > r.json 2>/dev/null
echo "exit=$?"
j r.json is_error subtype num_turns permission_denials total_cost_usd
cd $W

echo
echo "===== 段5 直す --allowedTools ====="
mkdir -p s5 && cd s5
claude -p "hello.txt を作り中身を hi に" \
  --allowedTools Write \
  --output-format json > r.json 2>/dev/null
echo "exit=$?"
j r.json is_error permission_denials total_cost_usd
echo "--- hello.txt の中身 ---"; cat hello.txt
cd $W

echo
echo "===== 段6 直す --permission-mode ====="
mkdir -p s6 && cd s6
claude -p "hello.txt を作り中身を hi に" \
  --permission-mode acceptEdits \
  --output-format json > r.json 2>/dev/null
echo "exit=$?"
j r.json is_error permission_denials
echo "--- hello.txt ---"; cat hello.txt 2>/dev/null || echo "(無し)"
cd $W

echo
echo "===== 段7 本物のエラーは exit 1 ====="
mkdir -p s7 && cd s7
echo "--- 7a 存在しないモデル ---"
claude -p "1+1" --model no-such-model-xyz >a.txt 2>/dev/null
echo "exit=$?"
python3 -c "
print(open('a.txt',encoding='utf-8').read().strip()[:38])"
echo "--- 7b ターン上限 ---"
claude -p "a.txt と b.txt と c.txt を順に作って" \
  --allowedTools Write --max-turns 1 \
  --output-format json > b.json 2>/dev/null
echo "exit=$?"
j b.json is_error subtype terminal_reason
cd $W

echo
echo "===== 段8 Bashは部分許可できる ====="
mkdir -p s8 && cd s8 && git init -q .
echo x > f.txt
git add -A && git -c user.email=a@b -c user.name=a commit -qm init
claude -p "git status を実行し1行目だけ答えて" \
  --allowedTools "Bash(git status:*)" \
  --output-format json > r.json 2>/dev/null
echo "exit=$?"
j r.json permission_denials
python3 -c "
import json;print('result        ',json.load(open('r.json'))['result'][:24])"
cd $W

echo
echo "===== 段9 許可の外を頼むと ====="
mkdir -p s9 && cd s9
echo "--- 9a rm を許可した場合(3回) ---"
for i in 1 2 3; do
  rm -rf a$i && mkdir a$i && cd a$i
  echo x > f.txt
  claude -p "f.txt を rm で消して" \
    --allowedTools "Bash(rm:*)" \
    --output-format json > r.json 2>/dev/null
  E=$?
  D=$(python3 -c "
import json;print(len(json.load(open('r.json'))['permission_denials']))")
  L=$(ls f.txt >/dev/null 2>&1 && echo のこる || echo きえた)
  echo "$i回目 exit=$E denials=$D f.txt=$L"
  cd ..
done
echo "--- 9b rm を許可しない場合(3回) ---"
for i in 1 2 3; do
  rm -rf b$i && mkdir b$i && cd b$i
  echo x > f.txt
  claude -p "f.txt を rm で消して" \
    --allowedTools "Bash(git status:*)" \
    --output-format json > r.json 2>/dev/null
  E=$?
  D=$(python3 -c "
import json;print(len(json.load(open('r.json'))['permission_denials']))")
  L=$(ls f.txt >/dev/null 2>&1 && echo のこる || echo きえた)
  echo "$i回目 exit=$E denials=$D f.txt=$L"
  cd ..
done
echo "--- 9c 命令文だけ変えて3回 ---"
for i in 1 2 3; do
  rm -rf c$i && mkdir c$i && cd c$i
  echo x > f.txt
  claude -p "rm -rf f.txt を実行して" \
    --allowedTools "Bash(git status:*)" \
    --output-format json > r.json 2>/dev/null
  E=$?
  D=$(python3 -c "
import json;print(len(json.load(open('r.json'))['permission_denials']))")
  L=$(ls f.txt >/dev/null 2>&1 && echo のこる || echo きえた)
  echo "$i回目 exit=$E denials=$D f.txt=$L"
  cd ..
done
echo "--- 9b の応答の一例 ---"
python3 -c "
import json;print(json.load(open('b1/r.json'))['result'][:38])"
cd $W

echo "===== 段10 予算で止める ====="
mkdir -p s10 && cd s10
claude -p "1から100までの素数を全部数えて説明して" \
  --max-budget-usd 0.001 \
  --output-format json > r.json 2>/dev/null
echo "exit=$?"
j r.json is_error subtype total_cost_usd
cd $W

echo
echo "===== 段11 stdin から渡す ====="
mkdir -p s11 && cd s11
printf 'ERROR db timeout\nINFO ok\nERROR db timeout\n' > log.txt
cat log.txt | claude -p "ERRORの行数を数字だけで"
echo "exit=$?"
cd $W

echo
echo "===== 段12 続きから走らせる ====="
mkdir -p s12 && cd s12
SID=$(python3 -c "import uuid;print(uuid.uuid4())")
echo "session-id = ${SID:0:13}..."
claude -p "合言葉は「みかん」。覚えて" \
  --session-id "$SID" > /dev/null 2>&1
echo "1本目 exit=$?"
claude -p "合言葉を1語だけ答えて" --resume "$SID"
echo "2本目 exit=$?"
cd $W
echo
echo "===== おわり ====="
