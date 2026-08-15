# 2026-08-14_cache-busting の検証物

## 何を確かめたか
GitHub PagesでCSSが古いまま配信される事故の再現

## ファイル
```
serve.py … GitHub Pagesと同じ Cache-Control を返す確認用サーバー(HTML=no-cache / CSS=max-age=600)
repro.js … HTMLだけ新しくなり、CSSが古いまま残る状況を作って色を測る
notwork.js … 効かない対処(再訪問/F5/更新日時/別タブ)と効く対処(シークレット/Ctrl+Shift+R)を比較
pad.js … 日本語を全角2文字として桁を揃える(出力を幅380pxに収めるため)
```

## 動かし方
```bash
python3 serve.py &   # 8802番で待ち受け
node repro.js
node notwork.js
```

## 実行環境（記事に載せた数値を取ったときの構成）
Python 3.11.15 / Node.js v22.22.2 / Chromium 141.0.7390.37
playwright-core が必要。node_modules が無ければ `npm i playwright-core`。
Chromium は `/opt/pw-browsers/chromium` を executablePath に指定する。

## 注意
記事の数値を書き換えるときは、**必ずここで測り直してから**直すこと。
出力を手で書き換えるのは禁止（それは嘘になります）。
