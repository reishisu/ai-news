#!/bin/sh
# Chrome Releases に Android WebView 専用の告知が出ているかを見る
curl -sSL 'https://chromereleases.googleblog.com/feeds/posts/default/-/Android%20WebView?alt=json&max-results=5' \
  | python3 -c '
import json,sys
d=json.load(sys.stdin)
for e in d["feed"].get("entry",[])[:5]:
    print(e["published"]["$t"][:19], "|", e["title"]["$t"])
'
