# 2026-08-26_001 の検証記録

対象期間: **2026-08-25 05:00 〜 2026-08-26 05:00 JST**（= 08-24 20:00 〜 08-25 20:00 UTC）。
技術・研究の節だけ48時間に拡大した（24時間の枠に該当が0件だったため。記事本文にも明記）。

## 実行環境

- このコンテナ（Linux / UTC）。python3 3.x / curl / PHP 8.4.19 / playwright（`pip install playwright`）
- ブラウザは同梱の `/opt/pw-browsers/chromium` を使う（`playwright install` は不要）
- **github.com / api.github.com / openai.com は403。** raw.githubusercontent.com と cdn.jsdelivr.net は通る

## ファイル

| ファイル | 何を確かめるか |
|---|---|
| `verify_sources.sh` | 全体の裏取り。npmの公開時刻、CHANGELOGの行数、Laravelの差分、Chrome/WebViewの版、CVEの内訳、AWSの期間内item、読めなかったURLのHTTPステータス |
| `count_cves.py` | Chrome Releases の最新記事からCVEを重大度と部品ごとに数える |
| `laravel_strict.sh` | `in_array` / `doesnt_contain` / `contains` の3ルールを2つのタグのソースで比べる |
| `strict.php` | PHPの `in_array` が第3引数の有無でどう変わるかを実測 |
| `qa.py` | 幅380px / 900px の表示検証（横スクロール・はみ出し・JSエラー・チェックリスト） |
| `output.txt` | `verify_sources.sh` の実行結果 |
| `cves.txt` / `laravel_diff.txt` / `strict_out.txt` | 記事に貼った出力と同一 |
| `watch.txt` | `_watch_sources.py --since 3` の結果 |

## 分かったこと（次回に効く）

### 1. `_fetch_popular.py` の404は一時的なものだった

前号の申し送りに「`GOATCOUNTER_TOKEN` は設定済みなのに404。2日連続で失敗」とあったが、
**同じURLを直接叩くと200が返る。** 今回も1回目は404、そのまま再実行したら成功した。
`https://reishisu-ai-news.goatcounter.com/api/v0/stats/hits?start=...&limit=200` は
`api/v0/me` も含めて正常。**スクリプトの不具合ではないので、404が出たらもう一度流すこと。**

### 2. `chromiumdash` の `fetch_releases` は Chrome本体とWebViewを同じ形で引ける

```
https://chromiumdash.appspot.com/fetch_releases?channel=Stable&platform=webview&num=3
```

`platform` に `win` / `mac` / `android` / `webview` を渡せる。
**ただし返ってくる `time` はダッシュボード側の更新時刻**で、公開時刻ではない。
同じバッチで更新された複数の版が同じ時刻を持つ（今回、android の 152 と 151 が同じ 18:18 UTC）。
公開時刻は Chrome Releases の投稿時刻を使うこと。

### 3. AWSのドキュメントページは本文が取れない

`docs.aws.amazon.com/AmazonECS/latest/developerguide/monitor-container-instance-health.html`
はHTTP 200を返すが、**中身は1125バイトのJSシェル**で本文が入っていない。
抽出できるテキストは34文字（「Amazon Elastic Container Service」だけ）。
告知（What's New）の本文はサーバー側で組み立てられているので読める。**根拠は告知側に寄せること。**

### 4. Laravelのリリースノートは `raw.githubusercontent.com` の 13.x ブランチで読める

`cdn.jsdelivr.net` のブランチ配信は**キャッシュが古く、当日のリリースが載っていない**
（v13.27.0 のタグでも CHANGELOG には v13.26.1 までしか無かった。リリース後に
CHANGELOG を更新するコミットが別に入るため）。
`https://raw.githubusercontent.com/laravel/framework/13.x/CHANGELOG.md` は最新だった。

### 5. X(旧Twitter)は3日連続で取れていない

`syndication.twitter.com` のプロフィール取得は429。
ただし **`cdn.syndication.twimg.com/tweet-result?id=<ID>&token=a` は404を返す**（=到達はしている）。
投稿IDさえ分かれば個別本文は取れる可能性がある。**列挙する経路だけが塞がっている。**

### 6. openai.com はブラウザ相当のヘッダでも403

`User-Agent` / `Accept` / `Accept-Language` を付けても403（10KBのチャレンジページが返る）。
`help.openai.com` も403。**RSS（`openai.com/news/rss.xml`）だけは200で読める**ので、
「何が出たか」は分かるが「何が書いてあるか」は分からない。
第1節の規律どおり、本文を読めないものは項目にしない。

### 7. CHANGELOGを数えるとき `[VSCode]` 接頭辞で数え漏らす（8/26に踏んだ）

`grep -oE '^- (Added|Changed|Fixed|Improved|Updated)'` だと
**`- [VSCode] Fixed …` のような接頭辞付きの行を落とす。**
2.1.243 は箇条書きが60行あるのに、この正規表現では56行にしかならなかった。

```bash
# まず総数を出して、内訳の合計と突き合わせること
awk '/^## 2\.1\.243$/{f=1;next} /^## /{f=0} f' CHANGELOG.md | grep -c '^- '
awk '/^## 2\.1\.243$/{f=1;next} /^## /{f=0} f' CHANGELOG.md \
 | grep -oE '^- (\[VSCode\] )?(Added|Changed|Removed|Fixed|Improved|Updated)' \
 | sed 's/\[VSCode\] //' | sort | uniq -c
```

CLAUDE.md 第16節の「数えた件数と、扱った件数・捨てた件数が合うことを確認」は、
**総数と内訳の合計を突き合わせて初めて効く。** 内訳だけ見ても漏れに気づけない。

### 8. 引用は「行末のピリオド」まで原文どおりにする

Claude Code の CHANGELOG は各行の末尾にピリオドが無い。
記事に貼るとき無意識に足していて、検証で見つかった。
**原文を貼ったら、必ず取得元の文字列に対して `in` で一致を確認すること**
（`_labs/2026-08-26_001/` の検証ではこの照合を最後に回した）。
