# 2026-08-14_unity-web-threads の検証物

## 何を確かめたか
クロスオリジン分離の有無でSharedArrayBufferがどうなるか

## ファイル
```
coi.py … 同じHTMLを、COOP/COEPヘッダーの有無だけ変えて2つのURLで配る
probe.js … 両方のURLを開き crossOriginIsolated / SharedArrayBuffer / WebGL2 / WebGPU を測る
```

## 動かし方
```bash
python3 coi.py &     # 8811番で待ち受け
node probe.js
```

## 実行環境（記事に載せた数値を取ったときの構成）
Python 3.11.15 / Node.js v22.22.2 / Chromium 141.0.7390.37
playwright-core が必要。node_modules が無ければ `npm i playwright-core`。
Chromium は `/opt/pw-browsers/chromium` を executablePath に指定する。

## 注意
記事の数値を書き換えるときは、**必ずここで測り直してから**直すこと。
出力を手で書き換えるのは禁止（それは嘘になります）。
