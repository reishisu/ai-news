# Laravel を最初に動かすまで — 実証記録

実施日: 2026年8月15日

## 何を確かめたか

1. `composer create-project laravel/laravel` を実際に実行した
2. **その直後の `php artisan test` は落ちない**（依頼された前提とは違った。後述）
3. `git clone` 相当の状況（`APP_KEY` 空）で `php artisan test` が
   `MissingAppKeyException` で落ちる様子を測った
4. `php artisan key:generate` 後に通る様子を測った
5. ルート `/hello` を1本足して HTTP レスポンスを確認した
6. `APP_KEY` を空に戻すと HTTP 500、`key:generate` で 200 に戻ることを確認した

## 動かし方

```bash
bash repro.sh /path/to/workdir       # PORT=8903 などで上書き可
```

`narrow.py` が出力を40桁に折り返します（**折り返しのみ。内容は書き換えていません**）。
`width.py` は各行の表示幅を確認する検算用です。

- `output.txt` … `repro.sh` を最初から通して実行した結果（記事に貼るのはこれ）
- `create-project.log` … 最初の `composer create-project` の全ログ（724行、無加工）
- `err-page.png` … `APP_KEY` 空のときブラウザに出るエラー画面（Chromium 141で撮影）

## 実行環境

| 対象 | 版 |
|---|---|
| PHP | 8.4.19 |
| Composer | 2.8.12 |
| Laravel Framework | 13.25.0 |
| laravel/laravel | v13.9.0 |
| PHPUnit | 12.5.33 |
| Python | 3.11.15 |
| Chromium | 141.0.7390.37 |

## 重要な発見

### 1. `create-project` 直後の `php artisan test` は落ちない

依頼の前提（初回テストが `No application encryption key` で落ちる）は
**この手順では再現しなかった**。`composer.json` の
`post-create-project-cmd` が `key:generate` を自動実行するため。

```
"post-create-project-cmd": [
    "@php artisan key:generate --ansi",
    "@php -r \"file_exists('database/database.sqlite') || touch(...);\"",
    "@php artisan migrate --graceful --ansi"
]
```

`create-project` のログにも `INFO Application key set successfully.` が出ている。
`output.txt` のセクション3で `exit=0` / `2 passed`。

**あのエラーが出るのは `git clone` した既存プロジェクトの側**。
`.env.example` の `APP_KEY=` は空なので、`cp .env.example .env` した直後は鍵が無い。
`repro.sh` のセクション4はこれを再現している。

### 2. なぜ Unit は通って Feature だけ落ちるのか

- `tests/Unit/ExampleTest.php` … `PHPUnit\Framework\TestCase` を継承（Laravel を起動しない）
- `tests/Feature/ExampleTest.php` … `Tests\TestCase` を継承（Laravel を起動する）

鍵が要るのはアプリ起動時なので、`1 failed, 1 passed` になる。

### 3. `phpunit.xml` は `APP_KEY` を上書きしていない

`phpunit.xml` の `<php><env>` は `APP_ENV` `DB_CONNECTION` などを設定するが
`APP_KEY` は無い。だからテストは `.env` の `APP_KEY` をそのまま使う。
（テスト用DBは `sqlite` の `:memory:` に固定されている。）

### 4. `laravel/agent-detector` が出力形式を変える

Laravel 13 は `laravel/agent-detector` を同梱する。環境変数 `CLAUDECODE` などが
あると `php artisan test` の出力が **JSON になる**。

```
$ php artisan test
{"tool":"phpunit","result":"passed","tests":2,...}
```

`vendor/laravel/agent-detector/src/AgentDetector.php:19` に
`'CLAUDECODE' => KnownAgent::Claude` がある。人間と同じ表示を得るには
`env -u CLAUDECODE -u AI_AGENT` で外す。`repro.sh` はこれを行っている。

### 5. 出力幅は `COLUMNS` で制御できる

`COLUMNS=40` を渡すと Symfony Console / Collision が幅40で整形する。
ただし例外発生時のソース抜粋と `at vendor/...` のパスは折り返さない（最大88桁）。
`repro.sh` は `head -9` で要点だけを切り出している。

## 再現できなかったもの / 環境の制約

- **dist（zip）でのインストールは不可。** `codeload.github.com` が
  プロキシで HTTP 403 になるため、110パッケージすべてが
  `Failed to download ... from dist` → `Now trying to download from source`
  となり **git clone で入った**。
- そのため **`vendor/` の容量は参考にならない**。実測は 3.6G
  （`.git` を除いても 917M）だが、これは source インストールで各リポジトリの
  `.git` と `tools/`（phive で入る phar 群）まで入るため。
  通常の dist インストールでの容量は**この環境では測れていない**ので記事に書かない。
- Docker はデーモンが動いておらず**未実行**。
- MySQL/TiDB との接続は**この検証では行っていない**（テストDBは sqlite `:memory:`、
  アプリ側は `database/database.sqlite`）。

## 所要時間

`composer create-project` を含む `repro.sh` の全体が約65秒
（composer のキャッシュが温まった2回目以降の実測）。初回はもっとかかる。

---

## 追加の実証（2026年8月15日、記事執筆時に追加）

### `dbtest.sh` — テストDBは `.env` ではなく `phpunit.xml` を見ている

`bash dbtest.sh <example-app のパス>` → `dbtest-output.txt`

`tests/Feature/UserCountTest.php`（このディレクトリにコピーあり）で
`DB::table('users')->count()` を呼ぶだけのテストを実行した。

- `RefreshDatabase` なし → `QueryException` /
  `no such table: users (Connection: sqlite, Database: :memory:, ...)`
- `RefreshDatabase` あり → `1 passed`

アプリ側の `database/database.sqlite` には users を含む10テーブルが実在する
（`tables.php` で列挙）。それでもテストが `no such table` になるのは、
`phpunit.xml` が `DB_DATABASE` を `:memory:` に上書きしているため。

### `configcache.sh` — `config:cache` を打つと `.env` が読まれなくなる

`bash configcache.sh <example-app のパス>` → `configcache-output.txt`

1. `config:cache` を実行
2. `.env` の `APP_KEY` を空にする → `config("app.key")` は **まだ「あり」**
3. `config:clear` を実行 → ここで初めて「なし」になる
4. `key:generate` で後片付け

`php artisan tinker --execute` で `config("app.key")` の有無を出力している。

### 出力幅

`dbtest-output.txt` / `configcache-output.txt` はいずれも全行37桁以内
（`width.py` で検算済み）。`narrow.py` による折り返し以外の加工はしていない。

---

## 編集時の訂正（2026年8月15日、公開直前の検証で判明）

### 訂正1: スタックトレースの「先頭」は `public/index.php:20` ではない

初稿では「スタックトレースの先頭は `public/index.php:20`」と書いていたが**誤り**。
`APP_KEY` を空にして `php artisan serve --port=8917` に `curl` を当て、
エラー画面のHTMLを `err.html` として保存し、埋め込まれているコピー用データを
`trace-frames.txt` に抜き出して確認した。

- トレースの先頭（例外の発生地点）は
  `Illuminate/Encryption/EncryptionServiceProvider.php:83`
- `public/index.php:20` は **47番目**（コピー用データの通し番号）。
  さらに外側の48番目は `Illuminate/Foundation/resources/server.php:23`
  （`artisan serve` の組み込みサーバのルータ。本番構成には出てこない）

記事の2章・4章の該当箇所を訂正済み。

### 訂正2: JSON出力の犯人は `laravel/pao`。`agent-detector` は検出のみ

初稿では「原因は `laravel/agent-detector`」と書いていたが不正確。

- `composer.lock`: `laravel/pao v1.1.4` が `laravel/agent-detector ^2.0.2` を require
- `laravel/pao` の description は `Agent-optimized output for PHP testing tools`
- `duration_ms` を出しているのは
  `vendor/laravel/pao/src/Drivers/Concerns/TestResultParsable.php:231`
- `laravel/pao` は `laravel/framework` の依存ではなく、
  雛形 `laravel/laravel` の `require-dev`（`"laravel/pao": "^1.0.6"`）経由

再現ログは `agentoutput.txt`（`CLAUDECODE=1` あり／なしの両方）。

### 訂正3: 記事に貼るログの切り出しを全面的に見直した

`output.txt` から記事へ貼るとき、初稿では
セクション2まるごとと `Duration:` 行、`INFO Application key set` 行、
`{"message":"hello",...}` 行が**無断で落ちていた**。
これらを全部戻し、記事の `<pre>` が `output.txt` /
`dbtest-output.txt` / `configcache-output.txt` に
**部分文字列として完全一致する**ことを機械照合で確認した（空行の数まで一致）。

照合コマンド:

```bash
python3 - <<'PY'
import re,html
s=open('contents/2026-08-15_laravel-first/index.html').read()
blocks=re.findall(r'<div class="code term[^"]*">\s*<div class="code-head">(.*?)</div>\s*<pre>(.*?)</pre>',s,re.S)
srcs={n:open(f'_labs/2026-08-15_laravel-first/{n}.txt').read()
      for n in ('output','dbtest-output','configcache-output','agentoutput')}
for head,body in blocks:
    t=html.unescape(re.sub(r'</?span[^>]*>','',body))
    hit=[n for n,f in srcs.items() if t in f]
    print(('OK  ' if hit else 'MISS'), hit, '|', re.sub('<[^>]+>','',head)[:60])
PY
```

`dbtest.sh` は `head -6` でテスト出力を6行に切っているので、
記事の code-head にも「先頭6行だけ切り出し」と明記した。

### 訂正4: その他

- 公式Installationの引用は**ページの1文目ではなく**
  `Installing PHP and the Laravel Installer` 節の冒頭。記事の表現を修正。
- 必要ソフトは `either Node and NPM or Bun`。Bun を落としていたので追記。
- Encryption / Configuration / Database Testing の引用が途中で切れていた、
  名前空間を勝手に短縮していた、離れた2段落を無印で結合していた。
  いずれも原文どおりに戻し、間を空けた箇所は `（… 原文ではここに…）` と明示。
- `artisan` と `public/index.php` は「実質部分」と称して
  `define('LARAVEL_START', ...)` やメンテナンスモード判定を落としていた。
  **全文（18行 / 20行）を行番号つきで掲載**に変更。
  これで `public/index.php:20` が最終行であることも読者が確認できる。
- `sqlite_sequence` は SQLite の内部テーブル。
  「10個のテーブル」→「10個のうちマイグレーションが作ったのは9個」に修正。
- Pest 4系が入るという断定は `laravel new` 未実行のため推論。
  「〜になるはず」＋推論である旨の明記に修正。

## 追加したファイル

| ファイル | 内容 |
|---|---|
| `agentoutput.txt` | `CLAUDECODE=1` あり／なしでの `php artisan test` の出力 |
| `err.html.gz` | `APP_KEY` 空のときのエラー画面のHTML（curlで取得、gzip圧縮。`gunzip -k err.html.gz` で展開） |
| `trace-frames.txt` | `err.html` から抜き出したスタックトレース48フレームの一覧 |

再取得の手順（`example-app` に対して）:

```bash
cp .env /tmp/env.bak
sed -i 's/^APP_KEY=.*/APP_KEY=/' .env
php artisan config:clear
php artisan serve --port=8917 &
curl -s http://127.0.0.1:8917/ -o err.html && gzip -9 err.html
pkill -f 'artisan serve --port=8917'
cp /tmp/env.bak .env && php artisan key:generate
```
