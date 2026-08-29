#!/usr/bin/env bash
# --output-format json が返すキーを、実際に1回叩いて全部並べる。
# 使い方: bash keys.sh 2>&1 | tee keys.txt
export COLUMNS=40
W=/tmp/cc-auto-keys
rm -rf $W && mkdir -p $W && cd $W
claude -p "1+1は？数字だけ" --output-format json > r.json 2>/dev/null
echo "exit=$?"
echo "--- 返ってきたキー ---"
python3 -c "
import json
d=json.load(open('r.json'))
for k in sorted(d):
    t=type(d[k]).__name__
    print('%-22s %s'%(k,t))
print()
print('キーの数:',len(d))
"
