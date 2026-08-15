"""
provider_v2_broken.py
providerチームが後日、consumerに知らせずに入れてしまった
破壊的変更のシナリオ。

やってしまった変更:
  1. "score" フィールドを "relevance_score" にリネームした
  2. "id" を整数から文字列("s-1"のような形)に変えた

サーバー内部の見直しのつもりだったが、
契約(schema.json)には合わせていない。
"""


def search(q: str) -> dict:
    """検索APIのレスポンスを生成する(v2・契約を破っている)。"""
    data = [
        {"id": "s-1", "title": "Unity WebGLの基礎", "relevance_score": 0.92},
        {"id": "s-2", "title": "WebViewとfetch", "relevance_score": 0.71},
        {"id": "s-3", "title": "VRChatワールド入門", "relevance_score": 0.55},
    ]
    hits = [d for d in data if q in d["title"]] if q else data
    return {"results": hits, "total": len(hits)}


if __name__ == "__main__":
    import json
    print(json.dumps(search(""), ensure_ascii=False, indent=2))
