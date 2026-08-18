#!/usr/bin/env python3
"""記事の video.json から、YouTube向けの動画(MP4)を組み立てる。

## 何をするか

1. `contents/<記事>/video.json`(読み上げ原稿。スライド構成つき)を読む
2. ローカルで起動している VOICEVOX Engine でナレーションを合成する
3. サムネイルと同じデザイン言語(配色・柄・キャラクター)でスライドHTMLを組み、
   headless Chromium で 1280x720 のPNGに撮影する
4. ffmpeg(imageio-ffmpeg 同梱のフルビルド)で H.264 + AAC のMP4に組み立てる

**乱数は使わない。** 同じ video.json・同じ音声モデルなら同じ動画になる
(サムネイルと同じ方針。背景の柄も記事の日付で決まる)。

## 前提

- VOICEVOX Engine が起動していること(既定 http://127.0.0.1:50021)。
  この環境には無いので、初回は _video/README.md の手順で取得して起動する
- pip: pillow, imageio-ffmpeg

## 使い方

```bash
python3 _render_video.py 2026-08-18_001
python3 _render_video.py 2026-08-18_001 --engine http://127.0.0.1:50021
```

出力は `_video_out/<記事>/` に中間物(スライドPNG・wav・読み仮名)、
`_video_out/<記事>.mp4` に完成品。`_video_out/` はコミットしない(.gitignore)。

読み仮名は `_video_out/<記事>/readings.json` に残す。**公開前に目を通すこと**
(固有名詞の読み間違いは、ここを見るのが一番早い)。
"""

import argparse
import base64
import html as htmlmod
import json
import subprocess
import sys
import urllib.parse
import urllib.request
import wave
from pathlib import Path

import _render_thumbs as thumbs

HERE = Path(__file__).resolve().parent
CONTENTS = HERE / "contents"
OUT_ROOT = HERE / "_video_out"
WIDTH, HEIGHT = 1280, 720
SITE_BASE = "https://reishisu.github.io/ai-news/"

# ナレーションの前後に入れる無音(秒)。スライドの切り替わりに息継ぎを作る。
PRE_SILENCE = 0.20
POST_SILENCE = 0.70


# ---------------------------------------------------------------- VOICEVOX

def engine_get(base, path):
    with urllib.request.urlopen(base + path, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def resolve_style(base, speaker_name, style_name):
    """話者名とスタイル名から、VOICEVOXのスタイルIDを引く。

    IDを直書きしないのは、エンジンの版で番号が増減しても
    名前なら安定して同じ声を指せるため。
    """
    for sp in engine_get(base, "/speakers"):
        if sp["name"] == speaker_name:
            for st in sp["styles"]:
                if st["name"] == style_name:
                    return st["id"]
            raise SystemExit(
                f"話者「{speaker_name}」にスタイル「{style_name}」がありません。"
                f" あるのは: {[s['name'] for s in sp['styles']]}")
    raise SystemExit(f"話者「{speaker_name}」がエンジンに見つかりません。")


def synthesize(base, style_id, text, speed, out_wav):
    """1スライドぶんのナレーションをwavにする。読み仮名を返す。"""
    q_url = (f"{base}/audio_query?speaker={style_id}"
             f"&text={urllib.parse.quote(text)}")
    req = urllib.request.Request(q_url, method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        query = json.loads(r.read().decode("utf-8"))
    query["speedScale"] = speed
    query["prePhonemeLength"] = PRE_SILENCE
    query["postPhonemeLength"] = POST_SILENCE
    req = urllib.request.Request(
        f"{base}/synthesis?speaker={style_id}",
        data=json.dumps(query).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=300) as r:
        out_wav.write_bytes(r.read())
    return query.get("kana", "")


def wav_seconds(path):
    with wave.open(str(path)) as w:
        return w.getnframes() / w.getframerate()


# ---------------------------------------------------------------- スライドHTML

def data_uri(path):
    b64 = base64.b64encode(Path(path).read_bytes()).decode("ascii")
    return f"data:image/png;base64,{b64}"


def base_css(t, dirname):
    """全スライド共通の枠。サムネイル(_render_thumbs.py)と同じ作り。"""
    pat_key, tone = thumbs.variant_for(dirname)
    pattern = thumbs.PATTERNS[pat_key].format(a=t["accent"])
    bg1 = thumbs._mix(t["bg1"], t["chip"], tone["mix"])
    bg2 = thumbs._mix(t["bg2"], t["accent"], tone["mix"] * 0.6)
    faces = (thumbs.font_face("NotoJP", "NotoSansJP-Black.ttf", 900)
             + thumbs.font_face("NotoJP", "NotoSansJP-Regular.ttf", 400))
    return f"""
{faces}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{WIDTH}px;height:{HEIGHT}px}}
body{{font-family:'NotoJP','IPAGothic',sans-serif;background:#000}}
.frame{{
  position:relative;width:{WIDTH}px;height:{HEIGHT}px;overflow:hidden;
  background:
    radial-gradient({tone['glow']}, {t['accent']}66 0%, transparent 56%),
    linear-gradient(135deg, {bg1} 0%, {bg2} 100%);
  border-top:26px solid #000;border-bottom:26px solid #000;
  border-left:12px solid {t['accent']};border-right:12px solid {t['accent']};
}}
.pat{{position:absolute;inset:0;background:{pattern};pointer-events:none}}
.shine{{
  position:absolute;inset:0;pointer-events:none;
  background:
    linear-gradient(108deg, transparent 30%, #ffffff26 42%, transparent 52%),
    linear-gradient(108deg, transparent 58%, #ffffff1a 66%, transparent 74%);
}}
.frame::before{{content:"";position:absolute;left:0;right:0;top:0;height:5px;background:{t['accent']}}}
.frame::after{{content:"";position:absolute;left:0;right:0;bottom:0;height:5px;background:{t['accent']}}}
.stack{{
  position:absolute;inset:0;z-index:3;
  padding:20px 34px 16px;display:flex;flex-direction:column;gap:12px;justify-content:center;
}}
.hook{{
  color:#ffe83d;font-weight:900;
  -webkit-text-stroke:10px #000;paint-order:stroke fill;
  filter:drop-shadow(0 0 12px #ffd21e) drop-shadow(0 4px 0 rgba(0,0,0,.5));
  letter-spacing:.01em;white-space:nowrap;overflow:hidden;
}}
.big{{
  font-weight:900;color:#fff;line-height:1.12;
  -webkit-text-stroke:var(--stroke-w,10px) var(--stroke-c,#000);paint-order:stroke fill;
  filter:
    drop-shadow(3px 0 0 #fff) drop-shadow(-3px 0 0 #fff)
    drop-shadow(0 3px 0 #fff) drop-shadow(0 -3px 0 #fff)
    drop-shadow(0 0 22px {t['accent']}) drop-shadow(0 8px 2px rgba(0,0,0,.6));
  /* 「レビュ/ー」のような語中改行を避ける(サムネイルで実証済みの組み合わせ)。
     auto-phrase が効かない環境でも break-word が安全網になる */
  overflow-wrap:break-word;word-break:auto-phrase;line-break:strict;
  letter-spacing:-.01em;
}}
.big em{{font-style:normal;color:#ffe83d}}
.cardline{{
  background:#fff;color:#111;font-weight:900;line-height:1.3;
  padding:14px 22px;border-radius:12px;
  box-shadow:0 5px 0 rgba(0,0,0,.55);
  overflow-wrap:break-word;word-break:auto-phrase;line-break:strict;
}}
.cardline .no{{color:{t['chip']};margin-right:10px}}
.chipname{{
  display:inline-block;background:{t['chip']};color:#fff;font-weight:900;font-size:26px;
  padding:6px 18px;border-radius:8px;box-shadow:0 3px 0 rgba(0,0,0,.5);white-space:nowrap;
}}
.figure{{
  border-radius:14px;border:4px solid #ffffff2e;background:#0b1020;
  box-shadow:0 10px 24px rgba(0,0,0,.45);object-fit:contain;
}}
.foot{{
  position:absolute;left:34px;right:34px;bottom:14px;z-index:4;
  display:flex;align-items:center;gap:14px;
}}
.cat{{
  background:{t['chip']};color:#fff;font-weight:900;font-size:22px;
  padding:6px 16px;border-radius:6px;white-space:nowrap;box-shadow:0 3px 0 rgba(0,0,0,.5);
}}
.site{{color:#ffffffbb;font-weight:900;font-size:19px;letter-spacing:.04em;white-space:nowrap}}
.pageno{{margin-left:auto;color:#ffffff99;font-weight:900;font-size:20px}}
.chara{{position:absolute;right:14px;bottom:26px;z-index:2;object-fit:contain}}
"""


def foot_html(cat, idx, total, e):
    return (f'<div class="foot"><span class="cat">{e(cat)}</span>'
            f'<span class="site">AIニュース デイリーダイジェスト</span>'
            f'<span class="pageno">{idx + 1} / {total}</span></div>')


def slide_body(slide, art_dir, dirname, cat, t, e):
    """スライト種別ごとの中身。foot以外を返す。"""
    kind = slide["kind"]
    heading = slide.get("heading", "")
    points = slide.get("points") or []

    if kind == "title":
        chara, chara_w = thumbs.character_img(cat, dirname)
        avail = WIDTH - 2 * 12 - 2 * 34 - chara_w
        hook_px = thumbs.size_for(heading, avail, 90, 64, 32, 1, 1.06)[0]
        sub = slide.get("sub", "")
        main_px, main_lines = thumbs.size_for(sub, avail, 380, 110, 48)
        stroke = max(9, int(main_px * 0.13))
        stroke_c = thumbs._mix(t["chip"], "#000000", 0.42)
        return f"""{chara}
<div class="stack" style="padding-right:{34 + chara_w}px">
  <div class="hook" style="font-size:{hook_px}px">{e(heading)}</div>
  <div class="big" style="font-size:{main_px}px;--stroke-w:{stroke}px;--stroke-c:{stroke_c};
       display:-webkit-box;-webkit-line-clamp:{main_lines};-webkit-box-orient:vertical;overflow:hidden">{e(sub)}</div>
</div>"""

    if kind in ("summary", "list"):
        rows = "".join(
            f'<div class="cardline" style="font-size:33px"><span class="no">{i + 1}</span>{e(p)}</div>'
            for i, p in enumerate(points))
        hook_px = thumbs.size_for(heading, WIDTH - 92, 70, 56, 30, 1, 1.06)[0]
        # 見出しは上に固定し、カードは残りの高さの中央に置く(下が空くと間延びする)
        return f"""
<div class="stack" style="justify-content:flex-start;padding-top:34px;gap:16px">
  <div class="hook" style="font-size:{hook_px}px">{e(heading)}</div>
  <div style="flex:1;display:flex;flex-direction:column;gap:18px;justify-content:center;padding-bottom:44px">{rows}</div>
</div>"""

    if kind == "topic":
        fig = slide.get("figure")
        fig_path = art_dir / fig if fig else None
        section = slide.get("section", "")
        stroke_c = thumbs._mix(t["chip"], "#000000", 0.42)
        head_px, head_lines = thumbs.size_for(heading, WIDTH - 92, 150, 62, 36, 2, 1.14)
        rows = "".join(
            f'<div class="cardline" style="font-size:30px">{e(p)}</div>' for p in points)
        if fig_path and fig_path.is_file():
            body = f"""
  <div style="display:flex;gap:22px;align-items:center;min-height:0;flex:1">
    <div style="display:flex;flex-direction:column;gap:14px;flex:1;min-width:0">{rows}</div>
    <img class="figure" src="{data_uri(fig_path)}"
         style="max-width:46%;max-height:430px;flex:0 0 auto">
  </div>"""
        else:
            body = f'<div style="display:flex;flex-direction:column;gap:16px;justify-content:center;flex:1">{rows}</div>'
        chip = f'<div><span class="chipname">{e(section)}</span></div>' if section else ""
        return f"""
<div class="stack" style="justify-content:flex-start;padding-top:26px;gap:14px">
  {chip}
  <div class="big" style="font-size:{head_px}px;--stroke-w:{max(7, int(head_px * 0.12))}px;--stroke-c:{stroke_c};
       display:-webkit-box;-webkit-line-clamp:{head_lines};-webkit-box-orient:vertical;overflow:hidden">{e(heading)}</div>
  {body}
</div>"""

    # outro
    chara, chara_w = thumbs.character_img(cat, dirname)
    avail = WIDTH - 2 * 12 - 2 * 34 - chara_w
    main_px = thumbs.size_for(heading, avail, 220, 120, 48, 2)[0]
    stroke_c = thumbs._mix(t["chip"], "#000000", 0.42)
    credit = slide.get("credit_line", "音声: VOICEVOX ずんだもん")
    return f"""{chara}
<div class="stack" style="padding-right:{34 + chara_w}px;gap:20px">
  <div class="big" style="font-size:{main_px}px;--stroke-w:{max(9, int(main_px * 0.13))}px;--stroke-c:{stroke_c}">{e(heading)}</div>
  <div class="cardline" style="font-size:30px;align-self:flex-start">記事全文・出典は概要欄から</div>
  <div style="color:#fff;font-weight:900;font-size:24px;text-shadow:0 2px 0 #000">{e(credit)}</div>
</div>"""


def slide_html(slide, art_dir, dirname, cat, idx, total):
    t = thumbs.THEMES.get(cat, thumbs.DEFAULT_THEME)
    e = htmlmod.escape
    return f"""<!doctype html><html lang="ja"><head><meta charset="utf-8"><style>
{base_css(t, dirname)}
</style></head><body><div class="frame">
  <div class="pat"></div>
  <div class="shine"></div>
  {slide_body(slide, art_dir, dirname, cat, t, e)}
  {foot_html(cat, idx, total, e)}
</div></body></html>"""


# ---------------------------------------------------------------- 組み立て

def find_ffmpeg():
    """フルビルドのffmpegを探す。

    Playwright同梱のffmpegは音声コーデックが入っていない削減ビルドなので使えない。
    imageio-ffmpeg(pip)のものは libx264 + AAC 入り(実測)。
    """
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        raise SystemExit("imageio-ffmpeg がありません: pip install imageio-ffmpeg")


def encode_segment(ffmpeg, png, wav, out_mp4):
    """静止画1枚 + 音声1本 → 1スライドぶんのMP4。"""
    run = subprocess.run(
        [ffmpeg, "-y", "-loop", "1", "-framerate", "30", "-i", str(png),
         "-i", str(wav),
         "-c:v", "libx264", "-preset", "medium", "-tune", "stillimage",
         "-crf", "20", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "128k",
         "-shortest", str(out_mp4)],
        capture_output=True, text=True)
    if run.returncode != 0:
        raise SystemExit(f"ffmpegが失敗: {out_mp4.name}\n{run.stderr[-1200:]}")


def concat_segments(ffmpeg, segs, out_mp4):
    lst = out_mp4.parent / "concat.txt"
    lst.write_text("".join(f"file '{s}'\n" for s in segs), encoding="utf-8")
    run = subprocess.run(
        [ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
         "-c", "copy", "-movflags", "+faststart", str(out_mp4)],
        capture_output=True, text=True)
    if run.returncode != 0:
        raise SystemExit(f"ffmpeg(concat)が失敗\n{run.stderr[-1200:]}")


def youtube_meta(meta, video, dirname, total_sec):
    """アップロード用のタイトル・説明欄を video.json と meta.json から組む。

    説明欄には記事URLとVOICEVOXのクレジット(利用規約で必要)を必ず入れる。
    """
    url = f"{SITE_BASE}contents/{dirname}/"
    desc = (f"{meta.get('summary', '')}\n\n"
            f"記事全文(出典・参考文献つき):\n{url}\n\n"
            f"※この動画は上記記事(一次資料を確認して執筆)をもとに、"
            f"読み上げ原稿を人が確認したうえで生成しています。\n\n"
            f"音声: {video.get('credit', 'VOICEVOX:ずんだもん')}\n")
    return {
        "title": meta.get("title", dirname),
        "description": desc,
        "tags": (meta.get("tags") or [])[:10],
        "categoryId": "28",
        "privacyStatus": "private",
        "durationSec": round(total_sec, 1),
    }


def render(dirname, engine):
    art_dir = CONTENTS / dirname
    video = json.loads((art_dir / "video.json").read_text(encoding="utf-8"))
    meta = json.loads((art_dir / "meta.json").read_text(encoding="utf-8"))
    cat = meta.get("category", "デイリーダイジェスト")
    voice = video.get("voice", {})
    speed = float(voice.get("speed", 1.1))
    style_id = resolve_style(engine, voice.get("speaker", "ずんだもん"),
                             voice.get("style", "ノーマル"))

    work = OUT_ROOT / dirname
    work.mkdir(parents=True, exist_ok=True)
    ffmpeg = find_ffmpeg()
    slides = video["slides"]
    total = len(slides)
    readings, segs, total_sec = [], [], 0.0

    for i, slide in enumerate(slides):
        png = work / f"slide-{i:02d}.png"
        wav = work / f"slide-{i:02d}.wav"
        seg = work / f"seg-{i:02d}.mp4"
        kana = synthesize(engine, style_id, slide["narration"], speed, wav)
        sec = wav_seconds(wav)
        total_sec += sec
        readings.append({"slide": i, "heading": slide.get("heading", ""),
                         "sec": round(sec, 2), "kana": kana})
        html = slide_html(slide, art_dir, dirname, cat, i, total)
        if not thumbs.shoot(html, png, WIDTH, HEIGHT):
            raise SystemExit(f"スライド{i}の撮影に失敗")
        encode_segment(ffmpeg, png, wav, seg)
        segs.append(seg)
        print(f"  slide {i + 1}/{total}: {sec:5.1f}秒  {slide.get('heading', '')[:24]}")

    out_mp4 = OUT_ROOT / f"{dirname}.mp4"
    concat_segments(ffmpeg, segs, out_mp4)
    (work / "readings.json").write_text(
        json.dumps(readings, ensure_ascii=False, indent=1), encoding="utf-8")
    (work / "youtube.json").write_text(
        json.dumps(youtube_meta(meta, video, dirname, total_sec),
                   ensure_ascii=False, indent=1), encoding="utf-8")
    mb = out_mp4.stat().st_size / 1e6
    print(f"完成: {out_mp4}  {total_sec / 60:.1f}分  {mb:.1f}MB")
    print(f"読み仮名: {work / 'readings.json'} を確認すること")
    return out_mp4


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dirname", help="記事ディレクトリ名 (例: 2026-08-18_001)")
    ap.add_argument("--engine", default="http://127.0.0.1:50021")
    args = ap.parse_args()
    if not (CONTENTS / args.dirname / "video.json").is_file():
        raise SystemExit(f"{args.dirname}/video.json がありません")
    try:
        ver = engine_get(args.engine, "/version")
    except OSError:
        raise SystemExit(
            f"VOICEVOX Engine に繋がりません ({args.engine})。"
            " _video/README.md の手順で起動してください。")
    print(f"VOICEVOX Engine {ver} / {args.dirname}")
    render(args.dirname, args.engine)


if __name__ == "__main__":
    main()
