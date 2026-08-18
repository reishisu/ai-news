#!/usr/bin/env python3
"""サムネイル用のキャラクター画像を取り込む。

用意した1枚のPNG(背景透過)を、そのままサムネイルに使える形に整えて
`_assets/character/` に置きます。やることは4つだけです。

1. 背景が透過しているか確かめる(透過していないと四角い板が右に出る)
2. まわりの透明な余白を切り落とす(余白があるぶん、キャラが小さく写る)
3. 大きすぎるものを縮める(サムネイルでは幅268px程度にしか出ないため)
4. サムネイル上で実際に何pxで出るか、文字の幅がどれだけ狭まるかを表示する

使い方:

    # 全カテゴリ共通で使う
    python3 _prepare_character.py ~/Downloads/chara.png

    # カテゴリ別に差し替える(そのカテゴリだけこちらが使われる)
    python3 _prepare_character.py ~/Downloads/chara_green.png クライアント技術

    # キャラ複数 × ポーズ複数(cast)に入れる。記事の日付で1枚が選ばれる
    python3 _prepare_character.py <画像> --cast hinata --as wave --matte

    # 背景を抜いてから取り込む(ComfyUI の素の出力など)
    python3 _prepare_character.py <画像> --rembg    # 影も抜ける(rembg が要る)
    python3 _prepare_character.py <画像> --matte    # 単色背景だけ(追加なしで動く)

    # いま置いてある画像を検査するだけ(書き換えない)
    python3 _prepare_character.py --check

取り込んだあとは、サムネイルを撮り直してから **Read で目視確認**してください。

    python3 _render_thumbs.py <記事ディレクトリ名>

権利について: 自作したもの、または権利が明確なものだけを置いてください。
他人のイラスト・参考にしたチャンネルのキャラクターは使えません(CLAUDE.md 第6節)。
"""

import sys
from pathlib import Path

from PIL import Image

from _render_thumbs import CAST_DIR, CHARA_DIR, CHARA_H, CHARA_W, THEMES, fit_chara

HERE = Path(__file__).resolve().parent

# 保存する高さの上限。サムネイル上では高さ660pxまでしか使わないので、
# その2倍あれば足りる。これ以上大きいと、PNGを毎回 base64 で埋め込むぶんだけ遅くなる。
MAX_STORE_H = 1320
# これを下回ると、縮小してもぼやける。
MIN_H = 500

VALID_NAMES = ["default"] + list(THEMES)


def cut_out(im):
    """背景除去モデル(rembg)で切り抜く。無ければ None を返す。

    `--matte` の塗りつぶしと違い、**床の影**と**脚の間のように囲まれた背景**も抜けます。
    ComfyUI の素の出力はどちらも出るので、入っているならこちらを使ってください。

        python3 -m pip install rembg onnxruntime

    初回はモデル(u2net, 176MB)を取りに行きます。以降は ~/.rembg に残ります。
    """
    try:
        from rembg import new_session, remove
    except ImportError:
        return None
    return remove(im, session=new_session("u2net"))


def matte(im, tol=32):
    """四隅と同じ色の背景を、外側から塗りつぶして透過にする。

    塗りは**外周から繋がっている部分だけ**に広げます。単純に「白い画素を全部消す」と
    白いシャツや目のハイライトまで穴が開くためです。

    単色・平坦な背景でしか綺麗に抜けません。髪の輪郭には背景色の縁が少し残ります。
    ComfyUI 側に背景除去のノード(rembg など)を入れているなら、そちらで透過PNGを
    書き出したほうが確実です。
    """
    from collections import deque

    w, h = im.size
    px = bytearray(im.tobytes())            # RGBA が1画素4バイトで並ぶ
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    ref = [sum(px[(y * w + x) * 4 + c] for x, y in corners) // 4 for c in range(3)]

    seen = bytearray(w * h)
    q = deque()

    def push(x, y):
        i = y * w + x
        if seen[i]:
            return
        j = i * 4
        if px[j + 3] == 0:                  # もともと透明なら塗る必要がない
            seen[i] = 1
            return
        if (abs(px[j] - ref[0]) + abs(px[j + 1] - ref[1]) + abs(px[j + 2] - ref[2])) > tol * 3:
            return
        seen[i] = 1
        q.append((x, y))

    for x in range(w):
        push(x, 0)
        push(x, h - 1)
    for y in range(h):
        push(0, y)
        push(w - 1, y)

    n = 0
    while q:
        x, y = q.popleft()
        px[(y * w + x) * 4 + 3] = 0
        n += 1
        if x > 0:
            push(x - 1, y)
        if x < w - 1:
            push(x + 1, y)
        if y > 0:
            push(x, y - 1)
        if y < h - 1:
            push(x, y + 1)

    out = Image.frombytes("RGBA", (w, h), bytes(px))
    return out, n / (w * h)


def alpha_report(im):
    """透過の状況を返す。(透明なピクセルの割合, アルファチャンネルの有無)"""
    if "A" not in im.getbands():
        return 0.0, False
    a = im.getchannel("A")
    hist = a.histogram()
    total = sum(hist)
    clear = sum(hist[:16])          # ほぼ透明とみなす
    return (clear / total if total else 0.0), True


def describe(path):
    """置いてある画像が、サムネイル上でどう出るかを表示する。"""
    with Image.open(path) as im:
        w, h = im.size
        ratio, has_alpha = alpha_report(im)
    disp_w, disp_h = fit_chara(w, h)
    print(f"  {path.name}: {w}x{h}px / 透明 {ratio * 100:.0f}%"
          f"{'' if has_alpha else ' (アルファチャンネル無し)'}")
    print(f"    サムネイル上: {disp_w}x{disp_h}px"
          f"  文字に使える幅が {disp_w}px 狭まります")
    if not has_alpha:
        print("    警告: 背景が透過していません。右に四角い板が出ます。")
    elif ratio < 0.05:
        print("    警告: 透明な部分がほとんどありません。書き出し設定を確認してください。")
    if h < MIN_H:
        print(f"    警告: 縦が{h}pxしかありません({MIN_H}px以上を推奨)。")


def prepare(src, dst, do_matte=False, tol=32, do_rembg=False):
    with Image.open(src) as raw:
        im = raw.convert("RGBA")
    before = im.size

    if do_rembg:
        cut = cut_out(im)
        if cut is None:
            print("中止: rembg が入っていません。次で入れるか、--matte を使ってください:",
                  file=sys.stderr)
            print("      python3 -m pip install rembg onnxruntime", file=sys.stderr)
            return 1
        im = cut
        ratio, _ = alpha_report(im)
        print(f"  背景を抜きました(rembg): 全体の {ratio * 100:.0f}% を透過にしました")
    elif do_matte:
        im, removed = matte(im, tol)
        print(f"  背景を抜きました: 全体の {removed * 100:.0f}% を透過にしました"
              f"(許容差 {tol})")
        if removed < 0.05:
            print("    警告: ほとんど抜けていません。背景が単色でないか、"
                  "--tolerance を上げる必要があります。")
    ratio, _ = alpha_report(im)

    if ratio < 0.02:
        print(f"中止: {src} は背景が透過していません(透明 {ratio * 100:.1f}%)。", file=sys.stderr)
        print("      背景透過のPNGで書き出し直してください。"
              "白背景のまま置くと、サムネイルの右に四角い板が出ます。", file=sys.stderr)
        print("      ・VRoid Studio: 「撮影・エクスポート」で背景を透過にして書き出す",
              file=sys.stderr)
        print("      ・ComfyUI の素の出力なら --rembg(影も抜ける) か --matte(単色のみ)",
              file=sys.stderr)
        return 1

    # 透明な余白を落とす。余白が入ったままだと、そのぶんキャラが小さく写る。
    box = im.getchannel("A").getbbox()
    if box and box != (0, 0, *im.size):
        im = im.crop(box)
        print(f"  透明な余白を切りました: {before[0]}x{before[1]} → {im.width}x{im.height}")

    if im.height > MAX_STORE_H:
        new_w = max(1, round(im.width * MAX_STORE_H / im.height))
        im = im.resize((new_w, MAX_STORE_H), Image.LANCZOS)
        print(f"  大きすぎるので縮めました: → {im.width}x{im.height}")
    elif im.height < MIN_H:
        print(f"  警告: 縦が{im.height}pxしかありません。"
              f"{MIN_H}px以上あるほうが綺麗です(拡大はしません)。")

    dst.parent.mkdir(parents=True, exist_ok=True)
    im.save(dst, "PNG", optimize=True)
    print(f"  保存しました: {dst.relative_to(HERE)} ({dst.stat().st_size // 1024}KB)")
    describe(dst)
    print()
    print("次にやること:")
    print("  python3 _render_thumbs.py <記事ディレクトリ名>   # 撮り直す")
    print("  そのあと images/thumb.png を Read で開いて目視確認する")
    return 0


def check():
    found = False
    if CAST_DIR.is_dir():
        for folder in sorted(p for p in CAST_DIR.iterdir() if p.is_dir()):
            shots = sorted(folder.glob("*.png"))
            if not shots:
                continue
            found = True
            print(f"{folder.relative_to(HERE)}: {len(shots)}枚 "
                  f"({', '.join(x.stem for x in shots)})")
            describe(shots[0])
    files = sorted(CHARA_DIR.glob("*.png")) if CHARA_DIR.is_dir() else []
    for f in files:
        found = True
        if f.stem not in VALID_NAMES:
            print(f"  {f.name}: この名前は使われません。"
                  f"使える名前: {' / '.join(n + '.png' for n in VALID_NAMES)}")
            continue
        describe(f)
    if not found:
        print(f"{CHARA_DIR.relative_to(HERE)} に画像はありません。"
              "キャラ無しで組まれます(文字が広く使えます)。")
    return 0


def main():
    argv = sys.argv[1:]
    flags = {"--cast": None, "--as": None, "--tolerance": "32"}
    args = []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in flags:
            i += 1
            flags[a] = argv[i] if i < len(argv) else None
        elif a.startswith("--tolerance="):
            flags["--tolerance"] = a.split("=", 1)[1]
        elif not a.startswith("--"):
            args.append(a)
        i += 1

    if "--check" in argv or not args:
        if not args:
            print(__doc__.strip().splitlines()[0])
            print(f"(表示できる箱は 幅{CHARA_W}px × 高さ{CHARA_H}px です)\n")
        return check()

    src = Path(args[0]).expanduser()
    if not src.is_file():
        print(f"中止: {src} がありません。", file=sys.stderr)
        return 1

    if flags["--cast"]:
        # キャラ複数 × ポーズ複数の置き場に入れる
        pose = flags["--as"] or src.stem
        dst = CAST_DIR / flags["--cast"] / f"{pose}.png"
    else:
        # 1キャラだけ置く従来の形
        name = args[1] if len(args) > 1 else "default"
        if name not in VALID_NAMES:
            print(f"中止: カテゴリ名 '{name}' は使えません。", file=sys.stderr)
            print(f"      使えるのは: {' / '.join(VALID_NAMES)}", file=sys.stderr)
            print("      キャラを複数置くなら --cast <キャラ名> --as <ポーズ名> です。",
                  file=sys.stderr)
            return 1
        dst = CHARA_DIR / f"{name}.png"

    return prepare(src, dst, do_matte="--matte" in argv, tol=int(flags["--tolerance"]),
                   do_rembg="--rembg" in argv)


if __name__ == "__main__":
    sys.exit(main())
