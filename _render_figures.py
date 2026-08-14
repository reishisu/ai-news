#!/usr/bin/env python3
"""図版レンダラー — SVGソースをPNG画像に変換する。

各号の `contents/<号>/_figures/*.svg` を読み、ヘッドレスChromiumで
`contents/<号>/images/<名前>.png`(ライト)と `<名前>-dark.png`(ダーク)を
2倍解像度で書き出す。HTML側は <picture> で出し分ける。

SVGソースは以下のCSS変数を使って書く(色を直書きしない):
  --fg   本文色      --sub  補助色
  --new  強調バー色  --old  比較用の薄いバー色   --track バーの背景
  --b/--c/--a/--d    カテゴリ色
使い方: python3 _render_figures.py [号のディレクトリ名]
引数を省略すると全号を処理する(PNGが既にあり、SVGより新しい場合はスキップ)。
"""

import subprocess
import sys
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SECTION_DIRS = [HERE / "contents", HERE / "notes"]
CHROMIUM = "/opt/pw-browsers/chromium"
SCALE = 2

THEMES = {
    "": {  # ライト
        "bg": "#fcfcfb", "fg": "#14161a", "sub": "#5b6472",
        "new": "#2a78d6", "old": "#a9c9ef", "track": "#eceef2",
        "b": "#2a78d6", "c": "#eb6834", "a": "#1baf7a", "d": "#eda100",
    },
    "-dark": {
        "bg": "#191b1f", "fg": "#f2f4f8", "sub": "#aab3c0",
        "new": "#4a97ea", "old": "#4a6b8d", "track": "#2a2e35",
        "b": "#4a97ea", "c": "#f0784c", "a": "#26c08a", "d": "#e2a72c",
    },
}

WRAPPER = """<!doctype html><meta charset="utf-8">
<style>
  html, body {{ margin: 0; padding: 0; background: {bg}; }}
  svg {{ display: block; width: {w}px; height: {h}px;
    --bg: {bg}; --fg: {fg}; --sub: {sub};
    --new: {new}; --old: {old}; --track: {track};
    --b: {b}; --c: {c}; --a: {a}; --d: {d};
    font-family: system-ui, -apple-system, "Segoe UI", "Hiragino Sans", "Noto Sans JP", sans-serif;
  }}
</style>
{svg}
"""


def viewbox_size(svg_text, default=(640, 200)):
    m = re.search(r'viewBox\s*=\s*"([\d.\s-]+)"', svg_text)
    if not m:
        return default
    parts = m.group(1).split()
    if len(parts) != 4:
        return default
    try:
        return (round(float(parts[2])), round(float(parts[3])))
    except ValueError:
        return default


def crop(out_path, w, h):
    """余白付きで撮ったスクリーンショットを図版のサイズちょうどに切り詰める。

    Chromiumはウィンドウ高と内容高が同じだと下端を描画しないことがあるため、
    高さに余裕を持たせて撮影してから切り詰める。Pillowが無い環境では
    下に少し余白が残るが、背景色は図版と同じなので実害はない。
    """
    try:
        from PIL import Image
    except ImportError:
        return
    with Image.open(out_path) as im:
        im.crop((0, 0, w * SCALE, h * SCALE)).save(out_path)


def render(svg_path, out_path, theme_key):
    svg_text = svg_path.read_text(encoding="utf-8")
    w, h = viewbox_size(svg_text)
    palette = dict(THEMES[theme_key])
    html = WRAPPER.format(svg=svg_text, w=w, h=h, **palette)

    tmp_html = out_path.parent / f".render-{svg_path.stem}{theme_key}.html"
    tmp_html.write_text(html, encoding="utf-8")
    try:
        subprocess.run(
            [CHROMIUM, "--headless", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
             f"--force-device-scale-factor={SCALE}",
             f"--window-size={w},{h + 160}",
             f"--screenshot={out_path}",
             f"file://{tmp_html}"],
            check=True, capture_output=True, timeout=120,
        )
        crop(out_path, w, h)
    finally:
        tmp_html.unlink(missing_ok=True)


def process_issue(issue_dir):
    src_dir = issue_dir / "_figures"
    if not src_dir.is_dir():
        return 0
    out_dir = issue_dir / "images"
    out_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    for svg_path in sorted(src_dir.glob("*.svg")):
        for theme_key in THEMES:
            out_path = out_dir / f"{svg_path.stem}{theme_key}.png"
            if out_path.is_file() and out_path.stat().st_mtime >= svg_path.stat().st_mtime:
                continue
            render(svg_path, out_path, theme_key)
            print(f"生成: {out_path.relative_to(HERE)}")
            count += 1
    return count


def resolve(name):
    """号のディレクトリ名(または相対パス)を実際のパスに解決する。"""
    direct = HERE / name
    if direct.is_dir():
        return direct
    for base in SECTION_DIRS:
        if (base / name).is_dir():
            return base / name
    return direct


def main():
    targets = []
    if len(sys.argv) > 1:
        targets = [resolve(name) for name in sys.argv[1:]]
    else:
        for base in SECTION_DIRS:
            if base.is_dir():
                targets += [p for p in sorted(base.iterdir()) if p.is_dir()]

    total = 0
    for issue_dir in targets:
        if not issue_dir.is_dir():
            print(f"見つかりません: {issue_dir}", file=sys.stderr)
            continue
        total += process_issue(issue_dir)
    print(f"図版を{total}枚生成しました")


if __name__ == "__main__":
    main()
