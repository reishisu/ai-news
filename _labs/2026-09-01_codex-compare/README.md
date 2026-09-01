# 2026-09-01 Claude Code / Codex 分業実測

## この記事で使う確定値

- Codex CLI: `0.151.0`
- 実行時間: `181.232` 秒
- exit code: `0`
- Codex側: `16,817` tokens
- Claudeへ渡した最終結果: `6` 行・`310` 文字
- Claude Code: `2.1.251 (Claude Code)`

`codex-exec-metrics.txt`、`codex-exec-raw.log`、`codex-exec-result.txt` が
初回の測定3点です。録画の撮り直しではこれらを変更せず、`recording-` 接頭辞の
別ファイルへ出しました。

## 数値訂正

初回の6行には「長尺19本・中央値28・2.5倍」という誤りがあります。
19本は原稿がある動画だけでした。`VIEWS_LOG.json` の全記録で数え直した正は次です。
この誤りはCodexとClaudeの両方が最初は見逃し、Claudeが後から全記録を
自分で数え直して発見しました。相互検証で捕捉した誤りではありません。

- 長尺23本
- 中央値22
- 69再生は23本中6位
- 中央値の3.1倍

`MUST-number-correction.md` と `recording-codex-exec-result.txt` を参照してください。

## 実行コマンド

研究実行は `run-research-demo.ps1` 内の次の呼び出しです。

```powershell
& codex exec --sandbox read-only --skip-git-repo-check --color never `
  -c 'plugins."computer-use@openai-bundled".enabled=false' `
  -c 'plugins."chrome@openai-bundled".enabled=false' `
  -c 'plugins."browser@openai-bundled".enabled=false' `
  -o $lastMessage $prompt
```

画像引数の再現は次です。

```powershell
codex exec --sandbox read-only --skip-git-repo-check --color never `
  -i out/wintest/probe_12s.png "画像の文字を一行で書き写す"
```

出力は次の1行です。

```text
No prompt provided. Either specify one as an argument or pipe the prompt into stdin.
```

## 録画

Windows Terminalへの引き渡しを `conhost.exe -ForceNoHandoff --` で止め、
PowerShell 7を不透明なconhost内で起動しました。3本とも1458x812で、
2.30:1のcropは `[0, 0, 1458, 634]` です。

- `takes/2026-09-01_codex-compare/research.mp4`
- `takes/2026-09-01_codex-compare/research-result.mp4`
- `takes/2026-09-01_codex-compare/image-arity.mp4`

必須の目視確認コマ:

- `out/_codex/verify-research.png`
- `out/_codex/verify-research-result.png`
- `out/_codex/verify-image-arity.png`

## 限界

- モデルの賢さ、SWE-bench、料金は比較していません。
- Claude側の仕事単位トークンは測れません。
- 75,201対11,393は入力準備と依頼範囲が違う2実行で、統制実験ではありません。
- 現在の `rebuttal.log` は108,156バイト・75,201 tokensで完走した後続実行です。
  7分で止めた先行試行のログと同一視しません。
- Claudeが7分で止めた進行判断は運営者が訂正しました。短縮版は60秒で返ったものの
  根拠が1つ誤り、待って完走した版が題材を覆す反論を出しました。

## 公開版で伏せた箇所について

このディレクトリは記事の検証可能性のために公開しています。ただし次の2点だけ、
**元のログから伏せて（または外して）あります。**

1. **運営方針の数字**（チャンネルの目標・登録者数・1日あたりの再生ペース）は
   `（運営方針の数字のため、公開版では伏せています）` に置き換えました。
   **測定値そのものは1つも変えていません。**
2. **`rebuttal.log` は公開していません。** 108,156バイトのうちに、この非公開
   リポジトリのスクリプトの全文が引用されていたためです。

`rebuttal.log` について、記事と動画が引用している値は次のとおりです。

| | 値 |
|---|---|
| ファイルの大きさ（元） | **108,156 バイト** |
| Codex側のトークン | **75,201** |
| 版 | `codex-cli 0.151.0` |

同じ実行の**Codexの回答そのもの**は `topic-rebuttal-2026-09-01.md` に全文があります。
