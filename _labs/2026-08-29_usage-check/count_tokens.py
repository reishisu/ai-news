"""~/.claude/projects/ のログから、トークンの合計を種類別に数える。依存なし。"""
import json, glob, os, collections
tot = collections.Counter()
for f in glob.glob(os.path.expanduser("~/.claude/projects/*/*.jsonl")):
    for ln in open(f, encoding="utf-8", errors="ignore"):
        try:
            u = (json.loads(ln).get("message") or {}).get("usage")
        except Exception:
            continue
        if not u:
            continue
        for k in ("input_tokens", "output_tokens",
                  "cache_read_input_tokens", "cache_creation_input_tokens"):
            tot[k] += u.get(k, 0)
for k, v in tot.items():
    print(f"{k:32s}{v:>15,}")
