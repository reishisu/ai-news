"""
provider_v1.py
providerチーム(委託先サーバー)が最初に実装した
GET /api/search?q=... のレスポンス生成コード。

契約(schema.json)どおりの形で返す。
実際のDB検索は行わず、固定データで応答を模擬する。
"""


def search(q: str) -> dict:
    """検索APIのレスポンスを生成する(v1・契約どおり)。"""
    data = [
        {"id": 1, "title": "Unity WebGLの基礎", "score": 0.92},
        {"id": 2, "title": "WebViewとfetch", "score": 0.71},
        {"id": 3, "title": "VRChatワールド入門", "score": 0.55},
    ]
    hits = [d for d in data if q in d["title"]] if q else data
    return {"results": hits, "total": len(hits)}


if __name__ == "__main__":
    import json
    print(json.dumps(search(""), ensure_ascii=False, indent=2))
