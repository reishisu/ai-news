#!/usr/bin/env bash
# 2026-08-25_001 の出典確認。記事に書いた数値・日付の再現手順。
# 実行: bash _labs/2026-08-25_001/verify_sources.sh
set -u
UA='ai-news-jp/1.0 (daily digest; contact: poiponn697@gmail.com)'

echo "=== 1. minio/minio:latest の最終 push 日時 ==="
# 記事の「2025年9月7日から動いていない」の根拠。出力は幅40桁に収まる形に絞る。
curl -s 'https://hub.docker.com/v2/repositories/minio/minio/tags/latest' \
  | python3 -c 'import sys,json; d=json.load(sys.stdin); \
print("tag     ", d["name"]); \
print("pushed  ", d["tag_last_pushed"][:10])'

echo
echo "=== 2. MinIO のリポジトリが保守終了と書いているか ==="
# github.com はこの環境から403。jsDelivr 経由で本文を読む。
curl -s 'https://cdn.jsdelivr.net/gh/minio/minio@master/README.md' | head -3

echo
echo "=== 3. Laravel Sail が指している image ==="
curl -s 'https://cdn.jsdelivr.net/gh/laravel/sail@1.x/stubs/minio.stub' | sed -n '1,2p'

echo
echo "=== 4. Claude Tag のドキュメントの更新日時（sitemap の lastmod）==="
# 「skills-repo が対象期間内に出た」の根拠。JST 5:00 = 前日 20:00 UTC。
curl -s -A "$UA" 'https://claude.com/docs/sitemap.xml' \
  | python3 -c '
import sys,re,datetime
s=sys.stdin.read()
lo=datetime.datetime(2026,8,23,20,0,tzinfo=datetime.timezone.utc)
for b in re.findall(r"<url\b.*?</url>", s, re.S):
    l=re.search(r"<loc>(.*?)</loc>", b, re.S).group(1)
    m=re.search(r"<lastmod>(.*?)</lastmod>", b, re.S)
    if not m or "claude-tag" not in l: continue
    d=datetime.datetime.fromisoformat(m.group(1).replace("Z","+00:00"))
    if d>=lo:
        print(d.strftime("%m-%d %H:%M"), l.rsplit("/",1)[-1])'

echo
echo "=== 5. Claude Code の最新版と、その版の変更行 ==="
curl -s https://cdn.jsdelivr.net/gh/anthropics/claude-code@main/CHANGELOG.md \
  | awk '/^## 2\.1\.241$/{f=1;next} /^## /{f=0} f' | grep '^- ' | cat -n

echo
echo "=== 6. AWS What's New に読者のスタックの新着があるか ==="
curl -s 'https://aws.amazon.com/about-aws/whats-new/recent/feed/' \
  | python3 -c '
import sys,re,email.utils,datetime
s=sys.stdin.read()
lo=datetime.datetime(2026,8,23,20,0,tzinfo=datetime.timezone.utc)
n=0
for it in re.findall(r"<item>(.*?)</item>", s, re.S):
    t=re.search(r"<title>(.*?)</title>", it, re.S).group(1)
    d=email.utils.parsedate_to_datetime(
        re.search(r"<pubDate>(.*?)</pubDate>", it, re.S).group(1))
    if d>=lo:
        n+=1; print(" ", re.sub(r"<[^>]+>","",t)[:44])
print("期間内", n, "件")'

echo
echo "=== 7. VRChat の yt-dlp 更新要望が未解決か ==="
# 「回避策をまだ戻せない」の根拠。ページに埋まっている投稿データの status を見る。
# 見出しの文字列(Complete/In Progress)を grep すると、Canny の絞り込みUIの
# ラベルまで拾ってしまう。必ず該当投稿の周辺から取ること。
curl -s -A "$UA" \
  'https://feedback.vrchat.com/feature-requests/p/update-to-yt-dlp-20260819' \
  > /tmp/vrc_yt.html
python3 - /tmp/vrc_yt.html <<'PY_END'
import re, sys
s = open(sys.argv[1]).read()
i = s.find('"urlName":"update-to-yt-dlp-20260819"')
seg = s[max(0, i - 600):i + 400]
for k in ("status", "score", "createdAt", "created", "updatedAt"):
    m = re.search(r'"' + k + r'":"?([^,"]+)', seg)
    if m:
        print(f"{k:10}", m.group(1)[:19])
PY_END
