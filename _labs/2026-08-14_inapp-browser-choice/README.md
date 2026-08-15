# アプリ内ブラウザの選び方 — 検証コード

記事: `contents/2026-08-14_inapp-browser-choice/`

## 何を確かめたか

「WebView / Custom Tabs / SFSafariViewController の違いは、Cookieとストレージの置き場である」
という記事の主張を、ブラウザ側の性質として再現する。

| ファイル | 確かめること |
|---|---|
| `server.js` | ログインするだけの最小サイト。`sid` Cookie(HttpOnly) を配り、localStorage に初回だけランダムな印を置く |
| `exp1_share.js` | データ置き場(プロファイル)が別か同じかで、ログイン状態が引き継がれるかを測る |
| `exp2_spy.js` | 埋め込み型ではホストアプリが入力キーとHttpOnly Cookieを盗めることを実演（RFC 8252 §8.12 の懸念そのもの） |

## 動かし方

`playwright-core` だけに依存する。同ディレクトリに `node_modules/playwright-core` が要る。

```bash
node server.js &                      # http://127.0.0.1:8863
rm -rf prof    && node exp1_share.js ./prof
rm -rf spyprof && node exp2_spy.js
```

Chromium の実体は `/opt/pw-browsers/chromium`（両スクリプトの `EXE` に直書き）。

## 実行環境

- Chromium 141.0.7390.37
- Node.js v22.22.2
- playwright-core 1.62.1
- Python 3.11.15 / Linux 6.18.5
- 初回実行: 2026年8月14日

## 実行結果

`output.txt` が記事に貼ったものと同一。

## 再現性の注意

`ls.tag` の値は `Math.random().toString(36).slice(2, 8)` なので**毎回変わる**。
比較すべきは値そのものではなく、次の3点。

1. `1` と `4` の `ls.tag` が一致する（同じ置き場を見ている）
2. `2` と `3` は互いに別値で、どちらも `status: ANON`
3. `4` はログイン操作なしで `LOGGED_IN alice`

2026年8月15日に別ディレクトリで再実行し、上の3点がすべて再現することを確認した
（そのときの `ls.tag` は `7q56e8` / `a9k8dp` / `14s3uh` / `7q56e8`）。
`exp2_spy.js` の出力は `output.txt` と1文字も違わなかった。

## この実験でわかっていないこと

iOS / Android の実機と、SFSafariViewController・Custom Tabs・WKWebView そのものは動かしていない。
測ったのは「アプリがコンテキストを共有できるか / 隔離されるか / 制御できるか」という
ブラウザ側の性質だけで、Chromium の `launchPersistentContext` のデータディレクトリ切り替えで代替した。
各プラットフォームのAPIが実際にどちらの領域を使うかは、記事では一次資料の記述のみを根拠にしている。
