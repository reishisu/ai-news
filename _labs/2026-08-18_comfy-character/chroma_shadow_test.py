#!/usr/bin/env python3
"""chroma_cut の影抜きの検証。

    python3 _labs/2026-08-18_comfy-character/chroma_shadow_test.py

実機の候補(2026/8/18 のピンク背景移行時)で起きること
──「背景は抜けるが床の影が残る」「背景と同じ色味の小物に穴が開く」──を
合成画像で再現し、chroma_cut が次を満たすことを確かめる。

  1. 平坦な背景は完全に透明になる
  2. 床の影(背景が0.4〜0.9倍に暗くなった帯)も透明になる
  3. キャラ側の色(黒髪・茶髪・紺髪・金髪・白シャツ・肌・頬の赤み・緑の瞳)は
     不透明のまま残る(平均アルファ250以上)
  4. 背景と同じ色味の小物(ピンクの服など)には穴が開く
     ──これは仕様上の限界なので「開くこと」を確認して記録する

背景はピンク(新recipe)とオリーブ緑(移行前の実機出力で見た色)の2通りで回す。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from PIL import Image

from _prepare_character import chroma_cut, drop_islands

# キャラ側の色(採用画像から拾った代表値)と、背景に似せた危険色
PATCHES = {
    "黒髪":     (30, 30, 35),
    "茶髪":     (90, 60, 50),
    "紺髪":     (40, 60, 110),
    "金髪":     (240, 220, 150),
    "白シャツ": (240, 240, 245),
    "肌":       (250, 220, 200),
    "頬の赤み": (250, 180, 190),
    "緑の瞳":   (90, 160, 70),
}

BACKGROUNDS = {
    "ピンク(新recipe)": (243, 106, 167),
    "オリーブ緑(移行前の実機出力)": (168, 200, 50),
}

# パステルに振れた背景は色で抜いてはいけない(白シャツd=75・頬d=15まで近づく)。
# chroma_cut が None を返し、呼び出し側が birefnet に回すことを確かめる。
PASTELS = {
    "パステルピンク": (255, 183, 197),
    "パステル水色": (180, 235, 235),
}


def build(bg):
    """背景一色 + 下端に影の帯 + キャラ色のパッチ、の合成画像を作る。"""
    w, h = 768, 1344
    im = Image.new("RGBA", (w, h), (*bg, 255))
    px = im.load()
    # 床の影: 明るさ0.4〜0.9倍のグラデーション(実物の影は滑らかに減衰する)
    for y in range(1200, 1300):
        k = 0.4 + 0.5 * (y - 1200) / 100
        row = tuple(int(c * k) for c in bg)
        for x in range(200, 600):
            px[x, y] = (*row, 255)
    # キャラ色のパッチ(100x100)を等間隔に置く
    boxes = {}
    for n, (name, col) in enumerate(PATCHES.items()):
        x0, y0 = 80 + (n % 4) * 160, 200 + (n // 4) * 200
        for y in range(y0, y0 + 100):
            for x in range(x0, x0 + 100):
                px[x, y] = (*col, 255)
        boxes[name] = (x0, y0)
    # 背景に似た色の小物(穴が開くことを確認する側)
    near = tuple(min(255, int(c * 0.92)) for c in bg)
    for y in range(700, 800):
        for x in range(80, 180):
            px[x, y] = (*near, 255)
    boxes["背景に似た小物"] = (80, 700)
    # キャラ本体に相当する大きな塊(島落としの「最大成分」になる)
    for y in range(550, 1150):
        for x in range(300, 550):
            px[x, y] = (50, 50, 60, 255)
    # 本体から離れて浮く装飾マーク(実物: 白いハート・黄色い矢印)。
    # 背景色と違う色なので色では抜けず、島落としで消えるべきもの。
    marks = {"白いハート風": ((245, 245, 245), (620, 100)),
             "黄色い矢印風": ((250, 210, 60), (620, 620))}
    for name, (col, (x0, y0)) in marks.items():
        for y in range(y0, y0 + 40):
            for x in range(x0, x0 + 40):
                px[x, y] = (*col, 255)
    return im, boxes, marks


def mean_alpha(im, x0, y0, size=100):
    a = im.getchannel("A")
    total = 0
    for y in range(y0 + 10, y0 + size - 10):
        for x in range(x0 + 10, x0 + size - 10):
            total += a.getpixel((x, y))
    n = (size - 20) * (size - 20)
    return total / n


def main():
    failed = 0
    for bg_name, bg in BACKGROUNDS.items():
        im, boxes, marks = build(bg)
        out = chroma_cut(im)
        if out is None:
            print(f"NG {bg_name}: chroma_cut が None(彩度の判定に落ちた)")
            failed += 1
            continue
        out, dropped = drop_islands(out)
        print(f"== {bg_name} {bg} == (島落とし: {dropped}個)")
        checks = [
            ("平坦な背景", mean_alpha(out, 500, 60), "== 0"),
            ("床の影",     mean_alpha(out, 300, 1210, 80), "== 0"),
            ("本体の塊",   mean_alpha(out, 350, 700), ">= 250"),
        ]
        for name, (_, (x0, y0)) in marks.items():
            checks.append((f"浮遊マーク({name})", mean_alpha(out, x0, y0, 40), "== 0"))
        for name, (x0, y0) in boxes.items():
            checks.append((name, mean_alpha(out, x0, y0),
                           "穴が開く(仕様の限界)" if name == "背景に似た小物" else ">= 250"))
        for name, val, want in checks:
            if want == "== 0":
                ok = val < 1
            elif want == ">= 250":
                ok = val >= 250
            else:
                ok = val < 250        # 小物は「開くこと」を確認する
            mark = "OK" if ok else "NG"
            if not ok:
                failed += 1
            print(f"  {mark} {name:12s} 平均アルファ {val:6.1f}  期待: {want}")
    for bg_name, bg in PASTELS.items():
        im, _, _ = build(bg)
        out = chroma_cut(im)
        ok = out is None
        if not ok:
            failed += 1
        print(f"{'OK' if ok else 'NG'} {bg_name}: chroma_cut は None"
              f"(色では抜かず rembg に回す)  → 実際: {'None' if out is None else '抜いてしまった'}")
    print()
    print("結果:", "全て期待どおり" if failed == 0 else f"{failed}件が期待と違う")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
