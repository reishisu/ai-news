#!/usr/bin/env python3
"""同じ質問を N 回投げて、スキルが呼ばれた回数を数える。

使い方: python3 run_trials.py <親ディレクトリ> <回数> <スキル名> [A名] [B名]
出力は幅380pxで読めるよう1行40桁以内に収める。
"""
import json, subprocess, sys, uuid

PROMPT = "リリース前に何を確認すればいい？"


def fired(dirpath, skill):
    """1回走らせて (呼ばれたか, 費用ドル) を返す。"""
    cmd = ["claude", "-p", PROMPT,
           "--session-id", str(uuid.uuid4()),
           "--output-format", "stream-json", "--verbose"]
    p = subprocess.run(cmd, cwd=dirpath, capture_output=True,
                       text=True, timeout=300)
    hit, cost = False, 0.0
    for line in p.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            o = json.loads(line)
        except ValueError:
            continue
        if o.get("type") == "assistant":
            for c in o["message"].get("content", []):
                if c.get("type") == "tool_use" and c["name"] == "Skill" \
                        and c.get("input", {}).get("skill") == skill:
                    hit = True
        if o.get("type") == "result":
            cost = o.get("total_cost_usd", 0.0)
    return hit, cost


def main():
    base, n, skill = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    la = sys.argv[4] if len(sys.argv) > 4 else "A 曖昧"
    lb = sys.argv[5] if len(sys.argv) > 5 else "B 具体"
    total = 0.0
    for label, sub in ((la, "A"), (lb, "B")):
        marks, hits = "", 0
        for i in range(n):
            hit, cost = fired(f"{base}/{sub}", skill)
            total += cost
            marks += "o" if hit else "."
            hits += hit
            print(f"{label} {i+1}回目: "
                  f"{'呼ばれた' if hit else '呼ばれない'}", flush=True)
        print(f"--> {label} {marks} {hits}/{n}\n", flush=True)
    print(f"費用 合計 ${total:.2f}")


main()
