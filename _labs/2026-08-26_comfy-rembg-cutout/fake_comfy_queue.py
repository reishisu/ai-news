#!/usr/bin/env python3
"""キューを1本だけ持つ偽の ComfyUI。**詰まりを再現するために書いた。**

本物と同じ形で /prompt /queue /history /interrupt /free /view を返す。
違うのは絵を描かないことだけで、1枚 FAST 秒かかったことにする。
`--stall` に入れた番号の枚だけ SLOW 秒かける(詰まった状態の代わり。
**原因が何であれ**、遅い1枚が後続をどうするかを見るためのもの)。

本物と揃えたところ:
  - **キューは1本**。実行中は1件だけで、あとは順番待ち
  - /queue の1件は [番号, prompt_id, prompt, extra, outputs]
  - /history の status.messages は [イベント名, {..., "timestamp": ミリ秒}]
  - POST /queue {"delete":[id]} は**順番待ちしか消せない**
  - POST /interrupt {"prompt_id":id} は**走っているのが自分のときだけ**止める
"""
import json
import sys
import threading
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

FAST, SLOW = 1.0, 40.0
STALL = set()           # 何枚目を遅くするか(1始まり)
# 空きVRAMの返し方。**実機で測った値に合わせてある**(2026/8/26)。
#   生成中   316〜607MB … ここでは 450 を返す
#   空いた後 6540MB
# 終わってすぐ戻るのではなく RECOVER_S 秒かけて戻ることにしている。
# これで wait_vram() の待ちループが実際に回る(即返しだと試したことにならない)。
#
# **遅さの原因をVRAMと決めつけないこと。** 2026/8/25 に一度そう断定して
# 外している(main の c61af10)。ここは wait_vram() を試すための足場。
VRAM_BUSY_MB, VRAM_IDLE_MB, VRAM_TOTAL_MB = 450, 6540, 8192
RECOVER_S = 6.0
BUSY_UNTIL = 0.0
PNG = (b"\x89PNG\r\n\x1a\n" + b"\x00" * 64)

LOCK = threading.Lock()
PENDING, RUNNING, HISTORY = [], [], {}
SEEN = 0                # 受け付けた枚数
INTERRUPT = threading.Event()

# ここに関数を差すと、時間を数えるだけでなく**本物のモデルで描く**。
# 差し方は real_backend.make_renderer() を参照（--real で有効になる）。
RENDER = None
IMAGES = {}             # filename → PNG のバイト列（本物で描いたとき）


def now_ms():
    return int(time.time() * 1000)


def vram_free_mb():
    """いまの空きVRAM(MB)。生成中は少なく、終わってから徐々に戻る。"""
    if RUNNING:
        return VRAM_BUSY_MB
    left = BUSY_UNTIL - time.monotonic()
    if left <= 0:
        return VRAM_IDLE_MB
    # 直線で戻す
    t = 1.0 - left / RECOVER_S
    return int(VRAM_BUSY_MB + (VRAM_IDLE_MB - VRAM_BUSY_MB) * t)


def worker():
    global RUNNING, BUSY_UNTIL
    while True:
        with LOCK:
            item = PENDING.pop(0) if PENDING else None
            if item:
                RUNNING = [item]
        if not item:
            time.sleep(0.05)
            continue
        num, pid, prompt, extra, outs, want = item
        INTERRUPT.clear()
        start = now_ms()
        killed = False
        if RENDER is not None:
            # 本物のモデルで描く。取り消しは1ステップごとに見る
            try:
                blob = RENDER(prompt, INTERRUPT.is_set)
            except Exception as e:
                print(f"  描画に失敗: {e}", flush=True)
                blob = None
            if blob:
                IMAGES[f"{pid}.png"] = blob
            else:
                killed = True
        else:
            end = time.monotonic() + want
            while time.monotonic() < end:
                if INTERRUPT.is_set():
                    killed = True
                    break
                time.sleep(0.05)
        with LOCK:
            RUNNING = []
            BUSY_UNTIL = time.monotonic() + RECOVER_S
            if killed:
                HISTORY[pid] = {"status": {"status_str": "error", "completed": False,
                                           "messages": [["execution_interrupted",
                                                         {"timestamp": now_ms()}]]},
                                "outputs": {}}
            else:
                HISTORY[pid] = {
                    "status": {"status_str": "success", "completed": True,
                               "messages": [["execution_start", {"timestamp": start}],
                                            ["execution_success", {"timestamp": now_ms()}]]},
                    "outputs": {"7": {"images": [{"filename": f"{pid}.png",
                                                  "subfolder": "", "type": "output"}]}}}


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send(self, obj, raw=False):
        body = obj if raw else json.dumps(obj).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "image/png" if raw else "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        p = u.path
        if p == "/system_stats":
            # devices も本物と同じ形で返す。生成中は空きが少なく、
            # 終わってから RECOVER_S 秒かけて戻る(wait_vram() を試すため)
            mb = 1024 * 1024
            free = vram_free_mb()
            return self.send({
                "system": {"comfyui_version": "fake"},
                "devices": [{"name": "NVIDIA GeForce RTX 3070 Ti (fake)",
                             "type": "cuda", "index": 0,
                             "vram_total": VRAM_TOTAL_MB * mb,
                             "vram_free": free * mb}]})
        if p == "/prompt":
            with LOCK:
                return self.send({"exec_info": {"queue_remaining": len(PENDING) + len(RUNNING)}})
        if p == "/queue":
            with LOCK:
                return self.send({"queue_running": [list(i[:5]) for i in RUNNING],
                                  "queue_pending": [list(i[:5]) for i in PENDING]})
        if p.startswith("/history/"):
            pid = p.rsplit("/", 1)[1]
            with LOCK:
                return self.send({pid: HISTORY[pid]} if pid in HISTORY else {})
        if p == "/view":
            q = urllib.parse.parse_qs(u.query)
            name = (q.get("filename") or [""])[0]
            return self.send(IMAGES.get(name, PNG), raw=True)
        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        data = json.loads(self.rfile.read(n) or b"{}")
        global SEEN
        if self.path == "/prompt":
            with LOCK:
                SEEN += 1
                pid = f"p{SEEN:04d}"
                want = SLOW if SEEN in STALL else FAST
                PENDING.append((SEEN, pid, data.get("prompt"), {}, [], want))
            return self.send({"prompt_id": pid, "number": SEEN})
        if self.path == "/queue":
            with LOCK:
                if data.get("clear"):
                    PENDING.clear()
                for pid in data.get("delete") or []:
                    # 本物と同じで、**順番待ちしか消せない**
                    for i, it in enumerate(list(PENDING)):
                        if it[1] == pid:
                            PENDING.pop(i)
            return self.send(b"", raw=True)
        if self.path == "/interrupt":
            pid = data.get("prompt_id")
            with LOCK:
                mine = (not pid) or any(i[1] == pid for i in RUNNING)
            if mine:
                INTERRUPT.set()
            return self.send(b"", raw=True)
        if self.path == "/free":
            return self.send(b"", raw=True)
        self.send_response(404)
        self.end_headers()


def serve(port, stall=(), fast=FAST, slow=SLOW):
    global STALL, FAST, SLOW
    STALL, FAST, SLOW = set(stall), fast, slow
    threading.Thread(target=worker, daemon=True).start()
    srv = ThreadingHTTPServer(("127.0.0.1", port), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


if __name__ == "__main__":
    argv = sys.argv[1:]
    real = None
    if "--real" in argv:
        i = argv.index("--real")
        real = argv[i + 1]
        del argv[i:i + 2]
    steps = None
    if "--steps" in argv:
        i = argv.index("--steps")
        steps = int(argv[i + 1])
        del argv[i:i + 2]
    size = None
    if "--size" in argv:
        i = argv.index("--size")
        size = tuple(int(x) for x in argv[i + 1].split("x"))
        del argv[i:i + 2]
    port = int(argv[0]) if argv else 8199
    stall = [int(x) for x in argv[1:]]
    if real:
        import real_backend
        print(f"本物のモデルを読みます: {real}", flush=True)
        t0 = time.monotonic()
        RENDER = real_backend.make_renderer(real, steps_override=steps,
                                            size_override=size)
        print(f"  読み込み完了({time.monotonic() - t0:.0f}秒)"
              f"  steps={steps or 'recipeのまま'} size={size or 'recipeのまま'}",
              flush=True)
    serve(port, stall)
    print(f"偽ComfyUI: http://127.0.0.1:{port}  "
          f"{'本物のモデルで描きます' if real else f'遅くする枚: {stall or None}'}",
          flush=True)
    while True:
        time.sleep(3600)
