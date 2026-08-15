#!/usr/bin/env python3
"""Unity Web (WebAssembly) のマルチスレッドに必要な条件を確かめるサーバー。

/plain/  … 何もヘッダーを付けない
/coi/    … COOP と COEP を付ける(クロスオリジン分離)
"""
import http.server
import socketserver

PORT = 8811

PAGE = b"""<!doctype html><html lang="ja"><head><meta charset="utf-8"></head>
<body><h1>probe</h1></body></html>
"""


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(PAGE)))
        if self.path.startswith("/coi"):
            self.send_header("Cross-Origin-Opener-Policy", "same-origin")
            self.send_header("Cross-Origin-Embedder-Policy", "require-corp")
        self.end_headers()
        self.wfile.write(PAGE)

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
        httpd.serve_forever()
