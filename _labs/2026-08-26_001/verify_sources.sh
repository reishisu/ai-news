#!/usr/bin/env bash
# 2026-08-26_001 号の裏取り一式。
# 対象期間: 2026-08-25 05:00 〜 2026-08-26 05:00 JST（= 08-24 20:00 〜 08-25 20:00 UTC）
# 実行環境: このコンテナ（python3 / curl）。github.com は403なので raw.githubusercontent.com を使う。
set -u
UA='Mozilla/5.0 (compatible; ai-news-daily/1.0; contact poiponn697@gmail.com)'

echo "== 1. Claude Code の版と公開時刻（npm レジストリ）"
curl -sS https://registry.npmjs.org/@anthropic-ai/claude-code \
 | python3 -c 'import json,sys,datetime
d=json.load(sys.stdin); t=d["time"]
rows=sorted([(v,ts) for v,ts in t.items() if v[0].isdigit()], key=lambda r:r[1])[-6:]
for v,ts in rows:
    j=datetime.datetime.fromisoformat(ts.replace("Z","+00:00"))+datetime.timedelta(hours=9)
    print(f"{v:9} JST {j:%m/%d %H:%M}")'

echo "== 2. 2.1.243 の変更行を種類ごとに数える"
curl -sS https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md -o /tmp/cc.md
# 注意: [VSCode] 接頭辞の行があるので、それを見込まないと数え漏らす（8/26に踏んだ）
awk '/^## 2\.1\.243$/{f=1;next} /^## /{f=0} f' /tmp/cc.md | grep -c '^- '
awk '/^## 2\.1\.243$/{f=1;next} /^## /{f=0} f' /tmp/cc.md \
 | grep -oE '^- (\[VSCode\] )?(Added|Changed|Removed|Fixed|Improved|Updated)' \
 | sed 's/\[VSCode\] //' | sort | uniq -c

echo "== 3. Laravel v13.27.0 の公開時刻（Packagist）"
curl -sS https://repo.packagist.org/p2/laravel/framework.json \
 | python3 -c 'import json,sys
d=json.load(sys.stdin)["packages"]["laravel/framework"]
for v in d[:3]: print(v["version"], v["time"])'

echo "== 4. in_array / doesnt_contain の差分（ソースを2つのタグで取って比べる）"
for t in v13.26.1 v13.27.0; do
  curl -sS -o "/tmp/va_$t.php" \
    "https://raw.githubusercontent.com/laravel/framework/$t/src/Illuminate/Validation/Concerns/ValidatesAttributes.php"
done
diff <(grep -A18 'function validateInArray' /tmp/va_v13.26.1.php) \
     <(grep -A18 'function validateInArray' /tmp/va_v13.27.0.php) | grep 'in_array('
diff <(grep -A14 'function validateDoesntContain' /tmp/va_v13.26.1.php) \
     <(grep -A14 'function validateDoesntContain' /tmp/va_v13.27.0.php) | grep 'in_array('
echo "-- contains は差分なしのはず"
diff -q <(grep -A12 'function validateContains' /tmp/va_v13.26.1.php) \
        <(grep -A12 'function validateContains' /tmp/va_v13.27.0.php) && echo "contains: 同一"

echo "== 5. Chrome / WebView の安定版（chromiumdash）"
for p in win android webview; do
  curl -sS "https://chromiumdash.appspot.com/fetch_releases?channel=Stable&platform=$p&num=2" \
   | python3 -c "import json,sys,datetime
for r in json.load(sys.stdin):
    u=datetime.datetime.utcfromtimestamp(r['time']/1000)+datetime.timedelta(hours=9)
    print(f\"$p {r['version']:18} JST {u:%m/%d %H:%M}\")"
done

echo "== 6. Chrome 152 のセキュリティ修正を重大度と部品で数える"
python3 -c "import urllib.request;open('/tmp/cr.xml','wb').write(urllib.request.urlopen(urllib.request.Request('https://chromereleases.googleblog.com/feeds/posts/default',headers={'User-Agent':'ai-news-daily/1.0'}),timeout=60).read())"
python3 - <<'PY'
import re,html
from collections import Counter
s=open('/tmp/cr.xml',encoding='utf-8',errors='replace').read()
e=re.findall(r'<entry>(.*?)</entry>',s,re.S)[0]
t=re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]+>','',html.unescape(re.search(r'<content[^>]*>(.*?)</content>',e,re.S).group(1)))))
cves=re.findall(r'(Critical|High|Medium|Low)\s+(CVE-\d{4}-\d+):\s*([^.]+)\.',t)
print("total", len(cves), Counter(c[0] for c in cves))
print("components", Counter(c[2].strip().rsplit(' in ',1)[-1] for c in cves).most_common(6))
for k in ('WebView','CustomTabs'):
    print(k, sum(1 for c in cves if c[2].strip().rsplit(' in ',1)[-1]==k))
PY

echo "== 7. AWS What's New の対象期間内の item"
python3 -c "import urllib.request;open('/tmp/aws.xml','wb').write(urllib.request.urlopen(urllib.request.Request('https://aws.amazon.com/about-aws/whats-new/recent/feed/',headers={'User-Agent':'ai-news-daily/1.0'}),timeout=60).read())"
python3 - <<'PY'
import re,html,email.utils,datetime
s=open('/tmp/aws.xml',encoding='utf-8',errors='replace').read()
lo=datetime.datetime(2026,8,24,20,tzinfo=datetime.timezone.utc)
hi=datetime.datetime(2026,8,25,20,tzinfo=datetime.timezone.utc)
n=0
for it in re.findall(r'<item>(.*?)</item>',s,re.S):
    d=email.utils.parsedate_to_datetime(re.search(r'<pubDate>(.*?)</pubDate>',it,re.S).group(1))
    if lo<=d<hi:
        n+=1
        ti=html.unescape(re.sub('<[^>]+>','',re.search(r'<title>(.*?)</title>',it,re.S).group(1))).strip()
        print(f"  {d:%m/%d %H:%M}Z {ti[:70]}")
print("期間内", n, "件")
PY

echo "== 8. 読めなかったもの（到達できないことは「無い」の根拠にしない）"
for u in https://openai.com/index/introducing-admin-plugin \
         https://openai.com/index/jalapeno-first-results \
         https://syndication.twitter.com/srv/timeline-profile/screen-name/ClaudeDevs ; do
  printf '%s  %s\n' "$(curl -sSL -o /dev/null -w '%{http_code}' -A "$UA" "$u")" "$u"
done
