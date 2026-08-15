#!/usr/bin/env python3
"""out/*.truth と out/*.json から、幅の狭い結果表を出す。
1行は半角40文字以内。"""
import json, sys, glob, os, textwrap

B = os.path.dirname(os.path.abspath(__file__))
W = 38


def wrap(prefix, text):
    text = " ".join(text.split())
    for i, line in enumerate(textwrap.wrap(text, W - len(prefix)) or [""]):
        print(("  " + prefix if i == 0 else "  " + " " * len(prefix)) + line)


for name in sys.argv[1:]:
    t = open(f"{B}/out/{name}.truth").read().split()
    case, rc, before, after = t[0], t[1], t[2], t[3]
    pushed = "YES" if before != after else "no"
    print(f"[{case}]")
    print(f"  push reached remote : {pushed}")
    print(f"  remote main : {before} -> {after}")
    d = json.load(open(f"{B}/out/{name}.json"))
    den = d.get("permission_denials", [])
    print(f"  permission_denials  : {len(den)}")
    for x in den:
        wrap("denied cmd: ", x.get("tool_input", {}).get("command", "?"))
    print()
