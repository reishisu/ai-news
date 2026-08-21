# 2026-08-22_001 の検証記録

## 何を確かめたか

1. **記事の表示検証（CLAUDE.md 第7節）** — `qa.py`
   幅380px / 900px で開き、横スクロール・要素のはみ出し・`.code pre` の背景・
   JSエラー・チェックリストの動作を実測する。

2. **Claude Code 2.1.239 の変更行を数える（CLAUDE.md 第16節）** — `count_changelog.sh`
   全59行のうち何件を採用し何件を落としたかを、記事の記載と突き合わせるため。

3. **Chrome Releases に WebView 専用の告知が出ているか** — `webview_label.sh`
   ラベル別フィードを取得し、最新の投稿日を見る。

## 動かし方

```bash
pip install playwright        # ブラウザは /opt/pw-browsers/chromium を使う
python3 qa.py                 # ai-news-dev のリポジトリ直下で実行する
bash count_changelog.sh
bash webview_label.sh
```

## 2026-08-22 の実行結果

- `qa.py`: 幅380 / 900 とも横スクロール0・はみ出しなし・JSエラー0・
  チェックリスト 0/3 → 1/3 で反応。文書高は380pxで19700px（28.1画面）
- `count_changelog.sh`: 2.1.239 は `- ` 行が59行、うち `- Fixed` が39行。
  記事で扱ったのは3件、落としたのは56件
- `webview_label.sh`: 「Android WebView」ラベルの最新投稿は
  `Android WebView Stable Update` 2015-09-08T16:23:00。それ以降は無し

## 実行環境

Linux (Claude Code on the web のコンテナ) / Python 3 / Chromium は
`/opt/pw-browsers/chromium`。Pillow と Playwright は都度 `pip install` している
（コンテナが作り直されると消える）。
