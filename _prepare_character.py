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

from _render_thumbs import (CAST_DIR, CHARA_CROP, CHARA_DIR, CHARA_H, CHARA_W,
                            THEMES, chara_view)

HERE = Path(__file__).resolve().parent

# 保存する高さの上限。サムネイル上では高さ660pxまでしか使わないので、
# その2倍あれば足りる。これ以上大きいと、PNGを毎回 base64 で埋め込むぶんだけ遅くなる。
MAX_STORE_H = 1320
# これを下回ると、縮小してもぼやける。
MIN_H = 500

VALID_NAMES = ["default"] + list(THEMES)


def chroma_cut(im, lo=40, hi=100):
    """背景が彩色一色(ピンク・緑など)のときの切り抜き。色の距離だけで抜くので、
    髪と肩の間のような**囲まれた背景も完全に消える**。

    背景色は四隅から取る。lo/hi は「背景色からの距離」のしきい値で、
    lo 以下は完全に透明、hi 以上は完全に不透明、間は滑らかに繋ぐ
    (髪の輪郭のアンチエイリアスを保つため)。
    縁に残る背景色かぶりは、背景の最強チャンネルが他の2つを超えないよう抑える。

    **床の影も抜く。** 影は「背景と同じ色味のまま暗くなった画素」なので、
    色の距離では背景から遠くなり(実測でd=100超)、素朴な比較では残ってしまう。
    そこで明るさの比を背景に合わせてから比べ直し、比を合わせると背景と
    一致する画素だけを透明にする。黒髪・茶髪のような「ただ暗い画素」を
    巻き込まないよう、(1)最強・最弱チャンネルの向きが背景と同じ
    (2)彩度が明るさ相応にある、の2条件を付けている。
    検証: _labs/2026-08-18_comfy-character/chroma_shadow_test.py
    """
    im = im.convert("RGBA")
    w, h = im.size
    px = bytearray(im.tobytes())
    corners = [(3, 3), (w - 4, 3), (3, h - 4), (w - 4, h - 4)]
    bg = [sorted(px[(y * w + x) * 4 + c] for x, y in corners)[2] for c in range(3)]
    spread = max(bg) - min(bg)
    # 90未満は「彩色」と確信できないので色では抜かない(呼び出し側が rembg に回す)。
    # パステルに振れた背景は白い服(d=75)や頬の赤み(d=15)と近くなり、
    # 色で抜くと本体に穴が開くため(距離はL1の実測値)。
    if spread < 90:
        return None
    sb = bg[0] + bg[1] + bg[2]
    hi_ch = bg.index(max(bg))
    lo_ch = bg.index(min(bg))
    oth = [c for c in (0, 1, 2) if c != hi_ch]
    for i in range(w * h):
        j = i * 4
        c3 = (px[j], px[j + 1], px[j + 2])
        d = (abs(c3[0] - bg[0]) + abs(c3[1] - bg[1]) + abs(c3[2] - bg[2]))
        if d > lo:
            # 影の判定(docstring参照)。k は背景に対する明るさの比(256倍固定小数)
            k = (c3[0] + c3[1] + c3[2]) * 256 // sb
            if (77 <= k <= 269
                    and max(c3) == c3[hi_ch] and min(c3) == c3[lo_ch]
                    and (max(c3) - min(c3)) * 256 >= spread * k * 7 // 10):
                d2 = (abs(c3[0] - bg[0] * k // 256) + abs(c3[1] - bg[1] * k // 256)
                      + abs(c3[2] - bg[2] * k // 256))
                if d2 <= lo * k // 256 + 12:
                    d = 0                    # 暗くなっただけの背景=影
        if d <= lo:
            px[j + 3] = 0
        elif d < hi:
            a = (d - lo) * 255 // (hi - lo)
            px[j + 3] = min(px[j + 3], a)
            m = max(c3[oth[0]], c3[oth[1]])
            if c3[hi_ch] > m:               # 縁の背景色かぶりを抑える
                px[j + hi_ch] = m
    return Image.frombytes("RGBA", (w, h), bytes(px))


def drop_islands(im, keep_ratio=0.05, thresh=16):
    """本体から離れた小さな不透明の塊(装飾マーク)を消す。

    生成画像には、キャラの周りに装飾マークが浮くことがある(2026/8/19 の
    候補25枚では5人中3人に。白いハート・黄色い矢印・キラキラ)。背景色とは
    色が違うので色抜きでは消えず、モデルの背景除去でも残ることがある。
    アルファが thresh を超える画素の連結成分を取り、最大成分(=キャラ本体。
    一繋がりなので必ず最大になる)の keep_ratio 未満の成分を透明にする。
    """
    im = im.convert("RGBA")
    w, h = im.size
    a = im.getchannel("A").tobytes()
    label = [0] * (w * h)
    sizes = [0]
    nid = 0
    for start in range(w * h):
        if a[start] <= thresh or label[start]:
            continue
        nid += 1
        stack = [start]
        label[start] = nid
        n = 0
        while stack:
            p = stack.pop()
            n += 1
            x = p % w
            if x and not label[p - 1] and a[p - 1] > thresh:
                label[p - 1] = nid
                stack.append(p - 1)
            if x < w - 1 and not label[p + 1] and a[p + 1] > thresh:
                label[p + 1] = nid
                stack.append(p + 1)
            if p >= w and not label[p - w] and a[p - w] > thresh:
                label[p - w] = nid
                stack.append(p - w)
            if p < w * (h - 1) and not label[p + w] and a[p + w] > thresh:
                label[p + w] = nid
                stack.append(p + w)
        sizes.append(n)
    if nid <= 1:
        return im, 0
    floor_px = max(sizes) * keep_ratio
    keep = {i for i, s in enumerate(sizes) if i and s >= floor_px}
    if len(keep) == nid:
        return im, 0
    px = bytearray(im.tobytes())
    for p in range(w * h):
        if label[p] and label[p] not in keep:
            px[p * 4 + 3] = 0
    return Image.frombytes("RGBA", (w, h), bytes(px)), nid - len(keep)


def chroma_assist(out, src, lo=40):
    """モデルの切り抜き結果に対して、**確実に背景色の画素だけ**を追加で透明にする。

    髪と肩の間のような「囲まれた背景」をモデルが取り残したときの保険。
    部分透過はさせない(lo 以下の完全一致だけ)。肌と背景の距離は実測で
    81以上あるので、この条件では本体に触れない。
    """
    w, h = src.size
    pix = src.convert("RGBA").load()
    corners = [(3, 3), (w - 4, 3), (3, h - 4), (w - 4, h - 4)]
    bg = [sorted(pix[x, y][c] for x, y in corners)[2] for c in range(3)]
    if max(bg) - min(bg) < 90:
        return out, 0          # 背景が彩色と確信できないときは何もしない
    px = bytearray(out.convert("RGBA").tobytes())
    n = 0
    for i in range(w * h):
        j = i * 4
        if px[j + 3] == 0:
            continue
        s = pix[i % w, i // w]
        if abs(s[0] - bg[0]) + abs(s[1] - bg[1]) + abs(s[2] - bg[2]) <= lo:
            px[j + 3] = 0
            n += 1
    return Image.frombytes("RGBA", out.size, bytes(px)), n


def cut_out(im):
    """背景除去モデル(rembg)で切り抜く。無ければ色だけで抜くことを試す。

    `--matte` の塗りつぶしと違い、**床の影**と**脚の間のように囲まれた背景**も抜けます。
    ComfyUI の素の出力はどちらも出るので、入っているならこちらを使ってください。

        python3 -m pip install rembg onnxruntime

    初回はモデル(birefnet-general-lite, 224MB)を取りに行きます。以降は ~/.rembg に残ります。

    主経路をモデル(birefnet)にしている理由(2026/8/19 のピンク背景の実測):
    実際の背景は淡いピンク((248,151,190)など)に振れることがあり、暖色の肌との
    L1距離が81〜96まで縮む。色だけで抜くと肌が半透明に食われ、影の残渣も出た。
    モデルは「肌はキャラ」だと分かるのでこの問題が無い。色は、モデルが
    取り残した「確実な背景色」を消す補助(chroma_assist)に使う。
    """
    try:
        from rembg import new_session, remove
    except ImportError:
        # rembg が無いときだけ色で抜く。背景が鮮やかなら使えるが、
        # 淡い背景では肌が半透明になる危険がある(上記)。目視確認すること。
        keyed = chroma_cut(im)
        if keyed is None:
            return None
        keyed, dropped = drop_islands(keyed)
        if dropped:
            print(f"  キャラから離れて浮いていた装飾マークを{dropped}個消しました")
        print("  注意: rembg が無いため色だけで抜きました。肌の透け・影の残りを目視確認してください。")
        return keyed
    # birefnet-general-lite を使う。4つ実測して決めた:
    #   u2net            … 髪の外周に白いモヤが残る
    #   isnet-anime      … 外周は綺麗だが、髪と肩の間のような「囲まれた背景」を残す
    #   birefnet-general … 囲まれた背景まで抜けるが、推論中に約14GB使いOOMで落ちた
    #   birefnet-general-lite … 品質は同等で約7.6GB(採用)
    # 白背景では「囲まれた背景」を色で消すのは不可能(池も白い服も同じ白。実測)。
    # いまは背景がピンクなので、取り残しは chroma_assist が色で消せる。
    out = remove(im, session=new_session("birefnet-general-lite"))
    out, pooled = chroma_assist(out, im)
    if pooled:
        print(f"  モデルが取り残した背景色の画素を{pooled}個消しました")
    out, dropped = drop_islands(out)
    if dropped:
        print(f"  キャラから離れて浮いていた装飾マークを{dropped}個消しました")
    return out


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
    # サムネイルでは上から CHARA_CROP のぶん(胸から上)だけを使うので、
    # 表示サイズもその切り出し後で出す(_render_thumbs と同じ計算)。
    _, disp_w, disp_h = chara_view(path)
    print(f"  {path.name}: {w}x{h}px / 透明 {ratio * 100:.0f}%"
          f"{'' if has_alpha else ' (アルファチャンネル無し)'}")
    print(f"    サムネイル上: {disp_w}x{disp_h}px"
          f"(上から{CHARA_CROP * 100:.0f}%を使用)"
          f"  文字の幅が {disp_w}px 狭まります")
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
            print(f"(表示できる箱は 幅{CHARA_W}px × 高さ{CHARA_H}px。"
                  f"元画像の上から{CHARA_CROP * 100:.0f}%だけを使います)\n")
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
