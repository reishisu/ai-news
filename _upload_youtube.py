#!/usr/bin/env python3
"""_render_video.py が作ったMP4を、YouTubeにアップロードする。

**この環境では未実行**(認証情報が無いため。アップロードもトークン取得も
実行していない)。APIの仕様は公式リファレンス(developers.google.com/youtube/v3)に
沿って書いたが、初回は必ず手元で動作確認すること。

## 前提

- GCP側のセットアップが済んでいること(_video/README.md)
- 環境変数: YT_CLIENT_ID / YT_CLIENT_SECRET / YT_REFRESH_TOKEN

## 使い方

```bash
python3 _upload_youtube.py --get-token        # 初回: リフレッシュトークンを取る(手元のPCで)
python3 _upload_youtube.py 2026-08-18_001     # privateでアップロード
python3 _upload_youtube.py 2026-08-18_001 --privacy unlisted
```

- 既定は **private**。未監査のAPIプロジェクトはどのみちprivateに制限される
  (公式リファレンスに明記)うえ、「公開は人が確認してから」が方針のため
- サムネイルは記事の images/thumb.png を設定する(チャンネルの電話番号認証が必要)
- 標準ライブラリだけで動く(google-api-python-client は使わない)
"""

import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT_ROOT = HERE / "_video_out"
CONTENTS = HERE / "contents"

SCOPE = "https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube"
TOKEN_URL = "https://oauth2.googleapis.com/token"
UPLOAD_URL = ("https://www.googleapis.com/upload/youtube/v3/videos"
              "?uploadType=resumable&part=snippet,status")
THUMB_URL = "https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId={vid}"


def post_form(url, data):
    req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode(),
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


def get_token():
    """初回だけ手元のPCで実行して、リフレッシュトークンを取る。

    OAuthの「デスクトップアプリ」クライアントの loopback フロー。
    ブラウザで許可すると localhost にコードが返ってくる。
    """
    import http.server
    import secrets
    import webbrowser

    cid = os.environ.get("YT_CLIENT_ID") or input("クライアントID: ").strip()
    csec = os.environ.get("YT_CLIENT_SECRET") or input("クライアントシークレット: ").strip()
    state = secrets.token_urlsafe(16)
    port = 8765
    redirect = f"http://127.0.0.1:{port}"
    auth = ("https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode({
        "client_id": cid, "redirect_uri": redirect, "response_type": "code",
        "scope": SCOPE, "access_type": "offline", "prompt": "consent", "state": state}))
    print("ブラウザで開いて許可してください:\n", auth)
    webbrowser.open(auth)

    code_box = {}

    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            if q.get("state", [""])[0] == state and "code" in q:
                code_box["code"] = q["code"][0]
                body = b"OK. This window can be closed."
            else:
                body = b"invalid request"
            self.send_response(200)
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *a):
            pass

    with http.server.HTTPServer(("127.0.0.1", port), H) as srv:
        while "code" not in code_box:
            srv.handle_request()
    tok = post_form(TOKEN_URL, {
        "client_id": cid, "client_secret": csec, "code": code_box["code"],
        "grant_type": "authorization_code", "redirect_uri": redirect})
    print("\n以下を環境変数(またはSecrets)に設定してください:")
    print(f"  YT_CLIENT_ID={cid}")
    print(f"  YT_CLIENT_SECRET={csec}")
    print(f"  YT_REFRESH_TOKEN={tok['refresh_token']}")


def access_token():
    for name in ("YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN"):
        if not os.environ.get(name):
            raise SystemExit(f"環境変数 {name} がありません(_video/README.md 参照)")
    tok = post_form(TOKEN_URL, {
        "client_id": os.environ["YT_CLIENT_ID"],
        "client_secret": os.environ["YT_CLIENT_SECRET"],
        "refresh_token": os.environ["YT_REFRESH_TOKEN"],
        "grant_type": "refresh_token"})
    return tok["access_token"]


def api_request(url, data, headers, method="POST", retries=3):
    """5xxだけ 2/4/8秒 でリトライする。4xxは設定ミスなのですぐ止める。"""
    for i in range(retries + 1):
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            return urllib.request.urlopen(req, timeout=600)
        except urllib.error.HTTPError as err:
            if err.code >= 500 and i < retries:
                time.sleep(2 ** (i + 1))
                continue
            body = err.read().decode(errors="replace")[:800]
            raise SystemExit(f"APIエラー {err.code}: {body}")


def upload(dirname, privacy):
    mp4 = OUT_ROOT / f"{dirname}.mp4"
    meta_path = OUT_ROOT / dirname / "youtube.json"
    if not mp4.is_file() or not meta_path.is_file():
        raise SystemExit(f"{mp4} がありません。先に _render_video.py を実行してください")
    yt = json.loads(meta_path.read_text(encoding="utf-8"))
    token = access_token()

    body = json.dumps({
        "snippet": {
            "title": yt["title"],
            "description": yt["description"],
            "tags": yt.get("tags", []),
            "categoryId": yt.get("categoryId", "28"),
            "defaultLanguage": "ja",
            "defaultAudioLanguage": "ja",
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False,
        },
    }, ensure_ascii=False).encode("utf-8")

    # 1. resumable セッションを開く → アップロード先URLが Location で返る
    r = api_request(UPLOAD_URL, body, {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=UTF-8",
        "X-Upload-Content-Type": "video/mp4",
        "X-Upload-Content-Length": str(mp4.stat().st_size)})
    session = r.headers["Location"]

    # 2. 本体を送る
    print(f"アップロード中: {mp4.name} ({mp4.stat().st_size / 1e6:.1f}MB, {privacy})")
    r = api_request(session, mp4.read_bytes(), {
        "Authorization": f"Bearer {token}",
        "Content-Type": "video/mp4"}, method="PUT")
    video = json.loads(r.read().decode())
    vid = video["id"]
    print(f"完了: https://youtu.be/{vid} (privacyStatus={privacy})")

    # 3. サムネイル(記事と同じ絵)。電話番号認証が無いチャンネルでは失敗する
    thumb = CONTENTS / dirname / "images" / "thumb.png"
    if thumb.is_file():
        try:
            api_request(THUMB_URL.format(vid=vid), thumb.read_bytes(), {
                "Authorization": f"Bearer {token}", "Content-Type": "image/png"})
            print("サムネイルを設定しました")
        except SystemExit as err:
            print(f"サムネイル設定は失敗(動画は上がっています): {err}", file=sys.stderr)
    return vid


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dirname", nargs="?", help="記事ディレクトリ名")
    ap.add_argument("--privacy", default="private",
                    choices=["private", "unlisted", "public"])
    ap.add_argument("--get-token", action="store_true",
                    help="初回のリフレッシュトークン取得(手元のPCで)")
    args = ap.parse_args()
    if args.get_token:
        get_token()
        return
    if not args.dirname:
        ap.error("記事ディレクトリ名を指定してください")
    upload(args.dirname, args.privacy)


if __name__ == "__main__":
    main()
