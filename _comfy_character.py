#!/usr/bin/env python3
"""ComfyUI にキャラクター画像を作らせて、候補として持ってくる。

**ComfyUI はGPUのある手元のPCで動かしてください。** このスクリプトは
「動いている ComfyUI にHTTPで投げて、出てきたPNGを受け取る」だけです。
生成そのものはしません(この記事サイトの実行環境にGPUはありません)。

サムネイルのマスコットは**毎回同じ顔である必要がある**ので、次の形にしています。

- 生成の設定(モデル名・プロンプト・seed・サイズ)を `recipe.json` に書いて**コミットする**
- モデルのファイルそのものはコミットしない(数GBあり、ライセンスもまちまち)
- 生成は人が手で走らせて、**出てきた候補から人が1枚選ぶ**
- 日次のサムネイル生成(`_render_thumbs.py`)は画像を読むだけで、生成には一切触らない

使い方:

    # 1. 手元で ComfyUI を起動しておく(既定は http://127.0.0.1:8188)
    # 2. つながるか・必要なモデルがあるかを見る
    python3 _comfy_character.py --check

    # 3. 候補を4枚出す(seed は 1 ずつずれる)
    python3 _comfy_character.py --batch 4

    # モデルだけ一時的に変えて試す(recipe.json は書き換えない)
    python3 _comfy_character.py --batch 2 --checkpoint waiIllustriousSDXL_v160.safetensors

    # 4. 気に入った1枚を選んで取り込む(透過・トリム・リサイズ)
    python3 _prepare_character.py _assets/character/_candidates/<選んだ.png> --matte

接続先を変えるとき:

    COMFY_URL=http://192.168.1.20:8188 python3 _comfy_character.py --check
    python3 _comfy_character.py --url http://192.168.1.20:8188

自分で組んだワークフローを使うとき(ComfyUI の「ワークフロー → API形式でエクスポート」で
書き出したJSON。**UI形式ではありません**):

    python3 _comfy_character.py --workflow mychara.api.json

APIの仕様は ComfyUI 本体のソースで確認しています(server.py / execution.py / nodes.py)。

    POST /prompt          {"prompt": <API形式のワークフロー>, "client_id": ...}
                          → {"prompt_id": ..., "number": ..., "node_errors": {...}}
                          検証に落ちると 400 で {"error": ..., "node_errors": {...}}
    GET  /history/<id>    → {<id>: {"outputs": {<ノードID>: {"images": [...]}},
                                    "status": {"status_str": "success"|"error",
                                               "completed": true|false,
                                               "messages": [...]}}}
    GET  /view?filename=&subfolder=&type=output   → 画像そのもの
    GET  /object_info     → 入っているノードと、選べるモデル名の一覧
    GET  /system_stats    → 動いているかの確認に使う

権利について: 自作したもの、または権利が明確なものだけを置いてください。
特定の作品のキャラクターを狙って出すプロンプト・LoRAは使えません(CLAUDE.md 第6節)。
"""

import json
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
POLL_LIMIT = 1800     # 生成待ちの上限(秒)。CPU実行だと数分かかることがある


def api(url, path, data=None, raw=False, timeout=TIMEOUT):
    """ComfyUI に1回リクエストする。data があれば POST。"""
    req = urllib.request.Request(url.rstrip("/") + path)
    if data is not None:
        req.data = json.dumps(data).encode("utf-8")
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = r.read()
    return body if raw else json.loads(body.decode("utf-8"))


def load_recipe(path=None):
    path = Path(path) if path else RECIPE
    if not path.is_file():
        print(f"中止: {path} がありません。", file=sys.stderr)
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def build_workflow(recipe):
    """API形式のワークフローを組み立てる。

    使うのは ComfyUI の標準ノードだけです(追加のカスタムノードは要りません)。
    チェックポイント読み込み → プロンプト2つ → 空のラテント → サンプラー →
    VAEでデコード → 保存、という素の txt2img です。
    """
    return {
        "1": {"class_type": "CheckpointLoaderSimple",
              "inputs": {"ckpt_name": recipe["checkpoint"]}},
        "2": {"class_type": "CLIPTextEncode",
              "inputs": {"text": recipe["positive"], "clip": ["1", 1]}},
        "3": {"class_type": "CLIPTextEncode",
              "inputs": {"text": recipe["negative"], "clip": ["1", 1]}},
        "4": {"class_type": "EmptyLatentImage",
              "inputs": {"width": recipe["width"], "height": recipe["height"],
                         "batch_size": 1}},
        "5": {"class_type": "KSampler",
              "inputs": {"seed": recipe["seed"], "steps": recipe["steps"],
                         "cfg": recipe["cfg"], "sampler_name": recipe["sampler"],
                         "scheduler": recipe["scheduler"], "denoise": 1.0,
                         "model": ["1", 0], "positive": ["2", 0],
                         "negative": ["3", 0], "latent_image": ["4", 0]}},
        "6": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": ["1", 2]}},
        "7": {"class_type": "SaveImage",
              "inputs": {"filename_prefix": "ai-news-chara", "images": ["6", 0]}},
    }


def patch_workflow(wf, recipe):
    """手元で書き出したワークフローに、recipe.json の値を当てはめる。

    ノードIDは人によって違うので、`class_type` で探して差し替えます。
    差し替えるのは seed とサイズだけ(プロンプトやモデルは、書き出した本人の
    ワークフローに書いてあるものを尊重する)。
    """
    hit = []
    for node in wf.values():
        c = node.get("class_type")
        ins = node.get("inputs", {})
        if c == "KSampler" and "seed" in ins:
            ins["seed"] = recipe["seed"]
            hit.append("seed")
        elif c in ("EmptyLatentImage", "EmptySD3LatentImage"):
            ins["width"], ins["height"] = recipe["width"], recipe["height"]
            hit.append("size")
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


def wait(url, prompt_id):
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
                print(f"  完了({int(time.monotonic() - started)}秒)")
                return entry["outputs"]
        print(f"\r  生成中… {int(time.monotonic() - started)}秒", end="", flush=True)
        time.sleep(2)
    print(f"\n  {POLL_LIMIT}秒待っても終わりませんでした。", file=sys.stderr)
    return None


def fetch_images(url, outputs, seed):
    """outputs に並んだ画像を /view から落として、候補フォルダに置く。"""
    CANDIDATES.mkdir(parents=True, exist_ok=True)
    saved = []
    for node_id, out in outputs.items():
        for i, img in enumerate(out.get("images", [])):
            q = urllib.parse.urlencode({"filename": img["filename"],
                                        "subfolder": img.get("subfolder", ""),
                                        "type": img.get("type", "output")})
            blob = api(url, "/view?" + q, raw=True, timeout=120)
            dst = CANDIDATES / f"seed{seed}-{node_id}-{i}.png"
            dst.write_bytes(blob)
            saved.append(dst)
            print(f"  受け取り: {dst.relative_to(HERE)} ({len(blob) // 1024}KB)")
    return saved


def probe_ports(host="127.0.0.1", ports=(8188, 8000, 8001, 8080, 8189)):
    """よく使われるポートを順に叩いて、ComfyUI が居るところを探す。

    既定の 8188 以外で起動している人が多いので、繋がらなかったときに候補を出す。
    """
    found = []
    for p in ports:
        u = f"http://{host}:{p}"
        try:
            api(u, "/system_stats", timeout=2)
            found.append(u)
        except (urllib.error.URLError, OSError, json.JSONDecodeError):
            pass
    return found


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
            print(f"    COMFY_URL={hit[0]} python3 _comfy_character.py --batch 4",
                  file=sys.stderr)
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
    return 0


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
    if "--seed" in argv:
        recipe["seed"] = int(opt("--seed"))
    if "--checkpoint" in argv:
        recipe["checkpoint"] = opt("--checkpoint")
    if "ここに手元の" in recipe["checkpoint"]:
        # 雛形のまま投げると ComfyUI 側で 400 になる。手前で止めて案内する。
        print("中止: recipe.json の checkpoint が雛形のままです。", file=sys.stderr)
        print("      次で一覧を出して、実際のファイル名に書き換えてください:", file=sys.stderr)
        print(f"      python3 _comfy_character.py --check --url {url}", file=sys.stderr)
        print("      一時的に試すだけなら --checkpoint で上書きできます。", file=sys.stderr)
        return 1
    batch = int(opt("--batch", "1"))

    if "--workflow" in argv:
        path = Path(opt("--workflow")).expanduser()
        base = json.loads(path.read_text(encoding="utf-8"))
        if not all(isinstance(v, dict) and "class_type" in v for v in base.values()):
            print(f"中止: {path} はAPI形式ではありません。"
                  "ComfyUI の「API形式でエクスポート」で書き出したJSONを渡してください。",
                  file=sys.stderr)
            return 1
        print(f"ワークフロー: {path}")
    else:
        base = None

    if "--dump-workflow" in argv:
        WORKFLOW.parent.mkdir(parents=True, exist_ok=True)
        WORKFLOW.write_text(json.dumps(build_workflow(recipe), ensure_ascii=False, indent=2)
                            + "\n", encoding="utf-8")
        print(f"書き出しました: {WORKFLOW.relative_to(HERE)}")
        return 0

    client_id = str(uuid.uuid4())
    made = []
    for i in range(batch):
        seed = recipe["seed"] + i
        r = dict(recipe, seed=seed)
        if base is None:
            wf = build_workflow(r)
        else:
            wf = json.loads(json.dumps(base))
            hit = patch_workflow(wf, r)
            if "seed" not in hit:
                print("  注意: KSampler が見つからず seed を固定できませんでした。"
                      "毎回違う顔が出ます。", file=sys.stderr)
        print(f"[{i + 1}/{batch}] seed={seed} を投げます")
        try:
            prompt_id = submit(url, wf, client_id)
        except (urllib.error.URLError, OSError) as e:
            print(f"  つながりません: {e}", file=sys.stderr)
            return 1
        if not prompt_id:
            return 1
        outputs = wait(url, prompt_id)
        if outputs:
            made += fetch_images(url, outputs, seed)

    if not made:
        return 1
    print()
    print(f"候補を{len(made)}枚受け取りました。**Read で開いて選んでください。**")
    print("選んだら取り込みます(背景が透過していない場合は --matte を付ける):")
    print(f"  python3 _prepare_character.py {made[0].relative_to(HERE)} --matte")
    print("採用した seed は recipe.json に書き戻すと、同じ顔をあとから再現できます。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
