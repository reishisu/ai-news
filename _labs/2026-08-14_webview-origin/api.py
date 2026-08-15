#!/usr/bin/env python3
"""WebView からの呼び出しを試すための API サーバー。

CORS の返し方を3通り切り替えられる。
  /none       … CORS ヘッダーを返さない
  /star       … Access-Control-Allow-Origin: *
  /allowlist  … Access-Control-Allow-Origin: https://app.example.com (よくある許可リスト方式)
  /star-cred  … Access-Control-Allow-Origin: * + Allow-Credentials: true (Cookie付きを試す用)
"""
import http.server
import json
import socketserver

PORT = 8803


class Handler(http.server.BaseHTTPRequestHandler):
    def _cors(self):
        mode = self.path.strip("/").split("?")[0]
        if mode == "star":
            self.send_header("Access-Control-Allow-Origin", "*")
        elif mode == "allowlist":
            self.send_header("Access-Control-Allow-Origin", "https://app.example.com")
        elif mode == "echo":
            # 「リクエストのOriginをそのまま返す」実装。よく書かれるが穴になる
            self.send_header("Access-Control-Allow-Origin",
                             self.headers.get("Origin", "*"))
            self.send_header("Access-Control-Allow-Credentials", "true")
        # none は何も返さない

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.send_header("Access-Control-Allow-Headers", "content-type")
        self.end_headers()

    def do_GET(self):
        body = json.dumps({"ok": True}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        origin = self.headers.get("Origin", "(なし)")
        with open("api.log", "a", encoding="utf-8") as f:
            f.write(f"{self.command} {self.path}  Origin: {origin}\n")


if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
        httpd.serve_forever()
