#!/bin/sh
# check_quotes.py に渡す一次資料を取り直す。
# **キャッシュを使い回さないこと**（2026-08-28 に /tmp のキャッシュが古い版に
# 入れ替わっていて、危うく「引用した行が存在しない」と誤判定するところだった）。
set -e
OUT="${1:-./src}"
UA='ai-news-bot/1.0 (daily tech digest; contact: poiponn697@gmail.com)'
mkdir -p "$OUT"

get() { curl -sSL -A "$UA" -H 'Cache-Control: no-cache' "$2" -o "$OUT/$1" -w "%{http_code}  $1\n"; }

get cli.html      "https://code.claude.com/docs/en/cli-reference"
get changelog.md  "https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md"
get web.html      "https://code.claude.com/docs/en/claude-code-on-the-web"
get cowork.html   "https://claude.com/blog/cowork-built-in-browser"
get composer.md   "https://cdn.jsdelivr.net/gh/composer/composer@2.10.3/CHANGELOG.md"
get gha.html      "https://github.blog/changelog/2026-08-27-actions-retention-will-cover-checks-workflow-runs-and-statuses"
get php.html      "https://www.php.net/ChangeLog-8.php"
get play-blog.html "https://android-developers.googleblog.com/2026/08/app-quality-memory-optimization-secure-onboarding.html"
get play-help.html "https://support.google.com/googleplay/android-developer/answer/17492799"
get deepmind.html "https://deepmind.google/blog/piloting-the-worlds-first-double-blind-ai-evaluations/"
get mhs.html      "https://www.anthropic.com/news/model-hardware-standard-research-preview"
get gemini.html   "https://ai.google.dev/gemini-api/docs/changelog"
get vrchat.json   "https://ask.vrchat.com/t/developer-update-27-august-2026/48877.json"

echo
echo "照合:"
echo "  python3 check_quotes.py ../../contents/2026-08-28_001/index.html $OUT/*"
