#!/bin/bash
# 使い方: ./trust.sh <ディレクトリ絶対パス>
# .claude/settings.json の allow を有効にするため workspace を信頼済みにする
CJ="$HOME/.claude.json"
[ -f "$CJ" ] || echo '{}' > "$CJ"
tmp=$(mktemp)
jq --arg d "$1" '.projects[$d].hasTrustDialogAccepted = true' "$CJ" > "$tmp" && mv "$tmp" "$CJ"
jq --arg d "$1" '.projects[$d].hasTrustDialogAccepted' "$CJ"
