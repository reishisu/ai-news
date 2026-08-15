#!/usr/bin/env python3
# AWS Service Reference (公式の機械可読データ) で
# 記事に書くアクション名を1つずつ確かめる。
# 出典: https://servicereference.us-east-1.amazonaws.com/
import json
import sys

WANT = [
    ("s3", "GetObject"),
    ("s3", "PutObject"),
    ("s3", "ListBucket"),
    ("s3", "DeleteObject"),
    ("s3", "GetObjectt"),      # わざと綴りを間違えた
    ("sts", "AssumeRole"),
    ("sts", "GetCallerIdentity"),
    ("iam", "CreateUser"),
    ("iam", "PassRole"),
    ("iam", "CreateAccessKey"),
]


def load(svc):
    with open(f"svcref-{svc}.json", encoding="utf-8") as f:
        return json.load(f)


def main():
    cache = {}
    print("action                 ある? 種別")
    print("-" * 38)
    ng = 0
    for svc, act in WANT:
        d = cache.setdefault(svc, load(svc))
        hit = next((a for a in d["Actions"] if a["Name"] == act), None)
        name = f"{svc}:{act}"
        if hit is None:
            print(f"{name:<22} NG    -")
            ng += 1
            continue
        p = hit["Annotations"]["Properties"]
        kind = "書込" if p["IsWrite"] else "読取"
        if p["IsPermissionManagement"]:
            kind = "権限操作"
        print(f"{name:<22} OK    {kind}")
    print("-" * 38)
    print(f"見つからなかった: {ng} 件")
    return 0


if __name__ == "__main__":
    sys.exit(main())
