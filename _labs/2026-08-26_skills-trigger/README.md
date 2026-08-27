# スキルが自動で呼ばれる条件を測る

記事: `contents/2026-08-26_skills-trigger/`

## 何を確かめたか

Claude Code のスキルが「AIの判断で自動的に呼ばれる」かどうかは何で決まるのかを、
同じ質問を各条件10回ずつ投げて数えた（合計60回）。

| 実験 | 固定したもの | 変えたもの |
|---|---|---|
| 1 | フォルダ名 `release-check`、本文 | `description` の1行 |
| 2 | フォルダ名 `memo-1`、本文 | `description` の1行 |
| 3 | フォルダ名 `memo-1`、本文、良い `description` | `disable-model-invocation` の有無 |

実験1で差が出なかったため、原因（フォルダ名そのものが説明になっていた）を
潰したのが実験2。実験3は逆向きに「止まるか」を見たもの。

## 動かし方

```bash
./run_all.sh | tee output.txt          # 3実験ぜんぶ（60回。20分ほど）
python3 make_figure.py output.txt out.svg   # 結果から棒グラフSVGを作る
```

個別に動かす場合:

```bash
./setup.sh  /home/user/skilllab        # 実験1の2つのプロジェクトを作る
python3 run_trials.py /home/user/skilllab 10 release-check
```

`run_trials.py` の引数は `<親ディレクトリ> <回数> <スキル名> [A名] [B名]`。
親ディレクトリの下に `A/` と `B/` があることを前提にしている。

## ファイル

| ファイル | 中身 |
|---|---|
| `setup.sh` / `setup2.sh` / `setup3.sh` | 実験1/2/3の2つのプロジェクトを作る |
| `run_trials.py` | N回実行し、`Skill` ツールが呼ばれた回数を数える |
| `run_all.sh` | 3実験を順に走らせる |
| `make_figure.py` | `output.txt` から記事の棒グラフSVGを作る（数字を手で写さないため） |
| `output.txt` | 実行結果。記事に貼ったものと同一 |

## 判定のしかた

`claude -p ... --output-format stream-json --verbose` の各行を JSON として読み、
`type` が `assistant` のメッセージの中に
`tool_use` かつ `name == "Skill"` かつ `input.skill == <対象スキル名>`
があれば「呼ばれた」と数える。

毎回 `--session-id` に新しい UUID を渡し、前の回を引きずらないようにしている。

## 実行環境

- 実行日: 2026年8月26日 (JST)
- Claude Code 2.1.245
- Python 3.11.15
- Linux x86-64 のコンテナ

## 注意

- **数字は毎回揺れる。** 呼ぶかどうかはモデルの判断なので、同じ手順でも一致しない。
  1条件10回は統計として差を主張できる回数ではない。傾向を見るためのもの
- 1回あたり約 $0.09 かかった。60回で約 $5.5
- 記事に貼った出力は、中略を明示した以外は無加工

## 確認できなかったこと

公式ドキュメントの「Inject dynamic context」（本文に `` !`コマンド` `` と書くと
実行結果が埋め込まれる）は、`claude -p` では埋め込みが起きなかった。
モデルが自分で Bash を使ってコマンドを実行しようとした。
対話画面では試していないので、機能が動かないとは判断していない。記事でも使っていない。

## 記事に貼った英語原文の照合

公式ドキュメントは `.md` を付けると素のテキストで取れる。
記事の `<div class="code wrap">` に入れた英文が、一字一致するかを機械で確かめる。

```bash
curl -s -o /tmp/skills.md https://code.claude.com/docs/en/skills.md
python3 verify_quotes.py ../../contents/2026-08-26_skills-trigger/index.html /tmp/skills.md
```

2026年8月26日の実行結果: 原文ブロック5件、不一致0件。
markdown の強調記号（`**` と バッククォート）は表示上は出ないので、比較前に落としている。
ドキュメント本体はここには置かない（他社の文章なので、必要なときに取得する）。

## 手で呼べば動くことの確認（実験3の補足）

`disable-model-invocation: true` を付けたスキル（`/home/user/skilllab3/B`）に対して、
スラッシュで直接呼んだ場合:

```bash
cd /home/user/skilllab3/B
claude -p "/memo-1" --session-id <新規UUID> --disallowed-tools "Bash"
```

答えはスキル本文の3項目（`git status` / テスト / バージョン番号）に沿った内容になった。
つまり**自動起動を切っても、手で呼ぶ経路は生きている**。

なお、この経路では `tool_use` の `Skill` は出ない。スラッシュで呼ぶと
本文がそのまま読み込まれるため。自動起動の判定に `Skill` の有無を使えるのはこのため。

## 記事に貼った実行結果の照合

空白を1つ足して見た目を整えるだけでも嘘になるので、機械で突き合わせる。

```bash
python3 verify_output.py ../../contents/2026-08-26_skills-trigger/index.html output.txt
```

2026年8月26日の実行結果: 不一致0件。
（実際、実験3の行を桁揃えのつもりで空白1つ足していたのをこれで見つけた）

## 追加（2026-08-27 未明に測り足した）

記事を深掘りするにあたって、名前まわりとコストを2つ足した。**まだ記事本文には反映していない**（`_HANDOFF.md` 参照）。

### 実験4: 同じ名前のスキルが2つあったらどちらが動くか

プラグイン `mattpocock-skills`（`grill-me` を含む）を入れた状態で、
プロジェクト側の `.claude/skills/grill-me/SKILL.md` に同名のスキルを置いた。

| 打ったもの | 動いたほう |
|---|---|
| `/grill-me` | **プロジェクト側**（本文どおり `LOCAL-WINS` と返った） |
| `/mattpocock-skills:grill-me` | プラグイン側 |

```bash
./setup4.sh /tmp/collide /tmp/ccfg2
./run4.sh   /tmp/collide /tmp/ccfg2   # 出力は output4.txt
```

### 実験5: 「本文は呼ぶまでタダ」を数字で見る

`claude plugin details <名前>` が、常駐ぶんと呼び出しぶんを分けて出す。
25スキルで常駐は約1,609トークン、本文はスキルごとに20〜3,800トークン。
出力は `output5.txt`。
