#!/usr/bin/env bash
# 2026-08-24_001 の出典確認。記事に書いた数値・日付の再現手順。
# 実行: bash _labs/2026-08-24_001/verify_sources.sh
set -u

echo "=== 1. AWS What's New に対象期間(8/23 5:00〜8/24 5:00 JST)の新規があるか ==="
# JST 5:00 = 前日 20:00 GMT。8/22 20:00 GMT 以降の <item> があるかを見る。
# 注意: フィード先頭の <pubDate> はチャンネル自身の生成時刻なので、必ず <item> 内だけを見ること。
curl -s 'https://aws.amazon.com/about-aws/whats-new/recent/feed/' \
  | python3 -c 'import sys,re; s=sys.stdin.read(); \
items=re.findall(r"<item>(.*?)</item>", s, re.S); \
print("item数:", len(items)); \
print("\n".join(re.search(r"<pubDate>(.*?)</pubDate>", it, re.S).group(1) for it in items[:3]))'

echo
echo "=== 2. Chrome Releases の最新エントリの日付 ==="
curl -s https://chromereleases.googleblog.com/ \
  | sed 's/<[^>]*>/\n/g' \
  | grep -E '^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday), [A-Z]' \
  | head -3

echo
echo "=== 3. Claude Code の最新版と、その版の変更行 ==="
curl -s https://registry.npmjs.org/@anthropic-ai/claude-code \
  | python3 -c 'import sys,json; d=json.load(sys.stdin); t=d["time"]; \
vs=[(v,t[v]) for v in d["versions"]]; vs.sort(key=lambda x:x[1]); \
print("\n".join(f"{v}\t{ts}" for v,ts in vs[-4:]))'

echo
echo "=== 4. Chrome 153/154 の安定版の日付 ==="
# 記事の「9月8日 / 9月22日」の根拠。Stable Cut ではなく stable_date を見ること。
for m in 153 154; do
  curl -s "https://chromiumdash.appspot.com/fetch_milestone_schedule?mstone=$m" \
    | python3 -c "import sys,json;d=json.load(sys.stdin)['mstones'][0];print(d['mstone'], d['stable_date'])"
done

echo
echo "=== 5. RWS削除が WebView も対象か（desktop/android/webview）==="
# ChromeStatus の API は先頭に )]}' が付くので5文字落とす
for f in 5194473869017088 5162221567082496 5309598397497344; do
  curl -s "https://chromestatus.com/api/v0/features/$f" | tail -c +6 \
    | python3 -c "
import sys,json
d=json.load(sys.stdin); c=d['browsers']['chrome']
print(f\"{d['name'][:44]:46} desktop={c.get('desktop')} android={c.get('android')} webview={c.get('webview')} status={c['status']['text']}\")"
done

echo
echo "=== 6. WebView Beta ページがまだ 4 weeks か ==="
curl -s https://developer.android.com/develop/ui/views/layout/webapps/webview-testing \
  | sed 's/<[^>]*>//g' | grep -o '[0-9]* weeks before' | head -1
