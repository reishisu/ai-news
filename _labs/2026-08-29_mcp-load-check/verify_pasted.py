#!/usr/bin/env python3
"""記事に貼った端末ログの各行が、output.txt に一字一句あるかを確かめる。

CLAUDE.md 第1節・第4節。過去に「貼ったログを自分で折り返し直していた」
（行の削除・語の脱落・句点の追加）事故があったので、機械で突き合わせる。

  python3 verify_pasted.py

`$ ` で始まる行はこちらが打ったコマンドなので run_all.sh 側と照合し、
それ以外（＝出力）は output.txt に完全一致で存在することを求める。
"""
import html
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ART = HERE.parents[1] / "contents" / "2026-08-29_mcp-load-check" / "index.html"
OUT = HERE / "output.txt"
SH = HERE / "run_all.sh"

art = ART.read_text(encoding="utf-8")
out_lines = set(OUT.read_text(encoding="utf-8").splitlines())
sh = SH.read_text(encoding="utf-8")

# `.code term` のブロックだけを見る(コードの引用や JSON は対象外)
blocks = re.findall(r'<div class="code term">.*?<pre>(.*?)</pre>', art, re.S)
print(f"端末ログのブロック: {len(blocks)}")

bad, checked_out, checked_cmd = [], 0, 0
for b in blocks:
    text = html.unescape(re.sub(r"<[^>]+>", "", b))
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line:
            continue
        if line.startswith("$ ") or line.startswith("  --"):
            # こちらが打った側。run_all.sh に同じ断片があるか見る
            frag = line[2:].strip().rstrip("\\").strip()
            if frag and "python3 -c" not in frag and frag not in sh:
                bad.append(("CMD", line))
            checked_cmd += 1
            continue
        if line.endswith("\\"):          # コマンドの継続行
            checked_cmd += 1
            continue
        if line not in out_lines:
            bad.append(("OUT", line))
        checked_out += 1

print(f"出力行 {checked_out} 行 / コマンド行 {checked_cmd} 行を照合")
if bad:
    print(f"\n不一致 {len(bad)} 件:")
    for kind, line in bad:
        print(f"  [{kind}] {line}")
    sys.exit(1)
print("すべて一致しました。")
