#!/usr/bin/env python3
"""ComfyUI にキャラクター画像を作らせて、候補として持ってくる。

**ComfyUI はGPUのある手元のPCで動かしてください。** このスクリプトは
「動いている ComfyUI にHTTPで投げて、出てきたPNGを受け取る」だけです。
生成そのものはしません(この記事サイトの実行環境にGPUはありません)。

カテゴリごとに担当のキャラを決め(`recipe.json` の `cast`)、それぞれに
ポーズ・衣装の違い(`variations`)を作ります。5人 × 5種なら25枚です。

- 生成の設定(モデル名・プロンプト・seed)は `recipe.json` に書いて**コミットする**
- モデルのファイルそのものはコミットしない(数GBあり、ライセンスもまちまち)
- 生成は人が手で走らせて、**出てきた候補から人が選ぶ**
- 日次のサムネイル生成(`_render_thumbs.py`)は置いてある画像を読むだけで、生成には触らない

使い方:

    # 1. 手元で ComfyUI を起動しておく(既定は http://127.0.0.1:8188)
    # 2. つながるか・必要なモデルがあるかを見る
    python3 _comfy_character.py --check

    # 3. 全員 × 全ポーズを作る(recipe.json のとおり)
    python3 _comfy_character.py

    # 一部だけ作り直す
    python3 _comfy_character.py --who hinata            # このキャラだけ
    python3 _comfy_character.py --pose wave             # このポーズだけ
    python3 _comfy_character.py --who hinata --pose wave

    # 気に入らないときは seed を全体ごとずらす
    python3 _comfy_character.py --who hinata --seed-offset 100

    # モデルだけ一時的に変えて試す(recipe.json は書き換えない)
    python3 _comfy_character.py --pose wave --checkpoint animagineXL40_v4Opt.safetensors

受け取った画像は `_assets/character/_candidates/<キャラ名>/<ポーズ名>.png` に置きます。
選んだものを次で取り込みます。

    python3 _prepare_character.py <画像> --cast <キャラ名> --as <ポーズ名> --matte

接続先を変えるとき:

    COMFY_URL=http://127.0.0.1:8001 python3 _comfy_character.py
    python3 _comfy_character.py --url http://127.0.0.1:8001

顔を揃えるとき(IPAdapter)。**ワークフローを自分で組む必要はありません。**
こちらで組み立てて、投げる前にノードとモデルの有無を確かめます:

    python3 _comfy_character.py --face                     # 全員、基準の顔に揃えて作り直す
    python3 _comfy_character.py --face --who hinata        # 1人だけ
    python3 _comfy_character.py --face --weight 0.6        # 効きを弱める(既定 0.8)
    python3 _comfy_character.py --face --reference 基準.png --who hinata  # 基準を指定

基準の顔は、採用済みの絵 `_assets/character/cast/<キャラ>/wave.png` を自動で使います
(recipe の cast[].face でポーズ名を変えられます)。

自分で組んだワークフローを使いたいときだけ(ComfyUI の
「ワークフロー → API形式でエクスポート」で書き出したJSON。**UI形式ではありません**):

    python3 _comfy_character.py --workflow ipadapter.api.json --reference base.png

`--workflow` を渡すと、その中の KSampler(seed)・EmptyLatentImage(サイズ)・
CLIPTextEncode(プロンプト)・LoadImage(参照画像)を差し替えて投げます。

APIの仕様は ComfyUI 本体のソースで確認しています(server.py / execution.py / nodes.py)。

    POST /prompt          {"prompt": <API形式のワークフロー>, "client_id": ...}
                          → {"prompt_id": ..., "number": ..., "node_errors": {...}}
                          検証に落ちると 400 で {"error": ..., "node_errors": {...}}
    GET  /history/<id>    → {<id>: {"outputs": {<ノードID>: {"images": [...]}},
                                    "status": {"status_str": "success"|"error",
                                               "completed": true|false,
                                               "messages": [...]}}}
    GET  /view?filename=&subfolder=&type=output   → 画像そのもの
    POST /upload/image    multipart の image(ファイル) / type / subfolder / overwrite
                          → {"name": ..., "subfolder": ..., "type": ...}
    GET  /object_info     → 入っているノードと、選べるモデル名の一覧
    GET  /system_stats    → 動いているかの確認に使う

権利について: 自作したもの、または権利が明確なものだけを置いてください。
特定の作品のキャラクターを狙って出すプロンプト・LoRAは使えません(CLAUDE.md 第6節)。
"""

import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
COMFY_DIR = HERE / "_assets" / "character" / "comfy"
RECIPE = COMFY_DIR / "recipe.json"
WORKFLOW = COMFY_DIR / "character.api.json"
CANDIDATES = HERE / "_assets" / "character" / "_candidates"
DEFAULT_URL = os.environ.get("COMFY_URL", "http://127.0.0.1:8188")
TIMEOUT = 15          # 1リクエストの上限(秒)
POLL_LIMIT = 1800     # 生成待ちの上限(秒)。1枚あたり数十秒〜数分かかる


def api(url, path, data=None, raw=False, timeout=TIMEOUT, body=None, ctype=None):
    """ComfyUI に1回リクエストする。data(JSON) か body(生バイト) があれば POST。"""
    req = urllib.request.Request(url.rstrip("/") + path)
    if data is not None:
        req.data = json.dumps(data).encode("utf-8")
        req.add_header("Content-Type", "application/json")
    elif body is not None:
        req.data = body
        req.add_header("Content-Type", ctype)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        out = r.read()
    return out if raw else json.loads(out.decode("utf-8"))


def png_has_alpha(path):
    """PNGにアルファチャンネルがあるかを、ヘッダだけ読んで判定する(標準ライブラリのみ)。

    IHDR の color type が 4(グレー+α) か 6(RGBA) なら透過あり。
    """
    head = Path(path).read_bytes()[:33]
    return len(head) >= 26 and head[25] in (4, 6)


def flatten_reference(path):
    """基準にする画像が透過PNGなら、白背景に合成した一時ファイルを返す。

    **透過のまま参照に渡すと、壊れた絵が出ます(実機で発生)。**
    ComfyUI の LoadImage は画像を RGB に変換するだけなので、透明部分の
    下に残っている色がそのまま「参照すべき絵」として IPAdapter に入るためです。
    背景除去(rembg)を通した cast の絵はすべて透過なので、ここで必ず埋めます。

    合成には Pillow が要ります。無ければ None を返すので、呼び出し側で止めること。
    """
    path = Path(path)
    if not png_has_alpha(path):
        return path
    try:
        from PIL import Image
    except ImportError:
        return None
    import tempfile
    with Image.open(path) as im:
        im = im.convert("RGBA")
        bg = Image.new("RGB", im.size, (255, 255, 255))
        bg.paste(im, (0, 0), im)
    tmp = Path(tempfile.mkstemp(suffix=".png")[1])
    bg.save(tmp, "PNG")
    return tmp


def upload_reference(url, path):
    """基準の画像を、透過を白で埋めてから ComfyUI に送る。"""
    flat = flatten_reference(path)
    if flat is None:
        print(f"中止: {path} は透過PNGです。透過のまま参照に渡すと壊れた絵が出るため、",
              file=sys.stderr)
        print("      白背景に合成してから送る必要があります。次のどちらかで:", file=sys.stderr)
        print("        python3 -m pip install pillow   # 自動で合成できるようになる",
              file=sys.stderr)
        print("        --reference で背景付き(生成直後)の画像を渡す", file=sys.stderr)
        return None
    if flat != Path(path):
        print(f"  (透過を白背景で埋めました: {Path(path).name})")
    return upload_image(url, flat)


def upload_image(url, path):
    """画像を ComfyUI の input フォルダに送る。LoadImage から使えるようになる。

    multipart/form-data を手で組んでいます(標準ライブラリだけで動かすため)。
    戻り値は LoadImage の `image` に入れる文字列。
    """
    path = Path(path)
    boundary = "----ai-news-" + uuid.uuid4().hex
    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    parts = []
    for key, val in (("type", "input"), ("overwrite", "true")):
        parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{key}\"\r\n\r\n"
                     f"{val}\r\n".encode("utf-8"))
    parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"image\"; "
                 f"filename=\"{path.name}\"\r\nContent-Type: {mime}\r\n\r\n".encode("utf-8"))
    parts.append(path.read_bytes())
    parts.append(f"\r\n--{boundary}--\r\n".encode("utf-8"))
    res = api(url, "/upload/image", body=b"".join(parts),
              ctype=f"multipart/form-data; boundary={boundary}", timeout=120)
    name, sub = res.get("name", path.name), res.get("subfolder", "")
    return f"{sub}/{name}" if sub else name


def load_recipe(path=None):
    path = Path(path) if path else RECIPE
    if not path.is_file():
        print(f"中止: {path} がありません。", file=sys.stderr)
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def jobs_from(recipe, who=None, pose=None, offset=0):
    """作るものの一覧を組み立てる。(キャラ, ポーズ, プロンプト, seed) の並び。

    seed は『キャラの seed + ポーズの並び順 + --seed-offset』です。
    乱数は使わないので、同じ recipe なら何度でも同じ絵になります。
    """
    out = []
    cast = recipe.get("cast") or [{"name": "default", "seed": recipe.get("seed", 1),
                                   "tags": "", "category": ""}]
    variations = recipe.get("variations") or [{"name": "base", "tags": ""}]
    for c in cast:
        if who and c["name"] != who:
            continue
        for i, v in enumerate(variations):
            if pose and v["name"] != pose:
                continue
            prompt = ", ".join(x for x in (recipe.get("quality"), recipe.get("subject"),
                                           c.get("tags"), v.get("tags"),
                                           recipe.get("framing")) if x)
            out.append({"who": c["name"], "pose": v["name"], "category": c.get("category", ""),
                        "positive": prompt, "seed": int(c.get("seed", 1)) + i + offset})
    return out


def build_workflow(recipe, job):
    """API形式のワークフローを組み立てる。

    使うのは ComfyUI の標準ノードだけです(追加のカスタムノードは要りません)。
    チェックポイント読み込み → プロンプト2つ → 空のラテント → サンプラー →
    VAEでデコード → 保存、という素の txt2img です。
    """
    return {
        "1": {"class_type": "CheckpointLoaderSimple",
              "inputs": {"ckpt_name": recipe["checkpoint"]}},
        "2": {"class_type": "CLIPTextEncode",
              "inputs": {"text": job["positive"], "clip": ["1", 1]}},
        "3": {"class_type": "CLIPTextEncode",
              "inputs": {"text": recipe["negative"], "clip": ["1", 1]}},
        "4": {"class_type": "EmptyLatentImage",
              "inputs": {"width": recipe["width"], "height": recipe["height"],
                         "batch_size": 1}},
        "5": {"class_type": "KSampler",
              "inputs": {"seed": job["seed"], "steps": recipe["steps"],
                         "cfg": recipe["cfg"], "sampler_name": recipe["sampler"],
                         "scheduler": recipe["scheduler"], "denoise": 1.0,
                         "model": ["1", 0], "positive": ["2", 0],
                         "negative": ["3", 0], "latent_image": ["4", 0]}},
        "6": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": ["1", 2]}},
        "7": {"class_type": "SaveImage",
              "inputs": {"filename_prefix": "ai-news-chara", "images": ["6", 0]}},
    }


# IPAdapter で顔を揃えるときの既定値。
# weight は配布元(cubiq/ComfyUI_IPAdapter_plus)の README が
# 「まず 0.8 以下に下げるとよい」としているのに合わせている。
IPA_PRESET = "PLUS FACE (portraits)"
IPA_WEIGHT = 0.8


def build_ipadapter_workflow(recipe, job, reference, weight=IPA_WEIGHT, preset=IPA_PRESET):
    """基準の1枚を参照して顔を揃える版のワークフローを組み立てる。

    素の txt2img(build_workflow)との違いは、モデルが KSampler に届くまでに
    IPAdapter を1つ挟むところだけです。

        CheckpointLoaderSimple ─┬─→ IPAdapterUnifiedLoader ─→ IPAdapter ─→ KSampler
                                └─→ CLIPTextEncode ×2 ────────────────────↗
        LoadImage(基準の顔) → PrepImageForClipVision(上を切り出す) ────↗

    PrepImageForClipVision を挟むのは、参照画像が**全身の立ち絵**だからです。
    IPAdapter は画像を224pxの正方形にして読むので、全身のまま渡すと顔の情報が薄まります。
    `crop_position="top"` で頭の側だけを渡します。

    ノードの入出力は配布元の IPAdapterPlus.py で確認しています
    (IPAdapterUnifiedLoader → (MODEL, IPADAPTER)、IPAdapterSimple の入力は
     model / ipadapter / image / weight / start_at / end_at / weight_type)。
    """
    return {
        "1": {"class_type": "CheckpointLoaderSimple",
              "inputs": {"ckpt_name": recipe["checkpoint"]}},
        "2": {"class_type": "LoadImage", "inputs": {"image": reference}},
        "3": {"class_type": "PrepImageForClipVision",
              "inputs": {"image": ["2", 0], "interpolation": "LANCZOS",
                         "crop_position": "top", "sharpening": 0.0}},
        "4": {"class_type": "IPAdapterUnifiedLoader",
              "inputs": {"model": ["1", 0], "preset": preset}},
        "5": {"class_type": "IPAdapter",
              "inputs": {"model": ["4", 0], "ipadapter": ["4", 1], "image": ["3", 0],
                         "weight": weight, "start_at": 0.0, "end_at": 1.0,
                         "weight_type": "standard"}},
        "6": {"class_type": "CLIPTextEncode",
              "inputs": {"text": job["positive"], "clip": ["1", 1]}},
        "7": {"class_type": "CLIPTextEncode",
              "inputs": {"text": recipe["negative"], "clip": ["1", 1]}},
        "8": {"class_type": "EmptyLatentImage",
              "inputs": {"width": recipe["width"], "height": recipe["height"],
                         "batch_size": 1}},
        "9": {"class_type": "KSampler",
              "inputs": {"seed": job["seed"], "steps": recipe["steps"],
                         "cfg": recipe["cfg"], "sampler_name": recipe["sampler"],
                         "scheduler": recipe["scheduler"], "denoise": 1.0,
                         "model": ["5", 0], "positive": ["6", 0],
                         "negative": ["7", 0], "latent_image": ["8", 0]}},
        "10": {"class_type": "VAEDecode", "inputs": {"samples": ["9", 0], "vae": ["1", 2]}},
        "11": {"class_type": "SaveImage",
               "inputs": {"filename_prefix": "ai-news-chara", "images": ["10", 0]}},
    }


def verify_workflow(url, wf):
    """投げる前に、相手の ComfyUI にそのノードがあるか・値が選べるかを確かめる。

    ComfyUI は 400 を返してくれますが、メッセージが英語で長いので、
    **どのノードが無いのか**を先に日本語で出します。戻り値は不備の一覧。
    """
    problems, cache = [], {}
    for nid, node in sorted(wf.items(), key=lambda kv: int(kv[0])):
        cls = node.get("class_type")
        if cls not in cache:
            try:
                cache[cls] = api(url, f"/object_info/{cls}", timeout=60).get(cls)
            except (urllib.error.HTTPError, urllib.error.URLError, OSError):
                cache[cls] = None
        info = cache[cls]
        if info is None:
            problems.append(f"ノード『{cls}』が入っていません")
            continue
        required = (info.get("input") or {}).get("required") or {}
        for name, spec in required.items():
            if name not in node.get("inputs", {}):
                problems.append(f"{cls}: 入力『{name}』が足りません")
                continue
            value = node["inputs"][name]
            choices = spec[0] if isinstance(spec, list) and spec else None
            if isinstance(choices, list) and not isinstance(value, list):
                if value not in choices:
                    head = "、".join(map(str, choices[:4]))
                    problems.append(f"{cls}: 『{name}』に {value!r} は選べません"
                                    f"(選べるのは {head} など{len(choices)}種)")
    return problems


def patch_workflow(wf, recipe, job, reference=None):
    """手元で書き出したワークフローに、recipe と今回のジョブの値を当てはめる。

    ノードIDは人によって違うので、`class_type` で探して差し替えます。
    CLIPTextEncode が2つ以上あるときは、KSampler の positive / negative が
    指しているノードを見て、どちらが肯定側かを判定します。
    """
    hit = []
    pos_id = neg_id = None
    for nid, node in wf.items():
        if node.get("class_type") == "KSampler":
            ins = node.setdefault("inputs", {})
            if "seed" in ins:
                ins["seed"] = job["seed"]
                hit.append("seed")
            p, n = ins.get("positive"), ins.get("negative")
            pos_id = p[0] if isinstance(p, list) else None
            neg_id = n[0] if isinstance(n, list) else None
    for nid, node in wf.items():
        c, ins = node.get("class_type"), node.setdefault("inputs", {})
        if c in ("EmptyLatentImage", "EmptySD3LatentImage"):
            ins["width"], ins["height"] = recipe["width"], recipe["height"]
            hit.append("size")
        elif c == "CLIPTextEncode" and "text" in ins:
            if nid == pos_id:
                ins["text"] = job["positive"]
                hit.append("positive")
            elif nid == neg_id:
                ins["text"] = recipe["negative"]
                hit.append("negative")
        elif c == "LoadImage" and reference:
            ins["image"] = reference
            hit.append("reference")
    return hit


def submit(url, wf, client_id):
    try:
        res = api(url, "/prompt", {"prompt": wf, "client_id": client_id})
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")
        print(f"  ComfyUI がワークフローを受け付けませんでした (HTTP {e.code})", file=sys.stderr)
        try:
            err = json.loads(detail)
            print(f"  {json.dumps(err.get('error', err), ensure_ascii=False, indent=2)}",
                  file=sys.stderr)
            for node, ne in (err.get("node_errors") or {}).items():
                print(f"  ノード {node}: {json.dumps(ne, ensure_ascii=False)}", file=sys.stderr)
        except json.JSONDecodeError:
            print(f"  {detail[:400]}", file=sys.stderr)
        return None
    return res.get("prompt_id")


def wait(url, prompt_id, label=""):
    """/history をポーリングして、終わったら outputs を返す。

    WebSocket(/ws)でも進捗は取れますが、待つだけならHTTPのほうが依存が少ないので
    ポーリングにしています。
    """
    started = time.monotonic()
    while time.monotonic() - started < POLL_LIMIT:
        hist = api(url, f"/history/{prompt_id}")
        entry = hist.get(prompt_id)
        if entry:
            status = entry.get("status") or {}
            if status.get("status_str") == "error" or status.get("completed") is False:
                print(f"\n  生成に失敗しました: "
                      f"{json.dumps(status.get('messages', []), ensure_ascii=False)[:500]}",
                      file=sys.stderr)
                return None
            if entry.get("outputs"):
                # 進捗行を \r で上書きするので、前の行の残りを空白で消してから出す
                print(f"\r  {label} 完了({int(time.monotonic() - started)}秒)".ljust(40))
                return entry["outputs"]
        print(f"\r  {label} 生成中… {int(time.monotonic() - started)}秒".ljust(40),
              end="", flush=True)
        time.sleep(2)
    print(f"\n  {POLL_LIMIT}秒待っても終わりませんでした。", file=sys.stderr)
    return None


def fetch_images(url, outputs, job):
    """outputs に並んだ画像を /view から落として、候補フォルダに置く。"""
    saved = []
    for node_id, out in outputs.items():
        for i, img in enumerate(out.get("images", [])):
            q = urllib.parse.urlencode({"filename": img["filename"],
                                        "subfolder": img.get("subfolder", ""),
                                        "type": img.get("type", "output")})
            blob = api(url, "/view?" + q, raw=True, timeout=120)
            d = CANDIDATES / job["who"]
            d.mkdir(parents=True, exist_ok=True)
            suffix = "" if i == 0 else f"-{i}"
            dst = d / f"{job['pose']}{suffix}.png"
            dst.write_bytes(blob)
            saved.append(dst)
            print(f"    → {dst.relative_to(HERE)} ({len(blob) // 1024}KB)")
    return saved


def check(url, recipe_path=None):
    """つながるか、必要なモデルが入っているかを見る。"""
    print(f"接続先: {url}")
    try:
        stats = api(url, "/system_stats")
    except (urllib.error.URLError, OSError) as e:
        print(f"  つながりません: {e}", file=sys.stderr)
        print("  ComfyUI を起動してから実行してください。", file=sys.stderr)
        hit = probe_ports()
        if hit:
            print(f"  ただし {hit[0]} には ComfyUI が居ます。次のように指定してください:",
                  file=sys.stderr)
            print(f"    python3 _comfy_character.py --check --url {hit[0]}", file=sys.stderr)
            print(f"    COMFY_URL={hit[0]} python3 _comfy_character.py", file=sys.stderr)
        else:
            print("  別のPCで動かしているなら --url か COMFY_URL で指定します。"
                  "その場合 ComfyUI 側に --listen も要ります"
                  "(既定は 127.0.0.1 で、ループバックにしか繋がりません)。", file=sys.stderr)
        return 1
    for d in stats.get("devices", []):
        print(f"  デバイス: {d.get('name')} / VRAM {int(d.get('vram_total', 0)) // (1024**3)}GB")

    recipe = load_recipe(recipe_path)
    if recipe is None:
        return 1
    try:
        info = api(url, "/object_info/CheckpointLoaderSimple", timeout=60)
        names = (info["CheckpointLoaderSimple"]["input"]["required"]["ckpt_name"][0])
    except (KeyError, urllib.error.HTTPError, urllib.error.URLError, OSError) as e:
        print(f"  モデル一覧を取れませんでした: {e}", file=sys.stderr)
        return 1
    want = recipe["checkpoint"]
    print(f"  入っているモデル: {len(names)}個")
    if want in names:
        print(f"  recipe.json のモデル『{want}』: あります")
    else:
        print(f"  recipe.json のモデル『{want}』: **ありません**")
        print("  入っているのは次のものです。recipe.json の checkpoint を書き換えてください:")
        for n in names[:15]:
            print(f"    {n}")
    jobs = jobs_from(recipe)
    print(f"  作るもの: キャラ{len(recipe.get('cast') or [1])}人 × "
          f"ポーズ{len(recipe.get('variations') or [1])}種 = {len(jobs)}枚")
    check_ipadapter(url)
    return 0


# IPAdapter が「使えるか」の判定。配布元(cubiq/ComfyUI_IPAdapter_plus)の utils.py にある
# get_clipvision_file() / get_ipadapter_file() と**同じ正規表現**を使う。
# あちらは固定のファイル名ではなく名前のパターンで探すので、こちらも同じにしないと
# 「あるのに無いと言う」ことになる。preset は顔を寄せる PLUS FACE、SDXL 前提。
IPA_PATTERNS = {
    "clip_vision": (r"(ViT.H.14.*s32B.b79K|ipadapter.*sd15|sd1.?5.*model)\.(bin|safetensors)",
                    "CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors"),
    "ipadapter": (r"plus.face.sdxl.vit.h\.(safetensors|bin)$",
                  "ip-adapter-plus-face_sdxl_vit-h.safetensors"),
}


def options_of(url, node, field):
    """そのノードが選べる値の一覧を返す。ノードが無ければ None。"""
    try:
        info = api(url, f"/object_info/{node}", timeout=60)
    except (urllib.error.HTTPError, urllib.error.URLError, OSError):
        return None
    try:
        return info[node]["input"]["required"][field][0]
    except (KeyError, IndexError, TypeError):
        return None


def check_ipadapter(url):
    """IPAdapter を使う準備ができているかを見る(顔を揃えたいとき用)。

    ノードだけ入れてもモデルが無いと動きません。両方見ます。
    サブフォルダに入れた場合、名前がパターンに合わず**見つけてもらえない**ことがあるので、
    そこまで判定します(実例: `CLIP-ViT-H-14-laion2B-s32B-b79K\model.safetensors` は不可)。
    """
    import re

    presets = options_of(url, "IPAdapterUnifiedLoader", "preset")
    if presets is None:
        print("  IPAdapter: 入っていません"
              "(素の txt2img は動きます。顔を揃えたいときだけ必要)")
        return
    print(f"  IPAdapter: 入っています(preset {len(presets)}種)")
    for kind, node, field in (("clip_vision", "CLIPVisionLoader", "clip_name"),
                              ("ipadapter", "IPAdapterModelLoader", "ipadapter_file")):
        have = options_of(url, node, field) or []
        pattern, want = IPA_PATTERNS[kind]
        ok = [e for e in have if re.search(pattern, e, re.IGNORECASE)]
        if ok:
            print(f"    {kind}: {ok[0]} で見つかります")
            continue
        print(f"    {kind}: **見つかりません**")
        near = [e for e in have if re.search(want.split(".safetensors")[0].replace("-", ".")[:20],
                                             e, re.IGNORECASE)]
        if near:
            print(f"      ファイルはあるのに名前がパターンに合っていません: {near[0]}")
            print(f"      → models/{kind}/ の直下に『{want}』の名前で置いてください")
            print("      (Unified Loader はサブフォルダ内の model.safetensors を拾えません)")
        else:
            print(f"      → models/{kind}/ に『{want}』を置いてください")
            if have:
                print(f"      (いま入っているもの: {', '.join(have[:3])})")


def main():
    argv = sys.argv[1:]

    def opt(name, default=None):
        return argv[argv.index(name) + 1] if name in argv and argv.index(name) + 1 < len(argv) else default

    url = opt("--url", DEFAULT_URL)
    recipe_path = opt("--recipe")
    if "--check" in argv:
        return check(url, recipe_path)

    recipe = load_recipe(recipe_path)
    if recipe is None:
        return 1
    if "--checkpoint" in argv:
        recipe["checkpoint"] = opt("--checkpoint")
    if "ここに手元の" in recipe["checkpoint"]:
        # 雛形のまま投げると ComfyUI 側で 400 になる。手前で止めて案内する。
        print("中止: recipe.json の checkpoint が雛形のままです。", file=sys.stderr)
        print("      次で一覧を出して、実際のファイル名に書き換えてください:", file=sys.stderr)
        print(f"      python3 _comfy_character.py --check --url {url}", file=sys.stderr)
        print("      一時的に試すだけなら --checkpoint で上書きできます。", file=sys.stderr)
        return 1

    jobs = jobs_from(recipe, who=opt("--who"), pose=opt("--pose"),
                     offset=int(opt("--seed-offset", "0")))
    if not jobs:
        print("中止: 条件に合うものがありません。--who / --pose の名前を確認してください。",
              file=sys.stderr)
        print(f"      キャラ: {', '.join(c['name'] for c in recipe.get('cast', []))}",
              file=sys.stderr)
        print(f"      ポーズ: {', '.join(v['name'] for v in recipe.get('variations', []))}",
              file=sys.stderr)
        return 1

    base = None
    if "--workflow" in argv:
        path = Path(opt("--workflow")).expanduser()
        base = json.loads(path.read_text(encoding="utf-8"))
        if not all(isinstance(v, dict) and "class_type" in v for v in base.values()):
            print(f"中止: {path} はAPI形式ではありません。"
                  "ComfyUI の「API形式でエクスポート」で書き出したJSONを渡してください。",
                  file=sys.stderr)
            return 1
        print(f"ワークフロー: {path}")

    if "--dump-workflow" in argv:
        WORKFLOW.parent.mkdir(parents=True, exist_ok=True)
        WORKFLOW.write_text(json.dumps(build_workflow(recipe, jobs[0]),
                                       ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"書き出しました: {WORKFLOW.relative_to(HERE)}")
        return 0

    face = "--face" in argv
    weight = float(opt("--weight", str(IPA_WEIGHT)))

    reference = None
    if "--reference" in argv:
        if base is None and not face:
            print("中止: --reference は --face(または --workflow)と一緒に使ってください。",
                  file=sys.stderr)
            return 1
        try:
            reference = upload_reference(url, opt("--reference"))
        except (urllib.error.URLError, OSError) as e:
            print(f"中止: 参照画像を送れませんでした: {e}", file=sys.stderr)
            return 1
        if reference is None:
            return 1
        print(f"参照画像: {reference} を ComfyUI に送りました")

    # --face: 基準の1枚を参照して顔を揃える(IPAdapter)。ワークフローは
    # こちらで組み立てるので、ComfyUI の画面で何かを組む必要はない。
    refs = {}
    if face:
        cast_dir = HERE / "_assets" / "character" / "cast"
        for job in jobs:
            who = job["who"]
            if who in refs:
                continue
            if reference is not None:
                refs[who] = reference          # --reference で明示されたらそれを使う
                continue
            # 明示が無ければ、採用済みの絵(cast)から基準を探す。
            # recipe の cast[].face でポーズ名を指定でき、無ければ wave → 最初の1枚。
            entry = next((c for c in recipe.get("cast", []) if c["name"] == who), {})
            cand = [cast_dir / who / f"{entry.get('face', 'wave')}.png"]
            cand += sorted((cast_dir / who).glob("*.png")) if (cast_dir / who).is_dir() else []
            path = next((c for c in cand if c.is_file()), None)
            if path is None:
                print(f"中止: {who} の基準になる顔がありません。", file=sys.stderr)
                print(f"      _assets/character/cast/{who}/ に1枚も無いためです。"
                      "先に素の生成で1枚選んで取り込むか、--reference で渡してください。",
                      file=sys.stderr)
                return 1
            try:
                sent = upload_reference(url, path)
            except (urllib.error.URLError, OSError) as e:
                print(f"中止: 基準の顔を送れませんでした: {e}", file=sys.stderr)
                return 1
            if sent is None:
                return 1
            refs[who] = sent
            print(f"基準の顔: {who} ← {path.relative_to(HERE)}")

        # 投げる前に、必要なノードとモデルが揃っているかを確かめて日本語で出す
        probe = build_ipadapter_workflow(recipe, jobs[0], refs[jobs[0]["who"]], weight)
        problems = verify_workflow(url, probe)
        if problems:
            print("中止: この ComfyUI では顔揃えの準備ができていません。", file=sys.stderr)
            for x in problems:
                print(f"  - {x}", file=sys.stderr)
            print("  対処は _assets/character/comfy/README.md の"
                  "「2. 顔を揃えたいなら IPAdapter を入れる」を見てください。", file=sys.stderr)
            return 1
        print(f"ノードとモデルを確認しました(weight={weight}, preset={IPA_PRESET})")

    client_id = str(uuid.uuid4())
    made = []
    started = time.monotonic()
    for i, job in enumerate(jobs, 1):
        label = f"[{i}/{len(jobs)}] {job['who']} / {job['pose']} (seed={job['seed']})"
        print(label)
        if face:
            wf = build_ipadapter_workflow(recipe, job, refs[job["who"]], weight)
        elif base is None:
            wf = build_workflow(recipe, job)
        else:
            wf = json.loads(json.dumps(base))
            hit = patch_workflow(wf, recipe, job, reference)
            if "seed" not in hit:
                print("  注意: KSampler が見つからず seed を固定できませんでした。",
                      file=sys.stderr)
            if "positive" not in hit:
                print("  注意: 肯定プロンプトの差し替え先が見つかりませんでした。"
                      "ワークフローに書いてある文章のまま生成します。", file=sys.stderr)
        try:
            prompt_id = submit(url, wf, client_id)
        except (urllib.error.URLError, OSError) as e:
            print(f"  つながりません: {e}", file=sys.stderr)
            return 1
        if not prompt_id:
            return 1
        outputs = wait(url, prompt_id, label="")
        if outputs:
            made += fetch_images(url, outputs, job)

    if not made:
        return 1
    print()
    print(f"候補を{len(made)}枚受け取りました"
          f"(所要 {int(time.monotonic() - started)}秒)。**Read で開いて選んでください。**")
    print("採用する1枚ごとに取り込みます(背景が透過していない場合は --matte を付ける):")
    j = jobs[0]
    print(f"  python3 _prepare_character.py {(CANDIDATES / j['who'] / (j['pose'] + '.png')).relative_to(HERE)}"
          f" --cast {j['who']} --as {j['pose']} --matte")
    return 0


if __name__ == "__main__":
    sys.exit(main())
