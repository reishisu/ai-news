#!/usr/bin/env python3
"""ComfyUI形式のワークフローを、**本物のチェックポイントで**実際に描く。

`fake_comfy_queue.py` は既定では絵を描かず、時間だけ数えます（詰まりの再現用）。
このモジュールを差すと、同じサーバーが**実物のモデルで描いて**返します。

## なぜ diffusers なのか

この環境からは github.com が403で、ComfyUI 本体を持ってこられません
（CLAUDE.md 第18節）。モデルの重みは HuggingFace 経由で取れるので、
**同じ .safetensors を diffusers で読んで**描いています。

## だから、ComfyUI と同じ絵にはなりません（重要）

同じ重みでも、次が違います。**この違いを承知のうえで使うこと。**

| | ComfyUI | ここ(diffusers) |
|---|---|---|
| `(shadow:1.4)` の強調記法 | 効く | **効かない**（ただの文字として読む） |
| 75トークン超のプロンプト | 区切って全部使う | **77で切り捨てる** |
| CLIP skip | 既定 -1 相当 | 既定のまま |

確かめられるのは「モデルが読めること」「スクリプトの通し」「この機械での所要時間」で、
**絵柄の再現ではありません。**
"""
import io
import os

_PIPE = None


def load(ckpt_path, config_repo="LillyCherry/JANKUTrainedChenkinNoobai_v777",
         threads=None, dtype=None):
    """チェックポイントを1回だけ読む。以後は使い回す。

    既定は **bfloat16**。SDXL を float32 で置くと約14GBになり、
    この機械（メモリ15GB）では載りません（実測してこうしました）。
    """
    global _PIPE
    if _PIPE is not None:
        return _PIPE
    import torch
    from diffusers import StableDiffusionXLPipeline
    if threads:
        torch.set_num_threads(int(threads))
    dt = getattr(torch, dtype or os.environ.get("TORCH_DTYPE", "bfloat16"))
    _PIPE = StableDiffusionXLPipeline.from_single_file(
        str(ckpt_path), config=config_repo, torch_dtype=dt)
    _PIPE.to("cpu")
    _PIPE.set_progress_bar_config(disable=True)
    return _PIPE


SAMPLERS = {
    # ComfyUI の名前 → diffusers のスケジューラ
    "euler": "EulerDiscreteScheduler",
    "euler_ancestral": "EulerAncestralDiscreteScheduler",
    "dpmpp_2m": "DPMSolverMultistepScheduler",
}


def _read_graph(wf):
    """ComfyUI の API 形式のグラフから、描くのに要る値だけ取り出す。"""
    ks = next(n for n in wf.values() if n.get("class_type") == "KSampler")
    ins = ks["inputs"]
    pos_id = ins["positive"][0] if isinstance(ins.get("positive"), list) else None
    neg_id = ins["negative"][0] if isinstance(ins.get("negative"), list) else None
    latent = next((n for n in wf.values()
                   if n.get("class_type") in ("EmptyLatentImage",
                                              "EmptySD3LatentImage")), None)
    return {
        "positive": wf[pos_id]["inputs"]["text"] if pos_id else "",
        "negative": wf[neg_id]["inputs"]["text"] if neg_id else "",
        "width": (latent or {}).get("inputs", {}).get("width", 1024),
        "height": (latent or {}).get("inputs", {}).get("height", 1024),
        "steps": ins.get("steps", 30),
        "cfg": ins.get("cfg", 5.0),
        "seed": ins.get("seed", 0),
        "sampler": ins.get("sampler_name", "euler_ancestral"),
    }


def render(wf, should_stop=None, steps_override=None, size_override=None):
    """グラフを描いて PNG のバイト列を返す。

    should_stop() が True を返したら、そのステップで打ち切って None を返す。
    ComfyUI の /interrupt に相当する（**本物の取り消しを試すために要る**）。
    """
    import torch
    import diffusers
    g = _read_graph(wf)
    if steps_override:
        g["steps"] = int(steps_override)
    if size_override:
        g["width"], g["height"] = size_override
    pipe = _PIPE
    name = SAMPLERS.get(g["sampler"])
    if name and pipe.scheduler.__class__.__name__ != name:
        pipe.scheduler = getattr(diffusers, name).from_config(pipe.scheduler.config)

    stopped = {"hit": False}

    def on_step(p, i, t, kw):
        if should_stop and should_stop():
            stopped["hit"] = True
            raise KeyboardInterrupt("interrupted")
        return kw

    try:
        out = pipe(prompt=g["positive"], negative_prompt=g["negative"],
                   width=g["width"], height=g["height"],
                   num_inference_steps=g["steps"], guidance_scale=g["cfg"],
                   generator=torch.Generator("cpu").manual_seed(int(g["seed"])),
                   callback_on_step_end=on_step)
    except KeyboardInterrupt:
        return None
    if stopped["hit"]:
        return None
    buf = io.BytesIO()
    out.images[0].save(buf, format="PNG")
    return buf.getvalue()


def make_renderer(ckpt_path, **kw):
    """fake_comfy_queue.RENDER に差すための関数を作る。"""
    load(ckpt_path, threads=os.environ.get("TORCH_THREADS"))
    return lambda wf, should_stop=None: render(wf, should_stop, **kw)
