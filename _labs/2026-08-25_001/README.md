# 2026-08-25_001 の検証記録

## 何を確かめたか

この号（`contents/2026-08-25_001/`）に書いた数値・日付・状態の出どころを、
全部コマンドで取り直せるようにしてある。

| 手順 | 確かめたこと | 記事のどこ |
|---|---|---|
| 1 | `minio/minio:latest` の最終 push が 2025-09-07 | Web開発・インフラ |
| 2 | MinIO のリポジトリが「もう保守しない」と表明している | 同上 |
| 3 | Laravel Sail の `minio.stub` が `minio/minio:latest` を指す | 同上 |
| 4 | Claude Tag の各ドキュメントの更新日時（sitemap の lastmod） | 実務者向け |
| 5 | Claude Code 2.1.241 の変更行が1行だけ | 裏取りの節 |
| 6 | AWS What's New の対象期間内の7件 | 裏取りの節 |
| 7 | VRChat の yt-dlp 要望が `open` のまま | クライアント技術 |

## 動かし方

```bash
bash _labs/2026-08-25_001/verify_sources.sh   # 出典の再取得
python3 _labs/2026-08-25_001/qa.py            # 幅380px/900pxの表示検証
```

`output.txt` は `verify_sources.sh` の実行結果をそのまま保存したもの。
記事に貼ったターミナル出力はここから取っている（幅に合わせて URL を `...` に
省略し、行継続 `\` を入れた以外は変えていない）。

## 実行時の環境

- 2026年8月25日 JST 早朝、Claude Code のリモート実行コンテナ
- python3 / curl のみ。追加で `pip install pillow playwright` と
  `python3 -m playwright install chromium`（表示検証に必要）

## つまずいた点（次回のため）

### 1. VRChat のフィードバック板は grep で誤判定する

`grep -oiE 'complete|planned|in progress'` でページ本文を見ると **`Complete` が出る**。
これは Canny（掲示板の仕組み）の**絞り込みUIのラベル**であって、投稿の状態ではない。
必ずページに埋め込まれた投稿オブジェクトから `"status"` を取ること（手順7）。

`creators.vrchat.com` と `feedback.vrchat.com` は、**連絡先入りの User-Agent が無いと403**。

### 2. AWS のセキュリティ速報のRSSは日付が当てにならない

先頭5件が全部 `2026-08-20` で返るが、本文を開くと
`2026-048-AWS` の Publication Date は **06/29/2026**。約2か月ずれる。
What's New フィードの「先頭の `<pubDate>` はチャンネルの生成時刻」問題（8/24に判明）
とは**別の罠**なので、両方覚えておくこと。個別ページの `Publication Date:` を見る。

### 3. Claude の公開ドキュメントは本文に更新日が出ない

`claude.com/docs/sitemap.xml`（217件）の `<lastmod>` で判定する。
`code.claude.com/docs/sitemap.xml` も同じ。ただし **lastmod は「変わった」しか分からず、
どこが変わったかは取れない**。差分が読めないものを「新機能」と書かないこと。

### 4. X(旧Twitter) は2日連続で取得できていない

`syndication.twitter.com` 系が 429。8/24号でも同じ。**経路の作り直しが要る。**
