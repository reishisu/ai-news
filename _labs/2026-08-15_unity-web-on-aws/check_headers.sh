#!/bin/bash
# 配信URLに、Unity Web で効くヘッダーが付いているか見る。
# 使い方: ./check_headers.sh https://example.com/Build/x.wasm
set -u
curl -sS -D - -o /dev/null \
  -H 'Accept-Encoding: br, gzip' "$1" \
| tr -d '\r' \
| awk '
  { l = tolower($0) }
  l ~ /^http\// { print $1, $2; next }
  l ~ /^(content-type|content-encoding|cross-origin)/ {
    i = index($0, ":");
    print tolower(substr($0, 1, i - 1));
    print "  " substr($0, i + 2);
  }'
