#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""flow_signals.py

git のログだけで「止まっている作業」を本人の申告より先に見つける。
しきい値は決め打ちせず、そのリポジトリ自身の履歴から出す
(Kanban Guide: SLE は historical cycle time に基づくべき)。

測るもの
  Work Item Age : 着手(枝が分岐した最初のコミット)から現在まで
  静止時間      : 最後のコミットから現在まで
                  = 未統合の枝では「レビュー待ち時間」そのもの
  SLE           : 過去のマージから復元した レビュー待ち の 85%点
                  標本が5件未満なら サイクルタイム、それも無理なら
                  幹の連続コミット間隔 に落とす(落ちたことを明示する)

使い方
  python3 flow_signals.py <repo> [--trunk origin/main] [--pct 85]
                          [--now 2026-08-14T15:20:00Z]
"""
import argparse
import math
import subprocess
import sys
import time
import unicodedata

W = 40  # 出力1行の上限(半角換算)
MIN_N = 5  # SLE を出すのに必要な最小標本数


def disp_width(s):
    return sum(2 if unicodedata.east_asian_width(c) in "WFA" else 1 for c in s)


def say(s):
    if disp_width(s) > W:
        s += "  <<OVER%d" % disp_width(s)
    print(s)


def git(repo, *args):
    r = subprocess.run(["git", "-C", repo] + list(args),
                       capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


def hm(sec):
    sec = int(sec)
    d, rem = divmod(sec, 86400)
    h, m = divmod(rem, 3600)[0], (rem % 3600) // 60
    return "%dd%02dh" % (d, h) if d else "%dh%02dm" % (h, m)


def pct_nearest_rank(vals, pct):
    """「pct% は この値以内」を満たす最小値 (nearest-rank)。"""
    if not vals:
        return None
    s = sorted(vals)
    return s[max(1, math.ceil(pct / 100.0 * len(s))) - 1]


def merge_samples(repo, trunk):
    """幹のマージから (サイクルタイム, レビュー待ち) を復元する。"""
    cyc, rev = [], []
    for line in git(repo, "log", "--first-parent", "--merges",
                    "--format=%ct %P", trunk).splitlines():
        f = line.split()
        if len(f) < 3:          # ct p1 p2 で 3 個。ここを 4 にすると全滅する
            continue
        mts, p1, p2 = int(f[0]), f[1], f[2]
        base = git(repo, "merge-base", p1, p2)
        side = [int(x) for x in
                git(repo, "log", "--format=%ct", "%s..%s" % (base, p2)).split()]
        if not side:
            continue
        cyc.append(mts - min(side))   # 着手 -> 統合
        rev.append(mts - max(side))   # 最終コミット -> 統合
    return cyc, rev


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo")
    ap.add_argument("--trunk", default="origin/main")
    ap.add_argument("--pct", type=float, default=85.0)
    ap.add_argument("--now")
    a = ap.parse_args()
    repo, trunk = a.repo, a.trunk

    if a.now:
        now = int(time.mktime(time.strptime(a.now, "%Y-%m-%dT%H:%M:%SZ"))
                  - time.timezone)
    else:
        now = int(time.time())

    if not git(repo, "rev-parse", "--verify", trunk):
        say("trunk が無い: %s" % trunk)
        sys.exit(2)

    say("repo : %s" % repo.rstrip("/").split("/")[-1])
    say("trunk: %s" % trunk)
    say("now  : %s UTC" % time.strftime("%m-%d %H:%M", time.gmtime(now)))
    say("-" * 32)

    # --- 1. 履歴から SLE を出す -----------------------------------
    cyc, rev = merge_samples(repo, trunk)
    ts = sorted(int(x) for x in
                git(repo, "log", "--first-parent", "--format=%ct",
                    trunk).split())
    gaps = [ts[i + 1] - ts[i] for i in range(len(ts) - 1)]

    say("[履歴] マージから復元した標本")
    say("  サイクルタイム %d件 / レビュー待ち %d件" % (len(cyc), len(rev)))
    if len(rev) >= MIN_N:
        say("  レビュー待ち 中央値 %s" % hm(pct_nearest_rank(rev, 50)))
        say("               最長 %s" % hm(max(rev)))
        sle, src = pct_nearest_rank(rev, a.pct), "レビュー待ち"
    elif len(cyc) >= MIN_N:
        say("  レビュー待ちが%d件未満。サイクルタイムを使う" % MIN_N)
        sle, src = pct_nearest_rank(cyc, a.pct), "サイクルタイム"
    else:
        say("  %d件未満。SLE には使えない" % MIN_N)
        say("[代替] 幹の連続コミット間隔")
        say("  標本 %d件 / 中央値 %s / 最長 %s" %
            (len(gaps), hm(pct_nearest_rank(gaps, 50) or 0), hm(max(gaps or [0]))))
        sle, src = pct_nearest_rank(gaps, a.pct), "コミット間隔(代替)"
    if not sle:
        say("標本ゼロ。判定を中止する")
        sys.exit(3)

    say("-" * 32)
    say("[SLE] %s の %.0f%%点" % (src, a.pct))
    say("  %s を超えたら声をかける" % hm(sle))
    say("-" * 32)

    # --- 2. 幹に入っていない枝 ------------------------------------
    refs = [r for r in git(repo, "for-each-ref", "--format=%(refname:short)",
                           "refs/remotes", "refs/heads").splitlines()
            if r and not r.endswith("/HEAD") and r != trunk]
    merged = set(git(repo, "branch", "-a", "--merged", trunk,
                     "--format=%(refname:short)").splitlines())

    rows = []
    for ref in refs:
        if ref in merged:
            continue
        last = int(git(repo, "log", "-1", "--format=%ct", ref) or 0)
        if not last:
            continue
        cnt = git(repo, "rev-list", "--left-right", "--count",
                  "%s...%s" % (trunk, ref)).split()
        behind, ahead = (int(cnt[0]), int(cnt[1])) if len(cnt) == 2 else (0, 0)
        base = git(repo, "merge-base", trunk, ref)
        side = [int(x) for x in
                git(repo, "log", "--format=%ct",
                    "%s..%s" % (base, ref)).split()]
        start = min(side) if side else last
        rows.append(dict(ref=ref, idle=now - last, age=now - start,
                         ahead=ahead, behind=behind,
                         who=git(repo, "log", "-1", "--format=%an", ref)))
    rows.sort(key=lambda r: -r["idle"])

    say("■ 幹に未統合の枝 (静止時間 順)")
    hit = 0
    for r in rows:
        over = r["idle"] > sle
        hit += over
        name = r["ref"].replace("origin/", "")
        if disp_width(name) > 32:
            name = name[:30] + ".."
        ratio = r["idle"] / sle
        say("%s %s" % ("[!]" if over else "[ ]", name))
        say("    静止 %s = SLE の %sx" %
            (hm(r["idle"]), ("%.2f" if ratio < 1 else "%.1f") % ratio))
        say("    着手からの経過 %s" % hm(r["age"]))
        say("    自前%d件 / 幹に%d件 遅れ" % (r["ahead"], r["behind"]))
        say("    最終 %s" % r["who"][:20])
    if not rows:
        say("  未統合の枝は無い")
    say("-" * 32)
    say("要確認 %d件 / 検査 %d件" % (hit, len(rows)))


if __name__ == "__main__":
    main()
