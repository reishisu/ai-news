#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""bug_repro.py — flow_signals.py の merge_samples() で踏んだバグを再現する。

`git log --first-parent --merges --format='%ct %P'` の1行は
  親が2つのマージコミットで "ct p1 p2" = 3フィールド。
ガードを `len(f) < 4` にすると全マージが落ちて標本0件になる。
「標本0件」はリポジトリにマージが無いときと見た目が同じになる、が要点。

使い方: python3 bug_repro.py <repo> <trunk-or-rev>
"""
import subprocess
import sys


def git(repo, *args):
    r = subprocess.run(["git", "-C", repo] + list(args),
                       capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


def merge_samples(repo, trunk, guard):
    """guard 未満のフィールド数の行を捨てる。本来の正しい値は 3。"""
    n = 0
    for line in git(repo, "log", "--first-parent", "--merges",
                    "--format=%ct %P", trunk).splitlines():
        f = line.split()
        if len(f) < guard:
            continue
        mts, p1, p2 = int(f[0]), f[1], f[2]
        base = git(repo, "merge-base", p1, p2)
        side = git(repo, "log", "--format=%ct", "%s..%s" % (base, p2)).split()
        if not side:
            continue
        n += 1
    return n


def main():
    repo, trunk = sys.argv[1], sys.argv[2]
    raw = git(repo, "log", "--first-parent", "--merges",
              "--format=%ct %P", trunk).splitlines()
    print("マージコミット数 %d" % len(raw))
    print("1行のフィールド数 %s" % sorted({len(l.split()) for l in raw}))
    for guard in (4, 3):
        print("ガード <%d : 標本 %d件"
              % (guard, merge_samples(repo, trunk, guard)))


if __name__ == "__main__":
    main()
