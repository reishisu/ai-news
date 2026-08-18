#!/usr/bin/env python3
"""ComfyUI の API だけを真似た偽サーバー。

この環境にはGPUが無く、本物の ComfyUI を動かせません。
`_comfy_character.py` の**投げる・待つ・受け取る**の筋道だけを確かめるために使います。

真似ている範囲は、ComfyUI 本体のソースで確認した次の4つです。
(comfyanonymous/ComfyUI の server.py / execution.py / nodes.py, 2026年8月18日取得)

    POST /prompt                            → {"prompt_id", "number", "node_errors"}
                                              検証に落ちると 400 {"error", "node_errors"}
    GET  /history/<prompt_id>               → {<id>: {"outputs", "status", ...}}
    GET  /view?filename=&subfolder=&type=   → PNG そのもの
    POST /upload/image                      → {"name", "subfolder", "type"}
    GET  /object_info/CheckpointLoaderSimple, /system_stats

**これは本物の ComfyUI ではありません。** 生成は行わず、seed を書いた
「白背景に立つ人型」のダミーPNGを返します(--matte の検証も兼ねる)。

    python3 fake_comfy.py 8188
"""

import json
import os
import re
import sys
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from io import BytesIO

from PIL import Image, ImageDraw

# 本物では手元の models/checkpoints にあるファイル名が並ぶ
CHECKPOINTS = ["dummy-anime.safetensors", "dummy-sdxl.safetensors"]
DELAY = 4          # 生成にかかる時間のつもり(ポーリングが動くことの確認用)
JOBS = {}
UPLOADED = []
# IPAdapter が入っているかの再現。none=入っていない / nomodels=ノードだけ / full=モデルもある
IPA = os.environ.get("FAKE_IPA", "none")
IPA_PRESETS = ["LIGHT - SD1.5 only (low strength)", "STANDARD (medium strength)",
               "VIT-G (medium strength)", "PLUS (high strength)",
               "PLUS FACE (portraits)", "FULL FACE - SD1.5 only (portraits stronger)"]


def dummy_png(seed, w=832, h=1216):
    """白背景に人型を1つ描く。背景は完全な単色にしておく(--matte の検証用)。"""
    im = Image.new("RGB", (w, h), (255, 255, 255))
    d = ImageDraw.Draw(im)
    cx = w // 2
    d.ellipse((cx - 150, 150, cx + 150, 450), fill=(255, 205, 190))        # 頭
    d.ellipse((cx - 190, 120, cx + 190, 330), fill=(90, 60, 130))          # 髪
    d.rounded_rectangle((cx - 200, 470, cx + 200, 1100), 60, fill=(70, 140, 230))  # 服
    # 服の中の白。外周と繋がっていない白は残るはず(穴が開かないことの確認)
    d.rounded_rectangle((cx - 90, 560, cx + 90, 900), 20, fill=(255, 255, 255))
    d.ellipse((cx - 80, 300, cx - 30, 350), fill=(40, 40, 60))             # 目
    d.ellipse((cx + 30, 300, cx + 80, 350), fill=(40, 40, 60))
    d.text((cx - 60, 1140), f"seed {seed}", fill=(0, 0, 0))
    buf = BytesIO()
    im.save(buf, "PNG")
    return buf.getvalue()


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="application/json"):
        if isinstance(body, (dict, list)):
            body = json.dumps(body).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(u.query)
        if u.path == "/system_stats":
            return self._send(200, {"system": {"comfyui_version": "fake"},
                                    "devices": [{"name": "fake-cpu", "vram_total": 0}]})
        if u.path == "/object_info/CheckpointLoaderSimple":
            return self._send(200, {"CheckpointLoaderSimple": {
                "input": {"required": {"ckpt_name": [CHECKPOINTS, {}]}}}})
        if u.path.startswith("/object_info/IPAdapter"):
            if IPA == "none":
                return self._send(404, {"error": "not found"})
            node = u.path.rsplit("/", 1)[1]
            if node == "IPAdapterUnifiedLoader":
                return self._send(200, {node: {
                    "input": {"required": {"model": ["MODEL", {}],
                                           "preset": [IPA_PRESETS, {}]}}}})
            if node == "IPAdapterModelLoader":
                files = ["ip-adapter-plus-face_sdxl_vit-h.safetensors"]
                return self._send(200, {node: {
                    "input": {"required": {"ipadapter_file": [files, {}]}}}})
            return self._send(200, {node: {"input": {"required": {}}}})
        if u.path == "/object_info/CLIPVisionLoader":
            # nomodels は実機で出た状態の再現。ファイルはあるがサブフォルダの中にあり、
            # 名前が Unified Loader のパターンに合わない。
            names = (["CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors"] if IPA == "full" else
                     ["CLIP-ViT-H-14-laion2B-s32B-b79K\\model.safetensors",
                      "CLIP-ViT-H-14-laion2B-s32B-b79K\\open_clip_model.safetensors"])
            return self._send(200, {"CLIPVisionLoader": {
                "input": {"required": {"clip_name": [names, {}]}}}})
        if u.path.startswith("/history/"):
            pid = u.path.rsplit("/", 1)[1]
            job = JOBS.get(pid)
            if not job:
                return self._send(200, {})
            if time.monotonic() - job["t"] < DELAY:
                return self._send(200, {})       # まだ終わっていない(本物も空で返す)
            return self._send(200, {pid: {
                "prompt": [0, pid, {}, {}, []],
                "outputs": {"7": {"images": [{"filename": f"ai-news-chara_{pid[:8]}.png",
                                              "subfolder": "", "type": "output"}]}},
                "status": {"status_str": "success", "completed": True, "messages": []},
            }})
        if u.path.startswith("/object_info/"):
            # 上で答えなかったノード。核ノード(KSamplerなど)は「ある」ことにして
            # 空の required を返す。IPAdapter系と PrepImageForClipVision は
            # 入っていない状態(none)なら 404(本物も無いノードは404を返す)。
            node = u.path.rsplit("/", 1)[1]
            if IPA == "none" and (node.startswith("IPAdapter")
                                  or node == "PrepImageForClipVision"):
                return self._send(404, {"error": "not found"})
            return self._send(200, {node: {"input": {"required": {}}}})
        if u.path == "/view":
            name = (q.get("filename") or [""])[0]
            for pid, job in JOBS.items():
                if pid[:8] in name:
                    return self._send(200, dummy_png(job["seed"]), "image/png")
            return self._send(404, b"not found", "text/plain")
        return self._send(404, {"error": "no route"})

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(n)
        if self.path == "/upload/image":
            # multipart の中身までは見ない。名前を返せば LoadImage に差せる。
            m = re.search(rb'filename="([^"]+)"', raw)
            name = m.group(1).decode("utf-8") if m else "uploaded.png"
            UPLOADED.append(name)
            return self._send(200, {"name": name, "subfolder": "", "type": "input"})
        body = json.loads(raw or b"{}")
        if self.path != "/prompt":
            return self._send(404, {"error": "no route"})
        if "prompt" not in body:
            return self._send(400, {"error": {"type": "no_prompt",
                                              "message": "No prompt provided"},
                                    "node_errors": {}})
        wf = body["prompt"]
        seed = 0
        for nid, node in wf.items():
            if node.get("class_type") == "CheckpointLoaderSimple":
                ck = node["inputs"].get("ckpt_name")
                if ck not in CHECKPOINTS:
                    return self._send(400, {
                        "error": {"type": "prompt_outputs_failed_validation",
                                  "message": "Prompt outputs failed validation"},
                        "node_errors": {nid: {"errors": [{
                            "type": "value_not_in_list",
                            "message": f"Value not in list: ckpt_name: '{ck}' not in "
                                       f"{CHECKPOINTS}"}]}}})
            if node.get("class_type") == "KSampler":
                seed = node["inputs"].get("seed", 0)
        pid = f"{int(time.time() * 1000):x}-{seed}"
        JOBS[pid] = {"t": time.monotonic(), "seed": seed}
        return self._send(200, {"prompt_id": pid, "number": len(JOBS), "node_errors": {}})


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8188
    print(f"偽ComfyUI: http://127.0.0.1:{port} (生成待ち {DELAY}秒)")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
