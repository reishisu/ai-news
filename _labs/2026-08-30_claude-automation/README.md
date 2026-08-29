# Claude Code を無人で走らせたときに何が起きるか（2026-08-30）

記事: `contents/2026-08-30_claude-automation/`

## 何を確かめたか

`claude -p`（非対話モード）を cron のような無人の場所に置いたときに、
**「成功したのに何もしていない」状態が起きるか**、起きるならどう検出するか。

## 動かし方

```bash
bash run_all.sh 2>&1 | tee output.txt
```

`output.txt` は記事に貼ったものと同一。加工していない。
端末幅は記事の規約（幅380px）に合わせて `COLUMNS=40` で固定している。
作業ディレクトリは `/tmp/cc-auto-lab` に作り直すので、何度流しても同じ形になる。

## 実行時の環境

- Claude Code 2.1.251
- Ubuntu 24.04.4 LTS / Linux 6.18.44-fc-v22 x86_64
- 2026年8月30日 05:05〜05:35 JST に実行
- モデルは既定のまま（`--model` を指定した段7aを除く）

## 段の構成

| 段 | 見ていること |
|---|---|
| 1 | 版とOS |
| 2 | `claude -p` が動くこと |
| 3 | 権限が要る仕事は、exit 0 のまま実行されない |
| 4 | JSONでも `is_error=false` / `subtype=success` |
| 5 | `--allowedTools` で通る |
| 6 | `--permission-mode acceptEdits` でも通る |
| 7 | 本物のエラー（モデル名・ターン上限）は exit 1 |
| 8 | `Bash(git status:*)` のようにコマンド単位で許可できる |
| 9a | 許可した `rm` は3回とも実行された |
| 9b | 許可していない `rm` は3回とも denials に記録された |
| 9c | 命令文だけ変えて3回。9b と揃うか |
| 10 | `--max-budget-usd` は exit 1 で止まる |
| 11 | 標準入力から材料を渡せる |
| 12 | `--session-id` と `--resume` で続きから走る |

## やっていないこと

- `bypassPermissions` / `dontAsk` / `auto` / `manual` / `plan` の各モードは動かしていない。
  記事では `--help` の一覧として挙げるだけで、挙動を書かない
- `settings.json` の `permissions` による許可（CLIの旗だけを測った）
- MCPサーバーのツールに対する許可の挙動
- 実際の cron / CI に載せての長期運用

## 注意（測っている最中に分かったこと）

**同じ趣旨の命令でも、返り方が一定しない。**
最初の探りでは、許可していない `rm` を頼んだときに Claude が道具を呼ばずに
「削除してよろしいですか?」と聞き返し、`permission_denials` が空のまま
exit 0 で終わった。段9b・9c はその再現を狙っている。
**結果（2026/8/30 の実測）**: 段9c は 3回中2回で `denials=0` になり、
ファイルは3回とも残った。つまり `permission_denials` は
「出ていれば失敗が確実」だが「出ていなければ成功」とは言えない。
段9b は 1・2・5 と散らばった。記事の第8章がこの結果に対応する。

## 付属の道具

| ファイル | 何をするか |
|---|---|
| `run_all.sh` | 段1〜12を通しで実行し `output.txt` を作る |
| `keys.sh` | `--output-format json` のキーを全部並べ `keys.txt` を作る |
| `verify_pasted.py` | 記事の `.code term` の全行が、実行結果に逐語で在るかを照合する |
| `layout_qa.py` | 記事を幅380px/900pxで開き、横スクロール・はみ出し・JSエラーを測る |

**`layout_qa.py` は Playwright を使う。** Chromium を `--window-size=380` で
起動しても `innerWidth` は 500 に丸められるため、素のヘッドレスでは380pxを測れない
（2026/8/30に実測。`--dump-dom` 経由で「380pxで検証した」と誤って報告しかけた）。
