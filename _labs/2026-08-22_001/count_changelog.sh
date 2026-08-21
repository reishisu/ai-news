#!/bin/sh
# Claude Code の指定版の変更行を数える（CLAUDE.md 第16節）
V="${1:-2.1.239}"
curl -sSL https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md \
  | awk -v V="## $V" '$0==V{f=1;next} /^## /{f=0} f' > /tmp/cc_block.txt
echo "版: $V"
echo "  変更行の総数 : $(grep -c '^- ' /tmp/cc_block.txt)"
echo "  うち Fixed   : $(grep -c '^- Fixed' /tmp/cc_block.txt)"
echo "--- Fixed 以外の行 ---"
grep '^- ' /tmp/cc_block.txt | grep -v '^- Fixed' | cat -n
