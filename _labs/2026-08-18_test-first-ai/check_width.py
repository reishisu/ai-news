"""output.txt の各行の「表示幅」を測る。

pytest は幅を文字数で数えるので、全角が混じると
COLUMNS=40 を指定しても表示上は超えることがある。
ここでは全角を2桁として数え直す。
"""
import sys
import unicodedata

LIMIT = 40


def width(s: str) -> int:
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1
               for c in s)


def main(path: str) -> int:
    over = []
    for i, line in enumerate(open(path, encoding="utf-8"), 1):
        line = line.rstrip("\n")
        if line.startswith("####"):  # ラボ用のラベル行は対象外
            continue
        w = width(line)
        if w > LIMIT:
            over.append((i, w, line))
    print(f"limit={LIMIT} over={len(over)}")
    for i, w, line in over:
        print(f"L{i} w={w} {line}")
    return 1 if over else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "output.txt"))
