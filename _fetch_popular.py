#!/usr/bin/env python3
"""GoatCounterから各記事の閲覧数を取得して popular.json に書き出す。

トップページの「よく読まれている記事」はこのファイルを見て並びます。
ファイルが無い/空のときは、代わりに meta.json の featured が使われるので、
このスクリプトが失敗してもサイトは壊れません。

必要なもの:
  site.json の analytics.code   … GoatCounter のサイトコード
  環境変数 GOATCOUNTER_TOKEN    … GoatCounter の API トークン
    (GoatCounter の [設定] → [API tokens] で作成。権限は「Read statistics」だけでよい)
  ※ トークンはリポジトリに置かないこと。実行環境の環境変数に入れる。

使い方:
  GOATCOUNTER_TOKEN=xxxxx python3 _fetch_popular.py [集計日数(既定30)]
"""

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "popular.json"


def site_code():
    try:
        conf = json.loads((HERE / "site.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ""
    return str((conf.get("analytics") or {}).get("code") or "").strip()


def fetch(code, token, days):
    """記事ページのパスと閲覧数の一覧を返す。"""
    start = (date.today() - timedelta(days=days)).isoformat()
    url = (f"https://{code}.goatcounter.com/api/v0/stats/hits"
           f"?start={start}&limit=200")
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    })
    with urllib.request.urlopen(req, timeout=30) as res:
        data = json.loads(res.read().decode("utf-8"))

    items = []
    for hit in data.get("hits", []):
        path = str(hit.get("path", ""))
        if "/contents/" not in path:
            continue  # 記事ページだけを対象にする
        items.append({"path": path, "count": int(hit.get("count", 0))})
    items.sort(key=lambda x: -x["count"])
    return items


def main():
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    code = site_code()
    token = os.environ.get("GOATCOUNTER_TOKEN", "").strip()

    if not code:
        print("site.json に GoatCounter のサイトコードがありません。何もしません。")
        return
    if not token:
        print("環境変数 GOATCOUNTER_TOKEN がありません。何もしません(サイトは featured で表示されます)。")
        return

    try:
        items = fetch(code, token, days)
    except (urllib.error.URLError, urllib.error.HTTPError, ValueError, KeyError) as e:
        print(f"閲覧数の取得に失敗しました: {e}", file=sys.stderr)
        return  # 失敗しても既存の popular.json はそのまま残す

    OUT.write_text(
        json.dumps({"updated": date.today().isoformat(), "days": days, "items": items},
                   ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"popular.json を更新しました(直近{days}日・{len(items)}ページ)")


if __name__ == "__main__":
    main()
