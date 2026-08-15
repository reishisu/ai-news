#!/usr/bin/env python3
"""タスクの依存関係から、最短日数と各タスクの全余裕(total float)を出す。

使い方: python3 critical_path.py
TASKS に「id, 名前, 日数, 先に終わっている必要があるid」を書くだけ。
"""
import unicodedata

# id, 名前, 日数, 依存(先に終わっている必要があるタスク)
TASKS = [
    ("A", "仕様を1枚にまとめる",     0.5, []),
    ("B", "APIの入出力を決める",     0.5, ["A"]),
    ("C", "DBのテーブルを決める",    0.5, ["A"]),
    ("D", "認証APIを実装する",       2.0, ["B", "C"]),
    ("E", "ログイン画面を作る",      1.5, ["B"]),
    ("F", "入力エラーの表示を作る",  1.0, ["E"]),
    ("G", "つないでE2Eテストを書く", 1.0, ["D", "F"]),
]


def forward(days, deps):
    """前向き計算。最早開始(ES)と最早終了(EF)を出す。"""
    es, ef = {}, {}

    def ef_of(t):
        if t not in ef:
            es[t] = max([ef_of(d) for d in deps[t]], default=0.0)
            ef[t] = es[t] + days[t]
        return ef[t]

    for t in days:
        ef_of(t)
    return es, ef


def backward(days, deps, span):
    """後ろ向き計算。最遅開始(LS)を出す。全余裕はここでしか出ない。"""
    succ = {t: [] for t in days}
    for t in deps:
        for d in deps[t]:
            succ[d].append(t)
    ls = {}

    def ls_of(t):
        if t not in ls:
            lf = min([ls_of(s) for s in succ[t]], default=span)
            ls[t] = lf - days[t]
        return ls[t]

    for t in days:
        ls_of(t)
    return ls


def critical_paths(days, deps, span):
    """長さが span と同じ道を全部出す。1本とは限らない。"""
    heads = {d for t in deps for d in deps[t]}
    out = []

    def walk(t, tail, length):
        tail, length = [t] + tail, length + days[t]
        if not deps[t]:
            if abs(length - span) < 1e-9:
                out.append(tail)
            return
        for d in deps[t]:
            walk(d, tail, length)

    for t in sorted(days):
        if t not in heads:
            walk(t, [], 0.0)
    return out


def pad(text, width):
    """日本語(全角)を2文字ぶんとして数え、桁を揃える。"""
    w = sum(2 if unicodedata.east_asian_width(c) in "WFA" else 1 for c in text)
    return text + " " * max(0, width - w)


def report(tasks, label):
    days = {t[0]: t[2] for t in tasks}
    deps = {t[0]: t[3] for t in tasks}
    es, ef = forward(days, deps)
    span = max(ef.values())
    ls = backward(days, deps, span)

    print(f"=== {label} ===")
    print("  " + pad("id", 3) + pad("タスク", 24) + "日数 全余裕")
    for tid, name, d, _ in tasks:
        tf = round(ls[tid] - es[tid], 6)
        head = "* " if tf == 0.0 else "  "
        print(head + pad(tid, 3) + pad(name, 24) + f"{d:>4.1f} {tf:>5.1f}")
    print("* = 全余裕ゼロ(遅れたら納期が延びる)")
    print(f"1人で順番にやると : {sum(days.values()):>4.1f} 日")
    print(f"並行にやると      : {span:>4.1f} 日")
    print("納期を決めている道 :")
    for p in critical_paths(days, deps, span):
        print("  " + " → ".join(p))
    print()


if __name__ == "__main__":
    report(TASKS, "そのまま")

    # 一番大きいタスク D(2.0日) を半分にしてみる
    d_half = [(i, n, 1.0 if i == "D" else d, dp) for i, n, d, dp in TASKS]
    report(d_half, "D を 2.0→1.0日 に縮めた")

    # 全余裕ゼロの E(1.5日) を縮めてみる
    e_half = [(i, n, 0.5 if i == "E" else d, dp) for i, n, d, dp in TASKS]
    report(e_half, "E を 1.5→0.5日 に縮めた")
