#!/usr/bin/env python3
# 既定のlintでは "Action:* / Resource:*" に何も出ない。
# community auditors を有効にすると初めて指摘が出る。
from collections import Counter

from parliament import analyze_policy_string

src = open("policies/04-star-star.json", encoding="utf-8").read()

for flag in (False, True):
    p = analyze_policy_string(src, include_community_auditors=flag)
    label = "community あり" if flag else "既定"
    print(f"{label}: 指摘 {len(p.findings)} 件")
    for issue, n in Counter(f.issue for f in p.findings).most_common():
        print(f"  {issue} x{n}")
