#!/usr/bin/env python3
"""キャッシュ事故を再現する確認用サーバー。

HTML   … no-cache (毎回サーバーに聞きに行く)
CSS/JS … max-age=600 (10分間はサーバーに聞きに行かない ← GitHub Pages と同じ値)

この2つの寿命が違うことが、崩れの原因になる。
届いたリクエストは access.log に記録する。
"""
import functools
import http.server
import socketserver

PORT = 8802
ROOT = "pub"


class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        if self.path.split("?")[0].endswith((".css", ".js")):
            self.send_header("Cache-Control", "max-age=600")
        else:
            self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def log_message(self, fmt, *args):
        with open("access.log", "a", encoding="utf-8") as f:
            f.write(f"{self.command} {self.path}\n")


if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    handler = functools.partial(Handler, directory=ROOT)
    with socketserver.TCPServer(("127.0.0.1", PORT), handler) as httpd:
        httpd.serve_forever()
