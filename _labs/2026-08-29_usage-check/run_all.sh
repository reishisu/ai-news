#!/bin/bash
# 記事「Claude Codeの使用量と料金の確かめ方」の再現一式。
# 数字はあなたの機械のログの中身になります。
set -x
claude --version
ls ~/.claude/projects/ | head -3
npx -y ccusage@latest daily
npx -y ccusage@latest monthly
npx -y ccusage@latest blocks
npx -y ccusage@latest session
npx -y ccusage@latest daily --json | python3 daily_table.py
python3 count_tokens.py
claude -p "/cost" < /dev/null
claude -p "/usage" < /dev/null
