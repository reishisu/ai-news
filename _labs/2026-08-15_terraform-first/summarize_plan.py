#!/usr/bin/env python3
"""terraform show -json の出力から、planの中身を短く取り出す。

  terraform plan -out=tfplan
  terraform show -json tfplan > tfplan.json
  python3 summarize_plan.py tfplan.json

1行が半角40字を超えないように出力する。
"""
import json
import sys


def wrap(prefix, items, width=40):
    """items をカンマ区切りにして width で折り返す。"""
    lines, cur = [], prefix
    for i, name in enumerate(items):
        piece = name + ("," if i < len(items) - 1 else "")
        if len(cur) + len(piece) + 1 > width and cur.strip() != prefix.strip():
            lines.append(cur)
            cur = " " * len(prefix) + piece
        else:
            cur = cur + (" " if cur.endswith(",") else "") + piece
    lines.append(cur)
    return lines


def main():
    plan = json.load(open(sys.argv[1]))
    print("format_version : " + plan["format_version"])
    print("terraform_ver  : " + plan["terraform_version"])

    changes = plan.get("resource_changes", [])
    print("resource_count : %d" % len(changes))

    for rc in changes:
        print("")
        print("addr    : " + rc["address"])
        print("actions : " + ",".join(rc["change"]["actions"]))
        after = rc["change"].get("after") or {}
        known = sorted(k for k, v in after.items() if v is not None)
        unknown = sorted((rc["change"].get("after_unknown") or {}).keys())
        unknown = [k for k in unknown if k not in known]
        for line in wrap("known   : ", known):
            print(line)
        for line in wrap("unknown : ", unknown):
            print(line)


if __name__ == "__main__":
    main()
