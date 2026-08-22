#!/usr/bin/env bash
# 2026-08-23_001 号の裏取りを、記事に書いた順で再実行する。
# 実行環境: この記事を書いたコンテナ (Linux 6.18 / curl 8.x / python3)
set -u

say() { printf '\n=== %s ===\n' "$1"; }

say "1. Claude Code 2.1.240 の全変更行を数える"
curl -sS https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md \
  | awk '/^## 2\.1\.240$/{f=1;next} /^## /{f=0} f' \
  | grep -E '^- ' | cat -n

say "2. 2.1.240 の npm 公開時刻 (JST判定用)"
curl -sS https://registry.npmjs.org/@anthropic-ai/claude-code \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["time"]["2.1.240"])'

say "3. Laravel: debounce が listener 側に入ったのは v13.26.0 か"
for v in v13.25.0 v13.26.1; do
  n=$(curl -sS "https://cdn.jsdelivr.net/gh/laravel/framework@$v/src/Illuminate/Events/Dispatcher.php" \
        | grep -ci debounce)
  echo "  Dispatcher.php @ $v : debounce $n 箇所"
done

say "4. Laravel v13.26.0 のリリース日"
curl -sS https://packagist.org/packages/laravel/framework.json \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["package"]["versions"]["v13.26.0"]["time"])'

say "5. AWS: Bedrock の GPT-5.6 Sol 値下げ (JSTウィンドウ判定)"
curl -sS https://aws.amazon.com/about-aws/whats-new/recent/feed/ \
  | python3 -c '
import re,sys,email.utils,datetime
x=sys.stdin.read()
for it in re.findall(r"<item>(.*?)</item>",x,re.S):
    t=re.search(r"<title>(.*?)</title>",it,re.S)
    p=re.search(r"<pubDate>(.*?)</pubDate>",it,re.S)
    if not (t and p): continue
    ti=re.sub(r"<!\[CDATA\[|\]\]>","",t.group(1)).strip()
    if "GPT-5.6 Sol" not in ti: continue
    d=email.utils.parsedate_to_datetime(p.group(1).strip())
    j=d.astimezone(datetime.timezone(datetime.timedelta(hours=9)))
    print(f"  {j:%m/%d %H:%M} JST  {ti}")'

say "6. 掲載URLのHTTPステータス"
while read -r u; do
  [ -z "$u" ] && continue
  printf '  %s ' "$(curl -sSL -o /dev/null -w '%{http_code}' "$u")"
  echo "$u"
done < "$(dirname "$0")/urls.txt"
