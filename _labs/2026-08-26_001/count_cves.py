#!/usr/bin/env python3
"""Chrome Releases の最新記事から、修正されたCVEを重大度と部品で数える。

出力は幅380pxの画面で読めるように短く保つ（CLAUDE.md 第4節）。
"""
import re, html, urllib.request
from collections import Counter

URL = "https://chromereleases.googleblog.com/feeds/posts/default"
req = urllib.request.Request(URL, headers={"User-Agent": "ai-news-daily/1.0"})
xml = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace")

entry = re.findall(r"<entry>(.*?)</entry>", xml, re.S)[0]
body = html.unescape(re.search(r"<content[^>]*>(.*?)</content>", entry, re.S).group(1))
text = re.sub(r"\s+", " ", html.unescape(re.sub("<[^>]+>", "", body)))

cves = re.findall(r"(Critical|High|Medium|Low)\s+(CVE-\d{4}-\d+):\s*([^.]+)\.", text)
sev = Counter(c[0] for c in cves)
part = Counter(c[2].strip().rsplit(" in ", 1)[-1] for c in cves)

print("total    ", len(cves))
for k in ("Critical", "High", "Medium", "Low"):
    print(f"{k:9} {sev[k]:4}")
print("-- 部品ごと")
for k in ("ANGLE", "CustomTabs", "WebGL", "WebView"):
    print(f"{k:11} {part[k]:2}")
