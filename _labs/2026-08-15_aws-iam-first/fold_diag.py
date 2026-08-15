#!/usr/bin/env python3
# terraform validate -json を読んで、38桁で折り返して出す。
# 文言は一字も変えていない。折り返しだけしている。
import json
import sys
import textwrap

d = json.load(sys.stdin)
print(f"エラー {d['error_count']} 件")
for g in d["diagnostics"]:
    print(f"{g['range']['start']['line']}行目:")
    for ln in textwrap.wrap(g["summary"], width=38, subsequent_indent="  "):
        print(ln)
