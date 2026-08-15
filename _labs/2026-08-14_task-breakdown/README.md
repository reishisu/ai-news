# 2026-08-14_task-breakdown の検証物

## 何を確かめたか
タスクの依存関係から最短日数と全余裕を出す

## ファイル
```
critical_path.py … TASKS に (id, 名前, 日数, 依存) を書くと、前向き計算で最早開始/終了、
                   後ろ向き計算で最遅開始を出し、全余裕(total float)と最長経路を表示する
```

## 動かし方
```bash
python3 critical_path.py
```

## 実行環境（記事に載せた数値を取ったときの構成）
Python 3.11.15 / Node.js v22.22.2 / Chromium 141.0.7390.37
playwright-core が必要。node_modules が無ければ `npm i playwright-core`。
Chromium は `/opt/pw-browsers/chromium` を executablePath に指定する。

## 注意
記事の数値を書き換えるときは、**必ずここで測り直してから**直すこと。
出力を手で書き換えるのは禁止（それは嘘になります）。
