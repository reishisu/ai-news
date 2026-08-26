#!/usr/bin/env python3
"""諦めたジョブを降ろさないと、あとの全部に積み上がることを実測する。

偽の ComfyUI（キュー1本）に同じ12枚を投げ、待ち方だけを変えて比べる。

  旧 = 2026/8/25 以前の wait()。上限で諦めるが、**降ろさない**
  新 = いまの run_job()。順番待ちと実行中を分け、諦めたら降ろしてやり直す

時間は本物の1/40に縮めてある（速い枚=1秒 / 詰まった枚=40秒）。
`COMFY_POLL_LIMIT` と `COMFY_RETRY` を下げて呼ぶので、
_comfy_character.py の既定値（240秒 / 3回）を変えても結果は変わらない。
"""
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

N = 12
STALL = (3, 4)          # この2件だけ40秒かかる（詰まった状態の代わり）
OLD_LIMIT = 8           # 旧の POLL_LIMIT に相当
NEW_LIMIT = 4           # 新の POLL_LIMIT（**実行中の時間**の上限）
NEW_RETRY = 2

os.environ["COMFY_POLL_LIMIT"] = str(NEW_LIMIT)
os.environ["COMFY_RETRY"] = str(NEW_RETRY)

import fake_comfy_queue as fake          # noqa: E402
import _comfy_character as cc            # noqa: E402


def old_wait(url, prompt_id, limit=OLD_LIMIT):
    """2026/8/25 以前の wait()。諦めても ComfyUI からは降ろさない。"""
    started = time.monotonic()
    while time.monotonic() - started < limit:
        entry = cc.api(url, f"/history/{prompt_id}").get(prompt_id)
        if entry and entry.get("outputs"):
            return entry["outputs"]
        time.sleep(0.2)
    return None


def run(mode, port):
    fake.serve(port, stall=STALL, fast=1.0, slow=40.0)
    url = f"http://127.0.0.1:{port}"
    cc.api(url, "/system_stats")
    wf = {"1": {"class_type": "X", "inputs": {}}}
    t0 = time.monotonic()
    got = lost = 0
    print(f"\n── {mode} ──")
    for i in range(1, N + 1):
        if mode == "旧":
            pid = cc.submit(url, wf, "lab")
            outs = old_wait(url, pid)
            print(f"  [{i}/{N}] "
                  + ("受け取った" if outs else "諦めた（降ろしていない）"))
        else:
            outs = cc.run_job(url, wf, "lab", label=f"[{i}/{N}]")
        got, lost = (got + 1, lost) if outs else (got, lost + 1)
    wall = time.monotonic() - t0
    time.sleep(1.0)
    with fake.LOCK:
        made = sum(1 for h in fake.HISTORY.values() if h.get("outputs"))
    return wall, got, lost, made


def main():
    print(f"12枚投げる。{STALL} 枚目だけ40秒かかる（ほかは1秒）。")
    print(f"旧の上限={OLD_LIMIT}秒（submitからの合計） / "
          f"新の上限={NEW_LIMIT}秒（実行中のみ）・やり直し{NEW_RETRY}回")
    rows = []
    for mode, port in (("旧", 8391), ("新", 8392)):
        # サーバーごと作り直す（状態を持ち越さない）
        fake.PENDING.clear(); fake.RUNNING.clear(); fake.HISTORY.clear()
        fake.SEEN = 0
        rows.append((mode,) + run(mode, port))
    print("\n── まとめ ──")
    print(f"{'':4}{'全体':>8}{'受け取った':>12}{'諦めた':>8}{'サーバーが描いた':>18}")
    for mode, wall, got, lost, made in rows:
        print(f"{mode:4}{wall:7.1f}秒{got:>10}枚{lost:>7}枚{made:>16}枚")
    old, new = rows[0], rows[1]
    print(f"\n旧が捨てた実物: {old[4] - old[2]}枚 "
          f"（サーバーは描いたのに、スクリプトが受け取らなかった）")


if __name__ == "__main__":
    main()
