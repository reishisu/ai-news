# grill-me / grill-with-docs を入れて、動くところまで持っていく

記事: **未執筆**（2026/8/27 のルーティンで書く予定。`_HANDOFF.md` 参照）

## 何を確かめたか

Matt Pocock の "Skills For Real Engineers"（`mattpocock/skills`）から
`grill-me` と `grill-with-docs` を導入し、**実際に動く状態になるまで**を実測した。

| # | 確かめたこと | 結果 |
|---|---|---|
| 1 | 公式READMEどおりに `claude plugin install` が通るか | **通らない**。マーケットプレイス未登録だと失敗する |
| 2 | 何を足せば通るか | `claude plugin marketplace add anthropics/claude-plugins-official` |
| 3 | skills CLI で `grill-me` だけ入れたらどうなるか | **壊れる**。`Unknown skill: grilling` |
| 4 | 入っていない状態は何が返るか | `Unknown command: /grill-me`（0ターンで終了） |
| 5 | 入った状態は何が返るか | `❓ **Q1**` … `➡️ 推奨` の形式 |
| 6 | プラグイン経路のスキル名 | `mattpocock-skills:grilling` と名前空間が付く |
| 7 | grill-with-docs は本当に CONTEXT.md と ADR を書くか | **書く。ただし grilling が収束したあと** |

### 1 について（公式READMEとの食い違い）

README には "It's in Claude Code's official marketplace, so there's nothing to
add first" とある。実際 `mattpocock-skills` は `claude-plugins-official`
（289プラグイン）に**入っている**。それでも失敗するのは、公式マーケットプレイスの
登録タイミングが理由。公式ドキュメント（Create plugins）にこう書かれている:

> Claude Code registers it automatically the first time you start Claude Code
> interactively. If you run Claude Code non-interactively before that first
> interactive launch, or a marketplace policy blocked an earlier attempt,
> register it yourself with
> `claude plugin marketplace add anthropics/claude-plugins-official`.

つまり **`claude` を対話で1度も起動していない環境（CI・コンテナ・-p 専用）では
自動登録されない。** この検証環境がまさにそれだった。

### 7 について（domain-modeling が発火するタイミング）

`grill-with-docs` の本文は「`grilling` と `domain-modeling` を呼べ」の1行。
だが3ラウンド流したところ、実際に呼ばれたのは:

| ラウンド | 呼ばれたSkill | 書かれたファイル |
|---|---|---|
| 1（お題を渡す） | `grilling` | なし |
| 2（Q1〜Q3に回答） | （なし・grilling継続） | なし |
| 3（残りに回答＋「認識は揃いました」） | `domain-modeling` | `CONTEXT.md` / `docs/adr/0001-*.md` |

**質問が尽きるまで書き始めない。** 途中で止めるとドキュメントは残らない。
生成物は `artifacts/` にそのまま置いた。

## 動かし方

```bash
./setup_plugin.sh /tmp/ccfg          # 経路A: プラグイン
./setup_skills_cli.sh /path/to/proj  # 経路B: skills CLI
./verify.sh /path/to/proj            # 動作確認
```

`setup_plugin.sh` に渡すパスは `CLAUDE_CONFIG_DIR`。
**本番の `~/.claude` を汚さずに試せる**ので、検証はこれで行った。

## ファイル

| ファイル | 中身 |
|---|---|
| `setup_plugin.sh` | 経路A（プラグイン）の手順 |
| `setup_skills_cli.sh` | 経路B（skills CLI）の手順 |
| `verify.sh` | 対話画面を開かずに動作確認する |
| `output.txt` | 導入の実出力（未登録での失敗 → 登録 → 成功） |
| `output_verify.txt` | 4つの状態で `/grill-me` を叩いた実出力 |
| `artifacts/` | grill-with-docs が実際に書いた CONTEXT.md と ADR |

## 実行環境

- 2026年8月27日 JST（UTC では8月26日18時台）
- Linux x86-64 コンテナ / Claude Code 2.1.246 / Node.js 22.22.2 / npm 10.9.7
- `mattpocock-skills` プラグイン v1.2.3（25スキル）
- `skills` CLI v1.5.23（vercel-labs/skills）

## 測った数字

| 項目 | プラグイン | skills CLI |
|---|---|---|
| 導入にかかった時間 | 11秒（登録3秒＋導入8秒） | 2秒 |
| ディスク使用量 | 39MB | 40KB（2スキル） |
| 入るスキルの数 | 25 | 選んだぶんだけ |
| 常駐トークン | 約1,609（`claude plugin details` の表示） | 選んだぶんだけ |

時間は1回ずつの計測なので、回線状況で変わる。
