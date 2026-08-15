#!/usr/bin/env python3
"""Unity Web のビルドを「配る側」の設定を変えて並べるサーバー。

8821 = ゲームのページを置くオリジン
8822 = ビルド一式を置く別オリジン(CDN のつもり)

8821 のパス:
  /plain/    ヘッダーなしのページ
  /coi/      COOP + COEP を付けたページ
  /w/ok           application/wasm  無圧縮
  /w/octet        application/octet-stream  無圧縮
  /w/br-bare      brotli の中身だが Content-Encoding なし
  /w/br           brotli + Content-Encoding: br
  /w/br-lie       中身は無圧縮なのに Content-Encoding: br
  /w/gz-bare      gzip の中身だが Content-Encoding なし
  /w/gz           gzip + Content-Encoding: gzip

8822 のパス(app.wasm と loader.js を置く):
  /bare/   何も付けない
  /cors/   Access-Control-Allow-Origin: *
  /corp/   Cross-Origin-Resource-Policy: cross-origin
"""
import http.server
import pathlib
import socketserver
import threading

HERE = pathlib.Path(__file__).resolve().parent
RAW = (HERE / "app.wasm").read_bytes()
GZ = (HERE / "app.wasm.gz").read_bytes()
BR = (HERE / "app.wasm.br").read_bytes()

WASM = "application/wasm"
OCTET = "application/octet-stream"

# パス -> (本体, Content-Type, 追加ヘッダー)
TABLE = {
    "/w/ok":      (RAW, WASM,  {}),
    "/w/octet":   (RAW, OCTET, {}),
    "/w/br-bare": (BR,  WASM,  {}),
    "/w/br":      (BR,  WASM,  {"Content-Encoding": "br"}),
    "/w/br-lie":  (RAW, WASM,  {"Content-Encoding": "br"}),
    "/w/gz-bare": (GZ,  WASM,  {}),
    "/w/gz":      (GZ,  WASM,  {"Content-Encoding": "gzip"}),
}

PAGE = b"""<!doctype html><html lang="ja"><head><meta charset="utf-8">
<title>unity web delivery probe</title></head><body>
<h1>probe</h1></body></html>
"""


class App(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _send(self, body, ctype, extra):
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        for k, v in extra.items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.rstrip("/") or "/"
        if path == "/ae":
            # ブラウザが送ってきた Accept-Encoding をそのまま返す
            v = self.headers.get("Accept-Encoding", "(なし)").encode()
            return self._send(v, "text/plain; charset=utf-8", {})
        if path in TABLE:
            body, ctype, extra = TABLE[path]
            return self._send(body, ctype, extra)
        extra = {}
        if path == "/coi":
            extra = {
                "Cross-Origin-Opener-Policy": "same-origin",
                "Cross-Origin-Embedder-Policy": "require-corp",
            }
        self._send(PAGE, "text/html; charset=utf-8", extra)

    def log_message(self, *a):
        pass


LOADER = b"window.__loaded = true;\n"


class Cdn(http.server.BaseHTTPRequestHandler):
    """ビルド一式を置いた別オリジン。先頭のパスで付けるヘッダーを変える。

    /bare/ … 何も付けない
    /cors/ … Access-Control-Allow-Origin: *
    /corp/ … Cross-Origin-Resource-Policy: cross-origin
    """
    protocol_version = "HTTP/1.1"

    def do_GET(self):
        js = self.path.endswith(".js")
        body = LOADER if js else RAW
        self.send_response(200)
        self.send_header(
            "Content-Type",
            "text/javascript; charset=utf-8" if js else WASM)
        self.send_header("Content-Length", str(len(body)))
        if self.path.startswith("/cors"):
            self.send_header("Access-Control-Allow-Origin", "*")
        if self.path.startswith("/corp"):
            self.send_header("Cross-Origin-Resource-Policy", "cross-origin")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


class Quiet(socketserver.ThreadingTCPServer):
    """ブラウザが遮断した応答は接続ごと切られる。
    その例外の追跡表示まで出すと実測ログが読めないので黙らせる。"""

    def handle_error(self, request, client_address):
        pass


def serve(port, handler):
    Quiet.allow_reuse_address = True
    # 127.0.0.1 と、ループバックでないIPの両方で受ける。
    # (ブラウザは localhost だけ「安全な文脈」として扱うため、
    #  IP直打ちの http:// との差を測れるようにする)
    srv = Quiet(("0.0.0.0", port), handler)
    srv.serve_forever()


if __name__ == "__main__":
    threading.Thread(target=serve, args=(8822, Cdn), daemon=True).start()
    serve(8821, App)
