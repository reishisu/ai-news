#!/usr/bin/env python3
# 「Resource に何を書くか」を公式データで確かめる。
# s3:ListBucket と s3:GetObject では対象の型が違う。
# 幅を詰めるため ${Partition} だけ aws に置換して表示する。
import json

d = json.load(open("svcref-s3.json", encoding="utf-8"))
arn = {r["Name"]: r["ARNFormats"][0] for r in d["Resources"]}
KEEP = ("bucket", "object")

print("(${Partition} は aws に置換して表示)")
for act in ["ListBucket", "GetObject"]:
    a = next(x for x in d["Actions"] if x["Name"] == act)
    print(f"s3:{act}")
    skipped = []
    for r in a["Resources"]:
        if r["Name"] not in KEEP:
            skipped.append(r["Name"])
            continue
        s = arn[r["Name"]].replace("${Partition}", "aws")
        print(f"  対象 {r['Name']}")
        print(f"{s}")
    if skipped:
        print(f"  他 {len(skipped)} 種は省略: {','.join(skipped)}")
    print()
