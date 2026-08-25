#!/usr/bin/env python3
"""output.txt を読んで、結果の棒グラフSVGを書き出す。
数字を手で写さないため、記事の図は必ずこれで作る。"""
import re, sys

TITLES = {
    "1": "実験1  フォルダ名 release-check",
    "2": "実験2  フォルダ名 memo-1",
    "3": "実験3  自動起動を切る",
}


def parse(path):
    """[(実験番号, [(ラベル, 呼ばれた回数, 試行数), ...]), ...] を返す。"""
    out, cur = [], None
    for line in open(path, encoding="utf-8"):
        m = re.match(r"### 実験(\d)", line)
        if m:
            cur = (m.group(1), [])
            out.append(cur)
        m = re.match(r"--> (\S+ \S+) [o.]+ (\d+)/(\d+)", line)
        if m and cur:
            cur[1].append((m.group(1), int(m.group(2)), int(m.group(3))))
    return out


def svg(groups):
    X0, W, H = 190, 348, 26
    parts = [
        '<svg viewBox="0 0 640 %d" xmlns="http://www.w3.org/2000/svg" '
        'role="img">' % (44 + 98 * len(groups)),
        '<text x="10" y="24" font-size="15" font-weight="700" '
        'fill="var(--fg)">同じ質問を10回。スキルが自動で呼ばれた回数</text>',
    ]
    for i, (num, rows) in enumerate(groups):
        top = 44 + 98 * i
        parts.append(
            '<text x="10" y="%d" font-size="13" font-weight="700" '
            'fill="var(--fg)">%s</text>' % (top + 14, TITLES[num]))
        for j, (label, hit, n) in enumerate(rows):
            y = top + 24 + j * 34
            color = "var(--old)" if j == 0 else "var(--new)"
            parts += [
                '<text x="10" y="%d" font-size="12" fill="var(--sub)">%s</text>'
                % (y + 18, label),
                '<rect x="%d" y="%d" width="%d" height="%d" rx="6" '
                'fill="var(--track)"/>' % (X0, y, W, H),
            ]
            if hit:
                parts.append(
                    '<rect x="%d" y="%d" width="%.1f" height="%d" rx="6" '
                    'fill="%s"/>' % (X0, y, W * hit / n, H, color))
            parts.append(
                '<text x="%d" y="%d" font-size="12.5" font-weight="700" '
                'fill="var(--fg)">%d / %d</text>'
                % (X0 + W + 8, y + 18, hit, n))
    parts.append("</svg>")
    return "\n  ".join(parts) + "\n"


groups = parse(sys.argv[1])
open(sys.argv[2], "w", encoding="utf-8").write(svg(groups))
for num, rows in groups:
    print("実験%s: %s" % (num, "  ".join(
        "%s %d/%d" % (l, h, n) for l, h, n in rows)))
