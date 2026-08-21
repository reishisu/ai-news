# YouTube需要シグナルの収集（2026-08-21）

## 何を確かめたか

「次に書く記事のネタを、YouTubeの需要から見つけられるか」を測った。

## 動かし方

```bash
python3 _youtube_demand.py --domain aiツール --period week --out _labs/2026-08-21_demand/
python3 _youtube_demand.py --domain サーバー --domain クライアント --domain チーム \
        --period week --out _labs/2026-08-21_demand/other/
python3 _youtube_demand.py --period month --query "ALB 502" ... \
        --out _labs/2026-08-21_demand/symptoms/
```

取得元は YouTube の内部API（`youtubei/v1/search`、WEBクライアント）。
`params` は protobuf で「視聴回数順 + 投稿日フィルタ + 種別=動画」を指定している。
日割り視聴 = 視聴回数 ÷ 投稿からの日数（下限1日）。

## 結果

| 収集 | 検索語 | 動画 | 最高の日割り視聴 |
|---|---|---|---|
| `demand.json`（AI開発ツール・1週間） | 8 | 105 | 59,955回/日 |
| `other/demand.json`（サーバー等・1週間） | 22 | 38 | 3,276回/日 |
| `symptoms/demand.json`（症状で引く・1か月） | 8 | 3 | 3回/日 |

## 分かったこと

1. 需要はAI開発ツールに極端に偏る（語あたり13.1本 対 1.7本、ピークで約18倍）
2. **症状で引いても読者スタックの需要は出てこない。** 1か月8語で3本。
   この層はYouTubeではなく検索で解決している
3. よって YouTube は AI開発ツールのネタ探しにだけ使う。
   読者スタック側は公式の変更履歴と読者の実務から拾う

## 注意

需要が大きい項目ほど噂が混ざる。今回、日割り視聴の上位にあった
「DeepSeek Harness」「Claude Code の /design」は**一次資料を確認できず**、
ネタ帳では保留にした（`_TOPICS.md`）。

## 実行環境

Python 3（標準ライブラリのみ）。2026-08-21 に実行。
視聴回数は日々変わるので、同じコマンドでも数値は再現しない。
