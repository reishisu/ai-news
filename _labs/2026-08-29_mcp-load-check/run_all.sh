#!/usr/bin/env bash
# 記事 2026-08-29_mcp-load-check の実測を最初から再現する。
# 使い方: bash run_all.sh 2>&1 | tee output.txt
# サーバーは作業ディレクトリ直下に置く。端末の行を短くするため(CLAUDE.md 第4節)。
set -u
export COLUMNS=40
LAB=/home/user/lab-mcp
PROJ=$LAB/proj

say() { echo; echo "##### $* #####"; }

say "0. 環境"
claude --version
python3 --version

rm -rf "$PROJ"; mkdir -p "$PROJ"; cd "$PROJ"
cp "$LAB/hello_server.py" ./hello.py

say "1. まっさらな状態"
claude mcp list 2>&1

say "2. パスを打ち間違えて追加する"
claude mcp add demo -- python3 helo.py 2>&1 | head -1

say "3. 一覧で確かめる"
claude mcp list 2>&1

say "4. 消して、正しいパスで入れ直す"
claude mcp remove demo 2>&1 | head -1
claude mcp add demo -- python3 hello.py 2>&1 | head -1

say "5. もう一度一覧"
claude mcp list 2>&1

say "6. get で1台だけ見る"
claude mcp get demo 2>&1

say "7. モデルから本当に呼べるか"
claude -p "mcp__demo__hello を name=めたん で呼ぶ" \
  --allowedTools "mcp__demo__hello" < /dev/null 2>&1 | tail -2

say "8. 同じサーバーを project スコープでも追加する"
claude mcp add -s project team -- python3 hello.py 2>&1 | head -1
cat .mcp.json

say "9. 一覧: 中身は同じなのに片方だけ繋がらない"
claude mcp list 2>&1

say "10. local の方を消し、承認待ちの1台だけにする"
claude mcp remove demo 2>&1 | head -1
claude mcp list 2>&1

say "11. 承認待ちのまま -p で呼べるか"
claude -p "mcp__team__hello を name=ずんだもん で呼ぶ" \
  --allowedTools "mcp__team__hello" < /dev/null 2>&1 | tail -2

say "12. 承認の記録は空のまま"
python3 - <<'PY'
import json
d = json.load(open('/root/.claude.json'))
p = d.get('projects', {}).get('/home/user/lab-mcp/proj', {})
for k in ('enabledMcpjsonServers', 'disabledMcpjsonServers'):
    print(k, '=', p.get(k))
PY

say "13. --strict-mcp-config で締め出す"
claude -p "mcp__team__hello を呼ぶ。無ければツールが無いと言う" \
  --allowedTools "mcp__team__hello" --strict-mcp-config < /dev/null 2>&1 | tail -2

say "14. disabledMcpjsonServers で拒否する"
mkdir -p .claude
printf '{\n  "disabledMcpjsonServers": ["team"]\n}\n' > .claude/settings.json
cat .claude/settings.json
claude mcp get team 2>&1 | head -3

say "15. 拒否中の一覧"
claude mcp list 2>&1

say "16. 拒否中に -p で呼べるか"
claude -p "mcp__team__hello を呼ぶ。無ければツールが無いと言う" \
  --allowedTools "mcp__team__hello" < /dev/null 2>&1 | tail -2

say "おわり"
