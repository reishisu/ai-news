#!/bin/sh
# /context の出力から Skills の表とそれに関わる行を取り出す。
# claude -p は対話画面でなくても通る(2026-08-27に確認)。
set -eu
raw=$(mktemp)
claude -p "/context" > "$raw"
{
  echo "# /context の Skills 行を測る / $(date +%Y-%m-%d) JST"
  echo "# claude -p \"/context\" は対話画面でなくても通る"
  echo
  grep -n '^\*\*Tokens\|^| Skills ' "$raw"
  echo
  sed -n '/^### Skills/,$p' "$raw"
} > context.txt
rm -f "$raw"
echo "context.txt を作りました"
