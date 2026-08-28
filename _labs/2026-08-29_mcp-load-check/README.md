# 2026-08-29 「入れたMCPサーバーが読み込まれたか確かめる」の検証一式

記事: `contents/2026-08-29_mcp-load-check/`

## 何を確かめたか

1. `claude mcp add` は、**存在しないファイルを指しても成功する**（設定を書いただけ）
2. 繋がったかどうかは `claude mcp list` の健康チェックで初めて分かる
3. **同じサーバーを local と project の2スコープに入れると、片方だけ繋がらない。**
   `.mcp.json`（project スコープ）は `⏸ Pending approval` になる
4. **その承認待ちのサーバーは、`claude -p`（ヘッドレス）からは呼べる。**
   一覧の表示と、実際に読み込まれるかは別物だった
5. 締め出す手段は2つ効いた: `--strict-mcp-config` と `disabledMcpjsonServers`
6. `disabledMcpjsonServers` で拒否すると、**`claude mcp list` からは消える**
   （`No MCP servers configured` と出る）。`claude mcp get <名前>` には残る

## 動かし方

```bash
bash run_all.sh 2>&1 | tee output.txt
```

`run_all.sh` は `/home/user/lab-mcp/proj` を作り直してから始めるので、何度でも同じ結果になる。
`hello_server.py` は依存なしの最小MCPサーバー（stdio・ツール1つ）。`pip install` は要らない。

**サーバーは作業ディレクトリ直下に `hello.py` として置いてから登録している。**
`claude mcp list` は登録したコマンドをそのまま行に出すので、絶対パスで登録すると
1行が85桁を超える。パスを短くしたのは**出力形式を先に直してから実行し直した**もので、
出た文字を後から書き換えたわけではない（CLAUDE.md 第4節）。

それでも `× Failed to connect — CONNECTION_CLOSED: Connection closed`（85桁）と
`⏸ Pending approval (run \`claude\` to approve)`（69桁）は40桁に収まらない。
**この2つは `claude` 自身が出す文言なので縮められない。** 記事にはそのまま貼った。

## 実行環境（2026年8月29日 05:00〜06:00 JST に実行）

- Claude Code **2.1.251**
- Ubuntu 24.04.4 LTS / Linux 6.18.44
- Python 3.11.15
- `COLUMNS=40` を付けて実行（記事の幅に合わせるため。CLAUDE.md 第4節）

## やっていないこと

- **対話セッション（`claude` を素で起動）は試していない。** この環境は無人実行なので、
  承認ダイアログを出す経路そのものを踏めない。記事で対話側について書いた部分は
  すべて公式ドキュメントの引用で、自分の実測ではない
- **HTTP/SSE トランスポートのサーバーは試していない**（stdio のみ）。
  `Needs authentication` の状態は再現していない
- **`claude mcp reset-project-choices` は実行していない。** 承認した状態を
  作れなかったので、リセットする対象が無かった
- `enableAllProjectMcpServers` と、ワークスペース信頼（trust dialog）まわりは
  対話が要るので確かめていない
- 実在のMCPサーバー（Notion / Sentry など）には**一切接続していない**

## 出力の扱い

`output.txt` は `run_all.sh` の出力をそのまま貼ったもの。**1文字も編集していない。**
記事に載せた端末ログは、このファイルからの抜粋。行を省いた箇所は記事側に「(中略)」と書いた。

## 引用した一次資料

`docs_excerpt.txt` は https://code.claude.com/docs/en/mcp.md から該当箇所を抜いたもの
（2026年8月29日取得）。`curl` で全文（1,471行）を取得し、該当節を読んで確認した。

## 記事に貼ったコマンドとの差（1点だけ）

`run_all.sh` の `claude -p` には、無人実行で止まらないように
`< /dev/null 2>&1 | tail -2` を付けている。**記事にはこの配管を載せていない**
（読者が手で叩くときには要らないため）。コマンド本体と出力は一字一句そのまま。

`verify_pasted.py` が、記事に貼った端末ログの各行を `output.txt` と
`run_all.sh` に突き合わせる。**公開前に必ず走らせる。**

```bash
python3 verify_pasted.py
```

## 引用の検査

`check_quotes.py` が、記事に貼った英語の原文を公式ドキュメントと突き合わせる。
**公式ドキュメント本体はコミットしていない**（他社の文書なので、必要な箇所だけ
`docs_excerpt.txt` に引いてある）。走らせるときは先に取得する。

```bash
curl -sSL https://code.claude.com/docs/en/mcp.md -o mcp.md
python3 check_quotes.py mcp.md
```
