#!/usr/bin/env python3
"""ターミナル出力を幅40桁に折り返す（記事に貼るため）。

- 語の途中では折らない。継続行は2スペース字下げ。
- **文言は1文字も変えない。** 折り返しを入れるだけ。
- 生の出力は run_tests.sh の NARROW=0 で取れる（output-raw.txt）。
"""
import sys
import textwrap

W = 40

for line in sys.stdin.read().splitlines():
    if len(line) <= W:
        print(line)
        continue
    print("\n".join(textwrap.wrap(
        line, width=W, subsequent_indent="  ",
        break_long_words=False, break_on_hyphens=False,
    )))
