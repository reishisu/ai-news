# 2026-08-14_webview-origin の検証物

## 何を確かめたか
file:// から呼んだときのCORSの通り方

## ファイル
```
api.py … CORSの返し方を4通り切り替えるAPI(none / star / allowlist / echo)。受け取ったOriginをログに残す
cors.js … file:// と http:// の両方から、4通り×Cookie有無で fetch して結果を表にする
probe.js … file:// でのオリジン・localStorage・fetch の可否を並べる
```

## 動かし方
```bash
python3 api.py &     # 8803番で待ち受け
node cors.js
cat api.log        # 届いたOriginを確認
```

## 実行環境（記事に載せた数値を取ったときの構成）
Python 3.11.15 / Node.js v22.22.2 / Chromium 141.0.7390.37
playwright-core が必要。node_modules が無ければ `npm i playwright-core`。
Chromium は `/opt/pw-browsers/chromium` を executablePath に指定する。

## 注意
記事の数値を書き換えるときは、**必ずここで測り直してから**直すこと。
出力を手で書き換えるのは禁止（それは嘘になります）。
